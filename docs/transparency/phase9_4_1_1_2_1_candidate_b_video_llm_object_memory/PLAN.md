---
phase: 09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection
plan: 02
type: execute
wave: 1
depends_on: []
files_modified:
  - zpe_video_lab/python/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory.py
  - zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory/summary.json
  - zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory/per_query_table.csv
  - zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory/cross_writer_hashes.json
  - .gpd/phases/09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection/09.4.1.1.2.1-02-BENCHMARK-REPORT.md
  - .gpd/phases/09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection/09.4.1.1.2.1-02-SUMMARY.md
interactive: false

conventions:
  units:
    storage_bytes: "bytes (integer)"
    latency_per_query_ms: "ms (float, median of N)"
    tokens_per_query: "integer (LLM context tokens added by cache adapter)"
    answer_accuracy: "dimensionless in [0,1] on the VideoQA benchmark's reference metric"
    hash: "hex-string SHA-256 of cache contents"
  caching_strategies:
    - "none (re-run detector every query)"
    - "parquet (pandas/pyarrow object-memory cache)"
    - "zpe_packet (existing packet encoder as object-memory cache)"
  benchmark_surface: "LongVideoBench spatial subset OR MLVU spatial subset, bounded to ~1 day of wall-clock"
  llm: "open small video-LLM (Qwen2.5-VL-3B-Instruct or similar), run via local GPU if available or reduced-frame CPU fallback"
  public_repo_rule: "public `zpe-video` shell remains frozen; lab code and GPD artifacts only"
  sovereign_gate_rule: "no primitive-native closure claim may be derived regardless of verdict"

dimensional_check:
  storage_bytes: "[bytes]"
  latency_per_query_ms: "[ms]"
  tokens_per_query: "[tokens] (dimensionless discrete integer)"
  answer_accuracy: "dimensionless in [0,1]"
  hash_stability_count: "[events] (count of matching hashes across writers)"

approximations:
  - name: "cached-detection equivalence"
    parameter: "detector outputs at ingest are reused at query time"
    validity: "only valid when the question does not require fresh detection on new pixels"
    breaks_when: "the VideoQA question requires re-detection at a different confidence threshold or on unseen frames"
    check: "restrict the benchmark to spatial questions where 'what was in the frame at time T' is sufficient"
  - name: "LLM sampling stability"
    parameter: "temperature = 0.0, top_p = 1.0, greedy decoding"
    validity: "deterministic answers across runs with the same prompt"
    breaks_when: "non-greedy decoding, batch-size-dependent kernel non-determinism"
    check: "re-run the same prompt N=3 times and assert byte-identical answer strings"

