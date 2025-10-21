"""
Quantum search algorithms in Ariadne.

This module contains quantum algorithms for unstructured search and
related problems that demonstrate quantum speedup.
"""

import numpy as np
from qiskit import QuantumCircuit

from .base import AlgorithmMetadata, QuantumAlgorithm


class GroverSearch(QuantumAlgorithm):
    """Grover's quantum search algorithm."""

    @property
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            name="Grover's Search",
            description="Quantum algorithm for unstructured search with quadratic speedup",
            category="search",
            tags=["search", "unstructured", "amplitude_amplification"],
            min_qubits=2,
            complexity="medium",
            classical_complexity="O(N)",
            quantum_advantage=True,
            educational_value="high",
            use_cases=["database search", "optimization", "cryptography"],
            references=["Grover, L.K. (1996). 'A fast quantum mechanical algorithm for database search'"],
        )

    def create_circuit(self) -> QuantumCircuit:
        """Create a Grover's search circuit."""
        circuit = QuantumCircuit(self.params.n_qubits, self.params.n_qubits)

        # Get the marked state from custom parameters (default to all |1⟩)
        marked_state = self.params.custom_params.get("marked_state", "1" * self.params.n_qubits)

        # Initialize superposition
        for i in range(self.params.n_qubits):
            circuit.h(i)

        # Calculate optimal number of iterations
        n_states = 2**self.params.n_qubits
        iterations = int(np.pi / 4 * np.sqrt(n_states))
        iterations = min(iterations, 10)  # Limit for practicality

        # Apply Grover iterations
        for _ in range(iterations):
            # Oracle: flip phase of marked state
            self._apply_oracle(circuit, marked_state)

            # Diffusion operator
            self._apply_diffusion(circuit)

        circuit.measure_all()
        return circuit

    def _apply_oracle(self, circuit: QuantumCircuit, marked_state: str) -> None:
        """Apply the oracle that flips the phase of the marked state."""
        # Convert marked state to qubit operations
        for i, bit in enumerate(marked_state):
            if bit == "0":
                circuit.x(i)

        # Multi-controlled Z gate
        if self.params.n_qubits == 2:
            circuit.cz(0, 1)
        else:
            # Use ancilla method for multi-controlled Z
            circuit.h(self.params.n_qubits - 1)
            circuit.mcx(list(range(self.params.n_qubits - 1)), self.params.n_qubits - 1)
            circuit.h(self.params.n_qubits - 1)

        # Undo the X gates
        for i, bit in enumerate(marked_state):
            if bit == "0":
                circuit.x(i)

    def _apply_diffusion(self, circuit: QuantumCircuit) -> None:
        """Apply the diffusion operator (inversion about the mean)."""
        # Apply H gates
        for i in range(self.params.n_qubits):
            circuit.h(i)

        # Apply X gates
        for i in range(self.params.n_qubits):
            circuit.x(i)

        # Multi-controlled Z
        if self.params.n_qubits == 2:
            circuit.cz(0, 1)
        else:
            circuit.h(self.params.n_qubits - 1)
            circuit.mcx(list(range(self.params.n_qubits - 1)), self.params.n_qubits - 1)
            circuit.h(self.params.n_qubits - 1)

        # Apply X gates
        for i in range(self.params.n_qubits):
            circuit.x(i)

        # Apply H gates
        for i in range(self.params.n_qubits):
            circuit.h(i)

    def _get_mathematical_background(self) -> str:
        return """
        Grover's algorithm searches an unstructured database of size N = 2^n:

        1. Initialize uniform superposition: |ψ⟩ = (1/√N) Σ_x |x⟩
        2. Apply Grover iteration G = (2|ψ⟩⟨ψ| - I)O, where O is the oracle
        3. After O(√N) iterations, measure to find marked state with high probability

        The oracle flips the phase of the marked state: O|x⟩ = (-1)^f(x)|x⟩
        The diffusion operator inverts about the mean: 2|ψ⟩⟨ψ| - I

        This provides quadratic speedup over classical O(N) search.
        """

    def _get_implementation_notes(self) -> str:
        return """
        The optimal number of iterations is approximately π/4 * √N.
        For demonstration, we limit to 10 iterations for practicality.
        The oracle marks the state |11...1⟩ by default, but can be customized.
        Multi-controlled Z gates are implemented using an ancilla qubit method.
        """


class BernsteinVazirani(QuantumAlgorithm):
    """Bernstein-Vazirani algorithm for determining a hidden string."""

    @property
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            name="Bernstein-Vazirani",
            description="Quantum algorithm for determining a hidden binary string with one query",
            category="search",
            tags=["bernstein_vazirani", "hidden_string", "oracle"],
            min_qubits=2,
            complexity="low",
            classical_complexity="O(n)",
            quantum_advantage=True,
            educational_value="high",
            use_cases=["oracle learning", "function evaluation", "algorithmic complexity"],
            references=["Bernstein, E., Vazirani, U. (1997). 'Quantum complexity theory'"],
        )

    def create_circuit(self) -> QuantumCircuit:
        """Create a Bernstein-Vazirani circuit."""
        circuit = QuantumCircuit(self.params.n_qubits, self.params.n_qubits)

        # Get the hidden string from custom parameters (default to alternating pattern)
        hidden_string = self.params.custom_params.get("hidden_string", "10" * (self.params.n_qubits // 2))
        if len(hidden_string) != self.params.n_qubits:
            hidden_string = hidden_string[: self.params.n_qubits].ljust(self.params.n_qubits, "0")

        # Initialize last qubit to |1⟩ and apply Hadamard
        circuit.x(self.params.n_qubits - 1)
        circuit.h(self.params.n_qubits - 1)

        # Apply Hadamard to input qubits
        for i in range(self.params.n_qubits - 1):
            circuit.h(i)

        # Apply oracle (inner product with hidden string)
        for i, bit in enumerate(hidden_string[:-1]):  # Exclude last qubit which is output
            if bit == "1":
                circuit.cx(i, self.params.n_qubits - 1)

        # Apply Hadamard to input qubits
        for i in range(self.params.n_qubits - 1):
            circuit.h(i)

        circuit.measure_all()
        return circuit

    def _get_mathematical_background(self) -> str:
        return """
        The Bernstein-Vazirani algorithm determines an unknown n-bit string s
        given access to an oracle function f(x) = s·x (mod 2):

        Classical approach requires n queries to determine s
        Quantum approach determines s with a single query

        The circuit implements:
        1. Prepare state |0⟩^⊗(n-1)|1⟩
        2. Apply H^⊗n to create superposition
        3. Apply oracle implementing f(x) = s·x via CNOTs
        4. Apply H^⊗(n-1) to extract s

        Measurement of the first n-1 qubits yields the hidden string s.
        """

    def _get_implementation_notes(self) -> str:
        return """
        The algorithm uses n qubits: n-1 input qubits and 1 output qubit.
        The hidden string is encoded as CNOT gates from input to output qubit.
        By default, uses alternating "10" pattern, but can be customized.
        The algorithm achieves linear speedup: 1 query vs n classical queries.
        """
