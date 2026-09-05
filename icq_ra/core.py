from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

import numpy as np


@dataclass(frozen=True)
class RAEstimate:
    value: float
    per_intervention: Dict[float, float]
    valid_cells: Dict[float, int]


def _probabilities(samples: np.ndarray, bin_edges: np.ndarray, smoothing: float) -> np.ndarray:
    counts, _ = np.histogram(samples, bins=bin_edges)
    probs = counts.astype(float) + smoothing
    total = probs.sum()
    if total <= 0:
        raise ValueError("Histogram has zero total mass.")
    return probs / total


def empirical_js_distance(
    a: np.ndarray,
    b: np.ndarray,
    bin_edges: np.ndarray,
    *,
    smoothing: float = 1e-12,
) -> float:
    """Jensen-Shannon distance in [0, 1] using base-2 logarithms."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.size == 0 or b.size == 0:
        raise ValueError("Both samples must be non-empty.")

    p = _probabilities(a, bin_edges, smoothing)
    q = _probabilities(b, bin_edges, smoothing)
    m = 0.5 * (p + q)

    kl_pm = np.sum(p * np.log2(p / m))
    kl_qm = np.sum(q * np.log2(q / m))
    js_divergence = 0.5 * (kl_pm + kl_qm)
    return float(np.sqrt(max(0.0, js_divergence)))


def permutation_corrected_js_distance(
    a: np.ndarray,
    b: np.ndarray,
    bin_edges: np.ndarray,
    *,
    rng: np.random.Generator,
    n_permutations: int,
) -> float:
    """
    Finite-sample corrected estimator.

    Estimand: JSD(P_a, P_b)
    Estimator: max(0, empirical_JSD - mean(permutation-null empirical_JSD))

    The subtraction is a measurement-bias correction and is not part of
    the theoretical ICQ-RA definition.
    """
    if n_permutations < 1:
        raise ValueError("n_permutations must be >= 1.")

    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    observed = empirical_js_distance(a, b, bin_edges)

    pooled = np.concatenate([a, b])
    n_a = a.size
    null_values = np.empty(n_permutations, dtype=float)

    for i in range(n_permutations):
        perm = rng.permutation(pooled.size)
        null_values[i] = empirical_js_distance(
            pooled[perm[:n_a]],
            pooled[perm[n_a:]],
            bin_edges,
        )

    return float(max(0.0, observed - null_values.mean()))


def estimate_icq_ra(
    q: np.ndarray,
    h: np.ndarray,
    u: np.ndarray,
    y: np.ndarray,
    *,
    intervention_values: Iterable[float],
    history_values: Iterable[int],
    bin_edges: np.ndarray,
    min_cell: int,
    n_permutations: int,
    seed: int,
) -> RAEstimate:
    """
    Estimate history-conditioned response accessibility.

    Within each intervention and fixed history stratum, compare Y for q=0 vs q=1.
    Stratum distances are weighted by the number of observations contributing to
    the valid comparison. ICQ-RA is the maximum over allowed interventions.
    """
    q = np.asarray(q)
    h = np.asarray(h)
    u = np.asarray(u, dtype=float)
    y = np.asarray(y, dtype=float)

    n = len(y)
    if not (len(q) == len(h) == len(u) == n):
        raise ValueError("q, h, u, and y must have equal length.")

    rng = np.random.default_rng(seed)
    per_intervention: Dict[float, float] = {}
    valid_cells: Dict[float, int] = {}

    for u_value in intervention_values:
        distances = []
        weights = []

        for h_value in history_values:
            mask = (u == float(u_value)) & (h == h_value)
            y0 = y[mask & (q == 0)]
            y1 = y[mask & (q == 1)]

            if min(y0.size, y1.size) < min_cell:
                continue

            d = permutation_corrected_js_distance(
                y0,
                y1,
                bin_edges,
                rng=rng,
                n_permutations=n_permutations,
            )
            distances.append(d)
            weights.append(y0.size + y1.size)

        if distances:
            per_intervention[float(u_value)] = float(
                np.average(np.asarray(distances), weights=np.asarray(weights))
            )
            valid_cells[float(u_value)] = len(distances)

    if not per_intervention:
        raise ValueError("No intervention had enough valid history-conditioned cells.")

    return RAEstimate(
        value=max(per_intervention.values()),
        per_intervention=per_intervention,
        valid_cells=valid_cells,
    )


def observational_distance(
    q: np.ndarray,
    y: np.ndarray,
    *,
    bin_edges: np.ndarray,
) -> float:
    """Unadjusted observational baseline that ignores H and intervention structure."""
    q = np.asarray(q)
    y = np.asarray(y, dtype=float)
    return empirical_js_distance(y[q == 0], y[q == 1], bin_edges)