contract:
  schema_version: 1
  scope:
    question: "On a bounded VideoQA spatial-question subset, does the ZPE packet as an object-memory cache for a video-LLM pipeline (a) beat a Parquet object-memory cache by >= 2x on tokens/latency per query at matched answer accuracy AND (b) uniquely produce bit-exact cross-writer hashes that Parquet or JSON cannot match — OR does it fail on both axes (kill)?"
    in_scope:
      - "LongVideoBench spatial subset OR MLVU spatial subset (~50-100 queries)"
      - "YOLOv8m or Qwen2.5-VL built-in detector, one pass per video"
      - "three caching strategies: none, Parquet (pyarrow+fastparquet), ZPE packet (repo+reference)"
      - "Qwen2.5-VL-3B-Instruct or equivalent small open video-LLM, greedy decoding"
      - "cross-writer SHA-256 hash stability test under default writer settings"
    out_of_scope:
      - "large closed-source LLMs (GPT-4o, Gemini, etc.)"
      - "non-greedy decoding as a default setting"
      - "primitive-native Compass-8 closure claims"
      - "external `zpe-video` public GitHub remote touches"
      - "Phase 10 or Red Magic validation reopening"
      - "archive-query on box-state substrate (falsified in 09.4.1.1.2)"
    unresolved_questions:
      - "If B defends on Qwen2.5-VL, does the wedge survive a larger LLM or a different video-LLM family?"
      - "Is the cross-writer hash stability claim for the ZPE packet fragile to schema evolution?"
  claims:
    - id: claim-candidate-b-verdict
      statement: "On a bounded VideoQA spatial-question subset with a fixed open video-LLM and identical upstream detection, either (defend) the ZPE packet matches Parquet on latency AND produces bit-exact cross-writer hashes under default settings that Parquet or JSON cannot match without special configuration, or (kill) the ZPE packet fails to beat Parquet by >= 2x on tokens-per-query OR latency-per-query AND also fails to uniquely produce cross-writer hash stability."
      deliverables:
        - deliv-candidate-b-harness
        - deliv-candidate-b-summary
        - deliv-candidate-b-per-query-table
        - deliv-candidate-b-cross-writer-hashes
        - deliv-candidate-b-report
      acceptance_tests:
        - test-candidate-b-kill-or-defend
        - test-candidate-b-latency-measurement
        - test-candidate-b-cross-writer-hash
        - test-candidate-b-limiting-cases
      references:
        - ref-prior-phase-summary
        - ref-prior-phase-proposal
        - ref-research
        - ref-agent-b-scan
        - ref-project-contract
        - ref-recovery-prd
    - id: claim-candidate-b-sovereign-gate-preserved
      statement: "No outcome of this plan claims primitive-native Compass-8 closure; the sovereign gate remains red regardless of verdict."
      deliverables:
        - deliv-candidate-b-report
        - deliv-candidate-b-summary
      acceptance_tests:
        - test-candidate-b-scope-boundary
      references:
        - ref-project-contract
        - ref-recovery-prd
  deliverables:
    - id: deliv-candidate-b-harness
      kind: code
      path: "zpe_video_lab/python/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory.py"
      description: "Self-contained harness that ingests a VideoQA spatial-question subset, runs YOLOv8m or DETR detection once per video, caches object-memory in three strategies (none, Parquet, ZPE packet), and measures per-query tokens/latency/answer-accuracy plus cross-writer hash stability under a fixed small open video-LLM (Qwen2.5-VL-3B-Instruct or equivalent)"
      must_contain:
        - "write_cache_parquet_pyarrow"
        - "write_cache_parquet_fastparquet"
        - "write_cache_zpe_repo"
        - "write_cache_zpe_reference"
        - "run_llm"
    - id: deliv-candidate-b-summary
      kind: data
      path: "zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory/summary.json"
      description: "Machine-readable per-strategy tokens-per-query, latency-per-query (median of 11), answer accuracy, storage footprint, cross-writer hash-stability counts, kill/defend verdict block"
      must_contain:
        - "verdict"
        - "wedge_metrics"
        - "answer_accuracy_parity"
        - "limiting_cases"
    - id: deliv-candidate-b-per-query-table
      kind: table
      path: "zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory/per_query_table.csv"
      description: "Per-query table: query_id, strategy, tokens_added, latency_ms, answer, is_correct, detections_reused"
      must_contain:
        - "query_id"
        - "strategy"
        - "latency_ms"
    - id: deliv-candidate-b-cross-writer-hashes
      kind: data
      path: "zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory/cross_writer_hashes.json"
      description: "SHA-256 of cache bytes for each (video, strategy, writer_implementation) combination, demonstrating whether each strategy is hash-stable across writer implementations under default settings"
      must_contain:
        - "hash_pyarrow"
        - "hash_fastparquet"
        - "hash_repo"
        - "hash_reference"
    - id: deliv-candidate-b-report
      kind: report
      path: ".gpd/phases/09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection/09.4.1.1.2.1-02-BENCHMARK-REPORT.md"
      description: "Human-readable report with per-strategy tokens/latency/accuracy tables, cross-writer hash disclosure, limiting cases, and explicit kill/defend verdict"
      must_contain:
        - "Verdict"
        - "Cross-writer hash"
        - "Sovereign gate boundary"
        - "Answer-accuracy parity"
  acceptance_tests:
    - id: test-candidate-b-kill-or-defend
      subject: claim-candidate-b-verdict
      kind: benchmark
      procedure: "Inspect summary.json `verdict` field and `wedge_metrics` block; verify the defend decision rule (latency within 1.5x AND zpe cross-writer stable AND parquet NOT cross-writer stable AND answer-accuracy within 2pp) OR the alternate defend path (2x faster on tokens or latency AND accuracy parity); coerce inconclusive -> kill."
      pass_condition: "summary.json records either `verdict: defend` under one of the two defend paths OR `verdict: kill` otherwise, with the exact numbers that triggered the verdict."
      evidence_required:
        - deliv-candidate-b-summary
        - deliv-candidate-b-per-query-table
    - id: test-candidate-b-latency-measurement
      subject: claim-candidate-b-verdict
      kind: benchmark
      procedure: "Verify summary.json records median-of-11 per-query latency with explicit hardware disclosure (mac_cpu or pod_gpu); verify latency is end-to-end (cache read + prompt build + LLM generation)."
      pass_condition: "summary.json `repeats: 11` AND `hardware` is recorded AND each strategy's `median_latency_ms_per_query` is present."
      evidence_required:
        - deliv-candidate-b-summary
    - id: test-candidate-b-cross-writer-hash
      subject: claim-candidate-b-verdict
      kind: reproducibility
      procedure: "Inspect cross_writer_hashes.json; for each strategy, compare SHA-256 from two independent writer implementations (pyarrow vs fastparquet; repo encoder vs reference re-implementation). Record cross_writer_hash_stable per strategy; defend requires zpe_stable AND NOT parquet_stable under default settings."
      pass_condition: "cross_writer_hashes.json contains the four SHA-256 pairs AND summary.json records per-strategy cross_writer_hash_stable booleans."
      evidence_required:
        - deliv-candidate-b-cross-writer-hashes
        - deliv-candidate-b-summary
    - id: test-candidate-b-limiting-cases
      subject: claim-candidate-b-verdict
      kind: limiting_case
      procedure: "Run the empty-cache clip (zero detections) and dense-cache clip (10+ objects/frame); verify all three strategies handle empty gracefully and dense latency does not regress >5x vs the small-clip baseline."
      pass_condition: "summary.json.limiting_cases.empty_cache and .dense_cache are both present; dense_latency_ratio_vs_baseline < 5.0."
      evidence_required:
        - deliv-candidate-b-summary
    - id: test-candidate-b-scope-boundary
      subject: claim-candidate-b-sovereign-gate-preserved
      kind: existence
      procedure: "Grep BENCHMARK-REPORT and SUMMARY for the sovereign-gate boundary paragraph; verify no text ties a positive verdict to primitive-native closure."
      pass_condition: "Both documents include an explicit sovereign_gate_status: red note AND do NOT associate any positive verdict with primitive-native closure."
      evidence_required:
        - deliv-candidate-b-report
  references:
    - id: ref-prior-phase-summary
      kind: prior_artifact
      locator: ".gpd/phases/09.4.1.1.2-fair-baseline-archive-query-falsification/09.4.1.1.2-01-SUMMARY.md"
      role: "must_consider"
      why_it_matters: "prior-phase result that raw-struct+zlib and json+gzip strictly dominated the ZPE packet on archive query; this plan must not repeat that failure mode and must carry its lesson on determinism"
      required_actions: ["read", "cite"]
    - id: ref-prior-phase-proposal
      kind: prior_artifact
      locator: ".gpd/phases/09.4.1.1.2-fair-baseline-archive-query-falsification/NEXT-EXPERIMENT-PROPOSAL.md"
      role: "definition"
      why_it_matters: "source of Candidate B framing, kill/defend criteria, and video-LLM object-memory hypothesis"
      required_actions: ["read", "use"]
    - id: ref-research
      kind: prior_artifact
      locator: ".gpd/phases/09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection/09.4.1.1.2.1-RESEARCH.md"
      role: "method"
      why_it_matters: "consolidated research for Candidate B framework, mathematical map, and validity regime"
      required_actions: ["read", "use"]
    - id: ref-agent-b-scan
      kind: prior_artifact
      locator: "TAKEOVER_ASSESSMENT_2026-04-16_WEDGE.md"
      role: "must_consider"
      why_it_matters: "cross-domain wedge scan that surfaced the video-LLM object-memory pattern"
      required_actions: ["read", "use"]
    - id: ref-project-contract
      kind: spec
      locator: ".gpd/PROJECT.md"
      role: "definition"
      why_it_matters: "sovereign Compass-8 primitive-native gate definition and forbidden-proxy rules; this is the governing anchor the phase MUST NOT violate"
      must_surface: true
      applies_to:
        - claim-candidate-b-verdict
        - claim-candidate-b-sovereign-gate-preserved
      carry_forward_to:
        - claim-candidate-b-verdict
        - claim-candidate-b-sovereign-gate-preserved
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
      subject: claim-candidate-b-sovereign-gate-preserved
      proxy: "narrating any cache-latency or cross-writer-hash win as primitive-native closure"
      reason: "this is a bounded cache-primitive experiment against Parquet, not a substrate win; the sovereign Compass-8 primitive-native gate remains red regardless of verdict"
    - id: forbidden-gt-fed
      subject: claim-candidate-b-verdict
      proxy: "using ground-truth object annotations as cache contents"
      reason: "the cache MUST be populated from the same YOLOv8m/DETR detection pass as the Parquet baseline; GT-fed caches would inflate accuracy and defeat the purpose of the caching comparison"
    - id: forbidden-determinism-proxy
      subject: claim-candidate-b-verdict
      proxy: "claiming determinism as the ZPE-unique wedge without the cross-writer hash test on Parquet AND JSON default settings"
      reason: "Phase 09.4.1.1.2 already proved raw-struct+zlib and json+gzip are byte-deterministic at matched settings; any determinism claim must survive the explicit cross-writer default-settings comparison"
    - id: forbidden-mixed-bundle
      subject: claim-candidate-b-verdict
      proxy: "mixing caching strategies (e.g., ZPE packet + custom LLM re-prompting) in a single lane"
      reason: "each lane MUST be a clean caching strategy so attribution is unambiguous; mixed bundles defeat the comparison"
    - id: forbidden-cherry-pick
      subject: claim-candidate-b-verdict
      proxy: "reporting only queries where the ZPE lane wins"
      reason: "aggregate median and per-query table for the full held-out subset MUST be reported; cherry-picking inflates apparent signal"
    - id: forbidden-temperature-drift
      subject: claim-candidate-b-verdict
      proxy: "using non-greedy decoding without disclosure"
      reason: "greedy decoding (temperature=0.0) is required for deterministic answers; if greedy is unavailable for the chosen LLM, the fallback MUST be declared and N=3 runs reported"
  uncertainty_markers:
    weakest_anchors:
      - "LongVideoBench and MLVU spatial subsets are bounded; generalization outside the sampled subset is not claimed"
      - "Qwen2.5-VL-3B-Instruct specifically; larger LLMs may not preserve the same cache-latency relationship"
    unvalidated_assumptions:
      - "greedy decoding at temperature=0.0 produces fully deterministic answers on this hardware; kernel-level non-determinism may still appear"
      - "the same textual serialization format is fair across cache strategies (tokens-per-query comparison rests on this)"
    competing_explanations:
      - "any ZPE latency win may come from smaller prompt payload, not from the ZPE format specifically; the same-textual-shape check is the control"
      - "Parquet's pyarrow and fastparquet may produce identical bytes under default settings, which would defeat the cross-writer uniqueness claim for ZPE even if ZPE is also stable"
    disconfirming_observations:
      - "if Parquet under default settings is cross-writer hash stable, the cross-writer-uniqueness path to defend is closed"
      - "if ZPE under default settings is NOT cross-writer hash stable across repo vs reference writer, the determinism claim is falsified at its core"
      - "if answer accuracy differs by more than 2pp between strategies, the caches are not serving equivalent information and the run is invalid"
