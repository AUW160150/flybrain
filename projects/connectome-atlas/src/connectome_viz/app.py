from __future__ import annotations
import csv, io, json, mimetypes, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
from .provenance import *
from . import indexing as ix
from .ingest import FULL,SMALL

WEB=Path(__file__).parent/'web'

def database(scope):
    for p in [FULL,SMALL,ROOT/'cache/topology.sqlite']:
        if p.exists():
            db=ix.connect(p,True)
            if scope in ix.get_meta(db,'complete_scopes',[]):
                deadline=time.monotonic()+20
                db.set_progress_handler(lambda:int(time.monotonic()>deadline),10000)
                return db
            db.close()
    fail('E_INCOMPLETE_INGEST',f'{scope} not indexed. This panel is unavailable, not empty.',scope,'./visualization/viz ingest-full --rss-mib 512 --storage-gib 64 --max-seconds 300')

def state():
    path=REPORT/'dashboard.json'
    if not path.exists(): fail('E_INCOMPLETE_INGEST','Run build-views first','application','./visualization/viz build-views')
    return read(path)

def query(endpoint,q):
    value=lambda name,default=None:q.get(name,[default])[0]
    scope=value('scope','G3')
    if endpoint=='status': return state()
    if endpoint=='architecture': return read(REPORT/'architecture.json')
    if endpoint=='geometry':
        p=REPORT/'geometry.json'
        if not p.exists(): fail('E_GEOMETRY_UNAVAILABLE','No local geometry loaded','anatomy','./visualization/viz fetch-morphology --ids-from visualization/reports/current/subset-ids.json --max-ids 8')
        g=read(p); ident=value('id')
        if ident:
            r=g['records'].get(body_id(ident))
            if not r or r['status']!='loaded': fail('E_GEOMETRY_UNAVAILABLE',f'Geometry not loaded for {ident}','anatomy','./visualization/viz fetch-morphology --ids-from visualization/reports/current/subset-ids.json --max-ids 512',r)
            path=REPORT/'geometry'/(ident+'.json')
            if not path.exists() or sha(path)!=r['geometry_sha256']: fail('E_GEOMETRY_UNAVAILABLE','Geometry cache missing or changed; rerun morphology acquisition','anatomy')
            return read(path)
        return {k:v for k,v in g.items() if k!='records'} | {'available_ids':[k for k,v in g['records'].items() if v['status']=='loaded']}
    if endpoint=='snapshot':
        run=value('run','')
        if run not in [r['run_id'] for r in state()['runs']]: raise ValueError('Unknown run selector')
        p=REPORT/'snapshots'/(run+'.json')
        if not p.exists(): fail('E_CHECKPOINT_UNSTABLE_OR_UNSAFE','This run has no fixed snapshot','weights',f'./visualization/viz snapshot-run --run-dir fly_connectome_lm/runs/{run}')
        return read(p)
    if endpoint=='boundary-partners':
        return boundary_partners(value('id'),value('direction','incoming'),int(value('offset',0)),int(value('limit',50)))
    if endpoint=='ledger':
        p=REPORT/'removal-ledger.json'
        if not p.exists(): fail('E_INCOMPLETE_INGEST','Boundary ledger unavailable until source scan completes','boundary','./visualization/viz ingest-subset --rss-mib 512 --max-seconds 120')
        data=read(p); ident=value('id')
        if ident: return next((r for r in data['rows'] if r['body_id']==body_id(ident)),{'status':'no_matching_node'})
        return data
    db=database(scope)
    try:
        if endpoint=='summary': return ix.summary(db,scope)
        if endpoint=='search': return ix.search(db,scope,value('q',''))
        if endpoint=='node':
            result=ix.node(db,scope,value('id'))
            if (REPORT/'geometry.json').exists():
                geometry=read(REPORT/'geometry.json')['records'].get(result['body_id'],{})
                if geometry.get('status')=='loaded': result['coordinate_provenance']={'kind':'native skeleton geometry; no fabricated node position','source_url':geometry['source_url'],'sha256':geometry['sha256'],'units':'um','factor_applied_once':.008}
            return result
        if endpoint=='pair': return ix.pair(db,scope,value('source'),value('target'))
        if endpoint=='partners': return ix.partners(db,scope,value('id'),value('direction','incoming'),int(value('offset',0)),int(value('limit',50)))
        if endpoint=='groups': return ix.groups(db,scope)
        if endpoint=='group-pairs': return ix.group_pairs(db,scope,value('source_group'),value('target_group'),int(value('offset',0)),int(value('limit',50)))
        if endpoint=='tile':
            args=dict(ordering=value('order','model' if scope=='G3' else 'id'),bins=int(value('bins',128)))
            for key in ['x0','x1','y0','y1']:
                if value(key) is not None: args[key]=int(value(key))
            key=digest(dict(identity=ix.get_meta(db,'identity'),scope=scope,args=args,renderer='1'))
            cache=ROOT/'cache/tiles'/(key+'.json')
            if cache.exists(): return read(cache)
            r=ix.tile(db,scope,**args)
            existing=sum(p.stat().st_size for p in (ROOT/'cache/tiles').glob('*.json'))
            if existing<64*2**20: atomic(cache,r)
            return r
        if endpoint=='graph':
            if scope not in ('G3','G1-subset'): raise ValueError('Whole graphs use exact aggregates; individual graph capped to verified subset')
            nodes=[ix.node(db,scope,str(r['id'])) for r in db.execute('SELECT id FROM nodes WHERE model_index IS NOT NULL ORDER BY model_index')]
            edges=list(ix.edge_records(db.execute(f'SELECT * FROM edges WHERE {ix.SCOPES[scope]} ORDER BY target,source'),scope))
            return dict(nodes=nodes,edges=edges,scope=scope,layout='deterministic circle by saved index or annotation group; topology, not anatomy',total_edges=len(edges))
        raise ValueError('Unknown endpoint')
    finally: db.close()

