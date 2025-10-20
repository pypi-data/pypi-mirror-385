"""
Quantum Advantage Detection Algorithms

This module provides algorithms to detect when quantum circuits exhibit
characteristics that provide computational advantages over classical algorithms.
"""

from __future__ import annotations

import math
from typing import Any

from qiskit import QuantumCircuit

from ariadne.route.analyze import analyze_circuit


def detect_quantum_advantage(circuit: QuantumCircuit) -> dict[str, Any]:
    """
    Comprehensive quantum advantage detection analysis.

    Returns a detailed report on potential quantum advantages including:
    - Classical intractability
    - Quantum volume superiority
    - Entanglement complexity
    - Error threshold analysis
    """

    analysis = analyze_circuit(circuit)

    # Core advantage detection algorithms
    classical_intractability = detect_classical_intractability(circuit, analysis)
    quantum_volume_advantage = detect_quantum_volume_advantage(circuit, analysis)
    entanglement_advantage = detect_entanglement_advantage(circuit, analysis)
    error_threshold_analysis = analyze_error_threshold(circuit, analysis)
    sampling_advantage = detect_sampling_advantage(circuit, analysis)

    # Overall quantum advantage score
    advantage_score = calculate_overall_advantage_score(
        {
            "classical_intractability": classical_intractability,
            "quantum_volume_advantage": quantum_volume_advantage,
            "entanglement_advantage": entanglement_advantage,
            "error_threshold": error_threshold_analysis,
            "sampling_advantage": sampling_advantage,
        }
    )

    return {
        "overall_advantage_score": advantage_score,
        "has_quantum_advantage": advantage_score > 0.6,
        "advantage_type": classify_advantage_type(advantage_score, classical_intractability),
        "classical_intractability": classical_intractability,
        "quantum_volume_advantage": quantum_volume_advantage,
        "entanglement_advantage": entanglement_advantage,
        "error_threshold": error_threshold_analysis,
        "sampling_advantage": sampling_advantage,
        "recommendations": generate_recommendations(advantage_score, analysis),
    }


def detect_classical_intractability(circuit: QuantumCircuit, analysis: dict[str, Any]) -> dict[str, Any]:
    """
    Detect if circuit is classically intractable to simulate.

    Considers:
    - Exponential scaling with qubit count
    - Non-Clifford gate complexity
    - Circuit depth and entanglement
    """

    num_qubits = analysis["num_qubits"]
    is_clifford = analysis["is_clifford"]
    depth = analysis["depth"]
    entanglement_entropy = analysis.get("entanglement_entropy_estimate", 0)

    # Clifford circuits are always efficiently simulable
    if is_clifford:
        return {
            "is_intractable": False,
            "reason": "Clifford circuit - polynomial time classical simulation",
            "complexity_class": "P",
            "intractability_score": 0.0,
        }

    # Thresholds for classical intractability
    depth_threshold = 100  # Deep circuits become harder to simulate
    entanglement_threshold = 0.7  # High entanglement suggests complexity

    # Score factors
    qubit_factor = min(1.0, max(0.0, (num_qubits - 20) / 30))  # Scale from 20-50 qubits
    depth_factor = min(1.0, depth / depth_threshold)
    entanglement_factor = min(1.0, entanglement_entropy / entanglement_threshold)

    # Non-Clifford complexity
    clifford_ratio = analysis.get("clifford_ratio", 1.0)
    non_clifford_factor = 1.0 - clifford_ratio

    # Combined intractability score
    intractability_score = (
        0.4 * qubit_factor + 0.2 * depth_factor + 0.2 * entanglement_factor + 0.2 * non_clifford_factor
    )

    # Classify complexity
    if num_qubits >= 50 and non_clifford_factor > 0.1:
        complexity_class = "INTRACTABLE"
    elif num_qubits >= 30 and non_clifford_factor > 0.2:
        complexity_class = "HARD"
    elif num_qubits >= 20:
        complexity_class = "MODERATE"
    else:
        complexity_class = "EASY"

    return {
        "is_intractable": intractability_score > 0.7,
        "intractability_score": intractability_score,
        "complexity_class": complexity_class,
        "factors": {
            "qubit_factor": qubit_factor,
            "depth_factor": depth_factor,
            "entanglement_factor": entanglement_factor,
            "non_clifford_factor": non_clifford_factor,
        },
    }