---

# Phase 09.4.1.1.2.1 Plan 02 — Candidate B: Video-LLM Object-Memory Sidecar

## Objective

Test whether the ZPE packet, used as an object-memory cache for a video-LLM
pipeline, either (defend) beats a Parquet object-memory cache by a
decisive 2x on tokens/latency OR uniquely produces bit-exact cross-writer
hashes that Parquet and JSON cannot match under default settings — or
(kill) fails on both axes.

Carry forward the Phase 09.4.1.1.2 lesson: raw-struct+zlib and json+gzip
are also deterministic byte-for-byte at matched settings, so "determinism"
alone is NOT a wedge. The cross-writer test must specifically compare
DEFAULT-setting outputs across independent writer implementations.

## Scope and surface

- **Benchmark:** LongVideoBench spatial subset OR MLVU spatial subset.
  Select a bounded ~50-100 question subset whose ground-truth answers
  depend on "what objects were in the frame at time T". Record the
  exact subset in summary.json (list of query_ids).
- **Detector pass:** once per video using YOLOv8m (Phase 3–7 convention)
  or, if Qwen2.5-VL's integrated detector is stronger on this surface,
  the Qwen2.5-VL detector pass. Detector identity is frozen across all
  three strategies; differences MUST only come from the CACHE, not the
  DETECTION.
