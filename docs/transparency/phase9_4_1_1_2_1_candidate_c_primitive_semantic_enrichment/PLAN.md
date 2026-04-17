---
phase: 09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection
plan: 03
type: execute
wave: 1
depends_on: []
files_modified:
  - zpe_video_lab/python/phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment.py
  - zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment/summary.json
  - zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment/cv_table.csv
  - zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment/ablation_table.csv
  - .gpd/phases/09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection/09.4.1.1.2.1-03-BENCHMARK-REPORT.md
  - .gpd/phases/09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection/09.4.1.1.2.1-03-SUMMARY.md
interactive: false

conventions:
  units:
    precision: "dimensionless in [0,1]"
    recall: "dimensionless in [0,1]"
    cv_fold_count: "integer"
    feature_vector_dim: "integer"
    appearance_embedding_dim: "integer = 128 (SigLIP / DINOv2 projected to 128-D)"
    training_time_ms: "[ms]"
    extract_cost_ms_per_track: "[ms/track]"
  baseline_rule: "naive-operator precision on the same noisy proxy from Phase 09.4.1.1.2 is the exact baseline (precision = 0.138, recall = 1.0)"
  backbone: "frozen SigLIP or frozen DINOv2 (no fine-tuning), record the exact model id"
  classifier: "logistic regression AND gradient-boosted trees (sklearn / lightgbm); report both"
  cv: "stratified K-fold with K=5 on the same noisy proxy; no data leakage from train to test"
  public_repo_rule: "public `zpe-video` shell remains frozen; lab code and GPD artifacts only"
  sovereign_gate_rule: "no primitive-native closure claim may be derived regardless of verdict"

dimensional_check:
  precision: "dimensionless in [0,1]"
  recall: "dimensionless in [0,1]"
  feature_vector: "[integer dim] per track; record exact dim"
  appearance_mean: "128-D float vector"
  appearance_std: "128-D float vector"
  trajectory_features: "{displacement_px, length_frames, mean_speed_px_per_frame, portal_dwell_fraction}"
  cv_fold_precision: "dimensionless in [0,1] per fold"

approximations:
  - name: "frozen backbone appearance features"
    parameter: "no fine-tuning; SigLIP or DINOv2 weights frozen"
    validity: "appearance embedding is discriminative for real vs ghost tracks if the backbone was trained on broadly aligned image data"
    breaks_when: "the noisy proxy's ghost tracks visually resemble real tracks so strongly that frozen-backbone features cannot separate them"
    check: "report both appearance-only and trajectory-only ablations to show which lever (if any) carries the signal"
  - name: "cross-validation on a bounded proxy"
    parameter: "K=5 stratified folds on the Phase 09.4.1.1.2 noisy proxy"
    validity: "the proxy is a fair stand-in for the live VIRAT false-positive cloud IF the ghost-generator has not been over-fit to the proxy"
    breaks_when: "proxy is too small (< 29 predicted / 4 matched / 4 GT from 09.4.1.1.2) to support stable CV"
    check: "record per-fold precision and recall, report mean +/- stderr; if any fold collapses, re-examine proxy generation"

