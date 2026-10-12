"""Descriptive topology summaries; no inference of functional influence."""
from pathlib import Path
import csv,json,collections
ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/(ROOT/'config/current_structural_run.txt').read_text().strip()

def read(name):return list(csv.DictReader(open(RUN/name)))
def save(name,rows,fields=None):
    rows=list(rows)
    with open(RUN/name,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    nodes={int(r['body_id']):r for r in read('nodes.csv')}
    edges={(int(r['source']),int(r['target'])):r for r in read('raw_edges.csv')}
    pairs=collections.defaultdict(set);pairtypes=collections.defaultdict(set)
    for r in read('shortest_paths.csv'):
        if r['analysis']!='sensory_to_motor':continue
        path=json.loads(r['body_ids'])
        for v in path[1:-1]:
            pairs[v].add((r['source'],r['target']));pairtypes[v].add(r['source_type'])
    important=[]
    for v,ps in sorted(pairs.items(),key=lambda x:(-len(x[1]),x[0])):
        n=nodes[v]
        important.append(dict(body_id=v,type=n['type'],side=n['side'],classification=n['classification'],annotation_present=n['annotation_present'],sensory_motor_pairs_with_this_shortest_intermediate=len(ps),sensory_subtypes='|'.join(sorted(pairtypes[v])),predicted_neurotransmitter=n['predicted_neurotransmitter'],consensus_nt=n['consensus_nt'],named_in_inspected_paper_panels=n['named_in_inspected_paper_panels'],provenance='shortest_paths.csv; source_target_reachability.csv; nodes.csv',interpretation='Descriptive shortest-path occurrence, not functional importance'))
    save('important_intermediates.csv',important)
    reciprocal=[]
    for (a,b),r in sorted(edges.items()):
        if a<b and (b,a) in edges:
            reciprocal.append(dict(body_a=a,type_a=nodes[a]['type'],side_a=nodes[a]['side'],body_b=b,type_b=nodes[b]['type'],side_b=nodes[b]['side'],a_to_b_weight=r['weight'],b_to_a_weight=edges[b,a]['weight'],a_to_b_circuits=r['circuit_membership'],b_to_a_circuits=edges[b,a]['circuit_membership'],provenance='raw_edges.csv keyed by both directed body pairs'))
    save('reciprocal_pairs.csv',reciprocal)
    gr=json.loads((RUN/'analysis/groups.json').read_text());candidates=gr['groups']['GNG021'];adj=collections.defaultdict(dict)
    for (a,b),r in edges.items():adj[a][b]=int(r['weight'])
    triangles=[]
    for v in candidates:
        upstream={a for a,b in edges if b==v}
        for a,w1 in adj[v].items():
            if a==v:continue
            for b,w2 in adj[a].items():
                if b!=a and b!=v and b in upstream:triangles.append(dict(candidate_body=v,second_body=a,second_type=nodes[a]['type'],third_body=b,third_type=nodes[b]['type'],weight_1=w1,weight_2=w2,weight_3=adj[b][v],scope='All length-3 simple cycles around GNG021 in the exported graph; longer/full-universe cycles not enumerated',provenance='raw_edges.csv: candidate->second; second->third; third->candidate'))
    save('gng021_three_edge_cycles.csv',triangles,['candidate_body','second_body','second_type','third_body','third_type','weight_1','weight_2','weight_3','scope','provenance'])
    conv=read('convergence_divergence.csv');cv={(r['circuit'],int(r['body_id'])):r for r in conv};newconv=[]
    for r in conv:
        v=int(r['body_id'])
        if r['circuit']=='D' and int(r['in_degree'])>1 and int(cv.get(('B',v),{}).get('in_degree',0))<=1 and int(cv.get(('C',v),{}).get('in_degree',0))<=1:newconv.append(r)
    save('combined_only_convergence_motifs.csv',newconv,list(conv[0]))
    endpoints=set(gr['groups']['A']+gr['targets']);origin=[]
    for st in ('LB3a','LB3b','LB3c','LB3d'):
        ns=[n for n in nodes.values() if st in n['source_subtype_membership'].split('|')];es=[r for r in edges.values() if st in r['source_subtype_membership'].split('|')]
        origin.append(dict(sensory_subtype=st,starting_bodies=len(gr['groups'][st]),nodes=len(ns),non_endpoint_intermediate_segments=sum(int(n['body_id']) not in endpoints for n in ns),edges=len(es),nodes_unique_within_all_LB3=sum(n['source_subtype_membership']==st for n in ns),edges_unique_within_all_LB3=sum(r['source_subtype_membership']==st for r in es),bound_hops=4,provenance='nodes.csv; raw_edges.csv; exact all-path membership'))
    save('full_lb3_component_origins.csv',origin)
    counts=[]
    for c in 'ABCDE':
        ns=[n for n in nodes.values() if c in n['circuit_membership'].split('|')];es=[r for r in edges.values() if c in r['circuit_membership'].split('|')]
        counts.append(dict(circuit=c,nodes=len(ns),non_endpoint_intermediate_segments=sum(int(n['body_id']) not in endpoints for n in ns),edges=len(es),edges_of_weight_one=sum(int(r['weight'])==1 for r in es),unannotated_nodes=sum(n['annotation_present']=='False' for n in ns),opposite_side_edges=sum(r['side_relationship']=='opposite_side_endpoints' for r in es),unknown_side_edges=sum(r['side_relationship']=='unknown' for r in es),recurrent_edges_within_circuit=sum(c in r['recurrent_circuits'].split('|') for r in es),convergence_nodes=sum(r['circuit']==c and r['convergence']=='True' for r in conv),divergence_nodes=sum(r['circuit']==c and r['divergence']=='True' for r in conv),largest_scc=max([int(r['scc_size']) for r in conv if r['circuit']==c],default=0),bound_hops=4))
    save('circuit_summary.csv',counts)
    groups={'shared':set(),'LB3b_only':set(),'LB3c_only':set()}
    for v,n in nodes.items():
        if n['bc_comparison'] in groups and v not in endpoints:groups[n['bc_comparison']].add(v)
    summary={'non_endpoint_intermediate_comparison':{k:len(v) for k,v in groups.items()},'combined_only_convergence_nodes':len(newconv),'gng021_triangles_in_export':len(triangles),'reciprocal_pairs_in_export':len(reciprocal),'ranked_intermediate_bodies':len(important),'additional_summary_scope':'Static topology only; subtype membership refers to A-D sensory-to-motor paths; E is two separately bounded legs.'}
    (RUN/'supplemental_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2));print('Top shortest intermediates',important[:12]);print('Circuit summaries',counts)

if __name__=='__main__':main()
