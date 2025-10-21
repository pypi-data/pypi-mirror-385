# Ariadne Quantum Simulator Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Core Features](#core-features)
4. [Educational Tools](#educational-tools)
5. [Benchmarking Tools](#benchmarking-tools)
6. [CLI Usage](#cli-usage)
7. [API Reference](#api-reference)
8. [Examples](#examples)
9. [Troubleshooting](#troubleshooting)

## Introduction

Ariadne is a zero-configuration quantum simulator bundle that automatically routes your circuits to the optimal backend. Whether you're teaching quantum computing, running benchmarks across platforms, or setting up CI pipelines, Ariadne ensures reproducible results without the complexity of manual backend selection.

### Key Features
- **Intelligent Routing**: Mathematical analysis of circuit properties automatically selects the optimal backend
- **Auto-Detection**: Pure Clifford circuits are automatically routed to Stim
- **Hardware Acceleration**: Support for Apple Silicon, CUDA, and other specialized hardware
- **Zero Configuration**: Single function call handles all backend complexity
- **Universal Fallback**: Always returns a result even when specialized backends fail
- **Transparent Decisions**: Every routing decision can be inspected and validated

## Installation

### Basic Installation
```bash
pip install ariadne-router
```

### With Hardware Acceleration
```bash
# For Apple Silicon
pip install ariadne-router[apple]

# For CUDA
pip install ariadne-router[cuda]

# For all optional dependencies
pip install ariadne-router[apple,cuda,viz]
```

### Developer Installation
```bash
git clone https://github.com/Hmbown/ariadne.git
cd ariadne
pip install -e .
```

## Core Features

### Basic Usage
```python
from ariadne import simulate
from qiskit import QuantumCircuit

# Create any circuit - let Ariadne handle the rest
qc = QuantumCircuit(20, 20)
qc.h(range(10))
for i in range(9):
    qc.cx(i, i + 1)
qc.measure_all()

# One simple call that handles all backend complexity
result = simulate(qc, shots=1000)
print(f"Backend used: {result.backend_used}")
print(f"Execution time: {result.execution_time:.4f}s")
print(f"Unique outcomes: {len(result.counts)}")
```

### Manual Backend Selection
```python
# Force specific backend if needed
result = simulate(circuit, shots=1000, backend='qiskit')
```

### Routing Explanation
```python
from ariadne import explain_routing, show_routing_tree

# Get detailed explanation of routing decision
explanation = explain_routing(qc)
print(explanation)

# Visualize entire routing tree
print(show_routing_tree())
```

## Educational Tools

Ariadne includes powerful educational tools to help learn quantum algorithms and concepts.

### Interactive Circuit Builder
```python
from ariadne.education import InteractiveCircuitBuilder

# Create a 2-qubit circuit builder
builder = InteractiveCircuitBuilder(2, "Bell State")
builder.add_hadamard(0, "Hadamard Gate", "Creates superposition")
builder.add_cnot(0, 1, "CNOT Gate", "Creates entanglement")
builder.add_measurement(0, 0, "Measurement", "Measure qubit 0")
builder.add_measurement(1, 1, "Measurement", "Measure qubit 1")

# View the circuit
print(builder.get_circuit().draw())

# Access history of steps
for step in builder.history:
    print(f"Step {step.step_number}: {step.title}")
    print(f"Description: {step.description}")
```

### Algorithm Explorer
```python
from ariadne.education import AlgorithmExplorer

# Initialize explorer
explorer = AlgorithmExplorer()

# List available algorithms
algorithms = explorer.list_algorithms()
print(f"Available algorithms: {algorithms}")

# Get detailed information about an algorithm
info = explorer.get_algorithm_info('bell')
print(f"Description: {info['metadata'].description}")
print(f"Educational content: {info['educational_content']}")
print(f"Circuit properties: {info['circuit_properties']}")

# Create a learning path
learning_path = explorer.create_learning_path('bell', n_qubits=2)
for step in learning_path:
    print(f"Step {step.step_number}: {step.title}")
    print(step.description)
```

### Quantum Concept Explorer
```python
from ariadne.education import explore_quantum_concept

# Explore fundamental quantum concepts
superposition_builder = explore_quantum_concept('superposition')
entanglement_builder = explore_quantum_concept('entanglement')
interference_builder = explore_quantum_concept('interference')

# Print the circuits for each concept
print("Superposition Circuit:")
print(superposition_builder.get_circuit().draw())

print("Entanglement Circuit:")
print(entanglement_builder.get_circuit().draw())
```

### Education Dashboard
```python
from ariadne.education import EducationDashboard

# Initialize dashboard
dashboard = EducationDashboard()

# Show available algorithms
dashboard.show_algorithm_list()

# Compare multiple algorithms
dashboard.compare_algorithms_interactive(['bell', 'ghz'])

# Run a learning path
dashboard.run_learning_path('bell', n_qubits=2)
```

## Benchmarking Tools

Ariadne provides comprehensive benchmarking capabilities for performance analysis.

### Enhanced Benchmark Suite
```python
from ariadne.enhanced_benchmarking import EnhancedBenchmarkSuite

# Initialize benchmark suite
suite = EnhancedBenchmarkSuite()

# Benchmark a single algorithm
results = suite.benchmark_single_algorithm(
    algorithm_name='bell',
    qubit_count=2,
    backend_name='auto',
    shots=1000,
    iterations=3
)

# Analyze results
for result in results:
    if result.success:
        print(f"Time: {result.execution_time:.4f}s")
        print(f"Throughput: {result.throughput:.2f} shots/s")
    else:
        print(f"Failed: {result.error_message}")
```

### Backend Comparison
```python
# Compare performance across different backends
comparison = suite.benchmark_backend_comparison(
    algorithm_name='bell',
    qubit_count=2,
    backends=['auto', 'qiskit', 'stim'],
    shots=1000
)

for backend, result in comparison.items():
    if result.success:
        print(f"{backend}: {result.execution_time:.4f}s, {result.throughput:.2f} shots/s")
    else:
        print(f"{backend}: FAILED")
```

### Scalability Testing
```python
# Test how performance scales with qubit count
scalability_result = suite.scalability_test(
    algorithm_name='bell',
    qubit_range=(2, 8, 2),  # From 2 to 8 qubits in steps of 2
    backend_name='auto',
    shots=1000
)

print(f"Qubits: {scalability_result.qubit_counts}")
print(f"Execution times: {scalability_result.execution_times}")
print(f"Throughputs: {scalability_result.throughputs}")
```

### Cross-Validation
```python
from ariadne.enhanced_benchmarking import CrossValidationSuite
from ariadne.algorithms import get_algorithm
from ariadne.algorithms.base import AlgorithmParameters

# Create a test circuit
alg_class = get_algorithm('bell')
circuit = alg_class(AlgorithmParameters(n_qubits=2)).create_circuit()

# Validate consistency across backends
validator = CrossValidationSuite()
validation_result = validator.validate_backend_consistency(
    circuit=circuit,
    backends=['auto', 'qiskit'],
    shots=1000,
    tolerance=0.05
)

print(f"Consistent: {validation_result['consistent']}")
print(f"Message: {validation_result['message']}")
```

### Performance Reports
```python
# Generate comprehensive performance report
report = suite.generate_performance_report()
print(report)

# Export results to file
suite.export_results('benchmark_results.json', format='json')
suite.export_results('benchmark_results.csv', format='csv')
```

### Comprehensive Benchmarking
```python
from ariadne.enhanced_benchmarking import run_comprehensive_benchmark

# Run comprehensive benchmark across algorithms, backends, and qubit counts
suite = run_comprehensive_benchmark(
    algorithms=['bell', 'ghz'],
    backends=['auto', 'qiskit'],
    qubit_counts=[2, 3, 4],
    shots=100
)
```

## CLI Usage

Ariadne provides a comprehensive command-line interface for all functionality.

### Basic Simulation
```bash
# Basic simulation
ariadne simulate path/to/circuit.qasm --shots 1000

# Force specific backend
ariadne simulate path/to/circuit.qasm --shots 1000 --backend qiskit

# Save results
ariadne simulate path/to/circuit.qasm --shots 1000 --output results.json
```

### System Status
```bash
# Check status of all backends
ariadne status

# Check status of specific backend
ariadne status --backend stim

# Detailed status information
ariadne status --detailed
```

### Configuration Management
```bash
# Create configuration templates
ariadne config create --template production --format yaml --output config.yaml

# Validate configuration
ariadne config validate config.yaml

# Show current configuration
ariadne config show
```

### Benchmarking
```bash
# Run performance benchmarks
ariadne benchmark --circuit path/to/circuit.qasm --shots 1000 --iterations 5

# Run comprehensive benchmark suite
ariadne benchmark-suite --algorithms bell,ghz,qft --backends auto,stim,qiskit --shots 1000

# Benchmark with output file
ariadne benchmark-suite --algorithms bell --output benchmark_results.json
```

### Educational Commands
```bash
# Show available educational commands
ariadne education --help

# Run algorithm demonstration
ariadne education demo bell --qubits 2 --verbose

# Take a quiz
ariadne education quiz gates

# Visualize a circuit
ariadne education visualize path/to/circuit.qasm --format text

# Show learning resources
ariadne learning list --category tutorials

# Get information about a specific resource
ariadne learning info bell_state
```

## API Reference

### Main Functions
- `simulate(circuit, shots=1000, backend=None)`: Main simulation function with automatic routing
- `explain_routing(circuit)`: Detailed explanation of routing decision
- `show_routing_tree()`: Visualize the routing decision tree
- `get_config_manager()`: Get the global configuration manager

### Educational Functions
- `InteractiveCircuitBuilder(n_qubits, title)`: Interactive circuit builder
- `AlgorithmExplorer()`: Explore quantum algorithms
- `explore_quantum_concept(concept_name)`: Explore quantum concepts
- `EducationDashboard()`: Comprehensive education dashboard

### Benchmarking Functions
- `EnhancedBenchmarkSuite()`: Enhanced benchmark suite
- `CrossValidationSuite()`: Cross-validation of results
- `run_comprehensive_benchmark()`: Run comprehensive benchmarks

## Examples

### Complete Example: Learning Quantum Algorithms
```python
from ariadne.education import (
    InteractiveCircuitBuilder,
    AlgorithmExplorer,
    QuantumConceptExplorer
)
from ariadne.enhanced_benchmarking import EnhancedBenchmarkSuite

# Learn about quantum concepts
concept_builder = QuantumConceptExplorer().explore_concept('entanglement')
print("Entanglement Circuit:")
print(concept_builder.get_circuit().draw())

# Explore algorithms
explorer = AlgorithmExplorer()
info = explorer.get_algorithm_info('bell')
print(f"Bell State: {info['metadata'].description}")

# Create custom circuit
builder = InteractiveCircuitBuilder(2, "Custom Circuit")
builder.add_hadamard(0)
builder.add_cnot(0, 1)

# Benchmark performance
suite = EnhancedBenchmarkSuite()
results = suite.benchmark_single_algorithm('bell', 2, 'auto', 100)
if results and results[0].success:
    print(f"Simulation time: {results[0].execution_time:.4f}s")
```

## Troubleshooting

### Common Issues

1. **Backend Not Available**: Some backends require additional dependencies. Check that you've installed the appropriate extras.

2. **Performance Issues**: For large circuits, consider using specialized backends:
   - Clifford circuits: Use `stim` backend
   - Low-entanglement circuits: Use `mps` backend
   - High-entanglement circuits: Use tensor network backends

3. **Memory Issues**: Large statevector simulations can require significant memory. Consider using MPS or tensor network backends for large circuits with limited entanglement.

4. **Routing Issues**: If automatic routing doesn't select the expected backend, check `explain_routing(circuit)` to understand the decision.

### Getting Help
- Check the examples directory for working code
- Use `ariadne --help` for CLI commands
- Report issues on the GitHub repository
- Use the discussion forum for questions
