"""
Quantum optimization algorithms in Ariadne.

This module contains variational quantum algorithms for optimization
problems, including QAOA and VQE.
"""

import numpy as np
from qiskit import QuantumCircuit

from .base import AlgorithmMetadata, QuantumAlgorithm


class QAOA(QuantumAlgorithm):
    """Quantum Approximate Optimization Algorithm."""

    @property
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            name="QAOA",
            description="Quantum Approximate Optimization Algorithm for combinatorial optimization",
            category="optimization",
            tags=["qaoa", "optimization", "variational", "maxcut"],
            min_qubits=3,
            complexity="high",
            classical_complexity="NP-hard",
            quantum_advantage=True,
            educational_value="high",
            use_cases=["MaxCut", "graph coloring", "portfolio optimization", "scheduling"],
            references=["Farhi, E., Goldstone, J., Gutmann, S. (2014). 'A Quantum Approximate Optimization Algorithm'"],
        )

    def create_circuit(self) -> QuantumCircuit:
        """Create a QAOA circuit for MaxCut problem."""
        circuit = QuantumCircuit(self.params.n_qubits, self.params.n_qubits)

        # Get QAOA parameters
        p = self.params.custom_params.get("layers", 2)  # Number of QAOA layers
        gamma = self.params.custom_params.get("gamma", [0.5] * p)  # Problem unitary parameters
        beta = self.params.custom_params.get("beta", [0.3] * p)  # Mixer unitary parameters

        # Ensure parameter lists have correct length
        if len(gamma) < p:
            gamma = gamma + [0.5] * (p - len(gamma))
        if len(beta) < p:
            beta = beta + [0.3] * (p - len(beta))

        # Initialize superposition
        for i in range(self.params.n_qubits):
            circuit.h(i)

        # Apply QAOA layers
        for layer in range(p):
            # Problem Hamiltonian (MaxCut on ring graph)
            self._apply_problem_hamiltonian(circuit, gamma[layer])

            # Mixer Hamiltonian
            self._apply_mixer_hamiltonian(circuit, beta[layer])

        circuit.measure_all()
        return circuit

    def _apply_problem_hamiltonian(self, circuit: QuantumCircuit, gamma: float) -> None:
        """Apply the problem Hamiltonian for MaxCut on a ring graph."""
        # Ring graph: each qubit connected to next, last connected to first
        for i in range(self.params.n_qubits):
            j = (i + 1) % self.params.n_qubits
            circuit.cx(i, j)
            circuit.rz(2 * gamma, j)
            circuit.cx(i, j)

    def _apply_mixer_hamiltonian(self, circuit: QuantumCircuit, beta: float) -> None:
        """Apply the mixer Hamiltonian."""
        for i in range(self.params.n_qubits):
            circuit.rx(2 * beta, i)

    def _get_mathematical_background(self) -> str:
        return """
        QAOA approximates solutions to combinatorial optimization problems:

        For MaxCut problem on graph G = (V, E):
        - Problem Hamiltonian: C = Σ_(i,j)∈E (1 - Z_i Z_j)/2
        - Mixer Hamiltonian: B = Σ_i X_i

        QAOA prepares state: |β, γ⟩ = e^(-iβ_p B) e^(-iγ_p C) ... e^(-iβ_1 B) e^(-iγ_1 C) |+⟩^⊗n

        Parameters (β, γ) are optimized classically to maximize expectation value ⟨C⟩.
        Depth p controls approximation quality vs circuit complexity.
        """

    def _get_implementation_notes(self) -> str:
        return """
        This implementation solves MaxCut on a ring graph for simplicity.
        The problem Hamiltonian implements edge weights using CNOT-RZ-CNOT sequences.
        Default parameters are illustrative; in practice, they require classical optimization.
        The circuit depth is 2p layers, with p being the number of QAOA layers.
        """


