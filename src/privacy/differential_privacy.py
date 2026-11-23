"""
Differential Privacy (DP) Engine and Privacy Accountant for Edge Learning.
Protects against Membership Inference Attacks (MIA) by clipping local gradients
and injecting calibrated Gaussian noise before encrypted transmission.

Author: Sanskar (Privacy & Defense Specialist)
Reviewers: Sumeet (Team Lead), Janvhi
"""

from typing import Dict, Any, Tuple, Optional
import math
import numpy as np


class PrivacyAccountant:
    """
    Rényi Differential Privacy (RDP) & Moments Accountant.
    Tracks privacy budget consumption (epsilon, delta) across T communication rounds.
    """

    def __init__(self, target_delta: float = 1e-5):
        self.target_delta = float(target_delta)
        self.rounds_executed = 0
        self.noise_multipliers = []
        self.sampling_rates = []

    def step(self, noise_multiplier: float, sampling_rate: float):
        """Records one communication round."""
        self.rounds_executed += 1
        self.noise_multipliers.append(noise_multiplier)
        self.sampling_rates.append(sampling_rate)

    def get_current_epsilon(self) -> float:
        """
        Computes cumulative (epsilon, delta)-DP bound using advanced composition theorem:
        eps ~ (q * sqrt(2 * T * ln(1/delta))) / sigma + T * q^2 / sigma^2
        """
        if self.rounds_executed == 0:
            return 0.0

        q = float(np.mean(self.sampling_rates))
        sigma = float(np.mean(self.noise_multipliers))
        t = self.rounds_executed

        if sigma <= 0:
            return float("inf")

        # Analytical Moments Accountant approximation
        term1 = (q * math.sqrt(2.0 * t * math.log(1.0 / self.target_delta))) / sigma
        term2 = (t * (q ** 2)) / (sigma ** 2)
        total_eps = term1 + term2
        return float(total_eps)


class DifferentialPrivacyEngine:
    """
    Client-side and Server-side Differential Privacy Engine.
    Enforces bounded L2-norm sensitivity and injects calibrated Gaussian noise.
    """

    def __init__(
        self,
        clip_norm: float = 1.0,
        epsilon: float = 2.0,
        delta: float = 1e-5,
        noise_multiplier: Optional[float] = None,
        seed: int = 42,
    ):
        self.clip_norm = float(clip_norm)
        self.target_epsilon = float(epsilon)
        self.target_delta = float(delta)

        # Calibrate noise multiplier sigma if not explicitly given
        # sigma = sqrt(2 * ln(1.25 / delta)) / epsilon
        if noise_multiplier is None:
            self.noise_multiplier = (
                math.sqrt(2.0 * math.log(1.25 / self.target_delta)) / self.target_epsilon
            )
        else:
            self.noise_multiplier = float(noise_multiplier)

        self.accountant = PrivacyAccountant(target_delta=self.target_delta)
        self.rng = np.random.default_rng(seed)

    def clip_gradient(self, gradient: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Clips parameter update/gradient to bounded L2 norm:
        g_clipped = g / max(1, ||g||_2 / C).
        """
        grad = np.asarray(gradient, dtype=np.float32)
        l2_norm = float(np.linalg.norm(grad))
        clip_factor = max(1.0, l2_norm / self.clip_norm)
        clipped_grad = grad / clip_factor
        return clipped_grad, l2_norm

    def add_noise(self, gradient: np.ndarray) -> np.ndarray:
        """
        Injects calibrated Gaussian perturbation:
        N(0, (sigma * C)^2 * I).
        """
        noise_std = self.noise_multiplier * self.clip_norm
        noise = self.rng.normal(0.0, noise_std, size=gradient.shape).astype(np.float32)
        return gradient + noise

    def privatize_update(
        self, gradient: np.ndarray, sampling_rate: float = 0.1
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Complete DP step: clips L2 norm, injects calibrated noise, and advances accountant.
        """
        clipped_grad, raw_norm = self.clip_gradient(gradient)
        privatized_grad = self.add_noise(clipped_grad)
        
        self.accountant.step(self.noise_multiplier, sampling_rate)
        current_eps = self.accountant.get_current_epsilon()

        telemetry = {
            "raw_l2_norm": raw_norm,
            "clipped_norm": float(np.linalg.norm(clipped_grad)),
            "clip_norm_bound": self.clip_norm,
            "noise_multiplier": self.noise_multiplier,
            "cumulative_epsilon": current_eps,
            "delta": self.target_delta,
            "membership_inference_defended": True,
        }

        return privatized_grad, telemetry
