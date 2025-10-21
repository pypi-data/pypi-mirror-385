"""
Unified Quantum Simulation API

This module provides a comprehensive, unified API for quantum circuit simulation
with advanced options, backend preferences, and intelligent routing capabilities.
It serves as the main entry point for all quantum simulation operations.
"""

from __future__ import annotations

import os
import time
import warnings
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit

from .ft.resource_estimator import ResourceEstimate, estimate_circuit_resources
from .quantum_advantage import detect_quantum_advantage

# Import core Ariadne components
from .router import BackendType, SimulationResult


class OptimizationLevel(Enum):
    """Quantum circuit optimization levels."""

    NONE = 0  # No optimization
    BASIC = 1  # Basic gate optimization
    MEDIUM = 2  # Standard optimization with synthesis
    HIGH = 3  # Aggressive optimization with advanced passes


class ErrorMitigation(Enum):
    """Error mitigation techniques."""

    NONE = "none"
    ZNE = "zero_noise_extrapolation"
    CDR = "clifford_data_regression"
    SYMMETRY = "symmetry_verification"
    VIRTUAL_DISTILLATION = "virtual_distillation"


@dataclass
class SimulationOptions:
    """Comprehensive simulation configuration options."""

    # Backend preferences
    backend_preference: list[str] = field(default_factory=lambda: ["auto"])
    backend_options: dict[str, Any] = field(default_factory=dict)

    # Execution parameters
    shots: int = 1000
    seed: int | None = None

    # Precision and noise preferences (influence routing heuristics)
    precision: str = "default"  # one of: default, high
    noise_model: Any | None = None
    budget_ms: int | None = None

    # Optimization settings
    optimization_level: OptimizationLevel = OptimizationLevel.MEDIUM
    transpiler_options: dict[str, Any] = field(default_factory=dict)

    # Error mitigation
    error_mitigation: ErrorMitigation = ErrorMitigation.NONE
    mitigation_options: dict[str, Any] = field(default_factory=dict)

    # Analysis options
    analyze_quantum_advantage: bool = True
    estimate_resources: bool = True
    include_fault_tolerant: bool = False

    # Performance options
    enable_caching: bool = True
    memory_limit_mb: int | None = None
    timeout_seconds: float | None = None

    # Output options
    return_statevector: bool = False
    return_probabilities: bool = False
    save_intermediate_results: bool = False

    # Visualization options
    plot_results: bool = False
    save_plots: bool = False
    plot_format: str = "png"


@dataclass
class EnhancedSimulationResult:
    """Enhanced simulation result with comprehensive analysis."""

    # Core results
    counts: dict[str, int]
    execution_time: float
    backend_used: str

    # Circuit analysis
    circuit_analysis: dict[str, Any]
    quantum_advantage: dict[str, Any] | None = None
    resource_estimate: ResourceEstimate | None = None

    # Performance metrics
    backend_performance: dict[str, Any] = field(default_factory=dict)
    optimization_applied: list[str] = field(default_factory=list)

    # Optional outputs
    statevector: np.ndarray | None = None
    probabilities: np.ndarray | None = None
    intermediate_results: list[dict[str, Any]] = field(default_factory=list)

    # Metadata
    simulation_options: SimulationOptions | None = None
    warnings: list[str] = field(default_factory=list)

    def get_expectation_value(self, observable: str) -> float:
        """Calculate expectation value for a Pauli observable."""
        # Simplified implementation - in practice would use proper Pauli algebra
        total_shots = sum(self.counts.values())

        if observable == "Z":
            # For single-qubit Z observable
            prob_0 = sum(count for state, count in self.counts.items() if state.endswith("0")) / total_shots
            prob_1 = sum(count for state, count in self.counts.items() if state.endswith("1")) / total_shots
            return prob_0 - prob_1

        return 0.0  # Placeholder for complex observables

    def get_probability_distribution(self) -> dict[str, float]:
        """Get normalized probability distribution."""
        total_shots = sum(self.counts.values())
        return {state: count / total_shots for state, count in self.counts.items()}

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return {
            "counts": self.counts,
            "execution_time": self.execution_time,
            "backend_used": self.backend_used,
            "circuit_analysis": self.circuit_analysis,
            "quantum_advantage": self.quantum_advantage,
            "resource_estimate": self.resource_estimate.__dict__ if self.resource_estimate else None,
            "backend_performance": self.backend_performance,
            "optimization_applied": self.optimization_applied,
            "warnings": self.warnings,
        }


