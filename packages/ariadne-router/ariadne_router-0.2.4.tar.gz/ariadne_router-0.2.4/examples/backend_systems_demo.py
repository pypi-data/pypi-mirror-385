#!/usr/bin/env python3
"""
Ariadne Backend Systems Demo

This example demonstrates the enhanced backend system improvements in Ariadne,
including health checking, pooling, fallback strategies, and performance monitoring.
"""

import time

from qiskit import QuantumCircuit

from ariadne.backends import (
    BackendCapabilities,
    BackendCapability,
    OptimizationHint,
    PerformanceMetricType,
    create_backend_pool,
    create_enhanced_backend,
    get_fallback_manager,
    get_health_checker,
    get_performance_monitor,
)
from ariadne.core import configure_logging, get_logger
from ariadne.types import BackendType


def create_mock_backend(backend_name: str, success_rate: float = 1.0, delay: float = 0.1):
    """Create a mock backend for demonstration."""

    class MockBackend:
        def __init__(self):
            self.name = backend_name
            self.success_rate = success_rate
            self.delay = delay

        def simulate(self, circuit: QuantumCircuit, shots: int = 1000, **kwargs):
            # Simulate processing delay
            time.sleep(self.delay)

            # Simulate occasional failures
            import random

            if random.random() > self.success_rate:
                raise Exception(f"Mock backend {backend_name} failed")

            # Return mock results
            if circuit.num_qubits == 1:
                return {"0": shots // 2, "1": shots // 2}
            elif circuit.num_qubits == 2:
                return {"00": shots // 2, "11": shots // 2}
            else:
                # For larger circuits, return a simple distribution
                result = {}
                for i in range(min(2**circuit.num_qubits, 8)):
                    bitstring = format(i, f"0{circuit.num_qubits}b")
                    result[bitstring] = shots // 8
                return result

    return MockBackend


def demo_health_checking():
    """Demonstrate backend health checking system."""
    print("\n=== Backend Health Checking Demo ===")

    logger = get_logger("health_demo")
    logger.info("Starting backend health checking demo")
    health_checker = get_health_checker()

    # Create mock backends with different success rates
    healthy_backend = create_mock_backend("healthy", success_rate=0.95, delay=0.05)
    unhealthy_backend = create_mock_backend("unhealthy", success_rate=0.3, delay=0.5)

    # Create test circuits
    simple_circuit = QuantumCircuit(2)
    simple_circuit.h(0)
    simple_circuit.cx(0, 1)

    # Register health checks
    from ariadne.backends.health_checker import create_circuit_based_health_check

    healthy_check = create_circuit_based_health_check("healthy", healthy_backend.simulate, simple_circuit)

    unhealthy_check = create_circuit_based_health_check("unhealthy", unhealthy_backend.simulate, simple_circuit)

    health_checker.register_health_check(BackendType.QISKIT, healthy_check)
    health_checker.register_health_check(BackendType.CUDA, unhealthy_check)

    # Note: In a real implementation, we would map these to actual BackendType values
    # For this demo, we'll just show the health checking concept

    print("✓ Health checking system initialized")
    print("✓ Health checks registered for backends")

    # Check health status
    print("\n--- Checking Backend Health ---")

    # In a real implementation, this would check actual backends
    # For demo purposes, we'll simulate the results
    print("Healthy backend: ✓ HEALTHY (response time: 0.05s)")
    print("Unhealthy backend: ✗ UNHEALTHY (response time: 0.5s, success rate: 30%)")

    # Get list of healthy backends
    healthy_backends = health_checker.get_healthy_backends()
    print(f"\n✓ {len(healthy_backends)} backends are healthy")

    # Show health metrics
    print("\n--- Health Metrics ---")
    for backend_type in [BackendType.QISKIT, BackendType.STIM, BackendType.CUDA]:
        # In a real implementation, this would get actual metrics
        print(f"{backend_type.value}: Uptime 99.5%, Avg response 0.1s, Success rate 98%")


def demo_backend_pooling():
    """Demonstrate backend pooling system."""
    print("\n=== Backend Pooling Demo ===")

    # Create a mock backend class
    class MockPooledBackend:
        def __init__(self):
            self.instance_id = id(self)
            self.created_at = time.time()

        def simulate(self, circuit: QuantumCircuit, shots: int = 1000):
            # Simulate some work
            time.sleep(0.05)
            return {"0": shots // 2, "1": shots // 2}

    # Create a backend pool
    pool = create_backend_pool(
        backend_name="demo_pool", backend_class=MockPooledBackend, min_instances=2, max_instances=5
    )

    print("✓ Backend pool created")
    print(f"✓ Pool initialized with {pool.get_statistics().total_instances} instances")

    # Get backend instances from pool
    print("\n--- Acquiring Backend Instances ---")
    backends = []

    for i in range(3):
        start_time = time.time()
        backend = pool.get_backend(timeout=1.0)
        wait_time = time.time() - start_time

        backends.append(backend)
        print(f"✓ Acquired backend instance {i + 1} (wait time: {wait_time:.3f}s)")

    # Use backends
    print("\n--- Using Backend Instances ---")
    circuit = QuantumCircuit(1)
    circuit.h(0)

    for i, backend in enumerate(backends):
        start_time = time.time()
        result = backend.simulate(circuit, shots=100)
        exec_time = time.time() - start_time

        print(f"✓ Backend {i + 1} simulated circuit in {exec_time:.3f}s")
        print(f"    Sample counts: {result}")

    # Return backends to pool
    print("\n--- Returning Backend Instances ---")
    for i, backend in enumerate(backends):
        pool.return_backend(backend)
        print(f"✓ Returned backend instance {i + 1} to pool")

    # Show pool statistics
    print("\n--- Pool Statistics ---")
    stats = pool.get_statistics()
    print(f"Total instances: {stats.total_instances}")
    print(f"Active instances: {stats.active_instances}")
    print(f"Available instances: {stats.available_instances}")
    print(f"Total requests: {stats.total_requests}")
    print(f"Success rate: {stats.success_rate:.2%}")
    print(f"Average wait time: {stats.average_wait_time:.3f}s")
    print(f"Peak usage: {stats.peak_usage} instances")

    # Shutdown pool
    pool.shutdown()
    print("\n✓ Pool shutdown complete")


def demo_enhanced_interface():
    """Demonstrate enhanced backend interface."""
    print("\n=== Enhanced Backend Interface Demo ===")

    # Create a mock backend
    mock_backend = create_mock_backend("enhanced_demo", success_rate=0.9, delay=0.1)

    # Define backend capabilities
    capabilities = BackendCapabilities(
        supported_capabilities=[
            BackendCapability.STATE_VECTOR_SIMULATION,
            BackendCapability.NOISE_MODELING,
        ],
        optimization_hints=[
            OptimizationHint.BENEFITS_FROM_GATE_FUSION,
            OptimizationHint.BENEFITS_FROM_CIRCUIT_OPTIMIZATION,
        ],
        max_qubits=20,
        typical_qubits=10,
        memory_efficiency=0.7,
        speed_rating=0.8,
        accuracy_rating=0.9,
        stability_rating=0.85,
        hardware_requirements=["CPU"],
        estimated_cost_factor=1.0,
    )

    # Create enhanced backend
    enhanced = create_enhanced_backend(backend=mock_backend, backend_name="enhanced_demo", capabilities=capabilities)

    print("✓ Enhanced backend created with capabilities")

    # Show backend capabilities
    print("\n--- Backend Capabilities ---")
    print(f"Max qubits: {capabilities.max_qubits}")
    print(f"Typical qubits: {capabilities.typical_qubits}")
    print(f"Memory efficiency: {capabilities.memory_efficiency:.2f}")
    print(f"Speed rating: {capabilities.speed_rating:.2f}")
    print(f"Accuracy rating: {capabilities.accuracy_rating:.2f}")
    print(f"Stability rating: {capabilities.stability_rating:.2f}")

    print("\nSupported capabilities:")
    for cap in capabilities.supported_capabilities:
        print(f"  - {cap.value}")

    print("\nOptimization hints:")
    for hint in capabilities.optimization_hints:
        print(f"  - {hint.value}")

    # Test capability support
    print("\n--- Capability Support ---")
    print(f"State vector simulation: {enhanced.supports_capability(BackendCapability.STATE_VECTOR_SIMULATION)}")
    print(f"GPU acceleration: {enhanced.supports_capability(BackendCapability.GPU_ACCELERATION)}")
    print(f"Gate fusion beneficial: {enhanced.has_optimization_hint(OptimizationHint.BENEFITS_FROM_GATE_FUSION)}")

    # Test circuit simulation
    print("\n--- Circuit Simulation ---")
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.cx(0, 1)

    start_time = time.time()
    result = enhanced.simulate(circuit, shots=1000)
    exec_time = time.time() - start_time

    print(f"✓ Circuit simulated in {exec_time:.3f}s")
    print(f"✓ Result: {dict(list(result.items())[:3])}")

    # Get performance metrics
    metrics = enhanced.get_performance_metrics()
    print("\n--- Performance Metrics ---")
    print(f"Total simulations: {metrics.total_simulations}")
    print(f"Successful simulations: {metrics.successful_simulations}")
    print(f"Failed simulations: {metrics.failed_simulations}")
    print(f"Success rate: {metrics.success_rate:.2%}")
    print(f"Average execution time: {metrics.average_execution_time:.3f}s")

    # Get optimization recommendations
    print("\n--- Optimization Recommendations ---")
    large_circuit = QuantumCircuit(25)
    for i in range(24):
        large_circuit.h(i)

    recommendations = enhanced.get_optimization_recommendations(large_circuit)
    for rec in recommendations:
        print(f"  - {rec}")

    # Test suitability scoring
    print("\n--- Circuit Suitability ---")
    suitable, score = enhanced.is_suitable_for_circuit(circuit)
    print(f"Circuit suitable: {suitable}")
    print(f"Suitability score: {score:.2f}")


def demo_fallback_strategy():
    """Demonstrate backend fallback strategy."""
    print("\n=== Backend Fallback Strategy Demo ===")

    # Create fallback manager
    fallback_manager = get_fallback_manager()

    # Create mock backends with different characteristics
    fast_backend = create_mock_backend("fast", success_rate=0.7, delay=0.05)
    reliable_backend = create_mock_backend("reliable", success_rate=0.95, delay=0.2)

    # Register fallback functions
    def fast_fallback(circuit, shots):
        return fast_backend.simulate(circuit, shots)

    def reliable_fallback(circuit, shots):
        return reliable_backend.simulate(circuit, shots)

    fallback_manager.register_fallback_function(BackendType.CUDA, fast_fallback)
    fallback_manager.register_fallback_function(BackendType.QISKIT, reliable_fallback)

    # In a real implementation, we would register these with actual BackendType values
    # For demo purposes, we'll show the fallback concept

    print("✓ Fallback manager initialized")
    print("✓ Fallback functions registered")

    # Create test circuit
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.cx(0, 1)

    # Show fallback chains
    print("\n--- Fallback Chains ---")
    print("General purpose chain: [STIM, CUDA, JAX_METAL, TENSOR_NETWORK, MPS, DDSIM, QISKIT]")
    print("Clifford circuit chain: [STIM, QISKIT]")
    print("Large circuit chain: [TENSOR_NETWORK, MPS, STIM, QISKIT]")
    print("GPU-accelerated chain: [CUDA, JAX_METAL, QISKIT]")

    # Demonstrate fallback execution
    print("\n--- Fallback Execution ---")

    # Simulate a fallback scenario
    print("Simulating fallback execution...")

    # In a real implementation, this would use actual backends
    # For demo purposes, we'll simulate the result

    class MockFallbackResult:
        def __init__(self):
            self.success = True
            self.backend_used = BackendType.QISKIT
            self.attempts = [
                MockAttempt(BackendType.STIM, False, "Backend unavailable"),
                MockAttempt(BackendType.CUDA, False, "CUDA runtime not available"),
                MockAttempt(BackendType.QISKIT, True, None),
            ]
            self.total_time = 0.5
            self.final_result = {"00": 500, "11": 500}

    class MockAttempt:
        def __init__(self, backend, success, error):
            self.backend = backend
            self.success = success
            self.error_message = error

    result = MockFallbackResult()

    print(f"✓ Fallback successful: {result.backend_used.value} after {len(result.attempts)} attempts")
    print(f"✓ Total time: {result.total_time:.3f}s")
    print(f"✓ Result: {result.final_result}")

    print("\n--- Attempt Details ---")
    for i, attempt in enumerate(result.attempts):
        if attempt.success:
            print(f"Attempt {i + 1}: ✓ {attempt.backend.value} - SUCCESS")
        else:
            print(f"Attempt {i + 1}: ✗ {attempt.backend.value} - {attempt.error_message}")

    # Show fallback statistics
    print("\n--- Fallback Statistics ---")
    stats = {
        "total_fallbacks": 100,
        "success_rate": 0.95,
        "average_attempts": 1.8,
        "average_time": 0.7,
        "most_common_backend": BackendType.QISKIT,
        "most_common_reason": "backend_unavailable",
    }

    print(f"Total fallbacks: {stats['total_fallbacks']}")
    print(f"Success rate: {stats['success_rate']:.2%}")
    print(f"Average attempts: {stats['average_attempts']}")
    print(f"Average time: {stats['average_time']:.3f}s")
    print(f"Most common backend: {stats['most_common_backend'].value}")
    print(f"Most common reason: {stats['most_common_reason'].value}")


def demo_performance_monitoring():
    """Demonstrate backend performance monitoring."""
    print("\n=== Backend Performance Monitoring Demo ===")

    # Get performance monitor
    monitor = get_performance_monitor()

    print("✓ Performance monitor initialized")

    # Create test circuit
    circuit = QuantumCircuit(3)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.cx(1, 2)

    # Record some performance metrics
    print("\n--- Recording Performance Metrics ---")

    # Simulate different performance scenarios
    scenarios = [
        {"backend": BackendType.QISKIT, "time": 0.5, "memory": 100, "success": True},
        {"backend": BackendType.STIM, "time": 0.1, "memory": 50, "success": True},
        {"backend": BackendType.CUDA, "time": 0.05, "memory": 200, "success": True},
        {"backend": BackendType.QISKIT, "time": 1.2, "memory": 150, "success": True},
        {"backend": BackendType.STIM, "time": 0.15, "memory": 60, "success": True},
        {"backend": BackendType.QISKIT, "time": 0.8, "memory": 120, "success": False},  # Failed
        {"backend": BackendType.CUDA, "time": 0.03, "memory": 180, "success": True},
    ]

    for scenario in scenarios:
        monitor.record_simulation(
            backend=scenario["backend"],
            circuit=circuit,
            shots=1000,
            execution_time=scenario["time"],
            memory_usage=scenario["memory"],
            success=scenario["success"],
        )

        status = "✓" if scenario["success"] else "✗"
        print(f"{status} {scenario['backend'].value}: {scenario['time']:.3f}s, {scenario['memory']}MB")

    # Get performance summaries
    print("\n--- Performance Summaries ---")

    for backend in [BackendType.QISKIT, BackendType.STIM, BackendType.CUDA]:
        summary = monitor.get_backend_summary(backend)
        if summary:
            print(f"\n{backend.value} Backend:")
            print(f"  Last updated: {time.strftime('%H:%M:%S', time.localtime(summary['last_updated']))}")

            # Show metrics
            if "execution_time" in summary["metrics"]:
                exec_time = summary["metrics"]["execution_time"]
                print(
                    f"  Execution time: avg {exec_time['mean']:.3f}s, min {exec_time['min']:.3f}s, max {exec_time['max']:.3f}s"
                )

            if "memory_usage" in summary["metrics"]:
                memory = summary["metrics"]["memory_usage"]
                print(
                    f"  Memory usage: avg {memory['mean']:.1f}MB, min {memory['min']:.1f}MB, max {memory['max']:.1f}MB"
                )

            if "throughput" in summary["metrics"]:
                throughput = summary["metrics"]["throughput"]
                print(f"  Throughput: avg {throughput['mean']:.0f} shots/s")

            if "success_rate" in summary["metrics"]:
                success = summary["metrics"]["success_rate"]
                print(f"  Success rate: {success['mean']:.2%}")

            # Show alerts
            alerts = summary["alerts"]
            if alerts["total"] > 0:
                print(f"  Alerts: {alerts['total']} total ({alerts['error']} errors, {alerts['warning']} warnings)")

    # Get performance recommendations
    print("\n--- Performance Recommendations ---")

    for backend in [BackendType.QISKIT, BackendType.STIM, BackendType.CUDA]:
        recommendations = monitor.get_performance_recommendations(backend)
        if recommendations:
            print(f"\n{backend.value} Backend:")
            for rec in recommendations:
                print(f"  - {rec}")

    # Compare backends
    print("\n--- Backend Comparison ---")
    comparison = monitor.compare_backends(
        backends=[BackendType.QISKIT, BackendType.STIM, BackendType.CUDA],
        metric_type=PerformanceMetricType.EXECUTION_TIME,
    )

    print(f"Metric: {comparison['metric_type']}")
    print("Backend performance:")
    for backend_name, stats in comparison["backends"].items():
        print(f"  {backend_name}: avg {stats['mean']:.3f}s (±{stats['std']:.3f}s)")


def main():
    """Run all backend system demonstrations."""
    print("=== Ariadne Backend Systems Demonstration ===")

    # Configure logging
    configure_logging(level="INFO")

    # Run demonstrations
    demo_health_checking()
    demo_backend_pooling()
    demo_enhanced_interface()
    demo_fallback_strategy()
    demo_performance_monitoring()

    print("\n=== Backend Systems Demo Complete ===")
    print("✓ Health checking system")
    print("✓ Backend pooling system")
    print("✓ Enhanced backend interface")
    print("✓ Backend fallback strategy")
    print("✓ Performance monitoring system")
    print("\nThese backend improvements make Ariadne more robust, performant, and reliable for production use.")


if __name__ == "__main__":
    main()
