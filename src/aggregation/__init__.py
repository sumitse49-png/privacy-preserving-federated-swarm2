"""
Federated Aggregation protocols and Byzantine Fault Tolerance modules.
"""
from src.aggregation.fed_avg import FederatedAveraging
from src.aggregation.byzantine_defenses import ByzantineRobustAggregator, MaliciousNodeDetector
from src.aggregation.coordinator import FederatedCoordinator

__all__ = [
    "FederatedAveraging",
    "ByzantineRobustAggregator",
    "MaliciousNodeDetector",
    "FederatedCoordinator",
]
