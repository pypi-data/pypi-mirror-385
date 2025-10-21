#!/usr/bin/env python3
"""CUDA Integration Test

This script tests the complete CUDA integration with the router system
to verify that CUDA is being selected appropriately for different circuit types.
"""

import json
import time
from dataclasses import dataclass

from qiskit import QuantumCircuit

from ariadne import simulate
from ariadne.backends.cuda_backend import get_cuda_info, is_cuda_available


@dataclass
class IntegrationTestResult:
    """Results from an integration test."""

    circuit_name: str
    qubits: int
    is_clifford: bool
    shots: int
    backend_used: str
    execution_time: float
    confidence_score: float
    expected_speedup: float
    channel_capacity_match: float
    success: bool
    error: str = ""


def create_test_circuits() -> dict[str, QuantumCircuit]:
    """Create various test circuits for integration testing."""
    circuits = {}

    # Small Clifford circuit (4 qubits)
    qc = QuantumCircuit(4, 4)
    for i in range(4):
        qc.h(i)
    for i in range(3):
        qc.cx(i, i + 1)
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

    # Large non-Clifford circuit (16 qubits with T gates)
    qc = QuantumCircuit(16, 16)
    for i in range(16):
        qc.h(i)
        qc.t(i)
    for i in range(15):
        qc.cx(i, i + 1)
    qc.measure_all()
    circuits["large_non_clifford"] = qc

    # Very large non-Clifford circuit (20 qubits with T gates)
    qc = QuantumCircuit(20, 20)
    for i in range(20):
        qc.h(i)
        qc.t(i)
    for i in range(19):
        qc.cx(i, i + 1)
    qc.measure_all()
    circuits["very_large_non_clifford"] = qc

    return circuits


def is_clifford_circuit(circuit: QuantumCircuit) -> bool:
    """Check if a circuit is Clifford."""
    clifford_gates = {"h", "x", "y", "z", "s", "sdg", "sx", "sxdg", "cx", "cz", "swap"}

    for instruction, _, _ in circuit.data:
        name = instruction.name
        if name in {"measure", "barrier", "delay"}:
            continue
        if name not in clifford_gates:
            return False
    return True


def run_integration_tests() -> list[IntegrationTestResult]:
    """Run comprehensive integration tests."""
    print("🚀 Starting CUDA Integration Test")
    print("=" * 60)

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

    circuits = create_test_circuits()
    results = []

    # Test with different shot counts
    shot_counts = [100, 1000]

    for circuit_name, circuit in circuits.items():
        is_clifford = is_clifford_circuit(circuit)
        print(f"Testing {circuit_name} ({circuit.num_qubits} qubits, {'Clifford' if is_clifford else 'Non-Clifford'})")

        for shots in shot_counts:
            print(f"  Shots: {shots}")

            try:
                start_time = time.perf_counter()
                result = simulate(circuit, shots=shots)
                end_time = time.perf_counter()

                execution_time = end_time - start_time
                backend_used = (
                    result.backend_used.value if hasattr(result.backend_used, "value") else str(result.backend_used)
                )

                print(f"    Backend: {backend_used}")
                print(f"    Time: {execution_time:.4f}s")
                print(f"    Confidence: {result.routing_decision.confidence_score:.3f}")
                print(f"    Expected Speedup: {result.routing_decision.expected_speedup:.3f}x")
                print(f"    Capacity Match: {result.routing_decision.channel_capacity_match:.3f}")

                # Check if CUDA was selected for large non-Clifford circuits
                if not is_clifford and circuit.num_qubits >= 16 and backend_used == "cuda":
                    print("    ✓ CUDA correctly selected for large non-Clifford circuit")
                elif is_clifford and backend_used in ["qiskit", "stim"]:
                    print("    ✓ Appropriate backend selected for Clifford circuit")
                elif not is_clifford and circuit.num_qubits < 16 and backend_used != "cuda":
                    print("    ✓ Appropriate backend selected for small non-Clifford circuit")

                results.append(
                    IntegrationTestResult(
                        circuit_name=circuit_name,
                        qubits=circuit.num_qubits,
                        is_clifford=is_clifford,
                        shots=shots,
                        backend_used=backend_used,
                        execution_time=execution_time,
                        confidence_score=result.routing_decision.confidence_score,
                        expected_speedup=result.routing_decision.expected_speedup,
                        channel_capacity_match=result.routing_decision.channel_capacity_match,
                        success=True,
                    )
                )

            except Exception as e:
                print(f"    ✗ FAILED: {str(e)}")
                results.append(
                    IntegrationTestResult(
                        circuit_name=circuit_name,
                        qubits=circuit.num_qubits,
                        is_clifford=is_clifford,
                        shots=shots,
                        backend_used="",
                        execution_time=0.0,
                        confidence_score=0.0,
                        expected_speedup=0.0,
                        channel_capacity_match=0.0,
                        success=False,
                        error=str(e),
                    )
                )

            print()

    return results


