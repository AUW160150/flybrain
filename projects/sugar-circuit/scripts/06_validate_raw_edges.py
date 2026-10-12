"""Compare complete targeted neuPrint queries with the retained full flat graph."""
from pathlib import Path
import csv,json,hashlib,datetime
import numpy as np
import pyarrow as pa
import pyarrow.compute as pc

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/(ROOT/'config/current_structural_run.txt').read_text().strip()
NAMES=['sensory_out','motor_in','named_out','gng021_in','additional_named_out']

def main():
    queries={n:json.loads((RUN/'raw'/f'{n}.json').read_text()) for n in NAMES}
    neu={n:{(int(r[0]),int(r[1])):int(r[2]) for r in q['data']} for n,q in queries.items()}
    sources=set(a for n in ['sensory_out','named_out','additional_named_out'] for a,b in neu[n])
    targets=set(b for n in ['motor_in','gng021_in'] for a,b in neu[n])
    aset=pa.array(sorted(sources));bset=pa.array(sorted(targets))
    reader=pa.ipc.open_file(pa.memory_map(str(ROOT/'data/raw/connectome-weights-male-cns-v1.0-minconf-0.5.feather')))
    flat={};flatrows=[]
    for k in range(reader.num_record_batches):
        batch=reader.get_batch(k)
        keep=pc.or_(pc.is_in(batch.column(0),value_set=aset),pc.is_in(batch.column(1),value_set=bset))
        for row in batch.filter(keep).to_pylist():
            edge=(row['body_pre'],row['body_post']);flat[edge]=row['weight'];flatrows.append(row)
    with open(RUN/'raw/targeted_flat_edges_unfiltered.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['body_pre','body_post','weight']);w.writeheader();w.writerows(flatrows)
    comparisons=[]
    for name,edges in neu.items():
        side=0 if name.endswith('out') else 1
        bodyset={x[side] for x in edges}
        fset={x:w for x,w in flat.items() if x[side] in bodyset}
        for (a,b) in sorted(set(edges)|set(fset)):
            nw=edges.get((a,b));fw=fset.get((a,b))
            comparisons.append(dict(query=name,source=a,target=b,neuprint_weight=nw,flat_weight=fw,status='VERIFIED' if nw==fw else 'SOURCE CONFLICT',query_file=str((RUN/'queries'/f'{name}.json').relative_to(ROOT)),raw_query_file=str((RUN/'raw'/f'{name}.json').relative_to(ROOT)),flat_source='data/raw/connectome-weights-male-cns-v1.0-minconf-0.5.feather'))
    with open(RUN/'edge_source_comparison.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(comparisons[0]));w.writeheader();w.writerows(comparisons)
    stats={n:dict(neuprint_rows=len(neu[n]),compared=sum(r['query']==n for r in comparisons),disagreements=sum(r['query']==n and r['status']!='VERIFIED' for r in comparisons)) for n in NAMES}
    (RUN/'raw_validation_summary.json').write_text(json.dumps(stats,indent=2)+'\n')
    with open(ROOT/'logs/query_log.jsonl','a') as f:
        for name in ['additional_named_out','additional_named_metadata']:
            path=RUN/'raw'/f'{name}.json';q=json.loads(path.read_text())
            f.write(json.dumps(dict(timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),experiment='GATES_2_3_STRUCTURAL_ONLY',purpose=name,dataset='male-cns:v1.0',query=json.loads((RUN/'queries'/f'{name}.json').read_text()),output_file=str(path.relative_to(ROOT)),sha256=hashlib.file_digest(path.open('rb'),'sha256').hexdigest(),returned_row_count=len(q['data']),http_status=200,authentication='user-provided token; value omitted',errors=None))+'\n')
    print(json.dumps(stats,indent=2),flush=True)

if __name__=='__main__':main()
