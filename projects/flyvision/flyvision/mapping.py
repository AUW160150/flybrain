"""One-hop candidate column support, never a physiological receptive-field claim.

Photoreceptors use their outgoing connections to source-annotated columnar cells.
Other visual cells use their incoming connections from those anchors. Multiple
supported columns are retained as a distribution, not replaced by a fictitious
single receptive-field center. Coordinates remain in the source hex frame.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import sparse


class ColumnMapper:
    def __init__(self, atlas, heldout=None):
        self.atlas = atlas
        self.n = len(atlas)
        self.side = atlas.visual_side_hint.fillna("").to_numpy(dtype=str)
        self.photo = atlas.photoreceptor_type_annotation.to_numpy(dtype=bool)
        self.visual = atlas.visual_superclass_annotation.to_numpy(dtype=bool)
        valid = atlas.source_column_usable.to_numpy(dtype=bool)
        cols = atlas.loc[valid, ["visual_side_hint", "assignedOlHex1", "assignedOlHex2"]].drop_duplicates().sort_values(["visual_side_hint", "assignedOlHex1", "assignedOlHex2"])
        self.columns = cols.reset_index(drop=True).rename(columns={"visual_side_hint": "side_hint", "assignedOlHex1": "hex1", "assignedOlHex2": "hex2"})
        self.columns.insert(0, "column_index", np.arange(len(cols), dtype=np.int32))
        lookup = {(row.side_hint, int(row.hex1), int(row.hex2)): int(row.column_index) for row in self.columns.itertuples()}
        self.anchor_column = np.full(self.n, -1, dtype=np.int32)
        for row in atlas.loc[valid].itertuples():
            self.anchor_column[row.node_index] = lookup[(row.visual_side_hint, int(row.assignedOlHex1), int(row.assignedOlHex2))]
        if heldout is not None:
            self.anchor_column[np.asarray(heldout, dtype=int)] = -1
        self.target_parts, self.column_parts, self.weight_parts = [], [], []

    def consume(self, pre, post, weights):
        same_side = (self.side[pre] == self.side[post]) & np.isin(self.side[pre], ["L", "R"])
        # Exclude self loops so a held-out target cannot disclose its own coordinate.
        eligible = same_side & (pre != post)
        direct = eligible & self.visual[post] & ~self.photo[post] & (self.anchor_column[pre] >= 0)
        reverse = eligible & self.photo[pre] & (self.anchor_column[post] >= 0)
        for mask, targets, anchors in [(direct, post, pre), (reverse, pre, post)]:
            if mask.any():
                self.target_parts.append(targets[mask].copy())
                self.column_parts.append(self.anchor_column[anchors[mask]])
                self.weight_parts.append(weights[mask].copy())

    def finish(self, totals):
        if self.target_parts:
            support = sparse.coo_matrix((np.concatenate(self.weight_parts), (np.concatenate(self.target_parts), np.concatenate(self.column_parts))), shape=(self.n, len(self.columns)), dtype=np.int64).tocsr()
        else:
            support = sparse.csr_matrix((self.n, len(self.columns)), dtype=np.int64)
        support.sum_duplicates(); support.sort_indices()
        self.target_parts.clear(); self.column_parts.clear(); self.weight_parts.clear()
        # Denominator includes partners excluded by the Traced selection.
        total = np.where(self.photo,
                         totals["outgoing_synapses"] + totals["outgoing_to_excluded_synapses"],
                         totals["incoming_synapses"] + totals["incoming_from_excluded_synapses"])
        observed = np.asarray(support.sum(axis=1)).ravel()
        rows = []
        for i in np.flatnonzero(self.visual):
            start, end = support.indptr[i:i + 2]
            values, col_ids = support.data[start:end], support.indices[start:end]
            top = int(col_ids[np.argmax(values)]) if len(values) else None
            tied = bool(np.count_nonzero(values == values.max()) > 1) if len(values) else False
            h = self.columns.iloc[top] if top is not None else None
            p = values / values.sum() if len(values) else np.array([])
            rows.append({
                "node_index": int(i), "body_id": str(self.atlas.iloc[i].bodyId),
                "type": None if pd.isna(self.atlas.iloc[i].type) else str(self.atlas.iloc[i].type),
                "side_hint": self.side[i] or None,
                "source_hex_present": bool(self.atlas.iloc[i].has_source_hex_pair),
                "mapping_status": "STRUCTURAL_CANDIDATE" if len(values) else "UNRESOLVED",
                "direction": "outgoing_to_anchors" if self.photo[i] else "incoming_from_anchors",
                "supported_columns": len(values), "anchor_synapses": int(observed[i]),
                "all_partner_synapses": int(total[i]),
                "anchor_coverage_fraction": float(observed[i] / total[i]) if total[i] else None,
                "top_column_index": top, "top_hex1": int(h.hex1) if h is not None else None,
                "top_hex2": int(h.hex2) if h is not None else None,
                "top_fraction_of_anchor_support": float(p.max()) if len(p) else None,
                "top_is_tied": tied,
                "support_entropy_bits": float(-(p * np.log2(p)).sum()) if len(p) else None,
                "physiologically_validated": False,
                "angular_calibration_status": "UNAVAILABLE",
                "stimulus_binding_status": "UNMAPPED",
            })
        return support, pd.DataFrame(rows)


def choose_holdout(atlas, seed=20261008, fraction=0.2):
    # Stratify by cell type and side so evaluation covers both source eyemaps.
    rng = np.random.default_rng(seed)
    groups = atlas.loc[atlas.source_column_usable].groupby(["type", "visual_side_hint"], dropna=False)
    held = []
    for _, group in groups:
        indices = group.node_index.to_numpy(dtype=int)
        k = min(len(indices), max(1, int(len(indices) * fraction)))
        held.extend(rng.permutation(indices)[:k].tolist())
    return np.asarray(sorted(held), dtype=np.int32)


def evaluate_holdout(atlas, candidates, heldout):
    held = atlas.iloc[heldout][["node_index", "bodyId", "type", "visual_side_hint", "assignedOlHex1", "assignedOlHex2"]]
    scored = held.merge(candidates[["node_index", "top_hex1", "top_hex2", "top_is_tied", "anchor_coverage_fraction"]], on="node_index", how="left", validate="one_to_one")
    supported = scored.top_hex1.notna() & scored.top_hex2.notna()
    scored["has_prediction"] = supported
    scored["exact_hex_match"] = supported & scored.top_hex1.eq(scored.assignedOlHex1) & scored.top_hex2.eq(scored.assignedOlHex2)
    # Exact coordinate agreement does not require an unverified hex-axis angle convention.
    scored["hex1_absolute_error"] = (scored.top_hex1 - scored.assignedOlHex1).abs()
    scored["hex2_absolute_error"] = (scored.top_hex2 - scored.assignedOlHex2).abs()
    groups = []
    for (typ, side), g in scored.groupby(["type", "visual_side_hint"], dropna=False):
        predicted = g[g.has_prediction]
        unambiguous = predicted[~predicted.top_is_tied]
        groups.append({"type": str(typ), "side_hint": str(side), "heldout": len(g),
                       "predicted": len(predicted), "unique_top_predictions": len(unambiguous),
                       "exact_rate_all_heldout": float(g.exact_hex_match.mean()),
                       "exact_rate_supported": float(predicted.exact_hex_match.mean()) if len(predicted) else None,
                       "exact_rate_unique_top": float(unambiguous.exact_hex_match.mean()) if len(unambiguous) else None})
    summary = {"kind": "STRUCTURAL_COORDINATE_HOLDOUT_ONLY", "seed": 20261008,
               "heldout_neurons": len(scored), "supported_predictions": int(supported.sum()),
               "exact_hex_matches": int(scored.exact_hex_match.sum()),
               "exact_rate_all_heldout": float(scored.exact_hex_match.mean()) if len(scored) else None,
               "physiological_validation": False,
               "scope": "Held-out source column annotations; not an independent animal or receptive-field recording. Does not validate unannotated photoreceptors or T4/T5.",
               "groups": groups}
    return scored, summary
