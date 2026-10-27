"""Extract FlyHash's per-configuration work counters from the EXP3 B2 harness result files.

ANN-Benchmarks stores what a module's get_additional() returns as HDF5 attributes; the export CSV
(b2/export.csv) does not carry them. This script copies the attributes verbatim (no arithmetic)
into one CSV in the site's vendored sources (the experiment repository is not written to), with each
source file's SHA-256 so every row can be traced back to its result file.

Run with an interpreter that has h5py, from the workspace root:

    fly_retrieval/.venv/bin/python -I portfolio/scripts/extract_b2_touched.py fly_retrieval
"""
from __future__ import annotations

import csv
import hashlib
import sys
from pathlib import Path

import h5py

FIELDS = ["dataset", "name", "candidates_touched_per_query", "exact_distances_per_query",
          "result_file", "result_file_sha256"]


def main(root: str) -> None:
    root_p = Path(root).resolve()
    files = sorted((root_p / "b2" / "harness" / "results").glob("*/10/flyhash/*.hdf5"))
    if not files:
        raise SystemExit("no FlyHash result files found")
    rows = []
    for f in files:
        with h5py.File(f, "r") as h:
            a = h.attrs
            rows.append({
                "dataset": str(a["dataset"]),
                "name": str(a["name"]),
                "candidates_touched_per_query": repr(float(a["candidates_touched_per_query"])),
                "exact_distances_per_query": repr(float(a["exact_distances_per_query"])),
                "result_file": f.relative_to(root_p).as_posix(),
                "result_file_sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
            })
    rows.sort(key=lambda r: (r["dataset"], r["name"]))
    out = (Path(__file__).resolve().parents[1] / "site" / "src" / "results" / "sources" / "fly_retrieval"
           / "b2" / "flyhash_candidates_touched.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} rows -> {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "fly_retrieval")
