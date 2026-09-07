import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_p0b4_execution_is_explicitly_authorized_for_one_shot_only():
    e = load("configs/p0b4_execution.json")
    assert e["implementation_status"] == "IMPLEMENTATION_AUDIT_PASS_AUTHORIZED_FOR_ONE_SHOT"
    assert e["execution_authorized"] is True
    assert e["authorization_status"] == "EXPLICITLY_AUTHORIZED_FOR_ONE_SHOT"
    assert e["authorized_parent_head_sha"] == "7fb6d0d1c4101dbcd9ae094a6a92f65693d4e5e5"
    assert e["one_shot_only"] is True
    assert e["authorization_evidence"]["scope"] == "P0B-4_HIDDEN_MODIFIER_PROXY_FALSIFICATION_ONLY"
    assert e["authorization_evidence"]["p0b5_authorized"] is False
    assert e["authorization_evidence"]["l4_upgrade_authorized"] is False


def test_p0b4_execution_contract_matches_frozen_design():
    e = load("configs/p0b4_execution.json")
    d = load("configs/p0b4_design.json")
    assert e["parent_protocol_id"] == d["protocol_id"]
    assert e["gate"] == d["gate"]
    assert e["scenario"] == d["scenario"] == "HIDDEN_MODIFIER_PROXY"
    assert e["dag"] == d["dag"] == "Z -> Q; Z x U -> Y; Q -/-> Y"
    assert e["heldout_seed_bank_id"] == d["heldout_seed_bank_id"]
    assert e["heldout_seeds"] == d["heldout_seeds"] == list(range(6401, 6431))
    assert e["expected_seed_count"] == d["expected_seed_count"] == 30
    assert e["baseline_threshold_min"] == d["frozen_thresholds"]["phase0a_baseline"]["value"] == 0.15
    assert e["direct_threshold_max"] == d["frozen_thresholds"]["direct_intervention"]["value"] == 0.05
    assert e["scientific_source_snapshot"] == d["scientific_source_snapshot"]
    assert e["parent_config_semantic_freeze"] == {
        "generator_parameters": d["parent_config_semantic_freeze"]["generator_parameters"],
        "estimator_parameters": d["parent_config_semantic_freeze"]["estimator_parameters"],
    }


def test_p0b4_runner_and_one_shot_workflow_are_installed_after_freeze():
    assert (ROOT / "experiments/p0b4_qualify.py").exists()
    assert (ROOT / ".github/workflows/p0b4_execute.yml").exists()
    e = load("configs/p0b4_execution.json")
    assert e["execution_authorized"] is True
    assert not (ROOT / e["result_repo_path"]).exists()
    assert e["claim_firewall"]["p0b5_execution_authorized"] is False
    assert e["claim_firewall"]["general_l4_structural_identification_authorized"] is False
    assert e["claim_firewall"]["qualia_or_phenomenal_claim_authorized"] is False