contract:
  schema_version: 1
  scope:
    question: "On the same noisy proxy from Phase 09.4.1.1.2, can per-track appearance + trajectory features attached via a frozen backbone lift binary-classifier precision from 0.138 to >= 0.5 while preserving recall >= 0.9 under stratified cross-validation — and can ablations identify which of (appearance-only, trajectory-only, combined) is responsible for the lift?"
    in_scope:
      - "the exact noisy proxy from Phase 09.4.1.1.2 (29 predicted / 4 matched / 4 GT, regenerated at the same seed)"
      - "frozen SigLIP-so400m-patch14-384 OR DINOv2-base backbone (no fine-tuning)"
      - "logistic regression (sklearn) AND lightgbm classifiers"
      - "stratified 5-fold cross-validation at the track level with fixed seed"
      - "three ablations per classifier: appearance_only, trajectory_only, combined"
      - "shuffled-feature and saturated-feature controls; 3-seed robustness pass on the winner"
    out_of_scope:
      - "backbone fine-tuning or training new embeddings"
      - "moving beyond the 09.4.1.1.2 noisy proxy to live VIRAT (deferred to follow-up if C defends)"
      - "claiming ZPE-specific wedge from any result (state-layer IS representation-agnostic)"
      - "primitive-native Compass-8 closure claims"
      - "external `zpe-video` public GitHub remote touches"
      - "Phase 10 or Red Magic validation reopening"
    unresolved_questions:
      - "If C defends on the proxy, does the precision lift survive on live VIRAT where ghost-track generation is not synthetic?"
      - "What is the ceiling of appearance+trajectory features before richer primitive state is required?"
  claims:
    - id: claim-candidate-c-verdict
      statement: "On the Phase 09.4.1.1.2 noisy-proxy cohort, either (defend) a binary classifier on per-track appearance + trajectory features reaches precision >= 0.5 AND recall >= 0.9 under stratified 5-fold cross-validation AND at least one ablation (appearance-only or trajectory-only) demonstrates which feature family carries the lift, or (kill) no such classifier clears the joint precision/recall threshold."
      deliverables:
        - deliv-candidate-c-harness
        - deliv-candidate-c-summary
        - deliv-candidate-c-cv-table
        - deliv-candidate-c-ablation-table
        - deliv-candidate-c-report
      acceptance_tests:
        - test-candidate-c-kill-or-defend
        - test-candidate-c-ablation-required
        - test-candidate-c-cv-discipline
        - test-candidate-c-limiting-cases
        - test-candidate-c-extract-cost
      references:
        - ref-prior-phase-summary
        - ref-prior-phase-proposal
        - ref-research
        - ref-noisy-proxy-harness
        - ref-project-contract
        - ref-recovery-prd
    - id: claim-candidate-c-sovereign-gate-preserved
      statement: "No outcome of this plan claims primitive-native Compass-8 closure; the sovereign gate remains red regardless of verdict."
      deliverables:
        - deliv-candidate-c-report
        - deliv-candidate-c-summary
      acceptance_tests:
        - test-candidate-c-scope-boundary
      references:
        - ref-project-contract
        - ref-recovery-prd
    - id: claim-candidate-c-not-zpe-wedge-alone
      statement: "Even a positive verdict does NOT establish a ZPE-specific wedge, because appearance embeddings and trajectory features can be attached to any sparse-metadata cache (raw struct, parquet, json) equally well. A positive verdict establishes only that the STATE LAYER (not the serialization) is the lever; the report MUST include this disclosure."
      deliverables:
        - deliv-candidate-c-report
        - deliv-candidate-c-summary
      acceptance_tests:
        - test-candidate-c-scope-boundary
      references:
        - ref-prior-phase-summary
        - ref-recovery-prd
  deliverables:
    - id: deliv-candidate-c-harness
      kind: code
      path: "zpe_video_lab/python/phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment.py"
      description: "Self-contained harness that (1) loads the Phase 09.4.1.1.2 noisy proxy, (2) computes per-track 128-D appearance embeddings via a frozen SigLIP or DINOv2 backbone, (3) computes trajectory features, (4) trains logistic regression AND gradient-boosted classifiers under stratified 5-fold CV, (5) runs three ablations (appearance-only, trajectory-only, combined), (6) reports per-fold precision/recall/mean+stderr, (7) accounts for backbone extract cost"
      must_contain:
        - "regenerate_noisy_proxy"
        - "appearance_features"
        - "trajectory_features"
        - "cv_fit_eval"
        - "run_ablation"
    - id: deliv-candidate-c-summary
      kind: data
      path: "zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment/summary.json"
      description: "Machine-readable CV results per classifier per ablation, per-fold precision/recall, mean + stderr, extract cost, kill/defend verdict, forbidden-proxy audit"
      must_contain:
        - "verdict"
        - "results"
        - "robustness_seeds"
        - "controls"
        - "attribution"
    - id: deliv-candidate-c-cv-table
      kind: table
      path: "zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment/cv_table.csv"
      description: "Per-fold CV table: fold_idx, classifier, ablation, precision, recall, f1, n_train, n_test, n_positive"
      must_contain:
        - "fold_idx"
        - "classifier"
        - "ablation"
        - "precision"
        - "recall"
    - id: deliv-candidate-c-ablation-table
      kind: table
      path: "zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment/ablation_table.csv"
      description: "Summary ablation table: classifier, ablation (appearance_only, trajectory_only, combined), precision_mean, precision_stderr, recall_mean, recall_stderr, meets_threshold"
      must_contain:
        - "classifier"
        - "ablation"
        - "precision_mean"
        - "meets_threshold"
    - id: deliv-candidate-c-report
      kind: report
      path: ".gpd/phases/09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection/09.4.1.1.2.1-03-BENCHMARK-REPORT.md"
      description: "Human-readable report with CV tables, ablation analysis, limiting cases, extract-cost disclosure, explicit verdict, and the state-layer-not-serialization disclosure"
      must_contain:
        - "State-layer-not-serialization disclosure"
        - "Verdict"
        - "Sovereign gate boundary"
        - "Ablation"
  acceptance_tests:
    - id: test-candidate-c-kill-or-defend
      subject: claim-candidate-c-verdict
      kind: benchmark
      procedure: "Inspect summary.json `verdict` field and `results` blocks; verify the defend decision rule (precision_mean >= 0.5 AND recall_mean >= 0.9 across 5 folds AND classifier_agreement.agree AND attribution.lift_is_attributable AND NOT high_variance_flag AND shuffled_features_precision < 0.25)."
      pass_condition: "summary.json records either `verdict: defend` under the full decision rule OR `verdict: kill` otherwise, with the exact numbers that triggered the verdict."
      evidence_required:
        - deliv-candidate-c-summary
        - deliv-candidate-c-ablation-table
    - id: test-candidate-c-ablation-required
      subject: claim-candidate-c-verdict
      kind: cross_method
      procedure: "Verify summary.json `results` contains three ablations per classifier (appearance_only, trajectory_only, combined); verify attribution.lift_is_attributable is true when defend and based on a single-family ablation lift >= 0.1 over baseline 0.138."
      pass_condition: "Three ablations per classifier are present AND a defend verdict requires attribution.lift_is_attributable == true."
      evidence_required:
        - deliv-candidate-c-summary
        - deliv-candidate-c-ablation-table
    - id: test-candidate-c-cv-discipline
      subject: claim-candidate-c-verdict
      kind: reproducibility
      procedure: "Verify summary.json records stratified 5-fold CV at the track level with fixed seed; verify cv_table.csv has exactly 30 rows (2 classifiers x 3 ablations x 5 folds); verify no train/test track overlap within any fold."
      pass_condition: "summary.json.cv.split_level == 'track' AND cv_table.csv has 30 rows AND fold splits are track-disjoint."
      evidence_required:
        - deliv-candidate-c-summary
        - deliv-candidate-c-cv-table
    - id: test-candidate-c-limiting-cases
      subject: claim-candidate-c-verdict
      kind: limiting_case
      procedure: "Run the shuffled-features control (chance baseline) and saturated-features control (all tracks identical); verify shuffled_features_precision is within [0.05, 0.25] (near base rate) and saturated_features_precision equals 0.138 within 1e-3."
      pass_condition: "summary.json.controls.shuffled_features_precision < 0.25 AND controls.saturated_features_precision ~= 0.138 (within 1e-3)."
      evidence_required:
        - deliv-candidate-c-summary
    - id: test-candidate-c-extract-cost
      subject: claim-candidate-c-verdict
      kind: benchmark
      procedure: "Verify summary.json records extract_cost_ms_per_track.median and .p90; verify the report includes a feasibility note on whether the wedge is economical given that extract cost."
      pass_condition: "summary.json.extract_cost_ms_per_track has median and p90 AND the report discusses the extract-cost economics."
      evidence_required:
        - deliv-candidate-c-summary
        - deliv-candidate-c-report
    - id: test-candidate-c-scope-boundary
      subject: claim-candidate-c-sovereign-gate-preserved
      kind: existence
      procedure: "Grep BENCHMARK-REPORT and SUMMARY for the explicit state-layer-not-serialization disclosure AND the sovereign-gate boundary paragraph; verify no text ties a positive verdict to primitive-native closure or to a ZPE-specific wedge."
      pass_condition: "Both documents include (a) an explicit sovereign_gate_status: red note, (b) a state-layer-not-serialization disclosure, AND do NOT associate any positive verdict with primitive-native closure or a ZPE-specific wedge."
      evidence_required:
        - deliv-candidate-c-report
  references:
    - id: ref-prior-phase-summary
      kind: prior_artifact
      locator: ".gpd/phases/09.4.1.1.2-fair-baseline-archive-query-falsification/09.4.1.1.2-01-SUMMARY.md"
      role: "benchmark"
      why_it_matters: "prior-phase result that all five representations produce identical 0.138 precision under the naive operator on the noisy proxy; this is the exact baseline this plan attempts to beat"
      required_actions: ["read", "use", "compare"]
    - id: ref-prior-phase-proposal
      kind: prior_artifact
      locator: ".gpd/phases/09.4.1.1.2-fair-baseline-archive-query-falsification/NEXT-EXPERIMENT-PROPOSAL.md"
      role: "definition"
      why_it_matters: "source of Candidate C framing, kill/defend criteria, and state-layer hypothesis"
      required_actions: ["read", "use"]
    - id: ref-research
      kind: prior_artifact
      locator: ".gpd/phases/09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection/09.4.1.1.2.1-RESEARCH.md"
      role: "method"
      why_it_matters: "consolidated research for Candidate C framework, mathematical map, and validity regime"
      required_actions: ["read", "use"]
    - id: ref-noisy-proxy-harness
      kind: prior_artifact
      locator: "zpe_video_lab/python/phase9_4_1_1_2_fair_baseline_archive_query.py"
      role: "method"
      why_it_matters: "exact source of the noisy proxy corpus (ghost-track generator, portal definition, operator definitions); this plan MUST regenerate the proxy from this source, not a new seed"
      required_actions: ["read", "use"]
    - id: ref-project-contract
      kind: spec
      locator: ".gpd/PROJECT.md"
      role: "definition"
      why_it_matters: "sovereign Compass-8 primitive-native gate definition and forbidden-proxy rules; this is the governing anchor the phase MUST NOT violate"
      must_surface: true
      applies_to:
        - claim-candidate-c-verdict
        - claim-candidate-c-sovereign-gate-preserved
        - claim-candidate-c-not-zpe-wedge-alone
      carry_forward_to:
        - claim-candidate-c-verdict
        - claim-candidate-c-sovereign-gate-preserved
        - claim-candidate-c-not-zpe-wedge-alone
      required_actions: ["read", "use", "cite"]
    - id: ref-recovery-prd
      kind: spec
      locator: "EXECUTION_PRD_AUTHORITY_RECOVERY_AND_HANDOVER_RECONCILIATION_2026-03-13.md"
      role: "definition"
      why_it_matters: "recovery-lane authority discipline, detector-honest evidence rules, forbidden proxies"
      required_actions: ["read", "use"]
    - id: ref-license
      kind: spec
      locator: "LICENSE.txt"
      role: "definition"
      why_it_matters: "Compass-8 substrate definition; boundary for what MUST NOT be claimed"
      required_actions: ["read", "cite"]
  forbidden_proxies:
    - id: forbidden-rebrand
      subject: claim-candidate-c-not-zpe-wedge-alone
      proxy: "narrating a CV precision lift as primitive-native closure OR as a ZPE-specific wedge"
      reason: "a positive verdict establishes that the STATE LAYER is the lever, which is representation-agnostic; appearance embeddings and trajectory features can be attached to any sparse-metadata cache (raw struct, parquet, json) equally well, so a positive result is NOT a ZPE-specific wedge"
    - id: forbidden-leaky-cv
      subject: claim-candidate-c-verdict
      proxy: "leaking train-to-test by splitting folds at the feature level or reusing a track's features across train and test folds"
      reason: "fold splits MUST be at the track level (or higher); CV leak silently inflates precision and is the classic overfitting source; the shuffled-features control is the explicit check"
    - id: forbidden-overfit-combined-only
      subject: claim-candidate-c-verdict
      proxy: "claiming defend on the combined ablation alone without a single-family ablation (appearance_only or trajectory_only) showing measurable lift"
      reason: "a combined-only lift with dead single-family ablations is a classic overfitting pattern; attribution to appearance OR trajectory is required to claim real signal"
    - id: forbidden-gt-leakage
      subject: claim-candidate-c-verdict
      proxy: "using ground-truth class labels as features"
      reason: "labels are the supervision target, not a feature; label leakage is the strongest form of CV leak"
    - id: forbidden-cherry-pick
      subject: claim-candidate-c-verdict
      proxy: "reporting only the best-fold result"
      reason: "mean + stderr across all 5 folds MUST be reported; cherry-picking inflates apparent signal; small-sample CV requires honest variance reporting"
    - id: forbidden-ap-proxy
      subject: claim-candidate-c-verdict
      proxy: "substituting `ap_proxy` or any soft metric for precision and recall"
      reason: "binary precision/recall on portal-crossing positives is the only gate; `ap_proxy` is a forbidden proxy in the recovery PRD"
  uncertainty_markers:
    weakest_anchors:
      - "the noisy proxy has only 4 GT positives across 29 predictions; 5-fold CV at this sample size has high per-fold variance"
      - "frozen-backbone inference on Mac CPU may take seconds per track; the reported extract cost is hardware-specific"
    unvalidated_assumptions:
      - "the frozen SigLIP or DINOv2 backbone's generic visual features are discriminative for real vs ghost tracks on this proxy"
      - "track-level CV splits with 5 folds are stable enough to support the kill/defend decision on 29 tracks"
    competing_explanations:
      - "a precision lift may come from trajectory features alone (which can be computed without a backbone), collapsing the appearance-embedding extract-cost story"
      - "a positive combined-ablation result with dead single-family ablations is overfitting noise rather than real signal"
      - "shuffled-features precision elevated above base rate would indicate CV leakage, not real signal"
    disconfirming_observations:
      - "if shuffled_features_precision exceeds 0.25, the CV is leaking and the entire run is discarded"
      - "if logreg and lightgbm disagree on the threshold cross, the classifier is not robust enough to claim defend"
      - "if the 3-seed robustness pass spans defend to kill, the high-variance flag forces kill"
      - "if combined precision underperforms the best single-family ablation, the combined model is overfitting and verdict is kill"
