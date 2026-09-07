# P0B-3 DIRECT_ACTIVE Sensitivity — Frozen Experimental Design

**Protocol:** ICQ-RA-P0B-3-v0.1  
**Parent:** ICQ-RA-P0B-v0.1  
**Gate:** P0B-3_DIRECT_ACTIVE_SENSITIVITY  
**Status:** FROZEN_AWAITING_EXPLICIT_ONE_SHOT_AUTHORIZATION  
**Execution:** NOT AUTHORIZED

## 1. Question

Does the already-frozen ICQ-DI implementation detect the declared `DIRECT_ACTIVE` synthetic generator on a fresh held-out bank, after P0B-2 established the declared Null control?

This gate tests **sensitivity only**. It does not test the hidden-modifier falsification; that remains P0B-4.

## 2. Prerequisites

```text
P0B-0  PASS
P0B-1  PASS
P0B-2  PASS
```

If any prerequisite record changes or cannot be verified, P0B-3 stops before scientific execution.

## 3. Frozen generator and estimator

Scenario:

```text
DIRECT_ACTIVE

Y = aU + gamma H + bQU + epsilon
b = 0.9
```

Atomic arms:

```text
do(Q=0)
do(Q=1)
```

Per-seed estimator is exactly the existing:

```text
experiments.phase0b.estimate_direct_seed(
    "DIRECT_ACTIVE",
    seed,
    configs/phase0b.json
)
```

No P0B-3 pilot tuning is allowed.

Frozen scientific source Git blobs:

```text
configs/phase0b.json
fca2c0397fe3b01a84f728e92e4d95cac8289628

experiments/phase0b.py
2ae52c8a30a3bcb8137ccf0fa6f512f1064512fc

icq_ra/direct_intervention.py
17f1fa3f224b975b5d3754aac43ffe93ed578f79

requirements.txt
0da304d5ea05d410163d39c72fcabb67573f3a88

pyproject.toml
55ac1e2b774cfb8b6a3c16e50c92d900bda05173
```

Any mismatch is an implementation/integrity STOP, not a sensitivity FAIL.

## 4. Frozen held-out bank

```text
P0B3-HO-v1
6301-6330
n = 30
execution order = ascending
```

Every seed must appear exactly once. No replacement seed is permitted.

Routine CI, smoke tests, and documentation examples remain prohibited from executing this bank.

## 5. Primary estimand

For each seed `s`:

```text
D_s = ICQ-DI_s
```

Primary gate estimand:

```text
M_3 = (1/30) * sum_{s=6301}^{6330} D_s
```

There is exactly one gate decision metric:

```text
mean_seed(ICQ-DI)
```

## 6. Frozen decision rule

Inherited threshold:

```text
ACTIVE mean minimum = 0.15
```

Decision:

```text
PASS
iff
all integrity checks PASS
AND
mean_seed(ICQ-DI) >= 0.15

FAIL_SENSITIVITY
iff
all integrity checks PASS
AND
mean_seed(ICQ-DI) < 0.15
```

Any seed-bank, source-freeze, completeness, current-gate, or prerequisite mismatch yields:

```text
STOP_INTEGRITY_NO_SCIENTIFIC_DECISION
```

There is no rescue rule based on median, quantiles, per-seed pass fraction, confidence interval, or alternative threshold.

## 7. Descriptive outputs

The one-shot result, if later authorized, must report:

```text
n
mean
sample std (ddof=1)
median
q05 (NumPy linear quantile)
q95 (NumPy linear quantile)
min
max
all 30 per-seed ICQ-DI values
```

Only the mean enters the gate decision.

## 8. One-shot execution contract

At this design freeze:

```text
execution_authorized = false
qualification runner = not installed
one-shot workflow    = not installed
```

A later explicit authorization is required before any seed in 6301-6330 may be executed.

If execution is authorized later:

1. verify the frozen source snapshot,
2. verify exact seed bank and prerequisites,
3. execute each seed exactly once,
4. produce one immutable result artifact,
5. record workflow run, execution head, artifact ID and SHA-256,
6. remove the one-shot workflow immediately after capture,
7. never rerun a valid held-out result.

## 9. State transition

If P0B-3 passes:

```text
P0B-3 PASS
P0B-4 HIDDEN_MODIFIER_PROXY FALSIFICATION
ELIGIBLE
NOT AUTHORIZED
```

If P0B-3 fails:

```text
P0B-3 FAIL_SENSITIVITY
PHASE 0B STOP
P0B-4 NOT AUTHORIZED
L4 UPGRADE NOT AUTHORIZED
```

## 10. Claim firewall

A P0B-3 PASS would support only:

> Under the declared frozen synthetic DIRECT_ACTIVE generator, ICQ-DI exceeded the preregistered across-seed mean sensitivity threshold on the frozen P0B-3 held-out bank.

It would **not** establish hidden-proxy separation, general L4 structural identification, real-system identification, consciousness, qualia, or phenomenal state.

Those boundaries remain unchanged.
