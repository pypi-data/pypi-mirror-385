# Examples Gallery

This page lists runnable examples included in the repository. Activate your virtualenv first.

- **Bell/GHZ/Clifford routing**
  - File: `examples/quickstart.py`
  - Run:
```bash
python examples/quickstart.py
```
  - Shows: automatic routing to `stim` for Clifford, `MPS` for low entanglement, and fallback/force examples.

- **Custom inline example**
  - Snippet:
```python
from ariadne import simulate
from qiskit import QuantumCircuit
qc = QuantumCircuit(2, 2)
qc.h(0); qc.cx(0,1); qc.measure_all()
res = simulate(qc, shots=256)
print(res.backend_used, list(res.counts.items())[:3])
```

- **CLI simulation**
  - Run:
```bash
ariadne simulate path/to/circuit.qasm --shots 1000
```
  - Tip: use `ariadne status --detailed` to see available backends.
