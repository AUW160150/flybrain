"""Join annotations, cross-check raw edges, and export structural-only graph tables."""
from pathlib import Path
import csv,json,collections,hashlib,datetime
from xml.sax.saxutils import escape,quoteattr
import numpy as np
import pyarrow as pa
import pyarrow.feather as ft
import pyarrow.compute as pc
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/(ROOT/'config/current_structural_run.txt').read_text().strip()
DATASET='male-cns:v1.0';UUID='4b2087c0fbe046bfaf0d60bc970e3e5d'
PAPER=[('GNG042','GNG015',329),('GNG015','MN9',473),('GNG015','MN4a',188),('ANXXX462a','GNG585',179),('GNG585','GNG108',835),('GNG585','GNG120',359),('GNG108','MN9',376),('GNG108','MN4a',98),('GNG120','MN9',441),('GNG120','MN4a',89),('GNG585','GNG472',244),('GNG472','MN8',205)]
NAMED={'GNG042','ANXXX462a','GNG015','GNG021','GNG108','GNG120','GNG585','GNG472'}

def csvout(path,rows,fields=None):
    rows=list(rows)
    with open(path,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)

def circuits(mask):
    return '|'.join(c for c,test in [('A',mask&15),('B',mask&2),('C',mask&4),('D',mask&6),('E',mask&16)] if test)

def subtypes(mask):return '|'.join(s for i,s in enumerate(['LB3a','LB3b','LB3c','LB3d']) if mask&(1<<i))

def classification(superclass,cell_type):
    """Display grouping derived from supplied superclass; preserve original field."""
    sc=superclass or ''
    if sc.endswith('_tbc'):return 'uncertain_annotated_class'
    if '_sensory' in sc or sc.startswith('sensory_') or cell_type.startswith('LB3'):return 'sensory'
    if sc.endswith('_motor') or cell_type in ['MN4a','MN6','MN8','MN9']:return 'motor'
    if sc.endswith('_intrinsic') or sc in ['ascending_neuron','descending_neuron','visual_projection','visual_centrifugal']:return 'interneuron_or_projection_neuron'
    if sc.endswith('_endocrine'):return 'endocrine_neuron'
    return 'other_annotated_neuron' if sc else 'unclassified'

def scc(vs,pairs):
    lookup={v:i for i,v in enumerate(vs)}
    rows=[lookup[a] for a,b in pairs];cols=[lookup[b] for a,b in pairs]
    graph=csr_matrix((np.ones(len(rows),dtype=np.bool_),(rows,cols)),shape=(len(vs),len(vs)))
    _,lab=connected_components(graph,directed=True,connection='strong');sizes=np.bincount(lab)
    return {v:int(lab[i]) for i,v in enumerate(vs)},sizes

def graphml(path,nodes,edges):
    nk=['body_id','type','instance','synonyms','side','side_source','sensory_subtype','classification','predicted_neurotransmitter','consensus_nt','circuit_membership','source_subtype_membership','named_in_inspected_paper_panels','discovered_structurally','bc_comparison','annotation_present']
    ek=['source','target','weight','side_relationship','circuit_membership','context_circuit_membership','source_subtype_membership','recurrence_status','recurrent_circuits','reciprocal_context','known_paper_motif','query_provenance','verification_status']
    with open(path,'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<graphml xmlns="http://graphml.graphdrawing.org/xmlns">\n')
        for kind,keys in [('node',nk),('edge',ek)]:
            for key in keys:f.write(f'<key id="{kind}_{key}" for="{kind}" attr.name="{key}" attr.type="'+('long' if key=='weight' else 'string')+'"/>\n')
        f.write('<graph id="STRUCTURAL_CONNECTIVITY_ONLY" edgedefault="directed">\n')
        for row in nodes:
            f.write('<node id="'+str(row['body_id'])+'">')
            for k in nk:f.write('<data key="node_'+k+'">'+escape(str(row.get(k,'')))+'</data>')
            f.write('</node>\n')
        for i,row in enumerate(edges):
            f.write(f'<edge id="e{i}" source="{row["source"]}" target="{row["target"]}">')
            for k in ek:f.write('<data key="edge_'+k+'">'+escape(str(row.get(k,'')))+'</data>')
            f.write('</edge>\n')
        f.write('</graph></graphml>\n')

