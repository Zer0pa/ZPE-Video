# ZPE-Video Novelty Card

**Product:** ZPE-Video
**Domain:** Per-frame detector-and-tracker output for AI video pipelines — a compact, self-contained binary record of "what a detector + tracker saw in this video."
**What we sell:** A perception-receipt format for AI video pipelines: given identical per-frame box + track state, every conforming writer in any language emits byte-identical output under default settings, so the SHA-256 of a receipt is a stable cryptographic reference to "what the model saw." Cross-platform, zero-runtime-dep, integrity-checked, sub-millisecond reads.

## Novel contributions

1. **Cross-writer-stable perception-receipt wire format.** A deterministic binary envelope for per-frame `{box_id, label, x, y, w, h}` with intra-frame canonical sort order, frame-level delta encoding against the previous frame's canonical-sort state, fixed `zlib.compress(..., level=9)` framing, a 32-bit CRC over each compressed frame payload, and a 15-byte header with explicit `WIRE_MAGIC` + `WIRE_VERSION` + dimensions + a 32-bit opaque seed. Code: [`src/zpe_video/receipt.py:96-106`](../../src/zpe_video/receipt.py) (magic, version, header struct, frame struct); [`src/zpe_video/receipt.py:242-281`](../../src/zpe_video/receipt.py) (`encode_receipt`); [`src/zpe_video/receipt.py:427-468`](../../src/zpe_video/receipt.py) (`_encode_frame_payload`). Nearest prior art: Parquet (pyarrow / fastparquet), MCAP, rosbag2, MISB ST 0903 VMTI, ONVIF Profile M, plain JSON + gzip. What is genuinely new: cross-writer bit-exactness under **default** writer settings — no format above is byte-exact across two independent writer implementations under defaults (Parquet pyarrow vs fastparquet hashes diverge; MCAP chunk ordering and write-timestamp inclusion break hashes; JSON key-order, whitespace, and numeric formatting diverge across libraries; ONVIF is XML-over-RTSP and not designed for byte exactness). The receipt's explicit no-timestamp / no-writer-metadata discipline combined with sorted iteration and fixed zlib level produces a determinism property no incumbent format offers out-of-the-box.

2. **Independent cross-writer equivalence as a load-bearing conformance test.** The spec is normative with respect to byte output, not just data recovery. A conforming implementation must reproduce the library's bytes on the same input. The test file hand-rolls a minimal from-spec encoder and asserts byte-identity. Code: [`tests/test_receipt.py:127-165`](../../tests/test_receipt.py) (`test_cross_writer_independent_implementation_matches`). Nearest prior art: general determinism tests in codec libraries (typically compare hashes across runs of the same binary, not across two independent implementations). What is genuinely new: a codec whose conformance test re-implements its own wire format in the test and asserts agreement. This turns byte exactness into a commitment, not a coincidence.

3. **Per-frame CRC32 integrity with non-silent failure discipline.** Each compressed frame payload is CRC32'd before write and verified on read; mismatch raises a typed `ReceiptCorrupted` exception with specific failure sites (bad magic, unsupported version, truncated frame header, truncated frame payload, CRC mismatch, trailing bytes, truncated box header, truncated absolute/delta body, unknown mode byte, delta without prior box). Code: [`src/zpe_video/receipt.py:118`](../../src/zpe_video/receipt.py) (error class); [`src/zpe_video/receipt.py:284-359`](../../src/zpe_video/receipt.py) (`decode_receipt` with nine distinct failure sites); [`tests/test_receipt.py:190-226`](../../tests/test_receipt.py) (per-failure tests). Nearest prior art: zlib CRC in gzip containers, Parquet column-chunk CRCs when enabled. What is genuinely new: a metadata format where CRC protection is mandatory per frame at default settings and every documented failure site is pinned by a test that asserts a specific exception type and message fragment.

