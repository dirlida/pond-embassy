# POND Embassy - Verifiable Time Anchor

v2: RAW signs WALL

- RAW: cntvct_el0 / rdtsc / FED00000h - monotonic, never lags
- WALL: PHC HW timestamp or SW fallback
- Attestation: sig = hash(utc_ns || raw_tsc || prev_hash)
- Genesis: fb204d33

Field test: Kelaat Mgouna ARM64 mobile
Chain: fb204d33 -> 5594ad61f560851a -> 592711257590d6ee -> 22f6d8ef298f618e
HW timestamp unavailable on lo (expected mobile), SW uncert 6000000ns aligns with industry TrueTime bound

Deployed as auditor sidecar:
pond.now_verified() -> {raw, wall, uncert, prev_hash, sig}
Dashboard: TrueTime interval vs HW-anchored attested time

Build 676e31f
