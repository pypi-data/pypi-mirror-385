"""
Multi-Objective Optimization Framework for Quantum Circuit Routing

This module implements sophisticated multi-objective optimization algorithms
to balance performance, accuracy, memory usage, energy consumption, and cost
when selecting optimal backends for quantum circuit simulation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Any

from qiskit import QuantumCircuit

from ..route.analyze import analyze_circuit
from ..route.enhanced_router import UserContext
from ..route.performance_model import PerformancePredictor, PredictionResult
from ..router import BackendType


class OptimizationObjective(Enum):
    """Different optimization objectives."""

    MINIMIZE_TIME = "minimize_time"
    MINIMIZE_MEMORY = "minimize_memory"
    MINIMIZE_ENERGY = "minimize_energy"
    MINIMIZE_COST = "minimize_cost"
    MAXIMIZE_ACCURACY = "maximize_accuracy"
    MAXIMIZE_SUCCESS_RATE = "maximize_success_rate"
    MAXIMIZE_RELIABILITY = "maximize_reliability"


@dataclass
class ObjectiveWeight:
    """Weight configuration for multi-objective optimization."""

    time_weight: float = 0.3
    memory_weight: float = 0.2
    energy_weight: float = 0.15
    cost_weight: float = 0.1
    accuracy_weight: float = 0.15
    success_rate_weight: float = 0.1

    def normalize(self) -> ObjectiveWeight:
        """Normalize weights to sum to 1.0."""
        total = (
            self.time_weight
            + self.memory_weight
            + self.energy_weight
            + self.cost_weight
            + self.accuracy_weight
            + self.success_rate_weight
        )

        if total == 0:
            return ObjectiveWeight()  # Default equal weights

        return ObjectiveWeight(
            time_weight=self.time_weight / total,
            memory_weight=self.memory_weight / total,
            energy_weight=self.energy_weight / total,
            cost_weight=self.cost_weight / total,
            accuracy_weight=self.accuracy_weight / total,
            success_rate_weight=self.success_rate_weight / total,
        )


@dataclass
class OptimizationResult:
    """Result of multi-objective optimization."""

    backend: BackendType
    total_score: float
    objective_scores: dict[str, float]
    trade_off_analysis: dict[str, Any]
    pareto_rank: int
    dominated_solutions: list[BackendType]
    dominates_solutions: list[BackendType]


@dataclass
class BackendObjectiveScores:
    """Objective scores for a backend."""

    backend: BackendType
    time_score: float
    memory_score: float
    energy_score: float
    cost_score: float
    accuracy_score: float
    success_rate_score: float

    @property
    def objective_scores(self) -> dict[str, float]:
        """Get all objective scores as a dictionary."""
        return {
            "time": self.time_score,
            "memory": self.memory_score,
            "energy": self.energy_score,
            "cost": self.cost_score,
            "accuracy": self.accuracy_score,
            "success_rate": self.success_rate_score,
        }

    def get_score(self, objective: OptimizationObjective) -> float:
        """Get score for specific objective."""
        if objective == OptimizationObjective.MINIMIZE_TIME:
            return self.time_score
        elif objective == OptimizationObjective.MINIMIZE_MEMORY:
            return self.memory_score
        elif objective == OptimizationObjective.MINIMIZE_ENERGY:
            return self.energy_score
        elif objective == OptimizationObjective.MINIMIZE_COST:
            return self.cost_score
        elif objective == OptimizationObjective.MAXIMIZE_ACCURACY:
            return self.accuracy_score
        elif objective == OptimizationObjective.MAXIMIZE_SUCCESS_RATE:
            return self.success_rate_score
        else:
            return 0.0


class ParetoOptimizer:
    """Pareto-optimal solution finder for multi-objective optimization."""

    def find_pareto_front(self, solutions: list[BackendObjectiveScores]) -> list[BackendObjectiveScores]:
        """Find Pareto-optimal solutions."""
        pareto_front = []

        for candidate in solutions:
            is_dominated = False

            for other in solutions:
                if self._dominates(other, candidate):
                    is_dominated = True
                    break

            if not is_dominated:
                pareto_front.append(candidate)

        return pareto_front

    def _dominates(self, solution_a: BackendObjectiveScores, solution_b: BackendObjectiveScores) -> bool:
        """Check if solution A dominates solution B."""
        # Solution A dominates B if A is better or equal in all objectives
        # and strictly better in at least one objective

        objectives = [
            OptimizationObjective.MINIMIZE_TIME,
            OptimizationObjective.MINIMIZE_MEMORY,
            OptimizationObjective.MINIMIZE_ENERGY,
            OptimizationObjective.MINIMIZE_COST,
            OptimizationObjective.MAXIMIZE_ACCURACY,
            OptimizationObjective.MAXIMIZE_SUCCESS_RATE,
        ]

        better_count = 0
        equal_or_better_count = 0

        for objective in objectives:
            score_a = solution_a.get_score(objective)
            score_b = solution_b.get_score(objective)

            if objective in [
                OptimizationObjective.MINIMIZE_TIME,
                OptimizationObjective.MINIMIZE_MEMORY,
                OptimizationObjective.MINIMIZE_ENERGY,
                OptimizationObjective.MINIMIZE_COST,
            ]:
                # For minimization objectives, lower is better
                if score_a < score_b:
                    better_count += 1
                    equal_or_better_count += 1
                elif score_a == score_b:
                    equal_or_better_count += 1
            else:
                # For maximization objectives, higher is better
                if score_a > score_b:
                    better_count += 1
                    equal_or_better_count += 1
                elif score_a == score_b:
                    equal_or_better_count += 1

        return equal_or_better_count == len(objectives) and better_count > 0

    def rank_solutions(self, solutions: list[BackendObjectiveScores]) -> dict[BackendObjectiveScores, int]:
        """Assign Pareto ranks to solutions (0 = best)."""
        remaining_solutions = solutions.copy()
        ranks = {}
        current_rank = 0

        while remaining_solutions:
            pareto_front = self.find_pareto_front(remaining_solutions)

            for solution in pareto_front:
                ranks[solution] = current_rank
                remaining_solutions.remove(solution)

            current_rank += 1

        return ranks


class ObjectiveScorer:
    """Score backends against various objectives."""

    def __init__(self, performance_predictor: PerformancePredictor | None = None):
        self.performance_predictor = performance_predictor or PerformancePredictor()

    def score_backend_objectives(
        self, circuit: QuantumCircuit, backend: BackendType, context: UserContext
    ) -> BackendObjectiveScores:
        """Score a backend against all objectives."""

        # Get performance prediction
        prediction = self.performance_predictor.predict_performance(circuit, backend)
        analysis = analyze_circuit(circuit)

        # Score each objective (normalized to 0-1 scale, higher is better)
        time_score = self._score_execution_time(prediction.predicted_time)
        memory_score = self._score_memory_usage(prediction.predicted_memory_mb, context)
        energy_score = self._score_energy_consumption(backend, analysis, context)
        cost_score = self._score_computational_cost(backend, prediction)
        accuracy_score = self._score_accuracy(backend, analysis)
        success_rate_score = prediction.predicted_success_rate

        return BackendObjectiveScores(
            backend=backend,
            time_score=time_score,
            memory_score=memory_score,
            energy_score=energy_score,
            cost_score=cost_score,
            accuracy_score=accuracy_score,
            success_rate_score=success_rate_score,
        )

    def _score_execution_time(self, predicted_time: float) -> float:
        """Score execution time (lower time = higher score)."""
        # Use logarithmic scaling to handle wide range of execution times
        # Score of 1.0 for 0.001s, score of 0.0 for 1000s
        log_time = math.log10(max(predicted_time, 0.0001))
        log_min = math.log10(0.001)  # -3
        log_max = math.log10(1000)  # 3

        normalized = (log_max - log_time) / (log_max - log_min)
        return max(0.0, min(1.0, normalized))

    def _score_memory_usage(self, predicted_memory_mb: float, context: UserContext) -> float:
        """Score memory usage considering available system memory."""
        system_memory_mb = context.hardware_profile.total_memory_gb * 1024
        memory_ratio = predicted_memory_mb / system_memory_mb

        # Higher score for lower memory usage
        if memory_ratio <= 0.1:  # Uses <= 10% of system memory
            return 1.0
        elif memory_ratio <= 0.5:  # Uses <= 50% of system memory
            return 0.8
        elif memory_ratio <= 0.8:  # Uses <= 80% of system memory
            return 0.5
        else:  # Uses > 80% of system memory
            return 0.1

    def _score_energy_consumption(self, backend: BackendType, analysis: dict[str, Any], context: UserContext) -> float:
        """Score energy consumption (lower consumption = higher score)."""
        # Base energy scores for backends (higher = more energy efficient)
        base_energy_scores = {
            BackendType.STIM: 0.95,
            BackendType.TENSOR_NETWORK: 0.8,
            BackendType.DDSIM: 0.75,
            BackendType.QISKIT: 0.7,
            BackendType.JAX_METAL: 0.6,
            BackendType.CUDA: 0.4,
        }

        base_score = base_energy_scores.get(backend, 0.5)

        # Adjust for circuit size (larger circuits consume more energy)
        size_factor = 1.0 / (1.0 + analysis["num_qubits"] * 0.02)

        # Adjust for Apple Silicon efficiency
        if context.hardware_profile.apple_silicon and backend in [
            BackendType.JAX_METAL,
            BackendType.QISKIT,
        ]:
            base_score *= 1.2

        return min(1.0, base_score * size_factor)

    def _score_computational_cost(self, backend: BackendType, prediction: PredictionResult) -> float:
        """Score computational cost (lower cost = higher score)."""
        # Simplified cost model based on execution time and resource usage
        time_cost = prediction.predicted_time
        memory_cost = prediction.predicted_memory_mb / 1024  # GB

        # Different backends have different cost structures
        backend_cost_factors = {
            BackendType.STIM: 0.1,  # Very cheap for Clifford circuits
            BackendType.QISKIT: 1.0,  # Baseline cost
            BackendType.JAX_METAL: 0.8,  # Slightly cheaper due to efficiency
            BackendType.CUDA: 1.5,  # More expensive due to GPU usage
            BackendType.TENSOR_NETWORK: 1.2,  # Moderate cost
            BackendType.DDSIM: 0.9,  # Slightly cheaper than baseline
        }

        cost_factor = backend_cost_factors.get(backend, 1.0)
        total_cost = (time_cost + memory_cost) * cost_factor

        # Convert to score (lower cost = higher score)
        return 1.0 / (1.0 + total_cost)

    def _score_accuracy(self, backend: BackendType, analysis: dict[str, Any]) -> float:
        """Score numerical accuracy."""
        # Base accuracy scores
        base_accuracy = {
            BackendType.STIM: 1.0,  # Exact for Clifford circuits
            BackendType.TENSOR_NETWORK: 0.95,  # High precision
            BackendType.DDSIM: 0.9,  # Decision diagrams are exact
            BackendType.QISKIT: 0.85,  # Standard floating point
            BackendType.CUDA: 0.8,  # GPU precision considerations
            BackendType.JAX_METAL: 0.75,  # Some precision trade-offs
        }

        accuracy = base_accuracy.get(backend, 0.7)

        # Perfect accuracy for Clifford circuits with Stim
        if analysis["is_clifford"] and backend == BackendType.STIM:
            accuracy = 1.0
        elif not analysis["is_clifford"] and backend == BackendType.STIM:
            accuracy = 0.0  # Cannot handle non-Clifford

        return accuracy


class MultiObjectiveOptimizer:
    """Main multi-objective optimization engine."""

    def __init__(self, performance_predictor: PerformancePredictor | None = None):
        self.objective_scorer = ObjectiveScorer(performance_predictor)
        self.pareto_optimizer = ParetoOptimizer()

    def optimize(
        self,
        circuit: QuantumCircuit,
        available_backends: list[BackendType],
        context: UserContext,
        weights: ObjectiveWeight | None = None,
    ) -> list[OptimizationResult]:
        """Perform multi-objective optimization."""

        if weights is None:
            weights = self._infer_weights_from_context(context)
        else:
            weights = weights.normalize()

        # Score all backends
        backend_scores = []
        for backend in available_backends:
            scores = self.objective_scorer.score_backend_objectives(circuit, backend, context)
            backend_scores.append(scores)

        # Find Pareto front
        pareto_ranks = self.pareto_optimizer.rank_solutions(backend_scores)

        # Calculate weighted scores
        optimization_results = []

        for scores in backend_scores:
            weighted_score = self._calculate_weighted_score(scores, weights)

            # Trade-off analysis
            trade_offs = self._analyze_trade_offs(scores, backend_scores)

            # Domination analysis
            dominated = []
            dominates = []

            for other_scores in backend_scores:
                if other_scores.backend != scores.backend:
                    if self.pareto_optimizer._dominates(scores, other_scores):
                        dominates.append(other_scores.backend)
                    elif self.pareto_optimizer._dominates(other_scores, scores):
                        dominated.append(other_scores.backend)

            result = OptimizationResult(
                backend=scores.backend,
                total_score=weighted_score,
                objective_scores={
                    "time": scores.time_score,
                    "memory": scores.memory_score,
                    "energy": scores.energy_score,
                    "cost": scores.cost_score,
                    "accuracy": scores.accuracy_score,
                    "success_rate": scores.success_rate_score,
                },
                trade_off_analysis=trade_offs,
                pareto_rank=pareto_ranks[scores],
                dominated_solutions=dominated,
                dominates_solutions=dominates,
            )

            optimization_results.append(result)

        # Sort by weighted score (highest first)
        optimization_results.sort(key=lambda r: r.total_score, reverse=True)

        return optimization_results

    def find_optimal_backend(
        self,
        circuit: QuantumCircuit,
        available_backends: list[BackendType],
        context: UserContext,
        weights: ObjectiveWeight | None = None,
    ) -> OptimizationResult:
        """Find single optimal backend based on multi-objective optimization."""
        results = self.optimize(circuit, available_backends, context, weights)
        return results[0] if results else None

    def _infer_weights_from_context(self, context: UserContext) -> ObjectiveWeight:
        """Infer optimization weights from user context."""
        prefs = context.performance_preferences

        # Convert user preferences to optimization weights
        return ObjectiveWeight(
            time_weight=prefs.speed_priority,
            memory_weight=prefs.memory_priority,
            energy_weight=prefs.energy_priority,
            cost_weight=0.1,  # Default cost consideration
            accuracy_weight=prefs.accuracy_priority,
            success_rate_weight=0.1,  # Default reliability consideration
        ).normalize()

    def _calculate_weighted_score(self, scores: BackendObjectiveScores, weights: ObjectiveWeight) -> float:
        """Calculate weighted score for multi-objective optimization."""
        return (
            weights.time_weight * scores.time_score
            + weights.memory_weight * scores.memory_score
            + weights.energy_weight * scores.energy_score
            + weights.cost_weight * scores.cost_score
            + weights.accuracy_weight * scores.accuracy_score
            + weights.success_rate_weight * scores.success_rate_score
        )

    def _analyze_trade_offs(
        self, scores: BackendObjectiveScores, all_scores: list[BackendObjectiveScores]
    ) -> dict[str, Any]:
        """Analyze trade-offs for this solution."""
        # Find best scores for each objective
        best_scores = {
            "time": max(s.time_score for s in all_scores),
            "memory": max(s.memory_score for s in all_scores),
            "energy": max(s.energy_score for s in all_scores),
            "cost": max(s.cost_score for s in all_scores),
            "accuracy": max(s.accuracy_score for s in all_scores),
            "success_rate": max(s.success_rate_score for s in all_scores),
        }

        # Calculate how far this solution is from optimal in each objective
        trade_offs = {}

        for objective, best_score in best_scores.items():
            current_score = scores.objective_scores.get(objective, 0.0)
            if hasattr(scores, f"{objective}_score"):
                current_score = getattr(scores, f"{objective}_score")

            if best_score > 0:
                gap = (best_score - current_score) / best_score
                trade_offs[f"{objective}_gap"] = gap

        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []

        for objective, gap in trade_offs.items():
            if gap < 0.1:  # Within 10% of optimal
                strengths.append(objective.replace("_gap", ""))
            elif gap > 0.5:  # More than 50% from optimal
                weaknesses.append(objective.replace("_gap", ""))

        return {
            "gaps": trade_offs,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "overall_efficiency": 1.0 - sum(trade_offs.values()) / len(trade_offs),
        }


# Convenience functions for easy integration
def optimize_backend_selection(
    circuit: QuantumCircuit,
    available_backends: list[BackendType],
    context: UserContext,
    weights: ObjectiveWeight | None = None,
) -> OptimizationResult:
    """Convenience function for multi-objective backend optimization."""
    optimizer = MultiObjectiveOptimizer()
    return optimizer.find_optimal_backend(circuit, available_backends, context, weights)


def find_pareto_optimal_backends(
    circuit: QuantumCircuit, available_backends: list[BackendType], context: UserContext
) -> list[OptimizationResult]:
    """Find all Pareto-optimal backend choices."""
    optimizer = MultiObjectiveOptimizer()
    results = optimizer.optimize(circuit, available_backends, context)

    # Return only Pareto-optimal solutions (rank 0)
    return [result for result in results if result.pareto_rank == 0]
