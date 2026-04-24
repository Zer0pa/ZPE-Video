# The Commercial Wedge

Date: 2026-04-17
Status: narrow, defended, sovereign-gate-red

## What this document is

A plain-English statement of the one commercial wedge ZPE Video has
empirically defended, the reasoning for choosing it, and every wedge we
explicitly rejected on evidence. This document is a companion to
[`TRANSPARENCY_JOURNEY.md`](TRANSPARENCY_JOURNEY.md) (the full research
history) and [`ARCHITECTURE.md`](ARCHITECTURE.md) (how the artifact
implements this wedge).

## The wedge, in one line

**ZPE Video is the perception-receipt format for AI video pipelines: a
compact, deterministic binary record of what a detector + tracker saw in
a video that hashes identically across independent writer implementations
under default settings.**

## Why this matters to a buyer

Any organization that needs auditable, cross-platform, portable
"receipts" of what a vision model decided when it processed video has a
real problem today:

- **Parquet** diverges across writers (pyarrow vs fastparquet) under
  default settings — the same input produces different hashes.
- **JSON** diverges on key ordering, number formatting, and whitespace.
- **Pickle** is Python-only, non-portable, and insecure to load from
  untrusted sources.
- **Proprietary VMS formats** (Milestone, Verkada, Avigilon) are vendor-
  locked and not designed to be byte-exact re-implementable from a spec.
- **MCAP / rosbag2** carry timestamps and writer metadata that break
  byte-exactness across implementations.

The ZPE perception receipt does not diverge. The format is implementable
in <100 lines of any language with stdlib struct / zlib / crc32
primitives. Given identical detector + tracker output on the input side,
every conforming writer emits the **same bytes**, which means the same
SHA-256, which means the receipt is cryptographically quotable as a
stable reference to "what the model saw."

## Concrete customer shapes

### C2PA-style "AI perception credentials"

The C2PA Content Credentials 2.1 spec (April 2025) embeds cryptographically-
signed manifests of processing steps into media assets. Its assertions
about "what AI decisions were made about this content" are free-form
JSON referenced by hash. A ZPE receipt gives C2PA producers a tiny,
stable, binary artifact to point at: the receipt hash is stable across
platforms and implementations, so the credential remains valid even when
the assertion blob is regenerated downstream by a different pipeline.

The current receipt-core follow-up implements this as an external manifest
binding in `src/zpe_video/manifest.py`: the manifest stores receipt
SHA-256, byte length, wire magic/version, and caller content id, but does
not mutate or embed the receipt bytes. The manifest can be signed or
embedded by downstream C2PA tooling while the receipt blob remains the
stable authority surface.

### Regulated chain-of-custody for detector output

Police body-worn-camera workflows, legal discovery, and insurance-fraud
investigation increasingly need to disclose "what a person or vehicle
was doing at time T in this video" without disclosing the pixels (GDPR,
CCPA, NY S7023). The ZPE receipt is a legally-clean answer: sign it once,
distribute it widely, verify byte-for-byte on any receiver. The pixels
stay private; the track state is disclosable with integrity.

### Video-LLM / VideoRAG object-memory caches

Modern video-LLM pipelines (STORM, VideoAgent, VideoMem) re-extract
object-centric state on every query. This is the dominant cost. A cache
primitive that is small, fast to read, and cross-implementation
hash-stable lets two different cache implementations agree on "have we
seen this video before" by comparing the receipt hash only — without
trusting either implementation's Python internals.

### Cross-platform training-data provenance

ML teams that redistribute detection output as training data today either
hand out pickles (Python-only), custom Protocol Buffers (requires tooling
per consumer), or Parquet (diverges across writers). A ZPE receipt is a
cross-language byte-stable alternative that fits in a single file.

## Why this specifically, and not something bigger

We investigated several broader wedges. Every one of them failed under
evidence. Excerpt:

