"""Strict percentile/pruning tests; linear interpolation is an explicit toy choice."""
import unittest
import numpy as np

from src.effective_connectivity import above_percentile, two_stage_selection


class ThresholdTests(unittest.TestCase):
    def test_percentile_interpolation(self):
        # Linear q80 of 1..5: position .8*(5-1)=3.2 -> 4.2.
        r = above_percentile([1, 2, 3, 4, 5], reference=[1, 2, 3, 4, 5], percentile=80, quantile_method='linear')
        self.assertAlmostEqual(r.threshold, 4.2)
        np.testing.assert_array_equal(r.passes, [False, False, False, False, True])

    def test_ties_strictly_exceed(self):
        # Median=2; all values equal to 2 fail, regardless of their index.
        r = above_percentile([1, 2, 2, 2, 3], reference=[1, 2, 2, 2, 3], percentile=50, quantile_method='linear')
        np.testing.assert_array_equal(r.passes, [False, False, False, False, True])

    def test_original_input_pruning(self):
        # Reference 0..5 has q80=4. A passes output only, B both, C input only.
        r = two_stage_selection([5, 6, 3], [1, 5, 6], output_reference=range(6),
                                input_reference=range(6), percentile=80, quantile_method='linear')
        np.testing.assert_array_equal(r.to_output.passes, [True, True, False])
        np.testing.assert_array_equal(r.from_input.passes, [False, True, True])
        np.testing.assert_array_equal(r.selected, [False, True, False])

    def test_reference_population_changes_selection(self):
        # With twenty zero-score bodies, q80=.2; excluding them gives 4.2.
        scores = [1, 2, 3, 4, 5]
        full = above_percentile(scores, reference=[0]*20+scores, percentile=80, quantile_method='linear')
        candidates = above_percentile(scores, reference=scores, percentile=80, quantile_method='linear')
        self.assertAlmostEqual(full.threshold, .2)
        self.assertEqual(full.passes.sum(), 5)
        self.assertEqual(candidates.passes.sum(), 1)

    def test_estimator_is_material(self):
        # q80 linear=4.2 retains 5; nearest-rank 'higher'=5 retains none.
        scores = [1, 2, 3, 4, 5]
        r = above_percentile(scores, reference=scores, percentile=80, quantile_method='higher')
        self.assertEqual(r.threshold, 5)
        self.assertFalse(r.passes.any())

    def test_zero_ties_and_determinism(self):
        for _ in range(2):
            r = above_percentile([0, 0], reference=[0, 0], percentile=80, quantile_method='linear')
            self.assertEqual(r.threshold, 0)
            self.assertFalse(r.passes.any())

    def test_invalid_reference_or_scores(self):
        for reference in [[], [np.nan], [-1], [[1, 2]]]:
            with self.assertRaises(ValueError):
                above_percentile([1], reference=reference, percentile=80, quantile_method='linear')
        with self.assertRaises(ValueError):
            two_stage_selection([1, 2], [1], output_reference=[1], input_reference=[1], percentile=80, quantile_method='linear')


if __name__ == '__main__':
    unittest.main()
