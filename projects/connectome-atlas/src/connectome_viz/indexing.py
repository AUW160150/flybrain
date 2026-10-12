from __future__ import annotations
import sqlite3
from pathlib import Path
from .provenance import *

SCOPES={'G0':'1','G1':'curated=1','G2':'eligible=1','G3':'g3=1','G1-subset':'internal=1'}
NODE_WHERE={'G0':'g0=1','G1':'curated=1','G2':'curated=1','G3':'model_index IS NOT NULL','G1-subset':'model_index IS NOT NULL'}
SCHEMA='''
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS nodes(id INTEGER PRIMARY KEY, model_index INTEGER, curated INTEGER NOT NULL DEFAULT 0, cls TEXT, typ TEXT, side TEXT, g0 INTEGER NOT NULL DEFAULT 0, ref TEXT);
CREATE TABLE IF NOT EXISTS edges(source INTEGER NOT NULL, target INTEGER NOT NULL, contacts INTEGER NOT NULL CHECK(contacts>=0), ref INTEGER NOT NULL, curated INTEGER NOT NULL, eligible INTEGER NOT NULL, g3 INTEGER NOT NULL DEFAULT 0, internal INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(source,target));
CREATE TABLE IF NOT EXISTS ranks(scope TEXT, ordering TEXT, id INTEGER, rank INTEGER, PRIMARY KEY(scope,ordering,id));
CREATE UNIQUE INDEX IF NOT EXISTS rank_lookup ON ranks(scope,ordering,rank);
'''

def connect(path: Path, readonly: bool = False) -> sqlite3.Connection:
    if readonly:
        db=sqlite3.connect(f'file:{path.resolve()}?mode=ro',uri=True)
    else:
        if not path.resolve().is_relative_to(ROOT): fail('E_PROTECTED_INPUT_CHANGED','Database output outside visualization')
        path.parent.mkdir(parents=True,exist_ok=True); db=sqlite3.connect(path)
        db.execute('PRAGMA journal_mode=DELETE'); db.execute('PRAGMA synchronous=FULL')
    db.row_factory=sqlite3.Row; db.execute('PRAGMA cache_size=-16384'); db.execute('PRAGMA temp_store=FILE'); db.execute('PRAGMA threads=1')
    if not readonly: db.executescript(SCHEMA)
    return db

def put_meta(db,key,value):
    db.execute('INSERT OR REPLACE INTO meta VALUES (?,?)',(key,json.dumps(value,sort_keys=True)))

def get_meta(db,key,default=None):
    r=db.execute('SELECT value FROM meta WHERE key=?',(key,)).fetchone()
    return json.loads(r[0]) if r else default

def require_scope(db,scope: str):
    if scope not in SCOPES: raise ValueError('Unknown graph scope')
    if scope not in get_meta(db,'complete_scopes',[]): fail('E_INCOMPLETE_INGEST',f'{scope} is not fully indexed; missing entries cannot be interpreted as zero',scope,'./visualization/viz ingest-full --rss-mib 512 --storage-gib 64 --max-seconds 300')

def finish(db,scopes: list[str],budget=None,path=None):
    db.execute('CREATE INDEX IF NOT EXISTS edges_target ON edges(target,source)')
    for scope in scopes:
        for ordering in ['id','group','model']:
            if ordering=='model' and scope not in ('G3','G1-subset'): continue
            order={'id':'id','group':"COALESCE(cls,'Unknown'), COALESCE(typ,'Unknown'),id",'model':'model_index'}[ordering]
            db.execute('DELETE FROM ranks WHERE scope=? AND ordering=?',(scope,ordering))
            db.execute(f'INSERT INTO ranks SELECT ?,?,id,ROW_NUMBER() OVER (ORDER BY {order})-1 FROM nodes WHERE {NODE_WHERE[scope]}',(scope,ordering))
        if budget: budget.check([path])
    put_meta(db,'complete_scopes',scopes); put_meta(db,'indexed_utc',now()); db.commit()

