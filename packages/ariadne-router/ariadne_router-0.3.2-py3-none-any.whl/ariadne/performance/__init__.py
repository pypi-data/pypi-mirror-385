"""
Performance optimization system for Ariadne.

This module provides memory management, parallel processing, and caching
to improve performance and resource utilization.
"""

from .cache import (
    CacheBackend,
    CacheEntry,
    CachePolicy,
    CircuitHasher,
    IntelligentCache,
    Memoizer,
    MemoryCacheBackend,
    SimulationCache,
    cached_simulate,
    get_memoizer,
    get_simulation_cache,
    memoize,
)
from .memory import (
    MemoryEfficientSimulator,
    MemoryLevel,
    MemoryManager,
    MemoryMonitor,
    MemoryPool,
    MemoryStats,
    get_memory_manager,
    get_memory_stats,
    optimize_memory,
)
from .parallel import (
    DistributedSimulator,
    ExecutionMode,
    ParallelBenchmark,
    ParallelSimulationRequest,
    ParallelSimulationResult,
    ParallelSimulator,
    get_parallel_simulator,
    simulate_parallel,
)

__all__ = [
    # Caching
    "CacheBackend",
    "CacheEntry",
    "CachePolicy",
    "CircuitHasher",
    "IntelligentCache",
    "MemoryCacheBackend",
    "Memoizer",
    "SimulationCache",
    "cached_simulate",
    "get_memoizer",
    "get_simulation_cache",
    "memoize",
    # Memory management
    "MemoryEfficientSimulator",
    "MemoryLevel",
    "MemoryManager",
    "MemoryMonitor",
    "MemoryPool",
    "MemoryStats",
    "get_memory_manager",
    "get_memory_stats",
    "optimize_memory",
    # Parallel processing
    "DistributedSimulator",
    "ExecutionMode",
    "ParallelBenchmark",
    "ParallelSimulationRequest",
    "ParallelSimulationResult",
    "ParallelSimulator",
    "get_parallel_simulator",
    "simulate_parallel",
]
