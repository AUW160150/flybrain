import copy
import math
from pathlib import Path
import numpy as np
import pytest
import torch
import torch.nn.functional as F
from fly_connectome_lm.models import GraphRNN,build,accounting,CONDITIONS,choose_gru
from fly_connectome_lm.graph_extract import Graph,synthetic_graph,assert_scientific
from fly_connectome_lm.graph_controls import rewire,random_density,degrees,InvalidControl
from fly_connectome_lm.text_data import split_offsets,evaluation_blocks,WindowSampler,prepare_text,DevelopmentCorpus,duplicate_spans
from fly_connectome_lm.evaluate import metrics,evaluate,FinalTestCorpus,ngram_references
from fly_connectome_lm.train import train_run
from fly_connectome_lm.statistics import paired_effects
from fly_connectome_lm.util import load_config,setup

@pytest.fixture(autouse=True)
def deterministic_cpu(): setup('cpu',2)

def tiny(execution='scatter'):
    return GraphRNN(4,3,np.array([0,2,1,3,0]),np.array([1,1,2,0,3]),execution=execution).double()

def test_source_target_orientation():
    m=GraphRNN(3,2,np.array([0]),np.array([1])).double()
    with torch.no_grad(): m.theta.fill_(2); m.input.weight.zero_(); m.bias.zero_()
    h=torch.tensor([[.25,0.,0.]],dtype=torch.float64)
    _,states=m(torch.zeros((1,1),dtype=torch.long),state=h,return_states=True)
    expected=torch.tensor([[[.125,.5*math.tanh(.5),0.]]],dtype=torch.float64)
    torch.testing.assert_close(states,expected)
    assert m.dense_weight()[1,0]==2 and m.dense_weight()[0,1]==0

@pytest.mark.parametrize('execution',['dense','scatter','sparse'])
def test_dense_forward_and_backward(execution):
    m=tiny(execution); reference=copy.deepcopy(m)
    x=torch.tensor([[1,2,3,4],[4,5,6,1]]); y=torch.tensor([[2,3,4,5],[5,6,1,7]])
    logits,states=m(x,return_states=True); ref,refstates=reference.dense_reference(x)
    loss=F.cross_entropy(logits.flatten(0,1),y.flatten()); ref_loss=F.cross_entropy(ref.flatten(0,1),y.flatten())
    loss.backward(); ref_loss.backward()
    torch.testing.assert_close(logits,ref,rtol=1e-11,atol=1e-12)
    torch.testing.assert_close(states,refstates,rtol=1e-11,atol=1e-12)
    torch.testing.assert_close(loss,ref_loss,rtol=1e-12,atol=1e-12)
    for p,q in zip(m.parameters(),reference.parameters()): torch.testing.assert_close(p.grad,q.grad,rtol=1e-10,atol=1e-12)

def test_absent_edges_and_learned_core():
    m=tiny(); optimizer=torch.optim.AdamW(m.parameters(),lr=.01); before=m.theta.detach().clone()
    mask=torch.zeros((m.n,m.n),dtype=torch.bool); mask[m.target,m.source]=True
    for _ in range(3):
        optimizer.zero_grad(); loss=m(torch.tensor([[1,2,3]])).square().mean(); loss.backward()
        assert m.theta.grad.norm()>0; optimizer.step()
        assert torch.count_nonzero(m.dense_weight()[~mask])==0
    assert not torch.equal(before,m.theta)
    assert optimizer.state[m.theta]['exp_avg'].numel()==m.theta.numel()
    assert m.theta.numel()==5

def test_complete_node_relabeling():
    m=tiny(); permutation=torch.tensor([2,0,3,1])
    q=GraphRNN(4,3,permutation[m.source].numpy(),permutation[m.target].numpy()).double()
    with torch.no_grad():
        q.embedding.weight.copy_(m.embedding.weight); q.output.load_state_dict(m.output.state_dict())
        q.input.weight[permutation]=m.input.weight; q.readout.weight[:,permutation]=m.readout.weight
        q.bias[permutation]=m.bias
        lookup={(int(permutation[s]),int(permutation[t])):v.item() for s,t,v in zip(m.source,m.target,m.theta)}
        q.theta.copy_(torch.tensor([lookup[(int(s),int(t))] for s,t in zip(q.source,q.target)],dtype=torch.float64))
    x=torch.tensor([[1,3,2,4]]); a,ha=m(x,return_states=True); b,hb=q(x,return_states=True)
    torch.testing.assert_close(a,b,atol=1e-12,rtol=1e-11); torch.testing.assert_close(ha,hb[:,:,permutation])

