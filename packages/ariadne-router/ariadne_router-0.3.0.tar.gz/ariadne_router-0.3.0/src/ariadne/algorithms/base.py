"""
Base classes and interfaces for quantum algorithms in Ariadne.

This module defines the standardized interface that all quantum algorithms
must implement, ensuring consistency across the framework.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from qiskit import QuantumCircuit


@dataclass
class AlgorithmMetadata:
    """Metadata for a quantum algorithm."""

    name: str
    description: str
    category: str
    tags: list[str] = field(default_factory=list)
    min_qubits: int = 1
    max_qubits: int | None = None
    complexity: str = "medium"  # low, medium, high, very_high
    classical_complexity: str | None = None
    quantum_advantage: bool = False
    educational_value: str = "medium"  # low, medium, high
    use_cases: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)


@dataclass
class AlgorithmParameters:
    """Parameters for algorithm instantiation."""

    n_qubits: int
    depth: int | None = None
    shots: int = 1000
    seed: int | None = None
    custom_params: dict[str, Any] = field(default_factory=dict)


class QuantumAlgorithm(ABC):
    """
    Abstract base class for all quantum algorithms in Ariadne.

    This class defines the standardized interface that all algorithms must
    implement, ensuring consistency in circuit generation, parameterization,
    and educational content.
    """

    def __init__(self, params: AlgorithmParameters):
        """Initialize the algorithm with parameters."""
        self.params = params
        self._validate_parameters()

    @property
    @abstractmethod
    def metadata(self) -> AlgorithmMetadata:
        """Return algorithm metadata."""
        pass

    @abstractmethod
    def create_circuit(self) -> QuantumCircuit:
        """
        Create and return the quantum circuit for this algorithm.

        Returns:
            QuantumCircuit: The algorithm's quantum circuit
        """
        pass

    def _validate_parameters(self) -> None:
        """Validate algorithm parameters."""
        meta = self.metadata

        if self.params.n_qubits < meta.min_qubits:
            raise ValueError(f"{meta.name} requires at least {meta.min_qubits} qubits, got {self.params.n_qubits}")

        if meta.max_qubits and self.params.n_qubits > meta.max_qubits:
            raise ValueError(f"{meta.name} supports at most {meta.max_qubits} qubits, got {self.params.n_qubits}")

    def get_educational_content(self) -> dict[str, str]:
        """
        Get educational content about this algorithm.

        Returns:
            Dict containing educational information
        """
        return {
            "overview": self._get_overview(),
            "mathematical_background": self._get_mathematical_background(),
            "applications": self._get_applications(),
            "implementation_notes": self._get_implementation_notes(),
        }

    def _get_overview(self) -> str:
        """Get overview of the algorithm."""
        return self.metadata.description

    def _get_mathematical_background(self) -> str:
        """Get mathematical background. Override in subclasses."""
        return "Mathematical background not yet documented."

    def _get_applications(self) -> str:
        """Get applications of the algorithm. Override in subclasses."""
        if self.metadata.use_cases:
            return "Applications: " + ", ".join(self.metadata.use_cases)
        return "Applications not yet documented."

    def _get_implementation_notes(self) -> str:
        """Get implementation notes. Override in subclasses."""
        return "Implementation notes not yet documented."

    def analyze_circuit_properties(self) -> dict[str, Any]:
        """
        Analyze the properties of the generated circuit.

        Returns:
            Dictionary with circuit analysis
        """
        circuit = self.create_circuit()

        # Count gates by type
        gate_counts: dict[str, int] = {}
        for instruction, _, _ in circuit.data:
            gate_name = instruction.name
            gate_counts[gate_name] = gate_counts.get(gate_name, 0) + 1

        # Calculate entanglement heuristic
        two_qubit_gates = sum(count for gate, count in gate_counts.items() if gate in ["cx", "cz", "swap", "ch"])

        return {
            "n_qubits": circuit.num_qubits,
            "depth": circuit.depth(),
            "gate_counts": gate_counts,
            "two_qubit_gates": two_qubit_gates,
            "size": circuit.size(),
            "entanglement_heuristic": two_qubit_gates / circuit.num_qubits if circuit.num_qubits > 0 else 0,
        }


class AlgorithmRegistry:
    """Registry for quantum algorithms."""

    def __init__(self) -> None:
        """Initialize the algorithm registry."""
        self._algorithms: dict[str, type[QuantumAlgorithm]] = {}
        self._categories: dict[str, list[str]] = {}

    def register(self, name: str, algorithm_class: type[QuantumAlgorithm]) -> None:
        """
        Register an algorithm class.

        Args:
            name: Algorithm name
            algorithm_class: Algorithm class
        """
        self._algorithms[name] = algorithm_class

        # Update category mapping - use appropriate qubits for this algorithm
        # Try common qubit counts, starting with the algorithm's minimum
        for n_qubits in [2, 3, 4, 1]:  # Most common configurations
            try:
                temp_instance = algorithm_class(AlgorithmParameters(n_qubits=n_qubits))
                category = temp_instance.metadata.category
                if category not in self._categories:
                    self._categories[category] = []
                self._categories[category].append(name)
                break
            except ValueError:
                continue
        else:
            # If all fail, just add to 'unknown' category
            if "unknown" not in self._categories:
                self._categories["unknown"] = []
            self._categories["unknown"].append(name)

    def get(self, name: str) -> type[QuantumAlgorithm]:
        """
        Get an algorithm class by name.

        Args:
            name: Algorithm name

        Returns:
            Algorithm class

        Raises:
            KeyError: If algorithm not found
        """
        if name not in self._algorithms:
            raise KeyError(f"Algorithm '{name}' not found. Available: {list(self._algorithms.keys())}")
        return self._algorithms[name]

    def list_algorithms(self) -> list[str]:
        """List all available algorithm names."""
        return list(self._algorithms.keys())

    def get_by_category(self, category: str) -> list[str]:
        """
        Get all algorithms in a specific category.

        Args:
            category: Category name

        Returns:
            List of algorithm names in the category
        """
        return self._categories.get(category, [])

    def list_categories(self) -> list[str]:
        """List all available categories."""
        return list(self._categories.keys())


# Global registry instance
_registry = AlgorithmRegistry()


def algorithm(name: str) -> Callable:
    """
    Decorator to register an algorithm.

    Args:
        name: Algorithm name

    Returns:
        Decorator function
    """

    def decorator(algorithm_class: type[QuantumAlgorithm]) -> type[QuantumAlgorithm]:
        _registry.register(name, algorithm_class)
        return algorithm_class

    return decorator


def get_algorithm(name: str) -> type[QuantumAlgorithm]:
    """Get an algorithm class by name."""
    return _registry.get(name)


def list_algorithms() -> list[str]:
    """List all available algorithm names."""
    return _registry.list_algorithms()


def get_algorithms_by_category(category: str) -> list[str]:
    """Get all algorithms in a specific category."""
    return _registry.get_by_category(category)


def list_categories() -> list[str]:
    """List all available categories."""
    return _registry.list_categories()
