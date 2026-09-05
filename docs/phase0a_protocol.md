# ICQ-RA Phase 0A — Synthetic Response-Accessibility Qualification

**PROTOCOL_ID:** ICQ-RA-P0A-v0.1  
**STATUS:** DRAFT_NOT_FROZEN  
**CURRENT_GATE:** IMPLEMENTATION_AND_PREREGISTRATION_AUDIT  
**QUALIFICATION_RUN:** NOT_YET_EXECUTED  
**CONFIRMATORY_RUN:** NOT_AUTHORIZED  
**QUALIA_APPLICATION:** PROHIBITED_AT_THIS_GATE

## 1. Minimal research question

Can a measurement pipeline distinguish:

- a latent state difference that is causally response-accessible,
- a latent state difference that is response-inactive, and
- an observationally separated but causally confounded latent state?

No claim about consciousness, phenomenal experience, or qualia is tested in Phase 0A.

## 2. Core estimand

For binary latent states q1 and q2:

```text
Delta_RA(q1,q2 | u,H)
  = JSD(
      P(Y | do(u), q1, H),
      P(Y | do(u), q2, H)
    )

ICQ-RA(q1,q2 | H,U,Y)
  = max_{u in U} Delta_RA(q1,q2 | u,H)
```

The value is conditional on the declared history representation H, allowed intervention set U, and response variable Y. It is not an intrinsic scalar property of q.

## 3. Empirical estimator

Finite-sample histogram JSD is positively biased. Therefore each history/intervention cell uses:

```text
Delta_hat_corrected
  = max(
      0,
      JSD_empirical
      - mean(JSD_permutation_null)
    )
```

This correction is an estimator choice only. It does not alter the theoretical estimand.

## 4. Structural generators

All scenarios share:

```text
Y = a*u + gamma*H + b*q*u + epsilon
epsilon ~ Normal(0, sigma^2)
```

### ACTIVE

```text
q independent of H
b > 0
```

A q-dependent interaction with intervention exists. Expected result: ICQ-RA > 0.

### INACTIVE

```text
q independent of H
b = 0
```

q exists in the generator but has no structural path to Y. Expected result: ICQ-RA near 0.

### CONFOUNDED

```text
H -> q
H -> Y
q -/-> Y
b = 0
```

q is a noisy copy of binary H, creating an unconditional observational difference in Y. The ICQ-RA estimator compares q states only within fixed H strata. Expected result:

```text
OBS-Distance > 0
ICQ-RA near 0
```

## 5. Fixed primary metric and baseline

Primary metric:

```text
mean_seed(ICQ-RA)
```

Baseline:

```text
OBS-Distance = JSD(P(Y|q=0), P(Y|q=1))
```

OBS-Distance intentionally ignores H and causal structure.

## 6. Qualification thresholds

The draft configuration currently fixes:

```text
ACTIVE mean ICQ-RA      >= 0.15
INACTIVE mean ICQ-RA    <= 0.05
CONFOUNDED mean ICQ-RA  <= 0.05
CONFOUNDED mean OBS     >= 0.20
```

These are pipeline qualification thresholds, not scientific effect-size claims about real systems.

## 7. One proposition / one metric / one baseline / one falsification

**Proposition**  
Known response-accessible latent differences can be separated from response-inactive and confounded differences.

**Primary metric**  
ICQ-RA = maximum history-conditioned corrected JSD across allowed interventions.

**Baseline**  
Unadjusted OBS-Distance.

**Primary falsification**  
CONFOUNDED must exhibit observational separation without elevated ICQ-RA.

## 8. Stop conditions

STOP / FAIL if any occurs:

1. INACTIVE exceeds the null threshold.
2. CONFOUNDED exceeds the null threshold after history conditioning.
3. ACTIVE fails the sensitivity threshold.
4. CONFOUNDED fails to produce the required observational separation.
5. Results depend on an undeclared intervention, history representation, binning rule, or seed change.

## 9. Claim firewall

Phase 0A may support only:

> The ICQ-RA measurement pipeline survived the declared synthetic qualification tests.

Phase 0A must not support:

```text
ICQ-RA > 0 => qualia exist
ICQ-RA > 0 => qualia were measured
ICQ-RA = 0 => qualia are absent
response difference => phenomenal difference
```

A future qualia-related phase, if any, requires a separate bridge hypothesis connecting a real measurable latent-state candidate to phenomenal claims, plus independent identifiability and alternative-explanation audits.

## 10. Gate sequence

```text
P0A-0  Implementation audit
P0A-1  Seed reproducibility pilot
P0A-2  Null calibration
P0A-3  ACTIVE sensitivity qualification
P0A-4  CONFOUNDED falsification
P0A-5  Freeze decision
```

At the current commit, only experimental infrastructure is being proposed. Running the full qualification does not by itself authorize any downstream confirmatory or qualia-related experiment.
