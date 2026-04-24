# Authority Gates And Numbers

Date: `2026-03-22`

## Governing Gate

Current defended subordinate-wedge gate on `MOT17Det`:

- `>= 50%` detector-invocation suppression
- `>= 95%` retained utility
- measured across both `YOLOv8m` and `RT-DETR-L`

Anything below that remains bounded, regardless of secondary wins.

## Phase `09-09` Temporal Frontier

Verdict: `bounded_signal_only`

Best `>= 95%` retention points:

- `YOLOv8m`: `35.34%` suppression at `96.50%` retention
- `RT-DETR-L`: `33.33%` suppression at `96.96%` retention

Best near-half regime:

- `YOLOv8m`: `49.12%` suppression at `90.05%` retention
- `RT-DETR-L`: `47.44%` suppression at `92.13%` retention

Selected bounded candidate:

- `YOLOv8m`
- policy `roi_anchor_hysteresis_h12`
- threshold `0.11`
- `28.31%` suppression at `99.21%` retention

## Phase `09.1` Seedance-Informed Subchannel Factorization

Run-of-record verdict: `flat_lane_still_dominant`

Aggregate:

- clip count: `3`
- factorized bundle total: `12,074` bytes
- flat total: `27,495` bytes
- temporal-only total: `6,314` bytes
- mean bundle vs flat ratio: `0.6866x`
- mean bundle vs temporal-only ratio: `1.7571x`
- mean entity reuse ratio: `0.7042`
- factorized refresh help seen: `true`
- dynamic clip present: `true`
- hard-cut clip present: `true`
- audio clip present: `false`

Interpretation:

- the bundle beats the flat lane
- the bundle still loses to the simpler temporal-only split
- the persistence carrier has not earned its complexity

## Phase `09.2` Primitive-Layered Control Plane

Verdict: `bounded_signal_only`

Best `>= 95%` retention points:

- `YOLOv8m`: policy `primitive_layer_roi_bridge_h12`, threshold `0.20`, `39.93%` suppression at `95.72%` retention
- `RT-DETR-L`: policy `primitive_layer_roi_bridge_h12`, threshold `0.20`, `39.12%` suppression at `96.11%` retention

Important negative result:

- no layered policy reached any `>= 45%` suppression regime on the measured ladder

Selected bounded candidate:

- `YOLOv8m`
- policy `primitive_reset_guard_h8`
- threshold `0.14`
- `27.64%` suppression at `99.09%` retention
- invocation-efficiency gain proxy `1.3695x`

## Direct Comparison: `09-09` vs `09.2`

Important note before comparing:

- there is a cross-phase inconsistency between the `09-09` narrative summary and the `09.2` direct comparison note about the exact prior safe-side anchor
- treat `09.2` as proving only a bounded safe-side lift, not a clean regime change

Aggressive side:

- `09-09` still owns the near-half territory
- `09.2` loses that aggressive-side option entirely

Conclusion:

`09.2` is not a promotion over `09-09`. It is a bounded reshaping of the frontier with no gate closure.
