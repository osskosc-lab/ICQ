from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from phase0a import run_seed
from icq_ra.debug import config_fingerprint


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def binomial_cdf(k: int, n: int, p: float) -> float:
    return sum(
        math.comb(n, i) * (p ** i) * ((1.0 - p) ** (n - i))
        for i in range(k + 1)
    )


def clopper_pearson_upper_one_sided(k: int, n: int, alpha: float) -> float:
    if n <= 0:
        raise ValueError("n must be positive")
    if not (0.0 < alpha < 1.0):
        raise ValueError("alpha must lie in (0,1)")
    if k >= n:
        return 1.0
    if k < 0:
        raise ValueError("k must be non-negative")

    lo, hi = 0.0, 1.0
    for _ in range(100):
        mid = (lo + hi) / 2.0
        cdf = binomial_cdf(k, n, mid)
        if cdf > alpha:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def summarize(values: list[float]) -> dict:
    x = np.asarray(values, dtype=float)
    return {
        "n": int(x.size),
        "mean": float(x.mean()),
        "std": float(x.std(ddof=1)) if x.size > 1 else 0.0,
        "median": float(np.median(x)),
        "q95": float(np.quantile(x, 0.95)),
        "min": float(x.min()),
        "max": float(x.max()),
    }


def threshold_for(scenario: str, phase_cfg: dict) -> float:
    d = phase_cfg["per_run_diagnostic_thresholds"]
    if scenario == "INACTIVE":
        return float(d["inactive_icq_ra_max"])
    if scenario == "CONFOUNDED":
        return float(d["confounded_icq_ra_max"])
    raise ValueError(f"Unsupported null scenario: {scenario}")


def main():
    parser = argparse.ArgumentParser(description="ICQ-RA P0A-2 Null Calibration")
    parser.add_argument("--phase0a-config", required=True)
    parser.add_argument("--calibration-config", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    phase_cfg = load_json(args.phase0a_config)
    cal_cfg = load_json(args.calibration_config)

    seeds = [int(s) for s in phase_cfg["seeds"]]
    scenarios = list(cal_cfg["null_scenarios"])
    alpha = float(cal_cfg["binomial_alpha"])

    weights = cal_cfg["declared_null_mixture"]
    if float(weights["INACTIVE_weight"]) != 0.5 or float(weights["CONFOUNDED_weight"]) != 0.5:
        raise ValueError("P0A-2 pooled interpretation is frozen to the declared 50/50 Null mixture.")

    records = {}
    scenario_summary = {}
    pooled_exceedances = 0
    pooled_n = 0
    all_debug_pass = True

    for scenario in scenarios:
        threshold = threshold_for(scenario, phase_cfg)
        scenario_records = []
        for seed in seeds:
            result = run_seed(scenario, seed, phase_cfg, include_debug=True)
            debug = result["debug"]
            exceeded = float(result["icq_ra"]) > threshold
            pooled_exceedances += int(exceeded)
            pooled_n += 1
            all_debug_pass = all_debug_pass and bool(debug["debug_pass"])

            scenario_records.append({
                "seed": seed,
                "icq_ra": float(result["icq_ra"]),
                "obs_distance": float(result["obs_distance"]),
                "per_run_diagnostic_threshold": threshold,
                "exceeded": bool(exceeded),
                "dataset_sha256": debug["dataset_sha256"]["combined"],
                "debug_pass": bool(debug["debug_pass"]),
                "input_invariants_pass": bool(debug["input_invariants"]["all_pass"]),
                "estimator_reconstruction_pass": bool(
                    debug["estimator_reconstruction"]["all_pass"]
                ),
            })

        values = [r["icq_ra"] for r in scenario_records]
        exceedances = sum(int(r["exceeded"]) for r in scenario_records)
        upper = clopper_pearson_upper_one_sided(exceedances, len(scenario_records), alpha)

        records[scenario] = scenario_records
        scenario_summary[scenario] = {
            "per_run_diagnostic_threshold": threshold,
            "icq_ra": summarize(values),
            "exceedances": exceedances,
            "empirical_exceedance_rate": exceedances / len(scenario_records),
            "family_one_sided_95pct_exceedance_upper": upper,
            "family_bound_is_not_a_5pct_guarantee": True,
            "all_debug_pass": all(r["debug_pass"] for r in scenario_records),
        }

    mixture_upper = clopper_pearson_upper_one_sided(
        pooled_exceedances, pooled_n, alpha
    )

    expected_total = int(cal_cfg["expected_total_null_runs"])
    checks = {
        "run_count_exact": pooled_n == expected_total,
        "all_debug_pass": bool(all_debug_pass),
        "inactive_exceedances_zero": scenario_summary["INACTIVE"]["exceedances"] == 0,
        "confounded_exceedances_zero": scenario_summary["CONFOUNDED"]["exceedances"] == 0,
        "declared_50_50_mixture_one_sided_95pct_exceedance_upper_le_0_05": (
            mixture_upper
            <= float(
                cal_cfg["pass_rule"][
                    "declared_mixture_one_sided_95pct_exceedance_upper_max"
                ]
            )
        ),
    }

    decision = "PASS" if all(checks.values()) else "FAIL"
    payload = {
        "protocol_id": cal_cfg["protocol_id"],
        "semantic_revision": cal_cfg["semantic_revision"],
        "gate": cal_cfg["gate"],
        "decision": decision,
        "phase0a_config_sha256": config_fingerprint(phase_cfg),
        "calibration_config": cal_cfg,
        "checks": checks,
        "scenario_summary": scenario_summary,
        "declared_50_50_null_mixture": {
            "n": pooled_n,
            "exceedances": pooled_exceedances,
            "empirical_exceedance_rate": pooled_exceedances / pooled_n,
            "one_sided_95pct_exceedance_upper": mixture_upper,
            "interpretation": "APPLIES_ONLY_TO_DECLARED_50_50_INACTIVE_CONFOUNDED_SYNTHETIC_MIXTURE",
        },
        "records": records,
        "claim_ceiling": cal_cfg["claim_ceiling"],
        "next_gate_if_pass": "P0A-3_ACTIVE_SENSITIVITY_QUALIFICATION",
        "phase0a_qualification_authorized": False,
        "confirmatory_run_authorized": False,
        "qualia_claim_authorized": False,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({
        "protocol_id": payload["protocol_id"],
        "semantic_revision": payload["semantic_revision"],
        "gate": payload["gate"],
        "decision": payload["decision"],
        "checks": payload["checks"],
        "scenario_summary": payload["scenario_summary"],
        "declared_50_50_null_mixture": payload["declared_50_50_null_mixture"],
        "next_gate_if_pass": payload["next_gate_if_pass"],
    }, indent=2, ensure_ascii=False))

    raise SystemExit(0 if decision == "PASS" else 1)


if __name__ == "__main__":
    main()
