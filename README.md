[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23865745.svg)](https://doi.org/10.5281/zenodo.23865745)
[![C](https://img.shields.io/badge/C-82.9%25-00ff88?style=flat)](pond-kernel-32kb/c-kernel/)
[![Size](https://img.shields.io/badge/size-8044B-blue)](pond-kernel-32kb/final-bins/pond-256k-v12-final-a4c1a228.bin)
[![Kernel](https://img.shields.io/badge/kernel-a4c1a2285f33c07a-black)](pond-kernel-32kb/c-kernel/PROOF.txt)

**POND Embassy v12 Final — 8044B NVM Kernel — DOI: 10.5281/zenodo.23865745**
Canonical: `a4c1a2285f33c07a679989f4ce5a4346a1ba64814bc05854a1577ca6a3672005`


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
