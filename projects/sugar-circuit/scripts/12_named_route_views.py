"""Extract explicitly labeled paper-associated views AFTER unrestricted search."""
from pathlib import Path
import csv,json,itertools,collections
ROOT=Path(__file__).resolve().parents[1];RUN=ROOT/(ROOT/'config/current_structural_run.txt').read_text().strip()

def main():
    nodes={int(r['body_id']):r for r in csv.DictReader(open(RUN/'nodes.csv'))}
    bytype=collections.defaultdict(list)
    for v,r in nodes.items():bytype[r['type']].append(v)
    weights={}
    for name in ['sensory_out','named_out','motor_in','additional_named_out']:
        for a,b,w,*_ in json.loads((RUN/'raw'/f'{name}.json').read_text())['data']:weights[a,b]=w
    patterns=[('paper_associated',['GNG042','GNG015'],['MN4a','MN9']),('paper_associated',['ANXXX462a','GNG585','GNG108'],['MN4a','MN9']),('paper_associated',['ANXXX462a','GNG585','GNG120'],['MN4a','MN9']),('paper_associated',['ANXXX462a','GNG585','GNG472'],['MN8']),('candidate_overlap_not_paper_claim',['GNG042','GNG021','GNG015'],['MN4a','MN9'])]
    rows=[]
    for label,middle,targets in patterns:
        for st in ['LB3a','LB3b','LB3c','LB3d']:
            for tt in targets:
                for path in itertools.product(*(sorted(bytype[t]) for t in [st]+middle+[tt])):
                    if len(path)!=len(set(path)) or any(e not in weights for e in zip(path,path[1:])):continue
                    rows.append(dict(view=label,source_subtype=st,source=path[0],target=path[-1],target_type=tt,hops=len(path)-1,body_ids=json.dumps(path,separators=(',',':')),types=json.dumps([nodes[v]['type'] for v in path],separators=(',',':')),sides=json.dumps([nodes[v]['side'] for v in path],separators=(',',':')),edge_synapse_counts=json.dumps([weights[e] for e in zip(path,path[1:])],separators=(',',':')),provenance='raw/sensory_out.json; raw/named_out.json; raw/additional_named_out.json; raw/motor_in.json',evidence='STRUCTURAL CONNECTIVITY ONLY; post hoc named view; not a restriction on circuits A-D'))
    for name,label in [('paper_associated_paths.csv','paper_associated'),('gng021_overlap_examples.csv','candidate_overlap_not_paper_claim')]:
        with open(RUN/name,'w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(r for r in rows if r['view']==label)
    views=json.loads((RUN/'visualization_views.json').read_text());views['views']['paper_associated']['complete_named_route_file']='paper_associated_paths.csv';views['views']['paper_associated']['candidate_overlap_separate']='gng021_overlap_examples.csv';(RUN/'visualization_views.json').write_text(json.dumps(views,indent=2)+'\n')
    motors=set(json.loads((RUN/'analysis/groups.json').read_text())['targets']);motorrows=[]
    for r in csv.DictReader(open(RUN/'raw_edges.csv')):
        if int(r['source']) in motors and 'A' in r['circuit_membership'].split('|'):motorrows.append(r)
    with open(RUN/'motor_origin_edges_in_circuit_A.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(motorrows[0]));w.writeheader();w.writerows(motorrows)
    print('Named route views',collections.Counter(r['view'] for r in rows));print('Motor-origin edges in A',len(motorrows))

if __name__=='__main__':main()
