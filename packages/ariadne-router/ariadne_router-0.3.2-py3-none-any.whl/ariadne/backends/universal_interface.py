"""
Universal Backend Interface for Ariadne

This module provides a unified interface for all quantum simulation backends,
enabling seamless integration and switching between different backend types
while maintaining consistent APIs and performance monitoring.
"""

from __future__ import annotations

import importlib.util
import warnings
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any, cast

from qiskit import QuantumCircuit


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


@dataclass
class BackendMetrics:
    """Performance and capability metrics for a backend, including dynamic hardware metrics."""

    max_qubits: int
    typical_qubits: int
    memory_efficiency: float  # 0-1 scale
    speed_rating: float  # 0-1 scale
    accuracy_rating: float  # 0-1 scale
    stability_rating: float  # 1-1 scale
    capabilities: list[BackendCapability]
    hardware_requirements: list[str]
    estimated_cost_factor: float  # Relative computational cost

    # Dynamic Quantum Computing Metrics
    gate_times: dict[str, float]  # Gate name to time in seconds (e.g., {'rz': 1e-9})
    error_rates: dict[str, float]  # Error type to rate (e.g., {'single_qubit': 1e-3})
    connectivity_map: list[tuple[int, int]] | None  # List of connected qubit pairs


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
    additional_info: dict[str, Any] | None = None


class UniversalBackend(ABC):
    """Abstract base class for all quantum simulation backends."""

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
    def get_capabilities(self) -> list[BackendCapability]:
        """Get list of supported capabilities."""
        pass

    @abstractmethod
    def get_metrics(self) -> BackendMetrics:
        """Get performance and capability metrics."""
        pass

    @abstractmethod
    def can_simulate(self, circuit: QuantumCircuit, **kwargs: Any) -> tuple[bool, str]:
        """
        Check if backend can simulate the given circuit.

        Returns:
            (can_simulate, reason)
        """
        pass

    def estimate_resources(self, circuit: QuantumCircuit) -> dict[str, float]:
        """Estimate computational resources needed."""
        return {
            "memory_mb": self._estimate_memory_mb(circuit),
            "time_seconds": self._estimate_time_seconds(circuit),
            "cost_factor": 1.0,
        }

    def _estimate_memory_mb(self, circuit: QuantumCircuit) -> float:
        """Default memory estimation."""
        # State vector simulation memory estimate
        num_qubits = cast(int, getattr(circuit, "num_qubits", 0))
        memory_bytes = float(2**num_qubits) * 16.0
        return memory_bytes / (1024 * 1024)

    def _estimate_time_seconds(self, circuit: QuantumCircuit) -> float:
        """Default time estimation."""
        # Simple heuristic based on circuit size
        num_qubits = cast(int, getattr(circuit, "num_qubits", 0))
        depth_attr = getattr(circuit, "depth", None)
        depth_callable: Callable[[], int] | None = cast(Callable[[], int], depth_attr) if callable(depth_attr) else None
        depth = depth_callable() if depth_callable else 0
        return float(num_qubits) * float(depth) * 0.001


