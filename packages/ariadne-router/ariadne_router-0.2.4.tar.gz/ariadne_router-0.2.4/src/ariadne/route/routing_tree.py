"""
Comprehensive Quantum Circuit Routing Decision Tree

This module implements a comprehensive routing tree that consolidates all the different
routing strategies and backends available in Ariadne into a unified decision framework.
"""

from __future__ import annotations

import platform
from dataclasses import dataclass, field
from enum import Enum
from importlib.util import find_spec
from typing import Any, Protocol

from qiskit import QuantumCircuit

from ..types import BackendType, RoutingDecision
from .analyze import analyze_circuit, is_clifford_circuit
from .context_detection import detect_user_context
from .enhanced_router import UserContext
from .mps_analyzer import should_use_mps


class RoutingStrategy(Enum):
    """Comprehensive routing strategies."""

    # Performance-oriented strategies
    SPEED_FIRST = "speed_first"
    ACCURACY_FIRST = "accuracy_first"
    MEMORY_EFFICIENT = "memory_efficient"

    # Circuit-type specialized strategies
    CLIFFORD_OPTIMIZED = "clifford_optimized"
    ENTANGLEMENT_AWARE = "entanglement_aware"
    STABILIZER_FOCUSED = "stabilizer_focused"

    # Hardware-specific strategies
    APPLE_SILICON_OPTIMIZED = "apple_silicon_optimized"
    CUDA_OPTIMIZED = "cuda_optimized"
    CPU_OPTIMIZED = "cpu_optimized"

    # Workflow-specific strategies
    RESEARCH_MODE = "research_mode"
    EDUCATION_MODE = "education_mode"
    PRODUCTION_MODE = "production_mode"

    # Intelligent/adaptive strategies
    AUTO_DETECT = "auto_detect"
    HYBRID_MULTI_BACKEND = "hybrid_multi_backend"


@dataclass
class RoutingNode:
    """A node in the routing decision tree."""

    name: str
    condition: str
    backend: BackendType | None = None
    children: list[RoutingNode] = field(default_factory=list)
    fallback: BackendType = BackendType.QISKIT
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


class RoutingCondition(Protocol):
    """Protocol for routing conditions."""

    def evaluate(self, circuit: QuantumCircuit, context: UserContext) -> bool:
        """Evaluate if this condition is met."""
        ...


