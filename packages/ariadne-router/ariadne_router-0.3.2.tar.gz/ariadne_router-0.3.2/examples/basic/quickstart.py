#!/usr/bin/env python3
"""Ariadne Quick Start Example

This example demonstrates practical usage of Ariadne for quantum circuit simulation,
showing real-world scenarios and best practices.
"""

from qiskit import QuantumCircuit

from ariadne import simulate


def create_bell_state():
    """Create a Bell state circuit - good for testing basic functionality."""
    print("Creating Bell state circuit...")
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    return qc


def create_ghz_state(n_qubits=10):
    """Create a GHZ state - demonstrates scalability."""
    print(f"Creating {n_qubits}-qubit GHZ state...")
    qc = QuantumCircuit(n_qubits, n_qubits)
    qc.h(0)
    for i in range(n_qubits - 1):
        qc.cx(i, i + 1)
    qc.measure_all()
    return qc


def create_variational_circuit(n_qubits=8):
    """Create a variational quantum circuit - shows non-Clifford optimization."""
    print(f"Creating {n_qubits}-qubit variational circuit...")
    qc = QuantumCircuit(n_qubits, n_qubits)

    # Layer 1: Hadamard layer
    for i in range(n_qubits):
        qc.h(i)

    # Layer 2: Entangling layer
    for i in range(n_qubits - 1):
        qc.cx(i, i + 1)

    # Layer 3: Rotation layer (non-Clifford gates)
    for i in range(n_qubits):
        qc.ry(0.5, i)  # Parameterized rotation
        if i % 2 == 0:
            qc.t(i)  # T gates trigger GPU selection

    qc.measure_all()
    return qc


def analyze_result(result, circuit_name):
    """Analyze and display simulation results."""
    print(f"\n--- {circuit_name} Results ---")
    print(f"Backend used: {result.backend_used}")
    print(f"Execution time: {result.execution_time:.4f}s")
    print(f"Unique outcomes: {len(result.counts)}")

    # Show routing decision details
    decision = result.routing_decision
    print("\nRouting Analysis:")
    print(f"  Confidence: {decision.confidence_score:.3f}")
    print(f"  Expected speedup: {decision.expected_speedup:.2f}x")
    print(f"  Circuit entropy: {decision.circuit_entropy:.3f}")

    # Show most probable outcomes
    sorted_counts = sorted(result.counts.items(), key=lambda x: x[1], reverse=True)
    print("\nTop 3 outcomes:")
    for state, count in sorted_counts[:3]:
        probability = count / sum(result.counts.values())
        print(f"  {state}: {count} ({probability:.1%})")


def main():
    """Demonstrate Ariadne with various practical examples."""
    print("🚀 Ariadne Practical Examples")
    print("=" * 50)
    print("Demonstrating real-world quantum circuit simulation scenarios\n")

    # Example 1: Basic entanglement (CPU optimal)
    qc1 = create_bell_state()
    result1 = simulate(qc1, shots=1000)
    analyze_result(result1, "Bell State (2 qubits)")

    # Example 2: Multi-qubit entanglement (GPU beneficial)
    qc2 = create_ghz_state(12)
    result2 = simulate(qc2, shots=1000)
    analyze_result(result2, "GHZ State (12 qubits)")

    # Example 3: Variational circuit (GPU optimal due to T gates)
    qc3 = create_variational_circuit(10)
    result3 = simulate(qc3, shots=1000)
    analyze_result(result3, "Variational Circuit (10 qubits)")

    print("\n" + "=" * 50)
    print("✅ All examples completed successfully!")
    print("💡 Tip: Larger circuits with non-Clifford gates benefit most from GPU acceleration")


if __name__ == "__main__":
    main()
