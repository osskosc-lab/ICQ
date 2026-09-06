import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_p0b3_execution_is_explicitly_authorized_for_one_shot_only():
    e = load("configs/p0b3_execution.json")
    assert e["implementation_status"] == "IMPLEMENTATION_AUDIT_PASS_AUTHORIZED_FOR_ONE_SHOT"
    assert e["execution_authorized"] is True
    assert e["authorization_status"] == "EXPLICITLY_AUTHORIZED_FOR_ONE_SHOT"
    assert e["authorized_parent_head_sha"] == "9b7ed6eb43e2af3d5f7c325cb2e903ef347857fc"
    assert e["one_shot_only"] is True
    assert e["authorization_evidence"]["scope"] == "P0B-3_DIRECT_ACTIVE_SENSITIVITY_ONLY"
    assert e["authorization_evidence"]["p0b4_authorized"] is False


def test_p0b3_execution_contract_matches_frozen_design():
    e = load("configs/p0b3_execution.json")
    d = load("configs/p0b3_design.json")
    assert e["parent_protocol_id"] == d["protocol_id"]
    assert e["gate"] == d["gate"]
    assert e["scenario"] == d["scenario"] == "DIRECT_ACTIVE"
    assert e["heldout_seed_bank_id"] == d["heldout_seed_bank_id"]
    assert e["heldout_seeds"] == d["heldout_seeds"] == list(range(6301, 6331))
    assert e["expected_seed_count"] == d["expected_seed_count"] == 30
    assert e["threshold_min"] == d["frozen_threshold"]["value"] == 0.15
    assert e["scientific_source_snapshot"] == d["scientific_source_snapshot"]


def test_p0b3_runner_and_one_shot_workflow_are_installed_after_freeze():
    assert (ROOT / "experiments/p0b3_qualify.py").exists()
    assert (ROOT / ".github/workflows/p0b3_execute.yml").exists()
    e = load("configs/p0b3_execution.json")
    assert e["execution_authorized"] is True
    assert not (ROOT / e["result_repo_path"]).exists()
