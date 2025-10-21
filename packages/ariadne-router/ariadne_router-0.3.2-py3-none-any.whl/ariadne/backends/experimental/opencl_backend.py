from __future__ import annotations

import warnings
from typing import Any

from qiskit import QuantumCircuit


class OpenCLBackend:
    """Skeleton OpenCL backend adapter.

    Attempts to use pyopencl; currently falls back to Qiskit until kernels are implemented.
    """

    def __init__(self) -> None:  # noqa: D401
        pass

    def simulate(self, circuit: QuantumCircuit, shots: int = 1000) -> dict[str, int]:
        try:
            import pyopencl  # type: ignore  # noqa: F401

            # Not implemented yet: statevector kernels via OpenCL
            raise NotImplementedError("OpenCL kernels not implemented")
        except Exception as exc:
            warnings.warn(f"OpenCL simulation unavailable ({exc}), falling back to Qiskit", stacklevel=2)
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
        return {"name": "opencl"}
