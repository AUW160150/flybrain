import json
from pathlib import Path
import numpy as np
import pyarrow as pa
import pyarrow.feather as feather
import pytest
from fly_connectome_lm.util import atomic_json,sha256,load_config
from fly_connectome_lm.graph_extract import canonicalize,extract,Graph
from fly_connectome_lm.models import GraphRNN
from fly_connectome_lm.experiment import matrix,freeze_config
from fly_connectome_lm.final_evaluation import final_evaluate
from fly_connectome_lm.cli import main


def test_canonical_mapping_ids_exclusions_induced_graph(tmp_path):
    # IDs above the exact float64 integer range must survive unchanged.
    ids=np.arange(2**53+10,2**53+76,dtype=np.int64)
    ann=tmp_path/'body-annotations-test.feather'; weight=tmp_path/'connectome-weights-test.feather'
    table=pa.table({'bodyId':ids,'status':['Traced']*65+['Glia'],'statusLabel':['Traced']*65+['Glia'],
                    'type':[None]*66,'superclass':[None]*66,'class':[None]*66})
    feather.write_feather(table,ann)
    s=list(ids[:64])+[ids[3],ids[0],ids[65],ids[1]]
    t=list(ids[1:65])+[ids[1],ids[0],ids[0],ids[5]]
    c=[5]*64+[9,8,8,4]
    feather.write_feather(pa.table({'body_pre':pa.array(s,type=pa.int64()),'body_post':pa.array(t,type=pa.int64()),'weight':pa.array(c,type=pa.int64())}),weight)
    manifest=tmp_path/'raw.json'
    atomic_json(manifest,{'release':'male-cns:v1.0','files':[{'name':p.name,'path':str(p),'sha256':sha256(p),'schema':{'rows':len(s)}} for p in [ann,weight]]})
    output=tmp_path/'canonical'; result=canonicalize(manifest,output)
    assert result['retained_missing_type']==65
    assert result['exclusions']['removed_self_edges_at_threshold']==1
    assert result['exclusions']['excluded_noncurated_endpoints']==1
    assert result['exclusions']['curated_below_threshold']==1
    g=extract(output,64,101,smoke=True); assert len(g.ids)==64 and np.all(g.ids>=2**53)
    expected={(int(a),int(b)):v for a,b,v in zip(s,t,c) if a in set(g.ids) and b in set(g.ids) and a!=b and v>=5}
    actual={(int(g.ids[a]),int(g.ids[b])):int(v) for a,b,v in zip(g.source,g.target,g.counts)}
    assert actual==expected
    assert g.hash==extract(output,64,101,smoke=True).hash
    path=tmp_path/'graph.npz'; g.save(path); assert Graph.load(path).hash==g.hash


def test_ambiguous_duplicate_pairs_abort(tmp_path):
    ann=tmp_path/'body-annotations-test.feather'; weight=tmp_path/'connectome-weights-test.feather'
    feather.write_feather(pa.table({'bodyId':pa.array([1,2],type=pa.int64()),'status':['Traced']*2,'statusLabel':['Traced']*2,
                                  'type':[None]*2,'superclass':[None]*2,'class':[None]*2}),ann)
    feather.write_feather(pa.table({'body_pre':[1,1],'body_post':[2,2],'weight':[2,5]}),weight)
    manifest=tmp_path/'raw.json'; atomic_json(manifest,{'release':'male-cns:v1.0','files':[
        {'name':p.name,'path':str(p),'sha256':sha256(p),'schema':{'rows':2}} for p in [ann,weight]]})
    with pytest.raises(ValueError,match='Duplicate ordered pairs'): canonicalize(manifest,tmp_path/'out')


def test_count_initializations_equal_row_norms():
    import torch
    s=np.array([0,2,3,0,1,2]); t=np.array([1,1,1,3,3,3]); counts=np.array([5,10,20,6,8,7])
    models=[GraphRNN(4,3,s,t,counts=counts,initialization=k) for k in ['uniform','count','shuffled-count']]
    norm=models[0].dense_weight().norm(dim=1)
    for m in models[1:]: torch.testing.assert_close(m.dense_weight().norm(dim=1),norm)
    assert not torch.equal(models[0].theta,models[1].theta)
    assert not torch.equal(models[1].theta,models[2].theta)


def test_cli_synthetic_scientific_gate():
    with pytest.raises(PermissionError): main(['run','--config','pilot','--synthetic'])
    with pytest.raises(PermissionError): main(['run','--config','pilot','--synthetic','--smoke'])


def test_freeze_refuses_incomplete_development_and_pilot():
    with pytest.raises(ValueError): freeze_config(load_config('pilot'),{})
    with pytest.raises(ValueError): freeze_config(load_config('confirmation'),{'status':'incomplete'})


def test_final_evaluate_checks_freeze_before_reading_test(tmp_path,monkeypatch):
    import fly_connectome_lm.final_evaluation as final
    frozen={'config':load_config('confirmation'),'optional':[],'learning_rates':{'graph':.001}}
    p=tmp_path/'freeze.json'; atomic_json(p,frozen)
    def denied(*args): raise PermissionError('Invalid freeze')
    def never(*args): raise AssertionError('test loader called')
    monkeypatch.setattr(final,'validate_freeze',denied); monkeypatch.setattr(final,'FinalTestCorpus',never)
    with pytest.raises(PermissionError,match='Invalid freeze'): final_evaluate(p)


def test_final_incomplete_matrix_never_opens_test(tmp_path,monkeypatch):
    import fly_connectome_lm.final_evaluation as final
    p=tmp_path/'freeze.json'
    atomic_json(p,{'config':load_config('confirmation'),'optional':[],'learning_rates':{'graph':.001}})
    monkeypatch.setattr(final,'validate_freeze',lambda *args:None)
    monkeypatch.setattr(final,'ROOT',tmp_path)
    monkeypatch.setattr(final,'matrix',lambda *args:[{'run_id':'missing'}])
    def never(*args): raise AssertionError('Test loader called before complete frozen matrix')
    monkeypatch.setattr(final,'FinalTestCorpus',never)
    with pytest.raises(PermissionError,match='Incomplete frozen matrix'): final_evaluate(p)


def test_final_wrong_checkpoint_never_opens_test(tmp_path,monkeypatch):
    import torch
    import fly_connectome_lm.final_evaluation as final
    from fly_connectome_lm.util import digest
    config=load_config('confirmation'); p=tmp_path/'freeze.json'
    atomic_json(p,{'config':config,'optional':[],'learning_rates':{'graph':.001},'code_hash':'same-code'})
    run=tmp_path/'runs/wrong'; run.mkdir(parents=True)
    atomic_json(run/'manifest.json',{'status':'complete','code_hash':'same-code','signature':'correct-run'})
    atomic_json(run/'result.json',{'config_hash':digest(config),'final_step':20000,'selected_checkpoint_step':1000})
    torch.save({'signature':'different-run','code_hash':'same-code','step':1000},run/'best.pt')
    monkeypatch.setattr(final,'validate_freeze',lambda *args:None); monkeypatch.setattr(final,'ROOT',tmp_path)
    monkeypatch.setattr(final,'matrix',lambda *args:[{'run_id':'wrong','config':config}])
    def never(*args): raise AssertionError('Test loader called for mismatched checkpoint')
    monkeypatch.setattr(final,'FinalTestCorpus',never)
    with pytest.raises(PermissionError,match='Checkpoint does not match'): final_evaluate(p)
