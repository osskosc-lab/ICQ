from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase0a import run_seed
from icq_ra.debug import config_fingerprint


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description="ICQ-RA P0A-1 reproducibility manifest")
    parser.add_argument("--phase0a-config", required=True)
    parser.add_argument("--pilot-config", required=True)
    parser.add_argument("--order", choices=["forward", "reverse"], required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    cfg = load_json(args.phase0a_config)
    pilot = load_json(args.pilot_config)

    scenarios = list(pilot["scenarios"])
    seeds = [int(x) for x in pilot["seeds"]]
    cases = [(scenario, seed) for scenario in scenarios for seed in seeds]
    if args.order == "reverse":
        cases = list(reversed(cases))

    records = {}
    for scenario, seed in cases:
        result = run_seed(scenario, seed, cfg, include_debug=True)
        debug = result["debug"]
        key = f"{scenario}:{seed}"
        records[key] = {
            "scenario": scenario,
            "seed": seed,
            "dataset_sha256": debug["dataset_sha256"],
            "config_sha256": debug["config_sha256"],
            "icq_ra": result["icq_ra"],
            "obs_distance": result["obs_distance"],
            "per_intervention": result["per_intervention"],
            "valid_cells": result["valid_cells"],
            "debug_pass": debug["debug_pass"],
            "estimator_reconstruction_pass": debug["estimator_reconstruction"]["all_pass"],
            "input_invariants_pass": debug["input_invariants"]["all_pass"],
        }

    payload = {
        "protocol_id": pilot["protocol_id"],
        "gate": pilot["gate"],
        "mode": "P0A1_REPRODUCIBILITY_MANIFEST",
        "execution_order": args.order,
        "phase0a_config_sha256": config_fingerprint(cfg),
        "pilot_config": pilot,
        "case_count": len(records),
        "records": records,
        "claim_level": "REPRODUCIBILITY_PILOT_ONLY",
        "phase0a_qualification_decision": "NOT_EVALUATED",
        "qualia_claim_authorized": False,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({
        "protocol_id": payload["protocol_id"],
        "order": args.order,
        "case_count": payload["case_count"],
        "all_debug_pass": all(r["debug_pass"] for r in records.values()),
    }, indent=2))


if __name__ == "__main__":
    main()
