# The Transparency Journey

Date: 2026-04-17
Status: sovereign-gate-red, narrow-wedge-defended

## Why this document exists

We do radical transparency. Every falsification, every dead branch,
every "we thought this would work and it didn't" verdict is checked
into this repo alongside the narrow thing we ended up keeping.

This document is the path someone external can walk to verify that:

1. We did the work honestly.
2. We killed our own bigger claims on evidence.
3. The one wedge we chose — the perception receipt — is the one
   remaining signal we could not kill, and we show exactly what it is
   and isn't.

If you are evaluating us — as a partner, an auditor, an investor, a
buyer — read this before the pitch. The pitch is in
[`WEDGE.md`](WEDGE.md); this is the evidence behind it.

## Executive summary of the journey

We started with an ambitious research thesis: a primitive-native
Compass-8 video substrate (see [`PROJECT.md`](../../.gpd/PROJECT.md))
that we hoped would deliver a decisive machine-video advantage over
incumbents on a defended benchmark. This thesis was research-phase
framing, not a product claim. Over ~24 phases of research, we:

- Built executable prototypes under strict evidence discipline.
- Measured against real detector-honest benchmarks.
- Falsified our own codec-superiority claims when the evidence said so.
- Reframed repeatedly as narrow wedges revealed themselves — and
  falsified each narrow wedge in turn when fair commercial baselines
  showed the signal was generic, not ZPE-specific.
- Ended with exactly one narrow surviving wedge (perception receipts,
  Candidate B of Phase 09.4.1.1.2.1) and two dead ones (Candidate A ROI
  sidecar, Candidate C state-layer enrichment — the latter defended as
  an engineering insight but explicitly not a ZPE wedge).

The Compass-8 primitive-native substrate thesis was **tested and not
closed** as a product goal for this codec. v0.1.0 ships the perception-
receipt wedge, which does not use Compass-8 directional encoding. The
research thesis is preserved as historical context; it is not a current
product claim.

## Phase-by-phase verdict ledger

Every phase's full record is under
[`.gpd/phases/`](../../.gpd/phases/) in the outer research tree. The
below is a distilled verdict ledger.

