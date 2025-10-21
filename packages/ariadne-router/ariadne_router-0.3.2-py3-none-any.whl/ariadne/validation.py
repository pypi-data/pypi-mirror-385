"""
Validation and Error Handling Utilities for Ariadne.

This module provides comprehensive validation and error handling utilities
for the Ariadne quantum simulation framework.
"""

import warnings
from functools import wraps
from typing import Any

from qiskit import QuantumCircuit
from qiskit.exceptions import QiskitError

from ariadne.core import AriadneError, BackendUnavailableError, CircuitTooLargeError
from ariadne.types import BackendType


def validate_qubit_index(qubit_idx: int, max_qubits: int) -> None:
    """
    Validate that a qubit index is within the valid range.

    Args:
        qubit_idx: The qubit index to validate
        max_qubits: Maximum number of qubits allowed

    Raises:
        ValueError: If qubit index is out of range
    """
    if not 0 <= qubit_idx < max_qubits:
        raise ValueError(f"Qubit index {qubit_idx} is out of range [0, {max_qubits-1}]")


def validate_qubit_indices(control_idx: int, target_idx: int, max_qubits: int) -> None:
    """
    Validate that both control and target qubit indices are within the valid range and not equal.

    Args:
        control_idx: The control qubit index to validate
        target_idx: The target qubit index to validate
        max_qubits: Maximum number of qubits allowed

    Raises:
        ValueError: If qubit indices are out of range or if control equals target
    """
    validate_qubit_index(control_idx, max_qubits)
    validate_qubit_index(target_idx, max_qubits)

    if control_idx == target_idx:
        raise ValueError(f"Control and target qubits cannot be the same: {control_idx}")


def validate_shots(shots: int) -> None:
    """
    Validate that the number of shots is valid.

    Args:
        shots: Number of measurement shots

    Raises:
        ValueError: If shots is not a positive integer
    """
    if not isinstance(shots, int) or shots <= 0:
        raise ValueError(f"Number of shots must be a positive integer, got {shots}")


def validate_backend(backend: str | None) -> None:
    """
    Validate that the backend name is valid if provided.

    Args:
        backend: Backend name to validate (can be None for auto-routing)

    Raises:
        ValueError: If backend name is invalid
    """
    if backend is None:
        return  # None is valid for auto-routing

    try:
        BackendType(backend.lower())
    except ValueError:
        valid_backends = [bt.value for bt in BackendType]
        raise ValueError(f"Invalid backend '{backend}'. Valid options: {valid_backends}") from None


def validate_circuit(circuit: QuantumCircuit) -> None:
    """
    Validate that a quantum circuit is valid for simulation.

    Args:
        circuit: The quantum circuit to validate

    Raises:
        ValueError: If circuit is invalid
        CircuitTooLargeError: If circuit is too large for practical simulation
    """
    if circuit is None:
        raise ValueError("Circuit cannot be None")

    if circuit.num_qubits <= 0:
        raise ValueError(f"Circuit must have at least 1 qubit, got {circuit.num_qubits}")

    if circuit.num_qubits > 64:  # Reasonable limit for classical simulation
        raise CircuitTooLargeError(num_qubits=circuit.num_qubits, depth=circuit.depth(), backend=None)

    try:
        # Try basic operations to ensure circuit is valid
        circuit.size()  # This will raise an error if circuit is malformed
    except Exception as e:
        raise ValueError(f"Circuit validation failed: {e}") from e