4. **Delta-encoded per-track state with absolute-mode fallback and signed-16 overflow as an error, not a silent truncation.** Each box's subsequent observation encodes `(dx, dy)` as signed 16-bit integers against the previous frame's sorted-canonical state; if a delta would overflow, encoding raises `ValueError`, requiring the caller to assign a new `box_id` rather than accept silent truncation. Code: [`src/zpe_video/receipt.py:427-468`](../../src/zpe_video/receipt.py) (`_encode_frame_payload`). Nearest prior art: rosbag2 / MCAP delta encoding of message fields; MPEG video motion-vector encoding. What is genuinely new: the explicit overflow-is-an-error contract + the sorted-canonical previous state as the reference frame (rather than an arbitrary prior frame) — both combine to make the delta encoding hash-stable.

## Standard techniques used (explicit, not novel)

- `zlib.compress` at level 9 (stdlib zlib; level chosen for output stability, not novelty).
- `zlib.crc32` for the per-frame integrity check.
- `hashlib.sha256` for the receipt-level hash.
- `struct.pack` / `struct.unpack_from` for fixed-width binary framing.
- Signed 16-bit integer range for delta encoding (standard PCM-style delta).
- Absolute + delta two-mode encoding of per-object streams (standard video and sensor telemetry pattern).
- ASCII magic bytes + version byte (universal file-format convention).

## Compass-8 / 8-primitive architecture

**NO.**

This codec does not use the Compass-8 / N-primitive directional-encoding architecture. The perception-receipt module encodes delta-compressed per-frame box + track state using stdlib `struct` + `zlib` + `crc32`. There is no directional primitive basis, no eight-primitive alphabet, no stroke or contour-level geometry in the shipping v0.1.0 surface.

The Compass-8 substrate was a research thesis tested in pre-0.1.0 phases (documented in [`docs/TRANSPARENCY_JOURNEY.md`](../../docs/TRANSPARENCY_JOURNEY.md) and `.gpd/phases/` in the outer research tree). That thesis did not produce a defended product closure; the v0.1.0 product is the perception-receipt format described above, which stands on its own.

The legacy Wave-1 pipeline under `src/zpe_video/pipeline.py` and `src/zpe_video/codec.py` also does not implement Compass-8 directional encoding; it uses box-state with delta encoding. It is kept importable for historical-research backward compatibility only.

## Open novelty questions for the license agent

1. **Is "cross-writer byte-exactness under default settings" patentable or license-protectable as a method, or is it a combination of disclosure discipline (the spec says "sort these, use this zlib level, forbid these fields") plus a conformance test that asserts it?** Our view: the enforceable novelty is the **spec + conformance-test combination**, not any single ingredient. Want the license agent's read on whether this should be protected as a method claim or as a format-disclosure + trademark-usage clause.

2. **Does `test_cross_writer_independent_implementation_matches` (a test that re-implements the spec and asserts byte-identity with the library) count as a protectable "conformance test pattern," or is it prior-art-standard and merely good hygiene?** We think it is good hygiene with unusually explicit discipline, but would defer to the license agent on whether it appears in the per-product novelty schedule.

3. **The delta encoding's "overflow is an error, not silent truncation" contract.** Standalone this is a design choice; combined with the sorted-canonical previous state as delta base and the hash-stability guarantee, it is a load-bearing invariant. Should it be called out separately in the novelty schedule, or rolled into #1?

4. **The receipt module is zero-runtime-dependency and intentionally implementable in under 100 lines of any language.** This is a product property that makes third-party implementation trivial and cross-writer testing cheap. We are not claiming the implementability itself as novel; we are claiming the format designed-for-that-implementability is novel. Is this the right framing?

5. **No-timestamps / no-writer-metadata discipline.** Every comparable format (MCAP, Parquet with `use_deprecated_int96_timestamps`, JSON with default datetime handling, MISB KLV with pulse times) bakes in some kind of writer-observable metadata that breaks cross-writer hashes. The receipt forbids it in the spec. Is that prohibition-as-discipline a protectable novelty element, or a standard file-format hygiene note?