class BackendManager:
    """Manages all available quantum simulation backends."""

    def __init__(self) -> None:
        self.backends: dict[str, type[UniversalBackend]] = {}
        self.backend_instances: dict[str, UniversalBackend] = {}
        self._register_default_backends()

    def _register_default_backends(self) -> None:
        """Register all available backends."""
        if importlib.util.find_spec("ariadne.backends.qulacs_backend") is not None:
            self.register_backend("qulacs", QulacsUniversalWrapper)
        if importlib.util.find_spec("ariadne.backends.pennylane_backend") is not None:
            self.register_backend("pennylane", PennyLaneUniversalWrapper)
        if importlib.util.find_spec("ariadne.backends.cirq_backend") is not None:
            self.register_backend("cirq", CirqUniversalWrapper)
        if importlib.util.find_spec("ariadne.backends.intel_qs_backend") is not None:
            self.register_backend("intel_qs", IntelQSUniversalWrapper)

        # Always available fallback
        self.register_backend("qiskit", QiskitUniversalWrapper)

    def register_backend(self, name: str, backend_class: type[UniversalBackend]) -> None:
        """Register a new backend."""
        self.backends[name] = backend_class

    def get_backend(self, name: str, **kwargs: Any) -> UniversalBackend | None:
        """Get backend instance by name."""
        if name not in self.backends:
            return None

        # Create instance if not cached
        if name not in self.backend_instances:
            try:
                self.backend_instances[name] = self.backends[name](**kwargs)
            except Exception as e:
                warnings.warn(f"Failed to create backend {name}: {e}", stacklevel=2)
                return None

        return self.backend_instances[name]

    def list_available_backends(self) -> list[str]:
        """List all available backend names."""
        available: list[str] = []
        for name, backend_class in self.backends.items():
            try:
                # Try to create instance to check availability
                instance = backend_class()
                if instance:
                    available.append(name)
            except Exception:
                pass
        return available

    def get_best_backend_for_circuit(self, circuit: QuantumCircuit, criteria: str = "speed") -> str | None:
        """Find best backend for given circuit and criteria."""
        available_backends = self.list_available_backends()

        best_backend: str | None = None
        best_score = -1.0

        for backend_name in available_backends:
            backend = self.get_backend(backend_name)
            if not backend:
                continue

            can_sim, reason = backend.can_simulate(circuit)
            if not can_sim:
                continue

            metrics = backend.get_metrics()

            # Score based on criteria
            if criteria == "speed":
                score = metrics.speed_rating
            elif criteria == "accuracy":
                score = metrics.accuracy_rating
            elif criteria == "memory":
                score = metrics.memory_efficiency
            elif criteria == "stability":
                score = metrics.stability_rating
            else:
                score = (
                    metrics.speed_rating
                    + metrics.accuracy_rating
                    + metrics.memory_efficiency
                    + metrics.stability_rating
                ) / 4

            if score > best_score:
                best_score = score
                best_backend = backend_name

        return best_backend

    def benchmark_all_backends(self, circuit: QuantumCircuit, shots: int = 1000) -> dict[str, dict[str, Any]]:
        """Benchmark all available backends on given circuit."""
        import time

        results: dict[str, dict[str, Any]] = {}
        available_backends = self.list_available_backends()

        for backend_name in available_backends:
            backend = self.get_backend(backend_name)
            if not backend:
                continue

            can_sim, reason = backend.can_simulate(circuit)
            if not can_sim:
                results[backend_name] = {"success": False, "reason": reason}
                continue

            try:
                start_time = time.time()
                counts = backend.simulate(circuit, shots)
                execution_time = time.time() - start_time

                results[backend_name] = {
                    "success": True,
                    "execution_time": execution_time,
                    "counts_sample": dict(list(counts.items())[:3]),
                    "total_counts": sum(counts.values()),
                    "backend_info": backend.get_backend_info(),
                }

            except Exception as e:
                results[backend_name] = {"success": False, "error": str(e)}

        return results


# Universal wrappers for existing backends


class QulacsUniversalWrapper(UniversalBackend):
    """Universal wrapper for Qulacs backend."""

    def __init__(self, **kwargs: Any):
        from .qulacs_backend import QulacsBackend

        self.backend = QulacsBackend(**kwargs)

    def simulate(self, circuit: QuantumCircuit, shots: int = 1000, **kwargs: Any) -> dict[str, int]:
        return self.backend.simulate(circuit, shots, **kwargs)

    def get_backend_info(self) -> dict[str, Any]:
        return self.backend.get_backend_info()

    def get_capabilities(self) -> list[BackendCapability]:
        caps = [BackendCapability.STATE_VECTOR_SIMULATION]
        if self.backend.gpu_available:
            caps.append(BackendCapability.GPU_ACCELERATION)
        return caps

    def get_metrics(self) -> BackendMetrics:
        return BackendMetrics(
            max_qubits=25,
            typical_qubits=20,
            memory_efficiency=0.8,
            speed_rating=0.9,
            accuracy_rating=0.95,
            stability_rating=0.85,
            capabilities=self.get_capabilities(),
            hardware_requirements=["CUDA" if self.backend.gpu_available else "CPU"],
            estimated_cost_factor=0.3 if self.backend.gpu_available else 1.0,
            # Dynamic Metrics (Simulation Defaults)
            gate_times={"single_qubit": 1e-9, "two_qubit": 1e-8},
            error_rates={"single_qubit": 1e-10, "two_qubit": 1e-9},
            connectivity_map=None,
        )

    def can_simulate(self, circuit: QuantumCircuit, **kwargs: Any) -> tuple[bool, str]:
        return self.backend.can_simulate(circuit, **kwargs)


