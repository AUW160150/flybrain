"""Load the whole-CNS graph and extract the NPC sensory-to-descending sub-circuit."""
import json
import numpy as np
import pyarrow.feather as pf
import scipy.sparse as sp

from .config import PATHS
from .groups import (build_groups, effective_side, group_counts, LOOM_SEEDS, ODOUR_SEEDS,
                     TASTE_SEEDS, TARGETS, FORCE_INCLUDE)


def load_whole(min_w=None, with_root_side=True):
    """Whole traced CNS as a dict of arrays. Edges filtered to abs(weight) >= min_w when given."""
    z = np.load(PATHS["whole_npz"], allow_pickle=True)
    types = z["type"].astype(str)
    superclass = z["superclass"].astype(str)
    soma_side = z["side"].astype(str)
    body_id = z["body_id"]
    if with_root_side:
        t = pf.read_table(PATHS["annotations"], columns=["bodyId", "rootSide"])
        root = dict(zip(t.column("bodyId").to_pylist(), t.column("rootSide").to_pylist()))
        root_side = np.array([root.get(int(b)) or "" for b in body_id], dtype=str)
    else:
        root_side = np.full(len(body_id), "", dtype=str)
    side = effective_side(soma_side, root_side)
    pre, post, w = z["pre"].astype(np.int64), z["post"].astype(np.int64), z["weight"].astype(np.float32)
    if min_w is not None:
        keep = np.abs(w) >= min_w
        pre, post, w = pre[keep], post[keep], w[keep]
    return dict(N=len(body_id), pre=pre, post=post, weight=w, body_id=body_id, type=types,
                superclass=superclass, side=side)


def bfs_dist(N, pre, post, seeds, max_hops, reverse=False):
    """Hop distance from the seed set along edges pre->post (or post->pre). -1 = unreached."""
    A = sp.csr_matrix((np.ones(len(pre), dtype=np.float32), (pre, post)), shape=(N, N))
    step = A.T.tocsr() if not reverse else A       # x @ A: from pre to post
    dist = np.full(N, -1, dtype=np.int16)
    frontier = np.zeros(N, dtype=np.float32)
    frontier[np.asarray(seeds)] = 1.0
    dist[np.asarray(seeds)] = 0
    for h in range(1, max_hops + 1):
        reached = (step @ frontier) > 0
        new = reached & (dist < 0)
        if not new.any():
            break
        dist[new] = h
        frontier = new.astype(np.float32)
    return dist


def _inf(d):
    return np.where(d < 0, 10_000, d).astype(np.int32)


def extract_circuit(whole, min_w=5, loom_hops=3, odour_hops=4, taste_hops=4, max_hops=5):
    """Apply the plan's recipe on an already edge-filtered whole graph. Returns (keep_mask, dists)."""
    N, pre, post = whole["N"], whole["pre"], whole["post"]
    g = build_groups(whole["type"], whole["superclass"], whole["side"])
    cat = lambda names: np.unique(np.concatenate([g[n] for n in names]))
    loom, odour, taste, targets = cat(LOOM_SEEDS), cat(ODOUR_SEEDS), cat(TASTE_SEEDS), cat(TARGETS)
    d_bwd = _inf(bfs_dist(N, pre, post, targets, max_hops, reverse=True))
    d_loom = _inf(bfs_dist(N, pre, post, loom, max_hops))
    d_odour = _inf(bfs_dist(N, pre, post, odour, max_hops))
    d_taste = _inf(bfs_dist(N, pre, post, taste, max_hops))
    keep = ((d_loom + d_bwd) <= loom_hops) | ((d_odour + d_bwd) <= odour_hops) | ((d_taste + d_bwd) <= taste_hops)
    keep &= ~((whole["superclass"] == "ol_intrinsic") & (d_loom >= 2))
    keep[np.concatenate([loom, odour, taste, targets])] = True
    keep[cat(FORCE_INCLUDE)] = True
    return keep, dict(d_bwd=d_bwd, d_loom=d_loom, d_odour=d_odour, d_taste=d_taste)


def remap(whole, keep):
    """Sub-graph restricted to keep, with local indices, plus local group dict."""
    orig = np.flatnonzero(keep)
    local = np.full(whole["N"], -1, dtype=np.int64)
    local[orig] = np.arange(len(orig))
    e = keep[whole["pre"]] & keep[whole["post"]]
    circ = dict(N=len(orig), pre=local[whole["pre"][e]].astype(np.int32), post=local[whole["post"][e]].astype(np.int32),
                weight=whole["weight"][e].astype(np.float32), orig_index=orig.astype(np.int64),
                body_id=whole["body_id"][orig], type=whole["type"][orig], superclass=whole["superclass"][orig],
                side=whole["side"][orig])
    circ["groups"] = build_groups(circ["type"], circ["superclass"], circ["side"])
    return circ


def save_circuit(circ, npz_path=None, groups_path=None):
    npz_path = npz_path or PATHS["circuit_npz"]
    groups_path = groups_path or PATHS["circuit_groups"]
    np.savez_compressed(npz_path, pre=circ["pre"], post=circ["post"], weight=circ["weight"],
                        orig_index=circ["orig_index"], body_id=circ["body_id"], type=circ["type"].astype(str),
                        superclass=circ["superclass"].astype(str), side=circ["side"].astype(str))
    with open(groups_path, "w") as f:
        json.dump({k: v.tolist() for k, v in circ["groups"].items()}, f)


def load_circuit(npz_path=None, groups_path=None):
    npz_path = npz_path or PATHS["circuit_npz"]
    groups_path = groups_path or PATHS["circuit_groups"]
    z = np.load(npz_path, allow_pickle=True)
    circ = {k: z[k] for k in z.files}
    circ["type"] = circ["type"].astype(str); circ["superclass"] = circ["superclass"].astype(str); circ["side"] = circ["side"].astype(str)
    circ["N"] = len(circ["orig_index"])
    with open(groups_path) as f:
        circ["groups"] = {k: np.asarray(v, dtype=np.int64) for k, v in json.load(f).items()}
    return circ


def save_groups_whole(whole, path=None):
    path = path or PATHS["groups_whole"]
    g = build_groups(whole["type"], whole["superclass"], whole["side"])
    with open(path, "w") as f:
        json.dump({k: v.tolist() for k, v in g.items()}, f)
    return group_counts(g)


def load_groups_whole(path=None):
    path = path or PATHS["groups_whole"]
    with open(path) as f:
        return {k: np.asarray(v, dtype=np.int64) for k, v in json.load(f).items()}
