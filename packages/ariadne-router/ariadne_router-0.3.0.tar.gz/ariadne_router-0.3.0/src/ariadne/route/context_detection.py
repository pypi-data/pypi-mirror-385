"""
Context Detection System for Intelligent Quantum Routing

This module analyzes user patterns, hardware capabilities, and workflow types
to provide intelligent context-aware routing decisions.
"""

from __future__ import annotations

import json
import platform
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from pathlib import Path

from qiskit import QuantumCircuit

from ..router import BackendType
from .enhanced_router import HardwareProfile, PerformancePreferences, UserContext, WorkflowType


@dataclass
class CircuitPattern:
    """Pattern analysis of quantum circuits."""

    avg_qubits: float
    avg_depth: float
    clifford_ratio: float
    common_gates: list[str]
    entanglement_complexity: float
    circuit_families: list[str]  # ['optimization', 'ml', 'cryptography', etc.]


@dataclass
class UsagePattern:
    """User usage patterns and preferences."""

    session_count: int
    total_circuits: int
    preferred_shot_counts: list[int]
    time_of_day_preferences: list[int]  # Hours when user is most active
    backend_success_rates: dict[str, float]
    average_session_length: float  # Minutes


@dataclass
class PerformanceHistory:
    """Historical performance data for learning."""

    backend_performance: dict[BackendType, list[float]]  # Execution times
    user_satisfaction_scores: dict[BackendType, list[float]]  # Implicit satisfaction
    error_rates: dict[BackendType, float]
    memory_usage_patterns: dict[BackendType, list[float]]


class CircuitFamilyDetector:
    """Detect which family of quantum algorithms a circuit belongs to."""

    # Gate patterns that indicate specific algorithm families
    ALGORITHM_SIGNATURES = {
        "optimization": {
            "gates": ["ry", "rz", "cx", "cz"],
            "patterns": ["qaoa", "vqe", "ansatz"],
            "depth_ratio": "medium",  # depth/qubits ratio
        },
        "machine_learning": {
            "gates": ["ry", "rz", "rx", "cx"],
            "patterns": ["variational", "parameterized"],
            "depth_ratio": "high",
        },
        "cryptography": {
            "gates": ["h", "cx", "ccx", "x"],
            "patterns": ["shor", "factoring", "discrete_log"],
            "depth_ratio": "very_high",
        },
        "simulation": {
            "gates": ["ry", "rz", "cx", "u3", "u2"],
            "patterns": ["hamiltonian", "evolution"],
            "depth_ratio": "medium",
        },
        "error_correction": {
            "gates": ["h", "cx", "cz", "measure"],
            "patterns": ["syndrome", "stabilizer", "surface_code"],
            "depth_ratio": "low",
        },
        "basic_algorithms": {
            "gates": ["h", "x", "z", "cx"],
            "patterns": ["grover", "deutsch", "bernstein"],
            "depth_ratio": "low",
        },
    }

    def detect_circuit_family(self, circuit: QuantumCircuit) -> list[str]:
        """Detect which algorithm families this circuit likely belongs to."""
        gate_counts = self._count_gates(circuit)
        total_gates = sum(gate_counts.values())

        if total_gates == 0:
            return ["empty"]

        gate_frequencies = {gate: count / total_gates for gate, count in gate_counts.items()}
        depth_ratio = circuit.depth() / max(circuit.num_qubits, 1)

        family_scores = {}

        for family, signature in self.ALGORITHM_SIGNATURES.items():
            score = 0.0

            # Check gate frequency match
            for gate in signature["gates"]:
                if gate in gate_frequencies:
                    score += gate_frequencies[gate] * 2  # Weight gate presence highly

            # Check depth ratio match
            if signature["depth_ratio"] == "low" and depth_ratio <= 2:
                score += 1.0
            elif signature["depth_ratio"] == "medium" and 2 < depth_ratio <= 10:
                score += 1.0
            elif signature["depth_ratio"] == "high" and 10 < depth_ratio <= 50:
                score += 1.0
            elif signature["depth_ratio"] == "very_high" and depth_ratio > 50:
                score += 1.0

            family_scores[family] = score

        # Return families with score > threshold, sorted by score
        threshold = 0.5
        detected_families = [family for family, score in family_scores.items() if score > threshold]

        return sorted(detected_families, key=lambda f: family_scores[f], reverse=True)

    def _count_gates(self, circuit: QuantumCircuit) -> dict[str, int]:
        """Count gate types in circuit."""
        gate_counts: defaultdict[str, int] = defaultdict(int)

        for instruction, _, _ in circuit.data:
            if instruction.name not in ["measure", "barrier", "delay"]:
                gate_counts[instruction.name] += 1

        return dict(gate_counts)


