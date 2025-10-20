from qiskit import QuantumCircuit

from ariadne.route.enhanced_router import EnhancedQuantumRouter
from ariadne.route.topology_analyzer import detect_layout_properties
from ariadne.types import BackendType


def build_chain_like_nonclifford(n: int = 8) -> QuantumCircuit:
    qc = QuantumCircuit(n, n)
    # nearest-neighbor entanglement (chain)
    qc.h(0)
    qc.t(0)  # make non-Clifford to avoid STIM
    for i in range(n - 1):
        qc.cx(i, i + 1)
    qc.measure_all()
    return qc


def test_detects_chain_like_topology() -> None:
    qc = build_chain_like_nonclifford(8)
    props = detect_layout_properties(qc)
    assert isinstance(props, dict)
    assert props.get("chain_like") is True
    assert props.get("max_degree", 0) <= 2


def test_router_prefers_mps_for_chain_like() -> None:
    qc = build_chain_like_nonclifford(8)
    router = EnhancedQuantumRouter()
    decision = router.select_optimal_backend(qc)
    assert decision.recommended_backend == BackendType.MPS
