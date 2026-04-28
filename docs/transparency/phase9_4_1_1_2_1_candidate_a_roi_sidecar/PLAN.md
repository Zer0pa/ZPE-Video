---
phase: 09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - zpe_video_lab/python/phase9_4_1_1_2_1_candidate_a_roi_sidecar.py
  - zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_a_roi_sidecar/summary.json
  - zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_a_roi_sidecar/matched_bitrate_table.csv
  - .gpd/phases/09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection/09.4.1.1.2.1-01-BENCHMARK-REPORT.md
  - .gpd/phases/09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection/09.4.1.1.2.1-01-SUMMARY.md
interactive: false

conventions:
  units:
    total_bytes: "bytes (integer)"
    bitrate: "bits per pixel (bpp, float)"
    detector_utility: "mAP@50 (dimensionless, [0,1])"
    relative_gain: "percent ((candidate - baseline) / baseline * 100)"
    encoder: "libx265 with zones / QP-delta map; AV1/VVC deferred"
    detector: "YOLOv8m on a held-out slice of the chosen surface"
  baseline_rule: "flat-QP libx265 at matched total bitrate is the primary comparator; per-frame-mean importance is a control baseline"
  public_repo_rule: "public `zpe-video` shell remains frozen; lab code and GPD artifacts only"
  sovereign_gate_rule: "no primitive-native closure claim may be derived regardless of verdict"

dimensional_check:
  total_bytes: "[bytes]"
  bpp: "[bits] / [pixel] = dimensionless fraction"
  mAP_50: "dimensionless in [0,1]"
  relative_gain_pct: "dimensionless percent"
  encoder_time_ms: "[ms]"
  extract_cost_ms_per_frame: "[ms/frame]"

approximations:
  - name: "matched-bitrate comparison window"
    parameter: "total encoded bytes within +/- 2% of the candidate lane's bytes"
    validity: "only compare mAP@50 between lanes when the matched window holds"
    breaks_when: "any candidate forces bitrate outside +/- 2% of baseline; in that case either bracket the baseline with two flat-QP points or widen-and-note"
    check: "log candidate bytes + chosen flat-QP baseline bytes and their ratio in summary.json"
  - name: "Gaussian ROI importance map"
    parameter: "sigma scales with sqrt(box_area)"
    validity: "smooth per-frame importance surface over [0, 1]"
    breaks_when: "empty packet (all-zero map -> fall back to unmodified encoding) or full-frame coverage (all-one map -> fall back to unmodified encoding)"
    check: "explicitly test empty-packet and saturated-map limiting cases in the harness"

