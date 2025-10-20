"""
Asynchronous operations for Ariadne.

This module provides async/await patterns for non-blocking operations,
including simulation, backend health checking, and performance monitoring.
"""

from .simulation import (
    AsyncBackendInterface,
    AsyncSimulationRequest,
    AsyncSimulationResult,
    AsyncSimulator,
    get_async_simulator,
    simulate_async,
    simulate_batch_async,
)

__all__ = [
    "AsyncBackendInterface",
    "AsyncSimulationRequest",
    "AsyncSimulationResult",
    "AsyncSimulator",
    "get_async_simulator",
    "simulate_async",
    "simulate_batch_async",
]
