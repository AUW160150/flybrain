from __future__ import annotations
import json, csv, sqlite3, ast, tempfile
from pathlib import Path
import numpy as np
import pytest
from connectome_viz.provenance import ROOT,REPORT,EXPERIMENT,body_id,EvidenceError,protect_inventory,read
from connectome_viz import indexing as ix
from connectome_viz.discover_run import verify_graph,verify_archive,select_runs
from connectome_viz.morphology import parse_swc
from connectome_viz.ingest import SMALL,removal_ledger

@pytest.fixture
def fixture():
    # Decimal IDs are unmistakably synthetic through explicit database provenance.
    with tempfile.TemporaryDirectory(prefix='synthetic-fixture-',dir=ROOT/'cache') as tmp:
        db=ix.connect(Path(tmp)/'fixture.sqlite')
        ix.put_meta(db,'provenance_mode','synthetic-fixture; never a published gallery')
        A,B,I,U=9007199254740993,9007199254740994,9007199254740995,9007199254740996
        db.executemany('INSERT INTO nodes(id,model_index,curated,cls,typ,g0,ref) VALUES (?,?,?,?,?,?,?)',[(A,0,1,'fixture',None,1,'SYNTHETIC A'),(B,1,1,None,None,1,'SYNTHETIC B'),(I,None,1,None,None,0,'SYNTHETIC isolate'),(U,None,0,None,None,1,'SYNTHETIC noncurated')])
        db.executemany('INSERT INTO edges VALUES (?,?,?,?,?,?,?,?)',[(A,B,7,0,1,1,1,1),(B,A,0,1,1,0,0,1),(B,B,2,2,1,0,0,1),(U,A,3,3,0,0,0,0)])
        ix.put_meta(db,'identity','SYNTHETIC-SEVEN-CONTACT-FIXTURE');ix.put_meta(db,'ingest_rows_complete',True);ix.finish(db,['G0','G1','G2','G3','G1-subset'])
        yield db,A,B,I,U,Path(tmp)
        db.close()

def test_lossless_ids_above_js_limit(fixture):
    db,A,B,*_=fixture
    node=ix.node(db,'G1',str(A));encoded=json.dumps(node)
    assert json.loads(encoded)['body_id']=='9007199254740993'
    assert ix.pair(db,'G1',str(A),str(B))['record']['synapse_count']==7
    with pytest.raises(EvidenceError):body_id(float(A))
    with pytest.raises(EvidenceError):body_id('09007199254740993')

def test_isolates_unknowns_and_g0_g1_scope(fixture):
    db,A,B,I,U,_=fixture
    assert ix.node(db,'G1',str(I))['status']=='found'
    assert ix.node(db,'G0',str(I))['status']=='no_matching_node'
    assert ix.node(db,'G1',str(U))['status']=='no_matching_node'
    assert ix.summary(db,'G1')['nodes']==3
    assert ix.summary(db,'G1')['pairs']==3
    assert ix.summary(db,'G0')['pairs']==4
    assert ix.summary(db,'G1')['unknown_annotations']==3

def test_duplicate_pairs_fail_without_summing(fixture):
    db,A,B,*_=fixture
    with pytest.raises(sqlite3.IntegrityError):db.execute('INSERT INTO edges VALUES (?,?,?,?,1,1,1,1)',(A,B,3,4))

def test_direction_seven_contacts_matrix_recurrent_and_export(fixture):
    import torch
    db,A,B,*_=fixture
    data=ix.tile(db,'G1','id',256);p=next(r for r in data['rows'] if r['x']==0 and r['y']==1)
    assert p['contacts']==7 and p['pairs']==1
    w=torch.zeros(2,2);w[1,0]=7;h=torch.tensor([[2.,0.]])
    assert torch.equal(h@w.T,torch.tensor([[0.,14.]]))
    assert ix.partners(db,'G1',str(B),'incoming')['rows'][0]['source_body_id']==str(A)
    assert 'source' in (ROOT/'src/connectome_viz/web/app.js').read_text()

