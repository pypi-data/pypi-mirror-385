# Ariadne Quantum Algorithm Education

Instructors & students – runs on any laptop

This directory contains comprehensive educational materials for quantum algorithms, designed to work seamlessly with Ariadne's unified algorithm module. Each notebook includes mathematical background, implementation details, and cross-backend performance analysis.

## Available Education Notebooks

### Foundational Quantum Algorithms
1. **[Bell State Classroom](01_bell_state_classroom.ipynb)** - Entanglement basics and multi-simulator reproducibility
2. **[Quantum Fourier Transform](04_quantum_fourier_transform.ipynb)** - Foundation for phase estimation and Shor's algorithm
3. **[Quantum Phase Estimation](06_quantum_phase_estimation.ipynb)** - Precision measurement with quantum speedup

### Search and Optimization Algorithms
4. **[QAOA Algorithm](02_qaoa_algorithm.ipynb)** - Quantum Approximate Optimization for combinatorial problems
5. **[Grover's Search](05_grover_search.ipynb)** - Unstructured search with quadratic speedup
6. **[Variational Circuits](03_variational_circuits.ipynb)** - VQE ansatz exploration and optimization

### Advanced Quantum Computing Topics
7. **[Quantum Error Correction](07_quantum_error_correction.ipynb)** - Steane code implementation and fault tolerance
8. **[Quantum Machine Learning](08_quantum_machine_learning.ipynb)** - Quantum Support Vector Machine and feature maps

## Notebook Structure

Each education notebook follows a consistent structure:

1. **Algorithm Overview** - High-level introduction and significance
2. **Mathematical Background** - Detailed theoretical foundations
3. **Circuit Implementation** - Step-by-step circuit construction
4. **Cross-Backend Testing** - Performance analysis across different simulators
5. **Scaling Analysis** - How algorithm behavior changes with size
6. **Educational Content** - In-depth explanations and applications
7. **Key Takeaways** - Summary of important concepts

## Usage Instructions

### Prerequisites
```bash
pip install ariadne-router
# Optional: install hardware acceleration extras
pip install ariadne-router[apple,cuda]
```

### Running Notebooks
```bash
# Navigate to education directory
cd examples/education

# Start Jupyter notebook
jupyter notebook

# Or use JupyterLab
jupyter lab
```

### Quick Algorithm Testing
```python
from ariadne.algorithms import get_algorithm, AlgorithmParameters
from ariadne import simulate

# Test QFT
qft_class = get_algorithm('qft')
params = AlgorithmParameters(n_qubits=4)
qft = qft_class(params)
circuit = qft.create_circuit()

# Simulate across backends
for backend in ['stim', 'qiskit', 'mps']:
    try:
        result = simulate(circuit, shots=1000, backend=backend)
        print(f"{backend}: {result.execution_time:.4f}s")
    except Exception as e:
        print(f"{backend}: Failed - {e}")
```

## Algorithm Categories

### Foundational Algorithms
- **Bell States**: Demonstrate quantum entanglement and non-locality
- **GHZ States**: Multi-qubit entanglement and multipartite correlations
- **QFT**: Quantum Fourier transform and its applications

### Search Algorithms
- **Grover's Search**: Quadratic speedup for unstructured search
- **Bernstein-Vazirani**: Linear speedup for hidden string problems

### Optimization Algorithms
- **QAOA**: Combinatorial optimization with quantum enhancement
- **VQE**: Ground state energy estimation for Hamiltonians

### Error Correction
- **Steane Code**: [[7,1,3]] CSS code for fault tolerance
- **Surface Code**: Topological error correction (simplified)

### Quantum Machine Learning
- **QSVM**: Quantum Support Vector Machine with quantum kernels
- **VQC**: Variational Quantum Classifier
- **Quantum Neural Networks**: Parameterized quantum circuits

### Specialized Algorithms
- **QPE**: Quantum phase estimation for eigenvalue problems
- **Deutsch-Jozsa**: Constant vs balanced function discrimination
- **Simon's Algorithm**: Period finding with exponential speedup

## Educational Features

### Mathematical Rigor
- Detailed mathematical derivations
- Complexity analysis and quantum advantage explanations
- Connection to classical algorithms

### Practical Implementation
- Step-by-step circuit construction
- Parameter customization options
- Error handling and debugging tips

### Performance Analysis
- Cross-backend comparison
- Scaling behavior analysis
- Resource utilization metrics

### Interactive Learning
- Executable code cells
- Visualization of quantum states
- Real-time performance measurement

## Integration with Ariadne

These notebooks leverage Ariadne's unified algorithm module:

```python
from ariadne.algorithms import list_algorithms, get_algorithm

# List all available algorithms
algorithms = list_algorithms()
print(f"Available algorithms: {algorithms}")

# Get specific algorithm
algorithm_class = get_algorithm('grover')
```

### Automatic Backend Routing
Ariadne automatically selects the optimal backend for each algorithm:

```python
from ariadne import simulate, explain_routing

# Let Ariadne choose the best backend
result = simulate(circuit, shots=1000)

# Understand the routing decision
explanation = explain_routing(circuit)
print(explanation)
```

## Contributing

We welcome contributions to the education materials:

1. **New Algorithms**: Add notebooks for additional quantum algorithms
2. **Improvements**: Enhance existing notebooks with better explanations
3. **Translations**: Create versions in different languages
4. **Exercises**: Add practice problems and solutions

## Support

For questions about the education materials:
- Check the [Ariadne documentation](../../docs/README.md)
- Open an issue on [GitHub](https://github.com/Hmbown/ariadne/issues)
- Join the discussion in [GitHub Discussions](https://github.com/Hmbown/ariadne/discussions)
