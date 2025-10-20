import argparse
import os
from collections.abc import Callable
from dataclasses import dataclass

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from qiskit import QuantumCircuit

from ariadne import simulate


@dataclass
class Case:
    name: str
    builder: Callable[[], QuantumCircuit]
    expected: str


def build_clifford_bell() -> QuantumCircuit:
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    return qc


def build_low_entanglement() -> QuantumCircuit:
    qc = QuantumCircuit(8, 8)
    qc.h(0)
    qc.t(0)
    qc.cx(0, 1)
    qc.cx(2, 3)
    qc.cx(4, 5)
    qc.cx(6, 7)
    qc.measure_all()
    return qc


def build_general_nonclifford() -> QuantumCircuit:
    qc = QuantumCircuit(5, 5)
    qc.h(0)
    qc.t(0)
    qc.cx(0, 1)
    qc.t(1)
    qc.measure_all()
    return qc


def collect_results(shots: int = 256) -> list[tuple[str, str, str]]:
    cases = [
        Case("Clifford (Bell)", build_clifford_bell, "STIM"),
        Case("Low entanglement (pairs+T)", build_low_entanglement, "MPS"),
        Case("General (non-Clifford)", build_general_nonclifford, "QISKIT or METAL or MPS"),
    ]

    results: list[tuple[str, str, str]] = []
    for c in cases:
        qc = c.builder()
        res = simulate(qc, shots=shots)
        backend = str(res.backend_used).split(".")[-1]
        results.append((c.name, c.expected, backend))
    return results


def make_animation(results: list[tuple[str, str, str]], output_path: str) -> None:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axis("off")

    title = ax.text(0.5, 0.9, "Ariadne Quickstart Routing", ha="center", va="center", fontsize=16)
    subtitle = ax.text(0.5, 0.8, "", ha="center", va="center", fontsize=12)
    line_expected = ax.text(0.1, 0.6, "", ha="left", va="center", fontsize=12)
    line_actual = ax.text(0.1, 0.5, "", ha="left", va="center", fontsize=12)

    def init():
        subtitle.set_text("")
        line_expected.set_text("")
        line_actual.set_text("")
        return [title, subtitle, line_expected, line_actual]

    def update(frame_idx: int):
        name, expected, actual = results[frame_idx]
        subtitle.set_text(f"Case: {name}")
        line_expected.set_text(f"Expected: {expected}")
        line_actual.set_text(f"Actual: {actual}")
        return [title, subtitle, line_expected, line_actual]

    anim = FuncAnimation(fig, update, frames=len(results), init_func=init, blit=True, repeat=True, interval=1600)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        writer = PillowWriter(fps=1)
        anim.save(output_path, writer=writer)
        print(f"Saved GIF to {output_path}")
    except Exception as exc:
        print(f"Failed to write GIF: {exc}. Saving PNG fallback.")
        fig.savefig(output_path.replace(".gif", ".png"), dpi=200, bbox_inches="tight")


def main():
    parser = argparse.ArgumentParser(description="Generate a quickstart routing GIF")
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--shots", type=int, default=256)
    args = parser.parse_args()

    results = collect_results(shots=args.shots)
    make_animation(results, args.output)


if __name__ == "__main__":
    main()