def boundary_partners(ident,direction,offset=0,limit=50):
    ident=body_id(ident)
    if direction not in ('incoming','outgoing') or offset<0 or not 1<=limit<=200: raise ValueError('Invalid boundary query')
    if not SMALL.exists(): fail('E_INCOMPLETE_INGEST','Complete selected-incidence scan required','boundary','./visualization/viz ingest-subset --rss-mib 512 --max-seconds 120')
    db=ix.connect(SMALL,True)
    try:
        if ix.node(db,'G3',ident)['status']!='found': fail('E_INCOMPLETE_INGEST','Only saved subset neurons have complete G1 partner access in this bounded index. Full G1 is pending.','boundary','./visualization/viz ingest-full --rss-mib 512 --max-seconds 300')
        field,other=('target','source') if direction=='incoming' else ('source','target')
        where=f'curated=1 AND {field}=?'
        total=dict(db.execute(f'SELECT COUNT(*) partners,COALESCE(SUM(contacts),0) contacts FROM edges WHERE {where}',(ident,)).fetchone())
        rows=list(ix.edge_records(db.execute(f'SELECT * FROM edges WHERE {where} ORDER BY {other} LIMIT ? OFFSET ?',(ident,limit,offset)),'G1 selected-neuron incidence'))
        return dict(scope='G1: complete partners for this selected neuron only',total=total,rows=rows,offset=offset,limit=limit,showing=len(rows),direction=direction,body_id=ident)
    finally: db.close()

