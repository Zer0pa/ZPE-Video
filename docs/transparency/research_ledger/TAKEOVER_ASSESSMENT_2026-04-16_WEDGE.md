# ZPE Video Takeover Assessment — 2026-04-16

Date: 2026-04-16
Workspace root: `/Users/Zer0pa/ZPE/ZPE Video`
Author: incoming investigator (fresh eyes)
Status: one honest bounded experiment executed; ranked hypothesis ladder
updated; next experiment proposal requires operator decision.

## Executive summary

The inherited "archive-query wedge" story does not survive the first fair
commercial baseline. I ran a bounded fair-baseline experiment that falsifies
both the ZPE packet's claim to a unique structural advantage and the prior
phase's claim that "richer packet semantics" is the right next move. The
sovereign Compass-8 primitive-native gate remains red, and none of the
previously-ranked wedges are currently defended on evidence.

What is new:

1. The 20.29x live speedup from phase 09.4.1.1.1 is a generic property of
   "sparse metadata vs reprocessed pixels", not a ZPE property.
2. The box stream itself does not carry the information needed to separate
   real facility-crossings from ghost-track flicker; no representation-level
   change can fix that. The blocker is operator engineering AND/OR state
   enrichment, not packet serialization.
3. The only prior-ranked line still unfalsified is the ROI/foveated sidecar
   reserve line.
4. An adjacent-domain scan finds one non-obvious candidate (video-LLM
   object-memory sidecar), but its central claim — determinism uniqueness —
   is also weakened by the same experiment.

## What I did

Mandated bootstrap reading (20 files in specified order) completed: read
the operator rules, the handover, the phase artifacts, the research-map
surfaces, the phase 09.4.1 audit / hypothesis matrix / PRD, the phase
09.4.1.1 proxy benchmark, and the phase 09.4.1.1.1 live benchmark and
source.

Two independent Opus-class agents spawned in parallel on non-overlapping
scopes:

- agent A (strict audit): independent verdict on whether the live
  archive-query baseline is honest and where the real leverage point sits.
- agent B (cross-domain scan): search for defensible wedges in adjacent
  domains with no loyalty to inherited framing.

Both returned (artifacts in agent outputs, summarized below).

One bounded experiment executed:

- `zpe_video_lab/python/phase9_4_1_1_2_fair_baseline_archive_query.py`
- Results: `zpe_video_lab/reports/phase9_4_1_1_2_fair_baseline_archive_query/summary.json`
- Phase report: `.gpd/phases/09.4.1.1.2-fair-baseline-archive-query-falsification/09.4.1.1.2-01-BENCHMARK-REPORT.md`
- Next-experiment proposal: `.gpd/phases/09.4.1.1.2-fair-baseline-archive-query-falsification/NEXT-EXPERIMENT-PROPOSAL.md`

## Key empirical findings

### 1. The ZPE packet format has no unique structural advantage

On the clean 3-clip / 180-frame / 4-event proxy surface with the naive
operator, at matched precision = recall = 1.0:

| Representation   | Storage (B) | Storage / ZPE | Query (ms) | Query / ZPE |
| ---------------- | ----------: | ------------: | ---------: | ----------: |
| ZPE packet       |       7,595 |         1.00x |       2.38 |       1.00x |
| raw struct+zlib  |       1,077 |         0.14x |       1.81 |       0.76x |
| json+gzip        |       1,583 |         0.21x |       2.27 |       0.99x |
| sqlite           |      73,728 |         9.71x |       4.18 |       1.76x |
| parquet          |       8,431 |         1.11x |       6.57 |       2.76x |

Raw struct + zlib (the same per-frame struct without the delta encoding)
strictly dominates the ZPE packet on BOTH storage (7x smaller) AND query
latency (0.76x) with identical semantics. JSON + gzip does the same (5x
smaller storage, comparable latency). The ZPE packet's delta encoding
actively HURTS compression because zlib already exploits cross-frame
repetition; the delta-encoding metadata (mode byte + signed deltas +
re-serialized dimensions) is pure overhead.

### 2. The operator is the precision blocker, not the representation

On the noisy 3-clip surface (4 real GT events plus 30 ghost tracks that
drift near the portal), all 5 representations with the naive operator
produce:

- precision = 0.13793103448275862
- recall = 1.0
- 29 predicted / 4 matched / 4 ground-truth

Identical to 15 significant figures. The information needed to raise
precision is not in the box stream. No delta encoding, columnar
reshuffling, or indexing of the SAME boxes changes the outcome.

### 3. The prior phase's "20.29x speedup" is not wedge evidence

Phase 09.4.1.1.1 compared packet-parse against raw-pixel-decode plus fresh
background-subtraction plus fresh IoU tracking. That baseline is not any
real archive-query incumbent. A Parquet index, SQLite index, or plain
gzipped JSON sidecar persisted at ingest would match or beat the packet on
latency at a fraction of the ZPE packet's storage. The "wedge" was a
property of "sparse metadata" as a category, not of the ZPE packet
specifically.

