# Getting Started for Research Scientists

This guide provides everything you need to leverage Ariadne for quantum research, including benchmarking, reproducibility tools, and access to multiple quantum backends.

## Installation

Ariadne installs with a single pip command:

```bash
pip install ariadne-router
```

For specialized hardware acceleration:

```bash
# Apple Silicon
pip install ariadne-router[apple]

# NVIDIA GPU
pip install ariadne-router[cuda]

# All optional dependencies
pip install ariadne-router[apple,cuda,viz]
```

## Core Research Workflow

### 1. Automatic Backend Selection

Ariadne automatically routes your circuits to the optimal backend:

```python
from ariadne import simulate

# Your circuit works on any platform
result = simulate(your_circuit, shots=10000)

print(f"Backend used: {result.backend_used}")
print(f"Execution time: {result.execution_time:.4f}s")
print(f"Routing explanation: {result.routing_explanation}")
```

### 2. Reproducible Results

Every simulation includes routing transparency:

```python
from ariadne import simulate, explain_routing

# Understand why a backend was selected
explanation = explain_routing(your_circuit)
print(explanation)

# Or access routing info directly from results
result = simulate(your_circuit)
print(f"Backend: {result.backend_used}")
print(f"Routing explanation: {result.routing_explanation}")
print(f"Confidence score: {result.routin_confidence_score}")
```

## Benchmarking Tools

### 1. Performance Comparison

```python
from ariadne import simulate
import time

# Compare all available backends
from ariadne.types import BackendType

backends = list(BackendType)
results = {}

for backend in backends:
    start_time = time.time()
    try:
        result = simulate(your_circuit, shots=1000, backend=backend.value)
        end_time = time.time()
        results[backend.value] = {
            'time': end_time - start_time,
            'success': True,
            'backend_used': result.backend_used
        }
    except Exception as e:
        results[backend.value] = {
            'time': float('inf'),
            'success': False,
            'error': str(e)
        }

# Analyze performance
for backend, data in results.items():
    if data['success']:
        print(f"{backend}: {data['time']:.4f}s")
```

### 2. Benchmark Suite

Use the command line for comprehensive benchmarks:

```bash
# Run comprehensive benchmark suite
ariadne benchmark-suite --algorithms qft,grover,vqe --backends auto,qiskit,stim --shots 1000

# Generate reproducible benchmark reports
ariadne benchmark-suite --algorithms all --output benchmark_report.json
```

## Algorithm Library

Ariadne includes 15+ research-grade quantum algorithms:

```python
from ariadne.algorithms import get_algorithm, list_algorithms

# List all available algorithms
print("Available algorithms:", list_algorithms())

# Create and analyze a quantum algorithm
QAOA = get_algorithm("qaoa")
params = {"n_qubits": 6, "layers": 3}  # 3-layer QAOA
qaoa_circuit = QAOA(params)  # This would create a QAOA circuit

# Access educational content and analysis
algorithm = QAOA(params)
analysis = algorithm.analyze_circuit_properties()
print("Circuit analysis:", analysis)
```

## Advanced Routing Control

For research requiring specific backend selection:

```python
from ariadne import EnhancedQuantumRouter, RoutingStrategy

# Use specific routing strategies
router = EnhancedQuantumRouter()

# Research-mode routing with detailed explanations
decision = router.select_optimal_backend(
    circuit=your_circuit,
    strategy=RoutingStrategy.RESEARCH_MODE
)

print(f"Recommended: {decision.recommended_backend}")
print(f"Confidence: {decision.confidence_score}")
print(f"Reasoning: {decision.reasoning}")
```

## Reproducibility Features

### 1. Configuration Management

```python
from ariadne import get_config_manager

# Save and load configurations
config_manager = get_config_manager()
config_manager.save_config("research_config.json")

# Load specific configuration for reproducible results
config_manager.load_config("research_config.json")
```

### 2. Result Documentation

```python
from ariadne import simulate

# Each simulation includes metadata for reproducibility
result = simulate(your_circuit, shots=10000)

# Save complete results with routing information
research_output = {
    'circuit_properties': result.circuit_analysis,  # Circuit characteristics
    'backend_used': result.backend_used,           # Backend selection
    'routing_explanation': result.routing_explanation,  # Why this backend
    'execution_time': result.execution_time,       # Performance metrics
    'results': result.counts,                      # Measurement outcomes
    'metadata': result.metadata                    # Additional info
}
```

## Research-Specific Tips

1. **Performance Validation**: Use `ariadne benchmark-suite` to validate performance on your specific hardware
2. **Cross-Platform Verification**: Run the same experiment on different systems using the same code
3. **Backend Analysis**: Compare results across different simulators for verification
4. **Large-Scale Simulation**: Ariadne automatically routes large Clifford circuits to Stim for scalability

## Troubleshooting

- **Large Circuits**: Ariadne automatically routes to specialized backends (Stim, MPS, Tensor Network) for large circuits
- **Performance Variance**: First runs may have compilation overhead; subsequent runs are faster
- **Memory Management**: Use `get_resource_manager()` to monitor and manage memory usage

## Next Steps

- Review the [Core Concepts](../user-guide/core-concepts.md) for advanced features
- Explore the [Algorithm Library](../tutorials/education/algorithms.md) for research applications
- Check the [API Reference](../user-guide/api-reference.md) for complete documentation
- Try the [Benchmarking Guide](../tutorials/benchmarking/) for performance analysis
