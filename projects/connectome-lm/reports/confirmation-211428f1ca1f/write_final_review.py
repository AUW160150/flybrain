"""Write the completed frozen test comparison and separately labelled diagnostics."""
from collections import Counter
from pathlib import Path
import numpy as np
from fly_connectome_lm.util import ROOT, read_json, atomic_json, sha256, now

out = Path(__file__).resolve().parent
audit = read_json(out / 'final-audit.json')
assert audit['status'] == 'passed' and audit['completed_test_runs'] == 35
test = read_json(ROOT / 'reports/final-evaluation-ffb133aefbbd.json')
effects = read_json(out / 'final-test-effects.json')
training = {r['run_id']: r for r in read_json(out / 'run-values.json')}
diagnostics = read_json(out / 'validation-diagnostics-review.json')
assert diagnostics['status'] == 'complete' and len(diagnostics['records']) == 35
assert {r['run_id'] for r in diagnostics['records']} == set(training)
assert len({r['diagnostics']['sample']['prompt_hex'] for r in diagnostics['records']}) == 1
for record in test['records']:
    assert sha256(ROOT / 'runs' / record['run_id'] / 'test.json') == audit['test_artifact_sha256'][record['run_id']]
for record in diagnostics['records']:
    assert len(bytes.fromhex(record['diagnostics']['sample']['prompt_hex'])) == 32
    assert record['diagnostics']['sample']['length_bytes'] == 128
    assert record['diagnostics']['sample']['temperature'] == .8
    assert record['checkpoint_sha256'] == test['records'][[r['run_id'] for r in test['records']].index(record['run_id'])]['checkpoint_sha256']['best']
for seed in [11, 22, 33, 44, 55]:
    assert len({r['diagnostics']['sample']['sampling_seed'] for r in diagnostics['records'] if r['training_seed'] == seed}) == 1
conditions = ['FLY-TOPOLOGY', 'DEGREE-REWIRED', 'RANDOM-DENSITY', 'PARAMETER-MATCHED-GRU', 'NO-CROSS-NODE-RECURRENCE']
summaries, intervention_summaries = [], []
for condition in conditions:
    group = [r for r in test['records'] if r['condition'] == condition]
    summaries.append({'condition': condition, 'runs': len(group),
                      'parameters': training[group[0]['run_id']]['accounting']['active_trainable_parameters'],
                      'mean_test_bpb_validation_selected': float(np.mean([r['best']['bpb'] for r in group])),
                      'mean_test_bpb_final_checkpoint': float(np.mean([r['final']['bpb'] for r in group])),
                      'mean_byte_perplexity_validation_selected': float(np.mean([r['best']['byte_perplexity'] for r in group])),
                      'mean_accuracy_validation_selected': float(np.mean([r['best']['accuracy'] for r in group]))})
    ds = [r['diagnostics'] for r in diagnostics['records'] if r['condition'] == condition]
    item = {'condition': condition, 'runs': len(ds), 'baseline_validation_bpb': float(np.mean([r['baseline_validation']['bpb'] for r in ds]))}
    for key in ['zero_core', 'reset_each_byte', 'perturb_10_percent']:
        values = [r[key]['bpb'] for r in ds if key in r and 'bpb' in r[key]]
        item[key] = float(np.mean(values)) if values else None
    intervention_summaries.append(item)
primary = effects['best']['per_graph']['101']
secondary = effects['final']['per_graph']['101']
conclusion = ('No fly-topology advantage is established under this frozen experiment. The mean favors degree-preserving rewiring, '
              'but the 95% paired bootstrap interval includes zero, so a clear disadvantage is also not established. '
              'This is not proof of equality or a result about biological learning.')
summary = {'stage': 'confirmation final test complete and audited', 'reviewed_utc': now(),
           'condition_summaries': summaries, 'primary_test_contrast': effects['best'],
           'secondary_final_checkpoint_contrast': effects['final'], 'conclusion': conclusion,
           'validation_interventions': intervention_summaries, 'diagnostic_records': len(diagnostics['records']),
           'test_scoring_completed_utc': max(r['evaluated_utc'] for r in test['records']),
           'test_audit': 'final-audit.json', 'test_predictions_replayed_by_review': False,
           'training_launched_by_review': False, 'replication_launched': False,
           'source_code_hash': audit['code_hash'], 'freeze_sha256': audit['freeze_sha256']}
atomic_json(out / 'final-review-summary.json', summary)
lines = ['# Final confirmation result — frozen held-out test', '', conclusion, '',
         'All 35 test records are complete: five training seeds, with one fly model and three independently rewired controls '
         'per seed, plus random-density, GRU and diagonal-memory baselines. The experiment used a real MaleCNS v1.0 '
         '512-neuron/3,061-edge subgraph (sampling seed101) and Tiny Shakespeare, with the predeclared contiguous 90/5/5 split.', '',
         'Primary scores below use the checkpoint chosen by validation before test access. Final-step checkpoints are '
         'reported separately; no checkpoint was selected using test performance. Each checkpoint scored the same 55,769 '
         'test prediction positions, with 128-position blocks, state reset and a masked tail. Lower BPB is better.', '',
         '| Condition | Runs | Active parameters | Mean primary test BPB | Mean final-step test BPB | Mean byte perplexity | Mean accuracy |',
         '|---|---:|---:|---:|---:|---:|---:|']
for r in summaries:
    lines.append(f'| {r["condition"]} | {r["runs"]} | {r["parameters"]} | {r["mean_test_bpb_validation_selected"]:.6f} | '
                 f'{r["mean_test_bpb_final_checkpoint"]:.6f} | {r["mean_byte_perplexity_validation_selected"]:.4f} | '
                 f'{r["mean_accuracy_validation_selected"]:.4%} |')
