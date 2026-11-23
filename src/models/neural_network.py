"""
Deep Neural Network implementation for Edge Devices in Federated Swarm.
Vectorized, lightweight, and supports flat parameter serialization for FHE encryption.
"""

from typing import List, Tuple, Dict, Any, Optional
import numpy as np
from src.models.loss_functions import cross_entropy_loss, compute_accuracy, to_one_hot


class DeepNeuralNetwork:
    """
    Multi-layer Perceptron designed for edge device training.
    Provides forward inference, analytical backpropagation, and flat weight extraction
    compatible with Homomorphic Encryption and Differential Privacy clipping.
    """

    def __init__(
        self,
        layer_dims: List[int] = None,
        activation: str = "relu",
        seed: Optional[int] = 42,
    ):
        """
        layer_dims: List of dimensions [input_dim, hidden_1, ..., output_dim]
        activation: Activation function for hidden layers ('relu' or 'tanh')
        """
        if layer_dims is None:
            layer_dims = [16, 64, 32, 10]
        self.layer_dims = list(layer_dims)
        self.num_layers = len(layer_dims) - 1
        self.activation = activation.lower()
        self.seed = seed

        # Weight matrices and bias vectors
        self.weights: List[np.ndarray] = []
        self.biases: List[np.ndarray] = []

        # Velocity buffers for SGD with momentum
        self.v_weights: List[np.ndarray] = []
        self.v_biases: List[np.ndarray] = []

        self._initialize_weights()

    def _initialize_weights(self):
        """He / Xavier weight initialization."""
        rng = np.random.default_rng(self.seed)
        self.weights = []
        self.biases = []
        self.v_weights = []
        self.v_biases = []

        for i in range(self.num_layers):
            fan_in = self.layer_dims[i]
            fan_out = self.layer_dims[i + 1]

            # He normal initialization for ReLU
            std = np.sqrt(2.0 / fan_in) if self.activation == "relu" else np.sqrt(1.0 / fan_in)
            W = rng.normal(0.0, std, size=(fan_in, fan_out)).astype(np.float32)
            b = np.zeros((1, fan_out), dtype=np.float32)

            self.weights.append(W)
            self.biases.append(b)
            self.v_weights.append(np.zeros_like(W))
            self.v_biases.append(np.zeros_like(b))

    @staticmethod
    def _relu(z: np.ndarray) -> np.ndarray:
        return np.maximum(0.0, z)

    @staticmethod
    def _relu_deriv(z: np.ndarray) -> np.ndarray:
        return (z > 0.0).astype(np.float32)

    @staticmethod
    def _softmax(z: np.ndarray) -> np.ndarray:
        shift_z = z - np.max(z, axis=-1, keepdims=True)
        exp_z = np.exp(shift_z)
        return exp_z / np.sum(exp_z, axis=-1, keepdims=True)

    def forward(self, X: np.ndarray) -> Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]]:
        """
        Forward pass returning (output_probs, linear_cache_z, activation_cache_a).
        """
        A = np.asarray(X, dtype=np.float32)
        caches_z = []
        caches_a = [A]

        for i in range(self.num_layers - 1):
            Z = np.dot(A, self.weights[i]) + self.biases[i]
            caches_z.append(Z)
            if self.activation == "relu":
                A = self._relu(Z)
            elif self.activation == "tanh":
                A = np.tanh(Z)
            caches_a.append(A)

        # Output layer with Softmax
        Z_last = np.dot(A, self.weights[-1]) + self.biases[-1]
        caches_z.append(Z_last)
        A_last = self._softmax(Z_last)
        caches_a.append(A_last)

        return A_last, caches_z, caches_a

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Computes predicted class probabilities for input X."""
        probs, _, _ = self.forward(X)
        return probs

    def predict_classes(self, X: np.ndarray) -> np.ndarray:
        """Returns integer class predictions."""
        probs = self.predict(X)
        return np.argmax(probs, axis=-1)

    def compute_gradients(
        self, X: np.ndarray, y: np.ndarray
    ) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """
        Computes analytical gradients dW and db using backpropagation.
        """
        n_samples = len(X)
        if n_samples == 0:
            return [np.zeros_like(w) for w in self.weights], [np.zeros_like(b) for b in self.biases]

        probs, caches_z, caches_a = self.forward(X)
        y_oh = to_one_hot(y, self.layer_dims[-1])

        # Output gradient for CrossEntropy + Softmax
        dZ = (probs - y_oh) / float(n_samples)

        dW_list = [None] * self.num_layers
        db_list = [None] * self.num_layers

        for i in reversed(range(self.num_layers)):
            A_prev = caches_a[i]
            dW = np.dot(A_prev.T, dZ)
            db = np.sum(dZ, axis=0, keepdims=True)

            dW_list[i] = dW.astype(np.float32)
            db_list[i] = db.astype(np.float32)

            if i > 0:
                dA_prev = np.dot(dZ, self.weights[i].T)
                Z_prev = caches_z[i - 1]
                if self.activation == "relu":
                    dZ = dA_prev * self._relu_deriv(Z_prev)
                elif self.activation == "tanh":
                    dZ = dA_prev * (1.0 - np.square(np.tanh(Z_prev)))

        return dW_list, db_list

    def train_step(
        self,
        X: np.ndarray,
        y: np.ndarray,
        lr: float = 0.01,
        momentum: float = 0.9,
        weight_decay: float = 1e-4,
    ) -> float:
        """Executes a single SGD optimization step with momentum."""
        dW_list, db_list = self.compute_gradients(X, y)
        probs = self.predict(X)
        loss = cross_entropy_loss(probs, y)

        for i in range(self.num_layers):
            # Apply weight decay
            grad_w = dW_list[i] + weight_decay * self.weights[i]
            grad_b = db_list[i]

            # Update momentum velocities
            self.v_weights[i] = momentum * self.v_weights[i] + lr * grad_w
            self.v_biases[i] = momentum * self.v_biases[i] + lr * grad_b

            # Apply parameter updates
            self.weights[i] -= self.v_weights[i]
            self.biases[i] -= self.v_biases[i]

        return loss

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Evaluates model performance on dataset (X, y)."""
        probs = self.predict(X)
        loss = cross_entropy_loss(probs, y)
        acc = compute_accuracy(probs, y)
        return {"loss": loss, "accuracy": acc}

    def get_weights_flat(self) -> np.ndarray:
        """Serializes all model parameters into a single 1D float32 numpy vector."""
        flat_arrays = []
        for W, b in zip(self.weights, self.biases):
            flat_arrays.append(W.ravel())
            flat_arrays.append(b.ravel())
        return np.concatenate(flat_arrays).astype(np.float32)

    def set_weights_flat(self, flat_params: np.ndarray):
        """Restores model parameters from a single 1D numpy vector."""
        idx = 0
        flat_params = np.asarray(flat_params, dtype=np.float32).ravel()
        for i in range(self.num_layers):
            w_shape = self.weights[i].shape
            w_size = int(np.prod(w_shape))
            self.weights[i] = flat_params[idx : idx + w_size].reshape(w_shape).copy()
            idx += w_size

            b_shape = self.biases[i].shape
            b_size = int(np.prod(b_shape))
            self.biases[i] = flat_params[idx : idx + b_size].reshape(b_shape).copy()
            idx += b_size

    def total_parameters(self) -> int:
        """Returns total scalar parameter count."""
        total = 0
        for W, b in zip(self.weights, self.biases):
            total += W.size + b.size
        return total
