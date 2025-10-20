from __future__ import annotations

from qiskit import QuantumCircuit
from qiskit.qasm3 import dumps as qasm3_dumps
from qiskit.qasm3 import loads as qasm3_loads

from ariadne.verify.qcec import statevector_equiv
from examples._util import write_report


def build_circuit() -> QuantumCircuit:
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cx(0, 1)
    qc.t(1)
    qc.cx(1, 2)
    qc.h(2)
    return qc


def main() -> None:
    circ = build_circuit()
    qasm_text = qasm3_dumps(circ)

    # Perform QASM3 roundtrip using Qiskit's native parser
    circ_round = qasm3_loads(qasm_text)

    equivalent = statevector_equiv(circ, circ_round)
    report = f"""
# QASM3 Roundtrip Report

- Gates: {len(circ.data)}
- Equivalent: {equivalent}
- Method: Statevector Comparison
"""
    path = write_report("01_qasm3_roundtrip", report)
    print(f"Wrote report to {path}")


if __name__ == "__main__":
    main()
