#!/usr/bin/env python3
"""
Ariadne Performance Optimizations Demo

This example demonstrates the performance optimization features of Ariadne,
including asynchronous operations, circuit optimization, memory management,
parallel processing, and intelligent caching.
"""

import asyncio
import time

from qiskit import QuantumCircuit

# Import Ariadne components
from ariadne import simulate
from ariadne.async_ import simulate_batch_async
from ariadne.core import configure_logging, get_logger
from ariadne.optimization import (
    OptimizationType,
    analyze_optimization_opportunities,
    optimize_circuit,
)
from ariadne.performance import (
    ExecutionMode,
    MemoryLevel,
    ParallelBenchmark,
    get_memory_manager,
    get_memory_stats,
    get_parallel_simulator,
    get_simulation_cache,
    optimize_memory,
    simulate_parallel,
)
from ariadne.performance.cache import memoize


def demo_async_operations():
    """Demonstrate asynchronous operations."""
    print("\n=== Asynchronous Operations Demo ===")

    logger = get_logger("async_demo")
    logger.info("Preparing asynchronous simulation batch")

    # Create test circuits
    circuits = []
    for _ in range(5):
        circuit = QuantumCircuit(3, 3)
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.cx(1, 2)
        circuit.measure_all()
        circuits.append(circuit)

    # Run async simulation
    print("Running asynchronous simulations...")
    start_time = time.time()

    async def run_async_simulations():
        results = await simulate_batch_async(circuits, shots=100)
        return results

    # Run async operations
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        results = loop.run_until_complete(run_async_simulations())
    finally:
        loop.close()

    async_time = time.time() - start_time

    # Run synchronous simulations for comparison
    print("Running synchronous simulations for comparison...")
    start_time = time.time()

    sync_results = []
    for circuit in circuits:
        result = simulate(circuit, shots=100)
        sync_results.append(result)

    sync_time = time.time() - start_time

    # Compare results
    print("\nResults:")
    print(f"  Async time: {async_time:.3f}s")
    print(f"  Sync time: {sync_time:.3f}s")
    print(f"  Speedup: {sync_time / async_time:.2f}x")

    # Check results
    for i, (async_result, sync_result) in enumerate(zip(results, sync_results, strict=False)):
        if async_result.success and async_result.result:
            print(f"  Circuit {i + 1}: Success")
        else:
            print(f"  Circuit {i + 1}: Failed - {async_result.error}")

        async_counts = getattr(async_result, "counts", None)
        sync_counts = getattr(sync_result, "counts", None)
        if async_counts is not None and sync_counts is not None:
            status = "match" if async_counts == sync_counts else "differ"
            print(f"    Result counts {status} between async and sync runs")


def demo_circuit_optimization():
    """Demonstrate circuit optimization."""
    print("\n=== Circuit Optimization Demo ===")

    logger = get_logger("optimization_demo")
    logger.info("Analyzing circuit for optimization opportunities")

    # Create a circuit that can be optimized
    circuit = QuantumCircuit(4, 4)

    # Add some gates that can be optimized
    circuit.h(0)
    circuit.h(0)  # Redundant H gate
    circuit.x(1)
    circuit.x(1)  # Redundant X gate
    circuit.cx(0, 1)
    circuit.cx(0, 1)  # Redundant CX gate
    circuit.cx(1, 2)
    circuit.cx(2, 3)
    circuit.h(2)
    circuit.h(2)  # Redundant H gate
    circuit.measure_all()

    print("Original circuit:")
    print(f"  Qubits: {circuit.num_qubits}")
    print(f"  Depth: {circuit.depth()}")
    print(f"  Gate count: {len(circuit.data)}")

    # Analyze optimization opportunities
    print("\nAnalyzing optimization opportunities...")
    analysis = analyze_optimization_opportunities(circuit)

    print("Optimization opportunities:")
    for opt_type, opportunities in analysis["optimization_opportunities"].items():
        if "potential_reduction" in opportunities:
            print(f"  {opt_type}: {opportunities['potential_reduction']} potential reductions")

    print("Recommendations:")
    for rec in analysis["recommendations"]:
        print(f"  - {rec}")

    # Apply optimizations
    print("\nApplying optimizations...")
    result = optimize_circuit(circuit, OptimizationType.GATE_CANCELLATION)

    print("Optimized circuit:")
    print(f"  Qubits: {result.optimized_circuit.num_qubits}")
    print(f"  Depth: {result.optimized_circuit.depth()}")
    print(f"  Gate count: {len(result.optimized_circuit.data)}")
    print(f"  Depth reduction: {result.depth_reduction:.2f}%")
    print(f"  Gate count reduction: {result.gate_count_reduction:.2f}%")
    print(f"  Optimization time: {result.execution_time:.3f}s")

    # Simulate both circuits to verify correctness
    print("\nVerifying optimization correctness...")
    original_result = simulate(circuit, shots=100)
    optimized_result = simulate(result.optimized_circuit, shots=100)

    print(f"Original result: {original_result.counts}")
    print(f"Optimized result: {optimized_result.counts}")

    # Check if results are similar
    if original_result.counts == optimized_result.counts:
        print("✓ Optimization preserved circuit behavior")
    else:
        print("✗ Optimization changed circuit behavior")