class QuantumSimulator:
    """
    Unified quantum simulation interface with advanced capabilities.

    Provides a high-level API for quantum circuit simulation with intelligent
    backend routing, optimization, error mitigation, and comprehensive analysis.
    """

    def __init__(
        self,
        config_file: Path | None = None,
        enable_calibration: bool = True,
        cache_dir: Path | None = None,
    ):
        """Initialize quantum simulator with configuration."""

        # Core router with intelligent backend selection
        # Since QuantumRouter is removed, we rely on the top-level simulate function
        # or an internal EnhancedQuantumRouter instance if needed for configuration.
        # The simulate function in router.py now handles routing internally.
        pass

        # Configuration
        self.config_file = config_file
        self.cache_dir = cache_dir or Path.home() / ".ariadne" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Load configuration if provided
        if config_file and config_file.exists():
            self._load_configuration(config_file)

        # Performance tracking
        self.simulation_count = 0
        self.total_execution_time = 0.0
        self.backend_usage: dict[str, int] = {}

    def simulate(self, circuit: QuantumCircuit, options: SimulationOptions | None = None) -> EnhancedSimulationResult:
        """
        Simulate quantum circuit with comprehensive analysis.

        Args:
            circuit: Quantum circuit to simulate
            options: Simulation configuration options

        Returns:
            Enhanced simulation result with analysis
        """

        # Use default options if none provided
        if options is None:
            options = SimulationOptions()

        # Start timing
        time.perf_counter()

        # Validate inputs
        self._validate_inputs(circuit, options)

        # Apply circuit optimization
        optimized_circuit = self._optimize_circuit(circuit, options)

        # Analyze circuit if requested
        circuit_analysis = {}
        quantum_advantage = None
        resource_estimate = None

        if options.analyze_quantum_advantage or options.estimate_resources:
            from .route.analyze import analyze_circuit

            circuit_analysis = analyze_circuit(optimized_circuit)

            if options.analyze_quantum_advantage:
                quantum_advantage = detect_quantum_advantage(optimized_circuit)

            if options.estimate_resources:
                resource_estimate = estimate_circuit_resources(
                    optimized_circuit,
                    shots=options.shots,
                    include_magic_states=options.include_fault_tolerant,
                    include_measurement=options.include_fault_tolerant,
                )

        # Configure backend preferences
        self._configure_backend_preferences(options)

        # Execute simulation with error handling
        try:
            result = self._execute_simulation(optimized_circuit, options)
        except Exception as e:
            # Enhanced error handling with fallback
            warnings.warn(f"Primary simulation failed: {e}. Attempting fallback...", stacklevel=2)
            result = self._execute_fallback_simulation(optimized_circuit, options)

        # Apply error mitigation if requested
        if options.error_mitigation != ErrorMitigation.NONE:
            result = self._apply_error_mitigation(result, options)

        # Calculate additional outputs
        statevector = None
        probabilities = None

        if options.return_statevector:
            statevector = self._get_statevector(optimized_circuit)

        if options.return_probabilities:
            probabilities = self._calculate_probabilities(result.counts)

        # Create enhanced result
        enhanced_result = EnhancedSimulationResult(
            counts=result.counts,
            execution_time=result.execution_time,
            backend_used=result.backend_used.value,
            circuit_analysis=circuit_analysis,
            quantum_advantage=quantum_advantage,
            resource_estimate=resource_estimate,
            backend_performance=result.metadata,
            statevector=statevector,
            probabilities=probabilities,
            simulation_options=options,
        )

        # Update performance tracking
        self._update_performance_tracking(enhanced_result)

        # Generate visualization if requested
        if options.plot_results:
            self._generate_visualizations(enhanced_result, options)

        return enhanced_result

    def simulate_batch(
        self, circuits: list[QuantumCircuit], options: SimulationOptions | None = None
    ) -> list[EnhancedSimulationResult]:
        """Simulate multiple circuits with shared configuration."""

        if options is None:
            options = SimulationOptions()

        results = []
        for i, circuit in enumerate(circuits):
            # Add circuit index to options
            circuit_options = options
            circuit_options.backend_options = {**options.backend_options, "circuit_index": i}

            result = self.simulate(circuit, circuit_options)
            results.append(result)

        return results

    def compare_backends(
        self, circuit: QuantumCircuit, backends: list[str], shots: int = 1000
    ) -> dict[str, EnhancedSimulationResult]:
        """Compare circuit execution across multiple backends."""

        results = {}

        for backend in backends:
            options = SimulationOptions(
                backend_preference=[backend],
                shots=shots,
                analyze_quantum_advantage=False,  # Skip for comparison
                estimate_resources=False,
            )

            try:
                result = self.simulate(circuit, options)
                results[backend] = result
            except Exception as e:
                warnings.warn(f"Backend {backend} failed: {e}", stacklevel=2)

        return results

    def optimize_circuit(
        self, circuit: QuantumCircuit, level: OptimizationLevel = OptimizationLevel.MEDIUM
    ) -> QuantumCircuit:
        """Optimize quantum circuit with specified level."""

        options = SimulationOptions(optimization_level=level)
        return self._optimize_circuit(circuit, options)

    def estimate_resources(self, circuit: QuantumCircuit, include_fault_tolerant: bool = False) -> ResourceEstimate:
        """Estimate resources required for circuit execution."""

        return estimate_circuit_resources(
            circuit,
            include_magic_states=include_fault_tolerant,
            include_measurement=include_fault_tolerant,
        )

    def get_performance_stats(self) -> dict[str, Any]:
        """Get comprehensive performance statistics."""

        return {
            "simulation_count": self.simulation_count,
            "total_execution_time": self.total_execution_time,
            "average_execution_time": self.total_execution_time / max(1, self.simulation_count),
            "backend_usage": self.backend_usage,
            "router_stats": "Router functionality consolidated into EnhancedQuantumRouter.",
            "cache_stats": self._get_cache_stats(),
        }

    def _validate_inputs(self, circuit: QuantumCircuit, options: SimulationOptions) -> None:
        """Validate simulation inputs."""

        if circuit.num_qubits == 0:
            raise ValueError("Circuit must contain at least one qubit")

        if options.shots <= 0:
            raise ValueError("Number of shots must be positive")

        if options.timeout_seconds and options.timeout_seconds <= 0:
            raise ValueError("Timeout must be positive")

    def _optimize_circuit(self, circuit: QuantumCircuit, options: SimulationOptions) -> QuantumCircuit:
        """Apply circuit optimization based on specified level."""

        if options.optimization_level == OptimizationLevel.NONE:
            return circuit

        # Placeholder for actual optimization passes
        # In practice, would use Qiskit transpiler with appropriate passes
        optimized = circuit.copy()

        # Record optimization applied
        optimization_passes = []

        if options.optimization_level.value >= 1:
            optimization_passes.append("basic_gate_optimization")

        if options.optimization_level.value >= 2:
            optimization_passes.append("synthesis_optimization")

        if options.optimization_level.value >= 3:
            optimization_passes.append("aggressive_optimization")

        return optimized

    def _configure_backend_preferences(self, options: SimulationOptions) -> None:
        """Configure router with backend preferences."""

        # Update router backend capacities based on preferences
        # This functionality is now handled by EnhancedQuantumRouter internally if needed.
        # Since QuantumRouter is removed, we skip this direct manipulation.
        pass

    def _execute_simulation(self, circuit: QuantumCircuit, options: SimulationOptions) -> SimulationResult:
        """Execute simulation with configured options."""

        # Use top-level simulate function for intelligent backend selection
        from .router import simulate as core_simulate

        backend_name = (
            options.backend_preference[0]
            if options.backend_preference and options.backend_preference[0] != "auto"
            else None
        )
        # Map options to routing environment hints (non-invasive)
        prev_budget = os.environ.get("ARIADNE_ROUTING_BUDGET_MS")
        prev_ddsim = os.environ.get("ARIADNE_ROUTING_PREFER_DDSIM")
        try:
            if options.budget_ms is not None:
                os.environ["ARIADNE_ROUTING_BUDGET_MS"] = str(options.budget_ms)
            if (options.precision or "").lower() == "high" or options.noise_model is not None:
                os.environ["ARIADNE_ROUTING_PREFER_DDSIM"] = "1"
            return core_simulate(circuit, shots=options.shots, backend=backend_name)
        finally:
            # Restore prior env to avoid test leakage
            if prev_budget is None:
                os.environ.pop("ARIADNE_ROUTING_BUDGET_MS", None)
            else:
                os.environ["ARIADNE_ROUTING_BUDGET_MS"] = prev_budget
            if prev_ddsim is None:
                os.environ.pop("ARIADNE_ROUTING_PREFER_DDSIM", None)
            else:
                os.environ["ARIADNE_ROUTING_PREFER_DDSIM"] = prev_ddsim

    def _execute_fallback_simulation(self, circuit: QuantumCircuit, options: SimulationOptions) -> SimulationResult:
        """Execute simulation with basic fallback."""

        # Force Qiskit backend as ultimate fallback
        from qiskit.providers.basic_provider import BasicProvider

        provider = BasicProvider()
        backend = provider.get_backend("basic_simulator")
        job = backend.run(circuit, shots=options.shots)
        counts = job.result().get_counts()

        # Create compatible result
        from .router import RoutingDecision

        routing_decision = RoutingDecision(
            circuit_entropy=0.0,
            recommended_backend=BackendType.QISKIT,
            confidence_score=1.0,
            expected_speedup=1.0,
            channel_capacity_match=0.5,
            alternatives=[],
        )

        return SimulationResult(
            counts={str(k): v for k, v in counts.items()},
            backend_used=BackendType.QISKIT,
            execution_time=0.0,
            routing_decision=routing_decision,
            metadata={"fallback": True, "shots": options.shots},
        )

    def _apply_error_mitigation(self, result: SimulationResult, options: SimulationOptions) -> SimulationResult:
        """Apply error mitigation techniques."""

        # Placeholder for error mitigation implementation
        # In practice, would implement ZNE, CDR, etc.

        if options.error_mitigation == ErrorMitigation.ZNE:
            # Zero-noise extrapolation placeholder
            pass
        elif options.error_mitigation == ErrorMitigation.CDR:
            # Clifford data regression placeholder
            pass

        return result

    def _get_statevector(self, circuit: QuantumCircuit) -> np.ndarray | None:
        """Get final statevector if possible."""

        try:
            # Use router to get statevector
            # This would require backend-specific implementation
            return None  # Placeholder
        except Exception:
            return None

    def _calculate_probabilities(self, counts: dict[str, int]) -> np.ndarray:
        """Calculate probability distribution from counts."""

        total_shots = sum(counts.values())
        num_states = len(counts)

        probabilities = np.zeros(num_states)
        for i, (_state, count) in enumerate(counts.items()):
            probabilities[i] = count / total_shots

        return probabilities

    def _update_performance_tracking(self, result: EnhancedSimulationResult) -> None:
        """Update performance tracking statistics."""

        self.simulation_count += 1
        self.total_execution_time += result.execution_time

        backend = result.backend_used
        self.backend_usage[backend] = self.backend_usage.get(backend, 0) + 1

    def _generate_visualizations(self, result: EnhancedSimulationResult, options: SimulationOptions) -> None:
        """Generate result visualizations."""

        # Placeholder for visualization generation
        # In practice, would use matplotlib/plotly to create plots
        pass

    def _get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""

        # Placeholder for cache statistics
        return {"cache_dir": str(self.cache_dir), "cache_size_mb": 0, "cached_results": 0}

    def _load_configuration(self, config_file: Path) -> None:
        """Load configuration from file."""

        # Placeholder for configuration loading
        pass


