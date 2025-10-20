from __future__ import annotations

from pathlib import Path


def estimate_sv_bytes(n_qubits: int, complex_bytes: int = 16) -> int:
    """Estimate memory required for a state vector simulation."""
    return (2**n_qubits) * complex_bytes


def write_report(name: str, text: str, folder: Path | None = None) -> Path:
    folder = folder or Path("reports")
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{name}.md"
    path.write_text(text)
    return path
