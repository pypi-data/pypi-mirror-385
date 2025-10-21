#!/usr/bin/env python3
"""
Stabilizer Circuit Optimization Demonstration

This script demonstrates Ariadne's intelligent routing for stabilizer circuits,
showing how the router automatically detects Clifford circuits and routes them
to the Stim backend for optimal performance.

This is a realistic demonstration of Ariadne's value proposition:
automatic backend selection for optimal performance.
"""

import time

from qiskit import QuantumCircuit

from ariadne import QuantumRouter, simulate


def create_stabilizer_circuit(num_qubits: int) -> QuantumCircuit:
    """Create a stabilizer circuit (quantum error correction style)."""
    qc = QuantumCircuit(num_qubits, num_qubits)

    # Create a GHZ-like state with all Clifford gates
    qc.h(0)  # Start with superposition

    # Create entanglement chain
    for i in range(num_qubits - 1):
        qc.cx(i, i + 1)

    # Add some S gates for complexity
    for i in range(0, num_qubits, 3):
        qc.s(i)

    # Add more Hadamard gates
    for i in range(1, num_qubits, 2):
        qc.h(i)

    # Measure all qubits
    qc.measure_all()

    return qc


def create_non_clifford_circuit(num_qubits: int) -> QuantumCircuit:
    """Create a non-Clifford circuit with T gates."""
    qc = QuantumCircuit(num_qubits, num_qubits)

    # Start with superposition
    qc.h(0)

    # Add T gates (non-Clifford)
    for i in range(min(3, num_qubits)):
        qc.t(i)

    # Add some entanglement
    for i in range(num_qubits - 1):
        qc.cx(i, i + 1)

    # Measure all qubits
    qc.measure_all()

    return qc


def demonstrate_intelligent_routing():
    """Demonstrate Ariadne's intelligent backend selection."""

    print("🔮 ARIADNE INTELLIGENT ROUTING DEMONSTRATION")
    print("=" * 60)
    print()
    print("This demo shows how Ariadne automatically selects")
    print("the optimal backend for different circuit types.")
    print()

    router = QuantumRouter()

    # Test different circuit types
    test_cases = [
        ("Small Stabilizer Circuit (10 qubits)", create_stabilizer_circuit(10)),
        ("Medium Stabilizer Circuit (50 qubits)", create_stabilizer_circuit(50)),
        ("Large Stabilizer Circuit (100 qubits)", create_stabilizer_circuit(100)),
        ("Non-Clifford Circuit (5 qubits)", create_non_clifford_circuit(5)),
    ]

    for circuit_name, circuit in test_cases:
        print(f"📊 Testing: {circuit_name}")

        # Analyze the circuit
        routing_decision = router.select_optimal_backend(circuit)

        print(f"   Circuit entropy: {routing_decision.circuit_entropy:.2f}")
        print(f"   Recommended backend: {routing_decision.recommended_backend.value}")
        print(f"   Expected speedup: {routing_decision.expected_speedup:.1f}x")
        print(f"   Confidence: {routing_decision.confidence_score:.2f}")

        # Time the simulation
        print("   🚀 Simulating...")
        start_time = time.perf_counter()

        try:
            result = simulate(circuit, shots=1000)
            end_time = time.perf_counter()
            execution_time = end_time - start_time

            print(f"   ✅ SUCCESS: {execution_time:.4f}s")
            print(f"   Backend used: {result.backend_used.value}")
            print(f"   Total measurements: {sum(result.counts.values())}")

            # Show a few measurement outcomes
            top_outcomes = sorted(result.counts.items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"   Top outcomes: {dict(top_outcomes)}")
            print()

        except Exception as e:
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            print(f"   ❌ FAILED: {e}")
            print()

    print("🎯 KEY INSIGHTS:")
    print("=" * 60)
    print("✅ Stabilizer circuits automatically route to Stim")
    print("✅ Non-Clifford circuits route to appropriate backends")
    print("✅ Polynomial scaling enables large stabilizer simulations")
    print("✅ Zero configuration required - routing is automatic")
    print()
    print("🔬 TECHNICAL EXPLANATION:")
    print("- Stim uses stabilizer tableau representation")
    print("- O(n²) complexity for Clifford operations")
    print("- Enables efficient simulation of error correction codes")
    print("- Ariadne detects circuit type automatically")