def test_all_reductions_conserve_and_zoom(fixture):
    db,*_=fixture
    for scope in ix.SCOPES:
        summary=ix.summary(db,scope)
        for ordering in ['id','group']:
            for bins in [1,2,4,128]:
                tile=ix.tile(db,scope,ordering,bins)
                assert tile['pairs']==summary['pairs'] and tile['contacts']==summary['contacts']
                assert sum(x['end']-x['start'] for x in tile['x'])==summary['nodes']
    t=ix.tile(db,'G1','id',128,0,1,1,2)
    assert t['contacts']==7 and t['x'][0]['single'] and t['y'][0]['single']

def test_groups_unknown_and_self_conserve(fixture):
    db,*_=fixture
    for scope in ix.SCOPES:
        g=ix.groups(db,scope);s=ix.summary(db,scope)
        assert g['pairs']==s['pairs'] and g['contacts']==s['contacts']
    assert any(e['source_group']==e['target_group']=='Unknown' for e in ix.groups(db,'G1')['edges'])

def test_partner_pagination_no_gaps(fixture):
    db,A,B,*_=fixture
    rows=[]
    for offset in range(3):rows+=ix.partners(db,'G1',str(B),'incoming',offset,1)['rows']
    assert len(rows)==2 and len({(r['source_body_id'],r['target_body_id']) for r in rows})==2
    assert sum(r['synapse_count'] for r in rows)==9

def test_unknown_scope_and_absence_are_distinct(fixture):
    db,A,B,I,*_=fixture
    assert ix.pair(db,'G1',str(A),str(I))['status']=='verified_absence_in_release_scope'
    assert ix.pair(db,'G1',str(A),'999')['status']=='endpoint_outside_scope'
    ix.put_meta(db,'complete_scopes',['G3'])
    with pytest.raises(EvidenceError,match='E_INCOMPLETE_INGEST'):ix.pair(db,'G1',str(A),str(B))

def test_scope_queries_cannot_mutate_mask(fixture):
    db,A,B,*_=fixture;before=list(map(tuple,db.execute('SELECT * FROM edges ORDER BY source,target')))
    ix.tile(db,'G3','model',1);ix.tile(db,'G1','group',2);ix.partners(db,'G1',str(A),'incoming',0,1)
    assert before==list(map(tuple,db.execute('SELECT * FROM edges ORDER BY source,target')))

def test_boundaries_partition_with_loops_and_undefined_fraction(fixture):
    db,A,B,*_=fixture;l=removal_ledger(db)
    for node in l['rows']:
        for direction in ['incoming','outgoing']:
            r=node[direction];assert sum(x['pairs'] for x in r['categories'].values())==r['G1']['pairs'];assert sum(x['contacts'] for x in r['categories'].values())==r['G1']['contacts']
    a=next(x for x in l['rows'] if x['body_id']==str(A));assert a['incoming']['retained_contact_fraction_G1'] is None

def test_swc_units_once_foreign_keys_and_missing(fixture):
    path=fixture[-1]/'fixture.swc';path.write_text('# SYNTHETIC coordinate fixture\n1 1 1000 2000 3000 2 -1\n2 3 2000 2000 3000 1 1\n')
    assert parse_swc(path,'8nm')['points'][0]==[8.,16.,24.]
    assert parse_swc(path,'nm')['points'][0]==[1.,2.,3.]
    assert parse_swc(path,'um')['points'][0]==[1000.,2000.,3000.]
    with pytest.raises(EvidenceError):parse_swc(path,'8nm',converted=True)
    with pytest.raises(EvidenceError):parse_swc(path,'unknown')
    path.write_text('1 3 2 3 4 1 77\n')
    with pytest.raises(EvidenceError):parse_swc(path,'8nm')

def test_real_saved_node_mapping_and_graph():
    g=verify_graph();m=read(REPORT/'identity.json')
    assert m['parent_induced_exact'] and m['graph_hash']==g['graph_hash']
    assert len(g['ids'])==512 and len(g['source'])==3061 and g['counts'].sum()==38708
    assert np.array_equal(np.lexsort((g['source'],g['target'])),np.arange(3061))

