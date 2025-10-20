import argparse
from collections.abc import Callable
from dataclasses import dataclass

import matplotlib.pyplot as plt
from qiskit import QuantumCircuit

from ariadne import simulate


@dataclass
class Case:
    name: str
    description: str
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
    # Add a single non-Clifford gate to avoid Stim routing while keeping entanglement low
    qc.t(0)
    qc.cx(0, 1)
    qc.cx(2, 3)
    qc.cx(4, 5)
    qc.cx(6, 7)
    qc.measure_all()
    return qc


def build_non_clifford() -> QuantumCircuit:
    qc = QuantumCircuit(5, 5)
    qc.h(0)
    qc.t(0)
    qc.cx(0, 1)
    qc.t(1)
    qc.measure_all()
    return qc


def run_cases(shots: int = 256) -> list[tuple[str, str, str]]:
    cases = [
        Case(
            name="Clifford (Bell)",
            description="Pure Clifford",
            builder=build_clifford_bell,
            expected="STIM",
        ),
        Case(
            name="Low entanglement (pairs)",
            description="Shallow, pairwise entanglement",
            builder=build_low_entanglement,
            expected="MPS",
        ),
        Case(
            name="General (non-Clifford)",
            description="Has T gates",
            builder=build_non_clifford,
            expected="QISKIT or METAL",
        ),
    ]

    results: list[tuple[str, str, str]] = []
    for c in cases:
        qc = c.builder()
        res = simulate(qc, shots=shots)
        backend = str(res.backend_used)
        # backend may look like BackendType.STIM; normalize
        backend_str = backend.split(".")[-1]
        print(f"{c.name}: expected={c.expected} got={backend_str}")
        results.append((c.name, c.expected, backend_str))
    return results


def draw_table(data: list[tuple[str, str, str]], output_path: str) -> None:
    fig, ax = plt.subplots(figsize=(8, 2 + 0.5 * len(data)))
    ax.axis("off")
    table_data = [("Circuit", "Expected", "Actual")] + data
    table = ax.table(cellText=table_data, loc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)
    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    print(f"Saved routing matrix image to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Ariadne routing matrix demo")
    parser.add_argument("--shots", type=int, default=256)
    parser.add_argument(
        "--generate-image",
        type=str,
        default="",
        help="Path to save a routing matrix image (PNG)",
    )
    args = parser.parse_args()

    results = run_cases(shots=args.shots)

    if args.generate_image:
        draw_table(results, args.generate_image)


if __name__ == "__main__":
    main()
