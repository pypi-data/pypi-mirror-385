"""
Cross-Platform Performance Comparison Tools for Ariadne.

This module provides comprehensive tools for comparing quantum backend performance
across different platforms, architectures, and configurations to optimize
quantum circuit routing and backend selection.
"""

import importlib.util
import json
import logging
import platform
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, cast

import numpy as np
import psutil
from qiskit import QuantumCircuit

logger = logging.getLogger(__name__)

SummaryStats = dict[str, dict[str, float | int]]


class PlatformType(Enum):
    """Platform types for comparison."""

    MACOS_APPLE_SILICON = "macos_apple_silicon"
    MACOS_INTEL = "macos_intel"
    LINUX_X86 = "linux_x86"
    LINUX_ARM = "linux_arm"
    WINDOWS_X86 = "windows_x86"
    CLOUD_AWS = "cloud_aws"
    CLOUD_GCP = "cloud_gcp"
    CLOUD_AZURE = "cloud_azure"


class BackendType(Enum):
    """Backend types for comparison."""

    CPU_NUMPY = "cpu_numpy"
    METAL_APPLE = "metal_apple"
    CUDA_NVIDIA = "cuda_nvidia"
    OPENCL = "opencl"
    SIMULATOR_AER = "simulator_aer"
    REAL_HARDWARE = "real_hardware"


