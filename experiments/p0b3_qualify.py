from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

import numpy as np

from experiments.phase0b import estimate_direct_seed


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def git_blob_sha(path: str) -> str:
    data = (ROOT / path).read_bytes()
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def stop(reason: str, details: dict | None = None) -> None:
    payload = {
        "execution_status": "STOP_INTEGRITY_NO_SCIENTIFIC_DECISION",
        "reason": reason,
        "details": details or {},
    }
    print(json.dumps(payload, indent=2))
    raise SystemExit(2)


def require(condition: bool, reason: str, details: dict | None = None) -> None:
    if not condition:
        stop(reason, details)


def main() -> None:
    exec_cfg = load_json("configs/p0b3_execution.json")
    design = load_json("configs/p0b3_design.json")
    phase0b = load_json("configs/phase0b.json")

    require(exec_cfg["execution_authorized"] is True, "EXECUTION_NOT_AUTHORIZED")
    require(exec_cfg["authorization_status"] == "EXPLICITLY_AUTHORIZED_FOR_ONE_SHOT",
            "AUTHORIZATION_STATUS_MISMATCH")
    require(os.environ.get("GITHUB_EVENT_NAME") == exec_cfg["required_event"],
            "EVENT_MISMATCH", {"event": os.environ.get("GITHUB_EVENT_NAME")})
    require(int(os.environ.get("GITHUB_RUN_ATTEMPT", "0")) == int(exec_cfg["required_run_attempt"]),
            "RERUN_ATTEMPT_PROHIBITED",
            {"run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT")})

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    parent = subprocess.check_output(["git", "rev-parse", "HEAD^"], cwd=ROOT, text=True).strip()
    require(parent == exec_cfg["authorized_parent_head_sha"],
            "AUTHORIZATION_PARENT_HEAD_MISMATCH",
            {"observed_parent": parent, "expected_parent": exec_cfg["authorized_parent_head_sha"]})

    msg = subprocess.check_output(["git", "log", "-1", "--pretty=%B"], cwd=ROOT, text=True)
    require(exec_cfg["required_commit_message_token"] in msg,
            "AUTHORIZATION_COMMIT_TOKEN_MISSING")

    require(design["protocol_id"] == exec_cfg["parent_protocol_id"], "DESIGN_PROTOCOL_MISMATCH")
    require(design["design_status"] == exec_cfg["preflight"]["require_design_status"],
            "DESIGN_STATUS_MISMATCH")
    require(design["execution_contract"]["one_shot_only"] is True, "DESIGN_ONE_SHOT_MISMATCH")

    require(phase0b["current_gate"] == exec_cfg["preflight"]["require_phase0b_current_gate"],
            "CURRENT_GATE_MISMATCH")
    require(phase0b["current_gate_eligible"] is True, "CURRENT_GATE_NOT_ELIGIBLE")

    for gate in exec_cfg["preflight"]["require_prerequisites_pass"]:
        require(phase0b["completed_gates"].get(gate) == "PASS",
                "MISSING_PREREQUISITE_PASS", {"gate": gate})

    require(exec_cfg["scenario"] == "DIRECT_ACTIVE", "SCENARIO_MISMATCH")
    seeds = [int(s) for s in exec_cfg["heldout_seeds"]]
    require(seeds == list(range(6301, 6331)), "SEED_ORDER_OR_BANK_MISMATCH")
    require(len(seeds) == exec_cfg["expected_seed_count"] == 30, "SEED_COUNT_MISMATCH")
    require(len(set(seeds)) == 30, "DUPLICATE_SEED")

    pns = phase0b["seed_namespaces"]
    require(seeds == [int(s) for s in pns["p0b3_direct_active_heldout"]],
            "PARENT_SEED_BANK_MISMATCH")
    forbidden = (
        set(pns["debug_only_exposed"])
        | set(pns["p0b2_inactive_direct_heldout"])
        | set(pns["p0b4_hidden_proxy_heldout"])
        | set(range(1101, 1131))
        | set(range(2101, 2131))
        | set(range(3101, 3161))
        | set(range(4101, 4131))
    )
    require(not (set(seeds) & forbidden), "HELDOUT_SEED_OVERLAP")

    threshold = float(exec_cfg["threshold_min"])
    require(threshold == float(design["frozen_threshold"]["value"]) == 0.15,
            "THRESHOLD_MISMATCH")
    require(phase0b["frozen_thresholds"]["direct_active_mean_min"] == threshold,
            "PARENT_THRESHOLD_MISMATCH")

    for path, expected in exec_cfg["scientific_source_snapshot"].items():
        observed = git_blob_sha(path)
        require(observed == expected, "SOURCE_SNAPSHOT_MISMATCH",
                {"path": path, "observed": observed, "expected": expected})

    result_repo_path = ROOT / exec_cfg["result_repo_path"]
    require(not result_repo_path.exists(), "PRIOR_P0B3_RESULT_ALREADY_PRESENT")

    rows = []
    for seed in seeds:
        row = estimate_direct_seed("DIRECT_ACTIVE", seed, phase0b)
        require(int(row["seed"]) == seed, "RESULT_SEED_MISMATCH", {"seed": seed})
        require(row["scenario"] == "DIRECT_ACTIVE", "RESULT_SCENARIO_MISMATCH", {"seed": seed})
        value = float(row["icq_di"])
        require(np.isfinite(value), "NONFINITE_RESULT", {"seed": seed, "value": value})
        rows.append(row)

    require(len(rows) == 30, "INCOMPLETE_RESULT_COUNT")
    observed_seeds = [int(r["seed"]) for r in rows]
    require(observed_seeds == seeds, "RESULT_ORDER_MISMATCH")
    require(len(set(observed_seeds)) == 30, "DUPLICATE_RESULT_SEED")

    values = np.asarray([float(r["icq_di"]) for r in rows], dtype=float)
    mean = float(np.mean(values))
    decision = "PASS" if mean >= threshold else "FAIL_SENSITIVITY"

    payload = {
        "protocol_id": design["protocol_id"],
        "heldout_seed_bank_id": exec_cfg["heldout_seed_bank_id"],
        "execution_status": "COMPLETE_VALID_SCIENTIFIC_DECISION",
        "execution_head_sha": head,
        "execution_parent_sha": parent,
        "workflow_run": int(os.environ["GITHUB_RUN_ID"]),
        "workflow_run_attempt": int(os.environ["GITHUB_RUN_ATTEMPT"]),
        "artifact_name": exec_cfg["artifact_name"],
        "scientific_source_snapshot": exec_cfg["scientific_source_snapshot"],
        "n": int(values.size),
        "per_seed_icq_di": [
            {
                "seed": int(r["seed"]),
                "icq_di": float(r["icq_di"]),
                "per_intervention": r["per_intervention"],
                "valid_cells": r["valid_cells"],
            }
            for r in rows
        ],
        "mean": mean,
        "sample_std_ddof_1": float(np.std(values, ddof=1)),
        "median": float(np.median(values)),
        "q05": float(np.quantile(values, 0.05, method="linear")),
        "q95": float(np.quantile(values, 0.95, method="linear")),
        "min": float(np.min(values)),
        "max": float(np.max(values)),
        "threshold_min": threshold,
        "primary_metric": "mean_seed(ICQ-DI)",
        "decision": decision,
        "claim_ceiling": "DIRECT_ACTIVE_SYNTHETIC_SENSITIVITY_ONLY",
        "p0b4_execution_authorized": False,
        "general_l4_upgrade_authorized": False,
        "confirmatory_real_data_run_authorized": False,
        "qualia_or_phenomenal_claim_authorized": False,
    }

    out = ROOT / exec_cfg["result_path"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
