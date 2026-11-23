"""
Unit tests for Gradient Compression (Top-K Sparsity & INT8 Quantization).
"""

import unittest
import numpy as np
from src.crypto.compression import GradientCompressor, QuantizerInt8


class TestCompression(unittest.TestCase):
    def test_int8_quantization(self):
        q = QuantizerInt8()
        vec = np.array([-2.5, 0.0, 1.25, 3.75], dtype=np.float32)
        q_vec, scale, zp = q.quantize(vec)
        self.assertEqual(q_vec.dtype, np.int8)
        restored = q.dequantize(q_vec, scale, zp)
        np.testing.assert_allclose(restored, vec, atol=0.05)

    def test_top_k_sparsification(self):
        comp = GradientCompressor(sparsification_ratio=0.8, quantize_int8=False)
        vec = np.array([0.1, 5.0, 0.2, 0.3, 10.0, 0.1, 0.05, 0.4, 0.2, 0.1], dtype=np.float32)
        c_vec, meta = comp.compress(vec)
        # Should keep top 2 elements: 5.0 and 10.0
        self.assertEqual(meta["nonzeros_transmitted"], 2)
        self.assertAlmostEqual(c_vec[1], 5.0, places=4)
        self.assertAlmostEqual(c_vec[4], 10.0, places=4)
        self.assertEqual(c_vec[0], 0.0)


if __name__ == "__main__":
    unittest.main()
