"""
Circuit optimization system for Ariadne.

This module provides circuit transformation and optimization passes,
including gate fusion, cancellation, and circuit analysis for optimization opportunities.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from qiskit import QuantumCircuit
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import (
    Cancellation,
    CommutativeCancellation,
    Optimize1qGates,
    Optimize2qGates,
    Unroll3qOrMore,
    UnrollCustomDefinitions,
)

try:
    from ariadne.core import get_logger
except ImportError:
    # Fallback for when running as a script
    import os
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ariadne.core import get_logger


class OptimizationType(Enum):
    """Types of circuit optimizations."""

    GATE_FUSION = "gate_fusion"
    GATE_CANCELLATION = "gate_cancellation"
    COMMUTATIVE_CANCELLATION = "commutative_cancellation"
    SINGLE_QUBIT_OPTIMIZATION = "single_qubit_optimization"
    TWO_QUBIT_OPTIMIZATION = "two_qubit_optimization"
    RESET_REMOVAL = "reset_removal"
    CUSTOM_UNROLL = "custom_unroll"
    DEPTH_REDUCTION = "depth_reduction"
    CONNECTIVITY_OPTIMIZATION = "connectivity_optimization"


@dataclass
class OptimizationResult:
    """Result of circuit optimization."""

    original_circuit: QuantumCircuit
    optimized_circuit: QuantumCircuit
    optimization_type: OptimizationType
    execution_time: float
    metrics: dict[str, Any] = field(default_factory=dict)

    @property
    def depth_reduction(self) -> float:
        """Calculate depth reduction percentage."""
        if self.original_circuit.depth() == 0:
            return 0.0
        return float(
            (self.original_circuit.depth() - self.optimized_circuit.depth()) / self.original_circuit.depth() * 100
        )

    @property
    def gate_count_reduction(self) -> float:
        """Calculate gate count reduction percentage."""
        original_count = len(self.original_circuit.data)
        optimized_count = len(self.optimized_circuit.data)

        if original_count == 0:
            return 0.0

        result = float((original_count - optimized_count) / original_count * 100.0)
        return result


class CircuitOptimizer(ABC):
    """Base class for circuit optimizers."""

    def __init__(self, name: str) -> None:
        """
        Initialize the circuit optimizer.

        Args:
            name: Optimizer name
        """
        self.name = name
        self.logger = get_logger(f"optimizer.{name}")

    @abstractmethod
    def optimize(self, circuit: QuantumCircuit, **kwargs: Any) -> OptimizationResult:
        """
        Optimize a quantum circuit.

        Args:
            circuit: Circuit to optimize
            **kwargs: Additional optimization parameters

        Returns:
            Optimization result
        """
        pass

    def _calculate_metrics(self, original: QuantumCircuit, optimized: QuantumCircuit) -> dict[str, Any]:
        """Calculate optimization metrics."""
        return {
            "original_depth": original.depth(),
            "optimized_depth": optimized.depth(),
            "depth_reduction": self._calculate_depth_reduction(original, optimized),
            "original_gate_count": len(original.data),
            "optimized_gate_count": len(optimized.data),
            "gate_count_reduction": self._calculate_gate_count_reduction(original, optimized),
            "original_qubits": original.num_qubits,
            "optimized_qubits": optimized.num_qubits,
        }

    def _calculate_depth_reduction(self, original: QuantumCircuit, optimized: QuantumCircuit) -> float:
        """Calculate depth reduction percentage."""
        if original.depth() == 0:
            return 0.0
        return float((original.depth() - optimized.depth()) / original.depth() * 100)

    def _calculate_gate_count_reduction(self, original: QuantumCircuit, optimized: QuantumCircuit) -> float:
        """Calculate gate count reduction percentage."""
        original_count = len(original.data)
        optimized_count = len(optimized.data)

        if original_count == 0:
            return 0.0
        return float((original_count - optimized_count) / original_count * 100)


class GateFusionOptimizer(CircuitOptimizer):
    """Optimizer for gate fusion operations."""

    def __init__(self, max_fusion_size: int = 5):
        """
        Initialize the gate fusion optimizer.

        Args:
            max_fusion_size: Maximum number of gates to fuse together
        """
        super().__init__("gate_fusion")
        self.max_fusion_size = max_fusion_size

    def optimize(self, circuit: QuantumCircuit, **kwargs: Any) -> OptimizationResult:
        """Optimize circuit by fusing compatible gates."""
        start_time = time.time()

        # Create a copy of the circuit
        optimized = circuit.copy()

        # Apply gate fusion
        optimized = self._fuse_gates(optimized)

        execution_time = time.time() - start_time

        # Calculate metrics
        metrics = self._calculate_metrics(circuit, optimized)
        metrics["max_fusion_size"] = self.max_fusion_size

        return OptimizationResult(
            original_circuit=circuit,
            optimized_circuit=optimized,
            optimization_type=OptimizationType.GATE_FUSION,
            execution_time=execution_time,
            metrics=metrics,
        )

    def _fuse_gates(self, circuit: QuantumCircuit) -> QuantumCircuit:
        """Fuse compatible gates in the circuit."""
        # This is a simplified implementation
        # In a production system, this would be more sophisticated

        # For now, we'll use Qiskit's built-in optimization passes
        # which include some gate fusion
        pass_manager = PassManager(
            [
                Optimize1qGates(),
                Optimize2qGates(),
            ]
        )

        return pass_manager.run(circuit)


class GateCancellationOptimizer(CircuitOptimizer):
    """Optimizer for gate cancellation operations."""

    def __init__(self) -> None:
        """Initialize the gate cancellation optimizer."""
        super().__init__("gate_cancellation")

    def optimize(self, circuit: QuantumCircuit, **kwargs: Any) -> OptimizationResult:
        """Optimize circuit by canceling redundant gates."""
        start_time = time.time()

        # Create a copy of the circuit
        optimized = circuit.copy()

        # Apply gate cancellation
        pass_manager = PassManager(
            [
                Cancellation(),
                CommutativeCancellation(),
            ]
        )

        optimized = pass_manager.run(optimized)

        execution_time = time.time() - start_time

        # Calculate metrics
        metrics = self._calculate_metrics(circuit, optimized)

        return OptimizationResult(
            original_circuit=circuit,
            optimized_circuit=optimized,
            optimization_type=OptimizationType.GATE_CANCELLATION,
            execution_time=execution_time,
            metrics=metrics,
        )


class DepthReductionOptimizer(CircuitOptimizer):
    """Optimizer for reducing circuit depth."""

    def __init__(self) -> None:
        """Initialize the depth reduction optimizer."""
        super().__init__("depth_reduction")

    def optimize(self, circuit: QuantumCircuit, **kwargs: Any) -> OptimizationResult:
        """Optimize circuit to reduce depth."""
        start_time = time.time()

        # Create a copy of the circuit
        optimized = circuit.copy()

        # Apply depth reduction optimizations
        pass_manager = PassManager(
            [
                Optimize1qGates(),
                Optimize2qGates(),
                Cancellation(),
                CommutativeCancellation(),
            ]
        )

        optimized = pass_manager.run(optimized)

        execution_time = time.time() - start_time

        # Calculate metrics
        metrics = self._calculate_metrics(circuit, optimized)

        return OptimizationResult(
            original_circuit=circuit,
            optimized_circuit=optimized,
            optimization_type=OptimizationType.DEPTH_REDUCTION,
            execution_time=execution_time,
            metrics=metrics,
        )


class CustomUnrollOptimizer(CircuitOptimizer):
    """Optimizer for custom gate unrolling."""

    def __init__(self, basis_gates: list[str] | None = None):
        """
        Initialize the custom unroll optimizer.

        Args:
            basis_gates: List of basis gates to unroll to
        """
        super().__init__("custom_unroll")
        self.basis_gates = basis_gates or ["cx", "h", "t", "tdg", "s", "sdg", "x", "y", "z"]

    def optimize(self, circuit: QuantumCircuit, **kwargs: Any) -> OptimizationResult:
        """Optimize circuit by unrolling custom gates."""
        start_time = time.time()

        # Create a copy of the circuit
        optimized = circuit.copy()

        # Apply custom unroll
        pass_manager = PassManager(
            [
                UnrollCustomDefinitions(self.basis_gates),
                Unroll3qOrMore(basis_gates=self.basis_gates),
            ]
        )

        optimized = pass_manager.run(optimized)

        execution_time = time.time() - start_time

        # Calculate metrics
        metrics = self._calculate_metrics(circuit, optimized)
        metrics["basis_gates"] = self.basis_gates

        return OptimizationResult(
            original_circuit=circuit,
            optimized_circuit=optimized,
            optimization_type=OptimizationType.CUSTOM_UNROLL,
            execution_time=execution_time,
            metrics=metrics,
        )


class CompositeOptimizer(CircuitOptimizer):
    """Composite optimizer that applies multiple optimization passes."""

    def __init__(self, optimizers: list[CircuitOptimizer]):
        """
        Initialize the composite optimizer.

        Args:
            optimizers: List of optimizers to apply in sequence
        """
        super().__init__("composite")
        self.optimizers = optimizers

    def optimize(self, circuit: QuantumCircuit, **kwargs: Any) -> OptimizationResult:
        """Apply multiple optimization passes in sequence."""
        start_time = time.time()

        # Start with the original circuit
        current_circuit = circuit.copy()
        original_circuit = circuit

        # Apply each optimizer in sequence
        optimization_types: list[OptimizationType] = []
        total_metrics: dict[str, Any] = {}

        for optimizer in self.optimizers:
            result = optimizer.optimize(current_circuit, **kwargs)
            current_circuit = result.optimized_circuit
            optimization_types.append(result.optimization_type)

            # Merge metrics
            for key, value in result.metrics.items():
                if key in total_metrics:
                    total_metrics[f"{optimizer.name}_{key}"] = value
                else:
                    total_metrics[key] = value

        execution_time = time.time() - start_time

        # Calculate final metrics
        final_metrics = self._calculate_metrics(original_circuit, current_circuit)
        final_metrics.update(total_metrics)
        final_metrics["optimization_types"] = [t.value for t in optimization_types]

        return OptimizationResult(
            original_circuit=original_circuit,
            optimized_circuit=current_circuit,
            optimization_type=OptimizationType.DEPTH_REDUCTION,  # Use a generic type
            execution_time=execution_time,
            metrics=final_metrics,
        )


class CircuitOptimizationManager:
    """Manager for circuit optimization operations."""

    def __init__(self) -> None:
        """Initialize the circuit optimization manager."""
        self.logger = get_logger("optimization_manager")

        # Initialize optimizers
        self._optimizers = {
            OptimizationType.GATE_FUSION: GateFusionOptimizer(),
            OptimizationType.GATE_CANCELLATION: GateCancellationOptimizer(),
            OptimizationType.DEPTH_REDUCTION: DepthReductionOptimizer(),
            OptimizationType.CUSTOM_UNROLL: CustomUnrollOptimizer(),
        }

        # Initialize composite optimizers
        self._composite_optimizers = {
            "aggressive": CompositeOptimizer(
                [
                    self._optimizers[OptimizationType.GATE_CANCELLATION],
                    self._optimizers[OptimizationType.GATE_FUSION],
                    self._optimizers[OptimizationType.DEPTH_REDUCTION],
                ]
            ),
            "conservative": CompositeOptimizer(
                [
                    self._optimizers[OptimizationType.GATE_CANCELLATION],
                    self._optimizers[OptimizationType.DEPTH_REDUCTION],
                ]
            ),
        }

    def optimize(
        self, circuit: QuantumCircuit, optimization_type: OptimizationType | str, **kwargs: Any
    ) -> OptimizationResult:
        """
        Optimize a circuit using the specified optimization type.

        Args:
            circuit: Circuit to optimize
            optimization_type: Type of optimization to apply
            **kwargs: Additional optimization parameters

        Returns:
            Optimization result
        """
        # Get optimizer
        if isinstance(optimization_type, OptimizationType):
            if optimization_type in self._optimizers:
                optimizer = self._optimizers[optimization_type]
            else:
                raise ValueError(f"Unknown optimization type: {optimization_type}")
        elif isinstance(optimization_type, str):
            if optimization_type in self._composite_optimizers:
                optimizer = self._composite_optimizers[optimization_type]
            else:
                # Try to convert string to enum
                try:
                    opt_type = OptimizationType(optimization_type)
                    if opt_type in self._optimizers:
                        optimizer = self._optimizers[opt_type]
                    else:
                        raise ValueError(f"Unknown optimization type: {optimization_type}")
                except ValueError as exc:
                    raise ValueError(f"Unknown optimization type: {optimization_type}") from exc
        else:
            raise ValueError(f"Invalid optimization type: {optimization_type}")

        # Apply optimization
        self.logger.info(f"Applying {optimization_type} optimization to circuit")
        result = optimizer.optimize(circuit, **kwargs)

        # Log results
        self.logger.info(
            f"Optimization complete: depth reduction {result.depth_reduction:.2f}%, "
            f"gate count reduction {result.gate_count_reduction:.2f}%"
        )

        return result

    def analyze_optimization_opportunities(self, circuit: QuantumCircuit) -> dict[str, Any]:
        """
        Analyze a circuit for optimization opportunities.

        Args:
            circuit: Circuit to analyze

        Returns:
            Analysis results
        """
        circuit_info: dict[str, int] = {
            "num_qubits": circuit.num_qubits,
            "depth": circuit.depth(),
            "gate_count": len(circuit.data),
        }
        optimization_opportunities: dict[str, dict[str, Any]] = {}
        recommendations: list[str] = []
        analysis: dict[str, Any] = {
            "circuit_info": circuit_info,
            "optimization_opportunities": optimization_opportunities,
            "recommendations": recommendations,
        }

        # Analyze for gate cancellation opportunities
        cancellation_opportunities = self._analyze_cancellation_opportunities(circuit)
        optimization_opportunities["gate_cancellation"] = cancellation_opportunities

        if cancellation_opportunities["potential_reduction"] > 5:
            recommendations.append("Consider applying gate cancellation optimization")

        # Analyze for gate fusion opportunities
        fusion_opportunities = self._analyze_fusion_opportunities(circuit)
        optimization_opportunities["gate_fusion"] = fusion_opportunities

        if fusion_opportunities["potential_reduction"] > 5:
            recommendations.append("Consider applying gate fusion optimization")

        # Analyze for depth reduction opportunities
        depth_opportunities = self._analyze_depth_opportunities(circuit)
        optimization_opportunities["depth_reduction"] = depth_opportunities

        if depth_opportunities["potential_reduction"] > 10:
            recommendations.append("Consider applying depth reduction optimization")

        return analysis

    def _analyze_cancellation_opportunities(self, circuit: QuantumCircuit) -> dict[str, Any]:
        """Analyze circuit for gate cancellation opportunities."""
        # Count consecutive identical gates on the same qubit
        consecutive_gates = 0
        gate_sequences: dict[Any, int] = {}

        for item in circuit.data:
            if hasattr(item, "operation"):
                instruction = item.operation
                qargs = list(item.qubits)
                cargs = list(item.clbits)
            else:  # Legacy tuple form
                instruction, qargs, cargs = item

            gate_name = instruction.name
            qubit_indices = tuple(circuit.find_bit(q).index for q in qargs)

            key = (gate_name, qubit_indices)
            if key in gate_sequences:
                gate_sequences[key] += 1
                if gate_sequences[key] > 1:
                    consecutive_gates += 1
            else:
                gate_sequences[key] = 1

        # Estimate potential reduction
        potential_reduction = 0
        for count in gate_sequences.values():
            if count > 1:
                potential_reduction += count - 1

        return {
            "consecutive_gates": consecutive_gates,
            "potential_reduction": potential_reduction,
            "gate_sequences": gate_sequences,
        }

    def _analyze_fusion_opportunities(self, circuit: QuantumCircuit) -> dict[str, Any]:
        """Analyze circuit for gate fusion opportunities."""
        # Count single-qubit gates on the same qubit
        single_qubit_gates = {}

        for item in circuit.data:
            if hasattr(item, "operation"):
                instruction = item.operation
                qargs = list(item.qubits)
                cargs = list(item.clbits)
            else:  # Legacy tuple form
                instruction, qargs, cargs = item

            if len(qargs) == 1:  # Single-qubit gate
                qubit = circuit.find_bit(qargs[0]).index
                if qubit not in single_qubit_gates:
                    single_qubit_gates[qubit] = 0
                single_qubit_gates[qubit] += 1

        # Estimate potential reduction
        potential_reduction = 0
        for count in single_qubit_gates.values():
            if count > 2:
                # Assume we can fuse groups of 3-5 gates
                fusion_groups = count // 3
                potential_reduction += fusion_groups * 2  # Each fusion reduces 2 gates

        return {
            "single_qubit_gates": single_qubit_gates,
            "potential_reduction": potential_reduction,
        }

    def _analyze_depth_opportunities(self, circuit: QuantumCircuit) -> dict[str, Any]:
        """Analyze circuit for depth reduction opportunities."""
        # Simple heuristic: circuits with many single-qubit gates can often be optimized
        single_qubit_count = 0
        two_qubit_count = 0

        for item in circuit.data:
            if hasattr(item, "operation"):
                instruction = item.operation
                qargs = list(item.qubits)
                cargs = list(item.clbits)
            else:  # Legacy tuple form
                instruction, qargs, cargs = item

            if len(qargs) == 1:
                single_qubit_count += 1
            elif len(qargs) == 2:
                two_qubit_count += 1

        # Estimate potential reduction
        total_gates = single_qubit_count + two_qubit_count
        if total_gates == 0:
            potential_reduction = 0
        else:
            # Assume we can reduce depth by 10-30% for typical circuits
            potential_reduction = circuit.depth() * 0.2

        return {
            "single_qubit_count": single_qubit_count,
            "two_qubit_count": two_qubit_count,
            "potential_reduction": potential_reduction,
        }


# Global optimization manager instance
_global_optimization_manager: CircuitOptimizationManager | None = None


def get_optimization_manager() -> CircuitOptimizationManager:
    """Get the global circuit optimization manager."""
    global _global_optimization_manager
    if _global_optimization_manager is None:
        _global_optimization_manager = CircuitOptimizationManager()
    return _global_optimization_manager


def optimize_circuit(
    circuit: QuantumCircuit, optimization_type: OptimizationType | str = "aggressive", **kwargs: Any
) -> OptimizationResult:
    """
    Optimize a circuit using the global optimization manager.

    Args:
        circuit: Circuit to optimize
        optimization_type: Type of optimization to apply
        **kwargs: Additional optimization parameters

    Returns:
        Optimization result
    """
    manager = get_optimization_manager()
    return manager.optimize(circuit, optimization_type, **kwargs)


def analyze_optimization_opportunities(circuit: QuantumCircuit) -> dict[str, Any]:
    """
    Analyze a circuit for optimization opportunities using the global manager.

    Args:
        circuit: Circuit to analyze

    Returns:
        Analysis results
    """
    manager = get_optimization_manager()
    return manager.analyze_optimization_opportunities(circuit)
