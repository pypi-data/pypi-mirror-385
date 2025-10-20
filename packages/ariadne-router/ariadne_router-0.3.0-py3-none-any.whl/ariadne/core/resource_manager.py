"""
Resource management system for Ariadne.

This module provides system resource monitoring and management to ensure
simulations don't exceed available resources.
"""

from __future__ import annotations

import platform
import threading
import time
from dataclasses import dataclass

try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from qiskit import QuantumCircuit

from .error_handling import DependencyError, ResourceExhaustionError


@dataclass
class SystemResources:
    """System resource information."""

    available_memory_mb: float
    total_memory_mb: float
    available_cpu_cores: int
    total_cpu_cores: int
    gpu_memory_mb: float | None = None
    gpu_available: bool = False
    platform: str = ""
    architecture: str = ""

    @property
    def memory_usage_percent(self) -> float:
        """Calculate memory usage percentage."""
        if self.total_memory_mb > 0:
            return ((self.total_memory_mb - self.available_memory_mb) / self.total_memory_mb) * 100
        return 0.0


@dataclass
class ResourceRequirements:
    """Resource requirements for a circuit simulation."""

    memory_mb: float
    cpu_cores: int
    estimated_time_seconds: float
    backend: str


class ResourceError(Exception):
    """Raised when resource management fails."""

    pass


