#!/usr/bin/env python3
"""Large Circuit CUDA Performance Test

This script tests CUDA performance on larger circuits where
GPU acceleration should show significant benefits.
"""

import json
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from qiskit import QuantumCircuit

from ariadne.backends.cuda_backend import CUDABackend, get_cuda_info, is_cuda_available


@dataclass
class TestResult:
    """Results from a single test run."""

    circuit_name: str
    qubits: int
    shots: int
    cuda_time: float
    cpu_time: float
    speedup: float
    success: bool
    error: str = ""


def create_large_circuits() -> dict[str, QuantumCircuit]:
    """Create larger test circuits for benchmarking."""
    circuits = {}

    # Medium-large circuit (16 qubits)
    qc = QuantumCircuit(16, 16)
    for i in range(16):
        qc.h(i)
    for i in range(15):
        qc.cx(i, i + 1)
    qc.measure_all()
    circuits["medium_large"] = qc

    # Large circuit (20 qubits)
    qc = QuantumCircuit(20, 20)
    for i in range(20):
        qc.h(i)
    for i in range(19):
        qc.cx(i, i + 1)
    qc.measure_all()
    circuits["large"] = qc

    # Very large circuit (24 qubits)
    qc = QuantumCircuit(24, 24)
    for i in range(24):
        qc.h(i)
    for i in range(23):
        qc.cx(i, i + 1)
    qc.measure_all()
    circuits["very_large"] = qc

    # Non-Clifford large circuit (16 qubits with T gates)
    qc = QuantumCircuit(16, 16)
    for i in range(16):
        qc.h(i)
        qc.t(i)
    for i in range(15):
        qc.cx(i, i + 1)
    qc.measure_all()
    circuits["large_non_clifford"] = qc

    # Deep circuit (12 qubits, many layers)
    qc = QuantumCircuit(12, 12)
    for _ in range(10):  # 10 layers
        for i in range(12):
            qc.h(i)
        for i in range(11):
            qc.cx(i, i + 1)
        for i in range(12):
            qc.t(i)
    qc.measure_all()
    circuits["deep"] = qc

    return circuits


def test_cuda_backend(circuit: QuantumCircuit, shots: int) -> tuple[float, bool, str]:
    """Test CUDA backend performance."""
    try:
        if not is_cuda_available():
            return 0.0, False, "CUDA not available"

        backend = CUDABackend(prefer_gpu=True, allow_cpu_fallback=True)
        start_time = time.perf_counter()
        counts = backend.simulate(circuit, shots=shots)
        end_time = time.perf_counter()

        execution_time = end_time - start_time
        success = len(counts) > 0 and sum(counts.values()) == shots
        error = "" if success else "Invalid results"

        return execution_time, success, error

    except Exception as e:
        return 0.0, False, str(e)


def test_cpu_backend(circuit: QuantumCircuit, shots: int) -> tuple[float, bool, str]:
    """Test CPU backend performance (CUDA backend with CPU fallback)."""
    try:
        backend = CUDABackend(prefer_gpu=False, allow_cpu_fallback=True)
        start_time = time.perf_counter()
        counts = backend.simulate(circuit, shots=shots)
        end_time = time.perf_counter()

        execution_time = end_time - start_time
        success = len(counts) > 0 and sum(counts.values()) == shots
        error = "" if success else "Invalid results"

        return execution_time, success, error

    except Exception as e:
        return 0.0, False, str(e)


