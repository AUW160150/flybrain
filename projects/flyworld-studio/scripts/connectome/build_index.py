"""Build a server-only query index from pinned official files; never alter originals."""
import argparse
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.feather as feather

PROJECT = Path(__file__).resolve().parents[2]
BASE = 'https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/'
FILES = {
    'annotations': ('body-annotations-male-cns-v1.0-minconf-0.5.feather', '2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2'),
    'weights': ('connectome-weights-male-cns-v1.0-minconf-0.5.feather', 'e35da783d1c686b2b58b3b87cd6a403ae43bfcfba8bff28e08ef752c1a56afc1'),
}

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(4*1024*1024), b''): h.update(b)
    return h.hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=PROJECT.parents[1]/'data/flat-connectome')
    parser.add_argument('--output', type=Path, default=PROJECT/'data/connectome/index.sqlite')
    args = parser.parse_args()
    if args.output.exists(): raise SystemExit('Index exists; choose a new --output to rebuild without overwriting it.')
    sources = {}
    for kind, (name, expected) in FILES.items():
        path = args.source/name
        actual = digest(path)
        if actual != expected: raise ValueError('Pinned source checksum mismatch: '+name)
        sources[kind] = {'name': name, 'sha256': actual, 'url': BASE+name, 'bytes': path.stat().st_size}
    table = feather.read_table(args.source/FILES['annotations'][0])
    traced = table.filter(pc.equal(table['status'], 'Traced'))
    ids = traced['bodyId'].combine_chunks()
    # The catalogue is explicitly the source's Traced population, not every segment/glial row.
    records = traced.to_pylist()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix('.building.sqlite')
    if temporary.exists(): raise SystemExit('Incomplete index exists: '+str(temporary))
    db = sqlite3.connect(temporary)
    db.executescript('''PRAGMA journal_mode=OFF; PRAGMA synchronous=OFF;
        CREATE TABLE neurons (body INTEGER PRIMARY KEY, type TEXT, instance TEXT, search TEXT, record TEXT NOT NULL);
        CREATE TABLE edges (source INTEGER NOT NULL, target INTEGER NOT NULL, weight INTEGER NOT NULL);
        CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);''')
    for row in records:
        record = {k: row.get(k) for k in ['type','instance','synonyms','status','superclass','class','subclass','somaSide','rootSide','somaNeuromere','entryNerve','exitNerve','somaLocation','tosomaLocation']}
        record['bodyId'] = str(row['bodyId'])
        text = ' '.join(str(v) for v in [record['bodyId'],record['type'],record['instance'],record['synonyms'],record['superclass'],record['class']] if v).lower()
        db.execute('INSERT INTO neurons VALUES (?,?,?,?,?)',(row['bodyId'],row['type'],row['instance'],text,json.dumps(record,allow_nan=False,separators=(',',':'))))
    db.commit()
    reader = pa.ipc.open_file(args.source/FILES['weights'][0])
    raw_count = edge_count = weight_sum = 0
    for i in range(reader.num_record_batches):
        batch = reader.get_batch(i)
        raw_count += batch.num_rows
        filtered = batch.filter(pc.and_(pc.is_in(batch['body_pre'],value_set=ids),pc.is_in(batch['body_post'],value_set=ids)))
        cols = [filtered[c].to_pylist() for c in ['body_pre','body_post','weight']]
        rows = list(zip(*cols))
        if any(w < 1 for _,_,w in rows): raise ValueError('Invalid connection count')
        db.executemany('INSERT INTO edges VALUES (?,?,?)', rows)
        edge_count += len(rows); weight_sum += sum(cols[2])
        if i % 200 == 0:
            db.commit(); print(f'Indexed batch {i}/{reader.num_record_batches}: {edge_count:,} traced-to-traced edges',flush=True)
    db.commit()
    print('Building source and target indexes…',flush=True)
    db.executescript('CREATE UNIQUE INDEX edge_pair ON edges(source,target); CREATE INDEX edge_in ON edges(target,weight DESC); CREATE INDEX edge_out ON edges(source,weight DESC); CREATE INDEX neuron_type ON neurons(type COLLATE NOCASE);')
    manifest = {'schemaVersion':1,'dataset':'male-cns:v1.0','uuid':'4b2087c0fbe046bfaf0d60bc970e3e5d',
        'createdAt':datetime.now(timezone.utc).isoformat(),'sources':sources,'neuronCount':len(records),
        'annotationRows':table.num_rows,'edgeCount':edge_count,'synapseCount':weight_sum,
        'sourceEdgeRows':raw_count,'excludedEdgeRows':raw_count-edge_count,'scope':'Traced neurons and induced raw connections',
        'synapseConfidence':0.5,'coordinateSpace':'MaleCNS native EM','units':'8 nm',
        'orientationStatus':'ORIENTATION_UNVERIFIED','scientificLabel':'RAW_STRUCTURAL'}
    db.execute('INSERT INTO metadata VALUES (?,?)',('manifest',json.dumps(manifest)))
    db.commit()
    if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok': raise ValueError('Index integrity check failed')
    db.close(); temporary.rename(args.output)
    manifest['indexSha256'] = digest(args.output)
    args.output.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:manifest[k] for k in ['neuronCount','edgeCount','synapseCount','sourceEdgeRows']},indent=2),flush=True)

if __name__ == '__main__': main()
