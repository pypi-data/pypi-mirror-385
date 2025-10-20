"""Intelligent routing across the available quantum circuit simulators."""

from __future__ import annotations

import warnings
from time import perf_counter
from typing import Any

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from .backends.tensor_network_backend import TensorNetworkBackend
from .core import (
    BackendUnavailableError,
    CircuitTooLargeError,
    ResourceExhaustionError,
    SimulationError,
    check_circuit_feasibility,
    get_logger,
    get_resource_manager,
)
from .route.enhanced_router import EnhancedQuantumRouter, RouterType
from .types import BackendType, RoutingDecision, SimulationResult

CUDABackend: type[Any] | None = None


def is_cuda_available() -> bool:
    return False


try:  # pragma: no cover - import guard for optional CUDA support
    from .backends.cuda_backend import (
        CUDABackend as _RuntimeCUDABackend,
    )
    from .backends.cuda_backend import (
        is_cuda_available as _is_cuda_available,
    )

    CUDABackend = _RuntimeCUDABackend
    is_cuda_available = _is_cuda_available
except ImportError:  # pragma: no cover - executed when dependencies missing
    pass


MetalBackend: type[Any] | None = None


def is_metal_available() -> bool:
    return False


try:  # pragma: no cover - import guard for optional Metal support
    from .backends.metal_backend import (
        MetalBackend as _RuntimeMetalBackend,
    )
    from .backends.metal_backend import (
        is_metal_available as _is_metal_available,
    )

    MetalBackend = _RuntimeMetalBackend
    is_metal_available = _is_metal_available
except ImportError:  # pragma: no cover - executed when dependencies missing
    pass


# Global state for Tensor Network Backend instance
_TENSOR_BACKEND: TensorNetworkBackend | None = None

# ------------------------------------------------------------------
# Analysis helpers


def _apple_silicon_boost() -> float:
    import platform

    if platform.system() == "Darwin" and platform.machine() in {"arm", "arm64"}:
        # More realistic boost factor based on actual benchmarks
        return 1.5
    return 1.0


# ------------------------------------------------------------------
# Simulation helpers


def _simulate_stim(circuit: QuantumCircuit, shots: int) -> dict[str, int]:
    logger = get_logger("router")

    try:
        from .converters import convert_qiskit_to_stim, simulate_stim_circuit
    except ImportError as exc:
        raise BackendUnavailableError("stim", "Stim is not installed") from exc

    try:
        stim_circuit, measurement_map = convert_qiskit_to_stim(circuit)
        num_clbits = circuit.num_clbits or circuit.num_qubits
        return simulate_stim_circuit(stim_circuit, measurement_map, shots, num_clbits)
    except Exception as exc:
        logger.log_simulation_error(exc, backend="stim")
        raise SimulationError(f"Stim simulation failed: {exc}", backend="stim") from exc


def _simulate_qiskit(circuit: QuantumCircuit, shots: int) -> dict[str, int]:
    logger = get_logger("router")

    try:
        from qiskit.providers.basic_provider import BasicProvider
    except ImportError as exc:  # pragma: no cover - depends on qiskit extras
        raise BackendUnavailableError("qiskit", "Qiskit provider not available") from exc

    try:
        provider = BasicProvider()
        backend = provider.get_backend("basic_simulator")
        job = backend.run(circuit, shots=shots)
        counts = job.result().get_counts()
        return {str(key): value for key, value in counts.items()}
    except Exception as exc:
        logger.log_simulation_error(exc, backend="qiskit")
        raise SimulationError(f"Qiskit simulation failed: {exc}", backend="qiskit") from exc


def _real_tensor_network_simulation(circuit: QuantumCircuit, shots: int) -> dict[str, int]:
    global _TENSOR_BACKEND
    if _TENSOR_BACKEND is None:
        _TENSOR_BACKEND = TensorNetworkBackend()
    return _TENSOR_BACKEND.simulate(circuit, shots)


