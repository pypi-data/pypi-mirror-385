"""
Ariadne Benchmarking Utilities

This module provides utilities for generating citable, reproducible
benchmark reports across quantum simulators and algorithms.
"""

import platform
import sys
import time
from datetime import datetime
from typing import Any

from qiskit import QuantumCircuit

from . import simulate
from .algorithms import AlgorithmParameters, get_algorithm


def export_benchmark_report(
    algorithms: list[str], backends: list[str], shots: int = 1000, fmt: str = "json"
) -> dict[str, Any]:
    """
    Return dict ready for JSON/CSV/Latex; keys: date, algorithms, hardware, results.

    Args:
        algorithms: List of algorithm names to test (e.g., ['bell', 'qaoa', 'vqe'])
        backends: List of backend names to test (e.g., ['auto', 'stim', 'qiskit'])
        shots: Number of measurement shots per simulation
        fmt: Output format ('json', 'csv', 'latex')

    Returns:
        Dictionary containing benchmark report ready for export
    """
    if fmt not in ["json", "csv", "latex"]:
        raise ValueError(f"Format '{fmt}' not supported. Use 'json', 'csv', or 'latex'.")

    # Create benchmark circuits
    circuits = _create_benchmark_circuits()

    # Initialize report structure
    report = {
        "date": datetime.now().isoformat(),
        "algorithms": algorithms,
        "hardware": {
            "platform": platform.platform(),
            "python_version": sys.version,
        },
        "results": {},
    }

    # Run benchmarks for each algorithm
    for alg_name in algorithms:
        if alg_name not in circuits:
            print(f"Warning: Unknown algorithm '{alg_name}', skipping...")
            continue

        circuit = circuits[alg_name]
        report["results"][alg_name] = {  # type: ignore[index]
            "circuit_info": {
                "qubits": circuit.num_qubits,
                "depth": circuit.depth(),
                "gate_counts": dict(circuit.count_ops()),
            },
            "backends": {},
        }

        # Test each backend
        for backend in backends:
            try:
                start_time = time.perf_counter()
                result = simulate(circuit, shots=shots, backend=backend)
                end_time = time.perf_counter()

                backend_result = {
                    "success": True,
                    "execution_time": end_time - start_time,
                    "backend_used": result.backend_used.value,
                    "shots": shots,
                    "counts": dict(result.counts),
                    "unique_outcomes": len(result.counts),
                    "throughput": shots / (end_time - start_time) if (end_time - start_time) > 0 else 0,
                }

            except Exception as e:
                backend_result = {"success": False, "error": str(e), "backend_requested": backend, "shots": shots}

            report["results"][alg_name]["backends"][backend] = backend_result  # type: ignore[index]

    # Format output based on requested format
    if fmt == "json":
        return report
    elif fmt == "csv":
        return _format_as_csv(report)
    elif fmt == "latex":
        return _format_as_latex(report)

    return report