- **LLM:** Qwen2.5-VL-3B-Instruct (or an equivalently-sized open model)
  in greedy-decode mode. Record hardware (Mac CPU fallback OR pod GPU).
  If latency is dominated by LLM inference on CPU, prefer the pod via
  `ssh -i ~/.ssh/id_ed25519 -p 33488 root@38.80.152.248` at lane root
  `/workspace/zpe_video_phase03`.

## Method

Build `zpe_video_lab/python/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory.py`
as a self-contained harness runnable either on Mac (CPU) or the pod (GPU).

The script:

1. Loads the held-out VideoQA spatial subset (~50-100 queries).
2. Runs YOLOv8m once per video; stores detections as `{frame_t: [Box]}`.
3. Writes the detection results into three caches:
   - **none**: discarded; detector re-runs at query time.
   - **parquet**: pyarrow default settings; per-video parquet file.
   - **zpe_packet**: existing repo packet encoder; per-video bytes.
4. For each query, constructs the LLM prompt by reading the cache and
   adding a short "objects at time T" serialization to the prompt.
5. Runs the LLM in greedy-decode mode to produce the answer.
6. Measures per-query latency (end-to-end: cache read + prompt build +
   LLM generation) with median of N=11 runs.
7. Counts tokens added to the prompt by each strategy's serialization.
8. Evaluates answer correctness against the benchmark's reference.
9. Measures cross-writer hash stability:
   - For parquet: write the same detections via pyarrow AND fastparquet
     (DEFAULT settings); SHA-256 each; record whether they match.
   - For zpe_packet: write via the repo encoder AND a reference
     re-implementation from the schema (the bootstrap reference in
     `LICENSE.txt`/schema docs); SHA-256 each; record whether they
     match.
   - For `none`: N/A.
