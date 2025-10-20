#!/usr/bin/env python3
"""Advanced Quantum Algorithm Examples

This example demonstrates practical quantum algorithms and research applications
using Ariadne's intelligent backend selection.
"""

import time

from qiskit import QuantumCircuit

from ariadne import simulate


def create_quantum_fourier_transform(n_qubits: int) -> QuantumCircuit:
    """Create a Quantum Fourier Transform circuit - important for quantum algorithms."""
    print(f"Creating {n_qubits}-qubit QFT circuit...")
    qc = QuantumCircuit(n_qubits, n_qubits)

    # Quantum Fourier Transform implementation
    for i in range(n_qubits):
        qc.h(i)
        for j in range(i + 1, n_qubits):
            qc.cp(3.14159 / (2 ** (j - i)), i, j)

    # Inverse QFT for measurement
    for i in range(n_qubits // 2):
        qc.swap(i, n_qubits - 1 - i)

    qc.measure_all()
    return qc


def create_grover_oracle(n_qubits: int, marked_state: str) -> QuantumCircuit:
    """Create Grover's algorithm oracle - demonstrates quantum search."""
    print(f"Creating Grover oracle for {n_qubits}-qubit circuit...")
    qc = QuantumCircuit(n_qubits, n_qubits)

    # Oracle for marked state |11...1>
    for i in range(n_qubits):
        if marked_state[i] == "1":
            qc.x(i)

    # Multi-controlled X gate (Toffoli for n=2, general MCX for n>2)
    if n_qubits == 2:
        qc.cx(0, 1)
    else:
        qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)

    for i in range(n_qubits):
        if marked_state[i] == "1":
            qc.x(i)

    qc.measure_all()
    return qc


def create_variational_ansatz(n_qubits: int, layers: int = 2) -> QuantumCircuit:
    """Create a variational quantum ansatz - used in VQE and QML."""
    print(f"Creating {n_qubits}-qubit variational ansatz with {layers} layers...")
    qc = QuantumCircuit(n_qubits, n_qubits)

    # Initial Hadamard layer
    for i in range(n_qubits):
        qc.h(i)

    # Variational layers
    for layer in range(layers):
        # Entangling layer
        for i in range(n_qubits - 1):
            qc.cx(i, i + 1)

        # Rotation layer (parameterized)
        for i in range(n_qubits):
            qc.ry(0.1 * (layer + 1), i)  # Parameterized rotation
            if layer % 2 == 0:
                qc.t(i)  # T gates for GPU optimization

    qc.measure_all()
    return qc


def create_error_correction_demo(n_qubits: int = 5) -> QuantumCircuit:
    """Create a simple error correction demonstration."""
    print(f"Creating {n_qubits}-qubit error correction demo...")
    qc = QuantumCircuit(n_qubits, n_qubits)

    # Bit-flip code: |0> -> |000>, |1> -> |111>
    qc.cx(0, 1)
    qc.cx(0, 2)

    # Add some noise simulation (in practice, this would be physical noise)
    qc.x(1)  # Simulate bit flip error

    # Error correction
    qc.cx(0, 3)  # Syndrome measurement
    qc.cx(1, 3)
    qc.cx(1, 4)
    qc.cx(2, 4)

    qc.measure_all()
    return qc


def benchmark_algorithm(algorithm_func, name: str, **kwargs):
    """Benchmark a quantum algorithm with detailed analysis."""
    print(f"\n{'=' * 60}")
    print(f"Testing: {name}")
    print(f"{'=' * 60}")

    # Create circuit
    start_time = time.perf_counter()
    qc = algorithm_func(**kwargs)
    circuit_time = time.perf_counter() - start_time

    # Simulate
    sim_start = time.perf_counter()
    result = simulate(qc, shots=1000)
    sim_time = time.perf_counter() - sim_start
    total_time = time.perf_counter() - start_time

    # Analyze results
    print(f"Circuit creation: {circuit_time:.4f}s")
    print(f"Simulation time: {sim_time:.4f}s")
    print(f"Total time: {total_time:.4f}s")
    print(f"Backend used: {result.backend_used}")
    print(f"Unique outcomes: {len(result.counts)}")

    decision = result.routing_decision
    print("\nRouting Analysis:")
    print(f"  Confidence: {decision.confidence_score:.3f}")
    print(f"  Expected speedup: {decision.expected_speedup:.2f}x")
    print(f"  Circuit entropy: {decision.circuit_entropy:.3f}")

    # Show most probable outcomes
    sorted_counts = sorted(result.counts.items(), key=lambda x: x[1], reverse=True)
    print("\nTop outcomes:")
    for state, count in sorted_counts[:5]:
        probability = count / sum(result.counts.values())
        print(f"  {state}: {count} ({probability:.1%})")

    return result


def main():
    """Demonstrate advanced quantum algorithms with Ariadne."""
    print("🚀 Advanced Quantum Algorithm Demonstrations")
    print("=" * 60)
    print("Showcasing practical quantum computing applications\n")

    # Test different algorithms
    results = []

    # 1. Quantum Fourier Transform (important for many algorithms)
    results.append(
        benchmark_algorithm(create_quantum_fourier_transform, "Quantum Fourier Transform (8 qubits)", n_qubits=8)
    )

    # 2. Grover's Algorithm (quantum search)
    results.append(
        benchmark_algorithm(
            create_grover_oracle,
            "Grover's Algorithm (3 qubits, marked |111>)",
            n_qubits=3,
            marked_state="111",
        )
    )

    # 3. Variational Quantum Eigensolver (VQE) ansatz
    results.append(
        benchmark_algorithm(
            create_variational_ansatz,
            "Variational Quantum Ansatz (6 qubits, 2 layers)",
            n_qubits=6,
            layers=2,
        )
    )

    # 4. Error Correction (quantum fault tolerance)
    results.append(
        benchmark_algorithm(create_error_correction_demo, "Quantum Error Correction Demo (5 qubits)", n_qubits=5)
    )

    print(f"\n{'=' * 60}")
    print("✅ All advanced examples completed successfully!")
    print("💡 These algorithms demonstrate real quantum computing applications")
    print("🔬 QFT: Used in Shor's algorithm, quantum phase estimation")
    print("🔍 Grover: Quadratic speedup for unstructured search")
    print("⚛️ VQE: Finding ground state energy of molecules")
    print("🛡️ QEC: Essential for fault-tolerant quantum computing")


if __name__ == "__main__":
    main()