def summary(db,scope):
    require_scope(db,scope)
    row=dict(db.execute(f'SELECT COUNT(*) pairs, COALESCE(SUM(contacts),0) contacts, COALESCE(SUM(source=target),0) loops FROM edges WHERE {SCOPES[scope]}').fetchone())
    row.update(dict(db.execute(f'SELECT COUNT(*) nodes, COALESCE(SUM(cls IS NULL OR typ IS NULL),0) unknown_annotations FROM nodes WHERE {NODE_WHERE[scope]}').fetchone()))
    row.update(scope=scope,release=RELEASE,coverage='complete for named scope',filters={'G0':'all released segment pairs; minconf 0.5 product','G1':'Traced inventory, explicit non-neuronal/error exclusions; no count threshold','G2':'G1; contacts >= 5, then no self-edges','G3':'exact saved graph, contacts >= 5, no self-edges','G1-subset':'G1 induced on exact saved IDs before threshold'}[scope])
    return row

def node(db,scope,ident):
    require_scope(db,scope); ident=body_id(ident)
    r=db.execute(f'SELECT * FROM nodes WHERE id=? AND {NODE_WHERE[scope]}',(ident,)).fetchone()
    if not r: return {'status':'no_matching_node','body_id':ident,'scope':scope}
    d=dict(r); d['body_id']=str(d.pop('id')); d.update(status='found',scope=scope,release=RELEASE,dataset='MaleCNS',is_curated_neuron=bool(d['curated']),in_experiment=d['model_index'] is not None,coordinate_provenance=None,source_record_reference=d.pop('ref'),annotation_class=d.pop('cls'),annotation_type=d.pop('typ'))
    return d

def search(db,scope,query,limit=30):
    require_scope(db,scope)
    if len(query)>120: raise ValueError('Query too long')
    rs=db.execute(f'SELECT id,model_index,cls,typ FROM nodes WHERE {NODE_WHERE[scope]} AND (CAST(id AS TEXT)=? OR instr(lower(COALESCE(typ,\'\')),lower(?))>0) ORDER BY id LIMIT ?',(query,query,min(limit,100)))
    return [dict(body_id=str(r['id']),model_index=r['model_index'],annotation_class=r['cls'],annotation_type=r['typ']) for r in rs]

def edge_records(cursor,scope):
    for r in cursor:
        yield dict(source_body_id=str(r['source']),target_body_id=str(r['target']),synapse_count=r['contacts'],release=RELEASE,graph_scope=scope,source_record_reference=str(r['ref']))

def partners(db,scope,ident,direction,offset=0,limit=50):
    require_scope(db,scope); ident=body_id(ident)
    if direction not in ('incoming','outgoing') or offset<0 or not 1<=limit<=200: raise ValueError('Invalid partner query')
    field,other=('target','source') if direction=='incoming' else ('source','target')
    where=f'{SCOPES[scope]} AND {field}=?'
    total=dict(db.execute(f'SELECT COUNT(*) partners,COALESCE(SUM(contacts),0) contacts FROM edges WHERE {where}',(ident,)).fetchone())
    rows=list(edge_records(db.execute(f'SELECT * FROM edges WHERE {where} ORDER BY {other} LIMIT ? OFFSET ?',(ident,limit,offset)),scope))
    return dict(status='ok',node=node(db,scope,ident),direction=direction,total=total,rows=rows,offset=offset,limit=limit,showing=len(rows),scope=scope)

def pair(db,scope,source,target):
    require_scope(db,scope); source=body_id(source); target=body_id(target)
    if node(db,scope,source)['status']!='found' or node(db,scope,target)['status']!='found': return dict(status='endpoint_outside_scope',source_body_id=source,target_body_id=target,scope=scope)
    r=list(edge_records(db.execute(f'SELECT * FROM edges WHERE {SCOPES[scope]} AND source=? AND target=?',(source,target)),scope))
    return dict(status='represented' if r else 'verified_absence_in_release_scope',record=r[0] if r else None,source_body_id=source,target_body_id=target,scope=scope,matrix_convention='row target, column source')

