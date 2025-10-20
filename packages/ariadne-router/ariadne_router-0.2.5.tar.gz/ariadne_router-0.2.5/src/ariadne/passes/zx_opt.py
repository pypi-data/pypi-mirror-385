"""Trivial circuit simplifications for quick experiments."""

from __future__ import annotations

from collections.abc import Iterable

from qiskit import QuantumCircuit
from qiskit.circuit import Instruction

_CANCEL_PAIRS = {"h", "x", "y", "z", "cx", "cy", "cz", "swap"}


def _instruction_signature(instruction: Instruction, qubits: Iterable) -> tuple[str, tuple[object, ...]]:
    return instruction.name, tuple(qubits)


def trivial_cancel(circuit: QuantumCircuit) -> QuantumCircuit:
    """Return a copy of ``circuit`` with adjacent inverse pairs removed."""

    simplified = circuit.copy()
    new_data: list[tuple[Instruction, Iterable, Iterable]] = []

    for item in simplified.data:
        if hasattr(item, "operation"):
            instruction = item.operation
            qubits = item.qubits
            clbits = item.clbits
        else:
            instruction, qubits, clbits = item

        if new_data:
            last_instruction, last_qubits, last_clbits = new_data[-1]
            sig_current = _instruction_signature(instruction, qubits)
            sig_previous = _instruction_signature(last_instruction, last_qubits)

            if sig_current == sig_previous and instruction.name in _CANCEL_PAIRS:
                new_data.pop()
                continue

        new_data.append((instruction, qubits, clbits))

    simplified.data = new_data
    return simplified
