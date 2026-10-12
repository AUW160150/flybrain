from __future__ import annotations
import hashlib
import json
import os
import platform
import resource
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(8 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

def digest(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()

def read_json(path: Path) -> Any:
    return json.loads(Path(path).read_text())

def atomic_json(path: Path, obj: Any) -> None:
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(obj, sort_keys=True, indent=2, allow_nan=False) + '\n')
    os.replace(temp, path)

def atomic_torch(path: Path, obj: Any) -> None:
    temp = path.with_suffix(path.suffix + '.tmp')
    torch.save(obj, temp); os.replace(temp, path)

def seed_for(stream: str, *keys: int) -> int:
    return int(digest([stream, *keys])[:8], 16) % (2**31 - 1)

def revision() -> str | None:
    p = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True)
    return p.stdout.strip() if p.returncode == 0 else None

def code_hash() -> str:
    files = sorted((ROOT / 'src').rglob('*.py')) + sorted((ROOT / 'configs').glob('*.yaml')) + [ROOT / 'pyproject.toml']
    return digest({str(p.relative_to(ROOT)): sha256(p) for p in files})

def plan_receipt() -> dict:
    p = ROOT / 'docs/analysis_plan.md'
    return {'sha256': sha256(p), 'git_revision': revision(), 'recorded_utc': now()}

def sync(device: str | torch.device) -> None:
    name = str(device)
    if name.startswith('cuda'): torch.cuda.synchronize()
    if name.startswith('mps'): torch.mps.synchronize()

def setup(device: str = 'cpu', threads: int = 2) -> dict:
    if device.startswith('cuda') and not torch.cuda.is_available():
        raise RuntimeError('CUDA unavailable; choose CPU explicitly for every arm.')
    if device.startswith('mps') and not torch.backends.mps.is_available():
        raise RuntimeError('MPS unavailable; choose CPU explicitly for every arm.')
    torch.set_num_threads(threads)
    torch.use_deterministic_algorithms(True)
    torch.set_float32_matmul_precision('highest')
    return {'device': device, 'precision': 'float32', 'threads': threads,
            'deterministic_algorithms': True, 'matmul_precision': 'highest'}

def environment() -> dict:
    import importlib.metadata
    packages = ['torch','numpy','scipy','pyarrow','networkx','pytest','matplotlib']
    memory = None
    try:
        memory = os.sysconf('SC_PHYS_PAGES') * os.sysconf('SC_PAGE_SIZE')
    except (OSError, ValueError):
        p = subprocess.run(['sysctl','-n','hw.memsize'], capture_output=True, text=True)
        if p.returncode == 0: memory = int(p.stdout)
    return {'utc': now(), 'python': platform.python_version(), 'os': platform.platform(),
            'machine': platform.machine(), 'processor': platform.processor(), 'cpus': os.cpu_count(),
            'ram_bytes': memory, 'ram_note': None if memory else 'Hardware query unavailable in sandbox',
            'disk_free_bytes': shutil.disk_usage(ROOT).free,
            'cuda_available': torch.cuda.is_available(), 'mps_available': torch.backends.mps.is_available(),
            'versions': {p: importlib.metadata.version(p) for p in packages}, 'git_revision': revision()}

def peak_rss_bytes() -> int:
    n = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(n if platform.system() == 'Darwin' else n * 1024)

def load_config(name: str) -> dict:
    # JSON is a strict subset of YAML; avoid an extra parser/dependency.
    p = Path(name)
    return read_json(p if p.is_file() else ROOT / 'configs' / f'{name}.yaml')
