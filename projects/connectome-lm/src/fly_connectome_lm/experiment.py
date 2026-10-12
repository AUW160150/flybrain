from __future__ import annotations
import copy
import json
import sys
import time
from pathlib import Path
import numpy as np
import torch
from .util import ROOT,atomic_json,read_json,digest,sha256,code_hash,revision,now,seed_for,setup,sync,plan_receipt,environment
from .graph_extract import Graph,assert_scientific,synthetic_graph,extract
from .graph_controls import rewire,random_density,InvalidControl
from .models import CONDITIONS,GraphRNN,build,accounting
from .text_data import DevelopmentCorpus
from .train import train_run
from .evaluate import evaluate,ngram_references

CORPUS=ROOT/'data/processed/shakespeare'

def graph_path(n:int,sample:int,synthetic:bool=False) -> Path:
    return ROOT/'data/processed'/f'{"synthetic" if synthetic else "fly"}-n{n}-sample{sample}.npz'

def base_graph(config:dict,sample:int,synthetic:bool=False) -> Graph:
    path=graph_path(config['n'],sample,synthetic)
    if not path.exists():
        raise FileNotFoundError(f'Prepare graph first: {path}; use ./fly-lm prepare --nodes {config["n"]} --sampling-seeds {sample}'+(' --smoke' if config['profile']=='smoke' else ''))
    graph=Graph.load(path); assert_scientific(graph,config['profile']); return graph

def run_config(config:dict,seed:int,sample:int,condition:str,learning_rates:dict|None=None) -> dict:
    cfg={k:v for k,v in config.items() if k not in ('training_seeds','sampling_seeds','nulls_per_seed')}
    # Reuse already completed sample-101 confirmation in replication by identical run identity.
    if cfg['profile']=='replication': cfg['profile']='confirmation'
    if learning_rates: cfg['lr']=learning_rates.get(condition,learning_rates['graph'])
    return cfg

def matrix(config:dict,synthetic:bool=False,optional:tuple[str,...]=(),learning_rates:dict|None=None) -> list[dict]:
    if synthetic and config['profile']!='smoke': raise PermissionError('Synthetic only in smoke')
    rows=[]
    for sample in config['sampling_seeds']:
        graph=base_graph(config,sample,synthetic)
        for seed in config['training_seeds']:
            for condition in CONDITIONS+list(optional):
                for k in (range(1,config['nulls_per_seed']+1) if condition=='DEGREE-REWIRED' else [0]):
                    cfg=run_config(config,seed,sample,condition,learning_rates)
                    model=build(condition,graph,cfg,seed); acc=accounting(model)
                    effective={'condition':condition,'sample':sample,'seed':seed,'null_index':k,'config':cfg,
                               'base_graph_hash':graph.hash,'corpus_sha256':sha256(CORPUS/'manifest.json'),'code_hash':code_hash()}
                    run_id=f'{cfg["profile"]}-g{sample}-s{seed}-{condition.lower()}-k{k}-{digest(effective)[:12]}'
                    p=acc['active_trainable_parameters']; n=config['n']; b=config['batch']; t=config['context']; d=config['d']
                    # Transparent rough arithmetic: learned tensors+Adam+grad, BPTT saved state allowance; excludes library workspaces.
                    memory=16*p+4*b*t*(8*n+4*d+512)+4*n*n+acc['nontrainable_graph_storage_bytes']
                    edges=len(graph.source)
                    forward_ops=2*(n*n+2*n*d+256*d) if config['execution']=='dense' else 2*(edges+2*n*d+256*d)
                    if condition=='NO-CROSS-NODE-RECURRENCE' and config['execution']!='dense': forward_ops=2*(n+2*n*d+256*d)
                    if condition=='PARAMETER-MATCHED-GRU': forward_ops=2*(3*model.h*(model.h+d)+model.h*d+256*d)
                    if condition=='TRANSFORMER': forward_ops=2*(model.layers*(4*d*d+2*d*model.ff+2*t*d)+d*d+256*d)
                    rows.append({'run_id':run_id,'condition':condition,'training_seed':seed,'sampling_seed':sample,'null_index':k,
                                 'config':cfg,'base_graph_hash':graph.hash,'synthetic':synthetic,
                                 'null_seed':seed_for('rewire',sample,seed,k) if condition=='DEGREE-REWIRED' else seed_for('density',sample,seed),
                                 'accounting':acc,'expected_prediction_bytes':None if cfg.get('protocol')=='fixed-time' else b*t*config['updates'],
                                 'estimated_training_memory_bytes':memory,'estimated_checkpoint_storage_bytes':3*(16*p+4*n*n),
                                 'estimated_forward_multiply_add_flops_per_byte':forward_ops,
                                 'estimated_training_flops_per_byte':3*forward_ops,
                                 'operation_estimate_note':'Rough dense GEMM/scatter forward arithmetic; training ~3x; excludes elementwise/optimizer/softmax overhead',
                                 'already_complete':(ROOT/'runs'/run_id/'result.json').exists()})
    order=np.random.default_rng(seed_for('run-order',config['n'],sum(config['training_seeds']))).permutation(len(rows))
    return [rows[i] for i in order]

