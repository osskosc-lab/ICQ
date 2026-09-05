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

### Run

```bash
python -m pip install -r requirements.txt
python experiments/phase0a.py --config configs/phase0a.json --out results/phase0a_summary.json
pytest -q
```

The full Phase 0A experiment is intentionally **not** run by CI. CI only checks implementation invariants and smoke tests.

See [docs/phase0a_protocol.md](docs/phase0a_protocol.md) for the current research gate and claim firewall.
