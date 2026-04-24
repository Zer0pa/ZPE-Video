# Phase 09.4.1.1.2 Benchmark Report — Fair-Baseline Archive-Query Falsification

## Question

Does the ZPE packet format have a structural advantage over commodity
sparse-metadata storage formats (raw struct + zlib, SQLite, Parquet, JSON + gzip)
on the same archive-query workload, or is the "20.29x live speedup" from
phase 09.4.1.1.1 trivially explained by "parse sparse metadata vs decode raw
pixels + re-run CV at query time"?

## Why this phase exists

Phase 09.4.1.1.1 compared the packet path against a "full replay path" that
re-runs background subtraction + connected components + IoU tracking on raw
frames every time a query issues. No archive-query incumbent on earth does
that. A fair commercial baseline persists tracks at ingest and queries the
persisted state. The prior narrative concluded "richer packet semantics" was
the next move to attack the 0.0259 precision; that conclusion was reached
without testing whether the SAME box stream in any commodity format produces
the same precision cloud. This phase runs that missing test.

## Method

Executable artifact:
`zpe_video_lab/python/phase9_4_1_1_2_fair_baseline_archive_query.py`

Five representations stored lossless w.r.t. the tracked box stream:

1. `zpe_packet` — zlib-compressed, delta-encoded per-frame struct (same format
   used in the phase 09.4.1.1.1 pod harness)
2. `raw_struct_zlib` — same per-frame struct layout with NO delta encoding,
   single zlib pass over the whole buffer
3. `sqlite` — indexed relational table `(clip, frame, track, x, y, w, h, label)`
4. `parquet` — columnar with snappy compression
5. `json_gzip` — verbose JSON + gzip

Two operators:

- `naive` — center-of-box inside portal_box for `>= 4` consecutive frames
  (this is the phase 09.4.1.1.1 operator)
- `hardened` — shrink portal to inner 40%, require `>= 8` frames visible
  outside portal before entry, require `>= 15 px` displacement along motion
  axis while inside

Two surfaces:

- `proxy_clean` — 3 synthetic clips, 60 frames each, clean tracks
  (4 GT events)
- `proxy_noisy` — same clips + 10 short-lived ghost tracks per clip that
  briefly drift through the portal (simulates the live false-positive cloud
  seen at `precision = 0.0259`, `734 predicted / 19 GT` in 09.4.1.1.1)

Metrics per (representation, operator):
storage bytes, ingest latency (median of 5 repeats), query latency
(median of 11 repeats), precision, recall, predicted events, matched events,
mean temporal IoU.

## Results

All numbers from
`zpe_video_lab/reports/phase9_4_1_1_2_fair_baseline_archive_query/summary.json`.

### Clean surface, naive operator (precision/recall = 1.0 across all 5 representations)

| Representation     | Storage (B) | Storage / ZPE | Query (ms) | Query / ZPE | Ingest (ms) | Ingest / ZPE |
| ------------------ | ----------: | ------------: | ---------: | ----------: | ----------: | -----------: |
| `zpe_packet`       |       7,595 |         1.00x |       2.38 |       1.00x |        1.99 |        1.00x |
| `raw_struct_zlib`  |       1,077 |     **0.14x** |       1.81 |   **0.76x** |        0.76 |    **0.36x** |
| `sqlite`           |      73,728 |         9.71x |       4.18 |       1.76x |        9.44 |        3.29x |
| `parquet`          |       8,431 |         1.11x |       6.57 |       2.76x |        2.01 |        1.19x |
| `json_gzip`        |       1,583 |     **0.21x** |       2.27 |   **0.99x** |        1.32 |    **0.65x** |

### Noisy surface, naive operator (precision = 0.138, recall = 1.0, 29 predicted / 4 GT across ALL 5)

| Representation     | Storage (B) | Storage / ZPE | Query (ms) | Query / ZPE | Precision |
| ------------------ | ----------: | ------------: | ---------: | ----------: | --------: |
| `zpe_packet`       |       9,367 |         1.00x |       3.46 |       1.00x |   0.13793 |
| `raw_struct_zlib`  |       1,885 |     **0.20x** |       2.64 |       0.76x |   0.13793 |
| `sqlite`           |      81,920 |         8.75x |       5.73 |       1.66x |   0.13793 |
| `parquet`          |      10,161 |         1.08x |       7.99 |       2.31x |   0.13793 |
| `json_gzip`        |       2,388 |     **0.25x** |       3.45 |       1.00x |   0.13793 |

### Hardened operator

