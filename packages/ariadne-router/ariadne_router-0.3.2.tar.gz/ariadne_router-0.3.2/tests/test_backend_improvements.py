"""Test suite for Phase 2 backend improvements."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest
from qiskit import QuantumCircuit

from ariadne.backends import (
    BackendCapabilities,
    BackendCapability,
    BackendFallbackManager,
    BackendHealthChecker,
    BackendPerformanceMonitor,
    BackendPool,
    BackendPoolExhaustedError,
    BackendPoolManager,
    EnhancedBackendWrapper,
    FallbackResult,
    HealthStatus,
    OptimizationHint,
    PerformanceMetricType,
    PoolStatus,
    create_backend_pool,
    create_enhanced_backend,
    execute_with_fallback,
    get_fallback_manager,
    get_health_checker,
    get_performance_monitor,
    get_pool_manager,
    is_backend_healthy,
    record_simulation_performance,
)
from ariadne.core import BackendUnavailableError
from ariadne.types import BackendType

if TYPE_CHECKING:
    from ariadne.backends.health_checker import HealthCheckResult


class TestBackendHealthChecker:
    """Test the backend health checking system."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.health_checker = BackendHealthChecker(check_interval=0.1, timeout=0.5)

    def teardown_method(self) -> None:
        """Clean up after tests."""
        self.health_checker.stop_monitoring()

    def test_health_check_registration(self) -> None:
        """Test health check registration."""

        def mock_health_check() -> HealthCheckResult:
            from ariadne.backends.health_checker import HealthCheckResult, HealthStatus

            return HealthCheckResult(
                status=HealthStatus.HEALTHY,
                message="Test backend is healthy",
                timestamp=time.time(),
                response_time=0.1,
            )

        self.health_checker.register_health_check(BackendType.QISKIT, mock_health_check)
        assert BackendType.QISKIT in self.health_checker._health_checks

    def test_backend_health_check(self) -> None:
        """Test individual backend health check."""

        def mock_health_check() -> HealthCheckResult:
            from ariadne.backends.health_checker import HealthCheckResult, HealthStatus

            return HealthCheckResult(
                status=HealthStatus.HEALTHY,
                message="Test backend is healthy",
                timestamp=time.time(),
                response_time=0.1,
            )

        self.health_checker.register_health_check(BackendType.QISKIT, mock_health_check)
        result = self.health_checker.check_backend_health(BackendType.QISKIT)

        assert result.status == HealthStatus.HEALTHY
        assert "healthy" in result.message
        assert result.response_time > 0

    def test_unhealthy_backend_detection(self) -> None:
        """Test detection of unhealthy backends."""

        def failing_health_check() -> HealthCheckResult:
            from ariadne.backends.health_checker import HealthCheckResult, HealthStatus

            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message="Test backend is unhealthy",
                timestamp=time.time(),
                response_time=0.1,
            )

        self.health_checker.register_health_check(BackendType.QISKIT, failing_health_check)
        result = self.health_checker.check_backend_health(BackendType.QISKIT)

        assert result.status == HealthStatus.UNHEALTHY
        assert "unhealthy" in result.message

    def test_healthy_backends_list(self) -> None:
        """Test getting list of healthy backends."""

        def healthy_check() -> HealthCheckResult:
            from ariadne.backends.health_checker import HealthCheckResult, HealthStatus

            return HealthCheckResult(
                status=HealthStatus.HEALTHY,
                message="Healthy",
                timestamp=time.time(),
                response_time=0.1,
            )

        def unhealthy_check() -> HealthCheckResult:
            from ariadne.backends.health_checker import HealthCheckResult, HealthStatus

            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message="Unhealthy",
                timestamp=time.time(),
                response_time=0.1,
            )

        self.health_checker.register_health_check(BackendType.QISKIT, healthy_check)
        self.health_checker.register_health_check(BackendType.STIM, unhealthy_check)

        # Check backends
        self.health_checker.check_backend_health(BackendType.QISKIT)
        self.health_checker.check_backend_health(BackendType.STIM)

        healthy_backends = self.health_checker.get_healthy_backends()
        assert BackendType.QISKIT in healthy_backends
        assert BackendType.STIM not in healthy_backends

    def test_global_health_checker(self) -> None:
        """Test global health checker instance."""
        global_checker = get_health_checker()
        assert isinstance(global_checker, BackendHealthChecker)

        # Should return same instance
        global_checker2 = get_health_checker()
        assert global_checker is global_checker2

    def test_is_backend_healthy_function(self) -> None:
        """Test convenience function for checking backend health."""

        def healthy_check() -> HealthCheckResult:
            from ariadne.backends.health_checker import HealthCheckResult, HealthStatus

            return HealthCheckResult(
                status=HealthStatus.HEALTHY,
                message="Healthy",
                timestamp=time.time(),
                response_time=0.1,
            )

        global_checker = get_health_checker()
        global_checker.register_health_check(BackendType.QISKIT, healthy_check)
        global_checker.check_backend_health(BackendType.QISKIT)

        assert is_backend_healthy(BackendType.QISKIT)


