# P0B-0 / P0B-1 Formal Audit Result

**Protocol:** ICQ-RA-P0B-01-v0.1  
**Parent protocol:** ICQ-RA-P0B-v0.1  
**Execution status:** COMPLETE

## P0B-0 — Protocol and Implementation Audit

```text
DECISION: PASS
```

All required checks passed:

- parent protocol ID match
- protocol remains DRAFT_FOR_PREREGISTRATION_AUDIT
- qualification execution remains unauthorized
- confirmatory real-data execution remains unauthorized
- phenomenal / qualia claims remain unauthorized
- gate order exact
- seed namespaces pairwise disjoint
- Phase 0A and Phase 0B seed namespaces disjoint
- thresholds inherited from Phase 0A with no Phase 0B tuning
- one primary metric present
- one primary baseline present
- one primary falsification present

## P0B-1 — Atomic do(Q) Integrity Audit

```text
DECISION: PASS
```

Debug-only seeds:

```text
6101
6102
6103
```

No qualification seed was executed.

### INACTIVE_DIRECT

For all three debug seeds:

```text
max_abs_integrity_error = 0.0
```

Thus do(Q=0) and do(Q=1) leave Y unchanged when Q has no declared path to Y.

### DIRECT_ACTIVE

For all three debug seeds:

```text
max_abs_integrity_error
= 5.551115123125783e-16
```

This is below the frozen tolerance:

```text
1e-12
```

The observed response difference matches exactly, up to floating-point roundoff:

```text
Y(do(Q=1)) - Y(do(Q=0))
=
direct_q_coupling * U
```

### HIDDEN_MODIFIER_PROXY

For all three debug seeds:

```text
max_abs_integrity_error = 0.0
```

Thus atomic intervention on Q does not alter Y when the generator is:

```text
Z -> Q
Z x U -> Y
Q -/-> Y
```

## Execution issue and correction

The first formal audit attempt failed before scientific evaluation with:

```text
ModuleNotFoundError: No module named 'experiments'
```

This was localized to the audit runner import path and corrected without changing:

- protocol
- thresholds
- seeds
- estimator
- intervention semantics
- gate criteria

The corrected rerun passed.

## Provenance

```text
Successful workflow run:
33971378525

Artifact:
icq-ra-phase0b-p0b01-audit

Artifact ID:
9971018941

SHA-256:
8f873bf42718e2947d8319fc3a5782b0c6565f185842f5f22d44002a7a12bb13

Successful audit head:
6977d5843e6e3bad65f4be2b7ff5f338ab734037
```

## Gate state at time of formal P0B-0 / P0B-1 audit

This section is historical provenance for the original formal audit. The live repository gate may advance after later gates complete; `configs/phase0b.json` is authoritative for the current gate.


```text
P0B-0  PASS
P0B-1  PASS

NEXT ELIGIBLE:
P0B-2 INACTIVE_DIRECT NULL QUALIFICATION

P0B-2 EXECUTION:
NOT AUTHORIZED
```

## Claim firewall

This audit authorizes no scientific L4 upgrade.

```text
QUALIFICATION_EXECUTION       NOT AUTHORIZED
CONFIRMATORY_REAL_DATA_RUN    NOT AUTHORIZED
L4_UPGRADE                    NOT AUTHORIZED
QUALIA / PHENOMENAL CLAIM     NOT AUTHORIZED
```

The strongest current claim is limited to:

> The Phase 0B protocol and implementation survived the declared protocol audit and atomic do(Q) integrity audit on debug-only seeds.