def run_benchmarks() -> list[TestResult]:
    """Run comprehensive benchmarks."""
    print("🚀 Starting Large Circuit CUDA Performance Test")
    print("=" * 60)

    # Check CUDA availability
    try:
        cuda_info = get_cuda_info()
        print(f"CUDA Available: {cuda_info['available']}")
        if cuda_info["available"]:
            print(f"Device Count: {cuda_info['device_count']}")
            for device in cuda_info.get("devices", []):
                print(f"  Device {device['device_id']}: {device['name']}")
                print(f"    Memory: {device['total_memory'] / 1024**3:.1f} GB")
                print(f"    Compute Capability: {device['compute_capability']}")
        else:
            print("⚠️  CUDA not available - will use CPU fallback for testing")
    except Exception as e:
        print(f"⚠️  Error checking CUDA availability: {str(e)}")
        print("Will attempt to continue with CPU fallback")
    print()

    circuits = create_large_circuits()
    results = []

    # Test with fewer shots for large circuits to avoid memory issues
    shot_counts = [100, 1000]

    for circuit_name, circuit in circuits.items():
        print(f"Testing {circuit_name} ({circuit.num_qubits} qubits)")

        for shots in shot_counts:
            print(f"  Shots: {shots}")

            # Test CUDA backend
            cuda_time, cuda_success, cuda_error = test_cuda_backend(circuit, shots)
            print(f"    CUDA: {cuda_time:.4f}s {'✓' if cuda_success else '✗'}")
            if not cuda_success:
                print(f"      Error: {cuda_error}")

            # Test CPU backend
            cpu_time, cpu_success, cpu_error = test_cpu_backend(circuit, shots)
            print(f"    CPU:  {cpu_time:.4f}s {'✓' if cpu_success else '✗'}")
            if not cpu_success:
                print(f"      Error: {cpu_error}")

            # Calculate speedup
            if cuda_success and cpu_success and cuda_time > 0:
                speedup = cpu_time / cuda_time
                print(f"    Speedup: {speedup:.2f}x")
            else:
                speedup = 0.0
                print("    Speedup: N/A")

            # Store result
            results.append(
                TestResult(
                    circuit_name=circuit_name,
                    qubits=circuit.num_qubits,
                    shots=shots,
                    cuda_time=cuda_time,
                    cpu_time=cpu_time,
                    speedup=speedup,
                    success=cuda_success and cpu_success,
                    error=cuda_error if not cuda_success else cpu_error if not cpu_success else "",
                )
            )

            print()

    return results


def analyze_results(results: list[TestResult]) -> dict:
    """Analyze benchmark results and compute statistics."""
    successful_results = [r for r in results if r.success and r.speedup > 0]

    analysis = {
        "cuda_available": is_cuda_available(),
        "total_tests": len(results),
        "successful_tests": len(successful_results),
        "results": [
            {
                "circuit": r.circuit_name,
                "qubits": r.qubits,
                "shots": r.shots,
                "cuda_time": r.cuda_time,
                "cpu_time": r.cpu_time,
                "speedup": r.speedup,
            }
            for r in results
        ],
    }

    if successful_results:
        speedups = [r.speedup for r in successful_results]
        analysis["speedup_stats"] = {
            "average": np.mean(speedups),
            "median": np.median(speedups),
            "maximum": np.max(speedups),
            "minimum": np.min(speedups),
            "std_dev": np.std(speedups),
        }

        # Group by circuit size
        by_size = {}
        for r in successful_results:
            if r.qubits not in by_size:
                by_size[r.qubits] = []
            by_size[r.qubits].append(r.speedup)

        analysis["by_circuit_size"] = {
            str(qubits): {"average_speedup": np.mean(speedups), "test_count": len(speedups)}
            for qubits, speedups in by_size.items()
        }

    return analysis


def main():
    """Main benchmark execution."""
    results = run_benchmarks()
    analysis = analyze_results(results)

    # Print summary
    print("📊 Large Circuit Benchmark Summary")
    print("=" * 60)
    print(f"Total tests: {analysis['total_tests']}")
    print(f"Successful tests: {analysis['successful_tests']}")
    print(f"CUDA available: {analysis['cuda_available']}")

    if "speedup_stats" in analysis:
        stats = analysis["speedup_stats"]
        print("\nSpeedup Statistics:")
        print(f"  Average: {stats['average']:.2f}x")
        print(f"  Median:  {stats['median']:.2f}x")
        print(f"  Maximum: {stats['maximum']:.2f}x")
        print(f"  Minimum: {stats['minimum']:.2f}x")
        print(f"  Std Dev: {stats['std_dev']:.2f}x")

        print("\nBy Circuit Size:")
        for qubits, data in analysis["by_circuit_size"].items():
            print(f"  {qubits} qubits: {data['average_speedup']:.2f}x average ({data['test_count']} tests)")

    # Save results
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    with open(results_dir / "large_cuda_results.json", "w") as f:
        json.dump(analysis, f, indent=2)

    print(f"\nResults saved to: {results_dir / 'large_cuda_results.json'}")


if __name__ == "__main__":
    main()
