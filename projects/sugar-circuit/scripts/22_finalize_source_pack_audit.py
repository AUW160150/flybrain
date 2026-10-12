"""Validate and freeze this source/math audit, not the paper's full method."""
import csv
import datetime as dt
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
REL = Path('results/method_recovery/20261006T220302Z')
RUN = ROOT / REL


def record(path):
    return dict(path=str(path.relative_to(ROOT)), bytes=path.stat().st_size,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest())


CHECKPOINT = '''# Experiment 1R readiness checkpoint — source-pack continuation

**The mathematical core is implemented and tested. Experiment 1R remains unrun because its selection rules are not fully specified.** Run: `results/method_recovery/20261006T220302Z/`. Earlier readiness reports are preserved in the prior run and this run's before-snapshot.

The [final/preprint audit](final_vs_preprint_method_diff.md) documents recovered final Methods, verified preprint v2 XML, 48 parameter records, and 18 comparison rows. The source pack substantially improved access; complete final PDF access is no longer the blanket blocker.

| Required checkpoint question | Current answer |
| --- | --- |
| 1. Fully recovered method? | Partially. Matrix algebra, unsigned weights, both 80th-percentile criteria and bootstrap constants are confirmed. Execution-level selection policies remain unresolved. |
| 2. Remaining assumptions? | No unknown biological defaults adopted. Graph/filter/denominator eligibility; score grouping/body/type/bilateral pooling; percentile populations/zeros/estimator; candidate expansion and per-direction horizons/stopping remain open. |
| 3. Published circuit recovered in v1.0? | NOT_ASSESSED. No biological EC selection ran. |
| 4. Named neurons recovered? | Selection unknown. Existing validated identities for Quasimodo, Clavicle, GNG015, Sternum, Roundup, Roundtree and GNG472 are preserved. |
| 5. Missing neurons? | Not assessed; no failed-selection claims. Puddle/Tentacular and complete reference inventory remain unresolved. |
| 6. Additional selected neurons? | Not assessed; no GNG021 or other candidate was forced. |
| 7. Weights matching after selection? | Unknown. Prior all-body raw comparison has 4/12 matches; not selected weights. |
| 8. Remaining raw differences? | Eight, unchanged from the prior validated audit. |
| 9. Explanation for differences? | Whole-body/whole-edge removal with additive pooling cannot explain any of the eight under fixed mappings. Historical snapshot, synapse filters or other pooling are unresolved. |
| 10. Ready to freeze full method? | NO. 21 core/helper tests pass plus 6 prior tests, but the significant-path iterator, bootstrap CI policy and motif selector are not implemented/validated. |
| 11. Ready for unchanged sugar application? | NO. LB3b, LB3c and combined conditions remain disabled. |

The same 80th percentile selects different synthetic candidates under unresolved reference populations, pooling or hop horizons. See [examples](../results/method_recovery/20261006T220302Z/selection_ambiguity_examples.json). Passing algebra tests cannot resolve those source ambiguities.

The next required source is the Figure 6G/S16 generating function and call/config, including adjacency/denominator definition. An equivalent explicit primary-source description can also resolve B01–B04 in [readiness configuration](../config/method_readiness.json). Historical figure node/body/weight tables are additionally needed for complete comparison and discrepancy attribution. No additional user authorization is needed; this stop follows AGENTS.md and prompt_1.md sections4/7/12/24.

The neuPrint credential works: current v1.0 UUID is `4b2087c0fbe046bfaf0d60bc970e3e5d`. No simulations, method freeze, selected graphs or author contact. Current code/config hashes are audit provenance, not a frozen replication implementation.
'''

