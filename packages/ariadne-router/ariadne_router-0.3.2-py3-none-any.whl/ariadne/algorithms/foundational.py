"""
Foundational quantum algorithms in Ariadne.

This module contains basic quantum algorithms that form the foundation
for quantum computing education and research.
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT

from .base import AlgorithmMetadata, QuantumAlgorithm


class BellState(QuantumAlgorithm):
    """Bell state preparation algorithm."""

    @property
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            name="Bell State",
            description="Creates a maximally entangled two-qubit Bell state",
            category="foundational",
            tags=["entanglement", "bell", "basic"],
            min_qubits=2,
            max_qubits=2,
            complexity="low",
            quantum_advantage=True,
            educational_value="high",
            use_cases=["quantum cryptography", "teleportation", "entanglement studies"],
            references=["Bell, J.S. (1964). 'On the Einstein Podolsky Rosen paradox'"],
        )

    def create_circuit(self) -> QuantumCircuit:
        """Create a Bell state circuit."""
        if self.params.n_qubits != 2:
            raise ValueError("Bell state requires exactly 2 qubits")

        circuit = QuantumCircuit(self.params.n_qubits, self.params.n_qubits)

        # Create Bell state |Φ+⟩ = (|00⟩ + |11⟩)/√2
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.measure_all()

        return circuit

    def _get_mathematical_background(self) -> str:
        return """
        The Bell state |Φ+⟩ is created by applying a Hadamard gate to the first qubit
        followed by a CNOT gate with the first qubit as control and second as target:

        |00⟩ --H--> (|0⟩ + |1⟩)/√2 --CNOT--> (|00⟩ + |11⟩)/√2 = |Φ+⟩

        This creates a maximally entangled state where measuring one qubit
        instantly determines the state of the other, regardless of distance.
        """


class GHZState(QuantumAlgorithm):
    """GHZ state preparation algorithm."""

    @property
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            name="GHZ State",
            description="Creates a Greenberger-Horne-Zeilinger (GHZ) entangled state",
            category="foundational",
            tags=["entanglement", "ghz", "multi-qubit"],
            min_qubits=3,
            complexity="low",
            quantum_advantage=True,
            educational_value="high",
            use_cases=["quantum networks", "distributed quantum computing", "multipartite entanglement"],
            references=["Greenberger, D.M., Horne, M.A., Zeilinger, A. (1989). 'Going beyond Bell's theorem'"],
        )

    def create_circuit(self) -> QuantumCircuit:
        """Create a GHZ state circuit."""
        circuit = QuantumCircuit(self.params.n_qubits, self.params.n_qubits)

        # Create GHZ state |000...⟩ + |111...⟩)/√2
        circuit.h(0)
        for i in range(1, self.params.n_qubits):
            circuit.cx(0, i)
        circuit.measure_all()

        return circuit

    def _get_mathematical_background(self) -> str:
        return """
        The GHZ state generalizes the Bell state to multiple qubits:

        1. Apply Hadamard to first qubit: |0...0⟩ → (|0...0⟩ + |1...0⟩)/√2
        2. Apply CNOT from first qubit to all others: (|0...0⟩ + |1...1⟩)/√2

        This creates a multipartite entangled state that demonstrates
        quantum non-locality beyond what's possible with Bell states.
        """


class QuantumFourierTransform(QuantumAlgorithm):
    """Quantum Fourier Transform algorithm."""

    @property
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            name="Quantum Fourier Transform",
            description="Implements the Quantum Fourier Transform for quantum signal processing",
            category="foundational",
            tags=["qft", "fourier", "signal_processing"],
            min_qubits=2,
            complexity="medium",
            classical_complexity="O(N log N)",
            quantum_advantage=True,
            educational_value="high",
            use_cases=["phase estimation", "shor's algorithm", "quantum signal processing"],
            references=["Coppersmith, D. (1994). 'An approximate Fourier transform useful in quantum factoring'"],
        )

    def create_circuit(self) -> QuantumCircuit:
        """Create a QFT circuit."""
        circuit = QuantumCircuit(self.params.n_qubits, self.params.n_qubits)

        # Apply QFT using Qiskit's library
        qft = QFT(self.params.n_qubits)
        circuit.compose(qft, inplace=True)

        # Add measurements for educational purposes
        circuit.measure_all()

        return circuit

    def _get_mathematical_background(self) -> str:
        return """
        The Quantum Fourier Transform is the quantum analogue of the discrete Fourier transform:

        QFT|x⟩ = (1/√N) Σ_y e^(2πixy/N) |y⟩

        where N = 2^n for n qubits. The circuit consists of:
        1. Hadamard gate on each qubit
        2. Controlled phase rotations with angles π/2, π/4, ..., π/2^(n-1)
        3. Swap gates to reverse qubit order

        QFT achieves exponential speedup over classical FFT and is a key
        component in many quantum algorithms including Shor's factoring.
        """

    def _get_implementation_notes(self) -> str:
        return """
        The QFT circuit depth is O(n²) with O(n²) two-qubit gates.
        For large n, approximate QFT can be used by omitting small-angle
        rotations, reducing depth to O(n log n) with minimal error.
        """


class QuantumPhaseEstimation(QuantumAlgorithm):
    """Quantum Phase Estimation algorithm."""

    @property
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            name="Quantum Phase Estimation",
            description="Estimates the eigenphase of a unitary operator",
            category="foundational",
            tags=["qpe", "phase_estimation", "eigenvalue"],
            min_qubits=3,
            complexity="high",
            classical_complexity="O(1/ε)",
            quantum_advantage=True,
            educational_value="high",
            use_cases=["quantum chemistry", "factoring", "quantum simulation"],
            references=["Kitaev, A.Y. (1995). 'Quantum measurements and the Abelian Stabilizer Problem'"],
        )

    def create_circuit(self) -> QuantumCircuit:
        """Create a QPE circuit."""
        # For QPE, we need estimation qubits + target qubit
        # Use first n-1 qubits for estimation, last qubit as target
        n_estimation = self.params.n_qubits - 1
        if n_estimation < 1:
            raise ValueError("QPE requires at least 2 qubits (1 estimation + 1 target)")

        circuit = QuantumCircuit(self.params.n_qubits, self.params.n_qubits)

        # Initialize target qubit to |1⟩ (eigenstate of Z with eigenvalue -1)
        circuit.x(self.params.n_qubits - 1)

        # Apply Hadamard to estimation qubits
        for i in range(n_estimation):
            circuit.h(i)

        # Apply controlled unitary operations
        # For demonstration, use Z gate as the unitary
        for i in range(n_estimation):
            repetitions = 2**i
            for _ in range(repetitions):
                circuit.cp(np.pi, i, self.params.n_qubits - 1)  # Controlled-Z rotation

        # Apply inverse QFT to estimation qubits
        circuit.append(QFT(n_estimation).inverse(), range(n_estimation))

        # Measure all qubits
        circuit.measure_all()

        return circuit

    def _get_mathematical_background(self) -> str:
        return """
        Quantum Phase Estimation finds the eigenphase φ of a unitary U:
        U|ψ⟩ = e^(2πiφ)|ψ⟩

        The algorithm uses:
        1. n estimation qubits initialized to |0⟩^⊗n
        2. Target qubit prepared in eigenstate |ψ⟩
        3. Controlled-U^(2^k) operations creating phase kickback
        4. Inverse QFT to extract binary representation of φ

        The measurement yields an n-bit approximation of φ with precision 2^(-n).
        """

    def _get_implementation_notes(self) -> str:
        return """
        QPE requires implementing controlled-U^(2^k) operations.
        For demonstration, we use Z gate as U, giving phase φ = 0.5.
        In practice, U could be any unitary with known eigenstates.
        The accuracy improves exponentially with the number of estimation qubits.
        """
