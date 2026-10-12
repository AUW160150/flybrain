"""Versioned code curriculum with official MBPP splits and explicit subset exclusions."""
from __future__ import annotations
import ast
import hashlib
import json
import random
from collections import Counter
from pathlib import Path
from .common import ROOT, now, sha256, write_json, read_json
from .judge import judge

DIRECTORY=ROOT/'data/curriculum-v2'

def prompt(p):
    return p['statement']+'\nPython:\n'

def json_types(x):
    if type(x) in (str,int,float,bool,type(None)):return True
    if type(x) is list:return all(json_types(y) for y in x)
    if type(x) is dict:return all(type(k) is str and json_types(v) for k,v in x.items())
    return False

def adapt_mbpp(row):
    if row.get('test_setup_code','').strip():raise ValueError('test_setup_required')
    tree=ast.parse(row['code'])
    if len(tree.body)!=1 or not isinstance(tree.body[0],ast.FunctionDef):raise ValueError('requires_imports_or_multiple_definitions')
    fn=tree.body[0];old=fn.name
    if any(isinstance(x,ast.Name) and x.id==old for x in ast.walk(fn)):
        raise ValueError('recursion_or_function_reference')
    fn.name='solve'
    code=ast.unparse(tree)+'\n'
    if len(code)>1600:raise ValueError('reference_over_length_limit')
    cases=[]
    for test in row['test_list']:
        node=ast.parse(test).body[0]
        if not isinstance(node,ast.Assert) or not isinstance(node.test,ast.Compare):raise ValueError('unsupported_assertion_form')
        compare=node.test
        if len(compare.ops)!=1 or not isinstance(compare.ops[0],ast.Eq):raise ValueError('non_equality_assertion')
        call=compare.left
        if not isinstance(call,ast.Call) or not isinstance(call.func,ast.Name) or call.func.id!=old or call.keywords:
            raise ValueError('nonliteral_test_call')
        args=[ast.literal_eval(x) for x in call.args];expected=ast.literal_eval(compare.comparators[0])
        if not json_types(args) or not json_types(expected):raise ValueError('non_json_test_types')
        cases.append(dict(args=args,expected=expected))
    result=judge(code,cases)
    if not result.get('passed'):raise ValueError('reference_'+result['status'])
    params=', '.join(a.arg for a in fn.args.args)
    return dict(id=f'mbpp-{row["task_id"]}',family='mbpp',source='MBPP',source_task_id=row['task_id'],
                statement=f'solve({params}): '+row['text'],solution=code,cases=cases,
                original_function=old,reference_transform='AST rename entry function to solve; ast.unparse formatting')

def synthetic_curriculum():
    """Small verified exercises; variants share algorithm templates and are labeled accordingly."""
    train=[];validation=[];transfer=[]
    constants_train=[-5,-3,-1,0,1,2,3,5,7,10]
    constants_validation=[-4,4]
    constants_transfer=[-2,6,9]
    def add(split,family,k,words,expression,oracle):
        examples=[[-6,-1,0,2,7],[],[3,3,-2],[0],[10,-10,4]]
        p=dict(id=f'curr-{family}-{k}',family=family,source='authored_parameter_curriculum',
               statement=f'solve(nums): {words}',solution=f'def solve(nums):\n    return {expression}\n',
               cases=[dict(args=[x],expected=oracle(x)) for x in examples])
        split.append(p)
    for split,constants in [(train,constants_train),(validation,constants_validation),(transfer,constants_transfer)]:
        for k in constants:
            add(split,'add-each',k,f'Add {k} to every integer in nums. Return the new list.',f'[x + {k} for x in nums]',lambda a,k=k:[x+k for x in a])
            add(split,'multiply-each',k,f'Multiply every integer in nums by {k}. Return the new list.',f'[x * {k} for x in nums]',lambda a,k=k:[x*k for x in a])
            add(split,'keep-above',k,f'Keep only integers strictly greater than {k}, in original order.',f'[x for x in nums if x > {k}]',lambda a,k=k:[x for x in a if x>k])
            add(split,'keep-below',k,f'Keep only integers strictly less than {k}, in original order.',f'[x for x in nums if x < {k}]',lambda a,k=k:[x for x in a if x<k])
            add(split,'count-above',k,f'Count the integers strictly greater than {k}.',f'sum(x > {k} for x in nums)',lambda a,k=k:sum(x>k for x in a))
            add(split,'sum-above',k,f'Sum only the integers strictly greater than {k}.',f'sum(x for x in nums if x > {k})',lambda a,k=k:sum(x for x in a if x>k))
            add(split,'contains-number',k,f'Return whether nums contains the integer {k}.',f'{k} in nums',lambda a,k=k:k in a)
            add(split,'count-number',k,f'Count how often the integer {k} occurs in nums.',f'nums.count({k})',lambda a,k=k:a.count(k))
            add(split,'offset-sum',k,f'Add {k} to the sum of all numbers in nums.',f'sum(nums) + {k}',lambda a,k=k:sum(a)+k)
            add(split,'offset-length',k,f'Add {k} to the number of elements in nums.',f'len(nums) + {k}',lambda a,k=k:len(a)+k)
    # Additional distinct code patterns; do not call these independent real-world tasks.
    from .corpus import TRAIN
    for p in TRAIN:train.append({**p,'id':'curr-base-'+p['id'],'source':'original_pilot_training'})
    for split in (train,validation,transfer):
        for p in split:
            if not judge(p['solution'],p['cases']).get('passed'):raise ValueError('Authored reference failed: '+p['id'])
    return train,validation,transfer

