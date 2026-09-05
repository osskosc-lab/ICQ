# ICQ-RA Phase 0A — Frozen Release Record

**Release candidate:** `phase0a-v0.1-frozen`  
**Final verdict:** `B — CONDITIONALLY_SUPPORTED`  
**Phase 0A status:** `FROZEN_OPERATIONAL_SCOPE_L1_L3`

## Qualification ledger

```text
P0A-1   PASS
P0A-2   PASS
P0A-3   PASS
P0A-4A  PASS_EQUIVALENT
P0A-4B  FAIL_NONIDENTIFIABLE
P0A-5   FREEZE_APPROVED_WITH_SCOPE_LIMITATION
```

## Frozen epistemic scope

```text
L1 Implementation
  SUPPORTED

L2 Null Control
  SUPPORTED_WITH_EQUIVALENCE_MARGIN

L3 Response Sensitivity
  SUPPORTED

L4 Structural Identification
  REJECTED_NONIDENTIFIABLE

L5 Qualia / Phenomenal
  NOT AUTHORIZED
```

## Core conclusion

```text
Operationally Useful != Structurally Identified
```

ICQ-RA is frozen as a reproducible synthetic response-accessibility detector under the declared Phase 0A conditions. It is not qualified as a unique identifier of Q's causal efficacy.

## P0A-4A residual audit

```text
mean Delta_N = 0.00507935140306689
95% CI       = [0.002355609537210807, 0.007803093268922973]
TOST margin  = +/- 0.01
decision     = PASS_EQUIVALENT
```

## P0A-4B structural counterexample

```text
Z -> Q
Z x U -> Y
Q -/-> Y

mean ICQ-RA      = 0.21500508978334615
ACTIVE threshold = 0.15
decision         = FAIL_NONIDENTIFIABLE
```

Therefore:

```text
ICQ-RA >= ACTIVE threshold
does not uniquely imply
Q -> Y
```

## Archive evidence

P0A-5 qualification artifact:

```text
Actions run: 33964427753
Artifact: icq-ra-p0a0-p0a5
Artifact ID: 9968964888
SHA-256:
aad67ccdcf829a3e4abcfb6a0f4a4b73638df282454d78e9db413bf2a8bf3610
```

## Post-freeze policy

Routine CI no longer reruns qualification seed banks. It performs implementation tests and frozen-metadata checks only.

## Claim firewall

Not authorized:

```text
ICQ-RA uniquely identifies Q -> Y
ICQ-RA identifies consciousness
ICQ-RA measures qualia
ICQ-RA = 0 implies absence of qualia
confirmatory real-data execution under Phase 0A
```

Any L4 recovery or real-system extension requires a new protocol.
