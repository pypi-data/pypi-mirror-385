"""
Test module for validation utilities.
"""

import pytest
from qiskit import QuantumCircuit

from ariadne.core import CircuitTooLargeError
from ariadne.validation import (
    CircuitValidator,
    check_simulation_requirements,
    create_default_validator,
    validate_algorithm_parameters,
    validate_backend,
    validate_circuit,
    validate_measurement_indices,
    validate_qubit_index,
    validate_qubit_indices,
    validate_shots,
)


def test_validate_qubit_index():
    """Test qubit index validation."""
    # Valid indices
    validate_qubit_index(0, 5)  # Should not raise
    validate_qubit_index(4, 5)  # Should not raise

    # Invalid indices should raise ValueError
    with pytest.raises(ValueError):
        validate_qubit_index(-1, 5)

    with pytest.raises(ValueError):
        validate_qubit_index(5, 5)


def test_validate_qubit_indices():
    """Test qubit pair validation."""
    # Valid indices
    validate_qubit_indices(0, 1, 5)  # Should not raise

    # Invalid indices should raise ValueError
    with pytest.raises(ValueError):
        validate_qubit_indices(-1, 1, 5)  # Negative control

    with pytest.raises(ValueError):
        validate_qubit_indices(0, 5, 5)  # Invalid target

    with pytest.raises(ValueError):
        validate_qubit_indices(1, 1, 5)  # Same indices


def test_validate_shots():
    """Test shots validation."""
    # Valid shots
    validate_shots(1)  # Should not raise
    validate_shots(100)  # Should not raise

    # Invalid shots should raise ValueError
    with pytest.raises(ValueError):
        validate_shots(0)

    with pytest.raises(ValueError):
        validate_shots(-1)

    with pytest.raises(ValueError):
        validate_shots(1.5)


def test_validate_backend():
    """Test backend validation."""
    # Valid backends
    validate_backend(None)  # Should not raise (auto-routing)
    validate_backend("qiskit")  # Should not raise
    validate_backend("QISKIT")  # Should not raise (case-insensitive)

    # Invalid backend should raise ValueError
    with pytest.raises(ValueError):
        validate_backend("invalid_backend")


def test_validate_circuit():
    """Test circuit validation."""
    # Valid circuit
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    validate_circuit(qc)  # Should not raise

    # Invalid circuits
    with pytest.raises(ValueError):
        validate_circuit(None)

    # Circuit with no qubits
    empty_qc = QuantumCircuit(0)
    with pytest.raises(ValueError):
        validate_circuit(empty_qc)

    # Very large circuit (should trigger CircuitTooLargeError)
    large_qc = QuantumCircuit(65, 65)  # More than 64 qubits
    with pytest.raises(CircuitTooLargeError):
        validate_circuit(large_qc)


def test_validate_algorithm_parameters():
    """Test algorithm parameter validation."""
    # Valid parameters
    validate_algorithm_parameters("bell", {"n_qubits": 2})

    # Invalid parameters
    with pytest.raises(ValueError):
        validate_algorithm_parameters("bell", {"n_qubits": 0})  # Invalid qubits

    with pytest.raises(ValueError):
        validate_algorithm_parameters("bell", "invalid_params_type")  # Wrong type


def test_validate_measurement_indices():
    """Test measurement index validation."""
    # Valid indices
    validate_measurement_indices([0, 1], [0, 1], 5, 5)  # Should not raise

    # Invalid indices
    with pytest.raises(ValueError):
        validate_measurement_indices([0], [0, 1], 5, 5)  # Mismatched lengths

    with pytest.raises(ValueError):
        validate_measurement_indices([5], [0], 5, 5)  # Invalid qubit index

    with pytest.raises(ValueError):
        validate_measurement_indices([0], [5], 5, 5)  # Invalid classical index


def test_check_simulation_requirements():
    """Test simulation requirements checking."""
    # Valid circuit
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()

    results = check_simulation_requirements(qc)
    assert results["valid"] is True
    assert len(results["errors"]) == 0

    # Large circuit should have warnings but still be valid
    large_qc = QuantumCircuit(25, 25)
    results = check_simulation_requirements(large_qc)
    assert results["valid"] is True  # Still valid, just with warnings
    assert len(results["warnings"]) > 0


def test_circuit_validator():
    """Test the CircuitValidator class."""
    validator = CircuitValidator()

    # Add a simple check
    def check_depth(circuit):
        if circuit.depth() > 100:
            return False, "Circuit is too deep"
        return True, "Depth is acceptable"

    validator.add_check(check_depth, "Depth check")

    # Valid circuit
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)

    results = validator.validate(qc)
    assert results["valid"] is True
    assert len(results["failed_checks"]) == 0
    assert len(results["passed_checks"]) == 1


def test_default_validator():
    """Test the default validator."""
    validator = create_default_validator()

    # Valid circuit
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()

    results = validator.validate(qc)
    assert results["valid"] is True
    assert len(results["failed_checks"]) == 0
    assert len(results["passed_checks"]) >= 1


if __name__ == "__main__":
    # Run the tests
    test_validate_qubit_index()
    print("✓ validate_qubit_index test passed")

    test_validate_qubit_indices()
    print("✓ validate_qubit_indices test passed")

    test_validate_shots()
    print("✓ validate_shots test passed")

    test_validate_backend()
    print("✓ validate_backend test passed")

    test_validate_circuit()
    print("✓ validate_circuit test passed")

    test_validate_algorithm_parameters()
    print("✓ validate_algorithm_parameters test passed")

    test_validate_measurement_indices()
    print("✓ validate_measurement_indices test passed")

    test_check_simulation_requirements()
    print("✓ check_simulation_requirements test passed")

    test_circuit_validator()
    print("✓ CircuitValidator test passed")

    test_default_validator()
    print("✓ Default validator test passed")

    print("\nAll validation tests passed!")