---

# Phase 09.4.1.1.2.1 Plan 03 — Candidate C: Primitive-Semantic Enrichment

## Objective

Test whether per-track state enrichment (frozen-backbone appearance
embedding + trajectory features) attached to the same noisy proxy from
Phase 09.4.1.1.2 can lift binary-classifier precision from the naive
baseline (0.138) to `>= 0.5` while preserving `recall >= 0.9` under
stratified 5-fold cross-validation.

This plan explicitly tests the STATE LAYER, not the serialization. A
positive verdict does NOT establish a ZPE-specific wedge — appearance
embeddings and trajectory features can be attached to any sparse-
metadata cache equally well. A positive verdict establishes only that
the state layer is the lever.

Produce a kill-or-defend verdict. Do not claim primitive-native closure.

## Scope and surface

- **Primary surface:** the exact noisy proxy corpus from
  Phase 09.4.1.1.2 (`zpe_video_lab/python/phase9_4_1_1_2_fair_baseline_archive_query.py`
  noisy-proxy mode), with 29 predicted portal-crossings, 4 matched,
  4 GT. Reuse the proxy generator verbatim; do not regenerate with
  a new seed.
- **Features:**
  - **Appearance:** 128-D embedding per track from a frozen backbone
    (SigLIP-so400m-patch14-384 OR DINOv2-base). Record exact model
    id. For each track, extract crops from the track's first, middle,
    and last frame; compute embedding mean and std across those three
    crops.
  - **Trajectory:** `{displacement_px, length_frames,
    mean_speed_px_per_frame, portal_dwell_fraction,
    trajectory_curvature}`.
  - **Combined:** concatenation of appearance + trajectory (~260-D).
