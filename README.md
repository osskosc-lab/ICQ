# ICQ

Information Causal Quantity research repository.

## ICQ-RA Phase 0A — FROZEN

**ICQ-RA (Response Accessibility)** is an operational measurement program for testing whether a declared latent-state difference is reflected in observable response distributions under declared interventions and history conditioning.

Phase 0A is complete and frozen.

```text
FINAL VERDICT
B — CONDITIONALLY_SUPPORTED

PHASE 0A STATUS
FROZEN_OPERATIONAL_SCOPE_L1_L3

CORE CONCLUSION
Operationally Useful != Structurally Identified
```

> ICQ-RA does not measure qualia, does not establish consciousness, and does not uniquely identify the causal efficacy of latent state Q.

---

## Frozen epistemic scope

| Level | Status | Authorized interpretation |
|---|---|---|
| L1 Implementation | **SUPPORTED** | Numerical implementation and deterministic replay are qualified. |
| L2 Null Control | **SUPPORTED_WITH_EQUIVALENCE_MARGIN** | Tested Null-family residuals remain within the preregistered practical-equivalence margin. |
| L3 Response Sensitivity | **SUPPORTED** | The synthetic ACTIVE generator is detected on a frozen held-out seed bank. |
| L4 Structural Identification | **REJECTED_NONIDENTIFIABLE** | ICQ-RA does not uniquely identify `Q -> Y`. |
| L5 Qualia / Phenomenal | **NOT AUTHORIZED** | No phenomenal or consciousness claim is permitted. |

The Phase 0A claim ceiling is:

> Under the declared synthetic Phase 0A conditions, ICQ-RA is qualified as a reproducible response-accessibility detector with tested Null-control behavior and held-out ACTIVE sensitivity, while unique structural identification of Q's causal efficacy is not supported.

---

## Core estimand

For latent states `q1, q2`, history/context `H`, allowed intervention set `U`, and observable response `Y`:

```text
Delta_RA(q1,q2 | u,H)
  = JSD(
      P(Y | do(u), q1, H),
      P(Y | do(u), q2, H)
    )

ICQ-RA(q1,q2 | H,U,Y)
  = max_{u in U} Delta_RA(q1,q2 | u,H)
```

Phase 0A fixes `D` to Jensen-Shannon distance.

The empirical estimator uses permutation-null subtraction:

```text
Delta_hat_corrected
  = max(
      0,
      JSD_empirical
      - mean(JSD_permutation_null)
    )
```

This correction is part of the estimator, not the theoretical definition.

---

## Synthetic qualification models

### ACTIVE

```text
q -> Y
q x U -> Y
```

Expected behavior: ICQ-RA above the declared ACTIVE sensitivity threshold.

### INACTIVE

```text
q exists
q -/-> Y
```

Expected behavior: ICQ-RA near the Null region.

### CONFOUNDED

```text
H -> q
H -> Y
q -/-> Y
```

Expected behavior: observational separation can exist while history-conditioned ICQ-RA remains near the Null region.

### Structural counterexample used in P0A-4B

```text
Z -> Q
Z x U -> Y
Q -/-> Y
```

This model produced a strong ICQ-RA signal without a direct causal path `Q -> Y`, establishing the Phase 0A non-identifiability boundary.

---

## Completed gate chain

| Gate | Purpose | Result |
|---|---|---|
| P0A-0 | Implementation / debug qualification | **PASS** |
| P0A-1 | Seed reproducibility pilot | **PASS** |
| P0A-2 | Synthetic Null threshold-exceedance calibration | **PASS** |
| P0A-3 | ACTIVE sensitivity on frozen held-out seeds | **PASS** |
| P0A-4A | Null-family residual discrimination audit | **PASS_EQUIVALENT** |
| P0A-4B | Structural identifiability counterexample | **FAIL_NONIDENTIFIABLE** |
| P0A-5 | Phase 0A Gate Review / Freeze Decision | **FREEZE_APPROVED_WITH_SCOPE_LIMITATION** |

---

## Key results

### P0A-1 — deterministic replay

Representative seeds:

```text
1101, 1115, 1130
```

All 9 scenario × seed cases reproduced exactly across forward and reversed execution order.

Qualified only:

```text
DETERMINISTIC_SEED_REPRODUCIBILITY
```

