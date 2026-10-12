"""Generate a readable audit and line-preserving evidence appendix from receipts."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from flycodes.common import ROOT, read_json
from flycodes.curriculum_dashboard import latest_v2

run = latest_v2()
audit = run / read_json(run / 'syntax-audit-latest.json')['audit']
data = read_json(audit / 'results.json')
rows = data['results']
summaries = data['summaries']
lines = ['# Syntax-tolerant results', '', f'Saved run: `{run.name}`. Audit: `{audit.name}`.', '',
         'Mechanical repairs recovered one additional previously seen exercise for fly seed 19, and the same exercise for its no-recurrence control. No new MBPP or transfer success was verified. This is a post-hoc diagnostic; original benchmark scores remain unchanged.', '',
         '| Model | Split | Original passes | Verified after repair | Newly recovered | Made runnable | Unresolved syntax | Functional failures |',
         '|---|---|---:|---:|---:|---:|---:|---:|']
for s in summaries:
    lines.append(f'| {s["arm"]} | {s["split"]} | {s["original_passes"]}/{s["total"]} | {s["verified_passes"]}/{s["total"]} | {s["newly_recovered"]} | {s["mechanically_repaired"]} | {s["unresolved_syntax"]} | {s["functional_failures"]} |')
lines += ['', '**Unresolved is not a proven logic failure.** The diagnostic could not determine a runnable interpretation without guessing missing operands, bodies, names or control flow. Zero verified new-task passes does not prove no conceivable interpretation could work. Made runnable counts only formerly invalid programs; functional failures also include already-valid programs.', '',
          'Across both fly seeds, 25 previously invalid outputs became runnable. Of 48 MBPP attempts (24 tasks × two seeds), seven interpretations could be executed and failed; 41 remained unresolved. Of 60 transfer attempts, 41 could be executed and failed; 19 remained unresolved. Both fly seeds now have one verified seen-training reproduction out of eight. The matched controls give the same result.', '',
          'The repair function never receives the problem or its tests. Names, keywords, literals, operators, statement order and all original statements are preserved. All interpretations were frozen and hashed before testing. No model training, candidate regeneration, hosted API calls or test-guided edits occurred. [Exact repair policy and references](SYNTAX_AUDIT_PROTOCOL.md).', '',
          '## What the line-by-line evidence shows', '']
examples = [
    ('fly-s19', 'curr-offset-sum-0', 'A recovered seen example',
     'The function accepts the list. The first return already computes its sum; removing the extra colon makes it legal Python. Subsequent repeated returns are unreachable and were preserved. This is a training example, not evidence of new-task generalization.'),
    ('fly-s7', 'curr-offset-sum-6', 'Runnable, but missing the requested computation',
     'The first return computes only the sum and immediately exits. The next return contains −1 instead of +6 and is unreachable anyway. Fixing colons cannot supply the missing addition or reorder execution.'),
    ('fly-s19', 'curr-count-above-6', 'Recognizable code, wrong operation',
     'The first return adds the list elements. Counting elements greater than six requires a threshold condition and a count; neither is present in that return. Later repeated returns perform the same sum.'),
    ('fly-s7', 'mbpp-436', 'Closing a bracket does not supply a filtering algorithm',
     'Closing the list makes this text compilable, but its expression references undefined x and i. There is no iteration binding or negativity condition. Those would be algorithmic additions, so the audit does not insert them.'),
]
for arm, id, title, explanation in examples:
    r = next(x for x in rows if x['arm'] == arm and x['problem']['id'] == id)
    lines += [f'### {title}', '', f'`{arm}` / `{id}`: {r["problem"]["statement"]}', '', explanation, '',
              'Original:', '', '```python', r['original_code'].rstrip(), '```', '',
              'Mechanical interpretation:', '', '```python', r['interpretation']['code'].rstrip(), '```', '',
              f'Result: **{r["judgement"]["status"]}**.']
    if 'counterexample' in r:
        c = r['counterexample'];lines += [f'Counterexample: arguments `{c["args"]!r}`, expected `{c["expected"]!r}`, returned `{c["actual"]!r}`.']
    if r['judgement'].get('detail'): lines += [f'Detail: `{r["judgement"]["detail"]}`.']
    if r['judgement'].get('passed'):
        lines += [f'Passed {r["judgement"]["passed_cases"]}/{r["judgement"]["total_cases"]} cases, including the stronger boundary tests.']
    lines += ['']
lines += ['The complete original/interpretation pairs, line-specific edits, diffs, test outcomes and first wrong-answer counterexamples are in [the evidence appendix](SYNTAX_AUDIT_EVIDENCE.md). The UI offers an Original / Syntax audit selector. No repair was made to the frozen graph or trained models.']
(ROOT / 'docs/SYNTAX_AUDIT_RESULTS.md').write_text('\n'.join(lines) + '\n')
evidence = ['# Complete syntax audit evidence', '', 'Each candidate is retained in full. Unresolved candidates are tentative, incomplete edits, not executable solutions. Unchanged programs are shown once.', '']
for r in rows:
    x = r['interpretation']
    evidence += [f'## {r["arm"]} / {r["split"]} / {r["problem"]["id"]}', '', r['problem']['statement'], '',
                 f'Interpretation: **{x["status"]}**. Outcome: **{r["judgement"]["status"]}**.', '',
                 'Original:', '', '```python', r['original_code'].rstrip(), '```', '']
    if x['code'] != r['original_code']:
        evidence += ['Interpretation:', '', '```python', x['code'].rstrip(), '```', '', 'Edits:', '']
        evidence += ['- ' + edit for edit in x['edits']]
        evidence += ['', '```diff', x['diff'].rstrip(), '```', '']
    if x['remaining_error']: evidence += ['Unresolved: ' + x['remaining_error'], '']
    if r['judgement'].get('detail'): evidence += ['Judge detail: ' + r['judgement']['detail'], '']
    if 'counterexample' in r: evidence += ['Counterexample: `' + repr(r['counterexample']) + '`', '']
    if r['judgement'].get('passed'): evidence += [f'Passed {r["judgement"]["passed_cases"]}/{r["judgement"]["total_cases"]} cases.', '']
(ROOT / 'docs/SYNTAX_AUDIT_EVIDENCE.md').write_text('\n'.join(evidence) + '\n')
print(ROOT / 'docs/SYNTAX_AUDIT_RESULTS.md')
