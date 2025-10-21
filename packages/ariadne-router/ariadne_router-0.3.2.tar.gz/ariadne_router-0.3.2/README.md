<div align="center">

# Ariadne – Zero-config quantum simulator bundle

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![CI/CD Pipeline](https://img.shields.io/github/actions/workflow/status/Hmbown/ariadne/ci.yml?branch=main&label=CI%2FCD&style=for-the-badge)](https://github.com/Hmbown/ariadne/actions/workflows/ci.yml)
[![codecov](https://img.shields.io/codecov/c/github/Hmbown/ariadne/main?style=for-the-badge)](https://codecov.io/gh/Hmbown/ariadne)
[![Code Style](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![PyPI version](https://badge.fury.io/py/ariadne-router.svg)](https://badge.fury.io/py/ariadne-router)
[![Pytest](https://img.shields.io/badge/tested%20with-pytest-0-9.svg?logo=pytest)](https://pytest.org)

</div>

---

## Overview

> **Run 15+ quantum algorithms** (Bell, QAOA, VQE, QFT, Grover, QPE, stabilizer, error correction, quantum ML) **on any laptop or OS** with the same code. Ariadne automatically selects the optimal backend (Stim, Qiskit, MPS, Metal, CUDA) so students and CI pipelines never break.

Ariadne automatically routes quantum circuits to the optimal backend, eliminating manual simulator selection. Whether you're teaching quantum computing, running cross-platform benchmarks, or setting up CI pipelines, Ariadne ensures reproducible results without configuration complexity.

**Ideal for:**
- **Education**: One pip install that works across macOS, Linux, and WSL
- **Research**: Reproducible cross-simulator benchmarks
- **DevOps**: Multi-backend regression testing in GitHub Actions

## 🚦 Quick Links

- [Documentation Hub](docs/index.md) - Complete documentation with persona-based guides
- [For Instructors](docs/getting-started/for-instructors.md) - Classroom setup and education tools
- [For Researchers](docs/getting-started/for-researchers.md) - Advanced features and benchmarking
- [For DevOps](docs/getting-started/for-devops.md) - CI/CD integration and production deployment

### First Simulation

Ariadne automatically routes circuits to optimal simulators without code changes:

```python
from ariadne import simulate
from qiskit import QuantumCircuit

# Create any circuit - Ariadne handles backend selection
qc = QuantumCircuit(20, 20)
qc.h(range(10))
for i in range(9):
    qc.cx(i, i + 1)
qc.measure_all()

# Single call handles all backend complexity
result = simulate(qc, shots=1000)
print(f"Backend used: {result.backend_used}")
print(f"Execution time: {result.execution_time:.4f}s")
print(f"Unique outcomes: {len(result.counts)}")
```

[📖 Documentation](docs/index.md) • [💡 Examples](examples/README.md) • [🚀 Quick Start](#-getting-started) • [🧠 Core API](#-core-api) • [📊 Performance](#-performance)

---

## ✨ Key Features

- **🧠 Intelligent Routing** - Automatically selects optimal backend based on circuit properties
- **⚡ Stim Auto-Detection** - Routes pure Clifford circuits to Stim for large-scale simulation
- **🍎 Apple Silicon Acceleration** - JAX-Metal backend for M-series chip optimization
- **🚀 CUDA Support** - NVIDIA GPU acceleration when available
- **🔄 Zero Configuration** - `simulate(circuit, shots)` works without manual backend selection
- **🔢 Universal Fallback** - Always returns results, even when specialized backends fail
- **📊 Transparent Decisions** - Inspect and validate every routing decision
- **🔌 Extensible** - Modular backend interface for community contributions

---

## 🧰 Use Cases

**Education & Workshops**
- Run 15+ canonical algorithms without manual simulator selection
- Comprehensive education notebooks with mathematical background
- One-command demo: `python examples/quickstart.py`

**Research Prototyping**
- Iterate with `simulate(qc, shots)` - Ariadne picks best backend automatically
- Override when needed: `simulate(qc, backend='mps')`

**CI/Regression Testing**
- Same tests run across macOS/Linux/Windows
- Graceful fallback for missing backends with decision logging

**Benchmarking & Feasibility**
- Large stabilizer circuits route to Stim (when statevector fails)
- Low-entanglement circuits route to MPS for speed/memory benefits

**Apple Silicon Optimization**
- Metal backend for general-purpose circuits on M-series Macs
- Automatic fallback to CPU when needed

---

## 🧭 Routing Overview

| Circuit Type | Backend | Reason |
|---|---|---|
| Pure Clifford (GHZ, stabilizers) | `stim` | Fast stabilizer simulation |
| Low entanglement, shallow depth | `MPS` | Efficient tensor-network |
| High entanglement (QFT, QPE) | `Tensor Network` | Complex circuit contraction |
| Quantum search (Grover) | `Qiskit` | Balanced performance |
| Error correction (Steane) | `Qiskit` | Robust for stabilizers |
| General circuits (Apple Silicon) | `Metal` | JAX/Metal acceleration |
| General circuits (portable) | `Qiskit` | Reliable CPU fallback |

Override routing when needed:

```python
simulate(qc, shots=1000, backend='mps')
```

Command-line interface:

```bash
ariadne simulate circuit.qasm --shots 1000
ariadne benchmark-suite --algorithms qft,grover,qpe,steane
ariadne status --detailed
```

### Routing Matrix

![Routing matrix](docs/source/_static/routing_matrix.png)

Regenerate with:
```bash
python examples/routing_matrix.py --shots 256 --generate-image docs/source/_static/routing_matrix.png
```

---

## 🔌 Supported Backends

Ariadne automatically detects and routes to available backends:

- **Qiskit CPU simulator** (`qiskit`) - Always available baseline
- **Stim stabilizer simulator** (`stim`) - Specialized for Clifford circuits
- **Matrix Product State** (`mps`) via `quimb`
- **Tensor Network** (`tensor_network`) via `cotengra`/`quimb`
- **JAX Metal** (`jax_metal`) - Apple Silicon acceleration
- **CUDA** (`cuda`) - GPU acceleration via `cupy`
- **DDSIM** (`ddsim`) - Alternative simulator via `mqt.ddsim`
- **Cirq** (`cirq`) - Via `src/ariadne/backends/cirq_backend.py`
- **PennyLane** (`pennylane`) - Via `src/ariadne/backends/pennylane_backend.py`
- **Qulacs** (`qulacs`) - Via `src/ariadne/backends/qulacs_backend.py`
- **Experimental**: PyQuil, Braket, Q#, OpenCL

### Supported Algorithms

15+ quantum algorithms with standardized interfaces:

- **Foundational**: Bell States, GHZ States, Quantum Fourier Transform (QFT)
- **Search**: Grover's Search, Bernstein-Vazirani
- **Optimization**: QAOA, VQE
- **Error Correction**: Steane Code, Surface Code
- **Quantum ML**: QSVM, VQC, Quantum Neural Network
- **Specialized**: Quantum Phase Estimation (QPE), Deutsch-Jozsa, Simon's Algorithm, Quantum Walk, Amplitude Amplification

Backends are implemented in `src/ariadne/backends/` and selected via routing logic in `src/ariadne/router.py`.

---

## 🎯 Transparent Decision Making

Ariadne provides complete transparency into routing decisions:

```python
from ariadne import explain_routing, show_routing_tree
from qiskit import QuantumCircuit

# Create a circuit
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

# Get detailed routing explanation
explanation = explain_routing(qc)
print(explanation)

# Visualize the routing tree
print(show_routing_tree())
```

---

## 🚀 Getting Started

### Installation

**PyPI package:**
```bash
pip install ariadne-router
```

**Developer setup:**
```bash
git clone https://github.com/Hmbown/ariadne.git
cd ariadne
pip install -e .
```

**Hardware acceleration extras:**
```bash
# Apple Silicon (M1/M2/M3/M4)
pip install -e .[apple]

# NVIDIA GPU (CUDA)
pip install -e .[cuda]

# All optional dependencies
pip install -e .[apple,cuda,viz]
```

📖 **Detailed installation: [Comprehensive Installation Guide](docs/comprehensive_installation.md)**

### Quickstart Demo

Run the quickstart example to see Ariadne in action:

```bash
python examples/quickstart.py
```

**Demo features:**
- Automatic backend selection
- Performance comparisons
- Routing transparency
- Hardware acceleration

### Quickstart GIF

![Quickstart Routing Demo](docs/source/_static/quickstart.gif)

Regenerate with:
```bash
python examples/generate_quickstart_gif.py --output docs/source/_static/quickstart.gif
```

---

## 🧠 Core API

**`simulate`** - High-level function that selects optimal backend and returns results:

```python
from ariadne import simulate

result = simulate(circuit, shots=1000)
print(result.backend_used)
print(result.execution_time)
```

**`EnhancedQuantumRouter`** - Object-oriented interface for routing policies:

```python
from ariadne import EnhancedQuantumRouter

router = EnhancedQuantumRouter()
decision = router.select_optimal_backend(circuit)
print(decision.recommended_backend)
print(decision.confidence_score)
```

**`ComprehensiveRoutingTree`** - Deterministic explanation tools:

```python
from ariadne import ComprehensiveRoutingTree

tree = ComprehensiveRoutingTree()
decision = tree.route_circuit(circuit)
print(decision.recommended_backend)
print(decision.confidence_score)
```

Configuration helpers and CLI provide additional management options.

---

## 📊 Performance

Ariadne focuses on **capability extension** and **consistent execution**. Automated routing ensures circuits use optimal simulators, including specialized tools like Stim and tensor-network engines.

### Representative Results

| Circuit | Backend | Router (ms) | Direct Qiskit (ms) | Notes |
|---------|---------|-------------|-------------------|-------|
| `ghz_chain_10` | Stim | 17.9 | 1.47 | Stim enables scaling beyond 24 qubits |
| `random_clifford_12` | Stim | 339 | 13.2 | Correct routing for stabilizer workloads |
| `random_nonclifford_8` | Tensor Network | 111 | 1.65 | Accurate for non-Clifford circuits |
| `qaoa_maxcut_8_p3` | Tensor Network | 67.6 | 1.34 | Automatic tensor-network selection |

### Platform Highlights

- **Apple Silicon**: JAX-Metal provides 1.16×–1.51× speedups
- **CUDA**: GPU acceleration with safe CPU fallback
- **Operational**: Consistent simulator selection for Clifford circuits with deterministic fallbacks

Full benchmarks and reproducibility scripts available in `benchmarks/results`.

---

## 🔧 Usage Examples

### Automatic Specialized Circuit Detection

Ariadne routes large Clifford circuits to Stim automatically:

```python
from ariadne import simulate
from qiskit import QuantumCircuit

# 40-qubit GHZ state - would crash plain Qiskit
qc = QuantumCircuit(40, 40)
qc.h(0)
for i in range(39):
    qc.cx(i, i + 1)
qc.measure_all()

# Automatically routes to Stim
result = simulate(qc, shots=1000)
print(f"Backend used: {result.backend_used}")  # -> stim
```

### Advanced Routing Control

Fine-grained control over routing strategies:

```python
from ariadne import ComprehensiveRoutingTree, RoutingStrategy
from qiskit import QuantumCircuit

circuit = QuantumCircuit(2, 2)
circuit.h(0)
circuit.cx(0, 1)
circuit.measure_all()

router = ComprehensiveRoutingTree()
decision = router.route_circuit(circuit, strategy=RoutingStrategy.MEMORY_EFFICIENT)

print(f"Selected: {decision.recommended_backend.value}")
print(f"Confidence: {decision.confidence_score:.2f}")
print(f"Expected speedup: {decision.expected_speedup:.1f}x")
```

**Available routing strategies:**
- `SPEED_FIRST` - Prioritize execution speed
- `ACCURACY_FIRST` - Favor accuracy and robustness
- `MEMORY_EFFICIENT` - Optimize memory usage
- `CLIFFORD_OPTIMIZED` - Specialized for Clifford circuits
- `ENTANGLEMENT_AWARE` - Prefer TN/MPS for low entanglement
- `STABILIZER_FOCUSED` - Emphasize stabilizer-friendly paths
- `APPLE_SILICON_OPTIMIZED` - Hardware-aware for M-series
- `CUDA_OPTIMIZED` - GPU acceleration focused
- `CPU_OPTIMIZED` - Prefer portable CPU simulators
- `RESEARCH_MODE` - Exploration-oriented defaults
- `EDUCATION_MODE` - Deterministic, simplified defaults
- `PRODUCTION_MODE` - Conservative, reproducible defaults
- `AUTO_DETECT` - Intelligent analysis (default)
- `HYBRID_MULTI_BACKEND` - Adaptive multi-path strategy

---

## 🛡️ Project Status

### Test Coverage
- **Unit Tests**: 38%+ coverage across core modules
- **Integration Tests**: Continuous testing with one known flaky performance test
- **Backend Tests**: All major backends tested

### Documentation
- **Comprehensive Guides**: Installation, usage, and API documentation
- **Examples Gallery**: 15+ working examples
- **Performance Reports**: Detailed benchmarking
- **API Reference**: Complete documentation with examples

### Development Infrastructure
- **CI/CD Pipeline**: Automated testing on Python 3.11-3.12
- **Code Quality**: Ruff linting, mypy type checking, pre-commit hooks
- **Security**: Bandit security scanning, dependency safety checks
- **Release Management**: Automated versioning and changelog generation

---

## 🤝 Contributing

We welcome contributions from bug fixes to new features. Read our [**Contributing Guidelines**](docs/project/CONTRIBUTING.md) to get started.

### Development Setup

```bash
git clone https://github.com/Hmbown/ariadne.git
cd ariadne
pip install -e .[dev]

# Set up pre-commit hooks
pre-commit install

# Run unit tests
pytest tests/ -v
```

📖 **Detailed setup: [Comprehensive Installation Guide](docs/comprehensive_installation.md#development-setup)**

---

## 💬 Community

- **GitHub Discussions:** [Ask questions and share ideas](https://github.com/Hmbown/ariadne/discussions)
- **Issue Tracker:** [Report bugs and request features](https://github.com/Hmbown/ariadne/issues)

---

## ✅ Quick Verification

Ariadne has been comprehensively tested with 45 tests achieving 97.7% pass rate.

**Installation Check:**
```bash
# Verify installation
python3 -c "from ariadne import simulate; print('✓ Ready to go!')"

# Test basic functionality
python3 examples/quickstart.py

# Check CLI
ariadne status
```

**Performance Highlights:**
- Stim: ~100,000 shots/s (Clifford circuits)
- Qiskit: ~60,000 shots/s (general fallback)
- JAX Metal: 179-226k shots/s (Apple Silicon)
- Tensor Network: ~200-4,600 shots/s (low-entanglement)

**Usage Tips:**
- Start with automatic routing (`simulate()` without backend parameter)
- Use `explain_routing()` to understand backend selection
- Explore the algorithm library: `from ariadne.algorithms import list_algorithms`
- Run education notebooks for comprehensive learning

---

## 📜 License

Ariadne is released under the [Apache 2.0 License](LICENSE).

**Project Policies:**
- [CHANGELOG](CHANGELOG.md)
- [SECURITY](SECURITY.md)
- [CODE OF CONDUCT](CODE_OF_CONDUCT.md)

---

## 🙏 Acknowledgments

Ariadne builds upon excellent open-source quantum frameworks:
- [Qiskit](https://qiskit.org/) for quantum circuit representation
- [Stim](https://github.com/quantumlib/Stim) for Clifford circuit simulation
- [Quimb](https://github.com/quimb/quimb) for tensor network operations
- [JAX](https://github.com/google/jax) for hardware acceleration

---
