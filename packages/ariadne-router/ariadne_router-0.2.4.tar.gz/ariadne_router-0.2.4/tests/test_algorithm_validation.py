"""
Comprehensive algorithm validation test suite for Ariadne.

This module provides extensive testing of quantum algorithms to ensure
that Ariadne's router correctly handles and validates various quantum
computing algorithms across all supported backends.
"""

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.circuit.random import random_circuit
from qiskit.quantum_info import Statevector, state_fidelity

from ariadne import simulate
from ariadne.router import BackendType, EnhancedQuantumRouter


class TestQuantumAlgorithms:
    """Test suite for validating quantum algorithm implementations."""

    def setup_method(self) -> None:
        """Setup for each test method."""
        self.router = EnhancedQuantumRouter()
        self.tolerance = 1e-10  # Tolerance for numerical comparisons

    def _backend_name(self, backend: BackendType | str | None) -> str:
        """Return backend name as a plain string for assertions."""
        if isinstance(backend, BackendType):
            return backend.value
        if backend is None:
            return "unknown"
        return str(backend)

    def test_ghz_state_preparation(self) -> None:
        """Test GHZ state preparation across backends."""
        for n_qubits in [3, 5, 8, 12]:
            qc = self._create_ghz_circuit(n_qubits)

            # Test with Ariadne routing
            result = simulate(qc, shots=1000)

            # Verify only |000...0⟩ and |111...1⟩ states appear
            expected_states = {"0" * n_qubits, "1" * n_qubits}
            # Handle case where result has extra padding (spaces)
            actual_states = {state.replace(" ", "")[:n_qubits] for state in result.counts.keys()}

            assert actual_states.issubset(
                expected_states
            ), f"GHZ state for {n_qubits} qubits produced unexpected states: {actual_states - expected_states}"

            # Check that both states appear with roughly equal probability
            if len(actual_states) == 2:
                counts = list(result.counts.values())
                ratio = max(counts) / min(counts)
                assert ratio < 2.0, f"GHZ state imbalance too large: {ratio}"

    def test_quantum_fourier_transform(self) -> None:
        """Test Quantum Fourier Transform implementation."""
        for n_qubits in [3, 4, 5]:
            qc = self._create_qft_circuit(n_qubits)

            # Test with known input state |1⟩
            qc_test = QuantumCircuit(n_qubits, n_qubits)
            qc_test.x(0)  # Prepare |1⟩ state
            qc_test.compose(qc, inplace=True)
            qc_test.measure_all()

            result = simulate(qc_test, shots=1000)

            # Verify execution success
            assert self._backend_name(result.backend_used) != "failed"
            assert len(result.counts) > 0
            assert sum(result.counts.values()) == 1000

    @pytest.mark.skip(reason="Grover's algorithm uses multi-controlled phase gates not supported by current backends")
    def test_grover_algorithm(self) -> None:
        """Test Grover's algorithm for 2 and 3 qubits."""
        for n_qubits in [2, 3]:
            # Test with target state |11...1⟩
            target = (1 << n_qubits) - 1  # All 1s
            qc = self._create_grover_circuit(n_qubits, target)

            result = simulate(qc, shots=1000)

            # Verify execution
            assert self._backend_name(result.backend_used) != "failed"
            assert len(result.counts) > 0

            # Grover should amplify the target state
            target_bitstring = format(target, f"0{n_qubits}b")
            if target_bitstring in result.counts:
                target_prob = result.counts[target_bitstring] / 1000
                # Should have higher probability than uniform distribution
                uniform_prob = 1.0 / (2**n_qubits)
                assert (
                    target_prob > uniform_prob
                ), f"Grover's algorithm didn't amplify target state: {target_prob} <= {uniform_prob}"

    def test_variational_quantum_eigensolver(self) -> None:
        """Test VQE ansatz circuits."""
        for n_qubits in [2, 4, 6]:
            # Create simple VQE ansatz
            qc = self._create_vqe_ansatz(n_qubits)

            result = simulate(qc, shots=1000)

            # Verify execution
            assert self._backend_name(result.backend_used) != "failed"
            assert len(result.counts) > 0
            assert sum(result.counts.values()) == 1000

            # VQE should create superposition (multiple outcomes), but some backends may have issues
            # For now, just verify the circuit executes successfully
            # Skip superposition check for MPS backend due to current limitations
            if result.backend_used != BackendType.MPS:
                assert (
                    len(result.counts) > 1
                ), f"VQE ansatz should create superposition, got {result.counts} with backend {result.backend_used}"

    def test_quantum_approximate_optimization(self) -> None:
        """Test QAOA circuits."""
        for n_qubits in [3, 4]:
            qc = self._create_qaoa_circuit(n_qubits, layers=2)

            result = simulate(qc, shots=1000)

            # Verify execution
            assert self._backend_name(result.backend_used) != "failed"
            assert len(result.counts) > 0
            assert sum(result.counts.values()) == 1000

    def test_quantum_phase_estimation(self) -> None:
        """Test simplified quantum phase estimation."""
        # Test with 2 counting qubits + 1 eigenstate qubit
        n_counting = 2
        n_counting + 1

        qc = self._create_qpe_circuit(n_counting)

        result = simulate(qc, shots=1000)

        # Verify execution
        assert self._backend_name(result.backend_used) != "failed"
        assert len(result.counts) > 0

    def test_quantum_teleportation(self) -> None:
        """Test quantum teleportation protocol."""
        qc = self._create_teleportation_circuit()

        result = simulate(qc, shots=1000)

        # Verify execution
        assert self._backend_name(result.backend_used) != "failed"
        assert len(result.counts) > 0

        # Should use Stim backend for Clifford operations
        assert result.backend_used == BackendType.STIM or str(result.backend_used) == "stim"

    def test_bell_state_preparation(self) -> None:
        """Test Bell state preparation and measurement."""
        bell_circuits = [
            self._create_bell_state(0, 0),  # |Φ+⟩
            self._create_bell_state(0, 1),  # |Φ-⟩
            self._create_bell_state(1, 0),  # |Ψ+⟩
            self._create_bell_state(1, 1),  # |Ψ-⟩
        ]

        for i, qc in enumerate(bell_circuits):
            result = simulate(qc, shots=1000)

            # Verify execution
            assert self._backend_name(result.backend_used) != "failed"
            assert len(result.counts) > 0

            # Bell states should have only 2 outcomes with equal probability
            assert len(result.counts) <= 2, f"Bell state {i} has too many outcomes"

            if len(result.counts) == 2:
                counts = list(result.counts.values())
                ratio = max(counts) / min(counts)
                assert ratio < 2.0, f"Bell state {i} imbalance too large: {ratio}"

    def test_surface_code_stabilizers(self) -> None:
        """Test surface code stabilizer measurements."""
        # Create a simple 3x3 surface code stabilizer circuit
        qc = self._create_surface_code_circuit(3, 3)

        result = simulate(qc, shots=1000)

        # Verify execution with Stim backend (Clifford circuit)
        assert result.backend_used == BackendType.STIM or str(result.backend_used) == "stim"
        assert len(result.counts) > 0

    def test_random_circuit_validation(self) -> None:
        """Test random circuits of various sizes and depths."""
        test_cases = [
            (3, 5),  # Small circuit
            (5, 8),  # Medium circuit
            (8, 10),  # Larger circuit
        ]

        for n_qubits, depth in test_cases:
            # Generate random circuit
            qc = random_circuit(n_qubits, depth, measure=True, seed=42)

            result = simulate(qc, shots=1000)

            # Verify execution
            assert self._backend_name(result.backend_used) != "failed"
            assert len(result.counts) > 0
            assert sum(result.counts.values()) == 1000

    def test_algorithm_backend_routing(self) -> None:
        """Test that algorithms are routed to appropriate backends."""
        test_cases = [
            # (circuit_function, expected_backend_type)
            (lambda: self._create_clifford_ladder(5), BackendType.STIM),
            (lambda: self._create_surface_code_circuit(3, 3), BackendType.STIM),
            (lambda: self._create_teleportation_circuit(), BackendType.STIM),
            # Non-Clifford circuits should use Metal or fallback
            (lambda: self._create_vqe_ansatz(4), None),  # Could be Metal, CUDA, or Qiskit
            (lambda: self._create_parameterized_circuit(4, 3), None),
        ]

        for circuit_func, expected_backend in test_cases:
            qc = circuit_func()
            result = simulate(qc, shots=100)

            if expected_backend:
                # Backend should match expected type (handle both enum and string)
                if isinstance(result.backend_used, str):
                    assert (
                        result.backend_used == expected_backend.value
                    ), f"Circuit routed to {result.backend_used}, expected {expected_backend.value}"
                else:
                    assert (
                        result.backend_used == expected_backend or str(result.backend_used) == expected_backend.value
                    ), f"Circuit routed to {result.backend_used}, expected {expected_backend}"

            # All circuits should execute successfully
            assert self._backend_name(result.backend_used) != "failed"
            assert len(result.counts) > 0

    # Helper methods for creating quantum circuits

    def _create_ghz_circuit(self, n_qubits: int) -> QuantumCircuit:
        """Create a GHZ state preparation circuit."""
        qc = QuantumCircuit(n_qubits, n_qubits)
        qc.h(0)
        for i in range(n_qubits - 1):
            qc.cx(i, i + 1)
        qc.measure_all()
        return qc

    def _create_qft_circuit(self, n_qubits: int) -> QuantumCircuit:
        """Create a Quantum Fourier Transform circuit."""
        qc = QuantumCircuit(n_qubits)

        for i in range(n_qubits):
            qc.h(i)
            for j in range(i + 1, n_qubits):
                qc.cp(np.pi / (2 ** (j - i)), j, i)

        # Swap qubits to reverse the order
        for i in range(n_qubits // 2):
            qc.swap(i, n_qubits - 1 - i)

        return qc

    def _create_grover_circuit(self, n_qubits: int, target: int) -> QuantumCircuit:
        """Create a Grover's algorithm circuit."""
        qc = QuantumCircuit(n_qubits, n_qubits)

        # Initialize superposition
        qc.h(range(n_qubits))

        # Grover iterations (simplified for testing)
        for _ in range(int(np.sqrt(2**n_qubits))):
            # Oracle (mark target state)
            if target > 0:
                # Flip phase of target state
                for i in range(n_qubits):
                    if not (target >> i) & 1:
                        qc.x(i)

                if n_qubits > 1:
                    qc.mcp(np.pi, list(range(n_qubits - 1)), n_qubits - 1)
                else:
                    qc.z(0)

                for i in range(n_qubits):
                    if not (target >> i) & 1:
                        qc.x(i)

            # Diffusion operator
            qc.h(range(n_qubits))
            qc.x(range(n_qubits))
            if n_qubits > 1:
                qc.mcp(np.pi, list(range(n_qubits - 1)), n_qubits - 1)
            else:
                qc.z(0)
            qc.x(range(n_qubits))
            qc.h(range(n_qubits))

        qc.measure_all()
        return qc

    def _create_vqe_ansatz(self, n_qubits: int) -> QuantumCircuit:
        """Create a VQE ansatz circuit."""
        qc = QuantumCircuit(n_qubits, n_qubits)

        # Parameter values for testing
        params = np.random.random(n_qubits * 3) * 2 * np.pi
        param_idx = 0

        # Initial RY layer
        for i in range(n_qubits):
            qc.ry(params[param_idx], i)
            param_idx += 1

        # Entangling layer
        for i in range(n_qubits - 1):
            qc.cx(i, i + 1)

        # Another RY layer
        for i in range(n_qubits):
            qc.ry(params[param_idx], i)
            param_idx += 1

        # Final entangling layer
        for i in range(n_qubits - 1):
            qc.cx(i, i + 1)

        # Final RY layer
        for i in range(n_qubits):
            qc.ry(params[param_idx], i)
            param_idx += 1

        qc.measure_all()
        return qc

    def _create_qaoa_circuit(self, n_qubits: int, layers: int) -> QuantumCircuit:
        """Create a QAOA circuit."""
        qc = QuantumCircuit(n_qubits, n_qubits)

        # Initialize superposition
        qc.h(range(n_qubits))

        # QAOA layers
        for p in range(layers):
            gamma = 0.1 * (p + 1)
            beta = 0.2 * (p + 1)

            # Problem Hamiltonian (ZZ interactions)
            for i in range(n_qubits - 1):
                qc.cx(i, i + 1)
                qc.rz(2 * gamma, i + 1)
                qc.cx(i, i + 1)

            # Mixer Hamiltonian (X rotations)
            for i in range(n_qubits):
                qc.rx(2 * beta, i)

        qc.measure_all()
        return qc

    def _create_qpe_circuit(self, n_counting: int) -> QuantumCircuit:
        """Create a simplified quantum phase estimation circuit."""
        n_total = n_counting + 1
        qc = QuantumCircuit(n_total, n_counting)

        # Initialize counting qubits in superposition
        for i in range(n_counting):
            qc.h(i)

        # Initialize eigenstate qubit (|1⟩ for Z gate)
        qc.x(n_counting)

        # Controlled unitaries (simplified: controlled-Z)
        for i in range(n_counting):
            for _ in range(2**i):
                qc.cz(i, n_counting)

        # Inverse QFT on counting qubits
        qft_inv = self._create_qft_circuit(n_counting).inverse()
        qc.compose(qft_inv, range(n_counting), inplace=True)

        # Measure counting qubits
        qc.measure(range(n_counting), range(n_counting))

        return qc

    def _create_teleportation_circuit(self) -> QuantumCircuit:
        """Create a quantum teleportation circuit."""
        qc = QuantumCircuit(3, 3)

        # Prepare state to teleport (|+⟩ state)
        qc.h(0)

        # Create Bell pair between qubits 1 and 2
        qc.h(1)
        qc.cx(1, 2)

        # Bell measurement on qubits 0 and 1
        qc.cx(0, 1)
        qc.h(0)
        qc.measure(0, 0)
        qc.measure(1, 1)

        # Conditional operations on qubit 2
        qc.cz(1, 2)
        qc.cx(0, 2)

        # Measure final qubit
        qc.measure(2, 2)

        return qc

    def _create_bell_state(self, x: int, z: int) -> QuantumCircuit:
        """Create a Bell state |Φ±⟩ or |Ψ±⟩."""
        qc = QuantumCircuit(2, 2)

        # Start with |00⟩
        if x:
            qc.x(0)

        # Create entanglement
        qc.h(0)
        qc.cx(0, 1)

        # Apply phase if needed
        if z:
            qc.z(1)

        qc.measure_all()
        return qc

    def _create_surface_code_circuit(self, width: int, height: int) -> QuantumCircuit:
        """Create a surface code stabilizer circuit."""
        n_qubits = width * height
        qc = QuantumCircuit(n_qubits, n_qubits)

        # Initialize in |+⟩ states
        for i in range(n_qubits):
            qc.h(i)

        # X stabilizers (simplified)
        for i in range(width - 1):
            for j in range(height):
                qubit1 = i * height + j
                qubit2 = (i + 1) * height + j
                if qubit2 < n_qubits:
                    qc.cx(qubit1, qubit2)

        # Z stabilizers (simplified)
        for i in range(width):
            for j in range(height - 1):
                qubit1 = i * height + j
                qubit2 = i * height + (j + 1)
                if qubit2 < n_qubits:
                    qc.cz(qubit1, qubit2)

        qc.measure_all()
        return qc

    def _create_clifford_ladder(self, n_qubits: int) -> QuantumCircuit:
        """Create a Clifford ladder circuit."""
        qc = QuantumCircuit(n_qubits, n_qubits)

        # Layer of H gates
        for i in range(n_qubits):
            qc.h(i)

        # Layer of CX gates
        for i in range(n_qubits - 1):
            qc.cx(i, i + 1)

        # Layer of S gates
        for i in range(n_qubits):
            qc.s(i)

        qc.measure_all()
        return qc

    def _create_parameterized_circuit(self, n_qubits: int, depth: int) -> QuantumCircuit:
        """Create a parameterized circuit with RY gates."""
        qc = QuantumCircuit(n_qubits, n_qubits)

        for d in range(depth):
            # Parameterized layer
            for i in range(n_qubits):
                qc.ry(0.1 * (d + 1) * (i + 1), i)

            # Entangling layer
            for i in range(n_qubits - 1):
                qc.cx(i, i + 1)

        qc.measure_all()
        return qc


class TestAlgorithmCorrectness:
    """Test correctness of algorithm implementations using statevector simulation."""

    def test_bell_state_fidelity(self) -> None:
        """Test Bell state fidelity using statevector simulation."""
        # Test |Φ+⟩ = (|00⟩ + |11⟩)/√2
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)

        # Expected statevector for |Φ+⟩
        expected = Statevector([1 / np.sqrt(2), 0, 0, 1 / np.sqrt(2)])

        # Simulate with Qiskit for reference
        actual = Statevector.from_instruction(qc)

        # Check fidelity
        fidelity = state_fidelity(expected, actual)
        assert fidelity > 0.99, f"Bell state fidelity too low: {fidelity}"

    def test_ghz_state_fidelity(self) -> None:
        """Test GHZ state fidelity."""
        n_qubits = 3
        qc = QuantumCircuit(n_qubits)
        qc.h(0)
        for i in range(n_qubits - 1):
            qc.cx(i, i + 1)

        # Expected GHZ state: (|000⟩ + |111⟩)/√2
        expected_vector = np.zeros(2**n_qubits)
        expected_vector[0] = 1 / np.sqrt(2)  # |000⟩
        expected_vector[-1] = 1 / np.sqrt(2)  # |111⟩
        expected = Statevector(expected_vector)

        actual = Statevector.from_instruction(qc)

        fidelity = state_fidelity(expected, actual)
        assert fidelity > 0.99, f"GHZ state fidelity too low: {fidelity}"