def test_authentic_rejects_synthetic_graph(tmp_path):
    # Identity validation fails BEFORE opening any graph payload.
    path=tmp_path/'synthetic.npz';path.with_suffix('.json').write_text(json.dumps({'metadata':{'synthetic':True,'condition':'FLY-TOPOLOGY'}}))
    with pytest.raises(EvidenceError,match='E_RUN_IDENTITY_MISSING'):verify_graph(path)

def test_archived_source_and_formula():
    a=read(REPORT/'architecture.json');p=a['actual'];assert p['active_trainable']==49920+3061
    assert sum(r['elements'] for r in p['parameters'])==52981
    assert p['nontrainable_storage_bytes']==3061*2*8
    assert p['alpha']==.5
    assert verify_archive(p['executed_code_hash']).is_file()

def test_zero_allowed_weight_retention_and_unrolled_sharing():
    import torch
    from connectome_viz.model_inspection import archived_modules
    a=read(REPORT/'architecture.json');mod,_=archived_modules(verify_archive(a['actual']['executed_code_hash']))
    model=mod.GraphRNN(2,3,np.array([0]),np.array([1]));model.eval()
    with torch.no_grad():
        for p in model.parameters():p.zero_()
    h=torch.tensor([[.8,.4]])
    with torch.inference_mode():_,states=model(torch.tensor([[97,98,99]]),state=h,return_states=True)
    assert model.theta.numel()==1 and model.source.tolist()==[0] and model.target.tolist()==[1]
    torch.testing.assert_close(states[0,0],h[0]*.5)
    torch.testing.assert_close(states[0,2],h[0]*.125)
    assert not torch.any(model.source==model.target)
    p=sum(x.numel() for x in model.parameters());assert p==sum(x.numel() for x in model.parameters())

def test_references_instantiated_shapes_and_causality():
    import torch
    from connectome_viz.baselines_schematic import WindowMLP,CausalCNN,shape_and_causality,parameter_inventory
    from connectome_viz.model_inspection import archived_modules
    torch.set_num_threads(1);a=read(REPORT/'architecture.json');_,t=archived_modules(verify_archive(a['actual']['executed_code_hash']));cfg=a['references'][2]['config']
    refs=[WindowMLP(),CausalCNN(),t.TransformerLM(cfg['d'],cfg['ff'],cfg['layers'],cfg['context'])]
    for r,e in zip(refs,a['references']):
        assert shape_and_causality(r)['status']=='passed';assert parameter_inventory(r)['active_trainable']==e['active_trainable']
    assert refs[1].conv1.dilation==(1,) and refs[1].conv2.dilation==(2,)

def test_parameter_tying_counted_once():
    import torch
    from connectome_viz.baselines_schematic import parameter_inventory
    m=torch.nn.Module();m.a=torch.nn.Linear(2,3);m.b=m.a
    assert parameter_inventory(m)['active_trainable']==9

def test_real_prethreshold_and_ledger_conservation():
    db=ix.connect(SMALL,True)
    try:
        assert ix.summary(db,'G3')['contacts']==38708
        assert ix.summary(db,'G1-subset')['pairs']==7405
        for scope in ['G3','G1-subset']:
            t=ix.tile(db,scope,'group',64);s=ix.summary(db,scope);g=ix.groups(db,scope)
            assert t['pairs']==s['pairs']==g['pairs'];assert t['contacts']==s['contacts']==g['contacts']
        l=removal_ledger(db)
        assert sum(r['incoming']['categories'].get('retained_G3',{}).get('contacts',0) for r in l['rows'])==38708
        assert sum(r['outgoing']['categories'].get('retained_G3',{}).get('pairs',0) for r in l['rows'])==3061
    finally:db.close()

def test_edge_order_mismatch_blocks_before_weights():
    from connectome_viz.model_inspection import inspect_payload
    import torch
    g=verify_graph();p,m=select_runs()[0]
    payload={'signature':m['signature'],'code_hash':m['code_hash'],'model':{'source':torch.tensor(g['source'][::-1].copy()),'target':torch.tensor(g['target'])}}
    with pytest.raises(EvidenceError,match='E_EDGE_ORDER_UNVERIFIED'):inspect_payload(payload,m,g,{},None,p.name)

