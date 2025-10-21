"""
Educational Devices and Interactive Learning Tools for Quantum Algorithms.

This module provides interactive devices for learning quantum algorithms,
including step-by-step circuit builders, visualizations, and educational
simulations.
"""

from dataclasses import dataclass
from typing import Any

import numpy as np
from IPython.display import HTML, display
from qiskit import QuantumCircuit

from .algorithms import AlgorithmParameters, get_algorithm, list_algorithms
from .core import get_logger
from .router import simulate

# Set up logging
logger = get_logger(__name__)


@dataclass
class LearningStep:
    """Represents a step in an educational algorithm walkthrough."""

    step_number: int
    title: str
    description: str
    circuit: QuantumCircuit | None = None
    visualization_data: dict | None = None


class InteractiveCircuitBuilder:
    """
    Interactive circuit builder for educational purposes.

    Allows users to build quantum circuits step-by-step with explanations.
    """

    def __init__(self, n_qubits: int, title: str = "Quantum Circuit"):
        """
        Initialize the interactive circuit builder.

        Args:
            n_qubits: Number of qubits in the circuit
            title: Title for the circuit

        Raises:
            ValueError: If n_qubits is not positive
        """
        if n_qubits <= 0:
            raise ValueError(f"Number of qubits must be positive, got {n_qubits}")

        self.n_qubits = n_qubits
        self.title = title
        self.circuit = QuantumCircuit(n_qubits, n_qubits)  # Add classical bits too
        self.history: list[LearningStep] = []
        self.current_step = 0

    def add_hadamard(
        self,
        qubit_idx: int,
        step_title: str = "Hadamard Gate",
        description: str = "Apply a Hadamard gate to create superposition",
    ) -> "InteractiveCircuitBuilder":
        """
        Add a Hadamard gate to the circuit.

        Args:
            qubit_idx: Index of the qubit to apply the gate to
            step_title: Title for this learning step
            description: Description of what this step does

        Returns:
            Self instance for method chaining

        Raises:
            ValueError: If qubit index is out of range
        """
        if not 0 <= qubit_idx < self.n_qubits:
            raise ValueError(f"Qubit index {qubit_idx} is out of range for circuit with {self.n_qubits} qubits")

        try:
            self.circuit.h(qubit_idx)
            step = LearningStep(
                step_number=self.current_step + 1,
                title=step_title,
                description=description,
                circuit=self.circuit.copy(),
            )
            self.history.append(step)
            self.current_step += 1
            logger.info(f"Added Hadamard gate to qubit {qubit_idx} in circuit '{self.title}'")
        except Exception as e:
            logger.error(f"Failed to add Hadamard gate to qubit {qubit_idx}: {e}")
            raise

        return self

    def add_cnot(
        self,
        control_idx: int,
        target_idx: int,
        step_title: str = "CNOT Gate",
        description: str = "Apply a CNOT gate to create entanglement",
    ) -> "InteractiveCircuitBuilder":
        """
        Add a CNOT gate to the circuit.

        Args:
            control_idx: Index of the control qubit
            target_idx: Index of the target qubit
            step_title: Title for this learning step
            description: Description of what this step does

        Returns:
            Self instance for method chaining

        Raises:
            ValueError: If qubit indices are out of range or if control equals target
        """
        if not 0 <= control_idx < self.n_qubits:
            raise ValueError(
                f"Control qubit index {control_idx} is out of range for circuit with {self.n_qubits} qubits"
            )
        if not 0 <= target_idx < self.n_qubits:
            raise ValueError(f"Target qubit index {target_idx} is out of range for circuit with {self.n_qubits} qubits")
        if control_idx == target_idx:
            raise ValueError("Control and target qubits cannot be the same")

        try:
            self.circuit.cx(control_idx, target_idx)
            step = LearningStep(
                step_number=self.current_step + 1,
                title=step_title,
                description=description,
                circuit=self.circuit.copy(),
            )
            self.history.append(step)
            self.current_step += 1
            logger.info(f"Added CNOT gate with control {control_idx}, target {target_idx} in circuit '{self.title}'")
        except Exception as e:
            logger.error(f"Failed to add CNOT gate: control {control_idx}, target {target_idx}: {e}")
            raise

        return self

    def add_rotation(
        self,
        gate_type: str,
        qubit_idx: int,
        angle: float,
        step_title: str = "Rotation Gate",
        description: str = "Apply a rotation gate",
    ) -> "InteractiveCircuitBuilder":
        """
        Add a rotation gate to the circuit.

        Args:
            gate_type: Type of rotation gate ('rx', 'ry', 'rz')
            qubit_idx: Index of the qubit to apply the gate to
            angle: Rotation angle in radians
            step_title: Title for this learning step
            description: Description of what this step does

        Returns:
            Self instance for method chaining

        Raises:
            ValueError: If gate type is unknown or qubit index is out of range
        """
        if not 0 <= qubit_idx < self.n_qubits:
            raise ValueError(f"Qubit index {qubit_idx} is out of range for circuit with {self.n_qubits} qubits")

        gate_type_lower = gate_type.lower()
        if gate_type_lower not in ["rx", "ry", "rz"]:
            raise ValueError(f"Unknown rotation gate type: {gate_type}. Use 'rx', 'ry', or 'rz'")

        try:
            if gate_type_lower == "rx":
                self.circuit.rx(angle, qubit_idx)
            elif gate_type_lower == "ry":
                self.circuit.ry(angle, qubit_idx)
            elif gate_type_lower == "rz":
                self.circuit.rz(angle, qubit_idx)

            step = LearningStep(
                step_number=self.current_step + 1,
                title=step_title,
                description=description,
                circuit=self.circuit.copy(),
            )
            self.history.append(step)
            self.current_step += 1
            logger.info(
                f"Added {gate_type_lower} rotation gate with angle {angle} to qubit {qubit_idx} in circuit '{self.title}'"
            )
        except Exception as e:
            logger.error(f"Failed to add {gate_type} rotation gate to qubit {qubit_idx}: {e}")
            raise

        return self

    def add_measurement(
        self,
        qubit_idx: int,
        classical_idx: int,
        step_title: str = "Measurement",
        description: str = "Measure the qubit",
    ) -> "InteractiveCircuitBuilder":
        """
        Add a measurement operation.

        Args:
            qubit_idx: Index of the qubit to measure
            classical_idx: Index of the classical bit to store the result
            step_title: Title for this learning step
            description: Description of what this step does

        Returns:
            Self instance for method chaining

        Raises:
            ValueError: If qubit or classical bit index is out of range
        """
        if not 0 <= qubit_idx < self.n_qubits:
            raise ValueError(f"Qubit index {qubit_idx} is out of range for circuit with {self.n_qubits} qubits")
        if not 0 <= classical_idx < self.n_qubits:  # Assuming classical bits match qubits for now
            raise ValueError(
                f"Classical bit index {classical_idx} is out of range for circuit with {self.n_qubits} bits"
            )

        try:
            self.circuit.measure(qubit_idx, classical_idx)
            step = LearningStep(
                step_number=self.current_step + 1,
                title=step_title,
                description=description,
                circuit=self.circuit.copy(),
            )
            self.history.append(step)
            self.current_step += 1
            logger.info(
                f"Added measurement from qubit {qubit_idx} to classical bit {classical_idx} in circuit '{self.title}'"
            )
        except Exception as e:
            logger.error(f"Failed to add measurement from qubit {qubit_idx} to classical bit {classical_idx}: {e}")
            raise

        return self

    def get_circuit(self) -> QuantumCircuit:
        """Get the final circuit."""
        return self.circuit

    def explain_step(self, step_idx: int) -> str:
        """
        Get explanation for a specific step.

        Args:
            step_idx: Index of the step to explain

        Returns:
            Explanation string for the step
        """
        if not 0 <= step_idx < len(self.history):
            error_msg = f"Step {step_idx} not found. Available steps: 0-{len(self.history)-1 if self.history else 0}"
            logger.warning(error_msg)
            return error_msg

        step = self.history[step_idx]
        explanation = f"Step {step.step_number}: {step.title}\n{step.description}"
        logger.info(f"Retrieved explanation for step {step_idx}")
        return explanation

    def simulate_step(self, step_idx: int, shots: int = 1000) -> dict[str, int]:
        """
        Simulate the circuit up to a specific step.

        Args:
            step_idx: Index of the step to simulate
            shots: Number of measurement shots

        Returns:
            Dictionary of measurement counts
        """
        if not 0 <= step_idx < len(self.history):
            error_msg = f"Step {step_idx} not found. Available steps: 0-{len(self.history)-1 if self.history else 0}"
            logger.warning(error_msg)
            return {}

        step_circuit = self.history[step_idx].circuit
        if step_circuit is None:
            logger.warning(f"Circuit for step {step_idx} is None")
            return {}

        try:
            # Add measurements if not already present
            has_measurements = any(inst.name == "measure" for inst, _, _ in step_circuit.data)
            if not has_measurements:
                temp_circuit = step_circuit.copy()
                temp_circuit.measure_all()
            else:
                temp_circuit = step_circuit

            result = simulate(temp_circuit, shots=shots)
            logger.info(f"Successfully simulated step {step_idx} with {shots} shots")
            return result.counts
        except Exception as e:
            logger.error(f"Failed to simulate step {step_idx}: {e}")
            return {}

    def visualize_step(self, step_idx: int) -> None:
        """
        Visualize a specific step of the circuit.

        Args:
            step_idx: Index of the step to visualize
        """
        if not 0 <= step_idx < len(self.history):
            error_msg = f"Step {step_idx} not found. Available steps: 0-{len(self.history)-1 if self.history else 0}"
            logger.warning(error_msg)
            print(error_msg)
            return

        step_data = self.history[step_idx]
        if step_data.circuit is None:
            logger.warning(f"Circuit for step {step_idx} is None")
            print(f"Step {step_idx} has no circuit to visualize")
            return

        try:
            print(f"Step {step_data.step_number}: {step_data.title}")
            print(f"Description: {step_data.description}")
            print("Circuit:")
            print(step_data.circuit.draw())
            logger.info(f"Visualized step {step_idx}")
        except Exception as e:
            logger.error(f"Failed to visualize step {step_idx}: {e}")
            print(f"Failed to visualize step {step_idx}: {e}")


