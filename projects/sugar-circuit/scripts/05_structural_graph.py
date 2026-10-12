"""Deterministic structural graph preparation; no effective-connectivity model."""
from pathlib import Path
import csv, json, gc, time
import numpy as np
import pyarrow.feather as feather
from scipy.sparse import csr_matrix, save_npz, load_npz
from scipy.sparse.csgraph import dijkstra

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / (ROOT/'config/current_structural_run.txt').read_text().strip()
RAW = ROOT/'data/raw/connectome-weights-male-cns-v1.0-minconf-0.5.feather'
INF = np.iinfo(np.int16).max

def write_csv(path, rows, fields=None):
    rows=list(rows)
    with open(path,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)

def distances(graph, starts):
    d=dijkstra(graph, directed=True, indices=starts, unweighted=True, min_only=True)
    assert np.all(d[np.isfinite(d)] < INF)
    d[~np.isfinite(d)]=INF
    return d.astype(np.int16)

def main():
    start=time.time()
    if not (RUN/'analysis/graph.npz').exists():
        t=feather.read_table(RAW,memory_map=True)
        a=t['body_pre'].combine_chunks().to_numpy();b=t['body_post'].combine_chunks().to_numpy()
        w=t['weight'].combine_chunks().to_numpy()
        assert (w>0).all(), 'Nonpositive raw weights require review, not silent removal'
        print('Raw loaded',len(a),flush=True)
        ids=np.unique(np.concatenate((a,b)))
        print('All segment vertices',len(ids),'max weight',w.max(),flush=True)
        i=np.searchsorted(ids,a).astype(np.int32);j=np.searchsorted(ids,b).astype(np.int32)
        g=csr_matrix((w.astype(np.int32),(i,j)),shape=(len(ids),len(ids)))
        assert g.nnz==len(a), 'Duplicate body pairs must be investigated'
        summary=dict(raw_nodes=len(ids),raw_edges=len(a),synapse_sum=int(w.sum()),min_weight=int(w.min()),max_weight=int(w.max()),duplicate_pairs=0,zero_or_negative_weights=0,analysis_synapse_threshold=None,removed_nodes=0,removed_edges=0)
        (RUN/'analysis/graph_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
        np.save(RUN/'analysis/body_ids.npy',ids);save_npz(RUN/'analysis/graph.npz',g,compressed=False)
        del t,a,b,w,i,j;gc.collect()
        print('Graph saved',round(time.time()-start,1),flush=True)
    else:
        ids=np.load(RUN/'analysis/body_ids.npy');g=load_npz(RUN/'analysis/graph.npz')
    rev=g.T.tocsr()
    validated=list(csv.DictReader(open(ROOT/'results/validation/20261006T171922Z/resolved_bodies.csv')))
    groups={s:[int(r['body_id']) for r in validated if r['cell_type']==s] for s in ['LB3a','LB3b','LB3c','LB3d','GNG021']}
    groups['A']=sum((groups[s] for s in ['LB3a','LB3b','LB3c','LB3d']),[])
    groups['B']=groups['LB3b'];groups['C']=groups['LB3c'];groups['D']=groups['B']+groups['C']
    targets=[int(r['body_id']) for r in validated if r['cell_type'].startswith('MN')]
    (RUN/'analysis/groups.json').write_text(json.dumps(dict(groups=groups,targets=targets),indent=2)+'\n')
    reverse=[]
    for target in targets+groups['GNG021']:
        fn=RUN/f'analysis/distance_to_{target}.npy'
        if fn.exists():d=np.load(fn)
        else:
            d=distances(rev,[int(np.searchsorted(ids,target))]);np.save(fn,d)
        if target in targets:reverse.append(d)
        print('Reverse distances',target,'reachable',int((d<INF).sum()),flush=True)
    dm=np.minimum.reduce(reverse);np.save(RUN/'analysis/distance_to_any_motor.npy',dm)
    del reverse;gc.collect()
    # Prebound exploration: report depths 0..7; this is not a path enumeration bound.
    rows=[]
    for name, bodies in groups.items():
        fn=RUN/f'analysis/distance_from_{name}.npy'
        if fn.exists():d=np.load(fn)
        else:d=distances(g,np.searchsorted(ids,bodies));np.save(fn,d)
        print('Forward distances',name,'reachable',int((d<INF).sum()),flush=True)
        for depth in range(8):
            nodes=d<=depth
            # Count induced edges using CSR row batches, avoiding an E-size row-index array.
            induced=0;corr_edges=0
            for lo in range(0,len(ids),100000):
                hi=min(lo+100000,len(ids));ii=np.repeat(np.arange(lo,hi),np.diff(g.indptr[lo:hi+1]))
                jj=g.indices[g.indptr[lo]:g.indptr[hi]]
                induced+=int(np.count_nonzero(nodes[ii]&nodes[jj]))
                corr_edges+=int(np.count_nonzero(d[ii].astype(np.int32)+1+dm[jj]<=depth))
            row=dict(population=name,depth=depth,frontier_nodes=int((d==depth).sum()),cumulative_nodes=int(nodes.sum()),induced_edges=induced,outgoing_edges_from_reached=int(np.diff(g.indptr)[nodes].sum()),motor_corridor_nodes=int((d.astype(np.int32)+dm<=depth).sum()),motor_corridor_edges=corr_edges,scope='all released segments; directed unweighted distances; corridor may include bounded walks')
            rows.append(row)
            print(name,depth,row['cumulative_nodes'],induced,row['motor_corridor_nodes'],corr_edges,flush=True)
    write_csv(RUN/'graph_growth_by_depth.csv',rows)
    print('Exploration complete',round(time.time()-start,1),flush=True)

if __name__=='__main__':main()
