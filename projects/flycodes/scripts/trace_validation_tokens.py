"""Locate the first departure from a reference under saved validation features."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import torch
from flycodes.common import ROOT,read_json,write_json,sha256,now
from flycodes.curriculum_dashboard import latest_v2
from flycodes.curriculum_experiment import setup,head
from flycodes.curriculum_model import Tokenizer

setup(7);run=latest_v2();config=read_json(run/'config.json');tok=Tokenizer.load(run/'tokenizer.json')
base=ROOT/'diagnostics'/read_json(ROOT/'diagnostics/latest-backtrace.json')['directory']
data=np.load(run/'features-fly-validation.npz');x=data['x'];y=data['y']
offsets=read_json(run/'fly-validation-cache.json')['offsets']
problems={p['id']:p for p in read_json(run/'corpus-validation.json')};rows=[]
for seed in [7,19]:
    model=head(config,tok);model.load_state_dict(torch.load(run/f'fly-s{seed}.pt',weights_only=True));model.eval()
    for o in offsets:
        xx=x[o['start']:o['start']+o['targets']];yy=y[o['start']:o['start']+o['targets']]
        with torch.no_grad():probabilities=torch.softmax(model(torch.from_numpy(xx)),dim=-1)
        predictions=probabilities.argmax(-1).numpy();different=np.flatnonzero(predictions!=yy)
        first=int(different[0]) if len(different) else len(yy)
        record=dict(seed=seed,problem=o['id'],statement=problems[o['id']]['statement'],reference_targets=len(yy),
                    correct_reference_prefix_tokens=first,teacher_forced_token_accuracy=float(np.mean(predictions==yy)))
        if first<len(yy):
            values,indices=probabilities[first].topk(5)
            display=lambda t:'<EOS>' if int(t)==tok.eos else tok.pieces[int(t)].decode('utf-8',errors='replace')
            record.update(prefix=tok.decode(yy[:first]),expected=display(yy[first]),chosen=display(predictions[first]),
                          expected_probability=float(probabilities[first,yy[first]]),
                          top5=[dict(token=display(t),probability=float(p)) for p,t in zip(values,indices)])
        rows.append(record)
result=dict(created_at=now(),source_sha256=sha256(Path(__file__)),rows=rows,
            interpretation='The first greedy divergence matches free generation because all prior tokens are equal to the reference. After that position, teacher-forced token accuracy is not free-running accuracy. Equivalent alternative programs can differ; divergence alone is not a logic failure.',
            summaries={str(seed):dict(examples=60,median_first_divergence=float(np.median([r['correct_reference_prefix_tokens'] for r in rows if r['seed']==seed])),reference_matched_completely=sum(r['correct_reference_prefix_tokens']==r['reference_targets'] for r in rows if r['seed']==seed)) for seed in [7,19]})
write_json(base/'validation-token-traces.json',result)
print(result['summaries'])
for r in rows:
    if r['seed']==7 and r['problem'].startswith('curr-'):
        print({k:v for k,v in r.items() if k not in ['top5']});break
