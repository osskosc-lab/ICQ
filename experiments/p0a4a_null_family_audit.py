from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy import stats

from icq_ra import estimate_icq_ra


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def fingerprint(*arrays: np.ndarray) -> str:
    h = hashlib.sha256()
    for arr in arrays:
        a = np.ascontiguousarray(arr)
        h.update(str(a.dtype).encode())
        h.update(str(a.shape).encode())
        h.update(a.tobytes())
    return h.hexdigest()


def generate_pair(seed: int, cfg: dict):
    n = int(cfg["n_per_seed"])
    rng = np.random.default_rng(seed)
    h = rng.integers(0, 2, size=n)
    u = rng.choice(np.asarray(cfg["intervention_values"], dtype=float), size=n)
    noise = rng.normal(0.0, float(cfg["noise_sigma"]), size=n)

    qi = np.random.default_rng(seed + 1_000_000).integers(0, 2, size=n)
    rngc = np.random.default_rng(seed + 2_000_000)
    flip = rngc.random(n) < float(cfg["confounded_q_flip_probability"])
    qc = np.where(flip, 1 - h, h)

    y = (
        float(cfg["intervention_main_effect"]) * u
        + float(cfg["history_effect"]) * h
        + noise
    )
    return qi, qc, h, u, y, noise


def estimate(q, h, u, y, seed: int, cfg: dict) -> float:
    edges = np.linspace(
        float(cfg["histogram_min"]),
        float(cfg["histogram_max"]),
        int(cfg["histogram_bins"]) + 1,
    )
    est = estimate_icq_ra(
        q, h, u, y,
        intervention_values=cfg["intervention_values"],
        history_values=cfg["history_values"],
        bin_edges=edges,
        min_cell=int(cfg["min_cell"]),
        n_permutations=int(cfg["n_permutations"]),
        seed=seed + int(cfg["estimator_seed_offset"]),
    )
    return float(est.value)


def sign_flip_pvalue(diff: np.ndarray, n_perm: int, rng_seed: int) -> float:
    rng = np.random.default_rng(rng_seed)
    observed = float(np.mean(diff))
    ge = 0
    batch = 5000
    remaining = n_perm
    while remaining:
        m = min(batch, remaining)
        signs = rng.choice(np.array([-1.0, 1.0]), size=(m, diff.size))
        vals = np.mean(signs * diff[None, :], axis=1)
        ge += int(np.sum(vals >= observed))
        remaining -= m
    return float((ge + 1) / (n_perm + 1))


def mean_ci(diff: np.ndarray, confidence: float):
    mean = float(np.mean(diff))
    se = float(stats.sem(diff))
    if se == 0.0:
        return [mean, mean]
    alpha = 1.0 - confidence
    crit = float(stats.t.ppf(1.0 - alpha / 2.0, df=diff.size - 1))
    return [mean - crit * se, mean + crit * se]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase0a-config", required=True)
    ap.add_argument("--p0a4a-config", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    cfg = load_json(args.phase0a_config)
    gate = load_json(args.p0a4a_config)
    seeds = [int(s) for s in gate["paired_seeds"]]
    forbidden = set(range(1101, 1131)) | set(range(2101, 2131))
    overlap = sorted(set(seeds) & forbidden)

    preflight = {
        "seed_bank_disjoint": len(overlap) == 0,
        "pair_count_exact": len(seeds) == int(gate["expected_pairs"]),
        "seeds_unique": len(set(seeds)) == len(seeds),
    }
    if not all(preflight.values()):
        payload = {
            "protocol_id": gate["protocol_id"],
            "execution_status": "STOP_PREFLIGHT",
            "scientific_decision": "NOT_EVALUATED",
            "preflight": preflight,
            "overlap": overlap,
        }
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(json.dumps(payload, indent=2))
        raise SystemExit(1)

    rows = []
    for seed in seeds:
        qi, qc, h, u, y, noise = generate_pair(seed, cfg)
        rows.append({
            "seed": seed,
            "inactive_icq_ra": estimate(qi, h, u, y, seed, cfg),
            "confounded_icq_ra": estimate(qc, h, u, y, seed, cfg),
            "shared_h_u_y_noise_sha256": fingerprint(h, u, y, noise),
        })
        rows[-1]["difference"] = rows[-1]["confounded_icq_ra"] - rows[-1]["inactive_icq_ra"]

    d = np.asarray([r["difference"] for r in rows], dtype=float)
    margin = float(gate["equivalence_margin"])
    alpha = float(gate["alpha"])

    leak_p = sign_flip_pvalue(
        d,
        int(gate["leakage_test"]["n_permutations"]),
        int(gate["leakage_test"]["rng_seed"]),
    )

    lower = stats.ttest_1samp(d, popmean=-margin, alternative="greater")
    upper = stats.ttest_1samp(d, popmean=margin, alternative="less")
    tost_pass = bool(lower.pvalue < alpha and upper.pvalue < alpha)

    mean_d = float(np.mean(d))
    if tost_pass:
        decision = "PASS_EQUIVALENT"
    elif leak_p < alpha and mean_d > 0.0:
        decision = "FAIL_LEAKAGE"
    else:
        decision = "INCONCLUSIVE"

    payload = {
        "protocol_id": gate["protocol_id"],
        "gate": gate["gate"],
        "execution_status": "COMPLETE",
        "scientific_decision": decision,
        "preflight": preflight,
        "estimand": gate["estimand"],
        "n_pairs": int(d.size),
        "mean_difference": mean_d,
        "std_difference": float(np.std(d, ddof=1)),
        "median_difference": float(np.median(d)),
        "min_difference": float(np.min(d)),
        "max_difference": float(np.max(d)),
        "ci90_mean_difference": mean_ci(d, 0.90),
        "ci95_mean_difference": mean_ci(d, 0.95),
        "equivalence_margin": margin,
        "leakage_sign_flip_p_one_sided": leak_p,
        "tost": {
            "lower_test_p": float(lower.pvalue),
            "upper_test_p": float(upper.pvalue),
            "pass": tost_pass,
        },
        "rows": rows,
        "claim_ceiling": gate["claim_ceiling"],
        "phase0a_overall_qualification_authorized": False,
        "qualia_claim_authorized": False,
    }

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in payload.items() if k != "rows"}, indent=2))
    raise SystemExit(0)


if __name__ == "__main__":
    main()
