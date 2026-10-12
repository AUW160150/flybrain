"""Bounded, directed, vertex-simple path search on the FULL released graph.

Counts and node/edge membership are exhaustive within the configured bound.
CSV paths are deterministic examples with a separately reported per-pair/depth cap.
Weights annotate paths; they do not affect search or imply physiological influence.
"""
from pathlib import Path
import csv,json,collections,hashlib,gc,time
import numpy as np
import pyarrow.feather as ft
import pyarrow.compute as pc
import pyarrow as pa
from scipy.sparse import load_npz,csr_matrix
from scipy.sparse.csgraph import connected_components

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/(ROOT/'config/current_structural_run.txt').read_text().strip()
INF=32767

def csvout(path,rows,fields=None):
    rows=list(rows)
    with open(path,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)

def simple_paths(adj, starts, targets, distance, bound):
    """Yield simple paths, continuing past one target to permit other endpoints."""
    targetset=set(targets)
    cache={}
    def candidates(v,remaining):
        key=(v,remaining)
        if key not in cache:cache[key]=[u for u in adj.get(v,()) if distance.get(u,INF)<=remaining-1]
        return cache[key]
    def walk(path):
        v=path[-1];depth=len(path)-1
        if depth and v in targetset:yield path
        if depth==bound:return
        for u in candidates(v,bound-depth):
            if u not in path:yield from walk(path+(u,))
    for source in sorted(starts):yield from walk((source,))

def membership(mask):
    x=[]
    if mask&15:x.append('A')
    if mask&2:x.append('B')
    if mask&4:x.append('C')
    if mask&6:x.append('D')
    if mask&16:x.append('E')
    return '|'.join(x)

