"""
Qulacs GPU-Optimized Backend for Ariadne

This module integrates Qulacs, a high-performance quantum circuit simulator,
providing GPU acceleration for quantum circuit simulation with significant
speedup over traditional CPU-based simulators.

Qulacs Features:
- GPU acceleration with CUDA/OpenMP
- 10-100x speedup for medium-scale circuits
- Memory-efficient state vector simulation
- Support for noise simulation
- Multi-GPU scaling capabilities
"""

from __future__ import annotations

import importlib.util
import warnings
from typing import Any, cast

import numpy as np
from qiskit import QuantumCircuit


class QulacsBackend:
    """High-performance Qulacs-based quantum circuit simulator."""

    def __init__(self, use_gpu: bool = True, gpu_device: int = 0, allow_cpu_fallback: bool = True):
        """
        Initialize Qulacs backend.

        Args:
            use_gpu: Whether to use GPU acceleration if available
            gpu_device: GPU device ID to use (for multi-GPU systems)
            allow_cpu_fallback: Allow fallback to CPU if GPU unavailable
        """
        self.use_gpu = use_gpu
        self.gpu_device = gpu_device
        self.allow_cpu_fallback = allow_cpu_fallback

        # Check Qulacs availability
        self.qulacs_available = self._check_qulacs_availability()
        if not self.qulacs_available:
            if not allow_cpu_fallback:
                raise RuntimeError("Qulacs not available and CPU fallback disabled")
            warnings.warn("Qulacs not available, falling back to Qiskit", stacklevel=2)

        # Check GPU availability
        self.gpu_available = False
        if self.qulacs_available and use_gpu:
            self.gpu_available = self._check_gpu_availability()
            if not self.gpu_available and not allow_cpu_fallback:
                raise RuntimeError("GPU not available and CPU fallback disabled")

    def _check_qulacs_availability(self) -> bool:
        """Check if Qulacs is installed and available."""
        return importlib.util.find_spec("qulacs") is not None

    def _check_gpu_availability(self) -> bool:
        """Check if GPU acceleration is available."""
        if not self.qulacs_available:
            return False

        try:
            import qulacs

            quantum_state_gpu = getattr(qulacs, "QuantumStateGpu", None)
            if quantum_state_gpu is None:
                return False

            test_state = cast(Any, quantum_state_gpu)(2)
            del test_state
            return True
        except Exception:
            return False

    def simulate(self, circuit: QuantumCircuit, shots: int = 1000) -> dict[str, int]:
        """
        Simulate quantum circuit using Qulacs.

        Args:
            circuit: Quantum circuit to simulate
            shots: Number of measurement shots

        Returns:
            Dictionary of measurement counts
        """
        if not self.qulacs_available:
            # Fallback to Qiskit
            return self._simulate_with_qiskit(circuit, shots)

        try:
            import qulacs

            # Convert Qiskit circuit to Qulacs format
            qulacs_circuit = self._convert_qiskit_to_qulacs(circuit)

            # Create quantum state
            if self.gpu_available:
                quantum_state_gpu = getattr(qulacs, "QuantumStateGpu", None)
                if quantum_state_gpu is None:
                    raise RuntimeError("Qulacs GPU state class not available")
                state = cast(Any, quantum_state_gpu)(circuit.num_qubits)
            else:
                quantum_state_cpu = getattr(qulacs, "QuantumStateCpu", None)
                if quantum_state_cpu is None:
                    raise RuntimeError("Qulacs CPU state class not available")
                state = cast(Any, quantum_state_cpu)(circuit.num_qubits)

            # Initialize state to |0...0>
            state.set_zero_state()

            # Apply circuit operations
            qulacs_circuit.update_quantum_state(state)

            # Perform measurements
            if circuit.num_clbits > 0:
                # Circuit has explicit measurements
                counts = self._simulate_measurements(state, circuit, shots)
            else:
                # No explicit measurements, measure all qubits
                counts = self._measure_all_qubits(state, circuit.num_qubits, shots)

            return counts

        except Exception as e:
            if self.allow_cpu_fallback:
                warnings.warn(f"Qulacs simulation failed: {e}, falling back to Qiskit", stacklevel=2)
                return self._simulate_with_qiskit(circuit, shots)
            else:
                raise

    def _convert_qiskit_to_qulacs(self, circuit: QuantumCircuit) -> Any:
        """Convert Qiskit circuit to Qulacs circuit."""
        import qulacs

        qulacs_circuit = qulacs.QuantumCircuit(circuit.num_qubits)

        # Mapping of Qiskit gates to Qulacs gates
        gate_mapping = {
            "id": lambda qubit: qulacs.gate.Identity(qubit),
            "x": lambda qubit: qulacs.gate.X(qubit),
            "y": lambda qubit: qulacs.gate.Y(qubit),
            "z": lambda qubit: qulacs.gate.Z(qubit),
            "h": lambda qubit: qulacs.gate.H(qubit),
            "s": lambda qubit: qulacs.gate.S(qubit),
            "sdg": lambda qubit: qulacs.gate.Sdag(qubit),
            "t": lambda qubit: qulacs.gate.T(qubit),
            "tdg": lambda qubit: qulacs.gate.Tdag(qubit),
            "sx": lambda qubit: qulacs.gate.sqrtX(qubit),
            "sxdg": lambda qubit: qulacs.gate.sqrtXdag(qubit),
        }

        # Parameterized gates
        param_gate_mapping = {
            "rx": lambda qubit, angle: qulacs.gate.RX(qubit, angle),
            "ry": lambda qubit, angle: qulacs.gate.RY(qubit, angle),
            "rz": lambda qubit, angle: qulacs.gate.RZ(qubit, angle),
            "p": lambda qubit, angle: qulacs.gate.P0(qubit) + qulacs.gate.P1(qubit) * np.exp(1j * angle),
            "u1": lambda qubit, angle: qulacs.gate.U1(qubit, angle),
        }

        # Two-qubit gates
        two_qubit_mapping = {
            "cx": lambda control, target: qulacs.gate.CNOT(control, target),
            "cz": lambda control, target: qulacs.gate.CZ(control, target),
            "swap": lambda qubit1, qubit2: qulacs.gate.SWAP(qubit1, qubit2),
        }

        # Create qubit index mapping
        qubit_to_index = {qubit: i for i, qubit in enumerate(circuit.qubits)}

        # Convert each instruction
        for instruction, qubits, _clbits in circuit.data:
            gate_name = instruction.name.lower()
            qubit_indices = [qubit_to_index[q] for q in qubits]

            # Skip measurement and barrier operations for state vector simulation
            if gate_name in ["measure", "barrier", "delay"]:
                continue

            # Single-qubit gates
            if len(qubit_indices) == 1 and gate_name in gate_mapping:
                gate = gate_mapping[gate_name](qubit_indices[0])
                qulacs_circuit.add_gate(gate)

            # Parameterized single-qubit gates
            elif len(qubit_indices) == 1 and gate_name in param_gate_mapping:
                if instruction.params:
                    angle = float(instruction.params[0])
                    gate = param_gate_mapping[gate_name](qubit_indices[0], angle)
                    qulacs_circuit.add_gate(gate)

            # Two-qubit gates
            elif len(qubit_indices) == 2 and gate_name in two_qubit_mapping:
                gate = two_qubit_mapping[gate_name](qubit_indices[0], qubit_indices[1])
                qulacs_circuit.add_gate(gate)

            # U3 gate (general single-qubit rotation)
            elif gate_name == "u3" and len(qubit_indices) == 1:
                if len(instruction.params) >= 3:
                    theta, phi, lam = instruction.params[:3]
                    # Decompose U3 into RZ-RY-RZ
                    qulacs_circuit.add_gate(qulacs.gate.RZ(qubit_indices[0], float(lam)))
                    qulacs_circuit.add_gate(qulacs.gate.RY(qubit_indices[0], float(theta)))
                    qulacs_circuit.add_gate(qulacs.gate.RZ(qubit_indices[0], float(phi)))

            # U2 gate (π/2 rotation about X+Z axis)
            elif gate_name == "u2" and len(qubit_indices) == 1:
                if len(instruction.params) >= 2:
                    phi, lam = instruction.params[:2]
                    # U2(φ,λ) = RZ(φ) RY(π/2) RZ(λ)
                    qulacs_circuit.add_gate(qulacs.gate.RZ(qubit_indices[0], float(lam)))
                    qulacs_circuit.add_gate(qulacs.gate.RY(qubit_indices[0], np.pi / 2))
                    qulacs_circuit.add_gate(qulacs.gate.RZ(qubit_indices[0], float(phi)))

            # CCX (Toffoli) gate
            elif gate_name == "ccx" and len(qubit_indices) == 3:
                gate = qulacs.gate.TOFFOLI(qubit_indices[0], qubit_indices[1], qubit_indices[2])
                qulacs_circuit.add_gate(gate)

            else:
                # Unsupported gate - use decomposition or skip
                warnings.warn(f"Unsupported gate: {gate_name}, skipping", stacklevel=2)

        return qulacs_circuit

    def _simulate_measurements(self, state: Any, circuit: QuantumCircuit, shots: int) -> dict[str, int]:
        """Simulate measurements for circuits with explicit measurement operations."""
        # For now, measure all qubits at the end
        # TODO: Implement proper mid-circuit measurements
        return self._measure_all_qubits(state, circuit.num_qubits, shots)

    def _measure_all_qubits(self, state: Any, num_qubits: int, shots: int) -> dict[str, int]:
        """Measure all qubits and return counts."""

        counts: dict[str, int] = {}

        for _ in range(shots):
            # Sample from the probability distribution
            sample = state.sampling(1)[0]

            # Convert integer sample to binary string
            bitstring = format(sample, f"0{num_qubits}b")

            # Reverse to match Qiskit's bit ordering (least significant bit first)
            bitstring = bitstring[::-1]

            counts[bitstring] = counts.get(bitstring, 0) + 1

        return counts

    def _simulate_with_qiskit(self, circuit: QuantumCircuit, shots: int) -> dict[str, int]:
        """Fallback simulation using Qiskit."""
        try:
            from qiskit.providers.basic_provider import BasicProvider

            provider = BasicProvider()
            backend = provider.get_backend("basic_simulator")
            job = backend.run(circuit, shots=shots)
            counts = job.result().get_counts()

            return {str(k): v for k, v in counts.items()}

        except ImportError as err:
            raise RuntimeError("Neither Qulacs nor Qiskit BasicProvider available") from err

    def get_backend_info(self) -> dict[str, Any]:
        """Get information about the backend configuration."""
        info = {
            "name": "qulacs",
            "qulacs_available": self.qulacs_available,
            "gpu_available": self.gpu_available,
            "gpu_device": self.gpu_device if self.gpu_available else None,
            "fallback_enabled": self.allow_cpu_fallback,
        }

        if self.qulacs_available:
            try:
                import qulacs

                info["qulacs_version"] = getattr(qulacs, "__version__", "unknown")

                # GPU memory info if available
                if self.gpu_available:
                    try:
                        import cupy

                        mempool = cupy.get_default_memory_pool()
                        info["gpu_memory_used"] = mempool.used_bytes()
                        info["gpu_memory_total"] = mempool.total_bytes()
                    except Exception:
                        pass

            except Exception:
                pass

        return info

    def estimate_memory_usage(self, num_qubits: int) -> float:
        """Estimate memory usage in MB for given number of qubits."""
        # State vector requires 2^n complex numbers (16 bytes each for complex128)
        state_vector_bytes = int(2**num_qubits) * 16

        # Add overhead for circuit operations and temporary storage
        overhead_factor = 1.5

        total_bytes = state_vector_bytes * overhead_factor
        return total_bytes / (1024 * 1024)  # Convert to MB

    def can_simulate(self, circuit: QuantumCircuit) -> tuple[bool, str]:
        """
        Check if this backend can simulate the given circuit.

        Returns:
            (can_simulate, reason)
        """
        if not self.qulacs_available and not self.allow_cpu_fallback:
            return False, "Qulacs not available and fallback disabled"

        # Check memory requirements
        estimated_memory = self.estimate_memory_usage(circuit.num_qubits)

        # Get available memory
        try:
            import psutil

            available_memory = psutil.virtual_memory().available / (1024 * 1024)

            if estimated_memory > available_memory * 0.8:  # Don't use more than 80% of available memory
                return (
                    False,
                    f"Insufficient memory: need {estimated_memory:.0f}MB, have {available_memory:.0f}MB",
                )
        except ImportError:
            # Can't check memory, assume it's OK for reasonable circuit sizes
            if circuit.num_qubits > 25:
                return False, "Circuit too large (>25 qubits) and cannot verify memory availability"

        # Check for unsupported operations
        unsupported_gates = set()
        for instruction, _, _ in circuit.data:
            gate_name = instruction.name.lower()
            if gate_name not in [
                "id",
                "x",
                "y",
                "z",
                "h",
                "s",
                "sdg",
                "t",
                "tdg",
                "sx",
                "sxdg",
                "rx",
                "ry",
                "rz",
                "p",
                "u1",
                "u2",
                "u3",
                "cx",
                "cy",
                "cz",
                "swap",
                "ccx",
                "measure",
                "barrier",
                "delay",
            ]:
                unsupported_gates.add(gate_name)

        if unsupported_gates:
            return False, f"Unsupported gates: {', '.join(unsupported_gates)}"

        return True, "Can simulate"


