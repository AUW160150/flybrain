"""Loopback-only local research UI. No external accounts or code execution endpoints."""
import json
import mimetypes
import secrets
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit
import torch
from .common import ROOT,read_json,write_json,now,sha256,source_hashes
from .corpus import TEST,public
from .experiment import latest,generate_fly,generate_transformer,setup,pilot
from .connectome import load_graph
from .models import Reservoir,Readout,TinyTransformer
from .judge import judge

TOKEN=secrets.token_urlsafe(24)
LOCK=threading.Lock()
JOBS={}
BRAIN=None
UI_API_VERSION=2

def dashboard():
    from .curriculum_dashboard import latest_v2,dashboard_v2
    current=latest_v2()
    if current:return dict(ui_api_version=UI_API_VERSION,**dashboard_v2(current))
    run=latest()
    graph=ROOT/'data/graph/manifest.json'
    data=dict(ui_api_version=UI_API_VERSION,protocol='pilot-v1',graph=read_json(graph) if graph.exists() else None,run=run.name if run else None,
              problems=[public(p) for p in TEST],evaluations={},training={},status=None)
    if run:
        data['config']=read_json(run/'config.json');data['status']=read_json(run/'status.json')
        for p in run.glob('*-evaluation.json'):data['evaluations'][p.name.replace('-evaluation.json','')]=read_json(p)
        for p in run.glob('*-training.json'):data['training'][p.name.replace('-training.json','')]=read_json(p)
        events=run/'events.jsonl'
        data['events']=[json.loads(line) for line in events.read_text().splitlines()[-80:]] if events.exists() else []
    return data

def brain():
    global BRAIN
    if BRAIN is None:BRAIN=load_graph()
    return BRAIN

def create_job(action,request):
    if not LOCK.acquire(blocking=False):raise ValueError('Another experiment is running; wait for it to finish')
    job_id=uuid.uuid4().hex
    job=dict(id=job_id,status='running',action=action,started_at=now(),code='',activity=None)
    JOBS[job_id]=job
    def work():
        try:
            if action=='load':
                W,ids,m=brain();job['result']=dict(neurons=len(ids),edges=W.nnz,integrity='verified')
            elif action=='train':
                if request.get('protocol')=='curriculum-v2':
                    from .curriculum_experiment import run_v2
                    from .curriculum_audit import audit_run
                    run=run_v2();audit_run(run)
                    job['result']=dict(run=run.name)
                else:job['result']=dict(run=pilot().name)
            else:
                from .curriculum_dashboard import latest_v2,interactive
                current=latest_v2()
                if current:
                    W,ids,_=brain()
                    def update_v2(code,activity):job.update(code=code,activity=activity)
                    result=interactive(current,request,W,ids,update_v2)
                    job['result']=result;job['code']=result['code']
                    write_json(current/'interactive'/f'{job_id}.json',dict(time=now(),inference_sources=source_hashes(),**result))
                    job['status']='completed'
                    return
                run=latest()
                if not run or not (run/'fly.pt').exists():raise ValueError('No checkpoint; run the training pilot first')
                config=read_json(run/'config.json');setup(config['seed'])
                if request.get('statement'):
                    statement=request['statement']
                    if not isinstance(statement,str) or len(statement.encode())>600:raise ValueError('Custom statement must be at most 600 UTF-8 bytes')
                    problem=dict(id='custom',family='user-supplied',statement=statement)
                    cases=[]
                else:
                    problem=next((p for p in TEST if p['id']==request.get('problem')),None)
                    if problem is None:raise ValueError('Unknown problem')
                    cases=problem['cases']
                arm=request.get('arm','fly')
                if arm not in ('fly','transformer','no-recurrence'):raise ValueError('Unsupported model')
                artifact=read_json(run/'artifacts.json')
                if sha256(run/f'{arm}.pt')!=artifact[f'{arm}.pt']:raise ValueError('Checkpoint integrity failed')
                if arm=='transformer':
                    model=TinyTransformer();model.load_state_dict(torch.load(run/f'{arm}.pt',weights_only=True));model.eval()
                    result=generate_transformer(model,problem,config['max_new_bytes'])
                else:
                    W,ids,m=brain();reservoir=Reservoir(W,config['seed'],config['features'],arm=='fly')
                    model=Readout(config['features']);model.load_state_dict(torch.load(run/f'{arm}.pt',weights_only=True));model.eval()
                    def update(code,activity):job.update(code=code,activity=activity)
                    result=generate_fly(reservoir,model,problem,ids,config['max_new_bytes'],update)
                result.update(arm=arm,problem=public(problem),judgement=judge(result['code'],cases) if cases else
                              dict(status='unscored',passed=None,detail='Custom prompt has no evaluation cases'))
                job['result']=result;job['code']=result['code']
                write_json(run/'interactive'/f'{job_id}.json',dict(time=now(),inference_sources=source_hashes(),**result))
            job['status']='completed'
        except Exception as exc:job.update(status='failed',error=str(exc))
        finally:job['finished_at']=now();LOCK.release()
    threading.Thread(target=work,daemon=True).start()
    return job

class Handler(BaseHTTPRequestHandler):
    def send(self,value,status=200,ctype='application/json'):
        raw=json.dumps(value,allow_nan=False).encode() if ctype=='application/json' else value
        self.send_response(status);self.send_header('Content-Type',ctype);self.send_header('Content-Length',str(len(raw)))
        self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(raw)

    def local_host(self):
        return self.headers.get('Host') in (f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}')

    def do_GET(self):
        if not self.local_host():self.send({'error':'Local host required'},403);return
        path=urlsplit(self.path).path
        if path=='/api/dashboard':self.send(dict(token=TOKEN,**dashboard()));return
        if path.startswith('/api/jobs/'):
            job=JOBS.get(path.rsplit('/',1)[1]);self.send(job or {'error':'Unknown job'},200 if job else 404);return
        if path.startswith('/docs/'):
            file=(ROOT/path.lstrip('/')).resolve()
            if file.parent==ROOT/'docs' and file.suffix=='.md' and file.exists():self.send(file.read_bytes(),ctype='text/plain; charset=utf-8');return
        if path=='/api/export':self.send(dashboard());return
        file=ROOT/'web'/({'/':'index.html','/app.js':'app.js','/style.css':'style.css'}.get(path,'missing'))
        if file.is_file():self.send(file.read_bytes(),ctype=(mimetypes.guess_type(file)[0] or 'text/plain')+'; charset=utf-8')
        else:self.send({'error':'Not found'},404)

    def do_POST(self):
        if not self.local_host() or self.headers.get('X-Flycodes-Token')!=TOKEN:
            self.send({'error':'Local session token required'},403);return
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=4096:raise ValueError('Request limit: 4096 bytes')
            value=json.loads(self.rfile.read(length))
            action={'/api/load':'load','/api/train':'train','/api/generate':'generate'}.get(self.path)
            if not action:raise ValueError('Unknown action')
            self.send(create_job(action,value),202)
        except (ValueError,TypeError) as exc:self.send({'error':str(exc)},400)

    def log_message(self,*args):pass

def serve(port=8765):
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    print(f'Flycodes: http://127.0.0.1:{port}',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
