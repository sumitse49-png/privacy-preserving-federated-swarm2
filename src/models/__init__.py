"""
Model architecture modules for federated edge learning.
"""
from src.models.neural_network import DeepNeuralNetwork
from src.models.loss_functions import cross_entropy_loss, compute_accuracy

__all__ = ["DeepNeuralNetwork", "cross_entropy_loss", "compute_accuracy"]
