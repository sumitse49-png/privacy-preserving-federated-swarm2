"""
Byzantine Attack Simulator for Federated Learning.
Simulates rogue actors attempting model poisoning and data poisoning attacks.

Author: Sanskar (Privacy & Security Specialist)
Reviewers: Sumeet, Janvhi
"""

from typing import Dict, Any, Tuple
import numpy as np


class ByzantineAttackSimulator:
    """
    Simulates adversarial edge clients attempting to corrupt global consensus.
    """

    SUPPORTED_ATTACKS = ["label_flip", "sign_flip", "random_noise", "scale_poison"]

    @staticmethod
    def apply_gradient_attack(
        clean_gradient: np.ndarray,
        attack_type: str = "sign_flip",
        scale_factor: float = 20.0,
        seed: int = 42,
    ) -> np.ndarray:
        """
        Corrupts a parameter gradient vector according to specified Byzantine attack strategy.
        """
        grad = np.asarray(clean_gradient, dtype=np.float32).copy()
        rng = np.random.default_rng(seed)

        if attack_type == "sign_flip":
            # Gradient inversion attack
            return -2.5 * grad
        elif attack_type == "scale_poison":
            # Extreme magnitude scale poisoning
            return scale_factor * grad
        elif attack_type == "random_noise":
            # High-variance Gaussian flooding attack
            return rng.normal(0.0, 10.0, size=grad.shape).astype(np.float32)
        elif attack_type == "label_flip":
            # Handled at dataset level, but adds negative momentum
            return -1.0 * grad
        else:
            return grad

    @staticmethod
    def flip_labels(labels: np.ndarray, num_classes: int = 10) -> np.ndarray:
        """Applies deterministic target label flipping: y -> (num_classes - 1) - y."""
        return (num_classes - 1) - np.asarray(labels, dtype=int)
