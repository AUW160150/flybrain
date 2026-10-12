from __future__ import annotations
import argparse, csv, io, json, os, sys
from pathlib import Path
from .provenance import *

def parser():
    p=argparse.ArgumentParser(description='Read-only MaleCNS and saved-model inspection. CPU only. All outputs under visualization/.')
    sub=p.add_subparsers(dest='command',required=True)
    for name in ['inspect-workspace','inspect-data-schema','build-views','validate','build-indexes']:
        sub.add_parser(name)
    sub.add_parser('plan-resources').add_argument('--dry-run',action='store_true')
    for name in ['verify-run','snapshot-run']:
        q=sub.add_parser(name); q.add_argument('--run-dir')
        if name=='snapshot-run': q.add_argument('--checkpoint',choices=['final.pt','best.pt','latest.pt'],default='final.pt'); q.add_argument('--safe-export',type=Path)
    for name in ['ingest-full','ingest-subset']:
        q=sub.add_parser(name); q.add_argument('--rss-mib',type=int,default=512); q.add_argument('--storage-gib',type=int,default=64); q.add_argument('--max-seconds',type=int,default=300)
    q=sub.add_parser('fetch-morphology'); q.add_argument('--ids-from',type=Path); q.add_argument('--max-ids',type=int,default=8); q.add_argument('--download-mib',type=int,default=32); q.add_argument('--max-seconds',type=int,default=60); q.add_argument('--offline',action='store_true')
    sub.add_parser('inspect-model')
    q=sub.add_parser('serve'); q.add_argument('--host',choices=['127.0.0.1','localhost'],default='127.0.0.1'); q.add_argument('--port',type=int,default=8765)
    for name in ['export-neuron','export-edges','export-figures']:
        q=sub.add_parser(name); q.add_argument('--scope',default='G3'); q.add_argument('--id'); q.add_argument('--direction',choices=['incoming','outgoing'],default='outgoing'); q.add_argument('--output',type=Path)
    return p

def main():
    args=parser().parse_args()
    try:
        try: os.nice(10)
        except OSError: pass
        result=dispatch(args)
        if result is not None:
            print(json.dumps(result,indent=2,allow_nan=False))
            if isinstance(result,dict) and result.get('failed',0): return 1
    except EvidenceError as e:
        print(json.dumps(e.detail,indent=2),file=sys.stderr); return 2
    return 0

def dispatch(a):
    from . import discover_run as d
    if a.command=='inspect-workspace':
        r=d.inventory(); return dict(runs=len(r['runs']),report=str(REPORT/'inventory.json'))
    if a.command=='plan-resources': return d.plan()
    if a.command=='inspect-data-schema':
        from .ingest import inspect_schema
        return inspect_schema()
    if a.command=='verify-run':
        runs=d.select_runs(a.run_dir); g=d.verify_graph()
        if any(m['metadata']['graph_hash']!=g['graph_hash'] for _,m in runs): fail('E_GRAPH_MASK_MISMATCH','Run manifest differs from saved graph')
        from .ingest import topology_only
        topology_only(g); r=d.verify_parent(g)
        atomic(REPORT/'subset-ids.json',[str(v) for v in g['ids']]); return {k:v for k,v in r.items() if k!='parent_selected_stats'}
    if a.command.startswith('ingest-'):
        from .ingest import ingest
        return ingest(a.command=='ingest-full',a.rss_mib,a.storage_gib,a.max_seconds)
    if a.command=='build-indexes':
        from .ingest import ingest
        return ingest(True)
    if a.command=='inspect-model':
        from .model_inspection import inspect_models
        r=inspect_models(); return dict(actual_parameters=r['actual']['active_trainable'],references=[(x['name'],x['active_trainable']) for x in r['references']])
    if a.command=='snapshot-run':
        from .model_inspection import snapshot
        if not a.run_dir: fail('E_RUN_AMBIGUOUS','Choose a run explicitly; topology does not choose trained weights','weights','./visualization/viz snapshot-run --run-dir fly_connectome_lm/runs/confirmation-g101-s33-fly-topology-k0-441b7753ad8e --checkpoint final.pt')
        if a.safe_export:
            from .model_inspection import inspect_payload
            import torch
            directory,manifest=d.select_runs(a.run_dir)[0]; g=d.verify_graph()
            source=a.safe_export.resolve()
            copied,receipt=stable_copy(source,ROOT/'snapshots/safe-exports')
            data=torch.load(copied,map_location='cpu',weights_only=True)
            original=read(REPORT/'snapshots'/(directory.name+'.json'))
            if data.get('original_checkpoint_sha256')!=original['sha256']: fail('E_CHECKPOINT_UNSTABLE_OR_UNSAFE','Safe export does not identify this run immutable original snapshot')
            receipt['original_checkpoint_sha256']=original['sha256']
            receipt['weight_provenance']='User supplied trusted tensor-only export; correspondence attested externally, not proven by export hash'
            if data.get('graph_hash')!=g['graph_hash'] or not data.get('original_checkpoint_sha256'): fail('E_CHECKPOINT_UNSTABLE_OR_UNSAFE','Safe export needs graph_hash and original_checkpoint_sha256')
            r=inspect_payload(data,manifest,g,receipt,d.verify_archive(manifest['code_hash']),directory.name)
        else: r=snapshot(a.run_dir,a.checkpoint)
        return {k:v for k,v in r.items() if k not in ('weights','activity')}
    if a.command=='fetch-morphology':
        from .morphology import fetch
        return fetch(a.ids_from,a.max_ids,a.download_mib,a.max_seconds,a.offline)
    if a.command=='build-views':
        from .render import build
        return build()
    if a.command=='validate':
        from .validation import validate
        return validate()
    if a.command=='serve':
        from .app import serve
        serve(a.host,a.port); return
    if a.command.startswith('export-'):
        from .app import database
        from .indexing import edge_records,node,SCOPES,require_scope
        if a.command=='export-figures':
            from .render import build
            return build()
        db=database(a.scope); require_scope(db,a.scope); db.set_progress_handler(None,0)
        out=a.output or REPORT/'tables'/('neuron-'+body_id(a.id)+'.json' if a.command=='export-neuron' else a.scope+'-edges.csv')
        if not out.resolve().is_relative_to(ROOT): fail('E_PROTECTED_INPUT_CHANGED','Exports must stay inside visualization')
        if a.command=='export-neuron':
            r=node(db,a.scope,a.id); atomic(out,r); return dict(path=str(out))
        out.parent.mkdir(parents=True,exist_ok=True); tmp=out.with_name(out.name+'.partial')
        query=f'SELECT * FROM edges WHERE {SCOPES[a.scope]}'; params=[]
        if a.id:
            query+=' AND '+('target' if a.direction=='incoming' else 'source')+'=?'; params=[body_id(a.id)]
        query+=' ORDER BY source,target'
        count=0
        with tmp.open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=['source_body_id','target_body_id','synapse_count','release','graph_scope','source_record_reference']); w.writeheader()
            for r in edge_records(db.execute(query,params),a.scope): w.writerow(r); count+=1
        os.replace(tmp,out); atomic(out.with_suffix(out.suffix+'.manifest.json'),dict(scope=a.scope,release=RELEASE,records=count,sha256=sha(out),code_revision=revision(),filter_id=a.id,direction=a.direction)); return dict(path=str(out),rows=count)

if __name__=='__main__': sys.exit(main())
