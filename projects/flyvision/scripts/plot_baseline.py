"""Render inspectable source-coordinate and validation plots, not a fly-view image."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def main():
    p = argparse.ArgumentParser()
    p.add_argument("run", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    atlas = pd.read_parquet(args.run / "atlas.parquet")
    validation = json.loads((args.run / "holdout_validation.json").read_text())
    fig, axes = plt.subplots(2, 2, figsize=(13, 10), layout="constrained")
    fig.suptitle("FlyVision • local MaleCNS sensory mapping baseline", fontsize=18, fontweight="bold")
    for ax, side in zip(axes[0], ["L", "R"]):
        g = atlas[atlas.type.eq("L1") & atlas.visual_side_hint.eq(side) & atlas.has_source_hex_pair]
        ax.scatter(g.assignedOlHex1, g.assignedOlHex2, s=9, c="#097c89")
        ax.set(title=f"L1 source columns • {side} side hint • {len(g):,} cells", xlabel="Source hex1", ylabel="Source hex2")
        ax.set_aspect("equal")
        ax.text(0.02, 0.02, "Source indexing frame; no visual-angle calibration", transform=ax.transAxes, fontsize=8)
    types = ["R1-R6", "L1", "L2", "Mi1", "Mi4", "Mi9", "Tm1", "Tm2", "T4a", "T5a"]
    coverage = [atlas.loc[atlas.type.eq(t), "has_source_hex_pair"].mean() * 100 for t in types]
    ax = axes[1, 0]
    ax.barh(types[::-1], coverage[::-1], color="#097c89")
    ax.set(xlim=(0, 105), xlabel="Cells with source hex coordinates (%)", title="Mapping availability for selected cell types")
    ax = axes[1, 1]
    table = pd.DataFrame(validation["groups"])
    table["exact_count"] = table.exact_rate_all_heldout * table.heldout
    agg = table.groupby("type")[["exact_count", "heldout"]].sum()
    grouped = (agg.exact_count / agg.heldout).sort_values()
    ax.barh(grouped.index, grouped.values * 100, color="#aa6633")
    ax.set(xlim=(0, 105), xlabel="Exact recovery of withheld source pairs (%)", title="Structural holdout • not physiological validation")
    for ax in axes.flat:
        ax.spines[["top", "right"]].set_visible(False)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=180)


if __name__ == "__main__":
    main()