class PennyLaneUniversalWrapper(UniversalBackend):
    """Universal wrapper for PennyLane backend."""

    def __init__(self, **kwargs: Any):
        from .pennylane_backend import PennyLaneBackend

        self.backend = PennyLaneBackend(**kwargs)

    def simulate(self, circuit: QuantumCircuit, shots: int = 1000, **kwargs: Any) -> dict[str, int]:
        return self.backend.simulate(circuit, shots, **kwargs)

    def get_backend_info(self) -> dict[str, Any]:
        return self.backend.get_backend_info()

    def get_capabilities(self) -> list[BackendCapability]:
        caps = [
            BackendCapability.STATE_VECTOR_SIMULATION,
            BackendCapability.QUANTUM_ML,
            BackendCapability.PARAMETRIC_CIRCUITS,
        ]
        if self.backend.ml_framework:
            caps.append(BackendCapability.GPU_ACCELERATION)
        return caps

    def get_metrics(self) -> BackendMetrics:
        return BackendMetrics(
            max_qubits=20,
            typical_qubits=15,
            memory_efficiency=0.7,
            speed_rating=0.75,
            accuracy_rating=0.9,
            stability_rating=0.9,
            capabilities=self.get_capabilities(),
            hardware_requirements=["CPU", "GPU (optional)"],
            estimated_cost_factor=0.8,
            # Dynamic Metrics (Simulation Defaults)
            gate_times={"single_qubit": 1e-9, "two_qubit": 1e-8},
            error_rates={"single_qubit": 1e-10, "two_qubit": 1e-9},
            connectivity_map=None,
        )

    def can_simulate(self, circuit: QuantumCircuit, **kwargs: Any) -> tuple[bool, str]:
        if circuit.num_qubits > 20:
            return False, "Too many qubits for PennyLane backend"
        return True, "Can simulate"


class CirqUniversalWrapper(UniversalBackend):
    """Universal wrapper for Cirq backend."""

    def __init__(self, **kwargs: Any):
        from .cirq_backend import CirqBackend

        self.backend = CirqBackend(**kwargs)

    def simulate(self, circuit: QuantumCircuit, shots: int = 1000, **kwargs: Any) -> dict[str, int]:
        return self.backend.simulate(circuit, shots, **kwargs)

    def get_backend_info(self) -> dict[str, Any]:
        return self.backend.get_backend_info()

    def get_capabilities(self) -> list[BackendCapability]:
        caps = [BackendCapability.STATE_VECTOR_SIMULATION]
        if self.backend.simulator_type == "density_matrix":
            caps.append(BackendCapability.DENSITY_MATRIX_SIMULATION)
        if self.backend.noise_model:
            caps.append(BackendCapability.NOISE_MODELING)
        if self.backend.device:
            caps.append(BackendCapability.HARDWARE_INTEGRATION)
        return caps

    def get_metrics(self) -> BackendMetrics:
        return BackendMetrics(
            max_qubits=22,
            typical_qubits=18,
            memory_efficiency=0.75,
            speed_rating=0.8,
            accuracy_rating=0.95,
            stability_rating=0.85,
            capabilities=self.get_capabilities(),
            hardware_requirements=["CPU"],
            estimated_cost_factor=1.2,
            # Dynamic Metrics (Simulation Defaults)
            gate_times={"single_qubit": 5e-9, "two_qubit": 5e-8},
            error_rates={"single_qubit": 1e-4, "two_qubit": 1e-3},
            connectivity_map=None,
        )

    def can_simulate(self, circuit: QuantumCircuit, **kwargs: Any) -> tuple[bool, str]:
        if circuit.num_qubits > 22:
            return False, "Too many qubits for Cirq backend"
        return True, "Can simulate"


