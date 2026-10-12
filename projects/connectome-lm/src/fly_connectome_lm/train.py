from __future__ import annotations
import copy
import math
import random
import sys
import time
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
from .evaluate import evaluate
from .models import accounting,GraphRNN
from .text_data import DevelopmentCorpus,WindowSampler
from .util import atomic_json,atomic_torch,read_json,digest,code_hash,revision,now,seed_for,sync,peak_rss_bytes,plan_receipt

OPTIMIZER={'betas':(.9,.999),'eps':1e-8,'weight_decay':0.}

def rng_state() -> dict:
    return {'torch':torch.get_rng_state(),'numpy':np.random.get_state(),'python':random.getstate(),
            'cuda':torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None}

def restore_rng(state:dict) -> None:
    torch.set_rng_state(state['torch'].cpu()); np.random.set_state(state['numpy']); random.setstate(state['python'])
    if state['cuda'] is not None: torch.cuda.set_rng_state_all(state['cuda'])

def train_run(model,corpus:DevelopmentCorpus,config:dict,run_dir:Path,metadata:dict,
              resume:bool=False,stop_after:int|None=None) -> dict:
    """Validation-only training. The test split is not a valid argument or selector."""
    device=config['device']; model=model.to(device)
    optimizer=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=config['lr'],**OPTIMIZER)
    seed=metadata['training_seed']; stream_seed=seed_for('data',seed)
    sampler=WindowSampler(corpus.train,config['context'],config['batch'],stream_seed)
    torch.manual_seed(seed_for('runtime',seed)); np.random.seed(seed_for('runtime-numpy',seed)); random.seed(seed_for('runtime-python',seed))
    signature=digest({'config':config,'metadata':metadata})
    history=[]; step=0; best=float('inf'); best_step=0; training_seconds=0.; validation_seconds=0.
    initial_theta=model.theta.detach().cpu().clone() if isinstance(model,GraphRNN) else None
    run_dir.mkdir(parents=True,exist_ok=True)
    manifest_path=run_dir/'manifest.json'
    if manifest_path.exists():
        old=read_json(manifest_path)
        if old['signature']!=signature: raise ValueError('Refusing to overwrite a different immutable run')
        if old['status']=='complete': return read_json(run_dir/'result.json')
        if not resume: raise ValueError('Run exists; explicitly resume or choose a new run ID')
    manifest={'signature':signature,'status':'running','started_utc':now(),'config':config,'metadata':metadata,
              'accounting':accounting(model),'git_revision':revision(),'code_hash':code_hash(),
              'analysis_plan':plan_receipt(),'command':sys.argv,'optimizer':{'name':'AdamW','lr':config['lr'],**OPTIMIZER},
              'rng_derivation':'SHA256 JSON [stream, integer keys], first 8 hex modulo 2**31-1',
              'rng':{'initialization':seed,'data_order':stream_seed,'runtime':seed_for('runtime',seed)},
              'unique_training_corpus_bytes':len(corpus.train),'precision':'float32',
              'execution':config['execution'],'compilation_seconds':0.,'memory_note':'CPU RSS is process lifetime high-water, not isolated tensor peak'}
    if resume and (run_dir/'latest.pt').exists():
        checkpoint=torch.load(run_dir/'latest.pt',map_location='cpu',weights_only=False)
        if checkpoint['signature']!=signature: raise ValueError('Checkpoint signature differs')
        if checkpoint['code_hash']!=code_hash(): raise ValueError('Code changed since checkpoint; requires new labelled revision')
        model.load_state_dict(checkpoint['model']); optimizer.load_state_dict(checkpoint['optimizer'])
        for state in optimizer.state.values():
            for key,value in state.items():
                if isinstance(value,torch.Tensor): state[key]=value.to(device)
        sampler.load_state_dict(checkpoint['sampler']); restore_rng(checkpoint['rng'])
        step=checkpoint['step']; best=checkpoint['best']; best_step=checkpoint['best_step']; history=checkpoint['history']
        training_seconds=checkpoint['training_seconds']; validation_seconds=checkpoint['validation_seconds']
        initial_theta=checkpoint['initial_theta']; manifest=old; manifest['status']='running'
    elif resume:
        raise ValueError('No resumable checkpoint')
    atomic_json(manifest_path,manifest)
    probe=torch.from_numpy(corpus.train[:config['context']].astype(np.int64))[None].to(device)
    if not resume:
        atomic_json(run_dir/'initial_diagnostics.json',model.diagnostics(probe) if isinstance(model,GraphRNN) else {'architecture':type(model).__name__})
    if str(device).startswith('cuda'): torch.cuda.reset_peak_memory_stats()
    def save(path):
        atomic_torch(path,{'model':model.state_dict(),'optimizer':optimizer.state_dict(),'sampler':sampler.state_dict(),
             'rng':rng_state(),'step':step,'best':best,'best_step':best_step,'history':history,'signature':signature,
             'code_hash':manifest['code_hash'],'training_seconds':training_seconds,'validation_seconds':validation_seconds,
             'initial_theta':initial_theta})
    def done():
        return training_seconds>=config['time_budget_seconds'] if config.get('protocol')=='fixed-time' else step>=config['updates']
    try:
        while not done():
            if stop_after is not None and step>=stop_after: break
            sync(device); start=time.perf_counter()
            model.train(); x,y=sampler.next(); x,y=x.to(device),y.to(device)
            optimizer.zero_grad(set_to_none=True); logits=model(x)
            loss=F.cross_entropy(logits.flatten(0,1),y.flatten())
            if not torch.isfinite(loss): raise FloatingPointError('Nonfinite training loss')
            loss.backward()
            edge_grad=float(model.theta.grad.norm()) if isinstance(model,GraphRNN) and model.theta.grad is not None else None
            grad=torch.nn.utils.clip_grad_norm_(model.parameters(),1.,error_if_nonfinite=True)
            optimizer.step(); sync(device); training_seconds+=time.perf_counter()-start; step+=1
            history.append({'step':step,'training_bytes':step*config['batch']*config['context'],
                            'train_nll':float(loss.detach()),'gradient_norm_before_clip':float(grad),
                            'edge_gradient_norm':edge_grad,'training_seconds':training_seconds})
            if step%config['validate_every']==0 or done():
                sync(device); start=time.perf_counter()
                val=evaluate(model,corpus.validation,config['context'],config['evaluation_batch'])
                sync(device); validation_seconds+=time.perf_counter()-start
                history[-1]['validation']=val
                if val['bpb']<best:
                    best=val['bpb']; best_step=step; save(run_dir/'best.pt')
                atomic_json(run_dir/'history.json',history); save(run_dir/'latest.pt')
                print(f"{metadata['condition']} seed={seed} step={step} validation BPB={val['bpb']:.6f}",flush=True)
        if not done():
            save(run_dir/'latest.pt'); manifest['status']='paused'; atomic_json(manifest_path,manifest)
            return {'status':'paused','step':step}
        save(run_dir/'final.pt'); save(run_dir/'latest.pt')
        final_metrics=history[-1]['validation']
        final_diagnostics=model.diagnostics(probe) if isinstance(model,GraphRNN) else {'architecture':type(model).__name__}
        change=float((model.theta.detach().cpu()-initial_theta).norm()) if initial_theta is not None else None
        if isinstance(model,GraphRNN) and model.theta.requires_grad and (change==0. or not any((r['edge_gradient_norm'] or 0)>0 for r in history)):
            raise AssertionError('Trainable recurrent core did not learn')
        exposures=step*config['batch']*config['context']
        result={'status':'complete','condition':metadata['condition'],'training_seed':seed,'sampling_seed':metadata['sampling_seed'],
                'null_index':metadata.get('null_index',0),'profile':config['profile'],'protocol':config.get('protocol','fixed-bytes'),
                'synthetic':metadata['synthetic'],'validation_best':next(r['validation'] for r in history if r['step']==best_step),
                'validation_final':final_metrics,'selected_checkpoint_step':best_step,'final_step':step,
                'training_byte_exposures':exposures,'training_seconds':training_seconds,'validation_seconds':validation_seconds,
                'throughput_prediction_bytes_per_second':exposures/training_seconds,'peak_rss_bytes':peak_rss_bytes(),
                'peak_cuda_allocated_bytes':torch.cuda.max_memory_allocated() if str(device).startswith('cuda') else None,
                'peak_mps_allocated_bytes':None,'accounting':accounting(model),'core_weight_change_l2':change,
                'config_hash':digest(config),'graph_hash':metadata['graph_hash'],'code_hash':manifest['code_hash'],
                'final_diagnostics':final_diagnostics,'completed_utc':now()}
        atomic_json(run_dir/'result.json',result); atomic_json(run_dir/'history.json',history)
        manifest['status']='complete'; atomic_json(manifest_path,manifest); return result
    except Exception as exc:
        manifest['status']='failed'; manifest['failure']={'type':type(exc).__name__,'message':str(exc),'step':step,'utc':now()}
        atomic_json(manifest_path,manifest); atomic_json(run_dir/'failure.json',manifest['failure'])
        raise
