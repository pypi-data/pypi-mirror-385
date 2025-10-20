"""
Backend health checking system for Ariadne.

This module provides comprehensive health checking for all quantum simulation backends,
monitoring their availability, performance, and reliability.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from qiskit import QuantumCircuit

from ..core import get_logger
from ..types import BackendType


class HealthStatus(Enum):
    """Health status of a backend."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check."""

    status: HealthStatus
    message: str
    timestamp: float
    response_time: float
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def is_healthy(self) -> bool:
        """Check if backend is healthy."""
        return self.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]


@dataclass
class BackendHealthMetrics:
    """Health metrics for a backend."""

    backend_name: str
    status: HealthStatus
    last_check: float
    response_time: float
    success_rate: float
    total_checks: int
    consecutive_failures: int
    average_response_time: float
    uptime_percentage: float
    details: dict[str, Any] = field(default_factory=dict)


class HealthCheckError(Exception):
    """Raised when health check fails."""

    pass


class BackendHealthChecker:
    """
    Health checker for quantum simulation backends.

    This class monitors backend health through periodic checks and
    provides metrics and alerts for backend issues.
    """

    def __init__(self, check_interval: float = 60.0, timeout: float = 5.0):
        """
        Initialize the health checker.

        Args:
            check_interval: Interval between health checks in seconds
            timeout: Timeout for health checks in seconds
        """
        self.check_interval = check_interval
        self.timeout = timeout
        self.logger = get_logger("health_checker")

        # Health check registry
        self._health_checks: dict[BackendType, Callable[[], HealthCheckResult]] = {}
        self._backend_status: dict[BackendType, HealthStatus] = {}
        self._backend_metrics: dict[BackendType, BackendHealthMetrics] = {}

        # Threading
        self._running = False
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()

        # Statistics
        self._check_history: dict[BackendType, list[HealthCheckResult]] = {}
        self._max_history = 100  # Keep last 100 results per backend

    def register_health_check(self, backend: BackendType, health_check: Callable[[], HealthCheckResult]) -> None:
        """
        Register a health check for a backend.

        Args:
            backend: Backend type
            health_check: Function that performs health check
        """
        with self._lock:
            self._health_checks[backend] = health_check
            self._backend_status[backend] = HealthStatus.UNKNOWN
            self._check_history[backend] = []

            # Initialize metrics
            self._backend_metrics[backend] = BackendHealthMetrics(
                backend_name=backend.value,
                status=HealthStatus.UNKNOWN,
                last_check=0.0,
                response_time=0.0,
                success_rate=0.0,
                total_checks=0,
                consecutive_failures=0,
                average_response_time=0.0,
                uptime_percentage=0.0,
            )

        self.logger.info(f"Registered health check for backend: {backend.value}")

    def start_monitoring(self) -> None:
        """Start background health monitoring."""
        with self._lock:
            if self._running:
                return

            self._running = True
            self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._thread.start()

            self.logger.info("Started backend health monitoring")

    def stop_monitoring(self) -> None:
        """Stop background health monitoring."""
        with self._lock:
            if not self._running:
                return

            self._running = False

            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=self.timeout + 1.0)

            self.logger.info("Stopped backend health monitoring")

    def _monitor_loop(self) -> None:
        """Background monitoring loop."""
        while self._running:
            try:
                self._check_all_backends()
                time.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                time.sleep(min(self.check_interval, 10.0))  # Back off on error

    def _check_all_backends(self) -> None:
        """Check health of all registered backends."""
        backends = list(self._health_checks.keys())

        for backend in backends:
            try:
                result = self._check_backend(backend)
                self._update_metrics(backend, result)
            except Exception as e:
                self.logger.error(f"Health check failed for {backend.value}: {e}")

                # Create failure result
                result = HealthCheckResult(
                    status=HealthStatus.UNHEALTHY,
                    message=f"Health check failed: {e}",
                    timestamp=time.time(),
                    response_time=self.timeout,
                )
                self._update_metrics(backend, result)

    def _check_backend(self, backend: BackendType) -> HealthCheckResult:
        """Check health of a specific backend."""
        if backend not in self._health_checks:
            raise HealthCheckError(f"No health check registered for {backend.value}")

        start_time = time.time()

        try:
            # Execute health check with timeout
            result = self._health_checks[backend]()

            # Ensure response time is set
            if result.response_time <= 0:
                result.response_time = time.time() - start_time

            return result

        except Exception as e:
            # Health check failed
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message=f"Health check exception: {e}",
                timestamp=time.time(),
                response_time=time.time() - start_time,
            )

    def _update_metrics(self, backend: BackendType, result: HealthCheckResult) -> None:
        """Update health metrics for a backend."""
        with self._lock:
            # Update status
            self._backend_status[backend] = result.status

            # Add to history
            if backend not in self._check_history:
                self._check_history[backend] = []

            self._check_history[backend].append(result)

            # Trim history if needed
            if len(self._check_history[backend]) > self._max_history:
                self._check_history[backend] = self._check_history[backend][-self._max_history :]

            # Update metrics
            metrics = self._backend_metrics[backend]
            history = self._check_history[backend]

            metrics.status = result.status
            metrics.last_check = result.timestamp
            metrics.response_time = result.response_time
            metrics.total_checks = len(history)

            # Calculate success rate
            successful_checks = sum(1 for r in history if r.is_healthy)
            metrics.success_rate = successful_checks / len(history) if history else 0.0

            # Calculate consecutive failures
            if result.is_healthy:
                metrics.consecutive_failures = 0
            else:
                metrics.consecutive_failures += 1

            # Calculate average response time
            metrics.average_response_time = sum(r.response_time for r in history) / len(history) if history else 0.0

            # Calculate uptime percentage (last 24 hours)
            twenty_four_hours_ago = time.time() - 24 * 3600
            recent_checks = [r for r in history if r.timestamp >= twenty_four_hours_ago]
            if recent_checks:
                successful_recent = sum(1 for r in recent_checks if r.is_healthy)
                metrics.uptime_percentage = successful_recent / len(recent_checks) * 100
            else:
                metrics.uptime_percentage = 0.0

            # Update details
            metrics.details = result.details.copy()

    def check_backend_health(self, backend: BackendType) -> HealthCheckResult:
        """
        Manually check health of a backend.

        Args:
            backend: Backend type to check

        Returns:
            Health check result
        """
        result = self._check_backend(backend)
        self._update_metrics(backend, result)
        return result

    def get_backend_status(self, backend: BackendType) -> HealthStatus:
        """
        Get current status of a backend.

        Args:
            backend: Backend type

        Returns:
            Current health status
        """
        return self._backend_status.get(backend, HealthStatus.UNKNOWN)

    def get_backend_metrics(self, backend: BackendType) -> BackendHealthMetrics | None:
        """
        Get health metrics for a backend.

        Args:
            backend: Backend type

        Returns:
            Health metrics or None if not available
        """
        return self._backend_metrics.get(backend)

    def get_all_backend_metrics(self) -> dict[BackendType, BackendHealthMetrics]:
        """
        Get health metrics for all backends.

        Returns:
            Dictionary of backend metrics
        """
        return self._backend_metrics.copy()

    def get_healthy_backends(self) -> list[BackendType]:
        """
        Get list of healthy backends.

        Returns:
            List of healthy backend types
        """
        return [
            backend
            for backend, status in self._backend_status.items()
            if status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
        ]

    def get_unhealthy_backends(self) -> list[BackendType]:
        """
        Get list of unhealthy backends.

        Returns:
            List of unhealthy backend types
        """
        return [
            backend
            for backend, status in self._backend_status.items()
            if status in [HealthStatus.UNHEALTHY, HealthStatus.UNKNOWN]
        ]

    def get_backend_health_history(self, backend: BackendType, limit: int = 10) -> list[HealthCheckResult]:
        """
        Get health check history for a backend.

        Args:
            backend: Backend type
            limit: Maximum number of results to return

        Returns:
            List of health check results
        """
        history = self._check_history.get(backend, [])
        return history[-limit:] if history else []


