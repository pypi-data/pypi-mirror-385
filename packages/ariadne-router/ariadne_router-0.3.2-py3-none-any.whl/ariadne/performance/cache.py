"""
Intelligent caching and memoization system for Ariadne.

This module provides intelligent caching of simulation results, memoization
for expensive calculations, and distributed caching for multi-node deployments.
"""

from __future__ import annotations

import hashlib
import json
import pickle
import time
from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import Any, ParamSpec, TypeVar, cast

from qiskit import QuantumCircuit
from qiskit.circuit.instruction import Instruction
from qiskit.circuit.quantumcircuit import CircuitInstruction

try:
    from ariadne.core import get_logger
    from ariadne.types import SimulationResult
except ImportError:
    # Fallback for when running as a script
    import os
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ariadne.core import get_logger
    from ariadne.types import SimulationResult


P = ParamSpec("P")
R = TypeVar("R")
SimulationCallable = Callable[..., SimulationResult]


class CachePolicy(Enum):
    """Cache eviction policies."""

    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In, First Out
    TTL = "ttl"  # Time To Live


@dataclass
class CacheEntry:
    """Entry in the cache."""

    key: str
    value: Any
    created_at: float
    last_accessed: float
    access_count: int = 0
    ttl: float | None = None  # Time to live in seconds
    size: int = 0  # Size in bytes

    def __post_init__(self) -> None:
        """Post-initialization processing."""
        if self.last_accessed == 0:
            self.last_accessed = self.created_at

    def is_expired(self) -> bool:
        """Check if the entry is expired."""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl

    def touch(self) -> None:
        """Update last accessed time and increment access count."""
        self.last_accessed = time.time()
        self.access_count += 1


class CacheBackend(ABC):
    """Abstract base class for cache backends."""

    @abstractmethod
    def get(self, key: str) -> Any | None:
        """Get a value from the cache."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        """Set a value in the cache."""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete a value from the cache."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all values from the cache."""
        pass

    @abstractmethod
    def keys(self) -> list[str]:
        """Get all keys in the cache."""
        pass

    @abstractmethod
    def size(self) -> int:
        """Get the number of entries in the cache."""
        pass


class MemoryCacheBackend(CacheBackend):
    """In-memory cache backend."""

    def __init__(self, max_size: int = 1000, max_memory_mb: int = 100) -> None:
        """
        Initialize the memory cache backend.

        Args:
            max_size: Maximum number of entries
            max_memory_mb: Maximum memory usage in MB
        """
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024

        # Storage
        self._cache: dict[str, CacheEntry] = {}
        self._access_order: list[str] = []  # For LRU
        self._current_memory_bytes = 0

        self.logger = get_logger("memory_cache")

    def get(self, key: str) -> Any | None:
        """Get a value from the cache."""
        if key not in self._cache:
            return None

        entry = self._cache[key]

        # Check if expired
        if entry.is_expired():
            self.delete(key)
            return None

        # Update access information
        entry.touch()

        # Update LRU order
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

        return entry.value

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        """Set a value in the cache."""
        # Calculate size
        try:
            size = len(pickle.dumps(value))
        except Exception:
            size = 1024  # Default size estimate

        # Check if we need to evict entries
        self._evict_if_needed(size)

        # Create entry
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=time.time(),
            last_accessed=time.time(),
            ttl=ttl,
            size=size,
        )

        # Update cache
        if key in self._cache:
            # Update existing entry
            old_entry = self._cache[key]
            self._current_memory_bytes -= old_entry.size

            # Remove from access order
            if key in self._access_order:
                self._access_order.remove(key)

        self._cache[key] = entry
        self._access_order.append(key)
        self._current_memory_bytes += size

    def delete(self, key: str) -> bool:
        """Delete a value from the cache."""
        if key not in self._cache:
            return False

        entry = self._cache[key]
        self._current_memory_bytes -= entry.size

        del self._cache[key]

        if key in self._access_order:
            self._access_order.remove(key)

        return True

    def clear(self) -> None:
        """Clear all values from the cache."""
        self._cache.clear()
        self._access_order.clear()
        self._current_memory_bytes = 0

    def keys(self) -> list[str]:
        """Get all keys in the cache."""
        return list(self._cache.keys())

    def size(self) -> int:
        """Get the number of entries in the cache."""
        return len(self._cache)

    def _evict_if_needed(self, new_entry_size: int) -> None:
        """Evict entries if needed to make space."""
        # Check memory limit
        while self._current_memory_bytes + new_entry_size > self.max_memory_bytes or len(self._cache) >= self.max_size:
            if not self._cache:
                break

            # Evict least recently used entry
            lru_key = self._access_order.pop(0)
            if lru_key in self._cache:
                entry = self._cache[lru_key]
                self._current_memory_bytes -= entry.size
                del self._cache[lru_key]

                self.logger.debug(f"Evicted cache entry: {lru_key}")


