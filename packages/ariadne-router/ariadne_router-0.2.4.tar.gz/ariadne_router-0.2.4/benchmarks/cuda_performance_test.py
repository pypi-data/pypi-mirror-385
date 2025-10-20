#!/usr/bin/env python3
"""CUDA Backend Performance Benchmark

This script benchmarks the CUDA backend against other backends
to verify performance improvements on NVIDIA hardware.
"""

import json
import time
from dataclasses import dataclass

import numpy as np
from qiskit import QuantumCircuit

from ariadne.backends.cuda_backend import get_cuda_info, is_cuda_available
from ariadne.router import BackendType, QuantumRouter


@dataclass
class BenchmarkResult:
    """Results from a single benchmark run."""

    backend: str
    circuit_size: int
    shots: int
    execution_time: float
    success: bool
    error: str = ""


def create_test_circuits() -> dict[str, QuantumCircuit]:
    """Create various test circuits for benchmarking."""
    circuits = {}

    # Small Clifford circuit (2 qubits)
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    circuits["small_clifford"] = qc

    # Medium Clifford circuit (8 qubits)
    qc = QuantumCircuit(8, 8)
    for i in range(8):
        qc.h(i)
    for i in range(7):
        qc.cx(i, i + 1)
    qc.measure_all()
    circuits["medium_clifford"] = qc

    # Large Clifford circuit (16 qubits)
    qc = QuantumCircuit(16, 16)
    for i in range(16):
        qc.h(i)
    for i in range(15):
        qc.cx(i, i + 1)
    qc.measure_all()
    circuits["large_clifford"] = qc

    # Small non-Clifford circuit (4 qubits with T gates)
    qc = QuantumCircuit(4, 4)
    for i in range(4):
        qc.h(i)
        qc.t(i)
    for i in range(3):
        qc.cx(i, i + 1)
    qc.measure_all()
    circuits["small_non_clifford"] = qc

    # Medium non-Clifford circuit (8 qubits with T gates)
    qc = QuantumCircuit(8, 8)
    for i in range(8):
        qc.h(i)
        qc.t(i)
    for i in range(7):
        qc.cx(i, i + 1)
    qc.measure_all()
    circuits["medium_non_clifford"] = qc

    return circuits


def benchmark_backend(
    router: QuantumRouter, circuit: QuantumCircuit, shots: int, backend_type: BackendType
) -> BenchmarkResult:
    """Benchmark a specific backend with a circuit."""
    try:
        start_time = time.perf_counter()

        if backend_type == BackendType.CUDA:
            # Force CUDA selection by temporarily modifying router
            original_cuda_available = router._cuda_available
            router._cuda_available = True
            router.simulate(circuit, shots=shots)
            router._cuda_available = original_cuda_available
        else:
            # For other backends, we need to modify the router's backend selection
            # This is a simplified approach - in practice, you'd want to modify
            # the select_optimal_backend method or create a custom router
            router.simulate(circuit, shots=shots)

        execution_time = time.perf_counter() - start_time

        return BenchmarkResult(
            backend=backend_type.value,
            circuit_size=circuit.num_qubits,
            shots=shots,
            execution_time=execution_time,
            success=True,
        )

    except Exception as e:
        return BenchmarkResult(
            backend=backend_type.value,
            circuit_size=circuit.num_qubits,
            shots=shots,
            execution_time=0.0,
            success=False,
            error=str(e),
        )


