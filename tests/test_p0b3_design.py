import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def git_blob_sha(path):
    data = (ROOT / path).read_bytes()
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def test_p0b3_design_is_frozen_but_not_authorized():
    d = load("configs/p0b3_design.json")
    assert d["protocol_id"] == "ICQ-RA-P0B-3-v0.1"
    assert d["gate"] == "P0B-3_DIRECT_ACTIVE_SENSITIVITY"
    assert d["design_status"] == "FROZEN_AWAITING_EXPLICIT_ONE_SHOT_AUTHORIZATION"
    assert d["execution_contract"]["execution_authorized"] is False
    assert d["execution_contract"]["one_shot_only"] is True
    assert d["result_schema_after_authorized_execution"]["result_field_present_now"] is False


def test_p0b3_prerequisites_and_post_result_parent_state():
    d = load("configs/p0b3_design.json")
    p = load("configs/phase0b.json")

    for gate, expected in d["prerequisites"].items():
        assert p["completed_gates"][gate] == expected

    if "P0B-3_DIRECT_ACTIVE_SENSITIVITY" in p["completed_gates"]:
        assert p["completed_gates"]["P0B-3_DIRECT_ACTIVE_SENSITIVITY"] == "PASS"
        assert p["current_gate"] == "P0B-4_HIDDEN_MODIFIER_PROXY_FALSIFICATION"
        assert p["current_gate_eligible"] is True
        assert p["current_gate_execution_authorized"] is False
    else:
        assert p["current_gate"] == "P0B-3_DIRECT_ACTIVE_SENSITIVITY"
        assert p["current_gate_eligible"] is True
        assert p["current_gate_execution_authorized"] is False


def test_p0b3_seed_bank_is_exact_unique_and_disjoint():
    d = load("configs/p0b3_design.json")
    p = load("configs/phase0b.json")

    seeds = d["heldout_seeds"]
    assert seeds == list(range(6301, 6331))
    assert d["expected_seed_count"] == 30
    assert len(seeds) == 30
    assert len(set(seeds)) == 30
    assert seeds == p["seed_namespaces"]["p0b3_direct_active_heldout"]

    other = (
        set(p["seed_namespaces"]["debug_only_exposed"])
        | set(p["seed_namespaces"]["p0b2_inactive_direct_heldout"])
        | set(p["seed_namespaces"]["p0b4_hidden_proxy_heldout"])
        | set(range(1101, 1131))
        | set(range(2101, 2131))
        | set(range(3101, 3161))
        | set(range(4101, 4131))
    )
    assert not (set(seeds) & other)


def test_p0b3_primary_metric_and_threshold_are_exactly_inherited():
    d = load("configs/p0b3_design.json")
    p = load("configs/phase0b.json")

    assert d["scenario"] == "DIRECT_ACTIVE"
    assert d["primary_metric"]["name"] == "mean_seed(ICQ-DI)"
    assert d["primary_metric"]["only_gate_decision_metric"] is True
    assert d["frozen_threshold"]["operator"] == ">="
    assert d["frozen_threshold"]["value"] == 0.15
    assert d["frozen_threshold"]["value"] == p["frozen_thresholds"]["direct_active_mean_min"]
    assert d["decision_rule"]["PASS"].endswith("mean_seed(ICQ-DI) >= 0.15")
    assert d["decision_rule"]["FAIL_SENSITIVITY"].endswith("mean_seed(ICQ-DI) < 0.15")


def test_p0b3_scientific_source_snapshot_is_preserved_in_result_after_execution():
    d = load("configs/p0b3_design.json")
    result_path = ROOT / "configs/p0b3_result.json"
    if result_path.exists():
        r = load("configs/p0b3_result.json")
        assert r["scientific_source_snapshot"] == d["scientific_source_snapshot"]
        assert r["execution_status"] == "COMPLETE_VALID_SCIENTIFIC_DECISION"
    else:
        for path, expected_sha in d["scientific_source_snapshot"].items():
            assert git_blob_sha(path) == expected_sha, path


def test_p0b3_design_freeze_historically_preceded_execution_implementation():
    d = load("configs/p0b3_design.json")
    assert d["execution_contract"]["qualification_runner_present_at_design_freeze"] is False
    assert d["execution_contract"]["one_shot_workflow_present_at_design_freeze"] is False
    # Runner/workflow may be installed only after the frozen design commit.
    assert d["design_status"] == "FROZEN_AWAITING_EXPLICIT_ONE_SHOT_AUTHORIZATION"


def test_p0b3_state_transitions_preserve_claim_firewall():
    d = load("configs/p0b3_design.json")
    assert d["next_state_if_pass"]["next_gate"] == "P0B-4_HIDDEN_MODIFIER_PROXY_FALSIFICATION"
    assert d["next_state_if_pass"]["next_gate_execution_authorized"] is False
    assert d["next_state_if_fail"]["phase0b_stop"] is True
    assert d["next_state_if_fail"]["p0b4_execution_authorized"] is False
    assert d["claim_firewall"]["general_l4_structural_identification_authorized"] is False
    assert d["claim_firewall"]["real_system_identification_authorized"] is False
    assert d["claim_firewall"]["qualia_or_phenomenal_claim_authorized"] is False
