"""
Performance Validation and Testing Framework for Ariadne

This module provides comprehensive validation and testing capabilities
for quantum simulation performance, ensuring accuracy, reliability,
and consistency across all backends and optimization strategies.
"""

from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit


@dataclass
class ValidationResult:
    """Result of a validation test."""

    test_name: str
    passed: bool
    score: float  # 0-1 where 1 is perfect
    details: dict[str, Any]
    error_message: str | None = None
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class PerformanceMetrics:
    """Performance metrics for validation."""

    execution_time: float
    memory_usage_mb: float
    accuracy_score: float
    stability_score: float
    throughput_circuits_per_second: float
    scalability_factor: float


class ValidationTest(ABC):
    """Abstract base class for validation tests."""

    @abstractmethod
    def run_test(self, backend_name: str, **kwargs) -> ValidationResult:
        """Run the validation test."""
        pass

    @abstractmethod
    def get_test_name(self) -> str:
        """Get the name of this test."""
        pass


class AccuracyValidationTest(ValidationTest):
    """Test simulation accuracy against known reference results."""

    def get_test_name(self) -> str:
        return "accuracy_validation"

    def run_test(self, backend_name: str, **kwargs) -> ValidationResult:
        """Test accuracy by comparing with exact results."""

        try:
            from ..backends.universal_interface import get_backend

            backend = get_backend(backend_name)

            if not backend:
                return ValidationResult(
                    test_name=self.get_test_name(),
                    passed=False,
                    score=0.0,
                    details={},
                    error_message=f"Backend {backend_name} not available",
                )

            # Test circuits with known exact results
            test_cases = self._create_test_circuits()
            accuracy_scores = []

            for circuit, expected_state in test_cases:
                if not backend.can_simulate(circuit)[0]:
                    continue

                # Get simulation results
                counts = backend.simulate(circuit, shots=10000)

                # Calculate fidelity with expected state
                fidelity = self._calculate_fidelity(counts, expected_state, circuit.num_qubits)
                accuracy_scores.append(fidelity)

            if not accuracy_scores:
                return ValidationResult(
                    test_name=self.get_test_name(),
                    passed=False,
                    score=0.0,
                    details={},
                    error_message="No test circuits could be simulated",
                )

            avg_accuracy = np.mean(accuracy_scores)
            passed = avg_accuracy >= 0.95  # 95% fidelity threshold

            return ValidationResult(
                test_name=self.get_test_name(),
                passed=passed,
                score=avg_accuracy,
                details={
                    "individual_scores": accuracy_scores,
                    "num_tests": len(accuracy_scores),
                    "threshold": 0.95,
                },
            )

        except Exception as e:
            return ValidationResult(
                test_name=self.get_test_name(),
                passed=False,
                score=0.0,
                details={},
                error_message=str(e),
            )

    def _create_test_circuits(self) -> list[tuple[QuantumCircuit, np.ndarray]]:
        """Create test circuits with known exact results."""
        test_cases = []

        # Test 1: |0⟩ state
        circuit = QuantumCircuit(2)
        circuit.measure_all()
        expected_state = np.array([1, 0, 0, 0], dtype=complex)
        test_cases.append((circuit, expected_state))

        # Test 2: |+⟩ state (superposition)
        circuit = QuantumCircuit(1)
        circuit.h(0)
        circuit.measure_all()
        expected_state = np.array([1, 1], dtype=complex) / np.sqrt(2)
        test_cases.append((circuit, expected_state))

        # Test 3: Bell state
        circuit = QuantumCircuit(2)
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.measure_all()
        expected_state = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
        test_cases.append((circuit, expected_state))

        # Test 4: GHZ state
        circuit = QuantumCircuit(3)
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.cx(1, 2)
        circuit.measure_all()
        expected_state = np.zeros(8, dtype=complex)
        expected_state[0] = 1 / np.sqrt(2)  # |000⟩
        expected_state[7] = 1 / np.sqrt(2)  # |111⟩
        test_cases.append((circuit, expected_state))

        return test_cases

    def _calculate_fidelity(self, counts: dict[str, int], expected_state: np.ndarray, num_qubits: int) -> float:
        """Calculate fidelity between measurement counts and expected state."""
        # Convert counts to probability distribution
        total_shots = sum(counts.values())
        if total_shots == 0:
            return 0.0

        measured_probs = np.zeros(2**num_qubits)
        for bitstring, count in counts.items():
            # Convert bitstring to index (Qiskit bit ordering)
            index = int(bitstring[::-1], 2)  # Reverse for Qiskit convention
            measured_probs[index] = count / total_shots

        # Calculate expected probabilities
        expected_probs = np.abs(expected_state) ** 2

        # Fidelity between probability distributions
        fidelity = np.sum(np.sqrt(measured_probs * expected_probs))
        return fidelity