| Phase | Title | Verdict | What it actually proved |
|---|---|---|---|
| 01 | Primitive Substrate Recovery | complete | The Compass-8 thesis named; first artifact-class contract. |
| 02 | Primitive-Native Prototype | superseded | Harness real, representation below H2 floor. |
| 02.1 | Representation Quality Recovery | complete | Grouped ROI recovers 0.697 detector retention at 0.197 bitrate ratio; H2 gate red. |
| 02.2 | Rate-Efficiency Recovery | complete | Best grouped one-thumbnail point clears bitrate, fails detector by a wide margin. |
| 02.2.1 | Structured Interior Field Recovery | complete | Richer structured fields only tie 02.2 at worse bitrate; grouped low-rate line exhausted. |
| 02.2.1.1 | Artifact-Class Bifurcation | complete | Grouped low-rate transport is dead; next branch is a detector-facing augmentor. |
| 02.2.1.1.1 | Detector-Facing Augmentor Recovery | complete | `bbox_context_q30` at 0.851 retention / 0.180 bitrate clears the local gate. |
| 3 | Benchmark Wedge and Falsification | complete | **First defended H.265 wedge**: `mAP@50 = 0.600` at 1.70 MB vs matched-rate H.265 0.571. Inside `crf=38/39` bracket only. |
| 4 | Proof Packaging and Product Decision | complete | Lane promoted as detector-facing augmentor/kernel only; broad codec claims barred. |
| 5 | Interior Byte Barrier Reduction | complete | Quality-only sweep below q30 fails; q20 frontier at 1.37 MB, +4.77% (below 5% rule). |
| 6 | Detector Shape-Bias Recovery | complete | Adapted detector at fixed q20 clears the local rule by +6.05%. |
| 7 | Evidence Freeze and Second-Detector Verification | complete | Frozen RT-DETR-L also clears at q20; replay bundle frozen at tagged nested commit. |
| 8 | Comparator Expansion Against AV1, VVC, Learned | **failed** | **Killed universal-codec claim**: AV1 loses on both detectors; learned hyperprior loses on both; VVC also fails. Wedge is H.265-only. |
| 9 | Architectural Purification and Contour-Primary Recovery | bounded | 9 sub-plans; contour-primary substrate surfaces found but every byte-gate exceeded. Subordinate wedge bounded. |
| 09.1 | Seedance Subchannel Factorization | bounded | Internal-heterogeneity hypothesis real; persistence carrier loses to temporal-only on hard cuts. |
| 09.2 | Primitive-Native Layered Control-Plane | bounded | Layered scorer reaches 39.9% / 39.1% suppression at >=95% retention; no near-half regime. |
| 09.3 | Narrow Event-Annotated Surveillance | bounded | Sparse facility-event VIRAT: 14.67% suppression at 100% recall. |
| 09.3.1 | Portal-Anchored Primitive Consumer | bounded | 34.38% suppression at 96.30% recall; LOOCV unstable. |
| 09.3.2 | Portal-Local State Machine | **retired** | Best point 37.50% suppression; one clip at 5/6 recall; surface retired. |
| 09.4 | Live Repo Hardening | public-shell-hardened | Nested repo shell truthful; science wedge still red. |
| 09.4.1 | Ground-State Wedge Audit | direction-only | Re-ranked: archive query primary, ROI sidecar reserve. |
| 09.4.1.1 | Event-State Index Benchmark (proxy) | proxy-only | Mechanics prove; live VIRAT absent; no defended wedge. |
| 09.4.1.1.1 | Pod-Backed Live Archive-Query | bounded-signal-only | Packet is 20.29x faster than full replay, scans 0.11% of bytes, but precision only 0.0259. Blocker is specificity. |
| **09.4.1.1.2** | **Fair-Baseline Archive-Query Falsification** | **killed** | **Raw struct+zlib strictly dominates the ZPE packet on storage (0.14x) AND query latency (0.76x) with identical precision/recall. Archive-query wedge is NOT ZPE-specific; operator is the blocker, not the representation.** |
| **09.4.1.1.2.1-A** | **ROI/foveated sidecar** | **killed** | +7.93% matched-bitrate mAP lift, but mean-importance control produces identical +7.93%. Lift is generic non-flat-QP, not packet-derived. |
| **09.4.1.1.2.1-B** | **Video-LLM object-memory** | **defend** | **ZPE cross-writer hash-stable under defaults; Parquet pyarrow vs fastparquet diverge. 5-8x smaller storage, 15x faster cache-read than default-Parquet. End-to-end user latency dominated by LLM generation.** |
| 09.4.1.1.2.1-C | Primitive-semantic enrichment | defend-with-caveat | Trajectory features lift precision 0.138 → 1.0 on noisy proxy; state-layer is the lever, not ZPE. Not promoted as a ZPE-specific wedge. |

## The big reframe from 09.4.1.1.2 onward

The most important moment of the journey was Phase 09.4.1.1.2. Before
that phase, the project had been framing "archive query with 20x speedup
vs full replay" as an emerging commercial direction. The Phase 09.4.1.1.2
experiment asked a harder question:

> If we compare the ZPE packet against the baseline a real VMS buyer
> would use — a sparse-metadata sidecar like Parquet, SQLite, JSON+gzip,
> or a raw zlib-wrapped struct — does ZPE still win?

It does not. A 60-line raw-struct+zlib beats ZPE on storage (7x smaller)
AND query latency (1.3x faster) with identical precision/recall. The
"20x speedup" was a speedup against **re-running detection from pixels**
— a strawman baseline that no archive-query product does.

That falsification is preserved at
[`docs/transparency/phase9_4_1_1_2_fair_baseline_archive_query/`](transparency/)
and [`.gpd/phases/09.4.1.1.2-fair-baseline-archive-query-falsification/`](../../.gpd/phases/09.4.1.1.2-fair-baseline-archive-query-falsification/).

## The three parallel experiments that narrowed the wedge

With the archive-query story killed, we opened Phase 09.4.1.1.2.1 as
three **parallel, independent** bounded wedge experiments — with no
pre-selection and explicit kill criteria per candidate.

### Candidate A — ROI / foveated guidance sidecar (killed)

- **Hypothesis**: packet-derived ROI map used as H.265 bitrate-allocation
  prior lifts matched-bitrate mAP@50 on machine-vision tasks.
- **Result**: ROI lane gives +7.93% lift over flat H.265. So does the
  spatially-uninformed mean-importance control lane. Identical numbers.
- **Why killed**: the lift is a property of "non-flat QP allocation"
  on libx265 temporal zones, not a property of the packet-derived
  spatial shape. Any non-flat prior would produce the same gain.
- Full record: [`docs/transparency/phase9_4_1_1_2_1_candidate_a_roi_sidecar/`](transparency/)

### Candidate B — Video-LLM object-memory sidecar (defend)