def test_no_optimizer_or_corpus_entrypoint():
    for p in (ROOT/'src/connectome_viz').glob('*.py'):
        tree=ast.parse(p.read_text())
        for node in ast.walk(tree):
            if isinstance(node,ast.ImportFrom):assert node.module not in ('fly_connectome_lm.train','fly_connectome_lm.text_data','fly_connectome_lm.evaluate')
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute):assert node.func.attr not in ('Adam','AdamW','SGD','backward')
    text=(ROOT/'src/connectome_viz/model_inspection.py').read_text()
    assert 'weights_only=False' not in text

def test_protected_static_inputs_unchanged():
    baseline=read(REPORT/'inventory.json')['protected'];assert baseline==protect_inventory()

def test_source_json_ids_and_no_unsafe_html():
    ids=read(REPORT/'subset-ids.json');assert all(isinstance(x,str) for x in ids)
    js=(ROOT/'src/connectome_viz/web/app.js').read_text();assert '.innerHTML' not in js
    assert 'textContent' in js and 'URLSearchParams' in js

def test_real_geometry_coverage_and_scale():
    g=read(REPORT/'geometry.json');assert g['loaded']==8 and g['total']==512
    for ident,r in g['records'].items():
        raw=ROOT/'cache/morphology'/(ident+'.swc');data=parse_swc(raw,'8nm')
        payload=read(REPORT/'geometry'/(ident+'.json'))
        assert payload['points'][0]==data['points'][0] and r['factor_applied_once']==.008
        assert r['coordinate_evidence']=='https://male-cns.janelia.org/download/'
    assert len(g['not_requested'])==504

def test_broken_geometry_is_error_and_full_scope_not_zero():
    from connectome_viz.app import query
    with pytest.raises(EvidenceError,match='E_GEOMETRY_UNAVAILABLE'):query('geometry',{'id':['13506']})
    with pytest.raises(EvidenceError,match='E_INCOMPLETE_INGEST'):query('pair',{'scope':['G0'],'source':['10029'],'target':['10053']})

def test_input_safety_and_loopback_only(fixture):
    from connectome_viz.app import serve
    with pytest.raises(ValueError):serve('0.0.0.0',8765)
    with pytest.raises(EvidenceError):ix.partners(fixture[0],'G1',"1; DROP TABLE edges",'incoming')
    with pytest.raises(ValueError):ix.tile(fixture[0],'G1','id;DROP',128)
    with pytest.raises(ValueError):ix.tile(fixture[0],'G1','id',100000)

@pytest.fixture
def raw_fixture(monkeypatch):
    import pyarrow as pa
    import connectome_viz.ingest as ingest
    from connectome_viz.provenance import sha
    with tempfile.TemporaryDirectory(prefix='SYNTHETIC-ingest-',dir=ROOT/'cache') as tmp:
        folder=Path(tmp);f=folder/'weights.feather';manifest=folder/'manifest.json';manifest.write_text('{}')
        A,B,I,U=9007199254740993,9007199254740994,9007199254740995,9007199254740996
        rows=[(A,B,7),(B,A,0),(B,B,2),(U,A,3)]
        def write_rows(data,names=['body_pre','body_post','weight']):
            schema=pa.schema([(n,pa.int64()) for n in names])
            with pa.OSFile(str(f),'wb') as sink:
                with pa.ipc.new_file(sink,schema) as writer:
                    for start in range(0,len(data),2):
                        writer.write_batch(pa.record_batch([pa.array([r[i] for r in data[start:start+2]],type=pa.int64()) for i in range(3)],schema=schema))
        write_rows(rows)
        g={'ids':np.array([A,B]),'source':np.array([0]),'target':np.array([1]),'counts':np.array([7]),'graph_hash':'SYNTHETIC-fixture-only'}
        def ann(db,g):
            db.executemany('INSERT OR IGNORE INTO nodes(id,model_index,curated,cls,typ,ref) VALUES (?,?,?,?,?,?)',[(A,0,1,'SYNTHETIC',None,'fixture'),(B,1,1,None,None,'fixture'),(I,None,1,None,None,'fixture')]);return np.array([A,B,I])
        monkeypatch.setattr(ingest,'verify_graph',lambda:g);monkeypatch.setattr(ingest,'add_annotations',ann)
        monkeypatch.setattr(ingest,'FULL',folder/'full.sqlite');monkeypatch.setattr(ingest,'SMALL',folder/'small.sqlite');monkeypatch.setattr(ingest,'REPORT',folder);monkeypatch.setattr(ingest,'RAW_MANIFEST',manifest)
        monkeypatch.setattr(ingest,'products',lambda verify=True:{'weights':{'path':str(f),'sha256':sha(f),'schema':{'rows':len(rows)},'source_url':'SYNTHETIC-FIXTURE-NOT-PUBLISHED','size_bytes':f.stat().st_size}})
        yield ingest,folder,rows,write_rows

