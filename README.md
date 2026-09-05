# ICQ

Information Causal Quantity research repository.

This repository currently contains the experimental **ICQ-RA (Response Accessibility)** branch: a falsification-first attempt to operationalize whether a latent internal-state difference can be causally extracted as a difference in observable responses under declared interventions.

> **Important:** ICQ-RA does not measure qualia, does not establish that qualia exist, and does not identify a phenomenal state.

---

## ICQ-RA: Response Accessibility

### Minimal research question

Given two latent internal states, can an allowed intervention make their difference observable as a difference in response distributions?

For latent states `q1, q2`, history/context `H`, allowed intervention set `U`, and observable response `Y`:

```text
ICQ-RA(q1,q2 | H,U,Y)
  = max_{u in U} D[
      P(Y | do(u), q1, H),
      P(Y | do(u), q2, H)
    ]
```

Phase 0A fixes `D` to Jensen-Shannon distance.

The empirical estimator uses permutation-null subtraction to reduce finite-sample positive bias:

```text
Delta_hat_corrected
  = max(
      0,
      JSD_empirical
      - mean(JSD_permutation_null)
    )
```

This correction belongs to the estimator. It is not part of the theoretical definition of ICQ-RA.

---

## Claim firewall

ICQ-RA is an **operational response-accessibility quantity**.

The following inferences are not authorized:

```text
ICQ-RA > 0  => qualia exist
ICQ-RA > 0  => qualia were measured
ICQ-RA = 0  => qualia are absent
response difference => phenomenal difference
```

The strongest permitted interpretation at this stage is:

> A declared latent-state difference survived the specified causal-response accessibility tests under the tested synthetic model and controls.

---

## Phase 0A synthetic qualification models

Phase 0A currently uses synthetic structural models with known causal structure.

### ACTIVE

```text
q -> Y
q x intervention -> response difference
```

The latent state causally modulates the response under intervention.

Expected behavior:

```text
ICQ-RA > Null level
```

### INACTIVE

```text
q exists
q -/-> Y
```

The latent state exists in the generator but has no structural response path.

Expected behavior:

```text
ICQ-RA near 0
```

### CONFOUNDED

```text
H -> q
H -> Y
q -/-> Y
```

History produces observational separation between q groups without a causal q-to-Y path.

Expected behavior:

```text
OBS-Distance > 0
history-conditioned ICQ-RA near 0
```

This is the primary protection against mistaking correlation for causal response accessibility.

---

## Current qualification status

| Gate | Purpose | Status |
|---|---|---|
| P0A-0 | Implementation / debug qualification | **PASS** |
| P0A-1 | Seed reproducibility pilot | **PASS** |
| P0A-2 | Synthetic Null threshold-exceedance calibration | **PASS** |
| P0A-3 | ACTIVE sensitivity on frozen held-out seeds | **PASS** |
| P0A-4A | Null-family residual discrimination audit | **PASS_EQUIVALENT** |
| P0A-4B | Structural identifiability counterexample | **FAIL_NONIDENTIFIABLE** |
| P0A-5 | Phase 0A Gate Review / Freeze Decision | **FREEZE APPROVED WITH SCOPE LIMITATION** |
| Phase 0A final status | Operational qualification scope | **FROZEN L1-L3** |
| Confirmatory real-data run | External/real-system test | **NOT AUTHORIZED** |
| Qualia claim | Phenomenal interpretation | **NOT AUTHORIZED** |

---

## P0A-1 — Seed Reproducibility Pilot

Protocol:

```text
ICQ-RA-P0A-1-v0.1
```

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

Nine cases were executed twice in separate Python processes:

- Pass A: forward order
- Pass B: reversed order

All nine cases matched exactly on:

- dataset SHA-256
- config SHA-256
- ICQ-RA
- OBS-Distance
- per-intervention ICQ-RA
- valid-cell counts
- input invariants
- estimator reconstruction
- debug audit

Result:

```text
P0A-1_SEED_REPRODUCIBILITY_PILOT: PASS
```

This supports deterministic seed-specific replay only.

---

## P0A-2 — Null Calibration

Protocol:

```text
ICQ-RA-P0A-2-v0.1
semantic revision: v0.1.1_NO_NUMERIC_CHANGE
```

The original numeric result is preserved, but the interpretation was narrowed after audit.

### Threshold semantics

Two different decision quantities are now explicitly separated.

Phase 0A gate-level thresholds are **across-seed mean thresholds**:

```text
ACTIVE mean ICQ-RA      >= 0.15
INACTIVE mean ICQ-RA    <= 0.05
CONFOUNDED mean ICQ-RA  <= 0.05
```

P0A-2 separately uses `0.05` as a **single-run diagnostic threshold**:

```text
per-run diagnostic exceedance := ICQ-RA > 0.05
```

The same numeric value does not make these the same estimand.

Therefore:

```text
P0A-2 threshold-exceedance calibration
!=
false-positive rate of the Phase 0A across-seed mean decision rule
```

### Null results

```text
INACTIVE
n = 30
mean ICQ-RA = 0.010359420576004546
max = 0.0216481674918528
diagnostic exceedances = 0/30

CONFOUNDED
n = 30
mean ICQ-RA = 0.01479971335029107
max = 0.03808708582728814
diagnostic exceedances = 0/30
```

Family-specific one-sided 95% exact upper bounds are approximately:

```text
0.0950
```

They are **not** interpreted as a family-specific <5% guarantee.

The pooled result is interpreted only for the declared synthetic 50/50 Null mixture:

```text
P_null
  = 0.5 * P_INACTIVE
  + 0.5 * P_CONFOUNDED
```

