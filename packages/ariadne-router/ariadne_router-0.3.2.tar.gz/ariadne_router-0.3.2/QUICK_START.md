# Ariadne Quick Start Guide

Get up and running with Ariadne in minutes!

## Installation

Install Ariadne using pip:

```bash
pip install ariadne-router
```

For hardware acceleration on Apple Silicon:
```bash
pip install ariadne-router[apple]
```

## Your First Simulation

Start with a simple Bell state simulation:

```python
from ariadne import simulate
from qiskit import QuantumCircuit

# Create a Bell state circuit
qc = QuantumCircuit(2, 2)
qc.h(0)           # Hadamard gate on qubit 0
qc.cx(0, 1)       # CNOT gate from qubit 0 to 1
qc.measure_all()  # Measure all qubits

# Simulate the circuit - Ariadne chooses the optimal backend
result = simulate(qc, shots=1000)

print(f"Backend used: {result.backend_used}")
print(f"Execution time: {result.execution_time:.4f}s")
print(f"Measurement results: {dict(list(result.counts.items())[:5])}")
```

## Understanding the Routing

See why Ariadne chose a specific backend:

```python
from ariadne import explain_routing

explanation = explain_routing(qc)
print(explanation)
```

## Educational Exploration

Try out the educational tools:

```python
from ariadne.education import InteractiveCircuitBuilder

# Build a circuit step-by-step with explanations
builder = InteractiveCircuitBuilder(2, "Bell State")
builder.add_hadamard(0, "Create Superposition",
                    "Apply H gate to qubit 0 to create |+⟩ state")
builder.add_cnot(0, 1, "Create Entanglement",
                "Apply CNOT to entangle qubits 0 and 1")

print("Your circuit:")
print(builder.get_circuit().draw())

# Simulate your circuit
from ariadne import simulate
result = simulate(builder.get_circuit(), shots=1000)
print(f"Simulation completed in {result.execution_time:.4f}s")
```

## Algorithm Exploration

Explore quantum algorithms:

```python
from ariadne.education import AlgorithmExplorer

explorer = AlgorithmExplorer()
print("Available algorithms:", explorer.list_algorithms()[:5])  # First 5

# Learn about a specific algorithm
info = explorer.get_algorithm_info('bell')
print(f"Bell algorithm: {info['metadata'].description}")
```

## Performance Comparison

Compare different backends:

```python
from ariadne.enhanced_benchmarking import EnhancedBenchmarkSuite

suite = EnhancedBenchmarkSuite()

# Compare performance across backends
comparison = suite.benchmark_backend_comparison(
    algorithm_name='bell',
    qubit_count=2,
    backends=['auto', 'qiskit'],
    shots=1000
)

for backend, result in comparison.items():
    if result.success:
        print(f"{backend}: {result.execution_time:.4f}s, {result.throughput:.2f} shots/s")
```

## CLI Quick Start

Ariadne also provides a powerful command-line interface:

```bash
# Simulate a circuit
ariadne simulate my_circuit.qasm --shots 1000

# Check system status
ariadne status

# Run educational demos
ariadne education demo bell --qubits 2

# Run benchmarks
ariadne benchmark-suite --algorithms bell,ghz --shots 100

# Get help
ariadne --help
ariadne education --help
```

## Next Steps

1. **Explore algorithms**: Check out `ariadne.education.AlgorithmExplorer` for 15+ quantum algorithms
2. **Try different circuits**: Experiment with GHZ states, QFT, Grover's algorithm
3. **Benchmark performance**: Use `ariadne.enhanced_benchmarking` to compare backends
4. **Create custom circuits**: Use `InteractiveCircuitBuilder` to build step-by-step
5. **Visualize results**: Generate performance reports with `generate_performance_report()`

## Troubleshooting

- **For large Clifford circuits**: Ariadne automatically uses Stim for optimal performance
- **For hardware acceleration**: Make sure you have the right extras installed (`[apple]` or `[cuda]`)
- **For algorithm details**: Use `explain_routing()` to understand backend selection
- **For performance issues**: Try using specialized backends instead of auto-routing

Ready for more? Check out the comprehensive user guide in `USER_GUIDE.md`!
