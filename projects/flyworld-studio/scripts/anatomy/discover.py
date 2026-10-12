"""Bounded local inventory. No network, source writes, pickle loading or extraction."""
import csv
import hashlib
import io
import json
import os
import re
import sqlite3
import zipfile
from pathlib import Path
from contracts import sha256

FORMATS = {'.swc', '.eswc', '.obj', '.ply', '.stl', '.off', '.glb', '.gltf', '.h5', '.hdf5',
           '.n5', '.zarr', '.npz', '.npy', '.json', '.feather', '.parquet', '.csv', '.zip', '.gz', '.bz2', '.xz', '.tar', '.sqlite', '.db'}
GEOMETRY = {'.swc', '.eswc', '.obj', '.ply', '.stl', '.off', '.glb', '.gltf'}
EXCLUDED = {'.git', 'node_modules', '__pycache__', '.venv', '.cache', 'dist', '.pytest_cache'}
COLUMNS = ['path','format','size_bytes','checksum','candidate_dataset','candidate_version','candidate_body_id',
           'candidate_region','contains_coordinates','contains_connectivity','contains_metadata','confidence','notes']


def paths_in(roots):
    for root in roots:
        for current, dirs, files in os.walk(root, followlinks=False):
            dirs[:] = sorted(d for d in dirs if d not in EXCLUDED and not d.startswith('.venv')
                             and not (Path(current) / d).is_symlink())
            for name in sorted(files):
                p = Path(current) / name
                if name.startswith('.env') or p.is_symlink():
                    continue
                yield p


def fields_in(value, depth=0):
    if depth > 5:
        return set()
    if isinstance(value, dict):
        return set(value) | set().union(*(fields_in(v, depth+1) for v in value.values()))
    if isinstance(value, list):
        return set().union(*(fields_in(v, depth+1) for v in value[:3]))
    return set()


def describe(path, content=None):
    suffix = path.suffix.lower()
    notes, fields = [], set()
    coords = connection = metadata = 'UNKNOWN'
    if suffix in GEOMETRY:
        coords, connection, metadata = 'YES', 'NO', 'YES'
        notes.append('Geometry candidate; identity requires receipt/source verification. SWC parent links are cables, not synaptic connectivity.')
    elif suffix in {'.csv', '.json'}:
        try:
            if content is not None:
                raw = content.decode('utf8')
            elif suffix == '.csv':
                with path.open() as f:
                    raw = f.readline()
            elif path.stat().st_size <= 8 * 1024 * 1024:
                raw = path.read_text()
            else:
                raw = None
                notes.append('Large JSON hashed; content not fully parsed.')
            if raw is not None:
                if suffix == '.csv':
                    fields = set(next(csv.reader(io.StringIO(raw)), []))
                else:
                    fields = fields_in(json.loads(raw))
                metadata = 'YES'
                notes.append('Fields sampled: ' + ','.join(sorted(fields)[:65]))
        except (ValueError, UnicodeError) as exc:
            notes.append('Content parse failed: ' + type(exc).__name__)
    elif suffix in {'.feather', '.parquet'}:
        import pyarrow as pa
        import pyarrow.parquet as pq
        with pa.memory_map(str(path), 'r') as source:
            schema = pa.ipc.open_file(source).schema if suffix == '.feather' else pq.read_schema(source)
        fields = set(schema.names)
        metadata = 'YES'
        notes.append('Column metadata only; full graph not loaded: ' + ','.join(sorted(fields)))
    elif suffix == '.npy':
        import numpy as np
        with path.open('rb') as source:
            version = np.lib.format.read_magic(source)
            reader = {(1, 0): np.lib.format.read_array_header_1_0, (2, 0): np.lib.format.read_array_header_2_0}.get(version)
            if reader:
                shape, fortran, dtype = reader(source)
                notes.append(f'Array header only: shape={shape}, dtype={dtype}; values not interpreted as geometry.')
            else:
                notes.append(f'Array header version {version} uninspected; file checksum retained.')
    elif suffix in {'.sqlite', '.db'}:
        with sqlite3.connect(path.as_uri() + '?mode=ro&immutable=1', uri=True) as database:
            definitions = [row[0] for row in database.execute("SELECT sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL")]
        metadata = 'YES'
        notes.append('Read-only table definitions, not geometry inference: ' + ' | '.join(definitions))
    if fields:
        coords = 'YES' if fields & {'somaLocation','tosomaLocation','points','position','coordinates','x','y','z'} else 'UNKNOWN'
        connection = 'YES' if fields & {'raw_synapse_count','rawSynapseCount','weight','edges','body_pre','body_post','bodyId_pre','bodyId_post'} else 'UNKNOWN'
        if fields & {'regions', 'regionId'}:
            notes.append('Region/position fields may be educational or abstract; no anatomy verification implied.')
    name = str(path)
    dataset = 'male-cns' if re.search(r'male-?cns', name, re.I) else ''
    version = 'v1.0' if 'v1.0' in name else ''
    match = re.match(r'([1-9][0-9]*)(?:\.|$)', path.name)
    return dict(candidate_dataset=dataset, candidate_version=version,
                candidate_body_id=match.group(1) if match else '', candidate_region='',
                contains_coordinates=coords, contains_connectivity=connection, contains_metadata=metadata,
                confidence='CANDIDATE_ONLY', notes='; '.join(notes))


