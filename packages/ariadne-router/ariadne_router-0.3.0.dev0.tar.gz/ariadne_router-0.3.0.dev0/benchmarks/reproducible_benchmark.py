#!/usr/bin/env python3
"""
Reproducible benchmark suite for Ariadne quantum circuit router.

This script provides standardized benchmarks that can be run in CI/CD
environments to validate performance and detect regressions.
"""

import importlib.util
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from qiskit import QuantumCircuit

from ariadne import simulate
from ariadne.route.enhanced_router import EnhancedQuantumRouter
from ariadne.types import BackendType


@dataclass
class BenchmarkResult:
    """Results from a single benchmark run."""

    circuit_name: str
    backend_used: str
    execution_time: float
    success: bool
    error: str | None
    shots: int
    circuit_qubits: int
    circuit_depth: int
    expected_backend: str | None = None
    fallback_reason: str | None = None


@dataclass
class BenchmarkSuite:
    """Complete benchmark suite results."""

    timestamp: str
    total_tests: int
    passed: int
    failed: int
    results: list[BenchmarkResult]
    environment_info: dict[str, Any]


class ReproducibleBenchmarks:
    """Standardized benchmark suite for CI/CD validation."""

    def __init__(self, shots: int = 1000):
        self.shots = shots
        try:
            self.router = EnhancedQuantumRouter()
        except Exception as e:
            print(f"Warning: Failed to initialize EnhancedQuantumRouter: {str(e)}")
            self.router = None

    def create_test_circuits(self) -> dict[str, QuantumCircuit]:
        """Create standardized test circuits for benchmarking."""
        circuits = {}

        # Small Clifford circuits (should use Stim)
        circuits["small_clifford_ghz"] = self._create_ghz_circuit(3)
        circuits["small_clifford_ladder"] = self._create_clifford_ladder(4)

        # Medium Clifford circuits
        circuits["medium_clifford_ghz"] = self._create_ghz_circuit(10)
        circuits["medium_clifford_stabilizer"] = self._create_stabilizer_circuit(8)

        # Large Clifford circuits (test Stim capability)
        circuits["large_clifford_ghz"] = self._create_ghz_circuit(25)
        circuits["large_clifford_surface_code"] = self._create_surface_code_circuit(5, 5)

        # Non-Clifford circuits (should use Metal/CUDA/Tensor Network)
        circuits["small_non_clifford"] = self._create_parameterized_circuit(3, 2)
        circuits["medium_non_clifford"] = self._create_parameterized_circuit(8, 5)

        # Mixed circuits
        circuits["mixed_vqe_ansatz"] = self._create_vqe_ansatz(6)
        circuits["mixed_qaoa"] = self._create_qaoa_circuit(4)

        # Edge cases
        circuits["single_qubit"] = self._create_single_qubit_circuit()
        circuits["no_gates"] = self._create_empty_circuit(3)
        circuits["measurement_only"] = self._create_measurement_only_circuit(3)

        return circuits

    def _create_ghz_circuit(self, n_qubits: int) -> QuantumCircuit:
        """Create a GHZ state circuit (Clifford)."""
        qc = QuantumCircuit(n_qubits, n_qubits)
        qc.h(0)
        for i in range(n_qubits - 1):
            qc.cx(i, i + 1)
        qc.measure_all()
        return qc

    def _create_clifford_ladder(self, n_qubits: int) -> QuantumCircuit:
        """Create a Clifford ladder circuit."""
        qc = QuantumCircuit(n_qubits, n_qubits)
        for i in range(n_qubits):
            qc.h(i)
        for i in range(n_qubits - 1):
            qc.cx(i, i + 1)
        for i in range(n_qubits):
            qc.s(i)
        qc.measure_all()
        return qc

    def _create_stabilizer_circuit(self, n_qubits: int) -> QuantumCircuit:
        """Create a stabilizer circuit."""
        qc = QuantumCircuit(n_qubits, n_qubits)
        # Create random Clifford circuit
        for _ in range(n_qubits * 2):
            # Random H gates
            if _ % 3 == 0:
                qc.h(_ % n_qubits)
            # Random CX gates
            elif _ % 3 == 1:
                qc.cx(_ % n_qubits, (_ + 1) % n_qubits)
            # Random S gates
            else:
                qc.s(_ % n_qubits)
        qc.measure_all()
        return qc

    def _create_surface_code_circuit(self, width: int, height: int) -> QuantumCircuit:
        """Create a surface code-like circuit (Clifford)."""
        n_qubits = width * height
        qc = QuantumCircuit(n_qubits, n_qubits)

        # Initialize with |+⟩ states
        for i in range(n_qubits):
            qc.h(i)

        # Apply stabilizer measurements (simplified)
        for i in range(width - 1):
            for j in range(height - 1):
                center = i * height + j
                right = center + height
                bottom = center + 1

                if right < n_qubits and bottom < n_qubits:
                    qc.cx(center, right)
                    qc.cx(center, bottom)

        qc.measure_all()
        return qc

    def _create_parameterized_circuit(self, n_qubits: int, depth: int) -> QuantumCircuit:
        """Create a parameterized circuit (non-Clifford)."""
        qc = QuantumCircuit(n_qubits, n_qubits)

        for d in range(depth):
            # Layer of RY rotations
            for i in range(n_qubits):
                qc.ry(0.1 * (d + 1) * (i + 1), i)

            # Layer of entangling gates
            for i in range(n_qubits - 1):
                qc.cx(i, i + 1)

        qc.measure_all()
        return qc

    def _create_vqe_ansatz(self, n_qubits: int) -> QuantumCircuit:
        """Create a VQE ansatz circuit."""
        qc = QuantumCircuit(n_qubits, n_qubits)

        # Initial layer
        for i in range(n_qubits):
            qc.ry(0.1, i)

        # Entangling layers
        for layer in range(2):
            for i in range(n_qubits - 1):
                qc.cx(i, i + 1)
            for i in range(n_qubits):
                qc.ry(0.2 * (layer + 1), i)

        qc.measure_all()
        return qc

    def _create_qaoa_circuit(self, n_qubits: int) -> QuantumCircuit:
        """Create a QAOA circuit."""
        qc = QuantumCircuit(n_qubits, n_qubits)

        # Initial superposition
        for i in range(n_qubits):
            qc.h(i)

        # QAOA layers
        for p in range(2):
            # Problem layer (ZZ interactions)
            for i in range(n_qubits - 1):
                qc.cx(i, i + 1)
                qc.rz(0.1 * (p + 1), i + 1)
                qc.cx(i, i + 1)

            # Mixer layer
            for i in range(n_qubits):
                qc.rx(0.2 * (p + 1), i)

        qc.measure_all()
        return qc

    def _create_single_qubit_circuit(self) -> QuantumCircuit:
        """Create a single qubit circuit."""
        qc = QuantumCircuit(1, 1)
        qc.h(0)
        qc.measure_all()
        return qc

    def _create_empty_circuit(self, n_qubits: int) -> QuantumCircuit:
        """Create an empty circuit with just measurements."""
        qc = QuantumCircuit(n_qubits, n_qubits)
        qc.measure_all()
        return qc

    def _create_measurement_only_circuit(self, n_qubits: int) -> QuantumCircuit:
        """Create a circuit with only measurements."""
        qc = QuantumCircuit(n_qubits, n_qubits)
        qc.measure_all()
        return qc

    def run_benchmark(
        self, circuit_name: str, circuit: QuantumCircuit, expected_backend: str | None = None
    ) -> BenchmarkResult:
        """Run a single benchmark test."""
        if self.router is None:
            return BenchmarkResult(
                circuit_name=circuit_name,
                backend_used="failed",
                execution_time=float("inf"),
                success=False,
                error="EnhancedQuantumRouter not initialized",
                shots=self.shots,
                circuit_qubits=circuit.num_qubits,
                circuit_depth=circuit.depth(),
                expected_backend=expected_backend,
            )

        try:
            start_time = time.perf_counter()
            result = simulate(circuit, shots=self.shots)
            end_time = time.perf_counter()

            execution_time = end_time - start_time

            return BenchmarkResult(
                circuit_name=circuit_name,
                backend_used=result.backend_used.value,
                execution_time=execution_time,
                success=True,
                error=None,
                shots=self.shots,
                circuit_qubits=circuit.num_qubits,
                circuit_depth=circuit.depth(),
                expected_backend=expected_backend,
                fallback_reason=result.fallback_reason,
            )

        except Exception as e:
            return BenchmarkResult(
                circuit_name=circuit_name,
                backend_used="failed",
                execution_time=float("inf"),
                success=False,
                error=str(e),
                shots=self.shots,
                circuit_qubits=circuit.num_qubits,
                circuit_depth=circuit.depth(),
                expected_backend=expected_backend,
            )

    def run_full_suite(self) -> BenchmarkSuite:
        """Run the complete benchmark suite."""
        circuits = self.create_test_circuits()
        results = []

        # Define expected backends for validation
        expected_backends = {
            "small_clifford_ghz": "stim",
            "small_clifford_ladder": "stim",
            "medium_clifford_ghz": "stim",
            "medium_clifford_stabilizer": "stim",
            "large_clifford_ghz": "stim",
            "large_clifford_surface_code": "stim",
            # Non-Clifford circuits may use various backends
            "small_non_clifford": None,  # Could be Metal, CUDA, or Qiskit
            "medium_non_clifford": None,
            "mixed_vqe_ansatz": None,
            "mixed_qaoa": None,
            "single_qubit": None,
            "no_gates": None,
            "measurement_only": None,
        }

        print("Running reproducible benchmark suite...")

        for circuit_name, circuit in circuits.items():
            print(f"  Testing {circuit_name}...")
            expected = expected_backends.get(circuit_name)
            result = self.run_benchmark(circuit_name, circuit, expected)
            results.append(result)

        # Calculate summary statistics
        passed = sum(1 for r in results if r.success)
        failed = len(results) - passed

        # Get environment info
        environment_info = self._get_environment_info()

        suite = BenchmarkSuite(
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            total_tests=len(results),
            passed=passed,
            failed=failed,
            results=results,
            environment_info=environment_info,
        )

        return suite

    def _get_environment_info(self) -> dict[str, Any]:
        """Get information about the test environment."""
        import platform
        import sys

        try:
            from ariadne.backends.metal_backend import is_metal_available

            metal_available = is_metal_available()
        except Exception:  # pragma: no cover - environment inspection best-effort
            metal_available = False

        try:
            from ariadne.backends.cuda_backend import is_cuda_available

            cuda_available = is_cuda_available()
        except Exception:  # pragma: no cover - environment inspection best-effort
            cuda_available = False

        return {
            "platform": platform.platform(),
            "python_version": sys.version,
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "metal_available": metal_available,
            "cuda_available": cuda_available,
            "router_backends": [backend.value for backend in BackendType],
        }

    def validate_results(self, suite: BenchmarkSuite) -> list[str]:
        """Validate benchmark results and return list of issues."""
        issues = []

        for result in suite.results:
            # Check for failures
            if not result.success:
                issues.append(f"❌ {result.circuit_name}: Failed with error: {result.error}")
                continue

            # Validate expected backends for Clifford circuits
            if (
                result.expected_backend == "stim"
                and result.backend_used != "stim"
                and importlib.util.find_spec("stim") is not None
            ):
                issues.append(f"⚠️  {result.circuit_name}: Expected Stim but used {result.backend_used}")

            # Check for reasonable execution times (< 10 seconds for test circuits)
            if result.execution_time > 10.0:
                issues.append(f"🐌 {result.circuit_name}: Slow execution ({result.execution_time:.2f}s)")

            # Check for infinite execution times
            if result.execution_time == float("inf"):
                issues.append(f"💥 {result.circuit_name}: Infinite execution time")

        return issues

    def save_results(self, suite: BenchmarkSuite, filepath: Path) -> None:
        """Save benchmark results to JSON file."""
        # Convert to dict for JSON serialization
        suite_dict = asdict(suite)

        with open(filepath, "w") as f:
            json.dump(suite_dict, f, indent=2)

    def generate_report(self, suite: BenchmarkSuite) -> str:
        """Generate a human-readable benchmark report."""
        report = []
        report.append("# Ariadne Benchmark Report")
        report.append(f"**Timestamp:** {suite.timestamp}")
        report.append(f"**Environment:** {suite.environment_info['platform']}")
        report.append(f"**Tests:** {suite.passed}/{suite.total_tests} passed")
        report.append("")

        # Summary statistics
        successful_results = [r for r in suite.results if r.success]
        if successful_results:
            avg_time = sum(r.execution_time for r in successful_results) / len(successful_results)
            report.append(f"**Average execution time:** {avg_time:.4f}s")

        # Backend usage statistics
        backend_counts = {}
        for result in successful_results:
            backend_counts[result.backend_used] = backend_counts.get(result.backend_used, 0) + 1

        report.append("## Backend Usage")
        for backend, count in sorted(backend_counts.items()):
            percentage = (count / len(successful_results)) * 100
            report.append(f"- **{backend}:** {count} circuits ({percentage:.1f}%)")

        # Detailed results
        report.append("## Detailed Results")
        report.append("| Circuit | Backend | Time (s) | Status |")
        report.append("|---------|---------|----------|--------|")

        for result in suite.results:
            status = "✅ Pass" if result.success else "❌ Fail"
            time_str = f"{result.execution_time:.4f}" if result.success else "∞"
            report.append(f"| {result.circuit_name} | {result.backend_used} | {time_str} | {status} |")

        # Validation issues
        issues = self.validate_results(suite)
        if issues:
            report.append("## Issues Found")
            for issue in issues:
                report.append(f"- {issue}")

        return "\n".join(report)