def safe_execute(func):
    """
    Decorator to safely execute a function with comprehensive error handling.

    Args:
        func: The function to wrap

    Returns:
        A wrapped function with error handling
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CircuitTooLargeError:
            # Re-raise specific errors
            raise
        except BackendUnavailableError:
            # Re-raise specific errors
            raise
        except ValueError as e:
            # Log value errors but re-raise them
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Value error in {func.__name__}: {e}")
            raise
        except QiskitError as e:
            # Handle Qiskit-specific errors
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Qiskit error in {func.__name__}: {e}")
            raise AriadneError(f"Qiskit error: {e}") from e
        except Exception as e:
            # Handle unexpected errors
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise AriadneError(f"Unexpected error: {e}") from e

    return wrapper


def deprecation_warning(message: str, stacklevel: int = 3) -> None:
    """
    Issue a deprecation warning.

    Args:
        message: The deprecation warning message
        stacklevel: Stack level for the warning
    """
    warnings.warn(message, DeprecationWarning, stacklevel=stacklevel)


def validate_algorithm_parameters(algorithm_name: str, params: dict[str, Any]) -> None:
    """
    Validate parameters for a specific quantum algorithm.

    Args:
        algorithm_name: Name of the algorithm
        params: Parameters for the algorithm

    Raises:
        ValueError: If parameters are invalid for the algorithm
    """
    if not isinstance(params, dict):
        raise ValueError("Algorithm parameters must be a dictionary")

    n_qubits = params.get("n_qubits", 1)
    if not isinstance(n_qubits, int) or n_qubits <= 0:
        raise ValueError(f"Number of qubits must be a positive integer, got {n_qubits}")

    # Algorithm-specific validations
    if algorithm_name == "qft" and n_qubits > 20:
        deprecation_warning(
            f"QFT with {n_qubits} qubits may be computationally expensive. "
            f"Consider limiting to 20 qubits for reasonable simulation times."
        )
    elif algorithm_name == "grover" and n_qubits > 10:
        deprecation_warning(
            f"Grover's algorithm with {n_qubits} qubits requires 2^{n_qubits} operations "
            f"which may be computationally expensive."
        )


def validate_measurement_indices(
    qubit_indices: list[int], classical_indices: list[int], max_qubits: int, max_classical_bits: int
) -> None:
    """
    Validate qubit and classical bit indices for measurement operations.

    Args:
        qubit_indices: List of qubit indices to measure
        classical_indices: List of classical bit indices to store results
        max_qubits: Maximum number of qubits in the circuit
        max_classical_bits: Maximum number of classical bits in the circuit

    Raises:
        ValueError: If indices are invalid
    """
    if len(qubit_indices) != len(classical_indices):
        raise ValueError(f"Mismatched lengths: {len(qubit_indices)} qubits, {len(classical_indices)} classical bits")

    for q_idx in qubit_indices:
        validate_qubit_index(q_idx, max_qubits)

    for c_idx in classical_indices:
        if not 0 <= c_idx < max_classical_bits:
            raise ValueError(f"Classical bit index {c_idx} is out of range [0, {max_classical_bits-1}]")


def check_simulation_requirements(circuit: QuantumCircuit, backend: str | None = None) -> dict[str, Any]:
    """
    Check if the circuit meets simulation requirements for the specified backend.

    Args:
        circuit: The circuit to check
        backend: The backend to check requirements for (can be None for auto)

    Returns:
        Dictionary with validation results
    """
    results = {"valid": True, "warnings": [], "errors": [], "recommended_backend": backend or "auto"}

    # Validate basic circuit properties
    try:
        validate_circuit(circuit)
    except CircuitTooLargeError as e:
        results["errors"].append(str(e))
        results["valid"] = False
    except ValueError as e:
        results["errors"].append(str(e))
        results["valid"] = False

    # Add warnings for potentially problematic configurations
    if circuit.num_qubits > 20 and backend not in ["stim", "mps", "tensor_network"]:
        results["warnings"].append(
            f"Circuit with {circuit.num_qubits} qubits might benefit from specialized backends "
            f"like 'stim' (for Clifford circuits), 'mps', or 'tensor_network'."
        )

    if circuit.depth() > 100:
        results["warnings"].append(f"Circuit has depth {circuit.depth()}, which may result in longer simulation times.")

    # Check for specific backend requirements if specified
    if backend == "stim" and circuit.num_qubits > 50:
        results["warnings"].append(
            "Stim backend works well for large Clifford circuits, "
            "but non-Clifford gates will cause fallback to other backends."
        )

    return results


class CircuitValidator:
    """
    A class for comprehensive circuit validation with multiple check methods.
    """

    def __init__(self):
        self.checks = []

    def add_check(self, check_func, description: str):
        """
        Add a validation check function.

        Args:
            check_func: Function that takes a circuit and returns (is_valid, message)
            description: Description of what the check validates
        """
        self.checks.append((check_func, description))

    def validate(self, circuit: QuantumCircuit) -> dict[str, Any]:
        """
        Run all validation checks on a circuit.

        Args:
            circuit: Circuit to validate

        Returns:
            Dictionary with validation results
        """
        results = {"valid": True, "passed_checks": [], "failed_checks": [], "warnings": []}

        for check_func, description in self.checks:
            try:
                is_valid, message = check_func(circuit)
                if is_valid:
                    results["passed_checks"].append((description, message))
                else:
                    results["failed_checks"].append((description, message))
                    results["valid"] = False
            except Exception as e:
                results["failed_checks"].append((description, f"Check failed with error: {e}"))
                results["valid"] = False

        return results


def create_default_validator() -> CircuitValidator:
    """
    Create a validator with default checks.

    Returns:
        CircuitValidator with default checks
    """
    validator = CircuitValidator()

    def check_qubit_count(circuit: QuantumCircuit):
        if circuit.num_qubits <= 0:
            return False, "Circuit must have at least 1 qubit"
        if circuit.num_qubits > 64:
            return False, f"Circuit with {circuit.num_qubits} qubits may be too large"
        return True, f"Circuit has {circuit.num_qubits} qubits"

    def check_depth(circuit: QuantumCircuit):
        depth = circuit.depth()
        if depth > 10000:
            return True, f"Circuit has high depth ({depth}), simulation may be slow"
        if depth <= 0:
            return False, "Circuit has no gates"
        return True, f"Circuit has depth {depth}"

    def check_measurements(circuit: QuantumCircuit):
        measure_count = sum(1 for inst, _, _ in circuit.data if inst.name == "measure")
        if measure_count == 0:
            return True, "No measurements found (this is valid for some algorithms)"
        return True, f"Circuit has {measure_count} measurement operations"

    validator.add_check(check_qubit_count, "Qubit count validation")
    validator.add_check(check_depth, "Circuit depth validation")
    validator.add_check(check_measurements, "Measurement validation")

    return validator


# Validation utilities for backward compatibility
def validate_circuit_for_simulation(circuit: QuantumCircuit, backend: str | None = None):
    """
    Validate a circuit for simulation (backward compatibility function).

    Args:
        circuit: Circuit to validate
        backend: Target backend (optional)

    Returns:
        True if valid, raises exception if invalid
    """
    import logging

    logger = logging.getLogger(__name__)

    # Perform basic validation
    validate_circuit(circuit)

    # Check simulation requirements
    requirements = check_simulation_requirements(circuit, backend)

    # Log warnings
    for warning in requirements["warnings"]:
        logger.warning(warning)

    # Error if invalid
    if not requirements["valid"]:
        errors = "; ".join(requirements["errors"])
        raise ValueError(f"Invalid circuit for simulation: {errors}")

    return True


if __name__ == "__main__":
    # Demo usage
    print("Ariadne Validation Utilities Demo")
    print("=" * 40)

    # Create a simple circuit for testing
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()

    # Validate the circuit
    validator = create_default_validator()
    results = validator.validate(qc)

    print(f"Validation results: {results}")

    # Check simulation requirements
    req_results = check_simulation_requirements(qc)
    print(f"Requirements check: {req_results}")

    print("Validation demo completed successfully!")
