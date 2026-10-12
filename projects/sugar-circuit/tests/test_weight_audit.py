"""Hand-computed arithmetic checks, not tests of a paper selection algorithm."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('weight_audit', Path(__file__).resolve().parents[1]/'scripts/17_paper_weight_audit.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class WeightAuditTests(unittest.TestCase):
    def test_hand_calculated_sums(self):
        # Subsets of edges 3 and 5: empty=0, first=3, second=5, both=8.
        self.assertEqual(set(audit.attainable_sums([3, 5])), {0, 3, 5, 8})

    def test_duplicate_weights_are_distinct_edges(self):
        # Two edges of weight 2 permit 0, 2, 4; both are needed for 4.
        result = audit.attainable_sums([2, 2])
        self.assertEqual(set(result), {0, 2, 4})
        self.assertEqual(result[4], (0, 1))

    def test_empty_and_invalid(self):
        self.assertEqual(audit.attainable_sums([]), {0: ()})
        for invalid in [0, -1, 0.5]:
            with self.assertRaises(ValueError):
                audit.attainable_sums([invalid])

    def test_body_selection_is_stricter_than_edge_selection(self):
        # Matrix [[2,4],[7,10]]. Nonempty rectangular sums are
        # 2,4,7,10,6,17,9,14,23. Diagonal 2+10=12 is edge-only.
        edges = [dict(source=s,target=t,weight=w) for s,t,w in [(1,3,2),(1,4,4),(2,3,7),(2,4,10)]]
        self.assertIn(12, audit.attainable_sums([2,4,7,10]))
        self.assertEqual(audit.body_subset_matches(edges,12), [])
        self.assertEqual(audit.body_subset_matches(edges,6), [{'source_ids':(1,), 'target_ids':(3,4), 'weight':6}])

    def test_above_total_impossible(self):
        # No deletion of edges [3,5] can produce 9 > 8.
        self.assertNotIn(9, audit.attainable_sums([3,5]))

    def test_deterministic_witness(self):
        self.assertEqual(audit.attainable_sums([3,5,3]), audit.attainable_sums([3,5,3]))


if __name__ == '__main__':
    unittest.main()
