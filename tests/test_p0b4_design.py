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

def test_p0b4_design_is_frozen_but_not_authorized():
    d = load("configs/p0b4_design.json")
    assert d["protocol_id"] == "ICQ-RA-P0B-4-v0.1"
    assert d["gate"] == "P0B-4_HIDDEN_MODIFIER_PROXY_FALSIFICATION"
    assert d["design_status"] == "FROZEN_AWAITING_EXPLICIT_ONE_SHOT_AUTHORIZATION"
    assert d["execution_contract"]["execution_authorized"] is False
    assert d["execution_contract"]["one_shot_only"] is True
    assert d["result_schema_after_authorized_execution"]["result_field_present_now"] is False
    assert not (ROOT / "experiments/p0b4_qualify.py").exists()
    assert not (ROOT / ".github/workflows/p0b4_execute.yml").exists()

def test_p0b4_prerequisites_and_parent_state_are_exact():
    d = load("configs/p0b4_design.json")
    p = load("configs/phase0b.json")
    for gate, expected in d["prerequisites"].items():
        assert p["completed_gates"][gate] == expected
    assert p["current_gate"] == "P0B-4_HIDDEN_MODIFIER_PROXY_FALSIFICATION"
    assert p["current_gate_eligible"] is True
    assert p["current_gate_execution_authorized"] is False

def test_p0b4_seed_bank_is_exact_unique_and_disjoint():
    d = load("configs/p0b4_design.json")
    p = load("configs/phase0b.json")
    seeds = d["heldout_seeds"]
    assert seeds == list(range(6401, 6431))
    assert d["expected_seed_count"] == 30
    assert len(seeds) == 30
    assert len(set(seeds)) == 30
    assert seeds == p["seed_namespaces"]["p0b4_hidden_proxy_heldout"]
    other = (
        set(p["seed_namespaces"]["debug_only_exposed"])
        | set(p["seed_namespaces"]["p0b2_inactive_direct_heldout"])
        | set(p["seed_namespaces"]["p0b3_direct_active_heldout"])
        | set(range(1101, 1131))
        | set(range(2101, 2131))
        | set(range(3101, 3161))
        | set(range(4101, 4131))
    )
    assert not (set(seeds) & other)

def test_p0b4_dual_metrics_and_thresholds_are_exactly_inherited():
    d = load("configs/p0b4_design.json")
    p = load("configs/phase0b.json")
    assert d["scenario"] == "HIDDEN_MODIFIER_PROXY"
    assert d["dag"] == "Z -> Q; Z x U -> Y; Q -/-> Y"
    assert d["primary_metrics"]["joint_gate_rule"] == "BOTH_METRICS_REQUIRED_AND_NO_SUBSTITUTION"
    assert d["parent_config_semantic_freeze"]["generator_parameters"] == p["generator_parameters"]
    assert d["parent_config_semantic_freeze"]["estimator_parameters"] == p["estimator_parameters"]
    assert d["scientific_source_snapshot_policy"] == "CODE_AND_DEPENDENCY_BLOBS_EXACT; STATE_BEARING_PARENT_CONFIG_FROZEN_BY_SEMANTIC_FIELDS"
    b = d["frozen_thresholds"]["phase0a_baseline"]
    q = d["frozen_thresholds"]["direct_intervention"]
    assert b["operator"] == ">=" and b["value"] == 0.15
    assert q["operator"] == "<=" and q["value"] == 0.05
    assert b["value"] == p["frozen_thresholds"]["hidden_proxy_phase0a_baseline_mean_min"]
    assert q["value"] == p["frozen_thresholds"]["hidden_proxy_direct_mean_max"]
    assert "mean_seed(Phase0A ICQ-RA) >= 0.15" in d["decision_rule"]["PASS"]
    assert "mean_seed(ICQ-DI) <= 0.05" in d["decision_rule"]["PASS"]

def test_p0b4_scientific_source_snapshot_is_exact_at_design_freeze():
    d = load("configs/p0b4_design.json")
    result_path = ROOT / "configs/p0b4_result.json"
    if result_path.exists():
        r = load("configs/p0b4_result.json")
        assert r["scientific_source_snapshot"] == d["scientific_source_snapshot"]
        assert r["execution_status"] == "COMPLETE_VALID_SCIENTIFIC_DECISION"
    else:
        for path, expected_sha in d["scientific_source_snapshot"].items():
            assert git_blob_sha(path) == expected_sha, path

def test_p0b4_state_transitions_preserve_claim_firewall():
    d = load("configs/p0b4_design.json")
    assert d["next_state_if_pass"]["next_gate"] == "P0B-5_GATE_REVIEW_AND_FREEZE_DECISION"
    assert d["next_state_if_pass"]["next_gate_execution_authorized"] is False
    assert d["next_state_if_pass"]["l4_upgrade_authorized_before_p0b5"] is False
    assert d["next_state_if_fail"]["p0b5_gate_review_required"] is True
    assert d["claim_firewall"]["general_l4_structural_identification_authorized"] is False
    assert d["claim_firewall"]["directly_intervenable_synthetic_q_l4_upgrade_authorized_before_p0b5"] is False
    assert d["claim_firewall"]["real_system_identification_authorized"] is False
    assert d["claim_firewall"]["qualia_or_phenomenal_claim_authorized"] is False
