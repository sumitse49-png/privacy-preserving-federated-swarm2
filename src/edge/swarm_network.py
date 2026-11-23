"""
Virtualized Edge Swarm Network Simulator.
Manages hundreds to thousands of edge devices, handles device churn,
simulates network communication constraints, and samples cohorts for federated rounds.

Author: Janvhi (Edge Network Specialist)
Reviewer: Sumeet (Team Lead)
"""

from typing import List, Dict, Any, Optional
import numpy as np
from src.edge.edge_node import EdgeNode
from src.edge.non_iid_partitioner import NonIIDPartitioner, generate_synthetic_edge_dataset


class SwarmNetwork:
    """
    Simulates a decentralized edge swarm of thousands of heterogeneous devices.
    """

    def __init__(
        self,
        total_nodes: int = 100,
        clients_per_round: int = 10,
        dirichlet_alpha: float = 0.3,
        model_layer_dims: Optional[List[int]] = None,
        byzantine_ratio: float = 0.0,
        byzantine_attack: str = "label_flip",
        seed: int = 42,
    ):
        self.total_nodes = total_nodes
        self.clients_per_round = min(clients_per_round, total_nodes)
        self.dirichlet_alpha = dirichlet_alpha
        self.model_layer_dims = model_layer_dims or [16, 64, 32, 10]
        self.byzantine_ratio = byzantine_ratio
        self.byzantine_attack = byzantine_attack
        self.seed = seed

        self.nodes: Dict[int, EdgeNode] = {}
        self.partitioner = NonIIDPartitioner(alpha=dirichlet_alpha, seed=seed)
        self.rng = np.random.default_rng(seed)

        self._initialize_swarm()

    def _initialize_swarm(self):
        """Instantiates edge nodes with realistic device distribution."""
        # 50% mobile phones, 35% IoT sensors, 15% edge gateways
        types = (
            ["mobile_phone"] * int(0.50 * self.total_nodes)
            + ["iot_sensor"] * int(0.35 * self.total_nodes)
            + ["edge_gateway"] * (self.total_nodes - int(0.50 * self.total_nodes) - int(0.35 * self.total_nodes))
        )
        self.rng.shuffle(types)

        num_malicious = int(self.total_nodes * self.byzantine_ratio)
        malicious_ids = set(self.rng.choice(self.total_nodes, size=num_malicious, replace=False))

        for node_id in range(self.total_nodes):
            battery = self.rng.uniform(70.0, 100.0)
            node = EdgeNode(
                node_id=node_id,
                node_type=types[node_id],
                battery_level=battery,
                model_layer_dims=self.model_layer_dims,
                seed=self.seed + node_id,
            )
            if node_id in malicious_ids:
                node.mark_malicious(attack_type=self.byzantine_attack)

            self.nodes[node_id] = node

    def setup_datasets(self, n_samples: int = 10000) -> Dict[str, Any]:
        """Generates synthetic dataset and distributes it across all nodes non-IID."""
        X, y = generate_synthetic_edge_dataset(
            n_samples=n_samples,
            n_features=self.model_layer_dims[0],
            n_classes=self.model_layer_dims[-1],
            seed=self.seed,
        )

        partitions = self.partitioner.partition(X, y, num_clients=self.total_nodes)
        for node_id, (X_part, y_part) in partitions.items():
            self.nodes[node_id].set_dataset(X_part, y_part)

        return self.partitioner.get_heterogeneity_summary()

    def sample_cohort(self, round_num: int, dropout_prob: float = 0.05) -> List[EdgeNode]:
        """
        Samples an active cohort of edge nodes for the current communication round,
        accounting for random device dropouts and low battery thresholds.
        """
        round_rng = np.random.default_rng(self.seed + round_num * 1337)
        available_ids = [
            nid for nid, node in self.nodes.items()
            if node.battery_level > 5.0 and round_rng.random() > dropout_prob
        ]

        if len(available_ids) < self.clients_per_round:
            sampled_ids = available_ids
        else:
            sampled_ids = round_rng.choice(
                available_ids, size=self.clients_per_round, replace=False
            ).tolist()

        return [self.nodes[nid] for nid in sampled_ids]

    def get_swarm_status(self) -> Dict[str, Any]:
        """Returns overall swarm health and statistics."""
        batteries = [n.battery_level for n in self.nodes.values()]
        active_count = sum(1 for b in batteries if b > 5.0)
        malicious_count = sum(1 for n in self.nodes.values() if n.is_malicious)

        return {
            "total_nodes": self.total_nodes,
            "active_nodes": active_count,
            "malicious_nodes": malicious_count,
            "mean_battery": float(np.mean(batteries)),
            "device_types": {
                "mobile_phone": sum(1 for n in self.nodes.values() if n.node_type == "mobile_phone"),
                "iot_sensor": sum(1 for n in self.nodes.values() if n.node_type == "iot_sensor"),
                "edge_gateway": sum(1 for n in self.nodes.values() if n.node_type == "edge_gateway"),
            },
        }
