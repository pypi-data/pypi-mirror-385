"""Legacy routing helpers retained for compatibility with older tests."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from time import perf_counter
from typing import Literal

from qiskit import QuantumCircuit

from ..router import SimulationResult
from ..router import simulate as core_simulate
from .analyze import analyze_circuit

Backend = Literal["stim", "tn", "sv", "dd"]


def decide_backend(circuit: QuantumCircuit) -> Backend:
    metrics = analyze_circuit(circuit)

    if metrics.get("is_clifford", False):
        return "stim"

    treewidth = metrics.get("treewidth_estimate", 0)
    num_qubits = metrics.get("num_qubits", 0)
    depth = metrics.get("depth", 0)
    two_qubit_depth = metrics.get("two_qubit_depth", 0)
    edges = metrics.get("edges", 0)

    if treewidth <= 10 and edges <= num_qubits * 2:
        return "tn"

    if num_qubits <= 20 or two_qubit_depth >= max(1, depth // 2):
        return "sv"

    return "dd"


def _simulate_with_router(circuit: QuantumCircuit, shots: int) -> dict[str, object]:
    result: SimulationResult = core_simulate(circuit, shots=shots)
    return {
        "counts": result.counts,
        "backend": result.backend_used.value,
    }


@dataclass
class Trace:
    backend: Backend
    wall_time_s: float
    metrics: dict[str, float | int | bool]


def execute(circuit: QuantumCircuit, shots: int = 1024) -> dict[str, object]:  # pragma: no cover - integration helper
    backend = decide_backend(circuit)
    metrics = analyze_circuit(circuit)

    start = perf_counter()

    # Use router for actual simulation
    if backend == "stim" and metrics.get("is_clifford", False):
        result = _simulate_with_router(circuit, shots)
        payload = result
    else:
        # Fallback to qiskit or other backends
        try:
            from qiskit.quantum_info import Statevector

            statevector = Statevector.from_instruction(circuit)
            payload = {"statevector": statevector.data}
        except Exception as exc:
            payload = {"error": str(exc)}

    wall_time = perf_counter() - start

    trace = Trace(backend=backend, wall_time_s=wall_time, metrics=metrics)
    return {"trace": asdict(trace), **payload}
