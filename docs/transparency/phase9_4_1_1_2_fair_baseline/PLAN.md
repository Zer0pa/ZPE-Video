---
phase: 09.4.1.1.2-fair-baseline-archive-query-falsification
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - zpe_video_lab/python/phase9_4_1_1_2_fair_baseline_archive_query.py
  - zpe_video_lab/reports/phase9_4_1_1_2_fair_baseline_archive_query/summary.json
  - .gpd/phases/09.4.1.1.2-fair-baseline-archive-query-falsification/09.4.1.1.2-01-BENCHMARK-REPORT.md
  - .gpd/phases/09.4.1.1.2-fair-baseline-archive-query-falsification/NEXT-EXPERIMENT-PROPOSAL.md
  - .gpd/phases/09.4.1.1.2-fair-baseline-archive-query-falsification/09.4.1.1.2-01-SUMMARY.md
interactive: false

conventions:
  units: "storage bytes, ingest/query latency ms median, precision/recall, temporal IoU"
  baseline_rule: "fair commercial baseline must be a persisted sparse-metadata sidecar, not live-frame-decode-plus-detector-rerun"
  representation_set: "ZPE packet, raw struct+zlib, SQLite (indexed), Parquet (snappy), JSON+gzip"
  operator_set: "naive portal-crossing (center-inside-portal for >=4 frames); hardened (inner-40% portal + persistence + displacement)"
  public_repo_rule: "public `zpe-video` shell remains frozen; lab code and GPD artifacts only"

contract:
  schema_version: 1
  scope:
    question: "Does the ZPE packet format have a unique structural advantage for the archive-query workload versus commodity sparse-metadata formats, and is the representation the blocker for the 09.4.1.1.1 false-positive cloud?"
  claims:
    - id: claim-phase09_4_1_1_2-representation-falsified
      statement: "At least one commodity sparse-metadata format strictly dominates the ZPE packet on both storage and query latency with identical precision/recall, or matches within 2x on both axes; this falsifies the ZPE packet's claim to a unique structural advantage for archive query."
      deliverables: [deliv-phase09_4_1_1_2-harness, deliv-phase09_4_1_1_2-summary-json, deliv-phase09_4_1_1_2-report]
      acceptance_tests: [test-phase09_4_1_1_2-kill-criterion]
      references: [ref-phase09_4_1_1_1-bench, ref-phase09_4_1_1-proxy-harness, ref-agent-A-audit]
    - id: claim-phase09_4_1_1_2-operator-is-blocker
      statement: "All tested representations produce identical precision under the naive portal-crossing operator on a noisy proxy; this proves the information needed to move precision is not in the box stream, falsifying the 'richer packet semantics' thesis at the representation level."
      deliverables: [deliv-phase09_4_1_1_2-summary-json, deliv-phase09_4_1_1_2-report]
      acceptance_tests: [test-phase09_4_1_1_2-operator-equality]
      references: [ref-phase09_4_1_1_1-bench, ref-agent-A-audit]
    - id: claim-phase09_4_1_1_2-sovereign-gate-preserved
      statement: "This phase does not touch the sovereign Compass-8 primitive-native acceptance gate; the gate remains red, and no closure claim is made from this phase's result."
      deliverables: [deliv-phase09_4_1_1_2-report]
      acceptance_tests: [test-phase09_4_1_1_2-scope-boundary]
      references: [ref-project-contract, ref-recovery-prd]
  deliverables:
    deliv-phase09_4_1_1_2-harness:
      artifact: "zpe_video_lab/python/phase9_4_1_1_2_fair_baseline_archive_query.py"
      description: "Self-contained Python 3.14 harness that encodes the same tracked-box stream into five representations and runs two operators on clean and noisy proxies with median-of-repeats latency measurement"
    deliv-phase09_4_1_1_2-summary-json:
      artifact: "zpe_video_lab/reports/phase9_4_1_1_2_fair_baseline_archive_query/summary.json"
      description: "Machine-readable per-representation per-operator storage/ingest/query/precision/recall numbers with deterministic kill/defend verdict block"
    deliv-phase09_4_1_1_2-report:
      artifact: ".gpd/phases/09.4.1.1.2-fair-baseline-archive-query-falsification/09.4.1.1.2-01-BENCHMARK-REPORT.md"
      description: "Human-readable benchmark report with the five-representation comparison tables, the operator-equality finding, and an explicit verdict"
  acceptance_tests:
    test-phase09_4_1_1_2-kill-criterion:
      statement: "The summary.json verdict block shows at least one baseline strictly dominating or matching-within-2x the ZPE packet on both storage and query latency with identical precision/recall."
    test-phase09_4_1_1_2-operator-equality:
      statement: "The summary.json records identical naive-operator precision for all five representations on the noisy proxy (equal to 15 significant figures)."
    test-phase09_4_1_1_2-scope-boundary:
      statement: "The report explicitly preserves the sovereign gate boundary and does not claim primitive-native closure."
  references:
    ref-phase09_4_1_1_1-bench:
      locator: ".gpd/phases/09.4.1.1.1-pod-backed-live-fixed-camera-event-state-query-wedge/09.4.1.1.1-01-BENCHMARK-REPORT.md"
      role: "falsification target"
    ref-phase09_4_1_1-proxy-harness:
      locator: "zpe_video_lab/python/phase9_4_1_1_primitive_event_state_index.py"
      role: "harness pattern source"
    ref-agent-A-audit:
      locator: "independent Opus-class audit agent output, 2026-04-16"
      role: "operator-as-blocker hypothesis source"
    ref-project-contract:
      locator: ".gpd/PROJECT.md"
      role: "sovereign gate definition"
    ref-recovery-prd:
      locator: "EXECUTION_PRD_AUTHORITY_RECOVERY_AND_HANDOVER_RECONCILIATION_2026-03-13.md"
      role: "recovery-lane authority rules"
