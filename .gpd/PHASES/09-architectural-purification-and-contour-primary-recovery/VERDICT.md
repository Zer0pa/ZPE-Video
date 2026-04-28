# Phase 09-09 — Verdict

**Phase:** 09-09 — Architectural Purification and Contour Primary Recovery
**Date:** 2026-03-22
**Authority source:** `docs/inputs/review-packs/2026-03-22_science_engineering_pack/02_AUTHORITY_GATES_AND_NUMBERS.md`
  (accessed via `origin/reorientation/2026-04-17`)

## Verdict Line

**Descriptive label:** `bounded_signal_only`
**Canonical enum:** `INCONCLUSIVE`

## Brief

The temporal frontier of detector-invocation suppression on MOT17Det reached
35.34% suppression (YOLOv8m) at 96.50% retention — real signal, below the
50% sovereign gate. The near-half regime (49.12% suppression) is only
achievable at 90.05% retention, which fails the >= 95% retention floor.

This phase does not close the sovereign gate. The bounded candidate
(`roi_anchor_hysteresis_h12`, YOLOv8m, threshold 0.11) is carried forward
as a reference point for subsequent phases.
