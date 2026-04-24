---
phase: 09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection
plan: 03
depth: standard
one-liner: "Candidate C verdict: defend with joint_precision_cv=1.0, joint_recall_cv=1.0 on the Phase 09.4.1.1.2 noisy proxy; trajectory features alone achieve 1.0/1.0 under both LogReg and LightGBM under 5-fold stratified CV, lifting precision from the naive-operator baseline 0.138 to 1.0 — the state-layer (not the serialization) is the lever."
provides:
  - "Self-contained Python 3.11 harness at `zpe_video_lab/python/phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment.py` (smoke + full modes)"
  - "Machine-readable summary with verdict at `zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment/summary.json`"
  - "5-fold CV per-classifier per-ablation table at `zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment/cv_table.csv`"
  - "Ablation attribution table at `zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment/ablation_table.csv`"
  - "Feature cache (DINOv2-small embeddings + trajectory vectors) at `zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment/feature_cache.npz`"
affects:
  - wedge-ranking
  - state-layer-vs-serialization-attribution
  - wave-2-synthesis-input
methods:
  added: [frozen-dinov2-small-appearance-feature, trajectory-feature-vector, stratified-5fold-cv, logreg-and-lightgbm-classifier-agreement, shuffled-and-saturated-control-ablation]
  patterns: [state-layer-isolation, classifier-family-agreement, small-sample-nan-fold-reporting, sovereign-gate-preserved-despite-defend]
key-files:
  created:
    - zpe_video_lab/python/phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment.py
    - zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment/summary.json
    - zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment/cv_table.csv
    - zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment/ablation_table.csv
    - zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment/feature_cache.npz
    - .gpd/phases/09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection/09.4.1.1.2.1-03-SUMMARY.md
key-decisions:
  - "Trajectory features alone (track_length, total_displacement, mean_speed, std_speed, portal_dwell_fraction, direction_consistency) are sufficient to separate real facility-crossings from ghost tracks under 5-fold CV with classifier agreement (LogReg and LightGBM) on the 09.4.1.1.2 noisy proxy."
  - "Appearance features (frozen DINOv2-small patch embeddings rendered onto deterministic box crops) are NOT required: appearance-only fails LogReg recall threshold (0.75) but reaches 1.0/1.0 on LightGBM, indicating appearance carries some but not all information on this surface."
  - "The joint (appearance + trajectory) classifier matches trajectory-only at 1.0/1.0 — appearance adds no marginal value on this noisy proxy."
  - "Sovereign Compass-8 primitive-native gate remains red. A defend verdict here proves ONLY that the state layer is the lever; it does NOT prove the ZPE packet format is uniquely the right state carrier. Any format can carry trajectory features."
  - "Small-sample caveat: N=4 positives and N=25 negatives in the full proxy, so `nan_fold_count=1` on the joint configuration (one fold had degenerate test distribution). Precision=recall=1.0 should be read as 'the lift is large on the available sample', not 'statistical significance at the level of a standard benchmark'. This is disclosed explicitly and does NOT change the verdict under the plan contract (classifier agreement + meets_threshold + shuffled-control near base rate)."
plan_contract_ref: ".gpd/phases/09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection/09.4.1.1.2.1-03-PLAN.md#/contract"
contract_results:
  verdict: defend
  rationale: "Joint classifier reaches precision=recall=1.0 under stratified 5-fold CV on the 29-sample noisy proxy (4 real facility-crossing events + 25 ghost-track negatives from Phase 09.4.1.1.2). Trajectory features alone also reach 1.0/1.0 under both LogReg and LightGBM, establishing classifier-family agreement. Shuffled-features control falls to near base-rate as required. The state layer is confirmed as the precision lever that representation-level changes alone cannot move (see Phase 09.4.1.1.2 where all five serializations of the same box stream produced 0.138 precision under the naive operator). The sovereign Compass-8 primitive-native acceptance gate remains red and is not touched by this result."
  state_layer_not_serialization_disclosure: "A defend verdict here proves the STATE LAYER is the lever (appearance + trajectory features discriminate ghost tracks from real events) but does NOT prove ZPE format is uniquely the right carrier. Any sparse-metadata format (raw struct+zlib, Parquet, JSON+gzip) can carry the same per-track features and would produce the same classifier performance. This outcome opens a STATE-LAYER continuation direction, not a ZPE-specific wedge."
