import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.feather as feather
import pyarrow.parquet as parquet
import pytest

from flyvision.evidence import build_atlas
from flyvision.graph import export_graph, locate_ids
from flyvision.mapping import ColumnMapper, evaluate_holdout


def atlas_fixture():
    annotations = pd.DataFrame({
        "bodyId": [9007199254740993, 11, 12, 13, 14, 15],
        "status": ["Traced"] * 5 + ["Glia"],
        "type": ["R1-R6", "L1", "L1", "T4a", "L1", "glia"],
        "superclass": ["ol_sensory"] + ["ol_intrinsic"] * 4 + ["glia"],
        "class": ["visual"] * 5 + [None],
        "assignedOlHex1": [None, 1, 2, None, 8, None],
        "assignedOlHex2": [None, 3, 3, None, 9, None],
        "somaSide": [None, "L", "L", "L", "R", None],
        "rootSide": ["L", None, None, None, None, None],
    })
    nt = pd.DataFrame({"body": [11, 12], "consensus_nt": ["unclear", "glutamate"], "predicted_nt": [None, "glutamate"]})
    return annotations, nt, build_atlas(annotations, nt)


def test_atlas_preserves_identity_uncertainty_and_source_values():
    ann, nt, atlas = atlas_fixture()
    assert len(atlas) == 5
    assert atlas.iloc[-1].bodyId == 9007199254740993
    assert atlas.loc[atlas.bodyId.eq(11), "nt_consensus_nt"].item() == "unclear"
    assert atlas.loc[atlas.bodyId.eq(13), "nt_consensus_nt"].isna().all()
    assert "sign" not in atlas
    assert atlas.stimulus_binding_status.eq("UNMAPPED").all()
    assert atlas.loc[atlas.bodyId.eq(9007199254740993), "visual_side_hint_basis"].item() == "rootSide"


def test_duplicate_identity_is_rejected():
    ann, nt, _ = atlas_fixture()
    with pytest.raises(ValueError, match="unique"):
        build_atlas(pd.concat([ann, ann.iloc[:1]]), nt)
    with pytest.raises(ValueError, match="unique"):
        build_atlas(ann, pd.concat([nt, nt.iloc[:1]]))


def test_conflicting_side_does_not_silently_get_a_column():
    ann, nt, _ = atlas_fixture()
    ann.loc[ann.bodyId.eq(11), "rootSide"] = "R"
    atlas = build_atlas(ann, nt)
    assert atlas.loc[atlas.bodyId.eq(11), "side_annotation_conflict"].item()
    assert not atlas.loc[atlas.bodyId.eq(11), "source_column_usable"].item()


def test_index_boundary_and_missing_ids():
    ids = np.array([11, 12, 99], dtype=np.int64)
    idx, valid = locate_ids(ids, np.array([0, 11, 90, 99, 100]))
    assert valid.tolist() == [False, True, False, True, False]
    assert idx[valid].tolist() == [0, 2]


def test_graph_preserves_low_counts_and_counts_omitted_partners(tmp_path):
    _, _, atlas = atlas_fixture()
    photo = 9007199254740993
    edges = pa.table({"body_pre": [photo, 11, 11, 888, 12], "body_post": [11, 13, 888, 13, 12], "weight": [7, 1, 4, 6, 2]})
    feather.write_feather(edges, tmp_path / "input.feather")
    totals, summary = export_graph(tmp_path / "input.feather", tmp_path / "edges.parquet", atlas, progress=lambda *a, **k: None)
    out = parquet.read_table(tmp_path / "edges.parquet").to_pandas()
    assert out.synapse_count.tolist() == [7, 1, 2]
    assert out.source_row.tolist() == [0, 1, 4]
    assert summary["traced_edge_rows"] == 3 and summary["traced_synapse_count"] == 10
    assert totals["outgoing_to_excluded_synapses"][0] == 4
    assert totals["incoming_from_excluded_synapses"][2] == 6
    assert summary["autapse_rows"] == 1


def test_zero_raw_count_is_rejected(tmp_path):
    _, _, atlas = atlas_fixture()
    feather.write_feather(pa.table({"body_pre": [11], "body_post": [12], "weight": [0]}), tmp_path / "bad.feather")
    with pytest.raises(ValueError, match="positive integers"):
        export_graph(tmp_path / "bad.feather", tmp_path / "out.parquet", atlas)


def totals_fixture(n):
    return {k: np.full(n, 20, dtype=np.int64) for k in ["incoming_synapses", "outgoing_synapses", "incoming_from_excluded_synapses", "outgoing_to_excluded_synapses"]}


def test_candidate_directions_multicolumn_mass_and_cross_side_exclusion():
    _, _, atlas = atlas_fixture()
    mapper = ColumnMapper(atlas)
    # Sorted IDs: L1-L 0, L1-L 1, T4a-L 2, L1-R 3, photoreceptor-L 4.
    mapper.consume(np.array([4, 4, 0, 1, 3]), np.array([0, 1, 2, 2, 2]), np.array([9, 3, 8, 2, 100]))
    support, rows = mapper.finish(totals_fixture(len(atlas)))
    p = rows.set_index("node_index")
    assert support[4].sum() == 12
    assert support[2].sum() == 10  # opposite side's 100 never sneaks in
    assert p.loc[4, "top_fraction_of_anchor_support"] == 0.75
    assert p.loc[4, "anchor_coverage_fraction"] == 12 / 40
    assert p.loc[2, "supported_columns"] == 2
    assert p.loc[4, "body_id"] == "9007199254740993"
    assert not rows.physiologically_validated.any()


def test_heldout_coordinate_and_self_loop_cannot_leak_into_anchors():
    _, _, atlas = atlas_fixture()
    mapper = ColumnMapper(atlas, heldout=[0])
    mapper.consume(np.array([0, 0]), np.array([0, 2]), np.array([100, 100]))
    _, rows = mapper.finish(totals_fixture(len(atlas)))
    assert rows.mapping_status.eq("UNRESOLVED").all()
    scored, summary = evaluate_holdout(atlas, rows, np.array([0]))
    assert summary["supported_predictions"] == 0
    assert summary["exact_hex_matches"] == 0
    assert not summary["physiological_validation"]