class PerformanceStabilityTest(ValidationTest):
    """Test performance stability across multiple runs."""

    def get_test_name(self) -> str:
        return "performance_stability"

    def run_test(self, backend_name: str, num_runs: int = 10, **kwargs) -> ValidationResult:
        """Test performance stability."""

        try:
            from ..backends.universal_interface import get_backend

            backend = get_backend(backend_name)

            if not backend:
                return ValidationResult(
                    test_name=self.get_test_name(),
                    passed=False,
                    score=0.0,
                    details={},
                    error_message=f"Backend {backend_name} not available",
                )

            # Create test circuit
            circuit = self._create_test_circuit()

            if not backend.can_simulate(circuit)[0]:
                return ValidationResult(
                    test_name=self.get_test_name(),
                    passed=False,
                    score=0.0,
                    details={},
                    error_message="Backend cannot simulate test circuit",
                )

            # Run multiple times and measure consistency
            execution_times = []
            results_consistency = []

            reference_counts = None

            for _i in range(num_runs):
                start_time = time.time()
                counts = backend.simulate(circuit, shots=1000)
                execution_time = time.time() - start_time

                execution_times.append(execution_time)

                # Check result consistency
                if reference_counts is None:
                    reference_counts = counts
                else:
                    consistency = self._calculate_consistency(counts, reference_counts)
                    results_consistency.append(consistency)

            # Calculate stability metrics
            time_stability = 1.0 - (np.std(execution_times) / np.mean(execution_times))
            result_stability = np.mean(results_consistency) if results_consistency else 1.0

            overall_stability = (time_stability + result_stability) / 2
            passed = overall_stability >= 0.8  # 80% stability threshold

            return ValidationResult(
                test_name=self.get_test_name(),
                passed=passed,
                score=overall_stability,
                details={
                    "execution_times": execution_times,
                    "time_stability": time_stability,
                    "result_stability": result_stability,
                    "num_runs": num_runs,
                },
            )

        except Exception as e:
            return ValidationResult(
                test_name=self.get_test_name(),
                passed=False,
                score=0.0,
                details={},
                error_message=str(e),
            )

    def _create_test_circuit(self) -> QuantumCircuit:
        """Create circuit for stability testing."""
        circuit = QuantumCircuit(4)
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.ry(np.pi / 4, 2)
        circuit.cx(1, 2)
        circuit.rz(np.pi / 3, 3)
        circuit.cx(2, 3)
        circuit.measure_all()
        return circuit

    def _calculate_consistency(self, counts1: dict[str, int], counts2: dict[str, int]) -> float:
        """Calculate consistency between two measurement results."""
        total1 = sum(counts1.values())
        total2 = sum(counts2.values())

        if total1 == 0 or total2 == 0:
            return 0.0

        # Convert to probability distributions
        all_outcomes = set(counts1.keys()) | set(counts2.keys())

        consistency = 0.0
        for outcome in all_outcomes:
            p1 = counts1.get(outcome, 0) / total1
            p2 = counts2.get(outcome, 0) / total2
            consistency += np.sqrt(p1 * p2)  # Bhattacharyya coefficient

        return consistency


