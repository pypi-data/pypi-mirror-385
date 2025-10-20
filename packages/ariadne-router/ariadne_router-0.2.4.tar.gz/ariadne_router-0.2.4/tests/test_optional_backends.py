import importlib.util

import pytest
from qiskit import QuantumCircuit

from ariadne.router import simulate


def _has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


@pytest.mark.skipif(not _has_module("cirq"), reason="Cirq not installed")
def test_cirq_backend_simulation() -> None:
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()

    result = simulate(qc, shots=100, backend="cirq")
    assert sum(result.counts.values()) == 100


@pytest.mark.skipif(not _has_module("pennylane"), reason="PennyLane not installed")
def test_pennylane_backend_simulation() -> None:
    qc = QuantumCircuit(2)
    qc.ry(0.3, 0)
    qc.cx(0, 1)
    qc.measure_all()

    result = simulate(qc, shots=50, backend="pennylane")
    assert sum(result.counts.values()) == 50


@pytest.mark.skipif(not _has_module("qulacs"), reason="Qulacs not installed")
def test_qulacs_backend_simulation() -> None:
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()

    result = simulate(qc, shots=64, backend="qulacs")
    assert sum(result.counts.values()) == 64


@pytest.mark.skipif(not _has_module("pyquil"), reason="PyQuil not installed")
def test_pyquil_backend_simulation() -> None:
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()

    result = simulate(qc, shots=32, backend="pyquil")
    assert sum(result.counts.values()) == 32


@pytest.mark.skipif(not _has_module("braket"), reason="Braket SDK not installed")
def test_braket_backend_simulation() -> None:
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()

    result = simulate(qc, shots=16, backend="braket")
    assert sum(result.counts.values()) == 16


@pytest.mark.skipif(not _has_module("qsharp"), reason="Q# bridge not installed")
def test_qsharp_backend_simulation() -> None:
    qc = QuantumCircuit(1)
    qc.h(0)
    qc.measure_all()

    result = simulate(qc, shots=10, backend="qsharp")
    assert sum(result.counts.values()) == 10
