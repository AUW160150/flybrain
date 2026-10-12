from __future__ import annotations
import os, sqlite3, time
from pathlib import Path
import numpy as np
import pyarrow as pa
import pyarrow.feather as feather
from .provenance import *
from .discover_run import GRAPH, verify_graph
from .indexing import *

pa.set_cpu_count(1); pa.set_io_thread_count(1)
RAW_MANIFEST=EXPERIMENT/'data/raw/malecns-manifest.json'
SMALL=ROOT/'cache/subset.sqlite'
FULL=ROOT/'cache/full.sqlite'

def products(verify=True):
    m=read(RAW_MANIFEST)
    if m['release']!=RELEASE: fail('E_DATA_RELEASE_MISMATCH','Wrong release','G0/G1')
    items={('annotations' if f['name'].startswith('body-annotations') else 'weights'):f for f in m['files']}
    for f in items.values():
        p=Path(f['path']).resolve()
        if not p.is_relative_to(WORKSPACE): fail('E_RUN_IDENTITY_MISSING','Unconfigured data directory')
        if verify: checked(p,f['sha256'])
    return items

def inspect_schema():
    result={}
    for name,f in products(False).items():
        with pa.memory_map(f['path'],'r') as stream:
            reader=pa.ipc.open_file(stream)
            result[name]=dict(fields={s.name:str(s.type) for s in reader.schema},record_batches=reader.num_record_batches,rows=sum(reader.get_batch(i).num_rows for i in range(reader.num_record_batches)) if name=='annotations' else f['schema']['rows'],row_count_source='read annotations; saved previously audited weights manifest',source_url=f['source_url'],sha256=f['sha256'])
    atomic(REPORT/'schema.json',result); return result

def annotations():
    f=products(False)['annotations']; checked(Path(f['path']),f['sha256'])
    cols=['bodyId','status','statusLabel','class','superclass','type','somaSide']
    with pa.memory_map(f['path'],'r') as stream:
        names=pa.ipc.open_file(stream).schema.names
    side='somaSide' if 'somaSide' in names else 'side' if 'side' in names else None
    cols=[x for x in cols if x!='somaSide']+([side] if side else [])
    table=feather.read_table(f['path'],columns=cols,memory_map=True,use_threads=False)
    if table['bodyId'].type!=pa.int64() or table['bodyId'].null_count: fail('E_ID_PRECISION_LOSS','Unexpected annotation IDs')
    data=table.to_pydict(); ids=np.asarray(data['bodyId'],dtype=np.int64)
    if len(np.unique(ids))!=len(ids): fail('E_SCHEMA_OR_ROW_SEMANTICS_UNKNOWN','Duplicate annotation IDs')
    bad={'glia','error','non-neuronal','non_neuronal','artifact'}
    curated=np.array([s=='Traced' for s in data['status']])
    for col in ['statusLabel','superclass','class','type']: curated &= np.array([str(v).lower() not in bad for v in data[col]])
    return data,ids,curated,side

def add_annotations(db,g):
    data,ids,curated,side=annotations(); model={int(v):i for i,v in enumerate(g['ids'])}
    db.executemany('INSERT OR IGNORE INTO nodes(id,model_index,curated,cls,typ,side,ref) VALUES (?,?,?,?,?,?,?)',
        ((int(v),model.get(int(v)),int(curated[i]),data['superclass'][i],data['type'][i],data[side][i] if side else None,f'annotations:row:{i}') for i,v in enumerate(ids)))
    return np.sort(ids[curated])

def membership(ids,values):
    pos=np.searchsorted(ids,values); return (pos<len(ids))&(ids[np.minimum(pos,len(ids)-1)]==values)

def batches(f):
    # Buffered IPC reads avoid accumulating resident mmap pages across the 1 GB file.
    with pa.OSFile(f['path'],'rb') as stream:
        reader=pa.ipc.open_file(stream)
        if reader.schema.names!=['body_pre','body_post','weight'] or any(s.type!=pa.int64() for s in reader.schema):
            fail('E_SCHEMA_OR_ROW_SEMANTICS_UNKNOWN','Expected unique ordered-pair body_pre/body_post/weight int64 schema; no ROI aggregation is inferred')
        yield reader

