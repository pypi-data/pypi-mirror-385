#!/usr/bin/env python3
"""Comprehensive benchmark runner for Ariadne backends."""

import argparse
import json
import math
import subprocess
import sys
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class BenchmarkConfig:
    key: str
    script: str
    output_name: str
    json_flag: str
    description: str


@dataclass
class BenchmarkExecution:
    config: BenchmarkConfig
    success: bool
    output_path: Path | None
    stdout: str
    stderr: str


def run_benchmark(config: BenchmarkConfig, results_dir: Path, shots: int) -> BenchmarkExecution:
    """Run a benchmark script and capture its results."""

    script_path = Path(__file__).parent / config.script
    output_path = results_dir / config.output_name
    output_path.unlink(missing_ok=True)

    cmd = [
        sys.executable,
        str(script_path),
        f"--shots={shots}",
        f"{config.json_flag}={output_path}",
    ]

    print(f"🚀 Running {config.script}...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ {config.script} completed successfully")
        if output_path.exists():
            print(f"📊 Results saved to {output_path}")
        else:
            print("⚠️ Benchmark finished but did not produce an output file.")
    else:
        print(f"❌ {config.script} failed:")
        if result.stderr.strip():
            print(result.stderr)

    stored_output = output_path if output_path.exists() else None

    return BenchmarkExecution(
        config=config,
        success=result.returncode == 0,
        output_path=stored_output,
        stdout=result.stdout,
        stderr=result.stderr,
    )


def _group_by_circuit(
    entries: Iterable[dict[str, object]], circuit_key: str = "circuit"
) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for entry in entries:
        circuit_name = str(entry.get(circuit_key, "unknown"))
        grouped.setdefault(circuit_name, []).append(entry)
    return grouped


def _safe_float(value: object) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(result):
        return None
    return result


def _format_seconds(value: object) -> str:
    numeric = _safe_float(value)
    if numeric is None:
        return "—"
    return f"{numeric:.4f}"


def _summarise_metal(path: Path) -> str:
    try:
        entries = json.loads(path.read_text())
    except Exception as exc:  # noqa: BLE001
        return f"Could not parse Metal results: {exc}\n\n"

    if not isinstance(entries, list):
        return "Metal results are not in the expected list format.\n\n"

    grouped = _group_by_circuit(entries)
    lines = ["| Circuit | Shots | CPU (s) | Metal (s) | Speedup |", "|---|---|---|---|---|"]

    for circuit in sorted(grouped):
        backends = {entry.get("backend"): entry for entry in grouped[circuit]}
        cpu_entry = backends.get("qiskit_cpu")
        metal_entry = backends.get("metal")

        if not cpu_entry or not cpu_entry.get("success", True):
            lines.append(f"| {circuit} | — | Benchmark failed | — | — |")
            continue

        shots = cpu_entry.get("shots", "—")
        cpu_time = _safe_float(cpu_entry.get("execution_time"))

        if not metal_entry:
            lines.append(f"| {circuit} | {shots} | {_format_seconds(cpu_time)} | — | Metal backend results missing |")
            continue

        if not metal_entry.get("success", True):
            reason = metal_entry.get("error") or "Benchmark failed"
            lines.append(f"| {circuit} | {shots} | {_format_seconds(cpu_time)} | — | {reason} |")
            continue

        metal_time = _safe_float(metal_entry.get("execution_time"))
        speedup = "—"
        if cpu_time is not None and metal_time not in {None, 0.0}:
            speedup_value = cpu_time / metal_time if metal_time else None
            speedup = f"{speedup_value:.2f}x" if speedup_value else "—"

        lines.append(
            f"| {circuit} | {shots} | {_format_seconds(cpu_time)} | {_format_seconds(metal_time)} | {speedup} |"
        )

    return "\n".join(lines) + "\n\n"


