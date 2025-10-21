"""Circuit equivalence helpers."""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector


def statevector_equiv(left: QuantumCircuit, right: QuantumCircuit, *, atol: float = 1e-9) -> bool:
    """Return ``True`` when two circuits produce the same statevector."""

    sv_left = Statevector.from_instruction(left)
    sv_right = Statevector.from_instruction(right)
    fidelity = np.abs(np.vdot(sv_left.data, sv_right.data))
    return bool(fidelity > 1 - atol)


def assert_equiv(left: QuantumCircuit, right: QuantumCircuit, *, atol: float = 1e-9) -> None:
    """Raise ``AssertionError`` when two circuits are not equivalent."""

    if not statevector_equiv(left, right, atol=atol):
        raise AssertionError("Circuits are not equivalent under statevector comparison")

    try:  # pragma: no cover - optional dependency
        import mqt.qcec as qcec
    except ImportError:
        return

    try:
        result = qcec.compare_circuits(left, right)
    except Exception:
        return

    if hasattr(result, "equivalent") and not result.equivalent:
        raise AssertionError("Circuits are not equivalent according to mqt.qcec")
