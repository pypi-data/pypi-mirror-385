"""Simple error mitigation utilities."""

from __future__ import annotations

from collections.abc import Callable, Iterable

import numpy as np


def simple_zne(observable: Callable[[float], float], *, scales: Iterable[float], order: int = 1) -> float:
    """Zero-noise extrapolation using a polynomial fit."""

    scale_list = list(scales)
    if len(scale_list) < 2:
        raise ValueError("simple_zne requires at least two scale factors")

    values = np.asarray([observable(scale) for scale in scale_list], dtype=float)
    degree = min(order, len(scale_list) - 1)
    coeffs = np.polyfit(scale_list, values, deg=degree)
    return float(np.polyval(coeffs, 0.0))
