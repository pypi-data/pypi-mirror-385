# Quantum Algorithm Catalog

Ariadne includes a comprehensive collection of quantum algorithms with standardized interfaces and educational materials.

## Available Algorithms

### Foundational Algorithms
- **Bell State** - Maximally entangled two-qubit states
- **GHZ State** - Multi-qubit Greenberger-Horne-Zeilinger states
- **Quantum Fourier Transform (QFT)** - Basis for phase estimation and Shor's algorithm
- **Quantum Phase Estimation (QPE)** - Precision eigenphase estimation

### Search Algorithms
- **Grover's Search** - Unstructured search with quadratic speedup
- **Bernstein-Vazirani** - Linear speedup for hidden string problems

### Optimization Algorithms
- **QAOA** - Quantum Approximate Optimization Algorithm
- **VQE** - Variational Quantum Eigensolver

### Error Correction
- **Steane Code** - [[7,1,3]] CSS quantum error correction code
- **Surface Code** - Topological error correction (simplified)

### Machine Learning
- **QSVM** - Quantum Support Vector Machine
- **VQC** - Variational Quantum Classifier
- **Quantum Neural Network** - Parameterized quantum circuits

### Specialized Algorithms
- **Deutsch-Jozsa** - Constant vs balanced function discrimination
- **Simon's Algorithm** - Period finding with exponential speedup
- **Quantum Walk** - Quantum analogue of classical random walk
- **Amplitude Amplification** - General technique for algorithm speedup

## Usage

```python
from ariadne.algorithms import get_algorithm, AlgorithmParameters
from ariadne import simulate

# Get algorithm class
algorithm_class = get_algorithm('qft')

# Create instance with parameters
params = AlgorithmParameters(n_qubits=4)
algorithm = algorithm_class(params)

# Generate circuit
circuit = algorithm.create_circuit()

# Simulate with automatic backend selection
result = simulate(circuit, shots=1000)
```

## Educational Materials

Each algorithm includes comprehensive educational materials in the [`examples/education/`](../examples/education/) directory:

- Mathematical background and theory
- Step-by-step implementation guides
- Cross-backend performance analysis
- Interactive Jupyter notebooks

See the [Education README](../examples/education/README.md) for details.

## Algorithm Interface

All algorithms implement the standardized `QuantumAlgorithm` interface:

```python
class QuantumAlgorithm:
    def __init__(self, parameters: AlgorithmParameters):
        """Initialize algorithm with parameters"""

    def create_circuit(self) -> QuantumCircuit:
        """Generate the quantum circuit"""

    def get_metadata(self) -> AlgorithmMetadata:
        """Get algorithm metadata and information"""
```

## Listing Available Algorithms

```python
from ariadne.algorithms import list_algorithms

# Get all available algorithms
algorithms = list_algorithms()
print(f"Available algorithms: {algorithms}")
```
