# Ariadne Troubleshooting Guide

Common issues, error messages, and solutions for using Ariadne Quantum Framework.

## Quick Problem Reference

| Problem | Likely Cause | Quick Fix |
|---------|--------------|-----------|
| Import errors | Missing dependencies | `pip install -e .[dev]` |
| Backend not found | Hardware unavailable | Check backend requirements |
| Simulation fails | Circuit too large | Reduce qubit count or shots |
| Performance issues | Suboptimal routing | Use `analyze_circuit()` first |
| Memory errors | Insufficient RAM | Use smaller circuits or specialized backends |

## Installation Issues

### Python Version Problems

**Error**: `Python version 3.11 or higher is required`

**Solution**:
```bash
# Check current Python version
python --version

# Install Python 3.11+ using pyenv (recommended)
pyenv install 3.11.0
pyenv global 3.11.0

# Or use conda
conda create -n ariadne python=3.11
conda activate ariadne
```

### Dependency Conflicts

**Error**: `Conflict found when installing dependencies`

**Solution**:
```bash
# Create a clean virtual environment
python -m venv ariadne_clean
source ariadne_clean/bin/activate  # Windows: ariadne_clean\Scripts\activate

# Install with minimal dependencies first
pip install -e .
```

### CUDA Installation Issues

**Error**: `Could not find CUDA toolkit` or `cupy installation fails`

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
   export CUDA_PATH=/usr/local/cuda  # Adjust path as needed
   export LD_LIBRARY_PATH=$CUDA_PATH/lib64:$LD_LIBRARY_PATH
   ```

### Apple Silicon Issues

**Error**: `Metal backend not available` or `JAX Metal installation fails`

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
   import metal
   print("Metal is available")  # Should not raise error
   ```

## Runtime Issues

### Backend Selection Problems

**Error**: `No suitable backend found for circuit`

**Causes**:
- Circuit too large for available backends
- Missing specialized backend dependencies
- Hardware requirements not met

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

### Memory Errors

**Error**: `MemoryError` or `Killed` during simulation

**Causes**:
- Circuit too large for state vector simulation
- Insufficient system RAM
- Memory leak in backend

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
   # Increase memory limits
   ulimit -s unlimited
   ulimit -v unlimited
   ```

### Performance Issues

**Problem**: Slow simulation compared to direct backend usage

**Causes**:
- Router overhead for small circuits
- Suboptimal backend selection
- Circuit analysis taking significant time

**Solutions**:
```python
import time
from ariadne import simulate, analyze_circuit

# Measure routing overhead
qc = your_circuit

start = time.time()
result = simulate(qc, shots=1000)
end = time.time()
print(f"Total time: {end - start:.4f}s")

# Compare with direct backend usage
from ariadne.backends.stim_backend import StimBackend
backend = StimBackend()
start = time.time()
result = backend.simulate(qc, shots=1000)
end = time.time()
print(f"Direct backend time: {end - start:.4f}s")

# For small circuits, consider direct backend usage
if qc.num_qubits < 10:
    # Use direct backend for known circuit types
    pass
```

## Backend-Specific Issues

### Stim Backend Issues

**Error**: `Stim simulation failed` or `Clifford detection incorrect`

**Solutions**:
```python
from ariadne.backends.stim_backend import StimBackend

# Verify circuit is Clifford
backend = StimBackend()
if backend.supports_circuit(your_circuit):
    result = backend.simulate(your_circuit, shots=1000)
else:
    print("Circuit contains non-Clifford gates")

# Manual Clifford verification
from ariadne.route.context_detection import is_clifford_circuit
if is_clifford_circuit(your_circuit):
    print("Circuit should be routed to Stim")
```

### Metal Backend Issues

**Error**: `Metal device not found` or `JAX Metal kernel failed`

**Solutions**:
1. **Verify Metal availability**:
   ```python
   import jax
   devices = jax.devices()
   print(f"Available devices: {devices}")
   ```

2. **Check memory limits**:
   ```python
   # Metal has memory constraints on Apple Silicon
   # Reduce circuit size or use CPU fallback
   from ariadne import QuantumRouter
   router = QuantumRouter()
   result = router.simulate(smaller_circuit, shots=1000)
   ```

### CUDA Backend Issues

**Error**: `CUDA out of memory` or `Kernel launch failed`

**Solutions**:
1. **Monitor GPU memory**:
   ```bash
   watch -n 1 nvidia-smi
   ```

2. **Reduce memory usage**:
   ```python
   # Use fewer qubits or shots
   result = simulate(qc, shots=100)  # Reduce shots

   # Or use CPU fallback
   result = simulate(qc, backend="qiskit")
   ```

3. **Clear GPU cache**:
   ```python
   import cupy as cp
   cp.get_default_memory_pool().free_all_blocks()
   ```

## Common Error Messages

### "ModuleNotFoundError: No module named 'ariadne'"

**Solution**:
```bash
# Ensure you're in the correct directory
cd /path/to/ariadne

