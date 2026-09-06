from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from phase0b import estimate_direct_seed


def load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase0b-config", required=True)
    ap.add_argument("--execution-config", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    cfg = load(args.phase0b_config)
    exe = load(args.execution_config)

    gate = "P0B-2_INACTIVE_DIRECT_NULL_QUALIFICATION"
    if exe["gate"] != gate:
        raise SystemExit("P0B2_PREFLIGHT_FAIL: gate mismatch")

    completed = cfg.get("completed_gates", {})
    for k, v in exe["prerequisites"].items():
        if completed.get(k) != v:
            raise SystemExit(f"P0B2_PREFLIGHT_FAIL: prerequisite {k} != {v}")

    if cfg.get("current_gate") != gate:
        raise SystemExit("P0B2_PREFLIGHT_FAIL: current_gate mismatch")
    if cfg.get("current_gate_eligible") is not True:
        raise SystemExit("P0B2_PREFLIGHT_FAIL: current gate not eligible")

    seeds = [int(x) for x in exe["heldout_seeds"]]
    cfg_seeds = [int(x) for x in cfg["seed_namespaces"]["p0b2_inactive_direct_heldout"]]
    if seeds != cfg_seeds:
        raise SystemExit("P0B2_PREFLIGHT_FAIL: heldout seed bank mismatch")
    if len(seeds) != int(exe["expected_seed_count"]) or len(set(seeds)) != len(seeds):
        raise SystemExit("P0B2_PREFLIGHT_FAIL: seed count/uniqueness")

    debug = set(int(x) for x in cfg["seed_namespaces"]["debug_only_exposed"])
    later = (
        set(int(x) for x in cfg["seed_namespaces"]["p0b3_direct_active_heldout"])
        | set(int(x) for x in cfg["seed_namespaces"]["p0b4_hidden_proxy_heldout"])
    )
    if set(seeds) & debug:
        raise SystemExit("P0B2_PREFLIGHT_FAIL: overlap with debug seeds")
    if set(seeds) & later:
        raise SystemExit("P0B2_PREFLIGHT_FAIL: overlap with later qualification seeds")

    threshold = float(exe["frozen_threshold"]["value"])
    cfg_threshold = float(cfg["frozen_thresholds"]["direct_null_mean_max"])
    if threshold != cfg_threshold:
        raise SystemExit("P0B2_PREFLIGHT_FAIL: threshold mismatch")

    rows = [estimate_direct_seed("INACTIVE_DIRECT", seed, cfg) for seed in seeds]
    values = np.asarray([float(r["icq_di"]) for r in rows], dtype=float)

    stats = {
        "n": int(values.size),
        "mean": float(np.mean(values)),
        "std": float(np.std(values, ddof=1)),
        "median": float(np.median(values)),
        "q05": float(np.quantile(values, 0.05)),
        "q95": float(np.quantile(values, 0.95)),
        "min": float(np.min(values)),
        "max": float(np.max(values)),
    }

    decision = "PASS" if stats["mean"] <= threshold else "FAIL_NULL_CONTROL"

    payload = {
        "protocol_id": exe["protocol_id"],
        "parent_protocol_id": exe["parent_protocol_id"],
        "gate": gate,
        "execution_status": "COMPLETE",
        "scenario": "INACTIVE_DIRECT",
        "heldout_seed_bank_id": exe["heldout_seed_bank_id"],
        "seed_count": len(seeds),
        "seeds": seeds,
        "primary_metric": exe["primary_metric"],
        "frozen_threshold": threshold,
        "stats": stats,
        "decision": decision,
        "rows": rows,
        "later_gates_authorized": False,
        "confirmatory_real_data_run_authorized": False,
        "l4_upgrade_authorized": False,
        "qualia_claim_authorized": False,
        "claim_ceiling": "P0B2_INACTIVE_DIRECT_NULL_QUALIFICATION_ONLY"
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))

    # Scientific FAIL is a valid result. Only preflight/implementation errors fail CI.
    raise SystemExit(0)


if __name__ == "__main__":
    main()
