import json
import subprocess
import sys
from pathlib import Path

import numpy as np

from experiments.phase0b import generate_paired_integrity_case
from experiments.p0b01_audit import protocol_progress_checks
from icq_ra import estimate_icq_di


def load_cfg():
    return json.loads(Path("configs/phase0b.json").read_text())


def test_phase0b_qualification_is_not_authorized():
    cfg = load_cfg()
    assert cfg["protocol_status"] == "DRAFT_FOR_PREREGISTRATION_AUDIT"
    assert cfg["qualification_execution_authorized"] is False
    assert cfg["confirmatory_real_data_run_authorized"] is False
    assert cfg["l5_phenomenal_claim_authorized"] is False


def test_phase0b_seed_namespaces_are_disjoint_and_fresh():
    cfg = load_cfg()
    ns = cfg["seed_namespaces"]

    groups = [
        set(ns["debug_only_exposed"]),
        set(ns["p0b2_inactive_direct_heldout"]),
        set(ns["p0b3_direct_active_heldout"]),
        set(ns["p0b4_hidden_proxy_heldout"]),
    ]

    for i, a in enumerate(groups):
        for b in groups[i + 1:]:
            assert not (a & b)

    phase0a_used = (
        set(range(1101, 1131))
        | set(range(2101, 2131))
        | set(range(3101, 3161))
        | set(range(4101, 4131))
    )
    assert not (set().union(*groups) & phase0a_used)


def test_atomic_do_q_integrity_hidden_proxy_has_no_q_effect():
    cfg = load_cfg()
    case = generate_paired_integrity_case(
        "HIDDEN_MODIFIER_PROXY", seed=6101, cfg=cfg
    )
    assert np.array_equal(case["y_do_q0"], case["y_do_q1"])


def test_atomic_do_q_integrity_inactive_has_no_q_effect():
    cfg = load_cfg()
    case = generate_paired_integrity_case(
        "INACTIVE_DIRECT", seed=6101, cfg=cfg
    )
    assert np.array_equal(case["y_do_q0"], case["y_do_q1"])


def test_atomic_do_q_integrity_active_changes_y_only_through_declared_term():
    cfg = load_cfg()
    case = generate_paired_integrity_case(
        "DIRECT_ACTIVE", seed=6101, cfg=cfg
    )
    expected = (
        cfg["generator_parameters"]["direct_q_coupling"] * case["u"]
    )
    observed = case["y_do_q1"] - case["y_do_q0"]
    assert np.allclose(observed, expected)


def test_icq_di_zero_for_identical_do_q_response_distributions():
    n = 400
    h = np.zeros(n, dtype=int)
    u = np.ones(n, dtype=float)
    y = np.linspace(-1.0, 1.0, n)

    est = estimate_icq_di(
        h, u, y,
        h, u, y.copy(),
        intervention_values=[1.0],
        history_values=[0],
        bin_edges=np.linspace(-2.0, 2.0, 41),
        min_cell=100,
        n_permutations=20,
        seed=1,
    )
    assert est.value == 0.0


def test_icq_di_detects_large_direct_intervention_shift():
    n = 400
    h = np.zeros(n, dtype=int)
    u = np.ones(n, dtype=float)
    y0 = np.linspace(-1.0, 1.0, n)
    y1 = y0 + 2.0

    est = estimate_icq_di(
        h, u, y0,
        h, u, y1,
        intervention_values=[1.0],
        history_values=[0],
        bin_edges=np.linspace(-3.0, 4.0, 71),
        min_cell=100,
        n_permutations=20,
        seed=2,
    )
    assert est.value > 0.15


def test_p0b01_cli_module_entrypoint_is_importable():
    completed = subprocess.run(
        [sys.executable, "-m", "experiments.p0b01_audit", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert "--phase0b-config" in completed.stdout


def test_p0b01_progress_metadata_tracks_current_gate():
    cfg = load_cfg()
    checks, expected_current_gate = protocol_progress_checks(cfg)
    assert all(checks.values())
    assert expected_current_gate == "P0B-4_HIDDEN_MODIFIER_PROXY_FALSIFICATION"
    assert cfg["current_gate"] == expected_current_gate
    assert cfg["current_gate_execution_authorized"] is False
