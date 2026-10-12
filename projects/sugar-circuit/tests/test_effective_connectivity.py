"""Hand-calculated kernel tests, not validation of unknown selection policies."""
import unittest
import numpy as np

from src.effective_connectivity import BodyGraph, nonzero_mean_scale, require_replication_ready, ReplicationNotReady


class EffectiveConnectivityTests(unittest.TestCase):
    def setUp(self):
        # A->B=2/4, B->C=3/6, C->D=4/8; extra inputs outside
        # this graph are included in the supplied postsynaptic totals.
        self.graph = BodyGraph.from_edges([1, 2, 3, 4], [(1, 2, 2), (2, 3, 3), (3, 4, 4)],
                                          total_inputs=[0, 4, 6, 8])

    def test_one_hop_and_full_input_denominator(self):
        # Restricting the graph must not turn 2/4 into 2/2.
        np.testing.assert_allclose(self.graph.from_inputs([1], hops=1)[1].toarray(), [[0, .5, 0, 0]])
        self.assertEqual(self.graph.raw[0, 1], 2)

    def test_two_hops(self):
        # A->B->C: (2/4)(3/6)=1/4, no one-hop scores added.
        np.testing.assert_allclose(self.graph.from_inputs([1], hops=2)[2].toarray(), [[0, 0, .25, 0]])

    def test_three_hops(self):
        # A->B->C->D: (1/2)^3=1/8.
        np.testing.assert_allclose(self.graph.from_inputs([1], hops=3)[3].toarray(), [[0, 0, 0, .125]])

    def test_multiple_routes(self):
        graph = BodyGraph.from_edges([1, 2, 3, 4], [(1, 2, 2), (1, 3, 1), (2, 4, 3), (3, 4, 1)],
                                     total_inputs=[0, 4, 4, 8])
        # A->B->D plus A->C->D = (1/2)(3/8)+(1/4)(1/8)=7/32.
        self.assertEqual(graph.from_inputs([1], hops=2)[2][0, 3], 7 / 32)

    def test_recurrent_walks_and_self_loops(self):
        graph = BodyGraph.from_edges([1, 2], [(1, 1, 1), (1, 2, 1), (2, 1, 1)], total_inputs=[2, 2])
        layers = graph.from_inputs([1], hops=3)
        # P=[[.5,.5],[.5,0]], first row P²=[.5,.25], P³=[.375,.25].
        np.testing.assert_allclose(layers[2].toarray(), [[.5, .25]])
        np.testing.assert_allclose(layers[3].toarray(), [[.375, .25]])

    def test_zero_edges_and_zero_denominators(self):
        graph = BodyGraph.from_edges([1, 2], [], total_inputs=[0, 0])
        self.assertTrue(all(m.nnz == 0 for m in graph.from_inputs([1], hops=3).values()))
        np.testing.assert_array_equal(nonzero_mean_scale([0, 0], reference=[0, 0]), [0, 0])

    def test_nonzero_mean_normalization(self):
        # Nonzero mean of [0,1/4,3/4] is 1/2, NOT 1/3.
        np.testing.assert_allclose(nonzero_mean_scale([0, .25, .75], reference=[0, .25, .75]), [0, .5, 1.5])

    def test_scaling_does_not_change_propagation(self):
        layers = self.graph.from_inputs([1], hops=2)
        nonzero_mean_scale(layers[1].toarray()[0], reference=layers[1].toarray()[0])
        self.assertEqual(layers[2][0, 2], .25)  # Normalized one-hop value 1 must not be propagated.

    def test_toward_outputs_keeps_direction(self):
        # C->D=1/2, B->D at two hops=1/4, A->D at three=1/8.
        toward = self.graph.to_outputs([4], hops=3)
        np.testing.assert_allclose(toward[1].toarray().ravel(), [0, 0, .5, 0])
        np.testing.assert_allclose(toward[2].toarray().ravel(), [0, .25, 0, 0])
        np.testing.assert_allclose(toward[3].toarray().ravel(), [.125, 0, 0, 0])
        forward = self.graph.from_inputs([1, 2, 3, 4], hops=3)
        for hop in toward:
            np.testing.assert_allclose(toward[hop].toarray(), forward[hop][:, [3]].toarray())

    def test_bilateral_duplicate_types_remain_bodies(self):
        # Bodies 11/12 could share a type but represent L/R; they stay separate.
        graph = BodyGraph.from_edges([11, 12, 20], [(11, 20, 2), (12, 20, 6)], total_inputs=[0, 0, 8])
        scores = graph.from_inputs([11, 12], hops=1)[1].toarray()
        np.testing.assert_allclose(scores[:, 2], [.25, .75])
        self.assertEqual(scores.shape, (2, 3))

    def test_induced_graph_retains_recurrence_and_raw_counts(self):
        graph = BodyGraph.from_edges([1, 2, 3], [(1, 2, 2), (2, 1, 1), (2, 2, 1), (2, 3, 4)], total_inputs=[1, 3, 4])
        np.testing.assert_array_equal(graph.induced_raw([2, 1]).toarray(), [[1, 1], [2, 0]])

    def test_duplicate_edges_and_determinism(self):
        edges = [(1, 2, 1), (1, 2, 2), (2, 1, 1)]
        a = BodyGraph.from_edges([1, 2], edges, total_inputs=[1, 3])
        b = BodyGraph.from_edges([1, 2], list(reversed(edges)), total_inputs=[1, 3])
        for hop, values in a.from_inputs([1], hops=3).items():
            np.testing.assert_array_equal(values.toarray(), b.from_inputs([1], hops=3)[hop].toarray())
        self.assertEqual(a.raw[0, 1], 3)

    def test_invalid_data_rejected(self):
        for weight, totals in [(-1, [0, 1]), (np.nan, [0, 1]), (2, [0, 1]), (1, [0, 0])]:
            with self.subTest(weight=weight, totals=totals), self.assertRaises(ValueError):
                BodyGraph.from_edges([1, 2], [(1, 2, weight)], total_inputs=totals)
        with self.assertRaises(ValueError):
            BodyGraph.from_edges([1, 1], [], total_inputs=[0, 0])
        with self.assertRaises(ValueError):
            BodyGraph.from_edges([1], [(1, 2, 1)], total_inputs=[0])
        for hops in [0, -1, 1.5, True]:
            with self.assertRaises(ValueError):
                self.graph.from_inputs([1], hops=hops)
        with self.assertRaises(ValueError):
            self.graph.from_inputs([1, 1], hops=1)
        with self.assertRaises(ValueError):
            nonzero_mean_scale([1], reference=[0])

    def test_replication_gate(self):
        with self.assertRaises(ReplicationNotReady):
            require_replication_ready({'effective_math_tests_passed': True})
        with self.assertRaises(ReplicationNotReady):
            require_replication_ready(dict(method_verified=True, effective_math_tests_passed=True,
                experiment_01_allowed=True, selection_blockers=['pooling']))


if __name__ == '__main__':
    unittest.main()
