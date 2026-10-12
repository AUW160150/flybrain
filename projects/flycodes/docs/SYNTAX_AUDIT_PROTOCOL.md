# Syntax-tolerant diagnostic audit

Requested after the curriculum-v2 results, on 2026-10-09. This is a post-hoc diagnostic of saved outputs, not another training experiment or a replacement for original pass@1. Some original outputs were inspected before this protocol was written.

Question: does the saved program contain enough correct computation to pass when surface syntax mistakes are excused?

Scope: all 24 sampled MBPP, 30 transfer and 8 seen-training outputs for each of the two fly seeds and their matched no-recurrence controls. No regenerated answers, no training, no API calls. Original artifacts remain unchanged.

The repair function receives only the generated text. It cannot access the problem statement, reference solution, tests or verdicts. All interpretations are saved and hashed before any repaired program is tested. No repair is selected using test outcomes.

Allowed deterministic edits: add missing suite colons; remove trailing colons on simple statements; close unclosed delimiters at a physical line boundary; match or remove erroneous closing delimiters; normalize indentation for a single straight-line function with no nested suites. Every identifier, keyword, number, string, comma and computation/comparison operator stays in the same order. Every statement remains, including repeated and unreachable statements. Bracket repairs are explicitly tentative interpretations because invalid text has no guaranteed original Python semantics.

Forbidden: adding missing operands, conditions, loop bodies or algorithm steps; changing constants, variable names, function calls, operators or parameters; removing a wrong early return; completing truncated algorithms; guessing nested control flow. Programs requiring these changes remain **unresolved**, not assumed logically wrong or silently counted as passing. Already valid programs are unchanged.

Python compilation checks syntax, including duplicate parameters that AST parsing alone may not reject; compiled objects are never executed. The existing bounded AST interpreter runs functional tests in a subprocess. Authored exercises use the stronger boundary/exhaustive-short-list audit tests. MBPP uses the original supplied cases. A pass remains limited to those tests. See the [Python AST documentation](https://docs.python.org/3/library/ast.html) and [EvalPlus's test-adequacy motivation](https://arxiv.org/abs/2305.01210). These sources support the parsing/testing distinction and stronger testing; they do not validate these particular repair heuristics.

Report separately: original passes, passes under the diagnostic interpretation, newly recovered passes, syntax errors repaired to compilable Python, unresolved syntax, and functional failures. Keep training reproduction separate from new-task evaluation. An unresolved program prevents a definitive verdict about its intended algorithm; no claim of exhaustive repair search is made.
