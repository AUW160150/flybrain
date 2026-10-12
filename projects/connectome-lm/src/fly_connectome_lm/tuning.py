from __future__ import annotations
from collections import defaultdict
from pathlib import Path
import copy
import numpy as np
from .experiment import execute,matrix
from .util import ROOT,atomic_json,read_json,code_hash,now,sha256,digest

GRID=(.0003,.001,.003)

def tune(config:dict,output:Path,*,dry_run:bool=False,include_transformer:bool=False,resume:bool=False) -> dict:
    if config['profile']!='pilot': raise ValueError('Development uses fixed pilot profile budget, not test/confirmation seeds')
    config=copy.deepcopy(config); config.update(profile='development',training_seeds=[901,902],sampling_seeds=[101],nulls_per_seed=1)
    optional=('TRANSFORMER',) if include_transformer else ()
    trials=[]
    for lr in GRID:
        cfg={**config,'lr':lr}
        rows=execute(cfg,optional=optional,dry_run=dry_run,resume=resume)
        if not dry_run:
            for r in rows: trials.append({'lr':lr,**r})
    if dry_run: return {'status':'dry-run'}
    grouped=defaultdict(list); times=[]
    for r in trials:
        key='graph' if r['condition'] in ('FLY-TOPOLOGY','DEGREE-REWIRED') else r['condition']
        if key in ('graph','PARAMETER-MATCHED-GRU','TRANSFORMER'): grouped[(key,r['lr'])].append(r['validation_best']['bpb'])
        times.append(r['training_seconds']/r['final_step'])
    rates={}; scores={}
    for architecture in sorted({key[0] for key in grouped}):
        expected=4 if architecture=='graph' else 2
        if any(len(grouped[(architecture,lr)])!=expected for lr in GRID): raise ValueError('Incomplete development trials')
        vals={str(lr):float(np.mean(grouped[(architecture,lr)])) for lr in GRID}
        rates[architecture]=min(GRID,key=lambda lr:(vals[str(lr)],lr)); scores[architecture]=vals
    result={'status':'complete','development_seeds':[901,902],'grid':list(GRID),'trial_config':config,
            'learning_rates':rates,'pooled_validation_scores':scores,'trials':trials,'created_utc':now(),
            'code_hash':code_hash(),'fixed_time_budget_seconds':float(np.mean(times)*config['updates']),
            'time_budget_rule':'mean development seconds/update pooled over every complete trial times development updates; validation excluded',
            'corpus_manifest_sha256':sha256(ROOT/'data/processed/shakespeare/manifest.json')}
    if output.exists() and read_json(output)!=result: raise ValueError('Selection output exists; choose new study filename')
    atomic_json(output,result); return result