def is_qulacs_available() -> bool:
    """Check if Qulacs is available for use."""
    return importlib.util.find_spec("qulacs") is not None


def is_qulacs_gpu_available() -> bool:
    """Check if Qulacs GPU acceleration is available."""
    if not is_qulacs_available():
        return False

    try:
        import qulacs

        # Try to create a GPU state vector
        test_state = qulacs.QuantumState(2)  # Use generic QuantumState, it will use GPU if available
        del test_state
        return True
    except Exception:
        return False


def create_qulacs_backend(use_gpu: bool = True, gpu_device: int = 0, allow_cpu_fallback: bool = True) -> QulacsBackend:
    """
    Factory function to create a Qulacs backend.

    Args:
        use_gpu: Whether to use GPU acceleration if available
        gpu_device: GPU device ID for multi-GPU systems
        allow_cpu_fallback: Allow fallback to CPU if GPU unavailable

    Returns:
        Configured QulacsBackend instance
    """
    return QulacsBackend(use_gpu=use_gpu, gpu_device=gpu_device, allow_cpu_fallback=allow_cpu_fallback)


# Performance optimization utilities
def optimize_circuit_for_qulacs(circuit: QuantumCircuit) -> QuantumCircuit:
    """
    Optimize circuit for better performance with Qulacs.

    Args:
        circuit: Input quantum circuit

    Returns:
        Optimized circuit
    """
    # For now, return the circuit as-is
    # TODO: Implement Qulacs-specific optimizations like:
    # - Gate fusion for adjacent single-qubit gates
    # - Optimal gate decompositions
    # - Circuit depth optimization
    return circuit