- **Hypothesis**: the ZPE packet uniquely serves as a hash-stable
  object-memory cache for video-LLM pipelines.
- **Result**: ZPE hashes identically across two independent writer
  implementations under default settings. Parquet pyarrow vs
  fastparquet diverge on the same input under defaults. ZPE is 5-8x
  smaller and 15x faster cache-read. Answer accuracy across `none`,
  `Parquet`, `ZPE` strategies is identical (0.40 / 0.40 / 0.40).
- **Why defended**: cross-writer hash stability under defaults is a
  structural property Parquet does not have. The alt-defend branch of
  the plan contract fires cleanly. This is the narrow wedge.
- **What we did not claim**: that this is a user-visible speed win
  (LLM generation dominates end-to-end latency); that Parquet cannot be
  configured to match (it can, under non-default patterns); that this
  closes the sovereign Compass-8 gate (it does not).
- Full record: [`docs/transparency/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory/`](transparency/)

### Candidate C — Primitive-semantic enrichment (defend with caveat)

- **Hypothesis**: richer per-track state (appearance + trajectory) can
  lift operator precision where box-state-only cannot.
- **Result**: trajectory features alone lift noisy-proxy precision from
  0.138 to 1.00 at recall=1.00 under 5-fold CV with classifier-family
  agreement.
- **Why defended, with caveat**: the result is real but the wedge is in
  the **state layer** (attributes you attach per track), not in the ZPE
  format. Any sparse-metadata format can carry the same features. Sample
  size is small (4 positives). We keep this as an engineering insight
  but explicitly **do not** promote it as a ZPE-specific wedge.
- Full record: [`docs/transparency/phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment/`](transparency/)

## The chosen wedge, honestly

Only Candidate B produced a signal where the **ZPE packet itself**, and
not a category-level property of sparse metadata, is the thing doing the
work. That single finding is the commercial direction (see
[`WEDGE.md`](WEDGE.md)).

Candidate B is defended under the alt-defend branch of its plan
contract, which explicitly measured:

- Cross-writer hash stability (pyarrow ↔ fastparquet; ZPE repo ↔
  independent reference implementation)
- Storage bytes per video
- Cache-read latency per query
- End-to-end latency per query
- Answer accuracy parity across caching strategies
- LLM determinism spot-check

All six checks passed for ZPE. Only storage and cache-read passed for
Parquet; cross-writer hash stability failed under defaults.

## What we will not do

- Narrate a commercial win across ZPE Video as a class. Only the
  perception-receipt surface is defended.
- Claim the Compass-8 substrate is "almost there." It is a research
  thesis that was tested and not closed; v0.1.0 ships a different
  product (the perception receipt) that does not depend on Compass-8.
- Remove the kill verdicts from the repo. They stay, because they are
  part of why the defended wedge is trustworthy.
- Tune any single number post-hoc to improve the apparent story. The
  Wave-1 verdict aggregator (Plan 04) reads all three summary.json
  files verbatim, without filter or editorial correction, and writes
  them into the synthesis.

## How to verify

Every claim above has executable evidence:

- **Experiment harnesses** at `zpe_video_lab/python/phase9_4_1_1_2_*`
  and `zpe_video_lab/python/phase9_4_1_1_2_1_candidate_{a,b,c}_*`
- **Machine-readable summary.json** at
  `zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_{a,b,c}_*/summary.json`
- **GPD-ledger PLAN.md and SUMMARY.md** per plan under
  `.gpd/phases/09.4.1.1.2.1-parallel-bounded-wedge-discovery-.../`
- **Wave-2 verdict synthesis** at
  `.gpd/phases/09.4.1.1.2.1-.../VERDICT-SYNTHESIS.md`
- **Ranked hypothesis ladder** at
  `.gpd/phases/09.4.1.1.2.1-.../ranked_hypothesis_ladder.md`
- **Fresh-eyes takeover assessment** at
  `TAKEOVER_ASSESSMENT_2026-04-16_WEDGE.md` (workspace root)

Anyone who wants to re-run the decisive experiment from scratch can do
so with the scripts and proxy corpora documented in those artifacts.
The noisy proxy for Candidate C is a 29-sample deterministic
construction seeded at `seed=42`; the Candidate B benchmark is a
4-video deterministic subset with synthetic YOLOv8-shaped detector
output; Candidate A runs on 3 real VIRAT clips from the public Kitware
release.

Nothing has been hidden. If you find a claim you cannot reproduce, file
an issue.
