# ICQ-RA Phase 0B — Direct-Latent Intervention Identification Qualification

**PROTOCOL_ID:** ICQ-RA-P0B-v0.1  
**STATUS:** DRAFT_FOR_PREREGISTRATION_AUDIT  
**RESEARCH_MODE:** falsification-first structural identification  
**QUALIFICATION_EXECUTION:** NOT AUTHORIZED  
**REAL-DATA CONFIRMATORY:** NOT AUTHORIZED  
**QUALIA / PHENOMENAL CLAIM:** NOT AUTHORIZED

## 1. Why Phase 0B exists

Phase 0A ended at:

```text
B — CONDITIONALLY_SUPPORTED
FROZEN_OPERATIONAL_SCOPE_L1_L3
L4 STRUCTURAL IDENTIFICATION: REJECTED_NONIDENTIFIABLE
```

The blocking counterexample was:

```text
Z -> Q
Z x U -> Y
Q -/-> Y
```

Under this model, conditioning on Q while intervening only on U can produce ACTIVE-like ICQ-RA even though Q itself has no causal effect on Y.

Therefore Phase 0B does not attempt to improve Phase 0A by changing thresholds. It changes the intervention question.

## 2. Minimum proposition

> In a synthetic SCM where atomic intervention on Q is explicitly available and valid, direct intervention on Q can distinguish Q's causal efficacy from a hidden-modifier proxy structure that defeats the Phase 0A conditioning-based metric.

This is the only primary proposition.

## 3. Primary metric

Define:

```text
D_DI(u,h)
  = JSD[
      P(Y | do(Q=0), do(U=u), H=h),
      P(Y | do(Q=1), do(U=u), H=h)
    ]

ICQ-DI(Q->Y | H,U)
  = max_u weighted_mean_h D_DI(u,h)
```

The empirical estimator reuses the Phase 0A histogram Jensen-Shannon distance and permutation-null subtraction.

The difference from Phase 0A is semantic, not cosmetic:

```text
Phase 0A:
P(Y | do(U), Q, H)

Phase 0B:
P(Y | do(Q), do(U), H)
```

Conditioning on Q is replaced by explicit intervention on Q.

## 4. Primary baseline

The single primary baseline is the frozen Phase 0A conditioning-based metric:

```text
ICQ-RA(Q | do(U), H)
```

Its role is not to compete for predictive performance. It is used to reproduce the exact failure mode that motivated Phase 0B.

## 5. Primary falsification

The single primary falsification is:

```text
HIDDEN_MODIFIER_PROXY

Z -> Q
Z x U -> Y
Q -/-> Y
```

Required pattern:

```text
Phase 0A baseline:
mean ICQ-RA >= 0.15

Phase 0B direct intervention:
mean ICQ-DI <= 0.05
```

If the hidden-proxy generator also produces:

```text
mean ICQ-DI > 0.05
```

then the Phase 0B identification claim fails.

## 6. Synthetic generators

### INACTIVE_DIRECT

```text
Q is directly intervened on
Q -/-> Y

Y = aU + gamma H + epsilon
```

Expected:

```text
ICQ-DI near Null
```

### DIRECT_ACTIVE

```text
do(Q) is valid
Q x U -> Y

Y = aU + gamma H + bQU + epsilon
```

Expected:

```text
ICQ-DI above ACTIVE threshold
```

### HIDDEN_MODIFIER_PROXY

Observational / baseline generator:

```text
Z -> Q
Z x U -> Y
Q -/-> Y
```

with Q a noisy proxy of Z.

Under atomic do(Q), the structural assignment of Q is replaced. Z is not changed.

The do(Q) response generator remains:

```text
Y = aU + gamma H + cZU + epsilon
```

and contains no Q term.

Expected:

```text
Phase 0A ICQ-RA  ACTIVE-like
Phase 0B ICQ-DI  Null-like
```

## 7. Intervention integrity