class AlgorithmExplorer:
    """
    Interactive explorer for quantum algorithms.

    Provides an interface to explore different quantum algorithms with explanations.
    """

    def __init__(self) -> None:
        """Initialize the algorithm explorer."""
        self.available_algorithms = list_algorithms()

    def list_algorithms(self) -> list[str]:
        """Get list of available algorithms."""
        try:
            from .algorithms import list_algorithms as get_available_algorithms

            self.available_algorithms = get_available_algorithms()
            logger.info(f"Retrieved {len(self.available_algorithms)} available algorithms")
        except Exception as e:
            logger.error(f"Failed to retrieve algorithm list: {e}")
            self.available_algorithms = []

        return self.available_algorithms

    def get_algorithm_info(self, algorithm_name: str) -> dict[str, Any]:
        """
        Get detailed information about an algorithm.

        Args:
            algorithm_name: Name of the algorithm to get info for

        Returns:
            Dictionary with algorithm information

        Raises:
            ValueError: If algorithm is not available
            Exception: If there's an error creating the algorithm instance
        """
        if not self.available_algorithms:
            self.list_algorithms()  # Refresh the list

        if algorithm_name not in self.available_algorithms:
            available_str = ", ".join(self.available_algorithms[:10])  # Limit for readability
            extra_msg = "..." if len(self.available_algorithms) > 10 else ""
            raise ValueError(f"Algorithm {algorithm_name} not available. Available: {available_str}{extra_msg}")

        try:
            # Get the algorithm class
            algorithm_class = get_algorithm(algorithm_name)
            # Create a temporary instance to get metadata
            temp_instance = algorithm_class(AlgorithmParameters(n_qubits=2))  # Use default qubits

            info = {
                "name": algorithm_name,
                "metadata": temp_instance.metadata,
                "educational_content": temp_instance.get_educational_content(),
                "circuit_properties": temp_instance.analyze_circuit_properties(),
            }

            logger.info(f"Retrieved information for algorithm {algorithm_name}")
            return info
        except Exception as e:
            logger.error(f"Failed to get information for algorithm {algorithm_name}: {e}")
            raise

    def compare_algorithms(self, algorithm_names: list[str]) -> dict[str, Any]:
        """
        Compare multiple algorithms.

        Args:
            algorithm_names: List of algorithm names to compare

        Returns:
            Dictionary with comparison results
        """
        comparison = {}

        for name in algorithm_names:
            try:
                if name in self.available_algorithms or name in self.list_algorithms():
                    info = self.get_algorithm_info(name)
                    comparison[name] = {
                        "description": info["metadata"].description,
                        "complexity": info["metadata"].complexity,
                        "qubits": info["circuit_properties"]["n_qubits"],
                        "depth": info["circuit_properties"]["depth"],
                        "size": info["circuit_properties"]["size"],
                        "entanglement": info["circuit_properties"]["entanglement_heuristic"],
                    }
                else:
                    comparison[name] = {"error": f"Algorithm {name} not found"}
                    logger.warning(f"Algorithm {name} not found for comparison")
            except Exception as e:
                comparison[name] = {"error": f"Error comparing algorithm {name}: {str(e)}"}
                logger.error(f"Error comparing algorithm {name}: {e}")

        logger.info(f"Completed comparison for {len(algorithm_names)} algorithms")
        return comparison

    def create_learning_path(self, algorithm_name: str, n_qubits: int = 3) -> list[LearningStep]:
        """
        Create a step-by-step learning path for an algorithm.

        Args:
            algorithm_name: Name of the algorithm
            n_qubits: Number of qubits to use for the learning path

        Returns:
            List of learning steps

        Raises:
            ValueError: If algorithm is not available
            Exception: If there's an error creating the learning path
        """
        if not self.available_algorithms:
            self.list_algorithms()  # Refresh the list

        if algorithm_name not in self.available_algorithms:
            raise ValueError(f"Algorithm {algorithm_name} not available")

        try:
            # Get the algorithm class and create an instance
            algorithm_class = get_algorithm(algorithm_name)
            algorithm_instance = algorithm_class(AlgorithmParameters(n_qubits=n_qubits))

            # Create circuit
            circuit = algorithm_instance.create_circuit()

            # Create learning steps based on the algorithm
            steps = []

            # Step 1: Introduction
            steps.append(
                LearningStep(
                    step_number=1,
                    title=f"{algorithm_name.upper()} Algorithm Overview",
                    description=algorithm_instance.get_educational_content()["overview"],
                )
            )

            # Step 2: Circuit Structure
            props = algorithm_instance.analyze_circuit_properties()
            steps.append(
                LearningStep(
                    step_number=2,
                    title="Circuit Structure Analysis",
                    description=f"Qubits: {props['n_qubits']}, Depth: {props['depth']}, Gates: {props['size']}",
                    circuit=circuit,
                )
            )

            # Step 3: Simulation Results
            try:
                result = simulate(circuit, shots=1000)
                steps.append(
                    LearningStep(
                        step_number=3,
                        title="Simulation Results",
                        description=f"Backend used: {result.backend_used.value}, Time: {result.execution_time:.3f}s",
                        visualization_data={"counts": result.counts, "execution_time": result.execution_time},
                    )
                )
            except Exception as e:
                logger.error(f"Simulation failed for {algorithm_name}: {e}")
                steps.append(
                    LearningStep(
                        step_number=3, title="Simulation Failed", description=f"Error during simulation: {str(e)}"
                    )
                )

            logger.info(f"Created learning path for algorithm {algorithm_name} with {len(steps)} steps")
            return steps
        except Exception as e:
            logger.error(f"Failed to create learning path for algorithm {algorithm_name}: {e}")
            raise


