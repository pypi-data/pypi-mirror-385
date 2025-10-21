from __future__ import annotations

import warnings
from typing import Any

from qiskit import QuantumCircuit


class QSharpBackend:
    """Skeleton Q# backend adapter.

    Attempts to use Q# Python interoperability if available; otherwise falls back to Qiskit.
    """

    def __init__(self) -> None:  # noqa: D401
        pass

    def simulate(self, circuit: QuantumCircuit, shots: int = 1000) -> dict[str, int]:
        try:
            import qsharp  # noqa: F401

            # Real Qiskit -> Q# conversion not implemented yet.
            raise NotImplementedError("Qiskit->Q# conversion not implemented")
        except Exception as exc:
            warnings.warn(f"Q# simulation unavailable ({exc}), falling back to Qiskit", stacklevel=2)
            return self._simulate_with_qiskit(circuit, shots)

    def _simulate_with_qiskit(self, circuit: QuantumCircuit, shots: int) -> dict[str, int]:
        try:
            from qiskit.providers.basic_provider import BasicProvider

            provider = BasicProvider()
            backend = provider.get_backend("basic_simulator")
            job = backend.run(circuit, shots=shots)
            counts = job.result().get_counts()
            return {str(k): v for k, v in counts.items()}
        except Exception as exc:
            raise RuntimeError(f"Qiskit fallback failed: {exc}") from exc

    def get_backend_info(self) -> dict[str, Any]:
        return {"name": "qsharp"}
