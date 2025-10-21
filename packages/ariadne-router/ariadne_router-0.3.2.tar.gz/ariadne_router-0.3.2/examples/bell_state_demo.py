#!/usr/bin/env python3
"""Example: Bell state creation and measurement with Ariadne."""

from qiskit import QuantumCircuit

from ariadne import simulate


def main():
    """Demonstrate Bell state creation and measurement."""
    print("🔮 Ariadne Bell State Demo")
    print("=" * 30)

    # Create Bell state |Φ+⟩ = (|00⟩ + |11⟩)/√2
    qc = QuantumCircuit(2, 2)
    qc.h(0)  # Create superposition
    qc.cx(0, 1)  # Entangle qubits
    qc.measure_all()

    print("Bell state circuit:")
    print(qc.draw(output="text"))

    # Simulate with Ariadne
    result = simulate(qc, shots=1000)

    print(f"\nBackend used: {result.backend_used}")
    print(f"Execution time: {result.execution_time:.4f}s")
    print(f"Circuit entropy: {result.routing_decision.circuit_entropy:.3f}")

    print("\nMeasurement results:")
    for state, count in sorted(result.counts.items()):
        print(f"  {state}: {count}")

    # Verify Bell state properties
    total = sum(result.counts.values())
    prob_00 = result.counts.get("00", 0) / total
    prob_11 = result.counts.get("11", 0) / total

    print("\nBell state verification:")
    print(f"  P(00): {prob_00:.3f} (expected: ~0.5)")
    print(f"  P(11): {prob_11:.3f} (expected: ~0.5)")
    print(f"  P(01) + P(10): {1 - prob_00 - prob_11:.3f} (expected: ~0.0)")


if __name__ == "__main__":
    main()