class ScalabilityTest(ValidationTest):
    """Test scalability across different circuit sizes."""

    def get_test_name(self) -> str:
        return "scalability"

    def run_test(self, backend_name: str, max_qubits: int = 20, **kwargs) -> ValidationResult:
        """Test scalability performance."""

        try:
            from ..backends.universal_interface import get_backend

            backend = get_backend(backend_name)

            if not backend:
                return ValidationResult(
                    test_name=self.get_test_name(),
                    passed=False,
                    score=0.0,
                    details={},
                    error_message=f"Backend {backend_name} not available",
                )

            # Test across different qubit counts
            qubit_counts = [4, 8, 12, 16, 20]
            qubit_counts = [q for q in qubit_counts if q <= max_qubits]

            execution_times = []
            memory_usage = []
            success_qubits = []

            for num_qubits in qubit_counts:
                circuit = self._create_scalability_circuit(num_qubits)

                can_sim, reason = backend.can_simulate(circuit)
                if not can_sim:
                    break

                try:
                    start_time = time.time()
                    backend.simulate(circuit, shots=100)  # Fewer shots for speed
                    execution_time = time.time() - start_time

                    execution_times.append(execution_time)
                    success_qubits.append(num_qubits)

                    # Estimate memory usage
                    resources = backend.estimate_resources(circuit)
                    memory_usage.append(resources.get("memory_mb", 0))

                except Exception:
                    break

            if len(success_qubits) < 2:
                return ValidationResult(
                    test_name=self.get_test_name(),
                    passed=False,
                    score=0.0,
                    details={},
                    error_message="Insufficient successful simulations for scalability analysis",
                )

            # Analyze scaling behavior
            scalability_score = self._analyze_scaling(success_qubits, execution_times)
            passed = scalability_score >= 0.5 and len(success_qubits) >= 3

            return ValidationResult(
                test_name=self.get_test_name(),
                passed=passed,
                score=scalability_score,
                details={
                    "successful_qubits": success_qubits,
                    "execution_times": execution_times,
                    "memory_usage": memory_usage,
                    "max_qubits_tested": max(success_qubits) if success_qubits else 0,
                },
            )

        except Exception as e:
            return ValidationResult(
                test_name=self.get_test_name(),
                passed=False,
                score=0.0,
                details={},
                error_message=str(e),
            )

    def _create_scalability_circuit(self, num_qubits: int) -> QuantumCircuit:
        """Create circuit for scalability testing."""
        circuit = QuantumCircuit(num_qubits)

        # Add layers of gates for realistic complexity
        for _layer in range(3):
            # Single-qubit gates
            for i in range(num_qubits):
                circuit.ry(np.pi / 4, i)

            # Two-qubit gates
            for i in range(num_qubits - 1):
                circuit.cx(i, i + 1)

        circuit.measure_all()
        return circuit

    def _analyze_scaling(self, qubits: list[int], times: list[float]) -> float:
        """Analyze scaling behavior and return score."""
        if len(qubits) < 2:
            return 0.0

        # Calculate scaling factor
        # Good scaling: close to polynomial (< 2^n)
        # Bad scaling: exponential (~ 2^n or worse)

        scaling_factors = []
        for i in range(1, len(qubits)):
            qubit_ratio = qubits[i] / qubits[i - 1]
            time_ratio = times[i] / times[i - 1]

            # Ideal: time_ratio should be polynomial in qubit_ratio
            # Calculate effective scaling exponent
            if qubit_ratio > 1 and time_ratio > 1:
                scaling_exponent = np.log(time_ratio) / np.log(qubit_ratio)
                scaling_factors.append(scaling_exponent)

        if not scaling_factors:
            return 0.5

        avg_scaling = np.mean(scaling_factors)

        # Score based on scaling behavior
        # Linear scaling (exponent ~1): score = 1.0
        # Quadratic scaling (exponent ~2): score = 0.8
        # Exponential scaling (exponent >3): score < 0.5

        if avg_scaling <= 1.5:
            score = 1.0
        elif avg_scaling <= 2.5:
            score = 0.8
        elif avg_scaling <= 4.0:
            score = 0.6
        else:
            score = 0.3

        return score


