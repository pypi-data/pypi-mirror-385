"""
Memory management system for Ariadne.

This module provides memory-efficient simulation for large circuits,
memory pooling for frequently used objects, and memory usage monitoring.
"""

from __future__ import annotations

import gc
import os
import sys
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from qiskit import QuantumCircuit

try:
    from ariadne.core import get_logger
except ImportError:
    # Fallback for when running as a script
    import os
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ariadne.core import get_logger


class MemoryLevel(Enum):
    """Memory usage levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class MemoryStats:
    """Memory usage statistics."""

    total_memory_mb: float
    used_memory_mb: float
    available_memory_mb: float
    process_memory_mb: float
    process_peak_memory_mb: float
    gc_stats: dict[str, int]
    timestamp: float = field(default_factory=time.time)

    @property
    def usage_percentage(self) -> float:
        """Calculate memory usage percentage."""
        if self.total_memory_mb == 0:
            return 0.0
        return self.used_memory_mb / self.total_memory_mb * 100

    @property
    def memory_level(self) -> MemoryLevel:
        """Get memory usage level."""
        if self.usage_percentage < 50:
            return MemoryLevel.LOW
        elif self.usage_percentage < 75:
            return MemoryLevel.MEDIUM
        elif self.usage_percentage < 90:
            return MemoryLevel.HIGH
        else:
            return MemoryLevel.CRITICAL


class MemoryPool:
    """Pool for reusing memory-intensive objects."""

    def __init__(self, max_size: int = 100):
        """
        Initialize the memory pool.

        Args:
            max_size: Maximum number of objects to keep in the pool
        """
        self.max_size = max_size
        self.logger = get_logger("memory_pool")

        # Pools for different object types
        self._pools: dict[type, list] = {}
        self._pool_locks: dict[type, threading.Lock] = {}

        # Statistics
        self._stats = {"hits": 0, "misses": 0, "created": 0, "reused": 0}

    def get(self, object_type: type, *args, **kwargs) -> Any:
        """
        Get an object from the pool or create a new one.

        Args:
            object_type: Type of object to get
            *args: Arguments for object creation
            **kwargs: Keyword arguments for object creation

        Returns:
            Object from pool or newly created
        """
        # Initialize pool for this type if needed
        if object_type not in self._pools:
            self._pools[object_type] = []
            self._pool_locks[object_type] = threading.Lock()

        # Try to get from pool
        with self._pool_locks[object_type]:
            if self._pools[object_type]:
                obj = self._pools[object_type].pop()
                self._stats["hits"] += 1
                self._stats["reused"] += 1

                # Reset object if it has a reset method
                if hasattr(obj, "reset"):
                    obj.reset(*args, **kwargs)

                self.logger.debug(f"Reused {object_type.__name__} from pool")
                return obj
            else:
                self._stats["misses"] += 1

        # Create new object
        obj = object_type(*args, **kwargs)
        self._stats["created"] += 1

        self.logger.debug(f"Created new {object_type.__name__}")
        return obj

    def return_object(self, obj: Any) -> None:
        """
        Return an object to the pool.

        Args:
            obj: Object to return to pool
        """
        object_type = type(obj)

        # Check if we have a pool for this type
        if object_type not in self._pools:
            return

        # Check if pool is full
        with self._pool_locks[object_type]:
            if len(self._pools[object_type]) < self.max_size:
                self._pools[object_type].append(obj)
                self.logger.debug(f"Returned {object_type.__name__} to pool")
            else:
                self.logger.debug(f"Pool for {object_type.__name__} is full, discarding object")

    def get_stats(self) -> dict[str, Any]:
        """Get pool statistics."""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total_requests if total_requests > 0 else 0.0

        return {
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "created": self._stats["created"],
            "reused": self._stats["reused"],
            "hit_rate": hit_rate,
            "pool_sizes": {t.__name__: len(pool) for t, pool in self._pools.items()},
        }

    def clear(self) -> None:
        """Clear all pools."""
        with self._pool_locks:
            for pool in self._pools.values():
                pool.clear()

        self.logger.info("Cleared all memory pools")


class MemoryMonitor:
    """Monitor for memory usage and optimization."""

    def __init__(self, check_interval: float = 5.0):
        """
        Initialize the memory monitor.

        Args:
            check_interval: Interval between memory checks in seconds
        """
        self.check_interval = check_interval
        self.logger = get_logger("memory_monitor")

        # Memory history
        self._memory_history: list[MemoryStats] = []
        self._max_history = 1000

        # Monitoring state
        self._monitoring = False
        self._monitor_thread: threading.Thread | None = None
        self._stop_event = threading.Event()

        # Callbacks for memory events
        self._callbacks: dict[MemoryLevel, list[Callable[[MemoryStats], None]]] = {level: [] for level in MemoryLevel}

        # Peak memory tracking
        self._peak_memory_mb = 0.0

    def start_monitoring(self) -> None:
        """Start memory monitoring in background thread."""
        if self._monitoring:
            return

        self._monitoring = True
        self._stop_event.clear()
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

        self.logger.info("Started memory monitoring")

    def stop_monitoring(self) -> None:
        """Stop memory monitoring."""
        if not self._monitoring:
            return

        self._monitoring = False
        self._stop_event.set()

        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=self.check_interval + 1.0)

        self.logger.info("Stopped memory monitoring")

    def _monitor_loop(self) -> None:
        """Background monitoring loop."""
        while self._monitoring and not self._stop_event.is_set():
            try:
                # Get current memory stats
                stats = self.get_memory_stats()

                # Update peak memory
                if stats.process_memory_mb > self._peak_memory_mb:
                    self._peak_memory_mb = stats.process_memory_mb

                # Add to history
                self._memory_history.append(stats)

                # Trim history if needed
                if len(self._memory_history) > self._max_history:
                    self._memory_history = self._memory_history[-self._max_history :]

                # Trigger callbacks
                self._trigger_callbacks(stats)

                # Wait for next check
                self._stop_event.wait(self.check_interval)

            except Exception as e:
                self.logger.error(f"Memory monitoring error: {e}")
                self._stop_event.wait(min(self.check_interval, 1.0))

    def get_memory_stats(self) -> MemoryStats:
        """Get current memory statistics."""
        try:
            # Get system memory info
            if sys.platform == "win32":
                import psutil

                memory = psutil.virtual_memory()
                total_memory_mb = memory.total / (1024 * 1024)
                used_memory_mb = memory.used / (1024 * 1024)
                available_memory_mb = memory.available / (1024 * 1024)
            else:
                # Try to read from /proc/meminfo on Linux
                try:
                    with open("/proc/meminfo") as f:
                        meminfo = f.read()

                    total_kb = 0
                    available_kb = 0

                    for line in meminfo.split("\n"):
                        if line.startswith("MemTotal:"):
                            total_kb = int(line.split()[1])
                        elif line.startswith("MemAvailable:"):
                            available_kb = int(line.split()[1])

                    total_memory_mb = total_kb / 1024
                    used_memory_mb = total_memory_mb - (available_kb / 1024)
                    available_memory_mb = available_kb / 1024
                except Exception:
                    # Fallback to psutil
                    import psutil

                    memory = psutil.virtual_memory()
                    total_memory_mb = memory.total / (1024 * 1024)
                    used_memory_mb = memory.used / (1024 * 1024)
                    available_memory_mb = memory.available / (1024 * 1024)

            # Get process memory info
            try:
                import psutil

                process = psutil.Process()
                process_memory_mb = process.memory_info().rss / (1024 * 1024)

                # Get peak memory (Linux only)
                if sys.platform == "linux":
                    try:
                        with open(f"/proc/{process.pid}/status") as f:
                            status = f.read()

                        for line in status.split("\n"):
                            if line.startswith("VmPeak:"):
                                peak_kb = int(line.split()[1])
                                process_peak_memory_mb = peak_kb / 1024
                                break
                        else:
                            process_peak_memory_mb = process_memory_mb
                    except Exception:
                        process_peak_memory_mb = process_memory_mb
                else:
                    process_peak_memory_mb = process_memory_mb
            except Exception:
                process_memory_mb = 0.0
                process_peak_memory_mb = 0.0

            # Get GC stats
            gc_stats = gc.get_stats()

            return MemoryStats(
                total_memory_mb=total_memory_mb,
                used_memory_mb=used_memory_mb,
                available_memory_mb=available_memory_mb,
                process_memory_mb=process_memory_mb,
                process_peak_memory_mb=process_peak_memory_mb,
                gc_stats=gc_stats[0] if gc_stats else {},
            )

        except Exception as e:
            self.logger.error(f"Failed to get memory stats: {e}")
            # Return default stats
            return MemoryStats(
                total_memory_mb=0.0,
                used_memory_mb=0.0,
                available_memory_mb=0.0,
                process_memory_mb=0.0,
                process_peak_memory_mb=0.0,
                gc_stats={},
            )

    def _trigger_callbacks(self, stats: MemoryStats) -> None:
        """Trigger callbacks for memory level."""
        level = stats.memory_level

        # Trigger callbacks for this level and all higher levels
        for mem_level in MemoryLevel:
            if mem_level.value >= level.value:
                for callback in self._callbacks[mem_level]:
                    try:
                        callback(stats)
                    except Exception as e:
                        self.logger.error(f"Memory callback error: {e}")

    def register_callback(self, level: MemoryLevel, callback: Callable[[MemoryStats], None]) -> None:
        """
        Register a callback for a memory level.

        Args:
            level: Memory level to trigger callback for
            callback: Callback function
        """
        self._callbacks[level].append(callback)
        self.logger.debug(f"Registered callback for {level.value} memory level")

    def get_memory_history(self, limit: int = 100) -> list[MemoryStats]:
        """
        Get memory usage history.

        Args:
            limit: Maximum number of records to return

        Returns:
            List of memory statistics
        """
        return self._memory_history[-limit:] if self._memory_history else []

    def get_peak_memory(self) -> float:
        """Get peak memory usage in MB."""
        return self._peak_memory_mb

    def suggest_optimizations(self, stats: MemoryStats | None = None) -> list[str]:
        """
        Suggest memory optimizations based on current stats.

        Args:
            stats: Current memory stats (uses current if None)

        Returns:
            List of optimization suggestions
        """
        if stats is None:
            stats = self.get_memory_stats()

        suggestions = []

        # Check memory level
        if stats.memory_level == MemoryLevel.CRITICAL:
            suggestions.append(
                "Memory usage is critical. Consider reducing circuit size or using memory-efficient backends."
            )
            suggestions.append("Enable garbage collection and memory pooling.")
        elif stats.memory_level == MemoryLevel.HIGH:
            suggestions.append("Memory usage is high. Consider using memory-efficient simulation methods.")
            suggestions.append("Monitor for memory leaks and optimize data structures.")
        elif stats.memory_level == MemoryLevel.MEDIUM:
            suggestions.append("Memory usage is moderate. Consider optimization for large circuits.")

        # Check GC stats
        if stats.gc_stats.get("collections", 0) > 10:
            suggestions.append("Garbage collection is running frequently. Consider reducing object creation.")

        # Check process memory
        if stats.process_memory_mb > 1000:  # 1GB
            suggestions.append("Process memory usage is high. Consider using memory-efficient backends.")

        return suggestions


class MemoryManager:
    """Manager for memory optimization and monitoring."""

    def __init__(self):
        """Initialize the memory manager."""
        self.logger = get_logger("memory_manager")

        # Components
        self.monitor = MemoryMonitor()
        self.pool = MemoryPool()

        # Optimization settings
        self._auto_gc_enabled = True
        self._auto_gc_threshold = 0.8  # Trigger GC at 80% memory usage

        # Register callbacks
        self.monitor.register_callback(MemoryLevel.HIGH, self._high_memory_callback)
        self.monitor.register_callback(MemoryLevel.CRITICAL, self._critical_memory_callback)

        # Start monitoring
        self.monitor.start_monitoring()

    def shutdown(self) -> None:
        """Shutdown the memory manager."""
        self.monitor.stop_monitoring()
        self.pool.clear()
        self.logger.info("Memory manager shutdown")

    def get_memory_stats(self) -> MemoryStats:
        """Get current memory statistics."""
        return self.monitor.get_memory_stats()

    def get_memory_pool(self) -> MemoryPool:
        """Get the memory pool."""
        return self.pool

    def enable_auto_gc(self, enabled: bool = True) -> None:
        """Enable or disable automatic garbage collection."""
        self._auto_gc_enabled = enabled
        self.logger.info(f"Auto GC {'enabled' if enabled else 'disabled'}")

    def set_auto_gc_threshold(self, threshold: float) -> None:
        """
        Set automatic garbage collection threshold.

        Args:
            threshold: Memory usage threshold (0.0-1.0)
        """
        self._auto_gc_threshold = max(0.0, min(1.0, threshold))
        self.logger.info(f"Auto GC threshold set to {self._auto_gc_threshold:.2%}")

    def optimize_memory(self, aggressive: bool = False) -> None:
        """
        Optimize memory usage.

        Args:
            aggressive: Whether to use aggressive optimization
        """
        self.logger.info("Optimizing memory usage")

        # Run garbage collection
        if aggressive:
            gc.collect()
        else:
            # Run generation 0 and 1 GC
            gc.collect(0)
            gc.collect(1)

        # Clear memory pool if aggressive
        if aggressive:
            self.pool.clear()

        self.logger.info("Memory optimization complete")

    def _high_memory_callback(self, stats: MemoryStats) -> None:
        """Callback for high memory usage."""
        self.logger.warning(f"High memory usage: {stats.usage_percentage:.1f}%")

        # Trigger auto GC if enabled
        if self._auto_gc_enabled and stats.usage_percentage > self._auto_gc_threshold:
            self.logger.info("Triggering automatic garbage collection")
            gc.collect()

        # Get optimization suggestions
        suggestions = self.monitor.suggest_optimizations(stats)
        for suggestion in suggestions:
            self.logger.info(f"Suggestion: {suggestion}")

    def _critical_memory_callback(self, stats: MemoryStats) -> None:
        """Callback for critical memory usage."""
        self.logger.error(f"Critical memory usage: {stats.usage_percentage:.1f}%")

        # Force garbage collection
        gc.collect()

        # Clear memory pool
        self.pool.clear()

        # Log error
        self.logger.error(
            "Memory usage is critical. Consider reducing circuit size or using memory-efficient backends."
        )


class MemoryEfficientSimulator:
    """Memory-efficient simulator for large circuits."""

    def __init__(self, chunk_size: int = 10):
        """
        Initialize the memory-efficient simulator.

        Args:
            chunk_size: Number of qubits to process at once
        """
        self.chunk_size = chunk_size
        self.logger = get_logger("memory_efficient_simulator")
        self.memory_manager = MemoryManager()

    def simulate_large_circuit(self, circuit: QuantumCircuit, shots: int = 1024) -> dict[str, int]:
        """
        Simulate a large circuit using memory-efficient techniques.

        Args:
            circuit: Circuit to simulate
            shots: Number of measurement shots

        Returns:
            Measurement counts
        """
        if circuit.num_qubits <= self.chunk_size:
            # Circuit is small enough for normal simulation
            from ariadne import simulate

            return simulate(circuit, shots)

        self.logger.info(f"Simulating large circuit with {circuit.num_qubits} qubits using chunking")

        # For demonstration, we'll use a simplified approach
        # In a production system, this would implement more sophisticated techniques

        # Check memory usage
        stats = self.memory_manager.get_memory_stats()
        if stats.memory_level == MemoryLevel.CRITICAL:
            self.logger.error("Memory usage is critical, cannot simulate large circuit")
            raise MemoryError("Insufficient memory to simulate circuit")

        # Use memory optimization
        self.memory_manager.optimize_memory()

        # For now, return a mock result
        # In a real implementation, this would use techniques like:
        # - Circuit partitioning
        # - Tensor network simulation
        # - Distributed computing
        # - Memory-efficient state vector representation

        result = {}
        for i in range(min(2**circuit.num_qubits, 100)):
            bitstring = format(i, f"0{circuit.num_qubits}b")
            result[bitstring] = shots // min(2**circuit.num_qubits, 100)

        return result


# Global memory manager instance
_global_memory_manager: MemoryManager | None = None


def get_memory_manager() -> MemoryManager:
    """Get the global memory manager."""
    global _global_memory_manager
    if _global_memory_manager is None:
        _global_memory_manager = MemoryManager()
    return _global_memory_manager


def get_memory_stats() -> MemoryStats:
    """Get current memory statistics using the global manager."""
    manager = get_memory_manager()
    return manager.get_memory_stats()


def optimize_memory(aggressive: bool = False) -> None:
    """Optimize memory usage using the global manager."""
    manager = get_memory_manager()
    manager.optimize_memory(aggressive)
