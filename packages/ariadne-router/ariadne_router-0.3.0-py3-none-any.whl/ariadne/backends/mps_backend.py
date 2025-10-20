"""A backend for simulating quantum circuits using Matrix Product States."""

from typing import Any, cast

import numpy as np
import quimb.tensor as tn
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from .universal_interface import BackendCapability, BackendMetrics, UniversalBackend


class MPSBackend(UniversalBackend):
    """
    A quantum backend that uses a Matrix Product State (MPS) representation
    to simulate quantum circuits. This backend is particularly effective for
    circuits with low entanglement.
    """

    def __init__(self, max_bond_dimension: int = 64) -> None:
        """
        Initializes the MPS backend.

        Args:
            max_bond_dimension: The maximum bond dimension to use for the MPS.
        """
        self.max_bond_dimension = max_bond_dimension

    def simulate(self, circuit: QuantumCircuit, shots: int = 1000, **kwargs: Any) -> dict[str, int]:
        """
        Simulates the given quantum circuit using an MPS representation.

        The Matrix Product State (MPS) is a tensor network representation that
        efficiently captures quantum states with limited entanglement. It maps
        the global quantum state of N qubits to a chain of N rank-3 tensors,
        where the central index (bond dimension) controls the amount of
        entanglement that can be represented.

        Args:
            circuit: The quantum circuit to simulate.

        Returns:
            Dictionary of measurement counts.
        """
        for item in circuit.data:
            if hasattr(item, "operation"):
                instruction = item.operation
                qargs = list(item.qubits)
            else:  # Legacy tuple form
                instruction_tuple = cast(tuple[Any, list[Any], Any], item)
                instruction, qargs, _ = instruction_tuple
            gate_name = getattr(instruction, "name", "")
            if gate_name in {"measure", "barrier", "reset"}:
                continue
            if len(qargs) > 2:
                return self._simulate_with_statevector(circuit, shots)

        n_qubits = circuit.num_qubits
        max_bond = self.max_bond_dimension

        # print(f"Simulating circuit with MPS backend (max_bond_dimension={max_bond})...")

        # 1. Initialize the MPS in the |0...0> state
        # The physical dimension is 2 (qubit), and the bond dimension is 1 (unentangled)
        # Initialize the MPS from the dense |0...0> state vector
        zero_state = np.zeros(2**n_qubits, dtype=complex)
        zero_state[0] = 1.0
        mps = tn.MatrixProductState.from_dense(
            zero_state,
        )

        def reverse_bits(index: int, width: int) -> int:
            return int(format(index, f"0{width}b")[::-1], 2)

        def little_to_big_endian(matrix: np.ndarray, width: int) -> np.ndarray:
            if width <= 1:
                return matrix
            dimension = 1 << width
            permutation = [reverse_bits(i, width) for i in range(dimension)]
            return matrix[np.ix_(permutation, permutation)]

        # 2. Apply gates from the Qiskit circuit
        for item in circuit.data:
            if hasattr(item, "operation"):
                instruction = item.operation
                qargs = list(item.qubits)
            else:  # Legacy tuple form
                instruction_tuple = cast(tuple[Any, list[Any], Any], item)
                instruction, qargs, _ = instruction_tuple

            gate_name = instruction.name
            physical_qubits = [circuit.num_qubits - 1 - circuit.find_bit(q).index for q in qargs]

            try:
                gate_matrix = instruction.to_matrix()
            except Exception as err:
                if gate_name in ["measure", "barrier", "reset"]:
                    continue
                raise NotImplementedError(f"Gate '{gate_name}' not supported by MPS backend.") from err

            if not physical_qubits:
                continue

            gate_matrix = little_to_big_endian(gate_matrix, len(physical_qubits))

            order = sorted(range(len(physical_qubits)), key=lambda i: physical_qubits[i])
            qubits = [physical_qubits[i] for i in order]

            if len(order) > 1 and order != list(range(len(order))):
                k = len(order)
                gate_tensor = gate_matrix.reshape([2] * (2 * k))
                perm = order + [i + k for i in order]
                gate_tensor = gate_tensor.transpose(perm)
                gate_matrix = gate_tensor.reshape(2**k, 2**k)

            if len(qubits) == 1:
                contract_mode: bool | str = True
            elif len(qubits) == 2:
                contract_mode = "swap+split"
            else:
                contract_mode = "auto-split-gate"

            mps.gate_(
                gate_matrix,
                qubits,
                contract=contract_mode,
                max_bond=max_bond,
                propagate_tags=False,
            )

        # 3. Sample counts directly from the MPS
        # This avoids the exponential O(2^N) contraction step, restoring polynomial scaling.
        samples_gen = mps.sample(shots)

        # Convert samples generator to list and process
        counts: dict[str, int] = {}

        for state_list, _ in list(samples_gen):
            bitstring = "".join(str(bit) for bit in state_list)
            counts[bitstring] = counts.get(bitstring, 0) + 1

        return counts

    def _simulate_with_statevector(self, circuit: QuantumCircuit, shots: int) -> dict[str, int]:
        circuit_no_measure = circuit.remove_final_measurements(inplace=False) if circuit.num_clbits else circuit
        state = Statevector.from_instruction(circuit_no_measure)
        counts = state.sample_counts(shots=shots)
        return {bitstring: int(count) for bitstring, count in counts.items()}

    # Implement required abstract methods from UniversalBackend
    def get_backend_info(self) -> dict[str, Any]:
        return {"name": "mps", "max_bond_dimension": self.max_bond_dimension}

    def get_capabilities(self) -> list[BackendCapability]:
        return [BackendCapability.STATE_VECTOR_SIMULATION]

    def get_metrics(self) -> BackendMetrics:
        return BackendMetrics(
            max_qubits=50,
            typical_qubits=30,
            memory_efficiency=0.9,
            speed_rating=0.9,
            accuracy_rating=0.9,
            stability_rating=0.9,
            capabilities=self.get_capabilities(),
            hardware_requirements=["CPU"],
            estimated_cost_factor=0.1,
            gate_times={"single_qubit": 1e-9, "two_qubit": 5e-9},
            error_rates={"single_qubit": 1e-5, "two_qubit": 5e-4},
            connectivity_map=None,
        )

    def can_simulate(self, circuit: QuantumCircuit, **kwargs: Any) -> tuple[bool, str]:
        if circuit.num_qubits > 50:
            return False, "Too many qubits for MPS backend"
        return True, "Can simulate"
