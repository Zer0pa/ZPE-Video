# Phase 09.3.2 — Verdict

**Phase:** 09.3.2 — Portal-Local State Machine
**Date:** 2026-03-23
**Authority source:** `docs/inputs/status-notes/2026-03-23_phase09_3_2_retire_surface/01_STATUS.md`
  (accessed via `origin/reorientation/2026-04-17`)

## Verdict Line

**Descriptive label:** `retire_surface`
**Canonical enum:** `SUSPENDED_BY_OWNER`

## Brief

The best defended full-surface state machine improves the 09.3.1 point from
34.38% to 37.50% non-event suppression at the same 96.30% recall floor.
This is a real lift. It still fails because:

1. Sovereign gate (50%) is still missed by 12.5 percentage points.
2. One clip still fails the defended recall floor: 83.33% on
   `VIRAT_S_010200_00_000060_000218`.
3. Three of four LOOCV holdouts fail (83.33%, 66.67%, 66.67% recall).
4. Exiting-only split reaches 0.00% suppression.

The root cause diagnosed by dense diagnostics is event heterogeneity
(events 16 and 37 are flat or inverted), not absence of signal. More
threshold or state-machine tuning on this exact surface will not resolve it.

The owner decision is to retire the sparse VIRAT surveillance lane as a
promotable wedge. `SUSPENDED_BY_OWNER` reflects an evidence-grounded
deliberate retirement, not a test failure.
