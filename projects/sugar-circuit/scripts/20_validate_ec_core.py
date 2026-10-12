"""Reproduce hand-calculated checks and quantify unresolved policy sensitivity.

No MaleCNS graph is loaded; all examples below are synthetic and explicitly
choose linear quantiles. These choices are not assigned to the publication.
"""
from pathlib import Path
import json
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.effective_connectivity import BodyGraph, above_percentile


def main():
    run = ROOT / (ROOT / 'config/current_method_audit.txt').read_text().strip()
    if (run / 'manifest.json').exists():
        raise RuntimeError('Frozen run: choose a new output directory before rerunning')
    result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
                            cwd=ROOT, capture_output=True, text=True)
    (run / 'tests.log').write_text(result.stdout + result.stderr)
    if result.returncode:
        raise SystemExit(result.returncode)

    def choose(names, scores, reference):
        result = above_percentile(scores, reference=reference, percentile=80, quantile_method='linear')
        return dict(scores=list(map(float, scores)), reference=list(map(float, reference)),
                    threshold=result.threshold,
                    selected=[name for name, keep in zip(names, result.passes) if keep])

    names = ['A', 'B', 'C', 'D', 'E']
    scores = [1, 2, 3, 4, 5]
    reference = dict(candidates_only=choose(names, scores, scores),
                     including_twenty_zero_bodies=choose(names, scores, [0]*20 + scores))
    target_scores = np.array([[.6, 0], [.4, .4]])
    pooling = {name: choose(['A', 'B'], values, values) for name, values in
               [('sum_across_targets', target_scores.sum(axis=1)), ('max_across_targets', target_scores.max(axis=1))]}
    graph = BodyGraph.from_edges([1, 2, 3, 4], [(1, 4, 1), (2, 3, 1), (3, 4, 1)], total_inputs=[0, 0, 1, 2])
    # A=1 directly contacts motor=4. B=2 reaches motor through relay=3.
    horizon = {}
    for hop, values in graph.to_outputs([4], hops=2).items():
        scores = values.toarray()[:2, 0]
        horizon[f'hop_{hop}'] = choose(['A', 'B'], scores, scores)
    evidence = dict(scope='SYNTHETIC_ONLY_NOT_BIOLOGICAL_RESULTS', percentile=80,
                    quantile_method='linear (explicit example choice; paper estimator unverified)',
                    percentile_universe=reference, target_aggregation=pooling,
                    candidate_to_output_horizon=horizon)
    assert reference['candidates_only']['selected'] == ['E']
    assert reference['including_twenty_zero_bodies']['selected'] == names
    assert pooling['sum_across_targets']['selected'] == ['B']
    assert pooling['max_across_targets']['selected'] == ['A']
    assert horizon['hop_1']['selected'] == ['A'] and horizon['hop_2']['selected'] == ['B']
    (run / 'selection_ambiguity_examples.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(result.stderr)
    print('Three synthetic comparisons demonstrate membership changes under unresolved policies.')


if __name__ == '__main__':
    main()