def _simulate_tensor_network(circuit: QuantumCircuit, shots: int) -> dict[str, int]:
    """Simulate ``circuit`` using the tensor network backend."""
    logger = get_logger("router")

    try:
        return _real_tensor_network_simulation(circuit, shots)
    except ImportError as exc:
        raise BackendUnavailableError("tensor_network", "Tensor network dependencies are not installed") from exc
    except Exception as exc:  # pragma: no cover - graceful fallback path
        logger.log_backend_unavailable("tensor_network", str(exc))
        warnings.warn(
            f"Tensor network simulation failed, falling back to Qiskit: {exc}",
            RuntimeWarning,
            stacklevel=2,
        )
        return _simulate_qiskit(circuit, shots)


def _simulate_jax_metal(circuit: QuantumCircuit, shots: int) -> dict[str, int]:
    """Simulate using the new hybrid Metal backend for Apple Silicon."""
    logger = get_logger("router")

    try:
        from .backends.metal_backend import MetalBackend

        # Use our new MetalBackend with hybrid approach
        backend = MetalBackend(allow_cpu_fallback=True)
        result = backend.simulate(circuit, shots)

        # Log backend mode for debugging
        logger.debug(f"Metal backend executed in mode: {backend.backend_mode}")

        # Check if Metal actually accelerated or fell back to CPU
        if backend.backend_mode == "cpu":
            logger.debug("Metal backend fell back to CPU mode")

        return result

    except ImportError as exc:
        logger.log_backend_unavailable("metal", str(exc))
        raise BackendUnavailableError("metal", "Metal backend dependencies not available") from exc
    except Exception as exc:
        logger.log_simulation_error(exc, backend="metal")
        raise SimulationError(f"Metal backend execution failed: {exc}", backend="metal") from exc


def _simulate_ddsim(circuit: QuantumCircuit, shots: int) -> dict[str, int]:
    logger = get_logger("router")

    try:
        import mqt.ddsim as ddsim
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise BackendUnavailableError("ddsim", "MQT DDSIM not installed") from exc

    try:
        simulator = ddsim.DDSIMProvider().get_backend("qasm_simulator")
        job = simulator.run(circuit, shots=shots)
        counts = job.result().get_counts()
        return {str(key): value for key, value in counts.items()}
    except Exception as exc:
        logger.log_simulation_error(exc, backend="ddsim")
        raise SimulationError(f"DDSIM simulation failed: {exc}", backend="ddsim") from exc


def _simulate_cirq(circuit: QuantumCircuit, shots: int) -> dict[str, int]:
    """Simulate using the Cirq backend wrapper if available."""
    logger = get_logger("router")

    try:
        from .backends.cirq_backend import CirqBackend
    except ImportError as exc:
        raise BackendUnavailableError("cirq", "Cirq not installed") from exc

    try:
        backend = CirqBackend()
        return backend.simulate(circuit, shots)
    except Exception as exc:
        logger.log_simulation_error(exc, backend="cirq")
        raise SimulationError(f"Cirq simulation failed: {exc}", backend="cirq") from exc


def _simulate_pennylane(circuit: QuantumCircuit, shots: int) -> dict[str, int]:
    """Simulate using the PennyLane backend wrapper if available."""
    logger = get_logger("router")

    try:
        from .backends.pennylane_backend import PennyLaneBackend
    except ImportError as exc:
        raise BackendUnavailableError("pennylane", "PennyLane not installed") from exc

    try:
        backend = PennyLaneBackend()
        return backend.simulate(circuit, shots)
    except Exception as exc:
        logger.log_simulation_error(exc, backend="pennylane")
        raise SimulationError(f"PennyLane simulation failed: {exc}", backend="pennylane") from exc


def _simulate_qulacs(circuit: QuantumCircuit, shots: int) -> dict[str, int]:
    """Simulate using the Qulacs backend wrapper if available."""
    logger = get_logger("router")

    try:
        from .backends.qulacs_backend import QulacsBackend
    except ImportError as exc:
        raise BackendUnavailableError("qulacs", "Qulacs not installed") from exc

    try:
        backend = QulacsBackend()
        return backend.simulate(circuit, shots)
    except Exception as exc:
        logger.log_simulation_error(exc, backend="qulacs")
        raise SimulationError(f"Qulacs simulation failed: {exc}", backend="qulacs") from exc


