from __future__ import annotations

import argparse
import json
from pathlib import Path


FIELDS_EXACT = [
    "dataset_sha256",
    "config_sha256",
    "icq_ra",
    "obs_distance",
    "per_intervention",
    "valid_cells",
]


def load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description="Compare two P0A-1 manifests")
    parser.add_argument("--a", required=True)
    parser.add_argument("--b", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    a = load(args.a)
    b = load(args.b)

    checks = {
        "protocol_id_match": a["protocol_id"] == b["protocol_id"],
        "phase0a_config_sha256_match": a["phase0a_config_sha256"] == b["phase0a_config_sha256"],
        "case_key_set_match": set(a["records"]) == set(b["records"]),
        "case_count_is_9": len(a["records"]) == 9 and len(b["records"]) == 9,
        "execution_order_differs": a["execution_order"] != b["execution_order"],
    }

    case_results = {}
    if checks["case_key_set_match"]:
        for key in sorted(a["records"]):
            ra = a["records"][key]
            rb = b["records"][key]
            field_checks = {field: ra[field] == rb[field] for field in FIELDS_EXACT}
            field_checks["debug_pass_a"] = bool(ra["debug_pass"])
            field_checks["debug_pass_b"] = bool(rb["debug_pass"])
            field_checks["estimator_reconstruction_a"] = bool(ra["estimator_reconstruction_pass"])
            field_checks["estimator_reconstruction_b"] = bool(rb["estimator_reconstruction_pass"])
            field_checks["input_invariants_a"] = bool(ra["input_invariants_pass"])
            field_checks["input_invariants_b"] = bool(rb["input_invariants_pass"])
            case_results[key] = {
                "checks": field_checks,
                "pass": all(field_checks.values()),
            }

    all_cases_pass = len(case_results) == 9 and all(x["pass"] for x in case_results.values())
    checks["all_9_cases_exact_match_and_debug_pass"] = all_cases_pass

    decision = "PASS" if all(checks.values()) else "FAIL"
    payload = {
        "protocol_id": a["protocol_id"],
        "gate": "P0A-1_SEED_REPRODUCIBILITY_PILOT",
        "decision": decision,
        "checks": checks,
        "case_results": case_results,
        "claim_ceiling": "DETERMINISTIC_SEED_REPRODUCIBILITY_ONLY",
        "next_gate_if_pass": "P0A-2_NULL_CALIBRATION",
        "phase0a_qualification_authorized": False,
        "confirmatory_run_authorized": False,
        "qualia_claim_authorized": False,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    raise SystemExit(0 if decision == "PASS" else 1)


if __name__ == "__main__":
    main()
