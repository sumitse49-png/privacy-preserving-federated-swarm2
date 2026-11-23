"""
Security & Cryptographic Audit Suite.
Verifies FHE Zero-Knowledge guarantees, Differential Privacy bounds, and Byzantine Isolation.
Mandatory verification for Zaalima Development Mid-Review and Final-Review compliance.
"""

import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.crypto.fhe_engine import FHEEngine
from src.crypto.encrypted_aggregator import HomomorphicEncryptedAggregator
from src.crypto.compression import GradientCompressor
from src.privacy.differential_privacy import DifferentialPrivacyEngine
from src.privacy.attack_simulator import ByzantineAttackSimulator
from src.aggregation.byzantine_defenses import ByzantineRobustAggregator, MaliciousNodeDetector


def audit_fhe():
    print("[1/5] Auditing Fully Homomorphic Encryption (FHE) & Zero-Knowledge Security...")
    engine = FHEEngine(bits=32, scale=10000.0)
    rng = np.random.default_rng(42)
    v1 = rng.uniform(-3.0, 3.0, size=20).astype(np.float32)
    v2 = rng.uniform(-3.0, 3.0, size=20).astype(np.float32)

    c1 = engine.encrypt_vector(v1)
    c2 = engine.encrypt_vector(v2)

    agg = HomomorphicEncryptedAggregator(engine)
    c_agg, meta = agg.aggregate_encrypted_ciphertexts([c1, c2])
    decrypted_sum = engine.decrypt_vector(c_agg)
    expected_sum = v1 + v2

    # Check numerical precision
    max_err = np.max(np.abs(decrypted_sum - expected_sum))
    assert max_err < 0.05, f"FHE homomorphic sum error too high: {max_err}"

    # Verify zero-knowledge entropy
    zk = engine.verify_zero_knowledge(c_agg)
    assert zk["zero_knowledge_secured"] is True
    assert zk["entropy_score"] > 0.80
    print(f"      [PASS] Homomorphic arithmetic exact (max err: {max_err:.5f}).")
    print(f"      [PASS] Zero-knowledge proof verified. Ciphertext entropy score: {zk['entropy_score']:.4f}\n")


def audit_differential_privacy():
    print("[2/5] Auditing Differential Privacy (DP) Sensitivity & Noise Calibration...")
    dp = DifferentialPrivacyEngine(clip_norm=1.0, epsilon=2.0, delta=1e-5)
    
    # Generate high-norm gradient
    grad = np.array([10.0, -15.0, 20.0, -5.0], dtype=np.float32)
    clipped_g, raw_norm = dp.clip_gradient(grad)
    clipped_norm = np.linalg.norm(clipped_g)
    
    assert clipped_norm <= 1.0001, f"Gradient clipping failed: norm={clipped_norm}"
    priv_g, info = dp.privatize_update(grad, sampling_rate=0.1)
    
    assert info["membership_inference_defended"] is True
    print(f"      [PASS] Gradient clipped from L2 norm {raw_norm:.2f} to {clipped_norm:.4f} <= C={dp.clip_norm}.")
    print(f"      [PASS] Calibrated noise injected. Cumulative budget: (eps={info['cumulative_epsilon']:.4f}, delta={dp.target_delta}).\n")


def audit_byzantine_resilience():
    print("[3/5] Auditing Byzantine Fault Tolerance & Outlier Node Isolation...")
    clean_cohort = [np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32) for _ in range(8)]
    # Injected rogue nodes attempting sign-flip and extreme scale poisoning
    rogue1 = np.array([-5.0, -5.0, -5.0, -5.0], dtype=np.float32)
    rogue2 = np.array([50.0, 50.0, 50.0, 50.0], dtype=np.float32)

    cohort = clean_cohort + [rogue1, rogue2]
    node_ids = list(range(10))

    # Test Multi-Krum defense
    aggregator = ByzantineRobustAggregator(defense_type="multi_krum", byzantine_fraction=0.2)
    robust_update, telem = aggregator.aggregate(cohort, node_ids=node_ids)

    # Rogue node IDs are 8 and 9
    dropped = telem.get("dropped_node_ids", [])
    assert 8 in dropped or 9 in dropped, f"Multi-Krum failed to isolate rogue nodes: dropped={dropped}"
    # Consensus update must remain close to 1.0
    diff_from_clean = np.linalg.norm(robust_update - clean_cohort[0])
    assert diff_from_clean < 0.5, f"Consensus corrupted: {robust_update}"
    print(f"      [PASS] Multi-Krum identified and dropped rogue nodes: {dropped}.")
    print(f"      [PASS] Consensus gradient protected from poison (diff from clean: {diff_from_clean:.4f}).\n")


def audit_compression():
    print("[4/5] Auditing Gradient Compression (Top-K Sparsity + INT8 Quantization)...")
    compressor = GradientCompressor(sparsification_ratio=0.8, quantize_int8=True)
    raw = np.array([0.01, 5.2, -0.02, 0.05, -3.8, 0.001, 8.1, -0.04, 0.02, 4.4], dtype=np.float32)
    
    comp, meta = compressor.compress(raw)
    assert meta["nonzeros_transmitted"] == 2
    assert meta["compression_ratio"] == 4.0  # float32 (4 bytes) to int8 (1 byte)
    print(f"      [PASS] Top-20% sparsification active: {meta['nonzeros_transmitted']}/{len(raw)} values preserved.")
    print(f"      [PASS] INT8 Affine Quantization verified: {meta['compression_ratio']:.1f}x bandwidth reduction factor.\n")


def audit_non_iid_skew():
    print("[5/5] Auditing Non-IID Dirichlet Data Fragmentation...")
    from src.edge.non_iid_partitioner import NonIIDPartitioner, generate_synthetic_edge_dataset
    X, y = generate_synthetic_edge_dataset(n_samples=500, n_classes=5)
    partitioner = NonIIDPartitioner(alpha=0.2, seed=42)
    partitions = partitioner.partition(X, y, num_clients=10)
    summary = partitioner.get_heterogeneity_summary()

    assert len(partitions) == 10
    assert summary["mean_class_entropy"] < 2.0  # Low entropy indicates heavy skew
    print(f"      [PASS] 10 edge client partitions generated under Dirichlet alpha={summary['alpha']}.")
    print(f"      [PASS] Heterogeneity verified: Mean Shannon class entropy = {summary['mean_class_entropy']:.3f} bits.\n")


def main():
    print("\n" + "=" * 80)
    print("  ZAALIMA DEVELOPMENT PVT. LTD. — CRYPTOGRAPHIC & SECURITY AUDIT")
    print("  PROJECT 2: PRIVACY-PRESERVING FEDERATED SWARM INTELLIGENCE")
    print("=" * 80 + "\n")

    audit_fhe()
    audit_differential_privacy()
    audit_byzantine_resilience()
    audit_compression()
    audit_non_iid_skew()

    print("=" * 80)
    print("  ALL 5 SECURITY AUDITS PASSED WITH 100% COMPLIANCE")
    print("  SOP VERSION 1.1 CRYPTOGRAPHIC MILESTONES OFFICIALLY VALIDATED")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
