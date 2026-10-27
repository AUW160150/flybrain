"""Copy the EXP1-EXP3 result files the result pages cite into site/src/results/sources/, byte for byte.

The copies are what the site serves (every figure's source line links to one) and what
scripts/build_figures.py reads. Paths keep their layout relative to the Flybrain workspace,
so `fly_track/reports/stage1_headroom.md` is served at /results/sources/fly_track/reports/stage1_headroom.md.

    python3 scripts/vendor_results.py [--workspace ..]

The SHA-256 of every copy is checked against the original after copying; the manifest
(reports/figure_data_manifest.json) records the same digests and check_results_site.py re-checks them.
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEST = REPO / "site" / "src" / "results" / "sources"

# Every file a figure or page number is drawn from. Inventory-only files (read, not plotted) are
# listed in the manifest with their hashes but are not copied.
SOURCES = [
    "fly_track/reports/report.md",
    "fly_track/reports/stage1_headroom.md",
    "fly_track/reports/exp1c/g1.json",
    "fly_track/reports/stage1b_occlusion.md",
    "fly_track/reports/exp1c/g1b.json",
    "fly_track/reports/exp1c/power.json",
    "fly_track/reports/exp1c/activity.json",
    "fly_track/docs/exp1_continuation_preregistration.md",
    "fly_track/raw_results/exp2/conditional_seed_pilot/pilot_analysis.json",
    "fly_track/reports/exp2_conditional_power.json",
    "fly_track/reports/exp2_conditional_report.md",
    "fly_retrieval/reports/exp3_trackA_novelty.md",
    "fly_retrieval/reports/trackA_summary.json",
    "fly_retrieval/reports/exp3_trackB_connectome.md",
    "fly_retrieval/b2/export.csv",
    "fly_retrieval/reports/trackB2_summary.json",
    "fly_retrieval/reports/trackB2_costs.json",
    "fly_retrieval/reports/exp3_trackC_skew.md",
    "fly_retrieval/reports/trackC_summary.json",
    "fly_retrieval/docs/exp3_analysis.md",
    "fly_retrieval/docs/exp3_preregistration.md",
]
# Written straight into DEST by scripts/extract_b2_touched.py (HDF5 attributes, copied verbatim).
DERIVED = ["fly_retrieval/b2/flyhash_candidates_touched.csv"]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", default=str(REPO.parent))
    ws = Path(ap.parse_args().workspace).resolve()
    for rel in SOURCES:
        src, dst = ws / rel, DEST / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        a, b = sha256(src), sha256(dst)
        if a != b:
            raise SystemExit(f"copy mismatch for {rel}")
        print(f"{a}  {rel}")


if __name__ == "__main__":
    main()