class ComprehensiveRoutingTree:
    """
    Comprehensive routing tree that incorporates all available backends and strategies.

    This class consolidates all the different routing approaches into a unified
    decision tree that can handle any circuit type and user context.
    """

    def __init__(self):
        """Initialize the comprehensive routing tree."""
        self.tree = self._build_routing_tree()
        self.backend_availability = self._check_backend_availability()

    def _check_backend_availability(self) -> dict[BackendType, bool]:
        """Check which backends are actually available."""
        availability = {}

        # Always available
        availability[BackendType.QISKIT] = True

        # Check Stim
        availability[BackendType.STIM] = find_spec("stim") is not None

        # Check CUDA
        availability[BackendType.CUDA] = find_spec("cupy") is not None

        # Check Metal (Apple Silicon)
        availability[BackendType.JAX_METAL] = self._is_apple_silicon() and (find_spec("jax") is not None)

        # Check Tensor Network
        availability[BackendType.TENSOR_NETWORK] = bool(find_spec("cotengra") and find_spec("quimb"))

        # Check MPS
        availability[BackendType.MPS] = find_spec("quimb") is not None

        # Check DDSIM
        availability[BackendType.DDSIM] = find_spec("mqt.ddsim") is not None

        # Additional optional backends
        availability[BackendType.CIRQ] = find_spec("cirq") is not None
        availability[BackendType.PENNYLANE] = find_spec("pennylane") is not None
        availability[BackendType.QULACS] = find_spec("qulacs") is not None
        availability[BackendType.PYQUIL] = find_spec("pyquil") is not None
        availability[BackendType.BRAKET] = find_spec("braket") is not None
        availability[BackendType.QSHARP] = find_spec("qsharp") is not None
        availability[BackendType.OPENCL] = find_spec("pyopencl") is not None

        return availability

    def _build_routing_tree(self) -> RoutingNode:
        """Build the comprehensive routing decision tree."""

        # Root node
        root = RoutingNode(
            name="root",
            condition="always",
            metadata={"description": "Root of routing decision tree"},
        )

        # Level 1: Circuit type classification
        clifford_node = RoutingNode(
            name="clifford_circuits",
            condition="is_clifford_circuit(circuit)",
            metadata={"description": "Pure Clifford circuits - optimal for Stim"},
        )

        stabilizer_node = RoutingNode(
            name="stabilizer_circuits",
            condition="is_stabilizer_circuit(circuit)",
            metadata={"description": "Stabilizer circuits"},
        )

        general_node = RoutingNode(
            name="general_circuits",
            condition="not is_clifford_circuit(circuit)",
            metadata={"description": "General quantum circuits"},
        )

        root.children = [clifford_node, stabilizer_node, general_node]

        # Level 2: Clifford circuit routing
        stim_node = RoutingNode(
            name="stim_backend",
            condition="backend_available(BackendType.STIM)",
            backend=BackendType.STIM,
            confidence=0.95,
            metadata={"description": "Stim for Clifford circuits - fastest option"},
        )

        clifford_fallback = RoutingNode(
            name="clifford_fallback",
            condition="always",
            backend=BackendType.QISKIT,
            confidence=0.7,
            metadata={"description": "Qiskit fallback for Clifford"},
        )

        clifford_node.children = [stim_node, clifford_fallback]

        # Level 2: General circuit routing by size and complexity
        small_circuits = RoutingNode(
            name="small_circuits",
            condition="circuit.num_qubits <= 20",
            metadata={"description": "Small circuits (≤20 qubits)"},
        )

        medium_circuits = RoutingNode(
            name="medium_circuits",
            condition="20 < circuit.num_qubits <= 35",
            metadata={"description": "Medium circuits (21-35 qubits)"},
        )

        large_circuits = RoutingNode(
            name="large_circuits",
            condition="circuit.num_qubits > 35",
            metadata={"description": "Large circuits (>35 qubits)"},
        )

        general_node.children = [small_circuits, medium_circuits, large_circuits]

        # Level 3: Small circuits - hardware optimization
        small_apple_silicon = RoutingNode(
            name="small_apple_silicon",
            condition="is_apple_silicon() and backend_available(BackendType.JAX_METAL)",
            backend=BackendType.JAX_METAL,
            confidence=0.85,
            metadata={"description": "JAX Metal for small circuits on Apple Silicon"},
        )

        small_cuda = RoutingNode(
            name="small_cuda",
            condition="has_cuda() and backend_available(BackendType.CUDA)",
            backend=BackendType.CUDA,
            confidence=0.80,
            metadata={"description": "CUDA for small circuits with GPU"},
        )

        small_qiskit = RoutingNode(
            name="small_qiskit",
            condition="always",
            backend=BackendType.QISKIT,
            confidence=0.75,
            metadata={"description": "Qiskit for small circuits"},
        )

        # Additional options for small circuits (try optional backends before Qiskit fallback)
        small_cirq = RoutingNode(
            name="small_cirq",
            condition="backend_available(BackendType.CIRQ)",
            backend=BackendType.CIRQ,
            confidence=0.70,
            metadata={"description": "Cirq backend for small circuits"},
        )
        small_qulacs = RoutingNode(
            name="small_qulacs",
            condition="backend_available(BackendType.QULACS)",
            backend=BackendType.QULACS,
            confidence=0.72,
            metadata={"description": "Qulacs backend for small circuits"},
        )
        small_pennylane = RoutingNode(
            name="small_pennylane",
            condition="backend_available(BackendType.PENNYLANE)",
            backend=BackendType.PENNYLANE,
            confidence=0.68,
            metadata={"description": "PennyLane backend for small circuits"},
        )

        small_circuits.children = [
            small_apple_silicon,
            small_cuda,
            small_cirq,
            small_qulacs,
            small_pennylane,
            small_qiskit,
        ]

        # Level 3: Medium circuits - entanglement-aware routing
        medium_low_entanglement = RoutingNode(
            name="medium_low_entanglement",
            condition="has_low_entanglement(circuit)",
            metadata={"description": "Medium circuits with low entanglement"},
        )

        medium_high_entanglement = RoutingNode(
            name="medium_high_entanglement",
            condition="not has_low_entanglement(circuit)",
            metadata={"description": "Medium circuits with high entanglement"},
        )

        medium_circuits.children = [medium_low_entanglement, medium_high_entanglement]

        # Level 4: Medium low entanglement
        medium_mps = RoutingNode(
            name="medium_mps",
            condition="backend_available(BackendType.MPS)",
            backend=BackendType.MPS,
            confidence=0.90,
            metadata={"description": "MPS for low-entanglement medium circuits"},
        )

        medium_tensor = RoutingNode(
            name="medium_tensor",
            condition="backend_available(BackendType.TENSOR_NETWORK)",
            backend=BackendType.TENSOR_NETWORK,
            confidence=0.85,
            metadata={"description": "Tensor network for medium circuits"},
        )

        medium_qiskit = RoutingNode(
            name="medium_qiskit_fallback",
            condition="always",
            backend=BackendType.QISKIT,
            confidence=0.60,
            metadata={"description": "Qiskit fallback for medium circuits"},
        )

        medium_low_entanglement.children = [medium_mps, medium_tensor, medium_qiskit]

        # Level 4: Medium high entanglement
        medium_cuda_high = RoutingNode(
            name="medium_cuda_high",
            condition="has_cuda() and backend_available(BackendType.CUDA)",
            backend=BackendType.CUDA,
            confidence=0.80,
            metadata={"description": "CUDA for high-entanglement medium circuits"},
        )

        medium_apple_high = RoutingNode(
            name="medium_apple_high",
            condition="is_apple_silicon() and backend_available(BackendType.JAX_METAL)",
            backend=BackendType.JAX_METAL,
            confidence=0.75,
            metadata={"description": "JAX Metal for high-entanglement medium circuits"},
        )

        # Optional alternatives for medium high entanglement
        medium_opencl = RoutingNode(
            name="medium_opencl",
            condition="backend_available(BackendType.OPENCL)",
            backend=BackendType.OPENCL,
            confidence=0.60,
            metadata={"description": "OpenCL backend for medium circuits"},
        )
        medium_cirq = RoutingNode(
            name="medium_cirq",
            condition="backend_available(BackendType.CIRQ)",
            backend=BackendType.CIRQ,
            confidence=0.62,
            metadata={"description": "Cirq backend for medium circuits"},
        )
        medium_qulacs = RoutingNode(
            name="medium_qulacs",
            condition="backend_available(BackendType.QULACS)",
            backend=BackendType.QULACS,
            confidence=0.65,
            metadata={"description": "Qulacs backend for medium circuits"},
        )

        medium_high_entanglement.children = [
            medium_cuda_high,
            medium_apple_high,
            medium_opencl,
            medium_cirq,
            medium_qulacs,
            medium_qiskit,
        ]

        # Level 3: Large circuits - specialized backends only
        large_mps = RoutingNode(
            name="large_mps",
            condition="has_low_entanglement(circuit) and backend_available(BackendType.MPS)",
            backend=BackendType.MPS,
            confidence=0.95,
            metadata={"description": "MPS for large low-entanglement circuits"},
        )

        large_tensor = RoutingNode(
            name="large_tensor",
            condition="backend_available(BackendType.TENSOR_NETWORK)",
            backend=BackendType.TENSOR_NETWORK,
            confidence=0.85,
            metadata={"description": "Tensor network for large circuits"},
        )

        large_ddsim = RoutingNode(
            name="large_ddsim",
            condition="backend_available(BackendType.DDSIM)",
            backend=BackendType.DDSIM,
            confidence=0.70,
            metadata={"description": "DDSIM for large circuits"},
        )

        # For completeness, include experimental large-circuit fallbacks
        large_braket = RoutingNode(
            name="large_braket",
            condition="backend_available(BackendType.BRAKET)",
            backend=BackendType.BRAKET,
            confidence=0.40,
            metadata={"description": "Braket local simulators (experimental)"},
        )
        large_qsharp = RoutingNode(
            name="large_qsharp",
            condition="backend_available(BackendType.QSHARP)",
            backend=BackendType.QSHARP,
            confidence=0.35,
            metadata={"description": "Q# simulator (experimental)"},
        )

        large_fail = RoutingNode(
            name="large_fail",
            condition="always",
            backend=BackendType.QISKIT,  # Will likely fail but is the fallback
            confidence=0.10,
            metadata={"description": "Qiskit fallback for large circuits (likely to fail)"},
        )

        large_circuits.children = [
            large_mps,
            large_tensor,
            large_ddsim,
            large_braket,
            large_qsharp,
            large_fail,
        ]

        return root

    def route_circuit(
        self,
        circuit: QuantumCircuit,
        strategy: RoutingStrategy = RoutingStrategy.AUTO_DETECT,
        user_context: UserContext | None = None,
    ) -> RoutingDecision:
        """
        Route a quantum circuit using the comprehensive decision tree.

        Args:
            circuit: The quantum circuit to route
            strategy: The routing strategy to use
            user_context: Optional user context for intelligent routing

        Returns:
            A routing decision with backend selection and reasoning
        """
        if user_context is None:
            user_context = self._detect_user_context()

        # Apply strategy-specific modifications to the tree traversal
        if strategy == RoutingStrategy.CLIFFORD_OPTIMIZED:
            return self._clifford_optimized_routing(circuit, user_context)
        elif strategy == RoutingStrategy.APPLE_SILICON_OPTIMIZED:
            return self._apple_silicon_routing(circuit, user_context)
        elif strategy == RoutingStrategy.CUDA_OPTIMIZED:
            return self._cuda_routing(circuit, user_context)
        elif strategy == RoutingStrategy.MEMORY_EFFICIENT:
            return self._memory_efficient_routing(circuit, user_context)
        else:
            # Default tree traversal
            return self._traverse_tree(self.tree, circuit, user_context)

    def _traverse_tree(self, node: RoutingNode, circuit: QuantumCircuit, context: UserContext) -> RoutingDecision:
        """Traverse the routing tree to find the best backend."""

        # If this node has a backend and is available, consider it
        if node.backend and self.backend_availability.get(node.backend, False):
            return RoutingDecision(
                circuit_entropy=0.5,  # Default entropy
                recommended_backend=node.backend,
                confidence_score=node.confidence,
                expected_speedup=2.0,  # Default speedup
                channel_capacity_match=1.0,
                alternatives=[],
            )

        # Otherwise, traverse children
        for child in node.children:
            if self._evaluate_condition(child.condition, circuit, context):
                return self._traverse_tree(child, circuit, context)

        # Fallback to default
        return RoutingDecision(
            circuit_entropy=0.5,
            recommended_backend=node.fallback,
            confidence_score=0.5,
            expected_speedup=1.0,
            channel_capacity_match=0.5,
            alternatives=[],
        )

    def _evaluate_condition(self, condition: str, circuit: QuantumCircuit, context: UserContext) -> bool:
        """Evaluate a routing condition."""

        if condition == "always":
            return True
        elif condition == "is_clifford_circuit(circuit)":
            return is_clifford_circuit(circuit)
        elif condition == "not is_clifford_circuit(circuit)":
            return not is_clifford_circuit(circuit)
        elif condition == "circuit.num_qubits <= 20":
            return circuit.num_qubits <= 20
        elif condition == "20 < circuit.num_qubits <= 35":
            return 20 < circuit.num_qubits <= 35
        elif condition == "circuit.num_qubits > 35":
            return circuit.num_qubits > 35
        elif condition == "is_apple_silicon()":
            return self._is_apple_silicon()
        elif condition == "has_cuda()":
            return self._has_cuda()
        elif condition == "has_low_entanglement(circuit)":
            return self._has_low_entanglement(circuit)
        elif "backend_available" in condition:
            # Extract backend type from condition
            backend_name = condition.split("BackendType.")[1].rstrip(")")
            backend_type = BackendType(backend_name.lower())
            return self.backend_availability.get(backend_type, False)
        else:
            return False

    def _detect_user_context(self) -> UserContext:
        """Detect user context automatically."""
        return detect_user_context()

    def _is_apple_silicon(self) -> bool:
        """Check if running on Apple Silicon."""
        return platform.system() == "Darwin" and platform.machine() in ["arm64", "aarch64"]

    def _has_cuda(self) -> bool:
        """Check if CUDA is available."""
        return self.backend_availability.get(BackendType.CUDA, False)

    def _has_low_entanglement(self, circuit: QuantumCircuit) -> bool:
        """Check if circuit has low entanglement."""
        return should_use_mps(circuit)

    def _clifford_optimized_routing(self, circuit: QuantumCircuit, context: UserContext) -> RoutingDecision:
        """Routing optimized for Clifford circuits."""
        if is_clifford_circuit(circuit):
            if self.backend_availability.get(BackendType.STIM, False):
                return RoutingDecision(
                    circuit_entropy=0.1,
                    recommended_backend=BackendType.STIM,
                    confidence_score=0.95,
                    expected_speedup=10.0,
                    channel_capacity_match=1.0,
                    alternatives=[(BackendType.QISKIT, 0.7)],
                )

        # Fallback to general routing
        return self._traverse_tree(self.tree, circuit, context)

    def _apple_silicon_routing(self, circuit: QuantumCircuit, context: UserContext) -> RoutingDecision:
        """Routing optimized for Apple Silicon."""
        if self._is_apple_silicon() and self.backend_availability.get(BackendType.JAX_METAL, False):
            return RoutingDecision(
                circuit_entropy=0.5,
                recommended_backend=BackendType.JAX_METAL,
                confidence_score=0.85,
                expected_speedup=2.0,
                channel_capacity_match=0.9,
                alternatives=[(BackendType.QISKIT, 0.7)],
            )

        return self._traverse_tree(self.tree, circuit, context)

    def _cuda_routing(self, circuit: QuantumCircuit, context: UserContext) -> RoutingDecision:
        """Routing optimized for CUDA."""
        if self._has_cuda():
            return RoutingDecision(
                circuit_entropy=0.5,
                recommended_backend=BackendType.CUDA,
                confidence_score=0.85,
                expected_speedup=3.0,
                channel_capacity_match=0.9,
                alternatives=[(BackendType.QISKIT, 0.7)],
            )

        return self._traverse_tree(self.tree, circuit, context)

    def _memory_efficient_routing(self, circuit: QuantumCircuit, context: UserContext) -> RoutingDecision:
        """Routing optimized for memory efficiency."""
        if circuit.num_qubits > 30 and self._has_low_entanglement(circuit):
            if self.backend_availability.get(BackendType.MPS, False):
                return RoutingDecision(
                    circuit_entropy=0.2,
                    recommended_backend=BackendType.MPS,
                    confidence_score=0.90,
                    expected_speedup=5.0,
                    channel_capacity_match=0.95,
                    alternatives=[(BackendType.TENSOR_NETWORK, 0.8)],
                )

        return self._traverse_tree(self.tree, circuit, context)

    def get_routing_explanation(self, circuit: QuantumCircuit) -> str:
        """Get a detailed explanation of why a particular routing was chosen."""
        decision = self.route_circuit(circuit)

        analysis_details = analyze_circuit(circuit)
        backend_availability_lines = "\n".join(
            f"- {backend.value}: {'✅' if available else '❌'}"
            for backend, available in self.backend_availability.items()
        )
        alternatives_text = (
            "\n".join(f"- {backend.value}: confidence {score:.2f}" for backend, score in decision.alternatives)
            if decision.alternatives
            else "  (no alternatives)"
        )
        analysis_summary = "\n".join(f"- {key}: {value}" for key, value in analysis_details.items())

        explanation = f"""
Routing Decision Explanation:
============================

Circuit Properties:
- Qubits: {circuit.num_qubits}
- Gates: {len(circuit)}
- Depth: {circuit.depth()}
- Is Clifford: {is_clifford_circuit(circuit)}
- Estimated Entanglement: {"Low" if should_use_mps(circuit) else "High"}

Hardware Environment:
- Platform: {platform.system()} {platform.machine()}
- Apple Silicon: {self._is_apple_silicon()}
- CUDA Available: {self._has_cuda()}

Backend Availability:
{backend_availability_lines}

Selected Backend: {decision.recommended_backend.value}
Confidence: {decision.confidence_score:.2f}
Expected Speedup: {decision.expected_speedup:.2f}x
Channel Capacity Match: {decision.channel_capacity_match:.2f}
Alternatives:
{alternatives_text}

Analysis Details:
{analysis_summary}
        """

        return explanation

    def visualize_routing_tree(self) -> str:
        """Generate a text visualization of the routing tree."""

        def _visualize_node(node: RoutingNode, depth: int = 0) -> str:
            indent = "  " * depth
            icon = "🎯" if node.backend else "🔍"

            result = f"{indent}{icon} {node.name}"
            if node.backend:
                result += f" → {node.backend.value} (confidence: {node.confidence:.2f})"
            result += f"\n{indent}   └─ {node.condition}\n"

            for child in node.children:
                result += _visualize_node(child, depth + 1)

            return result

        return "Ariadne Routing Tree:\n" + "=" * 25 + "\n" + _visualize_node(self.tree)


# Global instance
_routing_tree: ComprehensiveRoutingTree | None = None


def get_routing_tree() -> ComprehensiveRoutingTree:
    """Get the global routing tree instance."""
    global _routing_tree
    if _routing_tree is None:
        _routing_tree = ComprehensiveRoutingTree()
    return _routing_tree


def route_with_tree(
    circuit: QuantumCircuit, strategy: RoutingStrategy = RoutingStrategy.AUTO_DETECT
) -> RoutingDecision:
    """Route a circuit using the comprehensive routing tree."""
    tree = get_routing_tree()
    return tree.route_circuit(circuit, strategy)


def explain_routing(circuit: QuantumCircuit) -> str:
    """Get a detailed explanation of routing decision."""
    tree = get_routing_tree()
    return tree.get_routing_explanation(circuit)


def show_routing_tree() -> str:
    """Show the routing tree structure."""
    tree = get_routing_tree()
    return tree.visualize_routing_tree()