def tile(db,scope,ordering='id',bins=128,x0=0,x1=None,y0=0,y1=None):
    require_scope(db,scope)
    if ordering not in ('id','group','model') or not 1<=bins<=256: raise ValueError('Invalid order or bins')
    n=db.execute('SELECT COUNT(*) FROM ranks WHERE scope=? AND ordering=?',(scope,ordering)).fetchone()[0]
    if n==0: raise ValueError('Ordering unavailable')
    x1=n if x1 is None else x1; y1=n if y1 is None else y1
    if not (0<=x0<x1<=n and 0<=y0<y1<=n): raise ValueError('Invalid matrix viewport')
    bx=min(bins,x1-x0); by=min(bins,y1-y0)
    sql=f'''SELECT ((s.rank-?)*? / ?) x, ((t.rank-?)*? / ?) y, COUNT(*) pairs,SUM(e.contacts) contacts,MAX(e.contacts) maximum
        FROM edges e JOIN ranks s ON s.id=e.source AND s.scope=? AND s.ordering=? JOIN ranks t ON t.id=e.target AND t.scope=? AND t.ordering=?
        WHERE {SCOPES[scope]} AND s.rank>=? AND s.rank<? AND t.rank>=? AND t.rank<? GROUP BY y,x'''
    rows=[dict(r) for r in db.execute(sql,(x0,bx,x1-x0,y0,by,y1-y0,scope,ordering,scope,ordering,x0,x1,y0,y1))]
    def ranges(start,end,b):
        out=[]
        for k in range(b):
            lo=start+(k*(end-start)+b-1)//b; hi=start+((k+1)*(end-start)+b-1)//b
            a=db.execute('SELECT id,rank FROM ranks WHERE scope=? AND ordering=? AND rank IN (?,?) ORDER BY rank',(scope,ordering,lo,hi-1)).fetchall()
            out.append(dict(start=lo,end=hi,first_id=str(a[0]['id']),last_id=str(a[-1]['id']),single=hi-lo==1))
        return out
    selected=[dict(body_id=str(r['id']),model_index=r['model_index'],rank=r['rank']) for r in db.execute('SELECT n.id,n.model_index,r.rank FROM nodes n JOIN ranks r ON n.id=r.id WHERE r.scope=? AND r.ordering=? AND n.model_index IS NOT NULL ORDER BY r.rank',(scope,ordering))]
    return dict(scope=scope,ordering=ordering,release=RELEASE,rows=rows,n=n,bins_x=bx,bins_y=by,x=ranges(x0,x1,bx),y=ranges(y0,y1,by),bounds=[x0,x1,y0,y1],pairs=sum(r['pairs'] for r in rows),contacts=sum(r['contacts'] for r in rows),subset_positions=selected,display_transform='log1p only; exact integer reductions stored',convention='rows receive; columns send',identity=get_meta(db,'identity'))

def groups(db,scope):
    require_scope(db,scope)
    rows=[dict(r) for r in db.execute(f'''SELECT COALESCE(s.cls,'Unknown') source_group,COALESCE(t.cls,'Unknown') target_group, COUNT(*) pairs, SUM(e.contacts) contacts FROM edges e JOIN nodes s ON s.id=e.source JOIN nodes t ON t.id=e.target WHERE {SCOPES[scope].replace('curated','e.curated')} GROUP BY source_group,target_group''')]
    nodes=[dict(r) for r in db.execute(f"SELECT COALESCE(cls,'Unknown') name,COUNT(*) nodes, SUM(model_index IS NOT NULL) in_experiment FROM nodes WHERE {NODE_WHERE[scope]} GROUP BY name")]
    return dict(scope=scope,grouping='disjoint published superclass (canonical annotation_class), null → Unknown; within-group edges retained',nodes=nodes,edges=rows,pairs=sum(r['pairs'] for r in rows),contacts=sum(r['contacts'] for r in rows))

def group_pairs(db,scope,a,b,offset=0,limit=50):
    require_scope(db,scope)
    if offset<0 or not 1<=limit<=200: raise ValueError('Pagination')
    where=f"{SCOPES[scope].replace('curated','e.curated')} AND COALESCE(s.cls,'Unknown')=? AND COALESCE(t.cls,'Unknown')=?"
    join='FROM edges e JOIN nodes s ON s.id=e.source JOIN nodes t ON t.id=e.target'
    total=db.execute(f'SELECT COUNT(*) {join} WHERE {where}',(a,b)).fetchone()[0]
    rows=list(edge_records(db.execute(f'SELECT e.* {join} WHERE {where} ORDER BY e.source,e.target LIMIT ? OFFSET ?',(a,b,limit,offset)),scope))
    return dict(total=total,rows=rows,offset=offset,scope=scope)
