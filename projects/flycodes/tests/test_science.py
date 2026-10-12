import numpy as np
import pytest
import scipy.sparse as sp
import torch
import pyarrow as pa
import pyarrow.feather as feather
from flycodes.connectome import prepare, load_graph, ANNOTATIONS, WEIGHTS
from flycodes.corpus import TRAIN, VALIDATION, TEST, prompt
from flycodes.experiment import transformer_batch, summarize
from flycodes.models import Reservoir, TinyTransformer
from flycodes.judge import judge

@pytest.mark.parametrize('problem', TRAIN+VALIDATION, ids=lambda x:x['id'])
def test_authored_training_examples_execute(problem):
    assert judge(problem['solution'],problem['cases'])['passed'] is True

def test_graph_preserves_direction_weak_edges_and_loops(tmp_path):
    raw=tmp_path/'raw';raw.mkdir()
    feather.write_feather(pa.table(dict(bodyId=[10,20,30,40],status=['Traced','Traced','Glia','Traced'],
                         type=['a','b','g','isolated'],superclass=['x']*4)),raw/ANNOTATIONS)
    feather.write_feather(pa.table(dict(body_pre=[10,20,30],body_post=[20,20,10],weight=[1,2,99])),raw/WEIGHTS)
    m=prepare(raw,tmp_path/'graph');W,ids,_=load_graph(tmp_path/'graph')
    assert ids.tolist()==[10,20,40]
    assert W.toarray().tolist()==[[0,0,0],[1,2,0],[0,0,0]]
    assert m['isolated_neurons']==1 and m['self_edges_retained']==1
    with pytest.raises(ValueError):W.data[0]=6
    (tmp_path/'graph/counts.npy').write_bytes(b'changed')
    with pytest.raises(ValueError,match='integrity'):load_graph(tmp_path/'graph')

def test_recurrence_changes_computation_without_mutating_graph():
    W=sp.csr_matrix(np.array([[0,2,0],[3,0,1],[0,4,0]],np.float32));before=W.toarray().copy()
    r=Reservoir(W,features=4);z=Reservoir(W,features=4,recurrence=False)
    for token in b'hello':a=r.step(token);b=z.step(token)
    assert not np.allclose(a,b)
    np.testing.assert_array_equal(W.toarray(),before)
    r.reset();first=r.step(100);r.reset();np.testing.assert_array_equal(first,r.step(100))

def test_solution_only_loss_and_disjoint_task_families():
    _,y=transformer_batch(TRAIN)
    assert int((y!=-100).sum())==sum(len(p['solution'].encode())+1 for p in TRAIN)
    assert not ({p['family'] for p in TRAIN}&{p['family'] for p in TEST})
    for i,p in enumerate(TRAIN):assert (y[i,:len(prompt(p).encode())-1]==-100).all()

def test_transformer_cannot_see_future_bytes():
    torch.set_num_threads(2);torch.manual_seed(1)
    m=TinyTransformer(width=16,layers=1).eval()
    a=torch.tensor([[1,2,3,4]]);b=torch.tensor([[1,2,8,9]])
    with torch.no_grad():
        np.testing.assert_allclose(m(a)[0,:2].numpy(),m(b)[0,:2].numpy(),atol=1e-6)

@pytest.mark.parametrize('source,status',[
    ('def solve(x):\n    return x + 1\n','passed'),
    ('def solve(x):\n    return x - 1\n','wrong_answer'),
    ('def solve(:','syntax_error'),
    ('import os\ndef solve(x):\n    return 3','unsupported'),
    ('def solve(x):\n    return open("/etc/passwd").read()','unsupported'),
    ('def solve(x):\n    return x.__class__','unsupported'),
    ('def solve(x):\n    while True:\n        pass','budget_exceeded'),
    ('def solve(x):\n    return [0] * 1000000000','budget_exceeded'),
])
def test_judge_outcomes(source,status):
    assert judge(source,[dict(args=[2],expected=3)])['status']==status

def test_stack_and_loops_supported():
    code='''def solve(s):
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    for c in s:
        if c in '([{':
            stack.append(c)
        else:
            if not stack or stack.pop() != pairs[c]:
                return False
    return not stack
'''
    assert judge(code,TEST[3]['cases'])['passed']

def test_unmeasured_is_not_zero():
    assert summarize([])['pass_at_1'] is None
    assert summarize([dict(judgement=dict(passed=None))])['pass_at_1'] is None
