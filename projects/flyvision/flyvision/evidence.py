"""Source integrity and the annotation-to-atlas boundary."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.feather as feather

VISUAL_SUPERCLASSES = ("ol_sensory", "ol_intrinsic", "visual_projection", "visual_centrifugal")
SENSORY_SUPERCLASSES = ("ol_sensory", "cb_sensory", "vnc_sensory")
PHOTORECEPTOR_TYPES = ("R1-R6", "R7p", "R7y", "R7d", "R7_unclear", "R8p", "R8y", "R8d", "R8_unclear", "R7R8_unclear")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def resolve_sources(config_path: Path, source_dir: Path | None = None):
    config = json.loads(config_path.read_text())
    root = source_dir.resolve() if source_dir else (config_path.parent / config["source_dir"]).resolve()
    files, receipts = {}, {}
    for key, record in config["files"].items():
        path = root / record["name"]
        digest = sha256(path)
        if digest != record["sha256"]:
            raise ValueError(f"Source hash mismatch for {key}: {path}. Do not silently substitute releases.")
        files[key] = path
        receipts[key] = {"path": str(path), "sha256": digest, "bytes": path.stat().st_size}
    return config, files, receipts


def build_atlas(annotations: pd.DataFrame, nt: pd.DataFrame) -> pd.DataFrame:
    if annotations.bodyId.isna().any() or annotations.bodyId.duplicated().any():
        raise ValueError("Annotation body IDs must be present and unique")
    if nt.body.isna().any() or nt.body.duplicated().any():
        raise ValueError("Neurotransmitter body IDs must be present and unique")
    atlas = annotations.loc[annotations.status.eq("Traced")].copy()
    atlas = atlas.sort_values("bodyId").reset_index(drop=True)
    # Preserve all original fields; body and cell-type predictions remain distinct.
    nt = nt.rename(columns={c: "nt_" + c for c in nt if c != "body"})
    atlas = atlas.merge(nt, left_on="bodyId", right_on="body", how="left", validate="one_to_one").drop(columns="body")
    atlas.insert(0, "node_index", np.arange(len(atlas), dtype=np.int32))
    atlas["visual_superclass_annotation"] = atlas.superclass.isin(VISUAL_SUPERCLASSES)
    atlas["photoreceptor_type_annotation"] = atlas.type.isin(PHOTORECEPTOR_TYPES)
    atlas["sensory_modality_annotation"] = atlas["class"].where(atlas.superclass.isin(SENSORY_SUPERCLASSES))
    h1 = pd.to_numeric(atlas.assignedOlHex1, errors="raise").to_numpy(dtype=float, na_value=np.nan)
    h2 = pd.to_numeric(atlas.assignedOlHex2, errors="raise").to_numpy(dtype=float, na_value=np.nan)
    finite = np.isfinite(h1) & np.isfinite(h2)
    integral = (np.nan_to_num(h1) == np.floor(np.nan_to_num(h1))) & (np.nan_to_num(h2) == np.floor(np.nan_to_num(h2)))
    atlas["has_source_hex_pair"] = finite & integral
    # A side hint is useful for grouping the two eyemaps but is not a verified visual hemifield.
    soma, root = atlas.somaSide.fillna(""), atlas.rootSide.fillna("")
    conflict = soma.isin(["L", "R"]) & root.isin(["L", "R"]) & soma.ne(root)
    side = soma.where(soma.isin(["L", "R"]), root.where(root.isin(["L", "R"])))
    atlas["visual_side_hint"] = side.where(atlas.visual_superclass_annotation & ~conflict)
    atlas["side_annotation_conflict"] = conflict
    atlas["visual_side_hint_basis"] = np.where(conflict, "CONFLICT", np.where(soma.isin(["L", "R"]), "somaSide", np.where(root.isin(["L", "R"]), "rootSide", "MISSING")))
    atlas["source_column_usable"] = atlas.has_source_hex_pair & atlas.visual_side_hint.isin(["L", "R"])
    atlas["stimulus_binding_status"] = "UNMAPPED"
    atlas["dynamics_status"] = "NOT_PARAMETERIZED"
    return atlas


def load_atlas(files):
    ann = feather.read_table(files["annotations"]).to_pandas()
    nt = feather.read_table(files["neurotransmitters"]).to_pandas()
    return ann, build_atlas(ann, nt)


def atlas_summary(annotations, atlas):
    visual = atlas.loc[atlas.visual_superclass_annotation]
    groups = []
    for key, frame in atlas.groupby(["superclass", "class"], dropna=False):
        groups.append({"superclass": None if pd.isna(key[0]) else str(key[0]), "class": None if pd.isna(key[1]) else str(key[1]), "neurons": len(frame), "source_hex_pairs": int(frame.has_source_hex_pair.sum())})
    return {
        "annotation_rows": len(annotations), "traced_neurons": len(atlas),
        "excluded_status_counts": annotations.loc[~annotations.status.eq("Traced"), "status"].fillna("MISSING").value_counts().to_dict(),
        "visual_superclass_neurons": len(visual),
        "source_hex_pairs": int(atlas.has_source_hex_pair.sum()),
        "source_columns_by_side": {str(s): len(g[["assignedOlHex1", "assignedOlHex2"]].drop_duplicates()) for s, g in atlas.loc[atlas.source_column_usable].groupby("visual_side_hint")},
        "side_annotation_conflicts": int(atlas.side_annotation_conflict.sum()),
        "physiologically_validated_stimulus_bindings": 0,
        "parameterized_neurons": 0,
        "groups": groups,
    }