def analyze_integration_results(results: list[IntegrationTestResult]) -> dict:
    """Analyze integration test results."""
    successful_results = [r for r in results if r.success]

    # Count backend usage
    backend_usage = {}
    for r in successful_results:
        backend_usage[r.backend_used] = backend_usage.get(r.backend_used, 0) + 1

    # Count CUDA selection for different circuit types
    cuda_selections = {
        "small_clifford": 0,
        "medium_clifford": 0,
        "large_clifford": 0,
        "small_non_clifford": 0,
        "medium_non_clifford": 0,
        "large_non_clifford": 0,
        "very_large_non_clifford": 0,
    }

    for r in successful_results:
        if r.backend_used == "cuda":
            cuda_selections[r.circuit_name] = cuda_selections.get(r.circuit_name, 0) + 1

    analysis = {
        "cuda_available": is_cuda_available(),
        "total_tests": len(results),
        "successful_tests": len(successful_results),
        "backend_usage": backend_usage,
        "cuda_selections": cuda_selections,
        "results": [
            {
                "circuit": r.circuit_name,
                "qubits": r.qubits,
                "is_clifford": r.is_clifford,
                "shots": r.shots,
                "backend": r.backend_used,
                "execution_time": r.execution_time,
                "confidence": r.confidence_score,
                "expected_speedup": r.expected_speedup,
            }
            for r in results
        ],
    }

    return analysis


def main():
    """Main integration test execution."""
    results = run_integration_tests()
    analysis = analyze_integration_results(results)

    # Print summary
    print("📊 CUDA Integration Test Summary")
    print("=" * 60)
    print(f"Total tests: {analysis['total_tests']}")
    print(f"Successful tests: {analysis['successful_tests']}")
    print(f"CUDA available: {analysis['cuda_available']}")

    print("\nBackend Usage:")
    for backend, count in analysis["backend_usage"].items():
        print(f"  {backend}: {count} tests")

    print("\nCUDA Selection by Circuit Type:")
    for circuit_type, count in analysis["cuda_selections"].items():
        print(f"  {circuit_type}: {count} tests")

    # Check if CUDA is being selected appropriately
    large_non_clifford_cuda = analysis["cuda_selections"].get("large_non_clifford", 0) + analysis[
        "cuda_selections"
    ].get("very_large_non_clifford", 0)
    total_large_non_clifford = sum(1 for r in results if r.success and not r.is_clifford and r.qubits >= 16)

    if large_non_clifford_cuda > 0:
        print(
            f"\n✓ CUDA is being selected for large non-Clifford circuits ({large_non_clifford_cuda}/{total_large_non_clifford})"
        )
    else:
        print("\n✗ CUDA is not being selected for large non-Clifford circuits")

    # Save results
    with open("benchmarks/cuda_integration_results.json", "w") as f:
        json.dump(analysis, f, indent=2)

    print("\nResults saved to: benchmarks/cuda_integration_results.json")


if __name__ == "__main__":
    main()