# Install in development mode
pip install -e .

# Check installation
python -c "import ariadne; print('Ariadne imported successfully')"
```

### "Backend 'xxx' not available"

**Solution**:
```python
from ariadne.router import QuantumRouter

router = QuantumRouter()
available = router.list_available_backends()
print(f"Available backends: {available}")

# Use available backend
if available:
    result = router.simulate(qc, backend=available[0])
```

### "Circuit too large for simulation"

**Solution**:
```python
# Reduce circuit complexity
qc = QuantumCircuit(20)  # Instead of 30+

# Use specialized backend
from ariadne.backends.mps_backend import MPSBackend
backend = MPSBackend()
if backend.supports_circuit(qc):
    result = backend.simulate(qc, shots=1000)
```

### "Timeout during circuit analysis"

**Solution**:
```python
# Set timeout for analysis
from ariadne import QuantumRouter

router = QuantumRouter()
router.analysis_timeout = 30  # 30 seconds
result = router.simulate(qc, shots=1000)
```

## Performance Optimization

### For Large Circuits
```python
# Use MPS backend for low-entanglement circuits
from ariadne.backends.mps_backend import MPSBackend
backend = MPSBackend()

# Use Stim for Clifford circuits
from ariadne.backends.stim_backend import StimBackend
backend = StimBackend()

# Batch small circuits
results = []
for circuit in circuit_batch:
    result = simulate(circuit, shots=100)
    results.append(result)
```

### For Small Circuits
```python
# Use direct backend to avoid routing overhead
from ariadne.backends.qiskit_backend import QiskitBackend
backend = QiskitBackend()
result = backend.simulate(qc, shots=1000)
```

## Debugging Tools

### Enable Debug Logging
```python
import logging

# Enable Ariadne debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('ariadne')
```

### Circuit Analysis Debugging
```python
from ariadne import analyze_circuit
from ariadne.visualization import plot_circuit_analysis

analysis = analyze_circuit(your_circuit)
print(f"Circuit analysis: {analysis}")

# Visualize routing decision
plot_circuit_analysis(analysis)
```

### Backend Performance Profiling
```python
import cProfile
from ariadne import simulate

# Profile simulation
profiler = cProfile.Profile()
profiler.enable()
result = simulate(your_circuit, shots=1000)
profiler.disable()
profiler.print_stats(sort='time')
```

## Getting Help

If you can't resolve an issue:

1. **Check existing issues**: [GitHub Issues](https://github.com/Hmbown/ariadne/issues)
2. **Search discussions**: [GitHub Discussions](https://github.com/Hmbown/ariadne/discussions)
3. **Create minimal reproducible example**:
   ```python
   # Include this in bug reports
   import ariadne
   from qiskit import QuantumCircuit

   qc = QuantumCircuit(2)
   qc.h(0)
   qc.cx(0, 1)
   qc.measure_all()

   # This fails with error...
   result = ariadne.simulate(qc, shots=100)
   ```

4. **Include system information**:
   ```python
   import platform
   import ariadne

   print(f"Python: {platform.python_version()}")
   print(f"OS: {platform.system()} {platform.release()}")
   print(f"Ariadne: {ariadne.__version__}")
   ```

## Emergency Fallbacks

If Ariadne consistently fails:

```python
# Direct Qiskit fallback
from qiskit import Aer, transpile
from qiskit import QuantumCircuit

qc = QuantumCircuit(5)
# ... build circuit

backend = Aer.get_backend('qasm_simulator')
transpiled = transpile(qc, backend)
job = backend.run(transpiled, shots=1000)
result = job.result()
```

---

*Still having issues? Check our [GitHub Issues](https://github.com/Hmbown/ariadne/issues) or create a new discussion with your problem details.*