class ResourceManager:
    """
    Singleton resource manager for monitoring and managing system resources.

    This class provides methods to check if the system can handle specific
    circuit simulations and tracks resource usage.
    """

    _instance: ResourceManager | None = None
    _lock = threading.Lock()

    def __new__(cls) -> ResourceManager:
        """Implement singleton pattern."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self) -> None:
        """Initialize the resource manager."""
        if self._initialized:
            return

        self._initialized: bool = False

        if not PSUTIL_AVAILABLE:
            raise DependencyError("psutil", "Resource management requires psutil. Install with: pip install psutil")

        self._initialized = True
        self._update_resources()
        self._last_update = time.time()
        self._update_interval = 5.0  # Update every 5 seconds

    def _update_resources(self) -> None:
        """Update system resource information."""
        try:
            # Memory information
            memory = psutil.virtual_memory()
            available_memory_mb = memory.available / (1024 * 1024)
            total_memory_mb = memory.total / (1024 * 1024)

            # CPU information
            cpu_count = psutil.cpu_count() or 1  # Default to 1 if psutil returns None
            available_cpu_cores = cpu_count  # Simplified - could check load

            # GPU information
            gpu_memory_mb, gpu_available = self._get_gpu_info()

            # Platform information
            system_platform = platform.system()
            architecture = platform.machine()

            self.resources = SystemResources(
                available_memory_mb=available_memory_mb,
                total_memory_mb=total_memory_mb,
                available_cpu_cores=available_cpu_cores,
                total_cpu_cores=cpu_count,
                gpu_memory_mb=gpu_memory_mb,
                gpu_available=gpu_available,
                platform=system_platform,
                architecture=architecture,
            )

        except Exception as exc:
            raise ResourceError(f"Failed to update system resources: {exc}") from exc

    def _get_gpu_info(self) -> tuple[float | None, bool]:
        """Get GPU information if available."""
        try:
            # Try CUDA
            try:
                import cupy

                if cupy.cuda.runtime.getDeviceCount() > 0:
                    device = cupy.cuda.Device()
                    gpu_memory_mb = device.mem_info[0] / (1024 * 1024)
                    return gpu_memory_mb, True
            except (ImportError, Exception):
                pass

            # Try Apple Silicon Metal
            if platform.system() == "Darwin" and platform.machine() in ["arm64", "aarch64"]:
                # Apple Silicon has unified memory, use system memory * 0.8 as estimate
                memory = psutil.virtual_memory()
                gpu_memory_mb = memory.total * 0.8 / (1024 * 1024)
                return gpu_memory_mb, True

            return None, False

        except Exception:
            return None, False

    def _ensure_fresh_resources(self) -> None:
        """Ensure resource information is up to date."""
        current_time = time.time()
        if current_time - self._last_update > self._update_interval:
            self._update_resources()
            self._last_update = current_time

    def get_resources(self) -> SystemResources:
        """
        Get current system resources.

        Returns:
            Current system resources
        """
        self._ensure_fresh_resources()
        return self.resources

    def estimate_circuit_requirements(self, circuit: QuantumCircuit, backend: str) -> ResourceRequirements:
        """
        Estimate resource requirements for circuit simulation.

        Args:
            circuit: Quantum circuit to simulate
            backend: Backend to use for simulation

        Returns:
            Estimated resource requirements
        """
        num_qubits = circuit.num_qubits
        depth = circuit.depth()

        # Memory estimation (simplified)
        if backend == "stim":
            # Clifford circuits use polynomial memory
            memory_mb = max(1.0, (num_qubits**2) * 0.001)
        elif backend in ["tensor_network", "mps"]:
            # Tensor networks and MPS are memory efficient
            memory_mb = max(1.0, (2 ** min(num_qubits, 20)) * 0.0001)
        else:
            # Statevector simulation needs exponential memory
            memory_mb = max(1.0, (2**num_qubits) * 16 / (1024 * 1024))

        # Add safety margin
        memory_mb *= 1.5

        # CPU estimation
        cpu_cores = min(4, max(1, num_qubits // 5))

        # Time estimation (very rough heuristic)
        if backend == "stim":
            time_seconds = max(0.001, (num_qubits**2) * depth * 0.000001)
        elif backend in ["cuda", "metal"]:
            time_seconds = max(0.001, (2 ** min(num_qubits, 25)) * depth * 0.0000001)
        else:
            time_seconds = max(0.01, (2 ** min(num_qubits, 20)) * depth * 0.000001)

        return ResourceRequirements(
            memory_mb=memory_mb,
            cpu_cores=cpu_cores,
            estimated_time_seconds=time_seconds,
            backend=backend,
        )

    def can_handle_circuit(self, circuit: QuantumCircuit, backend: str) -> tuple[bool, str]:
        """
        Check if system can handle circuit simulation.

        Args:
            circuit: Quantum circuit to simulate
            backend: Backend to use for simulation

        Returns:
            Tuple of (can_handle, reason)
        """
        try:
            self._ensure_fresh_resources()
            requirements = self.estimate_circuit_requirements(circuit, backend)

            # Check memory
            if requirements.memory_mb > self.resources.available_memory_mb * 0.8:  # Leave 20% margin
                return False, (
                    f"Insufficient memory: need {requirements.memory_mb:.1f}MB, "
                    f"available {self.resources.available_memory_mb:.1f}MB"
                )

            # Check CPU
            if requirements.cpu_cores > self.resources.available_cpu_cores:
                return False, (
                    f"Insufficient CPU cores: need {requirements.cpu_cores}, "
                    f"available {self.resources.available_cpu_cores}"
                )

            # Check GPU requirements
            if backend in ["cuda", "metal"] and not self.resources.gpu_available:
                return False, f"Backend '{backend}' requires GPU but none available"

            if backend in ["cuda", "metal"] and self.resources.gpu_memory_mb:
                if requirements.memory_mb > self.resources.gpu_memory_mb * 0.8:
                    return False, (
                        f"Insufficient GPU memory: need {requirements.memory_mb:.1f}MB, "
                        f"available {self.resources.gpu_memory_mb:.1f}MB"
                    )

            return True, "Resources sufficient"

        except Exception as e:
            return False, f"Resource check failed: {e}"

    def reserve_resources(self, circuit: QuantumCircuit, backend: str) -> ResourceRequirements:
        """
        Reserve resources for circuit simulation.

        Args:
            circuit: Quantum circuit to simulate
            backend: Backend to use for simulation

        Returns:
            Reserved resource requirements

        Raises:
            ResourceExhaustionError: If insufficient resources available
        """
        can_handle, reason = self.can_handle_circuit(circuit, backend)
        if not can_handle:
            raise ResourceExhaustionError("memory", 0, self.resources.available_memory_mb)

        requirements = self.estimate_circuit_requirements(circuit, backend)

        # Update available resources (simplified)
        self.resources.available_memory_mb -= requirements.memory_mb
        self.resources.available_cpu_cores -= requirements.cpu_cores

        return requirements

    def release_resources(self, requirements: ResourceRequirements) -> None:
        """
        Release previously reserved resources.

        Args:
            requirements: Resource requirements to release
        """
        self.resources.available_memory_mb += requirements.memory_mb
        self.resources.available_cpu_cores += requirements.cpu_cores

        # Ensure we don't exceed total resources
        self.resources.available_memory_mb = min(self.resources.available_memory_mb, self.resources.total_memory_mb)
        self.resources.available_cpu_cores = min(self.resources.available_cpu_cores, self.resources.total_cpu_cores)

    def get_recommendations(self, circuit: QuantumCircuit) -> list[str]:
        """
        Get recommendations for circuit simulation.

        Args:
            circuit: Quantum circuit to analyze

        Returns:
            List of recommendations
        """
        recommendations = []
        num_qubits = circuit.num_qubits
        depth = circuit.depth()

        # Memory recommendations
        if num_qubits > 25:
            recommendations.append("Consider using tensor network or MPS backend for large circuits")

        # Backend recommendations
        if depth > 100 and num_qubits > 15:
            recommendations.append("Deep circuits may benefit from GPU acceleration if available")

        # System recommendations
        if self.resources.memory_usage_percent > 80:
            recommendations.append("System memory usage is high, consider closing other applications")

        if self.resources.available_cpu_cores < 2:
            recommendations.append("Limited CPU cores available, simulation may be slow")

        return recommendations


# Global resource manager instance
_global_resource_manager: ResourceManager | None = None


def get_resource_manager() -> ResourceManager:
    """Get the global resource manager instance."""
    global _global_resource_manager
    if _global_resource_manager is None:
        _global_resource_manager = ResourceManager()
    return _global_resource_manager


def check_circuit_feasibility(circuit: QuantumCircuit, backend: str) -> tuple[bool, str]:
    """
    Check if circuit simulation is feasible with current resources.

    Args:
        circuit: Quantum circuit to check
        backend: Backend to use

    Returns:
        Tuple of (feasible, reason)
    """
    manager = get_resource_manager()
    return manager.can_handle_circuit(circuit, backend)