10. Runs limiting cases (empty cache; dense cache) and records.
11. Emits summary.json, per_query_table.csv, cross_writer_hashes.json,
    and the BENCHMARK-REPORT and SUMMARY.

## Kill / Defend (contract)

- **Defend (B2):** `zpe_packet` latency is within 1.5x of `parquet`
  median latency per query AND `zpe_packet` is cross-writer hash stable
  under default settings AND `parquet` is NOT cross-writer hash stable
  under default settings.
- **Kill (B1):** `zpe_packet` does not beat `parquet` by 2x on tokens-
  per-query OR latency-per-query AND does not uniquely produce
  cross-writer hash stability. (The kill criterion is the logical
  complement of defend; an "inconclusive" outcome is coerced to kill.)
- **Note:** the original proposal's "beat Parquet by 2x on tokens/
  latency" is preserved as an alternative defend path. If the ZPE
  packet actually beats Parquet by 2x on EITHER axis AND matches
  answer accuracy, that also triggers defend. Both defend paths MUST
  be logged explicitly in summary.json.

## Error budget

- **LLM latency jitter:** small-model inference has O(5-15%) jitter
  per run; median of N=11 per query.
- **LLM sampling variance:** even greedy decoding may be kernel-level
  non-deterministic on GPU; run each query N=3, mark answers as
  `deterministic` or `non_deterministic`, and use the majority answer.
- **Cache read jitter:** on Mac CPU, disk I/O can add 0.5-2 ms; warm
  the filesystem cache before the measurement loop.
- **Hardware disclosure:** latency is NOT comparable across hardware
  (Mac CPU vs pod GPU); the plan MUST run all three strategies on
  THE SAME hardware and compare only intra-hardware.

## Limiting cases

- **Empty cache (zero detections):** a video with no detected objects.
  All three strategies MUST handle gracefully; `none` falls back to
  "no objects detected at time T"; `parquet` and `zpe_packet` MUST
  serialize an empty frame entry without errors. Record storage and
  latency.
