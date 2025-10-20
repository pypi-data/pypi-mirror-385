"""
CUDA kernels for optimized quantum operations.

This module provides custom CUDA kernels for high-performance quantum gate operations,
state vector manipulations, and circuit simulations optimized for NVIDIA GPUs.
"""

import logging
from typing import Any

import numpy as np

try:
    import cupy as cp

    CUPY_AVAILABLE = True
except ImportError:
    CUPY_AVAILABLE = False
    cp = None

logger = logging.getLogger(__name__)


class CUDAKernels:
    """Manager for custom CUDA kernels for quantum operations."""

    def __init__(self) -> None:
        self.kernels: dict[str, Any] = {}
        self._compiled = False

        if not CUPY_AVAILABLE:
            logger.warning("CuPy not available, CUDA kernels disabled")
            return

        self._compile_kernels()

    def _compile_kernels(self) -> None:
        """Compile all CUDA kernels for quantum operations."""
        if not CUPY_AVAILABLE:
            return

        try:
            # Single qubit gate kernel
            self.kernels["single_qubit_gate"] = cp.RawKernel(
                r"""
            extern "C" __global__
            void single_qubit_gate(
                const float2* state,
                float2* result,
                const float2* gate,
                int target_qubit,
                int n_qubits,
                int n_states
            ) {
                int idx = blockIdx.x * blockDim.x + threadIdx.x;
                if (idx >= n_states) return;

                int target_mask = 1 << target_qubit;
                int high_bits = idx & ~((target_mask << 1) - 1);
                int low_bits = idx & (target_mask - 1);
                int state_idx = high_bits | low_bits;
                int pair_idx = state_idx | target_mask;

                if (idx & target_mask) return; // Only process lower states

                float2 s0 = state[state_idx];
                float2 s1 = state[pair_idx];

                // Matrix multiplication: gate * [s0; s1]
                result[state_idx] = make_float2(
                    gate[0].x * s0.x - gate[0].y * s0.y + gate[1].x * s1.x - gate[1].y * s1.y,
                    gate[0].x * s0.y + gate[0].y * s0.x + gate[1].x * s1.y + gate[1].y * s1.x
                );

                result[pair_idx] = make_float2(
                    gate[2].x * s0.x - gate[2].y * s0.y + gate[3].x * s1.x - gate[3].y * s1.y,
                    gate[2].x * s0.y + gate[2].y * s0.x + gate[3].x * s1.y + gate[3].y * s1.x
                );
            }
            """,
                "single_qubit_gate",
            )

            # Two qubit gate kernel
            self.kernels["two_qubit_gate"] = cp.RawKernel(
                r"""
            extern "C" __global__
            void two_qubit_gate(
                const float2* state,
                float2* result,
                const float2* gate,
                int control_qubit,
                int target_qubit,
                int n_qubits,
                int n_states
            ) {
                int idx = blockIdx.x * blockDim.x + threadIdx.x;
                if (idx >= n_states / 4) return;

                int control_mask = 1 << control_qubit;
                int target_mask = 1 << target_qubit;
                int both_mask = control_mask | target_mask;

                // Optimized index calculation for state_base (s00 index)
                // This replaces the slow loop by using bit manipulation to insert
                // two zero bits at the control and target qubit positions.
                int q_a = (control_qubit < target_qubit) ? control_qubit : target_qubit;
                int q_b = (control_qubit > target_qubit) ? control_qubit : target_qubit;

                // 1. Low part: bits < q_a
                int low_mask = (1 << q_a) - 1;
                int low_bits = idx & low_mask;

                // 2. Mid part: bits between q_a and q_b
                // The mid bits start at position q_a in idx.
                int mid_shift_in_idx = q_a;
                int mid_bit_count = q_b - q_a - 1;

                // mid_mask_in_idx is a mask of mid_bit_count ones
                int mid_mask_in_idx = (1 << mid_bit_count) - 1;
                int mid_bits_in_idx = (idx >> mid_shift_in_idx) & mid_mask_in_idx;

                // Shift mid bits to their position in state_base (skip q_a)
                int mid_bits_shifted = mid_bits_in_idx << (q_a + 1);

                // 3. High part: bits > q_b
                // The high bits start at position q_b - 1 in idx.
                int high_shift_in_idx = q_b - 1;
                int high_bits_in_idx = idx >> high_shift_in_idx;

                // Shift high bits to their position in state_base (skip q_a and q_b)
                int high_bits_shifted = high_bits_in_idx << (q_b + 1);

                int state_base = low_bits | mid_bits_shifted | high_bits_shifted;

                // Four computational basis states
                int s00 = state_base;
                int s01 = state_base | target_mask;
                int s10 = state_base | control_mask;
                int s11 = state_base | both_mask;

                float2 amp00 = state[s00];
                float2 amp01 = state[s01];
                float2 amp10 = state[s10];
                float2 amp11 = state[s11];

                // Apply 4x4 gate matrix
                for (int i = 0; i < 4; i++) {
                    float2 new_amp = make_float2(0.0f, 0.0f);

                    // Matrix-vector multiplication
                    float2 amplitudes[4] = {amp00, amp01, amp10, amp11};
                    for (int j = 0; j < 4; j++) {
                        float2 gate_elem = gate[i * 4 + j];
                        float2 amp = amplitudes[j];

                        new_amp.x += gate_elem.x * amp.x - gate_elem.y * amp.y;
                        new_amp.y += gate_elem.x * amp.y + gate_elem.y * amp.x;
                    }

                    int states[4] = {s00, s01, s10, s11};
                    result[states[i]] = new_amp;
                }
            }
            """,
                "two_qubit_gate",
            )

            # Measurement kernel
            self.kernels["measure_probabilities"] = cp.RawKernel(
                r"""
            extern "C" __global__
            void measure_probabilities(
                const float2* state,
                float* probabilities,
                int n_states
            ) {
                int idx = blockIdx.x * blockDim.x + threadIdx.x;
                if (idx >= n_states) return;

                float2 amp = state[idx];
                probabilities[idx] = amp.x * amp.x + amp.y * amp.y;
            }
            """,
                "measure_probabilities",
            )

            # State vector normalization kernel
            self.kernels["normalize_state"] = cp.RawKernel(
                r"""
            extern "C" __global__
            void normalize_state(
                float2* state,
                float norm,
                int n_states
            ) {
                int idx = blockIdx.x * blockDim.x + threadIdx.x;
                if (idx >= n_states) return;

                state[idx].x /= norm;
                state[idx].y /= norm;
            }
            """,
                "normalize_state",
            )

            # Expectation value kernel
            self.kernels["expectation_value"] = cp.RawKernel(
                r"""
            extern "C" __global__
            void expectation_value(
                const float2* state,
                const float2* operator_diag,
                float2* partial_results,
                int n_states
            ) {
                int idx = blockIdx.x * blockDim.x + threadIdx.x;
                if (idx >= n_states) return;

                float2 amp = state[idx];
                float2 op_elem = operator_diag[idx];

                // <psi|O|psi> = sum_i conj(psi_i) * O_ii * psi_i
                partial_results[idx] = make_float2(
                    (amp.x * op_elem.x + amp.y * op_elem.y) * amp.x +
                    (amp.x * op_elem.y - amp.y * op_elem.x) * amp.y,
                    (amp.x * op_elem.y - amp.y * op_elem.x) * amp.x -
                    (amp.x * op_elem.x + amp.y * op_elem.y) * amp.y
                );
            }
            """,
                "expectation_value",
            )

            self._compiled = True
            logger.info(f"Compiled {len(self.kernels)} CUDA kernels successfully")

        except Exception as e:
            logger.error(f"Failed to compile CUDA kernels: {e}")
            self.kernels = {}

    def apply_single_qubit_gate(self, state: cp.ndarray, gate: cp.ndarray, target_qubit: int) -> cp.ndarray:
        """Apply single qubit gate using custom CUDA kernel."""
        if not self._compiled or "single_qubit_gate" not in self.kernels:
            return self._fallback_single_qubit_gate(state, gate, target_qubit)

        n_qubits = int(np.log2(len(state)))
        n_states = len(state)
        result = cp.zeros_like(state)

        # Convert gate to complex64 if necessary
        gate_gpu = cp.asarray(gate, dtype=cp.complex64)

        # Launch kernel
        block_size = 256
        grid_size = (n_states + block_size - 1) // block_size

        self.kernels["single_qubit_gate"](
            (grid_size,), (block_size,), (state, result, gate_gpu, target_qubit, n_qubits, n_states)
        )

        return result

    def apply_two_qubit_gate(
        self, state: cp.ndarray, gate: cp.ndarray, control_qubit: int, target_qubit: int
    ) -> cp.ndarray:
        """Apply two qubit gate using custom CUDA kernel."""
        if not self._compiled or "two_qubit_gate" not in self.kernels:
            return self._fallback_two_qubit_gate(state, gate, control_qubit, target_qubit)

        n_qubits = int(np.log2(len(state)))
        n_states = len(state)
        result = cp.zeros_like(state)

        # Convert gate to complex64 if necessary
        gate_gpu = cp.asarray(gate.flatten(), dtype=cp.complex64)

        # Launch kernel
        block_size = 256
        grid_size = (n_states // 4 + block_size - 1) // block_size

        self.kernels["two_qubit_gate"](
            (grid_size,),
            (block_size,),
            (state, result, gate_gpu, control_qubit, target_qubit, n_qubits, n_states),
        )

        return result

    def measure_probabilities(self, state: cp.ndarray) -> cp.ndarray:
        """Calculate measurement probabilities using custom CUDA kernel."""
        if not self._compiled or "measure_probabilities" not in self.kernels:
            return cp.abs(state) ** 2

        n_states = len(state)
        probabilities = cp.zeros(n_states, dtype=cp.float32)

        # Launch kernel
        block_size = 256
        grid_size = (n_states + block_size - 1) // block_size

        self.kernels["measure_probabilities"]((grid_size,), (block_size,), (state, probabilities, n_states))

        return probabilities

    def normalize_state(self, state: cp.ndarray) -> cp.ndarray:
        """Normalize state vector using custom CUDA kernel."""
        if not self._compiled or "normalize_state" not in self.kernels:
            norm = cp.linalg.norm(state)
            return state / norm

        n_states = len(state)
        norm = float(cp.linalg.norm(state))

        # Launch kernel
        block_size = 256
        grid_size = (n_states + block_size - 1) // block_size

        self.kernels["normalize_state"]((grid_size,), (block_size,), (state, norm, n_states))

        return state

    def calculate_expectation_value(self, state: cp.ndarray, operator_diagonal: cp.ndarray) -> complex:
        """Calculate expectation value using custom CUDA kernel."""
        if not self._compiled or "expectation_value" not in self.kernels:
            return float(cp.real(cp.vdot(state, operator_diagonal * state)))

        n_states = len(state)
        partial_results = cp.zeros(n_states, dtype=cp.complex64)

        # Launch kernel
        block_size = 256
        grid_size = (n_states + block_size - 1) // block_size

        self.kernels["expectation_value"](
            (grid_size,), (block_size,), (state, operator_diagonal, partial_results, n_states)
        )

        return complex(cp.sum(partial_results))

    def _fallback_single_qubit_gate(self, state: cp.ndarray, gate: cp.ndarray, target_qubit: int) -> cp.ndarray:
        """Fallback implementation for single qubit gates."""
        int(np.log2(len(state)))
        n_states = len(state)
        result = cp.copy(state)

        target_mask = 1 << target_qubit

        for i in range(0, n_states, target_mask << 1):
            for j in range(target_mask):
                idx0 = i + j
                idx1 = idx0 + target_mask

                amp0 = state[idx0]
                amp1 = state[idx1]

                result[idx0] = gate[0, 0] * amp0 + gate[0, 1] * amp1
                result[idx1] = gate[1, 0] * amp0 + gate[1, 1] * amp1

        return result

    def _fallback_two_qubit_gate(
        self, state: cp.ndarray, gate: cp.ndarray, control_qubit: int, target_qubit: int
    ) -> cp.ndarray:
        """Fallback implementation for two qubit gates."""
        int(np.log2(len(state)))
        n_states = len(state)
        result = cp.copy(state)

        control_mask = 1 << control_qubit
        target_mask = 1 << target_qubit

        for i in range(n_states):
            if not (i & control_mask) and not (i & target_mask):
                # Base state |00⟩ relative to control and target
                idx00 = i
                idx01 = i | target_mask
                idx10 = i | control_mask
                idx11 = i | control_mask | target_mask

                amps = cp.array([state[idx00], state[idx01], state[idx10], state[idx11]])
                new_amps = gate @ amps

                result[idx00] = new_amps[0]
                result[idx01] = new_amps[1]
                result[idx10] = new_amps[2]
                result[idx11] = new_amps[3]

        return result

    @property
    def is_available(self) -> bool:
        """Check if CUDA kernels are available and compiled."""
        return CUPY_AVAILABLE and self._compiled

    def get_kernel_info(self) -> dict[str, Any]:
        """Get information about compiled kernels."""
        if not self.is_available:
            return {"available": False, "reason": "CuPy not available or compilation failed"}

        return {
            "available": True,
            "kernels": list(self.kernels.keys()),
            "cuda_version": cp.cuda.runtime.runtimeGetVersion() if CUPY_AVAILABLE else None,
            "device_count": cp.cuda.runtime.getDeviceCount() if CUPY_AVAILABLE else 0,
        }


# Global kernel manager instance
_kernel_manager = None


def get_cuda_kernels() -> CUDAKernels:
    """Get the global CUDA kernels manager instance."""
    global _kernel_manager
    if _kernel_manager is None:
        _kernel_manager = CUDAKernels()
    return _kernel_manager


# Utility functions for common quantum operations
def pauli_x_kernel(state: cp.ndarray, qubit: int) -> cp.ndarray:
    """Apply Pauli-X gate using CUDA kernel."""
    gate = cp.array([[0, 1], [1, 0]], dtype=cp.complex64)
    return get_cuda_kernels().apply_single_qubit_gate(state, gate, qubit)


def pauli_y_kernel(state: cp.ndarray, qubit: int) -> cp.ndarray:
    """Apply Pauli-Y gate using CUDA kernel."""
    gate = cp.array([[0, -1j], [1j, 0]], dtype=cp.complex64)
    return get_cuda_kernels().apply_single_qubit_gate(state, gate, qubit)


def pauli_z_kernel(state: cp.ndarray, qubit: int) -> cp.ndarray:
    """Apply Pauli-Z gate using CUDA kernel."""
    gate = cp.array([[1, 0], [0, -1]], dtype=cp.complex64)
    return get_cuda_kernels().apply_single_qubit_gate(state, gate, qubit)


def hadamard_kernel(state: cp.ndarray, qubit: int) -> cp.ndarray:
    """Apply Hadamard gate using CUDA kernel."""
    gate = cp.array([[1, 1], [1, -1]], dtype=cp.complex64) / cp.sqrt(2)
    return get_cuda_kernels().apply_single_qubit_gate(state, gate, qubit)


def cnot_kernel(state: cp.ndarray, control: int, target: int) -> cp.ndarray:
    """Apply CNOT gate using CUDA kernel."""
    gate = cp.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], dtype=cp.complex64)
    return get_cuda_kernels().apply_two_qubit_gate(state, gate, control, target)


