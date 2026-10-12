"""Recover primary sources and verify live release; never log credentials.

Creates a new audit run, not an Experiment 1R result. HTTP error bodies are
preserved as responses and must not be mistaken for scientific sources.
"""
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def fetch(url, path, purpose, payload=None, credential_path=None):
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    cmd = ['curl', '-L', '-sS', '--max-time', '45', '-o', str(path),
           '-w', '%{http_code}', url]
    config = ''
    if credential_path:
        raw = credential_path.read_text()
        candidates = re.findall(r'(?<![\w./-])[A-Za-z0-9_.-]{32,}(?![\w./-])', raw)
        if len(candidates) != 1:
            raise ValueError('Credential format is ambiguous; no values logged')
        token = candidates[0]
        # stdin avoids exposing the token in the process list or a temp file.
        config = 'header = "Authorization: Bearer ' + token + '"\n'
        cmd += ['--config', '-']
    if payload is not None:
        cmd += ['-H', 'Content-Type: application/json', '--data-binary', json.dumps(payload)]
    result = subprocess.run(cmd, input=config, capture_output=True, text=True)
    record = dict(timestamp=now(), experiment='METHOD_RECOVERY_AUDIT', purpose=purpose,
                  dataset=payload.get('dataset') if payload else None, url=url,
                  query=payload if payload else url, parameters={},
                  output_file=str(path.relative_to(ROOT)), http_status=result.stdout,
                  authentication='bearer via stdin' if credential_path else 'anonymous',
                  errors=result.stderr or (None if result.stdout == '200' else 'HTTP '+result.stdout),
                  returned_row_count=None)
    if path.exists():
        record.update(bytes=path.stat().st_size, sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        try:
            data = json.loads(path.read_text())
            if isinstance(data, dict) and isinstance(data.get('data'), list):
                record['returned_row_count'] = len(data['data'])
        except (ValueError, UnicodeError):
            pass
    log = ROOT/'logs'/('query_log.jsonl' if payload else 'source_fetch_log.jsonl')
    with log.open('a') as f:
        f.write(json.dumps(record)+'\n')
    print(json.dumps(record), flush=True)
    return record


def main():
    run_id = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run = ROOT/'results/method_recovery'/run_id
    run.mkdir(parents=True, exist_ok=False)
    (ROOT/'config/current_method_audit.txt').write_text(str(run.relative_to(ROOT))+'\n')
    payload = json.loads((ROOT/'results/structural/20261006T180116Z/queries/meta_start.json').read_text())
    (run/'meta_query.json').write_text(json.dumps(payload, indent=2)+'\n')
    record = fetch('https://neuprint.janelia.org/api/custom/custom', run/'meta_start.json',
                   'Verify target release before method and weight audit', payload, ROOT/'.venv/.env')
    if record['http_status'] != '200':
        raise RuntimeError('Live dataset identity not verified')
    response = json.loads((run/'meta_start.json').read_text())
    meta = dict(zip(response['columns'], response['data'][0]))
    assert meta['dataset']+':'+meta['tag'] == 'male-cns:v1.0'
    assert meta['uuid'] == '4b2087c0fbe046bfaf0d60bc970e3e5d'
    (run/'dataset_identity.json').write_text(json.dumps(meta,indent=2)+'\n')
    sources = [
        ('https://www.cell.com/cell/fulltext/S0092-8674(26)00943-8','cell_response.html'),
        ('https://www.sciencedirect.com/science/article/pii/S0092867426009438','sciencedirect_response.html'),
        ('https://api.elsevier.com/content/article/pii/S0092867426009438?view=FULL&httpAccept=text/xml','elsevier_full_response.xml'),
        ('https://api.crossref.org/works/10.1016/j.cell.2026.08.016','crossref.json'),
        ('https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:42691996%20AND%20SRC:MED&format=json&resultType=core','europepmc.json'),
        ('https://ars.els-cdn.com/content/image/1-s2.0-S0092867426009438-mmc1.pdf','supplement.pdf'),
        ('https://ars.els-cdn.com/content/image/1-s2.0-S0092867426009438-mmc2.xlsx','table_s1.xlsx'),
        ('https://api.github.com/orgs/ribeiro-lab/repos?per_page=100','ribeiro_repos.json'),
        ('https://api.github.com/users/ibrahimtastekin/repos?per_page=100','tastekin_repos.json'),
        ('https://www.biorxiv.org/content/10.1101/2025.08.25.671814v2.full.pdf','preprint_response.bin'),
    ]
    for url, name in sources:
        fetch(url, run/'sources'/name, 'Re-open final paper, corrections, supplements and publication-associated code')


if __name__ == '__main__':
    main()
