# Work Distribution Document
**Zaalima Development Pvt. Ltd. — Team Project Execution**  
**Project 2: Privacy-Preserving Federated Swarm Intelligence**  
**Cycle: Month 2 (8th to 7th of following month)**

---

### Team Allocation Overview

| Team Role | Assigned Member | Primary Responsibilities | Dedicated Git Branch |
|---|---|---|---|
| **Team Lead / Systems & Cryptography Architect** | **Sumeet** | Overall system orchestration, FHE homomorphic encryption engine, encrypted aggregator, Git repository management, and CI/CD pipelines | `sumeet/fhe-cryptography-core` |
| **Edge Network & Data Fragmentation Specialist** | **Janvhi** | Virtualized edge swarm network (100+ nodes), Non-IID Dirichlet partitioner ($\alpha = 0.3$), baseline FedAvg algorithm, and local edge SGD loops | `janvhi/edge-network-data` |
| **Privacy, Defense & Dashboard Specialist** | **Sanskar** | Differential Privacy engine (Rényi Moments Accountant), Byzantine defenses (Krum, Multi-Krum, Median), gradient compression (INT8 + Top-K), and Streamlit dashboard | `sanskar/byzantine-dp-dashboard` |

---

### Week-Wise Task Distribution

#### Week 1 (Implementation Phase 1: 8th to 15th)
- **Sumeet (Lead):**
  - Establish GitHub repository structure, branch management protocols, and initial configuration (`config/settings.py`, `config/federated_config.yaml`).
  - Architect core Deep Neural Network architecture (`src/models/neural_network.py`) with flat parameter vectorization for cryptographic serialization.
- **Janvhi (Data & Edge Specialist):**
  - Set up virtualized edge swarm simulator (`src/edge/swarm_network.py`) supporting hundreds of heterogeneous edge nodes (mobile phones, IoT sensors, edge gateways).
  - Implement Non-IID Dirichlet distribution partitioner ($\text{Dir}(\alpha)$) to simulate extreme sensory data fragmentation (`src/edge/non_iid_partitioner.py`).
  - Implement baseline Federated Averaging (FedAvg) aggregation protocol (`src/aggregation/fed_avg.py`).
- **Sanskar (Privacy & Security Specialist):**
  - Create test harness skeleton and benchmarking baseline (`src/benchmark/profiler.py`, `tests/test_models.py`).
  - Implement edge device local execution metrics and initial Docker Compose multi-container configuration (`docker/docker-compose.yml`).

#### Week 2 (Implementation Phase 2: 16th to 22nd)
- **Sumeet (Lead):**
  - Implement Fully Homomorphic Encryption (FHE) engine supporting CKKS / Additively Homomorphic Encryption scheme (`src/crypto/fhe_engine.py`).
  - Build cryptographic keypair generation, modular inverse arithmetic, and fixed-point float encoding.
  - Implement central homomorphic encrypted aggregator (`src/crypto/encrypted_aggregator.py`) allowing weight averaging directly over encrypted ciphertexts without server-side decryption.
  - Establish automated GitHub Actions CI/CD pipeline (`.github/workflows/federated-ci.yml`).
- **Janvhi (Data & Edge Specialist):**
  - Integrate local edge device training loops with battery depletion and latency constraints (`src/edge/edge_node.py`).
  - Validate baseline FedAvg weight synchronization across heterogeneous clients in the swarm.
- **Sanskar (Privacy & Security Specialist):**
  - Implement mathematical verification of zero-knowledge privacy and statistical entropy tests.
  - Develop initial test cases for encrypted ciphertext arithmetic (`tests/test_fhe_encryption.py`).
- **All Members:**
  - Mid-Project Review milestone validation: Edge network holding localized data, FedAvg syncing weights, and encrypted ciphertext aggregation mathematically verified.

#### Week 3 (Implementation Phase 3: 23rd to 29th)
- **Sumeet (Lead):**
  - Build central Federated Coordinator (`src/aggregation/coordinator.py`) orchestrating cohort sampling, cryptographic handoffs, and global parameter distribution.
  - Optimize FHE batch operations to eliminate cryptographic memory bottlenecks.
- **Janvhi (Data & Edge Specialist):**
  - Implement device churn simulator (intermittent disconnections, packet dropouts, and low-battery shutdowns).
  - Simulate label skew, quantity skew, and feature drift in Non-IID sensory distributions.
- **Sanskar (Privacy & Security Specialist):**
  - Mitigate FHE computational overhead by implementing Top-$K$ sparsification and Affine 8-bit INT8 Quantization (`src/crypto/compression.py`), achieving $4\times$ to $20\times$ bandwidth compression.
  - Implement Differential Privacy (DP) mechanisms with $L_2$ gradient sensitivity clipping and calibrated Gaussian noise injection (`src/privacy/differential_privacy.py`).
  - Develop Byzantine Fault Tolerant (BFT) aggregation algorithms: Krum, Multi-Krum, Coordinate-wise Median, and Trimmed Mean (`src/aggregation/byzantine_defenses.py`).
  - Implement Byzantine Attack Simulator (`src/privacy/attack_simulator.py`) modeling label-flipping, sign-flip inversion, and gradient scale poisoning.

#### Week 4 (Implementation Phase 4: 30th to 6th of next month)
- **Sumeet (Lead):**
  - Author comprehensive `FHE_FEDERATED_LEARNING_SECURITY_REPORT.md` detailing cryptographic security proofs and mathematical guarantees.
  - Conduct full security audit script (`scripts/run_security_audit.py`).
  - Oversee Git branch merges (`--no-ff`) into `main` and tag final release.
- **Janvhi (Data & Edge Specialist):**
  - Benchmark network communication overhead, latency profiles, and convergence rates across centralized vs vanilla vs swarm models (`scripts/run_benchmarks.py`).
  - Implement edge swarm telemetry reporting and client participation analytics.
- **Sanskar (Privacy & Security Specialist):**
  - Develop full-featured administrative supervisor dashboard using Streamlit (`dashboard/app.py`) visualizing swarm nodes, live training curves, FHE ciphertexts, DP budget, and detected malicious nodes.
  - Verify 100% isolation of poisoned nodes in pen-test scenarios.
- **All Members:**
  - Final Project Review defense and demonstration before Zaalima Development evaluation panel.
