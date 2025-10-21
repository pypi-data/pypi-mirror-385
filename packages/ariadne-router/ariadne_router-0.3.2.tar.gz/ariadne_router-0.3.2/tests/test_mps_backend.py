from __future__ import annotations

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

# Assuming MPSBackend is importable from the source path
from ariadne.backends.mps_backend import MPSBackend


class TestMPSBackendRigor:
    """
    Rigorously tests the core simulation capabilities of the MPSBackend.
    Focuses on correctness, entanglement handling, and robustness against truncation.
    """

    @pytest.fixture(scope="class")
    def backend(self: TestMPSBackendRigor) -> MPSBackend:
        """Fixture to provide a fresh MPSBackend instance."""
        return MPSBackend()

    def test_mps_simulates_bell_state_phi_plus(self, backend: MPSBackend) -> None:
        """
        Test 1: Verifies correct simulation of the maximally entangled Bell state |Φ+⟩.
        Circuit: H(0), CNOT(0, 1). Expected state: (|00⟩ + |11⟩) / √2.
        This confirms basic gate application, entanglement generation, and state representation fidelity.
        """
        num_qubits = 2
        qc = QuantumCircuit(num_qubits)
        qc.h(0)
        qc.cx(0, 1)

        # Calculate the reference state vector using Qiskit's simulator
        reference_state = Statevector(qc)
        expected_probabilities = reference_state.probabilities_dict()

        # Simulate using the MPS backend - returns counts dictionary
        counts = backend.simulate(qc, shots=1000)

        # Assertions for correctness - check that we get counts for |00⟩ and |11⟩
        assert len(counts) == 2, f"Expected 2 outcomes, got {len(counts)}"
        assert "00" in counts, "|00⟩ state not found in counts"
        assert "11" in counts, "|11⟩ state not found in counts"

        # Ensure non-zero probability states are represented in counts
        for state, probability in expected_probabilities.items():
            if probability > 0:
                assert state in counts, f"Expected state {state} missing from counts"

        # Check that counts are roughly equal (within 20% tolerance for 1000 shots)
        count_00 = counts.get("00", 0)
        count_11 = counts.get("11", 0)
        total = count_00 + count_11
        assert total == 1000, f"Expected total shots of 1000, got {total}"
        assert abs(count_00 - count_11) < 200, f"Counts imbalance too large: |00⟩={count_00}, |11⟩={count_11}"

    def test_mps_simulates_low_entanglement_product_state(self, backend: MPSBackend) -> None:
        """
        Test 2: Verifies correct simulation of a low-entanglement product state (separable state).
        Circuit: RZ(π/2) on 0, X on 1, H on 2 (3 qubits).
        This ensures the MPS representation correctly handles separable states where bond dimension D=1 is sufficient.
        """
        num_qubits = 3
        qc = QuantumCircuit(num_qubits)
        qc.rz(np.pi / 2, 0)
        qc.x(1)
        qc.h(2)

        # Calculate reference probabilities
        reference_state = Statevector(qc)
        reference_probs = reference_state.probabilities()

        # Simulate using the MPS backend
        counts = backend.simulate(qc, shots=5000)

        # Convert counts to empirical probabilities
        total_shots = sum(counts.values())
        empirical_probs = np.zeros(2**num_qubits)

        for bitstring, count in counts.items():
            idx = int(bitstring, 2)
            empirical_probs[idx] = count / total_shots

        # Check that empirical probabilities match reference within reasonable tolerance
        for i, (emp_prob, ref_prob) in enumerate(zip(empirical_probs, reference_probs, strict=False)):
            if ref_prob > 0.1:  # Only check significant probabilities
                assert (
                    abs(emp_prob - ref_prob) < 0.1
                ), f"Probability mismatch for state {i:03b}: empirical={emp_prob:.4f}, reference={ref_prob:.4f}"

    def test_mps_handles_high_entanglement_with_truncation(self) -> None:
        """
        Test 3: Checks robustness when simulating a highly entangled circuit (e.g., deep GHZ-like)
        with a severely restricted maximum bond dimension (D=2).
        The test ensures the simulation runs without error and produces counts,
        demonstrating the backend's ability to handle truncation gracefully.
        """
        num_qubits = 6
        qc = QuantumCircuit(num_qubits)

        # Create a highly entangled circuit
        for i in range(num_qubits):
            qc.h(i)
        for i in range(num_qubits - 1):
            qc.cx(i, i + 1)
        for i in range(num_qubits):
            qc.rx(0.5, i)

        # Create backend with low bond dimension to test truncation
        backend_low_bond = MPSBackend(max_bond_dimension=2)

        # Simulate using the MPS backend with truncation - should not raise an error
        counts = backend_low_bond.simulate(qc, shots=100)

        # Assertions for robustness
        assert counts is not None, "Simulation failed to return counts."
        total_shots = sum(counts.values())
        assert total_shots == 100, f"Expected 100 shots, got {total_shots}"
