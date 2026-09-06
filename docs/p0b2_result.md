# P0B-2 INACTIVE_DIRECT Null Qualification

**Protocol:** ICQ-RA-P0B-2-v0.1  
**Parent:** ICQ-RA-P0B-v0.1  
**Held-out bank:** P0B2-HO-v1  
**Seeds:** 6201-6230  
**n:** 30  
**Decision:** PASS

## Frozen decision rule

```text
mean_seed(ICQ-DI) <= 0.05
```

No threshold or generator tuning was performed after execution authorization.

## Observed result

```text
mean    0.012255957465935682
std     0.0074248519394979375
median  0.012447017307577569
q05     0.0017940479527481055
q95     0.02303821588814153
min     0.001435220334024419
max     0.027490121009634563
```

Frozen threshold:

```text
0.05
```

Therefore:

```text
0.012255957465935682 <= 0.05
PASS
```

## Interpretation

Under the declared synthetic INACTIVE_DIRECT generator and the frozen P0B-2 held-out bank, the direct-intervention ICQ-DI estimator remained within the preregistered Null ceiling.

This supports only the P0B-2 Null-control claim for the declared synthetic direct-intervention setting.

It does **not** establish:

- DIRECT_ACTIVE sensitivity
- hidden-modifier separation
- general structural identification
- real-system identification
- consciousness or qualia claims

## Provenance

```text
Workflow run:
33973310871

Execution head:
018fb520dfef82490f32ec4b95bec136c112174d

Artifact:
icq-ra-p0b2-one-shot

Artifact ID:
9971565732

SHA-256:
81ae84ba7a8aa46b35c9f1dc4740a9ebf62cfa886b306c4a442d743030d63ec8
```

The one-shot workflow was removed immediately after result capture to prevent accidental rerun of the held-out bank.

## Current gate

```text
P0B-0 PASS
P0B-1 PASS
P0B-2 PASS

NEXT ELIGIBLE:
P0B-3 DIRECT_ACTIVE SENSITIVITY

P0B-3 EXECUTION:
NOT AUTHORIZED
```
