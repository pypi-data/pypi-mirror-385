<div align="center">

# Ariadne

**Intelligent Quantum Circuit Routing**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![CI/CD Pipeline](https://img.shields.io/github/actions/workflow/status/Hmbown/ariadne/ci.yml?branch=main&label=CI%2FCD&style=for-the-badge)](https://github.com/Hmbown/ariadne/actions/workflows/ci.yml)
[![codecov](https://img.shields.io/codecov/c/github/Hmbown/ariadne/main?style=for-the-badge)](https://codecov.io/gh/Hmbown/ariadne)
[![Code Style](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![PyPI version](https://badge.fury.io/py/ariadne-router.svg)](https://badge.fury.io/py/ariadne-router)
[![Pytest](https://img.shields.io/badge/tested%20with-pytest-0-9.svg?logo=pytest)](https://pytest.org)

</div>

---

## 🔄 Release Status

- **PyPI package name**: `ariadne-router`
- **Publishing method**: Trusted Publisher (GitHub Actions OIDC)
- **Status**: Ready for release! Push a tag to publish to PyPI.


## Overview

> **In plain language:** Ariadne is a smart helper that looks at your quantum project and picks the machine that fits best, so you do not have to guess. You load a circuit, ask Ariadne to run it, and it quietly checks what hardware or simulator you have, chooses the match, runs the job, and keeps notes so you can repeat it later. This matters because it saves teams from trial-and-error testing, keeps results consistent, and lets newcomers focus on ideas instead of setup. Ready for the deeper dive? Jump to [Getting Started](#-getting-started), [Core API](#-core-api), or [Performance](#-performance).

Quantum development teams must balance diverse hardware constraints, simulator capabilities, and performance profiles. Ariadne automates that decision-making loop by analyzing each circuit and routing it to the most appropriate backend while preserving reproducibility and auditability. The platform eliminates manual benchmarking across numerous simulators and keeps workflows consistent across environments.

**Designed for**
- **Researchers** who need to iterate on algorithms quickly with deterministic, explainable routing decisions.
- **Developers** who integrate quantum workloads into larger systems and require predictable fallbacks.
- **Students** who want a single entry point for exploring multiple simulators without vendor-specific setup.
- **Enterprise teams** that demand governed execution paths, configurable policies, and transparent performance trade-offs.

Routing logic is deterministic and driven by measurable circuit characteristics, ensuring that every decision can be reproduced and audited when requirements evolve.

## 🚦 Start Here

- [Quick Start](#-getting-started)
- [Examples](#-usage-examples)
- [Advanced capabilities](#advanced-routing-control)

### Your First Simulation

Ariadne automatically routes your circuit to the optimal simulator without any code changes.

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

[📖 Local Docs](docs/README.md) • [💡 Examples](examples/README.md) • [🚀 Getting Started](#-getting-started) • [🧠 Core API](#-core-api) • [📊 Performance](#-performance) • [🤝 Contributing](#-contributing)

---

## ✨ Key Features

| Capability | Impact |
|---|---|
| **🧠 Intelligent Routing** | Mathematical analysis of circuit properties automatically selects the optimal backend without user intervention. |
| **⚡ Stim Auto-Detection** | Pure Clifford circuits are automatically routed to Stim, enabling the simulation of circuits that are too large for other backends. |
| **🍎 Apple Silicon Acceleration** | JAX-Metal backend can provide speedups for general-purpose circuits on M-series chips. |
| **🚀 CUDA Support** | NVIDIA GPU acceleration is supported when available, with performance improvements depending on the hardware and circuit structure. Actual speedups will vary based on your specific GPU and circuit characteristics. |
| **🔄 Zero Configuration** | `simulate(circuit, shots)` just works—no vendor imports or backend selection logic required. |
| **🔢 Universal Fallback** | Always returns a result, even when specialized backends fail. |
| **📊 Transparent Decisions** | Every routing decision can be inspected and validated with detailed reasoning. |
| **🔌 Extensible** | Apache 2.0 licensed with a modular backend interface for community contributions. |

---

## 🧰 Use Cases

- **Education and workshops**
  - Run canonical circuits (Bell/GHZ/Clifford, shallow variational) without choosing simulators. Ariadne routes to `stim`/`MPS`/`Qiskit`/`Metal` as appropriate.
  - One command demo: `python examples/quickstart.py`.

- **Research prototyping**
  - Iterate on algorithms with `simulate(qc, shots)` and let Ariadne pick the best backend by structure (Clifford ratio, entanglement heuristics).
  - Override when needed with `simulate(qc, backend='mps')` and compare.

- **CI/regression testing**
  - Same tests run across macOS/Linux/Windows. Missing backends fail over cleanly; logs record decisions.
  - Good for ensuring algorithms don’t silently degrade across environments.

- **Benchmarking and feasibility checks**
  - Large stabilizer circuits route to `stim` (feasible when statevector fails).
  - Low-entanglement shallow circuits route to `MPS` for speed/memory wins.

- **Apple Silicon acceleration**
  - On M-series Macs, try `Metal` for general-purpose circuits; otherwise fall back to CPU.

---

## 🧭 Routing at a glance

| Circuit characteristics | Expected backend | Why |
|---|---|---|
| Pure Clifford (e.g., GHZ, stabilizers) | `stim` | Specialized, extremely fast stabilizer simulation |
| Low entanglement, shallow depth | `MPS` | Efficient tensor-network representation |
| General circuits on Apple Silicon | `Metal` | Leverage JAX/Metal when available |
| General circuits (portable) | `Qiskit` | Robust CPU statevector/density matrix |

You can always override:

```python
simulate(qc, shots=1000, backend='mps')
```

And CLI:

```bash
ariadne simulate path/to/circuit.qasm --shots 1000
ariadne status --detailed
```

---

### Routing matrix (auto-generated)

![Routing matrix](docs/source/_static/routing_matrix.png)

Regenerate with:

```bash
python examples/routing_matrix.py --shots 256 --generate-image docs/source/_static/routing_matrix.png
```

---

## 🔌 Supported Backends & Integrations

The following backends are detected and routed to when available. Many are optional and only used if their dependencies are installed.

- Qiskit CPU simulator (`qiskit`) — always available baseline
- Stim stabilizer simulator (`stim`) — specialized for Clifford circuits
- Matrix Product State (`mps`) via `quimb`
- Tensor Network (`tensor_network`) via `cotengra`/`quimb`
- JAX Metal (`jax_metal`) — Apple Silicon acceleration when JAX/Metal is available
- CUDA (`cuda`) — GPU acceleration via `cupy`
- DDSIM (`ddsim`) — alternative simulator via `mqt.ddsim`
- Cirq (`cirq`) — via `src/ariadne/backends/cirq_backend.py`
- PennyLane (`pennylane`) — via `src/ariadne/backends/pennylane_backend.py`
- Qulacs (`qulacs`) — via `src/ariadne/backends/qulacs_backend.py`
- Experimental: PyQuil (`pyquil`), Braket (`braket`), Q# (`qsharp`), OpenCL (`opencl`)

Backends are implemented under `src/ariadne/backends/` and selected through the router in `src/ariadne/router.py` and the decision tree in `src/ariadne/route/routing_tree.py`.

---

## 🎯 The Ariadne Advantage: Intelligent Automation

Ariadne's core innovation is its comprehensive routing tree that analyzes circuit properties (size, gate types, entanglement patterns) and system capabilities (available backends, hardware acceleration) to automatically select the optimal execution environment. This eliminates the need for quantum developers to manually benchmark and select from 15+ different backends.

### Transparent Decision Making

Ariadne provides complete transparency into why a circuit was routed to a specific backend. You can inspect the entire decision path through the routing tree.

```python
from ariadne import explain_routing, show_routing_tree
from qiskit import QuantumCircuit

# Create a circuit
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

# Get a detailed, human-readable explanation of the routing decision
explanation = explain_routing(qc)
# explanation is a human-readable string describing the routing decision,
# e.g.:
# "Circuit routed to backend 'qiskit_simulator' because it has 2 qubits and no advanced gates."
print(explanation)

# You can also visualize the entire routing tree
print(show_routing_tree())
```

---

## 🚀 Getting Started

### Installation

**Typical install (PyPI):**
```bash
pip install ariadne-router
```

#### Developer or power-user setup

Clone the repository if you plan to contribute, run the examples from source, or enable hardware acceleration extras.

```bash
git clone https://github.com/Hmbown/ariadne.git
cd ariadne
pip install -e .
```

To enable optional hardware acceleration backends, install the extras that match your environment:

```bash
# Apple Silicon (M1/M2/M3/M4)
pip install -e .[apple]

# NVIDIA GPU (CUDA)
pip install -e .[cuda]

# All optional dependencies
pip install -e .[apple,cuda,viz]
```

📖 **For detailed installation instructions, including dependency notes, see the [Comprehensive Installation Guide](docs/comprehensive_installation.md)**

### Quickstart Demo

Run the complete quickstart example to see Ariadne in action:

```bash
python examples/quickstart.py
```

This demo showcases:
- Automatic backend selection for different circuit types
- Performance comparisons
- Routing decision transparency
- Hardware acceleration when available

---

### Quickstart GIF

![Quickstart Routing Demo](docs/source/_static/quickstart.gif)

Regenerate with:

```bash
python examples/generate_quickstart_gif.py --output docs/source/_static/quickstart.gif
```

---

## 🧠 Core API

- **`simulate`** – High-level helper that inspects a circuit, selects the best backend, and returns a `SimulationResult`.

  ```python
  from ariadne import simulate

  result = simulate(circuit, shots=1000)
  print(result.backend_used)
  print(result.execution_time)
  ```

- **`EnhancedQuantumRouter`** – Object-oriented interface for configuring routing policies and evaluating decisions programmatically.

  ```python
  from ariadne import EnhancedQuantumRouter

  router = EnhancedQuantumRouter()
  decision = router.select_optimal_backend(circuit)
  print(decision.recommended_backend)
  print(decision.confidence_score)
  ```

- **`ComprehensiveRoutingTree` / `explain_routing`** – Deterministic, auditable explanation tools for governance and debugging.

  ```python
from ariadne import ComprehensiveRoutingTree

tree = ComprehensiveRoutingTree()
decision = tree.route_circuit(circuit)
print(decision.recommended_backend)
print(decision.confidence_score)
  ```

Complementary helpers such as `get_config_manager()` and `configure_ariadne()` enable centrally managed policies, while the `ariadne` CLI mirrors these workflows for scripted environments.

---

## 📊 Performance

Ariadne emphasizes **capability extension** and **consistent execution**. Automated routing ensures that circuits land on the most suitable simulator, even when that involves specialized tooling such as Stim or tensor-network engines. Benchmarks focus on demonstrating routing correctness, fallbacks, and platform-specific acceleration rather than raw single-backend speed.

### Representative routing results

| Circuit | Selected backend | Router runtime (ms) | Direct Qiskit (ms) | Notes |
|---------|------------------|---------------------|--------------------|-------|
| `ghz_chain_10` | Stim | 17.9 | 1.47 | Router overhead exceeds direct Qiskit, but Stim unlocks scaling beyond 24 qubits. |
| `random_clifford_12` | Stim | 339 | 13.2 | Conversion cost dominates at moderate size; routing remains correct for stabilizer workloads. |
| `random_nonclifford_8` | Tensor network | 111 | 1.65 | Tensor contraction adds cost yet preserves accuracy for non-Clifford structure. |
| `qaoa_maxcut_8_p3` | Tensor network | 67.6 | 1.34 | Demonstrates automatic selection of tensor-network backend even without immediate speedup. |

### Platform-specific highlights

- **Apple Silicon** – JAX-Metal delivered 1.16×–1.51× speedups across sampled circuits, with minor regressions on a small subset when GPU transfer costs dominate.
- **CUDA** – Benchmarks executed without GPU hardware; CPU baselines are recorded for reference and CUDA routing falls back safely when accelerators are unavailable.
- **Operational insights** – Routing consistently selects specialized simulators for Clifford families, maintains deterministic fallbacks, and extends feasible circuit sizes beyond statevector limits.

Full benchmark outputs, reproducibility scripts, and raw JSON data are available under `benchmarks/results` for compliance reviews and custom analysis.

---

## 🔧 Usage Examples

### Automatic Detection of Specialized Circuits

Ariadne recognizes when circuits can benefit from specialized simulators like Stim.

```python
from ariadne import simulate
from qiskit import QuantumCircuit

# Large Clifford circuit that would crash plain Qiskit
qc = QuantumCircuit(40, 40)
qc.h(0)
for i in range(39):
    qc.cx(i, i + 1)  # Creates a 40-qubit GHZ state
qc.measure_all()

# Ariadne automatically routes to Stim for optimal performance
result = simulate(qc, shots=1000)
print(f"Backend used: {result.backend_used}")  # -> stim
```

### Advanced Routing Control

For users who need fine-grained control over the routing process:

```python
from ariadne import ComprehensiveRoutingTree, RoutingStrategy
from qiskit import QuantumCircuit

# Create a circuit
circuit = QuantumCircuit(2, 2)
circuit.h(0)
circuit.cx(0, 1)
circuit.measure_all()

# Initialize routing system
router = ComprehensiveRoutingTree()

# Use specific routing strategies
decision = router.route_circuit(
    circuit,
    strategy=RoutingStrategy.MEMORY_EFFICIENT
)

print(f"Selected: {decision.recommended_backend.value}")
print(f"Confidence: {decision.confidence_score:.2f}")
print(f"Expected speedup: {decision.expected_speedup:.1f}x")
```

Available routing strategies:
- `SPEED_FIRST` - Prioritize execution speed
- `ACCURACY_FIRST` - Favor accuracy/robustness when applicable
- `MEMORY_EFFICIENT` - Optimize for memory usage
- `CLIFFORD_OPTIMIZED` - Specialized for Clifford circuits
- `ENTANGLEMENT_AWARE` - Prefer TN/MPS paths for low entanglement
- `STABILIZER_FOCUSED` - Emphasize stabilizer-friendly paths
- `APPLE_SILICON_OPTIMIZED` - Hardware-aware for M-series chips
- `CUDA_OPTIMIZED` - GPU acceleration focused
- `CPU_OPTIMIZED` - Prefer portable CPU simulators
- `RESEARCH_MODE` - Exploration-oriented defaults
- `EDUCATION_MODE` - Deterministic, simplified defaults
- `PRODUCTION_MODE` - Conservative, reproducible defaults
- `AUTO_DETECT` - Intelligent analysis (default)
- `HYBRID_MULTI_BACKEND` - Adaptive, multi-path strategy


```

---

## 🛡️ Project Maturity

### Test Coverage
- **Unit Tests**: 38%+ coverage across core modules.
- **Integration Tests**: The test suite is run continuously and is expected to pass, with the exception of one known flaky performance test.
- **Backend Tests**: All major backends are tested.

### Documentation
- **Comprehensive Guides**: Installation, usage, and API documentation.
- **Examples Gallery**: 15+ working examples for different use cases.
- **Performance Reports**: Detailed benchmarking and validation.
- **API Reference**: Complete API documentation with examples.

### Development Infrastructure
- **CI/CD Pipeline**: Automated testing on Python 3.11-3.12.
- **Code Quality**: Ruff linting, mypy type checking, pre-commit hooks.
- **Security**: Bandit security scanning, dependency safety checks.
- **Release Management**: Automated versioning and changelog generation.

---

## 🤝 Contributing

We welcome contributions of all kinds, from bug fixes to new features. Please read our [**Contributing Guidelines**](docs/project/CONTRIBUTING.md) to get started.

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

📖 **For detailed development setup instructions, see the [Comprehensive Installation Guide](docs/comprehensive_installation.md#development-setup)**

---

## 💬 Community

- **GitHub Discussions:** [Ask questions and share ideas](https://github.com/Hmbown/ariadne/discussions)
- **Issue Tracker:** [Report bugs and request features](https://github.com/Hmbown/ariadne/issues)

---

## 📜 License

Ariadne is released under the [Apache 2.0 License](LICENSE).

### Policies

- [CHANGELOG](CHANGELOG.md)
- [SECURITY](SECURITY.md)
- [CODE OF CONDUCT](CODE_OF_CONDUCT.md)

---

## 🙏 Acknowledgments

Ariadne builds upon excellent open-source quantum computing frameworks:
- [Qiskit](https://qiskit.org/) for quantum circuit representation
- [Stim](https://github.com/quantumlib/Stim) for Clifford circuit simulation
- [Quimb](https://github.com/quimb/quimb) for tensor network operations
- [JAX](https://github.com/google/jax) for hardware acceleration

---
