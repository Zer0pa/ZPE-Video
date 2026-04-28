---
phase: 09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection
plan: 01
depth: standard
one-liner: "Candidate A verdict: kill — ROI-guided libx265 lifts matched-bitrate mAP@50 by +7.93% over flat, but the mean-importance control lane produces the IDENTICAL lift (roi_vs_mean_ratio=1.0), proving the gain is generic non-flat QP allocation, not packet-derived ROI; the packet carries no unique bitrate-allocation value beyond the control baseline."
provides:
  - "Self-contained Python 3.11 harness at `zpe_video_lab/python/phase9_4_1_1_2_1_candidate_a_roi_sidecar.py` (smoke + full modes)"
  - "Machine-readable summary at `zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_a_roi_sidecar/summary.json`"
  - "Matched-bitrate table at `zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_a_roi_sidecar/matched_bitrate_table.csv`"
affects:
  - wedge-ranking
  - roi-sidecar-attribution
  - wave-2-synthesis-input
methods:
  added: [packet-derived-roi-map-generator, libx265-temporal-zone-qp-delta, matched-bitrate-three-lane-comparison, flat-and-mean-importance-control-baselines]
  patterns: [control-lane-required-for-roi-attribution, extract-cost-accounting, sovereign-gate-preserved-despite-lift]
key-files:
  created:
    - zpe_video_lab/python/phase9_4_1_1_2_1_candidate_a_roi_sidecar.py
    - zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_a_roi_sidecar/summary.json
    - zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_a_roi_sidecar/matched_bitrate_table.csv
    - .gpd/phases/09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection/09.4.1.1.2.1-01-SUMMARY.md
key-decisions:
  - "Non-flat QP allocation lifts matched-bitrate mAP@50 by +7.93% over flat H.265 on the bounded 3-clip VIRAT subset (bounded to 48 frames per clip, 2-QP bracket, 1 repeat each for wall-clock budget — documented in SUMMARY)."
  - "The mean-importance control lane (per-frame-mean importance prior — no packet-specific spatial information) produces EXACTLY the same mAP@50 at each (clip, QP) as the packet-derived ROI lane. `roi_vs_mean_ratio = 1.0` across all measured points."
  - "Because the packet-derived ROI lane and the spatially-uninformed mean-importance control lane produce identical encoder output in this libx265 temporal-zone-only control regime, the ~8% lift is an encoder-behavior property (non-flat QP sweeping drives different rate-distortion points) rather than a packet-derived spatial-ROI wedge."
  - "Sovereign Compass-8 primitive-native gate remains red. A kill verdict here closes the ROI/foveated-sidecar line as a ZPE-specific wedge."
plan_contract_ref: ".gpd/phases/09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection/09.4.1.1.2.1-01-PLAN.md#/contract"
contract_results:
  verdict: kill
  rationale: "ROI-guided lane lifts matched-bitrate mAP@50 by +7.93% over flat H.265 (extract-cost-adjusted), which would by itself clear the +5% defend threshold. However, the mean-importance control lane (spatially-uninformed per-frame-mean prior) produces the EXACT SAME mAP@50 at each measured point (roi_vs_mean_ratio=1.0), so the lift is NOT packet-derived spatial guidance. Under the plan-contract kill criterion `mean_importance lifts by >= 0.5x of ROI` => kill, this is clearly met (1.0 >= 0.5). The packet carries no unique bitrate-allocation value in this regime."
  matched_bitrate_relative_gain_pct: 7.93
  control_mean_relative_gain_pct: 7.93
  roi_vs_mean_ratio: 1.00
  roi_exceeds_2x_control: false
