import pytest
from flycodes.syntax_audit import interpret, protected_tokens
from flycodes.judge import evaluate_local


@pytest.mark.parametrize('code', [
    'def solve(nums):\n    return sum(nums):\n',
    'def solve(nums)\nreturn sum(nums\n',
    'def solve(nums):\n    return sum(nums]\n',
])
def test_recovers_arithmetic_without_changing_logic(code):
    result = interpret(code)
    assert result['status'] == 'repaired'
    assert protected_tokens(code) == protected_tokens(result['code'])
    assert evaluate_local(result['code'], [{'args': [[2, 3]], 'expected': 5}])['passed']


def test_does_not_correct_wrong_constant():
    result = interpret('def solve(nums):\n    return sum(nums) + -1:\n')
    assert result['status'] == 'repaired'
    assert not evaluate_local(result['code'], [{'args': [[2, 3]], 'expected': 11}])['passed']


@pytest.mark.parametrize('code', [
    'def solve(nums):\n    return [x * - for x in nums]\n',
    'def solve(a, a):\n    return a\n',
    "def solve(nums):\n    return 'unfinished\n",
    'def solve(nums):\n    for x in nums:\n    return x\n',
    'def solve(nums):\n    return in nums\n',
])
def test_refuses_to_invent_algorithm_or_parameters(code):
    assert interpret(code)['status'] == 'unresolved'


def test_preserves_valid_wrong_logic_and_string_contents():
    code = "def solve(nums):\n    return 'brackets ] and colon :'\n"
    result = interpret(code)
    assert result['status'] == 'already_valid' and result['code'] == code


def test_keeps_original_return_order_and_all_statements():
    code = 'def solve(nums):\n    return sum(nums):\n    return sum(nums) + 6\n'
    result = interpret(code)
    assert result['status'] == 'repaired'
    assert result['code'].count('return') == 2
    assert not evaluate_local(result['code'], [{'args': [[2]], 'expected': 8}])['passed']
