from __future__ import annotations
import math
import shutil
import time
from pathlib import Path
import numpy as np
import torch
from torch.nn import functional as F
from .common import ROOT, now, event, write_json, read_json, sha256, environment, source_hashes
from .connectome import load_graph
from .corpus import TRAIN, VALIDATION, TEST, prompt, public, manifest
from .models import EOS, Reservoir, Readout, TinyTransformer, parameter_count
from .judge import judge

def setup(seed):
    torch.set_num_threads(2)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)
    np.random.seed(seed)

def new_run(seed,steps,max_bytes):
    run=ROOT/'runs'/('pilot-'+time.strftime('%Y%m%dT%H%M%S',time.gmtime())+f'-s{seed}')
    run.mkdir(parents=True,exist_ok=False)
    config=dict(protocol='pilot-v1',created_at=now(),seed=seed,steps=steps,features=1024,
                max_new_bytes=max_bytes,learning_rate_readout=.003,learning_rate_transformer=.001,
                selection='lowest validation answer-byte cross entropy, every 25 updates and last',
                decode='greedy, one candidate, no repair, EOS or output cap',
                corpus=manifest(),sources=source_hashes(),environment=environment(),
                label='development pilot, not confirmatory',judge='bounded-python-ast-v1',
                training='all train solution bytes + EOS at every update; prompt loss masked',
                frozen=['all connectome edges','all raw count ratios','input mapping','pooling mapping'],
                neuron_model='unsigned leaky tanh rate; global gain=.9/max incoming count; leak=.5',
                limitations=['single seed','12 authored training examples','6 held-out task families',
                             'not an official LeetCode benchmark','no physiological neurotransmitter signs',
                             'byte tokenization differs from pretrained LLM tokenization'])
    write_json(run/'config.json',config)
    (run/'source').mkdir()
    for name in config['sources']:
        shutil.copy2(ROOT/name,run/'source'/Path(name).name)
    write_json(run/'status.json',dict(state='running',phase='loading_graph',started_at=now()))
    return run,config

def feature_cache(reservoir,items,run,arm,split):
    xs,ys=[],[]
    t=time.perf_counter();ticks=0
    for problem in items:
        reservoir.reset()
        p=list(prompt(problem).encode())
        answer=list(problem['solution'].encode())+[EOS]
        sequence=p+answer
        for i,token in enumerate(sequence[:-1]):
            feature=reservoir.step(token);ticks+=1
            if i>=len(p)-1:
                xs.append(feature);ys.append(sequence[i+1])
        event(run,'features',arm=arm,split=split,problem=problem['id'],ticks=ticks)
    x=np.stack(xs);y=np.asarray(ys,np.int64)
    np.savez_compressed(run/f'features-{arm}-{split}.npz',x=x,y=y)
    event(run,'features_complete',arm=arm,split=split,seconds=time.perf_counter()-t,ticks=ticks,target_bytes=len(y))
    return torch.from_numpy(x),torch.from_numpy(y)

def transformer_batch(items):
    sequences=[];labels=[]
    for problem in items:
        p=list(prompt(problem).encode());seq=p+list(problem['solution'].encode())+[EOS]
        sequences.append(seq[:-1]);labels.append([-100]*(len(p)-1)+seq[len(p):])
    length=max(map(len,sequences))
    x=torch.full((len(items),length),EOS,dtype=torch.long)
    y=torch.full_like(x,-100)
    for i,(a,b) in enumerate(zip(sequences,labels)):
        x[i,:len(a)]=torch.tensor(a);y[i,:len(b)]=torch.tensor(b)
    return x,y

def train_model(model,train,validation,run,arm,config,lr):
    x,y=train;vx,vy=validation
    model.train();optimizer=torch.optim.AdamW(model.parameters(),lr=lr,weight_decay=.01)
    best=math.inf;history=[];start=time.perf_counter()
    exposures=int((y!=-100).sum())
    def loss_on(a,b):return F.cross_entropy(model(a).reshape(-1,257),b.reshape(-1))
    for step in range(config['steps']+1):
        if step:
            model.train();optimizer.zero_grad(set_to_none=True)
            loss=loss_on(x,y);loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(),1)
            optimizer.step()
        if step%25==0 or step==config['steps']:
            model.eval()
            with torch.no_grad():tl=float(loss_on(x,y));vl=float(loss_on(vx,vy))
            row=dict(step=step,train_loss=tl,validation_loss=vl,seconds=time.perf_counter()-start)
            history.append(row)
            event(run,'loss',arm=arm,**row)
            if vl<best:
                best=vl;best_step=step
                torch.save(model.state_dict(),run/f'{arm}.pt')
            write_json(run/f'{arm}-training.json',dict(history=history,best_step=best_step,
                        parameters=parameter_count(model),target_bytes_per_update=exposures,
                        answer_byte_exposures=step*exposures,training_seconds=time.perf_counter()-start))
    model.load_state_dict(torch.load(run/f'{arm}.pt',weights_only=True))
    model.eval()
    return model

