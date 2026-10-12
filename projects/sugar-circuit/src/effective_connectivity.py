"""Verified effective-connectivity algebra, not a completed paper replication.

Source: Tastekin et al., Cell (2026), DOI 10.1016/j.cell.2026.08.016,
Methods: Effective connectivity algorithm; Calculating significant paths.
See docs/final_vs_preprint_method_diff.md and config/method_readiness.json.

Rows are presynaptic bodies, columns postsynaptic bodies. P[i,j] = W[i,j]
/ total_inputs[j]. Exact-hop scores are P**h, computed as matrix products,
not elementwise powers, with no signs, cycle removal or intermediate pruning.
Every body stays separate. Counts and denominators must come from an explicitly
defined graph/synapse universe; this module does not choose that universe.

Normalization and percentile reference vectors are mandatory caller inputs.
No default population pooling, reference universe, quantile estimator, hop
limit, or significant-path iteration policy is asserted to be the paper's.
The two-stage helper acts on supplied scores; it is NOT that missing iterator.
"""
from dataclasses import dataclass
from numbers import Integral
from typing import Iterable, Mapping, Sequence

import numpy as np
from scipy import sparse


def _nonnegative_vector(values, name: str) -> np.ndarray:
    a = np.asarray(values, dtype=np.float64)
    if a.ndim != 1 or not np.isfinite(a).all() or (a < 0).any():
        raise ValueError(f"{name} must be a finite nonnegative vector")
    return a


def _hop_count(hops: int) -> int:
    if isinstance(hops, bool) or not isinstance(hops, Integral) or hops < 1:
        raise ValueError("hops must be a positive integer")
    return int(hops)


@dataclass(frozen=True)
class BodyGraph:
    """Body identity is explicit; repeated types and both sides are not pooled."""

    body_ids: tuple[int, ...]
    raw: sparse.csr_matrix
    total_inputs: np.ndarray
    proportional: sparse.csr_matrix

    @classmethod
    def from_edges(
        cls,
        body_ids: Sequence[int],
        edges: Iterable[tuple[int, int, float]],
        *,
        total_inputs: Sequence[float],
    ) -> "BodyGraph":
        """Sum duplicate edge records; preserve self-loops and zero-input bodies.

        total_inputs follows body_ids order, includes all relevant inputs even
        when some presynaptic bodies are outside this graph, and must be at
        least each raw column sum. It is never re-estimated after selection.
        """
        ids = tuple(body_ids)
        if any(isinstance(x, bool) or not isinstance(x, Integral) for x in ids):
            raise ValueError("body IDs must be integers")
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate body IDs")
        positions = {body: i for i, body in enumerate(ids)}
        totals = _nonnegative_vector(total_inputs, "total_inputs").copy()
        if len(totals) != len(ids):
            raise ValueError("one total_inputs value is required per body")
        rows, cols, weights = [], [], []
        for pre, post, weight in edges:
            if pre not in positions or post not in positions:
                raise ValueError("edge endpoint outside supplied body universe")
            if not np.isfinite(weight) or weight < 0:
                raise ValueError("synaptic weights must be finite and unsigned")
            rows.append(positions[pre])
            cols.append(positions[post])
            weights.append(weight)
        raw = sparse.csr_matrix((weights, (rows, cols)), shape=(len(ids), len(ids)), dtype=np.float64)
        raw.sum_duplicates()
        raw.eliminate_zeros()
        column_sums = np.asarray(raw.sum(axis=0)).ravel()
        if not np.isfinite(column_sums).all():
            raise ValueError("summed synaptic counts overflow")
        if ((totals == 0) & (column_sums > 0)).any() or (column_sums > totals + 1e-12).any():
            raise ValueError("total_inputs cannot be smaller than observed input counts")
        inv = np.divide(1.0, totals, out=np.zeros_like(totals), where=totals > 0)
        proportional = raw.multiply(inv[None, :]).tocsr()
        return cls(ids, raw, totals, proportional)

    def _indices(self, bodies: Sequence[int]) -> list[int]:
        bodies = tuple(bodies)
        if len(bodies) != len(set(bodies)):
            raise ValueError("duplicate focal bodies would duplicate observations")
        lookup = {body: i for i, body in enumerate(self.body_ids)}
        try:
            return [lookup[body] for body in bodies]
        except KeyError as exc:
            raise ValueError("focal body outside supplied universe") from exc

    def from_inputs(self, inputs: Sequence[int], *, hops: int) -> dict[int, sparse.csr_matrix]:
        """Per-source raw P**h rows; all routes of exactly h edges contribute.

        Revisited bodies and self-loops contribute naturally to matrix products.
        Layer-normalized values are never fed back into propagation. Returned
        matrices have shape (len(inputs), len(body_ids)) in the supplied order.
        """
        count = _hop_count(hops)
        scores = self.proportional[self._indices(inputs), :].copy()
        layers = {1: scores}
        for hop in range(2, count + 1):
            scores = (scores @ self.proportional).tocsr()
            layers[hop] = scores
        return layers

    def to_outputs(self, outputs: Sequence[int], *, hops: int) -> dict[int, sparse.csr_matrix]:
        """P**h columns toward separate targets; preserves edge direction."""
        count = _hop_count(hops)
        scores = self.proportional[:, self._indices(outputs)].copy()
        layers = {1: scores}
        for hop in range(2, count + 1):
            scores = (self.proportional @ scores).tocsr()
            layers[hop] = scores
        return layers

    def induced_raw(self, bodies: Sequence[int]) -> sparse.csr_matrix:
        """All raw edges among supplied bodies, including recurrent edges."""
        indices = self._indices(bodies)
        return self.raw[indices, :][:, indices].copy()


