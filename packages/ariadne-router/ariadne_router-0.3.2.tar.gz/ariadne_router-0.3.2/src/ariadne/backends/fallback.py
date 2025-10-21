"""
Backend fallback strategy system for Ariadne.

This module provides intelligent fallback strategies for quantum simulation backends,
ensuring simulations complete even when primary backends fail.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from qiskit import QuantumCircuit

from ..core import BackendUnavailableError, SimulationError, get_logger
from ..types import BackendType


class FallbackReason(Enum):
    """Reason for backend fallback."""

    BACKEND_UNAVAILABLE = "backend_unavailable"
    SIMULATION_ERROR = "simulation_error"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    TIMEOUT = "timeout"
    CIRCUIT_TOO_LARGE = "circuit_too_large"
    CAPABILITY_MISMATCH = "capability_mismatch"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    USER_PREFERENCE = "user_preference"


class FallbackStrategy(Enum):
    """Fallback strategy types."""

    IMMEDIATE = "immediate"  # Fall back immediately on error
    RETRY_THEN_FALLBACK = "retry_then_fallback"  # Retry before falling back
    DEGRADE_QUALITY = "degrade_quality"  # Degrade simulation quality
    ADAPTIVE = "adaptive"  # Adapt based on error type and circuit properties


@dataclass
class FallbackAttempt:
    """Record of a fallback attempt."""

    backend: BackendType
    success: bool
    execution_time: float
    error_message: str | None = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class FallbackResult:
    """Result of a fallback operation."""

    success: bool
    backend_used: BackendType
    attempts: list[FallbackAttempt]
    total_time: float
    final_result: dict[str, int] | None = None
    fallback_reason: FallbackReason | None = None

    @property
    def num_attempts(self) -> int:
        """Get number of fallback attempts."""
        return len(self.attempts)

    @property
    def first_backend(self) -> BackendType:
        """Get the first backend attempted."""
        return self.attempts[0].backend if self.attempts else BackendType.QISKIT

    @property
    def successful_backend(self) -> BackendType | None:
        """Get the backend that succeeded."""
        for attempt in reversed(self.attempts):
            if attempt.success:
                return attempt.backend
        return None


class BackendFallbackManager:
    """
    Manager for backend fallback strategies.

    This class provides intelligent fallback strategies for quantum simulation
    backends, ensuring simulations complete even when primary backends fail.
    """

    def __init__(self, default_strategy: FallbackStrategy = FallbackStrategy.ADAPTIVE):
        """
        Initialize the fallback manager.

        Args:
            default_strategy: Default fallback strategy to use
        """
        self.default_strategy = default_strategy
        self.logger = get_logger("fallback_manager")

        # Fallback chains for different scenarios
        self._fallback_chains: dict[str, list[BackendType]] = {}
        self._backend_priorities: dict[BackendType, int] = {}

        # Fallback functions
        self._fallback_functions: dict[BackendType, Callable[[QuantumCircuit, int], dict[str, int]]] = {}

        # Statistics
        self._fallback_history: list[FallbackResult] = []
        self._max_history = 1000

        # Initialize default fallback chains
        self._initialize_default_chains()

    def _initialize_default_chains(self) -> None:
        """Initialize default fallback chains."""
        # General purpose fallback chain
        self._fallback_chains["general"] = [
            BackendType.STIM,  # Best for Clifford circuits
            BackendType.CUDA,  # GPU acceleration
            BackendType.JAX_METAL,  # Apple Silicon GPU
            BackendType.TENSOR_NETWORK,  # Good for structured circuits
            BackendType.MPS,  # Memory efficient
            BackendType.DDSIM,  # Decision diagrams
            BackendType.QISKIT,  # Fallback
        ]

        # Clifford circuit fallback chain
        self._fallback_chains["clifford"] = [
            BackendType.STIM,
            BackendType.QISKIT,
        ]

        # Large circuit fallback chain
        self._fallback_chains["large"] = [
            BackendType.TENSOR_NETWORK,
            BackendType.MPS,
            BackendType.STIM,  # If it's a large Clifford circuit
            BackendType.QISKIT,
        ]

        # GPU-accelerated fallback chain
        self._fallback_chains["gpu"] = [
            BackendType.CUDA,
            BackendType.JAX_METAL,
            BackendType.QISKIT,
        ]

        # Set default priorities
        priorities = {
            BackendType.STIM: 10,
            BackendType.CUDA: 9,
            BackendType.JAX_METAL: 8,
            BackendType.TENSOR_NETWORK: 7,
            BackendType.MPS: 6,
            BackendType.DDSIM: 5,
            BackendType.QISKIT: 3,
        }

        self._backend_priorities.update(priorities)

    def register_fallback_function(
        self,
        backend: BackendType,
        fallback_function: Callable[[QuantumCircuit, int], dict[str, int]],
    ) -> None:
        """
        Register a fallback function for a backend.

        Args:
            backend: Backend type
            fallback_function: Function to call for fallback
        """
        self._fallback_functions[backend] = fallback_function
        self.logger.info(f"Registered fallback function for {backend.value}")

    def set_fallback_chain(self, scenario: str, backends: list[BackendType]) -> None:
        """
        Set a fallback chain for a specific scenario.

        Args:
            scenario: Scenario name
            backends: List of backends in fallback order
        """
        self._fallback_chains[scenario] = backends
        self.logger.info(f"Set fallback chain for {scenario}: {[b.value for b in backends]}")

    def set_backend_priority(self, backend: BackendType, priority: int) -> None:
        """
        Set priority for a backend.

        Args:
            backend: Backend type
            priority: Priority (higher = more preferred)
        """
        self._backend_priorities[backend] = priority
        self.logger.info(f"Set {backend.value} priority to {priority}")

    def get_fallback_chain(
        self,
        circuit: QuantumCircuit | None = None,
        scenario: str | None = None,
        initial_backend: BackendType | None = None,
    ) -> list[BackendType]:
        """
        Get appropriate fallback chain.

        Args:
            circuit: Circuit to simulate
            scenario: Specific scenario
            initial_backend: Initial backend that failed

        Returns:
            List of backends in fallback order
        """
        # If scenario is specified, use it
        if scenario and scenario in self._fallback_chains:
            chain = self._fallback_chains[scenario]
            self.logger.debug(f"Using scenario fallback chain for {scenario}: {[b.value for b in chain]}")
            return chain

        # If circuit is provided, analyze it
        if circuit:
            # Check if it's a large circuit first (prioritize over Clifford)
            if circuit.num_qubits > 25:
                chain = self._fallback_chains["large"]
                print(
                    f"DEBUG: Using large circuit fallback chain "
                    f"({circuit.num_qubits} qubits): {[b.value for b in chain]}"
                )
                self.logger.debug(
                    f"Using large circuit fallback chain ({circuit.num_qubits} qubits): {[b.value for b in chain]}"
                )
                return chain

            # Check if it's a Clifford circuit (only if not large)
            if self._is_clifford_circuit(circuit):
                chain = self._fallback_chains["clifford"]
                self.logger.debug(f"Using Clifford fallback chain: {[b.value for b in chain]}")
                return chain

        # Use general fallback chain
        chain = self._fallback_chains["general"]
        self.logger.debug(f"Using general fallback chain: {[b.value for b in chain]}")
        return chain

    def _is_clifford_circuit(self, circuit: QuantumCircuit) -> bool:
        """Check if circuit is a Clifford circuit."""
        # Simple heuristic - could be improved
        clifford_gates = {"h", "x", "y", "z", "s", "sdg", "sx", "sxdg", "cx", "cz", "swap"}

        for instruction in circuit.data:
            if instruction.operation.name not in clifford_gates:
                return False

        return True

    def execute_with_fallback(
        self,
        circuit: QuantumCircuit,
        shots: int,
        initial_backend: BackendType | None = None,
        fallback_chain: list[BackendType] | None = None,
        strategy: FallbackStrategy | None = None,
        max_attempts: int = 5,
    ) -> FallbackResult:
        """
        Execute simulation with fallback strategy.

        Args:
            circuit: Circuit to simulate
            shots: Number of shots
            initial_backend: Initial backend to try
            fallback_chain: Custom fallback chain
            strategy: Fallback strategy
            max_attempts: Maximum number of attempts

        Returns:
            Fallback result
        """
        start_time = time.time()
        strategy = strategy or self.default_strategy

        # Determine fallback chain
        if fallback_chain is None:
            if initial_backend:
                # Get fallback chain excluding initial backend
                chain = self.get_fallback_chain(circuit)
                fallback_chain = [initial_backend] + [b for b in chain if b != initial_backend]
            else:
                fallback_chain = self.get_fallback_chain(circuit)

        # Limit attempts
        fallback_chain = fallback_chain[:max_attempts]

        print(f"DEBUG: Executing with fallback chain: {[b.value for b in fallback_chain]}")
        print(f"DEBUG: Registered fallback functions: {[b.value for b in self._fallback_functions.keys()]}")
        self.logger.info(f"Executing with fallback chain: {[b.value for b in fallback_chain]}")
        self.logger.debug(f"Registered fallback functions: {[b.value for b in self._fallback_functions.keys()]}")

        # Execute with fallback
        attempts: list[FallbackAttempt] = []
        final_result: dict[str, int] | None = None
        fallback_reason: FallbackReason | None = None

        for backend in fallback_chain:
            attempt_start = time.time()
            success = False
            error_message = None

            try:
                self.logger.debug(f"Attempting simulation with {backend.value}")

                # Get fallback function
                if backend in self._fallback_functions:
                    self.logger.debug(f"Using registered fallback function for {backend.value}")
                    result = self._fallback_functions[backend](circuit, shots)
                else:
                    self.logger.debug(f"No fallback function registered for {backend.value}, trying direct simulation")
                    # Try to import and use the backend
                    result = self._simulate_with_backend(backend, circuit, shots)

                success = True
                final_result = result
                self.logger.info(f"Simulation successful with {backend.value}")

                # Record successful attempt
                attempts.append(
                    FallbackAttempt(backend=backend, success=success, execution_time=time.time() - attempt_start)
                )

                break

            except Exception as e:
                error_message = str(e)
                execution_time = time.time() - attempt_start

                # Determine fallback reason
                if isinstance(e, BackendUnavailableError):
                    fallback_reason = FallbackReason.BACKEND_UNAVAILABLE
                elif isinstance(e, SimulationError):
                    fallback_reason = FallbackReason.SIMULATION_ERROR
                elif "resource" in error_message.lower():
                    fallback_reason = FallbackReason.RESOURCE_EXHAUSTION
                elif "timeout" in error_message.lower():
                    fallback_reason = FallbackReason.TIMEOUT
                elif "large" in error_message.lower():
                    fallback_reason = FallbackReason.CIRCUIT_TOO_LARGE
                else:
                    fallback_reason = FallbackReason.SIMULATION_ERROR

                self.logger.warning(f"Simulation failed with {backend.value}: {error_message}")

                # Record failed attempt
                attempts.append(
                    FallbackAttempt(
                        backend=backend,
                        success=success,
                        execution_time=execution_time,
                        error_message=error_message,
                    )
                )

                # Apply strategy
                if strategy == FallbackStrategy.IMMEDIATE:
                    continue  # Immediately try next backend
                elif strategy == FallbackStrategy.RETRY_THEN_FALLBACK:
                    # Retry once before falling back
                    if len(attempts) == 1:  # First failure for this backend
                        try:
                            self.logger.debug(f"Retrying simulation with {backend.value}")
                            result = self._fallback_functions[backend](circuit, shots)
                            success = True
                            final_result = result

                            # Update last attempt
                            attempts[-1].success = True
                            attempts[-1].execution_time = time.time() - attempt_start
                            attempts[-1].error_message = None

                            self.logger.info(f"Retry successful with {backend.value}")
                            break
                        except Exception as retry_e:
                            self.logger.warning(f"Retry failed with {backend.value}: {retry_e}")
                            continue  # Fall back to next backend
                elif strategy == FallbackStrategy.DEGRADE_QUALITY:
                    # Try with reduced shots
                    if shots > 100:
                        try:
                            self.logger.debug(f"Retrying with reduced shots for {backend.value}")
                            reduced_shots = max(100, shots // 2)
                            result = self._fallback_functions[backend](circuit, reduced_shots)

                            # Scale up results if needed
                            if shots != reduced_shots:
                                scale_factor = shots / reduced_shots
                                result = {k: int(v * scale_factor) for k, v in result.items()}

                            success = True
                            final_result = result

                            # Update last attempt
                            attempts[-1].success = True
                            attempts[-1].execution_time = time.time() - attempt_start
                            attempts[-1].error_message = None

                            self.logger.info(f"Reduced shots simulation successful with {backend.value}")
                            break
                        except Exception as retry_e:
                            self.logger.warning(f"Reduced shots retry failed with {backend.value}: {retry_e}")
                            continue  # Fall back to next backend
                elif strategy == FallbackStrategy.ADAPTIVE:
                    # Adapt based on error type
                    if fallback_reason == FallbackReason.RESOURCE_EXHAUSTION:
                        # Try with a more memory-efficient backend
                        continue
                    elif fallback_reason == FallbackReason.TIMEOUT:
                        # Try with a faster backend
                        continue
                    else:
                        # Fall back to next backend
                        continue

        # Create result
        total_time = time.time() - start_time
        fallback_result = FallbackResult(
            success=final_result is not None,
            backend_used=attempts[-1].backend if attempts else BackendType.QISKIT,
            attempts=attempts,
            total_time=total_time,
            final_result=final_result,
            fallback_reason=fallback_reason,
        )

        # Record in history
        self._fallback_history.append(fallback_result)
        if len(self._fallback_history) > self._max_history:
            self._fallback_history = self._fallback_history[-self._max_history :]

        # Log summary
        if fallback_result.success:
            self.logger.info(
                f"Fallback successful: {fallback_result.backend_used.value} "
                f"after {fallback_result.num_attempts} attempts "
                f"in {total_time:.3f}s"
            )
        else:
            self.logger.error(f"Fallback failed after {fallback_result.num_attempts} attempts in {total_time:.3f}s")

        return fallback_result

    def _simulate_with_backend(self, backend: BackendType, circuit: QuantumCircuit, shots: int) -> dict[str, int]:
        """Simulate with a specific backend."""
        # This would be implemented based on available backends
        # For now, raise an error to indicate it needs to be implemented
        raise NotImplementedError(f"Simulation with {backend.value} not implemented")

    def get_fallback_statistics(self) -> dict[str, Any]:
        """
        Get fallback statistics.

        Returns:
            Dictionary of fallback statistics
        """
        if not self._fallback_history:
            return {
                "total_fallbacks": 0,
                "success_rate": 0.0,
                "average_attempts": 0.0,
                "average_time": 0.0,
                "most_common_backend": None,
                "most_common_reason": None,
            }

        total_fallbacks = len(self._fallback_history)
        successful_fallbacks = sum(1 for r in self._fallback_history if r.success)
        success_rate = successful_fallbacks / total_fallbacks

        total_attempts = sum(r.num_attempts for r in self._fallback_history)
        average_attempts = total_attempts / total_fallbacks

        total_time = sum(r.total_time for r in self._fallback_history)
        average_time = total_time / total_fallbacks

        # Most common backend
        backend_counts: dict[BackendType, int] = {}
        for result in self._fallback_history:
            backend = result.successful_backend or result.first_backend
            backend_counts[backend] = backend_counts.get(backend, 0) + 1

        most_common_backend = max(backend_counts.items(), key=lambda x: x[1])[0] if backend_counts else None

        # Most common fallback reason
        reason_counts: dict[FallbackReason, int] = {}
        for result in self._fallback_history:
            if result.fallback_reason:
                reason_counts[result.fallback_reason] = reason_counts.get(result.fallback_reason, 0) + 1

        most_common_reason = max(reason_counts.items(), key=lambda x: x[1])[0] if reason_counts else None

        return {
            "total_fallbacks": total_fallbacks,
            "success_rate": success_rate,
            "average_attempts": average_attempts,
            "average_time": average_time,
            "most_common_backend": most_common_backend,
            "most_common_reason": most_common_reason,
        }

    def get_recent_fallbacks(self, limit: int = 10) -> list[FallbackResult]:
        """
        Get recent fallback results.

        Args:
            limit: Maximum number of results to return

        Returns:
            List of recent fallback results
        """
        return self._fallback_history[-limit:] if self._fallback_history else []


# Global fallback manager instance
_global_fallback_manager: BackendFallbackManager | None = None


def get_fallback_manager() -> BackendFallbackManager:
    """Get the global fallback manager instance."""
    global _global_fallback_manager
    if _global_fallback_manager is None:
        _global_fallback_manager = BackendFallbackManager()
    return _global_fallback_manager


def execute_with_fallback(
    circuit: QuantumCircuit,
    shots: int,
    initial_backend: BackendType | None = None,
    fallback_chain: list[BackendType] | None = None,
    strategy: FallbackStrategy | None = None,
    max_attempts: int = 5,
) -> FallbackResult:
    """
    Execute simulation with fallback using the global fallback manager.

    Args:
        circuit: Circuit to simulate
        shots: Number of shots
        initial_backend: Initial backend to try
        fallback_chain: Custom fallback chain
        strategy: Fallback strategy
        max_attempts: Maximum number of attempts

    Returns:
        Fallback result
    """
    manager = get_fallback_manager()
    return manager.execute_with_fallback(
        circuit=circuit,
        shots=shots,
        initial_backend=initial_backend,
        fallback_chain=fallback_chain,
        strategy=strategy,
        max_attempts=max_attempts,
    )
