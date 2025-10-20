"""
Mathematical/Heuristic Performance Prediction System

This module uses mathematical models and circuit features to predict quantum circuit
execution performance across different backends, enabling intelligent routing decisions.
"""

from __future__ import annotations

import math
import warnings
from dataclasses import dataclass

from qiskit import QuantumCircuit

from ..router import BackendType


@dataclass
class CircuitFeatures:
    """Extracted features from quantum circuits for performance models."""

    num_qubits: int
    depth: int
    gate_count: int
    two_qubit_gate_count: int
    single_qubit_gate_count: int
    gate_entropy: float
    connectivity_index: float
    clifford_ratio: float
    parallelization_factor: float
    entanglement_complexity: float


@dataclass
class PerformanceMetrics:
    """Performance metrics for circuit execution."""

    execution_time: float
    memory_usage_mb: float
    success_probability: float
    accuracy_score: float
    energy_consumption: float


@dataclass
class PredictionResult:
    """Result of performance prediction."""

    backend: BackendType
    predicted_time: float
    predicted_memory_mb: float
    predicted_success_rate: float
    confidence_score: float
    feature_importance: dict[str, float]


class CircuitFeatureExtractor:
    """Extract mathematical features from quantum circuits."""

    def extract_features(self, circuit: QuantumCircuit) -> CircuitFeatures:
        """Extract comprehensive features from a quantum circuit."""

        # Basic circuit metrics
        num_qubits = circuit.num_qubits
        depth = circuit.depth()

        # Gate analysis
        gate_counts = self._count_gates(circuit)
        gate_count = sum(gate_counts.values())
        two_qubit_gate_count = self._count_two_qubit_gates(circuit)
        single_qubit_gate_count = gate_count - two_qubit_gate_count

        # Advanced metrics
        gate_entropy = self._calculate_gate_entropy(circuit)
        connectivity_index = self._calculate_connectivity_index(circuit)
        clifford_ratio = self._calculate_clifford_ratio(circuit)
        parallelization_factor = self._calculate_parallelization_factor(circuit)
        entanglement_complexity = self._estimate_entanglement_complexity(circuit)

        return CircuitFeatures(
            num_qubits=num_qubits,
            depth=depth,
            gate_count=gate_count,
            two_qubit_gate_count=two_qubit_gate_count,
            single_qubit_gate_count=single_qubit_gate_count,
            gate_entropy=gate_entropy,
            connectivity_index=connectivity_index,
            clifford_ratio=clifford_ratio,
            parallelization_factor=parallelization_factor,
            entanglement_complexity=entanglement_complexity,
        )

    def _count_gates(self, circuit: QuantumCircuit) -> dict[str, int]:
        """Count gates by type."""
        gate_counts = {}
        for instruction, _, _ in circuit.data:
            if instruction.name not in ["measure", "barrier", "delay"]:
                gate_counts[instruction.name] = gate_counts.get(instruction.name, 0) + 1
        return gate_counts

    def _count_two_qubit_gates(self, circuit: QuantumCircuit) -> int:
        """Count two-qubit gates."""
        count = 0
        for instruction, _, _ in circuit.data:
            if instruction.num_qubits == 2 and instruction.name not in ["measure", "barrier"]:
                count += 1
        return count

    def _calculate_gate_entropy(self, circuit: QuantumCircuit) -> float:
        """Calculate Shannon entropy of gate distribution."""
        gate_counts = self._count_gates(circuit)
        total_gates = sum(gate_counts.values())

        if total_gates == 0:
            return 0.0

        entropy = 0.0
        for count in gate_counts.values():
            if count > 0:
                p = count / total_gates
                entropy -= p * math.log2(p)

        return entropy

    def _calculate_connectivity_index(self, circuit: QuantumCircuit) -> float:
        """Calculate connectivity complexity of the circuit."""
        if circuit.num_qubits <= 1:
            return 0.0

        # Count unique qubit pairs involved in two-qubit gates
        qubit_pairs = set()
        qubit_map = {qubit: i for i, qubit in enumerate(circuit.qubits)}

        for instruction, qubits, _ in circuit.data:
            if instruction.num_qubits == 2:
                q1, q2 = qubits
                i1, i2 = qubit_map[q1], qubit_map[q2]
                qubit_pairs.add(tuple(sorted([i1, i2])))

        max_pairs = circuit.num_qubits * (circuit.num_qubits - 1) // 2
        return len(qubit_pairs) / max_pairs if max_pairs > 0 else 0.0

    def _calculate_clifford_ratio(self, circuit: QuantumCircuit) -> float:
        """Calculate ratio of Clifford gates."""
        clifford_gates = {"h", "x", "y", "z", "s", "sdg", "sx", "sxdg", "cx", "cz", "swap"}

        total_gates = 0
        clifford_count = 0

        for instruction, _, _ in circuit.data:
            if instruction.name not in ["measure", "barrier", "delay"]:
                total_gates += 1
                if instruction.name in clifford_gates:
                    clifford_count += 1

        return clifford_count / total_gates if total_gates > 0 else 1.0

    def _calculate_parallelization_factor(self, circuit: QuantumCircuit) -> float:
        """Calculate how parallelizable the circuit is."""
        if circuit.depth() == 0:
            return 1.0

        total_gates = sum(1 for inst, _, _ in circuit.data if inst.name not in ["measure", "barrier", "delay"])

        return total_gates / circuit.depth() if circuit.depth() > 0 else 1.0

    def _estimate_entanglement_complexity(self, circuit: QuantumCircuit) -> float:
        """Estimate entanglement generation complexity."""
        two_qubit_gates = self._count_two_qubit_gates(circuit)

        if circuit.num_qubits <= 1 or two_qubit_gates == 0:
            return 0.0

        # Normalize by maximum possible entanglement
        max_entanglement = circuit.num_qubits * (circuit.num_qubits - 1) // 2
        normalized_gates = two_qubit_gates / max_entanglement

        # Apply saturation function
        return 1.0 - math.exp(-normalized_gates)