- **Classifiers:** logistic regression (sklearn, L2 regularization,
  default C=1.0) AND gradient-boosted trees (lightgbm, default params).
- **Cross-validation:** stratified 5-fold, fixed random seed, split
  at the track level (not frame or feature level).
- **Labels:** binary, "real portal-crossing" vs "ghost track" from
  the existing noisy-proxy generator's ground truth.

## Method

Build `zpe_video_lab/python/phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment.py`
as a self-contained throwaway-venv-friendly script. Mac CPU sufficient
since the proxy is tiny and the backbone runs once per track.

Dependencies: numpy, scikit-learn, lightgbm, torch, transformers
(for SigLIP/DINOv2), opencv-python, the existing proxy generator.

The script:

1. Regenerates the Phase 09.4.1.1.2 noisy proxy deterministically
   (identical seed, identical generator).
2. For each track in the proxy, extracts the first/middle/last frame
   crops from the box locations.
3. Runs the frozen backbone on those crops; records 128-D embeddings
   (mean and std across the three crops). Records extract wall-clock.
4. Computes trajectory features from the box sequence.
5. Labels each track as `is_real_portal_crossing`.
6. Runs stratified 5-fold CV on logistic regression AND lightgbm,
   for three ablations each:
   - `appearance_only` (256-D: 128 mean + 128 std)
   - `trajectory_only` (5-D: displacement, length, speed, dwell,
     curvature)
   - `combined` (261-D)
