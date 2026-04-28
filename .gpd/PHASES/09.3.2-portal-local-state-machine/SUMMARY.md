# Phase 09.3.2 — Portal-Local State Machine

**Phase:** 09.3.2
**Date:** 2026-03-23
**Dataset:** VIRAT sparse facility events (same cohort as 09.3 and 09.3.1)
**Authority source:** `docs/inputs/status-notes/2026-03-23_phase09_3_2_retire_surface/01_STATUS.md`
  and `02_KEY_TABLES.md` and `00_READ_FIRST.md`
  (accessed via `origin/reorientation/2026-04-17`)

## What Was Tested

Phase 09.3.2 ran a bounded portal-local state-machine family on the same
frozen sparse VIRAT facility-crossing surface used in 09.3.1. The goals:
- Reproduce the 09.3.1 authority surface exactly
- Freeze the sparse VIRAT surface in code (exact clips, events, offsets,
  `portal_pad=16`)
- Execute a bounded aperture-only primitive state-machine family
- Evaluate full-surface, per-clip, LOOCV, and entering/exiting splits

## Results

Strongest defended full-surface result:

| Family | Recall | Suppression |
|---|---:|---:|
| `stroke_plus_point_state_machine` | 96.30% (26/27) | 37.50% (12/32) |
| 09.3.1 reference (pair rule) | 96.30% (26/27) | 34.38% (11/32) |

Sovereign gate: 50.00% — still missed.

Per-clip recall under best defended rule:

| Clip | Recall | Suppression |
|---|---:|---:|
| `VIRAT_S_010200_00_000060_000218` | 83.33% (5/6) | 50.00% (2/4) |
| `VIRAT_S_010203_06_000620_000760` | 100.00% (9/9) | 33.33% (4/12) |
| `VIRAT_S_010204_01_000072_000225` | 100.00% (9/9) | 41.67% (5/12) |
| `VIRAT_S_010204_04_000646_000754` | 100.00% (3/3) | 25.00% (1/4) |

Leave-one-clip-out failures:

| Held-out clip | Recall | Suppression |
|---|---:|---:|
| `VIRAT_S_010200_00_000060_000218` | 83.33% | 50.00% |
| `VIRAT_S_010203_06_000620_000760` | 66.67% | 50.00% |
| `VIRAT_S_010204_01_000072_000225` | 100.00% | 25.00% |
| `VIRAT_S_010204_04_000646_000754` | 66.67% | 25.00% |

Narrowed diagnostic splits:

| Split | Recall | Suppression | Status |
|---|---:|---:|---|
| entering-only | 100.00% (18/18) | 37.50% (9/24) | below split gate, LOOCV still fails |
| exiting-only | 100.00% (9/9) | 0.00% (0/8) | dead as a wedge |

Family ledger:

| Family | Safe candidates | Best safe recall | Best safe suppression |
|---|---:|---:|---:|
| `stroke_plus_point_state_machine` | 4 | 96.30% | 37.50% |
| `stroke_only_state_machine` | 4 | 96.30% | 34.38% |
| `stroke_plus_point_hysteresis_state_machine` | 7 | 96.30% | 34.38% |
| `ablation_without_stroke_delta` | 6 | 100.00% | 12.50% |
| `phase_tightened_state_machine` | 0 | — | — |
| `stroke_plus_count_guard_state_machine` | 0 | — | — |

Diagnostic read: dense portal-local diagnostics say the remaining issue is
event heterogeneity, not absence of signal. Flat or inverted dense events:
16, 37. Separating dense events: 5, 15, 26, 29, 30, 35, 38.

## Decision

Retire the sparse VIRAT surveillance lane as a promotable wedge.
Do not continue with more threshold or state-machine tuning on this exact surface.
The next honest move is a different artifact or consumer class.

## Verdict

Descriptive label: `retire_surface`
Canonical enum: `SUSPENDED_BY_OWNER`
