from __future__ import annotations
from collections import Counter,deque
from dataclasses import dataclass
from pathlib import Path
import os
import shutil
import tempfile
import time
import numpy as np
import pyarrow as pa
import pyarrow.feather as feather
from scipy import sparse
from scipy.sparse.csgraph import connected_components
import networkx as nx
from .util import atomic_json,read_json,digest,sha256,now

@dataclass
class Graph:
    ids: np.ndarray
    source: np.ndarray
    target: np.ndarray
    counts: np.ndarray
    metadata: dict
    def __post_init__(self):
        for arr in (self.ids,self.source,self.target,self.counts):
            if not np.issubdtype(arr.dtype,np.integer): raise ValueError('IDs/indices/counts must be integers')
        if len(np.unique(self.ids))!=len(self.ids): raise ValueError('Duplicate body IDs')
        if not (len(self.source)==len(self.target)==len(self.counts)): raise ValueError('Edge length mismatch')
        n=len(self.ids)
        if len(self.source):
            if min(self.source.min(),self.target.min())<0 or max(self.source.max(),self.target.max())>=n: raise ValueError('Edge bounds')
            if np.any(self.source==self.target): raise ValueError('Anatomical self-edge')
            if len(np.unique(self.source*n+self.target))!=len(self.source): raise ValueError('Duplicate ordered pairs')
        order=np.lexsort((self.source,self.target))
        self.source=self.source[order]; self.target=self.target[order]; self.counts=self.counts[order]
    @property
    def hash(self) -> str:
        return digest({'ids':[str(v) for v in self.ids],'source':self.source.tolist(),
                       'target':self.target.tolist(),'counts':self.counts.tolist(),'metadata':self.metadata})
    def save(self,path:Path) -> None:
        path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists():
            if Graph.load(path).hash!=self.hash: raise ValueError(f'Graph immutable: {path}')
            return
        with path.with_suffix('.tmp').open('wb') as f:
            np.savez_compressed(f,ids=self.ids,source=self.source,target=self.target,counts=self.counts)
        os.replace(path.with_suffix('.tmp'),path)
        nodes=path.with_suffix('.nodes.tsv'); nodes.write_text('model_index\tbody_id\n'+''.join(f'{i}\t{int(v)}\n' for i,v in enumerate(self.ids)))
        edges=path.with_suffix('.edges.tsv'); edges.write_text('source_body_id\ttarget_body_id\tsynapse_count\n'+''.join(f'{int(self.ids[s])}\t{int(self.ids[t])}\t{int(c)}\n' for s,t,c in zip(self.source,self.target,self.counts)))
        atomic_json(path.with_suffix('.json'),{'metadata':self.metadata,'graph_hash':self.hash,'file_sha256':sha256(path),
                                             'sidecar_sha256':{p.name:sha256(p) for p in [nodes,edges]},
                                             'diagnostics':diagnostics(self)})
    @classmethod
    def load(cls,path:Path):
        m=read_json(path.with_suffix('.json'))
        if sha256(path)!=m['file_sha256']: raise ValueError('Graph file checksum')
        for name,h in m.get('sidecar_sha256',{}).items():
            if sha256(path.parent/name)!=h: raise ValueError('Graph sidecar checksum')
        with np.load(path,allow_pickle=False) as d: g=cls(*(d[k] for k in ['ids','source','target','counts']),m['metadata'])
        if g.hash!=m['graph_hash']: raise ValueError('Graph content checksum')
        return g