contract:
  schema_version: 1
  scope:
    question: "On a bounded VCM surface, does a deterministic packet-derived ROI importance map used as a bitrate-allocation prior for incumbent H.265 produce a matched-bitrate detector utility lift of at least +5% mAP@50 (defend), or does it fail to reach +2% with extract-cost accounted (kill)?"
    in_scope:
      - "CompressAI-Vision COCO subset or frozen VIRAT ROI surface (bounded held-out slice)"
      - "libx265 encoder with zones / per-MB QP-delta prior"
      - "YOLOv8m detector on decoded output, mAP@50 as utility metric"
      - "flat-QP baseline and per-frame-mean importance control lane"
      - "extract-cost accounting for packet-derived ROI map"
    out_of_scope:
      - "AV1/VVC/learned comparators (deferred to follow-up if A defends)"
      - "detector retraining or adaptation"
      - "primitive-native Compass-8 closure claims"
      - "external `zpe-video` public GitHub remote touches"
      - "Phase 10 or Red Magic validation reopening"
    unresolved_questions:
      - "If A defends on YOLOv8m + H.265, does the wedge survive RT-DETR-L or AV1? (follow-up phase)"
      - "Is extract cost amortizable across many downstream detector runs in a real deployment?"
  claims:
    - id: claim-candidate-a-verdict
      statement: "On a bounded CompressAI-Vision COCO subset or frozen VIRAT ROI surface, either (defend) the packet-derived ROI-guided H.265 lane improves held-out matched-bitrate mAP@50 by >= 5% relative vs flat-QP H.265 with extract cost accounted, or (kill) it fails to reach +2% relative on the same surface; in all outcomes a control baseline (per-frame-mean importance and flat bitrate allocation) is reported so the signal is not confused with any ROI-map-in-general effect."
      deliverables:
        - deliv-candidate-a-harness
        - deliv-candidate-a-summary
        - deliv-candidate-a-matched-table
        - deliv-candidate-a-report
      acceptance_tests:
        - test-candidate-a-kill-or-defend
        - test-candidate-a-control-baseline
        - test-candidate-a-extract-cost
        - test-candidate-a-limiting-cases
      references:
        - ref-prior-phase-summary
        - ref-prior-phase-proposal
        - ref-research
        - ref-project-contract
        - ref-recovery-prd
    - id: claim-candidate-a-sovereign-gate-preserved
      statement: "No outcome of this plan claims primitive-native Compass-8 closure; the sovereign gate remains red regardless of verdict."
      deliverables:
        - deliv-candidate-a-report
        - deliv-candidate-a-summary
      acceptance_tests:
        - test-candidate-a-scope-boundary
      references:
        - ref-project-contract
        - ref-recovery-prd
  deliverables:
    - id: deliv-candidate-a-harness
      kind: code
      path: "zpe_video_lab/python/phase9_4_1_1_2_1_candidate_a_roi_sidecar.py"
      description: "Self-contained throwaway-venv-friendly harness that (1) derives a per-frame Gaussian ROI importance map from tracked boxes, (2) drives libx265 with a QP-delta zones prior, (3) runs YOLOv8m on the decoded video, (4) brackets flat-QP libx265 at matched total bytes, (5) logs control baselines (flat bitrate, per-frame-mean importance), (6) accounts extract cost"
      must_contain:
        - "build_roi_map"
        - "map_to_libx265_zones"
        - "encode_lane"
        - "eval_map50"
    - id: deliv-candidate-a-summary
      kind: data
      path: "zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_a_roi_sidecar/summary.json"
      description: "Machine-readable summary with per-lane total bytes, bpp, mAP@50 (median of N=3 runs), relative gain vs flat-QP H.265 bracket, extract cost in ms/frame, kill/defend verdict block"
      must_contain:
        - "verdict"
        - "matched_bitrate"
        - "limiting_cases"
        - "control_comparison"
    - id: deliv-candidate-a-matched-table
      kind: table
      path: "zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_a_roi_sidecar/matched_bitrate_table.csv"
      description: "Matched-bitrate table: lane, total_bytes, bpp, mAP@50 median, mAP@50 stderr, relative_gain_pct, extract_cost_ms_per_frame"
      must_contain:
        - "lane"
        - "mAP50_median"
        - "relative_gain_linear_pct"
    - id: deliv-candidate-a-report
      kind: report
      path: ".gpd/phases/09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection/09.4.1.1.2.1-01-BENCHMARK-REPORT.md"
      description: "Human-readable benchmark report with the matched-bitrate comparison, control-baseline disclosure, extract-cost disclosure, limiting-case checks, and explicit kill/defend verdict"
      must_contain:
        - "Verdict"
        - "Sovereign gate boundary"
        - "Control baseline"
        - "Extract cost"
  acceptance_tests:
    - id: test-candidate-a-kill-or-defend
      subject: claim-candidate-a-verdict
      kind: benchmark
      procedure: "Inspect summary.json `verdict` field; verify relative_gain_linear_pct AND relative_gain_log_pct meet the same threshold; verify extract-cost adjustment is applied in extract_adjusted_relative_gain_pct; coerce inconclusive -> kill."
      pass_condition: "summary.json records either `verdict: defend` with relative_gain_pct >= 5.0 on the held-out slice AND extract-cost accounted, OR `verdict: kill` with relative_gain_pct < 2.0 on the held-out slice AND extract-cost accounted."
      evidence_required:
        - deliv-candidate-a-summary
        - deliv-candidate-a-matched-table
    - id: test-candidate-a-control-baseline
      subject: claim-candidate-a-verdict
      kind: cross_method
      procedure: "Verify summary.json includes both a flat-QP control lane and a per-frame-mean importance control lane at matched QPs; compute roi_vs_mean_ratio; any defend verdict requires roi_vs_mean_ratio >= 2.0."
      pass_condition: "Both control lanes are present AND control_comparison.roi_exceeds_2x_control is true for any defend verdict."
      evidence_required:
        - deliv-candidate-a-summary
    - id: test-candidate-a-extract-cost
      subject: claim-candidate-a-verdict
      kind: benchmark
      procedure: "Verify summary.json records extract_cost_ms_per_frame with median and p90; verify extract_adjusted_relative_gain_pct is computed by subtracting a comparable compute budget from the flat-QP baseline or crediting the ROI lane a compute penalty."
      pass_condition: "extract_cost_ms_per_frame and extract_adjusted_relative_gain_pct are both present in summary.json."
      evidence_required:
        - deliv-candidate-a-summary
    - id: test-candidate-a-limiting-cases
      subject: claim-candidate-a-verdict
      kind: limiting_case
      procedure: "Run the empty-packet and saturated-packet clips through the ROI-guided encoder; record bpp_delta_pct and mAP50_delta versus flat-QP at the same QP."
      pass_condition: "Both limiting cases produce |bpp_delta_pct| < 1.0 vs flat-QP, confirming fallback to unmodified encoding."
      evidence_required:
        - deliv-candidate-a-summary
    - id: test-candidate-a-scope-boundary
      subject: claim-candidate-a-sovereign-gate-preserved
      kind: existence
      procedure: "Grep the BENCHMARK-REPORT and SUMMARY for an explicit sovereign-gate boundary paragraph; verify no text ties a positive verdict to primitive-native closure."
      pass_condition: "Both documents include an explicit sovereign_gate_status: red note AND do NOT associate any positive verdict with primitive-native closure."
      evidence_required:
        - deliv-candidate-a-report
  references:
    - id: ref-prior-phase-summary
      kind: prior_artifact
      locator: ".gpd/phases/09.4.1.1.2-fair-baseline-archive-query-falsification/09.4.1.1.2-01-SUMMARY.md"
      role: "must_consider"
      why_it_matters: "prior-phase verdict that falsified the archive-query wedge and reopened ROI guidance as a candidate"
      required_actions: ["read", "cite"]
    - id: ref-prior-phase-proposal
      kind: prior_artifact
      locator: ".gpd/phases/09.4.1.1.2-fair-baseline-archive-query-falsification/NEXT-EXPERIMENT-PROPOSAL.md"
      role: "definition"
      why_it_matters: "source of Candidate A framing, kill/defend criteria, and extract-cost concern"
      required_actions: ["read", "use"]
    - id: ref-research
      kind: prior_artifact
      locator: ".gpd/phases/09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection/09.4.1.1.2.1-RESEARCH.md"
      role: "method"
      why_it_matters: "consolidated research for Candidate A framework, mathematical map, and validity regime"
      required_actions: ["read", "use"]
    - id: ref-project-contract
      kind: spec
      locator: ".gpd/PROJECT.md"
      role: "definition"
      why_it_matters: "sovereign Compass-8 primitive-native gate definition and forbidden-proxy rules; this is the governing anchor the phase MUST NOT violate"
      must_surface: true
      applies_to:
        - claim-candidate-a-verdict
        - claim-candidate-a-sovereign-gate-preserved
      carry_forward_to:
        - claim-candidate-a-verdict
        - claim-candidate-a-sovereign-gate-preserved
      required_actions: ["read", "use", "cite"]
    - id: ref-recovery-prd
      kind: spec
      locator: "EXECUTION_PRD_AUTHORITY_RECOVERY_AND_HANDOVER_RECONCILIATION_2026-03-13.md"
      role: "definition"
      why_it_matters: "recovery-lane authority discipline, detector-honest evidence rules, forbidden proxies"
      required_actions: ["read", "use"]
    - id: ref-phase7-detector-patterns
      kind: prior_artifact
      locator: "zpe_video_lab/python/phase9_4_1_1_1_live_event_state_query.py"
      role: "method"
      why_it_matters: "prior live-VIRAT harness pattern for detector-honest evaluation"
      required_actions: ["read", "use"]
    - id: ref-license
      kind: spec
      locator: "LICENSE.txt"
      role: "definition"
      why_it_matters: "Compass-8 substrate definition; boundary for what MUST NOT be claimed"
      required_actions: ["read", "cite"]
  forbidden_proxies:
    - id: forbidden-rebrand
      subject: claim-candidate-a-sovereign-gate-preserved
      proxy: "narrating a matched-bitrate lift as primitive-native closure"
      reason: "this is a bounded ROI-sidecar experiment on incumbent H.265, not a substrate win; the sovereign Compass-8 primitive-native gate remains red regardless of verdict"
    - id: forbidden-gt-fed
      subject: claim-candidate-a-verdict
      proxy: "using ground-truth boxes as the ROI source"
      reason: "the ROI map MUST be derived from the same tracked-box packet used downstream, with extract cost accounted; GT-fed ROI inflates apparent utility without representing the deployed pipeline"
    - id: forbidden-ap-proxy
      subject: claim-candidate-a-verdict
      proxy: "substituting `ap_proxy` or any non-detector-honest utility surrogate for mAP@50"
      reason: "mAP@50 on YOLOv8m against the declared annotation source is the only utility metric; `ap_proxy` was flagged as a forbidden proxy by the recovery PRD"
    - id: forbidden-mixed-bundle
      subject: claim-candidate-a-verdict
      proxy: "combining the ROI-guidance lane with detector retraining, augmentor changes, or any second intervention in the same comparison"
      reason: "mixed bundles make attribution impossible; each lane MUST isolate one intervention"
    - id: forbidden-cherry-pick
      subject: claim-candidate-a-verdict
      proxy: "reporting only clips where the ROI lane wins"
      reason: "the matched-bitrate table MUST be reported on the full held-out slice with per-clip breakdown; cherry-picking inflates apparent signal"
  uncertainty_markers:
    weakest_anchors:
      - "libx265 `zones` behavior under default `aq-mode` may interact non-trivially with the QP-delta prior; the exact interaction is tool-version-dependent"
      - "extract cost is worker-local wall-clock; not yet a deployment metric"
    unvalidated_assumptions:
      - "the Gaussian importance map with sigma ~ sqrt(area) is a reasonable ROI shape; alternative kernels are not tested in this plan"
      - "N=3 encoding repeats are sufficient for 10% jitter on libx265 CPU"
    competing_explanations:
      - "any mAP@50 lift may come from `any ROI map`, not from the packet-derived ROI specifically; the mean-importance control lane is the check"
      - "extract cost may make the wedge uneconomical in production even if matched-bitrate mAP@50 passes"
    disconfirming_observations:
      - "if the mean-importance control lane matches roi_guided within 2x, the packet provides no specific value"
      - "if the ROI lane passes at some QPs but fails at others, the wedge is fragile and should be documented as such"
      - "if extract_cost_ms_per_frame exceeds ~5-10 ms on typical hardware, the operating regime where the wedge is net-positive is narrow"
