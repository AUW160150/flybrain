"""Post-run integrity audit and deterministic validation replay; never loads test bytes.
Run from workspace root: PYTHONPATH=fly_connectome_lm/src .venv/bin/python fly_connectome_lm/reports/pilot-f66c5c98ba1e/audit_pilot.py
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

bundle_path=ROOT/'runs/pilot-f66c5c98ba1e.json'
bundle=read_json(bundle_path); config=bundle['config']; setup(config['device'],config['threads'])
assert bundle['profile']=='pilot' and not bundle['synthetic']
assert bundle['code_hash']==code_hash()
assert bundle['analysis_plan']['sha256']==sha256(ROOT/'docs/analysis_plan.md')
assert bundle['corpus_manifest_sha256']==sha256(CORPUS/'manifest.json')
rows=matrix(config)
assert [row['run_id'] for row in rows]==bundle['run_ids']
assert len(rows)==15 and all(row['already_complete'] for row in rows)
assert Counter((row['training_seed'],row['condition']) for row in rows)==Counter((seed,c) for seed in [1,2,3] for c in CONDITIONS)
corpus=DevelopmentCorpus(CORPUS)
expected_sampler={}
for seed in [1,2,3]:
    sampler=WindowSampler(corpus.train,128,4,seed_for('data',seed))
    for _ in range(2000): sampler.next()
    expected_sampler[seed]=sampler.state_dict()
initials={}; checks=[]; errors=[]
for row in rows:
    path=ROOT/'runs'/row['run_id']; m=read_json(path/'manifest.json'); r=read_json(path/'result.json'); h=read_json(path/'history.json')
    assert m['status']==r['status']=='complete'
    assert m['code_hash']==r['code_hash']==bundle['code_hash']
    assert m['config']==row['config'] and r['config_hash']==digest(row['config'])
    assert m['signature']==digest({'config':m['config'],'metadata':m['metadata']})
    assert r['final_step']==2000 and r['training_byte_exposures']==1024000 and len(h)==2000
    assert [x['step'] for x in h]==list(range(1,2001))
    assert all(math.isfinite(x['train_nll']) and math.isfinite(x['gradient_norm_before_clip']) for x in h)
    validations=[x for x in h if 'validation' in x]
    assert [x['step'] for x in validations]==list(range(100,2001,100))
    chosen=min(validations,key=lambda x:x['validation']['bpb'])
    assert chosen['step']==r['selected_checkpoint_step'] and chosen['validation']==r['validation_best']
    assert validations[-1]['validation']==r['validation_final']
    assert all(x['validation']['scored_bytes']==55769 for x in validations)
    graph=resolved_graph(row,base_graph(config,101)); assert graph.hash==r['graph_hash']==m['metadata']['graph_hash']
    model=build(row['condition'],graph,row['config'],row['training_seed'])
    assert accounting(model)==r['accounting']==row['accounting']
    checkpoints={kind:torch.load(path/f'{kind}.pt',map_location='cpu',weights_only=False) for kind in ['best','final']}
    replay={}
    for kind,checkpoint in checkpoints.items():
        assert checkpoint['signature']==m['signature'] and checkpoint['code_hash']==bundle['code_hash']
        assert checkpoint['step']==(r['selected_checkpoint_step'] if kind=='best' else 2000)
        assert all(torch.isfinite(v).all() for v in checkpoint['model'].values())
        if isinstance(model,GraphRNN):
            assert torch.equal(model.source,checkpoint['model']['source'])
            assert torch.equal(model.target,checkpoint['model']['target'])
        model.load_state_dict(checkpoint['model'])
        if kind=='best' or r['selected_checkpoint_step']!=2000:
            scored=evaluate(model,corpus.validation,128,32)
            logged=r['validation_best' if kind=='best' else 'validation_final']
            difference=abs(scored['bpb']-logged['bpb']); assert difference<1e-6
            assert scored['scored_bytes']==logged['scored_bytes']==55769
            replay[kind]={'bpb':scored['bpb'],'absolute_bpb_difference':difference}
        else:
            assert all(torch.equal(checkpoint['model'][k],checkpoints['best']['model'][k]) for k in checkpoint['model'])
            replay[kind]={'same_model_as_replayed_best':True}
    final=checkpoints['final']; assert final['sampler']==expected_sampler[row['training_seed']]
    if isinstance(model,GraphRNN):
        assert any((x['edge_gradient_norm'] or 0)>0 for x in h)
        change=(final['model']['theta']-final['initial_theta']).norm().item()
        assert change==r['core_weight_change_l2'] and change>0
        initial=build(row['condition'],graph,row['config'],row['training_seed'])
        assert torch.equal(final['initial_theta'],initial.theta.detach())
        initials[(row['training_seed'],row['condition'])]=final['initial_theta']
    if row['condition']=='DEGREE-REWIRED':
        original=base_graph(config,101)
        for a,b in zip(degrees(original),degrees(graph)): np.testing.assert_array_equal(a,b)
        randomization=graph.metadata['randomization']; assert randomization['valid'] and randomization['accepted_swaps']==20*3061
    checks.append({'run_id':row['run_id'],'condition':row['condition'],'training_seed':row['training_seed'],
                   'best_step':r['selected_checkpoint_step'],'checkpoint_sha256':{kind:sha256(path/f'{kind}.pt') for kind in checkpoints},
                   'validation_replay':replay,'matched_sampler':True,'status':'passed'})
for seed in [1,2,3]:
    assert torch.equal(initials[(seed,'FLY-TOPOLOGY')],initials[(seed,'DEGREE-REWIRED')])
result={'status':'passed','reviewed_utc':now(),'bundle_sha256':sha256(bundle_path),'code_hash':code_hash(),
        'completed_runs':15,'training_byte_exposures':15*1024000,'checks':checks,
        'test_data_loaded':False,'test_result_files_found':len(list((ROOT/'runs').rglob('test.json'))),
        'training_launched':False,'audit_script_sha256':sha256(Path(__file__)),
        'matched_controls':'Exact labelled degrees, count, initial edge slots and final sampler RNG states verified',
        'metric_check':'All best-checkpoint validation metrics replayed; final separately replayed when selected step differed'}
atomic_json(ROOT/'reports/pilot-f66c5c98ba1e/audit.json',result)
print('PASS: 15 complete runs, 30 checkpoint identities, matched budgets/data RNGs/edge slots/degrees, and validation replay; no test loader used.')