def diagnostics(graph:Graph,original:Graph|None=None) -> dict:
    n=len(graph.ids); e=len(graph.source)
    g=nx.DiGraph(); g.add_nodes_from(range(n)); g.add_edges_from(zip(graph.source.tolist(),graph.target.tolist()))
    ind=np.bincount(graph.target,minlength=n); out=np.bincount(graph.source,minlength=n)
    result={'N':n,'E':e,'density':e/(n*(n-1)) if n>1 else 0.,'in_degree':ind.tolist(),'out_degree':out.tolist(),
            'in_degree_distribution':np.bincount(ind).tolist(),'out_degree_distribution':np.bincount(out).tolist(),
            'contact_count_quantiles':np.quantile(graph.counts,[0,.25,.5,.75,1]).tolist() if e else [],
            'contact_count_distribution':{str(k):int(v) for k,v in zip(*np.unique(graph.counts,return_counts=True))},
            'weak_component_sizes':sorted(map(len,nx.weakly_connected_components(g)),reverse=True),
            'strong_component_sizes':sorted(map(len,nx.strongly_connected_components(g)),reverse=True),
            'reciprocity':float(nx.reciprocity(g) or 0) if e else 0.,
            'counts_anatomical':graph.metadata.get('condition','FLY-TOPOLOGY')=='FLY-TOPOLOGY' and not graph.metadata.get('synthetic',False)}
    if original is not None:
        a=set(zip(original.source.tolist(),original.target.tolist())); b=set(g.edges())
        result['overlap_with_original_fraction']=len(a&b)/len(a) if a else 1.
    return result

def canonicalize(raw_manifest:Path,out:Path) -> dict:
    manifest=read_json(raw_manifest); out.mkdir(parents=True,exist_ok=True)
    existing=out/'canonical-manifest.json'
    if existing.exists():
        result=read_json(existing)
        if result['raw_manifest_sha256']!=sha256(raw_manifest): raise ValueError('Changed raw manifest')
        for name,h in result['files'].items():
            if sha256(out/name)!=h: raise ValueError('Changed canonical graph')
        return result
    t0=time.perf_counter()
    items={f['name']:f for f in manifest['files']}
    ann=next(v for k,v in items.items() if k.startswith('body-annotations'))
    weights=next(v for k,v in items.items() if k.startswith('connectome-weights'))
    for item in (ann,weights):
        if sha256(Path(item['path']))!=item['sha256']: raise ValueError('Raw file changed')
    table=feather.read_table(ann['path'],columns=['bodyId','status','statusLabel','type','superclass','class'],memory_map=True)
    if table['bodyId'].type!=pa.int64() or table['bodyId'].null_count: raise ValueError('Body ID schema')
    body=table['bodyId'].to_numpy(); statuses=table['status'].to_pylist()
    if len(np.unique(body))!=len(body): raise ValueError('Repeated annotation body IDs')
    explicitly_bad={'glia','error','non-neuronal','non_neuronal','artifact'}
    keep=np.array([s=='Traced' for s in statuses])
    explicit=np.zeros(len(body),dtype=bool)
    for col in ['statusLabel','superclass','class','type']:
        explicit|=np.array([str(v).lower() in explicitly_bad for v in table[col].to_pylist()])
    keep &= ~explicit
    inventory=table.filter(pa.array(keep)).sort_by([('bodyId','ascending')])
    ids=inventory['bodyId'].to_numpy().copy(); n=len(ids)
    feather.write_feather(inventory,out/'curated-neurons.feather')
    np.save(out/'body_ids.npy',ids)
    # Audit ALL raw ordered pairs via bounded disk partitions, including excluded endpoints.
    # No pair totals or region subtotals are summed; duplicate ambiguity aborts.
    estimate=weights['schema']['rows']*16
    if shutil.disk_usage(out).free<estimate+3_000_000_000: raise RuntimeError('Need disk for exact duplicate-pair audit')
    retained=[]; totals=Counter(); previous_counts=[]
    with tempfile.TemporaryDirectory(prefix='pair-audit-',dir=out) as temp:
        paths=[Path(temp)/f'{i}.bin' for i in range(32)]
        handles=[p.open('wb') for p in paths]
        try:
            with pa.memory_map(weights['path'],'r') as f:
                reader=pa.ipc.open_file(f)
                if reader.schema.names!=['body_pre','body_post','weight'] or any(field.type!=pa.int64() for field in reader.schema):
                    raise ValueError('Unrecognized weight schema; resolve aggregation/direction explicitly')
                for k in range(reader.num_record_batches):
                    b=reader.get_batch(k)
                    if any(c.null_count for c in b.columns): raise ValueError('Null edge fields')
                    s,t,c=[col.to_numpy() for col in b.columns]
                    if np.any(c<0) or np.any(s<0) or np.any(t<0): raise ValueError('Negative anatomical values')
                    pairs=np.column_stack((s,t)).astype('<i8',copy=False)
                    buckets=(s%32).astype(np.int8)
                    order=np.argsort(buckets,kind='stable'); boundaries=np.searchsorted(buckets[order],np.arange(33))
                    sorted_pairs=pairs[order]
                    for slot in range(32):
                        handles[slot].write(sorted_pairs[boundaries[slot]:boundaries[slot+1]].tobytes())
                    a=np.searchsorted(ids,s); z=np.searchsorted(ids,t)
                    valid=(a<n)&(z<n)&(ids[np.minimum(a,n-1)]==s)&(ids[np.minimum(z,n-1)]==t)
                    totals['raw_edges']+=len(s); totals['excluded_noncurated_endpoints']+=int((~valid).sum())
                    totals['curated_below_threshold']+=int((valid&(c<5)).sum())
                    above=valid&(c>=5)
                    totals['removed_self_edges_at_threshold']+=int((above&(s==t)).sum())
                    good=above&(s!=t)
                    retained.append(np.column_stack((a[good],z[good],c[good])).astype(np.int64))
                    if k%400==0: print(f'Canonical batch {k}/{reader.num_record_batches}',flush=True)
        finally:
            for h in handles: h.close()
        for p in paths:
            pairs=np.fromfile(p,dtype=np.dtype([('s','<i8'),('t','<i8')]))
            pairs.sort(order=['s','t'])
            if np.any(pairs[1:]==pairs[:-1]): raise ValueError('Duplicate ordered pairs in source: aggregation ambiguous; refusing to sum')
            p.unlink()
    edges=np.concatenate(retained); del retained
    order=np.lexsort((edges[:,1],edges[:,0])); edges=edges[order]
    np.save(out/'source.npy',edges[:,0].astype(np.int32)); np.save(out/'target.npy',edges[:,1].astype(np.int32)); np.save(out/'counts.npy',edges[:,2])
    files={name:sha256(out/name) for name in ['curated-neurons.feather','body_ids.npy','source.npy','target.npy','counts.npy']}
    result={'release':manifest['release'],'raw_manifest_sha256':sha256(raw_manifest),'created_utc':now(),
            'mapping':{'body_pre':'source_body_id','body_post':'target_body_id','weight':'synapse_count'},
            'aggregation':'All raw ordered pairs audited exactly by disk partitions; no duplicates; no regional fields; no summation',
            'inventory_rule':'status == Traced; exclude explicit non-neuronal/error labels; retain missing type',
            'status_counts':dict(Counter(str(v) for v in statuses)),
            'excluded_status_counts':dict(Counter(str(s) for s,k in zip(statuses,keep) if not k)),
            'explicitly_non_neuronal_or_error':int(explicit.sum()),
            'unresolved_classification_statuses':['None','Assign','Anchor','Unimportant','Orphan'],
            'retained_missing_type':inventory['type'].null_count,'curated_N':n,'retained_E':len(edges),
            'exclusions':dict(totals),'files':files,'preprocessing_seconds':time.perf_counter()-t0}
    atomic_json(existing,result); return result