---

# Phase 09.4.1.1.2.1 Plan 01 — Candidate A: ROI / Foveated Guidance Sidecar

## Objective

Test whether a deterministic packet-derived ROI importance map, used as a
bitrate-allocation prior for an incumbent H.265 encoder, produces a material
matched-bitrate detector-utility lift on a bounded VCM-style surface — with
extract cost accounted and with control baselines that isolate the ROI-map
contribution from any generic "spatially non-uniform bit allocation" effect.

Produce a kill-or-defend verdict. Do not claim primitive-native closure.

## Scope and surface

- **Primary surface:** a defended, held-out slice of a bounded VCM surface —
  either the CompressAI-Vision COCO subset referenced in VCM literature, or
  a frozen per-frame ROI surface derived from the live VIRAT facility-crossing
  cohort carried forward from `09.4.1.1.1`. The choice is recorded in
  summary.json and MUST be bounded to ~1 engineering day of runtime.
- **Detector:** YOLOv8m (the Phase 3–7 primary detector family). No
  adaptation, no retraining. Detector weights and inference flags recorded
  in summary.json.
- **Incumbent comparator:** libx265 flat-QP encoding at matched total
  bytes. If no single flat-QP point lands within +/- 2% of the candidate
  bytes, bracket with two neighbors and report both linear and log
  interpolations of mAP@50.