Atomic do(Q=q) is defined operationally as replacement of Q's structural assignment.

The following are mandatory invariants:

1. The do(Q) arm must not derive Q from Z or H.
2. Z's structural assignment is unchanged by do(Q).
3. H and U generation are unchanged by do(Q).
4. The Y equation differs between do(Q=0) and do(Q=1) only through a declared Q term when such a term exists.
5. In HIDDEN_MODIFIER_PROXY, Y contains no Q term.
6. Intervention-arm seed namespaces are explicit and reproducible.

Failure of any invariant is an implementation STOP, not a scientific FAIL.

## 8. Frozen thresholds

No Phase 0B pilot tuning is authorized before preregistration review.

For scale comparability, Phase 0B inherits the Phase 0A thresholds unchanged:

```text
ACTIVE mean minimum = 0.15
Null mean maximum   = 0.05
```

These values are not claimed to be optimal for ICQ-DI. They are a deliberately hard inherited benchmark.

## 9. Seed separation

Development/debug only:

```text
6101-6103
```

Frozen untouched qualification banks:

```text
P0B-2 INACTIVE_DIRECT
6201-6230

P0B-3 DIRECT_ACTIVE
6301-6330

P0B-4 HIDDEN_MODIFIER_PROXY
6401-6430
```

Qualification seeds must never be used by routine CI, smoke tests, documentation examples, or exploratory runs.

## 10. Gate sequence

```text
P0B-0  Protocol and implementation audit
P0B-1  Atomic do(Q) integrity audit
P0B-2  INACTIVE_DIRECT Null qualification
P0B-3  DIRECT_ACTIVE sensitivity qualification
P0B-4  HIDDEN_MODIFIER_PROXY falsification
P0B-5  Gate Review / freeze decision
```

No later gate may execute automatically.

## 11. Gate rules

### P0B-1

PASS only if the atomic-intervention implementation and sever invariants are verified.

### P0B-2

```text
mean ICQ-DI <= 0.05
```

on seeds 6201-6230.

### P0B-3

```text
mean ICQ-DI >= 0.15
```

on seeds 6301-6330.

### P0B-4

Both must hold:

```text
Phase 0A baseline mean ICQ-RA >= 0.15
Phase 0B mean ICQ-DI          <= 0.05
```

on seeds 6401-6430.

If the baseline does not reproduce the proxy failure, the result is INCONCLUSIVE rather than PASS.

## 12. Possible final verdicts

### L4_CONDITIONALLY_SUPPORTED_FOR_DIRECTLY_INTERVENABLE_SYNTHETIC_Q_ONLY

Allowed only if P0B-1 through P0B-4 all survive.

Meaning:

> Within the declared synthetic SCM class, when Q itself can be atomically intervened on, the direct-intervention metric distinguishes direct Q causal efficacy from the declared hidden-modifier proxy counterexample.

### FAIL_NONIDENTIFIABLE_UNDER_DO_Q_DESIGN

If the hidden proxy still produces elevated ICQ-DI.

### FAIL_ESTIMATOR_OR_INTERVENTION_INTEGRITY

If Null control or atomic-intervention invariants fail.

### INCONCLUSIVE

If the motivating proxy failure is not reproduced or the declared comparison cannot be evaluated.

## 13. Claim firewall

Even a complete Phase 0B PASS does not authorize:

```text
general structural identification of latent Q
identification when Q is not directly intervenable
real-system identification
consciousness identification
qualia measurement
phenomenal-state inference
```

Phase 0B addresses L4 only inside a synthetic, directly intervenable SCM.

## 14. Research boundary

The intended upgrade is:

```text
Phase 0A:
Operationally Useful != Structurally Identified

Phase 0B target:
Structurally Identified
ONLY WHEN Q IS DIRECTLY INTERVENABLE
AND ONLY WITHIN THE DECLARED SYNTHETIC MODEL CLASS
```

This limitation is part of the result, not a temporary disclaimer.