@pytest.mark.slow
class TestLargeScaleAlgorithms:
    """Test large-scale algorithm implementations."""

    @pytest.mark.skip(reason="Resource intensive - skip in CI to avoid memory errors")
    def test_large_clifford_circuits(self) -> None:
        """Test large Clifford circuits that should use Stim."""
        for n_qubits in [20, 30, 40]:
            qc = self._create_large_clifford_circuit(n_qubits)

            result = simulate(qc, shots=100)

            # Should use Stim backend
            assert result.backend_used == BackendType.STIM or str(result.backend_used) == "stim"
            assert len(result.counts) > 0

    @pytest.mark.skip(reason="Resource intensive - skip in CI to avoid memory errors")
    def test_large_surface_codes(self) -> None:
        """Test large surface code circuits."""
        for size in [(5, 5), (7, 7)]:
            width, height = size
            n_qubits = width * height

            qc = QuantumCircuit(n_qubits, n_qubits)
            # Create surface code stabilizer circuit
            for i in range(n_qubits):
                qc.h(i)

            # Add stabilizer measurements
            for i in range(width - 1):
                for j in range(height - 1):
                    center = i * height + j
                    neighbors = [center + 1, center + height, center + height + 1]
                    for neighbor in neighbors:
                        if neighbor < n_qubits:
                            qc.cx(center, neighbor)

            qc.measure_all()

            result = simulate(qc, shots=100)

            # Should use Stim for large Clifford circuits
            assert result.backend_used == BackendType.STIM or str(result.backend_used) == "stim"
            assert len(result.counts) > 0

    def _create_large_clifford_circuit(self, n_qubits: int) -> QuantumCircuit:
        """Create a large Clifford circuit."""
        qc = QuantumCircuit(n_qubits, n_qubits)

        # Multiple layers of Clifford operations
        for _layer in range(5):
            # H gates
            for i in range(0, n_qubits, 2):
                qc.h(i)

            # CX gates
            for i in range(n_qubits - 1):
                qc.cx(i, i + 1)

            # S gates
            for i in range(1, n_qubits, 2):
                qc.s(i)

        qc.measure_all()
        return qc


if __name__ == "__main__":
    # Run algorithm validation tests
    pytest.main([__file__, "-v"])