- **Control baselines (mandatory):**
  - flat-QP libx265 (no importance prior)
  - per-frame-mean importance map (same byte budget, importance = mean of
    boxes area / frame area; isolates "any ROI-map" from "packet-derived ROI")

## Method

Build `zpe_video_lab/python/phase9_4_1_1_2_1_candidate_a_roi_sidecar.py` as
a self-contained script runnable in a throwaway venv (pattern from
`/tmp/zpe_fair_baseline_venv` used in `09.4.1.1.2`). Dependencies: ffmpeg
with libx265, numpy, opencv-python, ultralytics (YOLOv8m weights), and
the existing packet parser already in the repo.

The script:

1. Loads the held-out slice.
2. Runs YOLOv8m per-frame on the original RGB source to establish the
   ground-truth-free mAP@50 ceiling for this detector (record; do not use
   as a wedge claim).
3. Extracts the per-frame tracked-box packet via the existing packet encoder
   (the same path used by Phase 09.4.1.1.2).
4. Builds per-frame Gaussian importance maps `M_t(i, j) = sum_b
   g(i - cx(b), j - cy(b); sigma(area(b)))` normalized to [0, 1].
5. Converts the normalized map to libx265 `zones` or QP-delta per-MB prior.
   If libx265 `zones` cannot accept per-MB resolution, fall back to
   rectangular-region zones that cover top-K importance tiles, recorded in
   summary.json.
