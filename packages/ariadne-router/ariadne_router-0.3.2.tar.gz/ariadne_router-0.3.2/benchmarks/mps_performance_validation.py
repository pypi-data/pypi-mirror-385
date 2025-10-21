#!/usr/bin/env python3
"""
Performance validation benchmark for MPSBackend against a standard State Vector simulator.

This script demonstrates the expected exponential speedup of MPS for low-entanglement
circuits by comparing simulation times across a range of qubit counts (10 to 20).
"""

import math
import statistics
import time
from collections.abc import Callable
from random import Random

from qiskit import QuantumCircuit
from qiskit.providers.basic_provider import BasicProvider

# Assuming ariadne is installed or path is set up correctly
# Assuming ariadne is installed or path is set up correctly
from ariadne.backends.mps_backend import MPSBackend

# --- Utility Functions ---


def time_function(fn: Callable[[], object], repetitions: int) -> tuple[float, float, bool, str | None]:
    """Times a function execution over multiple repetitions."""
    timings: list[float] = []
    success = True
    error = None

    for _ in range(repetitions):
        start = time.perf_counter()
        try:
            fn()
        except Exception as exc:
            success = False
            error = str(exc)
            break
        timings.append(time.perf_counter() - start)

    if not success:
        return float("inf"), 0.0, False, error

    if not timings:
        return float("inf"), 0.0, False, "No timings recorded"

    mean_time = statistics.mean(timings)
    stdev = statistics.pstdev(timings) if len(timings) > 1 else 0.0

    return mean_time, stdev, True, None


# --- Circuit Generation ---


def build_low_entanglement_circuit(num_qubits: int, depth: int) -> QuantumCircuit:
    """
    Generates a shallow, low-entanglement circuit suitable for MPS simulation.
    Uses random single-qubit rotations and nearest-neighbor CNOTs (brick-layer).
    """
    qc = QuantumCircuit(num_qubits, num_qubits)
    rng = Random(42)  # Fixed seed for reproducibility

    for _ in range(depth):
        # Single qubit rotations
        for i in range(num_qubits):
            qc.rx(rng.random() * math.pi, i)
            qc.rz(rng.random() * math.pi, i)

        # Nearest-neighbor CNOTs (brick-layer pattern)
        # Even pairs
        for i in range(0, num_qubits - 1, 2):
            qc.cx(i, i + 1)
        # Odd pairs
        for i in range(1, num_qubits - 1, 2):
            qc.cx(i, i + 1)

    qc.measure_all()
    return qc


# --- Main Benchmark Logic ---


def run_mps_validation_benchmark(qubit_range: range, depth: int = 5, repetitions: int = 3, shots: int = 1024):
    """
    Compares MPSBackend performance against a standard StateVectorBackend
    for low-entanglement circuits across a range of qubit counts.
    """

    print("--- MPS Performance Validation Benchmark ---")
    print(f"Circuit Depth: {depth}, Repetitions per test: {repetitions}, Shots: {shots}")
    print("-" * 50)

    # Initialize backends
    # Standard State Vector Backend (Qiskit Basic Simulator)
    qiskit_provider = BasicProvider()
    sv_backend = qiskit_provider.get_backend("basic_simulator")

    # MPS Backend (using a reasonable bond dimension for low entanglement)
    # Bond dimension 64 is typically sufficient for shallow, low-entanglement circuits.
    mps_backend = MPSBackend(max_bond_dimension=64)

    results = []

    for n_qubits in qubit_range:
        print(f"Benchmarking N={n_qubits} qubits...")
        circuit = build_low_entanglement_circuit(n_qubits, depth)

        # 1. Benchmark MPS Backend (State Vector simulation mode)
        def mps_run(current_circuit: QuantumCircuit = circuit):
            # MPSBackend.simulate returns the state vector, which is sufficient for timing
            mps_backend.simulate(current_circuit)

        mps_mean, mps_stdev, mps_success, mps_error = time_function(mps_run, repetitions)

        # 2. Benchmark Standard State Vector Backend (Qiskit Basic Simulator)
        def sv_run(current_circuit: QuantumCircuit = circuit):
            # We run the Qiskit job and wait for results
            job = sv_backend.run(current_circuit, shots=shots)
            job.result().get_counts()

        sv_mean, sv_stdev, sv_success, sv_error = time_function(sv_run, repetitions)

        results.append(
            {
                "qubits": n_qubits,
                "mps_time": mps_mean,
                "sv_time": sv_mean,
                "mps_success": mps_success,
                "sv_success": sv_success,
                "mps_error": mps_error,
                "sv_error": sv_error,
            }
        )

        # Print intermediate results
        mps_status = f"{mps_mean * 1e3:.3f} ms" if mps_success else f"FAIL ({mps_error})"
        sv_status = f"{sv_mean * 1e3:.3f} ms" if sv_success else f"FAIL ({sv_error})"

        print(f"  MPS Time: {mps_status}")
        print(f"  SV Time:  {sv_status}")

    print("\n--- Summary Table (Mean Time in ms) ---")
    print("| Qubits | MPS Backend | State Vector Backend | Speedup (SV/MPS) |")
    print("|--------|-------------|----------------------|------------------|")

    for res in results:
        mps_time_ms = res["mps_time"] * 1e3
        sv_time_ms = res["sv_time"] * 1e3

        if res["mps_success"] and res["sv_success"] and mps_time_ms > 0:
            speedup = sv_time_ms / mps_time_ms
            speedup_str = f"{speedup:.1f}x"
        else:
            speedup_str = "N/A"

        mps_str = f"{mps_time_ms:.3f}" if res["mps_success"] else "FAIL"
        sv_str = f"{sv_time_ms:.3f}" if res["sv_success"] else "FAIL"

        print(f"| {res['qubits']:<6} | {mps_str:<11} | {sv_str:<20} | {speedup_str:<16} |")


if __name__ == "__main__":
    # Run benchmark from 10 to 20 qubits (inclusive)
    run_mps_validation_benchmark(range(10, 21))
