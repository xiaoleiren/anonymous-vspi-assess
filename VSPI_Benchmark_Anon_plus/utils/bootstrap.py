from __future__ import annotations

from typing import Callable, Iterable, Tuple

import numpy as np


def bootstrap_ci(
    values: Iterable[float],
    stat_fn: Callable[[np.ndarray], float],
    n_resamples: int = 1000,
    seed: int = 0,
    alpha: float = 0.05,
) -> Tuple[float, float]:
    arr = np.asarray(list(values), dtype=float)
    if arr.size == 0:
        return 0.0, 0.0
    if arr.size == 1:
        x = float(stat_fn(arr))
        return x, x
    rng = np.random.default_rng(seed)
    stats = np.empty(n_resamples, dtype=float)
    for i in range(n_resamples):
        sample = rng.choice(arr, size=arr.size, replace=True)
        stats[i] = float(stat_fn(sample))
    lo = float(np.quantile(stats, alpha / 2.0))
    hi = float(np.quantile(stats, 1.0 - alpha / 2.0))
    return lo, hi