def _simulate_pyquil(circuit: QuantumCircuit, shots: int) -> dict[str, int]:
    """Simulate using the PyQuil backend (skeleton, falls back to Qiskit)."""
    logger = get_logger("router")

    try:
        from .backends.experimental.pyquil_backend import PyQuilBackend
    except ImportError as exc:
        raise BackendUnavailableError("pyquil", "PyQuil not installed") from exc

    try:
        backend = PyQuilBackend()
        return backend.simulate(circuit, shots)
    except Exception as exc:
        logger.log_simulation_error(exc, backend="pyquil")
        raise SimulationError(f"PyQuil simulation failed: {exc}", backend="pyquil") from exc


def _simulate_braket(circuit: QuantumCircuit, shots: int) -> dict[str, int]:
    """Simulate using the Braket backend (skeleton, falls back to Qiskit)."""
    logger = get_logger("router")

    try:
        from .backends.experimental.braket_backend import BraketBackend
    except ImportError as exc:
        raise BackendUnavailableError("braket", "Braket SDK not installed") from exc

    try:
        backend = BraketBackend()
        return backend.simulate(circuit, shots)
    except Exception as exc:
        logger.log_simulation_error(exc, backend="braket")
        raise SimulationError(f"Braket simulation failed: {exc}", backend="braket") from exc


def _simulate_qsharp(circuit: QuantumCircuit, shots: int) -> dict[str, int]:
    """Simulate using the Q# backend (skeleton, falls back to Qiskit)."""
    logger = get_logger("router")

    try:
        from .backends.experimental.qsharp_backend import QSharpBackend
    except ImportError as exc:
        raise BackendUnavailableError("qsharp", "Q# Python bridge not installed") from exc

    try:
        backend = QSharpBackend()
        return backend.simulate(circuit, shots)
    except Exception as exc:
        logger.log_simulation_error(exc, backend="qsharp")
        raise SimulationError(f"Q# simulation failed: {exc}", backend="qsharp") from exc


def _simulate_opencl(circuit: QuantumCircuit, shots: int) -> dict[str, int]:
    """Simulate using the OpenCL backend (skeleton, falls back to Qiskit)."""
    logger = get_logger("router")

    try:
        from .backends.experimental.opencl_backend import OpenCLBackend
    except ImportError as exc:
        raise BackendUnavailableError("opencl", "pyopencl not installed") from exc

    try:
        backend = OpenCLBackend()
        return backend.simulate(circuit, shots)
    except Exception as exc:
        logger.log_simulation_error(exc, backend="opencl")
        raise SimulationError(f"OpenCL simulation failed: {exc}", backend="opencl") from exc


def _simulate_cuda(circuit: QuantumCircuit, shots: int) -> dict[str, int]:
    logger = get_logger("router")

    if not is_cuda_available() or CUDABackend is None:
        raise BackendUnavailableError("cuda", "CUDA runtime not available")

    try:
        assert CUDABackend is not None
        backend = CUDABackend()
        result = backend.simulate(circuit, shots)
        # Ensure result is of correct type
        return dict(result)
    except Exception as exc:
        logger.log_simulation_error(exc, backend="cuda")
        raise SimulationError(f"CUDA simulation failed: {exc}", backend="cuda") from exc


def _simulate_mps(circuit: QuantumCircuit, shots: int) -> dict[str, int]:
    """Simulate ``circuit`` using the Matrix Product State backend."""
    logger = get_logger("router")

    try:
        from .backends.mps_backend import MPSBackend
    except ImportError as exc:
        raise BackendUnavailableError("mps", "MPS backend dependencies not available") from exc

    try:
        backend = MPSBackend()
        return backend.simulate(circuit, shots)
    except Exception as exc:
        logger.log_simulation_error(exc, backend="mps")
        raise SimulationError(f"MPS simulation failed: {exc}", backend="mps") from exc


