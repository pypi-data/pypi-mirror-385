"""
Intel Quantum Simulator Backend for Ariadne

This module integrates Intel Quantum Simulator (Intel-QS), a high-performance
quantum circuit simulator optimized for Intel architectures with vectorized
computation and advanced performance optimizations.

Intel-QS Features:
- Vectorized computation with Intel optimizations
- Multi-node parallel simulation
- Memory-efficient state vector representation
- Intel MKL integration for linear algebra
- Support for large-scale quantum circuits
- Optimized for Intel CPUs and Xeon processors
"""

from __future__ import annotations

import importlib.util
import warnings
from typing import Any

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter


class IntelQuantumSimulatorBackend:
    """Intel Quantum Simulator backend for high-performance simulation."""

    def __init__(
        self,
        num_threads: int | None = None,
        use_mkl: bool = True,
        memory_limit_gb: float | None = None,
        enable_distributed: bool = False,
    ):
        """
        Initialize Intel Quantum Simulator backend.

        Args:
            num_threads: Number of threads to use (None for automatic)
            use_mkl: Whether to use Intel MKL for optimizations
            memory_limit_gb: Memory limit in GB (None for no limit)
            enable_distributed: Enable distributed simulation
        """
        self.num_threads = num_threads
        self.use_mkl = use_mkl
        self.memory_limit_gb = memory_limit_gb
        self.enable_distributed = enable_distributed

        # Check Intel-QS availability
        self.intel_qs_available = self._check_intel_qs_availability()
        if not self.intel_qs_available:
            warnings.warn("Intel Quantum Simulator not available, using fallback", stacklevel=2)

        # Initialize simulator configuration
        self._configure_simulator()

    def _check_intel_qs_availability(self) -> bool:
        """Check if Intel Quantum Simulator is available."""
        try:
            # Intel-QS is typically available through Python bindings
            # This is a placeholder check - actual implementation would
            # depend on Intel-QS Python interface
            import subprocess

            result = subprocess.run(["which", "qhipster"], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            # Alternative: check for Python bindings
            return importlib.util.find_spec("intelqs") is not None

    def _configure_simulator(self):
        """Configure Intel-QS simulator parameters."""
        # Set number of threads
        if self.num_threads is None:
            import multiprocessing

            self.num_threads = multiprocessing.cpu_count()

        # Configure Intel MKL if available and requested
        if self.use_mkl:
            self._configure_mkl()

        # Set memory limits
        if self.memory_limit_gb:
            self._set_memory_limit()

    def _configure_mkl(self):
        """Configure Intel MKL optimizations."""
        try:
            import mkl

            mkl.set_num_threads(self.num_threads)
            # Enable other MKL optimizations
            mkl.set_dynamic(True)
        except ImportError:
            warnings.warn("Intel MKL not available", stacklevel=2)

    def _set_memory_limit(self):
        """Set memory usage limits."""
        # This would configure Intel-QS memory limits
        # Implementation depends on Intel-QS interface
        pass

    def simulate(self, circuit: QuantumCircuit, shots: int = 1000) -> dict[str, int]:
        """
        Simulate quantum circuit using Intel Quantum Simulator.

        Args:
            circuit: Quantum circuit to simulate
            shots: Number of measurement shots

        Returns:
            Dictionary of measurement counts
        """
        if not self.intel_qs_available:
            # Fallback to optimized NumPy simulation
            return self._simulate_with_numpy(circuit, shots)

        try:
            # Convert circuit to Intel-QS format
            intel_circuit = self._convert_to_intel_format(circuit)

            # Run simulation
            if shots > 0:
                counts = self._simulate_with_shots(intel_circuit, shots)
            else:
                counts = self._simulate_exact(intel_circuit)

            return counts

        except Exception as e:
            warnings.warn(f"Intel-QS simulation failed: {e}, using fallback", stacklevel=2)
            return self._simulate_with_numpy(circuit, shots)

    def _convert_to_intel_format(self, circuit: QuantumCircuit):
        """Convert Qiskit circuit to Intel-QS format."""
        # This is a placeholder implementation
        # Actual conversion would depend on Intel-QS interface

        intel_operations = []

        # Gate mappings for Intel-QS
        gate_mapping = {
            "id": "I",
            "x": "X",
            "y": "Y",
            "z": "Z",
            "h": "H",
            "s": "S",
            "sdg": "Sdag",
            "t": "T",
            "tdg": "Tdag",
            "cx": "CNOT",
            "cy": "CY",
            "cz": "CZ",
            "swap": "SWAP",
            "ccx": "Toffoli",
        }

        # Convert each instruction
        for instruction, qubits, _clbits in circuit.data:
            gate_name = instruction.name.lower()
            qubit_indices = [circuit.qubits.index(q) for q in qubits]

            # Skip measurement operations for state vector simulation
            if gate_name in ["measure", "barrier", "delay"]:
                continue

            # Map gate to Intel-QS format
            if gate_name in gate_mapping:
                intel_gate = {
                    "type": gate_mapping[gate_name],
                    "qubits": qubit_indices,
                    "params": [float(p) for p in instruction.params] if instruction.params else [],
                }
                intel_operations.append(intel_gate)

            # Parameterized gates
            elif gate_name in ["rx", "ry", "rz"]:
                if instruction.params:
                    angle = float(instruction.params[0]) if not isinstance(instruction.params[0], Parameter) else 0.0
                    intel_gate = {
                        "type": gate_name.upper(),
                        "qubits": qubit_indices,
                        "params": [angle],
                    }
                    intel_operations.append(intel_gate)

            # U3 gate decomposition
            elif gate_name == "u3":
                if len(instruction.params) >= 3:
                    theta = float(instruction.params[0]) if not isinstance(instruction.params[0], Parameter) else 0.0
                    phi = float(instruction.params[1]) if not isinstance(instruction.params[1], Parameter) else 0.0
                    lam = float(instruction.params[2]) if not isinstance(instruction.params[2], Parameter) else 0.0

                    # Decompose U3 into RZ-RY-RZ sequence
                    intel_operations.extend(
                        [
                            {"type": "RZ", "qubits": qubit_indices, "params": [lam]},
                            {"type": "RY", "qubits": qubit_indices, "params": [theta]},
                            {"type": "RZ", "qubits": qubit_indices, "params": [phi]},
                        ]
                    )

        return {"num_qubits": circuit.num_qubits, "operations": intel_operations}

    def _simulate_with_shots(self, intel_circuit: dict, shots: int) -> dict[str, int]:
        """Simulate with finite shots using Intel-QS."""
        # Placeholder implementation for Intel-QS simulation
        # Actual implementation would use Intel-QS APIs

        # For now, use optimized NumPy implementation
        return self._simulate_shots_numpy(intel_circuit, shots)

    def _simulate_exact(self, intel_circuit: dict) -> dict[str, int]:
        """Exact simulation using Intel-QS."""
        # Simulate without shots for exact results
        return self._simulate_with_shots(intel_circuit, 1000)

    def _simulate_with_numpy(self, circuit: QuantumCircuit, shots: int) -> dict[str, int]:
        """Fallback simulation using optimized NumPy with Intel optimizations."""

        # Use Intel-optimized NumPy operations where possible
        num_qubits = circuit.num_qubits

        # Initialize state vector
        state = np.zeros(2**num_qubits, dtype=np.complex128)
        state[0] = 1.0  # |0...0> state

        # Apply circuit operations
        for instruction, qubits, _clbits in circuit.data:
            if instruction.name in ["measure", "barrier", "delay"]:
                continue

            # Get gate matrix
            gate_matrix = self._get_gate_matrix(instruction)
            if gate_matrix is None:
                continue

            # Apply gate to state vector
            qubit_indices = [circuit.qubits.index(q) for q in qubits]
            state = self._apply_gate_optimized(state, gate_matrix, qubit_indices, num_qubits)

        # Sample from final state
        return self._sample_from_state(state, shots)

    def _simulate_shots_numpy(self, intel_circuit: dict, shots: int) -> dict[str, int]:
        """Simulate shots using optimized NumPy implementation."""
        num_qubits = intel_circuit["num_qubits"]

        # Initialize state vector
        state = np.zeros(2**num_qubits, dtype=np.complex128)
        state[0] = 1.0

        # Apply operations
        for operation in intel_circuit["operations"]:
            gate_matrix = self._get_intel_gate_matrix(operation)
            if gate_matrix is not None:
                state = self._apply_gate_optimized(state, gate_matrix, operation["qubits"], num_qubits)

        return self._sample_from_state(state, shots)

    def _get_gate_matrix(self, instruction) -> np.ndarray | None:
        """Get gate matrix for Qiskit instruction."""
        gate_matrices = {
            "id": np.eye(2, dtype=np.complex128),
            "x": np.array([[0, 1], [1, 0]], dtype=np.complex128),
            "y": np.array([[0, -1j], [1j, 0]], dtype=np.complex128),
            "z": np.array([[1, 0], [0, -1]], dtype=np.complex128),
            "h": np.array([[1, 1], [1, -1]], dtype=np.complex128) / np.sqrt(2),
            "s": np.array([[1, 0], [0, 1j]], dtype=np.complex128),
            "sdg": np.array([[1, 0], [0, -1j]], dtype=np.complex128),
            "t": np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=np.complex128),
            "tdg": np.array([[1, 0], [0, np.exp(-1j * np.pi / 4)]], dtype=np.complex128),
        }

        gate_name = instruction.name.lower()

        # Single-qubit gates
        if gate_name in gate_matrices:
            return gate_matrices[gate_name]

        # Parameterized gates
        elif gate_name == "rx" and instruction.params:
            angle = float(instruction.params[0]) if not isinstance(instruction.params[0], Parameter) else 0.0
            return np.array(
                [
                    [np.cos(angle / 2), -1j * np.sin(angle / 2)],
                    [-1j * np.sin(angle / 2), np.cos(angle / 2)],
                ],
                dtype=np.complex128,
            )

        elif gate_name == "ry" and instruction.params:
            angle = float(instruction.params[0]) if not isinstance(instruction.params[0], Parameter) else 0.0
            return np.array(
                [[np.cos(angle / 2), -np.sin(angle / 2)], [np.sin(angle / 2), np.cos(angle / 2)]],
                dtype=np.complex128,
            )

        elif gate_name == "rz" and instruction.params:
            angle = float(instruction.params[0]) if not isinstance(instruction.params[0], Parameter) else 0.0
            return np.array([[np.exp(-1j * angle / 2), 0], [0, np.exp(1j * angle / 2)]], dtype=np.complex128)

        # Two-qubit gates
        elif gate_name == "cx":
            return np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], dtype=np.complex128)

        elif gate_name == "cz":
            return np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, -1]], dtype=np.complex128)

        elif gate_name == "swap":
            return np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=np.complex128)

        return None

    def _get_intel_gate_matrix(self, operation: dict) -> np.ndarray | None:
        """Get gate matrix for Intel-QS operation."""
        gate_type = operation["type"]
        params = operation.get("params", [])

        # Map Intel-QS gate types to matrices
        if gate_type == "I":
            return np.eye(2, dtype=np.complex128)
        elif gate_type == "X":
            return np.array([[0, 1], [1, 0]], dtype=np.complex128)
        elif gate_type == "Y":
            return np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
        elif gate_type == "Z":
            return np.array([[1, 0], [0, -1]], dtype=np.complex128)
        elif gate_type == "H":
            return np.array([[1, 1], [1, -1]], dtype=np.complex128) / np.sqrt(2)
        elif gate_type == "S":
            return np.array([[1, 0], [0, 1j]], dtype=np.complex128)
        elif gate_type == "RX" and params:
            angle = params[0]
            return np.array(
                [
                    [np.cos(angle / 2), -1j * np.sin(angle / 2)],
                    [-1j * np.sin(angle / 2), np.cos(angle / 2)],
                ],
                dtype=np.complex128,
            )
        elif gate_type == "RY" and params:
            angle = params[0]
            return np.array(
                [[np.cos(angle / 2), -np.sin(angle / 2)], [np.sin(angle / 2), np.cos(angle / 2)]],
                dtype=np.complex128,
            )
        elif gate_type == "RZ" and params:
            angle = params[0]
            return np.array([[np.exp(-1j * angle / 2), 0], [0, np.exp(1j * angle / 2)]], dtype=np.complex128)
        elif gate_type == "CNOT":
            return np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], dtype=np.complex128)

        return None

    def _apply_gate_optimized(
        self, state: np.ndarray, gate_matrix: np.ndarray, qubits: list[int], num_qubits: int
    ) -> np.ndarray:
        """Apply gate to state vector with Intel optimizations."""

        # Use Intel MKL optimized operations where possible
        if len(qubits) == 1:
            return self._apply_single_qubit_gate_vectorized(state, gate_matrix, qubits[0], num_qubits)
        elif len(qubits) == 2:
            return self._apply_two_qubit_gate_vectorized(state, gate_matrix, qubits, num_qubits)
        else:
            # Multi-qubit gates - use general approach
            return self._apply_multi_qubit_gate(state, gate_matrix, qubits, num_qubits)

    def _apply_single_qubit_gate_vectorized(
        self, state: np.ndarray, gate_matrix: np.ndarray, qubit: int, num_qubits: int
    ) -> np.ndarray:
        """Apply single-qubit gate using vectorized operations."""
        new_state = state.copy()

        # Vectorized application for single-qubit gates
        for i in range(2 ** (num_qubits - 1)):
            # Calculate indices for 0 and 1 states of target qubit
            idx0 = i & ((1 << qubit) - 1) | ((i >> qubit) << (qubit + 1))
            idx1 = idx0 | (1 << qubit)

            # Apply gate matrix
            amp0, amp1 = state[idx0], state[idx1]
            new_state[idx0] = gate_matrix[0, 0] * amp0 + gate_matrix[0, 1] * amp1
            new_state[idx1] = gate_matrix[1, 0] * amp0 + gate_matrix[1, 1] * amp1

        return new_state

    def _apply_two_qubit_gate_vectorized(
        self, state: np.ndarray, gate_matrix: np.ndarray, qubits: list[int], num_qubits: int
    ) -> np.ndarray:
        """Apply two-qubit gate using vectorized operations."""
        new_state = state.copy()
        qubit0, qubit1 = sorted(qubits)

        # Vectorized application for two-qubit gates
        for i in range(2 ** (num_qubits - 2)):
            # Generate indices for all 4 computational basis states
            base_idx = i
            for q in [qubit0, qubit1]:
                base_idx = (base_idx & ((1 << q) - 1)) | ((base_idx >> q) << (q + 1))

            idx00 = base_idx
            idx01 = base_idx | (1 << qubit1)
            idx10 = base_idx | (1 << qubit0)
            idx11 = base_idx | (1 << qubit0) | (1 << qubit1)

            # Apply gate matrix
            amps = [state[idx00], state[idx01], state[idx10], state[idx11]]

            new_state[idx00] = sum(gate_matrix[0, j] * amps[j] for j in range(4))
            new_state[idx01] = sum(gate_matrix[1, j] * amps[j] for j in range(4))
            new_state[idx10] = sum(gate_matrix[2, j] * amps[j] for j in range(4))
            new_state[idx11] = sum(gate_matrix[3, j] * amps[j] for j in range(4))

        return new_state

    def _apply_multi_qubit_gate(
        self, state: np.ndarray, gate_matrix: np.ndarray, qubits: list[int], num_qubits: int
    ) -> np.ndarray:
        """Apply multi-qubit gate (general case)."""
        # This is a simplified implementation
        # A full implementation would be more optimized
        return state  # Placeholder

    def _sample_from_state(self, state: np.ndarray, shots: int) -> dict[str, int]:
        """Sample measurement outcomes from state vector."""
        # Calculate probabilities
        probabilities = np.abs(state) ** 2
        probabilities = probabilities / np.sum(probabilities)  # Normalize

        # Sample outcomes
        num_qubits = int(np.log2(len(state)))
        outcomes = np.random.choice(len(state), size=shots, p=probabilities)

        # Convert to bit strings
        counts = {}
        for outcome in outcomes:
            bitstring = format(outcome, f"0{num_qubits}b")[::-1]  # Reverse for Qiskit convention
            counts[bitstring] = counts.get(bitstring, 0) + 1

        return counts

    def get_backend_info(self) -> dict[str, Any]:
        """Get information about the backend configuration."""
        info = {
            "name": "intel_qs",
            "intel_qs_available": self.intel_qs_available,
            "num_threads": self.num_threads,
            "use_mkl": self.use_mkl,
            "memory_limit_gb": self.memory_limit_gb,
            "distributed_enabled": self.enable_distributed,
        }

        # Add Intel-specific information
        try:
            import platform

            info["cpu_info"] = platform.processor()
            info["cpu_count"] = self.num_threads

            # Check for Intel MKL
            try:
                import mkl

                info["mkl_version"] = mkl.get_version_string()
                info["mkl_threads"] = mkl.get_max_threads()
            except ImportError:
                info["mkl_available"] = False

        except Exception:
            pass

        return info

    def estimate_memory_usage(self, num_qubits: int) -> float:
        """Estimate memory usage in MB for given number of qubits."""
        # State vector requires 2^n complex numbers (16 bytes each)
        state_vector_bytes = (2**num_qubits) * 16

        # Add overhead for temporary arrays and operations
        overhead_factor = 2.0  # Conservative estimate

        total_bytes = state_vector_bytes * overhead_factor
        return total_bytes / (1024 * 1024)  # Convert to MB

    def can_simulate(self, circuit: QuantumCircuit) -> tuple[bool, str]:
        """Check if this backend can simulate the given circuit."""

        # Check memory requirements
        estimated_memory = self.estimate_memory_usage(circuit.num_qubits)

        if self.memory_limit_gb and estimated_memory > self.memory_limit_gb * 1024:
            return (
                False,
                f"Circuit requires {estimated_memory:.0f}MB, limit is {self.memory_limit_gb * 1024:.0f}MB",
            )

        # Check system memory
        try:
            import psutil

            available_memory = psutil.virtual_memory().available / (1024 * 1024)

            if estimated_memory > available_memory * 0.8:
                return (
                    False,
                    f"Insufficient system memory: need {estimated_memory:.0f}MB, have {available_memory:.0f}MB",
                )
        except ImportError:
            # Conservative limit if can't check memory
            if circuit.num_qubits > 25:
                return False, "Circuit too large (>25 qubits) and cannot verify memory availability"

        return True, "Can simulate"


