"""
Unit tests for Non-IID Dirichlet Data Partitioner and Swarm Network.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import unittest
import numpy as np
from src.edge.non_iid_partitioner import NonIIDPartitioner, generate_synthetic_edge_dataset
from src.edge.swarm_network import SwarmNetwork


class TestNonIIDData(unittest.TestCase):
    def test_synthetic_dataset_generation(self):
        X, y = generate_synthetic_edge_dataset(n_samples=200, n_features=16, n_classes=5, seed=42)
        self.assertEqual(X.shape, (200, 16))
        self.assertEqual(len(y), 200)
        self.assertEqual(len(np.unique(y)), 5)

    def test_dirichlet_partitioner(self):
        X, y = generate_synthetic_edge_dataset(n_samples=500, n_classes=5, seed=42)
        partitioner = NonIIDPartitioner(alpha=0.3, seed=42)
        partitions = partitioner.partition(X, y, num_clients=10)
        self.assertEqual(len(partitions), 10)

        # Check total samples preserved
        total_samples = sum(len(p[1]) for p in partitions.values())
        self.assertGreaterEqual(total_samples, 500)

        summary = partitioner.get_heterogeneity_summary()
        self.assertEqual(summary["num_clients"], 10)
        self.assertLess(summary["mean_class_entropy"], 2.32)

    def test_swarm_network_sampling(self):
        swarm = SwarmNetwork(total_nodes=20, clients_per_round=5, seed=42)
        cohort = swarm.sample_cohort(round_num=1)
        self.assertEqual(len(cohort), 5)

        status = swarm.get_swarm_status()
        self.assertEqual(status["total_nodes"], 20)
        self.assertGreater(status["mean_battery"], 50.0)


if __name__ == "__main__":
    unittest.main()
