"""Named neuron groups: how the game refers to populations in the connectome.

A group is a regex over the MaleCNS `type` column (or a superclass). Lateral
groups get `_L` and `_R` subgroups from the effective side (somaSide, else rootSide).
"""
import re
import numpy as np

# (name, regex on type, role) ; role: "out" motor readout, "in" sensory / modulatory, "panel" extra buttons, "pop" population
GROUP_SPECS = [
    ("DNp01", r"^DNp01$", "out"),      # giant fiber: escape jump
    ("DNp09", r"^DNp09$", "out"),      # forward walking
    ("MDN", r"^MDN$", "out"),          # backward walking
    ("DNa01", r"^DNa01$", "out"),      # steering, secondary
    ("DNa02", r"^DNa02$", "out"),      # steering, ipsilateral turn
    ("DNg11", r"^DNg11$", "out"),      # grooming
    ("MN9", r"^MN9$", "out"),          # proboscis extension (eat)
    ("DNp10", r"^DNp10$", "panel"),
    ("DNg13", r"^DNg13$", "panel"),
    ("DNg100", r"^DNg100$", "panel"),
    ("DNg02", r"^DNg02_[a-g]$", "panel"),   # wing amplitude
    ("DNa_all", r"^DNa0[1-9]$", "panel"),
    ("HS", r"^HS[ENS]$", "panel"),          # optic flow
    ("LC4", r"^LC4$", "in"),           # looming: angular velocity
    ("LPLC2", r"^LPLC2$", "in"),       # looming: angular size
    ("LC16", r"^LC16$", "in"),         # looming -> backward
    ("LC6", r"^LC6$", "in"),           # looming, escape
    ("LC11", r"^LC11$", "in"),         # small moving object
    ("ORN_DM1", r"^ORN_DM1$", "in"),   # food odour (vinegar)
    ("ORN_DM4", r"^ORN_DM4$", "in"),
    ("ORN_DC1", r"^ORN_DC1$", "in"),
    ("ORN_DA1", r"^ORN_DA1$", "in"),   # cVA, conspecific
    ("ORN_VA1v", r"^ORN_VA1v$", "in"),
    ("LB3c", r"^LB3c$", "in"),         # labellar taste proxy
    ("PPL101", r"^PPL101$", "in"),     # punishment dopamine
    ("PAM", r"^PAM\d\d", "pop"),       # reward dopamine
    ("KC", r"^KC", "pop"),             # Kenyon cells
    ("MBON", r"^MBON\d\d", "pop"),
]
SUPERCLASS_GROUPS = [("DN_all", "descending_neuron")]

# Whole-CNS counts measured from processed/malecns_v1.0_traced_minw1.npz on 2026-09-25.
EXPECTED_COUNTS = {
    "DNp01": 2, "DNp09": 2, "MDN": 4, "DNa01": 2, "DNa02": 2, "DNg11": 6, "MN9": 2,
    "DNp10": 2, "DNg13": 2, "DNg100": 2, "DNg02": 29, "DNa_all": 18, "HS": 6,
    "LC4": 126, "LPLC2": 185, "LC16": 182, "LC6": 124, "LC11": 143,
    "ORN_DM1": 74, "ORN_DM4": 32, "ORN_DC1": 32, "ORN_DA1": 204, "ORN_VA1v": 130,
    "LB3c": 23, "PPL101": 2, "PAM": 316, "KC": 4064, "MBON": 97, "DN_all": 1314,
}
LATERAL = {n for n, _, role in GROUP_SPECS if role in ("out", "in", "panel")}
OUT_GROUPS = [n for n, _, role in GROUP_SPECS if role == "out"]
IN_GROUPS = [n for n, _, role in GROUP_SPECS if role == "in"]
LOOM_SEEDS = ["LC4", "LPLC2", "LC16", "LC6"]
ODOUR_SEEDS = ["ORN_DM1", "ORN_DM4", "ORN_DC1", "ORN_DA1", "ORN_VA1v"]
TASTE_SEEDS = ["LB3c"]
TARGETS = ["DNp01", "DNp09", "MDN", "DNa01", "DNa02", "DNg11", "MN9"]
FORCE_INCLUDE = ["DNp10", "DNg13", "DNg100", "HS", "PPL101", "DNg02", "DNa_all"]


def build_groups(types, superclass, side):
    """Return {name: sorted int64 index array} including _L/_R subgroups for lateral groups."""
    types = np.asarray(types).astype(str)
    superclass = np.asarray(superclass).astype(str)
    side = np.asarray(side).astype(str)
    groups = {}
    for name, pattern, _ in GROUP_SPECS:
        rx = re.compile(pattern)
        idx = np.flatnonzero(np.fromiter((rx.match(t) is not None for t in types), bool, len(types)))
        groups[name] = idx.astype(np.int64)
        if name in LATERAL:
            groups[name + "_L"] = idx[side[idx] == "L"].astype(np.int64)
            groups[name + "_R"] = idx[side[idx] == "R"].astype(np.int64)
    for name, sc in SUPERCLASS_GROUPS:
        groups[name] = np.flatnonzero(superclass == sc).astype(np.int64)
    return groups


def effective_side(soma_side, root_side):
    """somaSide when present, else rootSide; anything other than L/R becomes ''."""
    soma = np.asarray(soma_side).astype(str)
    root = np.asarray(root_side).astype(str)
    out = np.where(np.isin(soma, ["L", "R"]), soma, root)
    out = np.where(np.isin(out, ["L", "R"]), out, "")
    return out.astype(str)


def group_counts(groups):
    return {k: int(len(v)) for k, v in groups.items()}


def panel_order():
    """Group names in the order the in-game panel lists them."""
    return [n for n, _, _ in GROUP_SPECS] + [n for n, _ in SUPERCLASS_GROUPS]
