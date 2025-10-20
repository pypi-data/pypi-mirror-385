from __future__ import annotations

import time

import numpy as np

from examples._util import write_report


def main() -> None:
    try:
        import stim
    except Exception as e:
        path = write_report("02_stim_qec", f"Stim unavailable: {e}\n")
        print(f"Wrote report to {path}")
        return

    # Small stabilizer benchmark to estimate throughput
    n = 200  # qubits
    depth = 50
    shots = 5000

    circ = stim.Circuit()
    for i in range(n):
        circ.append_operation("H", [i])
    rng = np.random.default_rng(1234)
    for _ in range(depth):
        # random CZs on neighboring pairs
        for i in range(0, n - 1, 2):
            circ.append_operation("CZ", [i, i + 1])
        # random X flips
        flips = np.where(rng.random(n) < 0.05)[0].tolist()
        if flips:
            circ.append_operation("X", flips)
    for i in range(n):
        circ.append_operation("M", [i])

    t0 = time.perf_counter()
    sampler = circ.compile_sampler()
    _ = sampler.sample(shots, rand_seed=1234)
    t1 = time.perf_counter()
    sps = shots / (t1 - t0)
    report = f"""
# Stim QEC sampling throughput (proxy)

- Qubits: {n}
- Depth: {depth}
- Shots: {shots}
- Samples/sec: {sps:.1f}
Note: Decoder not included; this measures sampler throughput only.
"""
    path = write_report("02_stim_qec", report)
    print(f"Wrote report to {path}")


if __name__ == "__main__":
    main()
