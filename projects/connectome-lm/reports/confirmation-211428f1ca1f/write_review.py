"""Summarize audited confirmation validation; never opens test data or trains."""
from collections import Counter
from datetime import datetime
from pathlib import Path
import numpy as np
from fly_connectome_lm.util import ROOT, read_json, atomic_json, now
from fly_connectome_lm.statistics import paired_effects
from fly_connectome_lm.report import plt, COLORS

out = Path(__file__).resolve().parent
audit = read_json(out / 'audit.json')
assert audit['status'] == 'passed' and audit['completed_runs'] == 35 and not audit['test_data_loaded']
rows = read_json(out / 'run-values.json')
conditions = ['FLY-TOPOLOGY', 'DEGREE-REWIRED', 'RANDOM-DENSITY', 'PARAMETER-MATCHED-GRU', 'NO-CROSS-NODE-RECURRENCE']
summary = []
for condition in conditions:
    group = [r for r in rows if r['condition'] == condition]
    summary.append({'condition': condition, 'runs': len(group),
                    'active_parameters': group[0]['accounting']['active_trainable_parameters'],
                    'mean_best_validation_bpb': float(np.mean([r['validation_best']['bpb'] for r in group])),
                    'mean_final_validation_bpb': float(np.mean([r['validation_final']['bpb'] for r in group])),
                    'mean_training_seconds': float(np.mean([r['training_seconds'] for r in group]))})
stats = paired_effects([{**r, 'bpb': r['validation_best']['bpb']} for r in rows], 3)
assert not stats['incomplete_pairs'] and len(stats['pairs']) == 5
stats['analysis_stage'] = 'Validation only; checkpoints selected on these data. Primary test outcome not evaluated.'
for group in stats['per_graph'].values():
    group['interpretation'] = 'Descriptive validation comparison only; no confirmatory test inference.'
atomic_json(out / 'validation-paired-effects.json', stats)
manifests = [read_json(ROOT / 'runs' / r['run_id'] / 'manifest.json') for r in rows]
started = min(m['started_utc'] for m in manifests)
finished = max(r['completed_utc'] for r in rows)
timing = {'started_utc': started, 'completed_utc': finished,
          'wall_seconds': (datetime.fromisoformat(finished) - datetime.fromisoformat(started)).total_seconds(),
          'training_seconds': sum(r['training_seconds'] for r in rows),
          'validation_seconds': sum(r['validation_seconds'] for r in rows)}
selected = dict(sorted(Counter(r['selected_checkpoint_step'] for r in rows).items()))
next_command = './fly_connectome_lm/fly-lm final-evaluate --freeze fly_connectome_lm/configs/confirmation-frozen.json'
atomic_json(out / 'review-summary.json', {
    'stage': 'confirmation training complete; validation audited; test sealed', 'reviewed_utc': now(),
    'condition_summaries': summary, 'validation_paired_effects': stats, 'timing': timing,
    'selected_checkpoint_steps': selected, 'total_training_byte_exposures': 716800000,
    'test_evaluation_performed': False, 'training_launched_by_review': False,
    'audit': 'audit.json', 'next_command': next_command})
fig, ax = plt.subplots(figsize=(7, 4))
pairs = stats['pairs']
ax.scatter([p['training_seed'] for p in pairs], [p['delta'] for p in pairs], color=COLORS['FLY-TOPOLOGY'])
ax.axhline(0, color='black', linewidth=.8)
ax.axhline(.02, color='gray', linestyle='--', label='Predeclared practical threshold +0.02')
ax.set(xticks=[p['training_seed'] for p in pairs], xlabel='Training seed',
       ylabel='Mean rewired BPB minus fly BPB', title='Validation only: paired effects after full training')
ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(out / 'validation-paired-effects.png', dpi=160); plt.close(fig)
effect = stats['per_graph']['101']
lines = [
    '# Completed confirmation training — validation review', '',
    'All 35 runs completed and passed the post-run integrity audit. The test set has not been evaluated. '
    'These validation scores selected the checkpoints, so they are not the predeclared primary test outcome.', '',
    f'Execution: {started} to {finished}; {timing["wall_seconds"]/3600:.3f} hours wall time. '
    'Real male-cns:v1.0, sample101, N512/E3061; five training seeds11/22/33/44/55, three independently rewired controls each.', '',
    'Every run trained 20,000 updates at batch8/context128 and selected lr .003: 20,480,000 prediction-byte exposures per run, '
    '716,800,000 total. Unique training corpus: 1,003,854 bytes. CPU float32/dense execution, two threads.', '',
    '| Condition | Runs | Active parameters | Mean best-validation BPB | Mean final-validation BPB | Mean training seconds |',
    '|---|---:|---:|---:|---:|---:|']
