# ZPE Perception Receipt — Wire Format Specification

Version: 1
Stability: stable within major version; breaking changes bump
`WIRE_VERSION`.

This document is the authoritative byte-level specification. The
reference implementation at
[`src/zpe_video/receipt.py`](../src/zpe_video/receipt.py) must agree with
this document; if they disagree, this document is correct and the
implementation is buggy.

The goal is that any language with stdlib struct / zlib / crc32
primitives can implement a conforming writer or reader in well under 100
lines of code, and that any two such implementations produce **byte-
identical output** on byte-identical input under default settings.

## Endianness and types

All multi-byte integers are **little-endian**. All fields use C99-style
fixed widths.

## High-level layout

```
+--------------------+
|      HEADER        |   15 bytes, fixed
+--------------------+
|     FRAME 0        |   11-byte frame header + variable-length zlib payload
+--------------------+
|     FRAME 1        |
+--------------------+
|        ...         |
+--------------------+
| FRAME frame_count-1|
+--------------------+
```

No trailer, no checksum over the whole blob, no padding. A reader must
consume all bytes; trailing bytes after the last frame are an error.

## Header (15 bytes)

```
struct Header {
    char     magic[6];       // "ZPVID1"  (0x5A 0x50 0x56 0x49 0x44 0x31)
    uint8_t  version;        // 1
    uint16_t width;          // frame width in pixels  (0..65535)
    uint16_t height;         // frame height in pixels (0..65535)
    uint16_t frame_count;    // number of frames       (0..65535)
    uint32_t seed;           // opaque provenance tag; canonical = 0
};
```

Python `struct` format: `<6sBHHHI`.

- `magic` and `version` identify a conforming receipt. A reader seeing a
  different magic or version **must** abort with an error.
- `seed` is a 32-bit opaque field. The canonical default is 0. Changing
  it produces different bytes (and therefore different hashes) for the
  same frame content — this is intentional and can be used as a salt.
- A header with `frame_count = 0` is legal; the blob is exactly 15 bytes.

## Frame header (11 bytes)

Each of the `frame_count` frames begins with:

```
struct FrameHeader {
    uint16_t frame_index;    // must equal position in the sequence: 0, 1, 2, ...
    uint8_t  mode;           // 1 (reserved; only compressed delta mode is defined)
    uint32_t payload_len;    // number of zlib-compressed bytes that follow
    uint32_t crc32;          // zlib CRC-32 of the compressed payload bytes
};
```

Python `struct` format: `<HBII`.

- `frame_index` is a redundancy check; a reader **must** verify it equals
  the zero-based position in the sequence and abort on mismatch.
- `mode` is reserved. Only value `1` (compressed-delta) is currently
  defined; other values **must** be rejected.
- `crc32` is computed over the `payload_len` compressed bytes (not the
  decompressed payload). Readers **must** verify and abort on mismatch.

## Frame payload (after decompression)

The per-frame payload is zlib-compressed with **level=9**. Any conforming
writer **must** use `zlib.compress(payload, level=9)`; other levels can
produce byte-valid but hash-different output and are nonconforming.

The decompressed payload begins with a 1-byte box count, followed by
that many per-box records.

```
struct FramePayload {
    uint8_t       box_count;        // 0..255; >255 is an error at encode time
    BoxRecord     boxes[box_count]; // MUST be sorted by box_id ascending
};
```

### Box record

Each box is variable-length depending on its mode byte:

```
struct BoxRecord {
    uint8_t   box_id;         // 0..255
    uint8_t   label;          // 0..255, caller-defined semantics
    uint8_t   mode;           // 0 = absolute, 1 = delta
    union {
        struct {                     // mode == 0
            uint16_t x, y, w, h;    // absolute coords, 0..65535
        } absolute;
        struct {                     // mode == 1
            int16_t  dx, dy;        // signed delta from previous frame's box_id
            uint16_t w, h;          // absolute width/height
        } delta;
    };
};
```

Python `struct` formats: `<HHHH` for absolute body (8 bytes), `<hhHH`
for delta body (8 bytes).

### Delta encoding rules

- The first observation of any `box_id` in the blob **must** use
  `mode = 0` (absolute). A `mode = 1` with no prior box of that id is an
  error.
- Subsequent observations of the same `box_id` **may** use `mode = 1`
  (delta). The reference base for delta is the **previous frame's
  sorted-by-box_id state** (the same sorting the writer used).
- `dx` and `dy` are signed 16-bit. If the true delta overflows, the
  writer **must** fall back to absolute mode (or raise an error; the
  reference implementation raises). Silent truncation is nonconforming.

### Sort order — load-bearing

Within each frame, boxes **must** be serialized in ascending `box_id`
order. This is the single most important rule for cross-writer byte
stability: two writers that agree on input boxes but disagree on their
order will produce different output bytes. Readers are not required to
re-sort; they should consume boxes in the order written.

## Example: minimal valid 0-frame blob

```
header only:
5A 50 56 49 44 31  01  00 00  00 00  00 00  00 00 00 00
\__magic___________/  \ver\/ \w=0/  \h=0/  \fc=0/ \seed=0______/
```

15 bytes; decodes to `PerceptionReceipt(width=0, height=0, frame_count=0, frames=())`.

## What is explicitly NOT in the format

- No embedded timestamps. Absence is intentional for hash stability.
- No writer identifier, version string, or provenance metadata in the
  blob itself. Provenance belongs in the enclosing envelope (e.g., a
  C2PA manifest, a signed wrapper) that **references the receipt by
  hash**. The companion `zpe_video.manifest` module implements this
  pattern as deterministic external JSON; it is not part of the receipt
  wire bytes.
- No confidence scores. The receipt records what the model **decided**,
  not how certain it was.
- No class dictionary. The integer `label` value is caller-defined; the
  consumer is responsible for maintaining its own label mapping.
- No encryption. Encrypt the blob externally if needed; the format is
  plain bytes by design.

## Versioning policy

- The wire `version` byte is 1.
- Any change that alters the byte layout bumps the major version and is
  explicitly breaking.
- Additive changes that do not alter existing layouts are forbidden in
  this format: the whole point is byte-exactness, and slotting new
  fields in later would break old readers silently.
- If a change is needed, a new magic + version combination is used and
  old-version receipts are left interpretable by old readers.

## Conformance tests

See [`tests/test_receipt.py`](../tests/test_receipt.py). In particular,
`test_cross_writer_independent_implementation_matches` hand-rolls a
minimal from-spec writer and asserts it produces byte-identical output
to the library. A new implementation **should** replicate this test
against its own output.

## Reference implementation

[`src/zpe_video/receipt.py`](../src/zpe_video/receipt.py).

The functions exposed by that module (`encode_receipt`,
`decode_receipt`, `receipt_hash`, `verify_receipt`, `write_receipt`,
`read_receipt`, `PerceptionReceipt`, `Box`) are the stable public API.
The internal `_encode_frame_payload` / `_decode_frame_payload` functions
are implementation details and may change between versions.

Manifest binding helpers live in
[`src/zpe_video/manifest.py`](../src/zpe_video/manifest.py). They bind to
receipt bytes by SHA-256 and byte length without changing this wire
format.