def summary_matrix(rows:list[dict],profile:str) -> dict:
    return {'profile':profile,'run_count':len(rows),'to_train':sum(not r['already_complete'] for r in rows),
            'total_prediction_bytes':sum(r['expected_prediction_bytes'] or 0 for r in rows),
            'peak_estimated_training_memory_bytes':max(r['estimated_training_memory_bytes'] for r in rows),
            'estimated_total_checkpoint_storage_bytes':sum(r['estimated_checkpoint_storage_bytes'] for r in rows),
            'estimate_limitations':'Estimates exclude allocator/library workspaces and OS; actual memory/time must be measured',
            'runs':rows}

def resolved_graph(row:dict,base:Graph) -> Graph:
    condition=row['condition']
    if condition not in ('DEGREE-REWIRED','RANDOM-DENSITY'): return base
    path=ROOT/'data/processed/controls'/f'{condition.lower()}-{base.hash[:12]}-seed{row["null_seed"]}.npz'
    if path.exists():
        graph=Graph.load(path)
        if graph.metadata['original_graph_hash']!=base.hash: raise ValueError('Control graph base differs')
        return graph
    try:
        graph=rewire(base,row['null_seed']) if condition=='DEGREE-REWIRED' else random_density(base,row['null_seed'])
    except InvalidControl as exc:
        atomic_json(path.with_suffix('.invalid.json'),exc.diagnostic); raise
    graph.save(path); return graph

def backend_check(config:dict,optional:tuple[str,...]=()) -> dict:
    setup(config['device'],config['threads'])
    tiny=synthetic_graph(synthetic=True,smoke=True); results={}
    for condition in CONDITIONS+list(optional):
        model=build(condition,tiny,config,1).to(config['device'])
        x=torch.tensor([[1,2,3,4]],device=config['device']); y=model(x)
        y.square().mean().backward()
        if not torch.isfinite(y).all(): raise RuntimeError(f'{condition} backend returned nonfinite output')
        if isinstance(model,GraphRNN) and model.theta.requires_grad and model.theta.grad.norm()==0: raise RuntimeError('No core gradients')
        reference=copy.deepcopy(model).cpu()
        with torch.no_grad(): expected=reference(x.cpu())
        torch.testing.assert_close(y.cpu(),expected,atol=1e-5,rtol=1e-4)
        results[condition]={'forward_backward':'passed','compared_to_cpu':True}
    return {'device':config['device'],'execution':config['execution'],'checks':results}

