"""Single-use recorder for the 2026-10-07 source/preparation checkpoint."""
import csv
import datetime as dt
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.effective_connectivity import ReplicationNotReady, require_replication_ready

REL = Path('results/workflow/20261007T221035718347Z')
RUN = ROOT / REL


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path):
    return dict(path=str(path.relative_to(ROOT)), bytes=path.stat().st_size, sha256=sha(path))


def append(path, text):
    with (ROOT / path).open('a') as handle:
        handle.write(text)


def main():
    if (RUN / 'manifest.json').exists():
        raise FileExistsError('Finalized audit is immutable')
    stamp = dt.datetime.now(dt.timezone.utc).isoformat()
    readiness = json.loads((ROOT / 'config/method_readiness.json').read_text())
    try:
        require_replication_ready(readiness)
    except ReplicationNotReady:
        gate_blocks = True
    else:
        raise AssertionError('Biological execution must remain gated at this checkpoint')
    assert [b['id'] for b in readiness['selection_blockers']] == ['B01', 'B02', 'B03', 'B04']
    assert not readiness['experiment_01_allowed'] and not readiness['experiment_02_allowed']
    assert not readiness['method_frozen'] and not readiness['simulation_allowed']
    plan = json.loads((RUN / 'prepared_inputs/conditions.json').read_text())
    for item in plan['evidence']:
        assert sha(ROOT / item['path']) == item['sha256'], item['path']
    counts = {k: v['source_count'] for k, v in plan['conditions'].items()}
    assert list(counts.values()) == [77, 11, 23, 34]
    assert plan['population_counts'] == dict(LB3a=17, LB3b=11, LB3c=23, LB3d=26, MN4a=4, MN6=2, MN8=2, MN9=2)
    bodies = list(csv.DictReader((RUN / 'prepared_inputs/condition_bodies.csv').open()))
    assert len(bodies) == 185
    identities = {int(r['body_id']): r for r in csv.DictReader((ROOT / 'results/validation/20261006T171922Z/resolved_bodies.csv').open())}
    expected_rows = set()
    for condition, spec in plan['conditions'].items():
        assert spec['target_count'] == 10 and not spec['execution_allowed']
        for role in ('source', 'target'):
            for body in spec[f'{role}_body_ids']:
                expected_rows.add((condition, role, str(body)))
    assert {(r['condition'], r['role'], r['body_id']) for r in bodies} == expected_rows
    assert len(expected_rows) == len(bodies)
    for row in bodies:
        original = identities[int(row['body_id'])]
        for field in ('cell_type', 'side', 'dataset', 'verification_status'):
            assert row[field] == original[field]
    assert set(plan['gng021_sentinel_body_ids']) == {i for i, r in identities.items() if r['cell_type'] == 'GNG021'}

    validation = dict(timestamp=stamp, body_rows_checked=len(bodies), condition_source_counts=counts,
                      target_count_per_condition=10, identity_fields_match=True,
                      all_preparation_input_hashes_match=True, replication_gate_blocks=gate_blocks,
                      existing_tests_passed=27, tests_evidence=str(REL / 'tests_summary.txt'),
                      biological_selection_run=False)
    (RUN / 'preparation_validation.json').write_text(json.dumps(validation, indent=2) + '\n')

    # Register only sources actually used for conclusions; preserve all fetches separately.
    smpath = ROOT / 'config/source_manifest.yaml'
    sm = json.loads(smpath.read_text())
    number = max(int(s['source_id'][1:]) for s in sm['sources'])
    receipts = json.loads((RUN / 'sources/fetch_receipts.json').read_text())
    receipt_by_file = {r['file']: r for r in receipts}
    sources = [
        ('search3.txt', 'https://www.sciencedirect.com/science/article/abs/pii/S0092867426009438',
         'Indexed final Resource availability and Methods; only the final Cell hit used; mixed search response preserved'),
        ('coconatfly_multihop.R', receipt_by_file['coconatfly_multihop.R']['url'],
         'Pinned official software: multihop/min_frac function; not established as Tastekin Figure 6G generator'),
        ('malecns_neuprint.R', receipt_by_file['malecns_neuprint.R']['url'],
         'Pinned official package defaults; not evidence of historical paper settings'),
        ('coconatfly_multihop_history.json', receipt_by_file['coconatfly_multihop_history.json']['url'],
         'Bounded function history: July 2026 commits; not proof of use in the paper'),
        ('author_repos.json', receipt_by_file['author_repos.json']['url'], 'Bounded public author repository listing'),
        ('lab_repos.json', receipt_by_file['lab_repos.json']['url'], 'Bounded public lab repository listing'),
    ]
    source_ids = {}
    for filename, url, description in sources:
        number += 1
        source_ids[filename] = f'P{number:02}'
        sm['sources'].append(dict(source_id=f'P{number:02}', **record(RUN / 'sources' / filename),
                                  url=url, description=description, audit_recorded_utc=stamp))
    sm['latest_workflow_audit'] = str(REL)
    smpath.write_text(json.dumps(sm, indent=2) + '\n')
    for receipt in receipts:
        entry = dict(audit_recorded_utc=stamp, experiment='SEQUENTIAL_WORKFLOW_RECOVERY',
                     **receipt, **record(RUN / 'sources' / receipt['file']))
        append('logs/source_fetch_log.jsonl', json.dumps(entry) + '\n')

    ledger = ROOT / 'logs/claim_ledger.csv'
    claims = list(csv.DictReader(ledger.open()))
    number = max(int(c['claim_id'][1:]) for c in claims)
    specifications = [
        ('The final paper Resource availability identifies Carlos Ribeiro as lead contact and directs requests for additional reanalysis information there; its inspected availability paragraph has no dedicated analysis-repository link.',
         'PAPER_CLAIM', str(REL / 'sources/search3.txt'), 'docs/tastekin_methods_request.txt',
         'Scope is the inspected paragraph; no claim that code is absent from every host. Draft not sent.'),
        ('The inspected pinned coconatfly multihop_effective_matrix uses min_frac pruning and does not implement the final Tastekin two-percentile selection/pruning procedure; it is not a verified replacement for the Figure 6G generator.',
         'COMPUTATIONAL_RESULT', str(REL / 'sources/coconatfly_multihop.R'), 'results/method_recovery/20261006T220302Z/method_parameters.csv',
         'Official generic software inspection, not attribution of the function to Tastekin.'),
        ('Prepared and cross-checked source lists contain 77 all-LB3 bodies, 11 LB3b, 23 LB3c and 34 in their union, each using the same 10 verified motor bodies. These are non-executable input preparations, not selected circuits.',
         'COMPUTATIONAL_RESULT', str(REL / 'prepared_inputs/condition_bodies.csv'), str(REL / 'preparation_validation.json'),
         '185 condition/role/body rows; identities agree with frozen validation and structural groups; graph policies remain unspecified.'),
    ]
    claim_ids = []
    with ledger.open('a', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(claims[0]))
        for claim, kind, source1, source2, notes in specifications:
            number += 1
            claim_id = f'C{number:03}'
            claim_ids.append(claim_id)
            writer.writerow(dict(claim_id=claim_id, timestamp=stamp, experiment='SEQUENTIAL_WORKFLOW_RECOVERY',
                                 claim=claim, claim_type=kind, source_1=source1, source_2=source2,
                                 dataset='male-cns:v1.0', body_ids='', edge_ids='',
                                 support_level='Primary text/code or validated input records',
                                 verification_status='VERIFIED', confidence='high within stated scope',
                                 notes=notes, supersedes_claim_id=''))
    decisions = (ROOT / 'logs/decision_log.md').read_text()
    decision_id = f'D{max(map(int, re.findall(r"\bD(\d{3})\b", decisions))) + 1:03}'
    append('logs/decision_log.md', f'\n\n### {decision_id} — Sequential preparation while source gaps remain ({stamp})\n'
           'The user authorized proceeding step by step. Reverified the active dataset, checked additional primary/public code sources, and prepared exact source/target lists plus an unsent lead-contact request. '
           'Do not adopt generic coconatfly/malecns defaults as the historical Figure 6G settings. B01–B04 still materially affect selection, so preserve all disabled execution gates. '
           'Resume the same engine after source resolution, then Experiment 1R, its checkpoint/freeze, and the three sugar conditions. '
           f'No new biological experiment or simulation. Audit: `{REL}`. Claims: {", ".join(claim_ids)}.\n')
    append('logs/unresolved_questions.md', f'\n\n## {stamp} — Sequential workflow follow-up\n'
           'Q-004/Q-012 and B01–B04 remain open after bounded author/lab and pinned official-software checks. '
           'The final Resource availability supplies the lead-contact route; `docs/tastekin_methods_request.txt` is prepared but unsent. '
           'The exact four condition lists are prepared independently of the missing graph/pooling/percentile/iteration policies. '
           'A request response or the generating script/configuration remains the actionable dependency. No new mismatch was identified.\n')
    append('config/analysis.yaml', f'\nlatest_workflow_audit: "{REL}"\nprepared_condition_inputs: "{REL}/prepared_inputs/conditions.json"\n')
    update = (f'\n\n## {stamp} — Sequential workflow source check and input preparation\n\n'
              f'Reverified live v1.0 identity, inspected additional official sources, and checked all four input sets (77/11/23/34 sensory bodies; 10 fixed motors). '
              f'27 existing tests pass; input hashes, 185 exported body rows, and the blocking execution gate verified. '
              'B01–B04 remain unresolved; no biological selection or method freeze. '
              'The generic package functions are not a verified Figure 6G implementation. '
              f'See [workflow steps](docs/workflow_next_steps.txt), [unsent methods request](docs/tastekin_methods_request.txt), and [audit]({REL}/report.txt). '
              f'Claims {", ".join(claim_ids)}; decision {decision_id}.\n')
    append('STATUS.md', update)
    append('CHANGELOG.md', f'\n\n## {stamp}\nPrepared gated experiment inputs and a step-by-step resumption checklist; extended primary/code source audit; drafted but did not send the lead-contact methods request. `{REL}`.\n')
    for name in ('paper_method_reconstruction.md', 'experiment_01_replication_checkpoint.md', 'effective_connectivity_and_sugar_checkpoint.md'):
        append('docs/' + name, f'\n\n### Follow-up {stamp}\n'
               'Additional official software and author/lab repository checks did not resolve B01–B04. '
               'All four source lists and fixed motor targets are cross-checked and prepared, but no biological selection ran. '
               'The existing 27 tests pass. See [sequential checklist](workflow_next_steps.txt), '
               f'[new audit](../{REL}/report.txt), and [unsent request](tastekin_methods_request.txt). '
               'The full method remains unfrozen; generic package defaults were not imported.\n')

    # Preserve mutable current documents as immutable audit copies.
    changed = ['config/analysis.yaml', 'config/source_manifest.yaml', 'config/method_readiness.json',
               'STATUS.md', 'CHANGELOG.md', 'logs/claim_ledger.csv', 'logs/decision_log.md',
               'logs/unresolved_questions.md', 'logs/mismatch_ledger.csv',
               'docs/workflow_next_steps.txt', 'docs/tastekin_methods_request.txt',
               'docs/paper_method_reconstruction.md', 'docs/experiment_01_replication_checkpoint.md',
               'docs/effective_connectivity_and_sugar_checkpoint.md', 'scripts/prepare_workflow_inputs.py',
               'scripts/23_record_workflow_checkpoint.py']
    for relative in changed:
        destination = RUN / 'audit_snapshot' / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, destination)
    for path in (RUN / 'before/logs').glob('*'):
        if path.name in ('claim_ledger.csv', 'mismatch_ledger.csv', 'decision_log.md', 'unresolved_questions.md'):
            assert (ROOT / 'logs' / path.name).read_bytes().startswith(path.read_bytes())
    assert (ROOT / 'STATUS.md').read_bytes().startswith((RUN / 'before/STATUS.md').read_bytes())
    assert (ROOT / 'config/method_readiness.json').read_bytes() == (RUN / 'before/config/method_readiness.json').read_bytes()
    for filename, key in [('claim_ledger.csv', 'claim_id'), ('mismatch_ledger.csv', 'mismatch_id')]:
        rows = list(csv.DictReader((ROOT / 'logs' / filename).open()))
        assert len(rows) == len({r[key] for r in rows})
    # Check credential hygiene without printing the credential or surrounding file.
    secrets = re.findall(r'(?<![\w./-])[A-Za-z0-9_.-]{32,}(?![\w./-])', (ROOT / '.venv/.env').read_text())
    assert len(secrets) == 1
    assert not (ROOT / '.venv/workflow_auth.curl').exists()
    for path in RUN.rglob('*'):
        if path.is_file():
            assert secrets[0].encode() not in path.read_bytes(), f'Credential leak in {path.name}'

    manifest = dict(timestamp=stamp, experiment='SEQUENTIAL_WORKFLOW_RECOVERY_AND_PREPARATION',
                    dataset='male-cns:v1.0', dataset_uuid=plan['dataset_uuid'],
                    python=sys.version, platform=platform.platform(),
                    packages={p: importlib.metadata.version(p) for p in ('numpy', 'scipy', 'pyarrow')},
                    method_frozen=False, biological_selection_run=False, simulation_run=False,
                    author_message_sent=False, claim_ids=claim_ids, decision_id=decision_id,
                    registered_source_ids=source_ids, validation=validation,
                    limitations=['B01–B04 unresolved', 'Complete paper reference inventory unresolved',
                                 'No biological selected circuit', 'Bounded source search cannot establish code absence'],
                    files=[record(p) for p in sorted(RUN.rglob('*')) if p.is_file()])
    (RUN / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    for item in manifest['files']:
        assert sha(ROOT / item['path']) == item['sha256'], item['path']
    append('logs/run_manifest.jsonl', json.dumps(dict(timestamp=stamp, experiment=manifest['experiment'],
           run=str(REL), manifest_sha256=sha(RUN / 'manifest.json'), files_verified=len(manifest['files']),
           validation=validation, biological_selection_run=False)) + '\n')
    print(json.dumps(dict(run=str(REL), source_ids=source_ids, claims=claim_ids, decision=decision_id,
                          files_verified=len(manifest['files']), validation=validation), indent=2))


if __name__ == '__main__':
    main()
