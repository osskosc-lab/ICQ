from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

import numpy as np

from experiments.phase0b import estimate_direct_seed, estimate_hidden_proxy_baseline


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


def stats(values: np.ndarray) -> dict:
    return {
        "n": int(values.size),
        "mean": float(np.mean(values)),
        "sample_std_ddof_1": float(np.std(values, ddof=1)),
        "median": float(np.median(values)),
        "q05": float(np.quantile(values, 0.05, method="linear")),
        "q95": float(np.quantile(values, 0.95, method="linear")),
        "min": float(np.min(values)),
        "max": float(np.max(values)),
    }


def main() -> None:
    exec_cfg = load_json("configs/p0b4_execution.json")
    design = load_json("configs/p0b4_design.json")
    phase0b = load_json("configs/phase0b.json")

    require(exec_cfg["execution_authorized"] is True, "EXECUTION_NOT_AUTHORIZED")
    require(
        exec_cfg["authorization_status"] == "EXPLICITLY_AUTHORIZED_FOR_ONE_SHOT",
        "AUTHORIZATION_STATUS_MISMATCH",
    )
    require(
        os.environ.get("GITHUB_EVENT_NAME") == exec_cfg["required_event"],
        "EVENT_MISMATCH",
        {"event": os.environ.get("GITHUB_EVENT_NAME")},
    )
    require(
        int(os.environ.get("GITHUB_RUN_ATTEMPT", "0"))
        == int(exec_cfg["required_run_attempt"]),
        "RERUN_ATTEMPT_PROHIBITED",
        {"run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT")},
    )

    head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    parent = subprocess.check_output(
        ["git", "rev-parse", "HEAD^"], cwd=ROOT, text=True
    ).strip()
    require(
        parent == exec_cfg["authorized_parent_head_sha"],
        "AUTHORIZATION_PARENT_HEAD_MISMATCH",
        {
            "observed_parent": parent,
            "expected_parent": exec_cfg["authorized_parent_head_sha"],
        },
    )

    msg = subprocess.check_output(
        ["git", "log", "-1", "--pretty=%B"], cwd=ROOT, text=True
    )
    require(
        exec_cfg["required_commit_message_token"] in msg,
        "AUTHORIZATION_COMMIT_TOKEN_MISSING",
    )

    require(
        design["protocol_id"] == exec_cfg["parent_protocol_id"],
        "DESIGN_PROTOCOL_MISMATCH",
    )
    require(
        design["design_status"] == exec_cfg["preflight"]["require_design_status"],
        "DESIGN_STATUS_MISMATCH",
    )
    require(design["execution_contract"]["one_shot_only"] is True, "DESIGN_ONE_SHOT_MISMATCH")
    require(
        design["dag"] == exec_cfg["dag"] == "Z -> Q; Z x U -> Y; Q -/-> Y",
        "DAG_MISMATCH",
    )

    require(
        phase0b["current_gate"] == exec_cfg["preflight"]["require_phase0b_current_gate"],
        "CURRENT_GATE_MISMATCH",
    )
    require(phase0b["current_gate_eligible"] is True, "CURRENT_GATE_NOT_ELIGIBLE")
    require(
        phase0b["current_gate_execution_authorized"] is False,
        "PARENT_GATE_AUTHORIZATION_STATE_MISMATCH",
    )

    for gate in exec_cfg["preflight"]["require_prerequisites_pass"]:
        require(
            phase0b["completed_gates"].get(gate) == "PASS",
            "MISSING_PREREQUISITE_PASS",
            {"gate": gate},
        )

    require(exec_cfg["scenario"] == "HIDDEN_MODIFIER_PROXY", "SCENARIO_MISMATCH")
    seeds = [int(s) for s in exec_cfg["heldout_seeds"]]
    require(seeds == list(range(6401, 6431)), "SEED_ORDER_OR_BANK_MISMATCH")
    require(
        len(seeds) == exec_cfg["expected_seed_count"] == 30,
        "SEED_COUNT_MISMATCH",
    )
    require(len(set(seeds)) == 30, "DUPLICATE_SEED")

    pns = phase0b["seed_namespaces"]
    require(
        seeds == [int(s) for s in pns["p0b4_hidden_proxy_heldout"]],
        "PARENT_SEED_BANK_MISMATCH",
    )
    forbidden = (
        set(pns["debug_only_exposed"])
        | set(pns["p0b2_inactive_direct_heldout"])
        | set(pns["p0b3_direct_active_heldout"])
        | set(range(1101, 1131))
        | set(range(2101, 2131))
        | set(range(3101, 3161))
        | set(range(4101, 4131))
    )
    require(not (set(seeds) & forbidden), "HELDOUT_SEED_OVERLAP")

    baseline_threshold = float(exec_cfg["baseline_threshold_min"])
    direct_threshold = float(exec_cfg["direct_threshold_max"])
    require(
        baseline_threshold
        == float(design["frozen_thresholds"]["phase0a_baseline"]["value"])
        == 0.15,
        "BASELINE_THRESHOLD_MISMATCH",
    )
    require(
        direct_threshold
        == float(design["frozen_thresholds"]["direct_intervention"]["value"])
        == 0.05,
        "DIRECT_THRESHOLD_MISMATCH",
    )
    require(
        phase0b["frozen_thresholds"]["hidden_proxy_phase0a_baseline_mean_min"]
        == baseline_threshold,
        "PARENT_BASELINE_THRESHOLD_MISMATCH",
    )
    require(
        phase0b["frozen_thresholds"]["hidden_proxy_direct_mean_max"]
        == direct_threshold,
        "PARENT_DIRECT_THRESHOLD_MISMATCH",
    )

    require(
        phase0b["generator_parameters"]
        == exec_cfg["parent_config_semantic_freeze"]["generator_parameters"],
        "PARENT_GENERATOR_SEMANTIC_FREEZE_MISMATCH",
    )
    require(
        phase0b["estimator_parameters"]
        == exec_cfg["parent_config_semantic_freeze"]["estimator_parameters"],
        "PARENT_ESTIMATOR_SEMANTIC_FREEZE_MISMATCH",
    )

    for path, expected in exec_cfg["scientific_source_snapshot"].items():
        observed = git_blob_sha(path)
        require(
            observed == expected,
            "SOURCE_SNAPSHOT_MISMATCH",
            {"path": path, "observed": observed, "expected": expected},
        )

    result_repo_path = ROOT / exec_cfg["result_repo_path"]
    require(not result_repo_path.exists(), "PRIOR_P0B4_RESULT_ALREADY_PRESENT")

    baseline_rows = []
    direct_rows = []
    for seed in seeds:
        baseline = estimate_hidden_proxy_baseline(seed, phase0b)
        direct = estimate_direct_seed("HIDDEN_MODIFIER_PROXY", seed, phase0b)

        require(int(baseline["seed"]) == seed, "BASELINE_RESULT_SEED_MISMATCH", {"seed": seed})
        require(int(direct["seed"]) == seed, "DIRECT_RESULT_SEED_MISMATCH", {"seed": seed})
        require(
            baseline["scenario"] == "HIDDEN_MODIFIER_PROXY_BASELINE",
            "BASELINE_RESULT_SCENARIO_MISMATCH",
            {"seed": seed},
        )
        require(
            direct["scenario"] == "HIDDEN_MODIFIER_PROXY",
            "DIRECT_RESULT_SCENARIO_MISMATCH",
            {"seed": seed},
        )
        require(
            np.isfinite(float(baseline["phase0a_icq_ra"])),
            "NONFINITE_BASELINE_RESULT",
            {"seed": seed},
        )
        require(
            np.isfinite(float(direct["icq_di"])),
            "NONFINITE_DIRECT_RESULT",
            {"seed": seed},
        )

        baseline_rows.append(baseline)
        direct_rows.append(direct)

    require(len(baseline_rows) == 30, "INCOMPLETE_BASELINE_RESULT_COUNT")
    require(len(direct_rows) == 30, "INCOMPLETE_DIRECT_RESULT_COUNT")
    require(
        [int(r["seed"]) for r in baseline_rows] == seeds,
        "BASELINE_RESULT_ORDER_MISMATCH",
    )
    require(
        [int(r["seed"]) for r in direct_rows] == seeds,
        "DIRECT_RESULT_ORDER_MISMATCH",
    )

    baseline_values = np.asarray(
        [float(r["phase0a_icq_ra"]) for r in baseline_rows], dtype=float
    )
    direct_values = np.asarray(
        [float(r["icq_di"]) for r in direct_rows], dtype=float
    )

    baseline_stats = stats(baseline_values)
    direct_stats = stats(direct_values)
    b_ok = baseline_stats["mean"] >= baseline_threshold
    d_ok = direct_stats["mean"] <= direct_threshold

    if b_ok and d_ok:
        decision = "PASS"
    elif (not b_ok) and d_ok:
        decision = "FAIL_BASELINE_REPRODUCTION"
    elif b_ok and (not d_ok):
        decision = "FAIL_DIRECT_FALSE_POSITIVE"
    else:
        decision = "FAIL_BOTH"

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
        "parent_config_semantic_freeze": exec_cfg["parent_config_semantic_freeze"],
        "n": 30,
        "per_seed_phase0a_icq_ra": [
            {
                "seed": int(r["seed"]),
                "phase0a_icq_ra": float(r["phase0a_icq_ra"]),
                "per_intervention": r["per_intervention"],
                "valid_cells": r["valid_cells"],
            }
            for r in baseline_rows
        ],
        "per_seed_icq_di": [
            {
                "seed": int(r["seed"]),
                "icq_di": float(r["icq_di"]),
                "per_intervention": r["per_intervention"],
                "valid_cells": r["valid_cells"],
            }
            for r in direct_rows
        ],
        "phase0a_baseline_mean": baseline_stats["mean"],
        "phase0a_baseline_sample_std_ddof_1": baseline_stats["sample_std_ddof_1"],
        "phase0a_baseline_median": baseline_stats["median"],
        "phase0a_baseline_q05": baseline_stats["q05"],
        "phase0a_baseline_q95": baseline_stats["q95"],
        "phase0a_baseline_min": baseline_stats["min"],
        "phase0a_baseline_max": baseline_stats["max"],
        "direct_mean": direct_stats["mean"],
        "direct_sample_std_ddof_1": direct_stats["sample_std_ddof_1"],
        "direct_median": direct_stats["median"],
        "direct_q05": direct_stats["q05"],
        "direct_q95": direct_stats["q95"],
        "direct_min": direct_stats["min"],
        "direct_max": direct_stats["max"],
        "baseline_threshold_min": baseline_threshold,
        "direct_threshold_max": direct_threshold,
        "decision": decision,
        "claim_ceiling": "HIDDEN_PROXY_SYNTHETIC_DISCRIMINATION_PATTERN_ONLY",
        "p0b5_execution_authorized": False,
        "directly_intervenable_synthetic_q_l4_upgrade_authorized_before_p0b5": False,
        "general_l4_structural_identification_authorized": False,
        "real_system_identification_authorized": False,
        "confirmatory_real_data_run_authorized": False,
        "qualia_or_phenomenal_claim_authorized": False,
    }

    out = ROOT / exec_cfg["result_path"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
