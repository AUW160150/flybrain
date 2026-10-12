from __future__ import annotations
import argparse
import json
from pathlib import Path
import time
import numpy as np
import torch
from .util import ROOT,load_config,atomic_json,read_json,environment,setup,sha256,now,sync

def parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(description='Small MaleCNS-constrained byte LM; staged local execution')
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('inspect')
    d=sub.add_parser('download'); d.add_argument('--cache-dir',type=Path,default=ROOT.parent/'data/flat-connectome')
    for name in ['prepare','extract']:
        d=sub.add_parser(name); d.add_argument('--nodes',type=int,default=512); d.add_argument('--sampling-seeds',type=int,nargs='+',default=[101])
        d.add_argument('--synthetic',action='store_true'); d.add_argument('--smoke',action='store_true')
    for name in ['run','matrix','controls','smoke','profile','tune']:
        d=sub.add_parser(name); d.add_argument('--config',default='smoke' if name=='smoke' else 'pilot')
        d.add_argument('--dry-run',action='store_true'); d.add_argument('--synthetic',action='store_true'); d.add_argument('--smoke',action='store_true')
        d.add_argument('--resume',action='store_true'); d.add_argument('--device',choices=['cpu','cuda','mps']); d.add_argument('--execution',choices=['dense','scatter','sparse'])
        d.add_argument('--include',nargs='*',choices=['TRANSFORMER','FROZEN-FLY','COUNT-INIT','SHUFFLED-COUNT-INIT'],default=[])
        d.add_argument('--freeze',type=Path); d.add_argument('--selection',type=Path)
        d.add_argument('--protocol',choices=['fixed-bytes','fixed-time']); d.add_argument('--output',type=Path)
    d=sub.add_parser('freeze'); d.add_argument('--config',default='confirmation'); d.add_argument('--selection',type=Path,required=True)
    d.add_argument('--output',type=Path,required=True); d.add_argument('--include',nargs='*',default=[])
    d.add_argument('--protocol',choices=['fixed-bytes','fixed-time']); d.add_argument('--device',choices=['cpu','cuda','mps'])
    d=sub.add_parser('final-evaluate'); d.add_argument('--freeze',type=Path,required=True)
    d=sub.add_parser('report'); d.add_argument('--bundle',type=Path,required=True); d.add_argument('--output',type=Path)
    d=sub.add_parser('diagnose'); d.add_argument('--bundle',type=Path,required=True)
    return p

