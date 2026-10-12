"""Present all v2 seeds and split-specific scores, without changing old-run receipts."""
import json
from .common import ROOT,read_json,sha256

def latest_v2():
    index=ROOT/'runs/curriculum-latest.json'
    return ROOT/'runs'/read_json(index)['run'] if index.exists() else None

def problems(run,config):
    chosen=[]
    for split,ids in [('test',config['test_ids']),('transfer',config['transfer_ids']),('train',config['train_probe_ids'])]:
        rows={p['id']:p for p in read_json(run/f'corpus-{split}.json')}
        chosen.extend([{**rows[id],'evaluation_split':split} for id in ids])
    return chosen

def dashboard_v2(run):
    config=read_json(run/'config.json')
    data=dict(run=run.name,graph=read_json(run/'graph.json'),config=config,status=read_json(run/'status.json'),
              problems=[{k:p[k] for k in ('id','family','statement','source','evaluation_split')} for p in problems(run,config)],
              evaluations={},training={},scores=[],models=[],protocol='curriculum-v2')
    for arm in ['fly','no-recurrence']:
        for seed in config['seeds']:
            name=f'{arm}-s{seed}'
            data['models'].append(dict(id=name,label=f'{"Fly" if arm=="fly" else "No recurrence"} · seed {seed}'))
            records={}
            for split in ['test','transfer','train-reproduction']:
                path=run/f'{name}-{split}-evaluation.json'
                audited=run/'test-adequacy-audit'/path.name
                if audited.exists():path=audited
                if path.exists():records[split]=read_json(path)
            data['evaluations'][name]=dict(arm=name,results=[r for group in records.values() for r in group['results']],
                                           summary=records.get('test',{}).get('summary'))
            data['scores'].append(dict(arm=name,label=data['models'][-1]['label'],
                                       **{split:record['summary'] for split,record in records.items()}))
            path=run/f'{name}-training.json'
            if path.exists():data['training'][name]=read_json(path)
    events=run/'events.jsonl'
    data['events']=[json.loads(line) for line in events.read_text().splitlines()[-80:]]
    audit=run/'test-adequacy-audit/manifest.json'
    if audit.exists():data['test_audit']=read_json(audit)
    syntax_index=run/'syntax-audit-latest.json'
    if syntax_index.exists():
        syntax=read_json(run/read_json(syntax_index)['audit']/'results.json')
        # Full case arrays stay on disk; the UI needs verdicts, edits and one counterexample.
        for row in syntax['results']:
            for key in ['judgement','original_judgement']:
                row[key]={k:v for k,v in row[key].items() if k!='cases'}
        data['syntax_audit']=syntax
    return data

def interactive(run,request,W,ids,callback):
    import torch
    from .curriculum_model import Tokenizer
    from .curriculum_experiment import head,reservoir,generate,setup
    from .judge import judge
    config=read_json(run/'config.json');setup(7)
    arm=request.get('arm',f'fly-s{config["seeds"][0]}')
    allowed={f'{a}-s{s}' for a in ['fly','no-recurrence'] for s in config['seeds']}
    if arm not in allowed:raise ValueError('Unsupported v2 model')
    checkpoint=run/f'{arm}.pt';artifacts=read_json(run/'artifacts.json')
    if sha256(checkpoint)!=artifacts[checkpoint.name]:raise ValueError('Checkpoint integrity failure')
    if request.get('statement'):
        text=request['statement']
        if not isinstance(text,str) or len(text.encode())>600:raise ValueError('Custom statement must be at most 600 UTF-8 bytes')
        problem=dict(id='custom',family='user-supplied',statement=text,source='user',cases=[])
    else:
        problem=next((p for p in problems(run,config) if p['id']==request.get('problem')),None)
        if problem is None:raise ValueError('Unknown v2 problem')
    tok=Tokenizer.load(run/'tokenizer.json');res=reservoir(W,tok,config,config['selected_setting'],arm.startswith('fly'))
    model=head(config,tok);model.load_state_dict(torch.load(checkpoint,weights_only=True));model.eval()
    result=generate(res,model,tok,problem,ids,config,callback)
    from .curriculum_audit import stronger_cases
    result.update(arm=arm,problem={k:problem[k] for k in ('id','family','statement','source')},
                  judgement=judge(result['code'],stronger_cases(problem)) if problem['cases'] else dict(status='unscored',passed=None))
    return result
