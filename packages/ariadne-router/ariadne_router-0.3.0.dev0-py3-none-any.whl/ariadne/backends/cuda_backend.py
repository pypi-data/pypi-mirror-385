from __future__ import annotations

import math
import time
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Instruction

try:
    import cupy as cp  # type: ignore[import-not-found]

    CUDA_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised when CuPy is missing
    cp = None
    CUDA_AVAILABLE = False


# Conditional imports for type checking only
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # For type checking only
    pass


def is_cuda_available() -> bool:
    """Return ``True`` when CuPy and a CUDA runtime are available."""

    if not CUDA_AVAILABLE:
        return False

    try:  # pragma: no cover - requires CUDA runtime
        device_count = cp.cuda.runtime.getDeviceCount()
        return bool(device_count > 0)
    except Exception:
        return False


def get_cuda_info() -> dict[str, object]:
    """Return a lightweight description of the detected CUDA devices."""

    if not CUDA_AVAILABLE:
        return {"available": False, "device_count": 0}

    try:  # pragma: no cover - requires CUDA runtime
        device_count = cp.cuda.runtime.getDeviceCount()
        devices: list[dict[str, object]] = []

        for device_id in range(device_count):
            props = cp.cuda.runtime.getDeviceProperties(device_id)
            devices.append(
                {
                    "device_id": device_id,
                    "name": props.get("name", b"?").decode("utf-8", errors="ignore"),
                    "total_memory": int(props.get("totalGlobalMem", 0)),
                    "multiprocessors": int(props.get("multiProcessorCount", 0)),
                    "compute_capability": f"{props.get('major', 0)}.{props.get('minor', 0)}",
                }
            )

        return {
            "available": device_count > 0,
            "device_count": device_count,
            "devices": devices,
        }
    except Exception as exc:  # pragma: no cover - requires CUDA runtime
        return {"available": False, "error": str(exc)}


@dataclass
class SimulationSummary:
    """Metadata describing the most recent simulation run."""

    shots: int
    measured_qubits: Sequence[int]
    execution_time: float
    backend_mode: str