def test_rewiring_exact_degrees_and_initial_matching():
    g=synthetic_graph(64,synthetic=True,smoke=True); r=rewire(g,43)
    assert np.array_equal(g.ids,r.ids) and len(g.source)==len(r.source)
    assert not np.array_equal(g.source,r.source)
    for a,b in zip(degrees(g),degrees(r)): np.testing.assert_array_equal(a,b)
    info=r.metadata['randomization']; assert info['accepted_swaps']==20*len(g.source)
    assert info['proposals']<=500*len(g.source) and info['partners_changed']
    a=GraphRNN(64,16,g.source,g.target,seed=1); b=GraphRNN(64,16,r.source,r.target,seed=1)
    torch.testing.assert_close(a.theta,b.theta,rtol=0,atol=0)
    for name,p in a.named_parameters(): torch.testing.assert_close(p,dict(b.named_parameters())[name],rtol=0,atol=0)
    assert accounting(a)==accounting(b)
    dense=random_density(g,45); assert len(dense.source)==len(g.source)
    assert not np.array_equal(degrees(g)[0],degrees(dense)[0])

def test_invalid_null_does_not_fall_back():
    n=5; s,t=np.where(~np.eye(n,dtype=bool)); g=Graph(np.arange(n),s,t,np.ones(len(s),dtype=int),{})
    with pytest.raises(InvalidControl) as exc: rewire(g,1)
    assert not exc.value.diagnostic['valid']

@pytest.mark.parametrize('condition',CONDITIONS+['TRANSFORMER','FROZEN-FLY'])
def test_parameter_accounting_active_no_padding_causality(condition):
    g=synthetic_graph(64,synthetic=True,smoke=True); config=load_config('smoke')
    m=build(condition,g,config,1); a=build('FLY-TOPOLOGY',g,config,1)
    count=accounting(m)['active_trainable_parameters']; target=accounting(a)['active_trainable_parameters']
    if condition in ['PARAMETER-MATCHED-GRU','TRANSFORMER']: assert abs(count-target)/target<=.05
    elif condition in ['NO-CROSS-NODE-RECURRENCE','FROZEN-FLY']: assert count<target
    else: assert count==target
    x=torch.tensor([[1,2,3,4,5]]); y=x.clone(); y[:,3:]=9
    torch.testing.assert_close(m(x)[:,:3],m(y)[:,:3],atol=1e-6,rtol=1e-5)
    m(x).sum().backward()
    assert all(p.grad is not None for p in m.parameters() if p.requires_grad)
    torch.testing.assert_close(m(x),m(x))  # Default state resets on every call.

def test_byte_splits_windows_mask_and_metrics(tmp_path):
    data=bytes(range(128))*16; raw=tmp_path/'raw'; raw.write_bytes(data)
    out=tmp_path/'corpus'; manifest=prepare_text(raw,out,{'synthetic_text':True}); corpus=DevelopmentCorpus(out)
    offsets=split_offsets(len(data)); assert offsets['train']==(0,1843)
    assert (out/'test.bin').read_bytes()==data[offsets['test'][0]:]
    sampler=WindowSampler(corpus.train,32,10,1)
    x,y=sampler.next(); assert torch.equal(x[:,1:],y[:,:-1]); assert sampler.draws==10
    for name in ['train','validation','test']:
        split=np.frombuffer(data[offsets[name][0]:offsets[name][1]],dtype=np.uint8)
        scored=[]
        for x,y,mask in evaluation_blocks(split,32,batch=2):
            assert torch.all(x[~mask]==0) and torch.all(y[~mask]==0)
            scored.extend(y[mask].tolist())
        assert scored==split[1:].tolist()
    encoded='fly 🪰 café'.encode('utf-8'); assert bytes(np.frombuffer(encoded,dtype=np.uint8)).decode('utf-8')=='fly 🪰 café'
    metric=metrics(10*math.log(256),10,1); assert metric['bpb']==8 and metric['byte_perplexity']==256
    with pytest.raises(PermissionError): corpus._read_development('test')
    with pytest.raises(PermissionError): FinalTestCorpus(out,{'profile':'pilot'},'wrong')

def test_evaluation_scored_exactly_and_reset():
    data=np.arange(91,dtype=np.uint8); m=tiny('dense').float()
    a=evaluate(m,data,32,batch=1); b=evaluate(m,data,32,batch=3)
    assert a['scored_bytes']==90; assert abs(a['bpb']-b['bpb'])<1e-6
    first=m(torch.tensor([[1,2,3]])); m(torch.tensor([[6,7,8]])); torch.testing.assert_close(first,m(torch.tensor([[1,2,3]])))