Observed:

```text
0 / 60 diagnostic exceedances
one-sided exact 95% upper bound
= 0.04870291331009752
```

Permitted interpretation:

> Under the declared 50/50 synthetic mixture of INACTIVE and CONFOUNDED generators, no per-run diagnostic threshold exceedance occurred across 60 runs, and the mixture-specific one-sided exact 95% upper bound was below 0.05.

---

## P0A-3 — ACTIVE Sensitivity Qualification

Protocol:

```text
ICQ-RA-P0A-3-v0.1
```

A new seed bank was frozen before execution:

```text
P0A3-HO-v1
seeds: 2101-2130
n = 30
```

Previously observed seeds `1101-1130` are permanently classified as development / Null-calibration seeds and are forbidden from P0A-3.

The runner stops before ACTIVE generation if any seed overlap is detected.

Frozen primary rule:

```text
mean_seed(ICQ-RA) >= 0.15
```

Observed held-out ACTIVE result:

```text
n       30
mean    0.2488838299803236
std     0.010606465726866143
median  0.24968387098958572
q05     0.23199263023022018
q95     0.2628354530472504
min     0.23012517701890922
max     0.269254410429106
```

Result:

```text
0.2488838299803236 >= 0.15
P0A-3_ACTIVE_SENSITIVITY_QUALIFICATION: PASS
```

This supports synthetic ACTIVE sensitivity on the frozen held-out seed bank only.

---

## Debug and reproducibility layer

The debug system localizes failure in this order:

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

- Python / NumPy / platform information
- config SHA-256
- q / H / u / Y SHA-256 fingerprints
- per-cell q0 / q1 counts
- response mean / standard deviation
- observed JSD
- permutation-null mean / std / min / max
- corrected JSD
- per-intervention ICQ-RA
- reconstructed max-U ICQ-RA
- independent estimator reconstruction audit

The main estimator and debug reconstruction must agree to absolute tolerance:

```text
1e-12
```

Mismatch is an implementation STOP.

---

## Install and test

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
pytest -q
```

---

## Single-seed debug replay

```bash
python experiments/phase0a.py \
  --config configs/phase0a.json \
  --out results/replay.json \
  --scenario CONFOUNDED \
  --seed 1101 \
  --debug-dir results/debug
```

A debug replay never qualifies Phase 0A:

```text
DEBUG_PASS != PHASE0A_PASS
```

---

## Gate execution

### P0A-1

```bash
python experiments/p0a1_manifest.py \
  --phase0a-config configs/phase0a.json \
  --pilot-config configs/p0a1_reproducibility.json \
  --order forward \
  --out results/p0a1/pass_a.json
```

### P0A-2

```bash
python experiments/p0a2_null_calibration.py \
  --phase0a-config configs/phase0a.json \
  --calibration-config configs/p0a2_null_calibration.json \
  --out results/p0a2/decision.json
```

### P0A-3

```bash
python experiments/p0a3_active_sensitivity.py \
  --phase0a-config configs/phase0a.json \
  --p0a3-config configs/p0a3_active_sensitivity.json \
  --out results/p0a3/decision.json
```

The qualification chain P0A-1 through P0A-5 has been completed and archived. After the Phase 0A freeze, routine CI is restricted to implementation/debug tests so the qualification seed banks are not repeatedly treated as held-out evidence.

---

## Research-state boundary

Current state:

```text
P0A-0  PASS
P0A-1  PASS
P0A-2  PASS
P0A-3  PASS
P0A-4A PASS_EQUIVALENT
P0A-4B FAIL_NONIDENTIFIABLE
P0A-5  FREEZE_APPROVED_WITH_SCOPE_LIMITATION

FINAL VERDICT                  B — CONDITIONALLY_SUPPORTED
PHASE0A STATUS                 FROZEN_OPERATIONAL_SCOPE_L1_L3
L4 STRUCTURAL IDENTIFICATION   REJECTED_NONIDENTIFIABLE
CONFIRMATORY REAL-DATA RUN     NOT AUTHORIZED
QUALIA CLAIM                   NOT AUTHORIZED
```

Passing synthetic qualification gates does not establish that ICQ-RA identifies consciousness, subjective experience, or qualia.

---

## Documentation

- [Phase 0A protocol](docs/phase0a_protocol.md)
- [Debugging design](docs/debugging.md)
- [P0A-1 reproducibility](docs/p0a1_reproducibility.md)
- [P0A-2 Null calibration](docs/p0a2_null_calibration.md)
- [P0A-3 ACTIVE sensitivity](docs/p0a3_active_sensitivity.md)


---

## P0A-4 / P0A-5 final boundary

P0A-4A found a small but systematic positive Null-family residual:

```text
mean Delta_N = 0.00507935140306689
95% CI       = [0.002355609537210807, 0.007803093268922973]
TOST margin  = +/- 0.01
decision     = PASS_EQUIVALENT
```

P0A-4B constructed a hidden-modifier counterexample:

```text
Z -> Q
Z x U -> Y
Q -/-> Y

mean ICQ-RA = 0.21500508978334615
ACTIVE threshold = 0.15

decision = FAIL_NONIDENTIFIABLE
```

Therefore:

```text
Operationally Useful != Structurally Identified
```

P0A-5 formally froze Phase 0A at L1-L3.

The strongest authorized claim is that ICQ-RA is a reproducible **synthetic response-accessibility detector under the declared Phase 0A conditions**. It is not a unique identifier of Q's causal efficacy.

- [P0A-4 design](docs/p0a4_design.md)
- [P0A-5 Gate Review](docs/p0a5_gate_review.md)
