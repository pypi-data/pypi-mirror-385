"""Common types and enums for Ariadne."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class BackendType(Enum):
    """Available quantum simulation backends."""

    STIM = "stim"
    QISKIT = "qiskit"
    TENSOR_NETWORK = "tensor_network"
    JAX_METAL = "jax_metal"
    DDSIM = "ddsim"
    CUDA = "cuda"
    MPS = "mps"
    CIRQ = "cirq"
    PENNYLANE = "pennylane"
    QULACS = "qulacs"
    BRAKET = "braket"
    PYQUIL = "pyquil"
    QSHARP = "qsharp"
    OPENCL = "opencl"
    ROCM = "rocm"
    ONEAPI = "oneapi"


@dataclass
class BackendCapacity:
    """Simple scoring model for backend suitability."""

    clifford_capacity: float
    general_capacity: float
    memory_efficiency: float
    apple_silicon_boost: float


@dataclass
class RoutingDecision:
    """Information returned by the routing mechanism."""

    circuit_entropy: float
    recommended_backend: BackendType
    confidence_score: float
    expected_speedup: float
    channel_capacity_match: float
    alternatives: list[tuple[BackendType, float]]


@dataclass
class SimulationResult:
    """Container for the output of :func:`simulate`."""

    counts: dict[str, int]
    backend_used: BackendType
    execution_time: float
    routing_decision: RoutingDecision
    metadata: dict[str, Any]
    fallback_reason: str | None = None  # Reason for backend fallback
    warnings: list[str] | None = None  # Any warnings during execution
