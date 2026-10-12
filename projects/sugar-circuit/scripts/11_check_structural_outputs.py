"""Validate exported path witnesses, side metadata, graph schema, and counts."""
from pathlib import Path
import csv,json,collections,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/(ROOT/'config/current_structural_run.txt').read_text().strip()

def main():
    required=['nodes.csv','raw_edges.csv','source_target_reachability.csv','shortest_paths.csv','simple_paths.csv','recurrent_edges.csv','left_right_comparison.csv','lb3b_paths.csv','lb3c_paths.csv','lb3b_lb3c_combined_paths.csv','gng021_candidate_paths.csv','named_neuron_edge_validation.csv','circuit_graph.graphml']
    assert all((RUN/n).stat().st_size>0 for n in required)
    nodes={int(r['body_id']):r for r in csv.DictReader(open(RUN/'nodes.csv'))};weights={}
    for r in csv.DictReader(open(RUN/'raw_edges.csv')):
        e=int(r['source']),int(r['target']);assert e not in weights;weights[e]=int(r['weight'])
        assert all(v in nodes for v in e) and weights[e]>0 and r['query_provenance'] and r['verification_status']=='VERIFIED'
        assert r['source_side']==nodes[e[0]]['side'] and r['target_side']==nodes[e[1]]['side']
        assert r['source_predicted_neurotransmitter']==nodes[e[0]]['predicted_neurotransmitter']
        assert r['source_consensus_nt']==nodes[e[0]]['consensus_nt']
    reach={(r['analysis'],int(r['source']),int(r['target'])):r for r in csv.DictReader(open(RUN/'source_target_reachability.csv'))}
    path_counts=collections.Counter();short_counts=collections.Counter();example_ids={};totals={}
    names=['simple_paths','shortest_paths','lb3b_paths','lb3c_paths','lb3b_lb3c_combined_paths','gng021_candidate_paths']
    for name in names:
        ids=set();n=0
        for r in csv.DictReader(open(RUN/f'{name}.csv')):
            p=json.loads(r['body_ids']);w=json.loads(r['edge_synapse_counts']);s=json.loads(r['sides']);h=int(r['hops']);key=(r['analysis'],int(r['source']),int(r['target']))
            assert len(p)==len(set(p)) and len(p)==h+1 and h<=4 and p[0]==key[1] and p[-1]==key[2]
            assert w==[weights[e] for e in zip(p,p[1:])]
            assert s==[nodes[v]['side'] for v in p]
            assert (r['is_shortest']=='True')==(h==int(reach[key]['shortest_hops']))
            assert r['path_id'] not in ids;ids.add(r['path_id']);n+=1
            if name=='simple_paths':path_counts[key+(h,)]+=1
            if name=='shortest_paths':short_counts[key]+=1
            if name=='lb3b_paths':assert r['source_type']=='LB3b' and r['analysis']=='sensory_to_motor'
            if name=='lb3c_paths':assert r['source_type']=='LB3c' and r['analysis']=='sensory_to_motor'
            if name=='lb3b_lb3c_combined_paths':assert r['source_type'] in ('LB3b','LB3c') and r['analysis']=='sensory_to_motor'
        example_ids[name]=ids;totals[name]=n
    assert example_ids['lb3b_lb3c_combined_paths']==example_ids['lb3b_paths']|example_ids['lb3c_paths']
    for r in csv.DictReader(open(RUN/'path_enumeration_counts.csv')):
        key=(r['analysis'],int(r['source']),int(r['target']),int(r['hops']))
        assert path_counts[key]==int(r['saved_simple_paths'])==min(100,int(r['total_simple_paths']))
    for k,r in reach.items():assert short_counts[k]==int(r['shortest_path_count'])==int(r['shortest_paths_saved']) and r['shortest_enumeration_complete']=='True'
    for r in csv.DictReader(open(RUN/'recurrent_edges.csv')):
        a,b=int(r['source']),int(r['target']);assert nodes[a]['scc_export_graph']==nodes[b]['scc_export_graph'];assert a==b or int(nodes[a]['scc_export_graph_size'])>1
    named_counts={}
    for name in ['paper_associated_paths.csv','gng021_overlap_examples.csv']:
        count=0
        for r in csv.DictReader(open(RUN/name)):
            p=json.loads(r['body_ids']);assert len(p)==len(set(p)) and len(p)-1==int(r['hops'])<=4
            assert json.loads(r['edge_synapse_counts'])==[weights[e] for e in zip(p,p[1:])];count+=1
        named_counts[name]=count
    ns=set();en=0;ns_tag='{http://graphml.graphdrawing.org/xmlns}'
    for _,el in ET.iterparse(RUN/'circuit_graph.graphml',events=['end']):
        if el.tag==ns_tag+'node':ns.add(int(el.attrib['id']));el.clear()
        elif el.tag==ns_tag+'edge':
            a,b=int(el.attrib['source']),int(el.attrib['target']);assert a in ns and b in ns
            val=[x.text for x in el if x.attrib.get('key')=='edge_weight'];assert len(val)==1 and int(val[0])==weights[a,b];en+=1;el.clear()
    summary=json.loads((RUN/'export_summary.json').read_text());assert len(ns)==summary['visualization_nodes'] and en==summary['visualization_edges'];assert len(weights)==summary['raw_export_edges'] and len(nodes)==summary['raw_export_nodes']
    out=dict(status='PASS',required_files=len(required),validated_raw_edges=len(weights),validated_raw_nodes=len(nodes),path_rows_checked=totals,all_shortest_paths_saved=True,simple_examples_cap=100,path_counts_and_memberships_not_capped=True,graphml_nodes=len(ns),graphml_edges=en,minimum_exported_synapse_count=min(weights.values()),checks=['path uniqueness and simplicity','every saved path weight joined to a live-verified raw edge','side and neurotransmitter field consistency','shortest-path completeness against exhaustive bounded counts and full-graph distances','combined example union','recurrence SCC certificates','GraphML referential integrity and exact weight roundtrip','CSV schema and required files'])
    out['post_hoc_named_routes_checked']=named_counts
    (RUN/'validation_checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

if __name__=='__main__':main()