### P0A-2 — declared Null calibration

```text
INACTIVE
n = 30
mean ICQ-RA = 0.010359420576004546
max         = 0.0216481674918528
diagnostic exceedances > 0.05 = 0/30

CONFOUNDED
n = 30
mean ICQ-RA = 0.01479971335029107
max         = 0.03808708582728814
diagnostic exceedances > 0.05 = 0/30
```

For the declared 50/50 synthetic Null mixture:

```text
0 / 60 diagnostic exceedances
one-sided exact 95% upper bound
= 0.04870291331009752
```

This pooled bound applies only to the declared synthetic 50/50 mixture. It is not a universal or family-specific false-positive guarantee.

### P0A-3 — held-out ACTIVE sensitivity

Frozen seed bank:

```text
P0A3-HO-v1
2101-2130
n = 30
```

Frozen criterion:

```text
mean_seed(ICQ-RA) >= 0.15
```

Observed:

```text
mean    0.2488838299803236
std     0.010606465726866143
median  0.24968387098958572
min     0.23012517701890922
max     0.269254410429106
```

Decision:

```text
PASS
```

### P0A-4A — Null-family residual audit

Frozen paired seed bank:

```text
P0A4A-HO-v1
3101-3160
n = 60 pairs
```

Observed:

```text
mean Delta_N = 0.00507935140306689
95% CI       = [0.002355609537210807, 0.007803093268922973]
TOST margin  = +/- 0.01
paired sign-flip p = 0.00024
TOST         = PASS
```

Interpretation:

> CONFOUNDED is statistically higher than INACTIVE, but the difference remains within the preregistered practical-equivalence margin.

Decision:

```text
PASS_EQUIVALENT
```

### P0A-4B — structural non-identifiability

Frozen seed bank:

```text
P0A4B-HO-v1
4101-4130
n = 30 per alternative
```

The hidden-modifier proxy model:

```text
Z -> Q
Z x U -> Y
Q -/-> Y
```

produced:

```text
mean ICQ-RA      = 0.21500508978334615
ACTIVE threshold = 0.15
```

Therefore:

```text
ICQ-RA >= ACTIVE threshold
does NOT uniquely imply
Q -> Y
```

Decision:

```text
FAIL_NONIDENTIFIABLE
```

This is a valid scientific endpoint, not an implementation failure.

---

## Claim firewall

The following claims are prohibited:

```text
ICQ-RA uniquely identifies Q -> Y
ICQ-RA > 0 implies qualia exist
ICQ-RA > 0 implies qualia were measured
ICQ-RA = 0 implies qualia are absent
response difference implies phenomenal difference
synthetic qualification proves real-system identification
```

The working boundary is:

```text
Response-accessible != Structurally identified
Response-accessible != Phenomenal
```

---

## Debug and reproducibility layer

Failure localization:

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

Debug reports include:

- Python / NumPy / platform manifest
- configuration SHA-256
- q / H / u / Y fingerprints
- per-cell sample counts
- response moments
- observed JSD
- permutation-null statistics
- corrected JSD
- per-intervention ICQ-RA
- estimator reconstruction

The estimator reconstruction tolerance is:

```text
absolute tolerance = 1e-12
```

Current post-freeze debug state:

```text
Unit tests                         PASS
7 tests passed
Frozen metadata audit             PASS
Qualification rerun firewall      PASS
Archive-branch CI                 PASS
PR CI                             PASS
Push CI                           PASS
```

---

## Post-freeze CI policy

Phase 0A qualification evidence is historical and frozen.

Routine CI must **not** rerun P0A-1 through P0A-5 as if their seed banks remained unseen.

Routine CI is restricted to:

```text
package installation
unit tests
environment checks
frozen Phase 0A metadata audit
qualification rerun firewall
```

Historical qualification scripts remain in the repository for auditability and reproducibility, not for generating new held-out evidence.

---

## Install and implementation tests

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
pytest -q
```

A debug replay never changes the frozen scientific verdict:

```text
DEBUG_PASS != PHASE0A_REQUALIFICATION
```

---

## Archive record

Phase 0A is fixed by an exact commit and archive branch.

```text
Archive identifier:
phase0a-v0.1-frozen

