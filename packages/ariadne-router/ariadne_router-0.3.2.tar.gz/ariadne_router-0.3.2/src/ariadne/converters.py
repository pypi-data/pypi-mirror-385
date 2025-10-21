"""Circuit conversion utilities for Ariadne quantum router."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qiskit import QuantumCircuit

if TYPE_CHECKING:
    import stim

# Mapping from Qiskit gate names to Stim gate names
STIM_GATE_MAP = {
    "i": "I",
    "id": "I",
    "x": "X",
    "y": "Y",
    "z": "Z",
    "h": "H",
    "s": "S",
    "sdg": "S_DAG",
    "sx": "SQRT_X",
    "sxdg": "SQRT_X_DAG",
    "cx": "CX",
    "cz": "CZ",
    "swap": "SWAP",
    "measure": "M",
}


def convert_qiskit_to_stim(qc: QuantumCircuit) -> tuple[stim.Circuit, list[tuple[int, int]]]:
    """Convert Qiskit circuit to Stim circuit.

    CRITICAL: Uses explicit qubit/clbit index maps for Qiskit 2.x compatibility
    """
    import stim

    stim_circuit = stim.Circuit()

    # Create index maps (Qiskit 2.x removed .index attribute)
    qubit_map = {qubit: idx for idx, qubit in enumerate(qc.qubits)}
    clbit_map = {clbit: idx for idx, clbit in enumerate(qc.clbits)}

    # Track measurement mapping for proper bit ordering
    measurement_map: list[tuple[int, int]] = []  # (measurement_index, clbit_index)
    measurement_counter = 0

    for inst in qc.data:
        gate_name = inst.operation.name.lower()
        qubit_indices = [qubit_map[q] for q in inst.qubits]

        if gate_name == "measure":
            if not inst.clbits:
                continue
            for qubit, clbit in zip(inst.qubits, inst.clbits, strict=False):
                stim_circuit.append("M", [qubit_map[qubit]])
                if clbit in clbit_map:
                    measurement_map.append((measurement_counter, clbit_map[clbit]))
                measurement_counter += 1
            continue

        if gate_name in {"barrier", "delay"}:
            continue

        # Convert quantum gates
        stim_gate = STIM_GATE_MAP.get(gate_name)
        if stim_gate is None:
            raise ValueError(f"Unsupported gate '{gate_name}' for Stim backend")

        stim_circuit.append(stim_gate, qubit_indices)

    return stim_circuit, measurement_map


def simulate_stim_circuit(
    stim_circuit: stim.Circuit, measurement_map: list[tuple[int, int]], shots: int, num_clbits: int
) -> dict[str, int]:
    """Simulate Stim circuit and convert results to Qiskit format."""
    sampler = stim_circuit.compile_sampler()
    samples = sampler.sample(shots)

    counts: dict[str, int] = {}
    for sample in samples:
        bits = ["0"] * num_clbits
        for meas_index, clbit_index in measurement_map:
            if clbit_index < num_clbits:
                bits[clbit_index] = "1" if sample[meas_index] else "0"

        # Qiskit formats classical bitstrings little-endian
        bitstring = "".join(bits[::-1])
        counts[bitstring] = counts.get(bitstring, 0) + 1

    return counts
