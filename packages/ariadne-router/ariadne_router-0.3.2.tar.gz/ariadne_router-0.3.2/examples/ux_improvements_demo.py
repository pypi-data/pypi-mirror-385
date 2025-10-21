#!/usr/bin/env python3
"""
Ariadne UX Improvements Demo

This example demonstrates all the UX improvements made to Ariadne:
1. Unified documentation structure
2. Simplified CLI commands
3. Active routing transparency
4. Integrated education tools
5. Performance context
"""

from ariadne import (
    demo_bell_state,
    demo_ghz_state,
    demo_qft,
    explore_algorithm_step_by_step,
    get_algorithms_by_category,
    list_algorithms,
    # Core functionality
    run_educational_simulation,
)


def demonstrate_ux_improvements():
    """Demonstrate all UX improvements implemented in Ariadne."""
    print("=" * 70)
    print("ARIADNE UX IMPROVEMENTS DEMONSTRATION")
    print("=" * 70)

    print("\n1. UNIFIED EDUCATIONAL WORKFLOWS")
    print("-" * 40)

    # Show available algorithms
    print(f"Available quantum algorithms: {len(list_algorithms())} total")
    foundational = get_algorithms_by_category('foundational')
    search = get_algorithms_by_category('search')
    print(f"  Foundational: {foundational}")
    print(f"  Search: {search}")

    # Run educational demos with single functions
    print("\nRunning Bell State demo...")
    result = demo_bell_state(shots=1000, verbose=True)
    print(f"  -> Backend used: {result.backend_used.value}")
    print(f"  -> Execution time: {result.execution_time:.4f}s")
    print(f"  -> Routing explanation: {result.routing_explanation}")

    print("\nRunning GHZ State demo...")
    result = demo_ghz_state(n_qubits=4, shots=1000, verbose=False)
    print(f"  -> Backend used: {result.backend_used.value}")
    print(f"  -> Results: {dict(list(result.counts.items())[:3])}")

    print("\n2. ACTIVE ROUTING TRANSPARENCY")
    print("-" * 40)

    # Show routing explanation is now automatically included in results
    bell_result = demo_bell_state(1000)
    print(f"Bell state routing explanation: {bell_result.routing_explanation}")

    # Compare different algorithms
    algorithms_to_try = ['bell', 'ghz', 'qft']
    for alg_name in algorithms_to_try:
        try:
            result, _ = run_educational_simulation(alg_name, n_qubits=3 if alg_name != 'bell' else 2, verbose=False)
            print(f"{alg_name.upper()}: {result.backend_used.value} -> {result.routing_explanation[:60]}...")
        except Exception as e:
            print(f"{alg_name.upper()}: Error - {e}")

    print("\n3. EDUCATIONAL STEP-BY-STEP EXPLORATION")
    print("-" * 40)

    # Explore an algorithm in detail
    explore_algorithm_step_by_step('qft', n_qubits=3)

    print("\n4. SIMPLIFIED EDUCATIONAL WORKFLOWS")
    print("-" * 40)

    # Show how educational content is integrated
    print("Running educational simulation with automatic content retrieval...")
    result, edu_content = run_educational_simulation('grover', n_qubits=4, shots=100, verbose=True)

    print("\n5. PERFORMANCE ANALYSIS")
    print("-" * 30)
    print(f"Grover's algorithm execution time: {result.execution_time:.4f}s")
    print(f"Backend used: {result.backend_used.value}")
    print(f"Routing confidence reflected in explanation: {result.routing_explanation}")

    print("\n6. INTEGRATION EXAMPLES")
    print("-" * 25)

    # Example of how these features work together
    print("Combining education, simulation, and transparency:")
    circuit_result = demo_qft(n_qubits=3, shots=100, verbose=False)
    print("  - QFT circuit simulated")
    print(f"  - Backend: {circuit_result.backend_used.value}")
    print(f"  - Execution time: {circuit_result.execution_time:.4f}s")
    print(f"  - Routing explanation: {circuit_result.routing_explanation}")

    print("\n" + "=" * 70)
    print("UX IMPROVEMENTS SUMMARY")
    print("=" * 70)
    print("✓ Documentation: Unified structure with persona-based guides")
    print("✓ CLI: Simplified from 7 to 4 main commands (run, explain, benchmark, learn)")
    print("✓ Routing: Active transparency - explanations in every result")
    print("✓ Education: Integrated in primary workflows, not isolated")
    print("✓ Performance: Context included in all results")
    print("✓ Backward Compatibility: All original features preserved")
    print("=" * 70)

    print("\nTry these commands in your own code:")
    print("  - demo_bell_state(shots=1000)  # Quick educational demo")
    print("  - run_educational_simulation('qft', n_qubits=3)  # Educational + simulation")
    print("  - explore_algorithm_step_by_step('grover', n_qubits=4)  # Full exploration")
    print("  - result.routing_explanation  # Always available in results")


if __name__ == "__main__":
    demonstrate_ux_improvements()
