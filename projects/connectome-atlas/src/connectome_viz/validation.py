from __future__ import annotations
import os, subprocess, json, xml.etree.ElementTree as ET
from .provenance import *

def validate():
    env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(ROOT/'src'),OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1')
    junit=REPORT/'pytest.xml'
    p=subprocess.run([str(ROOT/'.venv/bin/python'),'-B','-m','pytest',str(ROOT/'tests'),'-q','--tb=short','-p','no:cacheprovider','--junitxml='+str(junit)],env=env,capture_output=True,text=True,timeout=120)
    (REPORT/'pytest.txt').write_text(p.stdout+p.stderr)
    tree=ET.parse(junit);suites=tree.findall('.//testsuite');counts={k:sum(int(s.get(k,0)) for s in suites) for k in ['tests','failures','errors','skipped']}
    browser=read(REPORT/'browser-validation.json') if (REPORT/'browser-validation.json').exists() else dict(status='skipped',reason='Browser harness not yet executed')
    result=dict(utc=now(),code_revision=revision(),unit=counts,passed=counts['tests']-counts['failures']-counts['errors']-counts['skipped'],failed=counts['failures']+counts['errors'],browser=browser,skipped=[{'test':'accelerator','reason':'CPU-only task; accelerator deliberately unused'},{'test':'full-production-G0/G1 index conservation','reason':'Resource-heavy ingestion not run; fixture coverage separate from production completeness'},{'test':'checkpoint weight/activity numerical replay','reason':'Safe loader rejected NumPy RNG pickle state; no unsafe fallback'},{'test':'neuPrint fetch_adjacencies installed-schema check','reason':'neuprint not installed or used; topology comes from verified bulk schema'}],protected_static_hashes_match=read(REPORT/'inventory.json')['protected']==protect_inventory())
    atomic(REPORT/'validation.json',result)
    if result['failed']:print(p.stdout+p.stderr)
    return result
