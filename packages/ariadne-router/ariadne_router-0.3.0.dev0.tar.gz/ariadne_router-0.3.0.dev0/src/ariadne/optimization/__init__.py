"""
Optimization system for Ariadne.

This module provides circuit transformation and optimization passes,
including gate fusion, cancellation, and circuit analysis for optimization opportunities.
"""

from .circuit import (
    CircuitOptimizationManager,
    CircuitOptimizer,
    CompositeOptimizer,
    CustomUnrollOptimizer,
    DepthReductionOptimizer,
    GateCancellationOptimizer,
    GateFusionOptimizer,
    OptimizationResult,
    OptimizationType,
    analyze_optimization_opportunities,
    get_optimization_manager,
    optimize_circuit,
)

__all__ = [
    "CircuitOptimizationManager",
    "CircuitOptimizer",
    "CompositeOptimizer",
    "CustomUnrollOptimizer",
    "DepthReductionOptimizer",
    "GateCancellationOptimizer",
    "GateFusionOptimizer",
    "OptimizationResult",
    "OptimizationType",
    "analyze_optimization_opportunities",
    "get_optimization_manager",
    "optimize_circuit",
]