def prepare():
    DIRECTORY.mkdir(exist_ok=True,parents=True)
    raw=ROOT/'data/mbpp/mbpp.jsonl'
    rows=[json.loads(line) for line in raw.read_text().splitlines()]
    splits={'train':[],'validation':[],'test':[]};excluded=[]
    for row in rows:
        id=row['task_id']
        if id<=10:continue
        split='test' if id<=510 else 'validation' if id<=600 else 'train'
        try:splits[split].append(adapt_mbpp(row))
        except Exception as exc:excluded.append(dict(id=id,split=split,reason=str(exc)[:180]))
    # Exact canonical-code and normalized-description overlap: test > validation > train.
    seen_code=set();seen_text=set();dedup={k:[] for k in splits}
    for split in ['test','validation','train']:
        for p in sorted(splits[split],key=lambda x:x['source_task_id']):
            code=p['solution'];text=' '.join(p['statement'].lower().split())
            if code in seen_code or text in seen_text:
                excluded.append(dict(id=p['source_task_id'],split=split,reason='exact_cross_or_within_split_duplicate'));continue
            seen_code.add(code);seen_text.add(text);dedup[split].append(p)
    synth_train,synth_val,transfer=synthetic_curriculum()
    # MBPP can overlap elementary authored examples; holdout priority is enforced again.
    protected={p['solution'] for p in dedup['test']+dedup['validation']}
    synth_train=[p for p in synth_train if p['solution'] not in protected]
    split_data=dict(train=dedup['train']+synth_train,validation=dedup['validation']+synth_val,
                    test=dedup['test'],transfer=transfer)
    manifests={}
    for name,items in split_data.items():
        path=DIRECTORY/f'{name}.json';write_json(path,items)
        manifests[name]=dict(count=len(items),sha256=sha256(path),sources=dict(Counter(p['source'] for p in items)))
    write_json(DIRECTORY/'exclusions.json',excluded)
    manifest=dict(created_at=now(),protocol='curriculum-v2',source_url='https://raw.githubusercontent.com/google-research/google-research/master/mbpp/mbpp.jsonl',
        source_sha256=sha256(raw),raw_records=len(rows),license='CC BY 4.0',attribution='Austin et al., Google Research, Mostly Basic Python Problems (2021)',
        official_splits={'train':'601..974','validation':'511..600','test':'11..510','unused_prompting':'1..10'},
        splits=manifests,mbpp_retained={k:len(v) for k,v in dedup.items()},exclusion_reasons=dict(Counter(x['reason'] for x in excluded)),
        exclusion_policy='one renamed function; literal JSON-compatible equality tests; bounded judge supports and passes reference; max reference 1600 chars; exact code/text dedup with test priority',
        benchmark_scope='filtered MBPP subset, not standard full-MBPP score; no claim of semantic decontamination',
        transfer_scope='unseen constants in seen authored templates; interpolation, not new algorithm families')
    write_json(DIRECTORY/'manifest.json',manifest)
    return manifest

def load(split):
    m=read_json(DIRECTORY/'manifest.json')
    path=DIRECTORY/f'{split}.json'
    if sha256(path)!=m['splits'][split]['sha256']:raise ValueError('Corpus hash mismatch')
    return read_json(path)