class VQE(QuantumAlgorithm):
    """Variational Quantum Eigensolver."""

    @property
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            name="VQE",
            description="Variational Quantum Eigensolver for finding ground state energies",
            category="optimization",
            tags=["vqe", "eigensolver", "variational", "chemistry"],
            min_qubits=2,
            complexity="high",
            classical_complexity="Exponential",
            quantum_advantage=True,
            educational_value="high",
            use_cases=["quantum chemistry", "materials science", "optimization"],
            references=[
                "Peruzzo, A., et al. (2014). 'A variational eigenvalue solver on a photonic quantum processor'"
            ],
        )

    def create_circuit(self) -> QuantumCircuit:
        """Create a VQE ansatz circuit."""
        circuit = QuantumCircuit(self.params.n_qubits, self.params.n_qubits)

        # Get VQE parameters
        depth = self.params.custom_params.get("depth", 2)  # Ansatz depth
        use_hardware_efficient = self.params.custom_params.get("hardware_efficient", True)

        if use_hardware_efficient:
            self._create_hardware_efficient_ansatz(circuit, depth)
        else:
            self._create_chemistry_ansatz(circuit, depth)

        circuit.measure_all()
        return circuit

    def _create_hardware_efficient_ansatz(self, circuit: QuantumCircuit, depth: int) -> None:
        """Create a hardware-efficient ansatz."""
        # Initial state preparation
        for i in range(self.params.n_qubits):
            circuit.h(i)

        # Variational layers
        for _layer in range(depth):
            # Entangling layer (nearest-neighbor)
            for i in range(0, self.params.n_qubits - 1, 2):
                circuit.cx(i, i + 1)

            # Single-qubit rotations (fixed parameters for demonstration)
            for i in range(self.params.n_qubits):
                circuit.ry(np.pi / 4, i)  # Fixed parameter
                circuit.rz(np.pi / 6, i)  # Fixed parameter

            # Second entangling layer (next-nearest-neighbor)
            for i in range(1, self.params.n_qubits - 1, 2):
                circuit.cx(i, i + 1)

    def _create_chemistry_ansatz(self, circuit: QuantumCircuit, depth: int) -> None:
        """Create a UCCSD-inspired ansatz for quantum chemistry."""
        # Hartree-Fock state preparation (simplified)
        for i in range(0, min(self.params.n_qubits // 2, 4), 2):
            circuit.x(i)

        # UCC-inspired excitations (simplified)
        for _layer in range(depth):
            # Single excitations
            for i in range(0, self.params.n_qubits - 1, 2):
                circuit.ry(0.1, i)
                circuit.ry(0.1, i + 1)
                circuit.cx(i, i + 1)
                circuit.rz(0.2, i + 1)
                circuit.cx(i, i + 1)

            # Double excitations (simplified)
            for i in range(0, self.params.n_qubits - 3, 4):
                if i + 3 < self.params.n_qubits:
                    circuit.cx(i, i + 2)
                    circuit.cx(i + 1, i + 3)
                    circuit.rz(0.15, i + 3)
                    circuit.cx(i + 1, i + 3)
                    circuit.cx(i, i + 2)

    def _get_mathematical_background(self) -> str:
        return """
        VQE finds the ground state energy of a Hamiltonian H:

        1. Prepare parameterized quantum state |ψ(θ)⟩ = U(θ)|0⟩
        2. Measure expectation value E(θ) = ⟨ψ(θ)|H|ψ(θ)⟩
        3. Classically optimize parameters θ to minimize E(θ)

        The variational principle guarantees: E(θ) ≥ E_0 (ground state energy)

        Common ansätze:
        - Hardware-efficient: native gates, shallow depth
        - UCCSD: chemically motivated, good for molecular systems
        - Problem-specific: tailored to Hamiltonian structure
        """

    def _get_implementation_notes(self) -> str:
        return """
        This implementation uses fixed parameters for demonstration.
        In practice, parameters require classical optimization using:
        - Gradient descent
        - SPSA (Simultaneous Perturbation Stochastic Approximation)
        - Natural gradient descent

        The hardware-efficient ansatz uses native gates with linear connectivity.
        The chemistry ansatz simulates UCCSD excitations for molecular systems.
        """
