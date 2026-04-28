# Phase 09.3.1 — Portal-Anchored Primitive Event Consumer on Sparse Facility Crossing

**Phase:** 09.3.1
**Date:** 2026-03-22
**Dataset:** VIRAT sparse facility events (same cohort as 09.3)
**Authority source:** `docs/inputs/review-packs/2026-03-22_science_engineering_pack_phase09_3_1_local/03_PHASE_09_3_1_PORTAL_LOCAL_CONSUMER.md`
  and `00_READ_FIRST.md`
  (accessed via `origin/reorientation/2026-04-17`)

## Why This Phase Existed

Phase 09.3 proved the right owned narrow surface was sparse facility-event
surveillance, but full-frame packet delta was too blunt. Phase 09.3.1 asked:
if the surface stays fixed and the aperture tightens around the event-linked
actor portal, does the packet become materially more selective?

## Surface Definition

Same 4-clip cohort as 09.3:
- `VIRAT_S_010204_04_000646_000754`
- `VIRAT_S_010200_00_000060_000218`
- `VIRAT_S_010203_06_000620_000760`
- `VIRAT_S_010204_01_000072_000225`

Event scope:
- 9 facility events
- 59 portal-local samples total (27 positive, 32 negative)

Portal rule: Use VIRAT events, objects, and mapping. Link each facility
event to its actor track. Take the union of that actor's boxes across the
event. Pad that union locally at runtime. The score comes from
primitive-local state inside the crop (not the full frame).

## Results

Best single-feature rule:
- Rule: `stroke_delta >= 0.006493506493506494`
- Recall: `96.30%`
- Suppression: `31.25%`

Best aggregate rule:
- Rule: `stroke_delta >= 0.006493506493506494 AND point_delta <= 0.1233644859813084`
- Recall: `96.30%`
- Suppression: `34.38%`

Per-clip breakdown under the global rule:

| Clip | Recall | Suppression |
|---|---:|---:|
| `VIRAT_S_010204_04_000646_000754` | 100% | 50.00% |
| `VIRAT_S_010200_00_000060_000218` | 100% | 25.00% |
| `VIRAT_S_010203_06_000620_000760` | 100% | 41.67% |
| `VIRAT_S_010204_01_000072_000225` | 88.89% | 25.00% |

Holdout check: Leave-one-clip-out behavior stays unstable. Multiple
holdouts collapse to 66.67% recall under the best training rule. One
holdout retains recall but only at weak suppression.

## What Fell Out

Portal-local aperture is materially better than full-frame: 34.38%
suppression vs 09.3's mixed result. However:
- One clip still fails the defended recall floor (88.89% < 95%)
- LOOCV is unstable across multiple holdouts

The phase proves the remaining problem is not "no local signal exists." The
problem is that the current portal-local consumer does not yet survive clip
changes well enough to count as a wedge.

## Verdict

Descriptive label: `bounded_signal_only`
Canonical enum: `INCONCLUSIVE`
