"""Test pooling explanations without fitting or implementing an unknown method.

The null explanation tested is deletion of whole, unchanged current body-pair
edges followed by summation. Its failure does not identify the historical cause.
No selected-circuit membership or effective-connectivity score is produced.
"""
import argparse
import csv
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'results/structural/20261006T180116Z'


def subsets(values):
    values = tuple(values)
    for n in range(1, len(values)+1):
        yield from itertools.combinations(values, n)


def attainable_sums(weights):
    """One deterministic witness per sum; equal-weight edges remain distinct."""
    sums = {0: ()}
    for i, w in enumerate(weights):
        if not isinstance(w, int) or w <= 0:
            raise ValueError('Expected positive integer synapse counts')
        for total, witness in tuple(sorted(sums.items())):
            sums.setdefault(total+w, witness+(i,))
    return sums


def body_subset_matches(edges, target):
    """Enumerate every nonempty source/target subset; keep the induced pairs."""
    sources = sorted({e['source'] for e in edges})
    targets = sorted({e['target'] for e in edges})
    matches = []
    for pres in subsets(sources):
        for posts in subsets(targets):
            total = sum(e['weight'] for e in edges if e['source'] in pres and e['target'] in posts)
            if total == target:
                matches.append({'source_ids': pres, 'target_ids': posts, 'weight': total})
    return matches


def write_csv(path, rows):
    with path.open('x', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(out):
    out.mkdir(parents=True, exist_ok=False)
    manifest = json.loads((BASE/'manifest.json').read_text())
    expected = {v['path']: v['sha256'] for v in manifest['input_files']+manifest['output_files']}
    inputs = [BASE/'paper_motif_comparison.csv', BASE/'named_neuron_edge_validation.csv',
              BASE/'raw/named_out.json', BASE/'raw/additional_named_out.json']
    checks = []
    for path in inputs:
        digest = sha(path)
        assert digest == expected[str(path.relative_to(ROOT))], path
        checks.append({'path': str(path.relative_to(ROOT)), 'sha256': digest, 'matches_baseline_manifest': True})
    motifs = list(csv.DictReader(inputs[0].open()))
    named = list(csv.DictReader(inputs[1].open()))
    variants = {}
    for path in inputs[2:]:
        raw = json.loads(path.read_text())
        for values in raw['data']:
            edge = dict(zip(raw['columns'], values))
            key = (edge['source'], edge['target'])
            if key in variants:
                assert variants[key] == edge
            variants[key] = edge
    audits, pairs, enumeration, sides = [], [], {}, []
    for motif in motifs:
        source, target = motif['source_type'], motif['target_type']
        paper = int(motif['paper_figure6_label'])
        matched = [e for e in named if (e['source_type'], e['target_type']) == (source, target)]
        edges = []
        for e in matched:
            edge = {k: int(e[k]) for k in ['source', 'target', 'weight']}
            edges.append(edge)
            live = variants.get((edge['source'], edge['target']))
            assert (live is not None) == (edge['weight'] > 0)
            assert edge['weight'] == (live['weight'] if live else 0)
            pairs.append(dict(source_type=source, target_type=target, **edge,
                              source_side=e['source_side'], target_side=e['target_side'],
                              weightHP=live['weightHP'] if live else 0,
                              weightHR=live['weightHR'] if live else 0,
                              provenance=e['provenance']))
        edges.sort(key=lambda e: (e['source'], e['target']))
        positive = [e for e in edges if e['weight'] > 0]
        sums = attainable_sums([e['weight'] for e in positive])
        body_matches = body_subset_matches(edges, paper)
        total = sum(e['weight'] for e in edges)
        assert total == int(motif['current_all_body_sum'])
        hp = sum(variants[(e['source'], e['target'])]['weightHP'] for e in positive)
        hr = sum(variants[(e['source'], e['target'])]['weightHR'] for e in positive)
        if total == paper:
            explanation = 'All-body raw sum matches; does not establish paper body selection or algorithm recovery'
        elif paper > total:
            explanation = 'Paper exceeds current raw total: deletion-only body/edge/synapse filtering cannot explain this under unchanged mappings and additive pooling'
        else:
            explanation = 'No subset of unchanged current raw body-pair counts equals paper: whole-body/whole-edge deletion alone is excluded; synapse filtering or changed data/mapping/pooling remains unresolved'
        audit = dict(source_type=source, target_type=target, paper_displayed_weight=paper,
                     current_v1_all_body_weight=total, paper_selected_body_ids_if_recoverable='',
                     v1_selected_body_ids='', selected_v1_weight='', difference=total-paper,
                     probable_explanation=explanation,
                     evidence='paper/primary/figure6.jpg panels I/J; body_pairs.csv; subset_enumeration.json',
                     status='RAW_TOTAL_MATCH_SELECTION_UNVERIFIED' if total == paper else 'UNRESOLVED',
                     v1_all_source_body_ids=';'.join(map(str, sorted({e['source'] for e in edges}))),
                     v1_all_target_body_ids=';'.join(map(str, sorted({e['target'] for e in edges}))),
                     any_raw_edge_subset_matches=paper in sums, raw_body_subset_match_count=len(body_matches),
                     current_v1_all_body_weightHP=hp, current_v1_all_body_weightHR=hr,
                     weightHP_matches=hp == paper, weightHR_matches=hr == paper,
                     selection_status='NOT_RUN_METHOD_BLOCKED')
        audits.append(audit)
        enumeration[source+'->'+target] = dict(
            positive_body_edges=positive,
            all_attainable_raw_edge_sums=sorted(sums),
            paper_weight=paper,
            raw_edge_witness=sums.get(paper), body_subset_matches=body_matches,
            nonempty_body_subset_combinations=(2**len({e['source'] for e in edges})-1)*(2**len({e['target'] for e in edges})-1),
            nearest_attainable_sums=sorted(sums, key=lambda s: (abs(s-paper), s))[:3],
            caveat='Arithmetic feasibility only. No witness is adopted as a selected circuit.')
        for pre_side, post_side in itertools.product(['L', 'R'], repeat=2):
            sides.append(dict(source_type=source,target_type=target,source_side=pre_side,target_side=post_side,
                              raw_weight=sum(int(e['weight']) for e in matched if e['source_side']==pre_side and e['target_side']==post_side)))
    write_csv(out/'paper_weight_comparison.csv', audits)
    write_csv(out/'body_pairs.csv', pairs)
    write_csv(out/'left_right_raw_weights.csv', sides)
    (out/'subset_enumeration.json').write_text(json.dumps(enumeration,indent=2)+'\n')
    (out/'input_integrity.json').write_text(json.dumps(checks,indent=2)+'\n')
    summary = dict(scope='RAW_WEIGHT_AUDIT_NOT_EXPERIMENT_1R', motif_count=len(audits),
                   raw_exact_matches=sum(a['difference']==0 for a in audits),
                   unresolved_differences=sum(a['difference']!=0 for a in audits),
                   mismatches_not_explained_by_any_raw_edge_subset=sum(a['difference']!=0 and not a['any_raw_edge_subset_matches'] for a in audits),
                   all_body_weightHP_matches=sum(a['weightHP_matches'] for a in audits),
                   all_body_weightHR_matches=sum(a['weightHR_matches'] for a in audits),
                   method_selected_nodes=None, effective_connectivity=None,
                   precision_recall=None, near_match_tolerance=None)
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New directory; existing results are never overwritten')
    main(parser.parse_args().output)
