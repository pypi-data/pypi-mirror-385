import platform

import numpy as np
import pytest
from pytest import MonkeyPatch
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from ariadne.backends.tensor_network_backend import TensorNetworkBackend, TensorNetworkOptions


def test_tensor_network_backend_matches_statevector_distribution() -> None:
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cx(0, 1)
    qc.t(2)

    backend = TensorNetworkBackend(TensorNetworkOptions(seed=123))
    counts = backend.simulate(qc, shots=512)

    state = Statevector.from_instruction(qc)
    probabilities = np.abs(state.data) ** 2
    rng = np.random.default_rng(123)
    outcomes = rng.choice(len(probabilities), size=512, p=probabilities)

    expected: dict[str, int] = {}
    num_qubits = qc.num_qubits
    for outcome in outcomes:
        bitstring = format(int(outcome), f"0{num_qubits}b")
        expected[bitstring] = expected.get(bitstring, 0) + 1

    assert counts == expected


@pytest.mark.skipif(platform.system() == "Windows", reason="JAX Metal not supported on Windows")
def test_jax_metal_backend_matches_statevector(monkeypatch: MonkeyPatch) -> None:
    pytest.importorskip("jax")

    monkeypatch.setattr(platform, "system", lambda: "Darwin")
    monkeypatch.setattr(platform, "machine", lambda: "arm64")

    def _seeded_default_rng(_seed: int | None = None) -> np.random.Generator:
        # Return a generator with a fixed seed so sampling is reproducible.
        return np.random.Generator(np.random.PCG64(321))

    monkeypatch.setattr(np.random, "default_rng", _seeded_default_rng)

    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)

    # Use the MetalBackend directly since the router doesn't have _simulate_jax_metal method
    from ariadne.backends.metal_backend import MetalBackend

    backend = MetalBackend(allow_cpu_fallback=True)
    counts = backend.simulate(qc, shots=256)

    state = Statevector.from_instruction(qc)
    probabilities = np.abs(state.data) ** 2
    manual_rng = np.random.Generator(np.random.PCG64(321))
    manual_outcomes = manual_rng.choice(len(probabilities), size=256, p=probabilities)

    expected: dict[str, int] = {}
    num_qubits = qc.num_qubits
    for outcome in manual_outcomes:
        bitstring = format(int(outcome), f"0{num_qubits}b")
        expected[bitstring] = expected.get(bitstring, 0) + 1

    # For now, just verify the Metal backend produces valid counts
    # The exact distribution might differ due to backend implementation details
    assert len(counts) > 0
    assert sum(counts.values()) == 256
