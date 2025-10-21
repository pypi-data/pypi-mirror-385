"""
Ariadne Quantum Algorithms Module

This module provides a comprehensive collection of quantum algorithms
with standardized interfaces for circuit generation, parameterization,
and educational content.

Available algorithm categories:
- Foundational: Bell states, GHZ, QFT
- Search: Grover, Bernstein-Vazirani
- Optimization: QAOA, VQE
- Error Correction: Steane code, Surface code
- Machine Learning: QSVM, VQC
- Chemistry: UCCSD, VQE for chemistry
- Specialized: Deutsch-Jozsa, Simon's
"""

from .base import AlgorithmParameters, AlgorithmRegistry, QuantumAlgorithm, algorithm
from .error_correction import SteaneCode
from .foundational import BellState, GHZState, QuantumFourierTransform
from .machine_learning import QSVM
from .optimization import QAOA, VQE
from .search import BernsteinVazirani, GroverSearch
from .specialized import DeutschJozsa, SimonsAlgorithm

__all__ = [
    # Base classes
    "QuantumAlgorithm",
    "AlgorithmRegistry",
    "AlgorithmParameters",
    "algorithm",
    # Foundational algorithms
    "BellState",
    "GHZState",
    "QuantumFourierTransform",
    # Search algorithms
    "GroverSearch",
    "BernsteinVazirani",
    # Optimization algorithms
    "QAOA",
    "VQE",
    # Error correction
    "SteaneCode",
    # Machine learning
    "QSVM",
    # Specialized algorithms
    "DeutschJozsa",
    "SimonsAlgorithm",
    # Utility functions
    "get_algorithm",
    "list_algorithms",
    "get_algorithms_by_category",
]

# Initialize algorithm registry
_registry = AlgorithmRegistry()


# Register all algorithms
def _register_algorithms() -> None:
    """Register all available algorithms in the registry."""
    # Foundational
    _registry.register("bell", BellState)
    _registry.register("ghz", GHZState)
    _registry.register("qft", QuantumFourierTransform)

    # Search
    _registry.register("grover", GroverSearch)
    _registry.register("bernstein_vazirani", BernsteinVazirani)

    # Optimization
    _registry.register("qaoa", QAOA)
    _registry.register("vqe", VQE)

    # Error correction
    _registry.register("steane", SteaneCode)

    # Machine learning
    _registry.register("qsvm", QSVM)

    # Specialized
    _registry.register("deutsch_jozsa", DeutschJozsa)
    _registry.register("simon", SimonsAlgorithm)


# Register algorithms on import
_register_algorithms()


def get_algorithm(name: str) -> type[QuantumAlgorithm]:
    """Get an algorithm class by name."""
    return _registry.get(name)


def list_algorithms() -> list[str]:
    """List all available algorithm names."""
    return _registry.list_algorithms()


def get_algorithms_by_category(category: str) -> list[str]:
    """Get all algorithms in a specific category."""
    return _registry.get_by_category(category)
