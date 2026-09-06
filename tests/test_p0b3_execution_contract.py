import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_p0b3_execution_implementation_is_not_yet_authorized():
    e = load("configs/p0b3_execution.json")
    assert e["implementation_status"] == "IMPLEMENTED_AWAITING_AUTHORIZATION"
    assert e["execution_authorized"] is False
    assert e["authorization_status"] == "NOT_AUTHORIZED"
    assert e["authorized_parent_head_sha"] is None
    assert e["one_shot_only"] is True


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
    assert e["execution_authorized"] is False
    assert not (ROOT / e["result_repo_path"]).exists()
