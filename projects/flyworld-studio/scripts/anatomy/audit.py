"""Reproduce Prompt 04A tables from pinned local sources. Does not fetch or publish."""
import csv
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import pyarrow as pa
import pyarrow.feather as feather
from contracts import DATASET, VERSION, UUID, OFFICIAL_BASE, IDENTITY, sha256, validate_mappings, convert_swc, write_immutable
from discover import csv_write

PROJECT = Path(__file__).resolve().parents[2]
WORKSPACE = PROJECT.parents[1]
RESEARCH = WORKSPACE / 'Sugar/malecns_sugar_circuit_v1'
DOCS = PROJECT / 'docs/anatomy'
CACHE = PROJECT / 'data/anatomy'
sys.path.insert(0, str(PROJECT / 'scripts/preprocess'))
from anatomy import parse_swc

STATE_COLUMNS = 'asset_or_feature claimed_status actual_file actual_format body_or_region_id dataset dataset_version source checksum coordinate_frame units verified notes'.split()
COVERAGE_COLUMNS = 'body_id type alias side expected_dataset geometry_path geometry_format mapping_evidence status checksum notes'.split()
FRAME_COLUMNS = 'source_id source_path dataset version units voxel_resolution axis_order axis_directions handedness origin orientation_labels existing_transform evidence status notes'.split()
CLAIM_COLUMNS = 'claim_id timestamp claim source_ids verification_status supersedes_claim_id notes'.split()
MISMATCH_COLUMNS = 'mismatch_id timestamp item old_assumption new_evidence consequence recommended_revision prior_views_valid status source_ids'.split()