@torch.no_grad()
def generate_fly(reservoir,model,problem,ids,max_bytes=384,callback=None):
    start=time.perf_counter();reservoir.reset();trace=[]
    for byte in prompt(problem).encode():feature=reservoir.step(byte)
    result=[];stopped='length'
    for i in range(max_bytes):
        token=int(model(torch.from_numpy(feature)).argmax())
        if token==EOS:stopped='eos';break
        result.append(token)
        feature=reservoir.step(token)
        if i%16==0:
            activity=reservoir.activity(ids)
            frame=dict(output_byte=i,**activity);trace.append(frame)
            if callback:callback(bytes(result).decode('utf-8',errors='replace'),frame)
    return dict(code=bytes(result).decode('utf-8',errors='replace'),output_bytes=len(result),
                stop_reason=stopped,latency_seconds=time.perf_counter()-start,activity=trace)

@torch.no_grad()
def generate_transformer(model,problem,max_bytes=384):
    start=time.perf_counter();seq=list(prompt(problem).encode());result=[];stopped='length'
    for _ in range(max_bytes):
        if len(seq)>=model.context:stopped='context_limit';break
        token=int(model(torch.tensor([seq]))[0,-1].argmax())
        if token==EOS:stopped='eos';break
        seq.append(token);result.append(token)
    return dict(code=bytes(result).decode('utf-8',errors='replace'),output_bytes=len(result),
                stop_reason=stopped,latency_seconds=time.perf_counter()-start)

def summarize(results):
    eligible=[r for r in results if r.get('judgement',{}).get('passed') is not None]
    n=len(eligible);k=sum(r['judgement']['passed'] for r in eligible)
    if not n:return dict(solved=None,total=0,pass_at_1=None,interval_95=None)
    z=1.959963984540054;p=k/n;den=1+z*z/n
    c=(p+z*z/(2*n))/den;half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return dict(solved=k,total=n,pass_at_1=p,interval_95=[max(0,c-half),min(1,c+half)],
                interval_method='Wilson descriptive task interval; six hand-authored tasks are not a population sample',
                unsupported=sum(r['judgement']['status']=='unsupported' for r in eligible),
                mean_latency_seconds=sum(r['latency_seconds'] for r in eligible)/n)

def evaluate(arm,generate,run,items=TEST):
    results=[]
    for problem in items:
        event(run,'generation_started',arm=arm,problem=problem['id'])
        result=dict(problem=public(problem),prompt=prompt(problem),**generate(problem))
        result['judgement']=judge(result['code'],problem['cases'])
        results.append(result)
        write_json(run/f'{arm}-evaluation.json',dict(arm=arm,results=results,summary=summarize(results),
                   split='test',completed=len(results)==len(items),benchmark='authored coding pilot v1'))
        event(run,'judged',arm=arm,problem=problem['id'],status=result['judgement']['status'])
    return results

def pilot(seed=7,steps=200,max_bytes=384):
    setup(seed);run,config=new_run(seed,steps,max_bytes)
    try:
        W,ids,graph=load_graph()
        write_json(run/'graph.json',graph)
        event(run,'graph_loaded',neurons=len(ids),edges=W.nnz)
        for arm,recurrence in [('fly',True),('no-recurrence',False)]:
            setup(seed)
            reservoir=Reservoir(W,seed,config['features'],recurrence)
            tr=feature_cache(reservoir,TRAIN,run,arm,'train')
            va=feature_cache(reservoir,VALIDATION,run,arm,'validation')
            model=Readout(config['features'])
            model.mean.copy_(tr[0].mean(0));model.scale.copy_(tr[0].std(0).clamp_min(.02))
            train_model(model,tr,va,run,arm,config,config['learning_rate_readout'])
            evaluate(arm,lambda p:generate_fly(reservoir,model,p,ids,max_bytes),run)
        setup(seed)
        model=TinyTransformer()
        train_model(model,transformer_batch(TRAIN),transformer_batch(VALIDATION),run,'transformer',config,config['learning_rate_transformer'])
        evaluate('transformer',lambda p:generate_transformer(model,p,max_bytes),run)
        load_graph(verify=True)
        write_json(run/'status.json',dict(state='completed',phase='local_pilot_complete',completed_at=now(),graph_integrity='verified_after_training'))
        write_json(ROOT/'runs/latest.json',dict(run=run.name))
        write_json(run/'artifacts.json',{p.name:sha256(p) for p in sorted(run.glob('*')) if p.is_file() and p.name!='events.jsonl'})
        event(run,'completed',run_id=run.name)
    except KeyboardInterrupt:
        write_json(run/'status.json',dict(state='interrupted',time=now()))
        event(run,'interrupted');raise
    except Exception as exc:
        write_json(run/'status.json',dict(state='failed',error=str(exc),time=now()))
        event(run,'failed',error=str(exc));raise
    return run

def latest():
    index=ROOT/'runs/latest.json'
    if index.exists():return ROOT/'runs'/read_json(index)['run']
    paths=sorted((ROOT/'runs').glob('pilot-*'))
    return paths[-1] if paths else None
