"""Prepare audited input lists only; this is not a biological experiment runner."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / 'results/validation/20261006T171922Z'
STRUCTURAL = ROOT / 'results/structural/20261006T180116Z'
DATASET = 'male-cns:v1.0'
UUID = '4b2087c0fbe046bfaf0d60bc970e3e5d'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metadata(path):
    doc = json.loads(path.read_text())
    if len(doc['data']) != 1:
        raise ValueError('Expected one dataset metadata row')
    return dict(zip(doc['columns'], doc['data'][0], strict=True))


def prepare(run):
    run = run.resolve()
    run.relative_to(ROOT / 'results/workflow')
    output = run / 'prepared_inputs'
    if output.exists() or (run / 'manifest.json').exists():
        raise FileExistsError('Refusing to overwrite an existing preparation or finalized run')
    live = metadata(run / 'meta_live.json')
    prior = metadata(STRUCTURAL / 'raw/meta_end.json')
    expected = dict(dataset='male-cns', tag='v1.0', uuid=UUID)
    for key, value in expected.items():
        if live[key] != value:
            raise ValueError(f'Wrong active dataset field: {key}')
    for key in ('uuid', 'lastDatabaseEdit', 'latestMutationId'):
        if live[key] != prior[key]:
            raise ValueError(f'Dataset changed since structural validation: {key}')

    body_file = VALIDATION / 'resolved_bodies.csv'
    validation_manifest = json.loads((VALIDATION / 'manifest.json').read_text())
    recorded_hash = validation_manifest['output_hashes'][str(body_file.relative_to(ROOT))]
    if digest(body_file) != recorded_hash:
        raise ValueError('Validated identity table hash changed')
    rows = list(csv.DictReader(body_file.open()))
    by_id = {int(row['body_id']): row for row in rows}
    if len(by_id) != len(rows):
        raise ValueError('Duplicate validated body ID')
    groups_doc = json.loads((STRUCTURAL / 'analysis/groups.json').read_text())
    groups = groups_doc['groups']
    populations = ('LB3a', 'LB3b', 'LB3c', 'LB3d', 'MN4a', 'MN6', 'MN8', 'MN9')
    by_type = {t: sorted(i for i, r in by_id.items() if r['cell_type'] == t)
               for t in populations}
    for t in populations[:4]:
        if by_type[t] != sorted(groups[t]):
            raise ValueError(f'Identity/structural group disagreement: {t}')
    motors = sorted(i for t in populations[4:] for i in by_type[t])
    if motors != sorted(groups_doc['targets']):
        raise ValueError('Motor identity/structural target disagreement')
    definitions = {
        'experiment_01_lb3a_d': list(populations[:4]),
        'experiment_02_lb3b': ['LB3b'],
        'experiment_02_lb3c': ['LB3c'],
        'experiment_02_lb3b_lb3c': ['LB3b', 'LB3c'],
    }
    conditions = {}
    csv_rows = []
    for condition, types in definitions.items():
        inputs = sorted(i for t in types for i in by_type[t])
        if len(inputs) != len(set(inputs)) or set(inputs) & set(motors):
            raise ValueError('Duplicate or overlapping sensory/motor identities')
        conditions[condition] = dict(source_types=types, source_body_ids=inputs,
                                     source_count=len(inputs), target_body_ids=motors,
                                     target_count=len(motors), execution_allowed=False)
        for role, ids in [('source', inputs), ('target', motors)]:
            for body in ids:
                row = by_id[body]
                if row['dataset'] != DATASET or row['verification_status'] != 'VERIFIED_FLAT_FILE_AND_NEUPRINT':
                    raise ValueError(f'Unverified identity: {body}')
                csv_rows.append(dict(condition=condition, role=role, body_id=body,
                                     cell_type=row['cell_type'], side=row['side'],
                                     dataset=DATASET, verification_status=row['verification_status']))
    readiness = json.loads((ROOT / 'config/method_readiness.json').read_text())
    report = dict(
        status='PREPARED_INPUTS_ONLY_NOT_EXECUTABLE', dataset=DATASET, dataset_uuid=UUID,
        metadata=live, conditions=conditions,
        population_counts={k: len(v) for k, v in by_type.items()},
        graph_policy='Use the same source-verified graph in every condition; change only starting sensory bodies. Graph eligibility remains unresolved.',
        graph_eligibility=None, input_denominator_policy=None, pooling_policy=None,
        percentile_reference_policy=None, iteration_policy=None,
        gng021_sentinel_body_ids=sorted(groups['GNG021']),
        sentinel_policy='Observe selection without forcing inclusion; not a starting input or motor target.',
        selection_blockers=readiness['selection_blockers'],
        experiment_01_checkpoint_passed=False, method_frozen=False,
        evidence=[dict(path=str(p.relative_to(ROOT)), sha256=digest(p)) for p in (
            body_file, VALIDATION / 'manifest.json', STRUCTURAL / 'analysis/groups.json',
            STRUCTURAL / 'raw/meta_end.json', run / 'meta_live.json',
            ROOT / 'config/method_readiness.json', Path(__file__).resolve())],
    )
    output.mkdir()
    (output / 'conditions.json').write_text(json.dumps(report, indent=2) + '\n')
    with (output / 'condition_bodies.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(csv_rows[0]))
        writer.writeheader()
        writer.writerows(csv_rows)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True,
                        help='Workflow directory with a freshly fetched meta_live.json')
    args = parser.parse_args()
    report = prepare(args.run)
    print(json.dumps(dict(status=report['status'], counts=report['population_counts'],
                          conditions={k: v['source_count'] for k, v in report['conditions'].items()})))