# Global health checker instance
_global_health_checker: BackendHealthChecker | None = None


def get_health_checker() -> BackendHealthChecker:
    """Get the global health checker instance."""
    global _global_health_checker
    if _global_health_checker is None:
        _global_health_checker = BackendHealthChecker()
    return _global_health_checker


def is_backend_healthy(backend: BackendType) -> bool:
    """
    Check if a backend is healthy.

    Args:
        backend: Backend type

    Returns:
        True if backend is healthy
    """
    checker = get_health_checker()
    status = checker.get_backend_status(backend)
    return status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]


# Default health checks
def create_basic_health_check(backend_name: str, test_function: Callable[[], bool]) -> Callable[[], HealthCheckResult]:
    """
    Create a basic health check function.

    Args:
        backend_name: Name of the backend
        test_function: Function that returns True if backend is healthy

    Returns:
        Health check function
    """

    def health_check() -> HealthCheckResult:
        start_time = time.time()

        try:
            is_healthy = test_function()
            status = HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY

            return HealthCheckResult(
                status=status,
                message=f"{backend_name} is {'healthy' if is_healthy else 'unhealthy'}",
                timestamp=time.time(),
                response_time=time.time() - start_time,
                details={"backend": backend_name},
            )
        except Exception as e:
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message=f"{backend_name} health check failed: {e}",
                timestamp=time.time(),
                response_time=time.time() - start_time,
                details={"backend": backend_name, "error": str(e)},
            )

    return health_check


def create_circuit_based_health_check(
    backend_name: str,
    simulate_function: Callable[[QuantumCircuit, int], dict[str, int]],
    test_circuit: QuantumCircuit,
) -> Callable[[], HealthCheckResult]:
    """
    Create a circuit-based health check function.

    Args:
        backend_name: Name of the backend
        simulate_function: Function that simulates a circuit
        test_circuit: Circuit to use for health check

    Returns:
        Health check function
    """

    def health_check() -> HealthCheckResult:
        start_time = time.time()

        try:
            # Run test simulation
            result = simulate_function(test_circuit, 10)  # Small number of shots

            # Check if result is valid
            if not result or sum(result.values()) != 10:
                return HealthCheckResult(
                    status=HealthStatus.UNHEALTHY,
                    message=f"{backend_name} returned invalid simulation result",
                    timestamp=time.time(),
                    response_time=time.time() - start_time,
                    details={"backend": backend_name, "result": result},
                )

            return HealthCheckResult(
                status=HealthStatus.HEALTHY,
                message=f"{backend_name} successfully simulated test circuit",
                timestamp=time.time(),
                response_time=time.time() - start_time,
                details={
                    "backend": backend_name,
                    "test_circuit_qubits": test_circuit.num_qubits,
                    "test_circuit_depth": test_circuit.depth(),
                    "result_sample": dict(list(result.items())[:3]),
                },
            )
        except Exception as e:
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message=f"{backend_name} circuit simulation failed: {e}",
                timestamp=time.time(),
                response_time=time.time() - start_time,
                details={"backend": backend_name, "error": str(e)},
            )

    return health_check
