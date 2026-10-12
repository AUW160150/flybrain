"""Initial checkpoint: compare published IDs with official v1.0 annotations.

Reads saved primary sources only. No connectivity analysis, hypothesis tests,
experiment execution, or simulation. Outputs go to a new directory every time.
"""
import collections
import csv
import datetime as dt
import hashlib
import json
import platform
import struct
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import pyarrow
import pyarrow.feather as feather

ROOT = Path(__file__).resolve().parents[1]
DATASET = 'male-cns:v1.0'
TARGETS = ['LB3a', 'LB3b', 'LB3c', 'LB3d', 'GNG042', 'ANXXX462a',
           'GNG015', 'GNG021', 'MN4', 'MN4a', 'MN6', 'MN8', 'MN9']
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sheet_rows(path, sheet_number):
    # Read Excel values as strings; never pass a body ID through floating point.
    with zipfile.ZipFile(path) as archive:
        strings = [''.join(e.itertext()) for e in
                   ET.fromstring(archive.read('xl/sharedStrings.xml'))]
        xml = ET.fromstring(archive.read(f'xl/worksheets/sheet{sheet_number}.xml'))
        headers = None
        rows = []
        for row in xml.findall('.//s:sheetData/s:row', NS):
            cells = {}
            for cell in row.findall('s:c', NS):
                column = ''.join(c for c in cell.attrib['r'] if c.isalpha())
                value = cell.find('s:v', NS)
                text = value.text if value is not None else ''
                if cell.attrib.get('t') == 's':
                    text = strings[int(text)]
                elif cell.attrib.get('t') == 'inlineStr':
                    text = ''.join(cell.find('s:is', NS).itertext())
                cells[column] = text
            if not any(cells.values()):
                continue
            if headers is None:
                headers = {k: v for k, v in cells.items() if v}
                continue
            item = {v: cells.get(k, '') for k, v in headers.items()}
            item['excel_row'] = row.attrib['r']
            rows.append(item)
        return rows


