"""Append visualization-only audit records after artifact validation has passed."""
import csv
import datetime as dt
import json
import re
from pathlib import Path
from model import ROOT,VIZ,DATASET,UUID,sha,write_json


def append(path,text):
    with path.open('a') as f:f.write(text)


def ledger(name,prefix,rows):
    path=ROOT/'logs'/name
    with path.open(newline='') as f:
        reader=csv.DictReader(f);fields=reader.fieldnames;old=list(reader)
    key=fields[0];count=max(int(r[key][len(prefix):]) for r in old)
    ids=[]
    with path.open('a',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields)
        for i,row in enumerate(rows,1):
            row=dict(row);row[key]=prefix+str(count+i).zfill(3);ids.append(row[key]);writer.writerow({k:row.get(k,'') for k in fields})
    return ids


def main():
    run=(VIZ/'data/current_run.txt').read_text().strip();data=VIZ/'data'/run
    if (data/'audit_record.json').exists():raise SystemExit('This build already has append-only audit records')
    validation=json.loads((data/'validation.json').read_text());ui=json.loads((data/'explorer_validation.json').read_text())
    assert validation['status']=='PASS' and ui['status']=='PASS'
    model=json.loads((data/'model.json').read_text());manifest=json.loads((data/'build_manifest.json').read_text())
    for file,digest in manifest['input_sha256'].items():assert sha(ROOT/file)==digest
    now=dt.datetime.now(dt.timezone.utc).isoformat()
    did='D'+str(max(map(int,re.findall(r'### D(\d+)',(ROOT/'logs/decision_log.md').read_text())))+1).zfill(3)
    qnext=max(map(int,re.findall(r'Q-(\d+)',(ROOT/'logs/unresolved_questions.md').read_text())))+1
    qsk='Q-'+str(qnext).zfill(3);qor='Q-'+str(qnext+1).zfill(3)
    base=dict(timestamp=now,experiment='VISUALIZATION_ONLY',dataset=DATASET,
        claim_type='COMPUTATIONAL_RESULT',support_level='display derivative of previously verified raw records',verification_status='VERIFIED',
        confidence='exact record checks',notes='No scientific result or experiment configuration changed; no effective analysis or physiology simulated.')
    claims=[
        dict(claim='The explicitly requested visualization inventory has 110 bodies and 1923 induced raw body edges; every saved weight matches the frozen validated source. This is not a selected sugar circuit.',
             source_1=f'visualization/data/{run}/model.json',source_2=f'visualization/data/{run}/validation.json',body_ids='|'.join(n['body_id'] for n in model['nodes'])),
        dict(claim='The PAPER-ASSOCIATED view has 102 bodies and 274 body edges from the saved mapped named routes. Sensory display cards pool only within subtype/side; individual bodies remain in HTML and graph files. Puddle remains unresolved; eight published/current pooled discrepancies are not corrected or hidden.',
             source_1=model['source_run']+'/paper_associated_paths.csv',source_2=f'visualization/graph/{run}/paper_associated.graphml'),
        dict(claim='The CANDIDATE comparison presents 12 bodies in six independent profiles. GNG042/GNG015 have mapped Figure 6 counterpart support; GNG232/DNg67/DNge080 have scoped supplementary-panel support (C061), not selected circuit membership. GNG021 paper presence remains unverified. No D badge is inferred from a Shiu synonym; this is not a claim that other candidates are absent from the full paper.',
             source_1=f'visualization/static/{run}/figure3_candidate_comparison.svg',source_2='results/method_recovery/20261006T214639Z/audit_snapshot_final/logs/claim_ledger.csv C061; '+model['source_run']+'/nodes.csv',
             claim_type='CORRECTION',supersedes_claim_id='C066',notes='Supersedes the earlier visualization claim C066 and its omitted supplementary P badges. New audit evidence appeared during visualization work; no raw result or selected membership changed.'),
        dict(claim='All four sugar-selection panels are unpopulated because no validated algorithm result exists; effective scores are null and the visualization does not compute them.',
             source_1=f'visualization/data/{run}/selected_results.json',source_2=f'visualization/data/{run}/explorer_validation.json'),
        dict(claim='Actual requested anatomy could not be obtained in this environment: the official per-body SWC request failed at DNS resolution, and sandbox escalation was rejected. Zero authentic requested SWCs are rendered; anatomical camera orientation also remains unverified.',
             source_1='visualization/anatomy/20261006T215922944362Z/retrieval/query_log.jsonl',source_2=f'visualization/anatomy/{run}/anatomy.json',
             support_level='retrieval outcome; no anatomical claim',verification_status='BLOCKED — SOURCE REQUIRED',claim_type='DISCREPANCY')]
    cids=ledger('claim_ledger.csv','C',[dict(base,**r) for r in claims])
    mids=ledger('mismatch_ledger.csv','M',[dict(timestamp=now,experiment='VISUALIZATION_ONLY',
        item='Initial visualization guard incorrectly compared entire start/end metadata row arrays',
        source_A='visualization/scripts/model.py initial draft',value_A='Required equal array length',
        source_B=model['source_run']+'/raw/meta_start.json; '+model['source_run']+'/raw/meta_end.json',
        value_B='End response includes two extra total-count fields; all shared identity/mutation/threshold fields match',
        severity='resolved implementation expectation; not a dataset disagreement',possible_explanation='Different query projections',
        resolved='yes',resolution='Compare all named start fields against end values; preserve strict family/tag/UUID and source mutation guards.',
        related_claim_ids=cids[0],follow_up_required='none')])
    append(ROOT/'logs/decision_log.md',f'''

### {did} — Visualization framework only ({now})
- QUESTION: How to display the verified structure without claiming a selected sugar circuit?
- AVAILABLE EVIDENCE: Initial/structural checkpoints, all current logs, frozen raw tables and mapped paper routes; explicit user visualization request.
- OPTIONS: Show the large raw export; infer a selected sugar circuit; create small explicitly labeled derivatives and pending selection panels.
- DECISION: Use 110 verified requested bodies. Paper mode uses only the 274 saved mapped-route edges. Split same/opposite endpoint-side sheets; preserve all body IDs. Independent candidate cards carry source-backed P/R badges. Unknown order stays gray. Puddle stays unresolved. No E/D/X badge without corresponding evidence. Raw and effective weights are separate fields.
- WHY: Structural presence and paper association do not establish algorithm selection or physiological action. No entire dense path union is drawn.
- ALTERNATIVES REJECTED: Forced candidate membership, anatomy inferred from topology, signs assigned from NT predictions, and anatomical crossings inferred from soma sides.
- WHAT WOULD CHANGE THIS DECISION: Independently validated, hashed Tastekin results or new body-mapped evidence; see visualization/docs/SELECTED_RESULTS.md.
- IMPLEMENTATION / VALIDATION: Build `{run}`; directed GraphML/GEXF roundtrips, exact source joins, 320-DPI checks, eight Python contract tests and {ui['checks']} offline JavaScript behavior checks. Chrome could not launch (exit 134), so full browser visual verification is not claimed. Static images were visually inspected; arrow routing was revised to avoid passing behind unrelated nodes. Earlier drafts are retained and marked superseded in visualization/data/build_history.json.
- ANATOMY: Official per-body downloads failed with curl DNS code 6; automatic approval rejected sandbox escalation. Stop retrieval after transport failure. Store explicit BLOCKED status, actual SWC parser/renderer and retry instructions. Camera handedness requires an authoritative orientation source before named anatomical views are enabled. No synthetic morphology.
- RELATED: {', '.join(cids)}; {', '.join(mids)}.
''')
    append(ROOT/'logs/unresolved_questions.md',f'''

## Visualization checkpoint — {now}

| ID | Question | Evidence / why it matters | Required resolution | Status |
|---|---|---|---|---|
| {qsk} | Can authentic allowlisted v1.0 SWCs be downloaded? | Official per-body request failed with curl DNS code 6; elevated download rejected by disabled sandbox escalation. Zero SWCs rendered. | Run the documented public/neuPrint retrieval in a network-enabled session; preserve response hashes and original geometry. | BLOCKED — ACCESS REQUIRED |
| {qor} | What authoritative axis-sign mapping establishes anterior/posterior/dorsal/lateral cameras in native MaleCNS EM coordinates? | Official source establishes 8-nm units; complete anatomical handedness was not verified here. | Supply verified orthonormal raw-to-right/dorsal/anterior matrix and primary source; see visualization/anatomy/orientation.json. | UNVERIFIED — SOURCE REQUIRED |

Q-003/Q-004/Q-012 remain blocked for effective-connectivity methodology. Q-013 Puddle remains unresolved. Q-014 crossing locations are not inferred from diagrams. No selection, Shiu dynamics, experimental validation or physiological simulation was performed by this visualization task.
''')
    append(ROOT/'STATUS.md',f'''

## {now} — Visualization framework checkpoint; STOPPED

### COMPLETED

Constructed `visualization/data`, `scripts`, `static`, `interactive`, `anatomy`, `graph`, and `docs`. Current build: `{run}`. [Open explorer](visualization/interactive/index.html); [figure index](visualization/docs/VISUALIZATION_INDEX.md). SVG/PDF/320-DPI PNG, self-contained local HTML, directed GraphML/GEXF, provenance manifests and reusable selected-result adapter are present.

### CURRENT FINDINGS

Figure 1 is explicitly PAPER-ASSOCIATED with current raw weights and separate same/opposite-side sheets. Figure 2 has four unpopulated effective-selection panels. Figure 3 has six independent CANDIDATE comparisons. No raw path is represented as the final selected sugar pathway.

### VERIFIED FACTS

110 bodies, 1923 scoped raw edges and 274 mapped paper-associated edges exactly join to the frozen source; both graph formats preserve body IDs, sides and raw weights. All static PNGs are 320 DPI. Eight contract tests and {ui['checks']} offline JS behavior checks pass. Original structural input hashes are unchanged. Claims: {', '.join(cids)}.

### UNVERIFIED ITEMS

Actual anatomy is BLOCKED: skeleton download failed due to DNS/network restrictions. Anatomical camera orientation remains unverified. The parser and native 3D renderer are implemented but authentic anatomical renders are not produced. Chrome launch failed, so no full-browser visual test is claimed. Puddle and effective-connectivity methodology remain unresolved.

### MISMATCHES

Existing eight paper/current pooled differences remain visible. {mids[0]} records a resolved metadata-guard implementation expectation, not a dataset mismatch. No scientific raw result was changed.

### NEW QUESTIONS

{qsk} authoritative skeleton retrieval access; {qor} native anatomical orientation evidence. These block anatomy, not the valid raw/paper-associated display derivatives.

### FILES CREATED

See [VISUALIZATION_INDEX](visualization/docs/VISUALIZATION_INDEX.md), [build instructions](visualization/README.md), [anatomy recovery](visualization/docs/ANATOMY.md), [selected-result contract](visualization/docs/SELECTED_RESULTS.md), and `visualization/data/{run}/` for manifests and validation reports. Prior drafts remain preserved.

### NEXT ACTION

Stop at the user-requested visualization framework/current-view boundary. No experiments, effective-connectivity calculations, selection, Shiu simulations or physiological analysis ran. Skeleton retrieval may be retried in a network-enabled session; algorithm-selected panels must wait for independently validated results.
''')
    append(ROOT/'CHANGELOG.md',f'\n## {now} — Visualization framework\n\nCreated labeled raw/paper/candidate views, four pending sugar panels, body-level offline explorer, SVG/PDF/320-DPI PNG and directed GraphML/GEXF, source/weight validation, and an anatomy retrieval/rendering pipeline with explicit BLOCKED output. Scientific source results unchanged. See [index](visualization/docs/VISUALIZATION_INDEX.md).\n')
    append(ROOT/'README.md','\n## Visualization framework\n\n[Open local explorer](visualization/interactive/index.html) · [Figure index](visualization/docs/VISUALIZATION_INDEX.md) · [Build/reuse instructions](visualization/README.md). Current raw/paper-associated and independent candidate views are available. Sugar-selection panels await validated results; actual anatomy is explicitly BLOCKED by skeleton retrieval access and unverified camera orientation.\n')
    history=[]
    for p in sorted((VIZ/'data').iterdir()):
        if p.is_dir() and p.name.startswith('20'):
            history.append(dict(run_id=p.name,status='CURRENT' if p.name==run else 'SUPERSEDED DISPLAY DRAFT' if (p/'model.json').exists() else 'ABORTED BEFORE DATA EXPORT',
                                reason='Final validated display' if p.name==run else 'Retained for audit; initial guard or arrow-routing layout revised. Do not use as final figure.'))
    write_json(VIZ/'data/build_history.json',history)
    record=dict(timestamp=now,run_id=run,claims=cids,mismatches=mids,python_contract_tests=8,offline_js_checks=ui['checks'],
                full_browser_visual_test='BLOCKED — Chrome process exit 134',scientific_source_inputs_unchanged=True)
    write_json(data/'audit_record.json',record)
    append(ROOT/'logs/run_manifest.jsonl',json.dumps(dict(record,experiment='VISUALIZATION_ONLY',dataset=DATASET,dataset_uuid=UUID,build_manifest=str((data/'build_manifest.json').relative_to(ROOT)),build_manifest_sha256=sha(data/'build_manifest.json')))+'\n')
    print(json.dumps(record,indent=2))


if __name__=='__main__':main()
