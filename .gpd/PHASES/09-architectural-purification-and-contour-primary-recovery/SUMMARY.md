# Phase 09-09 — Architectural Purification and Contour Primary Recovery

**Phase:** 09-09
**Date:** 2026-03-22
**Dataset:** MOT17Det
**Detector families tested:** YOLOv8m, RT-DETR-L
**Source:** `docs/inputs/review-packs/2026-03-22_science_engineering_pack/02_AUTHORITY_GATES_AND_NUMBERS.md`
  (accessed via `origin/reorientation/2026-04-17`)

## What Was Tested

Phase 09-09 probed the temporal frontier of detector-invocation suppression
using a scalar control-plane routing approach on the MOT17Det benchmark.

The governing gate for this phase family:
- `>= 50%` detector-invocation suppression
- `>= 95%` retained utility
- measured across both YOLOv8m and RT-DETR-L

## Results

Best >= 95% retention points:

| Detector | Suppression | Retention |
|---|---:|---:|
| YOLOv8m | 35.34% | 96.50% |
| RT-DETR-L | 33.33% | 96.96% |

Best near-half regime (below 95% retention threshold):

| Detector | Suppression | Retention |
|---|---:|---:|
| YOLOv8m | 49.12% | 90.05% |
| RT-DETR-L | 47.44% | 92.13% |

Selected bounded candidate:
- Detector: YOLOv8m
- Policy: `roi_anchor_hysteresis_h12`
- Threshold: `0.11`
- Suppression: `28.31%` at `99.21%` retention

## What Fell Out

The temporal frontier reached near-half suppression only at unacceptable
retention loss (90%). Within the governed retention floor (>= 95%), the
best suppression was 35.34%, well below the 50% sovereign gate.

The phase established that scalar temporal routing has real signal but
cannot close the sovereign gate on this surface.

## Verdict

Descriptive label: `bounded_signal_only`
Canonical enum: `INCONCLUSIVE`
