---
phase: 09.4.1.1.2-fair-baseline-archive-query-falsification
plan: 01
depth: standard
one-liner: "09.4.1.1.2-01 built and ran a five-representation / two-operator fair-baseline archive-query harness on clean and noisy Mac proxies, showed that raw struct+zlib strictly dominates the ZPE packet on both storage (0.14x) and query latency (0.76x) with identical precision/recall while json+gzip also strictly dominates on both axes, and proved all five representations produce identical naive-operator precision (0.138) on the noisy surface — falsifying both the ZPE packet's claim to a unique structural advantage and the 'richer packet semantics' thesis at the representation level."
provides:
  - "Self-contained Python 3.14 fair-baseline harness at `zpe_video_lab/python/phase9_4_1_1_2_fair_baseline_archive_query.py`"
  - "Machine-readable summary with deterministic kill/defend verdict at `zpe_video_lab/reports/phase9_4_1_1_2_fair_baseline_archive_query/summary.json`"
  - "Human-readable benchmark report at `.gpd/phases/09.4.1.1.2-fair-baseline-archive-query-falsification/09.4.1.1.2-01-BENCHMARK-REPORT.md`"
  - "Next-experiment proposal with three bounded candidates and per-candidate kill criteria at `.gpd/phases/09.4.1.1.2-fair-baseline-archive-query-falsification/NEXT-EXPERIMENT-PROPOSAL.md`"
  - "Fresh-eyes takeover assessment at `TAKEOVER_ASSESSMENT_2026-04-16_WEDGE.md`"
affects:
  - wedge-ranking
  - archive-query-line-retirement
  - next-phase-candidate-selection
methods:
  added: [fair-baseline-archive-query-harness, five-representation-comparison, naive-vs-hardened-operator-ablation, clean-vs-noisy-proxy-corpus, deterministic-kill-defend-verdict]
  patterns: [commodity-baseline-discipline, operator-vs-representation-decoupling, median-of-repeats-latency, parallel-opus-class-fresh-eyes-agents]
key-files:
  created:
    - zpe_video_lab/python/phase9_4_1_1_2_fair_baseline_archive_query.py
    - zpe_video_lab/reports/phase9_4_1_1_2_fair_baseline_archive_query/summary.json
    - .gpd/phases/09.4.1.1.2-fair-baseline-archive-query-falsification/09.4.1.1.2-01-BENCHMARK-REPORT.md
    - .gpd/phases/09.4.1.1.2-fair-baseline-archive-query-falsification/09.4.1.1.2-01-PLAN.md
    - .gpd/phases/09.4.1.1.2-fair-baseline-archive-query-falsification/09.4.1.1.2-01-SUMMARY.md
    - .gpd/phases/09.4.1.1.2-fair-baseline-archive-query-falsification/NEXT-EXPERIMENT-PROPOSAL.md
    - .gpd/phases/09.4.1.1.2-fair-baseline-archive-query-falsification/.continue-here.md
    - TAKEOVER_ASSESSMENT_2026-04-16_WEDGE.md
  modified:
    - .gpd/STATE.md
    - .gpd/ROADMAP.md
key-decisions:
  - "The prior 09.4.1.1.1 live-replay baseline was a strawman, not a commercial incumbent; a fair baseline must persist tracks at ingest and query the persisted state."
  - "The ZPE packet's delta encoding is empirically counterproductive for sparse/ephemeral-track data; single-pass zlib over raw struct recovers 7x smaller storage."
  - "The operator is the precision blocker on the current box stream; no serialization-level change can move precision."
  - "Demote 'searchable primitive event/state index' from the primary wedge line; it is not a ZPE-specific direction on this evidence."
  - "Do not reopen Phase 10 or Red Magic validation; sovereign gate remains red."
  - "Do not touch the external GitHub remote managed by the other agent."
plan_contract_ref: ".gpd/phases/09.4.1.1.2-fair-baseline-archive-query-falsification/09.4.1.1.2-01-PLAN.md#/contract"
contract_results:
  claims:
    claim-phase09_4_1_1_2-representation-falsified:
      status: passed
      summary: "Raw struct+zlib strictly dominates the ZPE packet on storage (1,077 B vs 7,595 B = 0.14x) AND query latency (1.81 ms vs 2.38 ms = 0.76x) with identical precision and recall on the clean proxy; json+gzip also strictly dominates on both axes (0.21x storage, 0.99x latency). The ZPE packet has NO unique structural advantage for archive query."
      linked_ids: [deliv-phase09_4_1_1_2-harness, deliv-phase09_4_1_1_2-summary-json, deliv-phase09_4_1_1_2-report, test-phase09_4_1_1_2-kill-criterion]
    claim-phase09_4_1_1_2-operator-is-blocker:
      status: passed
      summary: "All five representations produce exactly 0.13793103448275862 precision (29 predicted, 4 matched, 4 GT) under the naive operator on the noisy proxy, equal to 15 significant figures. No serialization-level change can move precision; the blocker is operator engineering and/or state enrichment, both of which are representation-agnostic."
      linked_ids: [deliv-phase09_4_1_1_2-summary-json, deliv-phase09_4_1_1_2-report, test-phase09_4_1_1_2-operator-equality]
    claim-phase09_4_1_1_2-sovereign-gate-preserved:
      status: passed
      summary: "This phase does not touch the sovereign Compass-8 primitive-native gate. The gate remains red. The benchmark report and takeover assessment explicitly subordinate this phase's verdict to the sovereign objective."
      linked_ids: [deliv-phase09_4_1_1_2-report, test-phase09_4_1_1_2-scope-boundary]
  deliverables:
    deliv-phase09_4_1_1_2-harness:
      status: delivered
      path: "zpe_video_lab/python/phase9_4_1_1_2_fair_baseline_archive_query.py"
    deliv-phase09_4_1_1_2-summary-json:
      status: delivered
      path: "zpe_video_lab/reports/phase9_4_1_1_2_fair_baseline_archive_query/summary.json"
    deliv-phase09_4_1_1_2-report:
      status: delivered
      path: ".gpd/phases/09.4.1.1.2-fair-baseline-archive-query-falsification/09.4.1.1.2-01-BENCHMARK-REPORT.md"
  verdict: "zpe_packet_beaten_by_commodity_format"
  rationale: "Raw struct+zlib strictly dominates ZPE packet on storage (0.14x) AND query latency (0.76x) with identical precision and recall on the clean proxy; json+gzip also strictly dominates on both axes. All five representations produce identical noisy-operator precision. The archive-query wedge as ZPE-specific is falsified; the 'richer packet semantics will attack false positives' thesis is also falsified at the representation level. The sovereign primitive-native gate remains red."
  next_required_work: "Operator decision required among three bounded candidates documented in NEXT-EXPERIMENT-PROPOSAL.md: (A) ROI/foveated guidance sidecar, (B) video-LLM object-memory sidecar pivot, (C) primitive-semantic enrichment on noisy proxy. Operator directive (2026-04-16) is to run all three as parallel hypotheses in phase 09.4.1.1.3 rather than pre-selecting."
---

# Phase 09.4.1.1.2 Plan 01 Summary — Fair-Baseline Archive-Query Falsification

See `09.4.1.1.2-01-BENCHMARK-REPORT.md` for the full benchmark tables and
interpretation. See `NEXT-EXPERIMENT-PROPOSAL.md` for the three bounded
candidate directions with explicit per-candidate kill criteria.

The sovereign Compass-8 primitive-native acceptance gate remains red and is
untouched by this phase. No closure claim is made.
