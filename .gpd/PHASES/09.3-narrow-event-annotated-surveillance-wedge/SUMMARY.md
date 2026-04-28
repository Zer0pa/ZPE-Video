# Phase 09.3 — Narrow Event-Annotated Surveillance Wedge

**Phase:** 09.3
**Date:** 2026-03-22
**Dataset:** VIRAT sparse facility events
**Authority source:** `docs/inputs/review-packs/2026-03-22_science_engineering_pack_phase09_3_local/03_PHASE_09_3_NARROW_SURVEILLANCE.md`
  and `06_REPO_RUNTIME_AND_ARTIFACT_MAP.md`
  (accessed via `origin/reorientation/2026-04-17`)

## Why This Phase Existed

The lane had already bounded scalar control-plane routing (09-09), richer
temporal routing (09.1), and primitive-layered routing (09.2). The honest
next move was to test whether narrowing the surface could expose a real wedge.

## Surface Definition

Selected cohort — four sparsest available facility-event clips on the
repo-owned VIRAT candidate surface:

| Clip | Facility-event coverage |
|---|---:|
| `VIRAT_S_010204_04_000646_000754` | ~3.11% (approx.) |
| `VIRAT_S_010200_00_000060_000218` | (sparse) |
| `VIRAT_S_010203_06_000620_000760` | (sparse) |
| `VIRAT_S_010204_01_000072_000225` | ~5.95% (approx.) |

Facility-event coverage ranged from approximately 3.11% to 5.95%, keeping
the evaluator narrow rather than saturating it with always-on event time.

## Results

Per-clip delta separation ratio under full-frame packet delta:

| Clip | Delta separation ratio | Direction |
|---|---:|---|
| `VIRAT_S_010204_04` | 1.25x | positive |
| `VIRAT_S_010200_00` | 1.08x | positive |
| `VIRAT_S_010203_06` | 0.75x | negative |
| `VIRAT_S_010204_01` | 0.93x | negative |

Two clips show positive separation; two do not.

## What Fell Out

Clip heterogeneity is the key 09.3 discovery. Narrowing to sparse facility
events was the right thought; the current full-frame delta rule still does
not become a selective surveillance wedge on this surface. The mixed per-clip
result means no single rule generalizes.

## Verdict

Descriptive label: `bounded_signal_only`
Canonical enum: `INCONCLUSIVE`
