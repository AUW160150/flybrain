from __future__ import annotations
import hashlib, json, os, platform, resource, shutil, time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT.parent
EXPERIMENT = WORKSPACE / 'fly_connectome_lm'
REPORT = ROOT / 'reports/current'
RELEASE = 'male-cns:v1.0'

class EvidenceError(RuntimeError):
    def __init__(self, code: str, message: str, panel: str, recovery: str, evidence: Any = None):
        self.detail = dict(code=code, message=message, panel=panel, recovery=recovery, evidence=evidence)
        super().__init__(f'{code}: {message}')

def fail(code: str, message: str, panel: str = 'data', recovery: str = './visualization/viz validate', evidence=None):
    raise EvidenceError(code, message, panel, recovery, evidence)

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def digest(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''): h.update(chunk)
    return h.hexdigest()

def read(path: Path) -> Any:
    return json.loads(Path(path).read_text())

def atomic(path: Path, obj: Any) -> None:
    path = Path(path).resolve()
    if not path.is_relative_to(ROOT): fail('E_PROTECTED_INPUT_CHANGED', 'Output must be inside visualization/', 'protection')
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + '\n')
    os.replace(tmp, path)

def stable_copy(source: Path, directory: Path) -> tuple[Path, dict]:
    """Content-addressed copy, source stat and digest checked before AND after copying."""
    source = source.resolve(); directory = directory.resolve()
    if not source.is_relative_to(WORKSPACE) or not directory.is_relative_to(ROOT):
        fail('E_PROTECTED_INPUT_CHANGED', 'Copy outside configured workspace')
    directory.mkdir(parents=True, exist_ok=True)
    before = source.stat()
    if time.time() - before.st_mtime < 2:
        fail('E_CHECKPOINT_UNSTABLE_OR_UNSAFE', 'File is too recent to snapshot', 'checkpoint', 'Retry the same snapshot-run command after the writer publishes a stable file')
    h = sha(source); destination = directory / (h + source.suffix)
    if not destination.exists():
        tmp = directory / (h + '.partial')
        with source.open('rb') as f, tmp.open('wb') as g:
            shutil.copyfileobj(f, g, 1 << 20); g.flush(); os.fsync(g.fileno())
        after = source.stat()
        if (before.st_ino,before.st_size,before.st_mtime_ns) != (after.st_ino,after.st_size,after.st_mtime_ns) or sha(tmp) != h or sha(source) != h:
            tmp.unlink(missing_ok=True)
            fail('E_CHECKPOINT_UNSTABLE_OR_UNSAFE','Source changed while copying','checkpoint','Retry snapshot-run after an atomic checkpoint publication')
        os.replace(tmp,destination); destination.chmod(0o444)
    elif sha(destination) != h:
        fail('E_CHECKPOINT_UNSTABLE_OR_UNSAFE','Immutable snapshot hash differs','checkpoint')
    return destination, dict(source=str(source.relative_to(WORKSPACE)), path=str(destination.relative_to(ROOT)), sha256=h, size_bytes=before.st_size, snapshot_time=now(), source_mtime_ns=before.st_mtime_ns)

def checked(path: Path, expected: str) -> str:
    actual = sha(path)
    if actual != expected: fail('E_PROTECTED_INPUT_CHANGED', f'Hash mismatch: {path.name}', evidence={'expected':expected,'actual':actual})
    return actual

def body_id(value: Any) -> str:
    # Reject floating IDs even when numerically integral. SQLite source schema is int64.
    if isinstance(value, bool) or isinstance(value, float): fail('E_ID_PRECISION_LOSS','Biological ID must never pass through floating point')
    s = str(value)
    if not s.isascii() or not s.isdecimal() or str(int(s)) != s or int(s) > 2**63-1:
        fail('E_ID_PRECISION_LOSS',f'Expected canonical nonnegative decimal int64 ID: {s[:40]}')
    return s

def revision() -> str:
    return digest({str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'src').rglob('*')) if p.is_file() and '__pycache__' not in str(p)})

def rss() -> int:
    n=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(n if platform.system()=='Darwin' else n*1024)

class Budget:
    def __init__(self, mib: int = 512, seconds: int = 300, storage_gib: int = 64):
        if not 32 <= mib <= 4096 or not 1 <= seconds <= 86400 or not 1 <= storage_gib <= 128: raise ValueError('Invalid budget')
        self.bytes=mib*2**20; self.deadline=time.monotonic()+seconds; self.storage=storage_gib*2**30
    def check(self, paths=()):
        expanded=[]
        for p in paths:
            expanded.extend(p.rglob('*') if p.is_dir() else [p])
        size=sum(p.stat().st_size for p in set(expanded) if p.is_file())
        if rss()>self.bytes or time.monotonic()>self.deadline or size>self.storage:
            fail('E_RESOURCE_BUDGET','Bound reached; committed batches remain resumable','ingestion','Rerun the same command during a quiet period; increase only measured-safe limits', {'peak_rss':rss(),'storage_bytes':size})

def protect_inventory() -> dict:
    files=list((EXPERIMENT/'src').rglob('*.py'))+list((EXPERIMENT/'configs').glob('*'))+list((EXPERIMENT/'data/processed').glob('fly-*'))
    files += [EXPERIMENT/'requirements.lock',EXPERIMENT/'pyproject.toml',EXPERIMENT/'docs/analysis_plan.md']
    return {str(p.relative_to(WORKSPACE)):sha(p) for p in sorted(files) if p.is_file()}
