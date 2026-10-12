"""Export the FlyWorld NPC sub-circuit to a compact binary the browser simulation can load.

Reads projects/flyworld-game/processed/circuit_npc.npz (+ groups and calibration) and writes
site/src/assets/circuit/circuit.bin and circuit-meta.json. Layout is documented in the JSON.
Run from the repo root with a Python that has numpy: python scripts/export_circuit.py
"""
import hashlib, json, os
from collections import deque
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'projects', 'flyworld-game', 'processed')
OUT = os.path.join(ROOT, 'site', 'src', 'assets', 'circuit')
MIN_W = 5

z = np.load(os.path.join(P, 'circuit_npc.npz'))
pre, post, w = z['pre'], z['post'], z['weight']
N = int(z['body_id'].shape[0])
keep = np.abs(w) >= MIN_W
pre, post, w = pre[keep], post[keep], w[keep]
order = np.argsort(pre, kind='stable'); pre, post, w = pre[order], post[order], w[order]
E = len(pre)
counts = np.bincount(pre, minlength=N)
indptr = np.concatenate([[0], np.cumsum(counts)]).astype(np.int32)
wi = np.clip(np.round(w), -32767, 32767).astype(np.int16)
groups = {k: v for k, v in json.load(open(os.path.join(P, 'circuit_npc_groups.json'))).items() if len(v) > 0}

# layered layout for display only: hops from the sensory seeds, targets pushed to the far right
seeds = set()
for g in ("LC4", "LPLC2", "LC16", "LC6", "LC11", "ORN_DM1", "ORN_DM4", "ORN_DC1", "ORN_DA1", "ORN_VA1v", "LB3c"):
    seeds.update(groups.get(g, []))
depth = np.full(N, -1, np.int32); dq = deque()
for s in seeds: depth[s] = 0; dq.append(s)
while dq:
    u = dq.popleft()
    for e in range(indptr[u], indptr[u + 1]):
        v = post[e]
        if depth[v] < 0: depth[v] = depth[u] + 1; dq.append(v)
depth[depth < 0] = depth.max() + 1
types = z['type'].astype(str); sc = z['superclass'].astype(str)
rng = np.random.default_rng(7)
targets = set()
for g in ("DNp01", "DNp09", "MDN", "DNa01", "DNa02", "DNg11", "MN9"): targets.update(groups.get(g, []))
x = depth.astype(np.float64) + rng.uniform(-0.35, 0.35, N)
for t in targets: x[t] = depth.max() + 1
tkey = np.array([int(hashlib.md5(t.encode()).hexdigest()[:6], 16) / 0xffffff for t in types])
y = tkey + rng.normal(0, 0.02, N)
x = (x - x.min()) / (x.max() - x.min()); y = (y - y.min()) / (y.max() - y.min())
pos16 = np.round(np.stack([x, y], 1) * 65535).astype(np.uint16)

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, 'circuit.bin'), 'wb') as f:
    f.write(indptr.astype('<i4').tobytes()); f.write(post.astype('<i4').tobytes()); f.write(wi.astype('<i2').tobytes())
    f.write(pos16.astype('<u2').tobytes()); f.write(depth.astype('<u1').tobytes())
sc_names = sorted(set(sc)); sc_idx = {s: i for i, s in enumerate(sc_names)}
calib = json.load(open(os.path.join(P, 'calibration.json')))
meta = {"N": N, "E": E,
        "layout": {"indptr": "int32[N+1]", "post": "int32[E]", "weight": "int16[E] signed synapse count", "pos": "uint16[N][2] layered layout, not anatomy", "depth": "uint8[N] hops from sensory seeds"},
        "params": {"dt_ms": 1, "tau_ms": 20, "thr": 1.0, "reset": 0.0, "refr_ms": 2, "gain": calib["gain"], "min_w": MIN_W, "governor_frac": 0.05, "governor_steps": 20, "panel_amp": calib["panel_amp"], "ring_ms": 200},
        "groups": groups, "superclass_names": [str(s) for s in sc_names], "superclass": [sc_idx[s] for s in sc],
        "source": "processed/circuit_npc.npz from scripts/extract_circuits.py (MaleCNS v1.0, edges >= 5 synapses)",
        "calibration": {"turn_bias_per_dnp09_hz": calib["turn_bias_per_dnp09_hz"]}}
json.dump(meta, open(os.path.join(OUT, 'circuit-meta.json'), 'w'), separators=(',', ':'))
print(f"N={N} E={E} -> {OUT}")
