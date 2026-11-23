"""
Privacy-Preserving Federated Swarm Intelligence
System Settings & Configuration Constants

Authors:
- Sumeet (Team Lead / Cryptography & System Architect)
- Janvhi (Edge Network & Distributed Swarm Specialist)
- Sanskar (Privacy, Defense & Dashboard Specialist)

Company: Zaalima Development Pvt. Ltd.
SOP Version: 1.1 Compliance
"""

import os
from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
CACHE_DIR = DATA_DIR / "cache"
CHECKPOINTS_DIR = DATA_DIR / "checkpoints"
DOCS_DIR = PROJECT_ROOT / "docs"

CACHE_DIR.mkdir(parents=True, exist_ok=True)
CHECKPOINTS_DIR.mkdir(parents=True, exist_ok=True)

# Swarm Configuration Defaults
DEFAULT_TOTAL_CLIENTS = 100
DEFAULT_ACTIVE_CLIENTS_PER_ROUND = 10
DEFAULT_COMMUNICATION_ROUNDS = 20
DEFAULT_LOCAL_EPOCHS = 3
DEFAULT_BATCH_SIZE = 32
DEFAULT_LEARNING_RATE = 0.01

# Non-IID Dirichlet Alpha Parameter
# Lower alpha (e.g., 0.1) -> highly skewed / non-IID
# Higher alpha (e.g., 10.0) -> uniform / IID
DEFAULT_DIRICHLET_ALPHA = 0.3

# Cryptography / FHE Settings
FHE_SCHEME = "CKKS_PAILLIER_HYBRID"
FHE_KEY_SIZE = 2048  # bits for homomorphic encryption
FHE_SCALING_FACTOR = 10000.0  # fixed-point scaling factor
FHE_MAX_CIPHERTEXT_BATCH = 512

# Compression Settings (FHE Optimization)
DEFAULT_QUANTIZATION_BITS = 8
DEFAULT_SPARSIFICATION_RATIO = 0.8  # Keep top 20% of weights/gradients

# Differential Privacy (DP) Settings
DEFAULT_DP_ENABLED = True
DEFAULT_L2_CLIP_NORM = 1.0
DEFAULT_DP_EPSILON = 2.0
DEFAULT_DP_DELTA = 1e-5
DEFAULT_DP_SIGMA = 1.12  # Calibrated for (eps=2.0, delta=1e-5)

# Byzantine Fault Tolerance (BFT) Settings
DEFAULT_BFT_DEFENSE = "KRUM"  # Options: KRUM, MULTI_KRUM, TRIMMED_MEAN, MEDIAN, FEDAVG
DEFAULT_BYZANTINE_FRACTION = 0.2  # Fraction of malicious nodes in swarm
DEFAULT_TRIM_FRACTION = 0.2
