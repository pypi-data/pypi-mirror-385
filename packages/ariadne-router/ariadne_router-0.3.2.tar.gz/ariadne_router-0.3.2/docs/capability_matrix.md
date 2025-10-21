# Ariadne Quantum Backend Capability Matrix

This document summarizes current backend coverage, hardware support, and routing intelligence.

## Major Quantum Simulators

- Implemented
  - Qiskit (fallback/basic simulator)
  - Stim (Clifford)
  - DDSIM (MQT)
  - Cirq (conversion + noise modeling)
  - PennyLane (variational/ML, QNode conversion)
  - Qulacs (CPU/GPU with fallback)
  - Tensor Networks (quimb/cotengra)
  - MPS (quimb MPS)
  - Metal (Apple Silicon hybrid)
  - CUDA (CuPy-based)
  - Intel QS (adaptor)

- Scaffolding present (safe Qiskit fallback)
  - PyQuil (Forest)
  - Braket (AWS)
  - Q# (Microsoft)
  - OpenCL (pyopencl)

- Missing (planned)
  - ProjectQ, QuTiP, Yao.jl, QuEST, XACC, TNQVM, ITensor, QuESTlink, trajectories simulators

## Hardware Acceleration

- Implemented
  - CPU, Apple Metal, CUDA, Intel QS

- Scaffolding
  - OpenCL (fallback)

- Planned
  - AMD ROCm/HIP, Intel GPU (oneAPI/Level Zero)

## Quantum Hardware Integrations (Planned)

- IBM Quantum, AWS Braket hardware, Rigetti, IonQ, Google QAI, Quantinuum, OQC

## Routing Intelligence

- Specialized filters
  - Clifford ⇒ Stim
  - Low-entanglement/chain-like ⇒ MPS
  - Tensor Network suitability ⇒ Tensor Network
  - Parameterized/variational and ML ⇒ PennyLane

- Scoring models
  - Speed/Accuracy heuristics per backend with hardware awareness (Metal/CUDA); OpenCL added
  - Performance model: heuristic (time/memory/success), calibration planned via benchmarks

## Tests

- Core suites cover CUDA, Metal, MPS, Tensor Networks, DDSIM, router selection
- Optional suites (skip-if-missing) for Cirq, PennyLane, Qulacs, PyQuil, Braket, Q#
- Variational routing test prefers PennyLane when available

## Next Milestones

- Implement Qiskit→PyQuil/Braket/Q# conversions and local sim paths
- Integrate ROCm/oneAPI backends and scoring
- Add benchmarking harness to calibrate performance model coefficients
- Add algorithm-family filters for QAOA/VQE/QFT/Grover/QEC
