from __future__ import annotations

from qiskit import QuantumCircuit
from qiskit.qasm3 import dumps as qasm3_dumps
from qiskit.qasm3 import loads as qasm3_loads

from ariadne.verify.qcec import assert_equiv
from examples._util import write_report


def build() -> QuantumCircuit:
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.h(0)
    return qc


def optimize(qc: QuantumCircuit) -> QuantumCircuit:
    out = QuantumCircuit(qc.num_qubits)
    # trivial H-H cancel
    for inst, qargs, cargs in qc.data:
        out.append(inst, qargs, cargs)
    # no real opt here; structure placeholder
    return out


def main() -> None:
    circ = build()
    circ2 = optimize(circ)
    qasm = qasm3_dumps(circ2)
    circ_back = qasm3_loads(qasm)
    ok = False
    try:
        assert_equiv(circ, circ_back)
        ok = True
    except Exception:
        pass
    report = f"""
# QASM3 + QCEC Equivalence Check

- Equivalent: {ok}
- Method: assert_equiv (Statevector + MQT.QCEC if available)
"""
    path = write_report("04_qasm3_qcec", report)
    print(f"Wrote report to {path}")


if __name__ == "__main__":
    main()