class ErrorHandlingTest(ValidationTest):
    """Test error handling and robustness."""

    def get_test_name(self) -> str:
        return "error_handling"

    def run_test(self, backend_name: str, **kwargs) -> ValidationResult:
        """Test error handling capabilities."""

        try:
            from ..backends.universal_interface import get_backend

            backend = get_backend(backend_name)

            if not backend:
                return ValidationResult(
                    test_name=self.get_test_name(),
                    passed=False,
                    score=0.0,
                    details={},
                    error_message=f"Backend {backend_name} not available",
                )

            # Test various error conditions
            error_tests = self._create_error_test_cases()

            passed_tests = 0
            total_tests = len(error_tests)
            test_details = {}

            for test_name, circuit, expected_behavior in error_tests:
                try:
                    # Check if backend properly reports capability
                    can_sim, reason = backend.can_simulate(circuit)

                    if expected_behavior == "should_fail":
                        if not can_sim:
                            passed_tests += 1
                            test_details[test_name] = "PASS - Correctly rejected"
                        else:
                            test_details[test_name] = "FAIL - Should have been rejected"

                    elif expected_behavior == "should_succeed":
                        if can_sim:
                            # Try actual simulation
                            backend.simulate(circuit, shots=100)
                            passed_tests += 1
                            test_details[test_name] = "PASS - Successful simulation"
                        else:
                            test_details[test_name] = f"FAIL - Rejected: {reason}"

                except Exception as e:
                    if expected_behavior == "should_fail":
                        passed_tests += 1
                        test_details[test_name] = f"PASS - Properly threw exception: {type(e).__name__}"
                    else:
                        test_details[test_name] = f"FAIL - Unexpected exception: {e}"

            score = passed_tests / total_tests if total_tests > 0 else 0.0
            passed = score >= 0.8

            return ValidationResult(
                test_name=self.get_test_name(),
                passed=passed,
                score=score,
                details={
                    "test_results": test_details,
                    "passed_tests": passed_tests,
                    "total_tests": total_tests,
                },
            )

        except Exception as e:
            return ValidationResult(
                test_name=self.get_test_name(),
                passed=False,
                score=0.0,
                details={},
                error_message=str(e),
            )

    def _create_error_test_cases(self) -> list[tuple[str, QuantumCircuit, str]]:
        """Create test cases for error handling."""
        test_cases = []

        # Test 1: Empty circuit
        circuit = QuantumCircuit(1)
        test_cases.append(("empty_circuit", circuit, "should_succeed"))

        # Test 2: Very large circuit (should be rejected by most backends)
        large_circuit = QuantumCircuit(50)
        for i in range(50):
            large_circuit.h(i)
        large_circuit.measure_all()
        test_cases.append(("large_circuit", large_circuit, "should_fail"))

        # Test 3: Normal circuit (should succeed)
        normal_circuit = QuantumCircuit(3)
        normal_circuit.h(0)
        normal_circuit.cx(0, 1)
        normal_circuit.measure_all()
        test_cases.append(("normal_circuit", normal_circuit, "should_succeed"))

        # Test 4: Circuit with no measurements
        no_measure_circuit = QuantumCircuit(2)
        no_measure_circuit.h(0)
        no_measure_circuit.cx(0, 1)
        test_cases.append(("no_measurements", no_measure_circuit, "should_succeed"))

        return test_cases


