# P0A-4 Orthogonal Failure-Localization Gate

P0A-4 is split into two independent sub-gates so estimator residuals and structural identifiability cannot contaminate each other's failure diagnosis.

## P0A-4A — Null-Family Discrimination Audit

Estimand:

```text
Delta_N = mean(ICQ-RA_CONFOUNDED - ICQ-RA_INACTIVE)
```

Frozen paired seed bank:

```text
P0A4A-HO-v1
3101-3160
n = 60 pairs
```

Each pair shares H, U, response noise, sample size, and estimator seed policy.

Tests:

```text
Positive leakage:
paired sign-flip Monte Carlo test

Practical equivalence:
paired TOST on mean difference
margin = +/- 0.01
alpha = 0.05
```

Decision:

```text
PASS_EQUIVALENT
  TOST passes.

FAIL_LEAKAGE
  TOST fails,
  positive leakage p < 0.05,
  and mean Delta_N > 0.

INCONCLUSIVE
  Any other valid result.
```

A non-significant difference test is never treated as evidence of equality.

## P0A-4B — Structural Identifiability Counterexample

Frozen seed bank:

```text
P0A4B-HO-v1
4101-4130
n = 30 per alternative
```

Frozen ACTIVE criterion:

```text
mean_seed(ICQ-RA) >= 0.15
```

Declared alternatives contain no direct Q term in Y.

### OBSERVED_HU_INTERACTION

```text
H -> Y
H x U -> Y
Q independent
Q -/-> Y
```

### HIDDEN_MODIFIER_PROXY

```text
Z -> Q
Z x U -> Y
Q -/-> Y
```

The hidden-modifier model tests whether Q can merely proxy an unobserved effect modifier while ICQ-RA still reaches the ACTIVE criterion.

Decision:

```text
FAIL_NONIDENTIFIABLE
  Any no-Q-direct-effect alternative reaches mean ICQ-RA >= 0.15.

SURVIVED_DECLARED_ALTERNATIVES
  All declared alternatives remain below 0.15.

INCONCLUSIVE
  Execution or invariants are invalid.
```

SURVIVED_DECLARED_ALTERNATIVES means only relative survival against the declared alternative classes, never absolute identification.

Scientific FAIL is a valid result and does not make CI fail. CI failure is reserved for execution/preflight failure.
