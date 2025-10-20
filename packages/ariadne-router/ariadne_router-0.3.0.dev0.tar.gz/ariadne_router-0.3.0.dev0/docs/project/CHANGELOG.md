# Changelog

All notable changes to Ariadne will be documented here.

## Unreleased

- Replace the placeholder CUDA backend with a lightweight statevector
  implementation that falls back to the CPU when CUDA is unavailable.
- Remove unverifiable performance claims and update the documentation to
  describe the current behaviour.
- Refresh the routing heuristics and compatibility helpers used by legacy
  tests.
- Add minimal testing and verification utilities (CUDA backend tests, ZNE shim,
  ZX cancellation helper).
- Introduce `benchmarks/cuda_vs_cpu.py` to compare Ariadne's CUDA and CPU modes
  against Qiskit's basic simulator.