7. Records per-fold precision, recall, f1, and the confusion matrix.
8. Runs the limiting-case controls: shuffled-features (chance) and
   saturation (all tracks identical features).
9. Runs a three-seed robustness pass on the winning ablation (seeds
   {0, 7, 42}); reports median.
10. Emits summary.json, cv_table.csv, ablation_table.csv,
    BENCHMARK-REPORT, and SUMMARY.

## Kill / Defend (contract)

- **Defend (C2):** precision_mean `>= 0.5` AND recall_mean `>= 0.9`
  across 5 stratified CV folds AND at least one of
  `appearance_only`/`trajectory_only` ablations shows precision
  `>= 0.138 + 0.1` (i.e., at least +0.1 absolute lift vs the naive
  baseline) so the signal is attributable to a specific feature
  family, not only to overfitting the combined feature set.
- **Kill (C1):** no (classifier, ablation) combination clears the
  joint threshold of precision_mean `>= 0.5` AND recall_mean `>= 0.9`.
- **Inconclusive is coerced to kill.**

## Error budget

- **Small-sample CV variance:** with 4 GT positives, per-fold
  precision has high variance; report stderr honestly; a fold where
  precision is undefined (zero predicted positives) MUST be recorded
  as NaN and included in the mean calculation as a missing-fold
  flag, not silently dropped.
- **Seed variance:** run 3 seeds {0, 7, 42} on the winning ablation;
  report median precision_mean and recall_mean. If the three seeds
  span `defend` to `kill`, flag as HIGH_VARIANCE and coerce to kill.
- **Backbone non-determinism:** set `torch.manual_seed(0)` and
  `torch.use_deterministic_algorithms(True)` where possible; if
  residual bit-level drift exists, record the L2 norm of the drift
  per track and report.
- **Extract cost jitter:** measure backbone wall-clock over N=10
  tracks; report median and p90.

## Limiting cases

- **Shuffled-features ablation (chance baseline):** shuffle the
  feature vectors across tracks while keeping labels fixed; report
  precision and recall. MUST be statistically indistinguishable from
  the base rate (4 / 29 ~ 0.138). If the shuffled-features classifier
  shows precision > 0.25, the CV split is leaking and the run is
  discarded.