def ingest(full=False,rss_mib=512,storage_gib=64,max_seconds=300):
    """Atomic per-batch transactions. Duplicate ordered pairs fail, never sum unknown units.

    Full import reads every released pair. Small import scans all rows but retains
    only curated pairs incident to the exact saved IDs for the boundary ledger.
    """
    budget=Budget(rss_mib,max_seconds,storage_gib); g=verify_graph(); files=products(True)
    identity=digest({'release':RELEASE,'sources':{k:v['sha256'] for k,v in files.items()},'graph':g['graph_hash'],'schema':2,'mode':'full' if full else 'selected-incidence'})
    path=FULL if full else SMALL; work=path.with_suffix('.partial.sqlite')
    if path.exists():
        db=connect(path,True)
        if get_meta(db,'identity')!=identity: fail('E_DATA_RELEASE_MISMATCH','Existing index has another identity; preserve it and use a new cache directory')
        return dict(status='already_complete',scopes=get_meta(db,'complete_scopes'))
    db=connect(work)
    if hasattr(budget,'deadline'):
        db.set_progress_handler(lambda: int(time.monotonic()>budget.deadline or rss()>budget.bytes), 100000)
    previous=get_meta(db,'identity')
    if previous and previous!=identity: fail('E_DATA_RELEASE_MISMATCH','Partial ingestion has different inputs; cannot resume')
    put_meta(db,'identity',identity); put_meta(db,'release',RELEASE); put_meta(db,'source_manifest_sha256',sha(RAW_MANIFEST))
    put_meta(db,'source_products',{k:{x:v[x] for x in ['source_url','sha256','size_bytes']} for k,v in files.items()})
    curated=add_annotations(db,g); db.commit()
    selected=np.sort(g['ids']); expected={(int(g['ids'][s]),int(g['ids'][t])):int(c) for s,t,c in zip(g['source'],g['target'],g['counts'])}
    progress=get_meta(db,'progress',{'batch':0,'raw_rows':0,'raw_contacts':0,'retained_rows':0})
    started=time.monotonic()
    try:
        for reader in batches(files['weights']):
            for k in range(progress['batch'],reader.num_record_batches):
                budget.check([work,work.with_name(work.name+'-journal'),ROOT/'cache/sqlite-temp']); b=reader.get_batch(k)
                if any(c.null_count for c in b.columns): fail('E_SCHEMA_OR_ROW_SEMANTICS_UNKNOWN','Null edge row; batch quarantined')
                s,t,c=[x.to_numpy() for x in b.columns]
                if np.any(s<0)|np.any(t<0)|np.any(c<0): fail('E_SCHEMA_OR_ROW_SEMANTICS_UNKNOWN','Negative ID/contact count; batch quarantined')
                cur=membership(curated,s)&membership(curated,t)
                inside=membership(selected,s)&membership(selected,t)
                eligible=cur&(c>=5)&(s!=t)
                use=np.ones(len(s),dtype=bool) if full else (cur&(membership(selected,s)|membership(selected,t)))
                rows=[]
                for i in np.flatnonzero(use):
                    a,z,v=int(s[i]),int(t[i]),int(c[i]); is_g3=(a,z) in expected
                    if is_g3 and expected[a,z]!=v: fail('E_GRAPH_MASK_MISMATCH','Raw count differs from saved count','G3',evidence={'source':str(a),'target':str(z),'raw_count':v,'saved_count':expected[a,z]})
                    if bool(inside[i]&eligible[i]) != is_g3: fail('E_GRAPH_MASK_MISMATCH','Raw parent induced graph differs from saved edge set','G3')
                    rows.append((a,z,v,progress['raw_rows']+int(i),int(cur[i]),int(eligible[i]),int(is_g3),int(inside[i]&cur[i])))
                try: db.executemany('INSERT INTO edges VALUES (?,?,?,?,?,?,?,?)',rows)
                except sqlite3.IntegrityError as e: fail('E_SCHEMA_OR_ROW_SEMANTICS_UNKNOWN',f'Duplicate ordered pairs or malformed rows in batch {k}; no ambiguous summation performed',evidence=str(e))
                progress=dict(batch=k+1,raw_rows=progress['raw_rows']+len(s),raw_contacts=progress['raw_contacts']+int(c.sum()),retained_rows=progress['retained_rows']+len(rows))
                put_meta(db,'progress',progress); db.commit()
                if k%300==0: print(json.dumps({'batch':k,'of':reader.num_record_batches,'retained':progress['retained_rows'],'peak_rss':rss()}),flush=True)
        if progress['raw_rows']!=files['weights']['schema']['rows']: fail('E_INCOMPLETE_INGEST','Raw row count does not match manifest')
        if db.execute('SELECT COUNT(*) FROM edges WHERE g3=1').fetchone()[0]!=len(expected): fail('E_GRAPH_MASK_MISMATCH','Saved edges missing from published product','G3')
        put_meta(db,'ingest_rows_complete',True); put_meta(db,'measured',{'seconds_this_invocation':time.monotonic()-started,'peak_rss_bytes':rss()}); db.commit()
        if full:
            # G0 endpoint universe includes unannotated segments; G1 isolates remain.
            db.execute('INSERT OR IGNORE INTO nodes(id,g0,ref) SELECT source,1,\'connection endpoint\' FROM edges GROUP BY source')
            db.execute('INSERT OR IGNORE INTO nodes(id,g0,ref) SELECT target,1,\'connection endpoint\' FROM edges GROUP BY target')
            db.execute('UPDATE nodes SET g0=1 WHERE id IN (SELECT source FROM edges UNION SELECT target FROM edges)'); db.commit()
            # Exact uniqueness guaranteed by primary key across ALL source batches.
            budget.check([work]); scopes=['G0','G1','G2','G3','G1-subset']
        else: scopes=['G3','G1-subset']
        finish(db,scopes,budget,work)
        if full:
            if summary(db,'G0')['pairs']!=progress['raw_rows'] or summary(db,'G0')['contacts']!=progress['raw_contacts']: fail('E_COUNT_CONSERVATION_FAILED','Full row/contact totals do not conserve')
        db.close(); os.replace(work,path)
        return dict(status='complete',scopes=scopes,raw_rows_scanned=progress['raw_rows'],retained_rows=progress['retained_rows'],peak_rss_bytes=rss())
    except Exception as e:
        db.set_progress_handler(None,0); db.rollback(); progress=get_meta(db,'progress',progress); db.close()
        detail=e.detail if isinstance(e,EvidenceError) else {'code':'E_RESOURCE_BUDGET' if 'interrupted' in str(e) else 'E_INCOMPLETE_INGEST','message':str(e),'panel':'ingestion','recovery':'Repeat the same bounded ingest command; committed batches are retained.'}
        atomic(REPORT/('full-ingest-error.json' if full else 'subset-ingest-error.json'),dict(detail,coverage='incomplete',last_committed_progress=progress))
        raise