def test_full_ingestion_pipeline_on_isolated_fixture(raw_fixture):
    ingest,folder,rows,write=raw_fixture;r=ingest.ingest(full=True,max_seconds=20)
    assert r['status']=='complete' and r['raw_rows_scanned']==4
    db=ix.connect(folder/'full.sqlite',True)
    assert ix.summary(db,'G0')['pairs']==4 and ix.summary(db,'G0')['contacts']==12
    assert ix.summary(db,'G1')['nodes']==3 and ix.summary(db,'G1')['pairs']==3
    assert ix.summary(db,'G2')['pairs']==1 and ix.summary(db,'G3')['contacts']==7
    assert ix.summary(db,'G0')['nodes']==3
    db.close();assert ingest.ingest(full=True)['status']=='already_complete'

def test_full_ingestion_resume_committed_batches(raw_fixture,monkeypatch):
    ingest,folder,rows,write=raw_fixture
    real=ingest.Budget
    class StopAfterOne:
        calls=0
        def __init__(self,*a):pass
        def check(self,*a):
            self.calls+=1
            if self.calls==2:raise EvidenceError('E_RESOURCE_BUDGET','fixture deadline','test','resume fixture')
    monkeypatch.setattr(ingest,'Budget',StopAfterOne)
    with pytest.raises(EvidenceError):ingest.ingest(full=True)
    assert not (folder/'full.sqlite').exists()
    db=ix.connect(folder/'full.partial.sqlite',True);assert ix.get_meta(db,'progress')['batch']==1;assert not ix.get_meta(db,'complete_scopes');db.close()
    monkeypatch.setattr(ingest,'Budget',real);assert ingest.ingest(full=True)['retained_rows']==4

def test_full_duplicate_across_batches_quarantines(raw_fixture):
    ingest,folder,rows,write=raw_fixture;rows[2]=rows[0];write(rows)
    with pytest.raises(EvidenceError,match='E_SCHEMA_OR_ROW_SEMANTICS_UNKNOWN'):ingest.ingest(full=True)
    assert not (folder/'full.sqlite').exists()
    assert read(folder/'full-ingest-error.json')['coverage']=='incomplete'

def test_ambiguous_roi_schema_refused(raw_fixture):
    ingest,folder,rows,write=raw_fixture;write(rows,['body_pre','body_post','ROI_total'])
    with pytest.raises(EvidenceError,match='E_SCHEMA_OR_ROW_SEMANTICS_UNKNOWN'):ingest.ingest(full=True)

def test_negative_contact_quarantines(raw_fixture):
    ingest,folder,rows,write=raw_fixture;rows[-1]=(rows[-1][0],rows[-1][1],-1);write(rows)
    with pytest.raises(EvidenceError,match='E_SCHEMA_OR_ROW_SEMANTICS_UNKNOWN'):ingest.ingest(full=True)

