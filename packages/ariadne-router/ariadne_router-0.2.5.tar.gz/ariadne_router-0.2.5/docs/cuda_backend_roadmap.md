# CUDA Backend Roadmap

This note collects follow-up ideas for the Ariadne CUDA backend. Keep it short
and actionable so we can turn items into issues/PRs later.

## Kernel and Memory Optimisations
- Replace the gate-by-gate matrix multiplies with fused CuPy RawKernels or
  batched GEMMs.
- Reuse statevector buffers across runs; integrate a CuPy memory pool and track
  usage metrics.
- Explore multi-shot sampling directly on the GPU to avoid host round-trips.

## Benchmarking & Validation
- Extend `benchmarks/cuda_vs_cpu.py` with bigger circuits (≥26 qubits) and
  automatically warm up the GPU before timed runs.
- Capture results in JSON and plot trends; check against Qiskit Aer GPU once a
  licence-friendly path is available.
- Run nightly smoke benchmarks on representative hardware (RTX 3080, laptop GPU).

## API & Usability
- Expose a `CUDABackend.simulate_statevector` shortcut that returns both the
  GPU array and a NumPy copy without reallocation.
- Surface performance telemetry (timings, memory) through
  `SimulationResult.metadata` for dashboards.

## Stretch Goals
- Investigate multi-GPU sharding (segment circuits, overlap transfers).
- Prototype hybrid routing where CUDA handles Clifford layers and Qiskit/Aer
  handles non-Clifford segments.