def topology_only(g):
    """Independent G3 panel available even if large inputs are inaccessible."""
    path=ROOT/'cache/topology.sqlite'
    if path.exists():
        db=connect(path,True)
        if get_meta(db,'identity')==g['graph_hash']: return path
        fail('E_GRAPH_MASK_MISMATCH','Cached topology identity changed')
    tmp=path.with_suffix('.partial.sqlite'); db=connect(tmp)
    md=g['manifest']['metadata']; ids=g['ids']
    db.executemany('INSERT INTO nodes(id,model_index,curated,cls,typ,ref) VALUES (?,?,1,?,?,?)',((int(v),i,md['node_classes']['superclass'][i],md['node_classes']['type'][i],f'saved model index {i}') for i,v in enumerate(ids)))
    db.executemany('INSERT INTO edges VALUES (?,?,?,?,1,1,1,1)',((int(ids[s]),int(ids[t]),int(c),k) for k,(s,t,c) in enumerate(zip(g['source'],g['target'],g['counts']))))
    put_meta(db,'identity',g['graph_hash']); put_meta(db,'source_reference_kind','saved parameter array position'); finish(db,['G3']); db.close(); os.replace(tmp,path); return path

def removal_ledger(db):
    if not get_meta(db,'ingest_rows_complete'): fail('E_INCOMPLETE_INGEST','Boundary ledger requires complete source scan','boundary')
    result=[]
    for row in db.execute('SELECT id,model_index FROM nodes WHERE model_index IS NOT NULL ORDER BY model_index').fetchall():
        ident=str(row['id']); out={'body_id':ident,'model_index':row['model_index']}
        for direction,field,other in [('incoming','target','source'),('outgoing','source','target')]:
            categories={}; total_pairs=total_contacts=0
            for r in db.execute(f'''SELECT CASE WHEN internal=0 THEN 'outside_subset' WHEN contacts<5 THEN 'internal_below_threshold' WHEN source=target THEN 'internal_self_edge' ELSE 'retained_G3' END category, COUNT(*) pairs,SUM(contacts) contacts FROM edges WHERE curated=1 AND {field}=? GROUP BY category''',(ident,)):
                categories[r['category']]=dict(pairs=r['pairs'],contacts=r['contacts']); total_pairs+=r['pairs']; total_contacts+=r['contacts']
            g2=db.execute(f'SELECT COUNT(*),COALESCE(SUM(contacts),0) FROM edges WHERE eligible=1 AND {field}=?',(ident,)).fetchone()
            retained=categories.get('retained_G3',{'pairs':0,'contacts':0})
            independent=db.execute(f'SELECT COUNT(*),COALESCE(SUM(contacts),0) FROM edges WHERE curated=1 AND {field}=?',(ident,)).fetchone()
            if (total_pairs,total_contacts)!=tuple(independent): fail('E_COUNT_CONSERVATION_FAILED','Boundary categories do not conserve')
            out[direction]=dict(categories=categories,G1=dict(pairs=total_pairs,contacts=total_contacts),G2=dict(pairs=g2[0],contacts=g2[1]),retained_contact_fraction_G1=retained['contacts']/total_contacts if total_contacts else None,retained_contact_fraction_G2=retained['contacts']/g2[1] if g2[1] else None)
        result.append(out)
    return dict(rows=result,predicate_order=['outside subset','internal contacts < 5','internal self edge','retained G3'],note='Incoming and outgoing are incidence totals; never sum them as unique network edges. G0-to-G1 exclusions are separate.',geometry_coverage='independent of graph statistics')
