# P0B-4 HIDDEN_MODIFIER_PROXY Falsification Qualification

**Protocol:** ICQ-RA-P0B-4-v0.1  
**Held-out bank:** P0B4-HO-v1  
**Seeds:** 6401-6430  
**n:** 30  
**Decision:** **PASS**

## Frozen joint rule

```text
mean_seed(Phase0A ICQ-RA) >= 0.15
AND
mean_seed(ICQ-DI) <= 0.05
```

Both means were mandatory. No substitution or rescue statistic was allowed.

## Observed Phase 0A conditioning baseline

```text
mean    0.2148279779106048
std     0.009686676633682459
median  0.2138082618670108
q05     0.2027339410931112
q95     0.2312050297319923
min     0.19420267808235833
max     0.23513774888565356
```

## Observed direct intervention ICQ-DI

```text
mean    0.010314975030800982
std     0.005142900354245091
median  0.009577571258797903
q05     0.003197070138211475
q95     0.01920046583849038
min     0.0023662058570749654
max     0.021064653546187785
```

Therefore:

```text
0.2148279779106048 >= 0.15
AND
0.010314975030800982 <= 0.05

P0B-4 PASS
```

## Provenance

```text
Workflow run:    34165808251
Execution head:  f1bde4c55470f48ad4a44daeba034bcbc591e6d6
Execution parent:7fb6d0d1c4101dbcd9ae094a6a92f65693d4e5e5
Run attempt:     1
Artifact:        icq-ra-p0b4-one-shot
Artifact ID:     10034099366
SHA-256:         2826093cf4c12c9e74930187413eec3232f2b9a6051b88755fb15c778f34eae8
```

## Interpretation

Supported only:

> Under the declared frozen synthetic hidden-modifier generator, the Phase 0A conditioning metric remained ACTIVE-like while atomic do(Q) produced a Null-like direct-intervention metric on the frozen P0B-4 held-out bank.

This is the specific discrimination pattern that P0B-4 preregistered.

Not established:

- general L4 structural identification
- real-system identification
- confirmatory real-data validity
- consciousness
- qualia or phenomenal-state inference

## Next gate

```text
P0B-5 GATE REVIEW AND FREEZE DECISION
ELIGIBLE
NOT AUTHORIZED
```

No L4 upgrade is authorized before P0B-5.
