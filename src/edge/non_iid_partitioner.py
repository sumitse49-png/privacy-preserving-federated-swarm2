"""
Non-IID Data Partitioner for Edge Swarm Intelligence.
Implements Dirichlet distribution (Dir(alpha)) partitioning to simulate real-world data fragmentation
across thousands of edge devices (IoT sensors, mobile phones, autonomous nodes).

Author: Janvhi (Edge Network & Data Fragmentation Specialist)
Reviewer: Sumeet (Team Lead)
"""

from typing import Dict, List, Tuple, Optional
import numpy as np


def generate_synthetic_edge_dataset(
    n_samples: int = 10000,
    n_features: int = 16,
    n_classes: int = 10,
    seed: int = 42,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generates a realistic multi-class sensory dataset simulating heterogeneous edge sensor readings.
    """
    rng = np.random.default_rng(seed)
    
    # Class centroids in feature space
    centroids = rng.uniform(-3.0, 3.0, size=(n_classes, n_features)).astype(np.float32)
    
    samples_per_class = n_samples // n_classes
    X_list = []
    y_list = []

    for c in range(n_classes):
        # Sensory variance with non-isotropic covariances
        spread = rng.uniform(0.5, 1.5, size=(n_features,)).astype(np.float32)
        samples = rng.normal(loc=centroids[c], scale=spread, size=(samples_per_class, n_features))
        
        # Add slight non-linear sensory noise
        noise = 0.05 * rng.standard_t(df=3, size=samples.shape)
        X_list.append((samples + noise).astype(np.float32))
        y_list.append(np.full((samples_per_class,), c, dtype=int))

    X = np.vstack(X_list)
    y = np.concatenate(y_list)

    # Global shuffle
    perm = rng.permutation(len(y))
    return X[perm], y[perm]


class NonIIDPartitioner:
    """
    Partitions global training data across K edge client devices using
    Dirichlet distribution over label allocations: p_k ~ Dir(alpha * 1).
    - When alpha is low (e.g. 0.1 - 0.3), each client receives samples from very few classes (high Non-IID skew).
    - When alpha is high (e.g. 10.0), each client has an identical balanced class distribution (IID).
    """

    def __init__(self, alpha: float = 0.3, min_samples_per_client: int = 10, seed: int = 42):
        self.alpha = float(alpha)
        self.min_samples = min_samples_per_client
        self.seed = seed
        self.client_partitions: Dict[int, Tuple[np.ndarray, np.ndarray]] = {}
        self.class_distributions: Dict[int, np.ndarray] = {}

    def partition(
        self, X: np.ndarray, y: np.ndarray, num_clients: int
    ) -> Dict[int, Tuple[np.ndarray, np.ndarray]]:
        """
        Executes Dirichlet-based Non-IID partitioning across num_clients.
        """
        rng = np.random.default_rng(self.seed)
        num_classes = len(np.unique(y))
        
        # Group indices by class
        class_indices = [np.where(y == c)[0] for c in range(num_classes)]
        for c in range(num_classes):
            rng.shuffle(class_indices[c])

        client_indices: List[List[int]] = [[] for _ in range(num_clients)]

        # Sample Dirichlet distributions for each class across clients
        for c in range(num_classes):
            idx_c = class_indices[c]
            n_c = len(idx_c)

            # Dirichlet distribution across num_clients
            proportions = rng.dirichlet(np.repeat(self.alpha, num_clients))
            
            # Balance small allocations
            proportions = np.array(
                [p * (len(idx_j) < (len(y) / num_clients)) for p, idx_j in zip(proportions, client_indices)]
            )
            if proportions.sum() == 0:
                proportions = rng.dirichlet(np.repeat(self.alpha, num_clients))
            proportions = proportions / proportions.sum()

            # Split indices according to proportions
            split_points = (np.cumsum(proportions) * n_c).astype(int)[:-1]
            splits = np.split(idx_c, split_points)

            for client_id, client_split in enumerate(splits):
                client_indices[client_id].extend(client_split.tolist())

        # Ensure all clients have at least minimum samples
        self.client_partitions = {}
        self.class_distributions = {}

        for client_id in range(num_clients):
            indices = np.array(client_indices[client_id], dtype=int)
            if len(indices) < self.min_samples:
                # Borrow random samples to satisfy minimum constraint
                extra_idx = rng.choice(len(y), size=(self.min_samples - len(indices)), replace=False)
                indices = np.concatenate([indices, extra_idx])

            client_X = X[indices]
            client_y = y[indices]

            self.client_partitions[client_id] = (client_X, client_y)

            # Record empirical class distribution
            class_counts = np.bincount(client_y, minlength=num_classes)
            self.class_distributions[client_id] = class_counts / float(len(client_y))

        return self.client_partitions

    def get_client_entropy(self, client_id: int) -> float:
        """Computes Shannon entropy of class distribution for a client (measures Non-IID degree)."""
        dist = self.class_distributions.get(client_id)
        if dist is None:
            return 0.0
        # Filter zero probabilities
        p = dist[dist > 0.0]
        return float(-np.sum(p * np.log2(p)))

    def get_heterogeneity_summary(self) -> Dict[str, float]:
        """Returns overall statistical metrics on data fragmentation and Non-IID heterogeneity."""
        entropies = [self.get_client_entropy(cid) for cid in self.client_partitions.keys()]
        sample_counts = [len(part[1]) for part in self.client_partitions.values()]

        return {
            "alpha": self.alpha,
            "num_clients": len(self.client_partitions),
            "mean_samples_per_client": float(np.mean(sample_counts)),
            "min_samples_per_client": int(np.min(sample_counts)),
            "max_samples_per_client": int(np.max(sample_counts)),
            "mean_class_entropy": float(np.mean(entropies)),
            "min_class_entropy": float(np.min(entropies)),
            "max_class_entropy": float(np.max(entropies)),
        }
