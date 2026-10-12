"""Development-only calibration followed by frozen, recorded v2 code evaluations."""
from __future__ import annotations
import gc
import json
import math
import random
import shutil
import time
from pathlib import Path
import numpy as np
import torch
from torch.nn import functional as F
from .common import ROOT, now, read_json, write_json, sha256, source_hashes, environment, event
from .connectome import load_graph
from .curriculum_data import DIRECTORY,load,prompt
from .curriculum_model import Tokenizer,CodingReservoir,CodeReadout,estimate_radius
from .models import parameter_count
from .judge import judge

def setup(seed):
    torch.set_num_threads(4);torch.manual_seed(seed);torch.use_deterministic_algorithms(True)

def head(config,tokenizer):return CodeReadout(config['features']*3+16,len(tokenizer),config['hidden'])

def reservoir(W,tokenizer,config,setting,recurrence=True):
    return CodingReservoir(W,len(tokenizer),seed=config['reservoir_seed'],features=config['features'],
        radius=config['radius']['radius'],recurrence=recurrence,**setting)

def cache(res,tokenizer,items,run,name):
    path=run/f'features-{name}.npz'
    start=time.perf_counter();xs=[];ys=[];ticks=0;offsets=[]
    for index,p in enumerate(items):
        inputs=tokenizer.encode(prompt(p));context=res.encode_prompt(inputs);ticks+=len(inputs)
        targets=tokenizer.encode(p['solution'])+[tokenizer.eos]
        offsets.append(dict(id=p['id'],start=len(ys),targets=len(targets)))
        for position,target in enumerate(targets):
            xs.append(res.feature(context,position));ys.append(target)
            if target!=tokenizer.eos:res.step(target);ticks+=1
        if index%8==0 or index+1==len(items):
            event(run,'feature_progress',arm=name,examples=index+1,total=len(items),ticks=ticks,seconds=time.perf_counter()-start)
    x=np.stack(xs);y=np.asarray(ys,np.int64)
    np.savez(path,x=x,y=y)
    receipt=dict(name=name,examples=len(items),targets=len(y),ticks=ticks,seconds=time.perf_counter()-start,
                 sha256=sha256(path),offsets=offsets)
    write_json(run/f'{name}-cache.json',receipt)
    return torch.from_numpy(x),torch.from_numpy(y)

def loss(model,data,vocab):
    total=0.;count=0
    with torch.no_grad():
        for x,y in zip(data[0].split(1024),data[1].split(1024)):
            total+=float(F.cross_entropy(model(x),y,reduction='sum'));count+=len(y)
    return total/count

def fit(train,validation,config,tokenizer,run,name,seed,steps):
    setup(seed);model=head(config,tokenizer)
    model.mean.copy_(train[0].mean(0));model.scale.copy_(train[0].std(0).clamp_min(.01))
    torch.save(model.state_dict(),run/f'{name}-initial.pt')
    optimizer=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=.01)
    generator=torch.Generator().manual_seed(seed+1000)
    start=time.perf_counter();history=[];best=math.inf;best_step=0
    for step in range(steps+1):
        if step:
            indices=torch.randint(len(train[1]),(512,),generator=generator)
            model.train();optimizer.zero_grad(set_to_none=True)
            value=F.cross_entropy(model(train[0][indices]),train[1][indices]);value.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(),1.);optimizer.step()
        if step%100==0 or step==steps:
            model.eval();tl=loss(model,train,len(tokenizer));vl=loss(model,validation,len(tokenizer))
            if not math.isfinite(tl+vl):raise ValueError('Nonfinite training loss')
            row=dict(step=step,train_loss=tl,validation_loss=vl,seconds=time.perf_counter()-start)
            history.append(row)
            if vl<best:
                best=vl;best_step=step;torch.save(model.state_dict(),run/f'{name}.pt')
            event(run,'loss',arm=name,**row)
            write_json(run/f'{name}-training.json',dict(history=history,best_step=best_step,best_validation_loss=best,
                parameters=parameter_count(model),updates=step,batch_size=512,solution_token_exposures=step*512,
                distinct_training_targets=len(train[1]),training_seconds=time.perf_counter()-start,
                seed=seed,checkpoint_sha256=sha256(run/f'{name}.pt')))
    model.load_state_dict(torch.load(run/f'{name}.pt',weights_only=True));model.eval()
    return model,best