# Convenience functions for common use cases
def simulate(
    circuit: QuantumCircuit, shots: int = 1000, backend: str | None = None, optimize: bool = True
) -> EnhancedSimulationResult:
    """Simple simulation interface."""

    simulator = QuantumSimulator()

    options = SimulationOptions(
        shots=shots,
        backend_preference=[backend] if backend else ["auto"],
        optimization_level=OptimizationLevel.MEDIUM if optimize else OptimizationLevel.NONE,
    )

    return simulator.simulate(circuit, options)


def simulate_with_analysis(circuit: QuantumCircuit, shots: int = 1000) -> EnhancedSimulationResult:
    """Simulation with full quantum advantage and resource analysis."""

    simulator = QuantumSimulator()

    options = SimulationOptions(
        shots=shots,
        analyze_quantum_advantage=True,
        estimate_resources=True,
        include_fault_tolerant=True,
    )

    return simulator.simulate(circuit, options)


def compare_backends(
    circuit: QuantumCircuit, backends: list[str] | None = None, shots: int = 1000
) -> dict[str, EnhancedSimulationResult]:
    """Compare circuit performance across backends."""

    if backends is None:
        backends = ["qiskit", "stim", "metal", "cuda", "tensor_network"]

    simulator = QuantumSimulator()
    return simulator.compare_backends(circuit, backends, shots)
