"""Optional, explicitly invoked pretrained reference. Never used by the fly model."""
import json
import os
import time
import urllib.request
from .common import now, write_json, read_json, event, sha256
from .corpus import TEST, prompt, public
from .judge import judge, clean_code
from .experiment import latest, summarize

MODEL='gpt-4.1-mini-2025-04-14'

def requests(run=None):
    run=run or latest()
    if run is None:raise ValueError('Run a local pilot first')
    out=run/'hosted';out.mkdir(exist_ok=True)
    for problem in TEST:
        write_json(out/f'{problem["id"]}-request.json',dict(model=MODEL,input=prompt(problem),
                   max_output_tokens=512,temperature=0,store=False))
    return out

def collect(run=None):
    run=run or latest();results=[];errors=[]
    config=read_json(run/'config.json')
    for problem in TEST:
        path=run/'hosted'/f'{problem["id"]}-response.json'
        if not path.exists():
            error_path=path.with_name(f'{problem["id"]}-error.json')
            if error_path.exists():errors.append(dict(problem=problem['id'],status='transport_error',error=read_json(error_path)))
            continue
        response=read_json(path)
        if response.get('error') or response.get('status') not in ('completed','incomplete'):
            errors.append(dict(problem=problem['id'],status='provider_error',error=response.get('error','Missing response status')));continue
        raw=''.join(c.get('text','') for item in response.get('output',[]) for c in item.get('content',[]) if c.get('type')=='output_text')
        if not raw:
            errors.append(dict(problem=problem['id'],status='empty_response'));continue
        code=clean_code(raw)
        limited=code.encode()[:config['max_new_bytes']].decode('utf-8',errors='replace')
        timing=path.with_name(f'{problem["id"]}-timing.json')
        result=dict(problem=public(problem),prompt=prompt(problem),code=limited,full_code=code,
                    full_output_judgement=judge(code,problem['cases']),judgement=judge(limited,problem['cases']),
                    output_bytes=len(limited.encode()),full_output_bytes=len(code.encode()),
                    latency_seconds=read_json(timing)['seconds'] if timing.exists() else None,
                    usage=response.get('usage'),model=response.get('model'),response_id=response.get('id'),
                    provider_status=response.get('status'),response_sha256=sha256(path),
                    stop_reason='byte_budget' if len(code.encode())>config['max_new_bytes'] else response.get('status'))
        results.append(result)
    timed=[r for r in results if r['latency_seconds'] is not None]
    summary=summarize([{**r,'latency_seconds':r['latency_seconds'] or 0} for r in results])
    summary['mean_latency_seconds']=sum(r['latency_seconds'] for r in timed)/len(timed) if timed else None
    summary['latency_measurements']=len(timed)
    report=dict(arm='pretrained-llm',model=MODEL,created_at=now(),results=results,errors=errors,
                summary=summary,completed=len(results)==len(TEST),
                comparison='pretrained reference; unequal pretraining/compute; same visible prompt, common code-byte cap',
                request_limit='six requests, each max_output_tokens=512, no retries',
                pretraining_contamination='unknown; these algorithm families are common in public code')
    write_json(run/'pretrained-llm-evaluation.json',report)
    return report

def run_baseline(run=None):
    run=run or latest();out=requests(run)
    key=os.environ.get('OPENAI_API_KEY')
    if not key:raise ValueError('OPENAI_API_KEY is not set')
    for problem in TEST:
        path=out/f'{problem["id"]}-response.json'
        if path.exists():continue
        payload=(out/f'{problem["id"]}-request.json').read_bytes()
        req=urllib.request.Request('https://api.openai.com/v1/responses',data=payload,
                headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
        start=time.perf_counter()
        try:
            with urllib.request.urlopen(req,timeout=60) as response:
                write_json(path,json.load(response))
        except Exception as exc:
            write_json(out/f'{problem["id"]}-error.json',dict(time=now(),type=type(exc).__name__,message=str(exc)))
            event(run,'provider_error',problem=problem['id'],error_type=type(exc).__name__)
            break
        write_json(out/f'{problem["id"]}-timing.json',dict(seconds=time.perf_counter()-start))
    return collect(run)
