from __future__ import annotations
import math, os, subprocess
from pathlib import Path
import numpy as np
from .provenance import *
from .discover_run import verify_graph

BASE='https://storage.googleapis.com/flyem-male-cns/v1.0/segmentation/skeletons-malecns/skeletons-swc/'
CATALOGUE='https://male-cns.janelia.org/download/'

def parse_swc(path: Path, source_units: str, converted: bool=False) -> dict:
    if converted or source_units not in ('8nm','nm','um'): fail('E_COORDINATE_UNITS_UNKNOWN','Unknown units or already converted data; refusing second conversion','anatomy')
    factor={'8nm':.008,'nm':.001,'um':1.}[source_units]
    rows=[]
    for line in path.read_text().splitlines():
        if not line.strip() or line.lstrip().startswith('#'): continue
        a=line.split()
        if len(a)!=7: fail('E_GEOMETRY_UNAVAILABLE','SWC row must have 7 fields','anatomy')
        rows.append((int(a[0]),int(a[1]),float(a[2]),float(a[3]),float(a[4]),float(a[5]),int(a[6])))
    if not rows or len(rows)>1000000: fail('E_RESOURCE_BUDGET','Empty/oversized skeleton','anatomy')
    ids={r[0]:i for i,r in enumerate(rows)}
    if len(ids)!=len(rows): fail('E_GEOMETRY_UNAVAILABLE','Duplicate skeleton point IDs','anatomy')
    xyz=np.array([r[2:5] for r in rows])*factor
    if not np.isfinite(xyz).all() or any(r[5]<0 for r in rows): fail('E_GEOMETRY_UNAVAILABLE','Invalid SWC geometry','anatomy')
    edges=[]
    for i,r in enumerate(rows):
        if r[6]==-1: continue
        if r[6] not in ids: fail('E_GEOMETRY_UNAVAILABLE','Missing SWC parent point','anatomy')
        edges.append([ids[r[6]],i])
    # Native 8nm volume bounds from official catalogue shape (axes x,y,z).
    if source_units=='8nm' and (np.any(xyz<0) or np.any(xyz>np.array([94088,78317,134576])*.008+1)):
        fail('E_COORDINATE_UNITS_UNKNOWN','Native coordinates outside catalogue reference volume','anatomy')
    return dict(points=xyz.tolist(),branches=edges,source_units=source_units,target_units='um',factor_applied_once=factor,axes='native MaleCNS x,y,z; no mirroring or template transform',bounds_um=[xyz.min(0).tolist(),xyz.max(0).tolist()],centroid_um=xyz.mean(0).tolist(),representative='skeleton-point centroid, not soma',kind='real reconstructed skeleton branches; not inter-neuron synapses')

def store_geometry(ident: str, record: dict) -> dict:
    path=REPORT/'geometry'/(ident+'.json')
    atomic(path,record)
    return {k:v for k,v in record.items() if k not in ('points','branches')} | dict(point_count=len(record['points']),branch_count=len(record['branches']),geometry_sha256=sha(path))

def fetch(ids_from: Path | None=None,max_ids=8,download_mib=32,max_seconds=60,offline=False):
    g=verify_graph(); exact=[str(v) for v in g['ids']]
    if ids_from:
        obj=read(ids_from); ids=obj if isinstance(obj,list) else obj.get('ids',[])
        ids=[body_id(v) for v in ids]
        if any(v not in exact for v in ids): fail('E_RUN_IDENTITY_MISSING','Morphology IDs must come from verified exact subset','anatomy')
    else: ids=exact
    if not 1<=max_ids<=512 or not 1<=download_mib<=256: raise ValueError('Morphology budget')
    folder=ROOT/'cache/morphology'; folder.mkdir(parents=True,exist_ok=True)
    budget=Budget(512,max_seconds,1); records={}
    existing=REPORT/'geometry.json'
    if existing.exists(): records=read(existing).get('records',{})
    total=0
    # Sequential (one worker), deterministic IDs; every failed/missing ID retained.
    for ident in ids[:max_ids]:
        budget.check(); path=folder/(ident+'.swc'); url=BASE+ident+'.swc'
        if ident in records and records[ident].get('status')=='loaded' and path.exists() and sha(path)==records[ident]['sha256'] and records[ident].get('geometry_sha256') and (REPORT/'geometry'/(ident+'.json')).exists(): continue
        receipt_path=path.with_suffix('.source.json')
        if path.exists() and receipt_path.exists():
            receipt=read(receipt_path)
            if receipt.get('source_url')==url and receipt.get('sha256')==sha(path):
                data=parse_swc(path,'8nm')
                records[ident]=store_geometry(ident,dict(status='loaded',body_id=ident,source_url=url,sha256=sha(path),retrieved_utc=receipt['retrieved_utc'],coordinate_evidence=CATALOGUE,**data))
                continue
        if offline: continue
        remaining=download_mib*2**20-total
        if remaining<=0: break
        tmp=path.with_suffix('.partial')
        p=subprocess.run(['curl','--fail','--location','--silent','--show-error','--max-time','10','--max-filesize',str(min(8*2**20,remaining)),url,'--output',str(tmp)],capture_output=True,text=True)
        if p.returncode:
            tmp.unlink(missing_ok=True); records[ident]=dict(status='failed',source_url=url,error=p.stderr.strip()[:300]); continue
        total+=tmp.stat().st_size
        try:
            data=parse_swc(tmp,'8nm'); os.replace(tmp,path)
            atomic(receipt_path,dict(source_url=url,sha256=sha(path),retrieved_utc=now()))
            records[ident]=store_geometry(ident,dict(status='loaded',body_id=ident,source_url=url,sha256=sha(path),retrieved_utc=now(),coordinate_evidence=CATALOGUE,**data))
        except EvidenceError as e:
            tmp.unlink(missing_ok=True); records[ident]=dict(status='failed',source_url=url,error=e.detail)
    loaded=sum(r['status']=='loaded' for r in records.values())
    result=dict(release=RELEASE,eligible_ids=exact,loaded=loaded,total=len(exact),failed=sum(r['status']=='failed' for r in records.values()),not_requested=[v for v in exact if v not in records],records=records,download_bytes_this_invocation=total,official_scene_entry=CATALOGUE,coverage=f'{loaded}/{len(exact)} exact-subset skeletons loaded; whole-CNS geometry not loaded',context='Native space verified against catalogue voxel scale and volume bounds; no ROI mesh context acquired')
    atomic(existing,result); return dict(loaded=loaded,failed=result['failed'],total=len(exact),bytes=total)
