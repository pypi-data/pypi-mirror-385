# Ariadne Installation Summary

Quick installation commands for common use cases.

## Package Naming Note
- **Install with**: `pip install ariadne-router`
- **Import in Python**: `import ariadne`

## Quick Install

### Basic Installation
```bash
git clone https://github.com/Hmbown/ariadne.git
cd ariadne
pip install -e .
```

### With Hardware Acceleration
```bash
# Apple Silicon (M1/M2/M3/M4)
pip install -e .[apple]

# NVIDIA GPU (CUDA)
pip install -e .[cuda]

# Visualization tools
pip install -e .[viz]

# All optional dependencies
pip install -e .[apple,cuda,viz]
```

### Development Setup
```bash
git clone https://github.com/Hmbown/ariadne.git
cd ariadne
pip install -e .[dev]
pre-commit install
```

## Platform-Specific

### macOS
```bash
# Apple Silicon
pip install -e .[apple]

# Intel Mac
pip install -e .
```

### Linux
```bash
# System dependencies
sudo apt install -y python3-dev python3-pip build-essential

# Standard installation
pip install -e .

# With CUDA (verify with: nvidia-smi)
pip install -e .[cuda]
```

### Windows
```bash
# Native Windows
pip install -e .

# WSL2 (recommended)
wsl --install
# Then in WSL2:
sudo apt install -y python3-dev python3-pip build-essential
pip install -e .
```

## Docker
```bash
# Using Docker Compose
docker-compose up -d

# Direct Docker
docker build -t ariadne .
docker run -it ariadne
```

## Verification
```python
from ariadne import simulate
from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

result = simulate(qc, shots=100)
print(f"Backend used: {result.backend_used}")
```

## Common Issues

| Problem | Solution |
|---------|----------|
| Python version too old | Upgrade to Python 3.11+ |
| CUDA not found | Install CUDA toolkit first |
| Metal backend unavailable | Verify Apple Silicon and use `[apple]` extras |
| Memory errors | Reduce circuit size or use specialized backends |

## Environment Variables
```bash
# Memory limits (Apple Silicon)
export ARIADNE_MEMORY_LIMIT_GB=24

# Thread limits
export OMP_NUM_THREADS=8

# CUDA path
export CUDA_PATH=/usr/local/cuda

# Backend preference
export ARIADNE_BACKEND_PREFERENCE="stim,tensor_network,qiskit"
```

---

*For detailed instructions, see [Comprehensive Installation Guide](comprehensive_installation.md)*
