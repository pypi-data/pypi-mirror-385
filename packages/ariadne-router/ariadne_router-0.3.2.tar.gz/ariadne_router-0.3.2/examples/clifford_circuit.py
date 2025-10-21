#!/usr/bin/env python3
"""Example: Clifford circuit simulation with Ariadne intelligent routing."""

from qiskit import QuantumCircuit

from ariadne import simulate


def main():
    """Demonstrate Ariadne's intelligent routing for Clifford circuits."""
    print("🔮 Ariadne Clifford Circuit Demo")
    print("=" * 40)

    # Create a Clifford circuit (H, S, CNOT gates only)
    qc = QuantumCircuit(4, 4)

    # Add Clifford gates
    qc.h(0)
    qc.s(1)
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.h(2)
    qc.s(3)
    qc.cx(2, 3)
    qc.measure_all()

    print(f"Circuit: {qc.num_qubits} qubits, {qc.depth()} depth")
    print(f"Gates: {len([inst for inst, _, _ in qc.data if inst.name != 'measure'])}")

    # Simulate with Ariadne (should route to Stim for Clifford circuits)
    result = simulate(qc, shots=1000)

    print(f"\nBackend used: {result.backend_used}")
    print(f"Execution time: {result.execution_time:.4f}s")
    print(f"Expected speedup: {result.routing_decision.expected_speedup:.1f}x")
    print(f"Confidence: {result.routing_decision.confidence_score:.2f}")

    print("\nMeasurement results:")
    for state, count in sorted(result.counts.items()):
        print(f"  {state}: {count}")


if __name__ == "__main__":
    main()