def detect_quantum_volume_advantage(circuit: QuantumCircuit, analysis: dict[str, Any]) -> dict[str, Any]:
    """
    Detect quantum volume advantage over classical systems.
    """

    quantum_volume = analysis.get("quantum_volume_estimate", 1)
    analysis["num_qubits"]
    analysis["depth"]

    # Current classical simulation limits (approximate)
    classical_volume_limit = 2**30  # ~1 billion state amplitudes

    # IBM quantum volume benchmarks for reference
    quantum_volume_benchmarks = {
        "current_classical": 2**30,
        "near_term_quantum": 2**40,
        "quantum_advantage_threshold": 2**50,
    }

    advantage_score = 0.0
    has_advantage = quantum_volume > classical_volume_limit

    if quantum_volume > quantum_volume_benchmarks["quantum_advantage_threshold"]:
        advantage_level = "STRONG"
        advantage_score = 1.0
    elif quantum_volume > quantum_volume_benchmarks["near_term_quantum"]:
        advantage_level = "MODERATE"
        advantage_score = 0.7
    elif quantum_volume > quantum_volume_benchmarks["current_classical"]:
        advantage_level = "WEAK"
        advantage_score = 0.4
    else:
        advantage_level = "NONE"
        advantage_score = 0.0

    return {
        "has_quantum_volume_advantage": has_advantage,
        "quantum_volume": quantum_volume,
        "advantage_level": advantage_level,
        "advantage_score": advantage_score,
        "classical_limit": classical_volume_limit,
        "quantum_volume_log2": math.log2(quantum_volume) if quantum_volume > 0 else 0,
    }


def detect_entanglement_advantage(circuit: QuantumCircuit, analysis: dict[str, Any]) -> dict[str, Any]:
    """
    Detect advantage from quantum entanglement.
    """

    entanglement_entropy = analysis.get("entanglement_entropy_estimate", 0)
    num_qubits = analysis["num_qubits"]
    two_qubit_gates = sum(
        1
        for inst in circuit.data
        if inst.operation.num_qubits == 2 and inst.operation.name not in ["measure", "barrier"]
    )

    # Maximum possible entanglement entropy
    max_entropy = num_qubits

    # Entanglement metrics
    entanglement_ratio = entanglement_entropy / max_entropy if max_entropy > 0 else 0
    entangling_gate_density = two_qubit_gates / max(1, circuit.depth())

    # Thresholds for entanglement advantage
    high_entanglement_threshold = 0.7
    moderate_entanglement_threshold = 0.4

    if entanglement_ratio > high_entanglement_threshold:
        advantage_level = "HIGH"
        advantage_score = 0.9
    elif entanglement_ratio > moderate_entanglement_threshold:
        advantage_level = "MODERATE"
        advantage_score = 0.6
    else:
        advantage_level = "LOW"
        advantage_score = 0.3

    return {
        "has_entanglement_advantage": entanglement_ratio > moderate_entanglement_threshold,
        "entanglement_entropy": entanglement_entropy,
        "entanglement_ratio": entanglement_ratio,
        "advantage_level": advantage_level,
        "advantage_score": advantage_score,
        "entangling_gate_density": entangling_gate_density,
    }


def analyze_error_threshold(circuit: QuantumCircuit, analysis: dict[str, Any]) -> dict[str, Any]:
    """
    Analyze if circuit can maintain quantum advantage despite noise.
    """

    noise_susceptibility = analysis.get("noise_susceptibility", 0.5)
    depth = analysis["depth"]
    two_qubit_gates = sum(
        1
        for inst in circuit.data
        if inst.operation.num_qubits == 2 and inst.operation.name not in ["measure", "barrier"]
    )

    # Error threshold estimates
    single_qubit_error_rate = 1e-4  # Typical target
    two_qubit_error_rate = 1e-2  # Typical target

    # Estimate total error accumulation
    total_single_qubit_ops = sum(
        1
        for inst in circuit.data
        if inst.operation.num_qubits == 1 and inst.operation.name not in ["measure", "barrier", "delay"]
    )

    estimated_error_rate = total_single_qubit_ops * single_qubit_error_rate + two_qubit_gates * two_qubit_error_rate

    # Error threshold for maintaining advantage
    error_threshold = 0.1  # 10% error threshold for meaningful results

    is_feasible = estimated_error_rate < error_threshold
    noise_tolerance = max(0.0, 1.0 - estimated_error_rate / error_threshold)

    return {
        "is_noise_feasible": is_feasible,
        "estimated_error_rate": estimated_error_rate,
        "error_threshold": error_threshold,
        "noise_tolerance": noise_tolerance,
        "noise_susceptibility": noise_susceptibility,
        "depth_penalty": min(1.0, depth / 1000),  # Normalize depth penalty
        "two_qubit_gate_count": two_qubit_gates,
    }


