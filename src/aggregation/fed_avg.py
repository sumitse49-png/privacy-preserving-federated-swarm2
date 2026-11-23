"""
Baseline Federated Averaging (FedAvg) implementation (McMahan et al., 2017).
Calculates sample-weighted average of client parameter updates.

Author: Janvhi (Distributed Systems Specialist)
Reviewers: Sumeet, Sanskar
"""

from typing import List, Optional
import numpy as np


class FederatedAveraging:
    """
    Standard Federated Averaging aggregator without cryptographic privacy or Byzantine defense.
    Serves as the empirical baseline.
    """

    @staticmethod
    def aggregate(
        client_updates: List[np.ndarray], sample_weights: Optional[List[int]] = None
    ) -> np.ndarray:
        """
        Computes sample-weighted average:
        Delta_avg = sum_k (n_k / N * Delta_k).
        """
        if not client_updates:
            raise ValueError("client_updates list cannot be empty.")

        n_clients = len(client_updates)
        if sample_weights is None:
            weights = np.ones(n_clients, dtype=np.float32) / float(n_clients)
        else:
            total_samples = float(sum(sample_weights))
            if total_samples <= 0:
                weights = np.ones(n_clients, dtype=np.float32) / float(n_clients)
            else:
                weights = np.array(sample_weights, dtype=np.float32) / total_samples

        stacked = np.array(client_updates, dtype=np.float32)
        # Reshape weights for broadcasting
        weight_matrix = weights.reshape(-1, 1)
        aggregated = np.sum(stacked * weight_matrix, axis=0)
        return aggregated.astype(np.float32)