lines += ['', 'Mean byte perplexity is the arithmetic mean of individual run perplexities, not exponentiated mean BPB. '
          'GRU has the lowest mean test BPB; these additional architecture comparisons are secondary and have different compute costs.', '',
          '## Predeclared primary comparison', '',
          'For each training seed: average the three rewired BPBs, then subtract the single fly BPB. Positive favors fly.', '',
          '| Seed | Fly test BPB | Mean rewired test BPB | Rewired minus fly |', '|---|---:|---:|---:|']
for p in effects['best']['pairs']:
    lines.append(f'| {p["training_seed"]} | {p["fly_bpb"]:.6f} | {np.mean(p["rewired_bpbs"]):.6f} | {p["delta"]:+.6f} |')
lines += ['', f'**Mean delta: {primary["mean_delta"]:+.6f} BPB. 95% paired bootstrap interval: '
          f'[{primary["ci95"][0]:+.6f}, {primary["ci95"][1]:+.6f}].** '
          '10,000 seed-level resamples, seed1729. Four seed-level means favor rewiring; one favors fly. '
          'The interval includes zero and does not support the predeclared +0.02 BPB practical fly advantage. '
          'Only five training seeds inform this interval; it does not estimate variation across animals or graph samples.', '',
          f'Secondary final-step contrast: {secondary["mean_delta"]:+.6f} BPB, interval '
          f'[{secondary["ci95"][0]:+.6f}, {secondary["ci95"][1]:+.6f}]. This does not replace the primary selection rule.', '',
          '![Paired primary test effects](paired-effects.png)', '',
          'Train-only additive-smoothed references (not parameter matched): '
          f'unigram test BPB {test["train_only_ngram_test"]["unigram"]["bpb"]:.6f}; '
          f'bigram {test["train_only_ngram_test"]["bigram"]["bpb"]:.6f}.', '',
          '## Integrity and execution', '',
          'The final audit checked the exact complete frozen matrix, all 70 checkpoint identities against hashes recorded '
          'before test access, validation-selected steps, score arithmetic, test-record/summary agreement, and an independent '
          'recalculation of the paired bootstrap. Test inference was performed by the user\'s explicit final-evaluate command; '
          'this review used its immutable artifacts and did not repeat test inference. The preceding audit replayed validation '
          'and verified degrees, initial interfaces/edge slots, training-window RNGs, learned recurrent weights and full budgets.', '',
          'Every model trained 20,000 updates, batch8/context128, lr .003, CPU float32 with two threads: 20,480,000 prediction-byte '
          'exposures per run, 716,800,000 total. No failed or missing runs were dropped. Training wall time was 4.462 hours. '
          'Equal parameter counts and bytes do not mean equal compute; GRU averaged 141.305 training seconds versus 508.623 for fly.', '',
          '## Predeclared validation-only dependence checks', '',
          'The fixed checks below were applied to copies of every validation-selected model after the main experiment. '
          'No checkpoint, graph, hyperparameter or test score was changed. Higher BPB after intervention measures dependence '
          'on the trained recurrence; damaging parameters is not evidence of a special anatomical benefit.', '',
          '| Condition | Baseline validation BPB | Zero core | Reset every byte | Zero fixed 10% of coefficients |',
          '|---|---:|---:|---:|---:|']
for r in intervention_summaries:
    perturbed = f'{r["perturb_10_percent"]:.6f}' if r['perturb_10_percent'] is not None else 'n/a'
    lines.append(f'| {r["condition"]} | {r["baseline_validation_bpb"]:.6f} | {r["zero_core"]:.6f} | '
                 f'{r["reset_each_byte"]:.6f} | {perturbed} |')
lines += ['', 'For the GRU, zero-core removes hidden-to-hidden matrices; for graph and diagonal models, it zeros recurrent '
          'coefficients. These are architecture-specific dependence checks. The diagonal model\'s 10% intervention affects '
          'independent memory coefficients. Fixed-prompt samples were generated for all 35 models: first 32 training bytes, '
          '128 generated bytes, temperature .8, same generation seed within each training-seed group. All samples are retained '
          'in [validation-diagnostics-review.json](validation-diagnostics-review.json); none are selected as topology evidence.', '',
          '## Limits and provenance', '',
          'One locally sampled subgraph from one specimen, mostly visual neurons; roughly 92% of the selected neurons\' '
          'filtered connectivity falls outside the subset and is omitted. Dense artificial interfaces, unrestricted learned '
          'signs, a single small text corpus, a fixed training budget, and only five training seeds limit generalization. '
          'Exact degree preservation does not establish uniform mixing of rewired controls. A lack of a clear difference is '
          'not proof that the architectures are equivalent.', '',
          f'Code SHA-256: `{audit["code_hash"]}`. Freeze file SHA-256: `{audit["freeze_sha256"]}`. '
          f'Analysis plan SHA-256: `{audit["analysis_plan_sha256"]}`. Git revision unavailable. '
          'No frozen code, plan, data, configuration or checkpoint was modified. The test split has now been used; '
          'future revisions must not treat it as unseen or retune this frozen study using these scores.', '',
          'The original unit suite remains 31 passed / 2 unavailable-accelerator skips; unchanged experiment code was not '
          'retested. New validation and test-artifact audits passed. No additional training, replication, paid compute or '
          'uploads were launched. The initial one-subgraph confirmation is complete; broader replication remains unrun.', '',
          '[Full per-run report and curves](report.md) · [final audit](final-audit.json) · '
          '[audit source](audit_final.py) · [machine-readable final summary](final-review-summary.json) · '
          '[primary and secondary paired analysis](final-test-effects.json) · [earlier validation review](validation-review.md)']
(out / 'final-review.md').write_text('\n'.join(lines) + '\n')
print(out / 'final-review.md')