- **Saturated-features ablation (all identical):** set all tracks to
  the same feature vector; report precision. MUST equal the base
  rate 4/29 ~ 0.138 (classifier is reduced to majority class / base
  rate).
- **Single-track-out:** leave-one-track-out stability check for
  the winning ablation; report how many tracks, when held out, flip
  the per-fold verdict.

## Consistency checks (cross-method)

- **Classifier agreement:** logistic regression and lightgbm MUST
  agree on the verdict (both pass or both fail the 0.5/0.9
  threshold). If one passes and the other does not, record as
  `classifier_disagree` and coerce to kill (not robust enough to
  defend).
- **Ablation sanity:** combined precision MUST be >=
  max(appearance_only, trajectory_only). If combined underperforms
  a single-family ablation, the combined model is overfitting and
  the verdict is kill.
- **Base-rate check:** the noisy proxy's base rate of real portal
  crossings (4 / 29 ~ 0.138) MUST match what the Phase 09.4.1.1.2
  report recorded; if the proxy regenerator drifts, the comparison
  is invalid.

## Sovereign gate discipline

This plan does NOT touch the Compass-8 primitive-native acceptance
gate. The sovereign gate remains red. Even a `defend` verdict does
NOT establish a ZPE-specific wedge, because enrichment features can
be attached to any sparse-metadata format equally well. The report
MUST include an explicit disclosure of this scope boundary.

## Forbidden proxies (contract)

- No primitive-native closure claim.
- No ZPE-specific wedge claim from a positive verdict (state layer
  is representation-agnostic).
- No leaky CV (track-level splits only).
- No claim on `combined`-only results without an appearance-only or
  trajectory-only ablation showing attribution.
- No ground-truth class labels used as features.
- No cherry-picked best-fold results.
- No `ap_proxy` substitution.
- No external-repo touches.
- No reopening Phase 10 or Red Magic validation.
- No reopening archive-query on box-state substrate.

<tasks>

<task type="auto">
  <name>Task 1: Stand up Candidate C harness and backbone integration</name>
  <files>zpe_video_lab/python/phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment.py</files>
  <action>
    Create the Candidate C harness with explicit dependency declaration:
    numpy, scikit-learn, lightgbm, torch, transformers, opencv-python,
    plus the existing noisy-proxy generator from
    `zpe_video_lab/python/phase9_4_1_1_2_fair_baseline_archive_query.py`.

    Implement:

    - `regenerate_noisy_proxy(seed=<identical to 09.4.1.1.2>) ->
       list of (clip_id, frames_rgb, tracks, labels)`
      where `tracks` is the list of (track_id, boxes, label). Reuse
      the exact generator; do not duplicate the ghost-track logic.
    - `load_backbone(name='siglip-so400m-patch14-384' or
       'dinov2-base') -> model` with `torch.manual_seed(0)`,
       `torch.use_deterministic_algorithms(True)` where possible.
    - `extract_appearance(backbone, frame_rgb, bbox) -> 128-D tensor`
      via cropping, resizing, normalizing, forward pass, and mean-
      pooling to 128-D (project down if backbone output is larger).
    - `appearance_features(track, frames) -> 256-D` = concat of
      embedding mean and std across first/middle/last frame crops.
    - `trajectory_features(track) -> 5-D` = {displacement, length,
       mean_speed, portal_dwell, curvature}.
    - `combined_features(track, frames) -> 261-D` = concat.
    - `cv_fit_eval(features, labels, classifier, k=5, seed=0) ->
       per_fold_results` with stratified track-level splits.
    - `run_ablation(features_by_ablation, labels, classifier) ->
       per_ablation_results`.
    - `shuffled_feature_control(features, labels) -> precision_mean`.
    - `saturated_feature_control(features, labels) -> precision_mean`.

    Add a `--smoke` mode that runs end-to-end on a single clip and
    verifies:
    - Proxy regeneration produces the expected 29 predicted / 4
      matched / 4 GT counts (assert equality to 09.4.1.1.2 numbers).
    - Backbone loading succeeds and returns 128-D embedding for one
      bbox crop.
    - Feature shapes: appearance_only = 256, trajectory_only = 5,
      combined = 261.
    - CV split is track-level (verify by asserting train and test
      tracks are disjoint).
  </action>
  <verify>
    1. `--help` prints usage with `--backbone`, `--classifier`,
       `--seed`, `--smoke`, `--output-dir`.
    2. Smoke mode asserts proxy regeneration count match.
    3. Smoke mode asserts feature dimensions.
    4. Smoke mode asserts CV splits are track-disjoint.
    5. Dimensional check: precision in [0, 1]; recall in [0, 1];
       feature_dim matches claimed size.
    6. Determinism check: two runs of smoke with same seed produce
       identical per-fold precision values (bit-equal or within
       floating-point epsilon of 1e-10).
  </verify>
  <done>Harness scaffolding exists, smoke mode passes determinism and dimension checks, proxy regeneration matches 09.4.1.1.2 counts</done>
