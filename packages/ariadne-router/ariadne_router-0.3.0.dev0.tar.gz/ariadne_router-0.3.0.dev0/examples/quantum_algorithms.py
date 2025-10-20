#!/usr/bin/env python3
"""
Quantum Algorithm Examples with Ariadne

Demonstrates how Ariadne intelligently routes different quantum algorithms.
"""

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

from ariadne import QuantumRouter, analyze_circuit, simulate


def grover_circuit(n_qubits: int = 3) -> QuantumCircuit:
    """Create Grover's algorithm circuit."""
    qc = QuantumCircuit(n_qubits, n_qubits)

    # Initialize in superposition
    for i in range(n_qubits):
        qc.h(i)

    # Oracle (mark |111...1>)
    qc.h(n_qubits - 1)
    qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
    qc.h(n_qubits - 1)

    # Diffusion operator
    for i in range(n_qubits):
        qc.h(i)
    for i in range(n_qubits):
        qc.x(i)
    qc.h(n_qubits - 1)
    qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
    qc.h(n_qubits - 1)
    for i in range(n_qubits):
        qc.x(i)
    for i in range(n_qubits):
        qc.h(i)

    qc.measure_all()
    return qc


def quantum_phase_estimation(n_counting_qubits: int = 3) -> QuantumCircuit:
    """Create a simple QPE circuit."""
    # Create registers
    counting = QuantumRegister(n_counting_qubits, "counting")
    target = QuantumRegister(1, "target")
    c_reg = ClassicalRegister(n_counting_qubits, "meas")

    qc = QuantumCircuit(counting, target, c_reg)

    # Initialize target in |1>
    qc.x(target)

    # Put counting qubits in superposition
    for qubit in counting:
        qc.h(qubit)

    # Controlled rotations
    repetitions = 1
    for counting_qubit in range(n_counting_qubits):
        for _ in range(repetitions):
            qc.cp(np.pi / 4, counting[counting_qubit], target)
        repetitions *= 2

    # Inverse QFT on counting qubits
    for qubit in range(n_counting_qubits // 2):
        qc.swap(counting[qubit], counting[n_counting_qubits - qubit - 1])

    for j in range(n_counting_qubits):
        for k in range(j):
            qc.cp(-np.pi / float(2 ** (j - k)), counting[k], counting[j])
        qc.h(counting[j])

    # Measure counting qubits
    qc.measure(counting, c_reg)

    return qc


def quantum_teleportation() -> QuantumCircuit:
    """Create quantum teleportation circuit."""
    qc = QuantumCircuit(3, 3)
    c_reg = qc.cregs[0]

    # Create entangled pair (Bell state)
    qc.h(1)
    qc.cx(1, 2)

    # Prepare state to teleport (arbitrary state on q0)
    qc.ry(np.pi / 3, 0)  # Some rotation

    qc.barrier()

    # Bell measurement on q0 and q1
    qc.cx(0, 1)
    qc.h(0)
    qc.measure([0, 1], [0, 1])

    qc.barrier()

    # Apply corrections
    qc.cx(1, 2).c_if(c_reg[1], 1)
    qc.cz(0, 2).c_if(c_reg[0], 1)

    # Measure target qubit
    qc.measure(2, 2)

    return qc


def bernstein_vazirani(n_bits: int = 4, secret: str = "1011") -> QuantumCircuit:
    """Bernstein-Vazirani algorithm - finds secret string in one query."""
    n_qubits = n_bits + 1  # n bits + 1 ancilla
    qc = QuantumCircuit(n_qubits, n_bits)

    # Initialize ancilla in |->
    qc.x(n_bits)
    qc.h(n_bits)

    # Put all qubits in superposition
    for i in range(n_bits):
        qc.h(i)

    # Oracle
    for i in range(n_bits):
        if secret[i] == "1":
            qc.cx(i, n_bits)

    # Another round of Hadamards
    for i in range(n_bits):
        qc.h(i)

    # Measure
    for i in range(n_bits):
        qc.measure(i, i)

    return qc


def analyze_algorithms():
    """Analyze how Ariadne routes different quantum algorithms."""
    print("=== Quantum Algorithm Routing Analysis ===\n")

    router = QuantumRouter()

    algorithms = [
        ("Grover's Search", grover_circuit(4)),
        ("Quantum Phase Estimation", quantum_phase_estimation(4)),
        ("Quantum Teleportation", quantum_teleportation()),
        ("Bernstein-Vazirani", bernstein_vazirani(5)),
    ]

    for name, circuit in algorithms:
        print(f"{name}:")

        # Analyze circuit
        analysis = analyze_circuit(circuit)
        print("  Circuit properties:")
        print(f"    - Qubits: {analysis['num_qubits']}")
        print(f"    - Depth: {analysis['depth']}")
        print(f"    - Gate count: {sum(analysis['gate_counts'].values())}")
        print(f"    - Clifford ratio: {analysis['clifford_ratio']:.2%}")
        print(f"    - Is pure Clifford: {analysis['is_clifford']}")

        # Get routing decision
        decision = router.select_optimal_backend(circuit)
        print("  Routing decision:")
        print(f"    - Backend: {decision.recommended_backend}")
        print(f"    - Circuit entropy: {decision.circuit_entropy:.3f}")
        print(f"    - Expected speedup: {decision.expected_speedup:.1f}x")

        # Run simulation
        result = simulate(circuit, shots=1000)
        print("  Execution:")
        print(f"    - Backend used: {result.backend_used}")
        print(f"    - Time: {result.execution_time:.4f}s")

        # Show some results
        if len(result.counts) <= 8:
            print(f"    - Results: {result.counts}")
        else:
            top_3 = sorted(result.counts.items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"    - Top 3 results: {dict(top_3)}")

        print()


def main():
    analyze_algorithms()

    print("=== Key Insights ===")
    print("- Clifford-heavy circuits (like some error correction) → Stim")
    print("- Circuits with rotations/phases → Qiskit or CUDA")
    print("- Large sparse circuits → Tensor networks (when available)")
    print("\nAriadne makes these decisions automatically!")


if __name__ == "__main__":
    main()