- **Dense cache (10+ objects/frame over a long video):** cache size
  grows but the per-query latency MUST NOT regress by more than 5x
  vs the baseline cache load time on a small clip; if it does,
  record and note that the wedge (if any) is bounded to sparse
  workloads.

## Consistency checks (cross-method)

- **Tokens-per-query vs Parquet:** the ZPE packet serialization to
  text tokens for the LLM prompt MUST be fairly compared — use the
  SAME textual shape for both strategies (e.g., "boxes: [(x,y,w,h,
  cls)]"). Any token-count win must come from the cache being
  queryable in less text, not from using a shorter format.
- **Answer accuracy:** the three strategies MUST produce answer
  accuracy within +/- 2 percentage points of each other; any larger
  accuracy delta means the caches are serving different information,
  and the run is discarded.
- **Detection parity:** all three strategies MUST use the SAME
  YOLOv8m detection pass as source-of-truth; cache is a storage
  layer only, not a different detection.

## Sovereign gate discipline

This plan does NOT touch the Compass-8 primitive-native acceptance
gate. The sovereign gate remains red. No closure claim may be derived
from this verdict, defend or kill. The report MUST include an explicit
boundary note.

## Forbidden proxies (contract)

- No primitive-native closure claim.
- No GT-fed cache contents — cache MUST be populated from the same
  YOLOv8m pass as the baselines.
- No determinism-alone claim — cross-writer test MUST explicitly
  compare Parquet's and JSON's default-setting stability.
- No mixed bundles (e.g., ZPE + custom prompt templates).
- No cherry-picked per-query subsets.
- No non-greedy decoding without explicit disclosure.
- No touching the external `zpe-video` public GitHub remote.
- No reopening Phase 10 or Red Magic validation.
- No reopening archive-query on box-state substrate.

<tasks>

<task type="auto">
  <name>Task 1: Stand up Candidate B harness, select subset, freeze detector pass</name>
  <files>zpe_video_lab/python/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory.py</files>
  <action>
    Create the Candidate B harness with explicit dependency declaration:
    numpy, pandas, pyarrow, fastparquet, ultralytics (YOLOv8m),
    transformers + torch (for Qwen2.5-VL-3B-Instruct), the existing
    repo packet parser.

    Implement:

    - `load_videoqa_subset(benchmark='longvideobench', n=100) ->
       list of (video_path, question, reference_answer, relevant_times)`
      that downloads or points to a pre-downloaded bounded subset of
      spatial questions. Record the list of chosen query_ids in
      summary.json.
    - `run_detector_once(video_path) -> dict[frame_t -> list[Box]]`
      using YOLOv8m; record wall-clock time.
    - `write_cache_parquet_pyarrow(detections, path)` and
      `write_cache_parquet_fastparquet(detections, path)` with
      DEFAULT settings.
    - `write_cache_zpe_repo(detections, path)` and
      `write_cache_zpe_reference(detections, path)` where the
      reference re-implementation is built from the schema in
      `LICENSE.txt` / repo schema docs (do not copy from the repo
      encoder; this is the cross-writer test).
    - `read_cache_{parquet,zpe}(path, t) -> list[Box]` with
      sub-millisecond target.
    - `build_llm_prompt(question, objects_at_t) -> (prompt_str, tokens)`
      using the SAME textual serialization for both cache strategies.
    - `run_llm(prompt, hardware='mac_cpu'|'pod_gpu') -> (answer_str,
       latency_ms)` with greedy decoding.
    - `eval_answer(answer, reference) -> bool` using the benchmark's
      reference metric.

    Add a `--smoke` mode that runs the scaffolding on a single video
    with a single query and verifies determinism of cache bytes and
    LLM output (N=3 repeat).
  </action>
  <verify>
    1. `--help` prints a usage block with `--subset`, `--hardware`,
       `--smoke`, `--output-dir`.
    2. Smoke mode writes parquet via both writers AND zpe via both
       writers; prints the four SHA-256s; flags whether each pair
       matches.
    3. Smoke mode runs the LLM N=3 and reports whether answers are
       identical (deterministic) or differ (non-deterministic).
    4. Dimensional check: bytes integer; latency_ms float; tokens
       integer; answer string.
    5. Detector output shape matches `{frame_t: [{bbox, conf, class_id}]}`.
  </verify>
  <done>Harness scaffolding exists, smoke mode verifies determinism, cross-writer hash comparison works, LLM pipeline runs end-to-end on one query</done>