def read(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def append_ledger(path, rows, columns):
    # Existing evidence is permanent. A changed claim needs a new ID/correction.
    existing = list(csv.DictReader(Path(path).open())) if Path(path).exists() else []
    by_id = {r[columns[0]]: r for r in existing}
    fresh = []
    for row in rows:
        if row[columns[0]] in by_id:
            old = by_id[row[columns[0]]]
            if any(str(row[k]) != old[k] for k in columns if k != 'timestamp'):
                raise ValueError('Append a superseding claim; never overwrite ' + row[columns[0]])
        else:
            fresh.append(row)
    if fresh:
        with Path(path).open('a', newline='') as out:
            writer = csv.DictWriter(out, fieldnames=columns)
            if not existing:
                writer.writeheader()
            writer.writerows(fresh)


def main():
    timestamp = datetime.now(timezone.utc).isoformat()
    lock = read(PROJECT / 'config/malecns_source_lock.json')
    if (lock['dataset'], lock['version'], lock['uuid']) != (DATASET, VERSION, UUID):
        raise ValueError('Dataset source lock changed')
    for source in lock['files']:
        if sha256(RESEARCH/source['path']) != source['sha256']:
            raise ValueError('Pinned source mismatch: ' + source['path'])
    structural = RESEARCH / lock['structuralRun']
    visual = RESEARCH / lock['visualizationRun']
    sm = read(structural/'manifest.json')
    vm = read(visual/'build_manifest.json')
    if (sm['dataset'], sm['dataset_version'], sm['dataset_uuid']) != (DATASET, VERSION, UUID):
        raise ValueError('Structural release mismatch')
    if (vm['dataset'], vm['dataset_uuid'], vm['source_run']) != (DATASET, UUID, lock['structuralRun']):
        raise ValueError('Visualization release/source mismatch')
    model = read(visual/'model.json')
    requested = {n['body_id']: n for n in model['nodes']}
    flat = RESEARCH/'data/raw/body-annotations-male-cns-v1.0-minconf-0.5.feather'
    flat_source = next(s for s in sm['input_files'] if s['path'] == str(flat.relative_to(RESEARCH)))
    flat_hash = sha256(flat)
    if flat_hash != flat_source['sha256']:
        raise ValueError('Official annotation checksum mismatch')
    cache_paths = sorted((WORKSPACE/'visualization/cache/morphology').glob('*.swc'))
    cache_ids = {p.stem for p in cache_paths}
    columns = ['bodyId','type','instance','synonyms','somaSide','rootSide','somaLocation','tosomaLocation']
    table = feather.read_table(flat, columns=columns)
    inventory = {}
    target_types = {'LB3b','LB3c','MN4a','MN6','MN8','MN9','GNG042','ANXXX462a','GNG015','GNG021',
                    'GNG585','GNG108','GNG120','GNG472','GNG232','DNg67','DNge080'}
    minimum_ids = set()
    for row in table.to_pylist():
        body = str(row['bodyId'])
        if row['type'] in target_types:
            minimum_ids.add(body)
        if body in requested or body in cache_ids or row['type'] in target_types:
            row['bodyId'] = body
            inventory[body] = row
    if minimum_ids - requested.keys():
        raise ValueError('Requested visualization inventory omits required type members')
    with (structural/'nodes.csv').open() as f:
        source_rows = {r['body_id']: r for r in csv.DictReader(f) if r['body_id'] in requested or r['body_id'] in cache_ids}
    for body, node in requested.items():
        if body not in inventory or body not in source_rows or node['type'] != inventory[body]['type'] or node['type'] != source_rows[body]['type']:
            raise ValueError('Authoritative requested-body join failed: '+body)
    save(CACHE/'manifests/authoritative-bodies.json', {
        'dataset':DATASET,'version':VERSION,'uuid':UUID,'source_path':str(flat),'source_sha256':flat_hash,
        'structural_manifest':str(structural/'manifest.json'),'bodies':inventory,
        'requested_body_ids':sorted(requested,key=int),'minimum_requested_type_ids':sorted(minimum_ids,key=int),
    })
    official_doc = RESEARCH/'paper/primary/malecns_download.html'
    html = official_doc.read_text()
    if 'coordinates specified in 8nm units' not in html or 'skeletons-malecns/skeletons-swc/' not in html:
        raise ValueError('Native SWC coordinate documentation absent')
    sources = {}
    def source(sid, path, purpose, **extra):
        path = Path(path)
        sources[sid] = dict(path=str(path),sha256=sha256(path),size_bytes=path.stat().st_size,purpose=purpose,**extra)
        return sid
    source('S-ANNOTATIONS', flat, 'Official full v1.0 annotation table; body identity, not morphology', url=flat_source.get('url', 'https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/'+flat.name))
    source('S-STRUCTURAL', structural/'manifest.json', 'Frozen structural run identity and hashes')
    source('S-NODES', structural/'nodes.csv', 'Verified structural body records')
    source('S-VISUAL', visual/'build_manifest.json', 'Latest immutable visualization manifest')
    source('S-REQUESTED', visual/'model.json', 'Exact 110 requested bodies')
    source('S-DOWNLOAD', official_doc, 'Saved authoritative native/template unit and volume documentation',url='https://male-cns.janelia.org/download/')
    source('S-ORIENTATION', RESEARCH/'visualization/anatomy/orientation.json', 'Explicitly missing anatomical orientation matrix')
    source('S-META', structural/'raw/meta_start.json', 'Saved authenticated dataset identity; no new live refresh')
    source('S-RESEARCH-SOURCES', RESEARCH/'config/source_manifest.yaml', 'Official document and raw-table acquisition provenance')
    source('S-CLAIMS', RESEARCH/'logs/claim_ledger.csv', 'Historical claims including C068/C073')
    source('S-MISMATCHES', RESEARCH/'logs/mismatch_ledger.csv', 'Historical unresolved and corrected discrepancies')
    source('S-QUESTIONS', RESEARCH/'logs/unresolved_questions.md', 'Current gaps, including Q019/Q020')
    source('S-WORKFLOW', RESEARCH/lock['workflowRun']/'manifest.json', 'Latest immutable workflow status')
    source('S-PLACEHOLDER', PROJECT/'src/brain/PlaceholderBrain.tsx', 'Procedural educational volumes, not MaleCNS geometry')
    source('S-RENDERER', PROJECT/'src/realdata/MorphologyView.tsx', 'Validated selected-body loader; float32 display-buffer centering')
    source('S-PACKAGES', PROJECT/'public/data/malecns/manifest.json', 'Current browser package catalog')
    source('S-PARSER', PROJECT/'scripts/preprocess/anatomy.py', 'Existing SWC topology parser reused without modification')
    source('S-CONVERTER', PROJECT/'scripts/anatomy/contracts.py', 'Lossless audit-cache conversion and guards')
    source('S-AUDIT', Path(__file__), 'Reproducible audit tables')
    source('S-DISCOVERY', PROJECT/'scripts/anatomy/discover.py', 'Bounded local discovery implementation')
    source('S-INVENTORY', DOCS/'LOCAL_ASSET_INVENTORY.csv', 'Candidate inventory; absence claims limited to these roots')
    source('S-RETRIEVAL', DOCS/'ANATOMY_RETRIEVAL_LOG.jsonl', 'Actual bounded request outcome and unattempted test bodies')
    required_research = ['AGENTS.md','STATUS.md','docs/RESEARCH_PROTOCOL.md','docs/initial_validation_checkpoint.md',
                        'docs/structural_connectivity_checkpoint.md','visualization/docs/VISUALIZATION_INDEX.md']
    required_flyworld = ['AGENTS.md','STATUS.md','docs/PRODUCT_NORTH_STAR.md','docs/SCIENTIFIC_BOUNDARIES.md',
                        'docs/CHECKPOINT_01_FOUNDATION.md','docs/CHECKPOINT_02_MVP.md','docs/CHECKPOINT_03_REAL_DATA.md',
                        'docs/DECISIONS.md','docs/UNRESOLVED.md']
    expected = [RESEARCH/p for p in required_research]+[PROJECT/p for p in required_flyworld]
    missing = [str(p) for p in expected if not p.is_file()]
    mappings, conversions, frames, derivatives = [], [], [], []
    for path in cache_paths:
        body = path.stem
        receipt_path = path.with_suffix('.source.json')
        receipt = read(receipt_path)
        rec = dict(body_id=body,dataset=DATASET,version=VERSION,status='VERIFIED_BODY_GEOMETRY',geometry_kind='NATIVE_SWC',
                   source_path=str(path),source_sha256=sha256(path),source_url=receipt['source_url'],
                   receipt_path=str(receipt_path),receipt_sha256=sha256(receipt_path),annotation_path=str(flat),annotation_sha256=flat_hash,
                   mapping_evidence='Exact official v1.0 per-body URL + checksum-matched acquisition receipt + authoritative annotation bodyId',
                   coordinate_evidence='S-DOWNLOAD native skeletons-swc section; S-ORIENTATION',
                   units='8 nm',scale_to_micrometers=0.008,orientation_status='ORIENTATION_UNVERIFIED',orientation_labels=None,transform=IDENTITY)
        mappings.append(rec)
    validate_mappings(mappings, inventory)
    for rec in mappings:
        body = rec['body_id']
        source('S-SWC-'+body, rec['source_path'], 'Verified native SWC '+body, url=rec['source_url'])
        source('S-RECEIPT-'+body, rec['receipt_path'], 'Official per-body URL/acquisition hash receipt')
        # Audit copies are separate, immutable, and excluded from browser loading.
        for key in ['source','receipt']:
            original = Path(rec[key+'_path'])
            dest = CACHE/'raw_refs'/(rec[key+'_sha256'] + original.suffix)
            write_immutable(dest, original.read_bytes())
            rec[key+'_cache_path'] = str(dest)
        conversion = convert_swc(rec, CACHE/'converted', parse_swc)
        conversion['parser_path'] = str(PROJECT/'scripts/preprocess/anatomy.py')
        conversion['parser_sha256'] = sha256(conversion['parser_path'])
        conversions.append(conversion)
        frames.append(dict(source_id='S-SWC-'+body,source_path=rec['source_path'],dataset=DATASET,version=VERSION,
            units='8 nm per coordinate unit',voxel_resolution='8,8,8 nm EM grid; skeleton sampling is separate',axis_order='X,Y,Z (SWC columns 3,4,5)',
            axis_directions='UNVERIFIED',handedness='UNVERIFIED',origin='Native EM origin retained; anatomical origin UNVERIFIED',
            orientation_labels='ORIENTATION_UNVERIFIED',existing_transform='Identity in stored SWC/cache; source skeletonization metadata retained',
            evidence='S-DOWNLOAD; S-ORIENTATION; S-RECEIPT-'+body,status='ORIENTATION_UNVERIFIED',
            notes=json.dumps(conversion['native_metadata'])+'; no individual brain/CNS extent classification; no validated synapse overlay.'))
        derivative_path = WORKSPACE/'visualization/reports/current/geometry'/(body+'.json')
        derivative = read(derivative_path)
        points, _ = parse_swc(Path(rec['source_path']).read_text(), 1_000_000)
        index = {p[0]: i for i, p in enumerate(points)}
        expected_branches = [[index[p[6]], i] for i, p in enumerate(points) if p[6] != -1]
        if (derivative['body_id'] != body or derivative['sha256'] != rec['source_sha256'] or
            derivative['source_url'] != rec['source_url'] or derivative['factor_applied_once'] != 0.008 or
            derivative['branches'] != expected_branches or len(derivative['points']) != len(points)):
            raise ValueError('Existing micrometer derivative provenance/topology mismatch: '+body)
        delta = max(abs(actual - raw * 0.008) for point, original in zip(derivative['points'], points)
                    for actual, raw in zip(point, original[2:5]))
        if delta > 1e-9:
            raise ValueError('Existing derivative coordinate scale mismatch: '+body)
        sid = source('S-UM-'+body, derivative_path, 'Existing micrometer display derivative; all points/branches cross-checked')
        derivatives.append(dict(body_id=body,path=str(derivative_path),sha256=sha256(derivative_path),
            source_sha256=rec['source_sha256'],scale=0.008,max_coordinate_error_um=delta,
            topology_exact=True,point_count=len(points),source='S-SWC-'+body))
        frames.append(dict(source_id=sid,source_path=str(derivative_path),dataset=DATASET,version=VERSION,units='micrometers',
            voxel_resolution='Source EM grid 8,8,8 nm',axis_order='X,Y,Z',axis_directions='UNVERIFIED',handedness='UNVERIFIED',
            origin='Native origin retained numerically; anatomical origin UNVERIFIED',orientation_labels='ORIENTATION_UNVERIFIED',
            existing_transform='XYZ multiplied by 0.008 once; branches retained; display derivative omits SWC radii/type columns',
            evidence='S-SWC-'+body+'; S-DOWNLOAD; S-AUDIT',status='ORIENTATION_UNVERIFIED',
            notes='Not a new body. Exact topology and scale checked against original SWC; not selected for raw-asset recovery.'))
    by_body = {r['body_id']:r for r in mappings}
    coverage=[]
    for body in sorted(requested.keys() | by_body.keys(),key=int):
        annotation=inventory[body]; record=by_body.get(body); node=requested.get(body,{})
        coverage.append(dict(body_id=body,type=annotation['type'] or '',alias=node.get('display_alias') or annotation['synonyms'] or '',
            side=node.get('side') or annotation['somaSide'] or annotation['rootSide'] or '',expected_dataset=DATASET,
            geometry_path=record['source_path'] if record else '',geometry_format='swc' if record else '',
            mapping_evidence=record['mapping_evidence'] if record else 'S-REQUESTED + S-NODES + S-ANNOTATIONS establish ID only; S-INVENTORY has no matching geometry',
            status='VERIFIED_BODY_GEOMETRY' if record else 'MISSING',checksum=record['source_sha256'] if record else '',
            notes=('REQUESTED_CIRCUIT' if body in requested else 'SEPARATE_CACHE_BODY; not substituted for requested circuit')+'; ORIENTATION_UNVERIFIED'))
    csv_write(DOCS/'BODY_GEOMETRY_COVERAGE.csv',coverage,COVERAGE_COLUMNS)
    catalog=read(PROJECT/'public/data/malecns/manifest.json')
    states=[]
    def state(feature, claimed, path, fmt, ids, frame, units, verified, notes, sid):
        states.append(dict(asset_or_feature=feature,claimed_status=claimed,actual_file=str(path) if path else '',actual_format=fmt,
            body_or_region_id=ids,dataset=DATASET if sid!='S-PLACEHOLDER' else 'NONE — EDUCATIONAL PLACEHOLDER',dataset_version=VERSION if sid!='S-PLACEHOLDER' else 'demo-1',
            source=sid,checksum=sha256(path) if path else '',coordinate_frame=frame,units=units,verified=verified,notes=notes))
    state('Brain inside avatar / educational regions','PLACEHOLDER_GEOMETRY',PROJECT/'src/brain/PlaceholderBrain.tsx','TSX procedural geometry','demo regions','Illustrative avatar space','arbitrary','NO','Five display volumes, generic demo nodes; not a real reference brain.','S-PLACEHOLDER')
    loaded=[]
    for entry in catalog['packages']:
        path=PROJECT/'public/data/malecns'/entry['file']
        if sha256(path)!=entry['sha256']:
            raise ValueError('Browser package hash mismatch')
        pkg=read(path)
        state(entry['id'],entry['scientificLabel'],path,'JSON circuit package','|'.join(n['bodyId'] for n in pkg['neurons']),
              'Abstract graph; native morphology only for explicit assets','N/A','METADATA_AND_STRUCTURE_ONLY',
              f"{len(pkg['neurons'])} bodies / {len(pkg['edges'])} structural edges; metadata is not morphology.",'S-PACKAGES')
        for node in pkg['neurons']:
            if node['anatomy']['status']!='SOURCE_BACKED_SWC': continue
            asset=PROJECT/'public'/node['anatomy']['asset'].lstrip('/')
            payload=read(asset);body=node['bodyId']; original=by_body[body]
            points,headers=parse_swc(Path(original['source_path']).read_text(),1_000_000)
            if sha256(asset)!=node['anatomy']['sha256'] or payload['points']!=points or payload['sourceHeaders']!=headers or payload['bodyId']!=body:
                raise ValueError('Loaded morphology/source round-trip mismatch: '+body)
            loaded.append(body)
            state('Loaded selected-body morphology '+body,'SOURCE_BACKED_SWC',asset,'FLYWORLD_NATIVE_SWC JSON',body,
                  'Native EM data; per-body centered float32 render buffer','8 nm','VERIFIED_BODY_GEOMETRY',
                  'Original numeric points/parents/headers match SWC; no shared render origin or anatomical axis labels.','S-SWC-'+body)
            sid=source('S-LOADED-'+body,asset,'Current native-coordinate browser cache')
            frames.append(dict(source_id=sid,source_path=str(asset),dataset=DATASET,version=VERSION,units='8 nm',
                voxel_resolution='Source EM grid 8,8,8 nm',axis_order='X,Y,Z',axis_directions='UNVERIFIED',handedness='UNVERIFIED',
                origin='Native origin retained in JSON',orientation_labels='ORIENTATION_UNVERIFIED',existing_transform='Identity in stored JSON',
                evidence='S-SWC-'+body+'; S-AUDIT',status='ORIENTATION_UNVERIFIED',notes='Numeric fields/headers match original SWC exactly; renderer transform recorded separately.'))
    for feature in ['Full reference brain surface','Ventral nerve cord envelope','Cervical connective geometry','Full CNS envelope','Neuropil/region meshes','Individual neuron meshes','Individual synapse coordinates']:
        state(feature,'UNAVAILABLE',None,'','', 'UNVERIFIED','UNITS_UNVERIFIED','NO',
              'No source-backed local asset identified in audited roots; official remote availability is a separate question.','S-INVENTORY')
    state('Soma annotation coordinates','SOURCE-BACKED METADATA',flat,'Feather','annotation body IDs','UNVERIFIED alignment to native SWCs','UNITS_UNVERIFIED','COORDINATES_PRESENT_NOT_GEOMETRY','somaLocation and tosomaLocation are point metadata, not neuron cables or synapse coordinates.','S-ANNOTATIONS')
    csv_write(DOCS/'CURRENT_ANATOMY_STATE.csv',states,STATE_COLUMNS)
    for sid,path,units,resolution,transform,notes in [
        ('REMOTE-NATIVE-PRECOMPUTED','gs://flyem-male-cns/v1.0/segmentation/skeletons-malecns/skeletons-precomputed/','1 nm','8 nm underlying EM grid','Native EM','Not downloaded; factor 8 differs from SWC numeric coordinates.'),
        ('REMOTE-MIRRORED-SWC','gs://flyem-male-cns/v1.0/segmentation/skeletons-malecns-mirrored/skeletons-swc/','8 nm','8 nm underlying EM grid','Mirrored by external transform, not audited','Not downloaded; forbidden as implicit native replacement.'),
        ('REMOTE-TEMPLATE','gs://flyem-male-cns/v1.0/segmentation/skeletons-unisex-template/','1 micrometer','Not applicable','Transformed to JRC2018 unisex template; matrix not available locally','Not downloaded; not native coordinates.'),
        ('REMOTE-BRAIN-ROI','gs://flyem-male-cns/rois/fullbrain-roi-v4','256 nm voxels','256,256,256 nm','Transferred/refined labels; transform unavailable','Remote volume description only; not a local surface or proven whole-brain envelope.'),
        ('REMOTE-VNC-ROI','gs://flyem-male-cns/rois/malecns-vnc-neuropil-roi-v0','256 nm voxels','256,256,256 nm','Refined ROI labels; transform unavailable','Remote volume description only; not a local VNC mesh.'),
        ('REMOTE-SYNAPSES','gs://flyem-male-cns/v1.0/connectome-data/flat-connectome/','8 nm','8,8,8 nm','Native XYZ per download documentation','Individual pre/post point tables not present locally; aggregate weights are not coordinates.'),
        ('S-ANNOTATIONS',str(flat),'UNITS_UNVERIFIED','UNVERIFIED','None applied by audit','XYZ point arrays retained; saved body-side labels do not prove native axis signs or alignment.'),
        ('S-RENDERER',str(PROJECT/'src/realdata/MorphologyView.tsx'),'Native numeric units in display buffer','Not applicable','Per-body bounding-box center subtraction after Float32 conversion','Single-body visual inspection only. A joint view must retain a common origin and explicit inverse transform.')]:
        frames.append(dict(source_id=sid,source_path=path,dataset=DATASET,version=VERSION if not sid.startswith('REMOTE-') else 'v1.0 context; verify remote metadata before import',
            units=units,voxel_resolution=resolution,axis_order='X,Y,Z; array/volume storage axis order not verified',axis_directions='UNVERIFIED',
            handedness='UNVERIFIED',origin='UNVERIFIED',orientation_labels='ORIENTATION_UNVERIFIED',existing_transform=transform,
            evidence='S-DOWNLOAD' if sid.startswith('REMOTE-') else sid,status='ORIENTATION_UNVERIFIED',notes=notes))
    probe=WORKSPACE/'visualization/cache/10029.probe.swc'
    if probe.read_bytes() != Path(by_body['10029']['source_path']).read_bytes():
        raise ValueError('Probe differs from canonical 10029; retain as unresolved candidate')
    probe_info={'path':str(probe),'sha256':sha256(probe),'canonical_10029_sha256':by_body['10029']['source_sha256'],
                'mapping_status':'VERIFIED_BODY_GEOMETRY','reason':'Byte-identical duplicate of receipt-verified canonical 10029; not an additional body or independent acquisition.'}
    source('S-PROBE',probe,'Byte-identical duplicate of canonical 10029; no independent acquisition claim')
    frames.append({**next(f for f in frames if f['source_id']=='S-SWC-10029'),
                   'source_id':'S-PROBE','source_path':str(probe),'notes':'Byte-identical canonical 10029 duplicate; not a ninth body.'})
    for conversion in conversions:
        frames.append({**next(f for f in frames if f['source_id']=='S-SWC-'+conversion['body_id']),
                       'source_id':'AUDIT-CONVERTED-'+conversion['body_id'],'source_path':conversion['output_path'],
                       'existing_transform':'Identity; scale 1; no simplification',
                       'notes':'New lossless audit-only cache. Conversion and parser hashes in conversions.json. Not imported into browser.'})
    csv_write(DOCS/'COORDINATE_FRAME_LEDGER.csv',frames,FRAME_COLUMNS)
    requested_verified=len(requested.keys() & by_body.keys())
    summary=dict(requested_bodies=len(requested),minimum_requested_type_bodies=len(minimum_ids),requested_verified_geometry=requested_verified,
                 separate_verified_cache_bodies=len(mappings),currently_loaded_body_ids=sorted(set(loaded),key=int),
                 reference_meshes_verified=0,orientation='ORIENTATION_UNVERIFIED',retrieval_status='BLOCKED — AUTHORITATIVE GEOMETRY SOURCE REQUIRED',
                 probe=probe_info,requested_type_counts=dict(Counter(n['type'] for n in requested.values())))
    save(CACHE/'manifests/geometry-mappings.json',mappings)
    save(CACHE/'manifests/conversions.json',conversions)
    save(CACHE/'manifests/existing-derivatives.json',derivatives)
    manifest=dict(format='FLYWORLD_ANATOMY_AUDIT',schema_version=1,timestamp=timestamp,dataset=DATASET,version=VERSION,neuprint_uuid=UUID,
                  authority_scope='Saved v1.0 release receipts and pinned source records; not a current mutation-state query',
                  missing_expected_files=missing,required_context_files=[str(p) for p in expected],sources=sources,
                  summary=summary,discovery=read(CACHE/'manifests/discovery.json'),
                  geometry_manifest='data/anatomy/manifests/geometry-mappings.json',conversion_manifest='data/anatomy/manifests/conversions.json',
                  no_runtime_changes=True,no_avatar_registration=True,no_simulation=True)
    save(DOCS/'ANATOMY_SOURCE_MANIFEST.json',manifest)
    save(CACHE/'manifests/summary.json',summary)
    claims=[
      ('A001','0 of the exact 110 requested circuit bodies has verified local geometry.','S-REQUESTED;S-INVENTORY','VERIFIED_WITHIN_SEARCH_SCOPE',''),
      ('A002','Eight separate native SWCs have matching official release receipts and annotation identities; three are loaded by the current application.','S-ANNOTATIONS;S-PACKAGES;S-SWC-*;S-RECEIPT-*','VERIFIED_BODY_GEOMETRY','No requested-body substitution.'),
      ('A003','The visible avatar brain is authored placeholder geometry; no local reference brain/CNS or neuron/neuropil mesh was identified.','S-PLACEHOLDER;S-INVENTORY','VERIFIED_WITHIN_SEARCH_SCOPE','Remote documented volumes are not local meshes.'),
      ('A004','Native SWC coordinates are in 8 nm units; native precomputed skeletons use 1 nm; template skeletons use 1 micrometer.','S-DOWNLOAD','VERIFIED_SAVED_OFFICIAL_DOCUMENT','Scale-to-micrometers for SWC is 0.008; skeleton point spacing is not voxel resolution.'),
      ('A005','Anatomical axis signs, handedness, anatomical origin and avatar registration remain unverified.','S-ORIENTATION;S-RENDERER','ORIENTATION_UNVERIFIED','Source XYZ values are retained; no named anatomical camera justified.'),
      ('A006','The first authorized native SWC test request failed DNS; the other four requests were not attempted after transport failure.','S-RETRIEVAL','BLOCKED — AUTHORITATIVE GEOMETRY SOURCE REQUIRED','This is not evidence those remote bodies are missing.'),
      ('A007','Soma coordinate annotations exist; no local individual synapse coordinate table was identified.','S-ANNOTATIONS;S-INVENTORY','VERIFIED_WITHIN_SEARCH_SCOPE','Body-to-body synapse counts and soma points are not synapse positions.'),
      ('A008','Existing three browser caches exactly preserve source numeric points, parent links and SWC headers.','S-PARSER;S-RENDERER;S-PACKAGES;S-SWC-*','VERIFIED','Display buffer is Float32 and independently centered for each selected body.'),
      ('A009','The 10029 probe is byte-identical to canonical receipt-backed 10029; it is a duplicate, not a ninth distinct body.','S-PROBE;S-SWC-10029;S-RECEIPT-10029','VERIFIED','Corrects AM004 provisional mapping uncertainty after byte comparison.'),
      ('A010','Eight existing micrometer JSON derivatives preserve all native skeleton points after scaling by 0.008 and retain parent-child topology.','S-UM-*;S-SWC-*;S-AUDIT','VERIFIED','These derivatives omit SWC radii/type columns and are not treated as raw assets.'),
    ]
    append_ledger(DOCS/'ANATOMY_CLAIM_LEDGER.csv',[dict(claim_id=i,timestamp=timestamp,claim=c,source_ids=s,verification_status=v,supersedes_claim_id='',notes=n) for i,c,s,v,n in claims],CLAIM_COLUMNS)
    mismatches=[
      ('AM001','Requested geometry versus loaded anatomy','0 requested SWCs may be read as no real anatomy anywhere','8 separate cached bodies verified; 3 loaded; 0/110 requested','Counts describe different populations','Keep requested and incidental-body coverage separate','YES','RESOLVED_SCOPE_DISTINCTION','S-REQUESTED;S-PACKAGES;S-INVENTORY'),
      ('AM002','Segmentation UUID versus neuPrint UUID','A SWC header UUID could be substituted for dataset UUID','SWC segmentation UUID and neuPrint dataset UUID are different provenance fields','No live mutation-state equivalence established','Retain both without substitution','YES','UNVERIFIED_MUTATION_ALIGNMENT','S-META;S-SWC-*'),
      ('AM003','Single-body framing versus shared anatomical placement','A loaded native skeleton may be assumed ready for direct avatar/shared-frame placement','Renderer centers each body independently; no authoritative anatomical transform','Current display buffers cannot establish relative body placement or anatomical axis signs','Use original native coordinates and one recorded shared transform; obtain orientation before avatar registration','YES, as labeled single-body inspection','SCIENTIFIC_PLAN_REVISION_REQUIRED','S-RENDERER;S-ORIENTATION'),
      ('AM004','Probe file identity','Filename 10029.probe.swc alone could establish a body mapping','No dedicated acquisition receipt; canonical 10029 has an independent receipt','Probe excluded from verified body count','Retain as likely/unverified candidate; use canonical receipt-backed SWC','YES','LIKELY_BUT_UNVERIFIED','S-INVENTORY;S-RECEIPT-10029'),
      ('AM005','Correction superseding AM004 probe uncertainty','AM004 provisionally excluded probe mapping pending evidence beyond its filename','Byte comparison and SHA256 establish exact identity with canonical receipt-backed 10029','Mapping supported via verified canonical bytes; independent acquisition still unverified','Treat as duplicate 10029; retain AM004 as superseded history','YES','RESOLVED_DUPLICATE; SUPERSEDES_AM004','S-PROBE;S-SWC-10029;S-RECEIPT-10029'),
    ]
    append_ledger(DOCS/'ANATOMY_MISMATCH_LEDGER.csv',[dict(zip(MISMATCH_COLUMNS,[i,timestamp,*rest])) for i,*rest in mismatches],MISMATCH_COLUMNS)
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