def nonzero_mean_scale(scores, *, reference) -> np.ndarray:
    """Scale one explicitly defined score group by its nonzero reference mean.

    The caller must resolve whether a group spans sources, targets, types, etc.
    All-zero scores/reference return zeros (numerical convention, not a paper
    claim). Positive scores with no nonzero reference are an invalid grouping.
    """
    values = _nonnegative_vector(scores, "scores")
    ref = _nonnegative_vector(reference, "reference")
    positive = ref[ref > 0]
    if positive.size == 0:
        if (values > 0).any():
            raise ValueError("positive scores have no nonzero normalization reference")
        return np.zeros_like(values)
    return values / positive.mean()


@dataclass(frozen=True)
class ThresholdResult:
    threshold: float
    passes: np.ndarray


def above_percentile(scores, *, reference, percentile: float, quantile_method: str) -> ThresholdResult:
    """Strictly exceed a percentile of an explicit, nonempty reference vector.

    Zeros are kept if supplied. Ties at the threshold fail. NumPy's estimator
    name must be chosen explicitly; no estimator is attributed to Tastekin.
    """
    values = _nonnegative_vector(scores, "scores")
    ref = _nonnegative_vector(reference, "reference")
    if ref.size == 0:
        raise ValueError("percentile reference must not be empty")
    if not np.isfinite(percentile) or not 0 <= percentile <= 100:
        raise ValueError("percentile must be between 0 and 100")
    threshold = float(np.percentile(ref, percentile, method=quantile_method))
    return ThresholdResult(threshold, values > threshold)


@dataclass(frozen=True)
class TwoStageResult:
    to_output: ThresholdResult
    from_input: ThresholdResult
    selected: np.ndarray


def two_stage_selection(
    to_output_scores, from_input_scores, *, output_reference, input_reference,
    percentile: float, quantile_method: str,
) -> TwoStageResult:
    """Keep candidates passing the output criterion AND original-input pruning.

    Candidate order must match in both vectors. These are precomputed scores;
    construction of the iterative candidate/reference sets remains unverified.
    """
    toward = above_percentile(to_output_scores, reference=output_reference,
                              percentile=percentile, quantile_method=quantile_method)
    originating = above_percentile(from_input_scores, reference=input_reference,
                                    percentile=percentile, quantile_method=quantile_method)
    if toward.passes.shape != originating.passes.shape:
        raise ValueError("candidate score vectors must have the same shape")
    return TwoStageResult(toward, originating, toward.passes & originating.passes)


class ReplicationNotReady(RuntimeError):
    """A mathematical kernel cannot authorize a biological replication."""


def require_replication_ready(readiness: Mapping) -> None:
    """Future runners must pass this gate before biological selection."""
    required = ("method_verified", "effective_math_tests_passed", "experiment_01_allowed")
    if any(readiness.get(key) is not True for key in required) or readiness.get("selection_blockers"):
        raise ReplicationNotReady("Selection rules are not fully source-verified; see config/method_readiness.json")
