from __future__ import annotations
import csv, hashlib, importlib.metadata, json, os, shutil, zipfile
from pathlib import Path
import numpy as np
from .provenance import *

GRAPH = EXPERIMENT/'data/processed/fly-n512-sample101.npz'

def inventory() -> dict:
    runs=[]
    for p in sorted((EXPERIMENT/'runs').glob('*/manifest.json')):
        m=read(p); meta=m.get('metadata',{})
        runs.append(dict(run_id=p.parent.name, path=str(p.parent.relative_to(WORKSPACE)), manifest_sha256=sha(p), condition=meta.get('condition'), graph_hash=meta.get('graph_hash'), synthetic=meta.get('synthetic'), status_at_inspection=m.get('status'), config=m.get('config'), code_hash=m.get('code_hash'), checkpoints=[{'name':f.name,'size_bytes':f.stat().st_size} for f in sorted(p.parent.glob('*.pt'))]))
    products=[]
    for f in read(EXPERIMENT/'data/raw/malecns-manifest.json')['files']:
        products.append({k:v for k,v in f.items() if k!='http_headers'})
    result=dict(inspected_utc=now(), runs=runs, products=products, protected=protect_inventory(), selection_policy='Shared topology only when one compatible graph hash; no automatic trained weight selection', code_revision=revision())
    atomic(REPORT/'inventory.json',result); return result

def plan() -> dict:
    source_files=read(EXPERIMENT/'data/raw/malecns-manifest.json')['files']
    rows=next(f['schema']['rows'] for f in source_files if f['name'].startswith('connectome-weights'))
    result=dict(utc=now(), cpu_threads=1, accelerator='disabled', available_ram_bytes=None,
        ram_note='Current RAM/process queries denied by sandbox; vm_stat observed compression and swap. Historical capacity is not available memory.',
        active_workload='Documented Shakespeare confirmation; treat as active. Never stop or alter it.',
        safe_work_rss_budget_mib=512, full_ingest_run=False,
        estimates={'compressed_input_bytes':sum(f['size_bytes'] for f in source_files),'decompressed_edge_columns_bytes':rows*24,'sqlite_and_indexes_peak_gib':64,'morphology_download_cap_mib':256,'tile_cache_cap_mib':64},
        full_ingest_reason=f'{rows:,} rows plus exact bidirectional indexes and sorting are deferred alongside training. Estimates are not measurements.',
        free_disk_bytes=shutil.disk_usage(ROOT).free,
        command='./visualization/viz ingest-full --rss-mib 512 --storage-gib 64 --max-seconds 300',
        resume='Repeat the command to resume committed batches. Then build-indexes and build-views. Verify 512 MiB <= 20% of available RAM before running.',
        environment={'python':os.sys.version.split()[0], 'versions':{x:importlib.metadata.version(x) for x in ['numpy','pyarrow','torch','pillow','pytest']},'isolation':'Separate visualization/.venv; read-only .pth reuse of existing packages. No package installed or changed in training environment.'})
    atomic(REPORT/'resource-plan.json',result); return result

def verify_graph(path: Path = GRAPH) -> dict:
    m=read(path.with_suffix('.json')); md=m['metadata']
    if md.get('synthetic') or md.get('condition')!='FLY-TOPOLOGY': fail('E_RUN_IDENTITY_MISSING','Authentic view refuses synthetic/control graphs','G3')
    if md.get('release')!=RELEASE: fail('E_DATA_RELEASE_MISMATCH','Saved release does not match configured release','G3')
    checked(path,m['file_sha256'])
    for name,h in m['sidecar_sha256'].items(): checked(path.parent/name,h)
    with np.load(path,allow_pickle=False) as z:
        ids,s,t,c=(z[k].copy() for k in ['ids','source','target','counts'])
    for a in [ids,s,t,c]:
        if a.dtype.kind not in 'iu': fail('E_ID_PRECISION_LOSS','Noninteger graph array','G3')
    n=len(ids)
    if len(set(ids.tolist()))!=n or len(set(zip(s.tolist(),t.tolist())))!=len(s) or len(s)!=len(t) or len(s)!=len(c): fail('E_GRAPH_MASK_MISMATCH','Duplicate or inconsistent saved arrays','G3')
    if min(s.min(),t.min(),c.min())<0 or max(s.max(),t.max())>=n: fail('E_GRAPH_MASK_MISMATCH','Invalid edge index/count','G3')
    if not np.array_equal(np.lexsort((s,t)),np.arange(len(s))): fail('E_EDGE_ORDER_UNVERIFIED','Saved edges are not target-major/source-minor','weights')
    h=digest(dict(ids=[body_id(v) for v in ids],source=s.tolist(),target=t.tolist(),counts=c.tolist(),metadata=md))
    if h!=m['graph_hash']: fail('E_GRAPH_MASK_MISMATCH','Graph content hash mismatch','G3')
    rows=list(csv.DictReader(path.with_suffix('.nodes.tsv').open(),delimiter='\t'))
    if [(int(r['model_index']),r['body_id']) for r in rows]!=list(enumerate(map(str,ids))): fail('E_RUN_IDENTITY_MISSING','Saved node map differs','G3')
    rows=list(csv.DictReader(path.with_suffix('.edges.tsv').open(),delimiter='\t'))
    if [(r['source_body_id'],r['target_body_id'],int(r['synapse_count'])) for r in rows]!=[(str(ids[a]),str(ids[b]),int(v)) for a,b,v in zip(s,t,c)]: fail('E_EDGE_ORDER_UNVERIFIED','TSV edge order differs','G3')
    return dict(ids=ids,source=s,target=t,counts=c,manifest=m,graph_hash=h)

