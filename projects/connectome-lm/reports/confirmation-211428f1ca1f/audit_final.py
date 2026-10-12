"""Verify the user-executed sealed evaluation and compute the fixed paired analysis.

This reads existing score artifacts/checkpoints, never raw test bytes, and does not
train, change checkpoint selection, or repeat test inference.
Run from workspace root:
PYTHONPATH=fly_connectome_lm/src .venv/bin/python fly_connectome_lm/reports/confirmation-211428f1ca1f/audit_final.py
"""
from collections import Counter
from datetime import datetime
from pathlib import Path
import math
import numpy as np
import torch
from fly_connectome_lm.util import ROOT, read_json, atomic_json, digest, sha256, code_hash, now
from fly_connectome_lm.experiment import validate_freeze, matrix, CORPUS
from fly_connectome_lm.statistics import paired_effects


def main():
    out = Path(__file__).resolve().parent
    freeze_path = ROOT / 'configs/confirmation-frozen.json'
    freeze = read_json(freeze_path)
    validate_freeze(freeze, freeze['config'], tuple(freeze['optional']), freeze['learning_rates'])
    bundle_path = ROOT / 'runs/confirmation-211428f1ca1f.json'
    bundle = read_json(bundle_path)
    previous = read_json(out / 'audit.json')
    assert previous['status'] == 'passed' and previous['completed_runs'] == 35
    assert previous['code_hash'] == code_hash() == freeze['code_hash']
    assert previous['freeze_sha256'] == sha256(freeze_path)
    assert previous['bundle_sha256'] == sha256(bundle_path)
    old_checks = {r['run_id']: r for r in previous['checks']}
    summary_path = ROOT / 'reports' / f'final-evaluation-{sha256(freeze_path)[:12]}.json'
    summary = read_json(summary_path)
    assert summary['freeze_sha256'] == sha256(freeze_path)
    rows = matrix(freeze['config'], False, tuple(freeze['optional']), freeze['learning_rates'])
    expected_ids = [r['run_id'] for r in rows]
    assert expected_ids == bundle['run_ids'] == freeze['run_ids']
    assert expected_ids == [r['run_id'] for r in summary['records']]
    assert len(rows) == len(set(expected_ids)) == 35
    scored_bytes = read_json(CORPUS / 'manifest.json')['splits']['test']['length'] - 1
    assert scored_bytes == 55769
    checks, training_results = [], []
    for row, record in zip(rows, summary['records']):
        run = ROOT / 'runs' / row['run_id']
        assert read_json(run / 'test.json') == record
        manifest, result = read_json(run / 'manifest.json'), read_json(run / 'result.json')
        assert result['status'] == manifest['status'] == 'complete'
        assert result['final_step'] == 20000 and result['training_byte_exposures'] == 20480000
        assert manifest['config'] == row['config'] and result['config_hash'] == digest(row['config'])
        assert manifest['signature'] == digest({'config': manifest['config'], 'metadata': manifest['metadata']})
        assert record['freeze_sha256'] == sha256(freeze_path)
        assert record['code_hash'] == manifest['code_hash'] == result['code_hash'] == code_hash()
        assert record['corpus_manifest_sha256'] == freeze['corpus_manifest_sha256']
        for key in ['condition', 'sampling_seed', 'training_seed', 'null_index']:
            assert record[key] == row[key] == result[key]
        assert datetime.fromisoformat(record['evaluated_utc']) > datetime.fromisoformat(previous['reviewed_utc'])
        for kind in ['best', 'final']:
            path = run / f'{kind}.pt'
            # Pre-test audit pins selection and bytes before seeing any test score.
            assert sha256(path) == record['checkpoint_sha256'][kind] == old_checks[row['run_id']]['checkpoint_sha256'][kind]
            checkpoint = torch.load(path, map_location='cpu', weights_only=False)
            assert checkpoint['code_hash'] == freeze['code_hash'] and checkpoint['signature'] == manifest['signature']
            assert checkpoint['step'] == (result['selected_checkpoint_step'] if kind == 'best' else 20000)
            score = record[kind]
            assert score['scored_bytes'] == scored_bytes
            assert all(math.isfinite(v) for v in score.values())
            assert math.isclose(score['bpb'], score['nll_sum'] / scored_bytes / math.log(2), rel_tol=1e-12)
            assert math.isclose(score['byte_perplexity'], 2 ** score['bpb'], rel_tol=1e-12)
            assert 0 <= score['accuracy'] <= 1
            assert abs(score['accuracy'] * scored_bytes - round(score['accuracy'] * scored_bytes)) < 1e-8
        training_results.append(result)
        checks.append({'run_id': row['run_id'], 'status': 'passed',
                       'test_artifact_sha256': sha256(run / 'test.json'),
                       'checkpoint_sha256': record['checkpoint_sha256'],
                       'selected_before_test_step': result['selected_checkpoint_step']})
    for kind in ['unigram', 'bigram']:
        ref = summary['train_only_ngram_test'][kind]
        assert ref['scored_bytes'] == scored_bytes
        assert math.isclose(ref['bpb'], ref['nll_sum'] / scored_bytes / math.log(2), rel_tol=1e-12)
    stats = {}
    for kind in ['best', 'final']:
        analysis = paired_effects([{**r, 'bpb': r[kind]['bpb']} for r in summary['records']], 3)
        assert len(analysis['pairs']) == 5 and not analysis['incomplete_pairs']
        assert {p['training_seed'] for p in analysis['pairs']} == {11, 22, 33, 44, 55}
        # Independently recompute one difference per seed; never repeat fly observations.
        deltas = []
        for seed in [11, 22, 33, 44, 55]:
            group = [r for r in summary['records'] if r['training_seed'] == seed]
            fly = [r[kind]['bpb'] for r in group if r['condition'] == 'FLY-TOPOLOGY']
            nulls = [r[kind]['bpb'] for r in group if r['condition'] == 'DEGREE-REWIRED']
            assert len(fly) == 1 and len(nulls) == 3
            deltas.append(float(np.mean(nulls) - fly[0]))
        np.testing.assert_allclose(deltas, [p['delta'] for p in analysis['pairs']], rtol=0, atol=1e-14)
        rng = np.random.default_rng(1729)
        samples = np.asarray(deltas)[rng.integers(0, 5, size=(10000, 5))].mean(axis=1)
        np.testing.assert_allclose(np.quantile(samples, [.025, .975]), analysis['per_graph']['101']['ci95'], rtol=0, atol=1e-14)
        stats[kind] = analysis
    latest_training = max(r['completed_utc'] for r in training_results)
    assert all(r['evaluated_utc'] > latest_training for r in summary['records'])
    artifact_hashes = {r['run_id']: sha256(ROOT / 'runs' / r['run_id'] / 'test.json') for r in rows}
    audit = {'status': 'passed', 'reviewed_utc': now(), 'completed_test_runs': 35, 'checkpoint_identities_verified': 70,
             'checks': checks, 'summary_sha256': sha256(summary_path), 'freeze_sha256': sha256(freeze_path),
             'code_hash': code_hash(), 'analysis_plan_sha256': freeze['analysis_plan_sha256'],
             'corpus_manifest_sha256': freeze['corpus_manifest_sha256'], 'scored_bytes_per_checkpoint': scored_bytes,
             'primary_checkpoint_rule': freeze['checkpoint_selection'], 'test_inference_repeated': False,
             'raw_test_data_loaded_by_audit': False, 'training_launched': False,
             'prior_validation_audit_sha256': sha256(out / 'audit.json'), 'audit_script_sha256': sha256(Path(__file__)),
             'metric_check': 'Arithmetic and complete artifact/checkpoint identity checks; predictions not replayed.',
             'test_artifact_sha256': artifact_hashes}
    atomic_json(out / 'final-audit.json', audit)
    atomic_json(out / 'final-test-effects.json', stats)
    print('PASS: 35 test records, 70 unchanged pre-test checkpoint identities, metric arithmetic, and fixed paired bootstrap verified.')
    print('Primary test contrast:', stats['best']['per_graph']['101'])


if __name__ == '__main__':
    main()
