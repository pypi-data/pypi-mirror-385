#!/usr/bin/env python3
"""Performance Comparison Example

This example compares Ariadne's automatic backend selection
with direct backend usage for different circuit types.
"""

import time

from qiskit import QuantumCircuit

from ariadne import simulate
from ariadne.backends.cuda_backend import CUDABackend


def create_clifford_circuit(qubits: int) -> QuantumCircuit:
    """Create a Clifford circuit."""
    qc = QuantumCircuit(qubits, qubits)
    for i in range(qubits):
        qc.h(i)
    for i in range(qubits - 1):
        qc.cx(i, i + 1)
    qc.measure_all()
    return qc


def create_non_clifford_circuit(qubits: int) -> QuantumCircuit:
    """Create a non-Clifford circuit."""
    qc = QuantumCircuit(qubits, qubits)
    for i in range(qubits):
        qc.h(i)
        qc.t(i)  # T gate makes it non-Clifford
    for i in range(qubits - 1):
        qc.cx(i, i + 1)
    qc.measure_all()
    return qc


def benchmark_circuit(circuit: QuantumCircuit, shots: int = 1000) -> dict:
    """Benchmark a circuit with different approaches."""
    results = {}

    # Ariadne automatic selection
    start_time = time.perf_counter()
    ariadne_result = simulate(circuit, shots=shots)
    ariadne_time = time.perf_counter() - start_time

    results["ariadne"] = {
        "time": ariadne_time,
        "backend": ariadne_result.backend_used.value,
        "confidence": ariadne_result.routing_decision.confidence_score,
        "speedup": ariadne_result.routing_decision.expected_speedup,
    }

    # Direct CUDA backend (if available)
    try:
        cuda_backend = CUDABackend()
        start_time = time.perf_counter()
        cuda_result = cuda_backend.simulate(circuit, shots=shots)
        cuda_time = time.perf_counter() - start_time

        results["cuda_direct"] = {
            "time": cuda_time,
            "backend": "cuda",
            "mode": cuda_backend.backend_mode,
            "sample_counts": dict(list(cuda_result.items())[:3]),
        }
    except Exception as e:
        results["cuda_direct"] = {"error": str(e)}

    return results


def main():
    """Performance comparison demonstration."""
    print("🚀 Performance Comparison: Ariadne vs Direct Backends")
    print("=" * 60)

    # Test different circuit types and sizes
    test_cases = [
        ("Clifford", create_clifford_circuit, [4, 8, 12]),
        ("Non-Clifford", create_non_clifford_circuit, [4, 8, 12]),
    ]

    for circuit_type, create_func, sizes in test_cases:
        print(f"\n{circuit_type} Circuits:")
        print("-" * 30)

        for qubits in sizes:
            print(f"\n{qubits} qubits:")
            circuit = create_func(qubits)

            results = benchmark_circuit(circuit, shots=1000)

            # Ariadne results
            ariadne = results["ariadne"]
            print(f"  Ariadne: {ariadne['time']:.4f}s ({ariadne['backend']})")
            print(f"    Confidence: {ariadne['confidence']:.3f}")
            print(f"    Expected speedup: {ariadne['speedup']:.2f}x")

            # Direct CUDA results
            if "error" in results["cuda_direct"]:
                print(f"  CUDA Direct: {results['cuda_direct']['error']}")
            else:
                cuda = results["cuda_direct"]
                print(f"  CUDA Direct: {cuda['time']:.4f}s ({cuda['mode']})")

                # Calculate speedup
                if cuda["time"] > 0:
                    speedup = ariadne["time"] / cuda["time"]
                    print(f"    Ariadne vs CUDA: {speedup:.2f}x")


if __name__ == "__main__":
    main()
