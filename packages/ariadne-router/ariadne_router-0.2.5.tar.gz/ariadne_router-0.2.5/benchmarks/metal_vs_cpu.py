from __future__ import annotations

import argparse
import json
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass

from qiskit import QuantumCircuit
from qiskit.providers.basic_provider import BasicProvider

from ariadne.backends.metal_backend import MetalBackend, get_metal_info, is_metal_available


@dataclass
class BenchmarkCase:
    name: str
    circuit: QuantumCircuit


@dataclass
class BenchmarkResult:
    circuit: str
    backend: str
    shots: int
    execution_time: float
    success: bool
    error: str | None = None


def create_benchmark_cases() -> list[BenchmarkCase]:
    """Create a set of benchmark circuits."""

    cases = []

    # 1. Small Clifford circuit
    circuit = QuantumCircuit(3, 3)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.cx(1, 2)
    circuit.measure_all()
    cases.append(BenchmarkCase("small_clifford", circuit))

    # 2. Medium Clifford circuit
    circuit = QuantumCircuit(5, 5)
    for i in range(4):
        circuit.h(i)
        circuit.cx(i, i + 1)
    circuit.measure_all()
    cases.append(BenchmarkCase("medium_clifford", circuit))

    # 3. Small general circuit
    circuit = QuantumCircuit(3, 3)
    circuit.h(0)
    circuit.ry(0.5, 1)
    circuit.cx(0, 1)
    circuit.rz(0.3, 2)
    circuit.cx(1, 2)
    circuit.measure_all()
    cases.append(BenchmarkCase("small_general", circuit))

    # 4. Medium general circuit
    circuit = QuantumCircuit(5, 5)
    for i in range(4):
        circuit.h(i)
        circuit.ry(0.1 * i, i)
        circuit.cx(i, i + 1)
    circuit.measure_all()
    cases.append(BenchmarkCase("medium_general", circuit))

    # 5. Large Clifford circuit
    circuit = QuantumCircuit(8, 8)
    for i in range(7):
        circuit.h(i)
        circuit.cx(i, i + 1)
    circuit.measure_all()
    cases.append(BenchmarkCase("large_clifford", circuit))

    return cases


def run_qiskit_backend(circuit: QuantumCircuit, shots: int) -> None:
    """Run circuit on Qiskit CPU backend."""
    provider = BasicProvider()
    backend = provider.get_backend("basic_simulator")
    job = backend.run(circuit, shots=shots)
    job.result()


def run_metal_backend(circuit: QuantumCircuit, shots: int) -> None:
    """Run circuit on Metal backend."""
    backend = MetalBackend(allow_cpu_fallback=True)
    backend.simulate(circuit, shots=shots)


def benchmark_backend(
    backend_func: Callable[[QuantumCircuit, int], None],
    circuit: QuantumCircuit,
    circuit_name: str,
    shots: int,
    backend_name: str,
    warmup_runs: int = 3,
    timing_runs: int = 5,
) -> BenchmarkResult:
    """Benchmark a single backend with a circuit."""

    # Warmup runs
    for _ in range(warmup_runs):
        try:
            backend_func(circuit, shots)
        except Exception:
            pass  # Ignore warmup errors

    # Timing runs
    times = []
    success = True
    error = None

    for _ in range(timing_runs):
        try:
            start = time.perf_counter()
            backend_func(circuit, shots)
            end = time.perf_counter()
            times.append(end - start)
        except Exception as e:
            success = False
            error = str(e)
            break

    if success and times:
        execution_time = sum(times) / len(times)
    else:
        execution_time = float("inf")

    return BenchmarkResult(
        circuit=circuit_name,
        backend=backend_name,
        shots=shots,
        execution_time=execution_time,
        success=success,
        error=error,
    )


def run_benchmarks(
    cases: list[BenchmarkCase],
    shots: int = 1024,
    output_file: str | None = None,
) -> list[BenchmarkResult]:
    """Run benchmarks for all cases and backends."""

    results = []

    print("🚀 Starting Metal vs CPU benchmarks...")
    print(f"Metal available: {is_metal_available()}")
    print(f"Metal info: {get_metal_info()}")
    print()

    for case in cases:
        print(f"Testing {case.name}...")

        # Qiskit CPU backend
        print("  Running Qiskit CPU...")
        result = benchmark_backend(
            run_qiskit_backend,
            case.circuit,
            case.name,
            shots,
            "qiskit_cpu",
        )
        results.append(result)
        print(f"    Time: {result.execution_time:.4f}s")

        # Metal backend
        print("  Running Metal...")
        result = benchmark_backend(
            run_metal_backend,
            case.circuit,
            case.name,
            shots,
            "metal",
        )
        results.append(result)
        if result.success:
            print(f"    Time: {result.execution_time:.4f}s")
        else:
            print(f"    Error: {result.error}")

        print()

    # Save results
    if output_file:
        with open(output_file, "w") as f:
            json.dump([asdict(r) for r in results], f, indent=2)
        print(f"Results saved to {output_file}")

    return results


def print_summary(results: list[BenchmarkResult]) -> None:
    """Print benchmark summary."""

    print("📊 Benchmark Summary")
    print("=" * 50)

    # Group results by circuit
    by_circuit = {}
    for result in results:
        if result.circuit not in by_circuit:
            by_circuit[result.circuit] = {}
        by_circuit[result.circuit][result.backend] = result

    for circuit_name, backends in by_circuit.items():
        print(f"\n{circuit_name}:")

        if "qiskit_cpu" in backends and "metal" in backends:
            cpu_result = backends["qiskit_cpu"]
            metal_result = backends["metal"]

            if cpu_result.success and metal_result.success:
                speedup = cpu_result.execution_time / metal_result.execution_time
                print(f"  CPU:  {cpu_result.execution_time:.4f}s")
                print(f"  Metal: {metal_result.execution_time:.4f}s")
                print(f"  Speedup: {speedup:.2f}x")
            else:
                print(f"  CPU:  {'✓' if cpu_result.success else '✗'}")
                print(f"  Metal: {'✓' if metal_result.success else '✗'}")
        else:
            for backend, result in backends.items():
                status = "✓" if result.success else "✗"
                time_str = f"{result.execution_time:.4f}s" if result.success else "failed"
                print(f"  {backend}: {status} {time_str}")


def main() -> None:
    """Main benchmark function."""

    parser = argparse.ArgumentParser(description="Benchmark Metal vs CPU backends")
    parser.add_argument("--shots", type=int, default=1024, help="Number of shots")
    parser.add_argument("--output", type=str, help="Output JSON file")
    parser.add_argument("--cases", nargs="+", help="Specific test cases to run")

    args = parser.parse_args()

    # Get test cases
    all_cases = create_benchmark_cases()
    if args.cases:
        cases = [c for c in all_cases if c.name in args.cases]
        if not cases:
            print(f"Error: No matching test cases found. Available: {[c.name for c in all_cases]}")
            return
    else:
        cases = all_cases

    # Run benchmarks
    results = run_benchmarks(cases, args.shots, args.output)

    # Print summary
    print_summary(results)


if __name__ == "__main__":
    main()