class QuantumConceptExplorer:
    """
    Interactive explorer for fundamental quantum computing concepts.
    """

    def __init__(self) -> None:
        """Initialize the concept explorer."""
        self.concepts = {
            "superposition": self._explore_superposition,
            "entanglement": self._explore_entanglement,
            "interference": self._explore_interference,
            "amplitude_amplification": self._explore_amplitude_amplification,
        }

    def _explore_superposition(self) -> InteractiveCircuitBuilder:
        """Create an interactive circuit to explore superposition."""
        builder = InteractiveCircuitBuilder(1, "Superposition Explorer")
        builder.add_hadamard(
            0, "Create Superposition", "Apply H gate to qubit 0 to create an equal superposition of |0⟩ and |1⟩"
        )
        return builder

    def _explore_entanglement(self) -> InteractiveCircuitBuilder:
        """Create an interactive circuit to explore entanglement."""
        builder = InteractiveCircuitBuilder(2, "Entanglement Explorer")
        builder.add_hadamard(0, "Create Superposition", "Apply H gate to qubit 0 to create superposition")
        builder.add_cnot(
            0, 1, "Create Entanglement", "Apply CNOT with qubit 0 as control and qubit 1 as target to entangle them"
        )
        return builder

    def _explore_interference(self) -> InteractiveCircuitBuilder:
        """Create an interactive circuit to explore interference."""
        builder = InteractiveCircuitBuilder(1, "Interference Explorer")
        builder.add_hadamard(0, "First Superposition", "Apply H gate to create initial superposition")
        builder.add_rotation("rz", 0, np.pi / 4, "Phase Shift", "Apply Rz gate with π/4 phase shift")
        builder.add_hadamard(0, "Second Superposition", "Apply second H gate to create interference pattern")
        return builder

    def _explore_amplitude_amplification(self) -> InteractiveCircuitBuilder:
        """Create an interactive circuit to explore amplitude amplification."""
        builder = InteractiveCircuitBuilder(2, "Amplitude Amplification Explorer")
        # This is a simplified version - real amplitude amplification requires more complex circuits
        builder.add_hadamard(0, "Prepare Superposition", "Apply H gate to qubit 0")
        builder.add_hadamard(1, "Prepare Superposition", "Apply H gate to qubit 1")
        return builder

    def explore_concept(self, concept_name: str) -> InteractiveCircuitBuilder:
        """
        Explore a specific quantum concept.

        Args:
            concept_name: Name of the concept to explore

        Returns:
            InteractiveCircuitBuilder configured for the concept

        Raises:
            ValueError: If the concept is not available
            Exception: If there's an error creating the concept exploration
        """
        concept_name = concept_name.lower().replace(" ", "_")
        if concept_name not in self.concepts:
            available_str = ", ".join(self.concepts.keys())
            raise ValueError(f"Concept {concept_name} not available. Available: {available_str}")

        try:
            builder = self.concepts[concept_name]()
            logger.info(f"Created exploration for quantum concept: {concept_name}")
            return builder
        except Exception as e:
            logger.error(f"Failed to create exploration for concept {concept_name}: {e}")
            raise


