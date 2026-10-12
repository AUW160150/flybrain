import numpy as np
import scipy.sparse as sp
import torch
from flycodes.curriculum_model import Tokenizer,CodingReservoir,estimate_radius
from flycodes.curriculum_data import load,adapt_mbpp
from flycodes.curriculum_experiment import summary
from flycodes.judge import judge

def test_lexical_codec_roundtrip_unknown_unicode_and_whitespace():
    tok=Tokenizer.fit(['def solve(nums):\n    return sum(nums)\n'])
    for text in ['new_identifier_983', 'héllo 雪 😀', '\n\t  \r\n','', 'def solve(nums):\n    return 1234\n']:
        assert tok.decode(tok.encode(text))==text
    assert b'new_identifier_983' not in tok.lookup

def test_prompt_context_does_not_contain_future_answer():
    torch.set_num_threads(2)
    W=sp.csr_matrix(np.array([[0,2,0],[1,0,1],[0,2,0]],np.float32))
    r=CodingReservoir(W,300,features=8,radius=2,target_radius=.9)
    before=W.toarray().copy();context=r.encode_prompt([1,2,3]);saved=context.copy()
    feature=r.feature(context,0)
    r.step(100)
    np.testing.assert_array_equal(context,saved)
    np.testing.assert_array_equal(r.feature(context,1)[8:24],saved)
    assert not np.array_equal(feature[:8],r.feature(context,1)[:8])
    np.testing.assert_array_equal(W.toarray(),before)

def test_radius_matches_known_graph():
    W=sp.csr_matrix(np.array([[2,1],[1,2]],np.float32))
    result=estimate_radius(W)
    assert abs(result['radius']-3)<1e-5 and result['relative_residual']<1e-5

def test_reference_adapter_renames_only_function():
    source=dict(task_id=900,text='Return the sum.',code='def add(a, b):\n    return a+b\n',test_setup_code='',
                test_list=['assert add(2, 3) == 5'])
    p=adapt_mbpp(source)
    assert p['solution'].startswith('def solve(a, b):') and judge(p['solution'],p['cases'])['passed']

def test_corpus_split_ids_and_code_disjoint():
    train=load('train');validation=load('validation');test=load('test');transfer=load('transfer')
    assert len(train)>200
    assert all(p['source_task_id']>=601 for p in train if p['source']=='MBPP')
    assert all(511<=p['source_task_id']<=600 for p in validation if p['source']=='MBPP')
    assert all(11<=p['source_task_id']<=510 for p in test)
    assert not ({p['solution'] for p in train}&{p['solution'] for p in test})
    assert not ({p['id'] for p in train}&{p['id'] for p in validation+test+transfer})

def test_summary_does_not_count_judge_failure_as_wrong_answer():
    rows=[dict(judgement=dict(status='judge_error',passed=None),latency_seconds=1)]
    s=summary(rows)
    assert s['pass_at_1'] is None and s['total']==0 and s['attempted']==1
