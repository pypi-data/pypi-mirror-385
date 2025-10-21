# Ariadne Installation Guide

Comprehensive installation instructions for Ariadne on all supported platforms and configurations.

## System Requirements

### Minimum Requirements
- **Python**: 3.11 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 1GB free space

### Platform-Specific Requirements

#### macOS
- **Minimum**: macOS 12.0 (Monterey) or higher
- **Recommended**: macOS 13.0 (Ventura) or higher for Apple Silicon optimization
- **Apple Silicon**: M1, M2, M3, or M4 series for Metal acceleration

#### Linux
- **Ubuntu**: 20.04 LTS or higher
- **CentOS**: 8 or higher
- **Other**: Most modern distributions with Python 3.11+

#### Windows
- **Windows**: 10 or 11
- **WSL**: Windows Subsystem for Linux 2 recommended for development

## Installation Methods

### Method 1: Install from Source (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Hmbown/ariadne.git
   cd ariadne
   ```

2. **Create a virtual environment (recommended)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
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

## Optional Dependencies

### Apple Silicon Acceleration
For M-series Mac optimization:
```bash
pip install -e .[apple]
```

This installs:
- `jax` and `jaxlib` for Apple Silicon
- `jax-metal` for Metal acceleration

### NVIDIA GPU Acceleration
For CUDA-enabled systems:
```bash
pip install -e .[cuda]
```

This installs:
- `cupy-cuda12x` for CUDA support

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

### Documentation Building
For building documentation locally:
```bash
pip install -e .[docs]
```

This installs:
- `sphinx`, `sphinx-rtd-theme`, `myst-parser`

## Platform-Specific Installation

### macOS Installation

#### Apple Silicon (M1/M2/M3/M4)
```bash
# Install with Metal acceleration
pip install -e .[apple]

# Verify Metal backend availability
python -c "from ariadne.backends.metal_backend import MetalBackend; print('Metal backend available')"
```

#### Intel Mac
```bash
# Standard installation
pip install -e .
```

### Linux Installation

#### Ubuntu/Debian
```bash
# Update package list
sudo apt update

# Install system dependencies (if needed)
sudo apt install -y python3-dev python3-pip build-essential

# Install Ariadne
pip install -e .
```

#### CUDA Support on Linux
```bash
# Ensure CUDA toolkit is installed
nvidia-smi  # Verify GPU availability

# Install with CUDA support
pip install -e .[cuda]
```

### Windows Installation

#### Native Windows
```bash
# Install using PowerShell or Command Prompt
pip install -e .
```

#### Windows Subsystem for Linux (WSL2)
```bash
# In WSL2 environment
pip install -e .

# For CUDA support in WSL2
pip install -e .[cuda]
```

## Docker Installation

### Using Docker Compose
```bash
# Build and run with Docker Compose
docker-compose up -d

# Access the container
docker-compose exec ariadne bash
```

### Using Docker Directly
```bash
# Build the image
docker build -t ariadne .

# Run the container
docker run -it ariadne python -c "from ariadne import simulate; print('Ariadne ready!')"
```

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
```

### Backend Availability Check
```python
from ariadne.router import QuantumRouter

router = QuantumRouter()
available_backends = router.list_available_backends()
print(f"Available backends: {available_backends}")
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
```

## Troubleshooting Installation

### Common Issues

#### Python Version Issues
**Problem**: Python version too old
**Solution**: Upgrade to Python 3.11+
```bash
# Check Python version
python --version

# Install Python 3.11 (using pyenv)
pyenv install 3.11.0
pyenv global 3.11.0
```

#### Dependency Conflicts
**Problem**: Package conflicts during installation
**Solution**: Use a clean virtual environment
```bash
# Create fresh virtual environment
python -m venv ariadne_env
source ariadne_env/bin/activate
pip install -e .
```

#### CUDA Installation Issues
**Problem**: CUDA dependencies fail to install
**Solution**: Install CUDA toolkit first, then use compatible versions
```bash
# Install CUDA toolkit from NVIDIA
# Then install with specific CUDA version
pip install cupy-cuda12x
```

#### Apple Silicon Issues
**Problem**: Metal backend not available
**Solution**: Ensure you're on Apple Silicon and using correct Python
```bash
# Check architecture
uname -m  # Should return 'arm64'

# Reinstall with Apple extras
pip install -e .[apple]
```

### Getting Help

If you encounter installation issues:

1. **Check our [Troubleshooting Guide](troubleshooting.md)**
2. **Search [GitHub Issues](https://github.com/Hmbown/ariadne/issues)**
3. **Ask in [GitHub Discussions](https://github.com/Hmbown/ariadne/discussions)**
4. **Verify system requirements match your environment**

## Next Steps

After successful installation:

- Follow the [Quick Start Guide](quickstart.md) for your first simulation
- Explore the [Examples Gallery](../examples/README.md) for use cases
- Read the [Performance Guide](PERFORMANCE_GUIDE.md) for optimization tips

---

*Installation complete? Continue to the [Quick Start Guide](quickstart.md) to run your first quantum circuit!*
