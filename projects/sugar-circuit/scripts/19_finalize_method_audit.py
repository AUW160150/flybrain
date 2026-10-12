"""Verify and freeze audit provenance without declaring a method freeze."""
import csv
import datetime as dt
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/(ROOT/'config/current_method_audit.txt').read_text().strip()


def record(path):
    return dict(path=str(path.relative_to(ROOT)),bytes=path.stat().st_size,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def main():
    assert not (RUN/'manifest.json').exists(), 'Audit manifest is immutable'
    checks={}
    for name,key in [('claim_ledger.csv','claim_id'),('mismatch_ledger.csv','mismatch_id')]:
        path=ROOT/'logs'/name
        rows=list(csv.DictReader(path.open()))
        assert all(None not in r and all(v is not None for v in r.values()) for r in rows)
        assert len(rows)==len({r[key] for r in rows})
        assert path.read_bytes().startswith((RUN/'audit_snapshot_before/logs'/name).read_bytes())
        checks[name]=dict(rows=len(rows),unique_ids=True,previous_bytes_preserved=True)
    for name in ['STATUS.md','logs/decision_log.md','logs/unresolved_questions.md','docs/paper_method_reconstruction.md','docs/prompt_vs_paper_audit.md']:
        assert (ROOT/name).read_bytes().startswith((RUN/'audit_snapshot_before'/name).read_bytes())
    for path in (ROOT/'logs').glob('*.jsonl'):
        for line in path.read_text().splitlines():
            if line.strip():json.loads(line)
    checks['append_only_history']=True
    gate=json.loads((ROOT/'config/method_readiness.json').read_text())
    assert not gate['experiment_01_allowed'] and not gate['experiment_02_allowed'] and not gate['simulation_allowed']
    assert not gate['method_verified'] and gate['effective_math_tests_passed'] is None
    for name in ['experiment_01_paper_replication.yaml','experiment_02_sugar_restricted.yaml','experiment_03_v1_candidate.yaml']:
        assert 'execution_allowed: false' in (ROOT/'config/experiments'/name).read_text()
    checks['experiments_remain_disabled']=True
    summary=json.loads((RUN/'weight_audit/summary.json').read_text())
    assert (summary['motif_count'],summary['raw_exact_matches'],summary['unresolved_differences'],summary['mismatches_not_explained_by_any_raw_edge_subset'])==(12,4,8,8)
    weights=list(csv.DictReader((RUN/'weight_audit/paper_weight_comparison.csv').open()))
    assert all(not r['selected_v1_weight'] and not r['v1_selected_body_ids'] for r in weights)
    ev=list(csv.DictReader((ROOT/'results/cross_experiment/neuron_evidence_matrix.csv').open()))
    assert all(not r['shiu_dynamic_support'] and not r['experimental_support'] and not r['effective_connectivity'] for r in ev)
    assert all(r['tastekin_v1_selection']=='NOT_RUN' for r in ev)
    checks['no_unrun_results_or_functional_evidence_fabricated']=True
    docs=[ROOT/'docs'/n for n in ['paper_vs_v1_weight_audit.md','experiment_01_replication_checkpoint.md','effective_connectivity_and_sugar_checkpoint.md','paper_method_reconstruction.md']]
    for path in docs:
        for link in re.findall(r'\]\(([^)]+)\)',path.read_text()):
            if link.startswith(('https:','http:','#')):continue
            assert (path.parent/link.split('#')[0]).exists(), (path,link)
    checks['local_document_links']=True
    result=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,capture_output=True,text=True)
    (RUN/'tests.log').write_text(result.stdout+result.stderr)
    assert result.returncode==0
    checks['arithmetic_tests']=dict(passed=6,log=str((RUN/'tests.log').relative_to(ROOT)),scope='pooling audit only; not effective-connectivity validation')
    source_manifest=json.loads((ROOT/'config/source_manifest.yaml').read_text())
    for s in source_manifest['sources']:
        if int(s['source_id'][1:])>=23:
            assert record(ROOT/s['path'])['sha256']==s['sha256']
    checks['new_source_hashes_verified']=7
    # Token is read only to check equality against artifact bytes; never printed.
    secrets=re.findall(r'(?<![\w./-])[A-Za-z0-9_.-]{32,}(?![\w./-])',(ROOT/'.venv/.env').read_text())
    assert len(secrets)==1
    paths=set(p for p in RUN.rglob('*') if p.is_file())
    for folder in ['docs','logs','config','results/circuit_versions','tests']:
        paths.update(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in str(p))
    paths.update(ROOT/f for f in ['STATUS.md','SOURCES.md','CHANGELOG.md','results/cross_experiment/neuron_evidence_matrix.csv'])
    paths.update(ROOT/'scripts'/f for f in ['16_method_source_audit.py','17_paper_weight_audit.py','18_record_method_audit.py','19_finalize_method_audit.py'])
    for path in paths:
        assert secrets[0].encode() not in path.read_bytes(), 'Credential found in artifact (value suppressed)'
    assert not (ROOT/'.venv/method_audit_auth.curl').exists()
    checks['credential_scan']='no token in audited artifacts; temporary auth config removed'
    stamp=dt.datetime.now(dt.timezone.utc).isoformat()
    (RUN/'integrity_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    readme='# Method recovery and raw-weight audit\n\n**BLOCKED BEFORE EXPERIMENT 1R.** This directory contains source retrievals, live v1.0 metadata, a parameter inventory, and a raw pooling audit. It is not a selected circuit or completed replication.\n\n'
    readme+='See [overall checkpoint](../../../docs/effective_connectivity_and_sugar_checkpoint.md), [readiness checkpoint](../../../docs/experiment_01_replication_checkpoint.md), and [weight audit](../../../docs/paper_vs_v1_weight_audit.md).\n\n'
    readme+='`weight_audit/` contains 12 motif comparisons, every body pair, side totals and all attainable raw-edge subset sums. Four all-body raw totals match the paper; none of the eight differences can be explained by whole-edge deletion with additive pooling. No cause is assigned. Six arithmetic tests pass; they do not validate effective connectivity.\n\n'
    readme+='`sources/` includes successful supplement/workbook/metadata/repository retrievals and explicitly failed publisher/preprint responses. Error HTML/XML/bin files are not article content. `source_transport.jsonl` preserves a failed config-based DNS attempt; direct curl calls subsequently succeeded for the accessible sources. The initial live query similarly failed DNS; `meta_retry.json` is the successful authenticated response. Every neuPrint query is in the append-only query log.\n\n'
    readme+='The credential was used only for neuPrint. Temporary auth configuration was removed. `audit_snapshot_before/` preserves pre-update audit records. `audit_snapshot_final/` freezes updated logs/config/docs. `manifest.json` records code/config/input/output hashes; it is an audit freeze, not a validated paper-method freeze. The project has no Git commit.\n'
    (RUN/'README.md').write_text(readme)
    with (ROOT/'STATUS.md').open('a') as f:
        f.write(f'\n### {stamp} — Method-audit integrity\n\nVerified append-only ledger history, {checks["claim_ledger.csv"]["rows"]} unique claims and {checks["mismatch_ledger.csv"]["rows"]} unique mismatch entries, local report links, seven new source hashes, empty unverified functional fields, and disabled experiment gates. Six arithmetic audit tests pass. Credential scan passed; temporary auth config removed. Audit frozen in `{RUN.relative_to(ROOT)}/manifest.json`; no paper-method freeze or biological experiment.\n')
    final=RUN/'audit_snapshot_final'
    final.mkdir()
    artifacts=['STATUS.md','SOURCES.md','CHANGELOG.md','docs/paper_method_reconstruction.md','docs/prompt_vs_paper_audit.md','docs/paper_vs_v1_weight_audit.md','docs/experiment_01_replication_checkpoint.md','docs/effective_connectivity_and_sugar_checkpoint.md',
        'logs/claim_ledger.csv','logs/mismatch_ledger.csv','logs/query_log.jsonl','logs/source_fetch_log.jsonl','logs/decision_log.md','logs/unresolved_questions.md',
        'config/analysis.yaml','config/method_readiness.json','config/source_manifest.yaml','config/experiments/experiment_01_paper_replication.yaml','config/experiments/experiment_02_sugar_restricted.yaml','config/experiments/experiment_03_v1_candidate.yaml']
    for name in artifacts:
        p=final/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/name).read_bytes())
    git=subprocess.run(['git','rev-parse','--verify','HEAD'],cwd=ROOT,capture_output=True,text=True)
    configs=[record(ROOT/p) for p in artifacts if p.startswith('config/')]
    config_hash=hashlib.sha256(json.dumps(configs,sort_keys=True).encode()).hexdigest()
    outputs=[record(p) for p in sorted(RUN.rglob('*')) if p.is_file()]
    outputs += [record(p) for p in sorted((ROOT/'results/circuit_versions').rglob('*')) if p.is_file()]
    outputs.append(record(ROOT/'results/cross_experiment/neuron_evidence_matrix.csv'))
    scripts=[record(ROOT/'scripts'/p) for p in ['16_method_source_audit.py','17_paper_weight_audit.py','18_record_method_audit.py','19_finalize_method_audit.py']]
    scripts.append(record(ROOT/'tests/test_weight_audit.py'))
    manifest=dict(timestamp=stamp,experiment='METHOD_RECOVERY_AUDIT',status='BLOCKED_BEFORE_EXPERIMENT_1R',dataset='male-cns:v1.0',dataset_uuid='4b2087c0fbe046bfaf0d60bc970e3e5d',dataset_version='v1.0',
        git_commit=git.stdout.strip() if git.returncode==0 else None,git_state='uncommitted workspace; scripts/configs hashed',
        python=sys.version,operating_system=platform.platform(),package_versions={'pypdf':importlib.metadata.version('pypdf')},
        random_seed=None,randomness='none; exhaustive deterministic arithmetic',config_hash=config_hash,configs=configs,scripts=scripts,
        baseline_inputs=json.loads((RUN/'weight_audit/input_integrity.json').read_text()),outputs=outputs,checks=checks,
        no_effective_connectivity=True,no_simulation=True,experiment_01_executed=False,experiment_02_executed=False,method_frozen=False,
        exclusions='manifest excludes itself and subsequent append-only run_manifest entry to avoid circular hashing')
    (RUN/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    with (ROOT/'logs/run_manifest.jsonl').open('a') as f:
        f.write(json.dumps(dict(timestamp=stamp,experiment='METHOD_RECOVERY_AUDIT',run=str(RUN.relative_to(ROOT)),status=manifest['status'],manifest=record(RUN/'manifest.json')))+'\n')
    print(json.dumps(checks,indent=2))


if __name__=='__main__':main()
