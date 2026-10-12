"""Import measured reference directions without silently transferring neuron identity."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import warnings

import numpy as np
import pandas as pd

from .evidence import sha256, write_json
from .optics import rays_to_angles


def validate_permutation(values, size):
    values = np.asarray(values)
    if values.shape != (size,) or not np.isfinite(values).all() or not np.equal(values, np.floor(values)).all():
        raise ValueError("Invalid one-based lens correspondence")
    values = values.astype(int)
    if not np.array_equal(np.sort(values), np.arange(1, size + 1)):
        raise ValueError("Lens correspondence must be a one-based permutation")
    return values - 1


def verify_reference(root, lock):
    receipts = {}
    for record in lock["files"]:
        path = root / record["path"]
        data = path.read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        if len(data) != record["bytes"] or blob != record["git_blob_sha1"]:
            raise ValueError(f"Pinned reference differs: {path}")
        receipts[record["path"]] = {**record, "sha256": hashlib.sha256(data).hexdigest()}
    return receipts


def extract_geometry(eye, neighbors, published_map):
    rays = np.asarray(eye["ucl_rot_sm"], dtype=float)
    n = len(rays)
    if rays.shape != (n, 3) or not np.isfinite(rays).all():
        raise ValueError("Invalid reference directions")
    norm_error = float(np.max(np.abs(np.linalg.norm(rays, axis=1) - 1)))
    if norm_error > 1e-9:
        raise ValueError("Published directions are not unit vectors")
    lens_for_cone = validate_permutation(eye["i_match"], n)
    cone_for_lens = np.argsort(lens_for_cone)
    left_cone = np.asarray(eye["ind_left_cone"], dtype=bool)
    left_lens = np.asarray(eye["ind_left_lens"], dtype=bool)
    if left_cone.shape != (n,) or left_lens.shape != (n,) or not np.array_equal(left_cone, left_lens[lens_for_cone]):
        raise ValueError("Reference lens/cone eye assignments disagree")
    # Confirm the head-axis meaning from both the published code and data fields.
    for key, expected in [("vf", [1, 0, 0]), ("vleft", [0, 1, 0]), ("vn", [0, 0, 1])]:
        if not np.allclose(eye[key], expected, atol=1e-12):
            raise ValueError(f"Unexpected head basis: {key}")
    az, el = rays_to_angles(rays)
    frame = pd.DataFrame({
        "ray_id": [f"uct20240701:cone:{i + 1}" for i in range(n)],
        "cone_index_1based": np.arange(1, n + 1), "lens_index_1based": lens_for_cone + 1,
        "eye": np.where(left_cone, "L", "R"),
        "forward": rays[:, 0], "left": rays[:, 1], "up": rays[:, 2],
        "azimuth_deg": az, "elevation_deg": el,
        "geometry_evidence": "PUBLISHED_MICROCT_REFERENCE",
        "specimen_scope": "female_reference_20240701",
        "malecns_body_id": pd.Series([None] * n, dtype="string"),
        "malecns_registration": "UNRESOLVED",
    })
    stats, max_error = {}, 0.0
    lens_ordered_rays = rays[cone_for_lens]
    for side, side_name, mask in [("L", "left", left_lens), ("R", "right", ~left_lens)]:
        v = lens_ordered_rays[mask]
        nb = np.asarray(neighbors["nb_ind_" + side_name])
        published_dist = np.asarray(neighbors["nb_dist_ucl_" + side_name])
        central = nb[:, 0].astype(int) - 1
        valid = np.isfinite(nb[:, 1:])
        indices = np.where(valid, nb[:, 1:], 1).astype(int) - 1
        if (central < 0).any() or (central >= len(v)).any() or (indices[valid] < 0).any() or (indices[valid] >= len(v)).any():
            raise ValueError("Out-of-range published neighbor index")
        angles = np.arccos(np.clip(np.einsum("ij,ikj->ik", v[central], v[indices]), -1, 1))
        expected = published_dist[central, 1:]
        if not np.array_equal(np.isfinite(expected), valid):
            raise ValueError("Neighbor availability disagrees with published angles")
        error = float(np.max(np.abs(angles[valid] - expected[valid])))
        max_error = max(max_error, error)
        if error > 1e-8:
            raise ValueError("Neighbor angles do not reproduce published values")
        stats[side] = {"rays": int(mask.sum()), "neighbor_spacing_degrees_quantiles_5_50_95": np.percentile(np.degrees(angles[valid]), [5, 50, 95]).tolist()}
    # The paper's FAFB eyemap must select the same right-eye lens rays.
    eyemap = np.asarray(published_map["eyemap"])
    selected = eyemap[:, 1].astype(int) - 1
    ref = lens_ordered_rays[~left_lens][selected]
    discrepancy = float(np.max(np.abs(ref - np.asarray(published_map["ucl_rot_sm"]))))
    if discrepancy > 1e-10:
        raise ValueError("Published FAFB reference map is inconsistent with the full eye rays")
    checks = {"unit_vector_max_error": norm_error, "max_neighbor_angle_error_radians": max_error,
              "fafb_reference_map_max_component_error": discrepancy, "fafb_reference_mapped_columns": len(selected),
              "eyes": stats, "malecns_registered_neurons": 0,
              "validation_scope": "Reference-file consistency and coordinate/index interpretation; not MaleCNS registration or physiological validation"}
    return frame, checks


def build_reference(project_root, baseline, output):
    import rdata
    if output.exists():
        raise ValueError("Refusing to overwrite a reference run")
    lock_path = project_root / "config/eye_reference.json"
    lock = json.loads(lock_path.read_text())
    root = project_root / "references/eyemap_T4"
    receipts = verify_reference(root, lock)
    base_manifest = json.loads((baseline / "manifest.json").read_text())
    if base_manifest["status"] != "COMPLETE":
        raise ValueError("Incomplete MaleCNS baseline")
    for name in ["atlas.parquet", "source_columns.csv", "visual_candidates.parquet"]:
        if sha256(baseline / name) != base_manifest["artifacts"][name]["sha256"]:
            raise ValueError(f"MaleCNS baseline has changed: {name}")
    conversion_warnings = []
    def read(name):
        with warnings.catch_warnings(record=True) as notices:
            warnings.simplefilter("always")
            value = rdata.read_rda(root / name)
        conversion_warnings.extend(str(x.message) for x in notices)
        return value
    frame, checks = extract_geometry(read("data/microCT/20240701.RData"), read("data/microCT/20240701_nb.RData"), read("data/eyemap.RData"))
    atlas = pd.read_parquet(baseline / "atlas.parquet")
    candidates = pd.read_parquet(baseline / "visual_candidates.parquet")
    photo = atlas.loc[atlas.photoreceptor_type_annotation, ["node_index", "bodyId", "type", "visual_side_hint"]].copy()
    photo["body_id"] = photo.bodyId.map(str)
    photo = photo.drop(columns="bodyId").merge(candidates[["node_index", "mapping_status", "supported_columns", "anchor_coverage_fraction", "top_fraction_of_anchor_support"]], on="node_index", validate="one_to_one")
    photo["ray_id"] = None
    photo["registration_status"] = "NO_VERIFIED_CROSSWALK"
    photo["input_eligible"] = False
    audit = {
        "local_dataset": "male-cns:v1.0", "reference_geometry": "female_microCT_20240701",
        "reference_neural_reconstruction": "FAFB; separate specimen and identifier namespace",
        "reference_commit": lock["commit"], "reference_rays": len(frame),
        "local_photoreceptor_labelled_neurons": len(photo), "verified_photoreceptor_bindings": 0,
        "local_columns_by_side": pd.read_csv(baseline / "source_columns.csv").groupby("side_hint").size().to_dict(),
        "blocking_evidence": "No verified correspondence from MaleCNS hex coordinates/body IDs to the reference eye grid was found in the inspected files.",
        "do_not_transfer_by": ["numeric ID equality", "row order", "matching grid coordinate values", "soma sphere fit"],
        "next_evidence": "MaleCNS equator/meridian landmarks and a documented cross-specimen registration, or a dataset-matched eye-to-column map; validate orientation, uncertainty and missing coverage.",
        "physiological_validation": False,
    }
    output.mkdir(parents=True)
    frame.to_csv(output / "reference_rays.csv", index=False)
    photo.to_parquet(output / "malecns_photoreceptor_bindings.parquet", index=False)
    write_json(output / "geometry_validation.json", checks)
    write_json(output / "registration_audit.json", audit)
    manifest = {
        "status": "COMPLETE", "kind": "REFERENCE_OPTICS_WITH_UNRESOLVED_MALECNS_REGISTRATION",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "reference_repository": lock["repository"], "reference_commit": lock["commit"],
        "source_lock_sha256": sha256(lock_path), "sources": receipts,
        "baseline_manifest_sha256": sha256(baseline / "manifest.json"),
        "baseline_inputs": {name: base_manifest["artifacts"][name] for name in ["atlas.parquet", "source_columns.csv", "visual_candidates.parquet"]},
        "code_sha256": {str(p.relative_to(project_root)): sha256(p) for p in [Path(__file__), Path(__file__).with_name("optics.py")]},
        "rdata_version": rdata.__version__, "rdata_conversion_warnings": sorted(set(conversion_warnings)),
        "simulation_run": False, "physiological_validation": False,
        "artifacts": {p.name: {"sha256": sha256(p), "bytes": p.stat().st_size} for p in sorted(output.iterdir())},
    }
    write_json(output / "manifest.json", manifest)
    print(f"Imported {len(frame)} measured reference rays; verified reference angle/index consistency. MaleCNS bindings remain unresolved for {len(photo)} photoreceptor-labelled neurons.")


def load_reference(run):
    manifest = json.loads((run / "manifest.json").read_text())
    if manifest.get("status") != "COMPLETE" or manifest.get("kind") != "REFERENCE_OPTICS_WITH_UNRESOLVED_MALECNS_REGISTRATION":
        raise ValueError("Expected a complete reference optics run")
    for name, meta in manifest["artifacts"].items():
        if sha256(run / name) != meta["sha256"]:
            raise ValueError(f"Reference artifact changed: {name}")
    frame = pd.read_csv(run / "reference_rays.csv")
    return frame, manifest


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Import and verify published reference eye directions")
    project = Path(__file__).resolve().parents[1]
    parser.add_argument("--baseline", type=Path, default=project / "runs/baseline")
    parser.add_argument("--out", type=Path, default=project / "runs/eye-reference")
    args = parser.parse_args()
    build_reference(project, args.baseline.resolve(), args.out.resolve())