def _create_benchmark_circuits() -> dict[str, QuantumCircuit]:
    """Create standard benchmark circuits for testing using the unified algorithm module."""

    circuits = {}

    # Define algorithm configurations
    algorithm_configs = {
        "bell": {"n_qubits": 2},
        "ghz": {"n_qubits": 4},
        "qaoa": {"n_qubits": 6, "custom_params": {"layers": 2}},
        "vqe": {"n_qubits": 5, "custom_params": {"depth": 2}},
        "stabilizer": {"n_qubits": 8},
        "qft": {"n_qubits": 4},
        "grover": {"n_qubits": 4, "custom_params": {"marked_state": "1111"}},
        "qpe": {"n_qubits": 4},
        "steane": {"n_qubits": 7},
        "qsvm": {"n_qubits": 4, "custom_params": {"use_feature_map": True}},
        "deutsch_jozsa": {"n_qubits": 3, "custom_params": {"function_type": "balanced"}},
        "bernstein_vazirani": {"n_qubits": 4, "custom_params": {"hidden_string": "1011"}},
    }

    # Create circuits using the unified algorithm module
    for alg_name, config in algorithm_configs.items():
        try:
            algorithm_class = get_algorithm(alg_name)
            params = AlgorithmParameters(**config)  # type: ignore[arg-type]
            algorithm = algorithm_class(params)
            circuits[alg_name] = algorithm.create_circuit()
        except Exception as e:
            print(f"Warning: Failed to create circuit for {alg_name}: {e}")
            # Fallback to original implementation for basic algorithms
            if alg_name == "bell":
                bell = QuantumCircuit(2, 2)
                bell.h(0)
                bell.cx(0, 1)
                bell.measure_all()
                circuits["bell"] = bell
            elif alg_name == "ghz":
                ghz = QuantumCircuit(4, 4)
                ghz.h(0)
                for i in range(1, 4):
                    ghz.cx(0, i)
                ghz.measure_all()
                circuits["ghz"] = ghz
            elif alg_name == "stabilizer":
                stabilizer = QuantumCircuit(8, 8)
                for i in range(8):
                    stabilizer.h(i)
                for i in range(7):
                    stabilizer.cx(i, i + 1)
                stabilizer.s(0)
                stabilizer.h(1)
                stabilizer.measure_all()
                circuits["stabilizer"] = stabilizer

    return circuits


def _format_as_csv(report: dict[str, Any]) -> dict[str, Any]:
    """Convert report to CSV-friendly format."""
    csv_data = []

    for alg_name, alg_data in report["results"].items():
        circuit_info = alg_data["circuit_info"]

        for backend_name, backend_data in alg_data["backends"].items():
            row = {
                "algorithm": alg_name,
                "backend": backend_name,
                "qubits": circuit_info["qubits"],
                "depth": circuit_info["depth"],
                "success": backend_data["success"],
                "execution_time": backend_data.get("execution_time", 0),
                "throughput": backend_data.get("throughput", 0),
                "unique_outcomes": backend_data.get("unique_outcomes", 0),
            }

            if not backend_data["success"]:
                row["error"] = backend_data.get("error", "Unknown error")

            csv_data.append(row)

    return {"date": report["date"], "format": "csv", "data": csv_data}


def _format_as_latex(report: dict[str, Any]) -> dict[str, Any]:
    """Convert report to LaTeX-friendly format."""
    latex_sections = []

    # Header
    latex_sections.append("\\section*{Quantum Simulator Benchmark Report}")
    latex_sections.append(f"\\textbf{{Date:}} {report['date']}")
    latex_sections.append(f"\\textbf{{Platform:}} {report['hardware']['platform']}")
    latex_sections.append("")

    # Results table
    latex_sections.append("\\begin{table}[h]")
    latex_sections.append("\\centering")
    latex_sections.append("\\begin{tabular}{|l|l|c|c|c|c|}")
    latex_sections.append("\\hline")
    latex_sections.append("Algorithm & Backend & Qubits & Success & Time (s) & Throughput \\\\")
    latex_sections.append("\\hline")

    for alg_name, alg_data in report["results"].items():
        circuit_info = alg_data["circuit_info"]

        for backend_name, backend_data in alg_data["backends"].items():
            success_str = "✓" if backend_data["success"] else "✗"
            time_str = f"{backend_data.get('execution_time', 0):.3f}" if backend_data["success"] else "N/A"
            throughput_str = f"{backend_data.get('throughput', 0):.0f}" if backend_data["success"] else "N/A"

            latex_sections.append(
                f"{alg_name} & {backend_name} & {circuit_info['qubits']} & {success_str} & {time_str} & {throughput_str} \\\\"
            )
            latex_sections.append("\\hline")

    latex_sections.append("\\end{tabular}")
    latex_sections.append("\\caption{Benchmark results across quantum simulators}")
    latex_sections.append("\\end{table}")

    return {"date": report["date"], "format": "latex", "content": "\n".join(latex_sections)}
