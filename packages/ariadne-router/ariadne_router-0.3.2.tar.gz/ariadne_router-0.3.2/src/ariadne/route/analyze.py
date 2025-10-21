from __future__ import annotations

import math
from typing import Any, cast

import networkx as nx
from qiskit import QuantumCircuit

CLIFFORD_ONE_Q = {"i", "x", "y", "z", "h", "s", "sdg", "sx", "sxdg"}
CLIFFORD_TWO_Q = {"cx", "cz", "swap"}


def is_clifford_circuit(circ: QuantumCircuit, properties: dict[str, Any] | None = None) -> bool:
    if properties is None:
        # Fallback for standalone use
        for inst in circ.data:
            name = inst.operation.name
            if name in {"measure", "barrier", "delay"}:
                continue
            if (name not in CLIFFORD_ONE_Q) and (name not in CLIFFORD_TWO_Q):
                return False
        return True

    # Optimized calculation using pre-calculated properties
    return cast(int, properties.get("total_gates")) == cast(int, properties.get("clifford_gates"))


def _get_circuit_properties(circ: QuantumCircuit) -> dict[str, int | set[str] | dict[str, int]]:
    properties: dict[str, int | set[str] | dict[str, int]] = {
        "total_gates": 0,
        "two_qubit_gates": 0,
        "parameterized_gates": 0,
        "clifford_gates": 0,
        "gate_counts": {},
        "gate_types": set(),
    }

    for inst in circ.data:
        name = inst.operation.name
        if name in {"measure", "barrier", "delay"}:
            continue

        properties["total_gates"] = cast(int, properties["total_gates"]) + 1
        cast(set, properties["gate_types"]).add(name)
        gate_counts = cast(dict, properties["gate_counts"])
        gate_counts[name] = gate_counts.get(name, 0) + 1

        if inst.operation.num_qubits == 2:
            properties["two_qubit_gates"] = cast(int, properties["two_qubit_gates"]) + 1

        if hasattr(inst.operation, "params") and inst.operation.params:
            properties["parameterized_gates"] = cast(int, properties["parameterized_gates"]) + 1

        if (name in CLIFFORD_ONE_Q) or (name in CLIFFORD_TWO_Q):
            properties["clifford_gates"] = cast(int, properties["clifford_gates"]) + 1

    return properties


def calculate_gate_entropy(circ: QuantumCircuit, properties: dict[str, Any] | None = None) -> float:
    """Calculate Shannon entropy of gate distribution."""
    gate_counts: dict[str, int] = {}
    total_gates = 0

    for instruction in circ.data:
        name = instruction.operation.name
        if name not in ["measure", "barrier", "delay"]:
            gate_counts[name] = gate_counts.get(name, 0) + 1
            total_gates += 1

    if total_gates == 0:
        return 0.0

    entropy = 0.0
    for count in gate_counts.values():
        p = count / total_gates
        if p > 0:
            entropy -= p * math.log2(p)

    return entropy


def estimate_entanglement_entropy(circ: QuantumCircuit, properties: dict[str, Any] | None = None) -> float:
    """Estimate the entanglement entropy that will be generated."""
    if properties is None:
        properties = _get_circuit_properties(circ)

    entangling_gates = cast(int, properties["two_qubit_gates"])

    if entangling_gates == 0:
        return 0.0

    # Rough estimate: each two-qubit gate contributes to entanglement
    # Saturates at log2(2^n) = n for n qubits
    max_entropy = circ.num_qubits
    saturation_factor = 1 - math.exp(-entangling_gates / circ.num_qubits)

    return cast(float, max_entropy * saturation_factor)


def estimate_quantum_volume(circ: QuantumCircuit) -> float:
    """Estimate quantum volume based on depth and width."""
    # Quantum volume is 2^m where m = min(depth, width)
    m = min(circ.depth(), circ.num_qubits)
    return float(2**m)


