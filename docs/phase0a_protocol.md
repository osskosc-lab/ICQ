# ICQ-RA Phase 0A — Synthetic Response-Accessibility Qualification

**PROTOCOL_ID:** ICQ-RA-P0A-v0.1  
**STATUS:** FROZEN_OPERATIONAL_SCOPE_L1_L3  
**FINAL_VERDICT:** B — CONDITIONALLY_SUPPORTED  
**GATE_REVIEW:** FREEZE_APPROVED_WITH_SCOPE_LIMITATION  
**CONFIRMATORY_REAL_DATA_RUN:** NOT AUTHORIZED  
**QUALIA_APPLICATION:** NOT AUTHORIZED

## 1. Frozen research question

Can the ICQ-RA measurement pipeline reproducibly detect response-accessible latent-state differences under declared synthetic interventions while controlling the tested Null structures?

Phase 0A does **not** establish that the measured latent state is the unique causal source of the response difference.

## 2. Core estimand

```text
Delta_RA(q1,q2 | u,H)
  = JSD(
      P(Y | do(u), q1, H),
      P(Y | do(u), q2, H)
    )

ICQ-RA(q1,q2 | H,U,Y)
  = max_{u in U} Delta_RA(q1,q2 | u,H)
```

The value is conditional on the declared history representation H, intervention set U, and response variable Y.

## 3. Empirical estimator

```text
Delta_hat_corrected
  = max(
      0,
      JSD_empirical
      - mean(JSD_permutation_null)
    )
```

The correction is an estimator choice, not part of the theoretical estimand.

## 4. Completed gate chain

```text
P0A-0  Implementation / debug qualification        PASS
P0A-1  Seed reproducibility pilot                  PASS
P0A-2  Null threshold-exceedance calibration       PASS
P0A-3  ACTIVE held-out sensitivity                 PASS
P0A-4A Null-family residual audit                  PASS_EQUIVALENT
P0A-4B Structural identifiability counterexample   FAIL_NONIDENTIFIABLE
P0A-5  Phase 0A Gate Review / Freeze Decision      FREEZE_APPROVED_WITH_SCOPE_LIMITATION
```

## 5. P0A-4A frozen interpretation

The paired Null-family audit found a small positive residual:

```text
mean Delta_N = 0.00507935140306689
95% CI       = [0.002355609537210807, 0.007803093268922973]
TOST margin  = +/- 0.01
TOST         = PASS
```

Therefore the correct conclusion is not "no difference". The CONFOUNDED residual is statistically higher than INACTIVE, but the mean difference is practically equivalent under the preregistered ±0.01 margin.

## 6. P0A-4B non-identifiability result

A hidden-modifier counterexample was constructed:

```text
Z -> Q
Z x U -> Y
Q -/-> Y
```

with:

```text
mean ICQ-RA = 0.21500508978334615
frozen ACTIVE criterion = 0.15
```

Thus:

```text
ICQ-RA >= ACTIVE threshold
does not uniquely imply
Q -> Y
```

Structural identification of Q's unique causal efficacy is therefore rejected under the current intervention/measurement design.

## 7. Frozen epistemic levels

```text
L1 Implementation
  SUPPORTED

L2 Null Control
  SUPPORTED_WITH_EQUIVALENCE_MARGIN

L3 Response Sensitivity
  SUPPORTED

L4 Structural Identification
  REJECTED_NONIDENTIFIABLE

L5 Qualia / Phenomenal Interpretation
  NOT AUTHORIZED
```

## 8. Frozen claim ceiling

The strongest authorized Phase 0A claim is:

> Under the declared synthetic Phase 0A conditions, ICQ-RA is qualified as a reproducible response-accessibility detector with tested Null-control performance and held-out ACTIVE sensitivity, while unique structural identification of Q's causal efficacy is not supported.

The following claims are prohibited:

```text
ICQ-RA uniquely identifies Q -> Y
ICQ-RA identifies consciousness
ICQ-RA measures qualia
ICQ-RA = 0 implies absence of qualia
response difference implies phenomenal difference
```

## 9. Core conclusion

```text
Operationally Useful != Structurally Identified
```

## 10. Next action

Phase 0A is closed at the L1-L3 operational scope.

Permitted next actions:

```text
ARCHIVE_PHASE0A
PREPARE_LIMITED_SCOPE_MANUSCRIPT
DESIGN_A_NEW_PROTOCOL_FOR_L4_IDENTIFICATION
DESIGN_A_SEPARATE_PROTOCOL_FOR_REAL_SYSTEMS
```

No confirmatory real-data run is authorized by Phase 0A.
