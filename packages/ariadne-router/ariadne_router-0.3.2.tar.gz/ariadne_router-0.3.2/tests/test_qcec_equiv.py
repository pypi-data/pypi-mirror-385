from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ariadne.passes.zx_opt import trivial_cancel
from ariadne.verify.qcec import assert_equiv, statevector_equiv

if TYPE_CHECKING:
    from qiskit import QuantumCircuit


def build_cancellable() -> QuantumCircuit:
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(2)
    qc.h(0)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(0, 1)
    qc.t(0)  # keep nontrivial piece
    return qc


def test_statevector_equivalence_of_trivially_optimized() -> None:
    pytest.importorskip("qiskit")
    a = build_cancellable()
    b = trivial_cancel(a)
    assert statevector_equiv(a, b)


def test_qcec_equivalence_if_available() -> None:
    pytest.importorskip("qiskit")
    a = build_cancellable()
    b = trivial_cancel(a)
    pytest.importorskip("mqt.qcec")
    # If import succeeds, assert via QCEC
    assert_equiv(a, b)
