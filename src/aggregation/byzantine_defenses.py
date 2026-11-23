"""
Byzantine-Fault-Tolerant (BFT) Aggregation Protocols and Rogue Node Detection.
Provides Krum, Multi-Krum, Coordinate-wise Median, and Trimmed Mean defenses
to neutralize data and model poisoning attacks in decentralized swarms.

Author: Sanskar (Privacy & Defense Specialist)
Reviewers: Sumeet (Team Lead), Janvhi
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np


class MaliciousNodeDetector:
    """
    Computes pairwise Euclidean geometric distance matrices to identify
    and flag Byzantine malicious actors attempting gradient poisoning.
    """

    @staticmethod
    def compute_distance_matrix(vectors: List[np.ndarray]) -> np.ndarray:
        """Computes pairwise Euclidean distance matrix D[i, j] = ||v_i - v_j||."""
        arr = np.array(vectors, dtype=np.float32)
        diff = arr[:, np.newaxis, :] - arr[np.newaxis, :, :]
        dist_matrix = np.sqrt(np.sum(diff ** 2, axis=-1))
        return dist_matrix

    @classmethod
    def identify_outliers(
        cls, vectors: List[np.ndarray], contamination: float = 0.2
    ) -> List[int]:
        """
        Flags outlier indices with high average distances to swarm peers.
        """
        n = len(vectors)
        if n <= 2:
            return []

        dist_matrix = cls.compute_distance_matrix(vectors)
        # Average distance to other nodes (excluding self)
        np.fill_diagonal(dist_matrix, np.nan)
        mean_distances = np.nanmean(dist_matrix, axis=1)

        k_outliers = max(1, int(n * contamination))
        outlier_indices = np.argsort(mean_distances)[-k_outliers:].tolist()
        return outlier_indices


class ByzantineRobustAggregator:
    """
    Byzantine-Resilient Aggregation Algorithms.
    Defends against label flipping, sign-flip attacks, and gradient scale poisoning.
    """

    def __init__(self, defense_type: str = "multi_krum", byzantine_fraction: float = 0.2):
        self.defense_type = defense_type.lower()
        self.byzantine_fraction = float(byzantine_fraction)
        self.detected_malicious_indices: List[int] = []

    def aggregate(
        self, client_updates: List[np.ndarray], node_ids: Optional[List[int]] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Applies configured Byzantine defense protocol.
        """
        n = len(client_updates)
        if n == 0:
            raise ValueError("Empty updates list.")
        if n <= 2:
            # Fallback to simple mean if cohort too small
            return np.mean(client_updates, axis=0).astype(np.float32), {"defense": "fallback_mean", "dropped": 0}

        f = max(1, int(n * self.byzantine_fraction))
        if 2 * f + 2 >= n:
            f = max(1, (n - 3) // 2)

        if self.defense_type == "krum":
            return self._krum(client_updates, f, node_ids)
        elif self.defense_type == "multi_krum":
            return self._multi_krum(client_updates, f, node_ids)
        elif self.defense_type == "median":
            return self._coordinate_median(client_updates, node_ids)
        elif self.defense_type == "trimmed_mean":
            return self._trimmed_mean(client_updates, beta=self.byzantine_fraction, node_ids=node_ids)
        else:
            # Standard mean
            return np.mean(client_updates, axis=0).astype(np.float32), {"defense": "fedavg", "dropped": 0}

    def _krum(
        self, vectors: List[np.ndarray], f: int, node_ids: Optional[List[int]]
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Krum (Blanchard et al., 2017):
        Selects candidate vector that minimizes the sum of squared distances
        to its n - f - 2 closest neighbors.
        """
        n = len(vectors)
        dist_matrix = MaliciousNodeDetector.compute_distance_matrix(vectors)
        k_neighbors = max(1, n - f - 2)

        scores = np.zeros(n, dtype=np.float32)
        for i in range(n):
            sorted_dists = np.sort(dist_matrix[i])
            # Exclude self distance (0.0) at index 0
            scores[i] = np.sum(sorted_dists[1 : k_neighbors + 1] ** 2)

        best_idx = int(np.argmin(scores))
        dropped_count = n - 1
        dropped_ids = [node_ids[i] for i in range(n) if i != best_idx] if node_ids else []

        telemetry = {
            "defense": "krum",
            "selected_index": best_idx,
            "selected_node_id": node_ids[best_idx] if node_ids else best_idx,
            "dropped_count": dropped_count,
            "dropped_node_ids": dropped_ids,
            "byzantine_tolerance_f": f,
        }
        return vectors[best_idx].copy().astype(np.float32), telemetry

    def _multi_krum(
        self, vectors: List[np.ndarray], f: int, node_ids: Optional[List[int]], m: Optional[int] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Multi-Krum:
        Iteratively selects m lowest-scoring vectors and averages them.
        """
        n = len(vectors)
        if m is None:
            m = max(1, n - 2 * f)

        dist_matrix = MaliciousNodeDetector.compute_distance_matrix(vectors)
        k_neighbors = max(1, n - f - 2)

        scores = np.zeros(n, dtype=np.float32)
        for i in range(n):
            sorted_dists = np.sort(dist_matrix[i])
            scores[i] = np.sum(sorted_dists[1 : k_neighbors + 1] ** 2)

        selected_indices = np.argsort(scores)[:m].tolist()
        dropped_indices = [i for i in range(n) if i not in selected_indices]
        dropped_ids = [node_ids[i] for i in dropped_indices] if node_ids else dropped_indices

        selected_vecs = [vectors[i] for i in selected_indices]
        agg_vec = np.mean(selected_vecs, axis=0).astype(np.float32)

        telemetry = {
            "defense": "multi_krum",
            "m_selected": m,
            "dropped_count": len(dropped_indices),
            "dropped_node_ids": dropped_ids,
            "byzantine_tolerance_f": f,
        }
        return agg_vec, telemetry

    def _coordinate_median(
        self, vectors: List[np.ndarray], node_ids: Optional[List[int]]
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Coordinate-wise Median Aggregator."""
        arr = np.array(vectors, dtype=np.float32)
        median_vec = np.median(arr, axis=0).astype(np.float32)
        telemetry = {
            "defense": "coordinate_median",
            "input_vectors": len(vectors),
            "dropped_count": 0,
        }
        return median_vec, telemetry

    def _trimmed_mean(
        self, vectors: List[np.ndarray], beta: float, node_ids: Optional[List[int]]
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Trimmed Mean Aggregator: trims top and bottom beta fraction in each dimension."""
        arr = np.array(vectors, dtype=np.float32)
        n = len(vectors)
        k_trim = int(n * beta)

        if 2 * k_trim >= n:
            k_trim = max(0, (n - 1) // 2)

        sorted_arr = np.sort(arr, axis=0)
        if k_trim > 0:
            trimmed = sorted_arr[k_trim : n - k_trim, :]
        else:
            trimmed = sorted_arr

        mean_vec = np.mean(trimmed, axis=0).astype(np.float32)
        telemetry = {
            "defense": "trimmed_mean",
            "beta": beta,
            "k_trimmed_each_side": k_trim,
            "dropped_count": 2 * k_trim,
        }
        return mean_vec, telemetry
