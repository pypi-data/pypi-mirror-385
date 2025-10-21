"""Test suite for backend implementations."""

import pytest
from qiskit import QuantumCircuit

from ariadne import BackendType, simulate
from ariadne.backends.cuda_backend import CUDABackend, is_cuda_available


class TestCUDABackend:
    """Test CUDA backend functionality."""

    def test_cuda_availability(self) -> None:
        """Test CUDA availability detection."""
        available = is_cuda_available()
        assert isinstance(available, bool)

    def test_cuda_backend_cpu_fallback(self) -> None:
        """Test CPU fallback works correctly."""
        backend = CUDABackend(allow_cpu_fallback=True)

        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure_all()

        result = backend.simulate(qc, shots=100)
        assert isinstance(result, dict)
        assert sum(result.values()) == 100

    def test_cuda_backend_basic_gates(self) -> None:
        """Test basic quantum gates."""
        backend = CUDABackend()

        # Test X gate
        qc = QuantumCircuit(1)
        qc.x(0)
        qc.measure_all()
        result = backend.simulate(qc, shots=100)
        assert result == {"1": 100}

        # Test Hadamard
        qc = QuantumCircuit(1)
        qc.h(0)
        qc.measure_all()
        result = backend.simulate(qc, shots=1000)
        # Should be roughly 50/50
        assert 400 < result.get("0", 0) < 600
        assert 400 < result.get("1", 0) < 600

    def test_cuda_backend_entanglement(self) -> None:
        """Test entangled states."""
        backend = CUDABackend()

        # Bell state
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure_all()

        result = backend.simulate(qc, shots=1000)
        assert set(result.keys()).issubset({"00", "11"})
        # Should be roughly 50/50
        assert 400 < result.get("00", 0) < 600
        assert 400 < result.get("11", 0) < 600

    @pytest.mark.skipif(not is_cuda_available(), reason="CUDA not available")
    def test_cuda_backend_gpu_mode(self) -> None:
        """Test GPU execution mode."""
        backend = CUDABackend(prefer_gpu=True, allow_cpu_fallback=False)
        assert backend.backend_mode == "cuda"

        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure_all()

        result = backend.simulate(qc, shots=100)
        assert sum(result.values()) == 100

    def test_cuda_backend_statevector(self) -> None:
        """Test statevector simulation."""
        backend = CUDABackend()

        qc = QuantumCircuit(2)
        qc.h(0)

        statevector, measured_qubits = backend.simulate_statevector(qc)

        # Check statevector shape
        assert len(statevector) == 4  # 2^2

        # Check normalization
        import numpy as np

        norm = np.sum(np.abs(statevector) ** 2)
        assert abs(norm - 1.0) < 1e-10

    def test_cuda_backend_large_circuit(self) -> None:
        """Test larger circuit simulation."""
        backend = CUDABackend()

        # 10-qubit GHZ state
        qc = QuantumCircuit(10)
        qc.h(0)
        for i in range(1, 10):
            qc.cx(0, i)
        qc.measure_all()

        result = backend.simulate(qc, shots=1000)
        assert set(result.keys()).issubset({"0000000000", "1111111111"})


class TestBackendIntegration:
    """Test backend integration with main API."""

    def test_backend_selection_clifford(self) -> None:
        """Test Clifford circuits select appropriate backend."""
        qc = QuantumCircuit(5)
        for i in range(5):
            qc.h(i)
        for i in range(4):
            qc.cx(i, i + 1)
        qc.measure_all()

        result = simulate(qc, shots=100)
        assert result.backend_used == BackendType.STIM

    def test_backend_selection_general(self) -> None:
        """Test general circuits select appropriate backend."""
        qc = QuantumCircuit(3)
        qc.h(0)
        qc.t(1)  # Non-Clifford
        qc.cx(0, 1)
        qc.measure_all()

        result = simulate(qc, shots=100)
        assert result.backend_used in [
            BackendType.QISKIT,
            BackendType.CUDA,
            BackendType.TENSOR_NETWORK,
            BackendType.JAX_METAL,
            BackendType.MPS,
            BackendType.CIRQ,
            BackendType.PENNYLANE,
            BackendType.QULACS,
        ]

    def test_forced_backend_override(self) -> None:
        """Test forcing specific backend works."""
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure_all()

        # This is a Clifford circuit, but force Qiskit
        result = simulate(qc, shots=100, backend="qiskit")
        assert result.backend_used == BackendType.QISKIT

    def test_invalid_backend_error(self) -> None:
        """Test error handling for invalid backend."""
        qc = QuantumCircuit(1)
        qc.h(0)
        qc.measure_all()

        with pytest.raises(ValueError, match="Unknown backend"):
            simulate(qc, backend="invalid_backend")


class TestBackendConsistency:
    """Test consistency across backends."""

    def test_deterministic_circuit_consistency(self) -> None:
        """Test all backends give same results for deterministic circuits."""
        qc = QuantumCircuit(3)
        qc.x(0)
        qc.x(2)
        qc.measure_all()

        backends = ["qiskit"]
        if is_cuda_available():
            backends.append("cuda")

        results = {}
        for backend in backends:
            result = simulate(qc, shots=100, backend=backend)
            results[backend] = result.counts

        # All should give '101'
        for _backend, counts in results.items():
            assert counts == {"101": 100}

    def test_bell_state_consistency(self) -> None:
        """Test Bell state preparation is consistent."""
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure_all()

        backends = ["qiskit"]
        if is_cuda_available():
            backends.append("cuda")

        for backend in backends:
            result = simulate(qc, shots=1000, backend=backend)
            counts = result.counts

            # Should only see 00 and 11
            assert set(counts.keys()).issubset({"00", "11"})

            # Roughly equal probabilities
            if "00" in counts:
                assert 400 < counts["00"] < 600
            if "11" in counts:
                assert 400 < counts["11"] < 600