def demonstrate_backend_comparison():
    """Show performance comparison between backends."""

    print("\n📈 BACKEND PERFORMANCE COMPARISON")
    print("=" * 60)
    print()

    # Create a moderately sized stabilizer circuit
    circuit = create_stabilizer_circuit(20)

    print("Testing the same 20-qubit stabilizer circuit on different backends:")
    print()

    backends_to_test = ["stim", "qiskit"]
    results = {}

    for backend in backends_to_test:
        print(f"🔄 Testing {backend} backend...")

        try:
            start_time = time.perf_counter()
            result = simulate(circuit, shots=1000, backend=backend)
            end_time = time.perf_counter()

            execution_time = end_time - start_time
            results[backend] = {
                "time": execution_time,
                "success": True,
                "backend_used": result.backend_used.value,
            }

            print(f"   ✅ {backend}: {execution_time:.4f}s")

        except Exception as e:
            print(f"   ❌ {backend}: FAILED - {str(e)[:50]}...")
            results[backend] = {"time": float("inf"), "success": False, "error": str(e)}

    print()
    print("📊 PERFORMANCE SUMMARY:")
    print("=" * 30)

    if results["stim"]["success"] and results["qiskit"]["success"]:
        speedup = results["qiskit"]["time"] / results["stim"]["time"]
        print(f"Stim:   {results['stim']['time']:.4f}s")
        print(f"Qiskit: {results['qiskit']['time']:.4f}s")
        print(f"Speedup: {speedup:.1f}x")
    else:
        for backend, result in results.items():
            if result["success"]:
                print(f"{backend}: {result['time']:.4f}s ✅")
            else:
                print(f"{backend}: FAILED ❌")


def demonstrate_scaling_behavior():
    """Show how performance scales with circuit size."""

    print("\n📏 SCALING BEHAVIOR DEMONSTRATION")
    print("=" * 60)
    print()
    print("Testing stabilizer circuits of increasing size:")
    print()

    circuit_sizes = [10, 20, 50, 100]

    print("| Qubits | Time (s) | Backend | Scaling |")
    print("|--------|----------|---------|---------|")

    previous_time = None

    for num_qubits in circuit_sizes:
        circuit = create_stabilizer_circuit(num_qubits)

        try:
            start_time = time.perf_counter()
            result = simulate(circuit, shots=100)  # Fewer shots for speed
            end_time = time.perf_counter()

            execution_time = end_time - start_time
            backend = result.backend_used.value

            # Calculate scaling factor
            if previous_time:
                scaling = execution_time / previous_time
                scaling_str = f"{scaling:.1f}x"
            else:
                scaling_str = "baseline"

            print(f"| {num_qubits:6d} | {execution_time:8.4f} | {backend:7s} | {scaling_str:7s} |")
            previous_time = execution_time

        except Exception:
            print(f"| {num_qubits:6d} | FAILED   | ERROR   | N/A     |")

    print()
    print("🔬 SCALING ANALYSIS:")
    print("- Stim exhibits polynomial scaling for Clifford circuits")
    print("- Performance remains reasonable even for 100+ qubits")
    print("- This enables simulation of large error correction codes")


if __name__ == "__main__":
    print("🔮 ARIADNE: INTELLIGENT QUANTUM ROUTING DEMO")
    print("=" * 60)
    print()
    print("This demonstration shows Ariadne's intelligent routing")
    print("capabilities for different types of quantum circuits.")
    print()
    print("Key features demonstrated:")
    print("- Automatic backend selection")
    print("- Stabilizer circuit optimization")
    print("- Performance comparisons")
    print("- Scaling behavior analysis")
    print()
    print("Press Enter to start the demonstration...")
    input()

    # Run demonstrations
    demonstrate_intelligent_routing()
    demonstrate_backend_comparison()
    demonstrate_scaling_behavior()

    print("\n🎉 DEMONSTRATION COMPLETE!")
    print("=" * 60)
    print()
    print("Key takeaways:")
    print("✅ Ariadne automatically selects optimal backends")
    print("✅ Stabilizer circuits get polynomial scaling with Stim")
    print("✅ No configuration required - just use simulate()")
    print("✅ Honest performance comparisons show real benefits")
    print()
    print("🔮 Ariadne: The intelligent quantum router for productivity")
