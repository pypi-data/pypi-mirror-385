"""
Enhanced backend interface for Ariadne.

This module provides an enhanced interface for quantum simulation backends,
adding capability discovery, performance monitoring, and optimization hints.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, cast

from qiskit import QuantumCircuit

from ..core import get_logger


class BackendCapability(Enum):
    """Different capabilities that backends can support."""

    STATE_VECTOR_SIMULATION = "state_vector"
    DENSITY_MATRIX_SIMULATION = "density_matrix"
    STABILIZER_SIMULATION = "stabilizer"
    NOISE_MODELING = "noise_modeling"
    GPU_ACCELERATION = "gpu_acceleration"
    DISTRIBUTED_COMPUTING = "distributed"
    QUANTUM_ML = "quantum_ml"
    HARDWARE_INTEGRATION = "hardware"
    PARAMETRIC_CIRCUITS = "parametric"
    ERROR_MITIGATION = "error_mitigation"
    TENSOR_NETWORK = "tensor_network"
    MATRIX_PRODUCT_STATE = "matrix_product_state"
    PARTIAL_TRACE = "partial_trace"
    AMPLITUDE_AMPLIFICATION = "amplitude_amplification"


class OptimizationHint(Enum):
    """Optimization hints for backends."""

    PREFERS_SMALL_CIRCUITS = "prefers_small_circuits"
    PREFERS_SHALLOW_CIRCUITS = "prefers_shallow_circuits"
    PREFERS_CLIFFORD_CIRCUITS = "prefers_clifford_circuits"
    PREFERS_SPARSE_CONNECTIVITY = "prefers_sparse_connectivity"
    BENEFITS_FROM_GATE_FUSION = "benefits_from_gate_fusion"
    BENEFITS_FROM_CIRCUIT_OPTIMIZATION = "benefits_from_circuit_optimization"
    MEMORY_INTENSIVE = "memory_intensive"
    CPU_INTENSIVE = "cpu_intensive"
    GPU_INTENSIVE = "gpu_intensive"


@dataclass
class BackendCapabilities:
    """Capabilities and characteristics of a backend."""

    supported_capabilities: list[BackendCapability]
    optimization_hints: list[OptimizationHint]
    max_qubits: int
    typical_qubits: int
    memory_efficiency: float  # 0-1 scale
    speed_rating: float  # 0-1 scale
    accuracy_rating: float  # 0-1 scale
    stability_rating: float  # 0-1 scale
    hardware_requirements: list[str] = field(default_factory=list)
    estimated_cost_factor: float = 1.0
    special_features: dict[str, Any] = field(default_factory=dict)


@dataclass
class BackendPerformanceMetrics:
    """Performance metrics for a backend."""

    backend_name: str
    total_simulations: int
    successful_simulations: int
    failed_simulations: int
    average_execution_time: float
    min_execution_time: float
    max_execution_time: float
    average_memory_usage: float
    last_simulation_time: float
    uptime: float
    error_rate: float

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_simulations == 0:
            return 0.0
        return self.successful_simulations / self.total_simulations


@dataclass
class SimulationMetadata:
    """Metadata about a simulation execution."""

    backend_name: str
    execution_time: float
    memory_used_mb: float
    success: bool
    error_message: str | None = None
    optimization_applied: bool = False
    hardware_acceleration: bool = False
    additional_info: dict[str, Any] = field(default_factory=dict)


class EnhancedBackendInterface(ABC):
    """
    Enhanced interface for quantum simulation backends.

    This interface extends the basic backend interface with capability discovery,
    performance monitoring, and optimization hints.
    """

    @abstractmethod
    def simulate(self, circuit: QuantumCircuit, shots: int = 1000, **kwargs: Any) -> dict[str, int]:
        """
        Simulate quantum circuit and return measurement counts.

        Args:
            circuit: Quantum circuit to simulate
            shots: Number of measurement shots
            **kwargs: Backend-specific options

        Returns:
            Dictionary of measurement counts
        """
        pass

    @abstractmethod
    def get_backend_info(self) -> dict[str, Any]:
        """Get comprehensive backend information."""
        pass

    @abstractmethod
    def get_capabilities(self) -> BackendCapabilities:
        """Get backend capabilities and characteristics."""
        pass

    @abstractmethod
    def can_simulate(self, circuit: QuantumCircuit, **kwargs: Any) -> tuple[bool, str]:
        """
        Check if backend can simulate the given circuit.

        Args:
            circuit: Quantum circuit to check
            **kwargs: Additional constraints

        Returns:
            (can_simulate, reason)
        """
        pass

    def get_performance_metrics(self) -> BackendPerformanceMetrics:
        """
        Get performance metrics for the backend.

        Returns:
            Performance metrics
        """
        # Default implementation - subclasses should override
        return BackendPerformanceMetrics(
            backend_name=self.get_backend_info().get("name", "unknown"),
            total_simulations=0,
            successful_simulations=0,
            failed_simulations=0,
            average_execution_time=0.0,
            min_execution_time=0.0,
            max_execution_time=0.0,
            average_memory_usage=0.0,
            last_simulation_time=0.0,
            uptime=0.0,
            error_rate=0.0,
        )

    def estimate_resources(self, circuit: QuantumCircuit, shots: int = 1000) -> dict[str, float]:
        """
        Estimate computational resources needed for simulation.

        Args:
            circuit: Quantum circuit to estimate
            shots: Number of measurement shots

        Returns:
            Resource estimates
        """
        # Default implementation - subclasses should override
        num_qubits = circuit.num_qubits

        # Basic memory estimate (state vector)
        memory_mb = (2**num_qubits) * 16 / (1024 * 1024)

        # Basic time estimate
        time_seconds = circuit.depth() * num_qubits * 0.001

        return {"memory_mb": memory_mb, "time_seconds": time_seconds, "cost_factor": 1.0}

    def get_optimization_recommendations(self, circuit: QuantumCircuit) -> list[str]:
        """
        Get optimization recommendations for the circuit.

        Args:
            circuit: Quantum circuit to analyze

        Returns:
            List of optimization recommendations
        """
        recommendations = []
        capabilities = self.get_capabilities()

        # Check for optimization hints
        if OptimizationHint.BENEFITS_FROM_GATE_FUSION in capabilities.optimization_hints:
            recommendations.append("Consider gate fusion for better performance")

        if OptimizationHint.BENEFITS_FROM_CIRCUIT_OPTIMIZATION in capabilities.optimization_hints:
            recommendations.append("Consider circuit optimization before simulation")

        # Check circuit properties
        if circuit.num_qubits > capabilities.typical_qubits:
            recommendations.append(
                f"Circuit has {circuit.num_qubits} qubits, which is larger "
                f"than typical for this backend ({capabilities.typical_qubits})"
            )

        if circuit.depth() > 100:
            recommendations.append("Consider circuit decomposition for better performance")

        return recommendations

    def supports_capability(self, capability: BackendCapability) -> bool:
        """
        Check if backend supports a specific capability.

        Args:
            capability: Capability to check

        Returns:
            True if capability is supported
        """
        capabilities = self.get_capabilities()
        return capability in capabilities.supported_capabilities

    def has_optimization_hint(self, hint: OptimizationHint) -> bool:
        """
        Check if backend has a specific optimization hint.

        Args:
            hint: Optimization hint to check

        Returns:
            True if hint is present
        """
        capabilities = self.get_capabilities()
        return hint in capabilities.optimization_hints

    def is_suitable_for_circuit(self, circuit: QuantumCircuit) -> tuple[bool, float]:
        """
        Check if backend is suitable for the circuit and return a suitability score.

        Args:
            circuit: Quantum circuit to check

        Returns:
            (is_suitable, suitability_score)
        """
        can_simulate, reason = self.can_simulate(circuit)
        if not can_simulate:
            return False, 0.0

        # Calculate suitability score based on circuit properties and backend capabilities
        capabilities = self.get_capabilities()
        score = 0.5  # Base score

        # Adjust based on qubit count
        if circuit.num_qubits <= capabilities.typical_qubits:
            score += 0.2
        elif circuit.num_qubits > capabilities.max_qubits:
            score -= 0.5

        # Adjust based on circuit depth
        if circuit.depth() <= 50:
            score += 0.1
        elif circuit.depth() > 200:
            score -= 0.2

        # Adjust based on backend ratings
        score += (capabilities.speed_rating + capabilities.stability_rating) * 0.1

        # Ensure score is in [0, 1] range
        score = max(0.0, min(1.0, score))

        return True, score


class EnhancedBackendWrapper:
    """
    Wrapper to enhance existing backends with the enhanced interface.

    This class wraps existing backend implementations to provide
    the enhanced interface without requiring changes to the original code.
    """

    def __init__(self, backend: Any, backend_name: str, capabilities: BackendCapabilities | None = None):
        """
        Initialize the wrapper.

        Args:
            backend: Original backend instance
            backend_name: Name of the backend
            capabilities: Backend capabilities (auto-detected if None)
        """
        self.backend = backend
        self.backend_name = backend_name
        self.logger = get_logger(f"enhanced.{backend_name}")

        # Performance tracking
        self._total_simulations = 0
        self._successful_simulations = 0
        self._failed_simulations = 0
        self._execution_times: list[float] = []
        self._memory_usages: list[float] = []
        self._start_time = time.time()
        self._last_simulation_time = 0.0

        # Set capabilities
        if capabilities is None:
            self._capabilities = self._detect_capabilities()
        else:
            self._capabilities = capabilities

    def _detect_capabilities(self) -> BackendCapabilities:
        """Detect backend capabilities automatically."""
        # Default capabilities - should be overridden for specific backends
        return BackendCapabilities(
            supported_capabilities=[BackendCapability.STATE_VECTOR_SIMULATION],
            optimization_hints=[],
            max_qubits=20,
            typical_qubits=15,
            memory_efficiency=0.5,
            speed_rating=0.5,
            accuracy_rating=0.9,
            stability_rating=0.8,
            hardware_requirements=["CPU"],
            estimated_cost_factor=1.0,
        )

    def simulate(self, circuit: QuantumCircuit, shots: int = 1000, **kwargs: Any) -> dict[str, int]:
        """Simulate quantum circuit with performance tracking."""
        start_time = time.time()
        start_memory = self._get_memory_usage()

        try:
            # Update statistics
            self._total_simulations += 1

            # Call original backend
            if hasattr(self.backend, "simulate"):
                result = self.backend.simulate(circuit, shots, **kwargs)
            else:
                # Try to call the backend directly
                result = self.backend(circuit, shots, **kwargs)

            # Update success statistics
            self._successful_simulations += 1

            # Record performance metrics
            execution_time = time.time() - start_time
            memory_usage = self._get_memory_usage() - start_memory

            self._execution_times.append(execution_time)
            self._memory_usages.append(memory_usage)
            self._last_simulation_time = time.time()

            self.logger.debug(f"Simulation completed in {execution_time:.4f}s")

            return cast(dict[str, int], result)

        except Exception as e:
            # Update failure statistics
            self._failed_simulations += 1
            self._last_simulation_time = time.time()

            self.logger.error(f"Simulation failed: {e}")
            raise

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil

            process = psutil.Process()
            memory_bytes = process.memory_info().rss
            return float(memory_bytes / (1024 * 1024))
        except ImportError:
            return 0.0

    def get_backend_info(self) -> dict[str, Any]:
        """Get comprehensive backend information."""
        info: dict[str, Any] = {
            "name": self.backend_name,
            "type": type(self.backend).__name__,
            "enhanced": True,
            "total_simulations": self._total_simulations,
            "successful_simulations": self._successful_simulations,
            "failed_simulations": self._failed_simulations,
        }

        # Add original backend info if available
        if hasattr(self.backend, "get_backend_info"):
            original_info = self.backend.get_backend_info()
            info.update(original_info)

        return info

    def get_capabilities(self) -> BackendCapabilities:
        """Get backend capabilities."""
        return self._capabilities

    def can_simulate(self, circuit: QuantumCircuit, **kwargs: Any) -> tuple[bool, str]:
        """Check if backend can simulate the given circuit."""
        # Basic checks
        if circuit.num_qubits > self._capabilities.max_qubits:
            return (
                False,
                f"Circuit has {circuit.num_qubits} qubits, backend supports max {self._capabilities.max_qubits}",
            )

        # Check if original backend has can_simulate method
        if hasattr(self.backend, "can_simulate"):
            return cast(
                tuple[bool, str],
                self.backend.can_simulate(circuit, **kwargs),
            )

        # Default to true if no specific constraints
        return True, "Can simulate"

    def get_performance_metrics(self) -> BackendPerformanceMetrics:
        """Get performance metrics for the backend."""
        uptime = time.time() - self._start_time

        # Calculate statistics
        avg_execution_time = sum(self._execution_times) / len(self._execution_times) if self._execution_times else 0.0
        min_execution_time = min(self._execution_times) if self._execution_times else 0.0
        max_execution_time = max(self._execution_times) if self._execution_times else 0.0

        avg_memory_usage = sum(self._memory_usages) / len(self._memory_usages) if self._memory_usages else 0.0

        # Calculate error rate
        error_rate = self._failed_simulations / self._total_simulations if self._total_simulations > 0 else 0.0

        return BackendPerformanceMetrics(
            backend_name=self.backend_name,
            total_simulations=self._total_simulations,
            successful_simulations=self._successful_simulations,
            failed_simulations=self._failed_simulations,
            average_execution_time=avg_execution_time,
            min_execution_time=min_execution_time,
            max_execution_time=max_execution_time,
            average_memory_usage=avg_memory_usage,
            last_simulation_time=self._last_simulation_time,
            uptime=uptime,
            error_rate=error_rate,
        )

    def estimate_resources(self, circuit: QuantumCircuit, shots: int = 1000) -> dict[str, float]:
        """Estimate computational resources needed for simulation."""
        # Get basic estimates
        estimates: dict[str, float] = {
            "memory_mb": (2**circuit.num_qubits) * 16 / (1024 * 1024),
            "time_seconds": circuit.depth() * circuit.num_qubits * 0.001,
            "cost_factor": self._capabilities.estimated_cost_factor,
        }

        # Adjust based on backend capabilities
        if BackendCapability.GPU_ACCELERATION in self._capabilities.supported_capabilities:
            estimates["time_seconds"] *= 0.5  # GPU is faster

        if BackendCapability.TENSOR_NETWORK in self._capabilities.supported_capabilities:
            # Tensor networks are more memory efficient
            estimates["memory_mb"] *= 0.3

        if BackendCapability.STABILIZER_SIMULATION in self._capabilities.supported_capabilities:
            # Stabilizer simulation is much more efficient
            estimates["memory_mb"] = circuit.num_qubits * 0.001
            estimates["time_seconds"] *= 0.1

        return estimates

    def get_optimization_recommendations(self, circuit: QuantumCircuit) -> list[str]:
        """Get optimization recommendations for the circuit."""
        recommendations = []

        # Get basic recommendations from capabilities
        if OptimizationHint.BENEFITS_FROM_GATE_FUSION in self._capabilities.optimization_hints:
            recommendations.append("Consider gate fusion for better performance")

        if OptimizationHint.BENEFITS_FROM_CIRCUIT_OPTIMIZATION in self._capabilities.optimization_hints:
            recommendations.append("Consider circuit optimization before simulation")

        # Check circuit properties
        if circuit.num_qubits > self._capabilities.typical_qubits:
            recommendations.append(
                f"Circuit has {circuit.num_qubits} qubits, which is larger "
                f"than typical for this backend ({self._capabilities.typical_qubits})"
            )

        if circuit.depth() > 100:
            recommendations.append("Consider circuit decomposition for better performance")

        return recommendations

    def supports_capability(self, capability: BackendCapability) -> bool:
        """Check if backend supports a specific capability."""
        return capability in self._capabilities.supported_capabilities

    def has_optimization_hint(self, hint: OptimizationHint) -> bool:
        """Check if backend has a specific optimization hint."""
        return hint in self._capabilities.optimization_hints

    def is_suitable_for_circuit(self, circuit: QuantumCircuit) -> tuple[bool, float]:
        """Check if backend is suitable for the circuit and return a suitability score."""
        can_simulate, reason = self.can_simulate(circuit)
        if not can_simulate:
            return False, 0.0

        # Calculate suitability score
        score = 0.5  # Base score

        # Adjust based on qubit count
        if circuit.num_qubits <= self._capabilities.typical_qubits:
            score += 0.2
        elif circuit.num_qubits > self._capabilities.max_qubits:
            score -= 0.5

        # Adjust based on circuit depth
        if circuit.depth() <= 50:
            score += 0.1
        elif circuit.depth() > 200:
            score -= 0.2

        # Adjust based on backend ratings
        score += (self._capabilities.speed_rating + self._capabilities.stability_rating) * 0.1

        # Ensure score is in [0, 1] range
        score = max(0.0, min(1.0, score))

        return True, score


def create_enhanced_backend(
    backend: Any, backend_name: str, capabilities: BackendCapabilities | None = None
) -> EnhancedBackendWrapper:
    """
    Create an enhanced backend wrapper.

    Args:
        backend: Original backend instance
        backend_name: Name of the backend
        capabilities: Backend capabilities (auto-detected if None)

    Returns:
        Enhanced backend wrapper
    """
    return EnhancedBackendWrapper(backend, backend_name, capabilities)