Frozen commit:
86d8b801f9a1e32a3ffefcf0c404315cd3e1701c

Archive branch:
archive/phase0a-v0.1-frozen

Release record:
docs/releases/phase0a-v0.1-frozen.md
```

P0A-5 evidence artifact:

```text
Actions run: 33964427753
Artifact: icq-ra-p0a0-p0a5
Artifact ID: 9968964888
SHA-256:
aad67ccdcf829a3e4abcfb6a0f4a4b73638df282454d78e9db413bf2a8bf3610
```

The authoritative scientific status is the frozen Phase 0A protocol and release record. A Git tag or GitHub Release object is not required to interpret the scientific freeze state and is not asserted here unless independently created.

---

## Current authorized next directions

```text
ARCHIVE_PHASE0A
PREPARE_LIMITED_SCOPE_MANUSCRIPT
DESIGN_A_NEW_PROTOCOL_FOR_L4_IDENTIFICATION
DESIGN_A_SEPARATE_PROTOCOL_FOR_REAL_SYSTEMS
```

Not authorized under Phase 0A:

```text
CONFIRMATORY_REAL_DATA_RUN
L4_UPGRADE
QUALIA_CLAIM
```

---

## Phase 0B — L4 identification protocol (DRAFT)

Phase 0B is a separate protocol created after the frozen Phase 0A non-identifiability result.

```text
PROTOCOL_ID:
ICQ-RA-P0B-v0.1

STATUS:
DRAFT_FOR_PREREGISTRATION_AUDIT

COMPLETED AUDIT GATES:
P0B-0 PASS
P0B-1 PASS

CURRENT GATE:
P0B-2 INACTIVE_DIRECT NULL QUALIFICATION
ELIGIBLE / NOT AUTHORIZED

QUALIFICATION EXECUTION:
NOT AUTHORIZED
```

The Phase 0B question is narrower than general structural identification:

> If synthetic Q itself can be atomically intervened on, can a direct-intervention response metric distinguish direct Q causal efficacy from the hidden-modifier proxy that defeated Phase 0A?

Primary metric:

```text
ICQ-DI(Q->Y | H,U)
=
max_u weighted_mean_h
JSD[
  P(Y | do(Q=0), do(U=u), H=h),
  P(Y | do(Q=1), do(U=u), H=h)
]
```

Primary baseline:

```text
Phase 0A conditioning-based ICQ-RA
P(Y | do(U), Q, H)
```

Primary falsification:

```text
Z -> Q
Z x U -> Y
Q -/-> Y
```

Required Phase 0B pattern:

```text
Hidden-proxy Phase 0A baseline:
mean ICQ-RA >= 0.15

Hidden-proxy direct intervention:
mean ICQ-DI <= 0.05
```

Frozen untouched qualification seed banks:

```text
P0B-2 INACTIVE_DIRECT       6201-6230
P0B-3 DIRECT_ACTIVE         6301-6330
P0B-4 HIDDEN_MODIFIER      6401-6430
```

Routine CI may use only:

```text
6101-6103
DEBUG_ONLY_NO_SCIENTIFIC_INFERENCE
```

Even a complete Phase 0B PASS could support at most:

```text
L4_CONDITIONALLY_SUPPORTED_FOR_DIRECTLY_INTERVENABLE_SYNTHETIC_Q_ONLY
```

It would not authorize real-system identification, consciousness claims, or qualia claims.

See:

- [Phase 0B protocol](docs/phase0b_protocol.md)
- [Phase 0B design rationale](docs/phase0b_design_rationale.md)
- [P0B-0 / P0B-1 audit result](docs/p0b01_audit_result.md)

---

## Documentation

- [Phase 0A frozen protocol](docs/phase0a_protocol.md)
- [Debugging design](docs/debugging.md)
- [P0A-1 reproducibility](docs/p0a1_reproducibility.md)
- [P0A-2 Null calibration](docs/p0a2_null_calibration.md)
- [P0A-3 ACTIVE sensitivity](docs/p0a3_active_sensitivity.md)
- [P0A-4 orthogonal gate design](docs/p0a4_design.md)
- [P0A-5 Gate Review](docs/p0a5_gate_review.md)
- [Phase 0A frozen release record](docs/releases/phase0a-v0.1-frozen.md)
