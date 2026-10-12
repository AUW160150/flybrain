"""Can simple diagnostic readers recover the operation/constant from prompt states?

These readers are not the coding model and are never used to generate solutions.
Only existing train/validation authored-example prompt features are used.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from flycodes.common import ROOT,read_json,write_json,sha256,now
from flycodes.curriculum_dashboard import latest_v2

run=latest_v2();config=read_json(run/'config.json');f=config['features'];base=ROOT/'diagnostics'/read_json(ROOT/'diagnostics/latest-backtrace.json')['directory']
results={}
for arm in ['fly','no-recurrence']:
    rows=[]
    for split in ['train','validation']:
        features=np.load(run/f'features-{arm}-{split}.npz')['x']
        problems={p['id']:p for p in read_json(run/f'corpus-{split}.json')}
        for o in read_json(run/f'{arm}-{split}-cache.json')['offsets']:
            p=problems[o['id']]
            if p['source']!='authored_parameter_curriculum':continue
            family=p['family'];value=int(p['id'][len('curr-'+family+'-'):])
            rows.append(dict(id=p['id'],family=family,value=value,source_split=split,x=features[o['start'],f:3*f]))
    families=sorted({r['family'] for r in rows});values=sorted({r['value'] for r in rows});x=np.stack([r['x'] for r in rows]).astype(np.float64)
    probes={
        'operation_with_unseen_constants':dict(target='family',labels=families,
            train=[i for i,r in enumerate(rows) if r['source_split']=='train' and r['value'] not in [-1,3]],
            validation=[i for i,r in enumerate(rows) if r['value'] in [-1,3]],
            test=[i for i,r in enumerate(rows) if r['source_split']=='validation']),
        'constant_in_heldout_operation_families':dict(target='value',labels=values,
            train=[i for i,r in enumerate(rows) if r['family'] not in ['count-number','offset-length','sum-above']],
            validation=[i for i,r in enumerate(rows) if r['family']=='count-number'],
            test=[i for i,r in enumerate(rows) if r['family'] in ['offset-length','sum-above']])}
    results[arm]={}
    for name,p in probes.items():
        train=np.array(p['train']);val=np.array(p['validation']);test=np.array(p['test'])
        y=np.array([p['labels'].index(r[p['target']]) for r in rows]);target=np.eye(len(p['labels']))[y]
        mean=x[train].mean(0);scale=x[train].std(0).clip(1e-6);z=(x-mean)/scale
        center=target[train].mean(0);gram=z[train]@z[train].T/len(train);best=None;trials=[]
        for ridge in [1e-6,1e-4,.01,1.,100.]:
            dual=np.linalg.solve(gram+ridge*np.eye(len(train)),target[train]-center)
            weights=z[train].T@dual/len(train)
            pred=(z[val]@weights+center).argmax(1);accuracy=float(np.mean(pred==y[val]))
            trials.append(dict(ridge=ridge,validation_accuracy=accuracy))
            if best is None or accuracy>best[0]:best=(accuracy,ridge,weights)
        pred=(z[test]@best[2]+center).argmax(1)
        results[arm][name]=dict(classes=p['labels'],train_examples=len(train),validation_examples=len(val),test_examples=len(test),
            ridge=best[1],validation_trials=trials,test_accuracy=float(np.mean(pred==y[test])),
            test_predictions=[dict(id=rows[i]['id'],expected=p['labels'][y[i]],predicted=p['labels'][t]) for i,t in zip(test,pred)])
receipt=dict(created_at=now(),source_sha256=sha256(Path(__file__)),results=results,
    scope='Diagnostic linear classifiers on prompt-only context, not coding checkpoints. This measures available information and does not demonstrate code generation.',
    split='Operation probe holds out constants. Constant probe holds out operation families and deliberately sees every constant during its own training. Original code-training split is not claimed for this new probe.')
write_json(base/'prompt-information-probes.json',receipt)
for arm,probes in results.items():
    for name,r in probes.items():print(arm,name,r['test_accuracy'],r['test_examples'])
