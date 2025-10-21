#!/usr/bin/env python3
"""Benchmark Ariadne's router against baseline simulators."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import statistics
import time
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass
from pathlib import Path
from random import Random

from qiskit import QuantumCircuit

from ariadne.backends.tensor_network_backend import TensorNetworkBackend
from ariadne.route.analyze import analyze_circuit
from ariadne.route.enhanced_router import EnhancedQuantumRouter


@dataclass
class BenchmarkCase:
    name: str
    description: str
    builder: Callable[[], QuantumCircuit]
    category: str


@dataclass
class TimingResult:
    backend: str
    mean_time: float
    stdev: float
    repetitions: int
    succeeded: bool
    error: str | None


@dataclass
class CaseResult:
    name: str
    description: str
    category: str
    num_qubits: int
    num_gates: int
    analysis: dict[str, float | int | bool]
    timings: list[TimingResult]
    router_backend: str | None

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["timings"] = [asdict(timing) for timing in self.timings]
        return payload


Shots = int
Repetitions = int


def build_ghz_chain(num_qubits: int) -> QuantumCircuit:
    qc = QuantumCircuit(num_qubits, num_qubits)
    qc.h(0)
    for idx in range(num_qubits - 1):
        qc.cx(idx, idx + 1)
    qc.measure_all()
    return qc


def build_random_clifford(num_qubits: int, depth: int, seed: int) -> QuantumCircuit:
    rng = Random(seed)
    qc = QuantumCircuit(num_qubits, num_qubits)
    one_qubit_clifford = ["h", "s", "sdg", "x", "y", "z", "sx", "sxdg"]
    for _ in range(depth):
        for qubit in range(num_qubits):
            gate = rng.choice(one_qubit_clifford)
            getattr(qc, gate)(qubit)
        for ctrl in range(num_qubits - 1):
            qc.cx(ctrl, ctrl + 1)
    qc.measure_all()
    return qc


def build_random_nonclifford(num_qubits: int, depth: int, seed: int) -> QuantumCircuit:
    rng = Random(seed)
    qc = QuantumCircuit(num_qubits, num_qubits)
    for _ in range(depth):
        for qubit in range(num_qubits):
            theta = rng.random() * math.pi
            phi = rng.random() * math.pi
            qc.ry(theta, qubit)
            qc.rz(phi, qubit)
        for ctrl in range(num_qubits - 1):
            qc.cx(ctrl, ctrl + 1)
        for qubit in range(num_qubits):
            qc.t(qubit)
    qc.measure_all()
    return qc


def build_qaoa_maxcut(num_qubits: int, p_layers: int) -> QuantumCircuit:
    qc = QuantumCircuit(num_qubits, num_qubits)
    for qubit in range(num_qubits):
        qc.h(qubit)
    beta = math.pi / 8
    gamma = math.pi / 4
    for _ in range(p_layers):
        for idx in range(num_qubits - 1):
            qc.cx(idx, idx + 1)
            qc.rz(2 * gamma, idx + 1)
            qc.cx(idx, idx + 1)
        for qubit in range(num_qubits):
            qc.rx(2 * beta, qubit)
    qc.measure_all()
    return qc


def build_vqe_ansatz(num_qubits: int, layers: int) -> QuantumCircuit:
    qc = QuantumCircuit(num_qubits, num_qubits)
    theta = math.pi / 5
    for layer in range(layers):
        for qubit in range(num_qubits):
            qc.rx(theta * (layer + 1), qubit)
            qc.rz(theta / 2, qubit)
        for idx in range(0, num_qubits - 1, 2):
            qc.cx(idx, idx + 1)
        for idx in range(1, num_qubits - 1, 2):
            qc.cx(idx, idx + 1)
    qc.measure_all()
    return qc


def build_benchmark_cases() -> list[BenchmarkCase]:
    def ghz_10() -> QuantumCircuit:
        return build_ghz_chain(10)

    def clifford_med() -> QuantumCircuit:
        return build_random_clifford(num_qubits=12, depth=5, seed=42)

    def nonclifford_med() -> QuantumCircuit:
        return build_random_nonclifford(num_qubits=8, depth=4, seed=99)

    def qaoa8() -> QuantumCircuit:
        return build_qaoa_maxcut(num_qubits=8, p_layers=3)

    def vqe12() -> QuantumCircuit:
        return build_vqe_ansatz(num_qubits=12, layers=3)

    return [
        BenchmarkCase(
            name="ghz_chain_10",
            description="Clifford GHZ ladder (H + CX)",
            builder=ghz_10,
            category="clifford",
        ),
        BenchmarkCase(
            name="random_clifford_12",
            description="Random layered Clifford circuit",
            builder=clifford_med,
            category="clifford",
        ),
        BenchmarkCase(
            name="random_nonclifford_8",
            description="Random non-Clifford rotations + entanglement",
            builder=nonclifford_med,
            category="non_clifford",
        ),
        BenchmarkCase(
            name="qaoa_maxcut_8_p3",
            description="QAOA MaxCut with p=3 layers",
            builder=qaoa8,
            category="algorithmic",
        ),
        BenchmarkCase(
            name="vqe_ansatz_12",
            description="Hardware-efficient variational ansatz",
            builder=vqe12,
            category="algorithmic",
        ),
    ]


def time_function(fn: Callable[[], object], repetitions: int) -> tuple[list[float], bool, str | None]:
    timings: list[float] = []
    for _ in range(repetitions):
        start = time.perf_counter()
        try:
            fn()
        except Exception as exc:  # noqa: BLE001 - deliberate benchmark capture
            return timings, False, str(exc)
        timings.append(time.perf_counter() - start)
    return timings, True, None


def benchmark_case(
    case: BenchmarkCase,
    shots: Shots,
    repetitions: Repetitions,
    enable_tensor_network: bool,
) -> CaseResult:
    circuit = case.builder()
    analysis = analyze_circuit(circuit)
    num_qubits = circuit.num_qubits
    num_gates = len([item for item in circuit.data if item[0].name not in {"measure", "barrier", "delay"}])

    timings: list[TimingResult] = []
    router_backend: str | None = None

    try:
        router = EnhancedQuantumRouter()

        def router_run() -> None:
            nonlocal router_backend
            result = router.simulate(circuit, shots=shots)
            router_backend = result.backend_used.value

        router_timings, router_success, router_error = time_function(router_run, repetitions)
    except Exception as e:
        router_timings = []
        router_success = False
        router_error = f"Failed to initialize EnhancedQuantumRouter: {str(e)}"
    timings.append(
        TimingResult(
            backend="ariadne_router",
            mean_time=statistics.mean(router_timings) if router_timings else float("inf"),
            stdev=statistics.pstdev(router_timings) if len(router_timings) > 1 else 0.0,
            repetitions=len(router_timings),
            succeeded=router_success,
            error=router_error,
        )
    )

    from qiskit.providers.basic_provider import BasicProvider

    provider = BasicProvider()
    qiskit_backend = provider.get_backend("basic_simulator")

    def qiskit_run() -> None:
        job = qiskit_backend.run(circuit, shots=shots)
        job.result().get_counts()

    qiskit_timings, qiskit_success, qiskit_error = time_function(qiskit_run, repetitions)
    timings.append(
        TimingResult(
            backend="qiskit_basic",
            mean_time=statistics.mean(qiskit_timings) if qiskit_timings else float("inf"),
            stdev=statistics.pstdev(qiskit_timings) if len(qiskit_timings) > 1 else 0.0,
            repetitions=len(qiskit_timings),
            succeeded=qiskit_success,
            error=qiskit_error,
        )
    )

    if case.category == "clifford":
        if importlib.util.find_spec("stim") is None:
            timings.append(
                TimingResult(
                    backend="stim",
                    mean_time=float("inf"),
                    stdev=0.0,
                    repetitions=0,
                    succeeded=False,
                    error="Stim backend not available",
                )
            )
        else:
            stim_router = EnhancedQuantumRouter()

            def stim_run() -> None:
                stim_router._simulate_stim(circuit, shots)

            try:
                stim_timings, stim_success, stim_error = time_function(stim_run, repetitions)
                timings.append(
                    TimingResult(
                        backend="stim",
                        mean_time=statistics.mean(stim_timings) if stim_timings else float("inf"),
                        stdev=statistics.pstdev(stim_timings) if len(stim_timings) > 1 else 0.0,
                        repetitions=len(stim_timings),
                        succeeded=stim_success,
                        error=stim_error,
                    )
                )
            except Exception as exc:  # pragma: no cover - other errors
                timings.append(
                    TimingResult(
                        backend="stim",
                        mean_time=float("inf"),
                        stdev=0.0,
                        repetitions=0,
                        succeeded=False,
                        error=f"Stim backend error: {str(exc)}",
                    )
                )

    if enable_tensor_network and num_qubits <= 14:
        try:
            tn_backend = TensorNetworkBackend()

            def tensor_run() -> None:
                tn_backend.simulate(circuit, shots)

            tensor_timings, tensor_success, tensor_error = time_function(tensor_run, repetitions)
            timings.append(
                TimingResult(
                    backend="tensor_network",
                    mean_time=statistics.mean(tensor_timings) if tensor_timings else float("inf"),
                    stdev=statistics.pstdev(tensor_timings) if len(tensor_timings) > 1 else 0.0,
                    repetitions=len(tensor_timings),
                    succeeded=tensor_success,
                    error=tensor_error,
                )
            )
        except Exception as exc:
            timings.append(
                TimingResult(
                    backend="tensor_network",
                    mean_time=float("inf"),
                    stdev=0.0,
                    repetitions=0,
                    succeeded=False,
                    error=f"Tensor network backend error: {str(exc)}",
                )
            )

    return CaseResult(
        name=case.name,
        description=case.description,
        category=case.category,
        num_qubits=num_qubits,
        num_gates=num_gates,
        analysis=analysis,
        timings=timings,
        router_backend=router_backend,
    )


def generate_table(results: Iterable[CaseResult]) -> str:
    lines: list[str] = []
    header = (
        "Case",
        "Category",
        "Qubits",
        "Router Backend",
        "Backend",
        "Mean (ms)",
        "Stddev",
        "Reps",
        "Status",
    )
    lines.append("\t".join(header))
    for case in results:
        for timing in case.timings:
            mean_ms = timing.mean_time * 1e3 if math.isfinite(timing.mean_time) else float("inf")
            std_ms = timing.stdev * 1e3 if math.isfinite(timing.stdev) else float("inf")
            status = "OK" if timing.succeeded else f"FAIL ({timing.error})"
            lines.append(
                "\t".join(
                    [
                        case.name,
                        case.category,
                        str(case.num_qubits),
                        case.router_backend or "?",
                        timing.backend,
                        f"{mean_ms:.3f}" if math.isfinite(mean_ms) else "inf",
                        f"{std_ms:.3f}" if math.isfinite(std_ms) else "inf",
                        str(timing.repetitions),
                        status,
                    ]
                )
            )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark Ariadne router vs baselines")
    parser.add_argument("--shots", type=int, default=512, help="Number of measurement shots")
    parser.add_argument("--repetitions", type=int, default=3, help="Timing repetitions per backend")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/router_benchmark_results.json"),
        help="Path to write JSON results",
    )
    parser.add_argument("--no-tensor-network", action="store_true", help="Disable direct tensor network baseline")
    args = parser.parse_args()

    cases = build_benchmark_cases()
    results: list[CaseResult] = []
    for case in cases:
        print(f"Benchmarking {case.name} ({case.description})...")
        result = benchmark_case(
            case,
            shots=args.shots,
            repetitions=args.repetitions,
            enable_tensor_network=not args.no_tensor_network,
        )
        results.append(result)

    print("\nBenchmark results (mean timings in ms):")
    print(generate_table(results))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump([result.to_dict() for result in results], handle, indent=2)
    print(f"\nSaved detailed results to {args.output}")


if __name__ == "__main__":
    main()
