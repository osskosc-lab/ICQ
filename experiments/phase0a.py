from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from icq_ra import estimate_icq_ra, observational_distance
from icq_ra.debug import build_debug_report


def generate_scm(scenario: str, *, seed: int, n: int, cfg: dict):
    rng = np.random.default_rng(seed)

    h = rng.integers(0, 2, size=n)
    u_values = np.asarray(cfg["intervention_values"], dtype=float)
    u = rng.choice(u_values, size=n)

    if scenario == "CONFOUNDED":
        flip = rng.random(n) < float(cfg["confounded_q_flip_probability"])
        q = np.where(flip, 1 - h, h)
        latent_coupling = 0.0
    elif scenario == "ACTIVE":
        q = rng.integers(0, 2, size=n)
        latent_coupling = float(cfg["active_latent_coupling"])
    elif scenario == "INACTIVE":
        q = rng.integers(0, 2, size=n)
        latent_coupling = 0.0
    else:
        raise ValueError(f"Unknown scenario: {scenario}")

    noise = rng.normal(0.0, float(cfg["noise_sigma"]), size=n)

    # Structural response equation:
    # Y = a*u + gamma*H + b*q*u + epsilon
    y = (
        float(cfg["intervention_main_effect"]) * u
        + float(cfg["history_effect"]) * h
        + latent_coupling * q * u
        + noise
    )
    return q, h, u, y


def run_seed(scenario: str, seed: int, cfg: dict, *, include_debug: bool = False) -> dict:
    q, h, u, y = generate_scm(
        scenario,
        seed=seed,
        n=int(cfg["n_per_seed"]),
        cfg=cfg,
    )

    bin_edges = np.linspace(
        float(cfg["histogram_min"]),
        float(cfg["histogram_max"]),
        int(cfg["histogram_bins"]) + 1,
    )

    ra = estimate_icq_ra(
        q,
        h,
        u,
        y,
        intervention_values=cfg["intervention_values"],
        history_values=cfg["history_values"],
        bin_edges=bin_edges,
        min_cell=int(cfg["min_cell"]),
        n_permutations=int(cfg["n_permutations"]),
        seed=seed + int(cfg["estimator_seed_offset"]),
    )

    obs = observational_distance(q, y, bin_edges=bin_edges)

    result = {
        "seed": seed,
        "icq_ra": ra.value,
        "obs_distance": obs,
        "per_intervention": {str(k): v for k, v in ra.per_intervention.items()},
        "valid_cells": {str(k): v for k, v in ra.valid_cells.items()},
    }

    if include_debug:
        result["debug"] = build_debug_report(
            scenario=scenario,
            seed=seed,
            cfg=cfg,
            q=q,
            h=h,
            u=u,
            y=y,
            estimate=ra,
            obs_distance=obs,
            bin_edges=bin_edges,
        )

    return result


def summarize(values):
    x = np.asarray(values, dtype=float)
    return {
        "mean": float(x.mean()),
        "std": float(x.std(ddof=1)) if len(x) > 1 else 0.0,
        "min": float(x.min()),
        "max": float(x.max()),
    }


def qualification_decision(results: dict, cfg: dict) -> dict:
    thresholds = cfg["qualification_thresholds"]

    active = summarize([r["icq_ra"] for r in results["ACTIVE"]])
    inactive = summarize([r["icq_ra"] for r in results["INACTIVE"]])
    conf_ra = summarize([r["icq_ra"] for r in results["CONFOUNDED"]])
    conf_obs = summarize([r["obs_distance"] for r in results["CONFOUNDED"]])

    checks = {
        "ACTIVE_RA_MIN": active["mean"] >= float(thresholds["active_ra_mean_min"]),
        "INACTIVE_RA_MAX": inactive["mean"] <= float(thresholds["inactive_ra_mean_max"]),
        "CONFOUNDED_RA_MAX": conf_ra["mean"] <= float(thresholds["confounded_ra_mean_max"]),
        "CONFOUNDED_OBS_MIN": conf_obs["mean"] >= float(thresholds["confounded_obs_mean_min"]),
    }

    return {
        "checks": checks,
        "qualification_status": "PASS" if all(checks.values()) else "FAIL",
        "summary": {
            "ACTIVE_icq_ra": active,
            "INACTIVE_icq_ra": inactive,
            "CONFOUNDED_icq_ra": conf_ra,
            "CONFOUNDED_obs_distance": conf_obs,
        },
        "claim_level": "PIPELINE_QUALIFICATION_ONLY",
        "qualia_claim_authorized": False,
    }


def _write_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="ICQ-RA Phase 0A synthetic qualification")
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--scenario", choices=["ACTIVE", "INACTIVE", "CONFOUNDED"])
    parser.add_argument("--seed", type=int)
    parser.add_argument(
        "--debug-dir",
        help="Directory for a single-seed diagnostic JSON. Requires --scenario and --seed.",
    )
    args = parser.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))

    single_seed_mode = args.scenario is not None or args.seed is not None or args.debug_dir is not None
    if single_seed_mode:
        if args.scenario is None or args.seed is None:
            parser.error("--scenario and --seed are both required for debug replay mode.")

        result = run_seed(args.scenario, args.seed, cfg, include_debug=True)
        payload = {
            "protocol_id": cfg["protocol_id"],
            "protocol_status": cfg["protocol_status"],
            "mode": "SINGLE_SEED_DEBUG_REPLAY",
            "qualification_decision": "NOT_EVALUATED",
            "result": {k: v for k, v in result.items() if k != "debug"},
        }
        _write_json(Path(args.out), payload)

        if args.debug_dir:
            debug_path = Path(args.debug_dir) / f"{args.scenario.lower()}_seed_{args.seed}.debug.json"
            _write_json(debug_path, result["debug"])
            print(f"debug_report={debug_path}")

        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    seeds = [int(s) for s in cfg["seeds"]]
    results = {}
    for scenario in ("ACTIVE", "INACTIVE", "CONFOUNDED"):
        results[scenario] = [run_seed(scenario, seed, cfg) for seed in seeds]

    payload = {
        "protocol_id": cfg["protocol_id"],
        "protocol_status": cfg["protocol_status"],
        "mode": "PHASE0A_QUALIFICATION",
        "results": results,
        "decision": qualification_decision(results, cfg),
    }
    _write_json(Path(args.out), payload)
    print(json.dumps(payload["decision"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
