# P0A-2 Null Calibration — Semantic Clarification

**PROTOCOL_ID:** ICQ-RA-P0A-2-v0.1  
**SEMANTIC_REVISION:** v0.1.1_NO_NUMERIC_CHANGE  
**GATE:** P0A-2_NULL_CALIBRATION

The numeric P0A-2 result is preserved. This revision narrows the meaning of the thresholds and pooled bound; it does not alter seeds, generated data, estimator parameters, or the observed values.

## 1. Mean threshold and per-run diagnostic threshold are distinct

Phase 0A qualification thresholds are **across-seed mean thresholds**:

```text
ACTIVE mean ICQ-RA      >= 0.15
INACTIVE mean ICQ-RA    <= 0.05
CONFOUNDED mean ICQ-RA  <= 0.05
```

P0A-2 separately uses the fixed value 0.05 as a **single-run diagnostic threshold**:

```text
per-run diagnostic exceedance := ICQ-RA > 0.05
```

The same numeric value does not make these the same estimand or decision rule.

Therefore:

```text
P0A-2 0/60 exceedances
!=
false-positive rate of the Phase 0A across-seed mean decision rule
```

## 2. Pooled bound is mixture-specific

P0A-2 contains:

```text
30 INACTIVE
30 CONFOUNDED
```

The pooled exact binomial bound is interpreted only for the declared synthetic 50/50 Null mixture:

```text
P_null = 0.5 * P_INACTIVE + 0.5 * P_CONFOUNDED
```

It is not a family-specific guarantee.

With 0/30 in each family, the family-specific one-sided 95% upper bound remains about 0.095. With 0/60 pooled under the declared mixture, the one-sided 95% upper bound is about 0.0487.

Thus the permitted claim is:

> Under the declared 50/50 synthetic mixture of INACTIVE and CONFOUNDED Null generators, no per-run diagnostic threshold exceedance occurred in 60 runs, and the mixture-specific one-sided exact 95% upper bound was below 0.05.

Not permitted:

```text
INACTIVE family FPR < 5% proven
CONFOUNDED family FPR < 5% proven
arbitrary Null FPR < 5% proven
Phase 0A mean-decision FPR < 5% proven
```

## 3. Held-out integrity

Seeds 1101-1130 have now been observed in P0A-1/P0A-2 and are permanently classified as:

```text
DEVELOPMENT_AND_NULL_CALIBRATION_ONLY
NOT_HELD_OUT
```

P0A-3 must use a distinct, frozen seed bank.

## Claim firewall

```text
P0A-2 PASS != PHASE0A PASS
P0A-2 PASS != ACTIVE SENSITIVITY
P0A-2 PASS != QUALIA EVIDENCE
```
