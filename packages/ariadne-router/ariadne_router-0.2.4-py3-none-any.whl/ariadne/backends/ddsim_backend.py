from __future__ import annotations

from qiskit import QuantumCircuit


class DDSIMBackend:
    """Thin wrapper around MQT DDSIM provider to unify the backend interface."""

    def __init__(self) -> None:
        try:
            import mqt.ddsim as ddsim  # noqa: F401
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("MQT DDSIM not installed") from exc

    def simulate(self, circuit: QuantumCircuit, shots: int) -> dict[str, int]:
        import mqt.ddsim as ddsim

        provider = ddsim.DDSIMProvider()
        backend = provider.get_backend("qasm_simulator")
        job = backend.run(circuit, shots=shots)
        counts = job.result().get_counts()
        return {str(key): value for key, value in counts.items()}