def main():
    cfg=json.loads((RUN/'search_config.json').read_text());H=cfg['max_simple_path_hops'];cap=cfg['saved_simple_paths_per_pair_per_hop'];shortcap=cfg['saved_shortest_paths_per_pair']
    ids=np.load(RUN/'analysis/body_ids.npy',mmap_mode='r');g=load_npz(RUN/'analysis/graph.npz')
    gr=json.loads((RUN/'analysis/groups.json').read_text());groups=gr['groups'];motors=gr['targets'];candidate=groups['GNG021']
    dist={b:np.load(RUN/f'analysis/distance_to_{b}.npy',mmap_mode='r') for b in motors+candidate}
    dA=np.load(RUN/'analysis/distance_from_A.npy',mmap_mode='r');dE=np.load(RUN/'analysis/distance_from_GNG021.npy',mmap_mode='r')
    dm=np.load(RUN/'analysis/distance_to_any_motor.npy',mmap_mode='r');de=np.minimum(dist[candidate[0]],dist[candidate[1]])
    # Exact lower-bound corridor; no weight/type/side/status cutoff. DFS removes walks with repeated vertices.
    pool={}
    for lo in range(0,len(ids),100000):
        hi=min(lo+100000,len(ids));ii=np.repeat(np.arange(lo,hi),np.diff(g.indptr[lo:hi+1]));jj=g.indices[g.indptr[lo]:g.indptr[hi]];ww=g.data[g.indptr[lo]:g.indptr[hi]]
        keep=(dA[ii].astype(np.int32)+1+dm[jj]<=H)|(dA[ii].astype(np.int32)+1+de[jj]<=H)|(dE[ii].astype(np.int32)+1+dm[jj]<=H)
        for a,b,w in zip(ids[ii[keep]].tolist(),ids[jj[keep]].tolist(),ww[keep].tolist()):pool[a,b]=w
    print('Candidate corridor edges',len(pool),flush=True)
    adj=collections.defaultdict(list)
    for a,b in pool:adj[a].append(b)
    for a in adj:adj[a].sort()
    vs=sorted({v for e in pool for v in e});ix=np.searchsorted(ids,vs)
    reverse_small={t:dict(zip(vs,dist[t][ix].tolist())) for t in dist}
    md=dict(zip(vs,dm[ix].tolist()));ed=dict(zip(vs,de[ix].tolist()))
    annotations=ft.read_table(ROOT/'data/raw/body-annotations-male-cns-v1.0-minconf-0.5.feather').to_pylist()
    ann={r['bodyId']:r for r in annotations};del annotations
    def meta(b):
        r=ann.get(b,{})
        return r.get('type') or '',r.get('somaSide') or r.get('rootSide') or 'unknown'
    subtype={b:s for s in ['LB3a','LB3b','LB3c','LB3d'] for b in groups[s]}
    bits={'LB3a':1,'LB3b':2,'LB3c':4,'LB3d':8}
    fields=['path_id','analysis','source','source_type','source_side','target','target_type','target_side','hops','is_shortest','body_ids','edge_synapse_counts','types','sides','endpoint_laterality','opposite_side_steps','unknown_side_steps','circuit_membership','provenance','evidence']
    fnames=['simple_paths','shortest_paths','lb3b_paths','lb3c_paths','lb3b_lb3c_combined_paths','gng021_candidate_paths']
    handles={n:open(RUN/f'{n}.csv','w',newline='') for n in fnames};writers={n:csv.DictWriter(f,fieldnames=fields) for n,f in handles.items()}
    for w in writers.values():w.writeheader()
    counts=collections.Counter();shortsaved=collections.Counter();saved=collections.Counter()
    edges_by_hop=[{} for _ in range(H+1)];nodes_by_hop=[{} for _ in range(H+1)]
    via_candidate=collections.Counter();via_named=collections.Counter();path_side_counts=collections.Counter()
    namedtypes={'GNG042','GNG015','ANXXX462a','GNG021','GNG585','GNG108','GNG120','GNG472'}
    scopes=[('sensory_to_motor',groups['A'],motors,md),('sensory_to_gng021',groups['A'],candidate,ed),('gng021_to_motor',candidate,motors,md)]
    for mode,starts,targets,dmin in scopes:
        t0=time.time();n=0
        for path in simple_paths(adj,starts,targets,dmin,H):
            n+=1;source,target=path[0],path[-1];h=len(path)-1;key=(mode,source,target,h)
            counts[key]+=1;is_shortest=(h==reverse_small[target].get(source,INF));mask=bits[subtype[source]] if mode=='sensory_to_motor' else 16
            for v in path:nodes_by_hop[h][v]=nodes_by_hop[h].get(v,0)|mask
            for e in zip(path,path[1:]):edges_by_hop[h][e]=edges_by_hop[h].get(e,0)|mask
            if mode=='sensory_to_motor':
                if any(v in candidate for v in path):via_candidate[source,target,h]+=1
                nts={meta(v)[0] for v in path[1:-1]}&namedtypes
                for nt in nts:via_named[subtype[source],nt,target,h]+=1
            # All paths contribute to exact side totals, even if CSV examples are capped.
            ss=meta(source)[1];ts=meta(target)[1]
            path_side_counts[mode,subtype.get(source,'GNG021'),ss,meta(target)[0],ts,h]+=1
            save_simple=counts[key]<=cap; sk=(mode,source,target)
            save_short=is_shortest and shortsaved[sk]<shortcap
            if save_simple or save_short:
                types=[meta(v)[0] for v in path];sides=[meta(v)[1] for v in path]
                opposite=sum(a in ('L','R') and b in ('L','R') and a!=b for a,b in zip(sides,sides[1:]));unknown=sum(a not in ('L','R') or b not in ('L','R') for a,b in zip(sides,sides[1:]))
                row=dict(path_id=mode+'_'+hashlib.sha256(':'.join(map(str,path)).encode()).hexdigest()[:20],analysis=mode,source=source,source_type=types[0],source_side=sides[0],target=target,target_type=types[-1],target_side=sides[-1],hops=h,is_shortest=is_shortest,body_ids=json.dumps(path,separators=(',',':')),edge_synapse_counts=json.dumps([pool[e] for e in zip(path,path[1:])],separators=(',',':')),types=json.dumps(types,separators=(',',':')),sides=json.dumps(sides,separators=(',',':')),endpoint_laterality='ipsilateral' if ss==ts and ss in ('L','R') else 'contralateral' if ss in ('L','R') and ts in ('L','R') else 'unknown',opposite_side_steps=opposite,unknown_side_steps=unknown,circuit_membership=membership(mask),provenance='official_flat_full_graph; raw_edges.csv body pair join; edge query provenance in raw_edges.csv',evidence='STRUCTURAL CONNECTIVITY ONLY')
                if save_simple:
                    writers['simple_paths'].writerow(row);saved[key]+=1
                    if mode=='sensory_to_motor':
                        if subtype[source]=='LB3b':writers['lb3b_paths'].writerow(row)
                        if subtype[source]=='LB3c':writers['lb3c_paths'].writerow(row)
                        if subtype[source] in ('LB3b','LB3c'):writers['lb3b_lb3c_combined_paths'].writerow(row)
                    else:writers['gng021_candidate_paths'].writerow(row)
                if save_short:writers['shortest_paths'].writerow(row);shortsaved[sk]+=1
            if n%1000000==0:print(mode,n,'paths',round(time.time()-t0,1),'sec',flush=True)
        print(mode,'complete',n,round(time.time()-t0,1),'sec',flush=True)
    for f in handles.values():f.close()
    reach=[]
    for mode,starts,targets,_ in scopes:
        for a in sorted(starts):
            for b in sorted(targets):
                ai=int(np.searchsorted(ids,a));bi=int(np.searchsorted(ids,b));d=int(dist[b][ai]);shorttotal=counts[mode,a,b,d]
                assert d<=H or d==INF, 'Need additional shortest-only search beyond simple-path bound'
                reach.append(dict(analysis=mode,source=a,source_type=meta(a)[0],source_side=meta(a)[1],target=b,target_type=meta(b)[0],target_side=meta(b)[1],reachable=d<INF,shortest_hops=d if d<INF else '',direct_synapse_count=int(g[ai,bi]),shortest_path_count=shorttotal,shortest_paths_saved=shortsaved[mode,a,b],shortest_enumeration_complete=shorttotal==shortsaved[mode,a,b],simple_paths_h1=counts[mode,a,b,1],simple_paths_h2=counts[mode,a,b,2],simple_paths_h3=counts[mode,a,b,3],simple_paths_h4=counts[mode,a,b,4],bound_hops=H,scope='full released segment graph; no weight threshold',provenance='analysis/distance_to_'+str(b)+'.npy; analysis/graph.npz; raw/flat_weights_provenance.json'))
    csvout(RUN/'source_target_reachability.csv',reach)
    csvout(RUN/'path_enumeration_counts.csv',[dict(analysis=m,source=a,target=b,hops=h,total_simple_paths=n,saved_simple_paths=saved[m,a,b,h],csv_examples_complete=n==saved[m,a,b,h],membership_search_complete=True,max_hops=H) for (m,a,b,h),n in sorted(counts.items())])
    csvout(RUN/'path_counts_by_side.csv',[dict(analysis=m,source_subtype=s,source_side=ss,target_type=t,target_side=ts,hops=h,path_count=n) for (m,s,ss,t,ts,h),n in sorted(path_side_counts.items())])
    csvout(RUN/'gng021_end_to_end_path_counts.csv',[dict(source=a,target=b,hops=h,paths_through_gng021=n) for (a,b,h),n in sorted(via_candidate.items())],['source','target','hops','paths_through_gng021'])
    csvout(RUN/'named_overlap_path_counts.csv',[dict(sensory_subtype=s,intermediate_type=t,target=b,hops=h,path_count=n) for (s,t,b,h),n in sorted(via_named.items())],['sensory_subtype','intermediate_type','target','hops','path_count'])
    all_edges={};all_nodes={};growth=[]
    for h in range(1,H+1):
        for e,mask in edges_by_hop[h].items():all_edges[e]=all_edges.get(e,0)|mask
        for v,mask in nodes_by_hop[h].items():all_nodes[v]=all_nodes.get(v,0)|mask
        for circuit in 'ABCDE':
            growth.append(dict(circuit=circuit,max_hops=h,nodes=sum(circuit in membership(m).split('|') for m in all_nodes.values()),edges=sum(circuit in membership(m).split('|') for m in all_edges.values()),scope='exact union of all vertex-simple paths in this circuit query; E is two separately traced legs'))
    csvout(RUN/'bounded_circuit_growth.csv',growth)
    # Persist exact memberships for subsequent metadata/provenance exports.
    csvout(RUN/'analysis/path_edge_membership.csv',[dict(source=a,target=b,weight=pool[a,b],mask=m,minimum_path_hops=min(h for h in range(1,H+1) if (a,b) in edges_by_hop[h])) for (a,b),m in sorted(all_edges.items())])
    csvout(RUN/'analysis/path_node_membership.csv',[dict(body_id=v,mask=m,minimum_path_hops=min(h for h in range(1,H+1) if v in nodes_by_hop[h])) for v,m in sorted(all_nodes.items())])
    print('Final exact path graph',len(all_nodes),len(all_edges),flush=True)

if __name__=='__main__':main()
