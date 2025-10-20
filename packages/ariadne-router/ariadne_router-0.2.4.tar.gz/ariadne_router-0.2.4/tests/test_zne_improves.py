from __future__ import annotations

from ariadne.passes.mitigation import simple_zne


def test_zne_improves_on_fake_noise_model() -> None:
    ideal = 1.0
    noisy = 0.8

    def obs(scale: float) -> float:
        return ideal + (noisy - ideal) * scale

    est = simple_zne(obs, scales=(1.0, 2.0, 3.0), order=2)
    assert abs(est - ideal) < abs(noisy - ideal)