def discover(roots):
    rows, snapshot, archives = [], {}, []
    for path in paths_in(roots):
        digest = sha256(path)
        snapshot[str(path)] = digest
        if path.suffix.lower() not in FORMATS:
            continue
        row = dict(path=str(path), format=path.suffix.lower()[1:], size_bytes=path.stat().st_size, checksum=digest)
        row.update(describe(path))
        rows.append(row)
        if path.suffix.lower() in {'.zip', '.npz'}:
            with zipfile.ZipFile(path) as archive:
                entries = archive.infolist()
                archives.append({'path': str(path), 'sha256': digest, 'members': [e.filename for e in entries],
                                 'geometry_members': [e.filename for e in entries if Path(e.filename).suffix.lower() in GEOMETRY]})
                for entry in entries:
                    suffix = Path(entry.filename).suffix.lower()
                    if entry.is_dir() or suffix not in FORMATS:
                        continue
                    # No extraction; large array members remain bounded header/name observations.
                    data = archive.read(entry) if entry.file_size <= 8 * 1024 * 1024 else None
                    child = dict(path=str(path) + '::' + entry.filename, format=suffix[1:], size_bytes=entry.file_size,
                                 checksum=hashlib.sha256(data).hexdigest() if data is not None else '')
                    child.update(describe(Path(entry.filename), data) if data is not None and suffix in {'.json','.csv'} else
                                 dict(candidate_dataset='',candidate_version='',candidate_body_id='',candidate_region='',
                                      contains_coordinates='UNKNOWN',contains_connectivity='UNKNOWN',contains_metadata='UNKNOWN',
                                      confidence='CANDIDATE_ONLY',notes='Archive member; not extracted or treated as an independent geometry mapping.'))
                    if data is None:
                        child['notes'] += ' Member >8 MiB; container checksum recorded, member content not read.'
                    rows.append(child)
    return rows, snapshot, archives


def csv_write(path, rows, columns):
    with Path(path).open('w', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == '__main__':
    project = Path(__file__).resolve().parents[2]
    workspace = project.parents[1]
    roots = [workspace/'data', workspace/'processed', workspace/'runs', workspace/'visualization',
             workspace/'Sugar/malecns_sugar_circuit_v1', project/'public']
    rows, snapshot, archives = discover(roots)
    csv_write(project/'docs/anatomy/LOCAL_ASSET_INVENTORY.csv', rows, COLUMNS)
    baseline = project/'data/anatomy/manifests/source-baseline.json'
    if baseline.exists():
        if json.loads(baseline.read_text()) != snapshot:
            raise ValueError('Source set/hash changed since baseline; keep original and investigate before replacing it')
    else:
        baseline.write_text(json.dumps(snapshot, indent=2)+'\n')
    (project/'data/anatomy/manifests/discovery.json').write_text(json.dumps({
        'roots':list(map(str,roots)), 'excluded_directories':sorted(EXCLUDED),
        'excluded_files':'Environment/credential files and symlinks; no traversal outside authorized roots.',
        'inventory_rows':len(rows),'protected_files':len(snapshot),'archives':archives,
        'directory_containers_found': [str(p) for root in roots for p in root.rglob('*') if p.is_dir() and p.suffix in {'.n5','.zarr'}],
        'content_scope':'CSV headers; JSON <=8 MiB sampled keys; columnar schemas; NPY headers; archive directory and bounded members. UNKNOWN is not absence.',
    },indent=2)+'\n')
    print(json.dumps({'inventory_rows':len(rows),'protected_files':len(snapshot),'archives':len(archives)}))