def _summarise_cuda(path: Path, execution: BenchmarkExecution) -> str:
    try:
        entries = json.loads(path.read_text())
    except Exception as exc:  # noqa: BLE001
        return f"Could not parse CUDA results: {exc}\n\n"

    if not isinstance(entries, list):
        return "CUDA results are not in the expected list format.\n\n"

    grouped = _group_by_circuit(entries)
    lines = ["| Circuit | Shots | Qiskit (s) | CUDA (s) | Speedup |", "|---|---|---|---|---|"]

    cuda_available = any(entry.get("backend") == "ariadne-cuda" for entry in entries)
    availability_note = ""
    if not cuda_available:
        lower_stdout = execution.stdout.lower()
        if "cuda not available" in lower_stdout:
            availability_note = "CUDA backend unavailable on this system."
        else:
            availability_note = "No CUDA backend measurements recorded."

    for circuit in sorted(grouped):
        backends = {entry.get("backend"): entry for entry in grouped[circuit]}
        qiskit_entry = backends.get("qiskit-basic")
        cuda_entry = backends.get("ariadne-cuda")

        if not qiskit_entry:
            lines.append(f"| {circuit} | — | Baseline missing | — | — |")
            continue

        shots = qiskit_entry.get("shots", "—")
        qiskit_time = _safe_float(qiskit_entry.get("mean_time"))

        if not cuda_entry:
            lines.append(f"| {circuit} | {shots} | {_format_seconds(qiskit_time)} | — | CUDA data missing |")
            continue

        cuda_time = _safe_float(cuda_entry.get("mean_time"))
        speedup = "—"
        if qiskit_time is not None and cuda_time not in {None, 0.0}:
            speedup_value = qiskit_time / cuda_time if cuda_time else None
            speedup = f"{speedup_value:.2f}x" if speedup_value else "—"

        lines.append(
            f"| {circuit} | {shots} | {_format_seconds(qiskit_time)} | {_format_seconds(cuda_time)} | {speedup} |"
        )

    table = "\n".join(lines) + "\n\n"
    if availability_note:
        table += f"{availability_note}\n\n"
    return table


def _summarise_vs_qiskit(
    path: Path,
    execution: BenchmarkExecution,
    backend_key: str,
    backend_label: str,
) -> str:
    try:
        entries = json.loads(path.read_text())
    except Exception as exc:  # noqa: BLE001
        return f"Could not parse {backend_label} results: {exc}\n\n"

    if not isinstance(entries, list):
        return f"{backend_label} results are not in the expected list format.\n\n"

    grouped = _group_by_circuit(entries)
    lines = [
        f"| Circuit | Shots | Qiskit (s) | {backend_label} (s) | Speedup |",
        "|---|---|---|---|---|",
    ]

    backend_available = False
    backend_errors: list[str] = []

    for circuit in sorted(grouped):
        backends = {entry.get("backend"): entry for entry in grouped[circuit]}
        qiskit_entry = backends.get("qiskit-basic")
        backend_entry = backends.get(backend_key)

        if not qiskit_entry or not qiskit_entry.get("success", True):
            lines.append(f"| {circuit} | — | Baseline failed | — | — |")
            continue

        shots = qiskit_entry.get("shots", "—")
        qiskit_time = _safe_float(qiskit_entry.get("mean_time"))

        if backend_entry is None:
            lines.append(f"| {circuit} | {shots} | {_format_seconds(qiskit_time)} | — | {backend_label} data missing |")
            continue

        if not backend_entry.get("success", True):
            backend_errors.append(str(backend_entry.get("error") or "Benchmark failed"))
            lines.append(
                f"| {circuit} | {shots} | {_format_seconds(qiskit_time)} | — | {backend_entry.get('error') or 'Benchmark failed'} |"
            )
            continue

        backend_available = True
        backend_time = _safe_float(backend_entry.get("mean_time"))
        speedup = "—"
        if qiskit_time is not None and backend_time not in {None, 0.0}:
            speedup_value = qiskit_time / backend_time if backend_time else None
            speedup = f"{speedup_value:.2f}x" if speedup_value else "—"

        lines.append(
            f"| {circuit} | {shots} | {_format_seconds(qiskit_time)} | {_format_seconds(backend_time)} | {speedup} |"
        )

    table = "\n".join(lines) + "\n\n"
    if not backend_available:
        note = backend_errors[0] if backend_errors else "No successful measurements recorded."
        table += f"{backend_label} benchmarks unavailable: {note}\n\n"

    return table


def _summarise_stim(path: Path, execution: BenchmarkExecution) -> str:
    return _summarise_vs_qiskit(path, execution, backend_key="stim", backend_label="Stim")


def _summarise_mps(path: Path, execution: BenchmarkExecution) -> str:
    return _summarise_vs_qiskit(path, execution, backend_key="mps", backend_label="MPS")


