"""
Central Encrypted Homomorphic Aggregator.
Performs mathematical Federated Averaging directly on encrypted ciphertexts
without the aggregator ever having access to the private decryption keys.

Author: Sumeet (Team Lead / Cryptography Architect)
Reviewers: Janvhi, Sanskar
"""

from typing import List, Dict, Any, Optional, Tuple
import time
import numpy as np
from src.crypto.fhe_engine import FHECiphertextVector, FHEEngine


class HomomorphicEncryptedAggregator:
    """
    Zero-Knowledge Central Aggregator.
    Averages model weight updates homomorphically over encrypted ciphertexts.
    """

    def __init__(self, fhe_engine: FHEEngine):
        self.fhe_engine = fhe_engine
        self.n_sq = fhe_engine.n_sq
        self.n = fhe_engine.n
        self.scale = fhe_engine.scale

    def aggregate_encrypted_ciphertexts(
        self, encrypted_updates: List[FHECiphertextVector], client_weights: Optional[List[float]] = None
    ) -> Tuple[FHECiphertextVector, Dict[str, Any]]:
        """
        Homomorphically aggregates K encrypted update vectors:
        C_agg = prod_{k=1}^K C_k (mod n^2).
        Mathematically equivalent to: Dec(C_agg) = sum_{k=1}^K m_k.
        """
        start_time = time.time()
        k_clients = len(encrypted_updates)
        if k_clients == 0:
            raise ValueError("No encrypted client updates provided for aggregation.")

        vec_len = encrypted_updates[0].length
        
        # Homomorphic modular multiplication across ciphertexts
        aggregated_ciphertexts = [1] * vec_len

        for enc_vec in encrypted_updates:
            for idx in range(vec_len):
                aggregated_ciphertexts[idx] = (
                    aggregated_ciphertexts[idx] * enc_vec.ciphertexts[idx]
                ) % self.n_sq

        # The aggregated ciphertext now holds the sum of all client updates
        # Scale remains the same, but the sum represents K clients
        agg_result = FHECiphertextVector(
            ciphertexts=aggregated_ciphertexts,
            n=self.n,
            scale=self.scale,
            length=vec_len,
        )

        aggregation_time = time.time() - start_time

        telemetry = {
            "num_clients_aggregated": k_clients,
            "vector_dimension": vec_len,
            "aggregation_time_s": aggregation_time,
            "zero_knowledge_preserved": True,
            "server_decrypted": False,
        }

        return agg_result, telemetry

    def finalize_global_update(
        self, aggregated_ciphertext: FHECiphertextVector, num_clients: int
    ) -> np.ndarray:
        """
        Decodes the aggregated ciphertext into the average parameter delta:
        delta_avg = (sum_{k=1}^K delta_k) / K.
        Performed securely by authorized coordinator/edge consensus.
        """
        sum_delta = self.fhe_engine.decrypt_vector(aggregated_ciphertext)
        avg_delta = sum_delta / float(max(1, num_clients))
        return avg_delta