for s in summary:
    lines.append(f'| {s["condition"]} | {s["runs"]} | {s["active_parameters"]} | '
                 f'{s["mean_best_validation_bpb"]:.6f} | {s["mean_final_validation_bpb"]:.6f} | {s["mean_training_seconds"]:.3f} |')
lines += ['', 'Lower BPB is better. Rewired controls have lower mean validation BPB than fly topology; GRU is lowest. '
          'This validation comparison provides no fly-wiring advantage. It does not establish the final held-out result.', '',
          '| Training seed | Fly validation BPB | Mean of three rewired validation BPBs | Rewired minus fly |',
          '|---|---:|---:|---:|']
for p in pairs:
    lines.append(f'| {p["training_seed"]} | {p["fly_bpb"]:.6f} | {np.mean(p["rewired_bpbs"]):.6f} | {p["delta"]:+.6f} |')
lines += ['', f'Descriptive paired validation mean: {effect["mean_delta"]:+.6f} BPB; '
          f'95% percentile interval [{effect["ci95"][0]:+.6f}, {effect["ci95"][1]:+.6f}]. '
          '10,000 resamples of the five seed-level differences, after averaging each seed\'s three controls. '
          'Five seeds provide limited uncertainty; reused fly runs are not treated as independent observations. '
          'The interval is descriptive validation analysis, not a primary test result.', '',
          '![Validation paired effects](validation-paired-effects.png)', '',
          'Audit passed: frozen code/plan/corpus/graph/run identities; full budgets and validation schedules; '
          'all 70 best/final checkpoint identities; replayed validation metrics (all differences below 1e-6); '
          'exact labelled degrees and swap policy; matched initial recurrent slots and interfaces; optimizer settings; '
          'final training-window RNG states; finite losses and changed recurrent weights.', '',
          f'Selected steps: {selected}. Every run still consumed its full budget. '
          '28/35 selected an earlier checkpoint than step20,000; final checkpoint scores are reported separately. '
          'No training recipe, code, analysis plan, graph sample or checkpoint-selection rule was changed.', '',
          f'Training time {timing["training_seconds"]:.3f}s; validation {timing["validation_seconds"]:.3f}s. '
          'Equal parameter counts and training bytes do not imply equal compute. The GRU was faster in this CPU implementation.', '',
          'Limitations: one locally sampled subgraph from one specimen; mostly visual neurons; approximately 92% of external '
          'filtered connectivity cut; dense artificial interfaces and unrestricted learned signs; one small text corpus; '
          'degree preservation does not prove uniform null mixing. No biological learning or general-language superiority claim.', '',
          f'Code SHA-256: `{audit["code_hash"]}`. Freeze file SHA-256: `{audit["freeze_sha256"]}`. '
          f'Analysis plan SHA-256: `{audit["analysis_plan_sha256"]}`. No Git revision available.', '',
          'No retraining, test evaluation, paid compute, replication or optional intervention/text-generation diagnostics '
          'were launched in this review. The unchanged source retains its prior unit-test result (31 passed, 2 accelerator skips); '
          'this follow-up added and passed the artifact/validation audit.', '',
          'Full run values and plots: [generated report](report.md). '
          'Audit: [audit.json](audit.json), [audit source](audit_confirmation.py). '
          'Machine-readable review: [review-summary.json](review-summary.json).', '',
          'Next command, from `/Users/Rodela1/Code/Flybrain`, explicitly scores the frozen best and final checkpoints '
          'on the held-out test set; it does not retrain or select new checkpoints:', '',
          '```sh', next_command, '```']
(out / 'validation-review.md').write_text('\n'.join(lines) + '\n')
print(out / 'validation-review.md')
