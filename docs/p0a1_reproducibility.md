# P0A-1 Seed Reproducibility Pilot

**PROTOCOL_ID:** ICQ-RA-P0A-1-v0.1  
**GATE:** P0A-1_SEED_REPRODUCIBILITY_PILOT  
**PURPOSE:** deterministic replay qualification only

## Design

Representative seeds:

```text
1101, 1115, 1130
```

Scenarios:

```text
ACTIVE
INACTIVE
CONFOUNDED
```

Total cases per pass: 9.

Two manifests are generated in separate Python processes:

- Pass A: forward case order
- Pass B: reversed case order

Reversing order tests whether any hidden process-global RNG or mutable state contaminates a seed-specific result.

## PASS rule

Every one of the 9 cases must satisfy exact equality across Pass A and Pass B for:

- q/H/u/Y dataset SHA-256 fingerprints
- canonical Phase 0A config SHA-256
- ICQ-RA
- OBS-Distance
- per-intervention values
- valid-cell counts

Additionally, both passes must independently satisfy:

- input invariant audit
- estimator reconstruction audit
- debug_pass

No tolerance is used for the cross-pass comparison. The expected result on the same declared software/environment stack is bitwise-deterministic replay of generated arrays and exact JSON numeric equality.

## Claim ceiling

A PASS supports only:

> The declared ICQ-RA synthetic pipeline reproduced the same seed-specific datasets and outputs under reversed execution order in the P0A-1 pilot.

It does not qualify the Phase 0A scientific thresholds, calibrate Null behavior, or authorize any qualia-related claim.

```text
P0A-1 PASS != PHASE0A PASS
P0A-1 PASS != NULL CALIBRATION
P0A-1 PASS != QUALIA EVIDENCE
```