@torch.no_grad()
def generate(res,model,tokenizer,p,ids,config,callback=None):
    start=time.perf_counter();context=res.encode_prompt(tokenizer.encode(prompt(p)))
    tokens=[];trace=[];stop='token_limit'
    for position in range(config['max_new_tokens']):
        feature=res.feature(context,position)
        token=int(model(torch.from_numpy(feature)).argmax())
        if token==tokenizer.eos:stop='eos';break
        tokens.append(token);res.step(token)
        if position%12==0:
            frame=dict(output_token=position,**res.activity(ids));trace.append(frame)
            if callback:callback(tokenizer.decode(tokens),frame)
        if sum(len(tokenizer.pieces[t]) for t in tokens)>=config['max_new_bytes']:stop='byte_limit';break
    raw=b''.join(tokenizer.pieces[t] for t in tokens)
    if len(raw)>config['max_new_bytes']:raw=raw[:config['max_new_bytes']]
    return dict(code=raw.decode('utf-8',errors='replace'),output_bytes=len(raw),output_tokens=len(tokens),
                stop_reason=stop,latency_seconds=time.perf_counter()-start,activity=trace)

def summary(rows):
    valid=[x for x in rows if x['judgement'].get('passed') is not None];n=len(valid);k=sum(x['judgement']['passed'] for x in valid)
    z=1.959963984540054
    if n:
        p=k/n;den=1+z*z/n;center=(p+z*z/(2*n))/den;half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
        interval=[max(0.,center-half),min(1.,center+half)]
    else:p=None;interval=None
    return dict(solved=k if n else None,total=n,attempted=len(rows),pass_at_1=p,interval_95=interval,
                interval_method='descriptive Wilson task interval; filtered development sample',
                mean_latency_seconds=sum(x['latency_seconds'] for x in valid)/n if n else None,
                valid_python=sum(x['judgement']['status'] not in ('syntax_error','unsupported','judge_error') for x in rows),
                outcomes={s:sum(x['judgement']['status']==s for x in rows) for s in sorted({x['judgement']['status'] for x in rows})})

def evaluate(res,model,tok,items,run,name,split,ids,config):
    rows=[];path=run/f'{name}-{split}-evaluation.json'
    for index,p in enumerate(items):
        result=generate(res,model,tok,p,ids,config)
        result.update(problem={k:p[k] for k in ('id','family','statement','source')},prompt=prompt(p),judgement=judge(result['code'],p['cases']))
        rows.append(result)
        report=dict(arm=name,split=split,results=rows,summary=summary(rows),completed=len(rows)==len(items),
                    benchmark='filtered MBPP' if split=='test' else 'seen-template unseen-constant transfer' if split=='transfer' else split,
                    checkpoint_sha256=sha256(run/f'{name}.pt') if (run/f'{name}.pt').exists() else None)
        write_json(path,report)
        event(run,'judged',arm=name,split=split,problem=p['id'],index=index+1,total=len(items),status=result['judgement']['status'])
    return report

