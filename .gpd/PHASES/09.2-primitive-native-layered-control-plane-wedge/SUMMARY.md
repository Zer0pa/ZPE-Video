# Phase 09.2 — Primitive-Native Layered Control Plane Wedge

**Phase:** 09.2
**Date:** 2026-03-22
**Dataset:** MOT17Det
**Detector families tested:** YOLOv8m, RT-DETR-L
**Authority source:** `docs/inputs/review-packs/2026-03-22_science_engineering_pack/02_AUTHORITY_GATES_AND_NUMBERS.md`
  (accessed via `origin/reorientation/2026-04-17`)

## What Was Tested

Phase 09.2 tested whether a primitive-native layered control plane could
improve on the Phase 09-09 temporal frontier. The hypothesis was that
layering primitive-level routing on top of the scalar routing would lift
suppression beyond what 09-09 achieved.

The governing gate remains: >= 50% suppression at >= 95% retention.

## Results

Best >= 95% retention points:

| Detector | Policy | Threshold | Suppression | Retention |
|---|---|---|---:|---:|
| YOLOv8m | `primitive_layer_roi_bridge_h12` | 0.20 | 39.93% | 95.72% |
| RT-DETR-L | `primitive_layer_roi_bridge_h12` | 0.20 | 39.12% | 96.11% |

Selected bounded candidate:
- Detector: YOLOv8m
- Policy: `primitive_reset_guard_h8`
- Threshold: `0.14`
- Suppression: `27.64%` at `99.09%` retention
- Invocation-efficiency gain proxy: `1.3695x`

Key negative result: no layered policy reached any >= 45% suppression regime
on the measured ladder.

## Cross-Phase Comparison (09-09 vs 09.2)

Per the authority source:
- There is a cross-phase inconsistency between the 09-09 narrative summary
  and the 09.2 direct comparison note about the exact prior safe-side anchor.
  Treat 09.2 as proving only a bounded safe-side lift, not a clean regime change.
- Aggressive side: 09-09 still owns the near-half territory; 09.2 loses
  that aggressive-side option entirely.
- Conclusion: 09.2 is not a promotion over 09-09. It is a bounded reshaping
  of the frontier with no gate closure.

## What Fell Out

Primitive-layered routing reshapes the frontier slightly (best safe-side
up from ~28% to ~40% suppression) but cannot close the gate and loses
the near-half option that 09-09 preserved.

## Verdict

Descriptive label: `bounded_signal_only`
Canonical enum: `INCONCLUSIVE`
