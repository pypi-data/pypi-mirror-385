"""
Comprehensive Quantum Algorithm Benchmark Suite for Ariadne

This module provides standardized benchmarks for quantum circuit simulation,
enabling performance comparison across different backends and optimization
strategies. The benchmark suite covers major quantum algorithm families.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT, QuantumVolume
from qiskit.circuit.random import random_circuit


@dataclass
class BenchmarkResult:
    """Results from a single benchmark execution."""

    benchmark_name: str
    backend_name: str
    circuit_params: dict[str, Any]
    execution_time: float
    memory_used_mb: float
    success: bool
    error_message: str | None = None
    counts_entropy: float = 0.0
    optimization_applied: bool = False
    shots: int = 1000
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class BenchmarkSuite:
    """Configuration for a benchmark suite."""

    name: str
    description: str
    benchmarks: list[str]
    qubit_ranges: list[int]
    shot_counts: list[int]
    repetitions: int = 3


@dataclass
class BackendPerformanceStats:
    """Aggregate statistics for backend executions."""

    times: list[float] = field(default_factory=list)
    success_count: int = 0
    total_count: int = 0


@dataclass
class AlgorithmPerformanceStats:
    """Aggregate statistics for algorithm benchmarks."""

    success: int = 0
    total: int = 0
    times: list[float] = field(default_factory=list)


class QuantumAlgorithmBenchmarks:
    """Comprehensive quantum algorithm benchmark suite."""

    def __init__(self, output_dir: str | None = None) -> None:
        """Initialize benchmark suite."""
        self.output_dir = Path(output_dir) if output_dir else Path("benchmark_results")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Standard benchmark configurations
        self.benchmark_suites: dict[str, BenchmarkSuite] = {
            "quick": BenchmarkSuite(
                name="Quick Validation",
                description="Fast benchmarks for basic validation",
                benchmarks=["clifford", "random", "qft"],
                qubit_ranges=[4, 8, 12],
                shot_counts=[100, 1000],
                repetitions=2,
            ),
            "standard": BenchmarkSuite(
                name="Standard Performance",
                description="Comprehensive performance benchmarks",
                benchmarks=["clifford", "random", "qft", "quantum_volume", "grover", "qaoa"],
                qubit_ranges=[4, 8, 12, 16, 20],
                shot_counts=[100, 1000, 10000],
                repetitions=3,
            ),
            "comprehensive": BenchmarkSuite(
                name="Comprehensive Analysis",
                description="Full algorithm family coverage",
                benchmarks=[
                    "clifford",
                    "random",
                    "qft",
                    "quantum_volume",
                    "grover",
                    "qaoa",
                    "variational",
                    "error_correction",
                    "chemistry",
                    "optimization",
                ],
                qubit_ranges=[4, 8, 12, 16, 20, 24],
                shot_counts=[100, 1000, 10000],
                repetitions=5,
            ),
        }

    def create_clifford_circuit(self, num_qubits: int, depth: int | None = None) -> QuantumCircuit:
        """Create Clifford circuit for stabilizer simulation benchmarks."""
        if depth is None:
            depth = num_qubits * 2

        circuit = QuantumCircuit(num_qubits)

        # Random Clifford gates
        clifford_gates = ["h", "x", "y", "z", "s", "sdg"]
        two_qubit_gates = ["cx", "cz"]

        np.random.seed(42)  # Reproducible benchmarks

        for _ in range(depth):
            if np.random.random() < 0.3 and num_qubits > 1:
                # Two-qubit gate
                gate = np.random.choice(two_qubit_gates)
                qubits = np.random.choice(num_qubits, 2, replace=False)
                if gate == "cx":
                    circuit.cx(qubits[0], qubits[1])
                elif gate == "cz":
                    circuit.cz(qubits[0], qubits[1])
            else:
                # Single-qubit gate
                gate = np.random.choice(clifford_gates)
                qubit = np.random.randint(num_qubits)
                getattr(circuit, gate)(qubit)

        circuit.measure_all()
        return circuit

    def create_random_circuit(self, num_qubits: int, depth: int | None = None) -> QuantumCircuit:
        """Create random quantum circuit."""
        if depth is None:
            depth = num_qubits * 3

        circuit = random_circuit(num_qubits, depth, seed=42, measure=True)
        return circuit

    def create_qft_circuit(self, num_qubits: int) -> QuantumCircuit:
        """Create Quantum Fourier Transform circuit."""
        qft = QFT(num_qubits)
        circuit = QuantumCircuit(num_qubits)
        circuit.compose(qft, inplace=True)
        circuit.measure_all()
        return circuit

    def create_quantum_volume_circuit(self, num_qubits: int, depth: int | None = None) -> QuantumCircuit:
        """Create Quantum Volume circuit."""
        if depth is None:
            depth = num_qubits

        qv = QuantumVolume(num_qubits, depth, seed=42)
        circuit = QuantumCircuit(num_qubits)
        circuit.compose(qv, inplace=True)
        circuit.measure_all()
        return circuit

    def create_grover_circuit(self, num_qubits: int) -> QuantumCircuit:
        """Create simplified Grover's algorithm circuit."""
        if num_qubits < 2:
            num_qubits = 2

        circuit = QuantumCircuit(num_qubits)

        # Initialize superposition
        for i in range(num_qubits):
            circuit.h(i)

        # Grover iterations (simplified)
        iterations = int(np.pi * np.sqrt(2 ** (num_qubits - 1)) / 4)
        iterations = min(iterations, 3)  # Limit for benchmark

        for _ in range(iterations):
            # Oracle (mark last state)
            circuit.x(num_qubits - 1)
            circuit.h(num_qubits - 1)
            circuit.mcx(list(range(num_qubits - 1)), num_qubits - 1)
            circuit.h(num_qubits - 1)
            circuit.x(num_qubits - 1)

            # Diffusion operator
            for i in range(num_qubits):
                circuit.h(i)
                circuit.x(i)

            circuit.h(num_qubits - 1)
            circuit.mcx(list(range(num_qubits - 1)), num_qubits - 1)
            circuit.h(num_qubits - 1)

            for i in range(num_qubits):
                circuit.x(i)
                circuit.h(i)

        circuit.measure_all()
        return circuit

    def create_qaoa_circuit(self, num_qubits: int, layers: int = 2) -> QuantumCircuit:
        """Create QAOA (Quantum Approximate Optimization Algorithm) circuit."""
        circuit = QuantumCircuit(num_qubits)

        # Initialize superposition
        for i in range(num_qubits):
            circuit.h(i)

        # QAOA layers
        for _layer in range(layers):
            # Problem Hamiltonian (ZZ interactions)
            for i in range(num_qubits - 1):
                circuit.cx(i, i + 1)
                circuit.rz(0.5, i + 1)  # Simplified parameter
                circuit.cx(i, i + 1)

            # Mixer Hamiltonian (X rotations)
            for i in range(num_qubits):
                circuit.rx(0.3, i)  # Simplified parameter

        circuit.measure_all()
        return circuit

    def create_variational_circuit(self, num_qubits: int, layers: int = 2) -> QuantumCircuit:
        """Create variational quantum circuit for VQE-style algorithms."""
        circuit = QuantumCircuit(num_qubits)

        # Variational ansatz
        for _layer in range(layers):
            # Single-qubit rotations
            for i in range(num_qubits):
                circuit.ry(np.pi / 4, i)  # Fixed parameter for benchmark
                circuit.rz(np.pi / 6, i)

            # Entangling gates
            for i in range(num_qubits - 1):
                circuit.cx(i, i + 1)

        circuit.measure_all()
        return circuit

    def create_error_correction_circuit(self, num_qubits: int) -> QuantumCircuit:
        """Create simple quantum error correction circuit (bit flip code)."""
        if num_qubits < 3:
            num_qubits = 3

        # Use only first 3 qubits for 3-qubit bit flip code
        circuit = QuantumCircuit(num_qubits)

        # Encode logical |0⟩
        circuit.cx(0, 1)
        circuit.cx(0, 2)

        # Add some operations
        circuit.h(0)
        circuit.cx(0, 1)

        # Error syndrome measurement (simplified)
        if num_qubits >= 5:
            circuit.cx(0, 3)
            circuit.cx(1, 3)
            circuit.cx(1, 4)
            circuit.cx(2, 4)

        circuit.measure_all()
        return circuit

    def create_chemistry_circuit(self, num_qubits: int) -> QuantumCircuit:
        """Create quantum chemistry simulation circuit (simplified UCC ansatz)."""
        circuit = QuantumCircuit(num_qubits)

        # Hartree-Fock state preparation (simplified)
        for i in range(0, min(num_qubits // 2, 4), 2):
            circuit.x(i)

        # UCC singles and doubles (simplified)
        for i in range(0, num_qubits - 1, 2):
            circuit.ry(0.1, i)
            circuit.ry(0.1, i + 1)
            circuit.cx(i, i + 1)
            circuit.rz(0.2, i + 1)
            circuit.cx(i, i + 1)

        circuit.measure_all()
        return circuit

    def create_optimization_circuit(self, num_qubits: int) -> QuantumCircuit:
        """Create combinatorial optimization circuit (MaxCut-style)."""
        circuit = QuantumCircuit(num_qubits)

        # Initialize superposition
        for i in range(num_qubits):
            circuit.h(i)

        # Cost function (simplified MaxCut)
        for i in range(num_qubits):
            for j in range(i + 1, min(i + 3, num_qubits)):  # Local connectivity
                circuit.cx(i, j)
                circuit.rz(0.3, j)
                circuit.cx(i, j)

        # Mixer
        for i in range(num_qubits):
            circuit.rx(0.4, i)

        circuit.measure_all()
        return circuit

    def benchmark_circuit(
        self, circuit_name: str, num_qubits: int, backend_name: str, shots: int = 1000
    ) -> BenchmarkResult:
        """Benchmark a single circuit on a specific backend."""

        # Create circuit
        circuit_creators: dict[str, Callable[[int], QuantumCircuit]] = {
            "clifford": self.create_clifford_circuit,
            "random": self.create_random_circuit,
            "qft": self.create_qft_circuit,
            "quantum_volume": self.create_quantum_volume_circuit,
            "grover": self.create_grover_circuit,
            "qaoa": self.create_qaoa_circuit,
            "variational": self.create_variational_circuit,
            "error_correction": self.create_error_correction_circuit,
            "chemistry": self.create_chemistry_circuit,
            "optimization": self.create_optimization_circuit,
        }

        if circuit_name not in circuit_creators:
            raise ValueError(f"Unknown circuit type: {circuit_name}")

        circuit = circuit_creators[circuit_name](num_qubits)

        # Get backend
        try:
            from .universal_interface import get_backend

            backend = get_backend(backend_name)
            if not backend:
                return BenchmarkResult(
                    benchmark_name=circuit_name,
                    backend_name=backend_name,
                    circuit_params={"num_qubits": num_qubits},
                    execution_time=0.0,
                    memory_used_mb=0.0,
                    success=False,
                    error_message=f"Backend {backend_name} not available",
                    shots=shots,
                )
        except Exception as e:
            return BenchmarkResult(
                benchmark_name=circuit_name,
                backend_name=backend_name,
                circuit_params={"num_qubits": num_qubits},
                execution_time=0.0,
                memory_used_mb=0.0,
                success=False,
                error_message=f"Failed to load backend: {e}",
                shots=shots,
            )

        # Check if backend can simulate
        can_sim, reason = backend.can_simulate(circuit)
        if not can_sim:
            return BenchmarkResult(
                benchmark_name=circuit_name,
                backend_name=backend_name,
                circuit_params={"num_qubits": num_qubits, "depth": circuit.depth()},
                execution_time=0.0,
                memory_used_mb=0.0,
                success=False,
                error_message=reason,
                shots=shots,
            )

        # Estimate memory before execution
        estimated_memory = backend.estimate_resources(circuit).get("memory_mb", 0.0)

        # Execute benchmark
        try:
            start_time = time.time()
            counts = backend.simulate(circuit, shots)
            execution_time = time.time() - start_time

            # Calculate measurement entropy
            total_shots = sum(counts.values())
            entropy = 0.0
            if total_shots > 0:
                for count in counts.values():
                    if count > 0:
                        p = count / total_shots
                        entropy -= p * np.log2(p)

            return BenchmarkResult(
                benchmark_name=circuit_name,
                backend_name=backend_name,
                circuit_params={
                    "num_qubits": num_qubits,
                    "depth": circuit.depth(),
                    "gate_count": len(circuit.data),
                },
                execution_time=execution_time,
                memory_used_mb=estimated_memory,
                success=True,
                counts_entropy=entropy,
                shots=shots,
            )

        except Exception as e:
            return BenchmarkResult(
                benchmark_name=circuit_name,
                backend_name=backend_name,
                circuit_params={"num_qubits": num_qubits, "depth": circuit.depth()},
                execution_time=0.0,
                memory_used_mb=estimated_memory,
                success=False,
                error_message=str(e),
                shots=shots,
            )

    def run_benchmark_suite(
        self, suite_name: str = "standard", backend_names: list[str] | None = None
    ) -> dict[str, list[BenchmarkResult]]:
        """Run a complete benchmark suite."""

        if suite_name not in self.benchmark_suites:
            raise ValueError(f"Unknown benchmark suite: {suite_name}")

        suite = self.benchmark_suites[suite_name]

        # Get available backends if not specified
        if backend_names is None:
            try:
                from .universal_interface import list_backends

                backend_names = list_backends()
            except Exception:
                backend_names = ["qiskit"]  # Fallback

        print(f"🚀 Running benchmark suite: {suite.name}")
        print(f"📝 {suite.description}")
        print(f"🔧 Backends: {', '.join(backend_names)}")
        print(f"🧪 Benchmarks: {', '.join(suite.benchmarks)}")
        print(f"📊 Qubit ranges: {suite.qubit_ranges}")
        print()

        all_results: dict[str, Any] = {}
        total_benchmarks = (
            len(suite.benchmarks)
            * len(suite.qubit_ranges)
            * len(suite.shot_counts)
            * len(backend_names)
            * suite.repetitions
        )
        completed = 0

        for benchmark_name in suite.benchmarks:
            for num_qubits in suite.qubit_ranges:
                for shots in suite.shot_counts:
                    for backend_name in backend_names:
                        for rep in range(suite.repetitions):
                            completed += 1
                            print(
                                f"[{completed}/{total_benchmarks}] "
                                f"{benchmark_name}({num_qubits}q, {shots} shots) on {backend_name} "
                                f"(rep {rep + 1}/{suite.repetitions})"
                            )

                            result = self.benchmark_circuit(benchmark_name, num_qubits, backend_name, shots)

                            key = f"{benchmark_name}_{num_qubits}q_{shots}shots_{backend_name}"
                            if key not in all_results:
                                all_results[key] = []
                            all_results[key].append(result)

                            if result.success:
                                print(f"  ✅ {result.execution_time:.3f}s")
                            else:
                                print(f"  ❌ {result.error_message}")

        # Save results
        self._save_benchmark_results(suite_name, all_results)

        return all_results

    def _save_benchmark_results(self, suite_name: str, results: dict[str, list[BenchmarkResult]]) -> None:
        """Save benchmark results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"benchmark_{suite_name}_{timestamp}.json"
        filepath = self.output_dir / filename

        # Convert results to serializable format
        serializable_results: dict[str, list[dict[str, Any]]] = {}
        for result_key, result_list in results.items():
            serializable_results[result_key] = [asdict(result) for result in result_list]

        with open(filepath, "w") as f:
            json.dump(serializable_results, f, indent=2)

        print(f"💾 Results saved to: {filepath}")

    def generate_benchmark_report(self, suite_name: str, results: dict[str, list[BenchmarkResult]]) -> str:
        """Generate a comprehensive benchmark report."""

        report_lines: list[str] = []
        report_lines.append(f"# Ariadne Benchmark Report: {suite_name}")
        report_lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")

        # Summary statistics
        total_tests = sum(len(result_list) for result_list in results.values())
        successful_tests = sum(sum(1 for r in result_list if r.success) for result_list in results.values())
        success_percentage = successful_tests / total_tests * 100 if total_tests > 0 else 0.0

        report_lines.append("## Summary")
        report_lines.append(f"- **Total Tests**: {total_tests}")
        report_lines.append(f"- **Successful**: {successful_tests} ({success_percentage:.1f}%)")
        report_lines.append(f"- **Failed**: {total_tests - successful_tests}")
        report_lines.append("")

        # Backend performance comparison
        backend_stats: dict[str, BackendPerformanceStats] = {}
        for result_list in results.values():
            for result in result_list:
                stats = backend_stats.setdefault(result.backend_name, BackendPerformanceStats())
                if result.success:
                    stats.times.append(result.execution_time)
                    stats.success_count += 1
                stats.total_count += 1

        report_lines.append("## Backend Performance")
        report_lines.append("| Backend | Success Rate | Avg Time (s) | Min Time (s) | Max Time (s) |")
        report_lines.append("|---------|--------------|--------------|--------------|--------------|")

        for backend_name, backend_stat in backend_stats.items():
            success_rate = (
                backend_stat.success_count / backend_stat.total_count * 100 if backend_stat.total_count else 0.0
            )
            if backend_stat.times:
                avg_time = float(np.mean(backend_stat.times))
                min_time = float(np.min(backend_stat.times))
                max_time = float(np.max(backend_stat.times))
                report_lines.append(
                    f"| {backend_name} | {success_rate:.1f}% | {avg_time:.3f} | {min_time:.3f} | {max_time:.3f} |"
                )
            else:
                report_lines.append(f"| {backend_name} | {success_rate:.1f}% | - | - | - |")

        report_lines.append("")

        # Algorithm performance breakdown
        algorithm_stats: dict[str, AlgorithmPerformanceStats] = {}
        for key, result_list in results.items():
            algorithm = key.split("_")[0]
            algorithm_stat = algorithm_stats.setdefault(algorithm, AlgorithmPerformanceStats())

            for result in result_list:
                algorithm_stat.total += 1
                if result.success:
                    algorithm_stat.success += 1
                    algorithm_stat.times.append(result.execution_time)

        report_lines.append("## Algorithm Performance")
        report_lines.append("| Algorithm | Success Rate | Avg Time (s) | Std Dev (s) |")
        report_lines.append("|-----------|--------------|--------------|-------------|")

        for algorithm, algorithm_stat in algorithm_stats.items():
            success_rate = algorithm_stat.success / algorithm_stat.total * 100 if algorithm_stat.total else 0.0
            if algorithm_stat.times:
                avg_time = float(np.mean(algorithm_stat.times))
                std_time = float(np.std(algorithm_stat.times))
                report_lines.append(f"| {algorithm} | {success_rate:.1f}% | {avg_time:.3f} | {std_time:.3f} |")
            else:
                report_lines.append(f"| {algorithm} | {success_rate:.1f}% | - | - |")

        report_lines.append("")

        # Detailed results by circuit size
        report_lines.append("## Performance by Circuit Size")

        # Group by qubit count
        qubit_stats: dict[int, list[float]] = {}
        for _result_key, result_list in results.items():
            for result in result_list:
                if result.success:
                    qubits_value = result.circuit_params.get("num_qubits")
                    if isinstance(qubits_value, int):
                        qubit_stats.setdefault(qubits_value, []).append(result.execution_time)

        for qubits in sorted(qubit_stats.keys()):
            times = qubit_stats[qubits]
            avg_time = float(np.mean(times))
            report_lines.append(f"- **{qubits} qubits**: {avg_time:.3f}s average, {len(times)} successful runs")

        report_lines.append("")
        report_lines.append("---")
        report_lines.append("*Generated by Ariadne Quantum Simulation Framework*")

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"benchmark_report_{suite_name}_{timestamp}.md"
        report_filepath = self.output_dir / report_filename

        with open(report_filepath, "w") as f:
            f.write("\n".join(report_lines))

        print(f"📋 Report saved to: {report_filepath}")

        return "\n".join(report_lines)


def run_quick_benchmark() -> dict[str, list[BenchmarkResult]]:
    """Run quick benchmark for validation."""
    benchmarks = QuantumAlgorithmBenchmarks()
    return benchmarks.run_benchmark_suite("quick")


def run_comprehensive_benchmark() -> dict[str, list[BenchmarkResult]]:
    """Run comprehensive benchmark suite."""
    benchmarks = QuantumAlgorithmBenchmarks()
    return benchmarks.run_benchmark_suite("comprehensive")


def compare_backends_on_algorithm(
    algorithm: str, num_qubits: int, backend_names: list[str]
) -> dict[str, BenchmarkResult]:
    """Compare specific backends on a single algorithm."""
    benchmarks = QuantumAlgorithmBenchmarks()
    results = {}

    for backend_name in backend_names:
        result = benchmarks.benchmark_circuit(algorithm, num_qubits, backend_name)
        results[backend_name] = result

    return results