def main(argv:list[str]|None=None) -> None:
    args=parser().parse_args(argv)
    if args.command=='inspect':
        info=environment(); atomic_json(ROOT/'docs/environment.json',info); print(json.dumps(info,indent=2)); return
    if args.command=='download':
        from .data_download import acquire_malecns,acquire_shakespeare
        print(json.dumps(acquire_malecns(ROOT/'data/raw',args.cache_dir),indent=2)); acquire_shakespeare(ROOT/'data/raw'); return
    if args.command in ('prepare','extract'):
        from .data_download import acquire_shakespeare
        from .text_data import prepare_text
        from .graph_extract import canonicalize,extract,synthetic_graph
        from .experiment import graph_path
        if args.synthetic and not args.smoke: raise PermissionError('Synthetic requires --synthetic --smoke')
        if args.synthetic and args.nodes!=64: raise ValueError('Synthetic software smoke must use 64 nodes')
        if not args.synthetic: canonicalize(ROOT/'data/raw/malecns-manifest.json',ROOT/'data/processed/canonical')
        raw,manifest=acquire_shakespeare(ROOT/'data/raw'); prepare_text(raw,ROOT/'data/processed/shakespeare',manifest)
        graphs=[]
        for seed in args.sampling_seeds:
            graph=synthetic_graph(64,seed,synthetic=True,smoke=True) if args.synthetic else extract(ROOT/'data/processed/canonical',args.nodes,seed,args.smoke)
            path=graph_path(args.nodes,seed,args.synthetic); graph.save(path); graphs.append(graph)
            print(f'{path}: N={len(graph.ids)}, E={len(graph.source)}, SHA256={graph.hash}')
        if len(graphs)>1:
            atomic_json(ROOT/'data/processed'/f'overlaps-n{args.nodes}.json',[
                {'sample_a':a.metadata['sampling_seed'],'sample_b':b.metadata['sampling_seed'],
                 'shared_nodes':len(set(a.ids)&set(b.ids)),'jaccard':len(set(a.ids)&set(b.ids))/len(set(a.ids)|set(b.ids)),
                 'note':'overlapping samples from ONE specimen'} for i,a in enumerate(graphs) for b in graphs[i+1:]])
        return
    if args.command=='final-evaluate':
        from .final_evaluation import final_evaluate
        print(json.dumps(final_evaluate(args.freeze),indent=2)); return
    if args.command=='report':
        from .report import report
        print(report(args.bundle,args.output)); return
    if args.command=='diagnose':
        from .diagnostics import run_diagnostics
        for name in read_json(args.bundle)['run_ids']: run_diagnostics(ROOT/'runs'/name)
        return
    from .experiment import execute,matrix,base_graph,resolved_graph,freeze_config,backend_check
    config=load_config(args.config)
    if getattr(args,'device',None): config['device']=args.device
    if getattr(args,'execution',None): config['execution']=args.execution
    selection=read_json(args.selection) if getattr(args,'selection',None) else None
    if getattr(args,'protocol',None): config['protocol']=args.protocol
    if config['protocol']=='fixed-time':
        if selection is None: raise PermissionError('Fixed-time protocol requires complete pooled development profiling selection')
        config['time_budget_seconds']=selection['fixed_time_budget_seconds']
    if args.command=='freeze':
        freeze=freeze_config(config,selection,tuple(args.include))
        if args.output.exists(): raise FileExistsError('Freeze immutable; choose a new filename')
        atomic_json(args.output,freeze); print(f'Configuration frozen: {args.output}, SHA256={sha256(args.output)}'); return
    if args.synthetic and not (args.smoke or args.command=='smoke'): raise PermissionError('Use both --synthetic --smoke')
    if args.synthetic and config['profile']!='smoke': raise PermissionError('Synthetic only smoke')
    if args.smoke and config['profile']!='smoke': raise ValueError('--smoke requires smoke config')
    if args.command=='smoke' and config['profile']!='smoke': raise ValueError('Smoke command requires smoke preset')
    if args.command=='tune':
        from .tuning import tune
        tune(config,args.output or ROOT/'configs/development-selection.json',dry_run=args.dry_run,
             include_transformer='TRANSFORMER' in args.include,resume=args.resume); return
    if args.command=='profile':
        if args.dry_run:
            print(json.dumps({'action':'3 measured forward/backward steps after 1 warmup; no optimizer updates/test access','conditions':__import__('fly_connectome_lm.models',fromlist=['CONDITIONS']).CONDITIONS+args.include,'config':config},indent=2)); return
        from .models import build,CONDITIONS
        checks=backend_check(config,tuple(args.include)); g=base_graph(config,config['sampling_seeds'][0],args.synthetic)
        results=[]
        for condition in CONDITIONS+args.include:
            m=build(condition,g,config,1).to(config['device']); x=torch.arange(config['batch']*config['context']).reshape(config['batch'],config['context']).remainder(256).to(config['device'])
            times=[]
            for i in range(4):
                sync(config['device']); start=time.perf_counter(); m.zero_grad(); m(x).square().mean().backward(); sync(config['device'])
                if i: times.append(time.perf_counter()-start)
            results.append({'condition':condition,'mean_forward_backward_seconds':float(np.mean(times)),'note':'Synthetic token microbenchmark; no training or accuracy result'})
        out=args.output or ROOT/'reports'/f'profile-{config["profile"]}.json'; atomic_json(out,{'config':config,'checks':checks,'profiles':results}); print(out); return
    freeze=read_json(args.freeze) if args.freeze else None
    rates=freeze['learning_rates'] if freeze else (selection['learning_rates'] if selection else None)
    if args.command=='controls':
        rows=matrix(config,args.synthetic,tuple(args.include),rates)
        print(json.dumps(rows,indent=2))
        if not args.dry_run:
            for row in rows: resolved_graph(row,base_graph(config,row['sampling_seed'],args.synthetic))
        return
    execute(config,synthetic=args.synthetic,optional=tuple(args.include),dry_run=args.dry_run or args.command=='matrix',
            resume=args.resume,learning_rates=rates,freeze=freeze)

if __name__=='__main__': main()
