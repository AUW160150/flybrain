"""Render the audited development selection and next-stage record; no training."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/fly-lm-matplotlib')
from collections import Counter
from statistics import mean
from fly_connectome_lm.util import ROOT,read_json,atomic_json,sha256,code_hash,now
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

out=ROOT/'reports/development-review'; audit=read_json(out/'audit.json'); assert audit['status']=='passed'
selection=read_json(ROOT/'configs/development-selection.json'); records=read_json(out/'run-values.json')
freeze=read_json(ROOT/'configs/confirmation-frozen.json'); matrix=read_json(ROOT/'reports/confirmation-frozen-run-matrix.json')
conditions=['FLY-TOPOLOGY','DEGREE-REWIRED','RANDOM-DENSITY','PARAMETER-MATCHED-GRU','NO-CROSS-NODE-RECURRENCE']
means=[]
for lr in selection['grid']:
    for condition in conditions:
        rows=[r for r in records if r['lr']==lr and r['condition']==condition]
        means.append({'lr':lr,'condition':condition,'mean_best_validation_bpb':mean(r['validation_best']['bpb'] for r in rows),
                      'mean_final_validation_bpb':mean(r['validation_final']['bpb'] for r in rows),
                      'training_seeds':sorted(r['training_seed'] for r in rows)})
summary={'reviewed_utc':now(),'status':'complete_and_audited','development_runs':30,'condition_means':means,
         'selected_learning_rates':selection['learning_rates'],'selection_score_means':selection['pooled_validation_scores'],
         'training_byte_exposures':sum(r['training_byte_exposures'] for r in records),
         'training_seconds':sum(r['training_seconds'] for r in records),'validation_seconds':sum(r['validation_seconds'] for r in records),
         'checkpoint_steps':dict(Counter(r['selected_checkpoint_step'] for r in records)),
         'code_hash':code_hash(),'analysis_plan_sha256':sha256(ROOT/'docs/analysis_plan.md'),
         'selection_sha256':sha256(ROOT/'configs/development-selection.json'),
         'freeze_sha256':sha256(ROOT/'configs/confirmation-frozen.json'),
         'confirmation_run_count':35,'confirmation_prediction_bytes':716800000,
         'confirmation_started':False,'test_evaluated':False,
         'interpretation':'Development data selected hyperparameters only. No confirmatory topology inference or grid expansion.'}
atomic_json(out/'review-summary.json',summary)
lines=['# Development grid — audited validation-only results','',
'All 30 predeclared development trials completed: 3 learning rates × 2 development seeds (901/902) × 5 required conditions. Each consumed 2,000 updates and 1,024,000 prediction-byte exposures. No failed or missing trial was excluded. Total exposures: 30,720,000. No test evaluation was performed.',
'', '**Selected rate: 0.003 for the shared graph family and independently for the GRU.** The graph rate is selected from pooled FLY-TOPOLOGY and DEGREE-REWIRED validation over both seeds, then applied unchanged to A/B/C/E. Widths, anatomy, null policy and other settings are unchanged. It is the best rate in this fixed grid, not a claim of global optimality.',
'', '| Learning rate | Pooled fly + rewired best-validation BPB | GRU mean best-validation BPB |','|---|---:|---:|']
for lr in selection['grid']:
    scores=selection['pooled_validation_scores'];lines.append(f'| {lr} | {scores["graph"][str(lr)]:.6f} | {scores["PARAMETER-MATCHED-GRU"][str(lr)]:.6f} |')
lines+=['','No rates beyond the predeclared grid were tried. C/E do not receive separately optimized rates. Development seeds are excluded from confirmation estimates. These selected validation scores are not independent confirmation evidence.','',
'## Every condition and rate','', '| Rate | Condition | Mean best-validation BPB | Mean final-validation BPB |','|---|---|---:|---:|']
for r in means:lines.append(f'| {r["lr"]} | {r["condition"]} | {r["mean_best_validation_bpb"]:.6f} | {r["mean_final_validation_bpb"]:.6f} |')
fig,ax=plt.subplots(figsize=(8,5))
colors=['#1b7f3a','#ad5520','#3059b1','#8241a0','#697477']
for condition,color in zip(conditions,colors):
    rows=[r for r in means if r['condition']==condition]
    ax.plot([r['lr'] for r in rows],[r['mean_best_validation_bpb'] for r in rows],marker='o',color=color,label=condition)
ax.set(xscale='log',xlabel='Learning rate (fixed development grid)',ylabel='Mean best-validation bits per byte',title='Development only: seeds 901/902; lower is better')
ax.set_xticks(selection['grid'],[str(v) for v in selection['grid']]);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(out/'learning-rate-grid.png',dpi=160);plt.close(fig)
lines+=['','![Development grid](learning-rate-grid.png)','',
'## Audit','',
'- Matched every selection trial back to its run manifest, full history and checkpoint. Verified all 60 best/final checkpoint identities, exact budgets, validation schedules and checkpoint-selection minima.',
'- Recomputed the pooled selection scores and winners from run-level values. Replayed all best-checkpoint validation scores; separately replayed final checkpoints where different. All matched within 1e-6 BPB.',
'- Verified code/data/plan/graph hashes, exact labelled degrees and valid null-swap budgets, matching initial fly/null edge-slot weights, training-window RNG states, active parameter counts and finite losses/gradients. All graph cores changed. Graph realizations stayed the same across rates for each seed/condition.',
'- No test loader was invoked, and no test-result file exists. No training was launched during this review. Experiment source, presets, analysis plan and existing run artifacts were preserved.',
'',f'Aggregate logged training: {summary["training_seconds"]:.3f}s; validation: {summary["validation_seconds"]:.3f}s. The predeclared optional fixed-time budget, derived from pooled development profiling, is {selection["fixed_time_budget_seconds"]:.6f}s. The next stage remains the primary fixed-byte protocol; no fixed-time study ran.',
'', '[Audit](audit.json), [audit script](audit_development.py), [all run values](run-values.json), [machine-readable summary](review-summary.json).',
'', 'Per-rate reports: [0.0003](../development-63e04511192f/report.md), [0.001](../development-62e5665af1bf/report.md), [0.003](../development-61a97ac45aec/report.md).',
'', '## Frozen confirmation — not launched','',
'Created [confirmation-frozen.json](../../configs/confirmation-frozen.json) from the audited selection. Its hashes bind code, corpus, analysis plan, graph, selected rates, checkpoint-selection rule and exact run IDs. The preset base lr remains .001 for compatibility; frozen learning_rates override it to .003 in every resolved run, checked in the dry run.',
'', 'The exact matrix contains 35 untrained runs: confirmation seeds 11/22/33/44/55; one fly, three independently rewired nulls, one random-density, one GRU and one diagonal arm per seed. Each receives 20,000 updates, batch8/context128, totaling 20,480,000 prediction bytes per run and 716,800,000 over the matrix. Each fly is trained once. Test remains sealed throughout confirmation training.',
'',f'Freeze SHA-256: `{summary["freeze_sha256"]}`. Code SHA-256: `{code_hash()}`. Git revision: null (no Git repository). Plan SHA-256: `{summary["analysis_plan_sha256"]}`. Selection file SHA-256: `{summary["selection_sha256"]}`.',
'', '[Resolved confirmation matrix](../confirmation-frozen-run-matrix.json). Estimates exclude allocator/library overhead and are not runtime promises. The next command was dry-run checked but has not been executed:',
'', '```sh','./fly_connectome_lm/fly-lm run --config confirmation --freeze fly_connectome_lm/configs/confirmation-frozen.json','```','',
'This starts the full local confirmation training matrix. Final test evaluation is a separate explicit command after completion. One specimen, a local graph sample and a narrow corpus still limit interpretation; development scores must not be reported as confirmation results.']
(out/'report.md').write_text('\n'.join(lines)+'\n')

p=ROOT/'docs/STATUS.md'; status=p.read_text(); status=status.replace(status.splitlines()[2],f'Updated {now()}. This records completed work, not a proposed or unrun result.')
section=['## User-executed development grid — completed, audited and frozen','',
'The user ran `./fly_connectome_lm/fly-lm tune --config pilot`. All 30 development trials completed; selection written 2026-10-05T18:46:52Z. Seeds 901/902 and rates .0003/.001/.003 were used exactly as planned. Every arm trained to 2,000 updates (1,024,000 prediction bytes per run); 30,720,000 exposures total. No failed/missing trial was dropped.',
'', '| Learning rate | Pooled fly + rewired validation BPB | GRU validation BPB |','|---|---:|---:|']
for lr in selection['grid']:
    scores=selection['pooled_validation_scores'];section.append(f'| {lr} | {scores["graph"][str(lr)]:.6f} | {scores["PARAMETER-MATCHED-GRU"][str(lr)]:.6f} |')
section+=['', '**Selected common graph rate: .003; independently selected GRU rate: .003.** All A/B/C/E share the selected common rate. The fixed grid was not expanded. These are development selection values, not confirmatory topology evidence.',
'', 'Post-run audit passed for all 30 runs/60 best-final checkpoint identities. Replayed saved validation scores, matched histories and selection summaries, checked full budgets/schedules, active parameter counts, exact degree preservation, null policy, initial fly/null slot weights, learned-core changes, shared window RNG states, and hashes. No test loader used. No training launched by this review. The previous 31-pass/2-skip unit suite remains the latest suite result; code was unchanged, so it was not rerun.',
'', f'Logged training time {summary["training_seconds"]:.3f}s and validation {summary["validation_seconds"]:.3f}s. Optional secondary fixed-time budget derived from development is {selection["fixed_time_budget_seconds"]:.6f}s; that protocol has not run.',
'', 'Created `configs/confirmation-frozen.json` and validated the exact confirmation dry run. All 35 runs resolve lr .003 and remain untrained. Seeds11/22/33/44/55, three nulls per seed, 20,000 updates, batch8/context128; 716,800,000 prediction-byte exposures total. No default preset/source/analysis-plan changes. Test data remains sealed.',
'', f'Freeze SHA-256 `{summary["freeze_sha256"]}`. Code remains `{code_hash()}`. [Development report](../reports/development-review/report.md), [audit](../reports/development-review/audit.json), [selection](../configs/development-selection.json), [freeze](../configs/confirmation-frozen.json), [resolved confirmation matrix](../reports/confirmation-frozen-run-matrix.json).']
status=status.replace('## Unexecuted stages and blockers','\n'.join(section)+'\n\n## Unexecuted stages and blockers')
status=status.replace('The pilot is now complete. No development-grid corpus tuning, configuration freeze, confirmation, replication, fixed-time research or model test-set evaluation has run.', 'The pilot and development grid are complete and audited; the confirmation configuration is frozen. No confirmation training, replication, fixed-time research or model test-set evaluation has run.')
status=status.replace('No integrity blocker was found in the completed CPU pilot; the next planned stage is the development-only learning-rate grid.', 'No integrity blocker was found in the completed CPU pilot/development grid; the next planned stage is the frozen confirmation training matrix.')
status=status.replace('## Exact next command — development-only learning-rate grid (not launched)','## Exact next command — frozen confirmation training (not launched)')
status=status.replace('./fly_connectome_lm/fly-lm tune --config pilot\n```','./fly_connectome_lm/fly-lm run --config confirmation --freeze fly_connectome_lm/configs/confirmation-frozen.json\n```')
start='Run this only when you choose to start the next stage: 30 development runs, seeds 901/902, learning rates .0003/.001/.003, all five conditions with identical per-trial budgets. It saves configs/development-selection.json. The common graph rate is selected by pooled fly/rewired validation; GRU is selected separately. It never opens the test loader. Configuration freeze and confirmation remain later explicit stages.'
status=status.replace(start,'Run this only when you choose to start the full local confirmation matrix: 35 runs, 20,000 updates each, selected lr .003, with distinct confirmation seeds and three nulls per seed. It prints the matrix/estimates and does not evaluate test data. Final test scoring remains a separate explicit command after this training completes.')
p.write_text(status)
print('Development review and STATUS updated; confirmation frozen, no training launched.')
