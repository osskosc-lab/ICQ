from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from icq_ra import estimate_icq_di, estimate_icq_ra


SCENARIOS = ("INACTIVE_DIRECT", "DIRECT_ACTIVE", "HIDDEN_MODIFIER_PROXY")


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def bin_edges(cfg: dict) -> np.ndarray:
    e = cfg["estimator_parameters"]
    return np.linspace(
        float(e["histogram_min"]),
        float(e["histogram_max"]),
        int(e["histogram_bins"]) + 1,
    )


def _arm_seed(seed: int, q_value: int) -> int:
    return int(seed) + (10_000_000 if int(q_value) == 1 else 0)


def generate_do_q_arm(
    scenario: str,
    *,
    seed: int,
    q_value: int,
    cfg: dict,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray | None]:
    """
    Generate one explicit atomic do(Q=q_value) arm.

    Q is not sampled from any ordinary parent. The arm value q_value replaces
    Q's structural assignment. In HIDDEN_MODIFIER_PROXY, Q is deliberately
    absent from the Y equation.
    """
    if scenario not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario}")
    if q_value not in (0, 1):
        raise ValueError("q_value must be 0 or 1.")

    g = cfg["generator_parameters"]
    n = int(g["n_per_arm"])
    rng = np.random.default_rng(_arm_seed(seed, q_value))

    h = rng.integers(0, 2, size=n)
    u = rng.choice(np.asarray(g["intervention_values"], dtype=float), size=n)
    noise = rng.normal(0.0, float(g["noise_sigma"]), size=n)

    a = float(g["intervention_main_effect"])
    gamma = float(g["history_effect"])

    if scenario == "DIRECT_ACTIVE":
        b = float(g["direct_q_coupling"])
        y = a * u + gamma * h + b * float(q_value) * u + noise
        z = None

    elif scenario == "INACTIVE_DIRECT":
        y = a * u + gamma * h + noise
        z = None

    else:
        z = rng.integers(0, 2, size=n)
        c = float(g["hidden_modifier_strength"])
        y = a * u + gamma * h + c * z * u + noise

    return h, u, y, z


