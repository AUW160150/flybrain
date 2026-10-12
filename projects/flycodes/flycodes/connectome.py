"""Retain all Traced neurons and every recorded edge between them, including loops."""
from pathlib import Path
from collections import Counter
import csv
import time
import numpy as np
import pyarrow as pa
import pyarrow.feather as feather
import scipy.sparse as sp
from .common import ROOT, now, sha256, write_json, read_json

ANNOTATIONS = 'body-annotations-male-cns-v1.0-minconf-0.5.feather'
WEIGHTS = 'connectome-weights-male-cns-v1.0-minconf-0.5.feather'
BASE = 'https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/'

def prepare(raw, destination=None):
    raw = Path(raw).resolve()
    out = Path(destination or ROOT / 'data/graph')
    out.mkdir(parents=True, exist_ok=True)
    if (out / 'manifest.json').exists():
        return read_json(out / 'manifest.json')
    start = time.perf_counter()
    table = feather.read_table(raw / ANNOTATIONS).to_pydict()
    keep = np.asarray([s == 'Traced' for s in table['status']])
    ids = np.asarray(table['bodyId'], dtype=np.int64)[keep]
    order = np.argsort(ids)
    ids = ids[order]
    if len(np.unique(ids)) != len(ids):
        raise ValueError('Duplicate neuron IDs')
    n = len(ids)
    np.save(out / 'body_ids.npy', ids)
    original = np.flatnonzero(keep)[order]
    with (out / 'nodes.tsv').open('w') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['index', 'body_id', 'type', 'superclass', 'status'])
        for i, old in enumerate(original):
            writer.writerow([i, str(ids[i]), table['type'][old], table['superclass'][old], 'Traced'])
    pre_parts, post_parts, weight_parts = [], [], []
    rows = excluded = loops = 0
    with pa.memory_map(str(raw / WEIGHTS), 'r') as source:
        reader = pa.ipc.open_file(source)
        for b in range(reader.num_record_batches):
            batch = reader.get_batch(b)
            pre = batch.column('body_pre').to_numpy()
            post = batch.column('body_post').to_numpy()
            w = batch.column('weight').to_numpy()
            a, z = np.searchsorted(ids, pre), np.searchsorted(ids, post)
            good = (a < n) & (z < n)
            good &= (ids[np.minimum(a,n-1)] == pre) & (ids[np.minimum(z,n-1)] == post)
            if np.any(w[good] <= 0):
                raise ValueError('Nonpositive recorded count requires explicit policy')
            pre_parts.append(a[good].astype(np.int32))
            post_parts.append(z[good].astype(np.int32))
            weight_parts.append(w[good].astype(np.int32))
            rows += len(w)
            excluded += int((~good).sum())
            loops += int((pre[good] == post[good]).sum())
            if b % 300 == 0:
                print(f'graph audit: {rows:,} source rows scanned', flush=True)
    pre, post, counts = map(np.concatenate, (pre_parts, post_parts, weight_parts))
    del pre_parts, post_parts, weight_parts
    np.save(out / 'pre.npy', pre)
    np.save(out / 'post.npy', post)
    np.save(out / 'counts.npy', counts)
    # W[target, source]; raw integer counts remain separate and immutable.
    W = sp.csr_matrix((counts.astype(np.float32), (post, pre)), shape=(n,n))
    W.sort_indices()
    if W.nnz != len(counts):
        raise ValueError('Duplicate retained ordered pairs: require explicit aggregation policy')
    np.save(out / 'csr_indptr.npy', W.indptr)
    np.save(out / 'csr_indices.npy', W.indices)
    np.save(out / 'csr_counts.npy', W.data)
    incoming = np.asarray(W.sum(axis=1)).ravel()
    outgoing = np.asarray(W.sum(axis=0)).ravel()
    files = {p.name: sha256(p) for p in sorted(out.glob('*.npy'))}
    files['nodes.tsv'] = sha256(out / 'nodes.tsv')
    manifest = {
        'created_at': now(), 'release': 'male-cns:v1.0', 'scope': 'all status=Traced neurons in cached annotations',
        'neurons': n, 'annotation_rows': len(keep), 'source_edge_rows': rows,
        'directed_edges': len(counts), 'recorded_synapse_count_sum': int(counts.sum(dtype=np.int64)),
        'excluded_endpoint_rows': excluded, 'self_edges_retained': loops,
        'minimum_count': int(counts.min()), 'status_counts': dict(Counter(str(x) for x in table['status'])),
        'isolated_neurons': int(((incoming == 0) & (outgoing == 0)).sum()),
        'max_incoming_count': float(incoming.max()), 'files': files,
        'raw_sources': [{'path': str(raw / name), 'url': BASE + name, 'sha256': sha256(raw / name),
                         'bytes': (raw / name).stat().st_size, 'original_retrieval_time': None}
                        for name in (ANNOTATIONS, WEIGHTS)],
        'filter': 'both endpoints status=Traced; no strength threshold; preserve self-connections',
        'license': 'CC BY 4.0', 'catalogue': 'https://male-cns.janelia.org/download/',
        'counts_are': 'synapse counts, not measured physiological efficacies',
        'elapsed_seconds': time.perf_counter() - start,
    }
    write_json(out / 'manifest.json', manifest)
    return manifest

def load_graph(path=None, verify=True):
    path = Path(path or ROOT / 'data/graph')
    m = read_json(path / 'manifest.json')
    if verify:
        for name, expected in m['files'].items():
            if sha256(path / name) != expected:
                raise ValueError(f'Graph integrity failed: {name}')
    ids = np.load(path / 'body_ids.npy', mmap_mode='r')
    W = sp.csr_matrix((np.load(path / 'csr_counts.npy', mmap_mode='r'),
                       np.load(path / 'csr_indices.npy', mmap_mode='r'),
                       np.load(path / 'csr_indptr.npy', mmap_mode='r')), shape=(len(ids),len(ids)),copy=False)
    for a in (W.data, W.indices, W.indptr):
        a.flags.writeable = False
    return W, ids, m
