# Transparency Bundle

Date: 2026-04-17

This directory is a reproducible snapshot of the evidence behind the
commercial claims in [`../WEDGE.md`](../WEDGE.md). Everything in
[`../TRANSPARENCY_JOURNEY.md`](../TRANSPARENCY_JOURNEY.md) that is
referenced as "the kill verdict" or "the defend verdict" has its
machine-readable summary, its executable harness, and its GPD-ledger
PLAN / SUMMARY recorded below.

## Layout

```
docs/transparency/
├── phase9_4_1_1_2_fair_baseline/                         # archive-query fair-baseline kill
├── phase9_4_1_1_2_1_candidate_a_roi_sidecar/             # Candidate A: kill
├── phase9_4_1_1_2_1_candidate_b_video_llm_object_memory/ # Candidate B: defend (the wedge)
├── phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment/ # Candidate C: defend-with-caveat
├── phase09_4_1_1_2_2_receipt_core_provenance_benchmark/  # receipt-core C2PA-style follow-up
└── research_ledger/
    ├── VERDICT-SYNTHESIS.md
    ├── ranked_hypothesis_ladder.md
    ├── WAVE-2-SYNTHESIS-SUMMARY.md
    └── TAKEOVER_ASSESSMENT_2026-04-16_WEDGE.md
```

## Per-phase content

Each phase directory contains:

- `PLAN.md` — the contract-complete plan written before execution.
  Claims, deliverables, acceptance tests, forbidden proxies, kill and
  defend criteria.
- `SUMMARY.md` — the post-execution summary with verdict, rationale,
  and contract-result fields.
- `harness.py` — the exact Python harness that produced the numbers.
- `summary.json` — machine-readable run output.
- Additional artifacts per experiment (CSV tables, hash tables, etc.).

## Reproducing the evidence

Each harness is self-contained. To reproduce any experiment:

```bash
# Install
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip

# Receipt surface only (tests the commercial wedge directly)
python -m pip install -e ".[dev]"
python -m pytest tests/test_receipt.py::test_cross_writer_independent_implementation_matches -v

# Fair-baseline comparison (archive-query falsification)
python -m pip install pyarrow
python docs/transparency/phase9_4_1_1_2_fair_baseline/harness.py

# Candidate B (video-LLM object memory; cross-writer test is the core)
python -m pip install pandas pyarrow fastparquet torch transformers
python docs/transparency/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory/harness.py --smoke

# Receipt-core provenance benchmark (commercial follow-up; no Phase 10 claim)
python -m pip install -e ".[dev]"
python scripts/receipt_core_benchmark.py

# Candidate C (primitive-semantic enrichment; tiny CPU job)
python -m pip install scikit-learn lightgbm torch transformers pillow
python docs/transparency/phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment/harness.py --smoke

# Candidate A (ROI sidecar; needs ffmpeg + libx265 + ultralytics + VIRAT clips)
python -m pip install numpy opencv-python-headless ultralytics torch
# (VIRAT clips from Kitware Release 2 must be cached under .cache/virat_subset/)
python docs/transparency/phase9_4_1_1_2_1_candidate_a_roi_sidecar/harness.py --smoke
```

## Research ledger

- [`VERDICT-SYNTHESIS.md`](research_ledger/VERDICT-SYNTHESIS.md) —
  verbatim aggregation of the three Wave-1 verdicts, cross-verdict
  attribution table, and the explicit "what IS claimed" / "what is NOT
  claimed" split.
- [`ranked_hypothesis_ladder.md`](research_ledger/ranked_hypothesis_ladder.md) —
  updated wedge ranking after the three parallel experiments landed,
  including R1 (selected wedge) through R8 (quarantined).
- [`WAVE-2-SYNTHESIS-SUMMARY.md`](research_ledger/WAVE-2-SYNTHESIS-SUMMARY.md) —
  Wave-2 synthesis summary in GPD SUMMARY.md format.
- [`TAKEOVER_ASSESSMENT_2026-04-16_WEDGE.md`](research_ledger/TAKEOVER_ASSESSMENT_2026-04-16_WEDGE.md) —
  fresh-eyes takeover assessment at the start of this investigation arc,
  with the ranked hypothesis ladder as it stood when the archive-query
  falsification result was first surfaced.

## Integrity discipline

- Nothing in this directory is hand-edited to improve the story.
- The `summary.json` files are produced by the checked-in harness
  scripts and have not been filtered or re-ordered.
- If a future commit changes any of these artifacts, the change should
  be backed by a new executable experiment under a new phase directory
  in the outer `.gpd/phases/` tree.
- Kill verdicts stay. They are why the defend verdict is trustworthy.
- Receipt-core pass artifacts do not upgrade the sovereign primitive-native
  gate; they only support the commercial receipt wedge.

## Where the outer project artifacts live

The outer-repo canonical location for these artifacts is the
`.gpd/phases/09.4.1.1.2*/` tree in the parent workspace. This
directory is a copy for self-contained repo distribution. The two
locations are expected to stay in sync; if they diverge, the outer-repo
tree is authoritative.