def generate_hidden_proxy_observational(
    *,
    seed: int,
    cfg: dict,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Generate the Phase 0A-style hidden-proxy baseline:
      Z -> Q
      Z x U -> Y
      Q -/-> Y
    """
    g = cfg["generator_parameters"]
    n = int(g["n_per_arm"]) * 2
    rng = np.random.default_rng(int(seed) + 20_000_000)

    h = rng.integers(0, 2, size=n)
    u = rng.choice(np.asarray(g["intervention_values"], dtype=float), size=n)
    z = rng.integers(0, 2, size=n)
    flip = rng.random(n) < float(g["q_proxy_flip_probability"])
    q = np.where(flip, 1 - z, z)
    noise = rng.normal(0.0, float(g["noise_sigma"]), size=n)

    y = (
        float(g["intervention_main_effect"]) * u
        + float(g["history_effect"]) * h
        + float(g["hidden_modifier_strength"]) * z * u
        + noise
    )
    return q, h, u, y


def generate_paired_integrity_case(
    scenario: str,
    *,
    seed: int,
    cfg: dict,
) -> dict:
    """
    Common-random-number audit used only to verify intervention semantics.

    It is not a qualification estimator. The same H/U/Z/noise realization is
    used for q=0 and q=1 so any Y difference must come from the declared Q term.
    """
    g = cfg["generator_parameters"]
    n = 512
    rng = np.random.default_rng(int(seed) + 30_000_000)

    h = rng.integers(0, 2, size=n)
    u = rng.choice(np.asarray(g["intervention_values"], dtype=float), size=n)
    noise = rng.normal(0.0, float(g["noise_sigma"]), size=n)
    z = rng.integers(0, 2, size=n)

    a = float(g["intervention_main_effect"])
    gamma = float(g["history_effect"])

    if scenario == "DIRECT_ACTIVE":
        b = float(g["direct_q_coupling"])
        y0 = a * u + gamma * h + noise
        y1 = a * u + gamma * h + b * u + noise
    elif scenario == "INACTIVE_DIRECT":
        y0 = a * u + gamma * h + noise
        y1 = y0.copy()
    elif scenario == "HIDDEN_MODIFIER_PROXY":
        c = float(g["hidden_modifier_strength"])
        y0 = a * u + gamma * h + c * z * u + noise
        y1 = y0.copy()
    else:
        raise ValueError(f"Unknown scenario: {scenario}")

    return {
        "h": h,
        "u": u,
        "z": z,
        "y_do_q0": y0,
        "y_do_q1": y1,
    }


def estimate_direct_seed(scenario: str, seed: int, cfg: dict) -> dict:
    h0, u0, y0, _ = generate_do_q_arm(
        scenario, seed=seed, q_value=0, cfg=cfg
    )
    h1, u1, y1, _ = generate_do_q_arm(
        scenario, seed=seed, q_value=1, cfg=cfg
    )
    g = cfg["generator_parameters"]
    e = cfg["estimator_parameters"]

    est = estimate_icq_di(
        h0,
        u0,
        y0,
        h1,
        u1,
        y1,
        intervention_values=g["intervention_values"],
        history_values=g["history_values"],
        bin_edges=bin_edges(cfg),
        min_cell=int(e["min_cell"]),
        n_permutations=int(e["n_permutations"]),
        seed=int(seed) + int(e["estimator_seed_offset"]),
    )
    return {
        "seed": int(seed),
        "scenario": scenario,
        "icq_di": float(est.value),
        "per_intervention": {str(k): float(v) for k, v in est.per_intervention.items()},
        "valid_cells": {str(k): int(v) for k, v in est.valid_cells.items()},
    }


def estimate_hidden_proxy_baseline(seed: int, cfg: dict) -> dict:
    q, h, u, y = generate_hidden_proxy_observational(seed=seed, cfg=cfg)
    g = cfg["generator_parameters"]
    e = cfg["estimator_parameters"]

    est = estimate_icq_ra(
        q,
        h,
        u,
        y,
        intervention_values=g["intervention_values"],
        history_values=g["history_values"],
        bin_edges=bin_edges(cfg),
        min_cell=int(e["min_cell"]),
        n_permutations=int(e["n_permutations"]),
        seed=int(seed) + int(e["estimator_seed_offset"]) + 100_000,
    )
    return {
        "seed": int(seed),
        "scenario": "HIDDEN_MODIFIER_PROXY_BASELINE",
        "phase0a_icq_ra": float(est.value),
        "per_intervention": {str(k): float(v) for k, v in est.per_intervention.items()},
        "valid_cells": {str(k): int(v) for k, v in est.valid_cells.items()},
    }


def main():
    ap = argparse.ArgumentParser(description="ICQ-RA Phase 0B design/debug runner")
    ap.add_argument("--config", required=True)
    ap.add_argument("--scenario", choices=SCENARIOS)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--out")
    args = ap.parse_args()

    cfg = load_json(args.config)

    if args.scenario is None or args.seed is None:
        raise SystemExit(
            "QUALIFICATION_EXECUTION_NOT_AUTHORIZED: use explicit debug --scenario and --seed only."
        )

    debug_seeds = {int(s) for s in cfg["seed_namespaces"]["debug_only_exposed"]}
    if int(args.seed) not in debug_seeds:
        raise SystemExit(
            "SEED_FIREWALL: only debug_only_exposed seeds may be used by this runner before authorization."
        )

    payload = {
        "protocol_id": cfg["protocol_id"],
        "protocol_status": cfg["protocol_status"],
        "mode": "DEBUG_ONLY_NO_SCIENTIFIC_INFERENCE",
        "direct": estimate_direct_seed(args.scenario, args.seed, cfg),
    }

    if args.scenario == "HIDDEN_MODIFIER_PROXY":
        payload["phase0a_baseline"] = estimate_hidden_proxy_baseline(args.seed, cfg)

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
