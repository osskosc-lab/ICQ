from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from phase0a import run_seed
from icq_ra.debug import config_fingerprint


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def summarize(values: list[float]) -> dict:
    x = np.asarray(values, dtype=float)
    return {
        "n": int(x.size),
        "mean": float(x.mean()),
        "std": float(x.std(ddof=1)) if x.size > 1 else 0.0,
        "median": float(np.median(x)),
        "q05": float(np.quantile(x, 0.05)),
        "q95": float(np.quantile(x, 0.95)),
        "min": float(x.min()),
        "max": float(x.max()),
    }


def main():
    parser = argparse.ArgumentParser(description="ICQ-RA P0A-3 ACTIVE sensitivity qualification")
    parser.add_argument("--phase0a-config", required=True)
    parser.add_argument("--p0a3-config", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    phase_cfg = load_json(args.phase0a_config)
    gate_cfg = load_json(args.p0a3_config)

    seeds = [int(s) for s in gate_cfg["heldout_seeds"]]
    forbidden = {int(s) for s in gate_cfg["forbidden_previously_observed_seeds"]}
    overlap = sorted(set(seeds) & forbidden)

    threshold_from_source = float(
        phase_cfg["qualification_thresholds"]["active_ra_mean_min"]
    )
    frozen_threshold = float(gate_cfg["primary_threshold_value_frozen"])

    preflight = {
        "seed_bank_disjoint_from_previously_observed": len(overlap) == 0,
        "heldout_seed_count_exact": len(seeds) == int(gate_cfg["expected_run_count"]),
        "heldout_seeds_unique": len(set(seeds)) == len(seeds),
        "threshold_matches_frozen_source": threshold_from_source == frozen_threshold,
    }

    if not all(preflight.values()):
        payload = {
            "protocol_id": gate_cfg["protocol_id"],
            "gate": gate_cfg["gate"],
            "decision": "STOP_PREFLIGHT",
            "preflight": preflight,
            "overlap": overlap,
            "phase0a_qualification_authorized": False,
            "confirmatory_run_authorized": False,
            "qualia_claim_authorized": False,
        }
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(json.dumps(payload, indent=2))
        raise SystemExit(1)

    records = []
    for seed in seeds:
        result = run_seed("ACTIVE", seed, phase_cfg, include_debug=True)
        debug = result["debug"]
        records.append({
            "seed": seed,
            "icq_ra": float(result["icq_ra"]),
            "obs_distance": float(result["obs_distance"]),
            "per_intervention": result["per_intervention"],
            "valid_cells": result["valid_cells"],
            "dataset_sha256": debug["dataset_sha256"]["combined"],
            "debug_pass": bool(debug["debug_pass"]),
            "input_invariants_pass": bool(debug["input_invariants"]["all_pass"]),
            "estimator_reconstruction_pass": bool(
                debug["estimator_reconstruction"]["all_pass"]
            ),
        })

    values = [r["icq_ra"] for r in records]
    stats = summarize(values)
    all_debug_pass = all(r["debug_pass"] for r in records)

    checks = {
        **preflight,
        "run_count_exact": len(records) == int(gate_cfg["expected_run_count"]),
        "all_debug_pass": bool(all_debug_pass),
        "active_mean_icq_ra_ge_frozen_0_15": stats["mean"] >= frozen_threshold,
    }

    decision = "PASS" if all(checks.values()) else "FAIL"
    payload = {
        "protocol_id": gate_cfg["protocol_id"],
        "gate": gate_cfg["gate"],
        "decision": decision,
        "phase0a_config_sha256": config_fingerprint(phase_cfg),
        "heldout_seed_bank_id": gate_cfg["heldout_seed_bank_id"],
        "heldout_seeds": seeds,
        "checks": checks,
        "primary_metric": gate_cfg["primary_metric"],
        "primary_threshold": frozen_threshold,
        "active_icq_ra": stats,
        "records": records,
        "claim_ceiling": gate_cfg["claim_ceiling"],
        "next_gate_if_pass": "P0A-4_CONFOUNDED_FALSIFICATION_OR_PHASE0A_GATE_REVIEW",
        "phase0a_qualification_authorized": False,
        "confirmatory_run_authorized": False,
        "qualia_claim_authorized": False,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({
        "protocol_id": payload["protocol_id"],
        "gate": payload["gate"],
        "decision": payload["decision"],
        "heldout_seed_bank_id": payload["heldout_seed_bank_id"],
        "checks": payload["checks"],
        "primary_threshold": payload["primary_threshold"],
        "active_icq_ra": payload["active_icq_ra"],
        "next_gate_if_pass": payload["next_gate_if_pass"],
    }, indent=2, ensure_ascii=False))

    raise SystemExit(0 if decision == "PASS" else 1)


if __name__ == "__main__":
    main()