def detect_sampling_advantage(circuit: QuantumCircuit, analysis: dict[str, Any]) -> dict[str, Any]:
    """
    Detect quantum sampling advantage (like Google's quantum supremacy).
    """

    num_qubits = analysis["num_qubits"]
    depth = analysis["depth"]
    is_clifford = analysis["is_clifford"]
    gate_diversity = analysis.get("gate_diversity", 0)

    # Google's quantum supremacy parameters for reference
    supremacy_qubits = 53
    supremacy_depth = 20

    # Sampling advantage requires non-Clifford gates
    if is_clifford:
        return {
            "has_sampling_advantage": False,
            "reason": "Clifford circuits can be efficiently sampled classically",
            "advantage_score": 0.0,
        }

    # Score based on problem size and complexity
    qubit_score = min(1.0, num_qubits / supremacy_qubits)
    depth_score = min(1.0, depth / supremacy_depth)
    diversity_score = gate_diversity

    # Combined sampling advantage score
    sampling_score = 0.5 * qubit_score + 0.3 * depth_score + 0.2 * diversity_score

    # Classify advantage level
    if sampling_score > 0.8:
        advantage_level = "SUPREMACY"
    elif sampling_score > 0.6:
        advantage_level = "ADVANTAGE"
    elif sampling_score > 0.4:
        advantage_level = "PROMISING"
    else:
        advantage_level = "INSUFFICIENT"

    return {
        "has_sampling_advantage": sampling_score > 0.6,
        "sampling_score": sampling_score,
        "advantage_level": advantage_level,
        "factors": {
            "qubit_score": qubit_score,
            "depth_score": depth_score,
            "diversity_score": diversity_score,
        },
    }


def calculate_overall_advantage_score(components: dict[str, dict[str, Any]]) -> float:
    """
    Calculate overall quantum advantage score from all components.
    """

    # Extract scores from each component
    classical_score = float(components["classical_intractability"].get("intractability_score", 0))
    volume_score = float(components["quantum_volume_advantage"].get("advantage_score", 0))
    entanglement_score = float(components["entanglement_advantage"].get("advantage_score", 0))
    error_score = float(components["error_threshold"].get("noise_tolerance", 0))
    sampling_score = float(components["sampling_advantage"].get("sampling_score", 0))

    # Weighted combination
    overall_score = (
        0.3 * classical_score
        + 0.25 * volume_score
        + 0.2 * entanglement_score
        + 0.15 * error_score
        + 0.1 * sampling_score
    )

    return min(1.0, overall_score)


def classify_advantage_type(overall_score: float, classical_analysis: dict[str, Any]) -> str:
    """
    Classify the type of quantum advantage.
    """

    if overall_score < 0.3:
        return "NO_ADVANTAGE"
    elif overall_score < 0.5:
        return "WEAK_ADVANTAGE"
    elif overall_score < 0.7:
        return "MODERATE_ADVANTAGE"
    elif classical_analysis.get("complexity_class") == "INTRACTABLE":
        return "STRONG_ADVANTAGE"
    else:
        return "POTENTIAL_ADVANTAGE"


def generate_recommendations(advantage_score: float, analysis: dict[str, Any]) -> list[str]:
    """
    Generate recommendations based on quantum advantage analysis.
    """

    recommendations = []

    num_qubits = analysis["num_qubits"]
    is_clifford = analysis["is_clifford"]
    depth = analysis["depth"]

    if advantage_score < 0.3:
        recommendations.append("Circuit unlikely to provide quantum advantage")
        recommendations.append("Consider classical algorithms for this problem")

        if is_clifford:
            recommendations.append("Clifford circuit: Use Stim for efficient classical simulation")

        if num_qubits < 20:
            recommendations.append("Small circuit: Classical simulation is straightforward")

    elif advantage_score < 0.6:
        recommendations.append("Circuit shows potential for quantum advantage")
        recommendations.append("Suitable for near-term quantum devices")

        if depth > 100:
            recommendations.append("Deep circuit: Consider error mitigation techniques")

    else:
        recommendations.append("Circuit likely provides strong quantum advantage")
        recommendations.append("Excellent candidate for quantum hardware")

        if num_qubits > 30:
            recommendations.append("Large circuit: Classical verification will be challenging")

        recommendations.append("Consider quantum error correction for practical implementation")

    return recommendations
