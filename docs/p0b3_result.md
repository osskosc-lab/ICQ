# P0B-3 DIRECT_ACTIVE Sensitivity Qualification

**Protocol:** ICQ-RA-P0B-3-v0.1  
**Held-out bank:** P0B3-HO-v1  
**Seeds:** 6301-6330  
**n:** 30  
**Decision:** **PASS**

## Frozen rule

```text
mean_seed(ICQ-DI) >= 0.15
```

Only the across-seed arithmetic mean entered the gate decision.

## Observed result

```text
mean    0.2524101694466042
std     0.009340808271323851
median  0.2522989191334548
q05     0.23934134827280118
q95     0.2680915247661997
min     0.23209107913783666
max     0.2746032637641278
```

Therefore:

```text
0.2524101694466042 >= 0.15
P0B-3 PASS
```

## Provenance

```text
Workflow run:    34065143572
Execution head:  64a93ddc36dfe2a59b3b97bd35701ed50ecaccde
Execution parent:9b7ed6eb43e2af3d5f7c325cb2e903ef347857fc
Run attempt:     1
Artifact:        icq-ra-p0b3-one-shot
Artifact ID:     9998695614
SHA-256:         dea9cc9bef79faacdd079e8541ad066b27ac9d563ea04d5822508a9f5eb09fe4
```

The scientific source snapshot in the result is the exact snapshot frozen before execution.

## Interpretation

Supported only:

> Under the declared frozen synthetic DIRECT_ACTIVE generator, ICQ-DI exceeded the preregistered across-seed mean sensitivity threshold on the frozen P0B-3 held-out bank.

Not established:

- hidden-modifier separation
- general L4 structural identification
- real-system identification
- consciousness
- qualia or phenomenal-state inference

## Next gate

```text
P0B-4 HIDDEN_MODIFIER_PROXY FALSIFICATION
ELIGIBLE
NOT AUTHORIZED
```
