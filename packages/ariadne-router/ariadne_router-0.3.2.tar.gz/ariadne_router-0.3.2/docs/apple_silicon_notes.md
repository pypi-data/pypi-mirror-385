**Apple‑Silicon Notes**

- Unified memory: plan around total system RAM; default cap is 24 GiB for TN and SV.
- Thread caps: prefer moderate parallelism to avoid oversubscription (e.g., OMP_NUM_THREADS=6–8).
- Qiskit Aer on arm64: use `AerSimulator(method="statevector")` and prefer single precision when acceptable.
- JAX‑Metal: only useful for real‑valued, float32 kernels; complex dtypes and float64 are not supported as of 2025. We automatically fall back to CPU (NumPy) for complex arrays and warn once.
- Tensor networks: use cotengra with `max_memory` to enforce peak memory; enable slicing to respect the cap.

When to use JAX‑Metal
- Real‑valued heuristics for contraction planning or scoring candidates.
- Not for complex wavefunctions or exact TN contractions; fallback engages and runs CPU path.

Environment
- Use conda‑forge arm64 builds. See `environment.yml` for a reproducible setup, and the `Dockerfile` (arm64 base) for containerized runs.