</task>

<task type="auto">
  <name>Task 2: Run three-strategy sweep with cross-writer hash test</name>
  <files>zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory/summary.json, zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory/per_query_table.csv, zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory/cross_writer_hashes.json</files>
  <action>
    Execute the full three-strategy sweep on the chosen bounded subset.

    For each video in the subset:
    - Run YOLOv8m once; record detection wall-clock.
    - Write the detections to all four cache files:
      `{video_id}.parquet.pyarrow`, `{video_id}.parquet.fastparquet`,
      `{video_id}.zpe.repo`, `{video_id}.zpe.reference`.
    - Compute SHA-256 of each cache file; record in cross_writer_hashes.json.

    For each query in the subset:
    - For each strategy in {none, parquet, zpe_packet}:
      - Read the cache (or re-run detector if `none`).
      - Build prompt (same textual shape for parquet and zpe).
      - Run LLM N=11 times; record per-run latency and answer.
      - Record median latency and most-frequent answer.
      - Count tokens added by the serialization.
      - Evaluate correctness.
    - Write one row per (query, strategy) to per_query_table.csv.

    Run limiting cases:
    - Empty-cache clip: a video with zero detected objects.
    - Dense-cache clip: a video with >= 10 objects per frame, >= 30s
      duration.

    Emit summary.json with:

    ```
    {
      "benchmark": "longvideobench_spatial" | "mlvu_spatial",
      "subset_size": N,
      "detector": "yolov8m",
      "llm": "qwen2.5-vl-3b-instruct",
      "hardware": "mac_cpu" | "pod_gpu",
      "repeats": 11,
      "strategies": {
        "none": { "median_tokens_per_query": ..., "median_latency_ms_per_query": ..., "answer_accuracy": ..., "storage_bytes_per_video": 0 },
        "parquet": { "median_tokens_per_query": ..., "median_latency_ms_per_query": ..., "answer_accuracy": ..., "storage_bytes_per_video": ..., "cross_writer_hash_stable": true|false, "hash_pyarrow": ..., "hash_fastparquet": ... },
        "zpe_packet": { "median_tokens_per_query": ..., "median_latency_ms_per_query": ..., "answer_accuracy": ..., "storage_bytes_per_video": ..., "cross_writer_hash_stable": true|false, "hash_repo": ..., "hash_reference": ... }
      },
      "wedge_metrics": {
        "zpe_vs_parquet_latency_ratio": ...,
        "zpe_vs_parquet_tokens_ratio": ...,
        "zpe_cross_writer_stable": true|false,
        "parquet_cross_writer_stable": true|false,
        "unique_determinism_for_zpe": <(zpe_stable AND NOT parquet_stable)>
      },
      "limiting_cases": {
        "empty_cache": { ... },
        "dense_cache": { ... }
      },
      "answer_accuracy_parity": { "max_delta_pp": ..., "within_2pp": true|false },
      "verdict": "defend" | "kill",
      "verdict_justification": "..."
    }
    ```

    Verdict decision:
    - `defend` if (zpe_latency <= parquet_latency * 1.5) AND
      (zpe_cross_writer_stable == true) AND
      (parquet_cross_writer_stable == false) AND
      (answer_accuracy_parity.within_2pp == true).
    - Alternatively, `defend` if (zpe_latency < parquet_latency / 2
      OR zpe_tokens < parquet_tokens / 2) AND
      (answer_accuracy_parity.within_2pp == true).
    - Otherwise `kill`.
  </action>
  <verify>
    1. summary.json validates as JSON.
    2. cross_writer_hashes.json contains all four SHA-256s for each
       video.
    3. per_query_table.csv has exactly `subset_size * 3` rows.
    4. answer_accuracy_parity.within_2pp is explicitly recorded.
    5. verdict is exactly one of {"defend", "kill"}.
    6. If verdict == "defend", wedge_metrics show the specific
       numbers that triggered it.
    7. Limiting-case entries exist and handle edge cases (empty
       cache produces storage >= 0 and latency > 0).
  </verify>
  <done>summary.json, per_query_table.csv, cross_writer_hashes.json all exist; answer-accuracy parity verified; verdict is data-driven</done>