class EducationDashboard:
    """
    Comprehensive dashboard for quantum education with various tools.
    """

    def __init__(self) -> None:
        """Initialize the education dashboard."""
        self.algorithm_explorer = AlgorithmExplorer()
        self.concept_explorer = QuantumConceptExplorer()

    def show_algorithm_list(self) -> None:
        """Display all available algorithms in a formatted way."""
        algorithms = self.algorithm_explorer.list_algorithms()

        html = "<h2>Available Quantum Algorithms</h2>\n<ul>\n"
        for alg in algorithms:
            html += f"  <li><strong>{alg.upper()}</strong></li>\n"
        html += "</ul>\n"

        display(HTML(html))

    def compare_algorithms_interactive(self, algorithm_names: list[str]) -> None:
        """Create an interactive comparison of algorithms."""
        comparison = self.algorithm_explorer.compare_algorithms(algorithm_names)

        html = "<h2>Algorithm Comparison</h2>\n<table border='1'>\n"
        html += "<tr><th>Algorithm</th><th>Qubits</th><th>Depth</th><th>Size</th><th>Entanglement</th></tr>\n"

        for name, data in comparison.items():
            if "error" not in data:
                html += f"<tr><td>{name}</td><td>{data['qubits']}</td><td>{data['depth']}</td><td>{data['size']}</td><td>{data['entanglement']:.2f}</td></tr>\n"
            else:
                html += f"<tr><td>{name}</td><td colspan='4'>{data['error']}</td></tr>\n"

        html += "</table>\n"
        display(HTML(html))

    def run_learning_path(self, algorithm_name: str, n_qubits: int = 3) -> None:
        """Run a step-by-step learning path for an algorithm."""
        steps = self.algorithm_explorer.create_learning_path(algorithm_name, n_qubits)

        for step in steps:
            print(f"\n--- Step {step.step_number}: {step.title} ---")
            print(step.description)
            if step.circuit:
                print("\nCircuit:")
                print(step.circuit.draw())
            if step.visualization_data:
                if "counts" in step.visualization_data:
                    print(f"\nResults: {dict(list(step.visualization_data['counts'].items())[:5])}")
                    if len(step.visualization_data["counts"]) > 5:
                        print(f"  ... and {len(step.visualization_data['counts']) - 5} more")
            print("-" * 50)