def demo_memory_management():
    """Demonstrate memory management."""
    print("\n=== Memory Management Demo ===")

    logger = get_logger("memory_demo")
    logger.info("Inspecting memory usage and optimization suggestions")

    # Get memory manager
    memory_manager = get_memory_manager()

    # Get current memory stats
    print("Current memory statistics:")
    stats = get_memory_stats()
    print(f"  Total memory: {stats.total_memory_mb:.1f} MB")
    print(f"  Used memory: {stats.used_memory_mb:.1f} MB")
    print(f"  Available memory: {stats.available_memory_mb:.1f} MB")
    print(f"  Process memory: {stats.process_memory_mb:.1f} MB")
    print(f"  Memory level: {stats.memory_level.value}")

    # Get memory pool stats
    pool = memory_manager.get_memory_pool()
    pool_stats = pool.get_stats()
    print("\nMemory pool statistics:")
    print(f"  Hits: {pool_stats['hits']}")
    print(f"  Misses: {pool_stats['misses']}")
    print(f"  Hit rate: {pool_stats['hit_rate']:.2%}")
    print(f"  Created: {pool_stats['created']}")
    print(f"  Reused: {pool_stats['reused']}")

    # Optimize memory
    print("\nOptimizing memory...")
    optimize_memory(aggressive=False)

    # Get updated stats
    updated_stats = get_memory_stats()
    print(f"Updated process memory: {updated_stats.process_memory_mb:.1f} MB")

    # Get memory suggestions
    suggestions = memory_manager.monitor.suggest_optimizations(updated_stats)
    if suggestions:
        print("\nMemory optimization suggestions:")
        for suggestion in suggestions:
            print(f"  - {suggestion}")
    else:
        print("\nNo memory optimization suggestions needed")


