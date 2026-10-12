"""Audit the fixed development grid and replay validation without accessing test data.
Run: PYTHONPATH=fly_connectome_lm/src .venv/bin/python fly_connectome_lm/reports/development-review/audit_development.py
"""
from pathlib import Path
from collections import Counter
import math
import numpy as np
import torch
from fly_connectome_lm.util import ROOT,read_json,atomic_json,sha256,digest,code_hash,now,setup,seed_for
from fly_connectome_lm.experiment import matrix,base_graph,resolved_graph,CORPUS
from fly_connectome_lm.models import build,accounting,GraphRNN,CONDITIONS
from fly_connectome_lm.graph_controls import degrees
from fly_connectome_lm.text_data import DevelopmentCorpus,WindowSampler
from fly_connectome_lm.evaluate import evaluate

selection_path=ROOT/'configs/development-selection.json'; selection=read_json(selection_path)
assert selection['status']=='complete' and selection['development_seeds']==[901,902]
assert selection['grid']==[.0003,.001,.003]
assert selection['code_hash']==code_hash()
assert selection['corpus_manifest_sha256']==sha256(CORPUS/'manifest.json')
setup('cpu',2); corpus=DevelopmentCorpus(CORPUS)
expected_sampler={}
for seed in [901,902]:
    sampler=WindowSampler(corpus.train,128,4,seed_for('data',seed))
    for _ in range(2000):sampler.next()
    expected_sampler[seed]=sampler.state_dict()
trials={(r['lr'],r['training_seed'],r['condition']):r for r in selection['trials']}
assert len(trials)==len(selection['trials'])==30
initials={}; graph_hashes={}; checks=[]; records=[]; bundles=[]
for bp in sorted((ROOT/'runs').glob('development-*.json')):
    bundle=read_json(bp); config=bundle['config']; lr=config['lr']; bundles.append({'path':str(bp.relative_to(ROOT)),'lr':lr,'sha256':sha256(bp)})
    assert config['profile']=='development' and config['training_seeds']==[901,902]
    assert config['sampling_seeds']==[101] and config['nulls_per_seed']==1
    assert bundle['analysis_plan']['sha256']==sha256(ROOT/'docs/analysis_plan.md')
    assert bundle['code_hash']==selection['code_hash'] and not bundle['synthetic']
    rows=matrix(config)
    assert [row['run_id'] for row in rows]==bundle['run_ids'] and len(rows)==10
    assert Counter((row['training_seed'],row['condition']) for row in rows)==Counter((seed,c) for seed in [901,902] for c in CONDITIONS)
    for row in rows:
        p=ROOT/'runs'/row['run_id']; m=read_json(p/'manifest.json');r=read_json(p/'result.json'); h=read_json(p/'history.json')
        seed=row['training_seed']; condition=row['condition']
        assert trials[(lr,seed,condition)]=={'lr':lr,**r}
        assert m['status']==r['status']=='complete' and not r['synthetic']
        assert m['code_hash']==r['code_hash']==code_hash()
        assert m['config']==row['config'] and r['config_hash']==digest(row['config'])
        assert m['signature']==digest({'config':m['config'],'metadata':m['metadata']})
        assert r['final_step']==2000 and r['training_byte_exposures']==1024000
        assert len(h)==2000 and [x['step'] for x in h]==list(range(1,2001))
        assert all(math.isfinite(x['train_nll']) and math.isfinite(x['gradient_norm_before_clip']) for x in h)
        vals=[x for x in h if 'validation' in x]
        assert [x['step'] for x in vals]==list(range(100,2001,100))
        assert all(x['validation']['scored_bytes']==55769 for x in vals)
        best=min(vals,key=lambda x:x['validation']['bpb'])
        assert best['step']==r['selected_checkpoint_step'] and best['validation']==r['validation_best']
        assert vals[-1]['validation']==r['validation_final']
        graph=resolved_graph(row,base_graph(config,101)); assert graph.hash==r['graph_hash']==m['metadata']['graph_hash']
        model=build(condition,graph,row['config'],seed)
        assert accounting(model)==r['accounting']==row['accounting']
        graph_hashes[(lr,seed,condition)]=graph.hash
        checkpoints={k:torch.load(p/f'{k}.pt',map_location='cpu',weights_only=False) for k in ['best','final']}
        replays={}
        for kind,cp in checkpoints.items():
            assert cp['signature']==m['signature'] and cp['code_hash']==code_hash()
            assert cp['step']==(best['step'] if kind=='best' else 2000)
            assert all(torch.isfinite(v).all() for v in cp['model'].values())
            if isinstance(model,GraphRNN):
                assert torch.equal(model.source,cp['model']['source']) and torch.equal(model.target,cp['model']['target'])
            model.load_state_dict(cp['model'])
            if kind=='best' or best['step']!=2000:
                score=evaluate(model,corpus.validation,128,32)
                logged=r['validation_best' if kind=='best' else 'validation_final']
                difference=abs(score['bpb']-logged['bpb']); assert difference<1e-6
                replays[kind]={'bpb':score['bpb'],'absolute_bpb_difference':difference}
            else:
                assert all(torch.equal(cp['model'][k],checkpoints['best']['model'][k]) for k in cp['model'])
                replays[kind]={'same_model_as_replayed_best':True}
        cp=checkpoints['final']; assert cp['sampler']==expected_sampler[seed]
        if isinstance(model,GraphRNN):
            assert any((x['edge_gradient_norm'] or 0)>0 for x in h)
            change=(cp['model']['theta']-cp['initial_theta']).norm().item()
            assert change==r['core_weight_change_l2'] and change>0
            initial=build(condition,graph,row['config'],seed)
            assert torch.equal(cp['initial_theta'],initial.theta.detach())
            initials[(lr,seed,condition)]=cp['initial_theta']
        if condition=='DEGREE-REWIRED':
            for a,b in zip(degrees(base_graph(config,101)),degrees(graph)):np.testing.assert_array_equal(a,b)
            control=graph.metadata['randomization'];assert control['valid'] and control['accepted_swaps']==61220 and control['proposals']<=500*3061
        records.append({'run_id':row['run_id'],'lr':lr,**r})
        checks.append({'run_id':row['run_id'],'status':'passed','validation_replay':replays,
                       'checkpoint_sha256':{kind:sha256(p/f'{kind}.pt') for kind in checkpoints}})