# Convenience functions for interactive use
def get_interactive_builder(n_qubits: int, algorithm_name: str = "custom") -> InteractiveCircuitBuilder:
    """
    Get an interactive circuit builder pre-configured for learning.

    Args:
        n_qubits: Number of qubits for the circuit
        algorithm_name: Name for the algorithm/circuit (for labeling)

    Returns:
        InteractiveCircuitBuilder instance
    """
    return InteractiveCircuitBuilder(n_qubits, algorithm_name)


def explore_quantum_concept(concept_name: str) -> InteractiveCircuitBuilder:
    """
    Get an interactive circuit for exploring a quantum concept.

    Args:
        concept_name: Name of the concept to explore

    Returns:
        InteractiveCircuitBuilder instance
    """
    explorer = QuantumConceptExplorer()
    return explorer.explore_concept(concept_name)


def run_algorithm_exploration(algorithm_name: str, n_qubits: int = 3) -> None:
    """
    Run an interactive exploration of a quantum algorithm.

    Args:
        algorithm_name: Name of the algorithm to explore
        n_qubits: Number of qubits to use for the exploration
    """
    dashboard = EducationDashboard()
    dashboard.run_learning_path(algorithm_name, n_qubits)


def compare_algorithms(algorithm_names: list[str]) -> None:
    """
    Compare properties of multiple algorithms.

    Args:
        algorithm_names: List of algorithm names to compare
    """
    dashboard = EducationDashboard()
    dashboard.compare_algorithms_interactive(algorithm_names)


if __name__ == "__main__":
    # Demo usage
    print("Ariadne Educational Devices Demo")
    print("=" * 40)

    # Create an interactive circuit builder
    builder = InteractiveCircuitBuilder(2, "Bell State")
    builder.add_hadamard(0, "Hadamard", "Create superposition on qubit 0")
    builder.add_cnot(0, 1, "CNOT", "Entangle qubits 0 and 1")
    builder.add_measurement(0, 0, "Measure", "Measure qubit 0")
    builder.add_measurement(1, 1, "Measure", "Measure qubit 1")

    print("Bell State Circuit:")
    print(builder.get_circuit().draw())

    # Explore algorithms
    explorer = AlgorithmExplorer()
    print(f"\nAvailable algorithms: {explorer.list_algorithms()}")

    # Explore a concept
    concept_builder = explore_quantum_concept("entanglement")
    print("\nEntanglement exploration circuit:")
    print(concept_builder.get_circuit().draw())
