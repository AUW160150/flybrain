"""A coordinate-shuffle control for the structural holdout, not physiology.

Preserve the neuron graph, source counts, type, side and held-out split. Permute
the remaining anchor-coordinate assignments within each type/side stratum.
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from scipy import sparse

from flyvision.evidence import sha256, write_json
from flyvision.mapping import ColumnMapper, choose_holdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Refusing to overwrite a control result")
    manifest = json.loads((args.run / "manifest.json").read_text())
    if manifest["status"] != "COMPLETE":
        raise ValueError("Incomplete baseline")
    needed = ["atlas.parquet", "edges.parquet", "source_columns.csv", "holdout_validation.json"]
    for name in needed:
        if sha256(args.run / name) != manifest["artifacts"][name]["sha256"]:
            raise ValueError(f"Baseline artifact changed: {name}")
    atlas = pd.read_parquet(args.run / "atlas.parquet")
    held = choose_holdout(atlas)
    mapper = ColumnMapper(atlas, heldout=held)
    lookup = np.full(len(atlas), -1, dtype=np.int32)
    lookup[held] = np.arange(len(held))
    parts = [[], [], []]
    for batch in pq.ParquetFile(args.run / "edges.parquet").iter_batches(columns=["pre_index", "post_index", "synapse_count"]):
        pre, post, weights = [batch.column(i).to_numpy() for i in range(3)]
        keep = (lookup[post] >= 0) & (mapper.anchor_column[pre] >= 0) & (pre != post)
        keep &= (mapper.side[pre] == mapper.side[post]) & np.isin(mapper.side[pre], ["L", "R"])
        if keep.any():
            for dest, array in zip(parts, [pre[keep], lookup[post[keep]], weights[keep]]):
                dest.append(array.copy())
    sources, target_rows, weights = [np.concatenate(p) for p in parts]
    truth1 = atlas.iloc[held].assignedOlHex1.to_numpy()
    truth2 = atlas.iloc[held].assignedOlHex2.to_numpy()
    anchors = atlas.iloc[np.flatnonzero(mapper.anchor_column >= 0)]
    strata = [g.node_index.to_numpy(dtype=int) for _, g in anchors.groupby(["type", "visual_side_hint"], dropna=False)]

    def score(columns):
        matrix = sparse.coo_matrix((weights, (target_rows, columns[sources])), shape=(len(held), len(mapper.columns))).tocsr()
        pred = np.full(len(held), -1, dtype=int)
        for i in range(len(held)):
            start, end = matrix.indptr[i:i + 2]
            if end > start:
                pred[i] = matrix.indices[start:end][matrix.data[start:end].argmax()]
        valid = pred >= 0
        labels = mapper.columns.iloc[np.maximum(pred, 0)]
        correct = valid & (labels.hex1.to_numpy() == truth1) & (labels.hex2.to_numpy() == truth2)
        return {"exact_hex_matches": int(correct.sum()), "heldout": len(held), "supported": int(valid.sum()), "exact_rate_all_heldout": float(correct.mean())}

    observed = score(mapper.anchor_column)
    previous = json.loads((args.run / "holdout_validation.json").read_text())
    if observed["exact_hex_matches"] != previous["exact_hex_matches"]:
        raise ValueError("Control failed to reproduce the original holdout result")
    controls = []
    for seed in [101, 202, 303, 404, 505]:
        rng = np.random.default_rng(seed)
        columns = mapper.anchor_column.copy()
        for idx in strata:
            columns[idx] = rng.permutation(columns[idx])
        controls.append({"seed": seed, **score(columns)})
    result = {
        "kind": "WITHIN_TYPE_AND_SIDE_ANCHOR_COORDINATE_SHUFFLE",
        "baseline_manifest_sha256": sha256(args.run / "manifest.json"),
        "script_sha256": sha256(Path(__file__)),
        "inputs": {name: manifest["artifacts"][name] for name in needed},
        "observed": observed, "controls": controls,
        "physiological_validation": False,
        "interpretation": "Tests sensitivity to anchor-coordinate assignment within this dataset; five exploratory shuffles are not a physiological validation or a formal significance test.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_json(args.output, result)
    print(json.dumps({"observed": observed, "controls": controls}, indent=2))


if __name__ == "__main__":
    main()