assert len(checks)==30 and len(bundles)==3
for seed in [901,902]:
    for lr in selection['grid']:
        assert torch.equal(initials[(lr,seed,'FLY-TOPOLOGY')],initials[(lr,seed,'DEGREE-REWIRED')])
    for condition in CONDITIONS:
        assert len({graph_hashes[(lr,seed,condition)] for lr in selection['grid']})==1
scores={}
for name,conditions in [('graph',{'FLY-TOPOLOGY','DEGREE-REWIRED'}),('PARAMETER-MATCHED-GRU',{'PARAMETER-MATCHED-GRU'})]:
    scores[name]={}
    for lr in selection['grid']:
        values=[r['validation_best']['bpb'] for r in records if r['condition'] in conditions and r['lr']==lr]
        assert len(values)==2*len(conditions)
        scores[name][str(lr)]=float(np.mean(values))
        assert abs(scores[name][str(lr)]-selection['pooled_validation_scores'][name][str(lr)])<1e-12
    winner=min(selection['grid'],key=lambda lr:(scores[name][str(lr)],lr))
    assert winner==selection['learning_rates'][name]
budget=float(np.mean([r['training_seconds']/r['final_step'] for r in records])*2000)
assert abs(budget-selection['fixed_time_budget_seconds'])<1e-10
output=ROOT/'reports/development-review'
atomic_json(output/'audit.json',{'status':'passed','reviewed_utc':now(),'code_hash':code_hash(),
    'selection_sha256':sha256(selection_path),'bundles':bundles,'runs':checks,'completed_runs':30,
    'training_bytes':sum(r['training_byte_exposures'] for r in records),'selection_recomputed':scores,
    'learning_rates':selection['learning_rates'],'fixed_time_budget_seconds_recomputed':budget,
    'test_data_loaded':False,'test_result_files_found':len(list((ROOT/'runs').rglob('test.json'))),
    'training_launched':False,'audit_script_sha256':sha256(Path(__file__)),
    'matched_controls':'Exact labelled degrees, edge count, initial edge slots and final sampler RNG states verified; graph realization shared across rates'})
atomic_json(output/'run-values.json',records)
print('PASS: 30 development runs, 60 checkpoint identities, full budgets, validation replay and predeclared rate selection verified; no test loader used.')