def main():
    edges={(r['source'],r['target']):r for r in map(json.loads,(RUN/'analysis/export_edges.jsonl').read_text().splitlines())}
    plans=json.loads((RUN/'queries/graph_validation_plan.json').read_text());checks=[]
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    logged={r.get('output_file') for r in map(json.loads,(ROOT/'logs/query_log.jsonl').read_text().splitlines())}
    with open(ROOT/'logs/query_log.jsonl','a') as log:
        for plan in plans:
            name=plan['name'];path=RUN/'raw'/f'{name}.json';q=json.loads(path.read_text());assert 'data' in q,q
            assert len(q['data'])==plan['expected_rows'], (name,len(q['data']),plan['expected_rows'])
            for a,b,w,hp,hr in q['data']:
                e=edges[a,b];match=e['weight']==w
                checks.append(dict(source=a,target=b,flat_weight=e['weight'],neuprint_weight=w,status='VERIFIED' if match else 'SOURCE CONFLICT',query=name))
                e['query_names'].append(name);e['weightHP']=hp;e['weightHR']=hr
            if str(path.relative_to(ROOT)) not in logged:
                log.write(json.dumps(dict(timestamp=now,timestamp_note='Recorded during local response validation; response file mtime is retrieval completion proxy',experiment='GATES_2_3_STRUCTURAL_ONLY',purpose='Cross-check all exported path and reciprocal-context edges not already independently retrieved',dataset=DATASET,query_file=str((RUN/'queries'/f'{name}.json').relative_to(ROOT)),query_sha256=hashlib.file_digest((RUN/'queries'/f'{name}.json').open('rb'),'sha256').hexdigest(),parameters={'requested_body_pairs':plan['expected_rows'],'synapse_count_threshold':None},returned_row_count=len(q['data']),output_file=str(path.relative_to(ROOT)),sha256=hashlib.file_digest(path.open('rb'),'sha256').hexdigest(),authentication='user-provided token; value omitted',http_status=200,errors=None))+'\n')
    csvout(RUN/'path_edge_source_comparison.csv',checks)
    assert all(x['status']=='VERIFIED' for x in checks),'Investigate source conflicts before reporting validation'
    assert all(e['query_names'] for e in edges.values()),'Every exported edge must have live query provenance'
    node_masks={int(r['body_id']):int(r['mask']) for r in csv.DictReader(open(RUN/'analysis/path_node_membership.csv'))}
    vs=sorted({v for pair in edges for v in pair})
    annotations=ft.read_table(ROOT/'data/raw/body-annotations-male-cns-v1.0-minconf-0.5.feather')
    ann={r['bodyId']:r for r in annotations.filter(pc.is_in(annotations['bodyId'],value_set=pa.array(vs))).to_pylist()}
    nt=ft.read_table(ROOT/'data/raw/body-neurotransmitters-male-cns-v1.0.feather')
    nt={r['body']:r for r in nt.filter(pc.is_in(nt['body'],value_set=pa.array(vs))).to_pylist()}
    glabel,gsizes=scc(vs,list(edges))
    clabel={};csizes={}
    for c in 'ABCDE':
        ns=sorted(v for v,m in node_masks.items() if c in circuits(m));es=[e for e,r in edges.items() if c in circuits(r['path_mask'])]
        clabel[c],csizes[c]=scc(ns,es)
    def node(v):
        a=ann.get(v,{});n=nt.get(v,{});m=node_masks.get(v,0);t=a.get('type') or '';side=a.get('somaSide') or a.get('rootSide') or 'unknown';source='somaSide' if a.get('somaSide') else 'rootSide' if a.get('rootSide') else 'missing'
        return dict(body_id=v,type=t,instance=a.get('instance') or '',synonyms=a.get('synonyms') or '',annotation=json.dumps(a,separators=(',',':')),annotation_present=v in ann,side=side,side_source=source,soma_side=a.get('somaSide') or '',root_side=a.get('rootSide') or '',sensory_subtype=t if t.startswith('LB3') else '',classification=classification(a.get('superclass'),t),superclass=a.get('superclass') or '',cell_class=a.get('class') or '',status=a.get('status') or '',status_label=a.get('statusLabel') or '',entry_nerve=a.get('entryNerve') or '',exit_nerve=a.get('exitNerve') or '',predicted_neurotransmitter=n.get('predicted_nt') or '',predicted_nt_confidence=n.get('predicted_nt_confidence'),total_nt_predictions=n.get('total_nt_predictions'),ground_truth=n.get('ground_truth') or '',celltype_predicted_nt=n.get('celltype_predicted_nt') or '',celltype_predicted_nt_confidence=n.get('celltype_predicted_nt_confidence'),consensus_nt=n.get('consensus_nt') or '',circuit_membership=circuits(m),source_subtype_membership=subtypes(m),named_in_inspected_paper_panels=t in NAMED-{'GNG021'} or t.startswith('LB3') or t in ['MN4a','MN6','MN8','MN9'],discovered_structurally=t not in NAMED and not t.startswith('LB3') and t not in ['MN4a','MN6','MN8','MN9'],candidate_under_test=t=='GNG021',bc_comparison='shared' if m&2 and m&4 else 'LB3b_only' if m&2 else 'LB3c_only' if m&4 else 'outside_B_C',scc_export_graph=glabel[v],scc_export_graph_size=int(gsizes[glabel[v]]),dataset=DATASET,dataset_uuid=UUID,annotation_provenance='data/raw/body-annotations-male-cns-v1.0-minconf-0.5.feather',nt_provenance='data/raw/body-neurotransmitters-male-cns-v1.0.feather',evidence='STRUCTURAL CONNECTIVITY ONLY; neurotransmitters are supplied predictions/consensus')
    nodes={v:node(v) for v in vs};csvout(RUN/'nodes.csv',nodes.values())
    paperpairs={(a,b) for a,b,_ in PAPER};out=[]
    for (a,b),e in sorted(edges.items()):
        na,nb=nodes[a],nodes[b];sa,sb=na['side'],nb['side'];rec=glabel[a]==glabel[b] and (a==b or gsizes[glabel[a]]>1)
        rc=[]
        for c in circuits(e['path_mask']).split('|'):
            if c and clabel[c][a]==clabel[c][b] and (a==b or csizes[c][clabel[c][a]]>1):rc.append(c)
        m=e['path_mask']
        out.append(dict(source=a,source_type=na['type'],source_name=na['instance'],source_side=sa,target=b,target_type=nb['type'],target_name=nb['instance'],target_side=sb,direction='source_to_target',weight=e['weight'],neuprint_weightHP=e['weightHP'],neuprint_weightHR=e['weightHR'],source_predicted_neurotransmitter=na['predicted_neurotransmitter'],source_nt_confidence=na['predicted_nt_confidence'],source_consensus_nt=na['consensus_nt'],target_predicted_neurotransmitter=nb['predicted_neurotransmitter'],target_consensus_nt=nb['consensus_nt'],side_relationship='ipsilateral_endpoints' if sa==sb and sa in ('L','R') else 'opposite_side_endpoints' if sa in ('L','R') and sb in ('L','R') else 'unknown',anatomical_midline_crossing='UNVERIFIED; soma/root side is not synapse location',recurrence_status='cycle_in_export_graph' if rec else 'not_in_cycle_in_export_graph',recurrent_circuits='|'.join(rc),reciprocal_context=e['reciprocal_context'],self_loop=a==b,circuit_membership=circuits(m),context_circuit_membership=circuits(e['context_mask']),source_subtype_membership=subtypes(m),minimum_bounded_path_hops=e['minimum_path_hops'],bc_comparison='shared' if m&2 and m&4 else 'LB3b_only' if m&2 else 'LB3c_only' if m&4 else 'outside_B_C',known_paper_motif=(na['type'],nb['type']) in paperpairs,raw_scope='bounded_path' if m else 'reciprocal_or_self_loop_context' if e['context_mask'] else 'unfiltered_targeted_query_context',query_provenance='|'.join('raw/'+q+'.json' for q in e['query_names']),flat_provenance='data/raw/connectome-weights-male-cns-v1.0-minconf-0.5.feather',dataset=DATASET,dataset_uuid=UUID,verification_status='VERIFIED',evidence='STRUCTURAL CONNECTIVITY ONLY'))
    csvout(RUN/'raw_edges.csv',out);csvout(RUN/'recurrent_edges.csv',[r for r in out if r['recurrence_status']=='cycle_in_export_graph'])
    clean=[r for r in out if r['circuit_membership'] or r['context_circuit_membership'] or r['known_paper_motif']]
    cleanids={v for r in clean for v in [r['source'],r['target']]};cleannodes=[nodes[v] for v in sorted(cleanids)]
    csvout(RUN/'visualization_nodes.csv',cleannodes);csvout(RUN/'visualization_edges.csv',clean);graphml(RUN/'circuit_graph.graphml',cleannodes,clean)
    # Direct named-neuron matrix includes explicit tested absences, not invented zero-weight edges.
    gr=json.loads((RUN/'analysis/groups.json').read_text());motors=gr['targets'];sources=gr['groups']['A'];named=[v for v,r in nodes.items() if r['type'] in NAMED]
    sourcenames={}
    for name in ['sensory_out','named_out','additional_named_out']:
        for a,*_ in json.loads((RUN/'raw'/f'{name}.json').read_text())['data']:sourcenames[a]=name
    matrix=[]
    for a,targets in [(a,named+motors) for a in named]+[(a,named) for a in sources]:
        for b in targets:
            e=edges.get((a,b));na,nb=nodes[a],nodes[b]
            matrix.append(dict(source=a,source_type=na['type'],source_side=na['side'],target=b,target_type=nb['type'],target_side=nb['side'],present=e is not None,weight=e['weight'] if e else 0,source_predicted_neurotransmitter=na['predicted_neurotransmitter'],source_consensus_nt=na['consensus_nt'],verification_status='VERIFIED',known_paper_motif=(na['type'],nb['type']) in paperpairs,provenance='raw/'+sourcenames[a]+'.json; raw/targeted_flat_edges_unfiltered.csv',absence_meaning='No ConnectsTo record in complete outgoing query and full released flat graph' if e is None else ''))
    csvout(RUN/'named_neuron_edge_validation.csv',matrix)
    comparisons=[]
    for a,b,fig in PAPER:
        rows=[r for r in matrix if r['source_type']==a and r['target_type']==b];total=sum(r['weight'] for r in rows)
        comparisons.append(dict(source_type=a,target_type=b,paper_figure6_label=fig,current_all_body_sum=total,difference=total-fig,status='VERIFIED' if total==fig else 'SOURCE CONFLICT',raw_edges_present=sum(r['present'] for r in rows),tested_body_pairs=len(rows),paper_source='paper/primary/figure6.jpg panel I or J',raw_source='named_neuron_edge_validation.csv',interpretation='Descriptive comparison only; paper pooling and snapshot unresolved; equality does not establish strict replication'))
    csvout(RUN/'paper_motif_comparison.csv',comparisons)
    # All two-edge Quasimodo -> intermediate -> MN8 bridges, without assigning the unresolved Puddle name.
    bridges=[]
    quasi=[v for v in named if nodes[v]['type']=='GNG042'];mn8=[v for v in motors if nodes[v]['type']=='MN8']
    for a in quasi:
        for (u,v),e in edges.items():
            if u!=a:continue
            for b in mn8:
                if (v,b) in edges:bridges.append(dict(source=a,intermediate=v,intermediate_type=nodes[v]['type'],intermediate_side=nodes[v]['side'],target=b,first_weight=e['weight'],second_weight=edges[v,b]['weight'],puddle_identity='UNVERIFIED; do not assign Puddle from topology',provenance='raw/named_out.json; raw/motor_in.json'))
    csvout(RUN/'quasimodo_mn8_unassigned_bridges.csv',bridges)
    candidate=gr['groups']['GNG021'];partners=[]
    for v in candidate:
        for direction in ['upstream','downstream']:
            relevant=[r for r in out if (r['target'] if direction=='upstream' else r['source'])==v]
            for rank,r in enumerate(sorted(relevant,key=lambda x:(-x['weight'],x['source'],x['target'])),1):
                u=r['source'] if direction=='upstream' else r['target'];n=nodes[u]
                partners.append(dict(candidate_body=v,candidate_side=nodes[v]['side'],direction=direction,raw_weight_rank=rank,partner_body=u,partner_type=n['type'],partner_side=n['side'],weight=r['weight'],partner_predicted_neurotransmitter=n['predicted_neurotransmitter'],partner_consensus_nt=n['consensus_nt'],partner_circuits=n['circuit_membership'],partner_lb3_subtype_membership=n['source_subtype_membership'],reciprocal=(u,v) in edges and (v,u) in edges,provenance=r['query_provenance']))
    csvout(RUN/'gng021_partners.csv',partners)
    # Compare exact path unions, independently of saved path-example caps.
    nB={v for v,m in node_masks.items() if m&2};nC={v for v,m in node_masks.items() if m&4};nD={v for v,m in node_masks.items() if m&6}
    eB={e for e,r in edges.items() if r['path_mask']&2};eC={e for e,r in edges.items() if r['path_mask']&4};eD={e for e,r in edges.items() if r['path_mask']&6}
    assert nD==nB|nC and eD==eB|eC
    summary=dict(nodes_shared=len(nB&nC),nodes_LB3b_only=len(nB-nC),nodes_LB3c_only=len(nC-nB),nodes_combined_only=len(nD-(nB|nC)),edges_shared=len(eB&eC),edges_LB3b_only=len(eB-eC),edges_LB3c_only=len(eC-eB),edges_combined_only=len(eD-(eB|eC)),interpretation='Static directed paths from a union of source sets equal the union of the separate source paths at identical bounds. There are no combined-only routes under this definition; convergence is present but is not functional synergy.')
    (RUN/'structural_comparison_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    csvout(RUN/'structural_node_comparison.csv',[dict(body_id=v,type=nodes[v]['type'],side=nodes[v]['side'],classification=nodes[v]['classification'],comparison=nodes[v]['bc_comparison'],source_subtypes=nodes[v]['source_subtype_membership']) for v in sorted(nD)])
    shared_edges=eB&eC
    csvout(RUN/'structural_edge_comparison.csv',[dict(source=a,target=b,comparison='shared' if (a,b) in shared_edges else 'LB3b_only' if (a,b) in eB else 'LB3c_only',weight=edges[a,b]['weight']) for a,b in sorted(eD)])
    degrees={c:dict(ins=collections.defaultdict(set),outs=collections.defaultdict(set)) for c in 'ABCDE'}
    for (a,b),r in edges.items():
        for c in circuits(r['path_mask']).split('|'):
            if c:degrees[c]['outs'][a].add(b);degrees[c]['ins'][b].add(a)
    convergence=[]
    for c,ds in degrees.items():
        for v in sorted(set(ds['ins'])|set(ds['outs'])):
            ins,outs=ds['ins'][v],ds['outs'][v];ib={a for a in ins if edges[a,v]['path_mask']&2};ic={a for a in ins if edges[a,v]['path_mask']&4}
            convergence.append(dict(circuit=c,body_id=v,type=nodes[v]['type'],side=nodes[v]['side'],in_degree=len(ins),out_degree=len(outs),convergence=len(ins)>1,divergence=len(outs)>1,LB3b_supported_incoming=len(ib),LB3c_supported_incoming=len(ic),bc_shared_reachable_node=bool(node_masks.get(v,0)&2 and node_masks.get(v,0)&4),bc_distinct_incoming_branches=bool(ib and ic and len(ib|ic)>1),source_subtypes=nodes[v]['source_subtype_membership'],scc=clabel[c][v],scc_size=int(csizes[c][clabel[c][v]]),scope='exact bounded simple-path union; convergence/divergence are topological'))
    csvout(RUN/'convergence_divergence.csv',convergence)
    # Per-body side combinations and bilateral summaries use exact path counts, not CSV samples.
    reach=list(csv.DictReader(open(RUN/'source_target_reachability.csv')));lr=collections.defaultdict(list)
    for r in reach:lr[r['analysis'],r['source_type'],r['source_side'],r['target_type'],r['target_side']].append(r)
    lrrows=[]
    for (mode,st,ss,tt,ts),rs in sorted(lr.items()):
        ds=[int(r['shortest_hops']) for r in rs if r['reachable']=='True']
        lrrows.append(dict(analysis=mode,source_type=st,source_side=ss,target_type=tt,target_side=ts,endpoint_laterality='ipsilateral' if ss==ts else 'contralateral',body_pairs=len(rs),reachable_pairs=len(ds),shortest_hops_min=min(ds) if ds else '',shortest_hops_max=max(ds) if ds else '',direct_edge_count=sum(int(r['direct_synapse_count'])>0 for r in rs),direct_synapse_sum=sum(int(r['direct_synapse_count']) for r in rs),**{f'simple_paths_h{h}':sum(int(r[f'simple_paths_h{h}']) for r in rs) for h in range(1,5)},interpretation='Unequal sensory body counts retained; raw path-count asymmetry is not normalized or a statistical test'))
    csvout(RUN/'left_right_comparison.csv',lrrows)
    full=json.loads((RUN/'analysis/graph_summary.json').read_text())
    scope=dict(full_released_graph_nodes=full['raw_nodes'],full_released_graph_edges=full['raw_edges'],raw_export_nodes=len(nodes),raw_export_edges=len(edges),nodes_outside_raw_export=full['raw_nodes']-len(nodes),edges_outside_raw_export=full['raw_edges']-len(edges),visualization_nodes=len(cleannodes),visualization_edges=len(clean),raw_context_nodes_omitted_from_visualization=len(nodes)-len(cleannodes),raw_context_edges_omitted_from_visualization=len(edges)-len(clean),threshold_removed_nodes=0,threshold_removed_edges=0,selection='Raw export = all targeted boundary queries + exact bounded path union + reciprocal and self-loop context. Visualization = path union + reciprocal/self-loop context + named paper-motif edges. Full unfiltered source retained separately. Unbounded full-graph distances computed before extraction.',dataset=DATASET,uuid=UUID,query_comparisons_additional=len(checks),query_disagreements_additional=0,cycle_edges_export=sum(r['recurrence_status']=='cycle_in_export_graph' for r in out),reciprocal_directed_edges_export=sum((b,a) in edges for a,b in edges),self_loops_export=sum(a==b for a,b in edges),annotation_missing_raw_export=sum(not r['annotation_present'] for r in nodes.values()),annotation_missing_visualization=sum(not r['annotation_present'] for r in cleannodes),opposite_side_edges_raw=sum(r['side_relationship']=='opposite_side_endpoints' for r in out),unknown_side_edges_raw=sum(r['side_relationship']=='unknown' for r in out),anatomical_midline_crossing='UNVERIFIED; requires synapse locations or morphology')
    (RUN/'export_summary.json').write_text(json.dumps(scope,indent=2)+'\n')
    (RUN/'visualization_views.json').write_text(json.dumps({'label':'STRUCTURAL CONNECTIVITY ONLY','graph':'circuit_graph.graphml','views':{**{c:{'edges':'circuit_membership contains '+c,'feedback_context':'context_circuit_membership contains '+c,'bound':4,'definition':'sensory sources to motors' if c!='E' else 'union of LB3-to-GNG021 and GNG021-to-motor paths, each <=4 hops; not an 8-hop end-to-end enumeration'} for c in 'ABCDE'},'paper_associated':{'edges':'known_paper_motif == True','puddle':'identity unresolved; excluded as a named identity','additional_file':'quasimodo_mn8_unassigned_bridges.csv'}},'node_key':'body_id','edge_key':['source','target'],'raw_weight':'weight; no normalization','laterality':'soma/root endpoint labels; anatomical crossing unverified','prediction_fields':['predicted_neurotransmitter','consensus_nt'],'example_paths':'Capped; membership and counts exhaustive within bounds'},indent=2)+'\n')
    print(json.dumps(scope,indent=2),flush=True);print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':main()