def rotation_x_kernel(state: cp.ndarray, qubit: int, theta: float) -> cp.ndarray:
    """Apply rotation around X-axis using CUDA kernel."""
    cos_half = cp.cos(theta / 2)
    sin_half = cp.sin(theta / 2)
    gate = cp.array([[cos_half, -1j * sin_half], [-1j * sin_half, cos_half]], dtype=cp.complex64)
    return get_cuda_kernels().apply_single_qubit_gate(state, gate, qubit)


def rotation_y_kernel(state: cp.ndarray, qubit: int, theta: float) -> cp.ndarray:
    """Apply rotation around Y-axis using CUDA kernel."""
    cos_half = cp.cos(theta / 2)
    sin_half = cp.sin(theta / 2)
    gate = cp.array([[cos_half, -sin_half], [sin_half, cos_half]], dtype=cp.complex64)
    return get_cuda_kernels().apply_single_qubit_gate(state, gate, qubit)


def rotation_z_kernel(state: cp.ndarray, qubit: int, theta: float) -> cp.ndarray:
    """Apply rotation around Z-axis using CUDA kernel."""
    exp_neg = cp.exp(-1j * theta / 2)
    exp_pos = cp.exp(1j * theta / 2)
    gate = cp.array([[exp_neg, 0], [0, exp_pos]], dtype=cp.complex64)
    return get_cuda_kernels().apply_single_qubit_gate(state, gate, qubit)