def test_duplicate_spans_exact_without_source_text():
    shared=bytes(range(256))+b'abc'
    result=duplicate_spans({'a':b'X'+shared+b'Q','b':b'Z'+shared+b'R'})
    spans=result['a:b']['spans']; assert len(spans)==1 and spans[0]['length']==259
    assert spans[0]['a_offset']==spans[0]['b_offset']==1

def test_training_never_opens_test_and_resume_equivalence(tmp_path,monkeypatch):
    raw=tmp_path/'raw'; raw.write_bytes(bytes(range(31))*100); out=tmp_path/'corpus'
    prepare_text(raw,out,{}); original_read=Path.read_bytes
    def guarded(path):
        if path.name=='test.bin': raise AssertionError('TEST OPENED')
        return original_read(path)
    monkeypatch.setattr(Path,'read_bytes',guarded)
    corpus=DevelopmentCorpus(out); config=load_config('smoke')
    config.update(updates=4,validate_every=2,context=8,batch=2,d=3)
    metadata=dict(training_seed=1,condition='FLY-TOPOLOGY',sampling_seed=101,synthetic=True,graph_hash='test')
    a=tiny('dense').float(); b=copy.deepcopy(a)
    train_run(a,corpus,config,tmp_path/'full',metadata)
    train_run(b,corpus,config,tmp_path/'resumed',metadata,stop_after=2)
    train_run(b,corpus,config,tmp_path/'resumed',metadata,resume=True)
    full=torch.load(tmp_path/'full/final.pt',weights_only=False); resumed=torch.load(tmp_path/'resumed/final.pt',weights_only=False)
    for k in full['model']: torch.testing.assert_close(full['model'][k],resumed['model'][k],atol=0,rtol=0)
    for p,state in full['optimizer']['state'].items():
        for key,val in state.items(): torch.testing.assert_close(val,resumed['optimizer']['state'][p][key],atol=0,rtol=0)
    assert full['sampler']==resumed['sampler']
    torch.testing.assert_close(full['rng']['torch'],resumed['rng']['torch'],atol=0,rtol=0)
    assert [v['train_nll'] for v in full['history']]==[v['train_nll'] for v in resumed['history']]
    assert full['best_step']==resumed['best_step']

def test_tiny_synthetic_overfit():
    m=GraphRNN(8,8,np.arange(8),np.roll(np.arange(8),1),seed=3)
    x=torch.tensor([[65,66]*8,[66,65]*8]); y=torch.tensor([[66,65]*8,[65,66]*8])
    opt=torch.optim.AdamW(m.parameters(),lr=.01,weight_decay=0.)
    before=m.theta.detach().clone()
    for _ in range(300):
        opt.zero_grad(); loss=F.cross_entropy(m(x).flatten(0,1),y.flatten()); loss.backward()
        torch.nn.utils.clip_grad_norm_(m.parameters(),1.); opt.step()
    assert loss.item()<.05 and not torch.equal(m.theta,before)

def test_synthetic_gate():
    with pytest.raises(PermissionError): synthetic_graph()
    with pytest.raises(PermissionError): synthetic_graph(synthetic=True)
    g=synthetic_graph(synthetic=True,smoke=True)
    for name in ['pilot','confirmation','replication']:
        with pytest.raises(PermissionError): assert_scientific(g,name)

def test_paired_seed_bootstrap_not_reused_fly():
    records=[]
    for seed in [11,22,33,44,55]:
        records.append(dict(sampling_seed=101,training_seed=seed,condition='FLY-TOPOLOGY',bpb=4.,null_index=0))
        records.extend(dict(sampling_seed=101,training_seed=seed,condition='DEGREE-REWIRED',bpb=4.1,null_index=i) for i in [1,2,3])
    stats=paired_effects(records)
    assert len(stats['pairs'])==5 and stats['per_graph']['101']['training_seed_count']==5
    assert stats['per_graph']['101']['mean_delta']==pytest.approx(.1)

@pytest.mark.parametrize('device',['cpu','cuda','mps'])
def test_device_forward_backward(device):
    if device=='cuda' and not torch.cuda.is_available(): pytest.skip('CUDA unavailable')
    if device=='mps' and not torch.backends.mps.is_available(): pytest.skip('MPS unavailable in this process')
    setup(device,2); m=tiny('dense').float().to(device)
    y=m(torch.tensor([[1,2,3]],device=device)); y.sum().backward()
    assert torch.isfinite(y).all() and m.theta.grad.norm()>0
