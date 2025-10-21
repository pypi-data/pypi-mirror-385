from __future__ import annotations

import argparse
import json
import time
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass

from qiskit import QuantumCircuit
from qiskit.providers.basic_provider import BasicProvider

from ariadne.converters import convert_qiskit_to_stim, simulate_stim_circuit


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
    success: bool
    error: str | None = None

    @property
    def mean_time(self) -> float | None:
        return sum(self.timings) / len(self.timings) if self.timings else None

    @property
    def min_time(self) -> float | None:
        return min(self.timings) if self.timings else None

    @property
    def max_time(self) -> float | None:
        return max(self.timings) if self.timings else None

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload.update(
            mean_time=self.mean_time,
            min_time=self.min_time,
            max_time=self.max_time,
        )
        return payload


def build_clifford_ladder(qubits: int, depth: int) -> QuantumCircuit:
    circuit = QuantumCircuit(qubits, qubits)
    for _ in range(depth):
        for idx in range(qubits):
            circuit.h(idx)
            circuit.s(idx)
        for idx in range(qubits - 1):
            circuit.cx(idx, idx + 1)
    circuit.measure_all()
    return circuit


def build_measuring_chain(qubits: int) -> QuantumCircuit:
    circuit = QuantumCircuit(qubits, qubits)
    for idx in range(qubits):
        circuit.h(idx)
    for idx in range(qubits - 1):
        circuit.cx(idx, idx + 1)
    circuit.measure_all()
    return circuit


def case_definitions() -> list[BenchmarkCase]:
    return [
        BenchmarkCase("clifford_chain_10", build_clifford_ladder(10, depth=6)),
        BenchmarkCase("clifford_chain_16", build_clifford_ladder(16, depth=4)),
        BenchmarkCase("bell_measurement_12", build_measuring_chain(12)),
    ]


def time_call(fn: Callable[[], object]) -> float:
    start = time.perf_counter()
    fn()
    return time.perf_counter() - start


def run_qiskit_backend(circuit: QuantumCircuit, shots: int) -> None:
    provider = BasicProvider()
    backend = provider.get_backend("basic_simulator")
    job = backend.run(circuit, shots=shots)
    job.result().get_counts()


def run_stim_backend(circuit: QuantumCircuit, shots: int) -> None:
    stim_circuit, measurement_map = convert_qiskit_to_stim(circuit)
    num_clbits = circuit.num_clbits or circuit.num_qubits
    simulate_stim_circuit(stim_circuit, measurement_map, shots, num_clbits)


def benchmark_case(
    case: BenchmarkCase,
    shots: int,
    repetitions: int,
    include_qiskit: bool,
) -> list[BenchmarkResult]:
    results: list[BenchmarkResult] = []

    if include_qiskit:
        timings: list[float] = []
        success = True
        error: str | None = None
        for _ in range(repetitions):
            try:
                timings.append(time_call(lambda: run_qiskit_backend(case.circuit, shots)))
            except Exception as exc:  # noqa: BLE001
                success = False
                error = str(exc)
                break
        results.append(
            BenchmarkResult(
                circuit=case.name,
                backend="qiskit-basic",
                shots=shots,
                repetitions=len(timings),
                timings=timings,
                success=success,
                error=error,
            )
        )

    stim_timings: list[float] = []
    stim_success = True
    stim_error: str | None = None
    for _ in range(repetitions):
        try:
            stim_timings.append(time_call(lambda: run_stim_backend(case.circuit, shots)))
        except Exception as exc:  # noqa: BLE001
            stim_success = False
            stim_error = str(exc)
            break

    results.append(
        BenchmarkResult(
            circuit=case.name,
            backend="stim",
            shots=shots,
            repetitions=len(stim_timings),
            timings=stim_timings,
            success=stim_success,
            error=stim_error,
        )
    )

    return results


def format_table(results: Iterable[BenchmarkResult]) -> str:
    headers = ["Circuit", "Backend", "Shots", "Runs", "Mean (s)", "Status"]
    rows = [headers]

    for result in results:
        status = "ok" if result.success else (result.error or "failed")
        rows.append(
            [
                result.circuit,
                result.backend,
                str(result.shots),
                str(result.repetitions),
                f"{result.mean_time:.5f}" if result.mean_time is not None else "—",
                status,
            ]
        )

    widths = [max(len(row[idx]) for row in rows) for idx in range(len(headers))]
    lines: list[str] = []
    for idx, row in enumerate(rows):
        padded = [cell.ljust(width) for cell, width in zip(row, widths, strict=False)]
        lines.append("  ".join(padded))
        if idx == 0:
            lines.append("  ".join("-" * width for width in widths))

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark Stim vs Qiskit CPU backends")
    parser.add_argument("--shots", type=int, default=1024, help="Number of shots per run")
    parser.add_argument("--repetitions", type=int, default=5, help="Number of repetitions per case")
    parser.add_argument(
        "--json",
        type=str,
        default=None,
        help="Optional path to write results as JSON",
    )
    parser.add_argument("--skip-qiskit", action="store_true", help="Skip Qiskit baseline measurements")

    args = parser.parse_args()

    cases = case_definitions()
    results: list[BenchmarkResult] = []
    for case in cases:
        results.extend(
            benchmark_case(
                case,
                shots=args.shots,
                repetitions=args.repetitions,
                include_qiskit=not args.skip_qiskit,
            )
        )

    if not results:
        print("No benchmarks were executed.")
        return

    print(format_table(results))

    if args.json:
        payload = [result.to_dict() for result in results]
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)


if __name__ == "__main__":
    main()
