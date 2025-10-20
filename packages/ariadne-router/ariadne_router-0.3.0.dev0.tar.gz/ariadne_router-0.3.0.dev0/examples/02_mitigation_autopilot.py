from __future__ import annotations

from ariadne.passes.mitigation import simple_zne
from examples._util import write_report


def noisy_observable(true_value: float, bias: float) -> float:
    return true_value + bias


def main() -> None:
    ideal = 0.0  # e.g., <Z> on |+> is 0
    noisy = 0.15

    def obs(scale: float) -> float:
        # Linear bias model that increases with scale
        return noisy_observable(ideal, (noisy - ideal) * scale)

    est = simple_zne(obs, scales=(1.0, 2.0, 3.0), order=2)
    gain = abs(noisy - ideal) - abs(est - ideal)

    report = f"""
# Mitigation Autopilot (ZNE)

- Ideal: {ideal:.6f}
- Noisy: {noisy:.6f}
- ZNE estimate: {est:.6f}
- Absolute error reduction: {gain:.6f}
"""
    path = write_report("02_mitigation_autopilot", report)
    print(f"Wrote report to {path}")


if __name__ == "__main__":
    main()
