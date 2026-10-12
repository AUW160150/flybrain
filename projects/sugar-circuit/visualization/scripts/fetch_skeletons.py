"""Fetch only allowlisted v1.0 SWCs; immutable responses, no healing or invented cable.

Public source: https://male-cns.janelia.org/download/# (Skeletons).
Optional fallback: neuPrint skeleton endpoint, NEUPRINT_APPLICATION_CREDENTIALS.
Never enumerate a whole dataset. A transport failure stops the batch.
"""
import argparse
import datetime as dt
import json
import os
import subprocess
import tempfile
from pathlib import Path
from model import ROOT, DATASET, UUID, sha, write_json

PUBLIC = 'https://storage.googleapis.com/flyem-male-cns/v1.0/segmentation/skeletons-malecns/skeletons-swc/'
API = 'https://neuprint.janelia.org/api/skeletons/skeleton/male-cns:v1.0/'


def parse_swc(path):
    points = {}
    for line in Path(path).read_text().splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        fields = line.split()
        if len(fields) != 7:
            raise ValueError('SWC must have seven columns')
        i, parent = int(fields[0]), int(fields[6])
        xyz = [float(x) for x in fields[2:5]]
        import math
        if i in points or not all(math.isfinite(x) for x in xyz):
            raise ValueError('Duplicate or invalid SWC point')
        points[i] = dict(xyz=xyz, parent=parent, radius=float(fields[5]))
    if not points:
        raise ValueError('Empty SWC')
    for i, row in points.items():
        if row['parent'] != -1 and (row['parent'] not in points or row['parent'] == i):
            raise ValueError('Broken SWC parent reference')
    # Do not join disconnected roots; parent direction is not physiological flow.
    finished = set()
    for i in points:
        seen = set(); current = i
        while current != -1 and current not in finished:
            if current in seen:
                raise ValueError('SWC parent cycle')
            seen.add(current); current = points[current]['parent']
        finished.update(seen)
    segments = [[row['xyz'], points[row['parent']]['xyz']] for row in points.values() if row['parent'] != -1]
    if not segments:
        raise ValueError('SWC contains no cable segments')
    return points, segments


def request(url, output, token=None):
    # Credentials never appear in argv, logs or returned exception messages.
    config = None
    command = ['curl', '--location', '--silent', '--show-error', '--max-time', '35',
               '--output', str(output), '--write-out', '%{http_code}', url]
    try:
        if token:
            if '\n' in token or '\r' in token:
                raise ValueError('Invalid credential format')
            with tempfile.NamedTemporaryFile(mode='w', delete=False, prefix='sugar-auth-', dir='/tmp') as f:
                config = Path(f.name)
                f.write('header = "Authorization: Bearer ' + token.replace('\\','\\\\').replace('"','\\"') + '"\n')
            os.chmod(config, 0o600)
            command += ['--config', str(config)]
        result = subprocess.run(command, capture_output=True, text=True, timeout=40)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return 28, '000', 'Transport timeout'
    finally:
        if config:
            config.unlink(missing_ok=True)


def fetch(model, output):
    if model['dataset'] != DATASET or model['dataset_uuid'] != UUID:
        raise ValueError('Wrong dataset')
    nodes = model['nodes']
    if not 0 < len(nodes) <= 500:
        raise ValueError('Only a small explicit body allowlist is permitted')
    output.mkdir(parents=True, exist_ok=False)
    (output / 'skeletons').mkdir(); (output / 'responses').mkdir()
    write_json(output / 'allowlist.json', [dict(body_id=n['body_id'], type=n['type'], side=n['side']) for n in nodes])
    statuses = []; queries = []; transport_block = None
    token = os.environ.get('NEUPRINT_APPLICATION_CREDENTIALS')
    for node in nodes:
        body = node['body_id']
        record = dict(body_id=body, type=node['type'], side=node['side'], dataset=DATASET,
                      dataset_uuid=UUID, status='BLOCKED', source=None, attempts=[])
        if transport_block:
            record['reason'] = 'Not attempted after transport failure: ' + transport_block
            statuses.append(record); continue
        for source, url, auth in [('official-release', PUBLIC + body + '.swc', None),
                                  ('neuprint', API + body + '?format=swc', token)]:
            dest = output / 'responses' / (body + '_' + source + '.response')
            code, http, err = request(url, dest, auth)
            q = dict(timestamp=dt.datetime.now(dt.timezone.utc).isoformat(), experiment='VISUALIZATION_ONLY',
                     purpose='Retrieve actual morphology for an explicitly allowlisted body',
                     dataset=DATASET, query=url, parameters={'body_id':body,'heal':False,'mirrored':False},
                     returned_row_count=None, output_file=str(dest.relative_to(ROOT)) if dest.exists() else None,
                     sha256=sha(dest) if dest.exists() else None, http_status=http, transport_exit=code,
                     errors=err or None, authentication='environment credential; omitted' if auth else 'anonymous')
            record['attempts'].append(url)
            if code == 0 and http == '200':
                try:
                    points, segments = parse_swc(dest)
                    target = output / 'skeletons' / (body + '.swc')
                    target.write_bytes(dest.read_bytes())
                    record.update(status='VERIFIED', source=url, file=str(target.relative_to(ROOT)),
                                  sha256=sha(target), points=len(points), segments=len(segments),
                                  coordinate_space='MaleCNS native EM', units='8 nm', healed=False)
                    q['returned_row_count'] = len(points)
                except (ValueError, UnicodeError) as exc:
                    record['reason'] = 'Invalid SWC: ' + str(exc)
            else:
                record['reason'] = f'HTTP {http}; transport {code}: {err}'
            queries.append(q)
            if record['status'] == 'VERIFIED':
                break
            if code in [5,6,7,28]:
                transport_block = record['reason']; break
        statuses.append(record)
        print(body, record['status'], flush=True)
    successful = sum(r['status'] == 'VERIFIED' for r in statuses)
    manifest = dict(dataset=DATASET, dataset_uuid=UUID, status='VERIFIED' if successful==len(nodes) else 'PARTIAL' if successful else 'BLOCKED',
                    verified_bodies=successful, requested_bodies=len(nodes), bodies=statuses,
                    source_documentation='https://male-cns.janelia.org/download/',
                    limitations='Centerline skeletons only; no synapse positions, no healing, no inferred physiological direction.')
    write_json(output / 'retrieval_manifest.json', manifest)
    for log in [output / 'query_log.jsonl', ROOT / 'logs/query_log.jsonl']:
        with log.open('a') as f:
            for q in queries:
                f.write(json.dumps(q) + '\n')
    return manifest


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True, help='New immutable retrieval directory within this project')
    a=p.parse_args()
    if not a.output.resolve().is_relative_to(ROOT):
        p.error('Output must be inside this project')
    result=fetch(json.loads(a.model.read_text()),a.output.resolve())
    print(json.dumps({k:result[k] for k in ['status','verified_bodies','requested_bodies']}))
