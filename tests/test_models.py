"""
Unit tests for Neural Network and Loss Functions.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import unittest
import numpy as np
from src.models.neural_network import DeepNeuralNetwork
from src.models.loss_functions import cross_entropy_loss, compute_accuracy, to_one_hot


class TestModels(unittest.TestCase):
    def setUp(self):
        self.net = DeepNeuralNetwork(layer_dims=[16, 32, 10], seed=42)

    def test_forward_pass_dimensions(self):
        X = np.random.randn(8, 16).astype(np.float32)
        probs, _, _ = self.net.forward(X)
        self.assertEqual(probs.shape, (8, 10))
        # Softmax sum should equal 1
        sums = np.sum(probs, axis=-1)
        np.testing.assert_allclose(sums, np.ones(8), rtol=1e-5)

    def test_gradient_computation(self):
        X = np.random.randn(4, 16).astype(np.float32)
        y = np.array([0, 1, 2, 3])
        dW_list, db_list = self.net.compute_gradients(X, y)
        self.assertEqual(len(dW_list), 2)
        self.assertEqual(len(db_list), 2)
        self.assertEqual(dW_list[0].shape, (16, 32))
        self.assertEqual(dW_list[1].shape, (32, 10))

    def test_flat_weight_serialization(self):
        flat = self.net.get_weights_flat()
        total_expected = (16 * 32 + 32) + (32 * 10 + 10)
        self.assertEqual(len(flat), total_expected)
        
        # Mutate and restore
        new_flat = flat + 1.0
        self.net.set_weights_flat(new_flat)
        restored = self.net.get_weights_flat()
        np.testing.assert_allclose(new_flat, restored, rtol=1e-6)

    def test_one_hot_conversion(self):
        y = np.array([0, 2, 1])
        oh = to_one_hot(y, num_classes=4)
        expected = np.array([
            [1, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 1, 0, 0]
        ], dtype=np.float32)
        np.testing.assert_array_equal(oh, expected)


if __name__ == "__main__":
    unittest.main()
