**Apple‑Silicon Notes (Ariadne‑mac)**

- Unified memory: SV and TN respect a default 24 GiB cap; adjust with `--mem-cap-gib`.
- Thread caps: set `OMP_NUM_THREADS`, `VECLIB_MAXIMUM_THREADS`, `OPENBLAS_NUM_THREADS`; or pass `--threads`.
- State‑vector (Qiskit Aer): prefer `fp32` when acceptable to raise n‑qubit ceiling; use `--precision fp32|fp64`.
- Tensor‑networks (quimb+cotengra): planner uses `max_memory` to slice under the cap; logs tree and slice count.
- Tensor‑networks (quimb+cotengra): real contraction uses `HyperOptimizer(max_memory=<cap>)` with dynamic slicing; logs tree, nslices, and planned peak bytes; plans saved under `reports/trees/`.
- Decision diagrams (MQT DDSIM): good for redundancy‑heavy or structured circuits.
- JAX‑Metal: optional, real‑valued float32 helpers only (path‑finding/cost models). Complex and float64 not supported; code auto‑falls back to CPU with a one‑time warning.
  Use only for scoring/heuristics — core contractions and complex math run on CPU.

Reproducibility
- Deterministic seeds in examples/tests.
- Router/execution logs JSONL to `reports/runlogs/` with timestamps, chosen backend, metrics, and peak memory.

Environment
- Use `environment.yml` (conda‑forge arm64) or pip wheels; `Dockerfile` targets arm64 base.

Concurrency
- macOS uses 'spawn' start method for multiprocessing by default. We parallelize TN slices with ProcessPoolExecutor and set `OMP_NUM_THREADS=1` inside workers. Use `--threads` on the CLI to cap overall CPU pressure.