def main():
    """Run the benchmark suite and generate reports."""
    benchmarks = ReproducibleBenchmarks(shots=1000)
    suite = benchmarks.run_full_suite()

    # Create results directory
    results_dir = Path("benchmarks/results")
    results_dir.mkdir(exist_ok=True)

    # Save JSON results
    json_path = results_dir / "reproducible_benchmark_results.json"
    benchmarks.save_results(suite, json_path)

    # Generate and save report
    report = benchmarks.generate_report(suite)
    report_path = results_dir / "reproducible_benchmark_report.md"
    with open(report_path, "w") as f:
        f.write(report)

    # Print summary
    print("\n📊 Benchmark Results:")
    print(f"   Tests: {suite.passed}/{suite.total_tests} passed")
    print(f"   Results saved to: {json_path}")
    print(f"   Report saved to: {report_path}")

    # Validate and show issues
    issues = benchmarks.validate_results(suite)
    if issues:
        print(f"\n⚠️  Issues found ({len(issues)}):")
        for issue in issues[:5]:  # Show first 5 issues
            print(f"   {issue}")
        if len(issues) > 5:
            print(f"   ... and {len(issues) - 5} more")
    else:
        print("\n✅ All validations passed!")

    return 0 if suite.failed == 0 else 1


if __name__ == "__main__":
    exit(main())