def verify_parent(g: dict) -> dict:
    """Scan immutable, thresholded parent arrays in 64K blocks; never extract/sample."""
    p=EXPERIMENT/'data/processed/canonical'; meta=read(p/'canonical-manifest.json')
    checked(p/'canonical-manifest.json',g['manifest']['metadata']['canonical_manifest_sha256'])
    for name,h in meta['files'].items(): checked(p/name,h)
    ids,s,t,c=(np.load(p/name,mmap_mode='r') for name in ['body_ids.npy','source.npy','target.npy','counts.npy'])
    selected=np.searchsorted(ids,g['ids'])
    if not np.array_equal(ids[selected],g['ids']): fail('E_RUN_IDENTITY_MISSING','Subset absent from parent inventory','G3')
    inv=np.full(len(ids),-1,dtype=np.int32); inv[selected]=np.arange(len(selected))
    found=[]; stats=np.zeros((len(selected),4),dtype=np.int64)
    for k in range(0,len(s),65536):
        a,b,v=s[k:k+65536],t[k:k+65536],c[k:k+65536]; x,y=inv[a],inv[b]
        use=(x>=0)&(y>=0); found.extend(zip(x[use].tolist(),y[use].tolist(),v[use].tolist()))
        for model_idx,offset in [(x,0),(y,2)]:
            ok=model_idx>=0
            np.add.at(stats[:,offset],model_idx[ok],1); np.add.at(stats[:,offset+1],model_idx[ok],v[ok])
    expected=sorted(zip(g['source'].tolist(),g['target'].tolist(),g['counts'].tolist()))
    if sorted(found)!=expected: fail('E_GRAPH_MASK_MISMATCH','Saved graph differs from exact parent-induced graph','G3',evidence={'missing':list(set(expected)-set(found))[:20],'extra':list(set(found)-set(expected))[:20]})
    result=dict(status='passed',graph_hash=g['graph_hash'],canonical_manifest_sha256=sha(p/'canonical-manifest.json'),N=len(g['ids']),E=len(g['source']),contacts=int(g['counts'].sum()),loops=int((g['source']==g['target']).sum()),release=RELEASE,filters='Traced; explicit non-neuronal exclusions; counts >= 5; no self-edges; exact saved IDs',edge_order='parameter index k = saved target-major/source-minor array position',parent_induced_exact=True,parent_selected_stats=stats.tolist(),parent_columns=['out_pairs','out_contacts','in_pairs','in_contacts'])
    atomic(REPORT/'identity.json',result); return result

def verify_archive(code_hash: str) -> Path:
    archives=list((EXPERIMENT/'reports').glob('*source-'+code_hash[:12]+'.zip'))
    if len(archives)!=1: fail('E_RUN_IDENTITY_MISSING','Exact executed source archive unavailable','architecture')
    archive=archives[0]
    with zipfile.ZipFile(archive) as z:
        names=[n for n in z.namelist() if (n.startswith('src/') and n.endswith('.py')) or (n.startswith('configs/') and n.endswith('.yaml')) or n=='pyproject.toml']
        h=digest({n:hashlib.sha256(z.read(n)).hexdigest() for n in sorted(names)})
    if h!=code_hash: fail('E_RUN_IDENTITY_MISSING','Source archive does not reproduce recorded code hash','architecture',evidence={'expected':code_hash,'actual':h})
    copied,_=stable_copy(archive,ROOT/'snapshots/source')
    return copied

def select_runs(run_dir: str | None = None) -> list[tuple[Path,dict]]:
    paths=[Path(run_dir).resolve()/'manifest.json'] if run_dir else sorted((EXPERIMENT/'runs').glob('*/manifest.json'))
    compatible=[]
    for p in paths:
        if not p.resolve().is_relative_to(EXPERIMENT/'runs'): fail('E_RUN_IDENTITY_MISSING','Run must be inside configured experiment runs')
        m=read(p); md=m.get('metadata',{})
        if md.get('condition')=='FLY-TOPOLOGY' and m.get('config',{}).get('n')==512 and not md.get('synthetic'): compatible.append((p.parent,m))
    hashes={m['metadata']['graph_hash'] for p,m in compatible}
    if not compatible or len(hashes)!=1: fail('E_RUN_AMBIGUOUS','No unique compatible real topology; select a run','G3','./visualization/viz verify-run --run-dir fly_connectome_lm/runs/confirmation-g101-s33-fly-topology-k0-441b7753ad8e')
    return compatible