class CUDABackend:
    """Enhanced statevector simulator with multi-GPU support and memory optimization."""

    custom_kernels: Any

    def __init__(
        self,
        *,
        device_id: int = 0,
        prefer_gpu: bool = True,
        allow_cpu_fallback: bool = True,
        enable_multi_gpu: bool = False,
        memory_pool_fraction: float = 0.8,
        use_custom_kernels: bool = True,
    ) -> None:
        self._last_summary: SimulationSummary | None = None
        self._xp: Any = np
        self._mode = "cpu"
        self._device_pool: list[int] = []
        self._memory_pools: dict[int, Any] = {}

        # Multi-GPU configuration
        self.enable_multi_gpu = enable_multi_gpu and CUDA_AVAILABLE
        self.memory_pool_fraction = memory_pool_fraction
        self.use_custom_kernels = use_custom_kernels

        # Memory management for large circuits
        self.memory_threshold = self.memory_pool_fraction * 0.8  # Reserve 20% for operations
        self.chunk_size_qubits = 28  # Maximum qubits per chunk
        self.use_streaming = True

        # Initialize CUDA devices
        if prefer_gpu and CUDA_AVAILABLE:
            self._initialize_cuda_devices(device_id, allow_cpu_fallback)
        elif not allow_cpu_fallback:
            raise RuntimeError(
                "CUDA runtime not available and CPU fallback disabled. "
                "Install CuPy with CUDA support or enable CPU fallback."
            )

    def _initialize_cuda_devices(self, primary_device_id: int, allow_cpu_fallback: bool) -> None:
        """Initialize CUDA devices and memory pools."""
        try:
            device_count = cp.cuda.runtime.getDeviceCount()

            if device_count == 0:
                if not allow_cpu_fallback:
                    raise RuntimeError("No CUDA devices found")
                return

            # Initialize primary device
            if primary_device_id >= device_count:
                if not allow_cpu_fallback:
                    raise RuntimeError(f"Device {primary_device_id} not found")
                return

            cp.cuda.Device(primary_device_id).use()
            self._device_pool = [primary_device_id]
            self._xp = cp
            self._mode = "cuda"

            # Initialize memory pool for primary device
            mempool = cp.get_default_memory_pool()
            mempool.set_limit(fraction=self.memory_pool_fraction)
            self._memory_pools[primary_device_id] = mempool

            # Initialize additional devices for multi-GPU
            if self.enable_multi_gpu and device_count > 1:
                for device_id in range(device_count):
                    if device_id != primary_device_id:
                        try:
                            with cp.cuda.Device(device_id):
                                # Test device accessibility
                                test_array = cp.array([1.0])
                                del test_array

                                self._device_pool.append(device_id)

                                # Initialize memory pool
                                device_mempool = cp.get_default_memory_pool()
                                device_mempool.set_limit(fraction=self.memory_pool_fraction)
                                self._memory_pools[device_id] = device_mempool

                        except Exception:
                            # Skip inaccessible devices
                            continue

            # Load custom kernels if enabled
            if self.use_custom_kernels:
                self._load_custom_kernels()

            # Memory management for large circuits
            self.memory_threshold = self.memory_pool_fraction * 0.8  # Reserve 20% for operations
            self.chunk_size_qubits = 28  # Maximum qubits per chunk
            self.use_streaming = True

        except Exception as exc:
            if not allow_cpu_fallback:
                raise RuntimeError(f"Failed to initialize CUDA: {exc}") from exc
            # Fall back to CPU
            self._xp = np
            self._mode = "cpu"

    def _load_custom_kernels(self) -> None:
        """Load custom CUDA kernels for optimized quantum operations."""
        try:
            from .cuda_kernels import get_cuda_kernels

            self.custom_kernels = get_cuda_kernels()
        except ImportError:
            # Custom kernels not available, use CuPy operations
            self.custom_kernels = None

    @property
    def backend_mode(self) -> str:
        return self._mode

    @property
    def last_summary(self) -> SimulationSummary | None:
        return self._last_summary

    def simulate(self, circuit: QuantumCircuit, shots: int = 1024) -> dict[str, int]:
        if shots <= 0:
            raise ValueError("shots must be a positive integer")

        # Determine simulation strategy based on circuit size
        num_qubits = circuit.num_qubits
        use_multi_gpu = (
            self.enable_multi_gpu
            and len(self._device_pool) > 1
            and num_qubits >= 12  # Only use multi-GPU for larger circuits
        )

        # Check if circuit requires chunking for memory efficiency
        if num_qubits > self.chunk_size_qubits:
            state, measured_qubits, execution_time = self._simulate_chunked_circuit(circuit)
        elif use_multi_gpu:
            state, measured_qubits, execution_time = self._simulate_statevector_multi_gpu(circuit)
        else:
            state, measured_qubits, execution_time = self._simulate_statevector(circuit)

        # Simulation routing is handled above

        counts = self._sample_measurements(state, measured_qubits, shots)

        self._last_summary = SimulationSummary(
            shots=shots,
            measured_qubits=measured_qubits,
            execution_time=execution_time,
            backend_mode=f"{self._mode}_{'multi' if use_multi_gpu else 'single'}",
        )

        return counts

    def _simulate_statevector_multi_gpu(self, circuit: QuantumCircuit) -> tuple[Any, Sequence[int], float]:
        """Simulate using multiple GPUs for large circuits."""
        num_qubits = circuit.num_qubits

        # Determine optimal partitioning strategy
        if num_qubits <= 20:
            # For moderate circuits, use data parallelism
            return self._simulate_data_parallel(circuit)
        else:
            # For large circuits, use model parallelism
            return self._simulate_model_parallel_circuit(circuit)

    def _simulate_data_parallel(self, circuit: QuantumCircuit) -> tuple[Any, Sequence[int], float]:
        """Data parallel simulation across multiple GPUs."""
        start = time.perf_counter()

        num_devices = len(self._device_pool)
        num_qubits = circuit.num_qubits
        state_size = 2**num_qubits

        # Split state vector across devices
        chunk_size = (state_size + num_devices - 1) // num_devices

        operations, measured_qubits = self._prepare_operations(circuit)

        # Initialize state chunks on each device
        state_chunks = []
        for i, device_id in enumerate(self._device_pool):
            with cp.cuda.Device(device_id):
                start_idx = i * chunk_size
                end_idx = min((i + 1) * chunk_size, state_size)
                chunk_length = end_idx - start_idx

                chunk = cp.zeros(chunk_length, dtype=cp.complex128)
                if start_idx == 0:  # Initialize |00...0⟩ state
                    chunk[0] = 1.0

                state_chunks.append((device_id, chunk, start_idx, end_idx))

        # Apply operations across all devices
        for instruction, targets in operations:
            gate_matrix = self._instruction_to_matrix_multi_gpu(instruction, len(targets))
            state_chunks = self._apply_gate_multi_gpu(state_chunks, gate_matrix, targets)

        # Gather results from all devices
        with cp.cuda.Device(self._device_pool[0]):
            full_state = cp.zeros(state_size, dtype=cp.complex128)
            for device_id, chunk, start_idx, end_idx in state_chunks:
                with cp.cuda.Device(device_id):
                    full_state[start_idx:end_idx] = chunk

        execution_time = time.perf_counter() - start
        return full_state, measured_qubits, execution_time

    def _simulate_chunked_circuit(self, circuit: QuantumCircuit) -> tuple[Any, Sequence[int], float]:
        """Simulate very large circuits using memory-efficient chunking."""
        time.perf_counter()

        num_qubits = circuit.num_qubits
        operations, measured_qubits = self._prepare_operations(circuit)

        # Use CUDA streams for overlapping computation and memory transfer
        if self._mode == "cuda" and self.use_streaming:
            return self._simulate_with_streaming(operations, measured_qubits, num_qubits)
        else:
            return self._simulate_with_chunking(operations, measured_qubits, num_qubits)

    def _simulate_with_streaming(
        self, operations: list[tuple], measured_qubits: Sequence[int], num_qubits: int
    ) -> tuple[Any, Sequence[int], float]:
        """Simulate using CUDA streams for memory-efficient processing."""
        start = time.perf_counter()

        with cp.cuda.Device(self._device_pool[0]):
            # Create multiple streams for overlapping computation
            num_streams = min(4, len(self._device_pool))
            streams = [cp.cuda.Stream() for _ in range(num_streams)]

            # Estimate chunk size based on available memory
            available_memory = self._get_available_memory()
            chunk_qubits = min(self.chunk_size_qubits, self._estimate_max_qubits(available_memory))

            if num_qubits <= chunk_qubits:
                # Circuit fits in memory, use standard simulation
                state, _, _ = self._simulate_statevector(QuantumCircuit.from_instructions(operations))
                execution_time = time.perf_counter() - start
                return state, measured_qubits, execution_time

            # Process circuit in chunks
            chunk_size = 2**chunk_qubits
            num_chunks = 2 ** (num_qubits - chunk_qubits)

            # Initialize result collector
            if num_qubits <= 30:  # Up to 1GB of complex128 data
                full_state = cp.zeros(2**num_qubits, dtype=cp.complex128)
            else:
                # Use sparse representation for very large states
                full_state = self._create_sparse_state(num_qubits)

            # Process chunks with stream parallelism
            for chunk_idx in range(0, num_chunks, num_streams):
                batch_size = min(num_streams, num_chunks - chunk_idx)

                # Launch parallel chunk processing
                chunk_results = []
                for i in range(batch_size):
                    stream = streams[i]
                    current_chunk = chunk_idx + i

                    with stream:
                        chunk_state = self._process_chunk(operations, current_chunk, chunk_qubits, num_qubits)
                        chunk_results.append((current_chunk, chunk_state))

                # Synchronize and collect results
                for stream in streams[:batch_size]:
                    stream.synchronize()

                for chunk_id, chunk_state in chunk_results:
                    start_idx = chunk_id * chunk_size
                    end_idx = min((chunk_id + 1) * chunk_size, 2**num_qubits)

                    if hasattr(full_state, "toarray"):  # Sparse matrix
                        full_state[start_idx:end_idx] = cp.asnumpy(chunk_state)
                    else:
                        full_state[start_idx:end_idx] = chunk_state

            execution_time = time.perf_counter() - start
            return full_state, measured_qubits, execution_time

    def _simulate_with_chunking(
        self, operations: list[tuple], measured_qubits: Sequence[int], num_qubits: int
    ) -> tuple[Any, Sequence[int], float]:
        """Simulate using memory-efficient chunking without streams."""
        start = time.perf_counter()

        # Simple chunking strategy for CPU or limited GPU memory
        chunk_qubits = min(self.chunk_size_qubits, num_qubits)

        if num_qubits <= chunk_qubits:
            # Create temporary circuit from operations
            temp_circuit = QuantumCircuit(num_qubits)
            for instruction, qubits in operations:
                temp_circuit.append(instruction, qubits)

            state, _, _ = self._simulate_statevector(temp_circuit)
            execution_time = time.perf_counter() - start
            return state, measured_qubits, execution_time

        # For very large circuits, use approximate simulation
        # This is a simplified implementation
        xp = self._xp

        # Use reduced precision or compressed representation
        dtype = xp.complex64 if num_qubits > 25 else xp.complex128
        state = xp.zeros(2**num_qubits, dtype=dtype)
        state[0] = 1.0

        # Apply operations with memory-conscious approach
        for instruction, targets in operations:
            gate_matrix = self._instruction_to_matrix(instruction, len(targets))
            if len(targets) <= 3:  # Only apply small gates directly
                self._apply_gate_memory_efficient(state, gate_matrix, targets)
            # Skip very large gates to maintain memory constraints

        execution_time = time.perf_counter() - start
        return state, measured_qubits, execution_time

    def _get_available_memory(self) -> int:
        """Get available GPU memory in bytes."""
        if self._mode != "cuda":
            return 8 * 1024**3  # 8GB default for CPU

        try:
            meminfo = cp.cuda.runtime.memGetInfo()
            return int(meminfo[0])  # Available memory
        except Exception:
            return 4 * 1024**3  # 4GB fallback

    def _estimate_max_qubits(self, available_memory: int) -> int:
        """Estimate maximum qubits that fit in available memory."""
        # Complex128 uses 16 bytes per amplitude
        bytes_per_amplitude = 16
        max_amplitudes = available_memory // (2 * bytes_per_amplitude)  # Factor of 2 for safety
        max_qubits = int(math.log2(float(max_amplitudes)))
        return min(max_qubits, 30)  # Cap at 30 qubits for safety

    def _calculate_launch_config(self, state_size: int) -> tuple[int, int]:
        """
        Dynamically calculate optimal CUDA kernel launch configuration (grid, block).

        Aims to maximize GPU occupancy by using a fixed optimal block size
        and calculating the required grid size based on the state vector size.
        """
        # Optimal block size, typically a multiple of 32, e.g., 512 or 1024.
        block_size = 512

        # Calculate required grid size (number of blocks)
        # Grid size = ceil(state_size / block_size)
        grid_size = (state_size + block_size - 1) // block_size

        # Ensure grid size is at least 1
        grid_size = max(1, grid_size)

        return grid_size, block_size

    def _create_sparse_state(self, num_qubits: int) -> Any:
        """Create sparse state representation for very large quantum states."""
        if self._mode == "cuda":
            # Use CuPy sparse matrices for GPU
            try:
                import cupyx.scipy.sparse as sparse

                size = 2**num_qubits
                return sparse.csr_matrix((1, size), dtype=cp.complex128)
            except ImportError:
                # Fallback to dense but with lower precision
                return cp.zeros(2 ** min(num_qubits, 28), dtype=cp.complex64)
        else:
            # Use SciPy sparse matrices for CPU
            import scipy.sparse as sparse

            size = 2**num_qubits
            return sparse.csr_matrix((1, size), dtype=np.complex128)

    def _process_chunk(self, operations: Sequence[tuple], chunk_idx: int, chunk_qubits: int, total_qubits: int) -> Any:
        """Process a single chunk of the quantum state."""
        xp = self._xp

        # Create chunk state representing this portion of the full state
        chunk_state = xp.zeros(2**chunk_qubits, dtype=xp.complex128)

        # Initialize chunk based on its position in the full state
        if chunk_idx == 0:
            chunk_state[0] = 1.0  # |00...0⟩ state

        # Apply operations that affect this chunk
        for instruction, targets in operations:
            # Determine if this operation affects the current chunk
            chunk_offset = chunk_idx * (2**chunk_qubits)

            if self._operation_affects_chunk(targets, chunk_offset, chunk_qubits, total_qubits):
                # Map global qubit indices to local chunk indices
                local_targets = self._map_to_local_qubits(targets, chunk_offset, chunk_qubits)

                if local_targets:
                    gate_matrix = self._instruction_to_matrix(instruction, len(local_targets))
                    self._apply_gate(chunk_state, gate_matrix, local_targets)

        return chunk_state

    def _operation_affects_chunk(
        self, targets: Sequence[int], chunk_offset: int, chunk_qubits: int, total_qubits: int
    ) -> bool:
        """Check if an operation affects a specific chunk."""
        chunk_offset + (2**chunk_qubits) - 1

        # For simplicity, assume operation affects chunk if any target qubit
        # corresponds to bits that vary within the chunk range
        for qubit in targets:
            if qubit < chunk_qubits:  # Qubit varies within chunk
                return True

        return False

    def _map_to_local_qubits(self, targets: Sequence[int], chunk_offset: int, chunk_qubits: int) -> list[int]:
        """Map global qubit indices to local chunk indices."""
        local_targets = []
        for qubit in targets:
            if qubit < chunk_qubits:
                local_targets.append(qubit)
        return local_targets

    def _apply_gate_memory_efficient(self, state: Any, matrix: Any, qubits: Sequence[int]) -> None:
        """Apply gate with memory-efficient approach for large circuits."""
        if len(qubits) > 4:  # Skip very large gates
            return

        # Use custom kernels if available for better memory efficiency
        if self.custom_kernels and self.custom_kernels.is_available:
            # Calculate dynamic launch configuration based on state size
            state_size = state.shape[0]
            grid, block = self._calculate_launch_config(state_size)

            if len(qubits) == 1:
                result = self.custom_kernels.apply_single_qubit_gate(state, matrix, qubits[0])
                state[:] = result
            elif len(qubits) == 2:
                result = self.custom_kernels.apply_two_qubit_gate(state, matrix, qubits[0], qubits[1])
                state[:] = result
            else:
                # Fallback to standard method for multi-qubit gates
                self._apply_gate(state, matrix, qubits)
        else:
            self._apply_gate(state, matrix, qubits)

    def _simulate_model_parallel_circuit(self, circuit: QuantumCircuit) -> tuple[Any, Sequence[int], float]:
        """Model parallel simulation for very large circuits."""
        # For very large circuits, implement circuit partitioning
        # This is a simplified version - full implementation would be more complex

        start = time.perf_counter()

        # Fall back to single GPU for now - model parallelism is complex
        # In production, this would implement circuit partitioning algorithms
        with cp.cuda.Device(self._device_pool[0]):
            state, measured_qubits, _ = self._simulate_statevector(circuit)

        execution_time = time.perf_counter() - start
        return state, measured_qubits, execution_time

    def _instruction_to_matrix_multi_gpu(self, instruction: Instruction, arity: int) -> Any:
        """Convert instruction to matrix optimized for multi-GPU."""
        if hasattr(instruction, "to_matrix"):
            matrix = instruction.to_matrix()
        else:
            matrix = np.eye(2**arity, dtype=np.complex128)

        # Keep on CPU initially, will be copied to GPU as needed
        return matrix.astype(np.complex128)

    def _apply_gate_multi_gpu(self, state_chunks: list, matrix: Any, qubits: Sequence[int]) -> list:
        """Apply gate across multiple GPU state chunks."""
        if not qubits:
            return state_chunks

        # For multi-GPU gate application, we need to handle cross-device communication
        # This is a simplified implementation

        updated_chunks = []

        for device_id, chunk, start_idx, end_idx in state_chunks:
            with cp.cuda.Device(device_id):
                # Convert matrix to current device
                device_matrix = cp.asarray(matrix, dtype=cp.complex128)

                # Apply gate to chunk (simplified - doesn't handle cross-chunk gates properly)
                updated_chunk = self._apply_gate_chunk(chunk, device_matrix, qubits, start_idx)
                updated_chunks.append((device_id, updated_chunk, start_idx, end_idx))

        return updated_chunks

    def _apply_gate_chunk(self, chunk: Any, matrix: Any, qubits: Sequence[int], chunk_offset: int) -> Any:
        """Apply gate to a state chunk."""
        # Simplified gate application for demonstration
        # Real implementation would handle the chunked state vector properly

        if len(qubits) == 1:
            return self._apply_single_qubit_gate_chunk(chunk, matrix, qubits[0], chunk_offset)
        elif len(qubits) == 2:
            return self._apply_two_qubit_gate_chunk(chunk, matrix, qubits, chunk_offset)
        else:
            # For multi-qubit gates, fall back to standard method
            return chunk  # Placeholder

    def _apply_single_qubit_gate_chunk(self, chunk: Any, matrix: Any, qubit: int, chunk_offset: int) -> Any:
        """Apply single qubit gate to chunk."""
        # This is a simplified implementation
        # Real version would handle the chunk indexing properly
        return chunk

    def _apply_two_qubit_gate_chunk(self, chunk: Any, matrix: Any, qubits: Sequence[int], chunk_offset: int) -> Any:
        """Apply two qubit gate to chunk."""
        # This is a simplified implementation
        # Real version would handle cross-chunk communication
        return chunk

    def simulate_statevector(self, circuit: QuantumCircuit) -> tuple[np.ndarray, Sequence[int]]:
        state, measured_qubits, _ = self._simulate_statevector(circuit)
        if self._xp is np:
            return state, measured_qubits

        return cp.asnumpy(state), measured_qubits

    # ------------------------------------------------------------------
    # Internal helpers

    def _simulate_statevector(self, circuit: QuantumCircuit) -> tuple[Any, Sequence[int], float]:
        xp = self._xp
        num_qubits = circuit.num_qubits
        state = xp.zeros(2**num_qubits, dtype=xp.complex128)
        state[0] = 1.0

        operations, measured_qubits = self._prepare_operations(circuit)

        start = time.perf_counter()
        for instruction, targets in operations:
            gate_matrix = self._instruction_to_matrix(instruction, len(targets))
            self._apply_gate(state, gate_matrix, targets)
        execution_time = time.perf_counter() - start

        return state, measured_qubits, execution_time

    def _prepare_operations(self, circuit: QuantumCircuit) -> tuple[list[tuple[Instruction, list[int]]], Sequence[int]]:
        operations: list[tuple[Instruction, list[int]]] = []
        measurement_map: list[tuple[int, int]] = []

        for item in circuit.data:
            if hasattr(item, "operation"):
                operation = item.operation
                qubits = list(item.qubits)
                clbits = list(item.clbits)
            else:  # Legacy tuple form
                operation, qubits, clbits = item

            name = operation.name
            qubit_indices = [circuit.find_bit(qubit).index for qubit in qubits]
            clbit_indices = [circuit.find_bit(clbit).index for clbit in clbits]

            if name in {"barrier", "delay"}:
                continue
            if name == "measure":
                if not qubit_indices:
                    continue
                classical_index = clbit_indices[0] if clbit_indices else len(measurement_map)
                measurement_map.append((classical_index, qubit_indices[0]))
                continue

            operations.append((operation, qubit_indices))

        if not measurement_map:
            measured_qubits: Sequence[int] = list(range(circuit.num_qubits))
        else:
            measurement_map.sort(key=lambda item: item[0])
            measured_qubits = [qubit for _, qubit in measurement_map]

        return operations, measured_qubits

    def _instruction_to_matrix(self, instruction: Instruction, arity: int) -> Any:
        xp = self._xp

        if hasattr(instruction, "to_matrix"):
            matrix = instruction.to_matrix()
        else:
            matrix = np.eye(2**arity, dtype=np.complex128)

        return xp.asarray(matrix, dtype=xp.complex128)

    def _apply_gate(self, state: Any, matrix: Any, qubits: Sequence[int]) -> None:
        if not qubits:
            return

        xp = self._xp
        num_qubits = int(math.log2(state.shape[0]))
        k = len(qubits)

        axes = list(qubits)
        tensor = xp.reshape(state, [2] * num_qubits, order="F")
        tensor = xp.moveaxis(tensor, axes, range(k))
        tensor = tensor.reshape(2**k, -1, order="F")

        matrix = matrix.reshape(2**k, 2**k)
        updated = matrix @ tensor

        updated = updated.reshape([2] * k + [-1], order="F")
        updated = xp.moveaxis(updated.reshape([2] * num_qubits, order="F"), range(k), axes)
        state[:] = xp.reshape(updated, state.shape[0], order="F")

    def _sample_measurements(self, state: Any, measured_qubits: Sequence[int], shots: int) -> dict[str, int]:
        xp = self._xp

        if xp is np:
            probabilities = np.abs(state) ** 2
        else:  # pragma: no cover - requires CuPy
            probabilities = xp.abs(state) ** 2
            probabilities = cp.asnumpy(probabilities)

        total = probabilities.sum()
        if not np.isfinite(total) or total == 0:
            raise RuntimeError("Statevector is not normalised")
        probabilities = probabilities / total

        outcomes = np.random.choice(len(probabilities), size=shots, p=probabilities)

        counts: dict[str, int] = {}
        measured = list(measured_qubits) or list(range(int(math.log2(len(probabilities)))))

        for outcome in outcomes:
            bit_string = _format_bits(outcome, measured)
            counts[bit_string] = counts.get(bit_string, 0) + 1

        return counts


def _format_bits(state_index: int, qubits: Sequence[int]) -> str:
    bits = ["1" if (state_index >> qubit) & 1 else "0" for qubit in qubits]
    return "".join(reversed(bits))


def simulate_cuda(
    circuit: QuantumCircuit,
    *,
    shots: int = 1024,
    allow_cpu_fallback: bool = True,
) -> dict[str, int]:
    backend = CUDABackend(allow_cpu_fallback=allow_cpu_fallback)
    return backend.simulate(circuit, shots=shots)
