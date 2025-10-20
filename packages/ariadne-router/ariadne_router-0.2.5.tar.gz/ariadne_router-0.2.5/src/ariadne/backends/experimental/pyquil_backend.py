from __future__ import annotations

import warnings
from typing import Any

import numpy as np
from qiskit import QuantumCircuit


class PyQuilBackend:
    """Skeleton PyQuil backend adapter.

    Attempts to simulate using PyQuil if installed; otherwise falls back to Qiskit.
    """

    def __init__(self, device: str | None = None) -> None:
        self.device = device or "wavefunction-simulator"

    def simulate(self, circuit: QuantumCircuit, shots: int = 1000) -> dict[str, int]:
        try:
            # Lazy imports to keep dependency optional
            from pyquil import Program  # type: ignore
            from pyquil.gates import CNOT, CZ, RX, RY, RZ, SWAP, H, S, T, X, Y, Z  # type: ignore

            try:
                from pyquil.simulation.tools import program_state_vector  # type: ignore
            except Exception as exc:
                raise RuntimeError("pyquil.simulation.tools not available") from exc

            prog = Program()

            # Map Qiskit instructions to PyQuil gates (subset)
            for item in circuit.data:
                op = getattr(item, "operation", item[0])
                qargs = list(getattr(item, "qubits", item[1]))
                name = getattr(op, "name", "")

                # Skip non-unitary ops here; measurement handled in sampling
                if name in {"measure", "barrier", "delay", "reset"}:
                    continue

                # Single-qubit operations
                if op.num_qubits == 1:
                    q = circuit.find_bit(qargs[0]).index
                    if name == "h":
                        prog += H(q)
                    elif name == "x":
                        prog += X(q)
                    elif name == "y":
                        prog += Y(q)
                    elif name == "z":
                        prog += Z(q)
                    elif name == "s":
                        prog += S(q)
                    elif name == "t":
                        prog += T(q)
                    elif name == "rx":
                        prog += RX(float(op.params[0]), q)
                    elif name == "ry":
                        prog += RY(float(op.params[0]), q)
                    elif name == "rz":
                        prog += RZ(float(op.params[0]), q)
                    else:
                        raise NotImplementedError(f"Unsupported 1q gate for PyQuil: {name}")
                elif op.num_qubits == 2:
                    q0 = circuit.find_bit(qargs[0]).index
                    q1 = circuit.find_bit(qargs[1]).index
                    if name in {"cx", "cnot"}:
                        prog += CNOT(q0, q1)
                    elif name == "cz":
                        prog += CZ(q0, q1)
                    elif name == "swap":
                        prog += SWAP(q0, q1)
                    else:
                        raise NotImplementedError(f"Unsupported 2q gate for PyQuil: {name}")
                else:
                    raise NotImplementedError(f"Unsupported gate arity for PyQuil: {name}")

            # Compute statevector using PyQuil tool, then sample counts
            n = circuit.num_qubits
            state = program_state_vector(prog, n)
            probs = np.abs(state) ** 2

            # Sample shots from distribution
            outcomes = np.random.choice(2**n, size=shots, p=probs)
            counts: dict[str, int] = {}
            for idx in outcomes:
                bitstring = format(idx, f"0{n}b")
                counts[bitstring] = counts.get(bitstring, 0) + 1
            return counts
        except Exception as exc:
            warnings.warn(f"PyQuil simulation unavailable ({exc}), falling back to Qiskit", stacklevel=2)
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
        return {"name": "pyquil", "device": self.device}
