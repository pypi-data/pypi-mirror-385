"""
Asynchronous simulation interface for Ariadne.

This module provides async/await patterns for non-blocking simulation operations,
concurrent execution of multiple circuits, and async backend interfaces.
"""

from __future__ import annotations

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any

from qiskit import QuantumCircuit

try:
    from ariadne import simulate
    from ariadne.backends import get_health_checker
    from ariadne.core import get_logger
    from ariadne.types import BackendType, SimulationResult
except ImportError:
    # Fallback for when running as a script
    import os
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ariadne import simulate
    from ariadne.backends import get_health_checker
    from ariadne.core import get_logger
    from ariadne.types import BackendType, SimulationResult


@dataclass
class AsyncSimulationRequest:
    """A request for asynchronous simulation."""

    circuit: QuantumCircuit
    shots: int = 1024
    backend: str | None = None
    request_id: str | None = None
    priority: int = 0  # Higher priority requests are processed first
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization processing."""
        if self.request_id is None:
            # Generate a unique ID based on circuit hash and timestamp
            circuit_hash = hash(str(self.circuit.data))
            timestamp = int(time.time() * 1000000)
            self.request_id = f"req_{circuit_hash}_{timestamp}"


@dataclass
class AsyncSimulationResult:
    """Result of an asynchronous simulation."""

    request: AsyncSimulationRequest
    result: SimulationResult | None
    execution_time: float
    error: Exception | None = None
    timestamp: float = field(default_factory=time.time)

    @property
    def success(self) -> bool:
        """Check if simulation was successful."""
        return self.error is None and self.result is not None


class AsyncSimulator:
    """
    Asynchronous simulator for non-blocking simulation operations.

    This class provides async/await patterns for simulation operations,
    allowing for concurrent execution of multiple circuits and non-blocking
    processing of I/O-bound operations.
    """

    def __init__(self, max_concurrent_simulations: int = 4, thread_pool_size: int | None = None):
        """
        Initialize the async simulator.

        Args:
            max_concurrent_simulations: Maximum number of concurrent simulations
            thread_pool_size: Size of the thread pool for CPU-bound operations
        """
        self.logger = get_logger("async_simulator")
        self.max_concurrent_simulations = max_concurrent_simulations
        self.thread_pool_size = thread_pool_size or max_concurrent_simulations

        # Semaphore to limit concurrent simulations
        self._semaphore = asyncio.Semaphore(max_concurrent_simulations)

        # Thread pool for CPU-bound operations
        self._executor = ThreadPoolExecutor(max_workers=self.thread_pool_size)

        # Request queue for priority-based processing
        self._request_queue: asyncio.PriorityQueue[tuple[int, AsyncSimulationRequest]] = asyncio.PriorityQueue()

        # Background task processor
        self._processor_task: asyncio.Task | None = None
        self._running = False

    async def start(self) -> None:
        """Start the async simulator background processor."""
        if self._running:
            return

        self._running = True
        self._processor_task = asyncio.create_task(self._process_requests())
        self.logger.info("Async simulator started")

    async def stop(self) -> None:
        """Stop the async simulator background processor."""
        if not self._running:
            return

        self._running = False

        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass

        # Shutdown thread pool
        self._executor.shutdown(wait=True)

        self.logger.info("Async simulator stopped")

    async def simulate(
        self,
        circuit: QuantumCircuit,
        shots: int = 1024,
        backend: str | None = None,
        priority: int = 0,
    ) -> AsyncSimulationResult:
        """
        Simulate a quantum circuit asynchronously.

        Args:
            circuit: Quantum circuit to simulate
            shots: Number of measurement shots
            backend: Backend to use for simulation
            priority: Request priority (higher = processed first)

        Returns:
            Async simulation result
        """
        # Create request
        request = AsyncSimulationRequest(circuit=circuit, shots=shots, backend=backend, priority=priority)

        # Submit request
        return await self._submit_request(request)

    async def simulate_batch(
        self, requests: list[AsyncSimulationRequest], return_exceptions: bool = False
    ) -> list[AsyncSimulationResult]:
        """
        Simulate multiple circuits concurrently.

        Args:
            requests: List of simulation requests
            return_exceptions: Whether to return exceptions in results

        Returns:
            List of async simulation results
        """
        # Create tasks for all requests
        tasks = [self._submit_request(request) for request in requests]

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=return_exceptions)

        # Convert exceptions to error results if needed
        if not return_exceptions:
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    # Create error result
                    error_result = AsyncSimulationResult(
                        request=requests[i], result=None, execution_time=0.0, error=result
                    )
                    processed_results.append(error_result)
                else:
                    processed_results.append(result)
            return processed_results

        return results

    async def _submit_request(self, request: AsyncSimulationRequest) -> AsyncSimulationResult:
        """
        Submit a simulation request for processing.

        Args:
            request: Simulation request

        Returns:
            Async simulation result
        """
        # Acquire semaphore to limit concurrent simulations
        async with self._semaphore:
            start_time = time.time()

            try:
                # Run simulation in thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(self._executor, self._run_simulation, request)

                execution_time = time.time() - start_time

                return AsyncSimulationResult(request=request, result=result, execution_time=execution_time)

            except Exception as e:
                execution_time = time.time() - start_time

                self.logger.error(f"Simulation failed for request {request.request_id}: {e}")

                return AsyncSimulationResult(request=request, result=None, execution_time=execution_time, error=e)

    def _run_simulation(self, request: AsyncSimulationRequest) -> SimulationResult:
        """
        Run a simulation in the thread pool.

        Args:
            request: Simulation request

        Returns:
            Simulation result
        """
        # Prepare simulation arguments
        kwargs = {"shots": request.shots}
        if request.backend:
            kwargs["backend"] = request.backend

        # Run simulation
        return simulate(request.circuit, **kwargs)

    async def _process_requests(self) -> None:
        """Background task to process requests from the queue."""
        while self._running:
            try:
                # Get next request (with timeout to allow for cancellation)
                try:
                    priority, request = await asyncio.wait_for(self._request_queue.get(), timeout=1.0)
                except TimeoutError:
                    continue

                # Process request
                await self._submit_request(request)

                # Mark task as done
                self._request_queue.task_done()

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error processing request: {e}")


class AsyncBackendInterface:
    """
    Async interface for backend operations.

    This class provides async methods for backend health checking,
    performance monitoring, and other I/O-bound operations.
    """

    def __init__(self):
        """Initialize the async backend interface."""
        self.logger = get_logger("async_backend")
        self._health_checker = get_health_checker()

    async def check_backend_health(self, backend: BackendType) -> dict[str, Any]:
        """
        Check backend health asynchronously.

        Args:
            backend: Backend type to check

        Returns:
            Health check result
        """
        loop = asyncio.get_event_loop()

        # Run health check in thread pool
        result = await loop.run_in_executor(None, self._health_checker.check_backend_health, backend)

        return {
            "backend": backend.value,
            "status": result.status.value,
            "message": result.message,
            "response_time": result.response_time,
            "timestamp": result.timestamp,
            "details": result.details,
        }

    async def check_all_backends_health(self) -> dict[str, dict[str, Any]]:
        """
        Check health of all backends concurrently.

        Returns:
            Dictionary of health check results for all backends
        """
        from ariadne.types import BackendType

        # Create tasks for all backends
        tasks = [self.check_backend_health(backend) for backend in list(BackendType)]

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        health_results = {}
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                backend = list(BackendType)[i]
                health_results[backend.value] = {
                    "backend": backend.value,
                    "status": "error",
                    "message": str(result),
                    "response_time": 0.0,
                    "timestamp": time.time(),
                    "details": {"error": str(result)},
                }
            else:
                health_results[result["backend"]] = result

        return health_results

    async def monitor_backend_performance(
        self, backend: BackendType, duration: float = 60.0, interval: float = 5.0
    ) -> list[dict[str, Any]]:
        """
        Monitor backend performance over time.

        Args:
            backend: Backend to monitor
            duration: Monitoring duration in seconds
            interval: Monitoring interval in seconds

        Returns:
            List of performance metrics
        """
        metrics = []
        start_time = time.time()

        while time.time() - start_time < duration:
            # Get current metrics
            loop = asyncio.get_event_loop()
            backend_metrics = await loop.run_in_executor(None, self._get_backend_metrics, backend)

            metrics.append({"backend": backend.value, "timestamp": time.time(), "metrics": backend_metrics})

            # Wait for next interval
            await asyncio.sleep(interval)

        return metrics

    def _get_backend_metrics(self, backend: BackendType) -> dict[str, Any]:
        """Get current metrics for a backend."""
        # Get health metrics
        health_metrics = self._health_checker.get_backend_metrics(backend)

        if not health_metrics:
            return {"status": "unknown"}

        return {
            "status": health_metrics.status.value,
            "response_time": health_metrics.response_time,
            "success_rate": health_metrics.success_rate,
            "uptime_percentage": health_metrics.uptime_percentage,
            "total_checks": health_metrics.total_checks,
            "consecutive_failures": health_metrics.consecutive_failures,
        }


# Global async simulator instance
_global_async_simulator: AsyncSimulator | None = None


async def get_async_simulator() -> AsyncSimulator:
    """Get the global async simulator instance."""
    global _global_async_simulator
    if _global_async_simulator is None:
        _global_async_simulator = AsyncSimulator()
        await _global_async_simulator.start()
    return _global_async_simulator


async def simulate_async(
    circuit: QuantumCircuit, shots: int = 1024, backend: str | None = None, priority: int = 0
) -> AsyncSimulationResult:
    """
    Simulate a quantum circuit asynchronously using the global simulator.

    Args:
        circuit: Quantum circuit to simulate
        shots: Number of measurement shots
        backend: Backend to use for simulation
        priority: Request priority

    Returns:
        Async simulation result
    """
    simulator = await get_async_simulator()
    return await simulator.simulate(circuit, shots, backend, priority)


async def simulate_batch_async(
    circuits: list[QuantumCircuit],
    shots: int = 1024,
    backend: str | None = None,
    return_exceptions: bool = False,
) -> list[AsyncSimulationResult]:
    """
    Simulate multiple circuits asynchronously.

    Args:
        circuits: List of quantum circuits to simulate
        shots: Number of measurement shots
        backend: Backend to use for simulation
        return_exceptions: Whether to return exceptions in results

    Returns:
        List of async simulation results
    """
    # Create requests
    requests = [AsyncSimulationRequest(circuit=circuit, shots=shots, backend=backend) for circuit in circuits]

    # Get simulator and run batch simulation
    simulator = await get_async_simulator()
    return await simulator.simulate_batch(requests, return_exceptions)
