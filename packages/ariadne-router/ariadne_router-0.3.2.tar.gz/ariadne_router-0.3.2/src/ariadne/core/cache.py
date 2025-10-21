"""
Circuit analysis caching system for Ariadne.

This module provides caching functionality for circuit analysis results to avoid
redundant computations and improve performance.
"""

from __future__ import annotations

import hashlib
import pickle
import time
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from qiskit import QuantumCircuit

from .error_handling import AriadneError


@dataclass
class CacheEntry:
    """Entry in the circuit analysis cache."""

    analysis: dict[str, Any]
    timestamp: float
    access_count: int = 0
    last_access: float = 0.0

    def __post_init__(self) -> None:
        if self.last_access == 0.0:
            self.last_access = self.timestamp


class CacheError(AriadneError):
    """Raised when cache operations fail."""

    pass


class CircuitAnalysisCache:
    """
    LRU cache for circuit analysis results.

    This cache stores analysis results for quantum circuits to avoid
    redundant computations. It uses a deterministic hashing scheme
    to identify equivalent circuits.
    """

    def __init__(self, max_size: int = 1000, ttl_seconds: float = 3600.0) -> None:
        """
        Initialize the circuit analysis cache.

        Args:
            max_size: Maximum number of entries to store
            ttl_seconds: Time-to-live for cache entries in seconds
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    def _circuit_hash(self, circuit: QuantumCircuit) -> str:
        """
        Create deterministic hash of circuit structure.

        Args:
            circuit: Quantum circuit to hash

        Returns:
            SHA256 hash of the circuit structure
        """
        try:
            # Extract circuit structure for hashing
            circuit_data = {
                "num_qubits": circuit.num_qubits,
                "num_clbits": circuit.num_clbits,
                "instructions": [],
            }

            for item in circuit.data:
                if hasattr(item, "operation"):
                    instruction = item.operation
                    qargs = list(item.qubits)
                    cargs = list(item.clbits)
                else:  # Legacy tuple form
                    instruction, qargs, cargs = item

                # Convert qubits to indices for deterministic hashing
                qubit_indices = [circuit.find_bit(qubit).index for qubit in qargs]
                # Convert classical bits to indices
                clbit_indices = [circuit.find_bit(clbit).index for clbit in cargs]

                circuit_data["instructions"].append(
                    (
                        instruction.name,
                        tuple(qubit_indices),
                        tuple(clbit_indices),
                        tuple(instruction.params) if hasattr(instruction, "params") else (),
                    )
                )

            # Create hash
            serialized = pickle.dumps(circuit_data, protocol=pickle.HIGHEST_PROTOCOL)
            return hashlib.sha256(serialized).hexdigest()

        except Exception as exc:
            raise CacheError(f"Failed to create circuit hash: {exc}") from exc

    def get_analysis(self, circuit: QuantumCircuit) -> dict[str, Any] | None:
        """
        Get cached circuit analysis.

        Args:
            circuit: Quantum circuit to get analysis for

        Returns:
            Cached analysis or None if not found
        """
        try:
            circuit_hash = self._circuit_hash(circuit)

            if circuit_hash not in self._cache:
                self._misses += 1
                return None

            entry = self._cache[circuit_hash]

            # Check TTL
            if time.time() - entry.timestamp > self.ttl_seconds:
                del self._cache[circuit_hash]
                self._misses += 1
                return None

            # Update access information
            entry.access_count += 1
            entry.last_access = time.time()

            # Move to end (LRU)
            self._cache.move_to_end(circuit_hash)
            self._hits += 1

            return entry.analysis.copy()

        except Exception as exc:
            raise CacheError(f"Failed to get cached analysis: {exc}") from exc

    def store_analysis(self, circuit: QuantumCircuit, analysis: dict[str, Any]) -> None:
        """
        Store circuit analysis in cache.

        Args:
            circuit: Quantum circuit to store analysis for
            analysis: Analysis results to store
        """
        try:
            circuit_hash = self._circuit_hash(circuit)
            current_time = time.time()

            # Check if entry already exists
            if circuit_hash in self._cache:
                # Update existing entry
                entry = self._cache[circuit_hash]
                entry.analysis = analysis
                entry.timestamp = current_time
                entry.last_access = current_time
                entry.access_count += 1
                self._cache.move_to_end(circuit_hash)
                return

            # Check cache size limit
            if len(self._cache) >= self.max_size:
                # Evict oldest entry
                oldest_key, oldest_entry = next(iter(self._cache.items()))
                del self._cache[oldest_key]
                self._evictions += 1

            # Create new entry
            entry = CacheEntry(
                analysis=analysis.copy(),
                timestamp=current_time,
                last_access=current_time,
                access_count=1,
            )

            self._cache[circuit_hash] = entry

        except Exception as exc:
            raise CacheError(f"Failed to store analysis: {exc}") from exc

    def clear(self) -> None:
        """Clear all entries from the cache."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    def cleanup_expired(self) -> int:
        """
        Remove expired entries from cache.

        Returns:
            Number of entries removed
        """
        current_time = time.time()
        expired_keys = []

        for key, entry in self._cache.items():
            if current_time - entry.timestamp > self.ttl_seconds:
                expired_keys.append(key)

        for key in expired_keys:
            del self._cache[key]

        return len(expired_keys)

    def get_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "evictions": self._evictions,
            "hit_rate": hit_rate,
            "ttl_seconds": self.ttl_seconds,
        }

    def get_entry_info(self, circuit: QuantumCircuit) -> dict[str, Any] | None:
        """
        Get information about a cache entry.

        Args:
            circuit: Quantum circuit to get info for

        Returns:
            Entry information or None if not found
        """
        try:
            circuit_hash = self._circuit_hash(circuit)

            if circuit_hash not in self._cache:
                return None

            entry = self._cache[circuit_hash]
            current_time = time.time()

            return {
                "hash": circuit_hash,
                "timestamp": entry.timestamp,
                "age_seconds": current_time - entry.timestamp,
                "access_count": entry.access_count,
                "last_access": entry.last_access,
                "last_access_age": current_time - entry.last_access,
                "expired": current_time - entry.timestamp > self.ttl_seconds,
            }

        except Exception as exc:
            raise CacheError(f"Failed to get entry info: {exc}") from exc


# Global cache instance
_global_cache: CircuitAnalysisCache | None = None


def get_global_cache() -> CircuitAnalysisCache:
    """Get the global circuit analysis cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = CircuitAnalysisCache()
    return _global_cache


def set_global_cache(cache: CircuitAnalysisCache) -> None:
    """Set the global circuit analysis cache instance."""
    global _global_cache
    _global_cache = cache


def cached_analyze(
    circuit: QuantumCircuit, analyzer_func: Callable[..., dict[str, Any]], *args: Any, **kwargs: Any
) -> dict[str, Any]:
    """
    Analyze circuit with caching.

    Args:
        circuit: Quantum circuit to analyze
        analyzer_func: Function to perform analysis
        *args: Arguments to pass to analyzer function
        **kwargs: Keyword arguments to pass to analyzer function

    Returns:
        Analysis results
    """
    cache = get_global_cache()

    # Try to get from cache
    cached_result = cache.get_analysis(circuit)
    if cached_result is not None:
        return cached_result

    # Perform analysis
    result = analyzer_func(circuit, *args, **kwargs)

    # Store in cache
    cache.store_analysis(circuit, result)

    return result
