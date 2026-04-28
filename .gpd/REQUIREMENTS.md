# ZPE-Video — v0.1.0 Wedge Requirements

**Lane:** ZPE-Video
**Target:** v0.1.0 perception-receipt wedge
**GPD retrofit date:** 2026-04-28

## What Success Looks Like

Success for the v0.1.0 wedge is a **defended, cross-writer bit-exact
AI-perception receipt format** that satisfies all of the following gates.

### Gate 1 — Cross-Writer Bit-Exactness

Two conforming writer implementations, written independently in the same
language from the wire format spec (`docs/WIRE_FORMAT.md`), must produce
byte-identical output on byte-identical `{box_id, label, x, y, w, h}`
input under default settings.

Measured by:
`tests/test_receipt.py::test_cross_writer_independent_implementation_matches`

**Status:** PASS (Phase 09.4.1.1.2.1-B)

### Gate 2 — Parquet Divergence Under Default Settings

The default-settings Parquet baseline (pyarrow vs fastparquet) must
diverge in hash under the same conditions where ZPE converges.

Measured by: Phase 09.4.1.1.2.1-B experiment; documented in transparency bundle.

**Status:** PASS (pyarrow vs fastparquet hashes diverge; ZPE hashes match)

### Gate 3 — Storage and Cache-Read Economics

On a bounded VideoQA subset, the ZPE receipt must be meaningfully smaller
and faster to cache-read than default-Parquet.

Measured by:
`docs/transparency/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory/summary.json`

**Status:** PASS (5-8x smaller, 15x faster cache-read on bounded VideoQA subset)

### Gate 4 — Per-Frame Integrity

Every frame payload must carry a CRC32 that is verified on read.
Corruption must raise a typed exception with a specific failure site.

Measured by:
`tests/test_receipt.py` (per-failure tests for all nine documented failure modes)

**Status:** PASS

### Gate 5 — Spec Re-Implementability

The wire format must be re-implementable in under 100 lines of any
language with stdlib struct / zlib / crc32 primitives.

Measured by: the hand-rolled from-spec encoder in the conformance test.

**Status:** PASS (hand-rolled encoder in test file is ~40 lines)

### Gate 6 — External Manifest Binding (C2PA)

A manifest binding must store receipt SHA-256, byte length, wire
magic/version, and caller content id without mutating or embedding the
receipt bytes. This enables C2PA downstream signing.

Measured by:
`tests/test_manifest.py` (7 tests)
`src/zpe_video/manifest.py`

**Status:** PASS

## Sovereign Gate (Not Claimed Closed)

The broader sovereign gate — `>= 50%` detector-invocation suppression at
`>= 95%` retained utility — was the historical research gate for the
05/09 detector-suppression wedge family. It was NOT closed by any phase in
the 09 series (all phases in 09-09 through 09.3.2 are `bounded_signal_only`
or `retire_surface`).

The v0.1.0 product wedge is the **perception-receipt format**, not the
detector-suppression line. The sovereign gate above does not apply to the
receipt wedge; it applies only to the retired detector-routing research.

## What Is Explicitly Not Required for v0.1.0

- Universal video-codec superiority (killed in Phase 08)
- Archive-query ZPE-specificity (killed in Phase 09.4.1.1.2)
- Compass-8 / 8-primitive substrate (not used by this codec)
- ROI / foveated sidecar improvement (killed in Phase 09.4.1.1.2.1-A)
- Phase 10 readiness or sovereign primitive-native closure
