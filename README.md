# ICQ

Information Causal Quantity research repository.

## ICQ-RA: Response Accessibility

ICQ-RA is an experimental branch of ICQ for asking a deliberately narrower question:

> If two latent internal states differ, can that difference be made causally accessible as a difference in observable responses under an allowed intervention set?

ICQ-RA **does not measure qualia** and does not establish that qualia exist. Phase 0A uses only synthetic latent states with known structural equations to qualify the measurement pipeline before any application to consciousness-related data.

### Core estimand

For latent states `q1, q2`, history `H`, intervention set `U`, and observable response `Y`:

```text
ICQ-RA(q1,q2 | H,U,Y)
  = max_{u in U} D[
      P(Y | do(u), q1, H),
      P(Y | do(u), q2, H)
    ]
```

Phase 0A fixes `D` to Jensen-Shannon distance.

The empirical estimator subtracts a permutation-null finite-sample bias estimate. This correction belongs to the estimator, not to the theoretical definition.

### Phase 0A qualification scenarios

1. **ACTIVE** — latent state causally modulates the response under intervention. ICQ-RA should be positive.
2. **INACTIVE** — latent state exists but has no path to the response. ICQ-RA should remain near zero.
3. **CONFOUNDED** — history drives both latent state and response, creating observational separation without a latent-state causal path. OBS-Distance should be positive while history-conditioned ICQ-RA remains near zero.

### Install and test

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
pytest -q
```

### Full Phase 0A run

```bash
python experiments/phase0a.py \
  --config configs/phase0a.json \
  --out results/phase0a_summary.json
```

### Single-seed debug replay

```bash
python experiments/phase0a.py \
  --config configs/phase0a.json \
  --out results/replay.json \
  --scenario CONFOUNDED \
  --seed 1101 \
  --debug-dir results/debug
```

The debug report includes input invariants, data/config SHA-256 fingerprints, per-cell sample and JSD diagnostics, permutation-null statistics, and an independent estimator reconstruction.

The full Phase 0A experiment is intentionally **not** run by CI. CI only checks package installation, one single-seed debug smoke replay, implementation invariants, and unit tests.

See [docs/phase0a_protocol.md](docs/phase0a_protocol.md) for the research gate and [docs/debugging.md](docs/debugging.md) for failure-localization rules.
