"""Read-only source/access retrieval for the initial checkpoint; no experiments.

Each response has its own file, checksum, URL, and timestamp. Never overwrites
an earlier response. No credentials are accepted or recorded by this helper.
"""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def fetch(url, output, purpose, dataset=None, payload=None, timeout=90):
    path = ROOT / output
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    record = dict(timestamp=dt.datetime.now(dt.timezone.utc).isoformat(),
                  experiment='INITIAL_VALIDATION_ONLY', purpose=purpose,
                  dataset=dataset, query=url if payload is None else payload,
                  url=url, parameters={}, returned_row_count=None,
                  output_file=output, authentication='anonymous')
    cmd = ['curl', '-L', '--max-time', str(timeout), '-sS', '-o', str(path),
           '-w', '%{http_code}', url]
    if payload is not None:
        cmd += ['-H', 'Content-Type: application/json', '--data-binary', json.dumps(payload)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    record['http_status'] = result.stdout
    record['errors'] = result.stderr or (None if result.stdout == '200' else 'HTTP ' + result.stdout)
    if path.exists():
        record['bytes'] = path.stat().st_size
        record['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        try:
            data = json.loads(path.read_text())
            if isinstance(data, dict) and isinstance(data.get('data'), list):
                record['returned_row_count'] = len(data['data'])
        except (ValueError, UnicodeError):
            pass
    log = ROOT / 'logs' / ('query_log.jsonl' if dataset else 'source_fetch_log.jsonl')
    with log.open('a') as f:
        f.write(json.dumps(record) + '\n')
    print(json.dumps(record))
    return record


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('url')
    parser.add_argument('output')
    parser.add_argument('--purpose', required=True)
    parser.add_argument('--dataset')
    parser.add_argument('--payload')
    args = parser.parse_args()
    fetch(args.url, args.output, args.purpose, args.dataset,
          json.loads(args.payload) if args.payload else None)
