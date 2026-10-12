from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import platform
import time

import numpy as np
import pandas as pd
import pyarrow as pa
from scipy import sparse

from .evidence import atlas_summary, load_atlas, resolve_sources, sha256, write_json
from .graph import export_graph
from .mapping import ColumnMapper, choose_holdout, evaluate_holdout

ROOT = Path(__file__).resolve().parents[1]


def build(config_path, output, source_dir=None):
    if output.exists():
        raise ValueError(f"Output already exists: {output}. Use a new run directory to preserve evidence.")
    print("Verifying the three pinned local source files...", flush=True)
    config, files, receipts = resolve_sources(config_path, source_dir)
    output.mkdir(parents=True)
    started = time.monotonic()
    manifest = {
        "status": "RUNNING", "dataset": config["dataset"], "selection": config["selection"],
        "created_utc": datetime.now(timezone.utc).isoformat(), "sources": receipts,
        "source_config_sha256": sha256(config_path),
        "code_sha256": {str(p.relative_to(ROOT)): sha256(p) for p in sorted((ROOT / "flyvision").glob("*.py"))},
        "environment": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__, "pyarrow": pa.__version__},
        "simulation_run": False, "physiological_validation": False,
        "inference_method": "one-hop unsigned connection support from source-annotated columns",
    }
    write_json(output / "manifest.json", manifest)
    try:
        annotations, atlas = load_atlas(files)
        print(f"Atlas: {len(atlas):,} traced neurons. Preparing visual column anchors...", flush=True)
        summary = atlas_summary(annotations, atlas)
        mapper = ColumnMapper(atlas)
        heldout = choose_holdout(atlas)
        held_mapper = ColumnMapper(atlas, heldout=heldout)
        totals, graph_summary = export_graph(files["weights"], output / "edges.parquet", atlas,
                                            consumers=[mapper.consume, held_mapper.consume])
        for k, values in totals.items():
            atlas[k] = values
        atlas.to_parquet(output / "atlas.parquet", index=False)
        mapper.columns.to_csv(output / "source_columns.csv", index=False)
        print("Computing candidate column support and structural holdout results...", flush=True)
        support, candidates = mapper.finish(totals)
        sparse.save_npz(output / "column_support.npz", support)
        candidates.to_parquet(output / "visual_candidates.parquet", index=False)
        _, held_candidates = held_mapper.finish(totals)
        scored, validation = evaluate_holdout(atlas, held_candidates, heldout)
        scored.to_csv(output / "holdout_predictions.csv", index=False)
        write_json(output / "holdout_validation.json", validation)
        mapping_summary = {
            "visual_neurons": len(candidates), "supported_candidates": int(candidates.mapping_status.eq("STRUCTURAL_CANDIDATE").sum()),
            "unresolved_candidates": int(candidates.mapping_status.eq("UNRESOLVED").sum()),
            "source_hex_frame_only": True, "visual_angle_calibrated": False,
            "support_not_probability_of_correctness": True,
            "candidate_direction": "photoreceptors: outgoing to anchors; other visual neurons: incoming from anchors",
            "scope": "One-hop same-side structural support, preserving all supported columns. Not a physiological receptive field.",
        }
        for name, value in [("atlas_summary", summary), ("graph_summary", graph_summary), ("mapping_summary", mapping_summary)]:
            write_json(output / f"{name}.json", value)
        type_summary = atlas.loc[atlas.visual_superclass_annotation].groupby(["type", "visual_side_hint"], dropna=False).agg(neurons=("bodyId", "size"), source_hex_pairs=("has_source_hex_pair", "sum"))
        type_summary.to_csv(output / "visual_type_coverage.csv")
        render_report(output, summary, graph_summary, mapping_summary, validation)
        manifest["status"] = "COMPLETE"
        manifest["elapsed_seconds"] = round(time.monotonic() - started, 3)
        manifest["artifacts"] = {p.name: {"bytes": p.stat().st_size, "sha256": sha256(p)} for p in sorted(output.iterdir()) if p.is_file() and p.name != "manifest.json"}
        # A completed result also confirms source contents did not change during the run.
        for key, path in files.items():
            if sha256(path) != receipts[key]["sha256"]:
                raise ValueError(f"Source changed during build: {key}")
        write_json(output / "manifest.json", manifest)
        print(f"Complete: {output}\n{len(atlas):,} nodes; {graph_summary['traced_edge_rows']:,} raw edge rows; {mapping_summary['supported_candidates']:,} visual candidates", flush=True)
        return output
    except Exception as exc:
        manifest["status"] = "FAILED"
        manifest["error"] = str(exc)
        write_json(output / "manifest.json", manifest)
        raise