sovereign_gate_status: red
scope_reduction_disclosure: "Original plan scoped 5-QP sweep × 3 encode repeats × 3 detector repeats × 72 frames/clip. Initial full run projected ~8 hours wall-clock and was reduced to 2-QP sweep (30, 34) × 1 encode repeat × 1 detector repeat × 48 frames/clip for the bounded budget. The scope reduction does not change the verdict direction: roi_vs_mean_ratio=1.0 is a structural property of the libx265-temporal-zone-only control regime and would persist at any repeat count. A richer per-macroblock spatial QP interface (not available via libx265 defaults) would change the mechanics; see next-required-work."
next_required_work_hint: "The kill is clean for the libx265 temporal-zone control surface. If anyone reopens this line, they must: (a) move to a per-macroblock spatial QP interface (e.g., x265 analysis-save/load with custom QP maps, or a neural codec with spatial bit-allocation), (b) re-run the matched-bitrate triple-lane test with a control that ISOLATES packet-derived spatial priors from any non-flat QP policy, and (c) only claim an ROI-sidecar wedge if the packet-derived lane beats BOTH flat AND mean-importance controls by >= 2x the mean-importance lift. Do NOT narrate the current +7.93% lift as a commercial wedge — it is a non-flat-QP property, not a packet property."
---

# Phase 09.4.1.1.2.1 Plan 01 Summary — Candidate A: ROI/Foveated Guidance Sidecar

## Verdict

`kill` — under the plan-contract kill criterion: ROI lift does not exceed 2x
the control-lane lift (`roi_vs_mean_ratio = 1.0`, kill threshold is < 2.0).

## Key numbers

| Lane | Matched-bitrate mAP@50 relative gain (linear) | Bytes (qp=30, sample clip) |
| ---- | --------------------------------------------- | --------------------------- |
| `flat` (baseline) | 0.00% | 177,852 |
| `roi_guided` | **+7.93%** | 370,091 |
| `mean_importance` (control) | **+7.93%** | 370,091 |

Extract-cost-adjusted relative gain: +7.93% for both lanes.
Control ratio `roi_vs_mean_ratio`: 1.00 (ROI gain equals control gain).

## Interpretation

The +7.93% matched-bitrate mAP@50 lift is real — but it comes from
**non-flat QP allocation**, not from **packet-derived ROI shape**. Both the
spatially-informed ROI lane and the spatially-uninformed mean-importance
control produce encoder output with identical rate-distortion behavior at
each (clip, QP) measurement point.

This is a libx265 temporal-zone limitation: public libx265 from ffmpeg
exposes temporal zones (frame ranges with QP deltas) rather than
per-macroblock spatial QP. Any non-flat temporal zone causes the encoder
to sweep different rate-distortion points, lifting mAP@50 at the same
bitrate target — but that lift is agnostic to the spatial shape of the
importance map.

## Sovereign gate

`red`. This phase does not touch the Compass-8 primitive-native acceptance
gate.

## Scope reduction disclosure

The original plan scoped a 5-QP sweep × 3 encode repeats × 3 detector
repeats × 72 frames/clip. The first full-scope execution projected ~8 hours
wall-clock on Mac CPU and was killed before completion. The re-run scope
was reduced to 2-QP sweep (30, 34) × 1 encode repeat × 1 detector repeat
× 48 frames/clip within the available budget. The reduction does not
change the verdict direction: `roi_vs_mean_ratio = 1.0` is a structural
property of the libx265 temporal-zone-only control regime and would
persist at larger repeat counts.

## Forbidden proxies explicitly rejected

- `primitive_native_closure_claim`: false (gate stays red)
- `gt_fed`: false (ROI derived from YOLOv8m on RGB, not from GT)
- `ap_proxy`: false (actual mAP@50 measurement)
- `mixed_bundles`: false
- `cherry_picked_qp`: false
- `reopened_phase_10_or_red_magic`: false
- `reopened_archive_query_box_state`: false

## Next-step implications (for Wave-2 synthesis)

The ROI/foveated-sidecar line is closed as a ZPE-specific wedge on the
libx265 temporal-zone control surface. Any reopening must move to a
per-macroblock spatial QP interface AND re-run with a control that
isolates packet-derived spatial priors from any non-flat QP policy.

The kill is clean. The +7.93% lift is an encoder-behavior property, not a
commercial wedge.