def write_csv(path, rows, fields):
    with path.open('x', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    timestamp = dt.datetime.now(dt.timezone.utc).isoformat()
    out = ROOT / 'results/validation' / dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out.mkdir(parents=True, exist_ok=False)
    annotation_path = ROOT / 'data/raw/body-annotations-male-cns-v1.0-minconf-0.5.feather'
    nt_path = ROOT / 'data/raw/body-neurotransmitters-male-cns-v1.0.feather'
    table_path = ROOT / 'paper/supplement/table_s1.xlsx'
    dataset_path = ROOT / 'data/raw/neuprint_datasets.json'
    # Match the saved fetch records before reading downloaded data.
    downloads = [json.loads(line) for line in (ROOT / 'logs/query_log.jsonl').read_text().splitlines()]
    for path in [annotation_path, nt_path, dataset_path]:
        relative = str(path.relative_to(ROOT))
        assert any(r.get('output_file') == relative and r.get('dataset') == DATASET
                   and r.get('http_status') == '200' and r.get('sha256') == sha(path)
                   for r in downloads), f'Unpinned source: {relative}'
    metadata = json.loads(dataset_path.read_text())[DATASET]
    annotations = feather.read_table(annotation_path).to_pylist()
    selected = sorted((r for r in annotations if r['type'] in TARGETS),
                      key=lambda r: (r['type'], r['bodyId']))
    assert len({r['bodyId'] for r in selected}) == len(selected)
    selected_ids = {r['bodyId'] for r in selected}
    nt_rows = [r for r in feather.read_table(nt_path).to_pylist() if r['body'] in selected_ids]
    assert len({r['body'] for r in nt_rows}) == len(nt_rows)
    nt = {r['body']: r for r in nt_rows}
    live_path = ROOT / 'data/raw/neuprint_neurons_authenticated.json'
    meta_path = ROOT / 'data/raw/neuprint_meta_authenticated.json'
    live = None
    live_comparisons = []
    if live_path.exists() and meta_path.exists():
        for path in [live_path, meta_path]:
            assert any(r.get('output_file') == str(path.relative_to(ROOT))
                       and str(r.get('http_status')) == '200'
                       and r.get('sha256') == sha(path) for r in downloads)
        meta_result = json.loads(meta_path.read_text())
        live_meta = dict(zip(meta_result['columns'], meta_result['data'][0]))['metadata']
        assert live_meta['dataset'] + ':' + live_meta['tag'] == DATASET
        assert live_meta['uuid'] == metadata['uuid']
        raw = json.loads(live_path.read_text())
        live_rows = [dict(zip(raw['columns'], r))['neuron'] for r in raw['data']]
        assert len({r['bodyId'] for r in live_rows}) == len(live_rows)
        live = {r['bodyId']: r for r in live_rows}
        assert set(live) == selected_ids, 'Body-ID sets differ; stop and investigate.'
    paper = []
    for number, name in [(1, 'GRNs'), (2, 'MNs')]:
        rows = sheet_rows(table_path, number)
        write_csv(out / f'table_s1_{name}.csv', rows, list(rows[0]))
        for row in rows:
            cell_type = row.get('Subtype') if name == 'GRNs' else row['Type']
            if row['Connectome'] == 'maleCNS' and cell_type in TARGETS:
                paper.append(dict(body_id=int(row['Body_ID']), cell_type=cell_type,
                                  side=row['Root_Side'], nerve=row.get('Entry_Nerve', row.get('Exit_Nerve')),
                                  sheet=name, excel_row=row['excel_row']))
    assert len({r['body_id'] for r in paper}) == len(paper)
    paper_by_id = {r['body_id']: r for r in paper}
    resolved = []
    comparisons = []
    nt_differences = []
    for row in selected:
        body_id = row['bodyId']
        nr = nt.get(body_id, {})
        pr = paper_by_id.get(body_id)
        # Keep the original fields; side is a labeled convenience, not an alias
        # asserting that rootSide and somaSide are biologically interchangeable.
        side_source = 'rootSide' if row['rootSide'] else 'somaSide' if row['somaSide'] else 'missing'
        side = row.get(side_source)
        nerve_source = 'entryNerve' if row['entryNerve'] else 'exitNerve' if row['exitNerve'] else 'missing'
        resolved.append(dict(body_id=str(body_id), cell_type=row['type'], instance=row['instance'],
            side=side, side_source=side_source, root_side=row['rootSide'], soma_side=row['somaSide'],
            **{'class': row['class']}, superclass=row['superclass'], subclass=row['subclass'],
            nerve=row.get(nerve_source), nerve_source=nerve_source,
            entry_nerve=row['entryNerve'], exit_nerve=row['exitNerve'], synonyms=row['synonyms'],
            predicted_neurotransmitter=nr.get('predicted_nt'), nt_confidence=nr.get('predicted_nt_confidence'),
            total_nt_predictions=nr.get('total_nt_predictions'), ground_truth=nr.get('ground_truth'),
            celltype_predicted_nt=nr.get('celltype_predicted_nt'),
            celltype_predicted_nt_confidence=nr.get('celltype_predicted_nt_confidence'),
            consensus_nt=nr.get('consensus_nt'), status=row['status'], status_label=row['statusLabel'],
            dataset=DATASET, source=str(annotation_path.relative_to(ROOT)),
            nt_source=str(nt_path.relative_to(ROOT)), timestamp=timestamp,
            table_s1_reference=f"{pr['sheet']}!row {pr['excel_row']}" if pr else '',
            verification_status='VERIFIED_FLAT_FILE_AND_NEUPRINT' if live is not None else 'VERIFIED_FLAT_FILE;NEUPRINT_UNVERIFIED'))
        if live is not None:
            checks = {k: row[k] for k in ['type','instance','rootSide','somaSide','class',
                'superclass','subclass','entryNerve','exitNerve','synonyms','status','statusLabel']}
            checks.update({
                'predictedNt': nr.get('predicted_nt'),
                'predictedNtConfidence': nr.get('predicted_nt_confidence'),
                'celltypePredictedNt': nr.get('celltype_predicted_nt'),
                'celltypePredictedNtConfidence': nr.get('celltype_predicted_nt_confidence'),
                'consensusNt': nr.get('consensus_nt'),
                'totalNtPredictions': nr.get('total_nt_predictions'),
                'celltypeTotalNtPredictions': nr.get('celltype_total_nt_predictions')})
            for field, flat in checks.items():
                actual=live[body_id].get(field)
                status='EXACT_MATCH' if flat==actual else 'MISMATCH'
                explanation=''
                difference=None
                if isinstance(flat,float) and isinstance(actual,(float,int)):
                    difference=actual-flat
                    f32=struct.unpack('f',struct.pack('f',flat))[0]
                    if status=='MISMATCH' and abs(actual-f32)<1e-14:
                        status='EXPLAINED_DIFFERENCE'
                        explanation='neuPrint value matches float32 round-trip of flat-file float64 within 1e-14'
                live_comparisons.append(dict(body_id=str(body_id),field=field,
                    flat_file_value=flat,neuprint_value=actual,difference=difference,
                    status=status,explanation=explanation))
        if pr:
            comparisons.append(dict(body_id=str(body_id), paper_type=pr['cell_type'],
                v1_type=row['type'], type_status='EXACT_MATCH' if pr['cell_type']==row['type'] else 'MISMATCH',
                paper_root_side=pr['side'], v1_side_label=side, v1_side_property=side_source,
                side_label_status='EXACT_MATCH' if pr['side']==side else 'MISMATCH',
                side_semantics='same rootSide property' if side_source=='rootSide' else 'paper Root_Side compared with v1 somaSide; labels only',
                paper_nerve=pr['nerve'], v1_nerve=row.get(nerve_source),
                nerve_status='EXACT_MATCH' if pr['nerve']==row.get(nerve_source) else 'MISMATCH',
                paper_reference=f"{pr['sheet']}!row {pr['excel_row']}"))
        if nr and nr['predicted_nt'] != nr['consensus_nt']:
            nt_differences.append(dict(body_id=str(body_id),cell_type=row['type'],
                predicted_nt=nr['predicted_nt'],confidence=nr['predicted_nt_confidence'],
                celltype_predicted_nt=nr['celltype_predicted_nt'],ground_truth=nr['ground_truth'],
                consensus_nt=nr['consensus_nt'],
                difference_kind='BODY_UNCLEAR_CONSENSUS_ASSIGNED' if nr['predicted_nt']=='unclear' else 'BODY_PREDICTION_DIFFERS_FROM_CONSENSUS'))
    write_csv(out/'resolved_bodies.csv', resolved, list(resolved[0]))
    write_csv(out/'table_s1_comparison.csv', comparisons, list(comparisons[0]))
    write_csv(out/'nt_field_differences.csv', nt_differences, list(nt_differences[0]))
    if live_comparisons:
        write_csv(out/'neuprint_annotation_comparison.csv',live_comparisons,list(live_comparisons[0]))
    paper_ids=set(paper_by_id)
    summary=dict(timestamp=timestamp,scope='INITIAL_VALIDATION_ONLY',dataset=DATASET,
        server='https://neuprint.janelia.org',dataset_uuid=metadata['uuid'],
        metadata_last_mod=metadata['last-mod'],dataset_listing_verified=True,
        authenticated_custom_query_verified=live is not None,custom_query_http_status=200 if live is not None else 401,
        neuprint_comparison_counts=dict(collections.Counter(r['status'] for r in live_comparisons)),
        neuprint_unexplained_mismatches=[r for r in live_comparisons if r['status']=='MISMATCH'],
        annotation_rows=len(annotations),resolved_body_count=len(resolved),
        counts={t:sum(r['cell_type']==t for r in resolved) for t in TARGETS},
        side_counts={t:dict(collections.Counter(r['side'] for r in resolved if r['cell_type']==t)) for t in TARGETS},
        paper_target_body_count=len(paper),paper_ids_missing_from_selected=sorted(paper_ids-selected_ids),
        target_sensory_motor_ids_not_in_table=sorted(r['bodyId'] for r in selected if r['type'].startswith(('LB3','MN')) and r['bodyId'] not in paper_ids),
        type_mismatches=[r for r in comparisons if r['type_status']!='EXACT_MATCH'],
        side_label_mismatches=[r for r in comparisons if r['side_label_status']!='EXACT_MATCH'],
        nerve_mismatches=[r for r in comparisons if r['nerve_status']!='EXACT_MATCH'],
        nt_difference_counts=dict(collections.Counter(r['difference_kind'] for r in nt_differences)),
        nt_missing_bodies=sorted(selected_ids-set(nt)),
        experiments_run=False,simulations_run=False)
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    git = subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    inputs=[annotation_path,nt_path,table_path,dataset_path,Path(__file__),ROOT/'docs/RESEARCH_PROTOCOL.md']
    if live is not None: inputs.extend([live_path,meta_path])
    manifest=dict(timestamp=timestamp,experiment='INITIAL_VALIDATION_ONLY',git_commit=git.stdout.strip() if git.returncode==0 else None,
        git_state='uncommitted checkpoint',dataset=DATASET,dataset_version='v1.0',dataset_uuid=metadata['uuid'],
        python=sys.version,operating_system=platform.platform(),package_versions={'pyarrow':pyarrow.__version__},
        random_seed=None,randomness='none; deterministic annotation comparison',
        config={'target_types':TARGETS,'filters':'exact annotation type membership; no status exclusion',
                'source_annotation_filename_minconf':0.5,'analysis_confidence_threshold':None},
        input_hashes={str(p.relative_to(ROOT)):sha(p) for p in inputs},
        output_hashes={str(p.relative_to(ROOT)):sha(p) for p in out.iterdir()},
        output_directory=str(out.relative_to(ROOT)))
    manifest['config_hash']=hashlib.sha256(json.dumps(manifest['config'],sort_keys=True).encode()).hexdigest()
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    with (ROOT/'logs/run_manifest.jsonl').open('a') as f:f.write(json.dumps(manifest)+'\n')
    with (ROOT/'logs/query_log.jsonl').open('a') as f:
        f.write(json.dumps(dict(timestamp=timestamp,experiment='INITIAL_VALIDATION_ONLY',purpose='Local body-ID and metadata verification',
            dataset=DATASET,query='exact type selection and Table S1 join by integer body ID',parameters={'types':TARGETS},
            returned_row_count=len(resolved),output_file=str((out/'resolved_bodies.csv').relative_to(ROOT)),
            sha256=sha(out/'resolved_bodies.csv'),errors=None,transport='local official flat files'))+'\n')
    print(json.dumps(summary,indent=2))
    print('OUTPUT_DIRECTORY='+str(out.relative_to(ROOT)))


if __name__ == '__main__':
    main()
