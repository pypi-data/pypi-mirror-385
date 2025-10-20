"""
Parallel processing system for Ariadne.

This module provides multi-threading, multi-processing, and distributed computing
support for high-performance quantum circuit simulation.
"""

from __future__ import annotations

import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from qiskit import QuantumCircuit

try:
    from ariadne import simulate
    from ariadne.core import get_logger
    from ariadne.types import SimulationResult
except ImportError:
    # Fallback for when running as a script
    import os
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ariadne import simulate
    from ariadne.core import get_logger
    from ariadne.types import SimulationResult


class ExecutionMode(Enum):
    """Execution modes for parallel processing."""

    SINGLE_THREAD = "single_thread"
    MULTI_THREAD = "multi_thread"
    MULTI_PROCESS = "multi_process"
    DISTRIBUTED = "distributed"


@dataclass
class ParallelSimulationRequest:
    """A request for parallel simulation."""

    circuit: QuantumCircuit
    shots: int = 1024
    backend: str | None = None
    request_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Post-initialization processing."""
        if self.request_id is None:
            # Generate a unique ID based on circuit hash and timestamp
            circuit_hash = hash(str(self.circuit.data))
            timestamp = int(time.time() * 1000000)
            self.request_id = f"req_{circuit_hash}_{timestamp}"


@dataclass
class ParallelSimulationResult:
    """Result of a parallel simulation."""

    request: ParallelSimulationRequest
    result: SimulationResult | None
    execution_time: float
    worker_id: str | None = None
    error: Exception | None = None

    @property
    def success(self) -> bool:
        """Check if simulation was successful."""
        return self.error is None and self.result is not None


class ParallelSimulator:
    """
    Parallel simulator for high-performance simulation.

    This class provides multi-threading, multi-processing, and distributed
    computing support for quantum circuit simulation.
    """

    def __init__(
        self,
        execution_mode: ExecutionMode = ExecutionMode.MULTI_PROCESS,
        max_workers: int | None = None,
        chunk_size: int = 1,
    ) -> None:
        """
        Initialize the parallel simulator.

        Args:
            execution_mode: Execution mode for parallel processing
            max_workers: Maximum number of worker threads/processes
            chunk_size: Number of circuits to process per chunk
        """
        self.logger = get_logger("parallel_simulator")
        self.execution_mode = execution_mode
        self.chunk_size = chunk_size

        # Determine number of workers
        if max_workers is None:
            if execution_mode == ExecutionMode.MULTI_THREAD:
                max_workers = min(32, (os.cpu_count() or 1) + 4)
            elif execution_mode == ExecutionMode.MULTI_PROCESS:
                max_workers = os.cpu_count() or 1
            else:
                max_workers = 1

        self.max_workers = max_workers

        # Create executor
        self._executor = None
        self._initialize_executor()

    def _initialize_executor(self) -> None:
        """Initialize the appropriate executor based on execution mode."""
        if self.execution_mode == ExecutionMode.MULTI_THREAD:
            self._executor = ThreadPoolExecutor(max_workers=self.max_workers)
        elif self.execution_mode == ExecutionMode.MULTI_PROCESS:
            self._executor = ProcessPoolExecutor(max_workers=self.max_workers)
        elif self.execution_mode == ExecutionMode.SINGLE_THREAD:
            self._executor = None
        elif self.execution_mode == ExecutionMode.DISTRIBUTED:
            # For distributed computing, we'd use a more sophisticated setup
            # For now, fall back to multi-processing
            self._executor = ProcessPoolExecutor(max_workers=self.max_workers)
            self.logger.warning("Distributed mode not fully implemented, using multi-processing")
        else:
            raise ValueError(f"Unknown execution mode: {self.execution_mode}")

    def shutdown(self) -> None:
        """Shutdown the parallel simulator."""
        if self._executor:
            self._executor.shutdown(wait=True)
            self._executor = None

        self.logger.info("Parallel simulator shutdown")

    def simulate(
        self, circuit: QuantumCircuit, shots: int = 1024, backend: str | None = None
    ) -> ParallelSimulationResult:
        """
        Simulate a quantum circuit in parallel.

        Args:
            circuit: Quantum circuit to simulate
            shots: Number of measurement shots
            backend: Backend to use for simulation

        Returns:
            Parallel simulation result
        """
        # Create request
        request = ParallelSimulationRequest(circuit=circuit, shots=shots, backend=backend)

        # Simulate
        return self._simulate_request(request)

    def simulate_batch(self, requests: list[ParallelSimulationRequest]) -> list[ParallelSimulationResult]:
        """
        Simulate multiple circuits in parallel.

        Args:
            requests: List of simulation requests

        Returns:
            List of parallel simulation results
        """
        if not requests:
            return []

        # Choose simulation method based on execution mode
        if self.execution_mode == ExecutionMode.SINGLE_THREAD:
            return self._simulate_batch_single_thread(requests)
        elif self.execution_mode in [ExecutionMode.MULTI_THREAD, ExecutionMode.MULTI_PROCESS]:
            return self._simulate_batch_parallel(requests)
        else:
            # Fall back to single thread for unknown modes
            return self._simulate_batch_single_thread(requests)

    def _simulate_request(self, request: ParallelSimulationRequest) -> ParallelSimulationResult:
        """Simulate a single request."""
        start_time = time.time()

        try:
            # Prepare simulation arguments
            kwargs = {"shots": request.shots}
            if request.backend:
                kwargs["backend"] = request.backend

            # Run simulation
            result = simulate(request.circuit, **kwargs)

            execution_time = time.time() - start_time

            return ParallelSimulationResult(request=request, result=result, execution_time=execution_time)

        except Exception as e:
            execution_time = time.time() - start_time

            self.logger.error(f"Simulation failed for request {request.request_id}: {e}")

            return ParallelSimulationResult(request=request, result=None, execution_time=execution_time, error=e)

    def _simulate_batch_single_thread(
        self, requests: list[ParallelSimulationRequest]
    ) -> list[ParallelSimulationResult]:
        """Simulate batch in single thread."""
        results = []

        for request in requests:
            result = self._simulate_request(request)
            results.append(result)

        return results

    def _simulate_batch_parallel(self, requests: list[ParallelSimulationRequest]) -> list[ParallelSimulationResult]:
        """Simulate batch in parallel."""
        results = [None] * len(requests)

        # Submit all tasks
        future_to_index = {}
        for i, request in enumerate(requests):
            future = self._executor.submit(self._simulate_request, request)
            future_to_index[future] = i

        # Collect results as they complete
        for future in as_completed(future_to_index):
            index = future_to_index[future]
            try:
                result = future.result()
                results[index] = result
            except Exception as e:
                # Create error result
                request = requests[index]
                results[index] = ParallelSimulationResult(request=request, result=None, execution_time=0.0, error=e)

        return results

    def simulate_circuit_variations(
        self,
        base_circuit: QuantumCircuit,
        parameter_variations: list[dict[str, Any]],
        shots: int = 1024,
        backend: str | None = None,
    ) -> list[ParallelSimulationResult]:
        """
        Simulate variations of a base circuit with different parameters.

        Args:
            base_circuit: Base circuit to vary
            parameter_variations: List of parameter variations
            shots: Number of measurement shots
            backend: Backend to use for simulation

        Returns:
            List of parallel simulation results
        """
        # Create requests for each variation
        requests = []

        for i, params in enumerate(parameter_variations):
            # Create a copy of the base circuit
            circuit = base_circuit.copy()

            # Apply parameter variations
            circuit = self._apply_parameter_variations(circuit, params)

            # Create request
            request = ParallelSimulationRequest(
                circuit=circuit,
                shots=shots,
                backend=backend,
                request_id=f"variation_{i}",
                metadata={"variation_index": i, "parameters": params},
            )

            requests.append(request)

        # Simulate all variations
        return self.simulate_batch(requests)

    def _apply_parameter_variations(self, circuit: QuantumCircuit, params: dict[str, Any]) -> QuantumCircuit:
        """Apply parameter variations to a circuit."""
        # This is a simplified implementation
        # In a production system, this would handle various parameter types

        # For now, just return the original circuit
        # In a real implementation, this would modify the circuit based on parameters
        return circuit


class DistributedSimulator:
    """
    Distributed simulator for multi-node computing.

    This class provides distributed computing support for large-scale
    quantum circuit simulation across multiple nodes.
    """

    def __init__(self, node_addresses: list[str], local_rank: int = 0):
        """
        Initialize the distributed simulator.

        Args:
            node_addresses: List of node addresses
            local_rank: Rank of this node
        """
        self.logger = get_logger("distributed_simulator")
        self.node_addresses = node_addresses
        self.local_rank = local_rank
        self.num_nodes = len(node_addresses)

        # Initialize communication
        self._initialize_communication()

    def _initialize_communication(self) -> None:
        """Initialize communication between nodes."""
        # This is a placeholder for distributed communication setup
        # In a production system, this would use MPI, Dask, Ray, or similar

        self.logger.info(f"Initialized distributed simulator with {self.num_nodes} nodes")
        self.logger.info(f"Local rank: {self.local_rank}")

    def simulate_distributed(
        self, circuit: QuantumCircuit, shots: int = 1024, backend: str | None = None
    ) -> SimulationResult:
        """
        Simulate a circuit across multiple nodes.

        Args:
            circuit: Circuit to simulate
            shots: Number of measurement shots
            backend: Backend to use for simulation

        Returns:
            Simulation result
        """
        # This is a placeholder for distributed simulation
        # In a production system, this would partition the circuit
        # and distribute work across nodes

        self.logger.info("Running distributed simulation")

        # For now, just run locally
        return simulate(circuit, shots=shots, backend=backend)

    def shutdown(self) -> None:
        """Shutdown the distributed simulator."""
        # Clean up communication resources
        self.logger.info("Distributed simulator shutdown")


class ParallelBenchmark:
    """Benchmark for parallel performance evaluation."""

    def __init__(self) -> None:
        """Initialize the parallel benchmark."""
        self.logger = get_logger("parallel_benchmark")

    def benchmark_execution_modes(
        self, circuits: list[QuantumCircuit], shots: int = 1024, backend: str | None = None
    ) -> dict[str, dict[str, Any]]:
        """
        Benchmark different execution modes.

        Args:
            circuits: List of circuits to benchmark
            shots: Number of measurement shots
            backend: Backend to use for simulation

        Returns:
            Benchmark results for each execution mode
        """
        results = {}

        # Test single thread
        self.logger.info("Benchmarking single-thread execution")
        single_thread_sim = ParallelSimulator(execution_mode=ExecutionMode.SINGLE_THREAD)
        start_time = time.time()
        single_thread_results = single_thread_sim.simulate_batch(
            [ParallelSimulationRequest(circuit=circuit, shots=shots, backend=backend) for circuit in circuits]
        )
        single_thread_time = time.time() - start_time

        results["single_thread"] = {
            "total_time": single_thread_time,
            "success_rate": sum(1 for r in single_thread_results if r.success) / len(single_thread_results),
            "avg_time": sum(r.execution_time for r in single_thread_results) / len(single_thread_results),
        }

        single_thread_sim.shutdown()

        # Test multi-thread
        self.logger.info("Benchmarking multi-thread execution")
        multi_thread_sim = ParallelSimulator(execution_mode=ExecutionMode.MULTI_THREAD)
        start_time = time.time()
        multi_thread_results = multi_thread_sim.simulate_batch(
            [ParallelSimulationRequest(circuit=circuit, shots=shots, backend=backend) for circuit in circuits]
        )
        multi_thread_time = time.time() - start_time

        results["multi_thread"] = {
            "total_time": multi_thread_time,
            "success_rate": sum(1 for r in multi_thread_results if r.success) / len(multi_thread_results),
            "avg_time": sum(r.execution_time for r in multi_thread_results) / len(multi_thread_results),
            "speedup": single_thread_time / multi_thread_time,
        }

        multi_thread_sim.shutdown()

        # Test multi-process
        self.logger.info("Benchmarking multi-process execution")
        multi_process_sim = ParallelSimulator(execution_mode=ExecutionMode.MULTI_PROCESS)
        start_time = time.time()
        multi_process_results = multi_process_sim.simulate_batch(
            [ParallelSimulationRequest(circuit=circuit, shots=shots, backend=backend) for circuit in circuits]
        )
        multi_process_time = time.time() - start_time

        results["multi_process"] = {
            "total_time": multi_process_time,
            "success_rate": sum(1 for r in multi_process_results if r.success) / len(multi_process_results),
            "avg_time": sum(r.execution_time for r in multi_process_results) / len(multi_process_results),
            "speedup": single_thread_time / multi_process_time,
        }

        multi_process_sim.shutdown()

        return results

    def benchmark_scaling(
        self,
        circuit: QuantumCircuit,
        shots: int = 1024,
        backend: str | None = None,
        max_workers: int = 8,
    ) -> dict[int, dict[str, Any]]:
        """
        Benchmark scaling with different numbers of workers.

        Args:
            circuit: Circuit to benchmark
            shots: Number of measurement shots
            backend: Backend to use for simulation
            max_workers: Maximum number of workers to test

        Returns:
            Scaling results for each worker count
        """
        results = {}

        for num_workers in range(1, max_workers + 1):
            self.logger.info(f"Benchmarking with {num_workers} workers")

            # Create simulator
            sim = ParallelSimulator(execution_mode=ExecutionMode.MULTI_PROCESS, max_workers=num_workers)

            # Create multiple requests
            requests = [
                ParallelSimulationRequest(circuit=circuit, shots=shots, backend=backend)
                for _ in range(num_workers * 2)  # 2x more requests than workers
            ]

            # Benchmark
            start_time = time.time()
            sim_results = sim.simulate_batch(requests)
            total_time = time.time() - start_time

            # Calculate metrics
            success_rate = sum(1 for r in sim_results if r.success) / len(sim_results)
            avg_time = sum(r.execution_time for r in sim_results) / len(sim_results)
            throughput = len(sim_results) / total_time

            results[num_workers] = {
                "total_time": total_time,
                "success_rate": success_rate,
                "avg_time": avg_time,
                "throughput": throughput,
            }

            sim.shutdown()

        return results


# Global parallel simulator instance
_global_parallel_simulator: ParallelSimulator | None = None


def get_parallel_simulator(
    execution_mode: ExecutionMode = ExecutionMode.MULTI_PROCESS, max_workers: int | None = None
) -> ParallelSimulator:
    """
    Get the global parallel simulator instance.

    Args:
        execution_mode: Execution mode for parallel processing
        max_workers: Maximum number of worker threads/processes

    Returns:
        Parallel simulator instance
    """
    global _global_parallel_simulator
    if _global_parallel_simulator is None:
        _global_parallel_simulator = ParallelSimulator(execution_mode=execution_mode, max_workers=max_workers)
    return _global_parallel_simulator


def simulate_parallel(
    circuits: list[QuantumCircuit],
    shots: int = 1024,
    backend: str | None = None,
    execution_mode: ExecutionMode = ExecutionMode.MULTI_PROCESS,
) -> list[ParallelSimulationResult]:
    """
    Simulate multiple circuits in parallel using the global simulator.

    Args:
        circuits: List of quantum circuits to simulate
        shots: Number of measurement shots
        backend: Backend to use for simulation
        execution_mode: Execution mode for parallel processing

    Returns:
        List of parallel simulation results
    """
    simulator = get_parallel_simulator(execution_mode=execution_mode)

    # Create requests
    requests = [ParallelSimulationRequest(circuit=circuit, shots=shots, backend=backend) for circuit in circuits]

    # Simulate batch
    return simulator.simulate_batch(requests)
