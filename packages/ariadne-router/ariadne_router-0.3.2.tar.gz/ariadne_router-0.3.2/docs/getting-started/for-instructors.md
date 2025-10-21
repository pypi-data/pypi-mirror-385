# Getting Started for Classroom Instructors

This guide provides everything you need to start using Ariadne in your quantum computing courses. Ariadne simplifies quantum circuit simulation and provides educational tools that help students learn quantum algorithms.

## Installation

Ariadne installs with a single pip command that works across all platforms:

```bash
pip install ariadne-router
```

For Apple Silicon Macs, add hardware acceleration:
```bash
pip install ariadne-router[apple]
```

## Quick Classroom Demo

Start with a simple Bell state demonstration:

```python
from ariadne import simulate
from qiskit import QuantumCircuit

# Create a Bell state circuit (entangled pair)
qc = QuantumCircuit(2, 2)
qc.h(0)           # Hadamard on qubit 0
qc.cx(0, 1)       # CNOT gate
qc.measure_all()  # Measure both qubits

# Simulate with automatic backend selection
result = simulate(qc, shots=1000)

print(f"Backend used: {result.backend_used}")
print(f"Results: {dict(result.counts)}")
```

## Educational Algorithms

Ariadne includes 15+ quantum algorithms with educational content:

```python
from ariadne.algorithms import get_algorithm, list_algorithms

# List all available algorithms
print("Available algorithms:", list_algorithms())

# Create and run a Grover's algorithm example
Grover = get_algorithm("grover")
params = {"n_qubits": 4, "marked_state": "1011"}
grover_circuit = Grover(params)  # Not yet implemented with new API

# Or use the educational CLI command
# ariadne learn grover --qubits 4
```

## Educational Features

The `ariadne learn` command provides interactive demonstrations:

```bash
# Run algorithm demos
ariadne learn demo grover --qubits 4
ariadne learn demo qft --qubits 3

# Take quantum computing quizzes
ariadne learn quiz gates
ariadne learn quiz algorithms

# Visualize quantum circuits
ariadne learn visualize path/to/circuit.qasm
```

## Classroom Tips

1. **Cross-Platform Consistency**: Ariadne works the same way on macOS, Linux, and Windows
2. **Labs and Assignments**: Students can run the same code across different hardware
3. **Educational Mode**: Use `simulate(circuit, education_mode=True)` for detailed output
4. **Algorithm Exploration**: Students can experiment with different algorithm parameters

## Common Classroom Examples

### 1. Entanglement Demonstration
```python
# Bell state showing quantum entanglement
from ariadne import simulate
from qiskit import QuantumCircuit

bell = QuantumCircuit(2, 2)
bell.h(0)
bell.cx(0, 1)
bell.measure_all()

result = simulate(bell, shots=1000)
# Results will show only |00⟩ and |11⟩ states - demonstrating entanglement
```

### 2. Quantum Advantage
```python
# Show the difference between classical and quantum approaches
# Deutsch-Jozsa algorithm with exponential speedup
from ariadne.algorithms import get_algorithm

dj_algorithm = get_algorithm("deutsch_jozsa")
# Only 1 query vs 2^(n-1)+1 classically
```

## Troubleshooting

- **Performance**: First runs may be slow due to compilation overhead
- **Memory**: Large circuits may require reducing qubit count
- **Backends**: Ariadne automatically falls back if specialized backends aren't available

## Next Steps

- Explore the [Algorithm Library](../tutorials/education/algorithms.md) for classroom examples
- Review the [Core Concepts](../user-guide/core-concepts.md) for deeper understanding
- Try the [Interactive Tutorials](../tutorials/education/) for guided learning
