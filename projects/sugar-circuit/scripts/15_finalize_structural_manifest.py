"""Freeze run provenance and verify the credential is absent from project artifacts."""
from pathlib import Path
import csv,json,hashlib,datetime,platform,sys,shutil,subprocess,importlib.metadata,re
ROOT=Path(__file__).resolve().parents[1];REL=(ROOT/'config/current_structural_run.txt').read_text().strip();RUN=ROOT/REL
def sha(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def record(p):return dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=sha(p))
def main():
    checks=json.loads((RUN/'validation_checks.json').read_text());assert checks['status']=='PASS'
    # Remove only the temporary credential copy created for this task.
    auth=ROOT/'.venv/.neuprint-auth.curl'
    if auth.exists():auth.unlink()
    token=[x.split(':',1)[1].strip().encode() for x in (ROOT/'.venv/.env').read_text().splitlines() if x.lower().startswith('authorization_token:')]
    assert len(token)==1 and token[0]
    leaks=[];scanned=0
    for p in ROOT.rglob('*'):
        if not p.is_file() or any(x in ('.venv','.git','__pycache__') for x in p.relative_to(ROOT).parts):continue
        scanned+=1;tail=b''
        with p.open('rb') as f:
            while chunk:=f.read(8*1024*1024):
                if token[0] in tail+chunk:leaks.append(str(p.relative_to(ROOT)));break
                tail=chunk[-len(token[0]):]
    assert not leaks, 'Credential found in artifact paths: '+repr(leaks)
    print('Credential scan passed:',scanned,'files; temporary copy removed; original env preserved',flush=True)
    # Schema/identifier and link checks on final documents and ledgers.
    ledger_counts={}
    for name,key in [('claim_ledger.csv','claim_id'),('mismatch_ledger.csv','mismatch_id')]:
        rows=list(csv.DictReader(open(ROOT/'logs'/name)));assert len(rows)==len({r[key] for r in rows});assert all(None not in r for r in rows);ledger_counts[name]=len(rows)
    unresolved=[]
    for doc in [ROOT/'docs/structural_connectivity_checkpoint.md',RUN/'README.md']:
        for target in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
            if '://' in target or target.startswith('#'):continue
            path=(doc.parent/target.split('#')[0]).resolve()
            if path==RUN/'manifest.json':continue
            if not path.exists():unresolved.append(str(path))
    assert not unresolved,unresolved
    for p in (ROOT/'config/experiments').glob('*.yaml'):assert 'execution_allowed: false' in p.read_text()
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with open(ROOT/'STATUS.md','a') as f:f.write(f'\n### {now} — Structural artifact integrity\n\nAll 13 required outputs, 746,910 edge records, 33,851 complete shortest paths, capped path-example files and 37,246-node/643,834-edge GraphML pass integrity checks. Four synthetic behavior tests pass. Ledgers contain {ledger_counts["claim_ledger.csv"]} unique claims and {ledger_counts["mismatch_ledger.csv"]} unique mismatch records. Local report links resolve. No credential occurs in project artifacts; the temporary auth config was removed and the original ignored environment file preserved. Run provenance is frozen in `{REL}/manifest.json` and audit snapshots. Stop remains at structural Gates 2/3.\n')
    fetch=json.loads((RUN/'raw/flat_weights_provenance.json').read_text());existing=[json.loads(l).get('output_file') for l in (ROOT/'logs/source_fetch_log.jsonl').read_text().splitlines()]
    if fetch['output_file'] not in existing:
        with open(ROOT/'logs/source_fetch_log.jsonl','a') as f:f.write(json.dumps(fetch)+'\n')
    snapshot=RUN/'audit_snapshot';snapshot.mkdir(exist_ok=True)
    for name in ['claim_ledger.csv','mismatch_ledger.csv','query_log.jsonl','decision_log.md','unresolved_questions.md']:
        shutil.copyfile(ROOT/'logs'/name,snapshot/name)
    shutil.copyfile(ROOT/'STATUS.md',snapshot/'STATUS.md')
    shutil.copyfile(ROOT/'docs/structural_connectivity_checkpoint.md',snapshot/'structural_connectivity_checkpoint.md')
    security=dict(timestamp=now,credential_scan_files=scanned,credential_leaks=0,temporary_credential_copy_removed=True,original_env_preserved=True,local_links_valid=True,ledger_counts=ledger_counts,experiments_execution_disabled=True)
    (RUN/'artifact_integrity.json').write_text(json.dumps(security,indent=2)+'\n')
    inputs=[ROOT/'data/raw/connectome-weights-male-cns-v1.0-minconf-0.5.feather',ROOT/'data/raw/body-annotations-male-cns-v1.0-minconf-0.5.feather',ROOT/'data/raw/body-neurotransmitters-male-cns-v1.0.feather',ROOT/'results/validation/20261006T171922Z/resolved_bodies.csv',ROOT/'paper/primary/figure6.jpg',ROOT/'AGENTS.md',ROOT/'docs/RESEARCH_PROTOCOL.md']
    scripts=sorted((ROOT/'scripts').glob('0[5-9]_*.py'))+sorted((ROOT/'scripts').glob('1[0-5]_*.py'))+[ROOT/'scripts/test_structural_search.py']
    # A redirected stdout log changes after the manifest is written. It is diagnostic,
    # not scientific provenance; explicitly exclude it rather than store a stale hash.
    outputs=[record(p) for p in sorted(RUN.rglob('*')) if p.is_file() and p.name not in ('manifest.json','finalization.log')]
    commit=subprocess.run(['git','rev-parse','--verify','HEAD'],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
    manifest=dict(timestamp=now,experiment='GATES_2_3_STRUCTURAL_ONLY',label='STRUCTURAL CONNECTIVITY ONLY',dataset='male-cns:v1.0',dataset_version='v1.0',dataset_uuid='4b2087c0fbe046bfaf0d60bc970e3e5d',metadata_start=REL+'/raw/meta_start.json',metadata_end=REL+'/raw/meta_end.json',git_commit=commit.stdout.strip() if commit.returncode==0 else None,git_state='uncommitted local checkpoint; code hashes retained',python=sys.version,operating_system=platform.platform(),package_versions={p:importlib.metadata.version(p) for p in ['numpy','scipy','pyarrow','pypdf']},random_seed=None,randomness='none; deterministic directed graph traversal and ascending-ID examples',search_config=json.loads((RUN/'search_config.json').read_text()),search_config_sha256=sha(RUN/'search_config.json'),input_files=[record(p) for p in inputs],scripts=[record(p) for p in scripts],requirements=record(ROOT/'requirements-structural.txt'),output_files=outputs,validation=checks,artifact_integrity=security,scientific_limitations=['Puddle identity unmapped','Paper snapshot/pooling and eight figure-total differences unresolved','Paper exact equation/normalization/bootstrap/pruning/simulation methods unresolved','Anatomical midline crossings and physiological effects unverified','All graph comparisons use the stated raw source and four-hop simple-path bounds; E legs are separate'],no_effective_connectivity=True,no_statistical_replication=True,no_simulation=True,strict_replication_claimed=False)
    manifest['excluded_from_output_hashes']={'manifest.json':'Self-referential; SHA256 is recorded in logs/run_manifest.jsonl','analysis/finalization.log':'Diagnostic stdout log may change after manifest generation; not scientific evidence'}
    (RUN/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    with open(ROOT/'logs/run_manifest.jsonl','a') as f:f.write(json.dumps(dict(timestamp=now,experiment='GATES_2_3_STRUCTURAL_ONLY',dataset=manifest['dataset'],dataset_uuid=manifest['dataset_uuid'],output_directory=REL,manifest_path=REL+'/manifest.json',manifest_sha256=sha(RUN/'manifest.json'),git_commit=manifest['git_commit'],python=sys.version,operating_system=platform.platform(),package_versions=manifest['package_versions'],random_seed=None,config_hash=manifest['search_config_sha256'],required_outputs_verified=True))+'\n')
    print('Manifest frozen:',len(outputs),'output artifacts;',sum(x['bytes'] for x in outputs),'bytes;',ledger_counts,flush=True)

if __name__=='__main__':main()
