# P0A-2 Null Calibration

**PROTOCOL_ID:** ICQ-RA-P0A-2-v0.1  
**GATE:** P0A-2_NULL_CALIBRATION  
**STATUS:** EXECUTION_AUTHORIZED

## Purpose

Measure false-positive behavior of the already-defined ICQ-RA estimator under structural Null models before ACTIVE sensitivity qualification.

This gate does not alter the fixed threshold after observing results.

## Null families

```text
INACTIVE:
q exists, q -/-> Y

CONFOUNDED:
H -> q
H -> Y
q -/-> Y
```

All 30 Phase 0A seeds are used for each family.

```text
30 INACTIVE + 30 CONFOUNDED = 60 Null runs
```

## Fixed threshold

The threshold remains the existing Phase 0A draft value:

```text
ICQ-RA <= 0.05
```

An exceedance is defined strictly as:

```text
ICQ-RA > 0.05
```

## PASS conditions

All conditions must hold:

1. Exactly 60 declared Null runs execute.
2. Every run passes input and estimator debug audits.
3. INACTIVE has zero threshold exceedances.
4. CONFOUNDED has zero threshold exceedances.
5. Each Null-family mean remains at or below the fixed threshold.
6. The pooled one-sided 95% exact binomial upper bound on the per-run threshold-exceedance probability is <= 0.05.

For zero exceedances in 60 runs, the one-sided exact upper bound is approximately:

```text
1 - 0.05^(1/60) ~= 0.0487
```

Family-specific 30-run upper bounds are reported but are not independently required to be <= 0.05; with only 30 observations they are necessarily wider.

## Interpretation boundary

A PASS can support only:

> Under the two declared synthetic Null families and fixed simulation conditions, the ICQ-RA estimator showed no threshold exceedance across the declared 60-run calibration set, with the pooled exact one-sided 95% upper bound satisfying the predefined 5% ceiling.

It does not establish false-positive control for arbitrary real systems or other Null families.

```text
P0A-2 PASS != PHASE0A PASS
P0A-2 PASS != ACTIVE SENSITIVITY
P0A-2 PASS != QUALIA EVIDENCE
```

**Next eligible gate after PASS:** P0A-3 ACTIVE Sensitivity Qualification.
