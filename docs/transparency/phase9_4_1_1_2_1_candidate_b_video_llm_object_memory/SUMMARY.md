---
phase: 09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection
plan: 02
depth: standard
one-liner: "Candidate B verdict: defend — ZPE packet is cross-writer bit-exact under default settings while Parquet (pyarrow vs fastparquet) is NOT, and ZPE is 5.6x smaller storage and 15x faster cache-read than Parquet at matched LLM-answer accuracy (0.4 / 0.4 / 0.4 within 2pp) on a bounded VideoQA spatial subset; end-to-end query latency is dominated by LLM generation (~2.1s) so cache-format differences do not flow through to user-visible latency."
provides:
  - "Self-contained Python 3.11 harness at `zpe_video_lab/python/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory.py` (smoke + full modes)"
  - "Machine-readable summary at `zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory/summary.json`"
  - "Cross-writer hash test (pyarrow vs fastparquet, repo encoder vs independent reference implementation) at `zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory/cross_writer_hashes.json`"
  - "Per-query table at `zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory/per_query_table.csv`"
affects:
  - wedge-ranking
  - video-LLM-cache-wedge-attribution
  - wave-2-synthesis-input
methods:
  added: [video-LLM-object-memory-cache-benchmark, cross-writer-default-setting-hash-test, matched-answer-accuracy-latency-parity, boxes-as-text-token-serialization]
  patterns: [cross-writer-symmetry-test, default-settings-only-honesty, greedy-decoding-determinism-control, end-to-end-vs-cache-path-latency-decomposition]
key-files:
  created:
    - zpe_video_lab/python/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory.py
    - zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory/summary.json
    - zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory/cross_writer_hashes.json
    - zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory/per_query_table.csv
    - .gpd/phases/09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection/09.4.1.1.2.1-02-SUMMARY.md
key-decisions:
  - "Cross-writer hash stability under DEFAULT settings is the unique structural property of the ZPE packet isolated in this phase. Parquet pyarrow vs fastparquet produce DIFFERENT hashes on the same input under defaults; ZPE repo encoder vs an independent reference implementation (built from format spec) produce IDENTICAL hashes."
  - "Storage advantage is real but not load-bearing for the video-LLM wedge: ZPE 961-1124 bytes per video vs Parquet pyarrow 5359-5386 bytes (4.9x); the ratio grows with dense caches (Parquet fastparquet 25,242 bytes vs ZPE 2,970 bytes, 8.5x)."
  - "Cache-read latency advantage is real but does NOT flow through: ZPE 0.30 ms vs Parquet 4.50 ms (15x) is dominated by LLM generation at 2,087 ms, so end-to-end latency differs by <5% across strategies."
  - "Answer accuracy is identical across all three strategies (none / Parquet / ZPE): 0.4 / 0.4 / 0.4 with max delta 0 pp. This is REQUIRED for the wedge claim — the cache is not lifting accuracy, it is preserving accuracy at matched token count (54 tokens per query across all strategies)."
  - "Sovereign Compass-8 primitive-native gate remains red. Cross-writer hash stability is a SCHEMA-LEVEL property, not a substrate-level property. The defend verdict opens a provenance/audit-receipt direction, not primitive-native closure."
plan_contract_ref: ".gpd/phases/09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection/09.4.1.1.2.1-02-PLAN.md#/contract"
contract_results:
  verdict: defend
  rationale: "ZPE packet achieves the alt-defend branch of the plan contract: matches Parquet on end-to-end latency at matched answer accuracy AND uniquely produces bit-exact cross-writer hashes under default settings that Parquet fails (pyarrow vs fastparquet hashes diverge on identical input). Also meets the cache-read-latency branch (15x faster read) and the storage branch (5-8x smaller) at matched LLM-answer accuracy (within 0 pp). Detector is held identical across strategies (synthetic YOLOv8-shaped deterministic per-frame boxes); greedy decoding preserves deterministic LLM output; repeats=11 cache-path latency, N=1 greedy generation per query."
  cross_writer_hash_stable_zpe: true
  cross_writer_hash_stable_parquet: false
  storage_ratio_zpe_over_parquet_median: 0.18
  cache_read_ratio_zpe_over_parquet_median: 0.067
  answer_accuracy_parity_max_delta_pp: 0.0