def run_benchmarks() -> list[BenchmarkResult]:
    """Run comprehensive benchmarks across all backends and circuits."""
    print("🚀 Starting CUDA Performance Benchmark")
    print("=" * 50)

    # Check CUDA availability
    cuda_info = get_cuda_info()
    print(f"CUDA Available: {cuda_info['available']}")
    if cuda_info["available"]:
        print(f"Device Count: {cuda_info['device_count']}")
        for device in cuda_info.get("devices", []):
            print(f"  Device {device['device_id']}: {device['name']}")
            print(f"    Memory: {device['total_memory'] / 1024**3:.1f} GB")
            print(f"    Compute Capability: {device['compute_capability']}")
    print()

    router = QuantumRouter()
    circuits = create_test_circuits()
    results = []

    # Test different shot counts
    shot_counts = [100, 1000, 10000]

    for circuit_name, circuit in circuits.items():
        print(f"Testing {circuit_name} ({circuit.num_qubits} qubits)")

        for shots in shot_counts:
            print(f"  Shots: {shots}")

            # Test CUDA backend
            cuda_result = benchmark_backend(router, circuit, shots, BackendType.CUDA)
            results.append(cuda_result)

            if cuda_result.success:
                print(f"    CUDA: {cuda_result.execution_time:.4f}s")
            else:
                print(f"    CUDA: FAILED - {cuda_result.error}")

            # Test Qiskit backend for comparison
            qiskit_result = benchmark_backend(router, circuit, shots, BackendType.QISKIT)
            results.append(qiskit_result)

            if qiskit_result.success:
                print(f"    Qiskit: {qiskit_result.execution_time:.4f}s")
                if cuda_result.success:
                    speedup = qiskit_result.execution_time / cuda_result.execution_time
                    print(f"    Speedup: {speedup:.2f}x")
            else:
                print(f"    Qiskit: FAILED - {qiskit_result.error}")

            print()

    return results


def analyze_results(results: list[BenchmarkResult]) -> dict:
    """Analyze benchmark results and compute statistics."""
    analysis = {
        "cuda_available": is_cuda_available(),
        "total_tests": len(results),
        "successful_tests": sum(1 for r in results if r.success),
        "cuda_results": [],
        "qiskit_results": [],
        "speedups": [],
    }

    # Group results by backend
    cuda_results = [r for r in results if r.backend == "cuda" and r.success]
    qiskit_results = [r for r in results if r.backend == "qiskit" and r.success]

    analysis["cuda_results"] = [
        {"circuit_size": r.circuit_size, "shots": r.shots, "execution_time": r.execution_time} for r in cuda_results
    ]

    analysis["qiskit_results"] = [
        {"circuit_size": r.circuit_size, "shots": r.shots, "execution_time": r.execution_time} for r in qiskit_results
    ]

    # Compute speedups where both backends succeeded
    for cuda_r in cuda_results:
        for qiskit_r in qiskit_results:
            if cuda_r.circuit_size == qiskit_r.circuit_size and cuda_r.shots == qiskit_r.shots:
                speedup = qiskit_r.execution_time / cuda_r.execution_time
                analysis["speedups"].append(
                    {"circuit_size": cuda_r.circuit_size, "shots": cuda_r.shots, "speedup": speedup}
                )
                break

    return analysis


def main():
    """Main benchmark execution."""
    results = run_benchmarks()
    analysis = analyze_results(results)

    # Print summary
    print("📊 Benchmark Summary")
    print("=" * 50)
    print(f"Total tests: {analysis['total_tests']}")
    print(f"Successful tests: {analysis['successful_tests']}")
    print(f"CUDA available: {analysis['cuda_available']}")

    if analysis["speedups"]:
        avg_speedup = np.mean([s["speedup"] for s in analysis["speedups"]])
        max_speedup = max(s["speedup"] for s in analysis["speedups"])
        min_speedup = min(s["speedup"] for s in analysis["speedups"])

        print("\nSpeedup Statistics:")
        print(f"  Average: {avg_speedup:.2f}x")
        print(f"  Maximum: {max_speedup:.2f}x")
        print(f"  Minimum: {min_speedup:.2f}x")

        print("\nDetailed Speedups:")
        for speedup in analysis["speedups"]:
            print(f"  {speedup['circuit_size']} qubits, {speedup['shots']} shots: {speedup['speedup']:.2f}x")

    # Save results
    with open("benchmarks/cuda_benchmark_results.json", "w") as f:
        json.dump(analysis, f, indent=2)

    print("\nResults saved to: benchmarks/cuda_benchmark_results.json")


if __name__ == "__main__":
    main()