OVERALL = '''# Effective connectivity and sugar checkpoint — source-pack continuation

**Recovered final method sections and implemented a tested mathematical core. Biological circuit selection remains source-gated.** New audit: `results/method_recovery/20261006T220302Z/`.

## Method and validation

The user-supplied source pack enabled independently retrieved indexed final Methods and a full, version-verified bioRxiv v2 XML. The [method diff](final_vs_preprint_method_diff.md) separates final confirmation, preprint wording and unresolved details. Final Cell governs; the preprint is not silently treated as identical. The final supplement/Table S1 remain the earlier verified copies. Full final PDF and publication-specific code remain unavailable in the sources checked.

The new [single core](../src/effective_connectivity.py) implements unsigned body-level synapse fractions using postsynaptic total inputs; exact-hop matrix propagation; explicitly referenced nonzero-mean scaling; strict percentile helpers; original-input AND output filtering of supplied scores; and induced raw adjacency. Body identities and laterality remain separate. 21 new tests and 6 prior weight-audit tests pass. This is not a completed iterative circuit selector or bootstrap/motif implementation.

Remaining selection-critical gaps concern graph/filter/denominator eligibility, body/type/bilateral pooling and normalization grouping, percentile comparison populations/estimator, and iterative candidate/horizon/stopping rules. Three synthetic examples demonstrate changed membership with the 80th percentile held fixed. The [48-row inventory](../results/method_recovery/20261006T220302Z/method_parameters.csv) distinguishes known equations from those gaps.

## Paper reproduction and raw weights

Authenticated metadata again verifies `male-cns:v1.0`, UUID `4b2087c0fbe046bfaf0d60bc970e3e5d`, with unchanged mutation/edit identity. The structural baseline was reused.

Experiment 1R is NOT_RUN. Named-node/edge recovery, motor recovery, extra/missing selected neurons and topology precision/recall are NOT_ASSESSED, not zero. Puddle, Tentacular and the complete published selected inventory remain unresolved.

The [prior raw audit](paper_vs_v1_weight_audit.md) remains4/12 exact mapped motif totals and 8 unexplained differences. None of the 8 paper labels is a subset sum of the mapped current raw body-pair weights. Whole-body/whole-edge pruning alone with unchanged mappings and additive pooling is excluded. Historical adjacency, synapse-level filters and other pooling remain possible but unverified explanations. HP gives 0/12 exact and HR the same 4/12 as raw; no correct selected-weight result exists yet.

## Sugar conditions and candidate branches

LB3b, LB3c and their union remain NOT_RUN_METHOD_BLOCKED. Quasimodo/Clavicle/GNG015 retention, whole-path LB3c dominance, motor rankings, convergence and unique/shared branches remain unknown. Source-only restriction is already configured: change starting sensory bodies while retaining the rest of the graph. No threshold tuning.

GNG021 remains an indirect structural candidate overlapping the Quasimodo/GNG015 network; it has not passed or failed the paper method. GNG232/DNg67 labels in final S16A and DNg67/DNge080 in S19 are panel-specific published support, not confirmed Figure 6G selection. Shiu/FlyWire comparison remains a separate version; no dynamical or experimental evidence was imported.

The seven circuit versions and evidence matrix remain separate readiness/reference records. Empty effective/dynamic fields and NOT_RUN never mean biological absence. No functional effect follows from raw weights or the synthetic tests.

## Next required evidence

Recover the Figure 6G/S16 function/config or equally explicit primary rules resolving B01–B04, then finish the same engine and run Experiment 1R. Freeze only after its scientific checkpoint passes; apply unchanged to the three sugar conditions afterward. Historical figure source tables are needed for complete comparison. The [readiness checkpoint](experiment_01_replication_checkpoint.md) answers all 11 required questions. No simulation or additional permission step is part of this task.
'''


