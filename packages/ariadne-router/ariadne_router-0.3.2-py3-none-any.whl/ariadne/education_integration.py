"""
Educational Integration Module for Ariadne

This module provides helpers and integration points to make educational
features more discoverable and accessible in primary workflows.
"""

from typing import Any

from .algorithms import AlgorithmParameters, get_algorithm, list_algorithms
from .education import InteractiveCircuitBuilder
from .router import simulate
from .types import SimulationResult


def run_educational_simulation(
    algorithm_name: str, n_qubits: int = 3, shots: int = 1000, verbose: bool = False
) -> tuple[SimulationResult, dict[str, str] | None]:
    """
    Run a simulation with educational algorithm and return both result and educational content.

    Args:
        algorithm_name: Name of the quantum algorithm to run
        n_qubits: Number of qubits for the algorithm
        shots: Number of measurement shots
        verbose: Whether to print additional educational information

    Returns:
        Tuple of (simulation result, educational content as dict)
    """
    # Validate algorithm name
    available_algorithms = list_algorithms()
    if algorithm_name not in available_algorithms:
        raise ValueError(f"Unknown algorithm: {algorithm_name}. Available: {available_algorithms}")

    # Get and instantiate the algorithm
    algorithm_class = get_algorithm(algorithm_name)
    params = AlgorithmParameters(n_qubits=n_qubits)
    algorithm_instance = algorithm_class(params)

    # Create the circuit
    circuit = algorithm_instance.create_circuit()

    if verbose:
        print(f"Running {algorithm_name.upper()} algorithm with {n_qubits} qubits")
        print(f"Circuit depth: {circuit.depth()}")
        print(f"Number of gates: {circuit.size()}")

    # Run the simulation
    result = simulate(circuit, shots=shots)

    if verbose:
        print(f"Backend used: {result.backend_used.value}")
        print(f"Execution time: {result.execution_time:.4f}s")
        print(f"Sample results: {dict(list(result.counts.items())[:5])}")

    # Get educational content
    educational_content = None
    if verbose:
        educational_content = algorithm_instance.get_educational_content()
        print("\nEducational Content:")
        for key, value in educational_content.items():
            if value and "not yet documented" not in value.lower():
                print(f"  {key.replace('_', ' ').title()}: {value}")

    return result, educational_content


def build_and_simulate_circuit(n_qubits: int, steps: list[dict[str, Any]], shots: int = 1000) -> SimulationResult:
    """
    Build a quantum circuit step-by-step using the interactive builder and simulate it.

    Args:
        n_qubits: Number of qubits for the circuit
        steps: List of step dictionaries with gate information
        shots: Number of measurement shots

    Returns:
        Simulation result
    """
    """
    Build a quantum circuit step-by-step using the interactive builder and simulate it.

    Args:
        n_qubits: Number of qubits for the circuit
        steps: List of step dictionaries with gate information
        shots: Number of measurement shots

    Returns:
        Simulation result
    """
    builder = InteractiveCircuitBuilder(n_qubits, "Custom Educational Circuit")

    # Execute each step
    for step in steps:
        gate_type = step.get("gate")
        if gate_type == "h":
            qubit = step.get("qubit")
            title = step.get("title", "Hadamard Gate")
            desc = step.get("description", "Apply a Hadamard gate to create superposition")
            if qubit is not None and isinstance(qubit, int):
                builder.add_hadamard(qubit, title, desc)
        elif gate_type == "cx":
            control = step.get("control")
            target = step.get("target")
            title = step.get("title", "CNOT Gate")
            desc = step.get("description", "Apply a CNOT gate to create entanglement")
            if control is not None and target is not None and isinstance(control, int) and isinstance(target, int):
                builder.add_cnot(control, target, title, desc)
        elif gate_type == "rz":
            qubit = step.get("qubit")
            angle = step.get("angle", 0.0)
            title = step.get("title", "RZ Gate")
            desc = step.get("description", f"Apply an RZ rotation with angle {angle}")
            # We'll need to add rotation functionality to the builder in a real implementation
            # For now, we add a placeholder
            # builder.add_rotation(qubit, angle, title, desc)
        elif gate_type == "measure":
            qubit = step.get("qubit")
            title = step.get("title", "Measurement")
            desc = step.get("description", "Measure the qubit")
            if qubit is not None and isinstance(qubit, int):
                builder.add_measurement(qubit, title, desc)

    circuit = builder.get_circuit()
    return simulate(circuit, shots=shots)


def explore_algorithm_step_by_step(algorithm_name: str, n_qubits: int = 3) -> None:
    """
    Create a step-by-step exploration of a quantum algorithm.

    Args:
        algorithm_name: Name of the quantum algorithm to explore
        n_qubits: Number of qubits for the algorithm
    """
    print(f"Exploring {algorithm_name.upper()} Algorithm Step-by-Step")
    print("=" * 50)

    # Get and instantiate the algorithm
    algorithm_class = get_algorithm(algorithm_name)
    params = AlgorithmParameters(n_qubits=n_qubits)
    algorithm_instance = algorithm_class(params)

    # This would be more complex in practice - showing the actual algorithm steps
    print(f"Algorithm: {algorithm_instance.metadata.name}")
    print(f"Category: {algorithm_instance.metadata.category}")
    print(f"Description: {algorithm_instance.metadata.description}")
    print(f"Complexity: {algorithm_instance.metadata.complexity}")

    circuit = algorithm_instance.create_circuit()
    print("\nCircuit Properties:")
    print(f"  Qubits: {circuit.num_qubits}")
    print(f"  Depth: {circuit.depth()}")
    print(f"  Size: {circuit.size()}")

    analysis = algorithm_instance.analyze_circuit_properties()
    print(f"  Gate types: {list(analysis['gate_counts'].keys())}")
    print(f"  Two-qubit gates: {analysis['two_qubit_gates']}")
    print(f"  Entanglement heuristic: {analysis['entanglement_heuristic']:.3f}")

    # Show educational content
    educational_content = algorithm_instance.get_educational_content()
    print("\nEducational Content:")
    for key, value in educational_content.items():
        if value and "not yet documented" not in value.lower():
            print(f"  {key.replace('_', ' ').title()}: {value}")


# Convenience functions for common educational workflows
def demo_bell_state(shots: int = 1000, verbose: bool = False) -> SimulationResult:
    """Create and simulate a Bell state circuit."""
    result, _ = run_educational_simulation("bell", n_qubits=2, shots=shots, verbose=verbose)
    return result


def demo_ghz_state(n_qubits: int = 3, shots: int = 1000, verbose: bool = False) -> SimulationResult:
    """Create and simulate a GHZ state circuit."""
    result, _ = run_educational_simulation("ghz", n_qubits=n_qubits, shots=shots, verbose=verbose)
    return result


def demo_qft(n_qubits: int = 3, shots: int = 100, verbose: bool = False) -> SimulationResult:
    """Create and simulate a Quantum Fourier Transform circuit."""
    result, _ = run_educational_simulation("qft", n_qubits=n_qubits, shots=shots, verbose=verbose)
    return result


def demo_grover(n_qubits: int = 4, shots: int = 100, verbose: bool = False) -> SimulationResult:
    """Create and simulate a Grover's algorithm circuit."""
    result, _ = run_educational_simulation("grover", n_qubits=n_qubits, shots=shots, verbose=verbose)
    return result