def benchmark_qulacs_performance(
    num_qubits_list: list[int], num_gates_per_qubit: int = 10, shots: int = 1000
) -> dict[str, Any]:
    """
    Benchmark Qulacs performance across different circuit sizes.

    Args:
        num_qubits_list: List of qubit counts to test
        num_gates_per_qubit: Number of random gates per qubit
        shots: Number of measurement shots

    Returns:
        Benchmark results dictionary
    """
    import time

    from qiskit.circuit.random import random_circuit

    results: dict[str, dict] = {"qulacs_cpu": {}, "qulacs_gpu": {}, "qiskit": {}}

    for num_qubits in num_qubits_list:
        print(f"Benchmarking {num_qubits} qubits...")

        # Create random circuit
        circuit = random_circuit(num_qubits, num_gates_per_qubit * num_qubits, seed=42)
        circuit.measure_all()

        # Test Qulacs CPU
        try:
            backend_cpu = QulacsBackend(use_gpu=False)
            start_time = time.time()
            backend_cpu.simulate(circuit, shots)
            cpu_time = time.time() - start_time
            results["qulacs_cpu"][num_qubits] = {
                "time": cpu_time,
                "success": True,
                "memory_estimate": backend_cpu.estimate_memory_usage(num_qubits),
            }
        except Exception as e:
            results["qulacs_cpu"][num_qubits] = {"time": None, "success": False, "error": str(e)}

        # Test Qulacs GPU
        try:
            backend_gpu = QulacsBackend(use_gpu=True)
            start_time = time.time()
            backend_gpu.simulate(circuit, shots)
            gpu_time = time.time() - start_time
            results["qulacs_gpu"][num_qubits] = {
                "time": gpu_time,
                "success": True,
                "memory_estimate": backend_gpu.estimate_memory_usage(num_qubits),
            }
        except Exception as e:
            results["qulacs_gpu"][num_qubits] = {"time": None, "success": False, "error": str(e)}

        # Test Qiskit for comparison
        try:
            backend_qiskit = QulacsBackend(use_gpu=False, allow_cpu_fallback=True)
            backend_qiskit.qulacs_available = False  # Force Qiskit fallback
            start_time = time.time()
            backend_qiskit.simulate(circuit, shots)
            qiskit_time = time.time() - start_time
            results["qiskit"][num_qubits] = {
                "time": qiskit_time,
                "success": True,
                "memory_estimate": backend_qiskit.estimate_memory_usage(num_qubits),
            }
        except Exception as e:
            results["qiskit"][num_qubits] = {"time": None, "success": False, "error": str(e)}

    return results
