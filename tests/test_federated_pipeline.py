"""
End-to-End Unit Test for Federated Swarm Training Pipeline.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import unittest
from src.aggregation.coordinator import FederatedCoordinator


class TestFederatedPipeline(unittest.TestCase):
    def test_full_pipeline_round(self):
        coord = FederatedCoordinator(
            total_nodes=12,
            clients_per_round=4,
            use_fhe=True,
            use_dp=True,
            use_compression=True,
            byzantine_defense="multi_krum",
            byzantine_ratio=0.2,
            fhe_bits=32,
            seed=42,
        )
        setup_meta = coord.setup_system(n_samples=400)
        self.assertGreater(setup_meta["total_parameters"], 0)

        record = coord.train_round(round_num=1, local_epochs=1)
        self.assertEqual(record["round"], 1)
        self.assertIn("val_loss", record)
        self.assertIn("val_accuracy", record)
        self.assertTrue(record["fhe_telemetry"]["zero_knowledge_verified"])
        self.assertGreater(record["cumulative_epsilon"], 0.0)


if __name__ == "__main__":
    unittest.main()