6. Encodes three lanes at a sweep of target bitrates matched to a flat-QP
   curve:
   - **flat-QP** (incumbent, varies QP in `{28, 30, 32, 34, 36}` to build
     a rate-utility curve)
   - **packet-ROI-guided** (same QP sweep, plus ROI prior)
   - **mean-importance control** (same QP sweep, plus per-frame-mean prior)
7. Decodes each encoded file and runs YOLOv8m inference.
8. Computes mAP@50 per lane, median of N=3 runs, per-clip and aggregate.
9. Computes extract cost (packet extraction wall-clock ms/frame) and
   charges it to the packet-ROI-guided lane in the verdict calculation.
10. Runs limiting-case clips: (a) empty packet (no boxes) and (b) saturated
    packet (boxes covering full frame). Both MUST produce |bpp_delta| < 1%
    vs flat-QP.
11. Writes `summary.json`, `matched_bitrate_table.csv`, BENCHMARK-REPORT,
    and SUMMARY.

## Kill / Defend (contract)

- **Defend (C2):** matched-bitrate held-out mAP@50 lift vs flat-QP H.265
  bracket is `>= +5.0%` relative, extract cost accounted, on the full
  held-out slice with per-clip breakdown.
- **Kill (C1):** matched-bitrate held-out mAP@50 lift vs flat-QP H.265
  bracket is `< +2.0%` relative, extract cost accounted.
- **Inconclusive is coerced to kill.** A "maybe" verdict is not an
  outcome; any claim of signal MUST cross the defend threshold.

## Error budget

- **Encoding jitter:** libx265 wall-clock has O(10%) per-run jitter on
  Mac CPU; median of N=3 full encodes; report stderr.
- **Detector jitter:** YOLOv8m CPU inference has O(5%) per-image jitter
  on confidence floats; run N=3 full eval passes and report median mAP@50
  and stderr in the matched_bitrate_table.csv.
- **Bracketing noise:** if no flat-QP point is within +/- 2% of candidate
  bytes, interpolate linearly AND logarithmically between the two
  neighbors and report both; verdict MUST pass under both.
- **Extract cost noise:** measure extract cost over N=10 frames, report
  median and p90.

## Limiting cases

- **Empty packet:** a clip with zero tracked boxes. The ROI map is
  all-zero, so the encoder MUST produce bytes and mAP@50 statistically
  indistinguishable from flat-QP at matched QP. Record `bpp_delta` and
  `mAP_50_delta` in summary.json.
- **Saturated packet:** a clip where boxes cover the entire frame. The
  ROI map is flat, so the encoder MUST produce bytes and mAP@50
  statistically indistinguishable from flat-QP at matched QP. Record
  `bpp_delta` and `mAP_50_delta`.