The hardened operator as configured (`min_outside_frames_before >= 8`, inner
40% portal, min 15 px displacement) is miscalibrated for this specific proxy
where real tracks begin at frame 0 and move directly toward the portal. It
drops precision and recall to 0 on both surfaces for all 5 representations
equally. This is a calibration defect in the operator design, not an
evidence defect. The operator-as-blocker thesis is established by the
**identical naive-operator precision** across representations, not by
operator ablation alone.

## Interpretation

Three claims are directly measured.

### 1. The ZPE packet has NO unique structural advantage

`raw_struct_zlib` strictly dominates `zpe_packet` on BOTH storage (0.14x) AND
query latency (0.76x) with **identical precision and recall**. `json_gzip`
also strictly dominates on both axes (0.21x storage, 0.99x query latency).

The ZPE packet's delta encoding across frames actively HURTS compression
relative to single-pass zlib over raw struct, because zlib already exploits
cross-frame repetition in the raw bytes, and the delta-encoding metadata
(mode byte + signed deltas + re-serialized dimensions) adds overhead that the
encoder cannot recover.

### 2. The operator is the blocker, not the representation

On the noisy surface with the naive operator, all 5 representations produce:
- `events_precision = 0.13793103448275862`
- `events_recall = 1.0`
- `29 predicted events`
- `4 matched events`
- `4 ground-truth events`

This equality is exact to 15 significant figures. The information needed to
discriminate real entering/exiting events from ghost-track flicker is not in
the box stream at all — no delta encoding, columnar reshuffling, indexing, or
symbolic packing of the SAME boxes can move precision.

### 3. The "20.29x speedup" claim from 09.4.1.1.1 is not wedge evidence

The 09.4.1.1.1 baseline was raw-pixel decode + fresh background subtraction +
fresh IoU tracking at every query. The "20.29x" is the ratio of that path
against parsing 832 KB of sparse metadata. Any of the 5 representations in
this phase would produce a similar speedup against the same pixel-reprocessing
strawman, because ALL sparse-metadata formats parse in ~ms. This is not a ZPE
property; it is a property of "sparse metadata vs reprocessed pixels".

## Verdict

`zpe_packet_beaten_by_commodity_format`

The archive-query wedge as currently framed is **FALSIFIED** as a
ZPE-specific advantage. The prior phase's "richer packet semantics will
attack false positives" thesis is also falsified: representation is proven
irrelevant to precision under this operator.

## Implications for the program

### For Phase 09.4.1.1.1's "bounded_signal_only" result

That result stands as *measured* but should be re-interpreted: the live
economics delta was a property of storing sparse metadata at all, not of
storing it in the ZPE packet format. A Parquet or JSON sidecar would have
shown the same 0.0259 precision, same recall = 1.0, and similar speedup vs
the full-replay strawman.

### For the archive-query wedge ranking

Archive query should be demoted or removed from the ranked wedge list as a
ZPE-specific direction. It survives only as a commodity-metadata workload
in which ZPE has no unique position.

### For the Compass-8 primitive-native sovereign gate

This phase does NOT touch the sovereign primitive-native gate. That gate
remains red. But this phase does rule out one path to the gate: changing
the box-state packet's SERIALIZATION will not produce a wedge. If a
primitive-native advantage exists at all, it must live in the SEMANTICS
carried by the packet (appearance, class, trajectory motifs, geometry), not
in the packet format itself.

### For operator engineering as an alternative

The naive operator produces `precision = 0.138` with `29 predicted / 4 GT` on
a surface where 10 ghost tracks / clip were added. That is a **2.5x FP/GT
ratio** on noisy proxy vs the live surface's `38.6x FP/GT ratio`, suggesting
the proxy noise model is mild compared to real VIRAT noise. Operator
engineering (spatial gating, direction-consistent trajectory filters, trained
classifiers on track features) could plausibly move precision by 5-20x. But
this work is representation-agnostic: it would help parquet, sqlite, and JSON
equally. It is NOT a ZPE wedge.

## Falsifiers for this verdict

A later phase could overturn this finding by showing:
- a representation-level property ZPE uniquely provides (e.g.,
  bit-exact-across-writers determinism, O(1) random-access without sequential
  decode, something else) that a buyer specifically values over what commodity
  formats provide, AND
- a benchmark in which that unique property maps to measurable buyer value
  that commodity formats cannot reach.

No such property is established in this phase. The next honest move is
either to identify and test such a property directly, or to retire the
archive-query line entirely.

## Next required work

See `NEXT-EXPERIMENT-PROPOSAL.md` in this phase directory for the
concrete bounded next step.
