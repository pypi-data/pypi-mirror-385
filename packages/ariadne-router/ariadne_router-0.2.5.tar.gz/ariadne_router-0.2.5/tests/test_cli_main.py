import sys
from pathlib import Path

import pytest
from qiskit import QuantumCircuit
from qiskit.qpy import dump

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ariadne.cli.main import AriadneCLI


def test_cli_loads_first_qpy_circuit(tmp_path):
    circuit = QuantumCircuit(1)
    circuit.x(0)

    second_circuit = QuantumCircuit(1)
    second_circuit.h(0)

    qpy_path = tmp_path / "test_circuit.qpy"
    with open(qpy_path, "wb") as qpy_file:
        dump([circuit, second_circuit], qpy_file)

    cli = AriadneCLI()
    loaded = cli._load_circuit(str(qpy_path))

    assert isinstance(loaded, QuantumCircuit)
    assert loaded.count_ops() == circuit.count_ops()
    assert loaded.num_qubits == circuit.num_qubits


def test_cli_load_qpy_requires_circuit(tmp_path, monkeypatch):
    qpy_path = tmp_path / "empty.qpy"
    qpy_path.write_bytes(b"")

    def fake_load(_file):
        return []

    monkeypatch.setattr("qiskit.qpy.load", fake_load)

    cli = AriadneCLI()

    with pytest.raises(ValueError, match="does not contain any QuantumCircuit"):
        cli._load_circuit(str(qpy_path))
