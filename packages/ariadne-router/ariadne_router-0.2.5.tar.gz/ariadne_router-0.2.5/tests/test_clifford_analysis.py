from __future__ import annotations

import pytest

from ariadne.route.analyze import clifford_ratio, is_clifford_circuit


def test_clifford_ratio_for_clifford_only() -> None:
    pytest.importorskip("qiskit")
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cx(0, 1)
    qc.s(2)
    qc.cz(1, 2)
    assert is_clifford_circuit(qc) is True
    assert clifford_ratio(qc) == 1.0
