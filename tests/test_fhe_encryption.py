"""
Unit tests for Fully Homomorphic Encryption & Encrypted Aggregator.
"""

import unittest
import numpy as np
from src.crypto.fhe_engine import FHEEngine
from src.crypto.encrypted_aggregator import HomomorphicEncryptedAggregator


class TestFHEEncryption(unittest.TestCase):
    def setUp(self):
        self.engine = FHEEngine(bits=32, scale=10000.0)

    def test_encryption_decryption_fidelity(self):
        vec = np.array([1.5, -2.75, 0.0, 4.2], dtype=np.float32)
        enc_vec = self.engine.encrypt_vector(vec)
        dec_vec = self.engine.decrypt_vector(enc_vec)
        np.testing.assert_allclose(dec_vec, vec, atol=1e-3)

    def test_homomorphic_addition(self):
        v1 = np.array([2.0, -1.5, 3.25], dtype=np.float32)
        v2 = np.array([1.0, 4.5, -2.0], dtype=np.float32)

        c1 = self.engine.encrypt_vector(v1)
        c2 = self.engine.encrypt_vector(v2)

        c_sum = c1.homomorphic_add(c2)
        dec_sum = self.engine.decrypt_vector(c_sum)
        np.testing.assert_allclose(dec_sum, v1 + v2, atol=1e-3)

    def test_encrypted_aggregator(self):
        v1 = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        v2 = np.array([3.0, 4.0, 5.0], dtype=np.float32)

        c1 = self.engine.encrypt_vector(v1)
        c2 = self.engine.encrypt_vector(v2)

        agg = HomomorphicEncryptedAggregator(self.engine)
        c_agg, meta = agg.aggregate_encrypted_ciphertexts([c1, c2])
        avg_delta = agg.finalize_global_update(c_agg, num_clients=2)

        expected = np.array([2.0, 3.0, 4.0], dtype=np.float32)
        np.testing.assert_allclose(avg_delta, expected, atol=1e-3)
        self.assertTrue(meta["zero_knowledge_preserved"])

    def test_zero_knowledge_verification(self):
        v = np.random.randn(20).astype(np.float32)
        c = self.engine.encrypt_vector(v)
        zk = self.engine.verify_zero_knowledge(c)
        self.assertTrue(zk["zero_knowledge_secured"])
        self.assertGreater(zk["entropy_score"], 0.70)


if __name__ == "__main__":
    unittest.main()
