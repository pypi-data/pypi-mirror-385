#!/usr/bin/env python3
"""
Ariadne Production-Ready Example

This example demonstrates the new production-ready features of Ariadne,
including improved error handling, resource management, and logging.
"""

from qiskit import QuantumCircuit

from ariadne import (
    BackendUnavailableError,
    CircuitTooLargeError,
    ResourceExhaustionError,
    configure_logging,
    get_logger,
    get_resource_manager,
    simulate,
)


def main():
    print("=== Ariadne Production-Ready Example ===\n")

    # Configure logging for better visibility
    configure_logging(level="INFO")
    logger = get_logger("example")

    # Example 1: Basic simulation with logging
    print("1. Basic Bell State Simulation with Enhanced Logging")
    bell = QuantumCircuit(2, 2)
    bell.h(0)
    bell.cx(0, 1)
    bell.measure_all()

    result = simulate(bell, shots=1000)
    logger.info(f"Simulation completed using {result.backend_used.value} backend")
    logger.info(f"Execution time: {result.execution_time:.4f}s")
    logger.info(f"Results: {dict(list(result.counts.items())[:3])}")
    print()

    # Example 2: Resource management
    print("2. Resource Management")
    resource_manager = get_resource_manager()
    resources = resource_manager.get_resources()

    logger.info("System resources:")
    logger.info(f"  Available memory: {resources.available_memory_mb:.1f} MB")
    logger.info(f"  Available CPU cores: {resources.available_cpu_cores}")
    logger.info(f"  GPU available: {resources.gpu_available}")

    # Check circuit feasibility
    can_handle, reason = resource_manager.can_handle_circuit(bell, "qiskit")
    logger.info(f"Bell state feasible with Qiskit: {can_handle} ({reason})")
    print()

    # Example 3: Error handling
    print("3. Enhanced Error Handling")

    # Try to force an unavailable backend
    try:
        result = simulate(bell, backend="unavailable_backend")
    except ValueError as e:
        logger.info(f"Caught expected error: {e}")

    # Try a circuit that's too large for a specific backend
    large_circuit = QuantumCircuit(30)
    for i in range(30):
        large_circuit.h(i)
        if i < 29:
            large_circuit.cx(i, i + 1)

    try:
        result = simulate(large_circuit, backend="stim")  # Stim might not handle this
        logger.info(f"Large circuit simulated with {result.backend_used.value}")
    except (BackendUnavailableError, ResourceExhaustionError, CircuitTooLargeError) as e:
        logger.info(f"Caught expected error for large circuit: {e}")
    print()

    # Example 4: Performance recommendations
    print("4. Performance Recommendations")
    recommendations = resource_manager.get_recommendations(large_circuit)
    for rec in recommendations:
        logger.info(f"  Recommendation: {rec}")
    print()

    # Example 5: Clifford circuit optimization
    print("5. Clifford Circuit Optimization")
    clifford = QuantumCircuit(20)
    clifford.h(0)
    for i in range(19):
        clifford.cx(i, i + 1)
    clifford.measure_all()

    result = simulate(clifford, shots=1000)
    logger.info(f"Clifford circuit simulated with {result.backend_used.value} backend")
    logger.info(f"Execution time: {result.execution_time:.4f}s")

    if result.backend_used.value == "stim":
        logger.info("✓ Clifford circuit automatically routed to Stim for optimal performance")
    print()

    print("=== Production-Ready Features Demonstrated ===")
    print("✓ Enhanced error handling with specific exception types")
    print("✓ Resource management and feasibility checking")
    print("✓ Structured logging with circuit context")
    print("✓ Automatic backend selection with fallback")
    print("✓ Performance recommendations")
    print("✓ Clifford circuit optimization")


if __name__ == "__main__":
    main()