def calculate_parallelization_factor(circ: QuantumCircuit, properties: dict[str, Any] | None = None) -> float:
    """Calculate how much parallelization is possible."""
    if circ.depth() == 0:
        return 1.0

    if properties is None:
        properties = _get_circuit_properties(circ)

    total_gates = cast(int, properties["total_gates"])

    if total_gates == 0:
        return 1.0

    # Parallelization factor = total_gates / depth
    # Higher values indicate more parallel execution possible
    return cast(float, total_gates / circ.depth())


def estimate_noise_susceptibility(circ: QuantumCircuit, properties: dict[str, Any] | None = None) -> float:
    """Estimate circuit's susceptibility to noise."""
    if properties is None:
        properties = _get_circuit_properties(circ)

    total_gates = cast(int, properties["total_gates"])
    two_qubit_gates = cast(int, properties["two_qubit_gates"])

    # Factors: depth (decoherence), two-qubit gates (higher error), total operations
    depth_factor = min(1.0, float(circ.depth()) / 100.0)  # Normalize to reasonable scale

    if total_gates == 0:
        return 0.0

    two_qubit_ratio = float(two_qubit_gates) / float(total_gates)

    # Combine factors (0 = low susceptibility, 1 = high susceptibility)
    susceptibility = 0.6 * depth_factor + 0.4 * two_qubit_ratio
    return float(min(1.0, susceptibility))


def estimate_classical_complexity(circ: QuantumCircuit, properties: dict[str, Any] | None = None) -> float:
    """Estimate classical simulation complexity."""
    if is_clifford_circuit(circ, properties=properties):
        # Clifford circuits are polynomial time
        return float(circ.num_qubits**2)

    # Non-Clifford circuits are exponential
    # Complexity roughly 2^n * depth
    base_complexity = 2**circ.num_qubits
    depth_factor = max(1, circ.depth())

    return float(base_complexity * math.log2(depth_factor + 1))


def calculate_connectivity_score(graph: nx.Graph) -> float:
    """Calculate connectivity score of interaction graph."""
    if graph.number_of_nodes() <= 1:
        return 1.0

    # Density of the graph
    n = graph.number_of_nodes()
    max_edges = n * (n - 1) // 2

    if max_edges == 0:
        return 1.0

    density = float(graph.number_of_edges()) / float(max_edges)

    # Also consider clustering coefficient
    try:
        clustering = float(nx.average_clustering(graph))
    except Exception:
        clustering = 0.0

    # Combine density and clustering
    return 0.7 * density + 0.3 * clustering


def calculate_gate_diversity(circ: QuantumCircuit, properties: dict[str, Any] | None = None) -> float:
    """Calculate diversity of gate types used."""
    if properties is None:
        properties = _get_circuit_properties(circ)

    gate_types = cast(set, properties["gate_types"])
    total_gates = cast(int, properties["total_gates"])

    if total_gates == 0:
        return 0.0

    # Shannon diversity index for gate types
    return len(gate_types) / max(1, math.log2(total_gates + 1))


def calculate_expressivity(circ: QuantumCircuit, properties: dict[str, Any] | None = None) -> float:
    """Calculate circuit expressivity measure."""
    if properties is None:
        properties = _get_circuit_properties(circ)

    gate_types = cast(set, properties["gate_types"])
    total_gates = cast(int, properties["total_gates"])
    entangling_gates = cast(int, properties["two_qubit_gates"])
    parameterized_gates = cast(int, properties["parameterized_gates"])

    # Expressivity relates to how much of Hilbert space the circuit can explore
    # Factors: gate diversity, entangling gates, parameterized gates

    if total_gates == 0:
        return 0.0

    # Normalize components
    type_diversity = len(gate_types) / max(1, math.log2(total_gates + 1))
    entangling_ratio = entangling_gates / total_gates
    param_ratio = parameterized_gates / total_gates

    # Weighted combination
    expressivity = 0.4 * type_diversity + 0.4 * entangling_ratio + 0.2 * param_ratio

    return min(1.0, expressivity)