class IntelQSUniversalWrapper(UniversalBackend):
    """Universal wrapper for Intel Quantum Simulator backend."""

    def __init__(self, **kwargs: Any):
        from .intel_qs_backend import IntelQuantumSimulatorBackend

        self.backend = IntelQuantumSimulatorBackend(**kwargs)

    def simulate(self, circuit: QuantumCircuit, shots: int = 1000, **kwargs: Any) -> dict[str, int]:
        return self.backend.simulate(circuit, shots, **kwargs)

    def get_backend_info(self) -> dict[str, Any]:
        return self.backend.get_backend_info()

    def get_capabilities(self) -> list[BackendCapability]:
        caps = [BackendCapability.STATE_VECTOR_SIMULATION]
        if self.backend.enable_distributed:
            caps.append(BackendCapability.DISTRIBUTED_COMPUTING)
        return caps

    def get_metrics(self) -> BackendMetrics:
        return BackendMetrics(
            max_qubits=30,
            typical_qubits=25,
            memory_efficiency=0.85,
            speed_rating=0.95,
            accuracy_rating=0.9,
            stability_rating=0.8,
            capabilities=self.get_capabilities(),
            hardware_requirements=["Intel CPU", "Intel MKL (optional)"],
            estimated_cost_factor=0.6,
            # Dynamic Metrics (Simulation Defaults)
            gate_times={"single_qubit": 1e-9, "two_qubit": 1e-8},
            error_rates={"single_qubit": 1e-10, "two_qubit": 1e-9},
            connectivity_map=None,
        )

    def can_simulate(self, circuit: QuantumCircuit, **kwargs: Any) -> tuple[bool, str]:
        return self.backend.can_simulate(circuit, **kwargs)


class QiskitUniversalWrapper(UniversalBackend):
    """Universal wrapper for Qiskit backend (fallback)."""

    def __init__(self, **kwargs: Any):
        pass  # Always available

    def simulate(self, circuit: QuantumCircuit, shots: int = 1000, **kwargs: Any) -> dict[str, int]:
        try:
            from qiskit.providers.basic_provider import BasicProvider

            provider = BasicProvider()
            backend = provider.get_backend("basic_simulator")
            job = backend.run(circuit, shots=shots)
            counts = job.result().get_counts()

            return {str(k): v for k, v in counts.items()}

        except ImportError as err:
            raise RuntimeError("Qiskit BasicProvider not available") from err

    def get_backend_info(self) -> dict[str, Any]:
        return {"name": "qiskit", "type": "fallback", "always_available": True}

    def get_capabilities(self) -> list[BackendCapability]:
        return [BackendCapability.STATE_VECTOR_SIMULATION]

    def get_metrics(self) -> BackendMetrics:
        return BackendMetrics(
            max_qubits=24,
            typical_qubits=12,
            memory_efficiency=0.6,
            speed_rating=0.5,
            accuracy_rating=0.85,
            stability_rating=0.95,
            capabilities=self.get_capabilities(),
            hardware_requirements=["CPU"],
            estimated_cost_factor=2.0,
            # Dynamic Metrics (Simulation Defaults)
            gate_times={"single_qubit": 1e-8, "two_qubit": 1e-7},
            error_rates={"single_qubit": 1e-3, "two_qubit": 1e-2},
            connectivity_map=None,
        )

    def can_simulate(self, circuit: QuantumCircuit, **kwargs: Any) -> tuple[bool, str]:
        if circuit.num_qubits > 24:
            return False, "Too many qubits for Qiskit basic simulator"
        return True, "Can simulate"


# Global backend manager instance
_backend_manager: BackendManager | None = None


def get_backend_manager() -> BackendManager:
    """Get global backend manager instance."""
    global _backend_manager
    if _backend_manager is None:
        _backend_manager = BackendManager()
    return _backend_manager


def list_backends() -> list[str]:
    """List all available backends."""
    return get_backend_manager().list_available_backends()


def get_backend(name: str, **kwargs: Any) -> UniversalBackend | None:
    """Get backend by name."""
    return get_backend_manager().get_backend(name, **kwargs)


def simulate_with_best_backend(
    circuit: QuantumCircuit,
    shots: int = 1000,
    criteria: str = "speed",
    **kwargs: Any,
) -> tuple[dict[str, int], str]:
    """
    Simulate circuit with automatically selected best backend.

    Args:
        circuit: Circuit to simulate
        shots: Number of shots
        criteria: Selection criteria ('speed', 'accuracy', 'memory', 'stability')
        **kwargs: Backend-specific options

    Returns:
        (counts, backend_name)
    """
    manager = get_backend_manager()
    best_backend_name = manager.get_best_backend_for_circuit(circuit, criteria)

    if not best_backend_name:
        raise RuntimeError("No suitable backend found for circuit")

    backend = manager.get_backend(best_backend_name, **kwargs)
    if backend is None:
        raise RuntimeError(f"Backend {best_backend_name} could not be initialized")

    counts = backend.simulate(circuit, shots, **kwargs)

    return counts, best_backend_name


def benchmark_circuit(circuit: QuantumCircuit, shots: int = 1000) -> dict[str, dict[str, Any]]:
    """Benchmark circuit on all available backends."""
    return get_backend_manager().benchmark_all_backends(circuit, shots)
