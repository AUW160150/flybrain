"""Audit frozen v2 receipts and reproduce a saved generation via the UI backend."""
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from flycodes.common import read_json,write_json,sha256,now
from flycodes.curriculum_dashboard import latest_v2,interactive
from flycodes.connectome import load_graph

run=latest_v2()
if run is None:raise SystemExit('No completed v2 run')
config=read_json(run/'config.json');artifacts=read_json(run/'artifacts.json')
for name,expected in artifacts.items():
    if sha256(run/name)!=expected:raise RuntimeError('Artifact mismatch: '+name)
for name,expected in config['sources'].items():
    if sha256(run/'source'/Path(name).name)!=expected:raise RuntimeError('Source snapshot mismatch: '+name)
freeze=read_json(run/'evaluation-freeze.json')
if sha256(run/'config.json')!=freeze['config_sha256']:raise RuntimeError('Evaluation freeze mismatch')
audit=read_json(run/'test-adequacy-audit/manifest.json')
for name,expected in audit['hashes'].items():
    if sha256(run/'test-adequacy-audit'/name)!=expected:raise RuntimeError('Audit artifact mismatch: '+name)
for row in audit['scores']:
    name=f'{row["arm"]}-{row["split"]}-evaluation.json'
    original=read_json(run/name);corrected=read_json(run/'test-adequacy-audit'/name)
    if [r['code'] for r in original['results']]!=[r['code'] for r in corrected['results']]:
        raise RuntimeError('Audit changed generated candidates: '+name)
W,ids,graph=load_graph()
reference=read_json(run/'fly-s7-test-evaluation.json')['results'][0]
result=interactive(run,dict(arm='fly-s7',problem=reference['problem']['id']),W,ids,lambda *args:None)
if result['code']!=reference['code']:raise RuntimeError('Generation reproduction mismatch')
if result['judgement']['status']!=reference['judgement']['status']:raise RuntimeError('Judge reproduction mismatch')
old=root/'docs/verification-v2.json';receipt=read_json(old) if old.exists() else {}
receipt.update(verified_at=now(),run=run.name,artifact_hashes_checked=len(artifacts),artifact_integrity='passed',
    source_snapshot_integrity='passed',evaluation_freeze='passed',graph_integrity='passed',
    interactive_backend_exact_reproduction=True,reproduced_problem=reference['problem']['id'],
    test_audit_integrity='passed',test_audit_preserves_original_candidates=True)
write_json(old,receipt)
print(receipt)
