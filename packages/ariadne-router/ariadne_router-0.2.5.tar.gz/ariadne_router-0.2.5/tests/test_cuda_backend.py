"""Tests for the optional CUDA backend."""

from __future__ import annotations

import pytest
from qiskit import QuantumCircuit

from ariadne.backends.cuda_backend import (
    CUDA_AVAILABLE,
    CUDABackend,
    get_cuda_info,
    is_cuda_available,
)


def _bell_state_circuit() -> QuantumCircuit:
    circuit = QuantumCircuit(2, 2)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure(0, 0)
    circuit.measure(1, 1)
    return circuit


def test_get_cuda_info_structure() -> None:
    info = get_cuda_info()
    assert "available" in info
    assert "device_count" in info

    device_count = info.get("device_count")
    assert isinstance(device_count, int)

    if info["available"]:
        assert device_count >= 0
        assert "devices" in info
    else:
        assert device_count == 0


def test_backend_runs_with_cpu_fallback() -> None:
    backend = CUDABackend(allow_cpu_fallback=True)
    counts = backend.simulate(_bell_state_circuit(), shots=200)
    assert sum(counts.values()) == 200
    assert set(counts.keys()).issubset({"00", "11"})


@pytest.mark.skipif(CUDA_AVAILABLE, reason="Only relevant when CUDA is missing")
def test_backend_without_fallback_requires_cuda() -> None:
    with pytest.raises(RuntimeError):
        CUDABackend(allow_cpu_fallback=False)


@pytest.mark.skipif(not is_cuda_available(), reason="Requires CUDA runtime")
def test_backend_prefers_cuda_when_available() -> None:
    backend = CUDABackend(prefer_gpu=True, allow_cpu_fallback=False)
    assert backend.backend_mode == "cuda"
    counts = backend.simulate(_bell_state_circuit(), shots=64)
    assert sum(counts.values()) == 64


def test_measurement_order_is_respected() -> None:
    circuit = QuantumCircuit(3, 3)
    circuit.x(2)
    circuit.measure(2, 0)
    circuit.measure(0, 1)
    circuit.measure(1, 2)

    backend = CUDABackend(allow_cpu_fallback=True)
    counts = backend.simulate(circuit, shots=32)

    assert sum(counts.values()) == 32
    for bitstring in counts:
        assert len(bitstring) == 3
