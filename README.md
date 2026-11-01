# POND Embassy v12 Final — 8044B NVM Kernel

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23865745.svg)](https://doi.org/10.5281/zenodo.23865745)

**Artifact:** 8044-byte standalone kernel implementing a persistent monotonic counter at physical address 0x7E00.

**Property:** Maintains temporal continuity across host reboots. Provides externally verifiable timestamps via Bitcoin OTS anchoring.

**Interface:** Independent timing domain; exports read-only attestation to supervising kernels without requiring host kernel modification.

## Specification

- Size: 8044 B (a4c1a228)
- Resident: 0x7E00
- Persistence: NVM monotonic counter
- Verification: SHA256, OTS, Zenodo
- DOI: 10.5281/zenodo.23865745
- License: Apache-2.0 (code) AND CC0-1.0 (data)

## Verification

```sh
sha256sum pond-kernel-32kb/pond.img
cat ZENODO.txt