- **Single small box:** a clip with one small box in a single frame. The
  ROI map is nearly a delta; encoder MUST concentrate bits on the ROI;
  record `relative_gain_pct` (this is a best-case sanity check, not a
  verdict gate).

## Consistency checks (cross-method)

- **Control vs ROI:** matched-bitrate mAP@50 lift of the packet-ROI-guided
  lane MUST exceed the mean-importance control lane by at least 2x;
  otherwise the signal is "any ROI map" rather than "packet-derived ROI",
  and the verdict MUST be `kill` even if the raw vs-flat lift is `>= 5%`.
- **Flat baseline sanity:** mAP@50 of flat-QP at QP 32 MUST fall inside
  the sweep curve (i.e., the curve is monotonic in QP); otherwise the
  encoder pipeline is misconfigured and the run is discarded.

## Sovereign gate discipline

This plan does NOT touch the Compass-8 primitive-native acceptance gate.
The sovereign gate remains red. No closure claim may be derived from
this verdict, defend or kill. The report MUST include an explicit
boundary note to this effect.

## Forbidden proxies (contract)

- No primitive-native closure claim.
- No GT-fed ROI maps — maps MUST come from the same tracked-box packet.
- No `ap_proxy` or other detector-utility surrogates.
- No mixed bundles (detector retraining, extra augmentors).
- No cherry-picked per-clip subsets in the headline verdict.
- No touching the external `zpe-video` public GitHub remote.
- No reopening Phase 10 or Red Magic validation.
- No reopening archive-query on box-state substrate.

<tasks>

<task type="auto">
  <name>Task 1: Stand up Candidate A harness and surface selection</name>
  <files>zpe_video_lab/python/phase9_4_1_1_2_1_candidate_a_roi_sidecar.py</files>
  <action>
    Create the self-contained Candidate A harness. Write preamble that:

    1. Lists Python dependencies explicitly (numpy, opencv-python,
       ultralytics, the existing repo packet parser).
    2. Emits a DEPENDENCY_CHECK print if any are missing and exits 2.
    3. Declares the surface choice explicitly: CompressAI-Vision COCO
       subset (preferred if downloadable on Mac within ~1 day) OR a
       frozen per-frame ROI surface built from the live VIRAT facility-
       crossing cohort already on the pod at
       `/workspace/zpe_video_phase03` (fallback).
    4. Includes a `--surface` CLI flag; records the chosen surface in
       summary.json.

    Implement these functions:

    - `load_surface(name) -> iterable of (clip_id, frames_rgb, annotations)`
    - `extract_packet(frames) -> list of per-frame tracked-box lists`,
      using the existing repo packet encoder with wall-clock timing.
    - `build_roi_map(boxes, frame_shape, sigma_fn) -> ndarray[H,W]`,
      Gaussian importance map normalized to [0, 1].
    - `map_to_libx265_zones(roi_map) -> list of (x, y, w, h, qp_delta)`
      producing libx265 `zones` or `qpfile` entries.
    - `encode_lane(frames, mode, qp, zones=None) -> (path, bytes, wall_ms)`
      where `mode in {flat, roi_guided, mean_importance}`.
    - `eval_map50(encoded_path, annotations) -> (mAP_50, per_clip_dict)`
      using YOLOv8m on decoded frames.
    - `run_all_lanes(clip) -> lane_results_dict` computing all three
      lanes at QPs {28, 30, 32, 34, 36}.

    Do NOT run the experiment yet; the harness is scaffolding only.
  </action>
  <verify>
    1. The harness runs `--help` and prints a usage block.
    2. A `--smoke` mode runs a single 10-frame dummy clip through
       `build_roi_map` and `map_to_libx265_zones` and reports
       determinism (same RNG / same input -> byte-identical bytes).
    3. Dimensional check in smoke output: `total_bytes` integer;
       `bpp = total_bytes * 8 / (width * height * num_frames)` float;
       `mAP_50` in [0.0, 1.0].
    4. Empty-packet limiting case: forcing `boxes=[]` produces a map
       of all zeros and zones-list of length zero.
  </verify>
  <done>Harness scaffolding exists, smoke mode passes determinism and dimensional checks, limiting cases for empty packet return flat map</done>