def interaction_graph(circ: QuantumCircuit) -> nx.Graph:
    g = nx.Graph()
    g.add_nodes_from(range(circ.num_qubits))
    # Qiskit 2.x no longer exposes .index directly, so pre-compute lookup table
    qubit_index_map = {qubit: idx for idx, qubit in enumerate(circ.qubits)}
    for inst in circ.data:
        if inst.operation.num_qubits == 2:
            u, v = (qubit_index_map[q] for q in inst.qubits)
            if u != v:
                g.add_edge(u, v)
    return g


def approximate_treewidth(g: nx.Graph) -> int:
    if g.number_of_nodes() == 0:
        return 0
    try:
        # Use a quick heuristic approximation
        from networkx.algorithms.approximation import treewidth_min_fill_in

        width, _ = treewidth_min_fill_in(g)
        return int(width)
    except Exception:
        return max((deg for _, deg in g.degree()), default=0)


def clifford_ratio(circ: QuantumCircuit, properties: dict[str, Any] | None = None) -> float:
    if properties is None:
        properties = _get_circuit_properties(circ)

    total = cast(int, properties["total_gates"])
    cliff = cast(int, properties["clifford_gates"])

    return float(cliff) / float(total) if total else 1.0


def light_cone_width_estimate(circ: QuantumCircuit) -> int:
    # Simple proxy: max degree of interaction graph
    g = interaction_graph(circ)
    return max((deg for _, deg in g.degree()), default=0)


def two_qubit_depth(circ: QuantumCircuit) -> int:
    depth = 0
    current_layer_qubits: set[int] = set()
    for inst in circ.data:
        if inst.operation.num_qubits == 2:
            # Qiskit 2.x no longer exposes .index directly, so pre-compute lookup table
            qubit_index_map = {qubit: idx for idx, qubit in enumerate(circ.qubits)}
            qubits = {qubit_index_map[q] for q in inst.qubits}
            if current_layer_qubits & qubits:
                depth += 1
                current_layer_qubits = set(qubits)
            else:
                current_layer_qubits |= qubits
    return depth + (1 if current_layer_qubits else 0)


def analyze_circuit(circ: QuantumCircuit) -> dict[str, float | int | bool]:
    """Enhanced circuit analysis with advanced entropy and complexity metrics."""

    # Perform single pass analysis to gather all gate properties
    properties = _get_circuit_properties(circ)
    g = interaction_graph(circ)

    # Basic metrics
    basic_metrics = {
        "num_qubits": circ.num_qubits,
        "depth": int(circ.depth()),
        "two_qubit_depth": two_qubit_depth(circ),
        "edges": g.number_of_edges(),
        "treewidth_estimate": approximate_treewidth(g),
        "light_cone_width": light_cone_width_estimate(circ),
        "clifford_ratio": clifford_ratio(circ, properties=properties),
        "is_clifford": is_clifford_circuit(circ, properties=properties),
    }

    # Advanced entropy and complexity metrics
    advanced_metrics = {
        "gate_entropy": calculate_gate_entropy(circ, properties=properties),
        "entanglement_entropy_estimate": estimate_entanglement_entropy(circ, properties=properties),
        "quantum_volume_estimate": estimate_quantum_volume(circ),
        "parallelization_factor": calculate_parallelization_factor(circ, properties=properties),
        "noise_susceptibility": estimate_noise_susceptibility(circ, properties=properties),
        "classical_simulation_complexity": estimate_classical_complexity(circ, properties=properties),
        "connectivity_score": calculate_connectivity_score(g),
        "gate_diversity": calculate_gate_diversity(circ, properties=properties),
        "expressivity_measure": calculate_expressivity(circ, properties=properties),
    }

    # Combine all metrics
    return {**basic_metrics, **advanced_metrics}


def should_use_tensor_network(circuit: QuantumCircuit, analysis: dict[str, float | int | bool] | None = None) -> bool:
    """Return ``True`` if the circuit should target a tensor network backend."""

    metrics = analysis or analyze_circuit(circuit)

    if metrics["is_clifford"]:
        return False

    num_qubits = int(metrics["num_qubits"])
    if num_qubits <= 4:
        return False
    if num_qubits > 30:
        return False

    return True
