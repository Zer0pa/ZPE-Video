# Phase 09.3.2 Status

Verdict: `retire_surface`

## What Was Done

- reproduced the `09.3.1` authority surface exactly
- froze the sparse VIRAT surface in code: exact clips, exact events, exact offsets, and `portal_pad=16`
- ran dense portal-local diagnostics on the same events
- executed a bounded aperture-only primitive state-machine family
- evaluated full-surface, per-clip, leave-one-clip-out, and entering/exiting diagnostic splits

## Strongest Defended Full-Surface Result

- family: `stroke_plus_point_state_machine`
- config:
  - `stroke_delta >= 0.028662420382165606`
  - `point_delta <= 0.1233644859813084`
- aggregate recall: `26/27 = 96.30%`
- aggregate suppression: `12/32 = 37.50%`

That is a real lift over `09.3.1`, which reached `11/32 = 34.38%` suppression at the same recall floor.

## Why It Still Fails

- sovereign gate is still missed: `37.50% < 50.00%`
- one clip still fails the defended recall floor:
  - `VIRAT_S_010200_00_000060_000218 = 5/6 = 83.33%`
- leave-one-clip-out still fails on three holdouts:
  - `5/6 = 83.33%`
  - `6/9 = 66.67%`
  - `2/3 = 66.67%`
- entering-only reaches only `37.50%` suppression and still fails LOOCV
- exiting-only reaches `0.00%` suppression

## Diagnostic Read

Dense portal-local diagnostics say the remaining issue is event heterogeneity, not absence of signal.

Flat or inverted dense events:

- event `16`
- event `37`

Separating dense events:

- `5`, `15`, `26`, `29`, `30`, `35`, `38`

## Decision

Retire the sparse VIRAT surveillance lane as a promotable wedge.

Do not continue with more threshold or state-machine tuning on this exact surface.