class PerformanceValidationFramework:
    """Main framework for performance validation and testing."""

    def __init__(self, output_dir: str | None = None):
        """Initialize validation framework."""
        self.output_dir = Path(output_dir) if output_dir else Path("validation_results")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Register validation tests
        self.tests = {
            "accuracy": AccuracyValidationTest(),
            "stability": PerformanceStabilityTest(),
            "scalability": ScalabilityTest(),
            "error_handling": ErrorHandlingTest(),
        }

    def run_validation_suite(
        self, backend_names: list[str] | None = None, test_names: list[str] | None = None
    ) -> dict[str, dict[str, ValidationResult]]:
        """Run validation suite on specified backends."""

        # Get available backends if not specified
        if backend_names is None:
            try:
                from ..backends.universal_interface import list_backends

                backend_names = list_backends()
            except Exception:
                backend_names = ["qiskit"]

        # Use all tests if not specified
        if test_names is None:
            test_names = list(self.tests.keys())

        print("🧪 Running validation suite")
        print(f"🔧 Backends: {', '.join(backend_names)}")
        print(f"📋 Tests: {', '.join(test_names)}")
        print()

        all_results = {}

        for backend_name in backend_names:
            print(f"Testing {backend_name}...")
            backend_results = {}

            for test_name in test_names:
                if test_name not in self.tests:
                    print(f"  ⚠️ Unknown test: {test_name}")
                    continue

                print(f"  Running {test_name}...", end=" ")

                test = self.tests[test_name]
                result = test.run_test(backend_name)
                backend_results[test_name] = result

                if result.passed:
                    print(f"✅ {result.score:.2f}")
                else:
                    print(f"❌ {result.score:.2f}")
                    if result.error_message:
                        print(f"    Error: {result.error_message}")

            all_results[backend_name] = backend_results
            print()

        # Save results
        self._save_validation_results(all_results)

        return all_results

    def _save_validation_results(self, results: dict[str, dict[str, ValidationResult]]):
        """Save validation results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"validation_results_{timestamp}.json"
        filepath = self.output_dir / filename

        # Convert results to serializable format
        serializable_results = {}
        for backend_name, backend_results in results.items():
            serializable_results[backend_name] = {}
            for test_name, result in backend_results.items():
                serializable_results[backend_name][test_name] = asdict(result)

        with open(filepath, "w") as f:
            json.dump(serializable_results, f, indent=2)

        print(f"💾 Validation results saved to: {filepath}")

    def generate_validation_report(self, results: dict[str, dict[str, ValidationResult]]) -> str:
        """Generate comprehensive validation report."""

        report_lines = []
        report_lines.append("# Ariadne Performance Validation Report")
        report_lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")

        # Overall summary
        total_tests = sum(len(backend_results) for backend_results in results.values())
        passed_tests = sum(
            sum(1 for result in backend_results.values() if result.passed) for backend_results in results.values()
        )

        report_lines.append("## Summary")
        report_lines.append(f"- **Total Tests**: {total_tests}")
        report_lines.append(f"- **Passed**: {passed_tests} ({passed_tests / total_tests * 100:.1f}%)")
        report_lines.append(f"- **Failed**: {total_tests - passed_tests}")
        report_lines.append("")

        # Backend summary
        report_lines.append("## Backend Validation Summary")
        report_lines.append("| Backend | Accuracy | Stability | Scalability | Error Handling | Overall |")
        report_lines.append("|---------|----------|-----------|-------------|----------------|---------|")

        for backend_name, backend_results in results.items():
            scores = {}
            for test_name, result in backend_results.items():
                scores[test_name] = result.score if result.passed else 0.0

            overall_score = np.mean(list(scores.values())) if scores else 0.0

            report_lines.append(
                f"| {backend_name} | "
                f"{scores.get('accuracy', 0.0):.2f} | "
                f"{scores.get('stability', 0.0):.2f} | "
                f"{scores.get('scalability', 0.0):.2f} | "
                f"{scores.get('error_handling', 0.0):.2f} | "
                f"{overall_score:.2f} |"
            )

        report_lines.append("")

        # Detailed test results
        for backend_name, backend_results in results.items():
            report_lines.append(f"## {backend_name} Detailed Results")

            for test_name, result in backend_results.items():
                status = "✅ PASSED" if result.passed else "❌ FAILED"
                report_lines.append(f"### {test_name} - {status} (Score: {result.score:.2f})")

                if result.error_message:
                    report_lines.append(f"**Error**: {result.error_message}")

                # Add test-specific details
                if test_name == "accuracy" and "individual_scores" in result.details:
                    scores = result.details["individual_scores"]
                    report_lines.append(f"- Individual fidelities: {[f'{s:.3f}' for s in scores]}")

                elif test_name == "stability" and "execution_times" in result.details:
                    times = result.details["execution_times"]
                    report_lines.append(
                        f"- Execution time stability: {np.std(times) / np.mean(times) * 100:.1f}% variation"
                    )

                elif test_name == "scalability" and "successful_qubits" in result.details:
                    max_qubits = result.details.get("max_qubits_tested", 0)
                    report_lines.append(f"- Maximum qubits tested: {max_qubits}")

                report_lines.append("")

        report_lines.append("---")
        report_lines.append("*Generated by Ariadne Performance Validation Framework*")

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"validation_report_{timestamp}.md"
        report_filepath = self.output_dir / report_filename

        with open(report_filepath, "w") as f:
            f.write("\n".join(report_lines))

        print(f"📋 Validation report saved to: {report_filepath}")

        return "\n".join(report_lines)


def run_quick_validation() -> dict[str, dict[str, ValidationResult]]:
    """Run quick validation on all available backends."""
    framework = PerformanceValidationFramework()
    return framework.run_validation_suite(test_names=["accuracy", "error_handling"])


def run_full_validation() -> dict[str, dict[str, ValidationResult]]:
    """Run full validation suite."""
    framework = PerformanceValidationFramework()
    return framework.run_validation_suite()


def validate_backend(backend_name: str) -> dict[str, ValidationResult]:
    """Validate a specific backend."""
    framework = PerformanceValidationFramework()
    results = framework.run_validation_suite(backend_names=[backend_name])
    return results.get(backend_name, {})