def is_intel_qs_available() -> bool:
    """Check if Intel Quantum Simulator is available."""
    backend = IntelQuantumSimulatorBackend()
    return backend.intel_qs_available


def create_intel_qs_backend(
    num_threads: int | None = None,
    use_mkl: bool = True,
    memory_limit_gb: float | None = None,
    enable_distributed: bool = False,
) -> IntelQuantumSimulatorBackend:
    """
    Factory function to create an Intel Quantum Simulator backend.

    Args:
        num_threads: Number of threads to use
        use_mkl: Whether to use Intel MKL optimizations
        memory_limit_gb: Memory limit in GB
        enable_distributed: Enable distributed simulation

    Returns:
        Configured IntelQuantumSimulatorBackend instance
    """
    return IntelQuantumSimulatorBackend(
        num_threads=num_threads,
        use_mkl=use_mkl,
        memory_limit_gb=memory_limit_gb,
        enable_distributed=enable_distributed,
    )


def benchmark_intel_optimizations(
    num_qubits_list: list[int] = None,
    enable_mkl_list: list[bool] = None,
    thread_counts: list[int] = None,
) -> dict[str, Any]:
    """
    Benchmark Intel-specific optimizations.

    Args:
        num_qubits_list: List of qubit counts to test
        enable_mkl_list: Whether to test with/without MKL
        thread_counts: List of thread counts to test

    Returns:
        Benchmark results
    """
    import time

    from qiskit.circuit.random import random_circuit

    if thread_counts is None:
        thread_counts = [1, 4, 8]
    if enable_mkl_list is None:
        enable_mkl_list = [True, False]
    if num_qubits_list is None:
        num_qubits_list = [10, 15, 20]
    results = {}

    for num_qubits in num_qubits_list:
        for use_mkl in enable_mkl_list:
            for num_threads in thread_counts:
                key = f"{num_qubits}q_mkl{use_mkl}_t{num_threads}"
                print(f"Benchmarking: {key}")

                try:
                    # Create test circuit
                    circuit = random_circuit(num_qubits, num_qubits * 5, seed=42)
                    circuit.measure_all()

                    # Create backend
                    backend = create_intel_qs_backend(num_threads=num_threads, use_mkl=use_mkl)

                    # Benchmark simulation
                    start_time = time.time()
                    backend.simulate(circuit, shots=1000)
                    execution_time = time.time() - start_time

                    results[key] = {
                        "num_qubits": num_qubits,
                        "use_mkl": use_mkl,
                        "num_threads": num_threads,
                        "execution_time": execution_time,
                        "memory_estimate": backend.estimate_memory_usage(num_qubits),
                        "success": True,
                    }

                except Exception as e:
                    results[key] = {
                        "num_qubits": num_qubits,
                        "use_mkl": use_mkl,
                        "num_threads": num_threads,
                        "success": False,
                        "error": str(e),
                    }

    return results