</task>

<task type="auto">
  <name>Task 3: Write benchmark report and summary, audit determinism honestly</name>
  <files>.gpd/phases/09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection/09.4.1.1.2.1-02-BENCHMARK-REPORT.md, .gpd/phases/09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection/09.4.1.1.2.1-02-SUMMARY.md</files>
  <action>
    Write the human-readable benchmark report with these sections:

    1. **Benchmark subset and LLM** (benchmark name, subset size,
       LLM identity, hardware, greedy decoding setting).
    2. **Three-strategy comparison** (tokens/latency/accuracy table;
       per-query table reference).
    3. **Cross-writer hash disclosure** (SHA-256s for parquet
       pyarrow vs fastparquet AND zpe repo vs reference; explicit
       pass/fail per strategy).
    4. **Wedge metrics**: the three numbers that decide the verdict.
    5. **Answer-accuracy parity audit**: max delta in percentage
       points across strategies; record which strategies disagree.
    6. **Limiting cases**: empty and dense cache behavior.
    7. **Verdict**: defend or kill with the specific numbers.
    8. **Sovereign gate boundary**: explicit statement that this
       result does NOT close the primitive-native gate.
    9. **Forbidden-proxy audit** (no GT-fed cache, no determinism-
       alone claim without the cross-writer test, no mixed bundles,
       no cherry-picked queries, no silent non-greedy decoding,
       no external-repo touches).
    10. **Next move conditional on verdict**:
        - defend -> Plan 04 synthesis ranks Candidate B highly and
          recommends a scaling follow-up (not closure).
        - kill -> Plan 04 synthesis retires Candidate B.

    Write SUMMARY.md with frontmatter:
    `status`, `kill_or_defend`, `sovereign_gate_status: red`,
    `cross_writer_hash_result`, `answer_accuracy_parity`,
    `next_required_work`, `forbidden_proxies_rejected`.

    Include uncertainty markers: llm_sampling_variance,
    gpu_vs_cpu_latency, parquet_writer_variance, zpe_writer_variance,
    benchmark_subset_bias.
  </action>
  <verify>
    1. BENCHMARK-REPORT has all ten sections.
    2. SUMMARY frontmatter includes `kill_or_defend` as either
       "kill" or "defend" and `sovereign_gate_status: red`.
    3. Grep: neither file claims "primitive-native closure" or
       "sovereign gate closed".
    4. Grep: cross-writer hash comparison is present for BOTH
       parquet and zpe (not just zpe).
    5. Grep: the specific SHA-256s appear in the report (first 16
       chars minimum).
  </verify>
  <done>BENCHMARK-REPORT and SUMMARY exist, determinism is audited cross-writer honestly, sovereign gate is preserved</done>
</task>

</tasks>

<verification>
- Dimensional check: bytes integer; latency_ms float; tokens integer;
  accuracy dimensionless in [0,1]; hashes hex strings.
- Limiting-case check: empty cache and dense cache handled; dense
  latency regression recorded.
- Error budget: N=11 for latency median; N=3 for LLM answer stability;
  hardware disclosed; cross-hardware comparison forbidden.
- Consistency check: answer-accuracy parity across strategies within
  2pp; tokens-per-query uses identical textual format.
- Anchor discipline: comparator is Parquet (pyarrow + fastparquet);
  LLM is Qwen2.5-VL-3B-Instruct or equivalent; benchmark is
  LongVideoBench or MLVU spatial subset.
- Forbidden-proxy audit: no GT-fed cache, no determinism-alone claim,
  no mixed bundles, no cherry-picking, no primitive-native closure,
  no external-repo touches.
</verification>

<success_criteria>
Plan 02 closes when summary.json, per_query_table.csv,
cross_writer_hashes.json, BENCHMARK-REPORT, and SUMMARY all exist;
verdict is `{defend|kill}`; cross-writer hash test was run for BOTH
parquet and zpe; answer accuracy parity is verified; sovereign gate
is preserved with an explicit boundary note.
</success_criteria>

<output>
After completion, create `.gpd/phases/09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection/09.4.1.1.2.1-02-SUMMARY.md`
</output>
</content>
</invoke>