| Claimed wedge | Verdict | Phase | Falsifying evidence |
|---|---|---|---|
| Universal video-codec superiority | **Killed** | 08 | Lost to AV1, VVC, and learned baselines on mAP@50 at matched bitrate across both detector families. |
| Compass-8 / 8-primitive substrate as the product | **Retired** | pre-0.1.0 framing | This codec does not use Compass-8 directional encoding; see [`_reorientation/2026-04-17/NOVELTY_CARD.md`](_reorientation/2026-04-17/NOVELTY_CARD.md). The substrate was a research thesis, not the product surface. |
| Archive-query on box-state packet is ZPE-specific | **Killed** | 09.4.1.1.2 | A 60-line raw-struct+zlib beats the ZPE packet on BOTH storage (0.14x) and query latency (0.76x) with identical precision/recall. Archive-query is a sparse-metadata property, not a ZPE property. |
| ROI / foveated-guidance sidecar improves matched-bitrate mAP@50 | **Killed** | 09.4.1.1.2.1-A | Non-flat QP allocation lifts mAP@50 by +7.93%, but a spatially-uninformed mean-importance control lane produces the **identical** +7.93%. The lift is generic non-flat-QP, not packet-derived ROI. |
| State-layer enrichment (trajectory features) lifts precision | **Defend with caveat** | 09.4.1.1.2.1-C | Trajectory features lift noisy-proxy precision from 0.138 to 1.00. But the lift is state-layer, not ZPE-specific. Any sparse-metadata format can carry the same features. Kept as an engineering insight, not positioned as a ZPE wedge. |
| Cross-writer hash-stable AI-perception receipt | **Defend** | 09.4.1.1.2.1-B | ZPE hashes identically across two independent writer implementations under default settings. Parquet pyarrow vs fastparquet diverge. 5-8x smaller and 15x faster cache-read than default-Parquet. |

Every kill verdict is recorded in full at
[`TRANSPARENCY_JOURNEY.md`](TRANSPARENCY_JOURNEY.md), with the exact
experiment code, the machine-readable summary.json, and the scope
disclosure. No result has been hidden.

## What this wedge explicitly is not

- **Not** a claim about the Compass-8 / 8-primitive directional-encoding
  architecture. This codec does not use it. The Compass-8 substrate was
  a research thesis tested across prior phases and was not closed as a
  product goal for this codec; the v0.1.0 product is the perception
  receipt, which stands on its own.
- **Not** a compression claim. Modern codecs (AV1, VVC, learned) win on
  raw video. The receipt is a **companion** artifact, not a replacement.
- **Not** a claim that Parquet can never be stable. Parquet can be
  configured to enforce deterministic output (e.g., sorted columns,
  fixed encoding). The defended property is specifically about **default
  settings**. A buyer who will write the Parquet tuning config
  themselves does not need ZPE.
- **Not** a performance claim at the user-visible layer. In a video-LLM
  pipeline, LLM generation dominates end-to-end latency at ~97%. The
  receipt's speed advantage is a storage / memory property, not a
  response-time advantage.
- **Not** a universal video-perception pipeline. The receipt carries
  box + track state. Richer semantics (appearance hashes, class
  probabilities, attributes) are open directions, documented but not
  claimed to be ZPE-specific advantages.

## Where to go next

- Read [`TRANSPARENCY_JOURNEY.md`](TRANSPARENCY_JOURNEY.md) for the full
  falsification journey.
- Read [`WIRE_FORMAT.md`](WIRE_FORMAT.md) to re-implement the spec.
- Read [`QUICKSTART.md`](QUICKSTART.md) for the three-example onboarding.
- Check [`ARCHITECTURE.md`](ARCHITECTURE.md) for the package surface.
- Run `python scripts/receipt_core_benchmark.py` to regenerate the
  receipt-core provenance and manifest-binding benchmark.
- Every experiment and verdict is checked into this repo at
  [`docs/transparency/`](transparency/).

The bar is evidence, not intention. If this wedge is wrong, we want to
find out. If you can demonstrate a buyer for whom Parquet's default-
setting instability is not a real problem — or for whom an alternative
format already does this — file an issue. We will update this document.