def main():
    assert not (RUN/'manifest.json').exists(), 'Immutable audit already finalized'
    stamp = dt.datetime.now(dt.timezone.utc).isoformat()
    (ROOT/'docs/experiment_01_replication_checkpoint.md').write_text(CHECKPOINT)
    (ROOT/'docs/effective_connectivity_and_sugar_checkpoint.md').write_text(OVERALL)
    checks = {}
    for name, key in [('claim_ledger.csv','claim_id'), ('mismatch_ledger.csv','mismatch_id')]:
        path = ROOT/'logs'/name
        rows = list(csv.DictReader(path.open()))
        assert all(None not in r and all(v is not None for v in r.values()) for r in rows)
        assert len(rows)==len({r[key] for r in rows})
        assert path.read_bytes().startswith((RUN/'audit_snapshot_before/logs'/name).read_bytes())
        checks[name] = dict(rows=len(rows), unique_ids=True, earlier_bytes_preserved=True)
    for name in ['STATUS.md','SOURCES.md','CHANGELOG.md','docs/paper_method_reconstruction.md',
                 'docs/prompt_vs_paper_audit.md','logs/decision_log.md','logs/unresolved_questions.md']:
        assert (ROOT/name).read_bytes().startswith((RUN/'audit_snapshot_before'/name).read_bytes()), name
    checks['append_only_history_preserved'] = True
    for path in (ROOT/'logs').glob('*.jsonl'):
        for line in path.read_text().splitlines():
            if line.strip():
                json.loads(line)
    gate = json.loads((ROOT/'config/method_readiness.json').read_text())
    assert gate['core_algebra_implemented'] and gate['effective_math_tests_passed']
    assert len(gate['selection_blockers'])==4
    assert all(gate[key] is False for key in ['method_verified','experiment_01_allowed','experiment_02_allowed','simulation_allowed','method_frozen'])
    for name in ['experiment_01_paper_replication.yaml','experiment_02_sugar_restricted.yaml','experiment_03_v1_candidate.yaml']:
        assert 'execution_allowed: false' in (ROOT/'config/experiments'/name).read_text()
    checks['gates_consistent'] = True
    metadata = json.loads((RUN/'meta_start.json').read_text())
    meta = dict(zip(metadata['columns'], metadata['data'][0]))
    assert meta['dataset']=='male-cns' and meta['tag']=='v1.0'
    assert meta['uuid']=='4b2087c0fbe046bfaf0d60bc970e3e5d'
    checks['dataset_identity'] = meta
    xml = ET.parse(RUN/'sources/preprint_v2_response.xml').getroot()
    assert xml.tag=='article'
    identifiers = [''.join(e.itertext()) for e in xml.iter('article-id')]
    assert '10.1101/2025.08.25.671814' in identifiers and any('671814v2' in x for x in identifiers)
    assert (ROOT/'paper/preprint/tastekin_biorxiv_v2.xml').read_bytes()==(RUN/'sources/preprint_v2_response.xml').read_bytes()
    checks['preprint_identity_and_copy'] = True
    sources = json.loads((ROOT/'config/source_manifest.yaml').read_text())['sources']
    new_sources = [s for s in sources if s['path'].startswith(str(REL)+'/')]
    assert len(new_sources)==18 and len(sources)==len({s['source_id'] for s in sources})
    for source in new_sources:
        assert record(ROOT/source['path'])['sha256']==source['sha256']
    checks['new_source_hashes_verified'] = len(new_sources)
    tests = (RUN/'tests.log').read_text()
    assert 'Ran 27 tests' in tests and '\nOK\n' in tests
    checks['tests'] = dict(passed=27, core_and_threshold=21, existing_weight_audit=6,
                          log=str(REL/'tests.log'), scope='synthetic mathematics; not biological selection')
    from_ambiguity = json.loads((RUN/'selection_ambiguity_examples.json').read_text())
    assert from_ambiguity['scope']=='SYNTHETIC_ONLY_NOT_BIOLOGICAL_RESULTS'
    assert from_ambiguity['target_aggregation']['sum_across_targets']['selected']==['B']
    assert from_ambiguity['target_aggregation']['max_across_targets']['selected']==['A']
    checks['three_material_synthetic_ambiguities'] = True
    parameters = list(csv.DictReader((RUN/'method_parameters.csv').open()))
    assert len(parameters)==48 and len({r['parameter_name'] for r in parameters})==48
    checks['parameter_inventory'] = dict(rows=48, unique_names=True)
    docs = ['docs/final_vs_preprint_method_diff.md', 'docs/experiment_01_replication_checkpoint.md',
            'docs/effective_connectivity_and_sugar_checkpoint.md']
    for name in docs:
        path = ROOT/name
        for link in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if not link.startswith(('https:','http:','#')):
                assert (path.parent/link.split('#')[0]).exists(), (name,link)
    checks['current_checkpoint_links'] = True
    # Existing selected-version and evidence records must remain explicitly unrun.
    evidence = list(csv.DictReader((ROOT/'results/cross_experiment/neuron_evidence_matrix.csv').open()))
    assert all(r['tastekin_v1_selection']=='NOT_RUN' and not r['effective_connectivity'] for r in evidence)
    checks['no_selected_results_fabricated'] = True
    code_files = ['src/__init__.py','src/effective_connectivity.py', 'tests/test_effective_connectivity.py',
        'tests/test_thresholds.py','tests/test_weight_audit.py', 'scripts/20_validate_ec_core.py',
        'scripts/21_record_source_pack_recovery.py','scripts/22_finalize_source_pack_audit.py','requirements-ec.txt']
    for name in code_files:
        if name.endswith('.py'):
            compile((ROOT/name).read_text(), name, 'exec')
    checks['python_source_compilation'] = True
    secrets = re.findall(r'(?<![\w./-])[A-Za-z0-9_.-]{32,}(?![\w./-])', (ROOT/'.venv/.env').read_text())
    assert len(secrets)==1
    audited = [p for p in RUN.rglob('*') if p.is_file()]
    for folder in ['src','tests','scripts','docs','logs','config']:
        audited += [p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in str(p)]
    for path in audited:
        assert secrets[0].encode() not in path.read_bytes(), 'Credential detected (value suppressed)'
    assert not (ROOT/'.venv/method_source_pack_auth.curl').exists()
    checks['credential_scan'] = 'No token in audited artifacts; temporary curl auth removed'
    (RUN/'integrity_checks.json').write_text(json.dumps(checks, indent=2)+'\n')
    (RUN/'README.md').write_text('''# Source recovery and effective-connectivity core audit

**Core mathematics validated; Figure 6G selection remains source-gated.** This is not an Experiment 1R output or a frozen paper implementation.

The final indexed Methods and full preprint v2 XML are archived under `sources/`. Failed 429 response files are not PDFs. `final_vs_preprint_method_diff.csv` has 18 rows; `method_parameters.csv` has 48. `tests.log` records 21 new mathematics/threshold tests plus 6 prior tests, all passing. `selection_ambiguity_examples.json` contains synthetic examples only.

See [method diff](../../../docs/final_vs_preprint_method_diff.md) and [checkpoint](../../../docs/experiment_01_replication_checkpoint.md). `audit_snapshot_before/` preserves pre-update records; `audit_snapshot_final/` freezes code/config/docs/logs as recorded here. Previous dated research artifacts are untouched.

Reproduce the math tests with `.venv/bin/python -m unittest discover -s tests -v`. Script 20 regenerates the synthetic examples in an unfrozen run; it refuses to alter a manifested run. Scripts 21/22 are one-time audit recorders, not experiment runners. No MaleCNS connectivity matrix was loaded into the new core, no biological scores/selection were computed, and no simulation ran.
''')
    with (ROOT/'STATUS.md').open('a') as f:
        f.write(f'\n### {stamp} — Source-pack audit integrity\n\nVerified 27 tests from saved successful run,18 source hashes, 48 unique parameter records, append-only prior history, unique claim/mismatch IDs, current checkpoint links, current dataset identity and credential hygiene. All biological experiment gates remain disabled. Audit manifest: `{REL}/manifest.json`. Full method is not frozen. Concurrent visualization ledger entries were preserved; new method records used currently available IDs.\n')
    snapshot_names = ['STATUS.md','SOURCES.md','CHANGELOG.md', *docs,
        'docs/paper_method_reconstruction.md','docs/prompt_vs_paper_audit.md',
        'config/analysis.yaml','config/method_readiness.json','config/source_manifest.yaml',
        'config/current_method_audit.txt', 'logs/claim_ledger.csv','logs/mismatch_ledger.csv',
        'logs/decision_log.md','logs/unresolved_questions.md','logs/source_fetch_log.jsonl','logs/query_log.jsonl',
        *code_files]
    snapshot_names += ['config/experiments/'+name for name in ['experiment_01_paper_replication.yaml','experiment_02_sugar_restricted.yaml','experiment_03_v1_candidate.yaml']]
    for name in snapshot_names:
        dest = RUN/'audit_snapshot_final'/name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/name, dest)
    git = subprocess.run(['git','rev-parse','--verify','HEAD'],cwd=ROOT,capture_output=True,text=True)
    manifest = dict(timestamp=stamp, experiment='METHOD_SOURCE_PACK_RECOVERY', status=gate['status'],
        dataset='male-cns:v1.0', dataset_uuid=meta['uuid'], git_commit=git.stdout.strip() if git.returncode==0 else None,
        git_state='No commit; exact code/config copies hashed in final snapshot', python=sys.version,
        operating_system=platform.platform(), package_versions={name:importlib.metadata.version(name) for name in ['numpy','scipy']},
        method_frozen=False, experiment_01_executed=False, experiment_02_executed=False, simulation_executed=False,
        biological_effective_connectivity_computed=False, synthetic_math_tests_passed=True,
        randomness='none in synthetic examples/tests; no bootstrap executed', checks=checks,
        inputs=[record(ROOT/'Tastekin_methods_source_pack.md'),record(ROOT/'docs/prompt_1.md'),
                record(ROOT/'results/method_recovery/20261006T214639Z/manifest.json')],
        scripts=[record(ROOT/name) for name in code_files],
        outputs=[record(path) for path in sorted(RUN.rglob('*')) if path.is_file()],
        exclusions='Manifest excludes itself and subsequent run-log entry; credentials excluded')
    (RUN/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    with (ROOT/'logs/run_manifest.jsonl').open('a') as f:
        f.write(json.dumps(dict(timestamp=stamp,experiment='METHOD_SOURCE_PACK_RECOVERY',run=str(REL),status=gate['status'],manifest=record(RUN/'manifest.json')))+'\n')
    print(json.dumps(checks, indent=2))


if __name__=='__main__':
    main()