class WorkflowDetector:
    """Detect user workflow patterns from circuit and usage patterns."""

    def detect_workflow_type(
        self, circuit_patterns: list[CircuitPattern], usage_patterns: UsagePattern
    ) -> WorkflowType:
        """Infer workflow type from patterns."""

        # Education indicators
        if self._is_educational_pattern(circuit_patterns, usage_patterns):
            return WorkflowType.EDUCATION

        # Research indicators
        if self._is_research_pattern(circuit_patterns, usage_patterns):
            return WorkflowType.RESEARCH

        # Production indicators
        if self._is_production_pattern(circuit_patterns, usage_patterns):
            return WorkflowType.PRODUCTION

        # Benchmarking indicators
        if self._is_benchmarking_pattern(circuit_patterns, usage_patterns):
            return WorkflowType.BENCHMARKING

        # Default to research
        return WorkflowType.RESEARCH

    def _is_educational_pattern(self, circuit_patterns: list[CircuitPattern], usage_patterns: UsagePattern) -> bool:
        """Detect educational usage patterns."""
        if not circuit_patterns:
            return False

        avg_pattern = self._average_circuit_pattern(circuit_patterns)

        # Small circuits, basic algorithms, regular usage
        indicators = [
            avg_pattern.avg_qubits <= 10,  # Small educational circuits
            "basic_algorithms" in avg_pattern.circuit_families,
            usage_patterns.session_count > 5,  # Regular usage
            avg_pattern.avg_depth <= 20,  # Simple circuits
        ]

        return sum(indicators) >= 3

    def _is_research_pattern(self, circuit_patterns: list[CircuitPattern], usage_patterns: UsagePattern) -> bool:
        """Detect research usage patterns."""
        if not circuit_patterns:
            return True  # Default assumption

        avg_pattern = self._average_circuit_pattern(circuit_patterns)

        # Varied circuits, experimental patterns
        indicators = [
            len(avg_pattern.circuit_families) > 2,  # Diverse algorithms
            avg_pattern.entanglement_complexity > 0.3,  # Complex entanglement
            usage_patterns.total_circuits > 20,  # Substantial usage
            avg_pattern.avg_qubits > 5,  # Non-trivial circuits
        ]

        return sum(indicators) >= 2

    def _is_production_pattern(self, circuit_patterns: list[CircuitPattern], usage_patterns: UsagePattern) -> bool:
        """Detect production usage patterns."""
        if not circuit_patterns:
            return False

        avg_pattern = self._average_circuit_pattern(circuit_patterns)

        # Consistent circuits, reliability focus
        indicators = [
            len(set(usage_patterns.preferred_shot_counts)) <= 2,  # Consistent shots
            avg_pattern.avg_qubits >= 15,  # Production-scale circuits
            usage_patterns.session_count > 10,  # Regular production use
            len(avg_pattern.circuit_families) <= 2,  # Focused application
        ]

        return sum(indicators) >= 3

    def _is_benchmarking_pattern(self, circuit_patterns: list[CircuitPattern], usage_patterns: UsagePattern) -> bool:
        """Detect benchmarking usage patterns."""
        if not circuit_patterns:
            return False

        # Multiple backends used, varied circuits, performance focus
        indicators = [
            len(usage_patterns.backend_success_rates) > 3,  # Multiple backends
            usage_patterns.total_circuits > 50,  # Lots of testing
            len(set(usage_patterns.preferred_shot_counts)) > 3,  # Varied shot counts
        ]

        return sum(indicators) >= 2

    def _average_circuit_pattern(self, patterns: list[CircuitPattern]) -> CircuitPattern:
        """Compute average circuit pattern."""
        if not patterns:
            return CircuitPattern(0, 0, 0, [], 0, [])

        avg_qubits = sum(p.avg_qubits for p in patterns) / len(patterns)
        avg_depth = sum(p.avg_depth for p in patterns) / len(patterns)
        clifford_ratio = sum(p.clifford_ratio for p in patterns) / len(patterns)
        entanglement_complexity = sum(p.entanglement_complexity for p in patterns) / len(patterns)

        # Collect all gate types and families
        all_gates = []
        all_families = []
        for p in patterns:
            all_gates.extend(p.common_gates)
            all_families.extend(p.circuit_families)

        # Most common gates and families
        gate_counts: defaultdict[str, int] = defaultdict(int)
        family_counts: defaultdict[str, int] = defaultdict(int)

        for gate in all_gates:
            gate_counts[gate] += 1
        for family in all_families:
            family_counts[family] += 1

        common_gates = [gate for gate, count in sorted(gate_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
        circuit_families = [
            family for family, count in sorted(family_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        ]

        return CircuitPattern(
            avg_qubits=avg_qubits,
            avg_depth=avg_depth,
            clifford_ratio=clifford_ratio,
            common_gates=common_gates,
            entanglement_complexity=entanglement_complexity,
            circuit_families=circuit_families,
        )


class HardwareProfiler:
    """Detect and profile available hardware capabilities."""

    def detect_hardware_profile(self) -> HardwareProfile:
        """Comprehensive hardware detection."""
        return HardwareProfile(
            cpu_cores=self._detect_cpu_cores(),
            total_memory_gb=self._detect_memory_gb(),
            gpu_available=self._detect_gpu_available(),
            apple_silicon=self._detect_apple_silicon(),
            cuda_capable=self._detect_cuda_capable(),
            platform_name=platform.system(),
            rocm_capable=self._detect_rocm_capable(),
            oneapi_capable=self._detect_oneapi_capable(),
            opencl_available=self._detect_opencl_available(),
        )

    def _detect_cpu_cores(self) -> int:
        """Detect number of CPU cores."""
        try:
            import multiprocessing

            return multiprocessing.cpu_count()
        except Exception:
            return 4  # Reasonable default

    def _detect_memory_gb(self) -> float:
        """Detect total system memory in GB."""
        try:
            import psutil

            return psutil.virtual_memory().total / (1024**3)
        except Exception:
            return 8.0  # Default assumption

    def _detect_gpu_available(self) -> bool:
        """Detect if any GPU is available."""
        return self._detect_cuda_capable() or self._detect_apple_silicon()

    def _detect_apple_silicon(self) -> bool:
        """Detect Apple Silicon."""
        return platform.system() == "Darwin" and platform.machine() in ["arm64", "aarch64"]

    def _detect_cuda_capable(self) -> bool:
        """Detect CUDA capability."""
        try:
            import cupy

            device_count = cupy.cuda.runtime.getDeviceCount()
            return bool(device_count > 0)
        except Exception:
            return False

    def _detect_rocm_capable(self) -> bool:
        """Detect AMD ROCm capability (best-effort)."""
        try:
            import os

            # Minimal heuristic; robust ROCm detection requires system tools
            return bool(os.environ.get("ROCM_PATH"))
        except Exception:
            return False

    def _detect_oneapi_capable(self) -> bool:
        """Detect Intel oneAPI GPU capability (best-effort via dpctl)."""
        try:
            import dpctl

            try:
                devices = dpctl.get_devices()
                return bool(devices)
            except Exception:
                return True  # dpctl present but devices not queryable
        except Exception:
            return False

    def _detect_opencl_available(self) -> bool:
        """Detect OpenCL availability via pyopencl."""
        try:
            import pyopencl as cl

            try:
                plats = cl.get_platforms()
                return len(plats) > 0
            except Exception:
                return True  # pyopencl available but no platforms
        except Exception:
            return False


class ContextDetector:
    """Main context detection and management system."""

    def __init__(self, cache_file: str | None = None):
        """Initialize context detector with optional caching."""
        self.cache_file = Path(cache_file) if cache_file else Path.home() / ".ariadne" / "context_cache.json"
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)

        self.circuit_family_detector = CircuitFamilyDetector()
        self.workflow_detector = WorkflowDetector()
        self.hardware_profiler = HardwareProfiler()

        # Session tracking
        self.session_circuits: deque[QuantumCircuit] = deque(maxlen=100)
        self.session_start_time = time.time()
        self.performance_history = self._load_performance_history()

    def analyze_user_context(
        self,
        circuit_history: list[QuantumCircuit],
        backend_usage: dict[BackendType, int] | None = None,
        execution_times: dict[BackendType, list[float]] | None = None,
    ) -> UserContext:
        """Analyze comprehensive user context from circuit history and usage patterns."""

        # Analyze circuit patterns
        circuit_patterns = self._analyze_circuit_patterns(circuit_history)

        # Analyze usage patterns
        usage_patterns = self._analyze_usage_patterns(circuit_history, backend_usage or {})

        # Detect workflow type
        workflow_type = self.workflow_detector.detect_workflow_type(circuit_patterns, usage_patterns)

        # Get hardware profile
        hardware_profile = self.hardware_profiler.detect_hardware_profile()

        # Infer performance preferences from usage history
        performance_preferences = self._infer_performance_preferences(workflow_type, execution_times or {})

        # Determine preferred backends
        preferred_backends = self._determine_preferred_backends(backend_usage or {})

        context = UserContext(
            workflow_type=workflow_type,
            hardware_profile=hardware_profile,
            performance_preferences=performance_preferences,
            preferred_backends=preferred_backends,
        )

        # Cache the context
        self._save_context_cache(context)

        return context

    def _analyze_circuit_patterns(self, circuits: list[QuantumCircuit]) -> list[CircuitPattern]:
        """Analyze patterns in circuit collection."""
        if not circuits:
            return []

        patterns = []

        # Group circuits by similarity (simple grouping by qubit count)
        qubit_groups = defaultdict(list)
        for circuit in circuits:
            qubit_groups[circuit.num_qubits].append(circuit)

        for _qubit_count, group_circuits in qubit_groups.items():
            if len(group_circuits) >= 3:  # Only analyze groups with sufficient data
                pattern = self._analyze_circuit_group(group_circuits)
                patterns.append(pattern)

        return patterns

    def _analyze_circuit_group(self, circuits: list[QuantumCircuit]) -> CircuitPattern:
        """Analyze a group of similar circuits."""
        avg_qubits = sum(c.num_qubits for c in circuits) / len(circuits)
        avg_depth = sum(c.depth() for c in circuits) / len(circuits)

        # Analyze gate usage
        all_gates: list[str] = []
        clifford_count = 0

        for circuit in circuits:
            circuit_gates = []
            is_clifford = True

            for instruction, _, _ in circuit.data:
                gate_name = instruction.name
                if gate_name not in ["measure", "barrier", "delay"]:
                    circuit_gates.append(gate_name)
                    # Simple Clifford check
                    if gate_name not in ["h", "x", "y", "z", "s", "sdg", "cx", "cz"]:
                        is_clifford = False

            all_gates.extend(circuit_gates)
            if is_clifford:
                clifford_count += 1

        clifford_ratio = clifford_count / len(circuits)

        # Most common gates
        gate_counts: defaultdict[str, int] = defaultdict(int)
        for gate in all_gates:
            gate_counts[gate] += 1

        common_gates = [gate for gate, count in sorted(gate_counts.items(), key=lambda x: x[1], reverse=True)[:5]]

        # Detect circuit families
        all_families: list[str] = []
        for circuit in circuits:
            families = self.circuit_family_detector.detect_circuit_family(circuit)
            all_families.extend(families)

        family_counts: defaultdict[str, int] = defaultdict(int)
        for family in all_families:
            family_counts[family] += 1

        circuit_families = [
            family for family, count in sorted(family_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        ]

        # Estimate entanglement complexity (simplified)
        total_two_qubit_gates = sum(
            sum(1 for inst, _, _ in circuit.data if inst.num_qubits == 2) for circuit in circuits
        )
        total_gates = len(all_gates)
        entanglement_complexity = total_two_qubit_gates / max(total_gates, 1)

        return CircuitPattern(
            avg_qubits=avg_qubits,
            avg_depth=avg_depth,
            clifford_ratio=clifford_ratio,
            common_gates=common_gates,
            entanglement_complexity=entanglement_complexity,
            circuit_families=circuit_families,
        )

    def _analyze_usage_patterns(
        self, circuits: list[QuantumCircuit], backend_usage: dict[BackendType, int]
    ) -> UsagePattern:
        """Analyze user usage patterns."""
        session_count = 1  # Current session
        total_circuits = len(circuits)

        # Simplified usage pattern analysis
        return UsagePattern(
            session_count=session_count,
            total_circuits=total_circuits,
            preferred_shot_counts=[1000],  # Default
            time_of_day_preferences=[9, 10, 11, 14, 15, 16],  # Business hours
            backend_success_rates={backend.value: 0.95 for backend in backend_usage.keys()},
            average_session_length=30.0,  # 30 minutes default
        )

    def _infer_performance_preferences(
        self, workflow_type: WorkflowType, execution_times: dict[BackendType, list[float]]
    ) -> PerformancePreferences:
        """Infer user performance preferences from workflow and history."""

        if workflow_type == WorkflowType.EDUCATION:
            # Education values clarity and reliability over speed
            return PerformancePreferences(
                speed_priority=0.2, accuracy_priority=0.4, memory_priority=0.2, energy_priority=0.2
            )
        elif workflow_type == WorkflowType.PRODUCTION:
            # Production values speed and reliability
            return PerformancePreferences(
                speed_priority=0.5, accuracy_priority=0.3, memory_priority=0.1, energy_priority=0.1
            )
        elif workflow_type == WorkflowType.BENCHMARKING:
            # Benchmarking values accuracy above all
            return PerformancePreferences(
                speed_priority=0.2, accuracy_priority=0.6, memory_priority=0.1, energy_priority=0.1
            )
        else:  # RESEARCH
            # Research values balanced performance
            return PerformancePreferences(
                speed_priority=0.4, accuracy_priority=0.3, memory_priority=0.2, energy_priority=0.1
            )

    def _determine_preferred_backends(self, backend_usage: dict[BackendType, int]) -> list[BackendType]:
        """Determine preferred backends from usage history."""
        if not backend_usage:
            return []

        # Sort by usage count and return top choices
        sorted_backends = sorted(backend_usage.items(), key=lambda item: item[1], reverse=True)
        return [backend for backend, count in sorted_backends[:3] if count > 0]

    def _load_performance_history(self) -> PerformanceHistory:
        """Load performance history from cache."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file) as f:
                    data = json.load(f)
                    # Convert string keys back to BackendType
                    backend_performance = {}
                    for backend_str, times in data.get("backend_performance", {}).items():
                        try:
                            backend = BackendType(backend_str)
                            backend_performance[backend] = times
                        except ValueError:
                            continue

                    return PerformanceHistory(
                        backend_performance=backend_performance,
                        user_satisfaction_scores={},
                        error_rates={},
                        memory_usage_patterns={},
                    )
        except Exception:
            pass

        return PerformanceHistory(
            backend_performance={},
            user_satisfaction_scores={},
            error_rates={},
            memory_usage_patterns={},
        )

    def _save_context_cache(self, context: UserContext) -> None:
        """Save context to cache file."""
        try:
            cache_data = {
                "context": asdict(context),
                "timestamp": time.time(),
                "backend_performance": {
                    backend.value: times for backend, times in self.performance_history.backend_performance.items()
                },
            }

            with open(self.cache_file, "w") as f:
                json.dump(cache_data, f, indent=2, default=str)
        except Exception:
            pass  # Don't fail if caching fails

    def update_performance_history(self, backend: BackendType, execution_time: float, success: bool = True) -> None:
        """Update performance history with new execution data."""
        if backend not in self.performance_history.backend_performance:
            self.performance_history.backend_performance[backend] = []

        self.performance_history.backend_performance[backend].append(execution_time)

        # Keep only recent history (last 100 measurements)
        if len(self.performance_history.backend_performance[backend]) > 100:
            self.performance_history.backend_performance[backend] = self.performance_history.backend_performance[
                backend
            ][-100:]


# Convenience function for easy integration
def detect_user_context(
    circuit_history: list[QuantumCircuit] | None = None, cache_file: str | None = None
) -> UserContext:
    """Convenience function to detect user context."""
    detector = ContextDetector(cache_file)
    return detector.analyze_user_context(circuit_history or [])