class PerformanceModel:
    """Heuristic-based performance model."""

    def __init__(self):
        # Empirically derived performance coefficients
        self.backend_base_times = {
            BackendType.STIM: 0.001,
            BackendType.QISKIT: 0.01,
            BackendType.JAX_METAL: 0.005,
            BackendType.CUDA: 0.003,
            BackendType.TENSOR_NETWORK: 0.02,
            BackendType.DDSIM: 0.008,
        }

        self.scaling_factors = {
            BackendType.STIM: {"qubits": 1.0, "depth": 1.0},  # Linear for Clifford
            BackendType.QISKIT: {"qubits": 2.0, "depth": 1.2},  # Exponential scaling
            BackendType.JAX_METAL: {"qubits": 1.8, "depth": 1.1},  # GPU acceleration
            BackendType.CUDA: {"qubits": 1.5, "depth": 1.1},  # Better GPU acceleration
            BackendType.TENSOR_NETWORK: {"qubits": 1.3, "depth": 1.5},  # Good for structure
            BackendType.DDSIM: {"qubits": 1.6, "depth": 1.2},  # Decision diagram efficiency
        }

    def predict_execution_time(self, features: CircuitFeatures, backend: BackendType) -> float:
        """Predict execution time using heuristic model."""
        base_time = self.backend_base_times.get(backend, 0.01)
        scaling = self.scaling_factors.get(backend, {"qubits": 2.0, "depth": 1.2})

        # Special case for Clifford circuits with Stim
        if backend == BackendType.STIM and features.clifford_ratio > 0.95:
            # Polynomial scaling for Clifford circuits
            time_estimate = base_time * (features.num_qubits**2) * math.log(features.depth + 1)
        else:
            # Exponential scaling for general circuits
            qubit_factor = scaling["qubits"] ** features.num_qubits
            depth_factor = scaling["depth"] ** features.depth
            time_estimate = base_time * qubit_factor * depth_factor

        # Apply circuit complexity adjustments
        complexity_factor = 1.0 + features.entanglement_complexity * 0.5
        parallelization_bonus = 1.0 / (1.0 + features.parallelization_factor * 0.1)

        return time_estimate * complexity_factor * parallelization_bonus

    def predict_memory_usage(self, features: CircuitFeatures, backend: BackendType) -> float:
        """Predict memory usage in MB."""
        # Base memory usage (state vector simulation)
        if backend == BackendType.STIM and features.clifford_ratio > 0.95:
            # Polynomial memory for Clifford circuits
            memory_mb = 0.1 * features.num_qubits**2
        else:
            # Exponential memory for general circuits (complex128 state vector)
            state_vector_size = 2**features.num_qubits * 16  # bytes
            memory_mb = state_vector_size / (1024 * 1024)

        # Backend-specific adjustments
        if backend == BackendType.TENSOR_NETWORK:
            memory_mb *= 0.3  # Tensor contraction is memory efficient
        elif backend in [BackendType.JAX_METAL, BackendType.CUDA]:
            memory_mb *= 1.2  # GPU memory overhead

        return max(1.0, memory_mb)  # Minimum 1MB

    def predict_success_rate(self, features: CircuitFeatures, backend: BackendType) -> float:
        """Predict execution success probability."""
        base_success = 0.98

        # Larger circuits are more likely to fail
        size_penalty = min(0.1, features.num_qubits * 0.005)

        # Complex circuits are more likely to fail
        complexity_penalty = features.entanglement_complexity * 0.05

        # Backend-specific reliability
        backend_reliability = {
            BackendType.QISKIT: 0.95,
            BackendType.STIM: 0.99,
            BackendType.JAX_METAL: 0.93,
            BackendType.CUDA: 0.92,
            BackendType.TENSOR_NETWORK: 0.88,
            BackendType.DDSIM: 0.94,
        }

        backend_factor = backend_reliability.get(backend, 0.90)

        success_rate = base_success * backend_factor - size_penalty - complexity_penalty
        return max(0.1, min(1.0, success_rate))