</task>

<task type="auto">
  <name>Task 2: Run 2-classifier x 3-ablation x 5-fold CV sweep plus controls</name>
  <files>zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment/summary.json, zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment/cv_table.csv, zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment/ablation_table.csv</files>
  <action>
    Execute the full sweep on the regenerated noisy proxy.

    For each classifier in {logreg, lightgbm}:
      For each ablation in {appearance_only, trajectory_only, combined}:
        Run stratified 5-fold CV at seed=0; record per-fold
        precision, recall, f1, confusion matrix, n_train, n_test,
        n_positive. Write one row per fold to cv_table.csv.

    For the best ablation + classifier (by precision_mean subject to
    recall_mean >= 0.9), run the 3-seed robustness check at seeds
    {0, 7, 42}; report median of the three seed runs.

    Run the controls:
    - Shuffled-features ablation: shuffle feature vectors across
      tracks while keeping labels fixed; report precision and recall.
    - Saturated-features ablation: set all tracks to the same feature
      vector; report precision and recall.

    Record extract_cost_ms_per_track: wall clock for backbone
    inference on 10 tracks; report median and p90.

    Emit summary.json:

    ```
    {
      "proxy": { "seed": ..., "total_predicted": 29, "total_matched": 4, "total_gt": 4, "base_rate": 0.138 },
      "backbone": "<siglip-so400m-patch14-384|dinov2-base>",
      "classifiers": ["logreg", "lightgbm"],
      "ablations": ["appearance_only", "trajectory_only", "combined"],
      "cv": { "k": 5, "seed": 0, "split_level": "track" },
      "results": {
        "logreg": {
          "appearance_only": { "precision_mean": ..., "precision_stderr": ..., "recall_mean": ..., "recall_stderr": ..., "f1_mean": ..., "meets_threshold": true|false },
          "trajectory_only": { ... },
          "combined": { ... }
        },
        "lightgbm": { ... }
      },
      "robustness_seeds": {
        "winner_ablation": "<ablation>",
        "winner_classifier": "<classifier>",
        "seeds": [0, 7, 42],
        "precision_median": ...,
        "recall_median": ...,
        "high_variance_flag": true|false
      },
      "controls": {
        "shuffled_features_precision": ...,
        "shuffled_features_recall": ...,
        "saturated_features_precision": ...,
        "saturated_features_recall": ...
      },
      "attribution": {
        "combined_vs_appearance_only_delta": ...,
        "combined_vs_trajectory_only_delta": ...,
        "lift_is_attributable": true|false
      },
      "extract_cost_ms_per_track": { "median": ..., "p90": ... },
      "classifier_agreement": {
        "logreg_meets_threshold": true|false,
        "lightgbm_meets_threshold": true|false,
        "agree": true|false
      },
      "verdict": "defend" | "kill",
      "verdict_justification": "..."
    }
    ```

    Verdict decision rule:
    - `defend` iff:
      - At least one (classifier, ablation) combination has
        `precision_mean >= 0.5` AND `recall_mean >= 0.9`.
      - AND classifier_agreement.agree == true (both logreg and
        lightgbm pass the threshold under the winning ablation).
      - AND attribution.lift_is_attributable == true (appearance_only
        OR trajectory_only alone shows precision >= 0.138 + 0.1).
      - AND robustness_seeds.high_variance_flag == false.
      - AND controls.shuffled_features_precision < 0.25 (no CV leak).
    - `kill` otherwise.

    Write ablation_table.csv with one row per (classifier, ablation).
  </action>
  <verify>
    1. summary.json validates as JSON.
    2. cv_table.csv has exactly `2 * 3 * 5 = 30` rows.
    3. ablation_table.csv has exactly `2 * 3 = 6` rows.
    4. For each (classifier, ablation), precision_mean and recall_mean
       are in [0, 1].
    5. Shuffled-features precision is within [0.05, 0.25] (chance
       level around base rate).
    6. Saturated-features precision equals base rate `0.138` within
       1e-3 tolerance.
    7. combined precision >= max(appearance_only, trajectory_only)
       precision for each classifier; if not, attribution flags
       overfitting and verdict is kill.
    8. verdict is exactly one of {"defend", "kill"}.
    9. All five verdict prerequisites are explicitly recorded when
       defend is returned.
  </verify>
  <done>summary.json, cv_table.csv, ablation_table.csv exist; full 2x3x5 sweep ran; controls pass; attribution analyzed; verdict data-driven</done>
</task>