sovereign_gate_status: red
next_required_work_hint: "Candidate B opens a provenance / auditable-AI-perception-receipt direction. Follow-up must: (a) test on a larger, messier VideoQA benchmark (e.g., LongVideoBench, NExT-QA) with more realistic video content and wider question families, (b) investigate if the cross-writer hash property has a buyer (C2PA perception receipts, police chain-of-custody, video-LLM memory caching), (c) test whether Parquet can be configured to produce cross-writer-stable output (DuckDB-style enforced encoding) — if it can under any pattern a buyer would accept, the ZPE advantage narrows. Do NOT claim primitive-native closure."
---

# Phase 09.4.1.1.2.1 Plan 02 Summary — Candidate B: Video-LLM Object-Memory Sidecar

## Verdict

`defend` — under the alt-defend branch of the plan contract: ZPE matches
Parquet on end-to-end latency at matched answer accuracy AND uniquely
produces bit-exact cross-writer hashes under default settings.

## Cross-writer hash stability (the unique signal)

| Encoder pair | Cross-writer stable under defaults? |
| ------------ | ----------------------------------- |
| Parquet pyarrow vs Parquet fastparquet | **False** |
| ZPE repo-encoder vs independent reference implementation | **True** |

This is the key structural property Phase 09.4.1.1.2 did NOT isolate
(it compared a single writer of each format). Tested on 4 videos with
identical per-frame detection output; Parquet hashes diverge on every
video under defaults while ZPE hashes match byte-for-byte.

## Storage

| Strategy | Bytes per video | Ratio vs ZPE |
| -------- | --------------- | ------------ |
| Parquet (pyarrow) | 5,359 - 5,386 | 4.8x - 4.9x |
| Parquet (fastparquet) | 5,044 - 25,242 (dense) | 4.5x - 8.5x |
| ZPE packet (repo) | 961 - 2,970 | 1.00x |
| ZPE packet (reference) | 961 - 2,970 | 1.00x |

## Cache-read latency (per query)

| Strategy | Median ms | Ratio vs ZPE |
| -------- | --------- | ------------ |
| None (re-infer) | 0.01 | N/A (no cache) |
| Parquet | 4.50 | 14.9x |
| ZPE packet | 0.30 | 1.00x |

## End-to-end latency (per query)

| Strategy | Median ms | Comment |
| -------- | --------- | ------- |
| None | 2,088 | no cache, direct LLM |
| Parquet | 2,173 | cache + LLM |
| ZPE packet | 2,194 | cache + LLM |

LLM generation dominates (~97%), so cache-format differences do not
flow through to user-visible latency. The wedge is therefore primarily
on cross-writer hash stability and storage, not user-facing speed.

## Answer accuracy parity

| Strategy | Accuracy |
| -------- | -------- |
| None | 0.40 |
| Parquet | 0.40 |
| ZPE packet | 0.40 |

Max delta: 0 pp. Cache does not lift accuracy; it preserves accuracy
at matched token count (54 tokens per query, all strategies).

## What this verdict is NOT

- NOT a primitive-native closure claim. Sovereign gate remains red.
- NOT a storage-superiority claim over tuned Parquet (DuckDB-style
  enforced encoding may close the cross-writer gap; this test is
  specifically about default settings).
- NOT validated on a large / messy public VideoQA benchmark; this is a
  bounded deterministic subset derived from the Phase 09.4.1.1.2 proxy
  plus synthetic YOLOv8-shaped detector output. Explicit in the
  benchmark_note field of summary.json.
- NOT a claim that video-LLMs uniquely need this format; the property
  is schema-level (cross-writer hash stability) and could be achieved by
  any format with sorted, deterministic serialization.

## Sovereign gate status

`red`. This phase does not touch the Compass-8 primitive-native
acceptance gate.

## Next-step implications (for Wave-2 synthesis)

The provenance / perception-receipt direction is opened:
- test on larger VideoQA benchmark (LongVideoBench, NExT-QA)
- identify a buyer that specifically values cross-writer hash stability
  (C2PA provenance, chain-of-custody, regulated audit)
- investigate whether Parquet tuned to enforce determinism closes the
  gap under any pattern a buyer would accept
- preserve sovereign gate discipline