</task>

<task type="auto">
  <name>Task 2: Run three-lane matched-bitrate sweep with control baselines</name>
  <files>zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_a_roi_sidecar/summary.json, zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_a_roi_sidecar/matched_bitrate_table.csv</files>
  <action>
    Execute the full three-lane sweep on the chosen surface (held-out
    slice only).

    For each clip in the held-out slice, and for each QP in
    {28, 30, 32, 34, 36}, run:

    - lane=flat (libx265 -crf QP)
    - lane=roi_guided (libx265 -crf QP with packet-derived zones)
    - lane=mean_importance (libx265 -crf QP with per-frame-mean zones)

    Repeat each lane N=3 times; record median and stderr for
    (total_bytes, encode_wall_ms, mAP_50). Record extract_cost_ms per
    frame once per clip (median of N=10 frames).

    Build the matched-bitrate table:

    - For each (lane=roi_guided, QP) point, find the flat-QP bracket
      whose total_bytes bracket the candidate's bytes within +/- 2%.
    - If a single point is within +/- 2%, use it directly.
    - Otherwise interpolate mAP@50 linearly AND logarithmically between
      the two neighbors; record both.
    - Compute relative_gain_pct for roi_guided vs flat and for
      mean_importance vs flat at matched bytes.

    Apply the extract-cost adjustment: if the packet extract cost
    adds X ms/frame, EITHER charge (X ms/frame) of flat-lane compute
    to the ROI lane in the verdict calculation OR credit the flat lane
    a compute-neutral penalty equal to the extraction wall clock.

    Run the limiting-case clips (empty-packet, saturated-packet,
    single-small-box) and record bpp_delta + mAP_50_delta.

    Emit summary.json with structure:

    ```
    {
      "surface": "<CompressAI-COCO or VIRAT-ROI-subset>",
      "detector": "YOLOv8m",
      "repeats": 3,
      "lanes": {
        "flat": { "qp_sweep": [...], "bytes": [...], "mAP50_median": [...], "mAP50_stderr": [...] },
        "roi_guided": { ... },
        "mean_importance": { ... }
      },
      "matched_bitrate": [
        { "target_qp": 30, "candidate_bytes": N, "flat_bracket": [a, b],
          "flat_interp_linear": x, "flat_interp_log": y,
          "roi_mAP50": z, "relative_gain_linear_pct": ..., "relative_gain_log_pct": ... },
        ...
      ],
      "extract_cost_ms_per_frame": { "median": ..., "p90": ... },
      "extract_adjusted_relative_gain_pct": ...,
      "limiting_cases": {
        "empty_packet": { "bpp_delta_pct": ..., "mAP50_delta": ... },
        "saturated_packet": { "bpp_delta_pct": ..., "mAP50_delta": ... },
        "single_small_box": { "relative_gain_pct": ... }
      },
      "control_comparison": {
        "roi_vs_mean_ratio": ...,
        "roi_exceeds_2x_control": true/false
      },
      "verdict": "defend" | "kill",
      "verdict_justification": "..."
    }
    ```

    Also emit matched_bitrate_table.csv with columns:
    `clip_id,lane,qp,total_bytes,bpp,mAP50_median,mAP50_stderr,relative_gain_linear_pct,relative_gain_log_pct,extract_cost_ms_per_frame`.
  </action>
  <verify>
    1. summary.json validates as JSON.
    2. For each QP, `flat.bytes[QP]` monotonically decreases with QP
       (sanity of encoder sweep).
    3. `roi_guided.bytes` and `mean_importance.bytes` at a given QP
       are within +/- 2% of `flat.bytes` at the same QP (zones
       should not shift the global budget materially).
    4. Limiting-case empty_packet shows `|bpp_delta_pct| < 1.0`.
    5. Limiting-case saturated_packet shows `|bpp_delta_pct| < 1.0`.
    6. Verdict field is exactly one of `{"defend", "kill"}`.
    7. Control-baseline comparison field is present.
  </verify>
  <done>summary.json and matched_bitrate_table.csv exist, all sanity checks pass, verdict is computed from the data and not free-form</done>