def _simulate_metal(circuit: QuantumCircuit, shots: int) -> dict[str, int]:
    logger = get_logger("router")

    if not is_metal_available() or MetalBackend is None:
        raise BackendUnavailableError("metal", "JAX with Metal support not available")

    try:
        assert MetalBackend is not None
        backend = MetalBackend()
        result = backend.simulate(circuit, shots)
        # Ensure result is of correct type
        return dict(result)
    except Exception as exc:
        logger.log_simulation_error(exc, backend="metal")
        raise SimulationError(f"Metal simulation failed: {exc}", backend="metal") from exc


def _sample_statevector_counts(circuit: QuantumCircuit, shots: int, seed: int | None = None) -> dict[str, int]:
    if shots < 0:
        raise ValueError("shots must be non-negative")
    if shots == 0:
        return {}

    state = Statevector.from_instruction(circuit)
    probabilities = np.abs(state.data) ** 2
    total = probabilities.sum()
    if total == 0.0:
        raise RuntimeError("Statevector sampling produced invalid probabilities")
    if not np.isclose(total, 1.0):
        probabilities = probabilities / total

    rng = np.random.default_rng(seed)
    outcomes = rng.choice(len(probabilities), size=shots, p=probabilities)

    counts: dict[str, int] = {}
    num_qubits = circuit.num_qubits
    for outcome in outcomes:
        bitstring = format(int(outcome), f"0{num_qubits}b")[::-1]
        counts[bitstring] = counts.get(bitstring, 0) + 1
    return counts


# ------------------------------------------------------------------
# Core Execution Logic


def _execute_simulation(circuit: QuantumCircuit, shots: int, routing_decision: RoutingDecision) -> SimulationResult:
    """Execute simulation based on a routing decision, including fallback logic."""
    logger = get_logger("router")
    resource_manager = get_resource_manager()

    backend = routing_decision.recommended_backend
    backend_name = backend.value

    # Check resource availability
    can_handle, reason = check_circuit_feasibility(circuit, backend_name)
    if not can_handle:
        raise ResourceExhaustionError("memory", 0, resource_manager.get_resources().available_memory_mb)

    # Initialize result tracking
    fallback_reason = None
    warnings_list = []
    reserved_resources = None

    # Set up logging for backend selection
    logger.set_circuit_context(circuit)
    logger.log_routing_decision(circuit, backend_name, routing_decision.confidence_score, "Selected by router")

    # Reserve resources
    try:
        reserved_resources = resource_manager.reserve_resources(circuit, backend_name)
    except ResourceExhaustionError as exc:
        logger.error(f"Failed to reserve resources: {exc}")
        raise exc

    start = perf_counter()

    try:
        logger.log_simulation_start(circuit, backend_name, shots)

        if backend == BackendType.STIM:
            counts = _simulate_stim(circuit, shots)
        elif backend == BackendType.QISKIT:
            counts = _simulate_qiskit(circuit, shots)
        elif backend == BackendType.TENSOR_NETWORK:
            counts = _simulate_tensor_network(circuit, shots)
        elif backend == BackendType.JAX_METAL:
            counts = _simulate_jax_metal(circuit, shots)
        elif backend == BackendType.DDSIM:
            counts = _simulate_ddsim(circuit, shots)
        elif backend == BackendType.MPS:
            counts = _simulate_mps(circuit, shots)
        elif backend == BackendType.CUDA:
            counts = _simulate_cuda(circuit, shots)
        elif backend == BackendType.CIRQ:
            counts = _simulate_cirq(circuit, shots)
        elif backend == BackendType.PENNYLANE:
            counts = _simulate_pennylane(circuit, shots)
        elif backend == BackendType.QULACS:
            counts = _simulate_qulacs(circuit, shots)
        elif backend == BackendType.PYQUIL:
            counts = _simulate_pyquil(circuit, shots)
        elif backend == BackendType.BRAKET:
            counts = _simulate_braket(circuit, shots)
        elif backend == BackendType.QSHARP:
            counts = _simulate_qsharp(circuit, shots)
        elif backend == BackendType.OPENCL:
            counts = _simulate_opencl(circuit, shots)
        else:
            # Fallback for unknown or unhandled backend types
            logger.warning(f"Unknown backend {backend_name} selected, falling back to Qiskit")
            counts = _simulate_qiskit(circuit, shots)
            backend = BackendType.QISKIT
            backend_name = "qiskit"
            warnings_list.append(f"Unknown backend {backend.value} selected, falling back to Qiskit.")

    except Exception as exc:
        # Log the specific failure for debugging
        logger.log_simulation_error(exc, backend=backend_name)
        fallback_reason = f"Backend {backend_name} failed: {str(exc)}"

        # Attempt fallback to Qiskit
        try:
            logger.info(f"Falling back to Qiskit backend after {backend_name} failure")
            counts = _simulate_qiskit(circuit, shots)
            backend = BackendType.QISKIT
            backend_name = "qiskit"
        except Exception as qiskit_exc:
            # Last resort: log and re-raise the original exception
            logger.error(f"Qiskit fallback also failed: {qiskit_exc}")
            raise SimulationError(
                f"All backends failed. Original error: {exc}. Qiskit fallback error: {qiskit_exc}",
                backend=backend_name,
            ) from exc

    elapsed = perf_counter() - start

    # Release resources
    if reserved_resources:
        resource_manager.release_resources(reserved_resources)

    # Log completion
    logger.log_simulation_complete(elapsed, shots, backend=backend_name)

    # Check for experimental backend warnings
    if backend == BackendType.JAX_METAL and is_metal_available():
        warnings_list.append("JAX-Metal support is experimental and may show warnings")
    elif backend == BackendType.CUDA and not is_cuda_available():
        warnings_list.append("CUDA backend selected but CUDA not available")

    return SimulationResult(
        counts=counts,
        backend_used=backend,
        execution_time=elapsed,
        routing_decision=routing_decision,
        metadata={"shots": shots},
        fallback_reason=fallback_reason,
        warnings=warnings_list if warnings_list else None,
    )


