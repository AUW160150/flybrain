"""Build a factual v2 report from saved artifacts; never invent a missing score."""
import json
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from flycodes.common import read_json,write_json,now,sha256
from flycodes.curriculum_dashboard import latest_v2,dashboard_v2

run=latest_v2()
if run is None:raise SystemExit('No completed curriculum run')
d=dashboard_v2(run);config=d['config']
lines=['# Expanded curriculum results','',f'Run: `{run.name}`. Generated from saved artifacts at {now()}.',
       '',f'Training increased from 12 to **{config["training_count"]} verified examples**. The fixed network still contains {d["graph"]["neurons"]:,} neurons and {d["graph"]["directed_edges"]:,} directed edges.',
       '', 'The pretrained LLM comparison was deferred as requested. No API calls were made in this experiment.',
       '', '| Model | Fresh MBPP subset | Unseen constants | Seen training examples | Readout parameters |',
       '|---|---:|---:|---:|---:|']
for score in d['scores']:
    values=[]
    for split in ['test','transfer','train-reproduction']:
        s=score.get(split);values.append(f'{s["solved"]}/{s["total"]}' if s and s['total'] else 'Not measured')
    lines.append('| '+score['label']+' | '+' | '.join(values)+f' | {d["training"][score["arm"]]["parameters"]:,} |')
if d.get('test_audit'):
    lines+=['', 'The table uses the stronger post-run tests for authored exercises. Original weak tests incorrectly counted three transfer solutions as passing in each seed-19 model. All three used incorrect constants. The audit preserves every original result and rejudges the same code without retraining or regeneration. This correction was made after inspecting outputs, not preregistered.',
            '', 'The added tests cover all lists of length 0–2 over integers −8 through 12, exact threshold neighbors, duplicates and longer lists. MBPP supplied tests remain unchanged. This follows the test-adequacy motivation of [EvalPlus (Liu et al., 2023)](https://arxiv.org/abs/2305.01210); it is a custom audit, not the EvalPlus benchmark. Full cases, original scores and corrected scores are saved under `test-adequacy-audit/`.']
lines+=['','MBPP uses 24 problems selected before training from the 209 judge-compatible official-test records. This is not the full MBPP benchmark or an official LeetCode score. Transfer means 30 new constants in the same ten authored templates, not unseen algorithms. Training reproduction uses eight already-seen problems. The two seeds change readout initialization and minibatches; they share one frozen reservoir/input mapping.',
        '', '## Validation-only calibration', '', '| Setting | Recurrent target radius | Leak | Input scale | Best validation loss |','|---|---:|---:|---:|---:|']
for trial in read_json(run/'calibration-results.json'):
    s=trial['setting'];lines.append(f'| {trial["name"]} | {s["target_radius"]:.6f} | {s["leak"]} | {s["input_scale"]} | {trial["validation_loss"]:.6f} |')
lines+=['',f'Selected `{config["selected_calibration"]}` using only calibration-validation cross entropy. The graph dominant eigenvalue estimate was {config["radius"]["radius"]:.4f}, with relative residual {config["radius"]["relative_residual"]:.3g}. Spectral scaling does not itself establish biological plausibility or an echo-state guarantee.',
        '', '## Learning evidence', '', '| Model | Initial train loss | Final train loss | Selected step | Best validation loss |','|---|---:|---:|---:|---:|']
for row in d['scores']:
    t=d['training'][row['arm']];lines.append(f'| {row["label"]} | {t["history"][0]["train_loss"]:.4f} | {t["history"][-1]["train_loss"]:.4f} | {t["best_step"]} | {t["best_validation_loss"]:.4f} |')
lines+=['', 'Every full-data head received 1,600 updates × 512 targets = 819,200 solution-token/EOS exposures. These repeatedly sample the same corpus, not independent examples. This total is per arm and per head seed. Calibration and feature collection add further cost, retained in their own receipts. No test outcomes selected a checkpoint.',
        '', '## Initial-head probe', '', 'The untrained readouts were evaluated on a fixed small mix of two training, two transfer and two test problems. This probe is separate from the headline denominators.', '']
for arm in ['fly','no-recurrence']:
    p=run/f'{arm}-s7-initial-learning-probe-evaluation.json'
    if p.exists():
        r=read_json(p);lines.append(f'- {arm}: {r["summary"]["solved"]}/{r["summary"]["total"]} passed with the untrained head.')
lines+=['','## Exact program evidence','', 'The following are actual generated programs, with their evaluation split. A training reproduction or familiar-template pass must not be presented as a new algorithm solution.']
for arm in ['fly-s7','fly-s19']:
    records=d['evaluations'][arm]['results'];passing=[r for r in records if r['judgement'].get('passed')]
    if passing:
        for r in passing[:3]:
            id=r['problem']['id'];split=next(p['evaluation_split'] for p in d['problems'] if p['id']==id)
            lines.extend(['',f'### {arm}: {id} ({split})', '',r['problem']['statement'],'','```python',r['code'].rstrip(),'```',
                          f'Passed {r["judgement"]["passed_cases"]}/{r["judgement"]["total_cases"]} evaluated cases.'])
    else:lines+=['',f'{arm}: no passing program in the evaluated sets.']
fly=[r for r in d['scores'] if r['arm'].startswith('fly')];controls=[r for r in d['scores'] if r['arm'].startswith('no-recurrence')]
lines+=['','## Interpretation','']
test_solved=sum(r['test']['solved'] or 0 for r in fly)
if test_solved:
    lines+=['The fly-plus-readout system generated programs that passed some fresh sampled MBPP tasks. This is evidence of task-specific functional success under the supplied tests. The control scores above determine whether there is any observed advantage from recurrent graph input; this small study does not establish a fly-specific advantage.']
else:
    lines+=['The fly-plus-readout system did not solve a fresh sampled MBPP task in either readout seed. Training or template-level gains, if present above, are not evidence of general coding ability.']
lines+=['', 'All graph data and count ratios remain unchanged. Prompt-context memory, lexical tokenization, the output clock and the nonlinear readout are artificial modeling additions shared with the control. Any success belongs to that complete system; the connectome alone is not a demonstrated code-writing biological brain.',
        '', 'The sampled MBPP tasks are now exposed evaluation data. Further model changes should use validation data and fresh final-test tasks. Real-world programming claims need larger independent tests, more than two head seeds, and eventually the separately measured pretrained reference.',
        '', 'See [PROTOCOL_V2.md](PROTOCOL_V2.md) for methodological sources and the pre-training plan. Full source and program artifacts are under the run directory; no test-selected solution repairs or replacements are used.']
(root/'docs/RESULTS_V2.md').write_text('\n'.join(lines)+'\n')
write_json(run/'report-summary.json',dict(created_at=now(),scores=d['scores'],report_sha256=sha256(root/'docs/RESULTS_V2.md')))
print(root/'docs/RESULTS_V2.md')
