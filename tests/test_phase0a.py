import numpy as np

from icq_ra import estimate_icq_ra, empirical_js_distance
from experiments.phase0a import generate_scm


def test_js_distance_identical_is_zero():
    x = np.linspace(-1.0, 1.0, 1000)
    edges = np.linspace(-2.0, 2.0, 41)
    assert empirical_js_distance(x, x, edges) < 1e-12


def _estimate(scenario: str, seed: int = 1234):
    cfg = {
        "intervention_values": [-1.0, 0.0, 1.0],
        "confounded_q_flip_probability": 0.15,
        "active_latent_coupling": 0.9,
        "noise_sigma": 1.0,
        "intervention_main_effect": 0.7,
        "history_effect": 1.4,
    }
    q, h, u, y = generate_scm(scenario, seed=seed, n=9000, cfg=cfg)
    edges = np.linspace(-5.0, 5.0, 61)
    return estimate_icq_ra(
        q,
        h,
        u,
        y,
        intervention_values=[-1.0, 0.0, 1.0],
        history_values=[0, 1],
        bin_edges=edges,
        min_cell=80,
        n_permutations=10,
        seed=seed + 900000,
    ).value


def test_active_exceeds_inactive():
    active = _estimate("ACTIVE")
    inactive = _estimate("INACTIVE")
    assert active > inactive + 0.08


def test_confounding_does_not_mimic_active_after_history_conditioning():
    active = _estimate("ACTIVE", seed=4321)
    confounded = _estimate("CONFOUNDED", seed=4321)
    assert active > confounded + 0.08