def run_v2():
    setup(7)
    run=ROOT/'runs'/('curriculum-'+time.strftime('%Y%m%dT%H%M%S',time.gmtime()))
    run.mkdir(parents=True,exist_ok=False)
    train=load('train');validation=load('validation');test=load('test');transfer=load('transfer')
    rng=random.Random(20261009)
    test=rng.sample(test,24)
    cal_train=rng.sample([p for p in train if p['source']=='MBPP'],32)+rng.sample([p for p in train if p['source']!='MBPP'],32)
    cal_val=rng.sample([p for p in validation if p['source']=='MBPP'],8)+rng.sample([p for p in validation if p['source']!='MBPP'],8)
    train_probe=rng.sample([p for p in train if p['source']=='MBPP'],4)+rng.sample([p for p in train if p['source']!='MBPP'],4)
    tok=Tokenizer.fit([prompt(p) for p in train]+[p['solution'] for p in train]);tok.save(run/'tokenizer.json')
    config=dict(protocol='curriculum-v2',created_at=now(),reservoir_seed=7,seeds=[7,19],features=768,hidden=384,
        steps=1600,calibration_steps=400,max_new_tokens=192,max_new_bytes=2048,
        corpus=read_json(DIRECTORY/'manifest.json'),sources=source_hashes(),environment=environment(),
        tokenizer_sha256=sha256(run/'tokenizer.json'),protocol_sha256=sha256(ROOT/'docs/PROTOCOL_V2.md'),
        test_ids=[p['id'] for p in test],transfer_ids=[p['id'] for p in transfer],train_probe_ids=[p['id'] for p in train_probe],
        calibration_train_ids=[p['id'] for p in cal_train],calibration_validation_ids=[p['id'] for p in cal_val],
        training_count=len(train),validation_count=len(validation),label='development; fixed reservoir; two readout initialization seeds',
        checkpoint_selection='minimum full validation cross entropy',llm_baseline='deferred by user; no API calls')
    write_json(run/'config.json',config);write_json(run/'status.json',dict(state='running',phase='graph_loading',time=now()))
    (run/'source').mkdir()
    for name in config['sources']:shutil.copy2(ROOT/name,run/'source'/Path(name).name)
    shutil.copy2(ROOT/'docs/PROTOCOL_V2.md',run/'source/PROTOCOL_V2.md')
    for split in ['train','validation','test','transfer']:shutil.copy2(DIRECTORY/f'{split}.json',run/f'corpus-{split}.json')
    try:
        W,ids,graph=load_graph();write_json(run/'graph.json',graph)
        config['radius']=estimate_radius(W);write_json(run/'config.json',config)
        event(run,'graph_loaded',neurons=len(ids),edges=W.nnz,radius=config['radius'])
        candidates=[dict(target_radius=.9*config['radius']['radius']/graph['max_incoming_count'],leak=.5,input_scale=.35),
                    dict(target_radius=.9,leak=.5,input_scale=.1),dict(target_radius=.99,leak=.2,input_scale=.1)]
        write_json(run/'calibration-plan.json',candidates)
        trials=[]
        for i,setting in enumerate(candidates):
            name=f'calibration-{i}';res=reservoir(W,tok,config,setting)
            tr=cache(res,tok,cal_train,run,name+'-train');va=cache(res,tok,cal_val,run,name+'-validation')
            model,value=fit(tr,va,config,tok,run,name,7,config['calibration_steps'])
            trials.append(dict(name=name,setting=setting,validation_loss=value))
            write_json(run/'calibration-results.json',trials)
            del res,tr,va,model;gc.collect()
        selected=min(trials,key=lambda x:x['validation_loss'])
        config['selected_setting']=selected['setting'];config['selected_calibration']=selected['name']
        write_json(run/'config.json',config);event(run,'calibration_selected',**selected)
        # Frozen evaluation plan exists before full fits; no test performance enters selection.
        write_json(run/'evaluation-freeze.json',dict(time=now(),config_sha256=sha256(run/'config.json'),test_ids=config['test_ids'],
            selection=selected,protocol_sha256=config['protocol_sha256']))
        for arm,recurrence in [('fly',True),('no-recurrence',False)]:
            res=reservoir(W,tok,config,config['selected_setting'],recurrence)
            write_json(run/'status.json',dict(state='running',phase=arm+'_features',time=now()))
            tr=cache(res,tok,train,run,arm+'-train');va=cache(res,tok,validation,run,arm+'-validation')
            for seed in config['seeds']:
                name=f'{arm}-s{seed}'
                model,value=fit(tr,va,config,tok,run,name,seed,config['steps'])
                write_json(run/'status.json',dict(state='running',phase=name+'_evaluation',time=now()))
                evaluate(res,model,tok,train_probe,run,name,'train-reproduction',ids,config)
                evaluate(res,model,tok,transfer,run,name,'transfer',ids,config)
                evaluate(res,model,tok,test,run,name,'test',ids,config)
                if seed==config['seeds'][0]:
                    initial=head(config,tok);initial.load_state_dict(torch.load(run/f'{name}-initial.pt',weights_only=True));initial.eval()
                    evaluate(res,initial,tok,train_probe[:2]+transfer[:2]+test[:2],run,name+'-initial','learning-probe',ids,config)
                del model;gc.collect()
            del res,tr,va;gc.collect()
        load_graph(verify=True)
        write_json(run/'status.json',dict(state='completed',phase='curriculum_v2_complete',time=now(),graph_integrity='verified'))
        write_json(run/'artifacts.json',{p.name:sha256(p) for p in run.iterdir() if p.is_file() and p.name not in ('events.jsonl','artifacts.json')})
        write_json(ROOT/'runs/curriculum-latest.json',dict(run=run.name))
        event(run,'completed',run_id=run.name)
    except BaseException as exc:
        write_json(run/'status.json',dict(state='interrupted' if isinstance(exc,KeyboardInterrupt) else 'failed',time=now(),error=str(exc)))
        event(run,'failed',error=str(exc));raise
    return run

if __name__=='__main__':print(run_v2())