class Handler(BaseHTTPRequestHandler):
    server_version='ConnectomeInspector/0.1'
    def log_message(self,fmt,*args): pass
    def send(self,status,data,content_type='application/json; charset=utf-8',attachment=None):
        if not isinstance(data,bytes): data=json.dumps(data,allow_nan=False).encode()
        self.send_response(status); self.send_header('Content-Type',content_type); self.send_header('Content-Length',str(len(data))); self.send_header('X-Content-Type-Options','nosniff'); self.send_header('Cache-Control','no-store')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; object-src 'self'; connect-src 'self'; frame-ancestors 'none'")
        if attachment:self.send_header('Content-Disposition','attachment; filename="'+attachment+'"')
        self.end_headers(); self.wfile.write(data)
    def do_GET(self):
        u=urlsplit(self.path); q=parse_qs(u.query,keep_blank_values=True)
        if len(self.path)>4000: return self.send(400,{'error':'query too long'})
        try:
            if u.path.startswith('/api/'):
                return self.send(200,query(u.path[5:],q))
            if u.path=='/export/edges.csv': return self.export_edges(q)
            if u.path=='/export/boundary.csv': return self.export_edges(q,boundary=True)
            if u.path in ('/','/index.html'): p=WEB/'index.html'
            elif u.path in ('/app.js','/style.css'): p=WEB/u.path[1:]
            elif u.path.startswith('/report/'):
                rel=Path(u.path[len('/report/'):]); p=(REPORT/rel).resolve()
                if not p.is_relative_to(REPORT) or p.suffix not in ('.json','.csv','.svg','.png','.html','.npz'): return self.send(404,{'error':'not found'})
            else: return self.send(404,{'error':'not found'})
            if not p.is_file(): return self.send(404,{'error':'not found'})
            return self.send(200,p.read_bytes(),mimetypes.guess_type(p.name)[0] or 'application/octet-stream')
        except EvidenceError as e: self.send(409,{'error':e.detail})
        except (ValueError,TypeError,KeyError) as e: self.send(400,{'error':{'code':'E_INVALID_QUERY','message':str(e)}})
        except Exception as e: self.send(503,{'error':{'code':'E_QUERY_FAILED','message':type(e).__name__+': '+str(e),'recovery':'Inspect reports/current and rerun build-views; a failed query is not zero connections.'}})
    def export_edges(self,q,boundary=False):
        v=lambda k,d=None:q.get(k,[d])[0]; scope=v('scope','G3')
        if boundary:
            boundary_partners(v('id'),v('direction','incoming'),0,1)
            db=ix.connect(SMALL,True);scope='G1 selected-neuron incidence';where='curated=1'
        else:
            db=database(scope);ix.require_scope(db,scope);where=ix.SCOPES[scope]
        if not v('id') and scope in ('G0','G1','G2'):
            db.close();fail('E_RESOURCE_BUDGET','Whole-release CSV export is an offline operation; exact per-neuron exports remain available',scope,f'./visualization/viz export-edges --scope {scope} --output visualization/reports/current/tables/{scope}-edges.csv')
        sql=f'SELECT * FROM edges WHERE {where}';params=[]
        if v('id'):
            ident=body_id(v('id'));direction=v('direction','outgoing')
            if direction not in ('incoming','outgoing'):raise ValueError('Direction')
            sql+=' AND '+('target' if direction=='incoming' else 'source')+'=?';params.append(ident)
        sql+=' ORDER BY source,target'
        # Finish a bounded export before success headers: truncated files cannot masquerade as complete.
        stream=io.StringIO();fields=['source_body_id','target_body_id','synapse_count','release','graph_scope','source_record_reference'];writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
        try:
            for row in ix.edge_records(db.execute(sql,params),scope):
                writer.writerow(row)
                if stream.tell()>32*2**20:fail('E_RESOURCE_BUDGET','Filtered export exceeds browser download budget; use export-edges CLI','export')
            self.send(200,stream.getvalue().encode(),'text/csv; charset=utf-8','complete-partners.csv')
        finally:db.close()

def serve(host='127.0.0.1',port=8765):
    if host not in ('127.0.0.1','localhost'): raise ValueError('Loopback only')
    try: server=HTTPServer(('127.0.0.1',port),Handler)
    except PermissionError: fail('E_LOCAL_SERVER_UNAVAILABLE','This execution sandbox forbids listening sockets. Launch the same loopback-only command from your terminal.','application',f'./visualization/viz serve --host 127.0.0.1 --port {port}')
    print(f'Local viewer: http://127.0.0.1:{port} — Ctrl-C to stop',flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
