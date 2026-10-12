"""Original, deliberately small exercises. No scraped LeetCode content or model answers."""
import hashlib
import json

INSTRUCTION = ('Write Python code only. Define solve with the specified arguments. '
               'Use basic Python, no imports, classes, annotations or recursion.\n')

def item(id, family, prompt, code, cases):
    return dict(id=id, family=family, statement=prompt, solution=code, cases=[dict(args=a, expected=e) for a,e in cases])

TRAIN = [
 item('sum-two','arithmetic','solve(a, b): return the sum of two integers.','def solve(a, b):\n    return a + b\n', [([2,3],5),([-2,2],0)]),
 item('subtract','arithmetic','solve(a, b): return a minus b.','def solve(a, b):\n    return a - b\n', [([2,3],-1)]),
 item('multiply','arithmetic','solve(a, b): return their product.','def solve(a, b):\n    return a * b\n', [([2,3],6)]),
 item('absolute','scalar','solve(x): return the absolute value.','def solve(x):\n    return abs(x)\n', [([-2],2)]),
 item('largest','reduction','solve(nums): return the largest integer in a nonempty list.','def solve(nums):\n    return max(nums)\n', [([[2,3]],3)]),
 item('smallest','reduction','solve(nums): return the smallest integer in a nonempty list.','def solve(nums):\n    return min(nums)\n', [([[2,3]],2)]),
 item('list-sum','reduction','solve(nums): return the sum of all integers.','def solve(nums):\n    return sum(nums)\n', [([[2,3]],5)]),
 item('length','length','solve(nums): return the number of elements.','def solve(nums):\n    return len(nums)\n', [([[2,3]],2)]),
 item('reverse','sequence','solve(s): return the string in reverse order.','def solve(s):\n    return s[::-1]\n', [(['ab'],'ba')]),
 item('sort','sorting','solve(nums): return the integers sorted ascending.','def solve(nums):\n    return sorted(nums)\n', [([[3,2]],[2,3])]),
 item('even','parity','solve(x): return whether the integer is even.','def solve(x):\n    return x % 2 == 0\n', [([2],True)]),
 item('contains','membership','solve(nums, x): return whether x occurs in nums.','def solve(nums, x):\n    return x in nums\n', [([[1,2],2],True)]),
]
VALIDATION = [
 item('square','arithmetic','solve(x): return x multiplied by itself.','def solve(x):\n    return x * x\n', [([3],9),([-2],4)]),
 item('odd','parity','solve(x): return whether x is odd.','def solve(x):\n    return x % 2 != 0\n', [([3],True),([0],False)]),
]
# Algorithm-family holdout relative to training, not a certified uncontaminated LLM benchmark.
TEST = [
 item('two-sum','pair-search','solve(nums, target): return indices [i, j], i < j, whose values sum to target. Exactly one pair exists.',None,
      [([[2,7,11,15],9],[0,1]),([[3,2,4],6],[1,2]),([[3,3],6],[0,1]),([[-3,4,3,90],0],[0,2]),([[0,4,3,0],0],[0,3])]),
 item('palindrome','palindrome','solve(s): return True if the string reads the same forward and backward, else False.',None,
      [(['racecar'],True),(['ab'],False),([''],True),(['aa'],True),(['AbA'],True),(['abca'],False)]),
 item('running-sum','prefix-sum','solve(nums): return a list whose element i is the sum of nums[0] through nums[i].',None,
      [([[1,2,3,4]],[1,3,6,10]),([[]],[]),([[-1,2,-3]],[-1,1,-2]),([[0,0]],[0,0])]),
 item('valid-brackets','stack','solve(s): return whether a string of brackets ()[]{} is balanced and correctly nested.',None,
      [(['()[]{}'],True),(['([)]'],False),([''],True),(['{[]}'],True),(['('],False),([']'],False)]),
 item('deduplicate','stable-unique','solve(nums): remove repeated integers, keeping the first occurrence of each in original order.',None,
      [([[3,1,3,2,1]],[3,1,2]),([[]],[]),([[0,0]],[0]),([[-2,1,-2]],[-2,1])]),
 item('max-subarray','dynamic-programming','solve(nums): return the maximum sum of a nonempty contiguous subarray of a nonempty integer list.',None,
      [([[-2,1,-3,4,-1,2,1,-5,4]],6),([[-3,-1,-2]],-1),([[1]],1),([[5,4,-1,7,8]],23),([[0,-1,0]],0)]),
]

def prompt(problem):
    return INSTRUCTION + problem['statement'] + '\nCode:\n'

def manifest():
    splits = dict(train=TRAIN, validation=VALIDATION, test=TEST)
    return {name: {'count':len(items), 'ids':[x['id'] for x in items],
                   'sha256':hashlib.sha256(json.dumps(items,sort_keys=True).encode()).hexdigest()}
            for name,items in splits.items()}

def public(problem):
    return {k:problem[k] for k in ('id','family','statement')}
