"""Test suite for core stability improvements."""

import pytest
from qiskit import QuantumCircuit

from ariadne import simulate
from ariadne.core import (
    AriadneError,
    BackendUnavailableError,
    CircuitAnalysisCache,
    CircuitTooLargeError,
    ResourceExhaustionError,
    SimulationError,
    check_circuit_feasibility,
    get_logger,
    get_resource_manager,
)


class TestErrorHandling:
    """Test the new error handling system."""

    def test_error_hierarchy(self) -> None:
        """Test that error hierarchy is properly structured."""
        assert issubclass(BackendUnavailableError, AriadneError)
        assert issubclass(CircuitTooLargeError, AriadneError)
        assert issubclass(ResourceExhaustionError, AriadneError)
        assert issubclass(SimulationError, AriadneError)

    def test_error_details(self) -> None:
        """Test error details are properly stored."""
        error = BackendUnavailableError("stim", "Not installed", {"version": "1.0"})
        assert error.backend_name == "stim"
        assert error.reason == "Not installed"
        assert error.details["version"] == "1.0"

    def test_error_string_representation(self) -> None:
        """Test error string representation."""
        error = CircuitTooLargeError(30, 100, "stim")
        error_str = str(error)
        assert "30 qubits" in error_str
        assert "depth 100" in error_str
        assert "stim" in error_str


class TestCircuitAnalysisCache:
    """Test the circuit analysis caching system."""

    def test_cache_basic_operations(self) -> None:
        """Test basic cache operations."""
        cache = CircuitAnalysisCache(max_size=10)

        # Create test circuit
        circuit = QuantumCircuit(2)
        circuit.h(0)
        circuit.cx(0, 1)

        # Test storing and retrieving analysis
        analysis = {"num_qubits": 2, "depth": 2, "is_clifford": True}
        cache.store_analysis(circuit, analysis)

        retrieved = cache.get_analysis(circuit)
        assert retrieved == analysis

    def test_cache_miss(self) -> None:
        """Test cache miss behavior."""
        cache = CircuitAnalysisCache()

        circuit = QuantumCircuit(2)
        circuit.h(0)

        # Should return None for non-existent entry
        result = cache.get_analysis(circuit)
        assert result is None

    def test_cache_stats(self) -> None:
        """Test cache statistics."""
        cache = CircuitAnalysisCache()

        circuit = QuantumCircuit(2)
        circuit.h(0)
        analysis = {"num_qubits": 2}

        # Store and retrieve to generate stats
        cache.store_analysis(circuit, analysis)
        cache.get_analysis(circuit)  # Hit
        cache.get_analysis(QuantumCircuit(1))  # Miss

        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["size"] == 1

    def test_circuit_hash_determinism(self) -> None:
        """Test that circuit hash generation is deterministic."""
        cache = CircuitAnalysisCache()

        # Create two identical circuits
        circuit1 = QuantumCircuit(2)
        circuit1.h(0)
        circuit1.cx(0, 1)

        circuit2 = QuantumCircuit(2)
        circuit2.h(0)
        circuit2.cx(0, 1)

        # Hashes should be identical
        hash1 = cache._circuit_hash(circuit1)
        hash2 = cache._circuit_hash(circuit2)

        assert hash1 == hash2

        # Store analysis for one circuit
        analysis = {"num_qubits": 2, "depth": 2}
        cache.store_analysis(circuit1, analysis)

        # Should be able to retrieve with the other circuit
        retrieved = cache.get_analysis(circuit2)
        assert retrieved == analysis

    def test_circuit_hash_with_parameters(self) -> None:
        """Test circuit hash generation with parameterized gates."""
        cache = CircuitAnalysisCache()

        # Create circuits with different parameters
        circuit1 = QuantumCircuit(1)
        circuit1.rx(0.5, 0)  # Rotation of 0.5

        circuit2 = QuantumCircuit(1)
        circuit2.rx(1.0, 0)  # Rotation of 1.0

        # Hashes should be different
        hash1 = cache._circuit_hash(circuit1)
        hash2 = cache._circuit_hash(circuit2)

        assert hash1 != hash2


class TestResourceManager:
    """Test the resource management system."""

    def test_resource_manager_singleton(self) -> None:
        """Test that ResourceManager is a singleton."""
        manager1 = get_resource_manager()
        manager2 = get_resource_manager()
        assert manager1 is manager2

    def test_circuit_feasibility_check(self) -> None:
        """Test circuit feasibility checking."""
        circuit = QuantumCircuit(5)
        circuit.h(range(5))

        # Should return True, reason for small circuit
        can_handle, reason = check_circuit_feasibility(circuit, "qiskit")
        assert can_handle
        assert "sufficient" in reason.lower()

    def test_resource_requirements_estimation(self) -> None:
        """Test resource requirements estimation."""
        manager = get_resource_manager()

        circuit = QuantumCircuit(10)
        circuit.h(range(10))

        requirements = manager.estimate_circuit_requirements(circuit, "qiskit")
        assert requirements.memory_mb > 0
        assert requirements.cpu_cores > 0
        assert requirements.estimated_time_seconds > 0
        assert requirements.backend == "qiskit"


class TestLoggingSystem:
    """Test the enhanced logging system."""

    def test_logger_creation(self) -> None:
        """Test logger creation."""
        logger = get_logger("test")
        assert logger is not None

    def test_logger_context_setting(self) -> None:
        """Test logger context setting."""
        logger = get_logger("test")

        circuit = QuantumCircuit(3)
        circuit.h(0)
        circuit.cx(0, 1)

        logger.set_circuit_context(circuit)
        # Context should be set internally
        assert logger._context.num_qubits == 3
        assert logger._context.depth == 2


class TestIntegratedSimulation:
    """Test the integrated simulation with new core systems."""

    def test_basic_simulation_with_new_systems(self) -> None:
        """Test basic simulation works with new core systems."""
        circuit = QuantumCircuit(2)
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.measure_all()

        result = simulate(circuit, shots=100)

        assert result.counts is not None
        assert result.backend_used is not None
        assert result.execution_time > 0
        assert sum(result.counts.values()) == 100

    def test_simulation_error_handling(self) -> None:
        """Test simulation error handling."""
        # Create a circuit that might cause issues
        circuit = QuantumCircuit(1)
        circuit.x(0)
        circuit.measure_all()

        # This should work fine
        result = simulate(circuit, shots=10)
        assert result.counts == {"1": 10}

    def test_input_validation(self) -> None:
        """Test input validation in simulate function."""
        circuit = QuantumCircuit(2)
        circuit.h(0)

        # Test negative shots
        with pytest.raises(ValueError, match="shots must be non-negative"):
            simulate(circuit, shots=-1)


if __name__ == "__main__":
    pytest.main([__file__])
