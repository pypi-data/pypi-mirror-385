from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ariadne.route.execute import decide_backend

if TYPE_CHECKING:
    from qiskit import QuantumCircuit


def low_treewidth_circuit(n: int = 10) -> QuantumCircuit:
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(n)
    for i in range(n - 1):
        qc.cx(i, i + 1)
        qc.t(i)
    qc.t(n - 1)
    return qc


def dense_circuit(n: int = 10) -> QuantumCircuit:
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(n)
    for i in range(n):
        for j in range(i + 1, n):
            qc.cx(i, j)
    for i in range(n):
        qc.t(i)
    return qc


def test_router_picks_tn_for_low_treewidth() -> None:
    pytest.importorskip("qiskit")
    circ = low_treewidth_circuit()
    backend = decide_backend(circ)
    assert backend == "tn"


def test_router_picks_sv_for_dense() -> None:
    pytest.importorskip("qiskit")
    circ = dense_circuit()
    backend = decide_backend(circ)
    assert backend == "sv"
