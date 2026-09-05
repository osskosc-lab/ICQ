# ICQ-RA Debugging Design v0.1

The debug layer exists to localize implementation failures without changing the scientific estimand or qualification thresholds.

## Debug principles

1. **Replay before interpretation** — every failure must be reproducible from one scenario + one seed.
2. **Cell before aggregate** — inspect each (u, H, q) cell before discussing ICQ-RA.
3. **Observed vs permutation-null** — retain both values so a correction failure is visible.
4. **Fingerprint before rerun** — hash generated arrays and configuration to distinguish a real replay from a similar rerun.
5. **Invariant failure is a STOP** — malformed inputs or estimator reconstruction mismatch invalidate the run before scientific interpretation.

## Diagnostic levels

### D0 — Environment

Records Python, NumPy, and platform information.

Purpose: isolate environment-specific failures.

### D1 — Seed replay

Run exactly one declared scenario and seed:

```bash
python experiments/phase0a.py \
  --config configs/phase0a.json \
  --out results/replay.json \
  --scenario CONFOUNDED \
  --seed 1101 \
  --debug-dir results/debug
```

This mode explicitly returns:

```text
qualification_decision = NOT_EVALUATED
```

A debug replay can never qualify Phase 0A.

### D2 — Input and cell invariants

For every declared intervention/history cell the report records:

- q=0 and q=1 sample counts
- minimum-cell eligibility
- response mean and standard deviation
- finite-value and declared-domain checks

A failed invariant sets `debug_pass=false`.

### D3 — Permutation audit

For every eligible cell:

```text
observed JSD
permutation-null mean
permutation-null std
permutation-null min/max
corrected JSD
```

This makes finite-sample correction visible rather than hiding it behind one scalar.

### D4 — Estimator reconstruction

The debug layer independently replays the exact RNG order used by the estimator and reconstructs:

```text
per-intervention ICQ-RA
max-over-intervention ICQ-RA
```

The reconstructed values must match the reported estimator to absolute tolerance 1e-12.

Mismatch is an implementation STOP.

### D5 — Provenance fingerprints

The report records SHA-256 fingerprints for:

- q
- H
- u
- Y
- combined dataset
- canonicalized config

The same scenario/seed/config must reproduce the same fingerprints.

## Failure localization order

Use this order and stop at the first failure:

```text
ENVIRONMENT
  -> INPUT INVARIANTS
    -> DATA FINGERPRINT
      -> CELL COUNTS
        -> OBSERVED JSD
          -> PERMUTATION NULL
            -> CORRECTED JSD
              -> AGGREGATION / MAX-U
```

This prevents downstream metrics from masking an upstream defect.

## CI behavior

CI does not execute the 30-seed qualification.

CI only:

1. installs ICQ-RA as a package,
2. records environment information,
3. runs one INACTIVE debug smoke replay,
4. executes unit tests,
5. uploads debug JSON artifacts even if a later test fails.

## Claim firewall

Debug output authorizes no scientific inference.

```text
DEBUG_PASS != PHASE0A_PASS
DEBUG_PASS != QUALIA_EVIDENCE
DEBUG_FAIL => IMPLEMENTATION_INVESTIGATION_REQUIRED
```
