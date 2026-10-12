"""Post-run test-adequacy audit. Rejudge saved code; never regenerate or retrain."""
from itertools import product
from .common import read_json, write_json, sha256, now
from .judge import judge


def stronger_cases(problem):
    if problem.get('source') != 'authored_parameter_curriculum':
        return problem['cases']
    family = problem['family']
    k = int(problem['id'][len('curr-' + family + '-'):])
    def oracle(nums):
        if family == 'add-each': return [x + k for x in nums]
        if family == 'multiply-each': return [x * k for x in nums]
        if family == 'keep-above': return [x for x in nums if x > k]
        if family == 'keep-below': return [x for x in nums if x < k]
        if family == 'count-above': return sum(x > k for x in nums)
        if family == 'sum-above': return sum(x for x in nums if x > k)
        if family == 'contains-number': return k in nums
        if family == 'count-number': return nums.count(k)
        if family == 'offset-sum': return sum(nums) + k
        if family == 'offset-length': return len(nums) + k
        raise ValueError('No independent audit oracle for ' + family)
    domain = sorted(set(range(-8, 13)) | {k - 1, k, k + 1})
    inputs = [[]] + [[x] for x in domain] + [list(pair) for pair in product(domain, repeat=2)]
    inputs += [[k, k, k], [k - 1, k, k + 1, k], domain, domain[::-1]]
    cases = list(problem['cases'])
    seen = {tuple(c['args'][0]) for c in cases}
    for nums in inputs:
        if tuple(nums) not in seen:
            cases.append(dict(args=[nums], expected=oracle(nums)))
            seen.add(tuple(nums))
    return cases


def audit_run(run):
    from .curriculum_experiment import summary
    config = read_json(run / 'config.json')
    original_hashes = read_json(run / 'artifacts.json')
    for filename, expected in original_hashes.items():
        if sha256(run / filename) != expected:
            raise ValueError('Original artifact changed: ' + filename)
    audit = run / 'test-adequacy-audit'
    audit.mkdir(exist_ok=True)
    cases_by_id = {}
    for split in ['train', 'transfer']:
        for p in read_json(run / f'corpus-{split}.json'):
            if p['source'] == 'authored_parameter_curriculum':
                cases = stronger_cases(p)
                if not judge(p['solution'], cases).get('passed'):
                    raise ValueError('Audit reference failed: ' + p['id'])
                cases_by_id[p['id']] = cases
    write_json(audit / 'cases.json', cases_by_id)
    scores = []
    for arm in ['fly', 'no-recurrence']:
        for seed in config['seeds']:
            name = f'{arm}-s{seed}'
            for split in ['transfer', 'train-reproduction']:
                source = run / f'{name}-{split}-evaluation.json'
                record = read_json(source)
                before = record['summary']
                for row in record['results']:
                    cases = cases_by_id.get(row['problem']['id'])
                    if cases is not None:
                        row['original_judgement'] = row['judgement']
                        row['judgement'] = judge(row['code'], cases)
                        row['test_basis'] = 'Post-run boundary and exhaustive short-list audit; no regeneration'
                record.update(original_summary=before, summary=summary(record['results']),
                              original_evaluation_sha256=sha256(source), posthoc_test_audit=True)
                write_json(audit / source.name, record)
                scores.append(dict(arm=name, split=split, original=before, audited=record['summary']))
    receipt = dict(created_at=now(), reason='Original fixed inputs missed threshold boundaries and target integers, allowing incorrect constants to pass.',
                   methodology='All integer lists of length 0..2 over -8..12, target and neighbors, duplicates, longer ordered/reversed lists, plus every original case. Independent direct Python oracles.',
                   scope='Authored parameter templates only. MBPP supplied tests unchanged. Post hoc, not preregistered. No model updates or regenerated candidates.',
                   reference='https://arxiv.org/abs/2305.01210', scores=scores,
                   hashes={p.name: sha256(p) for p in sorted(audit.glob('*.json')) if p.name != 'manifest.json'})
    write_json(audit / 'manifest.json', receipt)
    return receipt
