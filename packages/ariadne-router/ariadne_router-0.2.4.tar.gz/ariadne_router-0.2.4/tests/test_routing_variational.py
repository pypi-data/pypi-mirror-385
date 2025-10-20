import importlib.util

import pytest
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter

from ariadne.route.enhanced_router import EnhancedQuantumRouter
from ariadne.types import BackendType


def _has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


@pytest.mark.skipif(not _has_module("pennylane"), reason="PennyLane not installed")
def test_variational_circuit_prefers_pennylane() -> None:
    qc = QuantumCircuit(2)
    theta = Parameter("theta")
    qc.ry(theta, 0)
    qc.cx(0, 1)
    qc.measure_all()

    router = EnhancedQuantumRouter()
    decision = router.select_optimal_backend(qc)

    assert (
        decision.recommended_backend == BackendType.PENNYLANE
    ), f"Expected PENNYLANE, got {decision.recommended_backend}"
