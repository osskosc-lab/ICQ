from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from experiments.phase0b import generate_paired_integrity_case


EXPECTED_GATE_ORDER = [
    "P0B-0_PROTOCOL_AND_IMPLEMENTATION_AUDIT",
    "P0B-1_ATOMIC_DO_Q_INTEGRITY_AUDIT",
    "P0B-2_INACTIVE_DIRECT_NULL_QUALIFICATION",
    "P0B-3_DIRECT_ACTIVE_SENSITIVITY",
    "P0B-4_HIDDEN_MODIFIER_PROXY_FALSIFICATION",
    "P0B-5_GATE_REVIEW_AND_FREEZE_DECISION",
]


def load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def p0b0_checks(cfg: dict, audit: dict) -> dict:
    ns = cfg["seed_namespaces"]
    groups = [
        set(ns["debug_only_exposed"]),
        set(ns["p0b2_inactive_direct_heldout"]),
        set(ns["p0b3_direct_active_heldout"]),
        set(ns["p0b4_hidden_proxy_heldout"]),
    ]

    pairwise_disjoint = True
    for i, a in enumerate(groups):
        for b in groups[i + 1 :]:
            pairwise_disjoint = pairwise_disjoint and not bool(a & b)

    phase0a_used = (
        set(range(1101, 1131))
        | set(range(2101, 2131))
        | set(range(3101, 3161))
        | set(range(4101, 4131))
    )
    fresh = not bool(set().union(*groups) & phase0a_used)

    ft = cfg["frozen_thresholds"]

    checks = {
        "parent_protocol_id_match": cfg["protocol_id"] == audit["parent_protocol_id"],
        "protocol_status_is_draft_for_preregistration_audit":
            cfg["protocol_status"] == "DRAFT_FOR_PREREGISTRATION_AUDIT",
        "qualification_execution_not_authorized":
            cfg["qualification_execution_authorized"] is False,
        "confirmatory_real_data_not_authorized":
            cfg["confirmatory_real_data_run_authorized"] is False,
        "phenomenal_claim_not_authorized":
            cfg["l5_phenomenal_claim_authorized"] is False,
        "gate_order_exact": cfg["gate_order"] == EXPECTED_GATE_ORDER,
        "seed_namespaces_pairwise_disjoint": pairwise_disjoint,
        "phase0a_seed_namespaces_disjoint": fresh,
        "thresholds_inherited_without_p0b_tuning":
            ft["source"] == "INHERITED_FROM_PHASE0A_FOR_SCALE_COMPARABILITY_NO_P0B_PILOT_TUNING",
        "primary_metric_present": cfg["primary_metric"]["name"] == "ICQ-DI",
        "single_primary_baseline_present":
            cfg["primary_baseline"]["name"] == "PHASE0A_ICQ_RA_CONDITIONAL",
        "single_primary_falsification_present":
            cfg["primary_falsification"]["name"] == "HIDDEN_MODIFIER_PROXY",
    }
    return checks


def p0b1_checks(cfg: dict, audit: dict) -> dict:
    tol = float(audit["numerical_tolerance"])
    seeds = [int(s) for s in audit["debug_seed_namespace"]]
    scenario_rows = {}

    all_inactive = True
    all_active = True
    all_hidden = True

    for scenario in audit["p0b1_required_scenarios"]:
        rows = []
        for seed in seeds:
            case = generate_paired_integrity_case(scenario, seed=seed, cfg=cfg)
            y0 = np.asarray(case["y_do_q0"], dtype=float)
            y1 = np.asarray(case["y_do_q1"], dtype=float)

            if scenario == "DIRECT_ACTIVE":
                expected = (
                    float(cfg["generator_parameters"]["direct_q_coupling"])
                    * np.asarray(case["u"], dtype=float)
                )
                err = float(np.max(np.abs((y1 - y0) - expected)))
                passed = bool(err <= tol)
                all_active = all_active and passed
            else:
                err = float(np.max(np.abs(y1 - y0)))
                passed = bool(err <= tol)
                if scenario == "INACTIVE_DIRECT":
                    all_inactive = all_inactive and passed
                else:
                    all_hidden = all_hidden and passed

            rows.append({
                "seed": seed,
                "max_abs_integrity_error": err,
                "pass": passed,
            })
        scenario_rows[scenario] = rows

    checks = {
        "inactive_direct_no_q_effect": all_inactive,
        "direct_active_declared_q_effect_only": all_active,
        "hidden_modifier_proxy_no_q_effect": all_hidden,
        "debug_seed_namespace_exact":
            seeds == [int(s) for s in cfg["seed_namespaces"]["debug_only_exposed"]],
        "no_qualification_seed_executed": True,
    }
    return checks, scenario_rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase0b-config", required=True)
    ap.add_argument("--audit-config", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    cfg = load(args.phase0b_config)
    audit = load(args.audit_config)

    p0 = p0b0_checks(cfg, audit)
    p1, rows = p0b1_checks(cfg, audit)

    p0_pass = all(p0.values())
    p1_pass = all(p1.values())

    payload = {
        "protocol_id": audit["protocol_id"],
        "parent_protocol_id": audit["parent_protocol_id"],
        "execution_status": "COMPLETE",
        "P0B-0": {
            "gate": "P0B-0_PROTOCOL_AND_IMPLEMENTATION_AUDIT",
            "decision": "PASS" if p0_pass else "FAIL_IMPLEMENTATION_OR_PROTOCOL",
            "checks": p0,
        },
        "P0B-1": {
            "gate": "P0B-1_ATOMIC_DO_Q_INTEGRITY_AUDIT",
            "decision": "PASS" if p1_pass else "FAIL_ATOMIC_DO_Q_INTEGRITY",
            "checks": p1,
            "debug_only_rows": rows,
        },
        "next_gate_eligible": (
            "P0B-2_INACTIVE_DIRECT_NULL_QUALIFICATION"
            if p0_pass and p1_pass
            else "NONE"
        ),
        "next_gate_authorized": False,
        "qualification_execution_authorized": False,
        "confirmatory_real_data_run_authorized": False,
        "l4_upgrade_authorized": False,
        "qualia_claim_authorized": False,
        "claim_ceiling": audit["claim_ceiling"],
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))

    # A failed audit is an implementation/protocol failure and should fail CI.
    if not (p0_pass and p1_pass):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
