# Phase 09.1 — Seedance-Informed Video Subchannel Factorization Hypothesis

**Phase:** 09.1
**Date:** 2026-03-22
**Authority source:** `docs/inputs/review-packs/2026-03-22_science_engineering_pack/02_AUTHORITY_GATES_AND_NUMBERS.md`
  (accessed via `origin/reorientation/2026-04-17`)

## What Was Tested

Phase 09.1 tested whether introducing a factorized multi-subchannel bundle
(informed by Seedance-style temporal decomposition) could beat the simpler
flat and temporal-only lane baselines.

## Results

Aggregate across 3 clips:

| Metric | Value |
|---|---|
| Clip count | 3 |
| Factorized bundle total | 12,074 bytes |
| Flat total | 27,495 bytes |
| Temporal-only total | 6,314 bytes |
| Bundle vs flat ratio | 0.6866x |
| Bundle vs temporal-only ratio | 1.7571x |
| Mean entity reuse ratio | 0.7042 |
| Factorized refresh help seen | true |
| Dynamic clip present | true |
| Hard-cut clip present | true |
| Audio clip present | false |

## Interpretation

- The factorized bundle beats the flat lane (0.6866x ratio, smaller).
- The factorized bundle loses to the simpler temporal-only split (1.7571x, larger).
- The persistence carrier has not earned its added complexity.
- Clip heterogeneity (dynamic, hard-cut) was represented in the test surface.

## What Fell Out

The Seedance-informed subchannel factorization is not the right decomposition
for this surface. The temporal-only split is cheaper and smaller. The
factorized bundle's additional complexity is not justified by the signal.

## Verdict

Descriptive label: `flat_lane_still_dominant`
Canonical enum: `INCONCLUSIVE`