def demo_parallel_processing():
    """Demonstrate parallel processing."""
    print("\n=== Parallel Processing Demo ===")

    logger = get_logger("parallel_demo")
    logger.info("Benchmarking different execution modes")

    # Create test circuits
    circuits = []
    for _ in range(8):
        circuit = QuantumCircuit(3, 3)
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.cx(1, 2)
        circuit.rz(0.5, 2)
        circuit.measure_all()
        circuits.append(circuit)

    # Benchmark different execution modes
    print("Benchmarking execution modes...")
    benchmark = ParallelBenchmark()

    results = benchmark.benchmark_execution_modes(circuits, shots=100)

    print("\nBenchmark results:")
    for mode, result in results.items():
        print(f"  {mode}:")
        print(f"    Total time: {result['total_time']:.3f}s")
        print(f"    Success rate: {result['success_rate']:.2%}")
        print(f"    Average time: {result['avg_time']:.3f}s")
        if "speedup" in result:
            print(f"    Speedup: {result['speedup']:.2f}x")

    # Test parallel simulation
    print("\nTesting parallel simulation...")
    start_time = time.time()

    parallel_results = simulate_parallel(circuits, shots=100, execution_mode=ExecutionMode.MULTI_PROCESS)

    parallel_time = time.time() - start_time

    # Test sequential simulation
    print("Testing sequential simulation...")
    start_time = time.time()

    sequential_results = []
    for circuit in circuits:
        result = simulate(circuit, shots=100)
        sequential_results.append(result)

    sequential_time = time.time() - start_time

    # Compare results
    print("\nParallel vs Sequential:")
    print(f"  Parallel time: {parallel_time:.3f}s")
    print(f"  Sequential time: {sequential_time:.3f}s")
    print(f"  Speedup: {sequential_time / parallel_time:.2f}x")

    # Check results
    success_count = sum(1 for r in parallel_results if r.success)
    print(f"  Success rate: {success_count}/{len(parallel_results)} ({success_count / len(parallel_results):.2%})")


def demo_intelligent_caching():
    """Demonstrate intelligent caching."""
    print("\n=== Intelligent Caching Demo ===")

    logger = get_logger("cache_demo")
    logger.info("Demonstrating cache hits and memoization")

    # Get simulation cache
    cache = get_simulation_cache()

    # Create a test circuit
    circuit = QuantumCircuit(2, 2)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure_all()

    # First simulation (not cached)
    print("First simulation (not cached)...")
    start_time = time.time()
    result1 = simulate(circuit, shots=1000)
    first_time = time.time() - start_time

    # Cache the result
    cache.set(circuit, 1000, result1)

    # Second simulation (cached)
    print("Second simulation (cached)...")
    start_time = time.time()
    result2 = cache.get(circuit, 1000)
    second_time = time.time() - start_time

    print("\nCaching results:")
    print(f"  First time: {first_time:.4f}s")
    print(f"  Second time: {second_time:.4f}s")
    print(f"  Speedup: {first_time / second_time:.1f}x")

    # Verify results are the same
    if result1.counts == result2.counts:
        print("✓ Cached result matches original")
    else:
        print("✗ Cached result differs from original")

    # Get cache statistics
    cache_stats = cache.cache.get_stats()
    print("\nCache statistics:")
    print(f"  Hits: {cache_stats['hits']}")
    print(f"  Misses: {cache_stats['misses']}")
    print(f"  Hit rate: {cache_stats['hit_rate']:.2%}")
    print(f"  Size: {cache_stats['size']} entries")

    # Demonstrate memoization
    print("\nDemonstrating memoization...")

    @memoize(ttl=60)  # Cache for 60 seconds
    def expensive_calculation(n):
        """Simulate an expensive calculation."""
        time.sleep(0.1)  # Simulate work
        return n * n

    # First call
    start_time = time.time()
    result1 = expensive_calculation(42)
    first_call_time = time.time() - start_time

    # Second call (should be cached)
    start_time = time.time()
    result2 = expensive_calculation(42)
    second_call_time = time.time() - start_time

    print("Memoization results:")
    print(f"  First call: {first_call_time:.4f}s (result: {result1})")
    print(f"  Second call: {second_call_time:.4f}s (result: {result2})")
    print(f"  Speedup: {first_call_time / second_call_time:.1f}x")

    if result1 == result2:
        print("✓ Memoized result matches original")
    else:
        print("✗ Memoized result differs from original")


