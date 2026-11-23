"""
Edge Client Node implementation for Federated Swarm Intelligence.
Simulates realistic edge devices (IoT sensors, smartphones, edge gateways)
with battery, network latency, local training, and privacy protections.

Author: Janvhi (Edge Network Specialist)
Reviewer: Sumeet (Team Lead)
"""

from typing import Dict, Any, Optional, Tuple
import time
import numpy as np
from src.models.neural_network import DeepNeuralNetwork


class EdgeNode:
    """
    Simulated Edge Device in a decentralized swarm network.
    """

    DEVICE_PROFILES = {
        "mobile_phone": {"compute_speed": 1.0, "base_latency_ms": 45.0, "battery_drain_rate": 0.5},
        "iot_sensor": {"compute_speed": 0.35, "base_latency_ms": 110.0, "battery_drain_rate": 0.2},
        "edge_gateway": {"compute_speed": 2.5, "base_latency_ms": 15.0, "battery_drain_rate": 0.05},
    }

    def __init__(
        self,
        node_id: int,
        node_type: str = "mobile_phone",
        X_local: Optional[np.ndarray] = None,
        y_local: Optional[np.ndarray] = None,
        battery_level: float = 100.0,
        model_layer_dims: Optional[list] = None,
        seed: int = 42,
    ):
        self.node_id = node_id
        self.node_type = node_type if node_type in self.DEVICE_PROFILES else "mobile_phone"
        self.profile = self.DEVICE_PROFILES[self.node_type]
        
        self.X_local = X_local if X_local is not None else np.empty((0, 16), dtype=np.float32)
        self.y_local = y_local if y_local is not None else np.empty((0,), dtype=int)
        self.battery_level = float(battery_level)
        self.seed = seed + node_id

        self.model = DeepNeuralNetwork(layer_dims=model_layer_dims, seed=self.seed)
        
        # Malicious / Byzantine actor state
        self.is_malicious = False
        self.attack_type: Optional[str] = None
        
        # Telemetry metrics
        self.rounds_participated = 0
        self.last_training_loss = 0.0
        self.last_training_time_s = 0.0

    def set_dataset(self, X: np.ndarray, y: np.ndarray):
        """Assigns local private partition to this edge node."""
        self.X_local = np.asarray(X, dtype=np.float32)
        self.y_local = np.asarray(y, dtype=int)

    def mark_malicious(self, attack_type: str = "label_flip"):
        """Configures node as an active Byzantine attacker."""
        self.is_malicious = True
        self.attack_type = attack_type

    def local_train(
        self,
        global_weights: np.ndarray,
        epochs: int = 3,
        batch_size: int = 32,
        lr: float = 0.02,
        momentum: float = 0.9,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Executes local SGD on private dataset starting from global_weights.
        Returns:
            (weight_update_vector, telemetry_dict)
            where weight_update_vector is delta = W_local - W_global.
        """
        start_time = time.time()
        
        # Initialize local model with global parameters
        self.model.set_weights_flat(global_weights)
        initial_weights = global_weights.copy()

        n_samples = len(self.X_local)
        if n_samples == 0:
            return np.zeros_like(global_weights), {"loss": 0.0, "samples": 0}

        rng = np.random.default_rng(self.seed + self.rounds_participated)
        total_loss = 0.0
        num_steps = 0

        # Simulate Byzantine attacks if malicious
        train_y = self.y_local.copy()
        if self.is_malicious and self.attack_type == "label_flip":
            num_classes = self.model.layer_dims[-1]
            train_y = (num_classes - 1) - train_y  # Flip targets

        for epoch in range(epochs):
            indices = rng.permutation(n_samples)
            for start_idx in range(0, n_samples, batch_size):
                batch_idx = indices[start_idx : start_idx + batch_size]
                batch_X = self.X_local[batch_idx]
                batch_y = train_y[batch_idx]

                step_loss = self.model.train_step(
                    batch_X, batch_y, lr=lr, momentum=momentum
                )
                total_loss += step_loss
                num_steps += 1

        avg_loss = total_loss / max(1, num_steps)
        self.last_training_loss = avg_loss

        # Compute parameter update delta
        local_weights = self.model.get_weights_flat()
        weight_update = local_weights - initial_weights

        # Handle other Byzantine attack types
        if self.is_malicious:
            if self.attack_type == "sign_flip":
                weight_update = -2.5 * weight_update
            elif self.attack_type == "random_noise":
                weight_update = rng.normal(0.0, 5.0, size=weight_update.shape).astype(np.float32)
            elif self.attack_type == "scale_poison":
                weight_update = 50.0 * weight_update

        # Update battery and telemetry
        elapsed = time.time() - start_time
        compute_factor = self.profile["compute_speed"]
        simulated_duration = (elapsed / compute_factor) + (self.profile["base_latency_ms"] / 1000.0)
        self.last_training_time_s = simulated_duration
        self.battery_level = max(0.0, self.battery_level - self.profile["battery_drain_rate"] * epochs)
        self.rounds_participated += 1

        telemetry = {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "samples": n_samples,
            "loss": avg_loss,
            "duration_s": simulated_duration,
            "battery_level": self.battery_level,
            "is_malicious": self.is_malicious,
            "attack_type": self.attack_type,
        }

        return weight_update, telemetry
