from flycodes.curriculum_audit import stronger_cases
from flycodes.curriculum_data import synthetic_curriculum
from flycodes.judge import evaluate_local


def test_boundary_audit_accepts_references_and_rejects_wrong_constants():
    _, _, transfer = synthetic_curriculum()
    for p in transfer:
        cases = stronger_cases(p)
        assert len(cases) > 460
        assert evaluate_local(p['solution'], cases)['passed'], p['id']
        k = int(p['id'][len('curr-' + p['family'] + '-'):])
        wrong = p['solution'].replace(str(k), str(k + 1))
        assert not evaluate_local(wrong, cases)['passed'], p['id']


def test_original_false_positives_are_rejected():
    _, _, transfer = synthetic_curriculum()
    by_id = {p['id']: p for p in transfer}
    for id, code in [
        ('curr-keep-below--2', 'def solve(nums):\n    return [x for x in nums if x < -3]'),
        ('curr-count-number-6', 'def solve(nums):\n    return nums.count(-5)'),
        ('curr-count-number-9', 'def solve(nums):\n    return nums.count(-5)'),
    ]:
        p = by_id[id]
        assert evaluate_local(code, p['cases'])['passed']
        assert not evaluate_local(code, stronger_cases(p))['passed']
