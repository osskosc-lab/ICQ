# P0A-3 ACTIVE Sensitivity Qualification

**PROTOCOL_ID:** ICQ-RA-P0A-3-v0.1  
**GATE:** P0A-3_ACTIVE_SENSITIVITY_QUALIFICATION  
**STATUS:** FROZEN_BEFORE_EXECUTION

## Purpose

Test whether the ICQ-RA estimator detects a known synthetic response-accessible latent-state effect on a seed bank that was not used in P0A-1 or P0A-2.

## Held-out seed bank

Frozen before execution:

```text
P0A3-HO-v1
2101-2130
n = 30
```

Previously observed seeds are permanently excluded:

```text
1101-1130
```

The runner stops before generating ACTIVE outputs if any overlap exists.

## Primary proposition

For the declared ACTIVE structural generator and frozen held-out seed bank:

```text
mean_seed(ICQ-RA) >= 0.15
```

The threshold 0.15 is inherited unchanged from the original Phase 0A draft configuration and is explicitly an across-seed mean threshold.

## PASS rule

All must hold:

1. Held-out seed bank is disjoint from all previously observed seeds.
2. Exactly 30 held-out runs execute.
3. All debug/invariant/reconstruction audits pass.
4. Mean held-out ACTIVE ICQ-RA is at least 0.15.

No additional effect-size rule may be introduced after results are observed.

## Claim ceiling

A PASS supports only:

> The declared synthetic ACTIVE generator exceeded the frozen across-seed mean ICQ-RA sensitivity threshold on the frozen held-out seed bank.

It does not authorize Phase 0A as a whole, any confirmatory real-data run, or any qualia claim.

```text
P0A-3 PASS != PHASE0A PASS
P0A-3 PASS != REAL-SYSTEM IDENTIFICATION
P0A-3 PASS != QUALIA EVIDENCE
```