sovereign_gate_status: red
next_required_work_hint: "Candidate C opens a state-layer continuation direction. Any follow-up must (a) test on a larger and messier surface (e.g., live VIRAT with real appearance from pixels, not rendered synthetic appearance) before trusting the 1.0/1.0 number, (b) treat ZPE format as one of several valid carriers, and (c) preserve sovereign gate discipline. Do NOT upgrade this verdict to 'primitive-native closure'."
---

# Phase 09.4.1.1.2.1 Plan 03 Summary — Candidate C: Primitive-Semantic Enrichment

## Verdict

`defend` — under the plan-contract kill/defend criteria: joint classifier
reaches precision=recall=1.0 under stratified 5-fold CV with classifier-family
agreement (LogReg and LightGBM) on the Phase 09.4.1.1.2 noisy proxy, and
shuffled-features control falls to near base rate.

## Key numbers

Cross-validation mean (5-fold stratified, 3-seed robustness):

| Classifier | Ablation | Precision | Recall | Meets threshold |
| ---------- | -------- | --------- | ------ | --------------- |
| LogReg | appearance_only | 1.00 | 0.75 | False |
| LogReg | trajectory_only | 1.00 | 1.00 | True |
| LogReg | combined | 1.00 | 1.00 | True |
| LightGBM | appearance_only | 1.00 | 1.00 | True |
| LightGBM | trajectory_only | 1.00 | 1.00 | True |
| LightGBM | combined | 1.00 | 1.00 | True |

Baseline: naive portal-crossing operator on the same box stream achieves
precision=0.138, recall=1.0 (from Phase 09.4.1.1.2).

Lift: precision 0.138 → 1.0 with recall preserved at 1.0.

## Attribution

Trajectory features alone are sufficient on this proxy. Appearance features
(frozen DINOv2-small on deterministic synthetic box renders) add no marginal
information on this surface.

This is expected: the proxy's ghost tracks are distinguished from real tracks
by their short, erratic, non-portal-traversing trajectories, which the
trajectory features (track_length, total_displacement, mean_speed, std_speed,
portal_dwell_fraction, direction_consistency) encode directly.

## Disclosures

- `nan_fold_count=1` on combined and trajectory-only for both classifiers.
  One CV fold had a degenerate test distribution (0 positives in test); the
  reported mean is over the remaining 4 folds. This is a small-sample
  artifact, not a signal defect.
- Sample size: 4 positives, 25 negatives across 3 clips. The 1.0/1.0 result
  should be interpreted as "the separation is clean on the available
  noisy-proxy sample" — not as a statistically-powered benchmark.
- Appearance features are built from deterministic RGB renders of the
  synthetic proxy (gray background + filled rectangles colored by box
  dimensions). This is an honest approximation noted in the BENCHMARK-REPORT;
  it is NOT real-world appearance.

## Sovereign gate status

`red`. This phase does not touch the Compass-8 primitive-native acceptance
gate. The defend verdict proves the state layer is the lever, not that ZPE
is the preferred carrier. Any format can carry these features.

## Next-step implications (for Wave-2 synthesis)

The state-layer continuation direction is opened. Follow-up should:
- test on a larger, messier surface (live VIRAT with real-pixel appearance)
- treat ZPE as one of several valid carriers of enriched state
- preserve sovereign gate discipline
- run broader ablations (per-feature importance, adversarial noise injection)
  before trusting this lift as a commercial wedge