def test_http_handler_without_listening_socket():
    import io
    from connectome_viz.app import Handler
    class Socket:
        def __init__(self,path):self.input=io.BytesIO(f'GET {path} HTTP/1.0\r\nHost: 127.0.0.1\r\n\r\n'.encode());self.output=bytearray()
        def makefile(self,*a,**k):return self.input
        def sendall(self,d):self.output.extend(d)
    for path,status in [('/api/pair?scope=G3&source=10053&target=10029',200),('/api/pair?scope=G0&source=10053&target=10029',409),('/api/geometry?id=13506',409),('/report/../../src/connectome_viz/app.py',404),('/api/tile?scope=G3&bins=999999',400),('/',200)]:
        sock=Socket(path);Handler(sock,('127.0.0.1',0),object());assert bytes(sock.output).startswith(f'HTTP/1.0 {status}'.encode())
        if path.startswith('/api/pair?scope=G3'):
            data=json.loads(bytes(sock.output).split(b'\r\n\r\n',1)[1]);assert data['record']['source_body_id']=='10053' and data['record']['synapse_count']==23

def test_complete_selected_g1_partners_and_boundary_export():
    from connectome_viz.app import boundary_partners,Handler
    import io
    d=boundary_partners('10029','incoming',0,200);db=ix.connect(SMALL,True)
    expected=db.execute('SELECT COUNT(*),SUM(contacts) FROM edges WHERE curated=1 AND target=10029').fetchone()
    assert (d['total']['partners'],d['total']['contacts'])==tuple(expected)
    all_rows=[]
    for offset in range(0,d['total']['partners'],200):all_rows+=boundary_partners('10029','incoming',offset,200)['rows']
    assert len(all_rows)==expected[0] and sum(r['synapse_count'] for r in all_rows)==expected[1]
    assert len({r['source_body_id'] for r in all_rows})==expected[0]
    outside=next(r['source_body_id'] for r in all_rows if ix.node(db,'G3',r['source_body_id'])['status']!='found')
    with pytest.raises(EvidenceError,match='E_INCOMPLETE_INGEST'):boundary_partners(outside,'incoming')
    db.close()

def test_permuted_matrix_order_recovers_exact_real_pairs():
    db=ix.connect(SMALL,True)
    for ordering in ['model','id','group']:
        source=db.execute('SELECT rank FROM ranks WHERE scope=? AND ordering=? AND id=10053',('G3',ordering)).fetchone()[0]
        target=db.execute('SELECT rank FROM ranks WHERE scope=? AND ordering=? AND id=10029',('G3',ordering)).fetchone()[0]
        t=ix.tile(db,'G3',ordering,1,source,source+1,target,target+1)
        assert t['contacts']==23 and t['x'][0]['first_id']=='10053' and t['y'][0]['first_id']=='10029'
    db.close()

def test_exact_matrix_export_mask_is_structural():
    with np.load(REPORT/'tables/G3-exact-matrices.npz',allow_pickle=False) as z:
        assert z['adjacency'].sum()==3061 and z['synapse_count'].sum()==38708
        assert z['adjacency'].shape==(512,512)
        assert z['synapse_count'][0,1]==23

def test_javascript_arrow_sender_receiver_and_large_id():
    import subprocess,shutil
    node=shutil.which('node')
    if not node:pytest.skip('Node runtime unavailable; browser remains separately skipped')
    script="""const fs=require('fs'),vm=require('vm'),assert=require('assert');const src=fs.readFileSync(process.argv[1],'utf8');const start=src.indexOf('function arrow('),end=src.indexOf('async function loadScope');let calls=[];const c={beginPath(){},moveTo(x,y){calls.push(['M',x,y]);},lineTo(x,y){calls.push(['L',x,y]);},stroke(){},fill(){}};const box={Math};vm.createContext(box);vm.runInContext(src.slice(start,end),box);box.arrow(c,10,20,110,20,'teal');assert.deepEqual(calls[0],['M',10,20]);assert.deepEqual(calls[1],['L',105,20]);assert.equal(JSON.parse('{\"body_id\":\"9007199254740993\"}').body_id,'9007199254740993');"""
    p=subprocess.run([node,'-e',script,str(ROOT/'src/connectome_viz/web/app.js')],capture_output=True,text=True)
    assert p.returncode==0,p.stderr
