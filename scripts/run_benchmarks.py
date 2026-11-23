"""
Benchmarking Script: Compares Centralized vs Vanilla FedAvg vs Privacy-Preserving FHE Swarm.
"""

import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.benchmark.profiler import SwarmBenchmarkProfiler


def main():
    print("\n" + "=" * 80)
    print("  ZAALIMA DEVELOPMENT PVT. LTD. — PERFORMANCE & SECURITY BENCHMARK")
    print("  PROJECT 2: PRIVACY-PRESERVING FEDERATED SWARM INTELLIGENCE")
    print("=" * 80 + "\n")

    profiler = SwarmBenchmarkProfiler(n_samples=1000, num_rounds=4, seed=42)
    print("[*] Executing comparative evaluation across architectures...")

    results = profiler.run_full_comparative_benchmark()
    df = pd.DataFrame(results)

    print("\n" + "-" * 80)
    print(df[["mode", "val_accuracy", "data_transferred_mb", "privacy_guarantee", "byzantine_resilience"]].to_string(index=False))
    print("-" * 80)
    print("\n[+] Benchmark completed successfully. All empirical metrics recorded.\n")


if __name__ == "__main__":
    main()
