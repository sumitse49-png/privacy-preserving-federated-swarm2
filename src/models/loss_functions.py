"""
Loss functions and evaluation metrics for Federated Neural Networks.
"""
import numpy as np

def to_one_hot(y: np.ndarray, num_classes: int) -> np.ndarray:
    """Converts 1D integer class array to 2D one-hot matrix."""
    y = np.asarray(y, dtype=int).ravel()
    one_hot = np.zeros((len(y), num_classes), dtype=np.float32)
    one_hot[np.arange(len(y)), y] = 1.0
    return one_hot

def cross_entropy_loss(y_pred: np.ndarray, y_true: np.ndarray, eps: float = 1e-12) -> float:
    """
    Computes numerically stable multi-class Cross-Entropy loss.
    y_pred: (N, C) predicted probabilities
    y_true: (N,) integer class labels or (N, C) one-hot matrix
    """
    y_pred = np.clip(y_pred, eps, 1.0 - eps)
    if y_true.ndim == 1 or (y_true.ndim == 2 and y_true.shape[1] == 1):
        n = len(y_true)
        correct_log_probs = -np.log(y_pred[np.arange(n), y_true.ravel().astype(int)])
        return float(np.mean(correct_log_probs))
    else:
        return float(-np.mean(np.sum(y_true * np.log(y_pred), axis=-1)))

def compute_accuracy(y_pred: np.ndarray, y_true: np.ndarray) -> float:
    """
    Computes classification accuracy.
    y_pred: (N, C) predicted probabilities or logits
    y_true: (N,) integer labels or (N, C) one-hot labels
    """
    preds = np.argmax(y_pred, axis=-1)
    if y_true.ndim == 1 or (y_true.ndim == 2 and y_true.shape[1] == 1):
        targets = y_true.ravel().astype(int)
    else:
        targets = np.argmax(y_true, axis=-1)
    return float(np.mean(preds == targets))
