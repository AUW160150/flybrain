"""Verify existing artifacts and directly exercise the actual interactive inference path."""
import base64
import hashlib
import json
import re
import sys
import time
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from flycodes.common import now,sha256,read_json,write_json
from flycodes.experiment import latest
from flycodes.server import create_job

run=latest()
checks=read_json(run/'artifacts.json')
bad=[name for name,h in checks.items() if sha256(run/name)!=h]
if bad:raise RuntimeError(f'Artifact mismatch: {bad}')
sources=read_json(run/'config.json')['sources']
for path,h in sources.items():
    if sha256(run/'source'/Path(path).name)!=h:raise RuntimeError('Source snapshot mismatch')

graph=read_json(root/'data/graph/manifest.json')
verified=[]
for source,label in zip(graph['raw_sources'],['annotations','weights']):
    headers=(root/f'docs/{label}-source.headers').read_text()
    matches=re.findall(r'md5=([^\s,]+)',headers)
    if not matches:raise RuntimeError('Official MD5 header missing')
    h=hashlib.md5()
    with Path(source['path']).open('rb') as f:
        for chunk in iter(lambda:f.read(8<<20),b''):h.update(chunk)
    actual=base64.b64encode(h.digest()).decode()
    if actual!=matches[-1]:raise RuntimeError('Source MD5 differs from official object')
    verified.append(dict(url=source['url'],local_md5_base64=actual,official_md5_base64=matches[-1],matches=True,sha256=source['sha256']))
write_json(root/'docs/source-verification.json',dict(time=now(),files=verified))

job=create_job('generate',dict(arm='fly',problem='two-sum'))
while job['status']=='running':time.sleep(.1)
if job['status']!='completed':raise RuntimeError(job)
saved=read_json(run/'fly-evaluation.json')['results'][0]
if job['result']['code']!=saved['code']:raise RuntimeError('Reproduction mismatch')
if job['result']['judgement']['status']!=saved['judgement']['status']:raise RuntimeError('Judge mismatch')
verification=dict(time=now(),run=run.name,artifact_hashes_checked=len(checks),artifact_integrity='passed',
    captured_source_integrity='passed',official_source_md5='passed',interactive_generation='passed',
    interactive_job=job['id'],exact_code_reproduction=True,
    http_socket_verification='blocked: PermissionError binding loopback port',
    browser_verification='blocked: installed Chrome terminated under managed sandbox',
    pretrained_llm='unmeasured: authenticated transport failed DNS',
    tests_command='../../.venv/bin/python -m pytest -q')
write_json(root/'docs/verification.json',verification)
print(json.dumps(verification,indent=2))