class PerformancePredictor:
    """Main performance prediction interface."""

    def __init__(self):
        self.feature_extractor = CircuitFeatureExtractor()
        self.model = PerformanceModel()

    def predict_performance(self, circuit: QuantumCircuit, backend: BackendType) -> PredictionResult:
        """Predict performance for circuit on given backend."""
        features = self.feature_extractor.extract_features(circuit)

        # Use the heuristic model directly
        predicted_time = self.model.predict_execution_time(features, backend)
        predicted_memory = self.model.predict_memory_usage(features, backend)
        predicted_success = self.model.predict_success_rate(features, backend)

        return PredictionResult(
            backend=backend,
            predicted_time=predicted_time,
            predicted_memory_mb=predicted_memory,
            predicted_success_rate=predicted_success,
            confidence_score=0.6,  # Confidence score for heuristic model
            feature_importance={
                "num_qubits": 0.4,
                "depth": 0.3,
                "clifford_ratio": 0.2,
                "entanglement_complexity": 0.1,
            },
        )

    def record_actual_performance(
        self,
        circuit: QuantumCircuit,
        backend: BackendType,
        execution_time: float,
        memory_usage_mb: float = 0.0,
        success: bool = True,
    ) -> None:
        """Record actual performance (logging hook for future analysis)."""
        # This function currently serves as a placeholder or logging hook.
        # We keep it to avoid breaking external calls, but it does nothing related to training.
        warnings.warn(
            "Performance recording is currently a no-op (no training performed).",
            stacklevel=2,
        )
        pass

    def get_best_backend_for_circuit(
        self,
        circuit: QuantumCircuit,
        available_backends: list[BackendType],
        optimize_for: str = "time",
    ) -> tuple[BackendType, PredictionResult]:
        """Find best backend for circuit based on optimization criterion."""
        predictions = {}

        for backend in available_backends:
            predictions[backend] = self.predict_performance(circuit, backend)

        if optimize_for == "time":
            best_backend = min(predictions.keys(), key=lambda b: predictions[b].predicted_time)
        elif optimize_for == "memory":
            best_backend = min(predictions.keys(), key=lambda b: predictions[b].predicted_memory_mb)
        elif optimize_for == "success":
            best_backend = max(predictions.keys(), key=lambda b: predictions[b].predicted_success_rate)
        else:
            # Default to time optimization
            best_backend = min(predictions.keys(), key=lambda b: predictions[b].predicted_time)

        return best_backend, predictions[best_backend]


# Convenience functions
def predict_circuit_performance(circuit: QuantumCircuit, backend: BackendType) -> PredictionResult:
    """Convenience function to predict circuit performance."""
    predictor = PerformancePredictor()
    return predictor.predict_performance(circuit, backend)


def find_optimal_backend(
    circuit: QuantumCircuit, available_backends: list[BackendType], optimize_for: str = "time"
) -> tuple[BackendType, PredictionResult]:
    """Convenience function to find optimal backend."""
    predictor = PerformancePredictor()
    return predictor.get_best_backend_for_circuit(circuit, available_backends, optimize_for)
