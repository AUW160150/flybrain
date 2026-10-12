from __future__ import annotations
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def now():
    return datetime.now(timezone.utc).isoformat()

def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(8 << 20), b''):
            h.update(block)
    return h.hexdigest()

def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    tmp.replace(path)

def read_json(path):
    return json.loads(Path(path).read_text())

def event(run, kind, **fields):
    value = {'time': now(), 'event': kind, **fields}
    with (Path(run) / 'events.jsonl').open('a') as f:
        f.write(json.dumps(value, allow_nan=False) + '\n')
    print(json.dumps(value), flush=True)

def environment():
    import numpy, scipy, pyarrow, torch
    return {'python': sys.version, 'platform': platform.platform(),
            'packages': {m.__name__: m.__version__ for m in (numpy, scipy, pyarrow, torch)},
            'torch_threads': torch.get_num_threads(), 'device': 'cpu'}

def source_hashes():
    return {str(p.relative_to(ROOT)): sha256(p) for p in sorted((ROOT / 'flycodes').glob('*.py'))}
