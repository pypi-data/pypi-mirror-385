# Ariadne Quick Start Guide

Get up and running with Ariadne in 5 minutes! This guide will help you install Ariadne and run your first quantum circuit simulation with intelligent routing.

## Installation

### Prerequisites
- Python 3.11 or higher
- pip package manager

### Install from Source
```bash
git clone https://github.com/Hmbown/ariadne.git
cd ariadne
pip install -e .
```

### Install with Optional Backends
For specific hardware acceleration, install with optional dependencies:

```bash
# For Apple Silicon (M-series chips)
pip install -e .[apple]

# For NVIDIA GPU acceleration
pip install -e .[cuda]

# For visualization capabilities
pip install -e .[viz]
```

## Your First Quantum Circuit

Ariadne automatically routes your circuit to the optimal simulator without any code changes.

```python
from ariadne import simulate
from qiskit import QuantumCircuit

# Create a quantum circuit
qc = QuantumCircuit(10, 10)
qc.h(range(10))  # Apply Hadamard gates to all qubits
for i in range(9):
    qc.cx(i, i + 1)  # Create entanglement
qc.measure_all()

# Let Ariadne handle the backend selection
result = simulate(qc, shots=1000)

print(f"Backend used: {result.backend_used}")
print(f"Execution time: {result.execution_time:.4f}s")
print(f"Unique outcomes: {len(result.counts)}")
print(f"Sample counts: {dict(list(result.counts.items())[:5])}")
```

## Automatic Clifford Circuit Detection

Ariadne recognizes when circuits can benefit from specialized simulators like Stim:

```python
from ariadne import simulate
from qiskit import QuantumCircuit

# Create a large Clifford circuit
qc = QuantumCircuit(40, 40)
qc.h(0)
for i in range(39):
    qc.cx(i, i + 1)  # Creates a 40-qubit GHZ state
qc.measure_all()

# Ariadne automatically routes to Stim for optimal performance
result = simulate(qc, shots=1000)
print(f"Backend used: {result.backend_used}")  # -> stim
print(f"Execution time: {result.execution_time:.4f}s")
```

## Using Different Circuit Libraries

Ariadne supports multiple quantum circuit formats:

### Qiskit Circuits
```python
from ariadne import simulate
from qiskit import QuantumCircuit

qc = QuantumCircuit(5)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()
result = simulate(qc, shots=1000)
```

### OpenQASM 3.0
```python
from ariadne import simulate

qasm_string = """
OPENQASM 3.0;
qubit[5] q;
bit[5] c;
h q[0];
cx q[0], q[1];
measure q -> c;
"""

result = simulate(qasm_string, shots=1000)
```

## Advanced Usage

### Custom Backend Selection
```python
from ariadne import simulate, QuantumRouter
from qiskit import QuantumCircuit

qc = QuantumCircuit(10)
qc.h(range(10))

# Force specific backend
router = QuantumRouter()
result = router.simulate(qc, shots=1000, backend="stim")

# Or let Ariadne choose
result = router.simulate(qc, shots=1000)  # Auto-routing
```

### Performance Analysis
```python
from ariadne import analyze_circuit
from qiskit import QuantumCircuit

qc = QuantumCircuit(20)
qc.h(range(20))
for i in range(19):
    qc.cx(i, i + 1)

analysis = analyze_circuit(qc)
print(f"Circuit analysis: {analysis}")
print(f"Recommended backend: {analysis.recommended_backend}")
```

## Next Steps

- Explore the [Examples Gallery](../examples/README.md) for more use cases
- Read the [Performance Guide](PERFORMANCE_GUIDE.md) for optimization tips
- Check out [Advanced Backend Routing](source/advanced_backends_routing.rst) for custom routing logic

## Troubleshooting

If you encounter any issues:

1. **Installation fails**: Ensure you have Python 3.11+ and the latest pip
2. **Import errors**: Verify all dependencies are installed with `pip install -e .[dev]`
3. **Backend errors**: Check that required hardware (GPU, Apple Silicon) is available

## Need Help?

- Check our [Troubleshooting Guide](troubleshooting.md)
- Join our [GitHub Discussions](https://github.com/Hmbown/ariadne/discussions)
- Report issues on our [Issue Tracker](https://github.com/Hmbown/ariadne/issues)

---

*Ready to explore more? Continue to the [Basic Usage Guide](basic-usage.md) for detailed API documentation and advanced features.*