def extract(canonical:Path,n:int,seed:int,smoke:bool=False) -> Graph:
    if n not in (64,512,1024) or (n==64 and not smoke): raise ValueError('64 only smoke; research 512; named follow-up 1024')
    meta=read_json(canonical/'canonical-manifest.json')
    for name,h in meta['files'].items():
        if sha256(canonical/name)!=h: raise ValueError('Canonical graph checksum mismatch')
    ids=np.load(canonical/'body_ids.npy',mmap_mode='r'); s=np.load(canonical/'source.npy',mmap_mode='r')
    t=np.load(canonical/'target.npy',mmap_mode='r'); c=np.load(canonical/'counts.npy',mmap_mode='r')
    a=sparse.csr_matrix((np.ones(len(s),dtype=np.uint8),(s,t)),shape=(len(ids),len(ids)))
    _,labels=connected_components(a,directed=True,connection='weak')
    sizes=np.bincount(labels); max_size=sizes.max()
    candidates=np.flatnonzero(sizes==max_size)
    label=min(candidates,key=lambda k:int(ids[np.flatnonzero(labels==k)[0]]))
    component=np.flatnonzero(labels==label)
    if len(component)<n: raise ValueError(f'Largest weak component {len(component)} < requested {n}')
    undirected=(a+a.T).astype(bool).tocsr(); undirected.sort_indices()
    rng=np.random.default_rng(seed); start=int(rng.choice(component)); selected={start}; queue=deque([start])
    while queue and len(selected)<n:
        current=queue.popleft(); neighbors=undirected.indices[undirected.indptr[current]:undirected.indptr[current+1]].copy()
        rng.shuffle(neighbors)
        for v in neighbors:
            if int(v) in selected: continue
            selected.add(int(v)); queue.append(int(v))
            if len(selected)==n: break
    indices=np.array(sorted(selected),dtype=np.int64)
    if len(indices)!=n: raise RuntimeError('BFS failed requested size')
    inverse=np.full(len(ids),-1,dtype=np.int32); inverse[indices]=np.arange(n)
    use=(inverse[s]>=0)&(inverse[t]>=0)
    out_degree=np.bincount(s,minlength=len(ids))[indices]; in_degree=np.bincount(t,minlength=len(ids))[indices]
    out_contacts=np.bincount(s,weights=c,minlength=len(ids))[indices]; in_contacts=np.bincount(t,weights=c,minlength=len(ids))[indices]
    internal_out=np.bincount(inverse[s[use]],minlength=n); internal_in=np.bincount(inverse[t[use]],minlength=n)
    internal_out_c=np.bincount(inverse[s[use]],weights=c[use],minlength=n); internal_in_c=np.bincount(inverse[t[use]],weights=c[use],minlength=n)
    inventory=feather.read_table(canonical/'curated-neurons.feather').take(pa.array(indices))
    metadata={'synthetic':False,'release':'male-cns:v1.0','condition':'FLY-TOPOLOGY','sampling_seed':seed,
              'canonical_manifest_sha256':sha256(canonical/'canonical-manifest.json'),'threshold':5,
              'algorithm':'uniform start, shuffled-neighbor BFS in largest weak component; induced directed graph',
              'start_body_id':str(ids[start]),'largest_weak_size':int(max_size),'requested_n':n,'smoke':smoke,
              'node_classes':{k:inventory[k].to_pylist() for k in ['type','superclass','class']},
              'external_loss':{'incoming_edges':(in_degree-internal_in).tolist(),'outgoing_edges':(out_degree-internal_out).tolist(),
                               'incoming_contacts':(in_contacts-internal_in_c).astype(np.int64).tolist(),
                               'outgoing_contacts':(out_contacts-internal_out_c).astype(np.int64).tolist(),
                               'incoming_edge_fraction':float((in_degree-internal_in).sum()/max(in_degree.sum(),1)),
                               'outgoing_edge_fraction':float((out_degree-internal_out).sum()/max(out_degree.sum(),1))},
              'bias_note':'A local connected neighborhood from one specimen; not independent animals'}
    return Graph(ids[indices].copy(),inverse[s[use]],inverse[t[use]],c[use].copy(),metadata)

def synthetic_graph(n:int=64,seed:int=101,*,synthetic:bool=False,smoke:bool=False) -> Graph:
    if not synthetic or not smoke: raise PermissionError('Synthetic requires --synthetic --smoke')
    rng=np.random.default_rng(seed)
    pairs=rng.choice(n*(n-1),size=n*6,replace=False); s=pairs//(n-1); t=pairs%(n-1); t+=t>=s
    return Graph(np.arange(n,dtype=np.int64),s,t,np.full(len(s),5,dtype=np.int64),
                 {'synthetic':True,'sampling_seed':seed,'condition':'FLY-TOPOLOGY','release':'SYNTHETIC-SMOKE','smoke':True})

def assert_scientific(graph:Graph,profile:str) -> None:
    if profile!='smoke' and (graph.metadata.get('synthetic') or graph.metadata.get('release')!='male-cns:v1.0'):
        raise PermissionError('Scientific runs require verified real male-cns:v1.0 graph')
    if profile!='smoke' and len(graph.ids)!=512: raise ValueError('Research profile requires 512 nodes; 1024 is a separate follow-up')
