from __future__ import annotations

import hashlib
import json
import platform
import sys
from typing import Iterable

import numpy as np

from .core import RAEstimate, empirical_js_distance


def _array_fingerprint(array: np.ndarray) -> str:
    x = np.ascontiguousarray(np.asarray(array))
    digest = hashlib.sha256()
    digest.update(str(x.dtype).encode("utf-8"))
    digest.update(str(x.shape).encode("utf-8"))
    digest.update(x.tobytes())
    return digest.hexdigest()


def dataset_fingerprint(q: np.ndarray, h: np.ndarray, u: np.ndarray, y: np.ndarray) -> dict:
    parts = {
        "q": _array_fingerprint(q),
        "h": _array_fingerprint(h),
        "u": _array_fingerprint(u),
        "y": _array_fingerprint(y),
    }
    joined = "|".join(parts[k] for k in ("q", "h", "u", "y"))
    parts["combined"] = hashlib.sha256(joined.encode("utf-8")).hexdigest()
    return parts


def config_fingerprint(cfg: dict) -> str:
    canonical = json.dumps(cfg, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def validate_inputs(
    q: np.ndarray,
    h: np.ndarray,
    u: np.ndarray,
    y: np.ndarray,
    *,
    intervention_values: Iterable[float],
    history_values: Iterable[int],
    bin_edges: np.ndarray,
    min_cell: int,
) -> dict:
    q = np.asarray(q)
    h = np.asarray(h)
    u = np.asarray(u, dtype=float)
    y = np.asarray(y, dtype=float)
    interventions = np.asarray(list(intervention_values), dtype=float)
    histories = np.asarray(list(history_values))

    checks = {
        "equal_lengths": len(q) == len(h) == len(u) == len(y),
        "nonempty": len(y) > 0,
        "q_binary": bool(np.all(np.isin(q, [0, 1]))),
        "history_declared": bool(np.all(np.isin(h, histories))),
        "intervention_declared": bool(np.all(np.isin(u, interventions))),
        "y_finite": bool(np.all(np.isfinite(y))),
        "bin_edges_finite": bool(np.all(np.isfinite(bin_edges))),
        "bin_edges_strictly_increasing": bool(np.all(np.diff(bin_edges) > 0)),
        "min_cell_positive": int(min_cell) > 0,
    }

    cell_counts = {}
    all_cells_sufficient = True
    for u_value in interventions:
        for h_value in histories:
            mask = (u == u_value) & (h == h_value)
            n0 = int(np.sum(mask & (q == 0)))
            n1 = int(np.sum(mask & (q == 1)))
            key = f"u={float(u_value)}|h={int(h_value)}"
            cell_counts[key] = {"q0": n0, "q1": n1, "min_required": int(min_cell)}
            if min(n0, n1) < int(min_cell):
                all_cells_sufficient = False

    checks["all_declared_cells_meet_min_cell"] = all_cells_sufficient

    return {
        "checks": checks,
        "all_pass": all(checks.values()),
        "failed": [name for name, passed in checks.items() if not passed],
        "cell_counts": cell_counts,
    }


def _permutation_audit(
    y0: np.ndarray,
    y1: np.ndarray,
    bin_edges: np.ndarray,
    *,
    rng: np.random.Generator,
    n_permutations: int,
) -> dict:
    observed = empirical_js_distance(y0, y1, bin_edges)
    pooled = np.concatenate([y0, y1])
    n0 = y0.size
    null_values = np.empty(n_permutations, dtype=float)

    for i in range(n_permutations):
        perm = rng.permutation(pooled.size)
        null_values[i] = empirical_js_distance(
            pooled[perm[:n0]],
            pooled[perm[n0:]],
            bin_edges,
        )

    null_mean = float(null_values.mean())
    corrected = float(max(0.0, observed - null_mean))
    return {
        "observed_jsd": float(observed),
        "permutation_null_mean": null_mean,
        "permutation_null_std": float(null_values.std(ddof=1)) if n_permutations > 1 else 0.0,
        "permutation_null_min": float(null_values.min()),
        "permutation_null_max": float(null_values.max()),
        "corrected_jsd": corrected,
    }


def cell_diagnostics(
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
    estimator_seed: int,
) -> dict:
    q = np.asarray(q)
    h = np.asarray(h)
    u = np.asarray(u, dtype=float)
    y = np.asarray(y, dtype=float)

    rng = np.random.default_rng(estimator_seed)
    cells = {}
    reconstructed = {}

    for u_value in intervention_values:
        distances = []
        weights = []

        for h_value in history_values:
            mask = (u == float(u_value)) & (h == h_value)
            y0 = y[mask & (q == 0)]
            y1 = y[mask & (q == 1)]
            key = f"u={float(u_value)}|h={int(h_value)}"

            entry = {
                "n_q0": int(y0.size),
                "n_q1": int(y1.size),
                "y_q0_mean": float(y0.mean()) if y0.size else None,
                "y_q1_mean": float(y1.mean()) if y1.size else None,
                "y_q0_std": float(y0.std(ddof=1)) if y0.size > 1 else None,
                "y_q1_std": float(y1.std(ddof=1)) if y1.size > 1 else None,
                "eligible": min(y0.size, y1.size) >= int(min_cell),
            }

            if entry["eligible"]:
                audit = _permutation_audit(
                    y0,
                    y1,
                    bin_edges,
                    rng=rng,
                    n_permutations=n_permutations,
                )
                entry.update(audit)
                distances.append(audit["corrected_jsd"])
                weights.append(y0.size + y1.size)

            cells[key] = entry

        if distances:
            reconstructed[str(float(u_value))] = float(
                np.average(np.asarray(distances), weights=np.asarray(weights))
            )

    return {
        "cells": cells,
        "reconstructed_per_intervention": reconstructed,
        "reconstructed_icq_ra": max(reconstructed.values()) if reconstructed else None,
    }


def build_debug_report(
    *,
    scenario: str,
    seed: int,
    cfg: dict,
    q: np.ndarray,
    h: np.ndarray,
    u: np.ndarray,
    y: np.ndarray,
    estimate: RAEstimate,
    obs_distance: float,
    bin_edges: np.ndarray,
) -> dict:
    estimator_seed = int(seed) + int(cfg["estimator_seed_offset"])
    validation = validate_inputs(
        q,
        h,
        u,
        y,
        intervention_values=cfg["intervention_values"],
        history_values=cfg["history_values"],
        bin_edges=bin_edges,
        min_cell=int(cfg["min_cell"]),
    )
    cells = cell_diagnostics(
        q,
        h,
        u,
        y,
        intervention_values=cfg["intervention_values"],
        history_values=cfg["history_values"],
        bin_edges=bin_edges,
        min_cell=int(cfg["min_cell"]),
        n_permutations=int(cfg["n_permutations"]),
        estimator_seed=estimator_seed,
    )

    reconstructed = cells["reconstructed_per_intervention"]
    expected = {str(float(k)): float(v) for k, v in estimate.per_intervention.items()}
    keys_match = set(reconstructed) == set(expected)
    values_match = keys_match and all(
        np.isclose(reconstructed[k], expected[k], atol=1e-12, rtol=0.0)
        for k in expected
    )
    icq_match = (
        cells["reconstructed_icq_ra"] is not None
        and np.isclose(cells["reconstructed_icq_ra"], estimate.value, atol=1e-12, rtol=0.0)
    )

    estimator_audit = {
        "per_intervention_match": bool(values_match),
        "icq_ra_match": bool(icq_match),
        "all_pass": bool(values_match and icq_match),
        "reported_per_intervention": expected,
        "reported_icq_ra": float(estimate.value),
        "reconstructed_per_intervention": reconstructed,
        "reconstructed_icq_ra": cells["reconstructed_icq_ra"],
    }

    return {
        "debug_schema": "ICQ-RA-DEBUG-v0.1",
        "mode": "SINGLE_SEED_DIAGNOSTIC",
        "scenario": scenario,
        "seed": int(seed),
        "estimator_seed": estimator_seed,
        "config_sha256": config_fingerprint(cfg),
        "dataset_sha256": dataset_fingerprint(q, h, u, y),
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "platform": platform.platform(),
        },
        "input_invariants": validation,
        "estimator_reconstruction": estimator_audit,
        "observed_outputs": {
            "icq_ra": float(estimate.value),
            "obs_distance": float(obs_distance),
            "per_intervention": expected,
            "valid_cells": {str(float(k)): int(v) for k, v in estimate.valid_cells.items()},
        },
        "cell_diagnostics": cells["cells"],
        "debug_pass": bool(validation["all_pass"] and estimator_audit["all_pass"]),
        "claim_level": "DEBUG_ONLY_NO_SCIENTIFIC_INFERENCE",
    }
