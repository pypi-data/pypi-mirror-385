"""
Backend pooling system for Ariadne.

This module provides pooling functionality for quantum simulation backends,
reducing initialization overhead and improving resource utilization.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from enum import Enum
from queue import Empty, Queue
from typing import Any

from ..core import get_logger


class PoolStatus(Enum):
    """Status of a backend pool."""

    INITIALIZING = "initializing"
    READY = "ready"
    DEGRADED = "degraded"
    EXHAUSTED = "exhausted"
    ERROR = "error"


@dataclass
class PoolStatistics:
    """Statistics for a backend pool."""

    backend_name: str
    total_instances: int
    active_instances: int
    available_instances: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_wait_time: float
    peak_usage: int
    created_at: float
    last_access: float

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests

    @property
    def utilization_rate(self) -> float:
        """Calculate utilization rate."""
        if self.total_instances == 0:
            return 0.0
        return self.active_instances / self.total_instances


@dataclass
class PooledBackend:
    """A pooled backend instance."""

    instance: Any
    created_at: float
    last_used: float
    usage_count: int
    is_active: bool
    error_count: int

    def mark_used(self) -> None:
        """Mark the backend as used."""
        self.last_used = time.time()
        self.usage_count += 1

    def mark_error(self) -> None:
        """Mark an error for the backend."""
        self.error_count += 1


class BackendPoolError(Exception):
    """Raised when backend pool operations fail."""

    pass


class BackendPoolExhaustedError(BackendPoolError):
    """Raised when backend pool is exhausted."""

    pass


class BackendPool:
    """
    Pool for quantum simulation backend instances.

    This class manages a pool of backend instances, reducing initialization
    overhead and improving resource utilization.
    """

    def __init__(
        self,
        backend_class: type,
        backend_name: str,
        min_instances: int = 1,
        max_instances: int = 5,
        instance_timeout: float = 300.0,  # 5 minutes
        max_idle_time: float = 600.0,  # 10 minutes
        max_errors: int = 5,
    ):
        """
        Initialize the backend pool.

        Args:
            backend_class: Class of the backend to pool
            backend_name: Name of the backend
            min_instances: Minimum number of instances to maintain
            max_instances: Maximum number of instances to create
            instance_timeout: Timeout for instance operations
            max_idle_time: Maximum idle time before instance is recycled
            max_errors: Maximum errors before instance is discarded
        """
        self.backend_class = backend_class
        self.backend_name = backend_name
        self.min_instances = min_instances
        self.max_instances = max_instances
        self.instance_timeout = instance_timeout
        self.max_idle_time = max_idle_time
        self.max_errors = max_errors

        self.logger = get_logger(f"pool.{backend_name}")

        # Pool state
        self._status = PoolStatus.INITIALIZING
        self._available: Queue[PooledBackend] = Queue(maxsize=max_instances)
        self._active: list[PooledBackend] = []
        self._all_instances: list[PooledBackend] = []

        # Threading
        self._lock = threading.RLock()
        self._maintenance_thread: threading.Thread | None = None
        self._running = False

        # Statistics
        self._stats = PoolStatistics(
            backend_name=backend_name,
            total_instances=0,
            active_instances=0,
            available_instances=0,
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            average_wait_time=0.0,
            peak_usage=0,
            created_at=time.time(),
            last_access=time.time(),
        )

        # Initialize minimum instances
        self._initialize_pool()

    def _initialize_pool(self) -> None:
        """Initialize the pool with minimum instances."""
        try:
            for _ in range(self.min_instances):
                instance = self._create_instance()
                if instance:
                    self._available.put(instance)

            self._status = PoolStatus.READY
            self._start_maintenance_thread()

            self.logger.info(f"Initialized {self.backend_name} pool with {self.min_instances} instances")

        except Exception as e:
            self._status = PoolStatus.ERROR
            self.logger.error(f"Failed to initialize {self.backend_name} pool: {e}")
            raise BackendPoolError(f"Pool initialization failed: {e}") from e

    def _create_instance(self) -> PooledBackend | None:
        """Create a new backend instance."""
        try:
            self.logger.debug(f"Creating new {self.backend_name} instance")
            backend_instance = self.backend_class()

            pooled_backend = PooledBackend(
                instance=backend_instance,
                created_at=time.time(),
                last_used=time.time(),
                usage_count=0,
                is_active=False,
                error_count=0,
            )

            with self._lock:
                self._all_instances.append(pooled_backend)
                self._stats.total_instances += 1

            return pooled_backend

        except Exception as e:
            self.logger.error(f"Failed to create {self.backend_name} instance: {e}")
            return None

    def _start_maintenance_thread(self) -> None:
        """Start the maintenance thread."""
        if self._running:
            return

        self._running = True
        self._maintenance_thread = threading.Thread(target=self._maintenance_loop, daemon=True)
        self._maintenance_thread.start()

    def _maintenance_loop(self) -> None:
        """Maintenance loop for pool management."""
        while self._running:
            try:
                self._perform_maintenance()
                time.sleep(30.0)  # Check every 30 seconds
            except Exception as e:
                self.logger.error(f"Pool maintenance error: {e}")
                time.sleep(60.0)  # Back off on error

    def _perform_maintenance(self) -> None:
        """Perform pool maintenance tasks."""
        current_time = time.time()

        with self._lock:
            # Check for idle instances
            idle_instances = []
            for instance in self._all_instances:
                if not instance.is_active:
                    idle_time = current_time - instance.last_used
                    if idle_time > self.max_idle_time:
                        idle_instances.append(instance)

            # Remove idle instances if we have more than minimum
            instances_to_remove = min(len(idle_instances), max(0, len(self._all_instances) - self.min_instances))

            for instance in idle_instances[:instances_to_remove]:
                self._remove_instance(instance)

            # Check for error instances
            error_instances = [instance for instance in self._all_instances if instance.error_count >= self.max_errors]

            for instance in error_instances:
                self._remove_instance(instance)

            # Create new instances if needed
            available_count = self._available.qsize()
            total_count = len(self._all_instances)

            if available_count < self.min_instances and total_count < self.max_instances:
                instances_to_create = min(self.min_instances - available_count, self.max_instances - total_count)

                for _ in range(instances_to_create):
                    new_instance = self._create_instance()
                    if new_instance:
                        self._available.put(new_instance)

            # Update statistics
            self._update_stats()

    def _remove_instance(self, instance: PooledBackend) -> None:
        """Remove an instance from the pool."""
        try:
            # Remove from available queue
            temp_instances = []
            while not self._available.empty():
                try:
                    available_instance = self._available.get_nowait()
                    if available_instance is not instance:
                        temp_instances.append(available_instance)
                except Empty:
                    break

            # Put back valid instances
            for temp_instance in temp_instances:
                self._available.put(temp_instance)

            # Remove from active list
            if instance in self._active:
                self._active.remove(instance)

            # Remove from all instances
            if instance in self._all_instances:
                self._all_instances.remove(instance)
                self._stats.total_instances -= 1

            self.logger.debug(f"Removed {self.backend_name} instance (errors: {instance.error_count})")

        except Exception as e:
            self.logger.error(f"Failed to remove {self.backend_name} instance: {e}")

    def _update_stats(self) -> None:
        """Update pool statistics."""
        self._stats.active_instances = len(self._active)
        self._stats.available_instances = self._available.qsize()
        self._stats.last_access = time.time()

        # Update peak usage
        current_usage = self._stats.active_instances
        if current_usage > self._stats.peak_usage:
            self._stats.peak_usage = current_usage

        # Update status based on pool state
        if self._stats.total_instances == 0:
            self._status = PoolStatus.ERROR
            self.logger.debug("Pool status set to ERROR: total_instances=0")
        elif self._stats.available_instances == 0:
            self._status = PoolStatus.EXHAUSTED
            self.logger.debug("Pool status set to EXHAUSTED: available_instances=0")
        else:
            self._status = PoolStatus.READY
            self.logger.debug(
                f"Pool status set to READY: total_instances={self._stats.total_instances}, "
                f"min_instances={self.min_instances}"
            )

    def get_backend(self, timeout: float = 10.0) -> Any:
        """
        Get a backend instance from the pool.

        Args:
            timeout: Maximum time to wait for an available instance

        Returns:
            Backend instance

        Raises:
            BackendPoolExhaustedError: If no instance is available
            BackendPoolError: If pool is in error state
        """
        if self._status == PoolStatus.ERROR:
            raise BackendPoolError(f"Backend pool {self.backend_name} is in error state")

        start_time = time.time()

        try:
            # Update statistics
            with self._lock:
                self._stats.total_requests += 1

            # Try to get an available instance
            try:
                pooled_backend: PooledBackend = self._available.get(timeout=timeout)
            except Empty as err:
                # Try to create a new instance if we haven't reached max
                with self._lock:
                    if len(self._all_instances) < self.max_instances:
                        new_backend = self._create_instance()
                        if new_backend is None:
                            raise BackendPoolExhaustedError(
                                f"Failed to create new {self.backend_name} instance"
                            ) from err
                        pooled_backend = new_backend
                    else:
                        raise BackendPoolExhaustedError(
                            f"No available {self.backend_name} instances (max: {self.max_instances})"
                        ) from err

            # Mark as active
            with self._lock:
                pooled_backend.is_active = True
                pooled_backend.mark_used()
                self._active.append(pooled_backend)
                self._stats.successful_requests += 1

            # Calculate wait time
            wait_time = time.time() - start_time
            with self._lock:
                # Update average wait time
                total_requests = self._stats.total_requests
                current_avg = self._stats.average_wait_time
                self._stats.average_wait_time = (current_avg * (total_requests - 1) + wait_time) / total_requests

            self.logger.debug(f"Retrieved {self.backend_name} instance (wait: {wait_time:.3f}s)")

            return pooled_backend.instance

        except BackendPoolExhaustedError as exc:
            with self._lock:
                self._stats.failed_requests += 1

            self.logger.error(f"Failed to get {self.backend_name} instance: {exc}")
            raise
        except Exception as exc:
            with self._lock:
                self._stats.failed_requests += 1

            self.logger.error(f"Failed to get {self.backend_name} instance: {exc}")
            raise BackendPoolError(f"Failed to get backend instance: {exc}") from exc

    def return_backend(self, backend_instance: Any) -> None:
        """
        Return a backend instance to the pool.

        Args:
            backend_instance: Backend instance to return
        """
        try:
            # Find the pooled backend
            pooled_backend = None
            with self._lock:
                for instance in self._active:
                    if instance.instance is backend_instance:
                        pooled_backend = instance
                        break

            if not pooled_backend:
                self.logger.warning(f"Unknown {self.backend_name} instance returned")
                return

            # Mark as inactive
            with self._lock:
                pooled_backend.is_active = False
                if pooled_backend in self._active:
                    self._active.remove(pooled_backend)

            # Return to available queue
            try:
                self._available.put_nowait(pooled_backend)
                self.logger.debug(f"Returned {self.backend_name} instance to pool")
            except Exception:
                # Pool is full, just let the instance be garbage collected
                self.logger.debug(f"Pool full, discarding {self.backend_name} instance")
                with self._lock:
                    if pooled_backend in self._all_instances:
                        self._all_instances.remove(pooled_backend)
                        self._stats.total_instances -= 1

        except Exception as e:
            self.logger.error(f"Failed to return {self.backend_name} instance: {e}")

    def get_statistics(self) -> PoolStatistics:
        """
        Get pool statistics.

        Returns:
            Pool statistics
        """
        with self._lock:
            self._update_stats()
            # Return a copy to prevent external modification
            return PoolStatistics(
                backend_name=self._stats.backend_name,
                total_instances=self._stats.total_instances,
                active_instances=self._stats.active_instances,
                available_instances=self._stats.available_instances,
                total_requests=self._stats.total_requests,
                successful_requests=self._stats.successful_requests,
                failed_requests=self._stats.failed_requests,
                average_wait_time=self._stats.average_wait_time,
                peak_usage=self._stats.peak_usage,
                created_at=self._stats.created_at,
                last_access=self._stats.last_access,
            )

    def get_status(self) -> PoolStatus:
        """
        Get pool status.

        Returns:
            Pool status
        """
        return self._status

    def shutdown(self) -> None:
        """Shutdown the pool and clean up resources."""
        self.logger.info(f"Shutting down {self.backend_name} pool")

        # Stop maintenance thread
        self._running = False
        if self._maintenance_thread and self._maintenance_thread.is_alive():
            self._maintenance_thread.join(timeout=5.0)

        # Clean up instances
        with self._lock:
            for instance in self._all_instances:
                try:
                    # Attempt to clean up backend instance
                    if hasattr(instance.instance, "cleanup"):
                        instance.instance.cleanup()
                    elif hasattr(instance.instance, "close"):
                        instance.instance.close()
                except Exception as e:
                    self.logger.warning(f"Error cleaning up {self.backend_name} instance: {e}")

            self._all_instances.clear()
            self._active.clear()

            # Clear available queue
            while not self._available.empty():
                try:
                    self._available.get_nowait()
                except Empty:
                    break

        self._status = PoolStatus.ERROR
        self.logger.info(f"Shutdown {self.backend_name} pool complete")


# Backend pool manager
class BackendPoolManager:
    """Manager for multiple backend pools."""

    def __init__(self) -> None:
        """Initialize the pool manager."""
        self.logger = get_logger("pool_manager")
        self._pools: dict[str, BackendPool] = {}
        self._lock = threading.Lock()

    def create_pool(
        self,
        backend_name: str,
        backend_class: type,
        min_instances: int = 1,
        max_instances: int = 5,
        **kwargs: Any,
    ) -> BackendPool:
        """
        Create a new backend pool.

        Args:
            backend_name: Name of the backend
            backend_class: Class of the backend to pool
            min_instances: Minimum number of instances to maintain
            max_instances: Maximum number of instances to create
            **kwargs: Additional arguments for BackendPool

        Returns:
            Created backend pool
        """
        with self._lock:
            if backend_name in self._pools:
                self.logger.warning(f"Pool for {backend_name} already exists")
                return self._pools[backend_name]

            pool = BackendPool(
                backend_class=backend_class,
                backend_name=backend_name,
                min_instances=min_instances,
                max_instances=max_instances,
                **kwargs,
            )

            self._pools[backend_name] = pool
            self.logger.info(f"Created pool for {backend_name}")

            return pool

    def get_pool(self, backend_name: str) -> BackendPool | None:
        """
        Get a backend pool by name.

        Args:
            backend_name: Name of the backend

        Returns:
            Backend pool or None if not found
        """
        with self._lock:
            return self._pools.get(backend_name)

    def get_backend(self, backend_name: str, timeout: float = 10.0) -> Any:
        """
        Get a backend instance from the specified pool.

        Args:
            backend_name: Name of the backend
            timeout: Maximum time to wait for an available instance

        Returns:
            Backend instance

        Raises:
            BackendPoolError: If pool is not found or exhausted
        """
        pool = self.get_pool(backend_name)
        if not pool:
            raise BackendPoolError(f"No pool found for backend: {backend_name}")

        return pool.get_backend(timeout)

    def return_backend(self, backend_name: str, backend_instance: Any) -> None:
        """
        Return a backend instance to the specified pool.

        Args:
            backend_name: Name of the backend
            backend_instance: Backend instance to return
        """
        pool = self.get_pool(backend_name)
        if pool:
            pool.return_backend(backend_instance)
        else:
            self.logger.warning(f"No pool found for backend: {backend_name}")

    def get_all_statistics(self) -> dict[str, PoolStatistics]:
        """
        Get statistics for all pools.

        Returns:
            Dictionary of pool statistics
        """
        with self._lock:
            return {name: pool.get_statistics() for name, pool in self._pools.items()}

    def shutdown_all(self) -> None:
        """Shutdown all pools."""
        with self._lock:
            for name, pool in self._pools.items():
                try:
                    pool.shutdown()
                except Exception as e:
                    self.logger.error(f"Error shutting down pool {name}: {e}")

            self._pools.clear()


# Global pool manager instance
_global_pool_manager: BackendPoolManager | None = None


def get_pool_manager() -> BackendPoolManager:
    """Get the global pool manager instance."""
    global _global_pool_manager
    if _global_pool_manager is None:
        _global_pool_manager = BackendPoolManager()
    return _global_pool_manager


def create_backend_pool(
    backend_name: str,
    backend_class: type,
    min_instances: int = 1,
    max_instances: int = 5,
    **kwargs: Any,
) -> BackendPool:
    """
    Create a new backend pool using the global pool manager.

    Args:
        backend_name: Name of the backend
        backend_class: Class of the backend to pool
        min_instances: Minimum number of instances to maintain
        max_instances: Maximum number of instances to create
        **kwargs: Additional arguments for BackendPool

    Returns:
        Created backend pool
    """
    manager = get_pool_manager()
    return manager.create_pool(
        backend_name=backend_name,
        backend_class=backend_class,
        min_instances=min_instances,
        max_instances=max_instances,
        **kwargs,
    )
