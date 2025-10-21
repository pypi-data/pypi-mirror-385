# Comprehensive Ariadne Installation Guide

This guide provides detailed installation instructions for the Ariadne quantum routing library across different environments and use cases.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Package Naming](#package-naming)
3. [Installation Methods](#installation-methods)
4. [Platform-Specific Instructions](#platform-specific-instructions)
5. [Optional Dependencies](#optional-dependencies)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)
8. [Development Setup](#development-setup)
9. [Production Deployment](#production-deployment)
10. [Quick Reference](#quick-reference)

## System Requirements

### Minimum Requirements
- **Python**: 3.11 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 1GB free space
- **Operating System**:
  - macOS 12.0 (Monterey) or higher
  - Linux (Ubuntu 20.04+, CentOS 8+, or equivalent)
  - Windows 10/11

### Platform-Specific Requirements

#### macOS
- **Intel Mac**: macOS 12.0+ (standard installation)
- **Apple Silicon (M1/M2/M3/M4)**: macOS 13.0+ recommended for Metal acceleration
- **Xcode Command Line Tools**: Required for some dependencies
  ```bash
  xcode-select --install
  ```

#### Linux
- **Ubuntu/Debian**: Build tools and Python development headers
  ```bash
  sudo apt update
  sudo apt install -y python3-dev python3-pip build-essential
  ```
- **CentOS/RHEL**: Development tools
  ```bash
  sudo yum groupinstall -y "Development Tools"
  sudo yum install -y python3-devel python3-pip
  ```

#### Windows
- **Visual Studio Build Tools**: Required for some packages
- **Windows Subsystem for Linux (WSL2)**: Recommended for development
- **Python 3.11+**: From python.org or Microsoft Store

## Package Naming

**Important Note**: There is a difference between the package name for installation and the import name:

- **Installation package**: `ariadne-router` (used with pip)
- **Python import**: `ariadne` (used in Python code)

```bash
# Install the package
pip install ariadne-router

# Use in Python
import ariadne
```

This naming convention distinguishes the Ariadne quantum package from other potential "ariadne" packages on PyPI.

## Installation Methods

### Method 1: Install from Source (Recommended for Development)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Hmbown/ariadne.git
   cd ariadne
   ```

2. **Create a virtual environment** (highly recommended):
   ```bash
   python -m venv ariadne_env
   source ariadne_env/bin/activate  # On Windows: ariadne_env\Scripts\activate
   ```

3. **Install in development mode**:
   ```bash
   pip install -e .
   ```

### Method 2: Install from PyPI (Coming Soon)

Once published to PyPI:
```bash
pip install ariadne-router
```

### Method 3: Install with Optional Dependencies

For specific hardware acceleration or features:

```bash
# Basic installation
pip install ariadne-router

# With Apple Silicon acceleration
pip install ariadne-router[apple]

# With CUDA acceleration
pip install ariadne-router[cuda]

# With visualization tools
pip install ariadne-router[viz]

# With all optional dependencies
pip install ariadne-router[apple,cuda,viz]
```

## Platform-Specific Instructions

### macOS Installation

#### Apple Silicon (M1/M2/M3/M4)

For optimal performance on Apple Silicon:

1. **Install with Metal acceleration**:
   ```bash
   pip install -e .[apple]
   ```

2. **Verify Metal availability**:
   ```python
   import jax
   print(f"Available devices: {jax.devices()}")

   # Check Metal backend
   from ariadne.backends.metal_backend import MetalBackend
   backend = MetalBackend()
   print(f"Metal backend available: {backend.is_available()}")
   ```

3. **Memory configuration** (optional):
   ```bash
   # Set memory limits for large circuits
   export ARIADNE_MEMORY_LIMIT_GB=24
   export OMP_NUM_THREADS=8
   ```

#### Intel Mac

Standard installation without hardware acceleration:
```bash
pip install -e .
```

### Linux Installation

#### Standard Installation

```bash
# Install system dependencies
sudo apt update
sudo apt install -y python3-dev python3-pip build-essential

# Install Ariadne
pip install -e .
```

#### CUDA Support (NVIDIA GPUs)

1. **Verify CUDA installation**:
   ```bash
   nvidia-smi
   nvcc --version
   ```

2. **Install with CUDA support**:
   ```bash
   pip install -e .[cuda]
   ```

3. **Set CUDA environment variables**:
   ```bash
   export CUDA_PATH=/usr/local/cuda
   export LD_LIBRARY_PATH=$CUDA_PATH/lib64:$LD_LIBRARY_PATH
   ```

4. **Verify CUDA backend**:
   ```python
   from ariadne.backends.cuda_backend import CUDABackend
   backend = CUDABackend()
   if backend.is_available():
       print(f"CUDA backend available: {backend.get_device_info()}")
   ```

### Windows Installation

#### Native Windows

1. **Install Visual Studio Build Tools** (if not already installed)

2. **Install Ariadne**:
   ```powershell
   pip install -e .
   ```

#### Windows Subsystem for Linux (WSL2)

1. **Install WSL2**:
   ```powershell
   wsl --install
   ```

2. **In WSL2 environment**:
   ```bash
   # Update system
   sudo apt update
   sudo apt install -y python3-dev python3-pip build-essential

   # Install Ariadne
   pip install -e .

   # For CUDA support in WSL2
   pip install -e .[cuda]
   ```

## Optional Dependencies

### Apple Silicon Acceleration

For M-series Mac optimization:

```bash
pip install -e .[apple]
```

This installs:
- `jax` and `jaxlib` for Apple Silicon
- `jax-metal` for Metal acceleration

**Compatibility**:
- macOS 13.0+ (Ventura) recommended
- M1/M2/M3/M4 chips
- Python 3.11+

### NVIDIA GPU Acceleration

For CUDA-enabled systems:

```bash
pip install -e .[cuda]
```

This installs:
- `cupy-cuda12x` for CUDA 12.x support

**Compatibility**:
- CUDA 11.x or 12.x
- NVIDIA GPU with compute capability 3.5+
- Linux or Windows (WSL2)

### Visualization Capabilities

For enhanced plotting and visualization:

```bash
pip install -e .[viz]
```

This installs:
- `matplotlib`, `seaborn`, `plotly` for visualization

### Development Tools

For contributing to Ariadne:

```bash
pip install -e .[dev]
```

This installs:
- Testing frameworks (`pytest`, `pytest-cov`)
- Code quality tools (`black`, `isort`, `ruff`, `mypy`)
- Security scanning (`bandit`, `safety`)

## Verification

After installation, verify Ariadne is working correctly:

### Basic Verification

```python
from ariadne import simulate
from qiskit import QuantumCircuit

# Create a simple circuit
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

# Test simulation
result = simulate(qc, shots=100)
print(f"Success! Backend used: {result.backend_used}")
print(f"Execution time: {result.execution_time:.4f}s")
```

### Backend Availability Check

```python
from ariadne.router import QuantumRouter

router = QuantumRouter()
available_backends = router.list_available_backends()
print(f"Available backends: {available_backends}")

# Check specific backends
for backend_name in available_backends:
    backend = router.get_backend(backend_name)
    print(f"{backend_name}: {backend.get_info()}")
```

### Performance Test

```python
import time
from ariadne import simulate
from qiskit import QuantumCircuit

# Test with a medium-sized circuit
qc = QuantumCircuit(10)
qc.h(range(10))
qc.measure_all()

start_time = time.time()
result = simulate(qc, shots=1000)
end_time = time.time()

print(f"Execution time: {end_time - start_time:.4f}s")
print(f"Backend: {result.backend_used}")
print(f"Memory usage: {result.memory_usage:.2f}MB")
```

## Troubleshooting

### Common Installation Issues

#### Python Version Issues

**Problem**: `Python version 3.11 or higher is required`

**Solution**:
```bash
# Check Python version
python --version

# Install Python 3.11+ using pyenv (recommended)
curl https://pyenv.run | bash
pyenv install 3.11.0
pyenv global 3.11.0

# Or use conda
conda create -n ariadne python=3.11
conda activate ariadne
```

#### Dependency Conflicts

**Problem**: `Conflict found when installing dependencies`

**Solution**:
```bash
# Create a clean virtual environment
python -m venv ariadne_clean
source ariadne_clean/bin/activate  # Windows: ariadne_clean\Scripts\activate

# Install with minimal dependencies first
pip install -e .

# Then add optional dependencies one by one
pip install -e .[apple]  # or [cuda], [viz], etc.
```

#### CUDA Installation Issues

**Problem**: `Could not find CUDA toolkit` or `cupy installation fails`

**Solution**:
1. **Verify CUDA installation**:
   ```bash
   nvidia-smi  # Should show GPU information
   nvcc --version  # Should show CUDA compiler version
   ```

2. **Install correct CuPy version**:
   ```bash
   # Match CuPy version to your CUDA version
   pip install cupy-cuda12x  # For CUDA 12.x
   pip install cupy-cuda11x  # For CUDA 11.x
   ```

3. **Set environment variables**:
   ```bash
   export CUDA_PATH=/usr/local/cuda
   export LD_LIBRARY_PATH=$CUDA_PATH/lib64:$LD_LIBRARY_PATH
   ```

#### Apple Silicon Issues

**Problem**: `Metal backend not available` or `JAX Metal installation fails`

**Solution**:
1. **Verify Apple Silicon**:
   ```bash
   uname -m  # Should return 'arm64'
   ```

2. **Install with Apple extras**:
   ```bash
   pip install -e .[apple]
   ```

3. **Check Metal compatibility**:
   ```python
   import jax
   devices = jax.devices()
   print(f"Available devices: {devices}")
   ```

### Runtime Issues

#### Backend Selection Problems

**Problem**: `No suitable backend found for circuit`

**Solutions**:
```python
from ariadne import analyze_circuit

# Analyze why backend selection fails
analysis = analyze_circuit(your_circuit)
print(f"Analysis: {analysis}")
print(f"Available backends: {analysis.available_backends}")

# Force specific backend
from ariadne import QuantumRouter
router = QuantumRouter()
result = router.simulate(your_circuit, backend="qiskit")  # Force fallback
```

#### Memory Errors

**Problem**: `MemoryError` or `Killed` during simulation

**Solutions**:
1. **Reduce circuit size**:
   ```python
   # Use fewer qubits
   qc = QuantumCircuit(20)  # Instead of 30+
   ```

2. **Use specialized backends**:
   ```python
   # For Clifford circuits, use Stim
   from ariadne.backends.stim_backend import StimBackend
   backend = StimBackend()
   result = backend.simulate(clifford_circuit, shots=1000)

   # For low-entanglement circuits, use MPS
   from ariadne.backends.mps_backend import MPSBackend
   backend = MPSBackend()
   result = backend.simulate(low_entanglement_circuit, shots=1000)
   ```

3. **Increase system limits** (Linux/macOS):
   ```bash
   ulimit -s unlimited
   ulimit -v unlimited
   ```

## Development Setup

For contributors to Ariadne:

1. **Clone and install with development dependencies**:
   ```bash
   git clone https://github.com/Hmbown/ariadne.git
   cd ariadne
   pip install -e .[dev]
   ```

2. **Set up pre-commit hooks**:
   ```bash
   pre-commit install
   ```

3. **Run tests**:
   ```bash
   # Run all tests
   pytest

   # Run specific test categories
   pytest -m unit
   pytest -m integration
   pytest -m benchmark
   ```

4. **Code formatting and linting**:
   ```bash
   # Format code
   black src/ tests/
   isort src/ tests/

   # Lint code
   ruff check src/ tests/
   mypy src/
   ```

## Production Deployment

For production environments:

### Docker Deployment

1. **Using Docker Compose**:
   ```bash
   # Build and run with Docker Compose
   docker-compose up -d

   # Access the container
   docker-compose exec ariadne bash
   ```

2. **Using Docker Directly**:
   ```bash
   # Build the image
   docker build -t ariadne .

   # Run the container
   docker run -it ariadne python -c "from ariadne import simulate; print('Ariadne ready!')"
   ```

### Performance Optimization

1. **Environment variables**:
   ```bash
   # Set backend preference
   export ARIADNE_BACKEND_PREFERENCE="stim,tensor_network,qiskit"

   # Memory limits
   export ARIADNE_MEMORY_LIMIT_MB=4096

   # Logging level
   export ARIADNE_LOG_LEVEL="WARNING"  # For production
   ```

2. **Resource management**:
   ```python
   from ariadne import configure_ariadne

   # Configure for production
   config = {
       "log_level": "WARNING",
       "memory_limit_mb": 4096,
       "backend_preference": ["stim", "tensor_network", "qiskit"],
       "enable_caching": True
   }

   configure_ariadne(config)
   ```

## Quick Reference

### Basic Installation

```bash
# Standard installation
git clone https://github.com/Hmbown/ariadne.git
cd ariadne
pip install -e .

# With Apple Silicon support
pip install -e .[apple]

# With CUDA support
pip install -e .[cuda]

# With visualization
pip install -e .[viz]

# Development setup
pip install -e .[dev]
```

### Verification Commands

```python
# Basic test
from ariadne import simulate
from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()
result = simulate(qc, shots=100)
print(f"Backend: {result.backend_used}")

# Check available backends
from ariadne.router import QuantumRouter
router = QuantumRouter()
print(router.list_available_backends())
```

### Common Environment Variables

```bash
# Memory limits (Apple Silicon)
export ARIADNE_MEMORY_LIMIT_GB=24

# Thread limits
export OMP_NUM_THREADS=8
export VECLIB_MAXIMUM_THREADS=8

# CUDA path
export CUDA_PATH=/usr/local/cuda
export LD_LIBRARY_PATH=$CUDA_PATH/lib64:$LD_LIBRARY_PATH

# Backend preference
export ARIADNE_BACKEND_PREFERENCE="stim,tensor_network,qiskit"
```

---

*Installation complete? Continue to the [Quick Start Guide](quickstart.md) to run your first quantum circuit!*
