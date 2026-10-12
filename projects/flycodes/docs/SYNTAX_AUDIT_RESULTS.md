# Syntax-tolerant results

Saved run: `curriculum-20261009T163310`. Audit: `syntax-audit-20261009T173433`.

Mechanical repairs recovered one additional previously seen exercise for fly seed 19, and the same exercise for its no-recurrence control. No new MBPP or transfer success was verified. This is a post-hoc diagnostic; original benchmark scores remain unchanged.

| Model | Split | Original passes | Verified after repair | Newly recovered | Made runnable | Unresolved syntax | Functional failures |
|---|---|---:|---:|---:|---:|---:|---:|
| fly-s7 | test | 0/24 | 0/24 | 0 | 1 | 21 | 3 |
| fly-s7 | transfer | 0/30 | 0/30 | 0 | 6 | 8 | 22 |
| fly-s7 | train-reproduction | 1/8 | 1/8 | 0 | 2 | 3 | 4 |
| fly-s19 | test | 0/24 | 0/24 | 0 | 4 | 20 | 4 |
| fly-s19 | transfer | 0/30 | 0/30 | 0 | 9 | 11 | 19 |
| fly-s19 | train-reproduction | 0/8 | 1/8 | 1 | 3 | 5 | 2 |
| no-recurrence-s7 | test | 0/24 | 0/24 | 0 | 1 | 21 | 3 |
| no-recurrence-s7 | transfer | 0/30 | 0/30 | 0 | 6 | 8 | 22 |
| no-recurrence-s7 | train-reproduction | 1/8 | 1/8 | 0 | 2 | 3 | 4 |
| no-recurrence-s19 | test | 0/24 | 0/24 | 0 | 4 | 20 | 4 |
| no-recurrence-s19 | transfer | 0/30 | 0/30 | 0 | 9 | 11 | 19 |
| no-recurrence-s19 | train-reproduction | 0/8 | 1/8 | 1 | 3 | 5 | 2 |

**Unresolved is not a proven logic failure.** The diagnostic could not determine a runnable interpretation without guessing missing operands, bodies, names or control flow. Zero verified new-task passes does not prove no conceivable interpretation could work. Made runnable counts only formerly invalid programs; functional failures also include already-valid programs.

Across both fly seeds, 25 previously invalid outputs became runnable. Of 48 MBPP attempts (24 tasks × two seeds), seven interpretations could be executed and failed; 41 remained unresolved. Of 60 transfer attempts, 41 could be executed and failed; 19 remained unresolved. Both fly seeds now have one verified seen-training reproduction out of eight. The matched controls give the same result.

The repair function never receives the problem or its tests. Names, keywords, literals, operators, statement order and all original statements are preserved. All interpretations were frozen and hashed before testing. No model training, candidate regeneration, hosted API calls or test-guided edits occurred. [Exact repair policy and references](SYNTAX_AUDIT_PROTOCOL.md).

## What the line-by-line evidence shows

### A recovered seen example

`fly-s19` / `curr-offset-sum-0`: solve(nums): Add 0 to the sum of all numbers in nums.

The function accepts the list. The first return already computes its sum; removing the extra colon makes it legal Python. Subsequent repeated returns are unreachable and were preserved. This is a training example, not evidence of new-task generalization.

Original:

```python
def solve(nums):
    return sum(nums):
    return sum(nums):
    return sum(nums):
    return sum(nums):
    return sum(nums):
    return sum(nums):
    return sum(nums):
    return sum(nums):
    return sum(nums):
    return sum(nums):
    return sum(nums):
    return sum(nums):
    return sum(nums):
    return sum(nums):
    return sum(nums):
    return sum(nums):
    return sum(nums):
    return sum(nums):
    return sum(nums):
    return sum(nums):
    return sum(nums):
    return sum(nums):
    return sum(nums):
```

Mechanical interpretation:

```python
def solve(nums):
    return sum(nums)
    return sum(nums)
    return sum(nums)
    return sum(nums)
    return sum(nums)
    return sum(nums)
    return sum(nums)
    return sum(nums)
    return sum(nums)
    return sum(nums)
    return sum(nums)
    return sum(nums)
    return sum(nums)
    return sum(nums)
    return sum(nums)
    return sum(nums)
    return sum(nums)
    return sum(nums)
    return sum(nums)
    return sum(nums)
    return sum(nums)
    return sum(nums)
    return sum(nums)
```

Result: **passed**.
Passed 470/470 cases, including the stronger boundary tests.

### Runnable, but missing the requested computation

`fly-s7` / `curr-offset-sum-6`: solve(nums): Add 6 to the sum of all numbers in nums.

The first return computes only the sum and immediately exits. The next return contains −1 instead of +6 and is unreachable anyway. Fixing colons cannot supply the missing addition or reorder execution.

Original:

```python
def solve(nums):
    return sum(nums):
    return sum(nums) + -1
```

Mechanical interpretation:

```python
def solve(nums):
    return sum(nums)
    return sum(nums) + -1
```

Result: **wrong_answer**.
Counterexample: arguments `[[-6, -1, 0, 2, 7]]`, expected `8`, returned `2`.

### Recognizable code, wrong operation

`fly-s19` / `curr-count-above-6`: solve(nums): Count the integers strictly greater than 6.

The first return adds the list elements. Counting elements greater than six requires a threshold condition and a count; neither is present in that return. Later repeated returns perform the same sum.

Original:

```python
def solve(nums):
    return sum(x for x in nums):
    return sum(x for x in nums):
    return sum(x for x in nums):
    return sum(x for x in nums)
```

Mechanical interpretation:

```python
def solve(nums):
    return sum(x for x in nums)
    return sum(x for x in nums)
    return sum(x for x in nums)
    return sum(x for x in nums)
```

Result: **wrong_answer**.
Counterexample: arguments `[[-6, -1, 0, 2, 7]]`, expected `1`, returned `2`.

### Closing a bracket does not supply a filtering algorithm

`fly-s7` / `mbpp-436`: solve(list1): Write a python function to print negative numbers in a list.

Closing the list makes this text compilable, but its expression references undefined x and i. There is no iteration binding or negativity condition. Those would be algorithmic additions, so the audit does not insert them.

Original:

```python
def solve(nums):
    return [x * i in nums[:-1]
```

Mechanical interpretation:

```python
def solve(nums):
    return [x * i in nums[:-1]]
```

Result: **runtime_error**.
Detail: `'x'`.

The complete original/interpretation pairs, line-specific edits, diffs, test outcomes and first wrong-answer counterexamples are in [the evidence appendix](SYNTAX_AUDIT_EVIDENCE.md). The UI offers an Original / Syntax audit selector. No repair was made to the frozen graph or trained models.
