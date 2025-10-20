"""Analyzes a quantum circuit to determine if it's suitable for MPS simulation."""

import math

from qiskit import QuantumCircuit


def should_use_mps(circuit: QuantumCircuit) -> bool:
    """
    The Feynman Intuition: Why Matrix Product States (MPS) work.

    Look, the universe is complicated, but sometimes, it's just not *that* complicated.
    Quantum mechanics tells us that a system of N qubits lives in a Hilbert space
    of dimension 2^N. That's a big number, exponentially big! If we had to keep track
    of all 2^N amplitudes, we'd run out of memory before we hit 50 qubits.

    But here's the trick, the physical intuition: most physically relevant states
    don't use that whole space. They are *sparse* in a very specific way.
    The entanglement between two halves of the system, when you cut it, often
    doesn't grow with the volume (the number of qubits), but only with the
    *area* (the boundary between the two halves). This is the "Area Law."

    Matrix Product States (MPS) exploit this. Instead of storing 2^N numbers,
    we store a chain of matrices. The size of these matrices—the 'bond dimension' (D)—
    is what limits the entanglement we can represent. If the entanglement is low,
    D can be small (maybe constant or logarithmic in N), and the simulation scales
    polynomially, not exponentially. It's a beautiful, simple idea: if the physics
    is local, the description should be local too.

    This function uses a simple heuristic to guess if the circuit is 'local enough'
    or 'small enough' to keep the entanglement low and the bond dimension manageable.

    Heuristic Criteria:
    1. Small System Size: Fewer than 15 qubits. (N < 15)
    2. Limited Interaction: The number of two-qubit gates (which generate entanglement)
       is less than 2 * N^1.5. This limits the depth and complexity of entanglement growth.

    Args:
        circuit: The quantum circuit to analyze.

    Returns:
        True if the circuit is likely suitable for efficient MPS simulation, False otherwise.
    """
    num_qubits = circuit.num_qubits
    if num_qubits >= 15:
        return False

    # Count two-qubit gates (entangling gates)
    two_qubit_gates = 0
    for instruction in circuit.data:
        if len(instruction.qubits) == 2:
            # We assume any two-qubit gate is an entangling gate for this heuristic
            # (e.g., CNOT, CZ, RXX, etc.)
            two_qubit_gates += 1

    # The threshold for two-qubit gates: 2 * N^1.5
    threshold = 2 * math.pow(num_qubits, 1.5)

    return two_qubit_gates < threshold
