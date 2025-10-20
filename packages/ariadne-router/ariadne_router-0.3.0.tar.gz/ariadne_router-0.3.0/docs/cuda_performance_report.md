# Ariadne CUDA Performance Report

## Test Environment
- **Hardware**: PC with NVIDIA GeForce RTX 3080 (10GB, 68 SMs, Compute 8.6)
- **Software**: Ariadne with CuPy CUDA backend
- **Benchmark**: benchmarks/cuda_vs_cpu.py

## Performance Results

### Summary
- **6.2x speedup** on Clifford circuits (20 qubits) vs Qiskit
- **2.2x speedup** on general quantum circuits (16 qubits) vs Qiskit
- Optimal for circuits with 16+ qubits where GPU overhead is amortized

### Detailed Benchmarks

| Circuit Type | Qubits | Depth | Ariadne CUDA | Qiskit Basic | Speedup |
|--------------|--------|-------|--------------|--------------|---------|
| Bell Ladder | 12 | 12 | 0.051s | 0.006s | 0.1x |
| Clifford Chain | 20 | 10 | 1.536s | 9.569s | **6.2x** |
| General Mixed | 16 | 8 | 0.124s | 0.274s | **2.2x** |

### Analysis

1. **Small Circuits (<16 qubits)**: GPU overhead dominates, CPU backends perform better
2. **Medium Circuits (16-20 qubits)**: GPU begins to show advantage, especially for Clifford circuits
3. **Large Circuits (20+ qubits)**: Significant GPU advantage expected (not yet benchmarked)

### Implementation Notes

- Current implementation uses generic matrix multiplication
- Future optimizations planned: custom kernels, batching, memory pooling
- CPU fallback ensures compatibility when CUDA unavailable

## Comparison to Other Quantum APIs

| Framework | GPU Support | Speedup (20 qubits) | Fallback |
|-----------|-------------|---------------------|----------|
| **Ariadne** | CuPy/CUDA | 6.2x | NumPy |
| Qiskit Aer | Thrust | ~10-100x* | No |
| PennyLane | Lightning | ~5-50x* | No |
| Cirq | None | - | - |
| Qulacs | CUDA | ~10-100x* | No |

*Vendor-reported figures for optimized kernels

### Key Differentiators

1. **Automatic Backend Selection**: Ariadne intelligently routes to optimal backend
2. **Graceful Fallback**: Works on any system, GPU accelerates when available
3. **Information-Theoretic Routing**: Uses circuit entropy for backend selection
4. **Unified API**: Consistent interface across Stim, Qiskit, TN, and CUDA backends