def simulate(circuit: QuantumCircuit, shots: int = 1024, backend: str | None = None) -> SimulationResult:
    """Convenience wrapper that routes and executes ``circuit``."""
    logger = get_logger("router")

    # Validate inputs
    if shots < 0:
        raise ValueError("shots must be non-negative")

    # Handle empty circuit case
    if circuit.num_qubits <= 0:
        return SimulationResult(
            counts={"": shots} if shots > 0 else {},
            backend_used=BackendType.QISKIT,  # Mock backend
            execution_time=0.0,
            routing_decision=RoutingDecision(
                circuit_entropy=0.0,
                recommended_backend=BackendType.QISKIT,
                confidence_score=1.0,
                expected_speedup=1.0,
                channel_capacity_match=1.0,
                alternatives=[],
            ),
            metadata={"shots": shots},
        )

    # Initialize Enhanced Router
    enhanced_router = EnhancedQuantumRouter()

    if backend is not None:
        # Force specific backend
        try:
            backend_type = BackendType(backend)
        except ValueError as exc:
            raise ValueError(f"Unknown backend: {backend}") from exc

        # Check if forced backend is available
        can_handle, reason = check_circuit_feasibility(circuit, backend)
        if not can_handle:
            raise CircuitTooLargeError(circuit.num_qubits, circuit.depth(), backend)

        # Create a forced routing decision
        routing_decision = RoutingDecision(
            circuit_entropy=0.0,
            recommended_backend=backend_type,
            confidence_score=1.0,
            expected_speedup=1.0,
            channel_capacity_match=1.0,
            alternatives=[],
        )

        logger.info(f"Using forced backend: {backend}")
    else:
        # Use Enhanced Router for optimal selection
        try:
            routing_decision = enhanced_router.select_optimal_backend(circuit, strategy=RouterType.HYBRID_ROUTER)
        except Exception as exc:
            logger.error(f"Router failed to select backend: {exc}")
            raise SimulationError(f"Router failed: {exc}") from exc

    try:
        return _execute_simulation(circuit, shots, routing_decision)
    except Exception as exc:
        logger.error(f"Simulation failed: {exc}")
        raise
