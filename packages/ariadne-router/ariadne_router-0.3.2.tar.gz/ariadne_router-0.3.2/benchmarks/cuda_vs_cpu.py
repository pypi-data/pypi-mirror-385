from __future__ import annotations

import argparse
import json
import time
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass

from qiskit import QuantumCircuit
from qiskit.providers.basic_provider import BasicProvider

from ariadne.backends.cuda_backend import CUDABackend, get_cuda_info, is_cuda_available


@dataclass
class BenchmarkCase:
    name: str
    circuit: QuantumCircuit


@dataclass
class BenchmarkResult:
    circuit: str
    backend: str
    shots: int
    repetitions: int
    timings: list[float]

    @property
    def mean_time(self) -> float:
        return sum(self.timings) / len(self.timings)

    @property
    def min_time(self) -> float:
        return min(self.timings)

    @property
    def max_time(self) -> float:
        return max(self.timings)

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload.update(
            mean_time=self.mean_time,
            min_time=self.min_time,
            max_time=self.max_time,
        )
        return payload


def build_clifford_chain(n_qubits: int, depth: int) -> QuantumCircuit:
    qc = QuantumCircuit(n_qubits, n_qubits)
    for _ in range(depth):
        for i in range(n_qubits):
            qc.h(i)
            qc.s(i)
        for i in range(n_qubits - 1):
            qc.cx(i, i + 1)
    qc.measure_all()
    return qc


def build_general_circuit(n_qubits: int, depth: int) -> QuantumCircuit:
    qc = QuantumCircuit(n_qubits, n_qubits)
    for _ in range(depth):
        for i in range(n_qubits):
            qc.h(i)
        for i in range(n_qubits - 1):
            qc.cx(i, i + 1)
        for i in range(n_qubits):
            qc.t(i)
    qc.measure_all()
    return qc


def build_small_bell_ladder(n_qubits: int) -> QuantumCircuit:
    qc = QuantumCircuit(n_qubits, n_qubits)
    for i in range(0, n_qubits, 2):
        qc.h(i)
        if i + 1 < n_qubits:
            qc.cx(i, i + 1)
    qc.measure_all()
    return qc


def case_definitions() -> list[BenchmarkCase]:
    return [
        BenchmarkCase("bell_ladder_12", build_small_bell_ladder(12)),
        BenchmarkCase("clifford_chain_20", build_clifford_chain(20, depth=10)),
        BenchmarkCase("general_mixed_16", build_general_circuit(16, depth=6)),
    ]


def time_call(fn: Callable[[], object]) -> float:
    start = time.perf_counter()
    fn()
    return time.perf_counter() - start


def run_cuda_backend(circuit: QuantumCircuit, shots: int, prefer_gpu: bool) -> None:
    backend = CUDABackend(prefer_gpu=prefer_gpu, allow_cpu_fallback=True)
    backend.simulate(circuit, shots=shots)


def run_qiskit_backend(circuit: QuantumCircuit, shots: int) -> None:
    provider = BasicProvider()
    backend = provider.get_backend("basic_simulator")
    job = backend.run(circuit, shots=shots)
    job.result().get_counts()


def benchmark_case(
    case: BenchmarkCase,
    shots: int,
    repetitions: int,
    include_cpu: bool,
    include_qiskit: bool,
) -> list[BenchmarkResult]:
    results: list[BenchmarkResult] = []

    if is_cuda_available():
        gpu_timings: list[float] = []
        for _ in range(repetitions):
            gpu_timings.append(time_call(lambda: run_cuda_backend(case.circuit, shots, prefer_gpu=True)))
        results.append(
            BenchmarkResult(
                circuit=case.name,
                backend="ariadne-cuda",
                shots=shots,
                repetitions=repetitions,
                timings=gpu_timings,
            )
        )

    if include_cpu:
        cpu_timings: list[float] = []
        for _ in range(repetitions):
            cpu_timings.append(time_call(lambda: run_cuda_backend(case.circuit, shots, prefer_gpu=False)))
        results.append(
            BenchmarkResult(
                circuit=case.name,
                backend="ariadne-cpu",
                shots=shots,
                repetitions=repetitions,
                timings=cpu_timings,
            )
        )

    if include_qiskit:
        qiskit_timings: list[float] = []
        for _ in range(repetitions):
            qiskit_timings.append(time_call(lambda: run_qiskit_backend(case.circuit, shots)))
        results.append(
            BenchmarkResult(
                circuit=case.name,
                backend="qiskit-basic",
                shots=shots,
                repetitions=repetitions,
                timings=qiskit_timings,
            )
        )

    return results


def format_table(results: Iterable[BenchmarkResult]) -> str:
    headers = ["Circuit", "Backend", "Shots", "Runs", "Mean (s)", "Min (s)", "Max (s)"]
    rows = [headers]
    for result in results:
        rows.append(
            [
                result.circuit,
                result.backend,
                str(result.shots),
                str(result.repetitions),
                f"{result.mean_time:.4f}",
                f"{result.min_time:.4f}",
                f"{result.max_time:.4f}",
            ]
        )

    widths = [max(len(row[i]) for row in rows) for i in range(len(headers))]
    lines = []
    for idx, row in enumerate(rows):
        padded = [cell.ljust(width) for cell, width in zip(row, widths, strict=False)]
        lines.append("  ".join(padded))
        if idx == 0:
            lines.append("  ".join("-" * width for width in widths))
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark Ariadne backends")
    parser.add_argument("--shots", type=int, default=1024, help="Number of shots per run")
    parser.add_argument("--repetitions", type=int, default=3, help="Number of repetitions per case")
    parser.add_argument("--cpu", action="store_true", help="Include Ariadne CPU fallback measurements")
    parser.add_argument(
        "--json",
        type=str,
        default=None,
        help="Optional path to write results as JSON",
    )
    parser.add_argument(
        "--skip-qiskit",
        action="store_true",
        help="Skip Qiskit baseline measurements",
    )

    args = parser.parse_args()

    cases = case_definitions()
    results: list[BenchmarkResult] = []
    for case in cases:
        results.extend(
            benchmark_case(
                case,
                shots=args.shots,
                repetitions=args.repetitions,
                include_cpu=args.cpu,
                include_qiskit=not args.skip_qiskit,
            )
        )

    if not results:
        print("No benchmarks ran (CUDA unavailable and all baselines skipped).")
        return

    print(format_table(results))

    if args.json:
        payload = [result.to_dict() for result in results]
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)

    if is_cuda_available():
        info = get_cuda_info()
        print("\nCUDA info:")
        print(json.dumps(info, indent=2))
    else:
        print("\nCUDA not available on this system.")


if __name__ == "__main__":
    main()