def demo_performance_integration():
    """Demonstrate integration of all performance optimizations."""
    print("\n=== Performance Integration Demo ===")

    logger = get_logger("integration_demo")
    logger.info("Running end-to-end performance workflow")

    # Create a more complex circuit
    circuit = QuantumCircuit(5, 5)

    # Add a variety of gates
    for i in range(5):
        circuit.h(i)

    for i in range(4):
        circuit.cx(i, i + 1)

    for i in range(5):
        circuit.rz(0.5, i)
        circuit.sx(i)

    circuit.measure_all()

    print("Test circuit:")
    print(f"  Qubits: {circuit.num_qubits}")
    print(f"  Depth: {circuit.depth()}")
    print(f"  Gate count: {len(circuit.data)}")

    # Step 1: Optimize circuit
    print("\nStep 1: Optimizing circuit...")
    opt_result = optimize_circuit(circuit, "aggressive")
    optimized_circuit = opt_result.optimized_circuit

    print(f"  Depth reduction: {opt_result.depth_reduction:.2f}%")
    print(f"  Gate count reduction: {opt_result.gate_count_reduction:.2f}%")

    # Step 2: Check memory
    print("\nStep 2: Checking memory...")
    memory_stats = get_memory_stats()
    print(f"  Memory level: {memory_stats.memory_level.value}")

    if memory_stats.memory_level == MemoryLevel.HIGH:
        print("  Optimizing memory...")
        optimize_memory()

    # Step 3: Simulate with caching
    print("\nStep 3: Simulating with caching...")
    cache = get_simulation_cache()

    start_time = time.time()
    result = simulate(optimized_circuit, shots=1000)
    simulation_time = time.time() - start_time

    # Cache result
    cache.set(optimized_circuit, 1000, result)

    # Step 4: Simulate again (should be cached)
    print("\nStep 4: Simulating again (should be cached)...")
    start_time = time.time()
    cached_result = cache.get(optimized_circuit, 1000)
    cached_time = time.time() - start_time

    print(f"  Original simulation: {simulation_time:.4f}s")
    print(f"  Cached simulation: {cached_time:.4f}s")
    print(f"  Cache speedup: {simulation_time / cached_time:.1f}x")
    if cached_result and cached_result.counts == result.counts:
        print("  Cached counts verified against original run")

    # Step 5: Parallel batch simulation
    print("\nStep 5: Parallel batch simulation...")

    # Create multiple similar circuits
    circuits = [optimized_circuit.copy() for _ in range(4)]

    start_time = time.time()
    parallel_results = simulate_parallel(circuits, shots=1000)
    parallel_time = time.time() - start_time

    print(f"  Parallel simulation time: {parallel_time:.4f}s")
    print(f"  Throughput: {len(circuits) / parallel_time:.1f} circuits/s")
    successes = sum(1 for res in parallel_results if res.success)
    print(f"  Successful parallel runs: {successes}/{len(parallel_results)}")

    # Step 6: Final performance summary
    print("\nPerformance Summary:")
    print(f"  Circuit optimization: {opt_result.depth_reduction:.1f}% depth reduction")
    print(f"  Memory usage: {memory_stats.process_memory_mb:.1f} MB")
    print(f"  Cache speedup: {simulation_time / cached_time:.1f}x")
    print(f"  Parallel throughput: {len(circuits) / parallel_time:.1f} circuits/s")

    # Get final cache stats
    cache_stats = cache.cache.get_stats()
    print(f"  Cache hit rate: {cache_stats['hit_rate']:.2%}")


def main():
    """Run all performance optimization demonstrations."""
    print("=== Ariadne Performance Optimizations Demo ===")

    # Configure logging
    configure_logging(level="INFO")

    # Run demonstrations
    demo_async_operations()
    demo_circuit_optimization()
    demo_memory_management()
    demo_parallel_processing()
    demo_intelligent_caching()
    demo_performance_integration()

    print("\n=== Performance Optimizations Demo Complete ===")
    print("✓ Asynchronous operations for non-blocking execution")
    print("✓ Circuit optimization for reducing depth and gate count")
    print("✓ Memory management for efficient resource utilization")
    print("✓ Parallel processing for high-throughput simulation")
    print("✓ Intelligent caching for avoiding redundant computations")
    print("\nThese optimizations make Ariadne significantly faster and more efficient for production workloads.")

    # Clean up resources
    get_memory_manager().shutdown()
    get_parallel_simulator().shutdown()


if __name__ == "__main__":
    main()
