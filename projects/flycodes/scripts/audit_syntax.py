"""Freeze task-blind interpretations, then evaluate their unchanged computation."""
import sys
import shutil
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from flycodes.common import ROOT, now, sha256, read_json, write_json
from flycodes.curriculum_dashboard import latest_v2, problems
from flycodes.curriculum_audit import stronger_cases
from flycodes.syntax_audit import interpret
from flycodes.judge import judge


def run_audit():
    run = latest_v2()
    if run is None: raise SystemExit('No completed curriculum run')
    output = run / ('syntax-audit-' + now().replace('-', '').replace(':', '').split('.')[0].replace('+0000', ''))
    output.mkdir(exist_ok=False)
    config = read_json(run / 'config.json')
    originals = read_json(run / 'artifacts.json')
    def verify_originals():
        for name, expected in originals.items():
            if sha256(run / name) != expected: raise RuntimeError('Original changed: ' + name)
    verify_originals()
    snapshots = ['flycodes/syntax_audit.py', 'scripts/audit_syntax.py',
                 'flycodes/curriculum_audit.py', 'flycodes/judge.py', 'docs/SYNTAX_AUDIT_PROTOCOL.md']
    (output / 'source').mkdir()
    for relative in snapshots: shutil.copyfile(ROOT / relative, output / 'source' / Path(relative).name)
    rows = []
    for arm in ['fly', 'no-recurrence']:
        for seed in config['seeds']:
            name = f'{arm}-s{seed}'
            for split in ['test', 'transfer', 'train-reproduction']:
                source = run / f'{name}-{split}-evaluation.json'
                audited = run / 'test-adequacy-audit' / source.name
                if audited.exists(): source = audited
                for row in read_json(source)['results']:
                    rows.append(dict(arm=name, split=split, problem=row['problem'],
                                     original_code=row['code'], original_judgement=row['judgement'],
                                     original_stop_reason=row['stop_reason'],
                                     interpretation=interpret(row['code']), source_sha256=sha256(source)))
    # No problem text or test cases are arguments to interpret(). Freeze all
    # interpretations before loading any problem cases or evaluating candidates.
    write_json(output / 'candidates.json', rows)
    write_json(output / 'freeze.json', dict(created_at=now(), phase='before candidate evaluation',
        candidates_sha256=sha256(output / 'candidates.json'),
        sources={name: sha256(ROOT / name) for name in snapshots},
        repair_selection='deterministic task-blind interpretation; no test-guided selection'))
    by_id = {p['id']: p for p in problems(run, config)}
    all_cases = {id: stronger_cases(p) for id, p in by_id.items()}
    write_json(output / 'cases.json', all_cases)
    for row in rows:
        interpretation = row['interpretation']
        if interpretation['status'] == 'unresolved':
            row['judgement'] = dict(status='unresolved_syntax', passed=None,
                                    detail='Intended logic cannot be established by the allowed mechanical edits: ' + interpretation['remaining_error'])
        else:
            cases = all_cases[row['problem']['id']]
            result = judge(interpretation['code'], cases)
            row['judgement'] = result
            for i, case in enumerate(result.get('cases', [])):
                if not case['passed']:
                    row['counterexample'] = dict(args=cases[i]['args'], actual=case['actual'], expected=case['expected'])
                    break
        print(row['arm'], row['split'], row['problem']['id'], interpretation['status'], row['judgement']['status'], flush=True)
    summaries = []
    for arm in ['fly', 'no-recurrence']:
        for seed in config['seeds']:
            name = f'{arm}-s{seed}'
            for split in ['test', 'transfer', 'train-reproduction']:
                group = [r for r in rows if r['arm'] == name and r['split'] == split]
                summaries.append(dict(arm=name, split=split, total=len(group),
                    original_passes=sum(r['original_judgement'].get('passed') is True for r in group),
                    verified_passes=sum(r['judgement'].get('passed') is True for r in group),
                    newly_recovered=sum(r['judgement'].get('passed') is True and r['original_judgement'].get('passed') is not True for r in group),
                    mechanically_repaired=sum(r['interpretation']['status'] == 'repaired' for r in group),
                    unresolved_syntax=sum(r['interpretation']['status'] == 'unresolved' for r in group),
                    functional_failures=sum(r['judgement'].get('passed') is False for r in group),
                    judge_errors=sum(r['judgement']['status'] == 'judge_error' for r in group),
                    outcomes=dict(Counter(r['judgement']['status'] for r in group))))
    if sha256(output / 'candidates.json') != read_json(output / 'freeze.json')['candidates_sha256']:
        raise RuntimeError('Candidate freeze changed')
    verify_originals()
    write_json(output / 'results.json', dict(created_at=now(), run=run.name, audit=output.name,
        scope='post-hoc diagnostic, unresolved intentions are unmeasured, not proven incorrect',
        summaries=summaries, results=rows))
    write_json(output / 'manifest.json', dict(completed_at=now(), original_artifacts_unchanged=True,
        original_artifacts_checked=len(originals),
        files={str(p.relative_to(output)): sha256(p) for p in sorted(output.rglob('*')) if p.is_file()}))
    write_json(run / 'syntax-audit-latest.json', dict(audit=output.name))
    print(output)
    for summary in summaries: print(summary)
    return output


if __name__ == '__main__': run_audit()
