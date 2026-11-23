"""
Unit tests for Byzantine Defenses and Malicious Actor Detection.
"""

import unittest
import numpy as np
from src.aggregation.byzantine_defenses import ByzantineRobustAggregator, MaliciousNodeDetector


class TestByzantineDefenses(unittest.TestCase):
    def test_krum_defense(self):
        clean = [np.array([1.0, 1.0, 1.0]) for _ in range(6)]
        poison = [np.array([-10.0, -10.0, -10.0])]
        cohort = clean + poison

        agg = ByzantineRobustAggregator(defense_type="krum", byzantine_fraction=0.15)
        consensus, telem = agg.aggregate(cohort)

        np.testing.assert_allclose(consensus, np.array([1.0, 1.0, 1.0]), atol=1e-5)
        self.assertEqual(telem["defense"], "krum")

    def test_multi_krum_defense(self):
        clean = [np.array([2.0, 2.0]) for _ in range(7)]
        poison = [np.array([-50.0, -50.0]), np.array([100.0, 100.0])]
        cohort = clean + poison

        agg = ByzantineRobustAggregator(defense_type="multi_krum", byzantine_fraction=0.25)
        consensus, telem = agg.aggregate(cohort, node_ids=list(range(9)))

        np.testing.assert_allclose(consensus, np.array([2.0, 2.0]), atol=1e-5)
        self.assertIn(7, telem["dropped_node_ids"])
        self.assertIn(8, telem["dropped_node_ids"])

    def test_coordinate_median(self):
        vectors = [
            np.array([1.0, 10.0]),
            np.array([2.0, 20.0]),
            np.array([3.0, 30.0]),
            np.array([100.0, -100.0]),  # Outlier
        ]
        agg = ByzantineRobustAggregator(defense_type="median")
        consensus, _ = agg.aggregate(vectors)
        # Median of [1, 2, 3, 100] is 2.5, Median of [10, 20, 30, -100] is 15.0
        np.testing.assert_allclose(consensus, np.array([2.5, 15.0]), atol=1e-5)

    def test_trimmed_mean(self):
        vectors = [
            np.array([1.0, 1.0]),
            np.array([2.0, 2.0]),
            np.array([3.0, 3.0]),
            np.array([4.0, 4.0]),
            np.array([100.0, 100.0]),  # Outlier
        ]
        agg = ByzantineRobustAggregator(defense_type="trimmed_mean", byzantine_fraction=0.2)
        consensus, _ = agg.aggregate(vectors)
        # Trims 1 from each end -> [2, 3, 4] -> mean = 3.0
        np.testing.assert_allclose(consensus, np.array([3.0, 3.0]), atol=1e-5)


if __name__ == "__main__":
    unittest.main()
