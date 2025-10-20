from __future__ import annotations

from qiskit import QuantumCircuit

from ariadne.route.analyze import analyze_circuit
from ariadne.route.execute import decide_backend
from examples._util import write_report


def low_treewidth_circuit(n: int = 10) -> QuantumCircuit:
    qc = QuantumCircuit(n)
    # Line of nearest-neighbor interactions with T gates to break Clifford
    for i in range(n - 1):
        qc.cx(i, i + 1)
        qc.t(i)
    qc.t(n - 1)
    return qc


def dense_circuit(n: int = 10) -> QuantumCircuit:
    qc = QuantumCircuit(n)
    # All-to-all layer of CX and T gates
    for i in range(n):
        for j in range(i + 1, n):
            qc.cx(i, j)
    for i in range(n):
        qc.t(i)
    return qc


def main() -> None:
    lt = low_treewidth_circuit()
    dn = dense_circuit()
    m_lt = analyze_circuit(lt)
    m_dn = analyze_circuit(dn)
    b_lt = decide_backend(lt)
    b_dn = decide_backend(dn)

    report = f"""
# Router Showdown

## Low treewidth
- Metrics: {m_lt}
- Backend: {b_lt}

## Dense circuit
- Metrics: {m_dn}
- Backend: {b_dn}
"""
    path = write_report("03_router_showdown", report)
    print(f"Wrote report to {path}")


if __name__ == "__main__":
    main()
