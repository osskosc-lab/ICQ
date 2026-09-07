# ICQ-RA Phase 0B — P0B-4 Hidden Modifier Proxy Falsification Design Freeze

## Status

- Gate: `P0B-4_HIDDEN_MODIFIER_PROXY_FALSIFICATION`
- Design: **FROZEN**
- Held-out execution: **NOT AUTHORIZED**
- One-shot qualification runner: **NOT INSTALLED**
- One-shot workflow: **NOT INSTALLED**

## Frozen falsification target

The synthetic counterexample is fixed as:

```text
Z -> Q
Z x U -> Y
Q -/-> Y
```

P0B-4 asks whether the same hidden-modifier structure is simultaneously:

1. **ACTIVE-like under the frozen Phase 0A conditioning baseline**
   - mean_seed(Phase0A ICQ-RA) >= 0.15
2. **Null-like under atomic direct intervention on Q**
   - mean_seed(ICQ-DI) <= 0.05

Both conditions are mandatory. Neither metric may substitute for the other.

## Held-out bank

```text
P0B4-HO-v1
6401-6430 inclusive
exact ascending order
n = 30
```

These seeds remain prohibited from routine CI and debug execution.

## Decision rule

`PASS` requires all integrity/preflight checks plus both frozen inequalities.

Failures are localized as:

- `FAIL_BASELINE_REPRODUCTION`
- `FAIL_DIRECT_FALSE_POSITIVE`
- `FAIL_BOTH`
- `STOP_INTEGRITY_NO_SCIENTIFIC_DECISION`

No post-result threshold, generator, estimator, or seed replacement is allowed.

## Claim firewall

A P0B-4 PASS would establish only the frozen synthetic discrimination pattern. It does **not** by itself authorize:

- a general L4 structural-identification claim,
- real-system identification,
- real-data confirmatory execution,
- consciousness claims,
- qualia or phenomenal claims.

Any L4 conditional upgrade is deferred to `P0B-5_GATE_REVIEW_AND_FREEZE_DECISION`.

## Authorization boundary

This design freeze does not authorize held-out execution. A later explicit authorization is required before any `6401-6430` seed is evaluated. The future execution, if authorized, must be one-shot and its workflow must be removed immediately after valid result capture.
