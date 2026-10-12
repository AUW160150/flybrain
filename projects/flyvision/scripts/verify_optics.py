"""Verify an optical recording and replay selected frames from its trajectory."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from flyvision.evidence import sha256, write_json
from flyvision.eye_reference import load_reference
from flyvision.optics import Pose, scene_radiance
from flyvision.world import SCENE_VERSION, scene_rgb


def main():
    p = argparse.ArgumentParser()
    p.add_argument("run", type=Path)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    if args.out.exists():
        raise ValueError("Choose a new acceptance report path")
    m = json.loads((args.run / "manifest.json").read_text())
    if m["status"] != "COMPLETE" or m["kind"] != "REFERENCE_OPTICAL_SIMULATION":
        raise ValueError("Expected a completed optical recording")
    geometry = Path(m["geometry_run"])
    if sha256(geometry / "manifest.json") != m["geometry_manifest_sha256"]:
        raise ValueError("Geometry manifest differs from the recording")
    frame, _ = load_reference(geometry)
    for name, record in m["artifacts"].items():
        if sha256(args.run / name) != record["sha256"]:
            raise ValueError(f"Recording artifact changed: {name}")
    project = Path(__file__).resolve().parents[1]
    for name, digest in m["code_sha256"].items():
        if sha256(project / "flyvision" / name) != digest:
            raise ValueError(f"Replay code differs from the recorded version: {name}")
    rgb = m.get("schema_version", 1) == 2
    if rgb and (m["parameters"]["scene"] != SCENE_VERSION or m["sample_format"]["layout"] != "frame by ray by RGB"):
        raise ValueError("Unsupported scene or sample layout")
    shape = (m["frames"], len(frame), 3) if rgb else (m["frames"], len(frame))
    values = np.fromfile(args.run / "optical_samples.f32", dtype="<f4").reshape(shape)
    trajectory = pd.read_csv(args.run / "trajectory.csv", float_precision="round_trip")
    if len(trajectory) != m["frames"] or not np.isfinite(values).all() or values.min() < 0 or values.max() > 1:
        raise ValueError("Invalid recorded frames or sample range")
    rays = frame[["forward", "left", "up"]].to_numpy()
    sampled_frames = sorted(set([0, len(values) // 2, len(values) - 1]))
    errors = []
    for i in sampled_frames:
        row = trajectory.iloc[i]
        pose = Pose(row.x_scene, row.y_scene, row.z_scene, row.yaw_deg, row.pitch_deg)
        renderer = scene_rgb if rgb else scene_radiance
        errors.append(float(np.max(np.abs(renderer(rays, pose, row.time_s) - values[i]))))
    if max(errors) > 1e-6:
        raise ValueError(f"Replay mismatch: {max(errors)}")
    bindings = pd.read_parquet(geometry / "malecns_photoreceptor_bindings.parquet")
    if not bindings.ray_id.isna().all() or bindings.input_eligible.any():
        raise ValueError("Reference-only milestone unexpectedly includes MaleCNS ray assignments")
    report = {"scope": "SOFTWARE_AND_REFERENCE_CONSISTENCY", "recording_manifest_sha256": sha256(args.run / "manifest.json"),
              "verification_script_sha256": sha256(Path(__file__)), "frames": len(values), "rays": len(frame),
              "sample_layout": m["sample_format"]["layout"],
              "replayed_frames": sampled_frames, "max_replay_error": max(errors),
              "first_last_mean_absolute_difference": float(np.mean(np.abs(values[-1] - values[0]))),
              "artifact_hashes_verified": True, "replay_code_hashes_verified": True,
              "malecns_verified_bindings": 0, "neural_simulation_run": False, "physiological_validation": False,
              "live_desktop_controls": "UNVERIFIED; agent sandbox exposes no display"}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    write_json(args.out, report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