def render_report(out, atlas, graph, mapping, validation):
    rate = validation["exact_rate_all_heldout"]
    report = f"""# FlyVision sensory mapping baseline

This run indexes **{atlas['traced_neurons']:,} traced MaleCNS v1.0 neurons** and preserves **{graph['traced_edge_rows']:,} raw directed connection rows**, representing **{graph['traced_synapse_count']:,} synapses** between those neurons. The source contains {atlas['annotation_rows']:,} annotated bodies in total; non-Traced statuses remain excluded and counted.

## Visual mapping coverage

- Visual superclasses contain {atlas['visual_superclass_neurons']:,} neurons. This is an annotation-defined set, not all neurons participating in vision.
- {atlas['source_hex_pairs']:,} traced neurons have source hex-coordinate pairs.
- {mapping['supported_candidates']:,} visual neurons have one-hop candidate column support; {mapping['unresolved_candidates']:,} have none under this rule.
- All physical stimulus bindings remain UNMAPPED. No neuron has a calibrated physiological model in this milestone.

Source hex coordinates describe locations in an eyemap, not viewing angles. Soma/root side is an explicitly provisional grouping hint, not proof of a visual hemifield. Source annotations remain intact in atlas.parquet. Candidates are kept separately in visual_candidates.parquet and column_support.npz; original coordinates are never overwritten.

## Structural holdout

The run hides {validation['heldout_neurons']:,} known coordinate pairs from the mapping anchors. It recovers the exact pair for {validation['exact_hex_matches']:,} neurons ({rate:.1%} of all held-out neurons), with {validation['supported_predictions']:,} supported predictions. Per-type and per-side results, including tied top candidates, are in holdout_validation.json.

This evaluates consistency with source annotations in the same animal. It does not validate physiological receptive fields, angular calibration, unannotated photoreceptors, T4/T5 receptive fields, or behavior. Source annotations themselves may have been inferred using connectivity, so this is not independent evidence of sensory function.

## Data and inference boundaries

Edges retain positive raw counts. Neurotransmitter predictions, confidence, consensus, and source ground-truth fields remain separate. No transmitter is automatically converted to excitation/inhibition; unknown transmitters are not assigned a default sign. No synapse count is presented as a physiological weight.

Candidate support sums counts to or from source-column anchors. Photoreceptors use outgoing links; other visual neurons use incoming links. Both use same-side hints and exclude self loops. Multiple supported columns and their relative mass are retained. Fractions and entropy measure the distribution of structural support, not confidence in the biological interpretation. Coverage denominators include partners outside the Traced set.

## Next scientific requirement

Recover and verify the eye-to-visual-angle transform and photoreceptor input mapping against published eye geometry and compatible source data. Fit temporal and synaptic parameters on designated physiological/training data, then evaluate separate held-out stimuli and interventions before connecting the model to a first-person world.

Primary method references and acceptance criteria are in ../../docs/RESEARCH_PLAN.md. This baseline is a structural foundation; no sensory simulation has been validated or run.
"""
    (out / "REPORT.md").write_text(report)


def verify(run):
    import json
    manifest = json.loads((run / "manifest.json").read_text())
    if manifest["status"] != "COMPLETE":
        raise ValueError("Run is incomplete")
    for name, record in manifest["artifacts"].items():
        path = run / name
        if path.stat().st_size != record["bytes"] or sha256(path) != record["sha256"]:
            raise ValueError(f"Artifact integrity failed: {name}")
    for name, record in manifest["sources"].items():
        if sha256(Path(record["path"])) != record["sha256"]:
            raise ValueError(f"Source integrity failed: {name}")
    print(f"Verified {len(manifest['artifacts'])} artifacts and {len(manifest['sources'])} source files. This is data integrity, not physiological validation.")


def main():
    parser = argparse.ArgumentParser(description="MaleCNS sensory mapping with explicit evidence boundaries")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("build", help="Build a full traced atlas, raw graph, and visual mapping candidates")
    p.add_argument("--config", type=Path, default=ROOT / "config/sources.json")
    p.add_argument("--source-dir", type=Path)
    p.add_argument("--out", type=Path, default=ROOT / "runs" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    p = sub.add_parser("verify", help="Verify a completed run's file and source hashes")
    p.add_argument("run", type=Path)
    args = parser.parse_args()
    if args.command == "build":
        build(args.config.resolve(), args.out.resolve(), args.source_dir)
    elif args.command == "verify":
        verify(args.run.resolve())


if __name__ == "__main__":
    main()
