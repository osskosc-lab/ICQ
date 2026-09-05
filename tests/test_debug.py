import copy

import numpy as np

from experiments.phase0a import generate_scm, run_seed
from icq_ra.debug import validate_inputs


CFG = {
    "protocol_id": "DEBUG-TEST",
    "protocol_status": "DRAFT_NOT_FROZEN",
    "n_per_seed": 6000,
    "intervention_values": [-1.0, 0.0, 1.0],
    "history_values": [0, 1],
    "intervention_main_effect": 0.7,
    "history_effect": 1.4,
    "active_latent_coupling": 0.9,
    "confounded_q_flip_probability": 0.15,
    "noise_sigma": 1.0,
    "histogram_min": -5.0,
    "histogram_max": 5.0,
    "histogram_bins": 50,
    "min_cell": 50,
    "n_permutations": 8,
    "estimator_seed_offset": 900000,
}


def test_debug_replay_is_deterministic_and_reconstructs_estimator():
    a = run_seed("ACTIVE", 2468, CFG, include_debug=True)
    b = run_seed("ACTIVE", 2468, copy.deepcopy(CFG), include_debug=True)

    assert a["debug"]["dataset_sha256"] == b["debug"]["dataset_sha256"]
    assert a["debug"]["config_sha256"] == b["debug"]["config_sha256"]
    assert a["debug"]["estimator_reconstruction"]["all_pass"]
    assert b["debug"]["estimator_reconstruction"]["all_pass"]
    assert a["icq_ra"] == b["icq_ra"]


def test_input_invariants_detect_nonfinite_response():
    q, h, u, y = generate_scm("INACTIVE", seed=99, n=3000, cfg=CFG)
    y[0] = np.nan
    edges = np.linspace(-5.0, 5.0, 51)

    audit = validate_inputs(
        q,
        h,
        u,
        y,
        intervention_values=CFG["intervention_values"],
        history_values=CFG["history_values"],
        bin_edges=edges,
        min_cell=CFG["min_cell"],
    )

    assert not audit["checks"]["y_finite"]
    assert "y_finite" in audit["failed"]
