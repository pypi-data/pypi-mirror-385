# Advanced Routing Options

Ariadne exposes simple knobs to influence routing when you need to bias for speed, precision, or noise modeling.

## SimulationOptions (Python)

`ariadne.simulation.SimulationOptions` adds these fields:

- `precision`: `"default" | "high"`
  - `"high"` hints the router to prefer higher-precision paths (e.g., DDSIM when available).
- `noise_model`: optional (any)
  - If provided, hints the router to prefer backends that support noise modeling.
- `budget_ms`: optional integer
  - A soft time-budget hint. Tight budgets (<100 ms) slightly bias toward faster approximate engines.

Example:

```python
from ariadne.simulation import QuantumSimulator, SimulationOptions
from qiskit import QuantumCircuit

qc = QuantumCircuit(5, 5)
qc.h(0); qc.t(0); qc.cx(0,1); qc.t(1); qc.measure_all()

sim = QuantumSimulator()
res = sim.simulate(qc, SimulationOptions(precision="high", budget_ms=50))
print(res.backend_used)
```

## CLI (environment variables)

You can also influence routing via environment variables for ad-hoc runs:

- `ARIADNE_ROUTING_BUDGET_MS`
  - Example: `export ARIADNE_ROUTING_BUDGET_MS=50`
- `ARIADNE_ROUTING_PREFER_DDSIM=1`
  - Set when you want to prefer DDSIM (if installed) for higher precision/noise workflows.

These are soft hints; routing still performs safety checks and graceful fallbacks.