<task type="auto">
  <name>Task 3: Write benchmark report, disclose state-layer scope, preserve sovereign gate</name>
  <files>.gpd/phases/09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection/09.4.1.1.2.1-03-BENCHMARK-REPORT.md, .gpd/phases/09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection/09.4.1.1.2.1-03-SUMMARY.md</files>
  <action>
    Write BENCHMARK-REPORT with these sections:

    1. **Noisy proxy reproduction** (confirm 29/4/4 counts match
       Phase 09.4.1.1.2).
    2. **Feature definitions** (exact appearance backbone id,
       exact trajectory feature math, exact dimensions).
    3. **CV discipline** (stratified, track-level, fixed seed).
    4. **Per-ablation results** (include ablation_table inline).
    5. **Attribution analysis** (appearance-only vs trajectory-only
       vs combined; which family carries the signal if any).
    6. **Controls** (shuffled, saturated; confirm no CV leak).
    7. **Robustness seeds** (three-seed median; high-variance flag).
    8. **Extract cost disclosure** (ms/track; feasibility note for
       scaling).
    9. **Classifier agreement**.
    10. **Verdict** (defend or kill with the specific numbers).
    11. **State-layer-not-serialization disclosure**: explicit
        paragraph stating that a positive result establishes only
        that state enrichment is the lever; appearance embeddings
        and trajectory features can be attached to raw struct+zlib,
        Parquet, or JSON equally well, so this does NOT establish a
        ZPE-specific wedge.
    12. **Sovereign gate boundary**: explicit statement that this
        result does NOT close the Compass-8 primitive-native gate,
        regardless of verdict.
    13. **Forbidden-proxy audit** (no primitive-native claim, no
        ZPE-specific claim from positive verdict, no leaky CV, no
        combined-only defend, no GT leakage, no cherry-picking, no
        `ap_proxy`, no external-repo touches).
    14. **Next move conditional on verdict**:
        - defend -> Plan 04 synthesis ranks Candidate C highly AND
          reframes the research question away from serialization
          toward state-layer primitives.
        - kill -> Plan 04 synthesis retires Candidate C and notes
          that the noisy proxy false-positive cloud is NOT
          attackable by this feature family.

    Write SUMMARY.md frontmatter:
    `status`, `kill_or_defend`, `sovereign_gate_status: red`,
    `precision_mean`, `recall_mean`, `winner_ablation` (if defend),
    `high_variance_flag`, `extract_cost_ms_per_track`,
    `state_layer_disclosure_present: true`, `next_required_work`,
    `forbidden_proxies_rejected`.

    Include uncertainty markers: backbone_nondeterminism,
    small_sample_cv, feature_choice_sensitivity, seed_variance,
    extract_cost_mac.
  </action>
  <verify>
    1. BENCHMARK-REPORT has all fourteen sections.
    2. SUMMARY frontmatter includes `kill_or_defend` as one of
       {"kill", "defend"} and `sovereign_gate_status: red`.
    3. SUMMARY frontmatter includes `state_layer_disclosure_present: true`.
    4. Grep: the phrase "not a ZPE-specific wedge" OR "state layer is
       representation-agnostic" appears explicitly in the report.
    5. Grep: the phrase "primitive-native closure" does NOT appear
       associated with any positive claim.
    6. Grep: "ap_proxy" does not appear as a source of evidence.
    7. If verdict=="defend", verify that attribution table shows a
       single-family ablation (appearance_only or trajectory_only)
       passed the minimum attribution lift.
  </verify>
  <done>BENCHMARK-REPORT and SUMMARY exist; state-layer disclosure is explicit; verdict data-driven; sovereign gate preserved</done>
</task>

</tasks>

<verification>
- Dimensional check: precision, recall in [0, 1]; CV fold count = 5;
  feature dims match claimed dimensions; extract cost in ms/track.
- Limiting-case check: shuffled-features ~ base rate; saturated-
  features == base rate; proxy-regeneration counts match 29/4/4.
- Error budget: 5-fold CV with stderr; 3-seed robustness on winner;
  high-variance flag forces kill.
- Consistency check: combined >= max(single-family); logreg and
  lightgbm must agree for defend; controls confirm no CV leak.
- Anchor discipline: baseline is naive-operator precision 0.138 from
  Phase 09.4.1.1.2 on the exact same noisy proxy.
- Forbidden-proxy audit: no ZPE-specific claim from positive verdict,
  no primitive-native closure, no leaky CV, no combined-only defend,
  no GT-leakage, no cherry-picking, no external-repo touches.
</verification>

<success_criteria>
Plan 03 closes when summary.json, cv_table.csv, ablation_table.csv,
BENCHMARK-REPORT, and SUMMARY all exist; 2x3x5 CV sweep and controls
are complete; verdict is `{defend|kill}` with all five defend
prerequisites recorded; state-layer-not-serialization disclosure is
present; sovereign gate is preserved.
</success_criteria>

<output>
After completion, create `.gpd/phases/09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection/09.4.1.1.2.1-03-SUMMARY.md`
</output>
</content>
</invoke>