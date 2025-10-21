#!/usr/bin/env python3
"""
Educational Demo for Ariadne Quantum Simulator

This example demonstrates the educational features of Ariadne,
including algorithm exploration, interactive learning, and
quantum circuit construction.
"""

from ariadne import (
    AlgorithmParameters,
    explain_routing,
    get_algorithm,
    get_algorithms_by_category,
    list_algorithms,
    simulate,
)
from ariadne.education import InteractiveCircuitBuilder


def demonstrate_education_features():
    """Demonstrate the educational features of Ariadne."""
    print("=" * 60)
    print("Ariadne Educational Features Demo")
    print("=" * 60)

    # 1. List available algorithms
    print("\n1. Available Quantum Algorithms:")
    print("-" * 30)
    algorithms = list_algorithms()
    print(f"Total algorithms available: {len(algorithms)}")

    # Show algorithms by category
    for category in get_algorithms_by_category.__code__.co_varnames:
        # Since we don't have a direct function to list categories,
        # we'll just show a few examples
        if category in ['foundational', 'search', 'optimization', 'error_correction', 'machine_learning', 'specialized']:
            category_algorithms = get_algorithms_by_category(category)
            if category_algorithms:
                print(f"  {category.title()}: {', '.join(category_algorithms[:5])}{'...' if len(category_algorithms) > 5 else ''}")

    print(f"\n  Full list: {', '.join(algorithms)}")

    # 2. Demonstrate using the Bell State algorithm
    print("\n2. Bell State Algorithm Demo:")
    print("-" * 30)

    BellState = get_algorithm("bell")
    bell_params = AlgorithmParameters(n_qubits=2)
    bell_algorithm = BellState(bell_params)

    bell_circuit = bell_algorithm.create_circuit()
    print(f"Bell circuit has {bell_circuit.num_qubits} qubits and depth {bell_circuit.depth()}")

    # Simulate the Bell state
    result = simulate(bell_circuit, shots=1000)
    print(f"Backend used: {result.backend_used.value}")
    print(f"Execution time: {result.execution_time:.4f}s")
    print(f"Routing explanation: {result.routing_explanation}")
    print(f"Sample results: {dict(list(result.counts.items())[:5])}")

    # Show educational content
    print("\nEducational Content:")
    educational_content = bell_algorithm.get_educational_content()
    for key, value in educational_content.items():
        if value and "not yet documented" not in value.lower():
            print(f"  {key.replace('_', ' ').title()}: {value[:100]}{'...' if len(value) > 100 else ''}")

    # 3. Demonstrate using the QFT algorithm
    print("\n3. Quantum Fourier Transform Demo:")
    print("-" * 30)

    QFT = get_algorithm("qft")
    qft_params = AlgorithmParameters(n_qubits=3)
    qft_algorithm = QFT(qft_params)

    qft_circuit = qft_algorithm.create_circuit()
    print(f"QFT circuit has {qft_circuit.num_qubits} qubits and depth {qft_circuit.depth()}")

    result = simulate(qft_circuit, shots=100)
    print(f"Backend used: {result.backend_used.value}")
    print(f"Routing explanation: {result.routing_explanation}")
    print(f"Sample results: {dict(list(result.counts.items())[:5])}")

    # 4. Demonstrate interactive circuit building
    print("\n4. Interactive Circuit Builder Demo:")
    print("-" * 30)

    builder = InteractiveCircuitBuilder(3, "GHZ State Circuit")
    # Build a GHZ state: H on first qubit, then CNOTs to the others
    builder.add_hadamard(0, "Create Superposition", "Apply H gate to qubit 0")
    builder.add_cnot(0, 1, "Create Entanglement", "Apply CNOT with qubit 0 as control, qubit 1 as target")
    builder.add_cnot(0, 2, "Extend Entanglement", "Apply CNOT with qubit 0 as control, qubit 2 as target")

    circuit = builder.get_circuit()
    print(f"Built circuit: {circuit.num_qubits} qubits, depth {circuit.depth()}")

    result = simulate(circuit, shots=100)
    print(f"GHZ State simulation result: {dict(result.counts)}")

    # 5. Show routing transparency for educational purposes
    print("\n5. Routing Decision Transparency:")
    print("-" * 30)

    explanation = explain_routing(bell_circuit)
    print(f"Bell state routing explanation: {explanation}")

    print("\n" + "=" * 60)
    print("Educational Features Demo Complete!")
    print("Try creating your own quantum algorithms using:")
    print("  - get_algorithm('algorithm_name') to get an algorithm class")
    print("  - AlgorithmParameters(n_qubits=N) to set parameters")
    print("  - algorithm_instance.create_circuit() to build the circuit")
    print("  - simulate(circuit) to run the simulation")
    print("  - algorithm_instance.get_educational_content() for learning materials")
    print("=" * 60)


if __name__ == "__main__":
    demonstrate_education_features()
