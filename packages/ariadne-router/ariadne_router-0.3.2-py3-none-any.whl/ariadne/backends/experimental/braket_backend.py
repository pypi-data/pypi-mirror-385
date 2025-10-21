from __future__ import annotations

import warnings
from typing import Any

import numpy as np
from qiskit import QuantumCircuit


class BraketBackend:
    """AWS Braket backend adapter with local simulator path.

    Uses Braket local simulator when SDK is available; otherwise falls back to Qiskit.
    """

    def __init__(self, device: str | None = None) -> None:
        # Default to local simulator; Braket handles the device selection internally
        self.device = device or "local:default"

    def simulate(self, circuit: QuantumCircuit, shots: int = 1000) -> dict[str, int]:
        try:
            from braket.circuits import Circuit as BraketCircuit  # type: ignore
            from braket.devices import LocalSimulator  # type: ignore

            bc = BraketCircuit()

            # Map Qiskit instructions to Braket circuit (subset)
            for item in circuit.data:
                op = getattr(item, "operation", item[0])
                qargs = list(getattr(item, "qubits", item[1]))
                name = getattr(op, "name", "")

                if name in {"measure", "barrier", "delay", "reset"}:
                    continue

                if op.num_qubits == 1:
                    q = circuit.find_bit(qargs[0]).index
                    if name == "h":
                        bc.h(q)
                    elif name == "x":
                        bc.x(q)
                    elif name == "y":
                        bc.y(q)
                    elif name == "z":
                        bc.z(q)
                    elif name == "s":
                        try:
                            bc.s(q)
                        except Exception:
                            bc.phaseshift(q, np.pi / 2)
                    elif name == "t":
                        try:
                            bc.t(q)
                        except Exception:
                            bc.phaseshift(q, np.pi / 4)
                    elif name == "rx":
                        bc.rx(q, float(op.params[0]))
                    elif name == "ry":
                        bc.ry(q, float(op.params[0]))
                    elif name == "rz":
                        bc.rz(q, float(op.params[0]))
                    else:
                        raise NotImplementedError(f"Unsupported 1q gate for Braket: {name}")
                elif op.num_qubits == 2:
                    q0 = circuit.find_bit(qargs[0]).index
                    q1 = circuit.find_bit(qargs[1]).index
                    if name in {"cx", "cnot"}:
                        bc.cnot(q0, q1)
                    elif name == "cz":
                        bc.cz(q0, q1)
                    elif name == "swap":
                        bc.swap(q0, q1)
                    else:
                        raise NotImplementedError(f"Unsupported 2q gate for Braket: {name}")
                else:
                    raise NotImplementedError(f"Unsupported gate arity for Braket: {name}")

            # Ensure measurements for counts
            bc.measure_all()

            device = LocalSimulator()
            task = device.run(bc, shots=shots)
            result = task.result()

            try:
                counts = result.measurement_counts
                # Normalize keys to strings
                return {str(k): int(v) for k, v in counts.items()}
            except Exception:
                # Fallback: construct counts from raw measurements
                meas = np.asarray(result.measurements)
                counts: dict[str, int] = {}
                for row in meas:
                    bitstring = "".join(str(int(b)) for b in row)
                    counts[bitstring] = counts.get(bitstring, 0) + 1
                return counts
        except Exception as exc:
            warnings.warn(f"Braket simulation unavailable ({exc}), falling back to Qiskit", stacklevel=2)
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
        return {"name": "braket", "device": self.device}
