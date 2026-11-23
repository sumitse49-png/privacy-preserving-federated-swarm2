"""
Edge network simulation and non-IID data partitioning modules.
"""
from src.edge.non_iid_partitioner import NonIIDPartitioner, generate_synthetic_edge_dataset
from src.edge.edge_node import EdgeNode
from src.edge.swarm_network import SwarmNetwork

__all__ = ["NonIIDPartitioner", "generate_synthetic_edge_dataset", "EdgeNode", "SwarmNetwork"]
