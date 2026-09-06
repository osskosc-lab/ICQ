import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_p0b3_execution_is_closed_after_valid_one_shot_result():
    e = load("configs/p0b3_execution.json")
    assert e["implementation_status"] == "COMPLETE_CLOSED_AFTER_VALID_RESULT"
    assert e["execution_authorized"] is False
    assert e["authorization_status"] == "COMPLETE_CLOSED_FOR_RERUN"
    assert e["authorized_parent_head_sha"] == "9b7ed6eb43e2af3d5f7c325cb2e903ef347857fc"
    assert e["one_shot_only"] is True
    assert e["authorization_evidence"]["scope"] == "P0B-3_DIRECT_ACTIVE_SENSITIVITY_ONLY"
    assert e["authorization_evidence"]["p0b4_authorized"] is False
    assert e["result"]["decision"] == "PASS"
    assert e["one_shot_workflow_close_pending"] is False
    assert e["one_shot_workflow_closed"] is True
    assert not (ROOT / ".github/workflows/p0b3_execute.yml").exists()


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


def test_p0b3_result_is_recorded_and_rerun_is_closed():
    assert (ROOT / "experiments/p0b3_qualify.py").exists()
    e = load("configs/p0b3_execution.json")
    assert e["execution_authorized"] is False
    assert (ROOT / e["result_repo_path"]).exists()
    r = load(e["result_repo_path"])
    assert r["decision"] == "PASS"
    assert r["workflow_run_attempt"] == 1
    assert r["p0b4_execution_authorized"] is False
