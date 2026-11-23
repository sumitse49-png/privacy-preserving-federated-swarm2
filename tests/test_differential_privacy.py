"""
Unit tests for Differential Privacy Engine and Privacy Accountant.
"""

import unittest
import numpy as np
from src.privacy.differential_privacy import DifferentialPrivacyEngine, PrivacyAccountant


class TestDifferentialPrivacy(unittest.TestCase):
    def setUp(self):
        self.dp = DifferentialPrivacyEngine(clip_norm=1.0, epsilon=2.0, delta=1e-5, seed=42)

    def test_gradient_clipping(self):
        grad = np.array([3.0, 4.0], dtype=np.float32)  # norm = 5.0
        clipped, raw_norm = self.dp.clip_gradient(grad)
        self.assertAlmostEqual(raw_norm, 5.0, places=4)
        clipped_norm = float(np.linalg.norm(clipped))
        self.assertAlmostEqual(clipped_norm, 1.0, places=4)

    def test_noise_perturbation(self):
        grad = np.zeros(100, dtype=np.float32)
        noisy = self.dp.add_noise(grad)
        self.assertNotEqual(float(np.sum(np.abs(noisy))), 0.0)
        self.assertEqual(len(noisy), 100)

    def test_privacy_accountant_growth(self):
        accountant = PrivacyAccountant(target_delta=1e-5)
        eps_0 = accountant.get_current_epsilon()
        self.assertEqual(eps_0, 0.0)

        for _ in range(5):
            accountant.step(noise_multiplier=1.12, sampling_rate=0.1)

        eps_5 = accountant.get_current_epsilon()
        self.assertGreater(eps_5, 0.0)
        self.assertLess(eps_5, 10.0)


if __name__ == "__main__":
    unittest.main()
