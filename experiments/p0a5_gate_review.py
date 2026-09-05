from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def get_decision(payload: dict) -> str:
    for key in ("decision", "scientific_decision", "qualification_status"):
        if key in payload:
            return str(payload[key])
    raise KeyError("No recognized decision field.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    gate = load(args.config)
    observed = {}
    for key, path in gate["inputs"].items():
        observed[key] = get_decision(load(path))

    required = gate["required_results"]
    checks = {key: observed.get(key) == value for key, value in required.items()}
    exact_chain_match = all(checks.values())

    if exact_chain_match:
        final_verdict = gate["final_verdict_if_required_results_match"]
        phase0a_status = gate["phase0a_status_if_required_results_match"]
        levels = gate["freeze_policy"]
        gate_decision = "FREEZE_APPROVED_WITH_SCOPE_LIMITATION"
    else:
        final_verdict = "HOLD_FOR_REVIEW"
        phase0a_status = "NOT_FROZEN"
        levels = {}
        gate_decision = "FREEZE_NOT_APPROVED"

    payload = {
        "protocol_id": gate["protocol_id"],
        "gate": gate["gate"],
        "execution_status": "COMPLETE",
        "gate_decision": gate_decision,
        "final_verdict": final_verdict,
        "phase0a_status": phase0a_status,
        "observed_results": observed,
        "required_results": required,
        "checks": checks,
        "supported_scope": levels,
        "core_conclusion": (
            "OPERATIONALLY_USEFUL_NOT_STRUCTURALLY_IDENTIFIED"
            if exact_chain_match else "NOT_FIXED"
        ),
        "confirmatory_real_data_run_authorized": False,
        "qualia_claim_authorized": False,
        "l4_upgrade_authorized": False,
        "next_action": gate["next_action"],
        "claim_ceiling": (
            "ICQ_RA_IS_A_SYNTHETIC_RESPONSE_ACCESSIBILITY_DETECTOR_WITHIN_DECLARED_PHASE0A_CONDITIONS"
            if exact_chain_match else "NO_NEW_CLAIM"
        )
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))

    # A B-verdict / L4 rejection is a valid scientific endpoint.
    raise SystemExit(0)


if __name__ == "__main__":
    main()