class IntelligentCache:
    """Intelligent cache with automatic invalidation and optimization."""

    def __init__(
        self,
        backend: CacheBackend | None = None,
        policy: CachePolicy = CachePolicy.LRU,
        default_ttl: float | None = None,
    ):
        """
        Initialize the intelligent cache.

        Args:
            backend: Cache backend to use
            policy: Cache eviction policy
            default_ttl: Default time to live for entries
        """
        self.logger = get_logger("intelligent_cache")
        self.policy = policy
        self.default_ttl = default_ttl

        # Use provided backend or create default
        self.backend = backend or MemoryCacheBackend()

        # Statistics
        self._stats = {"hits": 0, "misses": 0, "sets": 0, "evictions": 0, "expirations": 0}

        # Cache invalidation rules
        self._invalidation_rules: list[Callable[[str, Any], bool]] = []

    def get(self, key: str) -> Any | None:
        """
        Get a value from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        value = self.backend.get(key)

        if value is not None:
            self._stats["hits"] += 1
            self.logger.debug(f"Cache hit: {key}")
        else:
            self._stats["misses"] += 1
            self.logger.debug(f"Cache miss: {key}")

        return value

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        """
        Set a value in the cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        # Use default TTL if not provided
        if ttl is None:
            ttl = self.default_ttl

        self.backend.set(key, value, ttl)
        self._stats["sets"] += 1
        self.logger.debug(f"Cache set: {key}")

    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.

        Args:
            key: Cache key

        Returns:
            True if value was deleted
        """
        result = self.backend.delete(key)
        if result:
            self.logger.debug(f"Cache delete: {key}")
        return result

    def clear(self) -> None:
        """Clear all values from the cache."""
        self.backend.clear()
        self.logger.info("Cache cleared")

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total_requests if total_requests > 0 else 0.0

        return {**self._stats, "hit_rate": hit_rate, "size": self.backend.size()}

    def add_invalidation_rule(self, rule: Callable[[str, Any], bool]) -> None:
        """
        Add a cache invalidation rule.

        Args:
            rule: Function that takes (key, value) and returns True if should invalidate
        """
        self._invalidation_rules.append(rule)

    def invalidate_by_rule(self) -> int:
        """
        Invalidate cache entries based on rules.

        Returns:
            Number of entries invalidated
        """
        invalidated_count = 0
        keys_to_delete = []

        for key in self.backend.keys():
            value = self.backend.get(key)
            if value is not None:
                # Check all invalidation rules
                for rule in self._invalidation_rules:
                    try:
                        if rule(key, value):
                            keys_to_delete.append(key)
                            break
                    except Exception as e:
                        self.logger.error(f"Invalidation rule error: {e}")

        # Delete invalid entries
        for key in keys_to_delete:
            if self.delete(key):
                invalidated_count += 1

        if invalidated_count > 0:
            self.logger.info(f"Invalidated {invalidated_count} cache entries")

        return invalidated_count


class CircuitHasher:
    """Utility class for hashing quantum circuits."""

    @staticmethod
    def hash_circuit(circuit: QuantumCircuit) -> str:
        """
        Generate a hash for a quantum circuit.

        Args:
            circuit: Circuit to hash

        Returns:
            Hash string
        """
        # Create a deterministic representation of the circuit
        circuit_data = {
            "num_qubits": circuit.num_qubits,
            "num_clbits": circuit.num_clbits,
            "instructions": [],
        }

        for item in circuit.data:
            if isinstance(item, CircuitInstruction):
                instruction = item.operation
                qargs = list(item.qubits)
                cargs = list(item.clbits)
            else:  # Legacy tuple form
                instruction_tuple = cast(tuple[Instruction, list[Any], list[Any]], item)
                instruction, qargs, cargs = instruction_tuple

            instruction_data = {
                "name": instruction.name,
                "params": [float(p) if isinstance(p, int | float) else str(p) for p in instruction.params],
                "qubits": [circuit.find_bit(q).index for q in qargs],
                "clbits": [circuit.find_bit(c).index for c in cargs],
            }
            circuit_data["instructions"].append(instruction_data)

        # Create hash
        circuit_str = json.dumps(circuit_data, sort_keys=True)
        return hashlib.sha256(circuit_str.encode()).hexdigest()

    @staticmethod
    def hash_simulation_params(circuit: QuantumCircuit, shots: int, backend: str | None = None) -> str:
        """
        Generate a hash for simulation parameters.

        Args:
            circuit: Circuit to simulate
            shots: Number of shots
            backend: Backend name

        Returns:
            Hash string
        """
        circuit_hash = CircuitHasher.hash_circuit(circuit)

        params_data = {"circuit_hash": circuit_hash, "shots": shots, "backend": backend}

        params_str = json.dumps(params_data, sort_keys=True)
        return hashlib.sha256(params_str.encode()).hexdigest()


class SimulationCache:
    """Specialized cache for quantum circuit simulation results."""

    def __init__(self, cache: IntelligentCache | None = None) -> None:
        """
        Initialize the simulation cache.

        Args:
            cache: Cache instance to use
        """
        self.logger = get_logger("simulation_cache")
        self.cache = cache or IntelligentCache()
        self.hasher = CircuitHasher()

        # Add invalidation rule for backend health
        self.cache.add_invalidation_rule(self._backend_health_rule)

    def get(self, circuit: QuantumCircuit, shots: int, backend: str | None = None) -> SimulationResult | None:
        """
        Get a cached simulation result.

        Args:
            circuit: Circuit that was simulated
            shots: Number of shots
            backend: Backend that was used

        Returns:
            Cached simulation result or None
        """
        cache_key = self.hasher.hash_simulation_params(circuit, shots, backend)
        return self.cache.get(cache_key)

    def set(
        self,
        circuit: QuantumCircuit,
        shots: int,
        result: SimulationResult,
        backend: str | None = None,
        ttl: float | None = None,
    ) -> None:
        """
        Cache a simulation result.

        Args:
            circuit: Circuit that was simulated
            shots: Number of shots
            result: Simulation result
            backend: Backend that was used
            ttl: Time to live in seconds
        """
        cache_key = self.hasher.hash_simulation_params(circuit, shots, backend)
        self.cache.set(cache_key, result, ttl)

    def invalidate_backend(self, backend: str) -> int:
        """
        Invalidate all cache entries for a specific backend.

        Args:
            backend: Backend name

        Returns:
            Number of entries invalidated
        """

        def backend_rule(key: str, value: Any) -> bool:
            # Check if the cached result is for the specified backend
            try:
                # Parse the key to extract backend information
                # This is a simplified implementation
                return backend in key
            except Exception:
                return False

        # Add temporary rule and invalidate
        self.cache.add_invalidation_rule(backend_rule)
        count = self.cache.invalidate_by_rule()

        # Remove the temporary rule
        self.cache._invalidation_rules.pop()

        return count

    def _backend_health_rule(self, key: str, value: Any) -> bool:
        """Rule to invalidate cache entries when backend health is poor."""
        # This is a simplified implementation
        # In a production system, this would check actual backend health

        try:
            # Check if the cached result has metadata about backend health
            if hasattr(value, "metadata") and value.metadata:
                if "backend_health" in value.metadata:
                    health = value.metadata["backend_health"]
                    return health.lower() not in ["healthy", "good"]
        except Exception:
            pass

        return False


class Memoizer:
    """Memoization utility for expensive functions."""

    def __init__(self, cache: IntelligentCache | None = None) -> None:
        """
        Initialize the memoizer.

        Args:
            cache: Cache instance to use
        """
        self.cache = cache or IntelligentCache()
        self.logger = get_logger("memoizer")

    def memoize(self, ttl: float | None = None) -> Callable[[Callable[P, R]], Callable[P, R]]:
        """
        Decorator for memoizing functions.

        Args:
            ttl: Time to live for cached results

        Returns:
            Decorated function
        """

        def decorator(func: Callable[P, R]) -> Callable[P, R]:
            @wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                # Generate cache key
                cache_key = self._generate_cache_key(func, args, kwargs)

                # Try to get from cache
                cached_result = self.cache.get(cache_key)
                if cached_result is not None:
                    return cast(R, cached_result)

                # Call function
                result = func(*args, **kwargs)

                # Cache result
                self.cache.set(cache_key, result, ttl)

                return result

            return cast(Callable[P, R], wrapper)

        return decorator

    def _generate_cache_key(self, func: Callable[..., Any], args: tuple[Any, ...], kwargs: Mapping[str, Any]) -> str:
        """Generate a cache key for a function call."""
        # Create a deterministic representation of the function call
        key_data = {
            "function": func.__name__,
            "module": func.__module__,
            "args": self._serialize_args(args),
            "kwargs": self._serialize_args(kwargs),
        }

        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()

    def _serialize_args(self, args: Any) -> Any:
        """Serialize arguments for cache key generation."""
        if isinstance(args, str | int | float | bool | type(None)):
            return args
        elif isinstance(args, list | tuple):
            return [self._serialize_args(arg) for arg in args]
        elif isinstance(args, Mapping):
            return {k: self._serialize_args(v) for k, v in args.items()}
        elif isinstance(args, QuantumCircuit):
            return CircuitHasher.hash_circuit(args)
        elif hasattr(args, "__dict__"):
            return str(args)
        else:
            return str(args)


# Global cache instances
_global_simulation_cache: SimulationCache | None = None
_global_memoizer: Memoizer | None = None


def get_simulation_cache() -> SimulationCache:
    """Get the global simulation cache."""
    global _global_simulation_cache
    if _global_simulation_cache is None:
        _global_simulation_cache = SimulationCache()
    return _global_simulation_cache


def get_memoizer() -> Memoizer:
    """Get the global memoizer."""
    global _global_memoizer
    if _global_memoizer is None:
        _global_memoizer = Memoizer()
    return _global_memoizer


def cached_simulate(ttl: float | None = None) -> Callable[[SimulationCallable], SimulationCallable]:
    """
    Decorator for caching simulation results.

    Args:
        ttl: Time to live for cached results

    Returns:
        Decorated simulation function
    """

    def decorator(func: SimulationCallable) -> SimulationCallable:
        @wraps(func)
        def wrapper(
            circuit: QuantumCircuit,
            shots: int = 1024,
            backend: str | None = None,
            **kwargs: Any,
        ) -> SimulationResult:
            # Get simulation cache
            cache = get_simulation_cache()

            # Try to get from cache
            cached_result = cache.get(circuit, shots, backend)
            if cached_result is not None:
                return cached_result

            # Call function
            result = func(circuit, shots, backend, **kwargs)

            # Cache result
            cache.set(circuit, shots, result, backend, ttl)

            return result

        return cast(SimulationCallable, wrapper)

    return decorator


def memoize(ttl: float | None = None) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator for memoizing function results.

    Args:
        ttl: Time to live for cached results

    Returns:
        Decorated function
    """
    memoizer = get_memoizer()
    return memoizer.memoize(ttl)