</task>

<task type="auto">
  <name>Task 3: Write benchmark report and summary, preserve sovereign gate</name>
  <files>.gpd/phases/09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection/09.4.1.1.2.1-01-BENCHMARK-REPORT.md, .gpd/phases/09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection/09.4.1.1.2.1-01-SUMMARY.md</files>
  <action>
    Write the human-readable benchmark report with these sections:

    1. **Surface and detector** (which slice, how many clips/frames,
       detector identity, held-out rule).
    2. **Matched-bitrate comparison** (include the matched_bitrate
       table inline; show linear + log interpolation).
    3. **Control baseline disclosure** (mean_importance vs roi_guided
       ratio; if ratio < 2x, note that the signal is generic-ROI not
       packet-specific).
    4. **Extract cost disclosure** (median and p90 ms/frame; the
       extract-adjusted relative gain).
    5. **Limiting-case evidence** (empty / saturated / single-box).
    6. **Verdict** (defend or kill, with the specific numbers that
       triggered the verdict).
    7. **Sovereign gate boundary** (explicit statement that this
       result does NOT close the Compass-8 primitive-native gate,
       regardless of verdict).
    8. **Forbidden-proxy audit** (confirm no GT-fed boxes, no
       `ap_proxy`, no mixed bundles, no cherry-picking, no external-
       repo touches).
    9. **Next move conditional on verdict**:
       - defend -> hand off to Plan 04 (synthesis) and recommend a
         live/pod-scale follow-up (not a primitive-native closure).
       - kill -> hand off to Plan 04 (synthesis) for ranked-ladder
         update and retire Candidate A.

    Write the SUMMARY.md with the frontmatter schema used by
    prior phases (status, kill_or_defend, sovereign_gate_status,
    next_required_work, forbidden_proxies_rejected).

    Append the uncertainty markers: encoding_time_jitter,
    detector_inference_jitter, ffmpeg_zones_quirks, extract_cost_honesty.
  </action>
  <verify>
    1. BENCHMARK-REPORT has all nine sections.
    2. SUMMARY frontmatter includes exactly one of `kill_or_defend: kill`
       or `kill_or_defend: defend`.
    3. SUMMARY frontmatter includes `sovereign_gate_status: red` and
       an explicit sovereign-gate boundary note.
    4. Grep: neither file contains the phrase "primitive-native closure"
       associated with any positive claim.
    5. Grep: neither file contains "ap_proxy" or "ground-truth-fed" as
       a claimed evidence source.
  </verify>
  <done>BENCHMARK-REPORT and SUMMARY exist, verdict is explicit, sovereign gate is preserved, forbidden proxies are audited clean</done>
</task>

</tasks>

<verification>
- Dimensional check: bytes integer; bpp dimensionless; mAP@50 in [0,1];
  relative gain dimensionless percent; wall-clock in ms.
- Limiting-case check: empty-packet and saturated-packet lanes produce
  |bpp_delta_pct| < 1.0 vs flat-QP.
- Error budget: N=3 repeats with stderr reported; median-of-N used for
  all comparisons; matched-bitrate bracket within +/- 2%.
- Consistency check: control-baseline lane (mean_importance) reported
  alongside roi_guided; signal MUST exceed control by 2x for defend.
- Anchor discipline: comparator is flat-QP libx265 on the exact same
  held-out slice; detector is YOLOv8m; surface is CompressAI-Vision
  COCO subset OR frozen VIRAT ROI surface.
- Forbidden-proxy audit: no GT-fed ROI, no ap_proxy, no mixed bundles,
  no cherry-picking, no primitive-native closure claim.
</verification>

<success_criteria>
Plan 01 closes when summary.json, matched_bitrate_table.csv,
BENCHMARK-REPORT, and SUMMARY all exist; verdict is exactly
`{defend|kill}` on the held-out slice with extract cost accounted;
control baseline is reported; limiting cases pass; sovereign gate
is preserved with an explicit boundary note.
</success_criteria>

<output>
After completion, create `.gpd/phases/09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection/09.4.1.1.2.1-01-SUMMARY.md`
</output>
</content>
</invoke>