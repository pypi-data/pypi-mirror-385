# Routing Rules

Ariadne selects a backend based on circuit structure and your system context, then falls back if needed.

- Pure Clifford circuits (e.g., GHZ, stabilizers)
  - Backend: `stim`
  - Rationale: specialized and extremely fast for stabilizer circuits.

- Low-entanglement, shallow circuits
  - Backend: `MPS`
  - Rationale: efficient tensor-network representation.

- General circuits on Apple Silicon
  - Backend: `Metal` (when available)
  - Rationale: leverage Apple GPU via JAX/Metal.

- General circuits (portable)
  - Backend: `Qiskit`
  - Rationale: robust CPU statevector/density matrix.

You can always override with `backend='...'` and Ariadne will still fall back if the forced backend is unavailable.

## Reproducible examples

- Clifford → Stim
```python
from ariadne import simulate
from qiskit import QuantumCircuit
qc = QuantumCircuit(2, 2)
qc.h(0); qc.cx(0,1); qc.measure_all()
res = simulate(qc, shots=256)
print('Expected: STIM | Got:', res.backend_used)
```

- Low entanglement → MPS
```python
from ariadne import simulate
from qiskit import QuantumCircuit
qc = QuantumCircuit(8, 8)
qc.h(0); qc.cx(0,1); qc.cx(2,3); qc.cx(4,5); qc.cx(6,7); qc.measure_all()
res = simulate(qc, shots=512)
print('Expected: MPS | Got:', res.backend_used)
```

- General non-Clifford → Qiskit or Metal
```python
from ariadne import simulate
from qiskit import QuantumCircuit
qc = QuantumCircuit(5, 5)
qc.h(0); qc.t(0); qc.cx(0,1); qc.t(1); qc.measure_all()
res = simulate(qc, shots=256)
print('Expected: QISKIT or METAL | Got:', res.backend_used)
```

- Force backend and observe fallback
```python
from ariadne import simulate
from qiskit import QuantumCircuit
qc = QuantumCircuit(2,2); qc.h(0); qc.cx(0,1); qc.measure_all()
print('Force qiskit →', simulate(qc, shots=100, backend='qiskit').backend_used)
print('Force cuda (no CUDA) should fallback →', simulate(qc, shots=100, backend='cuda').backend_used)
```

## Where to look in code

- Router logic: `src/ariadne/router.py`
- Circuit analysis helpers: `src/ariadne/route/analyze.py`, `src/ariadne/route/mps_analyzer.py`
- Backends: `src/ariadne/backends/`