## Updated ranked hypothesis ladder

Old ranking (phase 09.4.1):

1. Searchable primitive event/state index — primary
2. ROI / foveated guidance sidecar — reserve
3. Product-shaped detector scheduling — conditional
4. Object-centric primitive token stream — enabling
5. World-model branch — quarantined

Updated ranking on 2026-04-16 evidence:

| Rank | Hypothesis | Status | Evidence | Kill criterion |
| ---- | --- | --- | --- | --- |
| R1 | ROI/foveated guidance sidecar (matched-bitrate detector utility) | unfalsified, untested | strong adjacent-science support; no live benchmark yet | fail matched-bitrate mAP@50 uplift on held-out at any defended bitrate |
| R2 | Richer state-layer enrichment with appearance or trajectory-motif tokens | unfalsified, untested | operator-blocker finding in 09.4.1.1.2 suggests state enrichment may help where serialization cannot | classifier with rich track features fails to move noisy-proxy precision to >= 0.5 |
| R3 | Video-LLM object-memory sidecar (agent B pivot) | weakened but not dead | determinism property is empirically not unique to ZPE, so value must come from something else | fail to produce >= 2x tokens/latency win over Parquet on a bounded VideoQA benchmark |
| R4 | Searchable primitive event/state index on box-state packet | **FALSIFIED as ZPE-specific** | 09.4.1.1.2 — commodity formats match or beat ZPE on the same workload | already dead; do not reopen |
| R5 | Selective-escalation detector scheduler | bounded, retired | 09.07 / 09.09 land bounded | do not reopen without new partner surface |
| R6 | Commodity fixed-camera analytics | retired | 09.3.2 closed as retire_surface | do not reopen |
| R7 | World-model / universe kernel | quarantined | speculative | do not reopen without bounded-domain utility |

## What the prior narrative was missing

Three systematic blindspots across the inherited framing:

1. The archive-query benchmark compared against a strawman baseline. Every
   real VMS persists tracks at ingest; none re-runs detection at query time.
   The 20.29x speedup was therefore an apples-to-oranges comparison that
   exaggerated the apparent value.

2. The narrative conflated "packet stores sparse state" with "packet is
   uniquely compact and queryable." The first is true. The second is
   falsified. Any sparse-metadata format achieves the same economics.

3. The recommendation to "upgrade packet semantics to attack false
   positives" was proposed without testing whether the SAME box stream in
   any other format produces the same false positives. It does. The FP
   cloud is operator-induced on a box stream that lacks appearance or
   class information; no serialization-level change can help.

## Sovereign gate status (unchanged)

The Compass-8 primitive-native acceptance gate remains red. Phase
09.4.1.1.2 does not touch the sovereign gate and does not close any
primitive-native contract. The gate is the governing objective; nothing
from this phase promotes to any closure claim.

## Operator rules compliance check

- Never optimize for a narratable win instead of the governing objective —
  respected; the falsification result is a truth output, not a story fix.
- Never let local improvements substitute for the authority metric —
  respected; authority metric still red and unchanged.
- Never close early once something looks defensible — respected;
  experiment executed before any narrative commitment.
- Never reward hack — respected; no thresholds tuned on target.
- Always treat the top acceptance gate as sovereign — respected; this
  phase's verdict explicitly subordinates itself.
- Always treat any regression on the authority metric as failure — no
  regression claim; authority metric untouched.
- Avoid toy/demo behavior — respected; experiment is repeatable, bounded,
  falsifiable.
- Do not touch the external GitHub remote — respected; no push, no pull,
  no gh operations.

## Stop condition

I have executed one honest next step (09.4.1.1.2) and recorded its
result. The result is a hard evidence-backed argument that:

- the archive-query wedge as ZPE-specific is falsified, AND
- the next best move is NOT obvious enough to execute without the
  operator selecting among candidates A / B / C in
  `NEXT-EXPERIMENT-PROPOSAL.md`.

I am stopping here. The operator's choice of next candidate will
determine the next bounded experiment.

## Files produced / modified by this takeover

- `zpe_video_lab/python/phase9_4_1_1_2_fair_baseline_archive_query.py` — new experiment script
- `zpe_video_lab/reports/phase9_4_1_1_2_fair_baseline_archive_query/summary.json` — result data
- `.gpd/phases/09.4.1.1.2-fair-baseline-archive-query-falsification/09.4.1.1.2-01-BENCHMARK-REPORT.md` — phase report
- `.gpd/phases/09.4.1.1.2-fair-baseline-archive-query-falsification/NEXT-EXPERIMENT-PROPOSAL.md` — candidates with kill criteria
- `TAKEOVER_ASSESSMENT_2026-04-16_WEDGE.md` — this document
- `.gpd/STATE.md` — updated below
- `.gpd/ROADMAP.md` — updated below (new phase row)

No changes to the external GitHub remote. No primitive-native closure
claims. No new Phase 10 activity.