---

# Phase 09.4.1.1.2 Plan 01 — Fair-Baseline Archive-Query Falsification

## Objective

Falsify or defend the ZPE packet format's claim to a unique structural advantage
for the archive-query workload by benchmarking it against four commodity
sparse-metadata formats on the same bounded Mac proxy corpus, using two
operators (naive and hardened) on clean and noisy surfaces, and decide whether
any representation-level change can move archive-query precision before any
new "richer packet semantics" proposal is accepted.

## Method

Build a self-contained Python harness that:

1. Generates a clean 3-clip / 60-frame proxy corpus with 4 ground-truth portal
   crossings (same specs as phase 09.4.1.1).
2. Generates a noisy variant with 10 ghost tracks per clip that briefly drift
   through the portal (simulates the 734-predicted / 19-GT live cloud from
   phase 09.4.1.1.1).
3. Encodes the same tracked-box stream into five representations:
   ZPE packet (delta + zlib), raw struct+zlib (no delta), indexed SQLite,
   Parquet (snappy), JSON+gzip.
4. Runs two operators on each representation: naive (current) and hardened
   (inner-40% portal + 8-frame outside persistence + 15-px displacement).
5. Measures storage, ingest latency (median of 5), query latency (median of
   11), precision, recall, mean temporal IoU per combination.
6. Derives a deterministic kill/defend verdict.

## Kill / Defend Criteria

- Kill (any one):
  - a baseline strictly dominates ZPE on both storage AND query latency with
    identical precision/recall
  - a baseline matches ZPE within 2x on both axes with identical semantics
  - all representations produce identical naive-operator precision on noisy
    surface (operator is the blocker, not representation)
- Defend (must hit):
  - ZPE dominates every baseline by >=2x on at least one of {storage, query
    latency} under matched operator

## Sovereign Gate Discipline

This phase does not touch the Compass-8 primitive-native acceptance gate.
The gate remains red. No closure claim may be derived from this phase's
result, whatever the outcome.