SUMMARY_RENDERERS: dict[str, Callable[[Path, BenchmarkExecution], str]] = {
    "metal": lambda path, exec_info: _summarise_metal(path),
    "cuda": _summarise_cuda,
    "stim": _summarise_stim,
    "mps": _summarise_mps,
}


def generate_summary_report(results_dir: Path, executions: list[BenchmarkExecution]) -> None:
    report_path = results_dir / "BENCHMARK_SUMMARY.md"

    lines: list[str] = ["# Ariadne Benchmark Summary", ""]
    lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    for execution in executions:
        config = execution.config
        lines.append(config.description)
        lines.append("")

        if not execution.success:
            failure_message = execution.stderr.strip() or "Benchmark process exited with an error."
            lines.append(f"Benchmark failed: {failure_message}")
            lines.append("")
            continue

        if not execution.output_path:
            lines.append("Benchmark completed but did not produce a results file.")
            lines.append("")
            continue

        renderer = SUMMARY_RENDERERS.get(config.key)
        if not renderer:
            lines.append("No summary renderer is available for these results yet.")
            lines.append("")
            continue

        summary = renderer(execution.output_path, execution)
        lines.append(summary.rstrip())
        lines.append("")

    report_path.write_text("\n".join(lines).strip() + "\n")
    print(f"📋 Summary report generated: {report_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run all Ariadne benchmarks")
    parser.add_argument("--shots", type=int, default=1000, help="Number of shots per circuit")
    parser.add_argument("--output-dir", type=str, default="results", help="Output directory for results")
    parser.add_argument("--skip-metal", action="store_true", help="Skip Metal benchmarks")
    parser.add_argument("--skip-cuda", action="store_true", help="Skip CUDA benchmarks")
    parser.add_argument("--skip-stim", action="store_true", help="Skip Stim benchmarks")
    parser.add_argument("--skip-mps", action="store_true", help="Skip MPS benchmarks")

    args = parser.parse_args()

    results_dir = Path(args.output_dir)
    results_dir.mkdir(exist_ok=True)

    configs: list[BenchmarkConfig] = [
        BenchmarkConfig(
            key="metal",
            script="metal_vs_cpu.py",
            output_name="metal_benchmark_results.json",
            json_flag="--output",
            description="## 🍎 Metal Backend Results (Apple Silicon)",
        ),
        BenchmarkConfig(
            key="cuda",
            script="cuda_vs_cpu.py",
            output_name="cuda_benchmark_results.json",
            json_flag="--json",
            description="## 🚀 CUDA Backend Results (NVIDIA)",
        ),
        BenchmarkConfig(
            key="stim",
            script="stim_vs_cpu.py",
            output_name="stim_benchmark_results.json",
            json_flag="--json",
            description="## ⚡️ Stim Backend Results",
        ),
        BenchmarkConfig(
            key="mps",
            script="mps_vs_cpu.py",
            output_name="mps_benchmark_results.json",
            json_flag="--json",
            description="## 🧵 MPS Backend Results",
        ),
    ]

    print("🚀 Starting Ariadne Benchmark Suite")
    print(f"📁 Results directory: {results_dir}")
    print(f"🎯 Shots per circuit: {args.shots}")
    print("")

    executions: list[BenchmarkExecution] = []

    for config in configs:
        if config.key == "metal" and args.skip_metal:
            continue
        if config.key == "cuda" and args.skip_cuda:
            continue
        if config.key == "stim" and args.skip_stim:
            continue
        if config.key == "mps" and args.skip_mps:
            continue
        executions.append(run_benchmark(config, results_dir, args.shots))
        print("")

    success_count = sum(1 for exec_info in executions if exec_info.success)
    total_benchmarks = len(executions)

    print("📊 Benchmark Summary")
    print("=" * 50)
    print(f"✅ Successful: {success_count}/{total_benchmarks}")
    print(f"❌ Failed: {total_benchmarks - success_count}/{total_benchmarks}")

    if executions:
        generate_summary_report(results_dir, executions)

    if success_count == total_benchmarks:
        print("\n🎉 All benchmarks completed successfully!")
        return 0

    print(f"\n⚠️ {total_benchmarks - success_count} benchmark(s) failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
