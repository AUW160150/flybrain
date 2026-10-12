"""Audit completed frozen confirmation and replay validation only; no training/test access.

Run from workspace root:
PYTHONPATH=fly_connectome_lm/src .venv/bin/python fly_connectome_lm/reports/confirmation-211428f1ca1f/audit_confirmation.py
"""
from collections import Counter
from pathlib import Path
import math
import numpy as np
import torch
from fly_connectome_lm.util import ROOT, read_json, atomic_json, sha256, digest, code_hash, now, setup, seed_for
from fly_connectome_lm.experiment import matrix, base_graph, resolved_graph, validate_freeze, CORPUS
from fly_connectome_lm.models import build, accounting, GraphRNN, CONDITIONS
from fly_connectome_lm.graph_controls import degrees
from fly_connectome_lm.text_data import DevelopmentCorpus, WindowSampler
from fly_connectome_lm.evaluate import evaluate


def main():
    output = Path(__file__).resolve().parent
    bundle_path = ROOT / 'runs/confirmation-211428f1ca1f.json'
    freeze_path = ROOT / 'configs/confirmation-frozen.json'
    bundle, freeze = read_json(bundle_path), read_json(freeze_path)
    config, rates = freeze['config'], freeze['learning_rates']
    validate_freeze(freeze, config, tuple(freeze['optional']), rates)
    assert bundle['profile'] == 'confirmation' and not bundle['synthetic']
    assert bundle['config'] == config and bundle['freeze_hash'] == digest(freeze)
    assert bundle['code_hash'] == freeze['code_hash'] == code_hash()
    assert bundle['analysis_plan']['sha256'] == sha256(ROOT / 'docs/analysis_plan.md')
    assert bundle['corpus_manifest_sha256'] == sha256(CORPUS / 'manifest.json')
    assert config['training_seeds'] == [11, 22, 33, 44, 55]
    assert config['sampling_seeds'] == [101] and config['nulls_per_seed'] == 3
    assert config['updates'] == 20000 and config['batch'] == 8 and config['context'] == 128
    assert freeze['selection_sha256'] == digest(read_json(ROOT / 'configs/development-selection.json'))
    setup(config['device'], config['threads'])
    rows = matrix(config, False, tuple(freeze['optional']), rates)
    assert [row['run_id'] for row in rows] == bundle['run_ids'] == freeze['run_ids']
    expected = [(seed, condition, k) for seed in config['training_seeds'] for condition in CONDITIONS
                for k in (range(1, 4) if condition == 'DEGREE-REWIRED' else [0])]
    assert len(rows) == 35 and all(row['already_complete'] for row in rows)
    assert Counter((r['training_seed'], r['condition'], r['null_index']) for r in rows) == Counter(expected)
    assert all(row['config']['lr'] == .003 for row in rows)
    corpus = DevelopmentCorpus(CORPUS)
    samplers = {}
    for seed in config['training_seeds']:
        sampler = WindowSampler(corpus.train, 128, 8, seed_for('data', seed))
        for _ in range(20000):
            sampler.next()
        samplers[seed] = sampler.state_dict()
    original = base_graph(config, 101)
    assert len(original.ids) == 512 and len(original.source) == 3061
    initial_states, checks, records = {}, [], []
    for index, row in enumerate(rows, 1):
        path = ROOT / 'runs' / row['run_id']
        manifest, result, history = (read_json(path / f'{name}.json') for name in ['manifest', 'result', 'history'])
        assert manifest['status'] == result['status'] == 'complete' and not result['synthetic']
        assert manifest['code_hash'] == result['code_hash'] == code_hash()
        assert manifest['config'] == row['config'] and result['config_hash'] == digest(row['config'])
        assert manifest['signature'] == digest({'config': manifest['config'], 'metadata': manifest['metadata']})
        assert manifest['analysis_plan']['sha256'] == freeze['analysis_plan_sha256']
        assert manifest['metadata']['corpus_manifest_sha256'] == freeze['corpus_manifest_sha256']
        assert manifest['optimizer'] == {'name': 'AdamW', 'lr': .003, 'betas': [.9, .999], 'eps': 1e-8, 'weight_decay': 0.}
        for key in ['condition', 'training_seed', 'sampling_seed', 'null_index']:
            assert result[key] == manifest['metadata'][key] == row[key]
        assert result['final_step'] == 20000 and result['training_byte_exposures'] == 20480000
        assert len(history) == 20000 and [v['step'] for v in history] == list(range(1, 20001))
        assert all(math.isfinite(v['train_nll']) and math.isfinite(v['gradient_norm_before_clip']) for v in history)
        assert all(v['training_bytes'] == v['step'] * 1024 for v in history)
        validations = [v for v in history if 'validation' in v]
        assert [v['step'] for v in validations] == list(range(1000, 20001, 1000))
        assert all(v['validation']['scored_bytes'] == len(corpus.validation) - 1 == 55769 for v in validations)
        best = min(validations, key=lambda v: v['validation']['bpb'])
        assert best['step'] == result['selected_checkpoint_step'] and best['validation'] == result['validation_best']
        assert validations[-1]['validation'] == result['validation_final']
        graph = resolved_graph(row, original)
        assert graph.hash == result['graph_hash'] == manifest['metadata']['graph_hash']
        assert np.array_equal(graph.ids, original.ids)
        if row['condition'] in ('FLY-TOPOLOGY', 'DEGREE-REWIRED', 'RANDOM-DENSITY'):
            assert len(graph.source) == 3061
            assert np.all(graph.source != graph.target)
            assert len(np.unique(graph.source * 512 + graph.target)) == 3061
        model = build(row['condition'], graph, row['config'], row['training_seed'])
        assert accounting(model) == result['accounting'] == row['accounting'] == manifest['accounting']
        if row['condition'] in ('FLY-TOPOLOGY', 'DEGREE-REWIRED'):
            initial_states[(row['training_seed'], row['condition'], row['null_index'])] = {
                k: v.clone() for k, v in model.state_dict().items() if k not in ('source', 'target')}
        checkpoints = {kind: torch.load(path / f'{kind}.pt', map_location='cpu', weights_only=False)
                       for kind in ['best', 'final']}
        replay = {}
        for kind, checkpoint in checkpoints.items():
            assert checkpoint['signature'] == manifest['signature'] and checkpoint['code_hash'] == freeze['code_hash']
            assert checkpoint['step'] == (best['step'] if kind == 'best' else 20000)
            assert all(torch.isfinite(value).all() for value in checkpoint['model'].values())
            if isinstance(model, GraphRNN):
                assert torch.equal(model.source, checkpoint['model']['source'])
                assert torch.equal(model.target, checkpoint['model']['target'])
            model.load_state_dict(checkpoint['model'])
            if kind == 'best' or best['step'] != 20000:
                score = evaluate(model, corpus.validation, 128, 32)
                logged = result['validation_best' if kind == 'best' else 'validation_final']
                differences = {key: abs(score[key] - logged[key]) for key in score}
                assert score['scored_bytes'] == logged['scored_bytes'] == 55769
                assert all(value < 1e-6 for value in differences.values())
                replay[kind] = {'score': score, 'absolute_differences': differences}
            else:
                assert all(torch.equal(value, checkpoints['best']['model'][key]) for key, value in checkpoint['model'].items())
                replay[kind] = {'same_model_as_replayed_best': True}
        final = checkpoints['final']
        assert final['sampler'] == samplers[row['training_seed']]
        if isinstance(model, GraphRNN):
            assert any((v['edge_gradient_norm'] or 0) > 0 for v in history)
            change = (final['model']['theta'] - final['initial_theta']).norm().item()
            assert change == result['core_weight_change_l2'] and change > 0
            initial = build(row['condition'], graph, row['config'], row['training_seed'])
            assert torch.equal(final['initial_theta'], initial.theta.detach())
        if row['condition'] == 'DEGREE-REWIRED':
            for before, after in zip(degrees(original), degrees(graph)):
                np.testing.assert_array_equal(before, after)
            control = graph.metadata['randomization']
            assert control['valid'] and control['accepted_swaps'] == 20 * 3061 and control['proposals'] <= 500 * 3061
            assert graph.hash != original.hash
        checks.append({'run_id': row['run_id'], 'status': 'passed', 'validation_replay': replay,
                       'checkpoint_sha256': {kind: sha256(path / f'{kind}.pt') for kind in checkpoints}})
        records.append({'run_id': row['run_id'], **result})
        print(f'Audited {index}/35: {row["condition"]} seed={row["training_seed"]} null={row["null_index"]}', flush=True)
    for seed in config['training_seeds']:
        fly = initial_states[(seed, 'FLY-TOPOLOGY', 0)]
        for k in [1, 2, 3]:
            null = initial_states[(seed, 'DEGREE-REWIRED', k)]
            assert fly.keys() == null.keys() and all(torch.equal(fly[key], null[key]) for key in fly)
    assert len(checks) == 35
    atomic_json(output / 'audit.json', {
        'status': 'passed', 'reviewed_utc': now(), 'completed_runs': len(checks),
        'bundle_sha256': sha256(bundle_path), 'freeze_sha256': sha256(freeze_path), 'code_hash': code_hash(),
        'analysis_plan_sha256': sha256(ROOT / 'docs/analysis_plan.md'), 'checks': checks,
        'training_byte_exposures': sum(r['training_byte_exposures'] for r in records),
        'test_data_loaded': False, 'test_result_files_found': len(list((ROOT / 'runs').rglob('test.json'))),
        'training_launched': False, 'audit_script_sha256': sha256(Path(__file__)),
        'matched_controls': 'Exact labelled degrees, counts, initial recurrent slots and interfaces, optimizer, full budgets and sampler RNG states verified.'})
    atomic_json(output / 'run-values.json', records)
    print('PASS: 35 runs, 70 checkpoint identities, frozen recipe, full budgets and validation replay verified; test data not loaded.', flush=True)


if __name__ == '__main__':
    main()
