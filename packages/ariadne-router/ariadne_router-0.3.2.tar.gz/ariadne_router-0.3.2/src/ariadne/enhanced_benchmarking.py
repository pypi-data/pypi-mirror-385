"""
Enhanced benchmarking tools for Ariadne quantum simulators.

This module provides comprehensive benchmarking capabilities including performance comparison,
scalability analysis, and cross-backend validation.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from qiskit import QuantumCircuit

from ariadne import simulate
from ariadne.algorithms import AlgorithmParameters, get_algorithm


@dataclass
class BenchmarkResult:
    """Results from a single benchmark execution."""

    algorithm: str
    backend: str
    qubits: int
    depth: int
    shots: int
    execution_time: float
    success: bool
    error_message: str | None = None
    throughput: float = 0.0
    unique_outcomes: int = 0
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if self.success and self.execution_time > 0:
            self.throughput = self.shots / self.execution_time


@dataclass
class ScalabilityResult:
    """Results for scalability testing across qubit counts."""

    algorithm: str
    qubit_counts: list[int]
    execution_times: list[float]
    throughputs: list[float]
    success_rates: list[float]
    memory_usage: list[float] | None = None


class EnhancedBenchmarkSuite:
    """Enhanced benchmark suite for Ariadne quantum simulators."""

    def __init__(self) -> None:
        """Initialize the enhanced benchmark suite."""
        self.results: list[BenchmarkResult] = []

    def benchmark_single_algorithm(
        self, algorithm_name: str, qubit_count: int, backend_name: str = "auto", shots: int = 1000, iterations: int = 3
    ) -> list[BenchmarkResult]:
        """Benchmark a single algorithm with specified parameters."""
        results = []

        for _i in range(iterations):
            try:
                # Get the algorithm class and create circuit
                algorithm_class = get_algorithm(algorithm_name)
                params = AlgorithmParameters(n_qubits=qubit_count, shots=shots)
                algorithm = algorithm_class(params)
                circuit = algorithm.create_circuit()

                # Run simulation
                start_time = time.time()
                # Use None for 'auto' backend to let the system choose
                backend_for_sim = None if backend_name == "auto" else backend_name
                result = simulate(circuit, shots=shots, backend=backend_for_sim)
                end_time = time.time()

                execution_time = end_time - start_time

                benchmark_result = BenchmarkResult(
                    algorithm=algorithm_name,
                    backend=result.backend_used.value,
                    qubits=qubit_count,
                    depth=circuit.depth(),
                    shots=shots,
                    execution_time=execution_time,
                    success=True,
                    throughput=shots / execution_time if execution_time > 0 else 0,
                    unique_outcomes=len(result.counts),
                )

                results.append(benchmark_result)

            except Exception as e:
                benchmark_result = BenchmarkResult(
                    algorithm=algorithm_name,
                    backend=backend_name,
                    qubits=qubit_count,
                    depth=0,
                    shots=shots,
                    execution_time=0.0,
                    success=False,
                    error_message=str(e),
                )

                results.append(benchmark_result)

        # Store results
        self.results.extend(results)
        return results

    def benchmark_backend_comparison(
        self, algorithm_name: str, qubit_count: int, backends: list[str], shots: int = 1000
    ) -> dict[str, BenchmarkResult]:
        """Compare performance of different backends on the same algorithm."""
        comparison_results = {}

        for backend_name in backends:
            try:
                # Create algorithm circuit
                algorithm_class = get_algorithm(algorithm_name)
                params = AlgorithmParameters(n_qubits=qubit_count, shots=shots)
                algorithm = algorithm_class(params)
                circuit = algorithm.create_circuit()

                # Run simulation
                start_time = time.time()
                # Use None for 'auto' backend to let the system choose
                backend_for_sim = None if backend_name == "auto" else backend_name
                result = simulate(circuit, shots=shots, backend=backend_for_sim)
                end_time = time.time()

                execution_time = end_time - start_time

                benchmark_result = BenchmarkResult(
                    algorithm=algorithm_name,
                    backend=result.backend_used.value,
                    qubits=qubit_count,
                    depth=circuit.depth(),
                    shots=shots,
                    execution_time=execution_time,
                    success=True,
                    throughput=shots / execution_time if execution_time > 0 else 0,
                    unique_outcomes=len(result.counts),
                )

                comparison_results[backend_name] = benchmark_result

            except Exception as e:
                benchmark_result = BenchmarkResult(
                    algorithm=algorithm_name,
                    backend=backend_name,
                    qubits=qubit_count,
                    depth=0,
                    shots=shots,
                    execution_time=0.0,
                    success=False,
                    error_message=str(e),
                )

                comparison_results[backend_name] = benchmark_result

        # Store results
        self.results.extend(comparison_results.values())
        return comparison_results

    def scalability_test(
        self,
        algorithm_name: str,
        qubit_range: tuple[int, int, int],  # start, stop, step
        backend_name: str = "auto",
        shots: int = 1000,
    ) -> ScalabilityResult:
        """Test scalability of an algorithm across different qubit counts."""
        start, stop, step = qubit_range
        qubit_counts = list(range(start, stop + 1, step))

        execution_times = []
        throughputs = []
        success_rates = []

        for qubits in qubit_counts:
            try:
                # Run benchmark
                results = self.benchmark_single_algorithm(
                    algorithm_name=algorithm_name,
                    qubit_count=qubits,
                    backend_name=backend_name,
                    shots=shots,
                    iterations=1,  # Single iteration for scalability
                )

                successful_results = [r for r in results if r.success]
                if successful_results:
                    avg_time = sum(r.execution_time for r in successful_results) / len(successful_results)
                    avg_throughput = sum(r.throughput for r in successful_results) / len(successful_results)

                    execution_times.append(avg_time)
                    throughputs.append(avg_throughput)
                    success_rates.append(len(successful_results) / len(results))
                else:
                    execution_times.append(0.0)
                    throughputs.append(0.0)
                    success_rates.append(0.0)

            except Exception:
                execution_times.append(0.0)
                throughputs.append(0.0)
                success_rates.append(0.0)

        scalability_result = ScalabilityResult(
            algorithm=algorithm_name,
            qubit_counts=qubit_counts,
            execution_times=execution_times,
            throughputs=throughputs,
            success_rates=success_rates,
        )

        return scalability_result

    def generate_performance_report(self) -> str:
        """Generate a comprehensive performance report from collected results."""
        if not self.results:
            return "No benchmark results available."

        # Convert to DataFrame for analysis
        data = []
        for result in self.results:
            data.append(asdict(result))

        df = pd.DataFrame(data)

        report = []
        report.append("# Ariadne Benchmark Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Summary statistics
        total_tests = len(df)
        successful_tests = len(df[df["success"]])
        success_rate = successful_tests / total_tests * 100 if total_tests > 0 else 0

        report.append("## Summary Statistics")
        report.append(f"- Total Tests: {total_tests}")
        report.append(f"- Successful: {successful_tests} ({success_rate:.1f}%)")
        report.append(f"- Failed: {total_tests - successful_tests}")
        report.append("")

        # Backend comparison
        report.append("## Backend Performance Comparison")
        backend_stats = (
            df[df["success"]]
            .groupby("backend")
            .agg({"execution_time": ["mean", "std", "min", "max"], "throughput": ["mean", "std"], "qubits": "mean"})
            .round(4)
        )

        if not backend_stats.empty:
            report.append("### Performance by Backend")
            for backend in backend_stats.index:
                stats = backend_stats.loc[backend]
                avg_time = stats["execution_time"]["mean"]
                avg_throughput = stats["throughput"]["mean"]
                avg_qubits = int(stats["qubits"]["mean"])

                report.append(
                    f"- **{backend}**: Avg Time: {avg_time:.4f}s, Avg Throughput: {avg_throughput:.2f}/s, Avg Qubits: {avg_qubits}"
                )

        report.append("")

        # Algorithm comparison
        report.append("## Algorithm Performance Comparison")
        algorithm_stats = (
            df[df["success"]]
            .groupby("algorithm")
            .agg({"execution_time": ["mean", "std", "min", "max"], "throughput": ["mean", "std"], "qubits": "mean"})
            .round(4)
        )

        if not algorithm_stats.empty:
            report.append("### Performance by Algorithm")
            for algorithm in algorithm_stats.index:
                stats = algorithm_stats.loc[algorithm]
                avg_time = stats["execution_time"]["mean"]
                avg_throughput = stats["throughput"]["mean"]
                avg_qubits = int(stats["qubits"]["mean"])

                report.append(
                    f"- **{algorithm}**: Avg Time: {avg_time:.4f}s, Avg Throughput: {avg_throughput:.2f}/s, Avg Qubits: {avg_qubits}"
                )

        report.append("")
        report.append("---")
        report.append("*Report generated by Ariadne Enhanced Benchmark Suite*")

        return "\n".join(report)

    def plot_backend_comparison(self, save_path: str | None = None) -> None:
        """Create a visualization comparing backend performance."""
        if not self.results:
            print("No benchmark results to visualize.")
            return

        # Convert to DataFrame
        data = []
        for result in self.results:
            if result.success:  # Only plot successful results
                data.append(asdict(result))

        if not data:
            print("No successful benchmark results to visualize.")
            return

        df = pd.DataFrame(data)

        # Create comparison plot
        plt.figure(figsize=(12, 8))

        # Execution time comparison
        plt.subplot(2, 2, 1)
        if "execution_time" in df.columns:
            sns.boxplot(data=df, x="backend", y="execution_time")
            plt.title("Execution Time by Backend")
            plt.xticks(rotation=45)

        # Throughput comparison
        plt.subplot(2, 2, 2)
        if "throughput" in df.columns:
            sns.boxplot(data=df, x="backend", y="throughput")
            plt.title("Throughput by Backend")
            plt.xticks(rotation=45)

        # Success rate by backend
        plt.subplot(2, 2, 3)
        success_rate = df.groupby("backend")["success"].mean()
        # Convert to lists for type compatibility with matplotlib
        backend_names = list(success_rate.index)
        success_values = list(success_rate.values)
        plt.bar(backend_names, success_values)
        plt.title("Success Rate by Backend")
        plt.xticks(rotation=45)
        plt.ylabel("Success Rate")

        # Algorithm performance
        plt.subplot(2, 2, 4)
        if "execution_time" in df.columns:
            sns.boxplot(data=df, x="algorithm", y="execution_time")
            plt.title("Execution Time by Algorithm")
            plt.xticks(rotation=45)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)
        plt.show()

    def export_results(self, filepath: str, format: str = "json") -> None:
        """Export benchmark results to file."""
        if format.lower() == "json":
            # Convert results to serializable format
            serializable_results = [asdict(result) for result in self.results]
            with open(filepath, "w") as f:
                json.dump(serializable_results, f, indent=2)
        elif format.lower() == "csv":
            # Convert to DataFrame and save as CSV
            data = []
            for result in self.results:
                data.append(asdict(result))
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False)
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'json' or 'csv'.")

        print(f"Results exported to: {filepath}")


class CrossValidationSuite:
    """Suite for cross-validation of quantum simulation results."""

    def __init__(self) -> None:
        """Initialize cross-validation suite."""
        self.validation_results: list[Any] = []

    def validate_backend_consistency(
        self, circuit: QuantumCircuit, backends: list[str], shots: int = 1000, tolerance: float = 0.05
    ) -> dict[str, Any]:
        """Validate that different backends produce consistent results."""
        results = {}

        # Run simulation on all backends
        for backend in backends:
            try:
                # Use None for 'auto' backend to let the system choose
                backend_for_sim = None if backend == "auto" else backend
                result = simulate(circuit, shots=shots, backend=backend_for_sim)
                results[backend] = {
                    "counts": result.counts,
                    "backend_used": result.backend_used.value,
                    "execution_time": result.execution_time,
                    "success": True,
                }
            except Exception as e:
                results[backend] = {
                    "counts": {},
                    "backend_used": backend,
                    "execution_time": 0.0,
                    "success": False,
                    "error": str(e),
                }

        # Compare results for consistency
        successful_backends = [backend for backend, result in results.items() if result["success"]]

        if len(successful_backends) < 2:
            return {
                "consistent": len(successful_backends) > 0,
                "message": f"Not enough successful backends for comparison. Success: {successful_backends}",
                "results": results,
            }

        # Compare first successful backend with others
        reference_backend = successful_backends[0]
        reference_counts = results[reference_backend]["counts"]

        all_consistent = True
        differences: dict[str, float] = {}

        for backend in successful_backends[1:]:
            comparison_counts = results[backend]["counts"]

            # Type guard: ensure counts are dictionaries
            if not isinstance(reference_counts, dict) or not isinstance(comparison_counts, dict):
                differences[backend] = 1.0  # Maximum difference if not dicts
                all_consistent = False
                continue

            # Calculate distribution similarity
            all_keys = set(reference_counts.keys()) | set(comparison_counts.keys())
            total_ref = sum(reference_counts.values())
            total_comp = sum(comparison_counts.values())

            max_diff = 0.0
            for key in all_keys:
                ref_prob = reference_counts.get(key, 0) / total_ref
                comp_prob = comparison_counts.get(key, 0) / total_comp
                diff = abs(ref_prob - comp_prob)
                max_diff = max(max_diff, diff)

            differences[backend] = max_diff
            if max_diff > tolerance:
                all_consistent = False

        return {
            "consistent": all_consistent,
            "message": f"Max distribution difference: {max(differences.values()) if differences else 0:.4f}",
            "tolerance": tolerance,
            "differences": differences,
            "results": results,
        }


def run_comprehensive_benchmark(
    algorithms: list[str], backends: list[str], qubit_counts: list[int], shots: int = 1000
) -> EnhancedBenchmarkSuite:
    """Run a comprehensive benchmark across algorithms, backends, and qubit counts."""
    suite = EnhancedBenchmarkSuite()

    print("Running comprehensive benchmark...")
    print(f"Algorithms: {algorithms}")
    print(f"Backends: {backends}")
    print(f"Qubit counts: {qubit_counts}")
    print(f"Shots: {shots}")
    print("-" * 50)

    total_tests = len(algorithms) * len(backends) * len(qubit_counts)
    completed_tests = 0

    for algorithm in algorithms:
        for qubits in qubit_counts:
            for backend in backends:
                completed_tests += 1
                print(f"[{completed_tests}/{total_tests}] {algorithm} - {qubits}q - {backend}")

                try:
                    results = suite.benchmark_single_algorithm(
                        algorithm_name=algorithm, qubit_count=qubits, backend_name=backend, shots=shots, iterations=1
                    )

                    if results and results[0].success:
                        print(f"  ✓ {results[0].execution_time:.3f}s")
                    else:
                        print(f"  ✗ {results[0].error_message if results else 'Unknown error'}")

                except Exception as e:
                    print(f"  ✗ {str(e)}")

    print("\nBenchmark completed!")
    return suite


# Convenience functions
def quick_performance_test() -> EnhancedBenchmarkSuite:
    """Run a quick performance test with common algorithms and backends."""
    suite = EnhancedBenchmarkSuite()

    # Common algorithms to test
    algorithms = ["bell", "ghz", "qft"]
    qubit_counts = [2, 3, 4]

    print("Running quick performance test...")

    for alg in algorithms:
        for qubits in qubit_counts:
            results = suite.benchmark_single_algorithm(algorithm_name=alg, qubit_count=qubits, shots=100)

            if results and results[0].success:
                print(f"{alg} ({qubits}q): {results[0].execution_time:.4f}s")

    print(suite.generate_performance_report())
    return suite


def compare_backends(algorithm: str, qubits: int, backends: list[str]) -> dict[str, BenchmarkResult]:
    """Compare performance of different backends on a specific algorithm."""
    suite = EnhancedBenchmarkSuite()

    print(f"Comparing backends for {algorithm} with {qubits} qubits...")

    results = suite.benchmark_backend_comparison(algorithm_name=algorithm, qubit_count=qubits, backends=backends)

    for backend, result in results.items():
        if result.success:
            print(f"{backend}: {result.execution_time:.4f}s, {result.throughput:.2f}/s")
        else:
            print(f"{backend}: FAILED - {result.error_message}")

    return results


if __name__ == "__main__":
    # Demo usage
    print("Ariadne Enhanced Benchmark Suite Demo")
    print("=" * 40)

    # Run a quick test
    suite = quick_performance_test()

    # Compare backends for GHZ state
    print("\nBackend comparison for GHZ algorithm:")
    compare_results = compare_backends("ghz", 4, ["auto", "qiskit"])
