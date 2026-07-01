from __future__ import annotations

from dataclasses import dataclass
from math import comb
from typing import Dict, Iterable, Tuple

from scipy.stats import beta, fisher_exact, binomtest


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> Tuple[float, float]:
    if n <= 0:
        raise ValueError("n must be positive")
    if k < 0 or k > n:
        raise ValueError("k must be in [0, n]")
    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2.0, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1.0 - alpha / 2.0, k + 1, n - k))
    return lo, hi


def fisher_p(k1: int, n1: int, k2: int, n2: int) -> float:
    table = [[k1, n1 - k1], [k2, n2 - k2]]
    return float(fisher_exact(table, alternative="two-sided").pvalue)


def mcnemar_exact_p(b: int, c: int) -> float:
    # Exact two-sided binomial test on discordant pairs.
    return float(binomtest(min(b, c), n=b + c, p=0.5, alternative="two-sided").pvalue)


def policy_loss(asr: float, frr: float, cost: float, lam: float, eta: float = 0.05) -> float:
    return lam * asr + frr + eta * cost


def pooled_break_even(asr_p1: float, asr_p2: float, frr_p1: float, frr_p2: float, cost_p1: float, cost_p2: float, eta: float = 0.05) -> float:
    return ((frr_p2 - frr_p1) + eta * (cost_p2 - cost_p1)) / (asr_p1 - asr_p2)


def prevalence_break_even(
    asr_p1: float,
    asr_p2: float,
    frr_p1: float,
    frr_p2: float,
    cost_p1: float,
    cost_p2: float,
    benign_prevalence: float,
    eta: float = 0.05,
) -> float:
    rho_b = benign_prevalence
    rho_m = 1.0 - rho_b
    if rho_m <= 0:
        raise ValueError("malicious prevalence must be positive")
    # Operational cost is per item, so it is not class-prevalence weighted.
    return (rho_b * (frr_p2 - frr_p1) + eta * (cost_p2 - cost_p1)) / (rho_m * (asr_p1 - asr_p2))


def fmt_interval(k: int, n: int, digits: int = 3) -> str:
    lo, hi = clopper_pearson(k, n)
    return f"[{lo:.{digits}f}, {hi:.{digits}f}]"
