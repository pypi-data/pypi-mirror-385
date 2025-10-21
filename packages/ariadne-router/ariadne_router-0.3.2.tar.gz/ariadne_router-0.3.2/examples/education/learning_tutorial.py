"""
Ariadne Quantum Algorithm Learning Tutorial

This notebook demonstrates how to use Ariadne's educational tools to learn quantum algorithms.
"""

# Import required modules
from ariadne.education import AlgorithmExplorer, EducationDashboard, InteractiveCircuitBuilder, explore_quantum_concept
from ariadne.enhanced_benchmarking import EnhancedBenchmarkSuite

print("=" * 60)
print("ARIADNE QUANTUM ALGORITHM LEARNING TUTORIAL")
print("=" * 60)

print("\n1. BASIC CIRCUIT CONSTRUCTION")
print("-" * 30)

# Create an interactive circuit builder for a Bell state
builder = InteractiveCircuitBuilder(2, "Bell State")
builder.add_hadamard(0, "Hadamard Gate", "Creates superposition: |0⟩ → (|0⟩ + |1⟩)/√2")
builder.add_cnot(0, 1, "CNOT Gate", "Creates entanglement: (|00⟩ + |11⟩)/√2")
builder.add_measurement(0, 0, "Measurement", "Measure first qubit")
builder.add_measurement(1, 1, "Measurement", "Measure second qubit")

print("Bell State Circuit:")
print(builder.get_circuit().draw())

print("\n2. QUANTUM CONCEPT EXPLORATION")
print("-" * 35)

# Explore quantum concepts
superposition_builder = explore_quantum_concept('superposition')
print("Superposition Circuit:")
print(superposition_builder.get_circuit().draw())

entanglement_builder = explore_quantum_concept('entanglement')
print("\nEntanglement Circuit:")
print(entanglement_builder.get_circuit().draw())

print("\n3. ALGORITHM EXPLORATION")
print("-" * 25)

# Use AlgorithmExplorer to learn about algorithms
explorer = AlgorithmExplorer()
available_algorithms = explorer.list_algorithms()
print(f"Available algorithms: {available_algorithms[:10]}...")  # Show first 10

# Explore a specific algorithm
if 'bell' in available_algorithms:
    print("\nLearning about the Bell algorithm:")
    info = explorer.get_algorithm_info('bell')
    print(f"Description: {info['metadata'].description}")
    print(f"Complexity: {info['metadata'].complexity}")

    # Create learning path
    learning_path = explorer.create_learning_path('bell', n_qubits=2)
    print(f"Created learning path with {len(learning_path)} steps")

print("\n4. EDUCATION DASHBOARD")
print("-" * 22)

# Create dashboard
dashboard = EducationDashboard()
print("Dashboard initialized with algorithm and concept explorers")

print("\n5. PRACTICAL EXAMPLE: Comparing Algorithms")
print("-" * 43)

# Compare two algorithms
if 'bell' in available_algorithms and 'ghz' in available_algorithms:
    try:
        dashboard.compare_algorithms_interactive(['bell', 'ghz'])
        print("Comparison completed")
    except:
        print("Comparison display failed (likely non-IPython environment)")

print("\n6. BENCHMARKING TOOLS")
print("-" * 24)

# Use benchmarking tools
suite = EnhancedBenchmarkSuite()

# Test a simple algorithm
results = suite.benchmark_single_algorithm(
    algorithm_name='bell',
    qubit_count=2,
    shots=100
)

if results and results[0].success:
    print(f"Bell state simulation: {results[0].execution_time:.4f}s")
else:
    print(f"Bell state simulation failed: {results[0].error_message if results else 'No result'}")

print("\n7. INTERACTIVE CIRCUIT WALKTHROUGH")
print("-" * 37)

# Step-by-step walkthrough
for _i, step in enumerate(builder.history):
    print(f"\nStep {step.step_number}: {step.title}")
    print(f"Description: {step.description}")
    print("Circuit at this step:")
    circuit_at_step = step.circuit
    print(circuit_at_step.draw())

print("\n8. LEARNING PATH COMPLETION")
print("-" * 27)

print("You have completed the Ariadne learning tutorial!")
print("Key concepts covered:")
print("- Interactive circuit building")
print("- Quantum concepts (superposition, entanglement)")
print("- Algorithm exploration")
print("- Performance benchmarking")
print("- Educational tools integration")

print("\nNext steps:")
print("- Try creating your own algorithms using InteractiveCircuitBuilder")
print("- Explore more quantum algorithms with AlgorithmExplorer")
print("- Use enhanced benchmarking tools to compare performance")
print("- Build custom learning paths for different concepts")

print("\n" + "=" * 60)
print("TUTORIAL COMPLETE")
print("=" * 60)