class TestBackendPool:
    """Test the backend pooling system."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_backend_class = Mock()
        self.mock_backend_instance = Mock()
        self.mock_backend_class.return_value = self.mock_backend_instance

        self.pool = BackendPool(
            backend_class=self.mock_backend_class,
            backend_name="test_backend",
            min_instances=1,
            max_instances=3,
        )

    def teardown_method(self) -> None:
        """Clean up after tests."""
        self.pool.shutdown()

    def test_pool_initialization(self) -> None:
        """Test pool initialization."""
        assert self.pool.get_status() == PoolStatus.READY
        assert self.pool._stats.total_instances >= 1

    def test_get_backend_from_pool(self) -> None:
        """Test getting backend from pool."""
        backend = self.pool.get_backend()
        assert backend is self.mock_backend_instance

        # Check statistics
        stats = self.pool.get_statistics()
        assert stats.total_requests == 1
        assert stats.successful_requests == 1

    def test_return_backend_to_pool(self) -> None:
        """Test returning backend to pool."""
        backend = self.pool.get_backend()
        self.pool.return_backend(backend)

        # Check statistics
        stats = self.pool.get_statistics()
        assert stats.available_instances >= 1

    def test_pool_exhaustion(self) -> None:
        """Test pool exhaustion behavior."""
        # Get all available backends
        backends = []
        for _ in range(self.pool.max_instances):
            try:
                backend = self.pool.get_backend(timeout=0.1)
                backends.append(backend)
            except Exception:
                break

        # Try to get one more (should fail)
        with pytest.raises(BackendPoolExhaustedError):
            self.pool.get_backend(timeout=0.1)

        # Return backends
        for backend in backends:
            self.pool.return_backend(backend)

    def test_pool_statistics(self) -> None:
        """Test pool statistics."""
        # Perform some operations
        backend = self.pool.get_backend()
        self.pool.return_backend(backend)

        stats = self.pool.get_statistics()
        assert stats.backend_name == "test_backend"
        assert stats.total_requests >= 1
        assert stats.successful_requests >= 1
        assert stats.utilization_rate >= 0

    def test_global_pool_manager(self) -> None:
        """Test global pool manager."""
        manager = get_pool_manager()
        assert isinstance(manager, BackendPoolManager)

        # Should return same instance
        manager2 = get_pool_manager()
        assert manager is manager2

    def test_create_backend_pool_function(self) -> None:
        """Test convenience function for creating backend pools."""
        pool = create_backend_pool(
            backend_name="test_pool",
            backend_class=self.mock_backend_class,
            min_instances=1,
            max_instances=2,
        )

        assert isinstance(pool, BackendPool)
        assert pool.backend_name == "test_pool"

        pool.shutdown()


class TestEnhancedBackendInterface:
    """Test the enhanced backend interface."""

    def test_enhanced_backend_wrapper_creation(self) -> None:
        """Test creation of enhanced backend wrapper."""
        mock_backend = Mock()
        mock_backend.simulate.return_value = {"00": 500, "11": 500}

        capabilities = BackendCapabilities(
            supported_capabilities=[BackendCapability.STATE_VECTOR_SIMULATION],
            optimization_hints=[OptimizationHint.BENEFITS_FROM_GATE_FUSION],
            max_qubits=20,
            typical_qubits=15,
            memory_efficiency=0.7,
            speed_rating=0.8,
            accuracy_rating=0.9,
            stability_rating=0.85,
        )

        enhanced = create_enhanced_backend(backend=mock_backend, backend_name="test_backend", capabilities=capabilities)

        assert isinstance(enhanced, EnhancedBackendWrapper)
        assert enhanced.backend_name == "test_backend"

    def test_enhanced_backend_simulation(self) -> None:
        """Test simulation with enhanced backend."""
        mock_backend = Mock()
        mock_backend.simulate.return_value = {"00": 500, "11": 500}

        enhanced = create_enhanced_backend(backend=mock_backend, backend_name="test_backend")

        circuit = QuantumCircuit(2)
        circuit.h(0)
        circuit.cx(0, 1)

        result = enhanced.simulate(circuit, shots=1000)
        assert result == {"00": 500, "11": 500}

        # Check performance metrics
        metrics = enhanced.get_performance_metrics()
        assert metrics.total_simulations == 1
        assert metrics.successful_simulations == 1

    def test_capability_support_check(self) -> None:
        """Test capability support checking."""
        capabilities = BackendCapabilities(
            supported_capabilities=[
                BackendCapability.STATE_VECTOR_SIMULATION,
                BackendCapability.NOISE_MODELING,
            ],
            optimization_hints=[],
            max_qubits=20,
            typical_qubits=15,
            memory_efficiency=0.7,
            speed_rating=0.8,
            accuracy_rating=0.9,
            stability_rating=0.85,
        )

        mock_backend = Mock()
        enhanced = create_enhanced_backend(backend=mock_backend, backend_name="test_backend", capabilities=capabilities)

        assert enhanced.supports_capability(BackendCapability.STATE_VECTOR_SIMULATION)
        assert enhanced.supports_capability(BackendCapability.NOISE_MODELING)
        assert not enhanced.supports_capability(BackendCapability.GPU_ACCELERATION)

    def test_optimization_recommendations(self) -> None:
        """Test optimization recommendations."""
        capabilities = BackendCapabilities(
            supported_capabilities=[BackendCapability.STATE_VECTOR_SIMULATION],
            optimization_hints=[
                OptimizationHint.BENEFITS_FROM_GATE_FUSION,
                OptimizationHint.BENEFITS_FROM_CIRCUIT_OPTIMIZATION,
            ],
            max_qubits=20,
            typical_qubits=15,
            memory_efficiency=0.7,
            speed_rating=0.8,
            accuracy_rating=0.9,
            stability_rating=0.85,
        )

        mock_backend = Mock()
        enhanced = create_enhanced_backend(backend=mock_backend, backend_name="test_backend", capabilities=capabilities)

        # Large circuit
        large_circuit = QuantumCircuit(25)
        for i in range(24):
            large_circuit.cx(i, i + 1)

        recommendations = enhanced.get_optimization_recommendations(large_circuit)
        assert any("gate fusion" in rec for rec in recommendations)
        assert any("circuit optimization" in rec for rec in recommendations)
        assert any("larger than typical" in rec for rec in recommendations)


class TestBackendFallbackStrategy:
    """Test the backend fallback strategy system."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        # Use the global fallback manager to ensure tests work with global functions
        self.fallback_manager = get_fallback_manager()

        # Clear fallback history to ensure clean test state
        self.fallback_manager._fallback_history.clear()

        # Register mock fallback functions
        def qiskit_fallback(circuit: QuantumCircuit, shots: int) -> dict[str, int]:
            return {"0": shots // 2, "1": shots // 2}

        def stim_fallback(circuit: QuantumCircuit, shots: int) -> dict[str, int]:
            return {"00": shots, "11": 0}

        self.fallback_manager.register_fallback_function(BackendType.QISKIT, qiskit_fallback)
        self.fallback_manager.register_fallback_function(BackendType.STIM, stim_fallback)

    def test_fallback_chain_selection(self) -> None:
        """Test fallback chain selection."""
        # Clifford circuit
        clifford_circuit = QuantumCircuit(2)
        clifford_circuit.h(0)
        clifford_circuit.cx(0, 1)

        chain = self.fallback_manager.get_fallback_chain(clifford_circuit)
        assert BackendType.STIM in chain
        assert BackendType.QISKIT in chain

    def test_large_circuit_fallback_chain(self) -> None:
        """Test fallback chain for large circuits."""
        large_circuit = QuantumCircuit(30)
        for i in range(29):
            large_circuit.h(i)

        print(f"DEBUG: Large circuit has {large_circuit.num_qubits} qubits")
        print(f"DEBUG: Is it Clifford? {self.fallback_manager._is_clifford_circuit(large_circuit)}")

        chain = self.fallback_manager.get_fallback_chain(large_circuit)
        print(f"DEBUG: Large circuit fallback chain: {[b.value for b in chain]}")
        # Should prioritize memory-efficient backends
        assert any(backend in chain for backend in [BackendType.TENSOR_NETWORK, BackendType.MPS])

    def test_successful_fallback_execution(self) -> None:
        """Test successful fallback execution."""
        circuit = QuantumCircuit(1)
        circuit.h(0)

        result = self.fallback_manager.execute_with_fallback(
            circuit=circuit, shots=100, fallback_chain=[BackendType.QISKIT]
        )

        assert isinstance(result, FallbackResult)
        assert result.success
        assert result.final_result == {"0": 50, "1": 50}
        assert result.backend_used == BackendType.QISKIT
        assert result.num_attempts == 1

    def test_fallback_after_failure(self) -> None:
        """Test fallback after primary backend failure."""
        circuit = QuantumCircuit(1)
        circuit.h(0)

        # Register a failing function
        def failing_fallback(circuit: QuantumCircuit, shots: int) -> dict[str, int]:
            raise BackendUnavailableError("test", "Test failure")

        self.fallback_manager.register_fallback_function(BackendType.CUDA, failing_fallback)

        result = self.fallback_manager.execute_with_fallback(
            circuit=circuit, shots=100, fallback_chain=[BackendType.CUDA, BackendType.QISKIT]
        )

        assert result.success
        assert result.backend_used == BackendType.QISKIT
        assert result.num_attempts == 2
        assert any(not attempt.success for attempt in result.attempts)

    def test_fallback_statistics(self) -> None:
        """Test fallback statistics."""
        circuit = QuantumCircuit(1)
        circuit.h(0)

        # Execute some fallbacks
        self.fallback_manager.execute_with_fallback(circuit=circuit, shots=100, fallback_chain=[BackendType.QISKIT])

        self.fallback_manager.execute_with_fallback(circuit=circuit, shots=100, fallback_chain=[BackendType.STIM])

        stats = self.fallback_manager.get_fallback_statistics()
        assert stats["total_fallbacks"] == 2
        assert stats["success_rate"] == 1.0

    def test_global_fallback_manager(self) -> None:
        """Test global fallback manager."""
        manager = get_fallback_manager()
        assert isinstance(manager, BackendFallbackManager)

        # Should return same instance
        manager2 = get_fallback_manager()
        assert manager is manager2

    def test_execute_with_fallback_function(self) -> None:
        """Test convenience function for fallback execution."""
        circuit = QuantumCircuit(1)
        circuit.h(0)

        result = execute_with_fallback(circuit=circuit, shots=100, fallback_chain=[BackendType.QISKIT])

        assert isinstance(result, FallbackResult)
        assert result.success


class TestBackendPerformanceMonitor:
    """Test the backend performance monitoring system."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.performance_monitor = BackendPerformanceMonitor()

    def test_metric_recording(self) -> None:
        """Test recording of performance metrics."""
        self.performance_monitor.record_metric(
            backend=BackendType.QISKIT,
            metric_type=PerformanceMetricType.EXECUTION_TIME,
            value=0.5,
            unit="seconds",
        )

        profile = self.performance_monitor.get_backend_profile(BackendType.QISKIT)
        assert profile is not None

        metrics = profile.get_latest_metrics(PerformanceMetricType.EXECUTION_TIME)
        assert len(metrics) == 1
        assert metrics[0].value == 0.5
        assert metrics[0].unit == "seconds"

    def test_simulation_performance_recording(self) -> None:
        """Test recording of simulation performance."""
        circuit = QuantumCircuit(2)
        circuit.h(0)
        circuit.cx(0, 1)

        self.performance_monitor.record_simulation(
            backend=BackendType.QISKIT,
            circuit=circuit,
            shots=1000,
            execution_time=0.5,
            memory_usage=100.0,
            success=True,
        )

        profile = self.performance_monitor.get_backend_profile(BackendType.QISKIT)
        assert profile is not None

        # Check execution time metric
        exec_time_metrics = profile.get_latest_metrics(PerformanceMetricType.EXECUTION_TIME)
        assert len(exec_time_metrics) >= 1
        assert exec_time_metrics[-1].value == 0.5

        # Check memory usage metric
        memory_metrics = profile.get_latest_metrics(PerformanceMetricType.MEMORY_USAGE)
        assert len(memory_metrics) >= 1
        assert memory_metrics[-1].value == 100.0

        # Check throughput metric
        throughput_metrics = profile.get_latest_metrics(PerformanceMetricType.THROUGHPUT)
        assert len(throughput_metrics) >= 1
        assert throughput_metrics[-1].value == 2000.0  # 1000 / 0.5

    def test_performance_alerts(self) -> None:
        """Test performance alert generation."""
        # Record a metric that should trigger an alert
        self.performance_monitor.record_metric(
            backend=BackendType.QISKIT,
            metric_type=PerformanceMetricType.EXECUTION_TIME,
            value=10.0,  # Above error threshold
            unit="seconds",
        )

        profile = self.performance_monitor.get_backend_profile(BackendType.QISKIT)
        assert profile is not None

        # Should have generated an alert
        assert len(profile.alerts) > 0
        assert profile.alerts[-1].metric_type == PerformanceMetricType.EXECUTION_TIME
        assert profile.alerts[-1].severity.value in ["error", "critical"]

    def test_backend_performance_summary(self) -> None:
        """Test backend performance summary."""
        circuit = QuantumCircuit(2)
        circuit.h(0)
        circuit.cx(0, 1)

        # Record some metrics
        self.performance_monitor.record_simulation(
            backend=BackendType.QISKIT,
            circuit=circuit,
            shots=1000,
            execution_time=0.5,
            memory_usage=100.0,
            success=True,
        )

        summary = self.performance_monitor.get_backend_summary(BackendType.QISKIT)
        assert summary["backend"] == "qiskit"
        assert "metrics" in summary
        assert "alerts" in summary
        assert PerformanceMetricType.EXECUTION_TIME.value in summary["metrics"]

    def test_performance_recommendations(self) -> None:
        """Test performance recommendations."""
        # Record some poor performance metrics
        self.performance_monitor.record_metric(
            backend=BackendType.QISKIT,
            metric_type=PerformanceMetricType.EXECUTION_TIME,
            value=5.0,  # High execution time
            unit="seconds",
        )

        self.performance_monitor.record_metric(
            backend=BackendType.QISKIT,
            metric_type=PerformanceMetricType.SUCCESS_RATE,
            value=0.8,  # Low success rate
            unit="percent",
        )

        recommendations = self.performance_monitor.get_performance_recommendations(BackendType.QISKIT)
        assert len(recommendations) > 0
        assert any("optimizing" in rec for rec in recommendations)

    def test_global_performance_monitor(self) -> None:
        """Test global performance monitor."""
        monitor = get_performance_monitor()
        assert isinstance(monitor, BackendPerformanceMonitor)

        # Should return same instance
        monitor2 = get_performance_monitor()
        assert monitor is monitor2

    def test_record_simulation_performance_function(self) -> None:
        """Test convenience function for recording performance."""
        circuit = QuantumCircuit(2)
        circuit.h(0)
        circuit.cx(0, 1)

        record_simulation_performance(
            backend=BackendType.QISKIT,
            circuit=circuit,
            shots=1000,
            execution_time=0.5,
            memory_usage=100.0,
            success=True,
        )

        monitor = get_performance_monitor()
        profile = monitor.get_backend_profile(BackendType.QISKIT)
        assert profile is not None


class TestIntegratedBackendSystems:
    """Test integration of all backend systems."""

    def test_health_checking_with_pooling(self) -> None:
        """Test integration of health checking with pooling."""
        # This would test that unhealthy backends are removed from pools
        # Implementation would depend on specific integration points
        pass

    def test_fallback_with_performance_monitoring(self) -> None:
        """Test integration of fallback with performance monitoring."""
        # This would test that fallback attempts are recorded in performance metrics
        # Implementation would depend on specific integration points
        pass

    def test_enhanced_interface_with_all_systems(self) -> None:
        """Test integration of enhanced interface with all systems."""
        # This would test that enhanced backends work with health checking,
        # pooling, fallback, and performance monitoring
        # Implementation would depend on specific integration points
        pass


if __name__ == "__main__":
    pytest.main([__file__])