@dataclass
class SystemInfo:
    """System information for performance context."""

    platform_type: PlatformType
    cpu_count: int
    cpu_frequency: float
    memory_total: int
    memory_available: int
    gpu_info: dict[str, Any] = field(default_factory=dict)
    python_version: str = ""
    os_version: str = ""
    architecture: str = ""

    def __post_init__(self) -> None:
        if not self.python_version:
            self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        if not self.os_version:
            self.os_version = platform.platform()
        if not self.architecture:
            self.architecture = platform.machine()


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark tests."""

    qubit_ranges: list[int] = field(default_factory=lambda: [5, 10, 15, 20, 25])
    circuit_depths: list[int] = field(default_factory=lambda: [10, 50, 100, 200])
    shot_counts: list[int] = field(default_factory=lambda: [100, 1000, 10000])
    iterations_per_test: int = 3
    warmup_iterations: int = 1
    timeout_seconds: float = 300.0


@dataclass
class PerformanceResult:
    """Single performance measurement result."""

    backend_type: BackendType
    system_info: SystemInfo
    circuit_qubits: int
    circuit_depth: int
    shots: int
    execution_time: float
    memory_peak: int
    throughput: float  # shots/second
    accuracy: float | None = None
    error_rate: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class ComparisonReport:
    """Comprehensive comparison report."""

    title: str
    results: list[PerformanceResult]
    summary_stats: SummaryStats = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)
    generated_at: float = field(default_factory=time.time)


class SystemProfiler:
    """Profiles system capabilities and characteristics."""

    @staticmethod
    def get_system_info() -> SystemInfo:
        """Get comprehensive system information."""
        # Detect platform type
        platform_type = SystemProfiler._detect_platform_type()

        # Get CPU information
        cpu_count = psutil.cpu_count(logical=True) or 1

        # Handle CPU frequency gracefully on macOS
        cpu_frequency = 0.0
        try:
            cpu_freq = psutil.cpu_freq()
            cpu_frequency = cpu_freq.current if cpu_freq else 0.0
        except (FileNotFoundError, AttributeError):
            # Fallback for macOS or systems without cpu_freq
            cpu_frequency = 0.0

        # Get memory information
        memory = psutil.virtual_memory()
        memory_total = memory.total
        memory_available = memory.available

        # Get GPU information
        gpu_info = SystemProfiler._get_gpu_info()

        return SystemInfo(
            platform_type=platform_type,
            cpu_count=cpu_count,
            cpu_frequency=cpu_frequency,
            memory_total=memory_total,
            memory_available=memory_available,
            gpu_info=gpu_info,
        )

    @staticmethod
    def _detect_platform_type() -> PlatformType:
        """Detect the current platform type."""
        system = platform.system().lower()
        machine = platform.machine().lower()

        if system == "darwin":  # macOS
            if "arm" in machine or "m1" in machine or "m2" in machine:
                return PlatformType.MACOS_APPLE_SILICON
            else:
                return PlatformType.MACOS_INTEL
        elif system == "linux":
            if "arm" in machine or "aarch64" in machine:
                return PlatformType.LINUX_ARM
            else:
                return PlatformType.LINUX_X86
        elif system == "windows":
            return PlatformType.WINDOWS_X86
        else:
            # Default to Linux x86
            return PlatformType.LINUX_X86

    @staticmethod
    def _get_gpu_info() -> dict[str, Any]:
        """Get GPU information if available."""
        gpu_info: dict[str, Any] = {"available": False}

        try:
            # Try NVIDIA GPU detection
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=name,memory.total,driver_version",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                nvidia_gpus = []

                for line in lines:
                    parts = line.split(", ")
                    if len(parts) >= 3:
                        nvidia_gpus.append(
                            {
                                "name": parts[0],
                                "memory_mb": int(parts[1]),
                                "driver_version": parts[2],
                            }
                        )

                if nvidia_gpus:
                    gpu_info["nvidia"] = nvidia_gpus
                    gpu_info["available"] = True

        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            pass

        # Try Apple Metal detection on macOS
        if platform.system() == "Darwin" and importlib.util.find_spec("Metal") is not None:
            gpu_info["metal"] = {"available": True}
            gpu_info["available"] = True

        try:
            # Try OpenCL detection
            import pyopencl as cl

            platforms = cl.get_platforms()
            opencl_devices = []

            for cl_platform in platforms:
                for device in cl_platform.get_devices():
                    opencl_devices.append(
                        {
                            "name": device.name,
                            "type": str(device.type),
                            "memory_mb": device.global_mem_size // (1024 * 1024),
                        }
                    )

            if opencl_devices:
                gpu_info["opencl"] = opencl_devices
                gpu_info["available"] = True

        except ImportError:
            pass

        return gpu_info


class BenchmarkRunner:
    """Runs performance benchmarks across different backends."""

    def __init__(self, config: BenchmarkConfig | None = None):
        self.config = config or BenchmarkConfig()
        self.system_info = SystemProfiler.get_system_info()

        # Available backends detection
        self.available_backends = self._detect_available_backends()

        logger.info(f"BenchmarkRunner initialized on {self.system_info.platform_type.value}")
        logger.info(f"Available backends: {[b.value for b in self.available_backends]}")

    def _detect_available_backends(self) -> list[BackendType]:
        """Detect which backends are available on this system."""
        available = [BackendType.CPU_NUMPY]  # Always available

        # Check for Metal (Apple Silicon)
        if (
            self.system_info.platform_type == PlatformType.MACOS_APPLE_SILICON
            and importlib.util.find_spec("Metal") is not None
        ):
            available.append(BackendType.METAL_APPLE)

        # Check for CUDA
        if self.system_info.gpu_info.get("nvidia") and importlib.util.find_spec("cupy") is not None:
            available.append(BackendType.CUDA_NVIDIA)

        # Check for OpenCL
        if self.system_info.gpu_info.get("opencl") and importlib.util.find_spec("pyopencl") is not None:
            available.append(BackendType.OPENCL)

        # Check for Qiskit Aer
        if importlib.util.find_spec("qiskit_aer") is not None:
            available.append(BackendType.SIMULATOR_AER)

        return available

    def run_comprehensive_benchmark(
        self,
        backends: list[BackendType] | None = None,
        save_results: bool = True,
        results_file: str | None = None,
    ) -> ComparisonReport:
        """Run comprehensive benchmark across all specified backends."""
        if backends is None:
            backends = self.available_backends

        logger.info(f"Starting comprehensive benchmark with {len(backends)} backends")

        all_results = []

        for backend in backends:
            if backend not in self.available_backends:
                logger.warning(f"Backend {backend.value} not available, skipping")
                continue

            logger.info(f"Benchmarking backend: {backend.value}")
            backend_results = self._benchmark_backend(backend)
            all_results.extend(backend_results)

        # Generate report
        report = self._generate_comparison_report(all_results, backends)

        if save_results:
            filename = results_file or f"benchmark_results_{int(time.time())}.json"
            self._save_results(report, filename)

        return report

    def _benchmark_backend(self, backend: BackendType) -> list[PerformanceResult]:
        """Benchmark a specific backend across all test configurations."""
        results = []

        for qubits in self.config.qubit_ranges:
            for depth in self.config.circuit_depths:
                for shots in self.config.shot_counts:
                    logger.debug(f"Testing {backend.value}: {qubits}q, depth {depth}, {shots} shots")

                    try:
                        result = self._run_single_benchmark(backend, qubits, depth, shots)
                        if result:
                            results.append(result)
                    except Exception as e:
                        logger.error(f"Benchmark failed for {backend.value}: {e}")
                        continue

        return results

    def _run_single_benchmark(
        self, backend: BackendType, qubits: int, depth: int, shots: int
    ) -> PerformanceResult | None:
        """Run a single benchmark test."""
        # Generate test circuit
        circuit = self._generate_test_circuit(qubits, depth)

        # Warmup runs
        for _ in range(self.config.warmup_iterations):
            try:
                self._execute_circuit(backend, circuit, shots)
            except Exception:
                pass  # Ignore warmup failures

        # Measured runs
        execution_times = []
        memory_peaks = []

        for iteration in range(self.config.iterations_per_test):
            try:
                start_memory = psutil.Process().memory_info().rss
                start_time = time.perf_counter()

                self._execute_circuit(backend, circuit, shots)

                end_time = time.perf_counter()
                end_memory = psutil.Process().memory_info().rss

                execution_time = end_time - start_time
                memory_peak = end_memory - start_memory

                execution_times.append(execution_time)
                memory_peaks.append(memory_peak)

                # Check for timeout
                if execution_time > self.config.timeout_seconds:
                    logger.warning(f"Benchmark timed out for {backend.value}")
                    break

            except Exception as e:
                logger.warning(f"Iteration {iteration} failed for {backend.value}: {e}")
                continue

        if not execution_times:
            return None

        # Calculate statistics
        avg_execution_time = statistics.mean(execution_times)
        avg_memory_peak = statistics.mean(memory_peaks)
        throughput = shots / avg_execution_time

        return PerformanceResult(
            backend_type=backend,
            system_info=self.system_info,
            circuit_qubits=qubits,
            circuit_depth=depth,
            shots=shots,
            execution_time=avg_execution_time,
            memory_peak=int(avg_memory_peak),
            throughput=throughput,
            metadata={
                "execution_times": execution_times,
                "memory_peaks": memory_peaks,
                "iterations": len(execution_times),
            },
        )

    def _generate_test_circuit(self, qubits: int, depth: int) -> QuantumCircuit:
        """Generate a standardized test circuit."""
        # Use a mix of single and two-qubit gates for realistic testing
        circuit = QuantumCircuit(qubits, qubits)

        # Add some structure to make it more realistic than pure random
        np.random.seed(42)  # Deterministic for comparison

        for _layer in range(depth):
            # Random single-qubit gates
            for qubit in range(qubits):
                if np.random.random() < 0.7:  # 70% chance of single-qubit gate
                    gate_type = np.random.choice(["h", "x", "y", "z", "rx", "ry", "rz"])

                    if gate_type == "h":
                        circuit.h(qubit)
                    elif gate_type == "x":
                        circuit.x(qubit)
                    elif gate_type == "y":
                        circuit.y(qubit)
                    elif gate_type == "z":
                        circuit.z(qubit)
                    elif gate_type == "rx":
                        circuit.rx(np.random.uniform(0, 2 * np.pi), qubit)
                    elif gate_type == "ry":
                        circuit.ry(np.random.uniform(0, 2 * np.pi), qubit)
                    elif gate_type == "rz":
                        circuit.rz(np.random.uniform(0, 2 * np.pi), qubit)

            # Random two-qubit gates
            available_qubits = list(range(qubits))
            np.random.shuffle(available_qubits)

            for i in range(0, len(available_qubits) - 1, 2):
                if np.random.random() < 0.3:  # 30% chance of two-qubit gate
                    control = available_qubits[i]
                    target = available_qubits[i + 1]

                    gate_type = np.random.choice(["cx", "cz", "cy"])
                    if gate_type == "cx":
                        circuit.cx(control, target)
                    elif gate_type == "cz":
                        circuit.cz(control, target)
                    elif gate_type == "cy":
                        circuit.cy(control, target)

        # Add measurements
        circuit.measure_all()

        return circuit

    def _execute_circuit(self, backend: BackendType, circuit: QuantumCircuit, shots: int) -> dict[str, Any]:
        """Execute circuit on specified backend."""
        if backend == BackendType.CPU_NUMPY:
            return self._execute_cpu_numpy(circuit, shots)
        elif backend == BackendType.METAL_APPLE:
            return self._execute_metal_apple(circuit, shots)
        elif backend == BackendType.CUDA_NVIDIA:
            return self._execute_cuda_nvidia(circuit, shots)
        elif backend == BackendType.SIMULATOR_AER:
            return self._execute_aer_simulator(circuit, shots)
        else:
            raise NotImplementedError(f"Backend {backend.value} not implemented")

    def _execute_cpu_numpy(self, circuit: QuantumCircuit, shots: int) -> dict[str, Any]:
        """Execute circuit using CPU NumPy backend."""
        # Use Ariadne's built-in CPU backend
        from ariadne.backends.cpu_backend import CPUBackend

        backend = CPUBackend()
        result = backend.simulate(circuit, shots=shots)

        return {"counts": result}

    def _execute_metal_apple(self, circuit: QuantumCircuit, shots: int) -> dict[str, Any]:
        """Execute circuit using Apple Metal backend."""
        try:
            from ariadne.backends.metal_backend import MetalBackend

            backend = MetalBackend()
            result = backend.simulate(circuit, shots=shots)

            return {"counts": result}
        except ImportError as err:
            raise RuntimeError("Metal backend not available") from err

    def _execute_cuda_nvidia(self, circuit: QuantumCircuit, shots: int) -> dict[str, Any]:
        """Execute circuit using CUDA backend."""
        try:
            from ariadne.backends.cuda_backend import CUDABackend

            backend = CUDABackend()
            result = backend.simulate(circuit, shots=shots)

            return {"counts": result}
        except ImportError as err:
            raise RuntimeError("CUDA backend not available") from err

    def _execute_aer_simulator(self, circuit: QuantumCircuit, shots: int) -> dict[str, Any]:
        """Execute circuit using Qiskit Aer simulator."""
        try:
            from qiskit import execute, transpile
            from qiskit_aer import AerSimulator

            simulator = AerSimulator()
            transpiled = transpile(circuit, simulator)
            job = execute(transpiled, simulator, shots=shots)
            result = job.result()

            return {"counts": result.get_counts()}
        except ImportError as err:
            raise RuntimeError("Aer simulator not available") from err

    def _generate_comparison_report(
        self, results: list[PerformanceResult], backends: list[BackendType]
    ) -> ComparisonReport:
        """Generate comprehensive comparison report."""

        # Group results by backend
        backend_results: dict[BackendType, list[PerformanceResult]] = {backend: [] for backend in backends}
        for result in results:
            if result.backend_type in backend_results:
                backend_results[result.backend_type].append(result)

        # Calculate summary statistics
        summary_stats: SummaryStats = {}
        recommendations = []

        for backend, backend_results_list in backend_results.items():
            if not backend_results_list:
                continue

            execution_times = [r.execution_time for r in backend_results_list]
            throughputs = [r.throughput for r in backend_results_list]
            memory_peaks = [r.memory_peak for r in backend_results_list]

            summary_stats[backend.value] = {
                "avg_execution_time": statistics.mean(execution_times),
                "min_execution_time": min(execution_times),
                "max_execution_time": max(execution_times),
                "avg_throughput": statistics.mean(throughputs),
                "max_throughput": max(throughputs),
                "avg_memory_peak": statistics.mean(memory_peaks),
                "total_tests": len(backend_results_list),
            }

        # Generate recommendations
        if summary_stats:
            # Find fastest backend
            fastest_backend = min(summary_stats.keys(), key=lambda k: summary_stats[k]["avg_execution_time"])
            recommendations.append(f"Fastest overall backend: {fastest_backend}")

            # Find highest throughput backend
            highest_throughput = max(summary_stats.keys(), key=lambda k: summary_stats[k]["max_throughput"])
            recommendations.append(f"Highest throughput backend: {highest_throughput}")

            # Find most memory efficient backend
            most_efficient = min(summary_stats.keys(), key=lambda k: summary_stats[k]["avg_memory_peak"])
            recommendations.append(f"Most memory efficient backend: {most_efficient}")

        report = ComparisonReport(
            title=f"Cross-Platform Performance Comparison - {self.system_info.platform_type.value}",
            results=results,
            summary_stats=summary_stats,
            recommendations=recommendations,
        )

        return report

    def _save_results(self, report: ComparisonReport, filename: str) -> None:
        """Save benchmark results to file."""
        # Convert dataclasses to dicts for JSON serialization
        report_dict = {
            "title": report.title,
            "generated_at": report.generated_at,
            "system_info": {
                "platform_type": report.results[0].system_info.platform_type.value if report.results else "unknown",
                "cpu_count": report.results[0].system_info.cpu_count if report.results else 0,
                "memory_total": report.results[0].system_info.memory_total if report.results else 0,
                "gpu_info": report.results[0].system_info.gpu_info if report.results else {},
            },
            "summary_stats": report.summary_stats,
            "recommendations": report.recommendations,
            "results": [
                {
                    "backend_type": result.backend_type.value,
                    "circuit_qubits": result.circuit_qubits,
                    "circuit_depth": result.circuit_depth,
                    "shots": result.shots,
                    "execution_time": result.execution_time,
                    "memory_peak": result.memory_peak,
                    "throughput": result.throughput,
                    "timestamp": result.timestamp,
                    "metadata": result.metadata,
                }
                for result in report.results
            ],
        }

        with open(filename, "w") as f:
            json.dump(report_dict, f, indent=2)

        logger.info(f"Benchmark results saved to {filename}")


class PerformanceAnalyzer:
    """Analyzes and compares performance results across platforms."""

    @staticmethod
    def load_results(filename: str) -> ComparisonReport:
        """Load benchmark results from file."""
        with open(filename) as f:
            data = json.load(f)

        # Reconstruct results
        results = []
        for result_data in data["results"]:
            # Create dummy system info (would need full reconstruction in real implementation)
            system_info = SystemInfo(
                platform_type=PlatformType(data["system_info"]["platform_type"]),
                cpu_count=data["system_info"]["cpu_count"],
                cpu_frequency=0,
                memory_total=data["system_info"]["memory_total"],
                memory_available=0,
                gpu_info=data["system_info"]["gpu_info"],
            )

            result = PerformanceResult(
                backend_type=BackendType(result_data["backend_type"]),
                system_info=system_info,
                circuit_qubits=result_data["circuit_qubits"],
                circuit_depth=result_data["circuit_depth"],
                shots=result_data["shots"],
                execution_time=result_data["execution_time"],
                memory_peak=result_data["memory_peak"],
                throughput=result_data["throughput"],
                timestamp=result_data["timestamp"],
                metadata=result_data.get("metadata", {}),
            )
            results.append(result)

        return ComparisonReport(
            title=data["title"],
            results=results,
            summary_stats=data["summary_stats"],
            recommendations=data["recommendations"],
            generated_at=data["generated_at"],
        )

    @staticmethod
    def compare_platforms(reports: list[ComparisonReport]) -> dict[str, Any]:
        """Compare performance across multiple platform reports."""
        platform_comparison: dict[str, dict[str, Any]] = {}

        for report in reports:
            if not report.results:
                continue

            platform = report.results[0].system_info.platform_type.value
            platform_comparison[platform] = {
                "summary_stats": report.summary_stats,
                "recommendations": report.recommendations,
                "total_results": len(report.results),
            }

        # Find best performing platform for each metric
        best_platforms: dict[str, dict[str, float | str]] = {}

        for metric in ["avg_execution_time", "max_throughput", "avg_memory_peak"]:
            best_platform: str | None = None
            best_value: float | None = None

            for platform, data in platform_comparison.items():
                summary_stats = cast(SummaryStats, data["summary_stats"])
                if not summary_stats:
                    continue

                # Get the best backend value for this platform
                platform_values: list[float] = []
                for backend_stats in summary_stats.values():
                    if metric in backend_stats:
                        value = backend_stats[metric]
                        if isinstance(value, int | float):
                            platform_values.append(float(value))

                if platform_values:
                    if metric in {"avg_execution_time", "avg_memory_peak"}:
                        platform_best = min(platform_values)
                    else:  # max_throughput
                        platform_best = max(platform_values)

                    should_update = False
                    if best_value is None:
                        should_update = True
                    elif metric in {"avg_execution_time", "avg_memory_peak"}:
                        should_update = platform_best < best_value
                    else:  # max_throughput
                        should_update = platform_best > best_value

                    if should_update:
                        best_value = platform_best
                        best_platform = platform

            if best_platform and best_value is not None:
                best_platforms[metric] = {"platform": best_platform, "value": best_value}

        return {
            "platform_comparison": platform_comparison,
            "best_platforms": best_platforms,
            "total_platforms": len(platform_comparison),
        }

    @staticmethod
    def generate_scaling_analysis(results: list[PerformanceResult]) -> dict[str, Any]:
        """Analyze how performance scales with circuit size."""
        scaling_analysis: dict[str, Any] = {}

        # Group by backend
        backend_results: dict[str, list[PerformanceResult]] = {}
        for result in results:
            backend = result.backend_type.value
            if backend not in backend_results:
                backend_results[backend] = []
            backend_results[backend].append(result)

        for backend, backend_results_list in backend_results.items():
            # Analyze scaling with qubit count
            qubit_scaling: dict[int, list[float]] = {}
            depth_scaling: dict[int, list[float]] = {}

            for result in backend_results_list:
                qubits = result.circuit_qubits
                depth = result.circuit_depth

                if qubits not in qubit_scaling:
                    qubit_scaling[qubits] = []
                qubit_scaling[qubits].append(float(result.execution_time))

                if depth not in depth_scaling:
                    depth_scaling[depth] = []
                depth_scaling[depth].append(float(result.execution_time))

            # Calculate average execution times
            qubit_averages = {q: statistics.mean(times) for q, times in qubit_scaling.items()}
            depth_averages = {d: statistics.mean(times) for d, times in depth_scaling.items()}

            scaling_analysis[backend] = {
                "qubit_scaling": qubit_averages,
                "depth_scaling": depth_averages,
                "total_samples": len(backend_results_list),
            }

        return scaling_analysis


# Convenience functions
def run_quick_comparison(backends: list[BackendType] | None = None) -> ComparisonReport:
    """Run a quick performance comparison with default settings."""
    config = BenchmarkConfig(
        qubit_ranges=[5, 10, 15], circuit_depths=[10, 50], shot_counts=[1000], iterations_per_test=2
    )

    runner = BenchmarkRunner(config)
    return runner.run_comprehensive_benchmark(backends)


def compare_backend_performance(
    backend1: BackendType,
    backend2: BackendType,
    qubits: int = 10,
    depth: int = 50,
    shots: int = 1000,
) -> dict[str, Any]:
    """Compare two specific backends on a single circuit configuration."""
    config = BenchmarkConfig(qubit_ranges=[qubits], circuit_depths=[depth], shot_counts=[shots], iterations_per_test=3)

    runner = BenchmarkRunner(config)
    report = runner.run_comprehensive_benchmark([backend1, backend2])

    if len(report.results) >= 2:
        result1 = next(r for r in report.results if r.backend_type == backend1)
        result2 = next(r for r in report.results if r.backend_type == backend2)

        speedup = result2.execution_time / result1.execution_time
        throughput_ratio = result1.throughput / result2.throughput

        return {
            "backend1": backend1.value,
            "backend2": backend2.value,
            "result1": result1,
            "result2": result2,
            "speedup": speedup,
            "throughput_ratio": throughput_ratio,
            "winner": backend1.value if result1.execution_time < result2.execution_time else backend2.value,
        }

    return {"error": "Insufficient results for comparison"}
