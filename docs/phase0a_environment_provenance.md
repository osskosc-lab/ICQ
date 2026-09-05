# Phase 0A Frozen Environment Provenance

**Purpose:** archival reproducibility hardening only  
**Scientific verdict:** unchanged  
**Qualification rerun:** prohibited by this record  
**Confirmatory / real-data execution:** not authorized  
**Qualia / phenomenal claims:** not authorized

## Authoritative scientific freeze

```text
Phase 0A archive commit:
86d8b801f9a1e32a3ffefcf0c404315cd3e1701c

Archive branch:
archive/phase0a-v0.1-frozen

Final verdict:
B — CONDITIONALLY_SUPPORTED

Scientific scope:
FROZEN_OPERATIONAL_SCOPE_L1_L3
```

This provenance file does not alter or supersede the frozen scientific commit. It records the software environment observed when the archive branch was validated by post-freeze CI.

## Evidence source

```text
GitHub Actions run:
33964641438

Job:
101302489850

Workflow role:
post-freeze implementation / metadata audit

Qualification seed rerun:
NO
```

The CI job reported:

```text
Unit tests:
7 passed in 0.18s

Frozen metadata audit:
PASS

Qualification rerun firewall:
PASS
```

## Runtime observed in the archived CI log

```text
Python:
3.12.14
full sys.version:
3.12.14 (main, Aug 13 2026, 02:47:42) [GCC 13.3.0]

Platform:
Linux-6.17.0-1022-azure-x86_64-with-glibc2.39

NumPy:
2.5.2

SciPy:
1.18.1

pytest:
8.4.2
```

## Python packages explicitly observed as installed

The archived CI log explicitly recorded:

```text
iniconfig==2.3.0
numpy==2.5.2
packaging==26.3
pluggy==1.6.0
pygments==2.21.0
pytest==8.4.2
scipy==1.18.1
```

The repository package itself was installed editable from the frozen checkout as:

```text
icq-ra==0.1.0
source:
frozen repository checkout
```

The archived build log also recorded an editable wheel build for `icq-ra==0.1.0`.

## Archival lock file

The corresponding evidence-backed package pins are stored in:

```text
requirements-phase0a-frozen.txt
```

This lock is intentionally **not** wired into routine CI and must not be interpreted as authorization to rerun qualification seeds.

## What this provenance does guarantee

It preserves the exact versions of the runtime and packages that were explicitly visible in the archived CI evidence:

- Python 3.12.14
- Linux kernel / glibc platform string reported by Python
- NumPy 2.5.2
- SciPy 1.18.1
- pytest 8.4.2
- pytest runtime dependencies listed above
- repository package version 0.1.0 installed from the frozen checkout

## What this provenance does not guarantee

This is **not a complete bit-for-bit environment reconstruction manifest**.

The archived log does not provide exact versions for every tool involved in environment construction, including all of:

- pip
- setuptools
- wheel / build backend dependencies
- GitHub-hosted runner image digest
- operating-system package set outside the reported platform string

Therefore the correct status is:

```text
ARCHIVAL_REPRODUCIBILITY_HARDENED
NOT_FULL_BITWISE_ENVIRONMENT_LOCK
```

No claim is made that a future fresh machine will reproduce every bit or floating-point implementation detail solely from this file.

## Scientific firewall

This archival hardening changes none of the Phase 0A scientific results:

```text
L1 SUPPORTED
L2 SUPPORTED_WITH_EQUIVALENCE_MARGIN
L3 SUPPORTED
L4 REJECTED_NONIDENTIFIABLE
L5 NOT AUTHORIZED
```

The core conclusion remains:

```text
Operationally Useful != Structurally Identified
```

No P0A qualification, confirmatory, real-data, L4-upgrade, consciousness, or qualia-related run is authorized by this provenance record.
