import json
import numpy as np
import pytest
from flyworld.groups import build_groups, effective_side, EXPECTED_COUNTS, GROUP_SPECS, LATERAL, TARGETS, LOOM_SEEDS
from flyworld.config import PATHS


def test_build_groups_synthetic():
    types = np.array(["DNp09", "DNp09", "LC4", "KCab-m", "MBON11", "PAM01", "DNg02_c", "HSE", "foo"])
    sc = np.array(["descending_neuron"] * 2 + ["visual_projection", "cb_intrinsic", "cb_intrinsic", "cb_intrinsic", "descending_neuron", "cb_intrinsic", "x"])
    side = np.array(["L", "R", "L", "", "R", "", "L", "R", ""])
    g = build_groups(types, sc, side)
    assert g["DNp09"].tolist() == [0, 1] and g["DNp09_L"].tolist() == [0] and g["DNp09_R"].tolist() == [1]
    assert g["LC4"].tolist() == [2] and g["KC"].tolist() == [3] and g["MBON"].tolist() == [4]
    assert g["PAM"].tolist() == [5] and g["DNg02"].tolist() == [6] and g["HS"].tolist() == [7]
    assert g["DN_all"].tolist() == [0, 1, 6]
    assert "KC_L" not in g


def test_effective_side():
    out = effective_side(["L", "", "", "M"], ["R", "R", "unknown", "L"])
    assert out.tolist() == ["L", "R", "", "L"]


@pytest.mark.skipif(not PATHS["groups_whole"].exists(), reason="run scripts/extract_circuits.py first")
def test_whole_group_counts_match_expected():
    with open(PATHS["groups_whole"]) as f:
        g = json.load(f)
    for name, exp in EXPECTED_COUNTS.items():
        assert len(g[name]) == exp, name
    for name in LATERAL:
        assert len(g[name + "_L"]) + len(g[name + "_R"]) <= len(g[name])


@pytest.mark.skipif(not PATHS["circuit_npz"].exists(), reason="run scripts/extract_circuits.py first")
def test_circuit_is_consistent_with_whole():
    z = np.load(PATHS["circuit_npz"], allow_pickle=True)
    w = np.load(PATHS["whole_npz"], allow_pickle=True)
    orig = z["orig_index"]
    assert len(np.unique(orig)) == len(orig)
    N = len(orig)
    assert z["pre"].max() < N and z["post"].max() < N and z["pre"].min() >= 0
    assert (z["type"].astype(str) == w["type"].astype(str)[orig]).all()
    assert (z["body_id"] == w["body_id"][orig]).all()
    assert np.abs(z["weight"]).min() >= 3
    with open(PATHS["circuit_groups"]) as f:
        g = json.load(f)
    for name in TARGETS + LOOM_SEEDS:
        assert len(g[name]) == EXPECTED_COUNTS[name]
        assert max(g[name]) < N
    # signs: DNp01 receives net excitatory drive from LC4 (cholinergic)
    lc4 = np.array(g["LC4"]); dnp01 = np.array(g["DNp01"])
    e = np.isin(z["pre"], lc4) & np.isin(z["post"], dnp01)
    assert e.sum() > 0 and z["weight"][e].sum() > 0
