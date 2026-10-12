"""Add explicitly marked reciprocal/self-loop context and plan exact edge checks."""
from pathlib import Path
import csv,json,collections
import numpy as np
from scipy.sparse import load_npz
ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/(ROOT/'config/current_structural_run.txt').read_text().strip()
NAMES=['sensory_out','motor_in','named_out','gng021_in','additional_named_out']

def main():
    edges={}
    for r in csv.DictReader(open(RUN/'analysis/path_edge_membership.csv')):
        a,b,w,m,h=(int(r[x]) for x in ['source','target','weight','mask','minimum_path_hops'])
        edges[a,b]=dict(weight=w,path_mask=m,minimum_path_hops=h,reciprocal_context=False,self_loop=False,context_mask=0,query_names=[],weightHP=None,weightHR=None)
    nodes={int(r['body_id']):int(r['mask']) for r in csv.DictReader(open(RUN/'analysis/path_node_membership.csv'))}
    ids=np.load(RUN/'analysis/body_ids.npy',mmap_mode='r');g=load_npz(RUN/'analysis/graph.npz')
    pairs=list(edges);aa=np.searchsorted(ids,[e[0] for e in pairs]);bb=np.searchsorted(ids,[e[1] for e in pairs]);back=np.asarray(g[bb,aa]).ravel()
    def newedge(a,b,w):
        if (a,b) not in edges:edges[a,b]=dict(weight=int(w),path_mask=0,minimum_path_hops=None,reciprocal_context=False,self_loop=False,context_mask=0,query_names=[],weightHP=None,weightHR=None)
        assert edges[a,b]['weight']==w
        return edges[a,b]
    for (a,b),w in zip(pairs,back):
        if w:
            e=newedge(b,a,w);e['reciprocal_context']=True;e['context_mask']|=edges[a,b]['path_mask']
    vv=sorted(nodes);ii=np.searchsorted(ids,vv);loops=np.asarray(g[ii,ii]).ravel()
    for v,w in zip(vv,loops):
        if w:
            e=newedge(v,v,w);e['self_loop']=True;e['context_mask']|=nodes[v]
    for name in NAMES:
        q=json.loads((RUN/'raw'/f'{name}.json').read_text())
        for a,b,w,hp,hr in q['data']:
            e=newedge(a,b,w);e['query_names'].append(name);e['weightHP']=hp;e['weightHR']=hr
    rows=[dict(source=a,target=b,**r) for (a,b),r in sorted(edges.items())]
    with open(RUN/'analysis/export_edges.jsonl','w') as f:
        for r in rows:f.write(json.dumps(r)+'\n')
    needed=[r for r in rows if not r['query_names']]
    plans=[]
    for offset in range(0,len(needed),5000):
        batch=needed[offset:offset+5000];group=collections.defaultdict(list)
        for r in batch:group[r['source']].append(r['target'])
        spec='['+','.join('{source:'+str(a)+',targets:'+json.dumps(bs,separators=(',',':'))+'}' for a,bs in group.items())+']'
        name=f'graph_edges_{offset//5000:03d}'
        q={'dataset':'male-cns:v1.0','cypher':f'UNWIND {spec} AS row MATCH (a:Segment {{bodyId: row.source}})-[e:ConnectsTo]->(b:Segment) WHERE b.bodyId IN row.targets RETURN a.bodyId AS source, b.bodyId AS target, e.weight AS weight, e.weightHP AS weightHP, e.weightHR AS weightHR ORDER BY source, target'}
        (RUN/'queries'/f'{name}.json').write_text(json.dumps(q)+'\n');plans.append(dict(name=name,expected_rows=len(batch)))
        for r in batch:r['planned_query']=name
    (RUN/'queries/graph_validation_plan.json').write_text(json.dumps(plans,indent=2)+'\n')
    conf=[]
    for k,p in enumerate(plans):
        name=p['name']
        if k:conf.append('next')
        conf+=['config = ".venv/.neuprint-auth.curl"','url = "https://neuprint.janelia.org/api/custom/custom"','header = "Content-Type: application/json"','data-binary = "@'+str((RUN/'queries'/f'{name}.json').relative_to(ROOT))+'"','output = "'+str((RUN/'raw'/f'{name}.json').relative_to(ROOT))+'"','max-time = 180','silent','show-error','write-out = "%{http_code} %{filename_effective}\\n"']
    (RUN/'queries/graph_validation.curl').write_text('\n'.join(conf)+'\n')
    print('Export edges',len(edges),'path edges',len(pairs),'new validation edges',len(needed),'batches',len(plans),flush=True)

if __name__=='__main__':main()
