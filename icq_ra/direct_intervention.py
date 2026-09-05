from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

import numpy as np

from .core import permutation_corrected_js_distance


@dataclass(frozen=True)
class DIEstimate:
    value: float
    per_intervention: Dict[float, float]
    valid_cells: Dict[float, int]


def estimate_icq_di(
    h_q0: np.ndarray,
    u_q0: np.ndarray,
    y_q0: np.ndarray,
    h_q1: np.ndarray,
    u_q1: np.ndarray,
    y_q1: np.ndarray,
    *,
    intervention_values: Iterable[float],
    history_values: Iterable[int],
    bin_edges: np.ndarray,
    min_cell: int,
    n_permutations: int,
    seed: int,
) -> DIEstimate:
    """
    Estimate direct-intervention response distance.

    Compare response distributions from explicit do(Q=0) and do(Q=1) arms
    within fixed U and H strata. Stratum distances are sample-size weighted;
    ICQ-DI is the maximum over declared U interventions.
    """
    h_q0 = np.asarray(h_q0)
    u_q0 = np.asarray(u_q0, dtype=float)
    y_q0 = np.asarray(y_q0, dtype=float)
    h_q1 = np.asarray(h_q1)
    u_q1 = np.asarray(u_q1, dtype=float)
    y_q1 = np.asarray(y_q1, dtype=float)

    if not (len(h_q0) == len(u_q0) == len(y_q0)):
        raise ValueError("q0 arm arrays must have equal length.")
    if not (len(h_q1) == len(u_q1) == len(y_q1)):
        raise ValueError("q1 arm arrays must have equal length.")

    rng = np.random.default_rng(seed)
    per_intervention: Dict[float, float] = {}
    valid_cells: Dict[float, int] = {}

    for u_value in intervention_values:
        distances = []
        weights = []

        for h_value in history_values:
            y0 = y_q0[(u_q0 == float(u_value)) & (h_q0 == h_value)]
            y1 = y_q1[(u_q1 == float(u_value)) & (h_q1 == h_value)]

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
        raise ValueError("No intervention had enough valid do(Q) history cells.")

    return DIEstimate(
        value=max(per_intervention.values()),
        per_intervention=per_intervention,
        valid_cells=valid_cells,
    )