def execute(config:dict,*,synthetic:bool=False,optional:tuple[str,...]=(),dry_run:bool=False,
            resume:bool=False,learning_rates:dict|None=None,freeze:dict|None=None) -> list[dict]:
    rows=matrix(config,synthetic,optional,learning_rates); preview=summary_matrix(rows,config['profile'])
    print(json.dumps(preview,indent=2),flush=True)
    if dry_run: return rows
    resources=environment()
    required_disk=preview['estimated_total_checkpoint_storage_bytes']+100_000_000
    excessive_memory=resources['ram_bytes'] is not None and preview['peak_estimated_training_memory_bytes']>.6*resources['ram_bytes']
    if resources['disk_free_bytes']<required_disk or excessive_memory:
        from .util import load_config
        proposal=ROOT/'configs/resource-limited-smoke.yaml'
        atomic_json(proposal,{**load_config('smoke'),'resource_scope':'separate smaller software smoke; no research inference'})
        raise RuntimeError(f'Preset exceeds resource estimate; explicitly review separate smaller preset {proposal}; no run launched')
    if config['profile'] in ('confirmation','replication') and freeze is None:
        raise PermissionError('Confirmation/replication require explicit frozen configuration before training')
    if config['profile'] in ('confirmation','replication'):
        validate_freeze(freeze,config,optional,learning_rates)
    env=setup(config['device'],config['threads']); checks=backend_check(config,optional)
    corpus=DevelopmentCorpus(CORPUS)
    bundle_id=f'{config["profile"]}-{digest([r["run_id"] for r in rows])[:12]}'
    bundle=ROOT/'runs'/f'{bundle_id}.json'
    if not bundle.exists():
        atomic_json(bundle,{'profile':config['profile'],'config':config,'run_ids':[r['run_id'] for r in rows],
                          'created_utc':now(),'code_hash':code_hash(),'corpus_manifest_sha256':sha256(CORPUS/'manifest.json'),
                          'analysis_plan':plan_receipt(),'command':sys.argv,'backend':env,'backend_check':checks,
                          'freeze_hash':digest(freeze) if freeze else None,'synthetic':synthetic})
    reference=ngram_references(corpus.train,corpus.validation)
    atomic_json(ROOT/'reports'/f'{bundle_id}-validation-ngram.json',reference)
    results=[]
    for row in rows:
        t0=time.perf_counter(); base=base_graph(config,row['sampling_seed'],synthetic)
        try:
            graph=resolved_graph(row,base)
        except InvalidControl as exc:
            failed_dir=ROOT/'runs'/row['run_id']; failed_dir.mkdir(parents=True,exist_ok=True)
            failure={'type':'InvalidControl','message':str(exc),'randomization':exc.diagnostic,'utc':now()}
            atomic_json(failed_dir/'manifest.json',{'status':'invalid_control','failure':failure,'config':row['config'],
                        'metadata':{k:row[k] for k in ['condition','training_seed','sampling_seed','null_index','null_seed']},
                        'git_revision':revision(),'code_hash':code_hash(),'command':sys.argv})
            atomic_json(failed_dir/'failure.json',failure)
            raise
        model=build(row['condition'],graph,row['config'],row['training_seed'])
        if row['condition'] in ('FLY-TOPOLOGY','DEGREE-REWIRED','RANDOM-DENSITY'):
            assert accounting(model)==row['accounting']
        metadata={k:row[k] for k in ['condition','training_seed','sampling_seed','null_index','null_seed','synthetic','base_graph_hash']}
        metadata.update(graph_hash=graph.hash,corpus_manifest_sha256=sha256(CORPUS/'manifest.json'))
        run_dir=ROOT/'runs'/row['run_id']
        if not (run_dir/'preparation.json').exists():
            run_dir.mkdir(parents=True,exist_ok=True)
            atomic_json(run_dir/'preparation.json',{'graph_and_model_initialization_seconds':time.perf_counter()-t0,'graph_metadata':graph.metadata})
        result=train_run(model,corpus,row['config'],run_dir,metadata,resume=resume)
        results.append(result)
    print(f'Completed bundle: {bundle}',flush=True); return results

def freeze_config(config:dict,selection:dict,optional:tuple[str,...]=()) -> dict:
    if config['profile'] not in ('confirmation','replication'): raise ValueError('Freeze only confirmation/replication')
    if selection.get('status')!='complete' or selection.get('development_seeds')!=[901,902]: raise ValueError('Complete development grid required')
    if selection['code_hash']!=code_hash(): raise ValueError('Development code changed; make a new study revision')
    if selection['corpus_manifest_sha256']!=sha256(CORPUS/'manifest.json'): raise ValueError('Development corpus changed')
    rates=selection['learning_rates']; rows=matrix(config,False,optional,rates)
    return {'profile':config['profile'],'config':config,'learning_rates':rates,'optional':list(optional),
            'code_hash':code_hash(),'git_revision':revision(),'analysis_plan_sha256':plan_receipt()['sha256'],
            'corpus_manifest_sha256':sha256(CORPUS/'manifest.json'),
            'graphs':{str(s):base_graph(config,s).hash for s in config['sampling_seeds']},
            'run_ids':[r['run_id'] for r in rows],'selection_sha256':digest(selection),'created_utc':now(),
            'checkpoint_selection':'best full deterministic validation BPB within fixed complete training budget; final also reported',
            'test_policy':'Explicit final-evaluate only after all declared runs complete; no pilot test'}

def validate_freeze(freeze:dict,config:dict,optional:tuple[str,...],rates:dict) -> None:
    if freeze['config']!=config or freeze['learning_rates']!=rates or freeze['optional']!=list(optional): raise PermissionError('Configuration differs from freeze')
    if freeze['code_hash']!=code_hash() or freeze['analysis_plan_sha256']!=plan_receipt()['sha256']: raise PermissionError('Code/analysis plan changed after freeze')
    if freeze['corpus_manifest_sha256']!=sha256(CORPUS/'manifest.json'): raise PermissionError('Corpus changed after freeze')
    for sample,value in freeze['graphs'].items():
        if base_graph(config,int(sample)).hash!=value: raise PermissionError('Graph changed after freeze')
    if [r['run_id'] for r in matrix(config,False,optional,rates)]!=freeze['run_ids']: raise PermissionError('Run matrix changed')
