"""
Automated Performance Benchmarking Suite

This module provides comprehensive automated benchmarking capabilities for
Ariadne's quantum simulation platform, including backend performance analysis,
regression detection, and cross-platform comparisons.
"""

from __future__ import annotations

import gc
import json
import platform
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import psutil
from qiskit import QuantumCircuit

# Import Ariadne components
from .simulation import QuantumSimulator, SimulationOptions
from .visualization import ResultVisualizer, VisualizationConfig


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark execution."""

    # Test circuits
    qubit_range: tuple[int, int, int] = (4, 16, 2)  # (start, stop, step)
    depth_range: tuple[int, int, int] = (5, 50, 5)
    circuit_types: list[str] = field(
        default_factory=lambda: [
            "random_clifford",
            "random_general",
            "ghz_state",
            "qft",
            "vqe_ansatz",
            "qaoa_maxcut",
        ]
    )

    # Execution parameters
    shots_per_test: int = 1000
    repetitions: int = 3
    timeout_seconds: float = 300.0

    # Backend selection
    backends_to_test: list[str] = field(
        default_factory=lambda: ["stim", "qiskit", "metal", "cuda", "tensor_network", "ddsim"]
    )

    # Performance analysis
    enable_memory_profiling: bool = True
    enable_cpu_profiling: bool = True
    enable_scaling_analysis: bool = True

    # Output options
    save_detailed_results: bool = True
    generate_reports: bool = True
    output_dir: Path = Path("./benchmark_results")


@dataclass
class BenchmarkResult:
    """Result of a single benchmark test."""

    # Test identification
    test_id: str
    circuit_type: str
    num_qubits: int
    circuit_depth: int
    backend_used: str

    # Performance metrics
    execution_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    shots: int

    # Success metrics
    success: bool
    error_message: str | None = None

    # System information
    platform_info: dict[str, str] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Circuit analysis
    circuit_analysis: dict[str, Any] = field(default_factory=dict)

    # Additional metrics
    throughput_shots_per_sec: float = 0.0
    memory_efficiency_shots_per_mb: float = 0.0


@dataclass
class BenchmarkSuite:
    """Complete benchmark suite results."""

    # Suite metadata
    suite_id: str
    start_time: str
    end_time: str
    total_duration: float

    # Configuration
    config: BenchmarkConfig

    # Results
    results: list[BenchmarkResult] = field(default_factory=list)

    # Summary statistics
    summary: dict[str, Any] = field(default_factory=dict)

    # System information
    system_info: dict[str, str] = field(default_factory=dict)


class CircuitGenerator:
    """Generator for benchmark test circuits."""

    @staticmethod
    def generate_random_clifford(num_qubits: int, depth: int | None) -> QuantumCircuit:
        """Generate random Clifford circuit."""
        qc = QuantumCircuit(num_qubits, num_qubits)

        if depth is None:
            depth = num_qubits * 2  # Default depth

        clifford_gates = ["h", "x", "y", "z", "s", "cx"]

        for _ in range(depth):
            gate = np.random.choice(clifford_gates)

            if gate == "cx":
                control = np.random.randint(num_qubits)
                target = np.random.randint(num_qubits)
                if control != target:
                    qc.cx(control, target)
            else:
                qubit = np.random.randint(num_qubits)
                getattr(qc, gate)(qubit)

        qc.measure_all()
        return qc

    @staticmethod
    def generate_random_general(num_qubits: int, depth: int | None) -> QuantumCircuit:
        """Generate random general circuit with non-Clifford gates."""
        qc = QuantumCircuit(num_qubits, num_qubits)

        if depth is None:
            depth = num_qubits * 3  # Default depth for general circuits

        gates = ["h", "x", "y", "z", "rx", "ry", "rz", "t", "cx"]

        for _ in range(depth):
            gate = np.random.choice(gates)

            if gate == "cx":
                control = np.random.randint(num_qubits)
                target = np.random.randint(num_qubits)
                if control != target:
                    qc.cx(control, target)
            elif gate in ["rx", "ry", "rz"]:
                qubit = np.random.randint(num_qubits)
                angle = np.random.uniform(0, 2 * np.pi)
                getattr(qc, gate)(angle, qubit)
            else:
                qubit = np.random.randint(num_qubits)
                getattr(qc, gate)(qubit)

        qc.measure_all()
        return qc

    @staticmethod
    def generate_ghz_state(num_qubits: int, depth: int | None = None) -> QuantumCircuit:
        """Generate GHZ state circuit."""
        qc = QuantumCircuit(num_qubits, num_qubits)

        qc.h(0)
        for i in range(1, num_qubits):
            qc.cx(0, i)

        qc.measure_all()
        return qc

    @staticmethod
    def generate_qft(num_qubits: int, depth: int | None = None) -> QuantumCircuit:
        """Generate Quantum Fourier Transform circuit."""
        qc = QuantumCircuit(num_qubits, num_qubits)

        # Simplified QFT implementation
        for i in range(num_qubits):
            qc.h(i)
            for j in range(i + 1, num_qubits):
                qc.cp(np.pi / (2 ** (j - i)), j, i)

        # Reverse the qubits
        for i in range(num_qubits // 2):
            qc.swap(i, num_qubits - 1 - i)

        qc.measure_all()
        return qc

    @staticmethod
    def generate_vqe_ansatz(num_qubits: int, depth: int | None) -> QuantumCircuit:
        """Generate VQE ansatz circuit."""
        qc = QuantumCircuit(num_qubits, num_qubits)

        if depth is None:
            depth = num_qubits  # Default depth

        # Initialize with Hadamards
        for i in range(num_qubits):
            qc.h(i)

        # Add parameterized layers
        for _layer in range(depth // 2):
            # Entangling layer
            for i in range(0, num_qubits - 1, 2):
                qc.cx(i, i + 1)

            # Rotation layer
            for i in range(num_qubits):
                qc.ry(np.random.uniform(0, 2 * np.pi), i)

        qc.measure_all()
        return qc

    @staticmethod
    def generate_qaoa_maxcut(num_qubits: int, depth: int | None) -> QuantumCircuit:
        """Generate QAOA MaxCut circuit."""
        qc = QuantumCircuit(num_qubits, num_qubits)

        if depth is None:
            depth = max(4, num_qubits)  # Default depth for QAOA

        # Initial superposition
        for i in range(num_qubits):
            qc.h(i)

        # QAOA layers
        for _layer in range(depth // 4):
            # Problem Hamiltonian
            for i in range(num_qubits - 1):
                qc.cx(i, i + 1)
                qc.rz(np.random.uniform(0, np.pi), i + 1)
                qc.cx(i, i + 1)

            # Mixer Hamiltonian
            for i in range(num_qubits):
                qc.rx(np.random.uniform(0, np.pi), i)

        qc.measure_all()
        return qc


class PerformanceBenchmarker:
    """Automated performance benchmarking system."""

    def __init__(self, config: BenchmarkConfig | None = None):
        """Initialize benchmarker with configuration."""
        self.config = config or BenchmarkConfig()
        self.circuit_generator = CircuitGenerator()

        # Ensure output directory exists
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize system monitoring
        self.system_info = self._collect_system_info()

    def run_full_benchmark_suite(self) -> BenchmarkSuite:
        """Run complete benchmark suite."""

        suite_id = f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()

        print(f"🚀 Starting benchmark suite: {suite_id}")
        print(
            f"Configuration: {len(self.config.backends_to_test)} backends, "
            f"{len(self.config.circuit_types)} circuit types"
        )

        # Generate test cases
        test_cases = self._generate_test_cases()
        print(f"Generated {len(test_cases)} test cases")

        # Run benchmarks
        results = []
        total_tests = len(test_cases)

        for i, test_case in enumerate(test_cases):
            print(f"Progress: {i + 1}/{total_tests} - Running {test_case['test_id']}")

            result = self._run_single_benchmark(test_case)
            results.append(result)

            # Periodic cleanup
            if i % 10 == 0:
                gc.collect()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Create benchmark suite
        suite = BenchmarkSuite(
            suite_id=suite_id,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            total_duration=duration,
            config=self.config,
            results=results,
            system_info=self.system_info,
        )

        # Generate summary statistics
        suite.summary = self._generate_summary_statistics(results)

        # Save results
        self._save_benchmark_results(suite)

        # Generate report
        if self.config.generate_reports:
            self._generate_benchmark_report(suite)

        print(f"✅ Benchmark suite completed in {duration:.2f} seconds")
        print(f"Results saved to: {self.config.output_dir}")

        return suite

    def run_backend_comparison(
        self, circuit: QuantumCircuit, backends: list[str] | None = None
    ) -> dict[str, BenchmarkResult]:
        """Run comparative benchmark across backends for a specific circuit."""

        backends = backends or self.config.backends_to_test
        results = {}

        for backend in backends:
            test_case = {
                "test_id": f"comparison_{backend}",
                "circuit": circuit,
                "circuit_type": "comparison",
                "backend": backend,
                "shots": self.config.shots_per_test,
            }

            result = self._run_single_benchmark(test_case)
            if result.success:
                results[backend] = result

        return results

    def run_scaling_benchmark(self, circuit_type: str, backend: str, max_qubits: int = 20) -> list[BenchmarkResult]:
        """Run scaling benchmark for a specific circuit type and backend."""

        results = []

        for num_qubits in range(4, max_qubits + 1, 2):
            circuit = self._generate_circuit(circuit_type, num_qubits, 10)

            test_case = {
                "test_id": f"scaling_{circuit_type}_{backend}_{num_qubits}q",
                "circuit": circuit,
                "circuit_type": circuit_type,
                "backend": backend,
                "shots": self.config.shots_per_test,
            }

            result = self._run_single_benchmark(test_case)
            results.append(result)

            # Stop if backend fails or takes too long
            if not result.success or result.execution_time > 60.0:
                break

        return results

    def _generate_test_cases(self) -> list[dict[str, Any]]:
        """Generate all test cases for benchmark suite."""

        test_cases = []
        test_id = 0

        for circuit_type in self.config.circuit_types:
            for num_qubits in range(*self.config.qubit_range):
                for depth in range(*self.config.depth_range):
                    for backend in self.config.backends_to_test:
                        # Generate circuit
                        circuit = self._generate_circuit(circuit_type, num_qubits, depth)

                        test_case = {
                            "test_id": f"test_{test_id:04d}",
                            "circuit": circuit,
                            "circuit_type": circuit_type,
                            "backend": backend,
                            "shots": self.config.shots_per_test,
                        }

                        test_cases.append(test_case)
                        test_id += 1

        return test_cases

    def _generate_circuit(self, circuit_type: str, num_qubits: int, depth: int) -> QuantumCircuit:
        """Generate circuit of specified type."""

        generator_map: dict[str, Callable[[int, int | None], QuantumCircuit]] = {
            "random_clifford": self.circuit_generator.generate_random_clifford,
            "random_general": self.circuit_generator.generate_random_general,
            "ghz_state": self.circuit_generator.generate_ghz_state,
            "qft": self.circuit_generator.generate_qft,
            "vqe_ansatz": self.circuit_generator.generate_vqe_ansatz,
            "qaoa_maxcut": self.circuit_generator.generate_qaoa_maxcut,
        }

        if circuit_type not in generator_map:
            raise ValueError(f"Unknown circuit type: {circuit_type}")

        return generator_map[circuit_type](num_qubits, depth)

    def _run_single_benchmark(self, test_case: dict[str, Any]) -> BenchmarkResult:
        """Run a single benchmark test."""

        circuit = test_case["circuit"]
        backend = test_case["backend"]
        shots = test_case["shots"]

        # Initialize monitoring
        start_memory = psutil.virtual_memory().used / (1024 * 1024)  # MB
        process = psutil.Process()

        try:
            # Configure simulation
            options = SimulationOptions(
                backend_preference=[backend],
                shots=shots,
                analyze_quantum_advantage=False,  # Skip for performance
                estimate_resources=False,
            )

            simulator = QuantumSimulator()

            # Run benchmark with timing
            start_time = time.perf_counter()
            start_cpu_times = process.cpu_times()

            result = simulator.simulate(circuit, options)

            end_time = time.perf_counter()
            end_cpu_times = process.cpu_times()

            # Calculate metrics
            execution_time = end_time - start_time
            end_memory = psutil.virtual_memory().used / (1024 * 1024)
            memory_usage = max(0, end_memory - start_memory)

            cpu_time = end_cpu_times.user - start_cpu_times.user + end_cpu_times.system - start_cpu_times.system
            cpu_usage = (cpu_time / execution_time * 100) if execution_time > 0 else 0

            # Calculate derived metrics
            throughput = shots / execution_time if execution_time > 0 else 0
            memory_efficiency = shots / max(memory_usage, 1) if memory_usage > 0 else shots

            # Analyze circuit
            from .route.analyze import analyze_circuit

            circuit_analysis = analyze_circuit(circuit)

            return BenchmarkResult(
                test_id=test_case["test_id"],
                circuit_type=test_case["circuit_type"],
                num_qubits=circuit.num_qubits,
                circuit_depth=circuit.depth(),
                backend_used=result.backend_used,
                execution_time=execution_time,
                memory_usage_mb=memory_usage,
                cpu_usage_percent=cpu_usage,
                shots=shots,
                success=True,
                platform_info=self.system_info,
                circuit_analysis=circuit_analysis,
                throughput_shots_per_sec=throughput,
                memory_efficiency_shots_per_mb=memory_efficiency,
            )

        except Exception as e:
            # Record failure
            return BenchmarkResult(
                test_id=test_case["test_id"],
                circuit_type=test_case["circuit_type"],
                num_qubits=circuit.num_qubits,
                circuit_depth=circuit.depth(),
                backend_used=backend,
                execution_time=0.0,
                memory_usage_mb=0.0,
                cpu_usage_percent=0.0,
                shots=shots,
                success=False,
                error_message=str(e),
                platform_info=self.system_info,
            )

    def _collect_system_info(self) -> dict[str, str]:
        """Collect system information for benchmarking context."""

        return {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "architecture": platform.architecture()[0],
            "python_version": platform.python_version(),
            "cpu_count": str(psutil.cpu_count()),
            "memory_total_gb": f"{psutil.virtual_memory().total / (1024**3):.2f}",
            "memory_available_gb": f"{psutil.virtual_memory().available / (1024**3):.2f}",
        }

    def _generate_summary_statistics(self, results: list[BenchmarkResult]) -> dict[str, Any]:
        """Generate summary statistics from benchmark results."""

        successful_results = [r for r in results if r.success]

        if not successful_results:
            return {"total_tests": len(results), "successful_tests": 0}

        execution_times = [r.execution_time for r in successful_results]
        throughputs = [r.throughput_shots_per_sec for r in successful_results]
        memory_usages = [r.memory_usage_mb for r in successful_results]

        # Backend performance
        backend_stats: dict[str, list[float]] = {}
        for result in successful_results:
            backend = result.backend_used
            if backend not in backend_stats:
                backend_stats[backend] = []
            backend_stats[backend].append(result.execution_time)

        backend_summary = {}
        for backend, times in backend_stats.items():
            backend_summary[backend] = {
                "count": len(times),
                "mean_time": np.mean(times),
                "std_time": np.std(times),
                "min_time": np.min(times),
                "max_time": np.max(times),
            }

        return {
            "total_tests": len(results),
            "successful_tests": len(successful_results),
            "success_rate": len(successful_results) / len(results),
            "execution_time_stats": {
                "mean": np.mean(execution_times),
                "std": np.std(execution_times),
                "min": np.min(execution_times),
                "max": np.max(execution_times),
                "median": np.median(execution_times),
            },
            "throughput_stats": {
                "mean": np.mean(throughputs),
                "std": np.std(throughputs),
                "max": np.max(throughputs),
            },
            "memory_stats": {
                "mean": np.mean(memory_usages),
                "std": np.std(memory_usages),
                "max": np.max(memory_usages),
            },
            "backend_performance": backend_summary,
        }

    def _save_benchmark_results(self, suite: BenchmarkSuite) -> None:
        """Save benchmark results to files."""

        # Save detailed results as JSON
        results_file = self.config.output_dir / f"{suite.suite_id}_results.json"

        # Convert to serializable format
        suite_dict = asdict(suite)

        with open(results_file, "w") as f:
            json.dump(suite_dict, f, indent=2, default=str)

        # Save summary as separate file
        summary_file = self.config.output_dir / f"{suite.suite_id}_summary.json"

        with open(summary_file, "w") as f:
            json.dump(suite.summary, f, indent=2, default=str)

        print(f"Results saved to: {results_file}")

    def _generate_benchmark_report(self, suite: BenchmarkSuite) -> None:
        """Generate comprehensive benchmark report with visualizations."""

        # Create visualizations
        viz_config = VisualizationConfig(output_dir=self.config.output_dir / "plots", save_plots=True, show_plots=False)

        visualizer = ResultVisualizer(viz_config)

        # Performance comparison plots
        successful_results = [r for r in suite.results if r.success]

        if successful_results:
            self._create_performance_plots(successful_results, visualizer)

        # Generate text report
        report_file = self.config.output_dir / f"{suite.suite_id}_report.md"
        self._create_text_report(suite, report_file)

    def _create_performance_plots(self, results: list[BenchmarkResult], visualizer: ResultVisualizer) -> None:
        """Create performance visualization plots."""

        # This would create various performance plots
        # Implementation would use matplotlib/plotly for visualization
        pass

    def _create_text_report(self, suite: BenchmarkSuite, report_file: Path) -> None:
        """Create markdown report."""

        with open(report_file, "w") as f:
            f.write("# Ariadne Benchmark Report\n\n")
            f.write(f"**Suite ID:** {suite.suite_id}\n")
            f.write(f"**Date:** {suite.start_time}\n")
            f.write(f"**Duration:** {suite.total_duration:.2f} seconds\n\n")

            f.write("## System Information\n\n")
            for key, value in suite.system_info.items():
                f.write(f"- **{key}:** {value}\n")

            f.write("\n## Summary Statistics\n\n")
            summary = suite.summary
            f.write(f"- **Total Tests:** {summary['total_tests']}\n")
            f.write(f"- **Successful Tests:** {summary['successful_tests']}\n")
            f.write(f"- **Success Rate:** {summary['success_rate']:.2%}\n")

            if "execution_time_stats" in summary:
                exec_stats = summary["execution_time_stats"]
                f.write(f"- **Mean Execution Time:** {exec_stats['mean']:.3f}s\n")
                f.write(f"- **Max Execution Time:** {exec_stats['max']:.3f}s\n")

            f.write("\n## Backend Performance\n\n")
            if "backend_performance" in summary:
                for backend, stats in summary["backend_performance"].items():
                    f.write(f"### {backend}\n\n")
                    f.write(f"- Tests: {stats['count']}\n")
                    f.write(f"- Mean Time: {stats['mean_time']:.3f}s\n")
                    f.write(f"- Best Time: {stats['min_time']:.3f}s\n\n")


# Convenience functions
def run_quick_benchmark(backends: list[str] | None = None) -> BenchmarkSuite:
    """Run a quick benchmark with default settings."""

    config = BenchmarkConfig(
        qubit_range=(4, 12, 4),
        depth_range=(5, 20, 5),
        circuit_types=["random_clifford", "random_general"],
        backends_to_test=backends or ["qiskit", "stim"],
        repetitions=1,
    )

    benchmarker = PerformanceBenchmarker(config)
    return benchmarker.run_full_benchmark_suite()


def compare_backends_performance(
    circuit: QuantumCircuit, backends: list[str] | None = None
) -> dict[str, BenchmarkResult]:
    """Quick backend comparison for a specific circuit."""

    benchmarker = PerformanceBenchmarker()
    return benchmarker.run_backend_comparison(circuit, backends)
