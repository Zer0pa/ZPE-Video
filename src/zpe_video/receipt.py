"""Perception receipt — the ZPE Video commercial-wedge surface.

A *perception receipt* is a compact, deterministic, hash-stable binary
record of "what a detector+tracker saw in this video." Given identical
per-frame box+track state on the input side, every conforming writer of
this format emits **byte-identical output**. Given that output, every
conforming reader recovers exactly the same per-frame boxes.

Why this exists
---------------

The ZPE Video research journey (see ``docs/TRANSPARENCY_JOURNEY.md``)
falsified several broader claims — universal-video-codec superiority,
archive-query-as-ZPE-specific, ROI/foveated-sidecar-as-ZPE-specific —
and converged on a single narrow commercial wedge where this format
has a real structural advantage over commodity alternatives:

- **Cross-writer bit-exactness under default settings.** Parquet (pyarrow
  vs fastparquet) diverges on the same input under defaults; JSON key-
  order, timestamps, and dictionary-encoding variation do the same.
  This format does not.
- **Self-contained.** No runtime dependency; the entire wire format can
  be re-implemented in <100 lines of any language with stdlib struct /
  zlib / crc32 primitives.
- **Small and fast to read.** 5-8x smaller than default-Parquet for the
  same sparse-scene state; 10-15x faster cache-read.

Concretely, this supports applications such as:

- C2PA-style "AI perception credentials" — cryptographically-quotable
  receipts of what a model saw in a video.
- Auditable chain-of-custody for detector output in regulated video
  disclosure workflows.
- Video-LLM / VideoRAG object-memory caches with integrity requirements.
- Cross-platform training-data provenance for vision pipelines.

What this does NOT claim
------------------------

- Universal video-compression superiority. Falsified; see Phase 08.
- Better than a raw struct + zlib for archive-query on box-state alone.
  Falsified; see Phase 09.4.1.1.2.
- Primitive-native Compass-8 closure. Sovereign gate remains red.

API
---

The exported surface is minimal and stable:

    >>> from zpe_video import PerceptionReceipt, Box
    >>> receipt = PerceptionReceipt(
    ...     width=1280, height=720, frame_count=2,
    ...     frames=[[Box(box_id=0, x=10, y=20, w=40, h=60)],
    ...             [Box(box_id=0, x=11, y=20, w=40, h=60)]],
    ... )
    >>> blob = receipt.encode()
    >>> isinstance(blob, bytes)
    True
    >>> blob == PerceptionReceipt.from_bytes(blob).encode()
    True

Wire format
-----------

See ``docs/WIRE_FORMAT.md`` for the full byte-level specification. Every
conforming writer must sort boxes by ``box_id`` within each frame, use
``zlib.compress(..., level=9)`` on each frame's payload, and emit a CRC32
over the compressed payload. Every conforming reader must verify the CRC
and raise on mismatch.
"""

from __future__ import annotations

import hashlib
import io
import struct
import zlib
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path

__all__ = [
    "Box",
    "PerceptionReceipt",
    "encode_receipt",
    "decode_receipt",
    "receipt_hash",
    "verify_receipt",
    "WIRE_MAGIC",
    "WIRE_VERSION",
    "CrossWriterMismatch",
    "ReceiptCorrupted",
]


WIRE_MAGIC = b"ZPVID1"
"""The 6-byte magic prefix that identifies a perception receipt."""

WIRE_VERSION = 1
"""Wire-format version. Bumps are breaking changes."""

_HEADER_STRUCT = struct.Struct("<6sBHHHI")
# magic(6s) | version(B) | width(H) | height(H) | frame_count(H) | seed(I)
_FRAME_STRUCT = struct.Struct("<HBII")
# frame_index(H) | mode(B) | payload_len(I) | crc32(I)

_RECEIPT_SEED_DEFAULT = 0
"""Canonical seed value for hash-stable receipts. Different seeds produce
different byte output even for identical frame content — do not change
this default unless you are intentionally sacrificing cross-writer
stability.
"""

_ZLIB_LEVEL = 9
"""zlib compression level fixed for hash stability."""


class ReceiptCorrupted(ValueError):
    """Raised when a receipt blob fails structural or CRC validation."""


class CrossWriterMismatch(ValueError):
    """Raised when two supposedly-equivalent receipts do not hash-match."""


@dataclass(frozen=True)
class Box:
    """A single per-frame detected/tracked box.

    Attributes
    ----------
    box_id:
        Stable track identifier (0-255). Persisted across frames to enable
        delta encoding of positions.
    x, y:
        Top-left corner in pixel coordinates (0-65535).
    w, h:
        Width and height in pixels (0-65535).
    label:
        Integer class label (0-255). Semantic meaning is caller-defined.
    confidence:
        Optional confidence score. NOT persisted in the receipt (the
        receipt records what the model *decided*, not probability). Kept
        on the dataclass for ergonomics and upstream pipeline use.
    """

    box_id: int
    x: int
    y: int
    w: int
    h: int
    label: int = 1
    confidence: float = 1.0


@dataclass(frozen=True)
class PerceptionReceipt:
    """A video perception receipt.

    Attributes
    ----------
    width, height:
        Frame dimensions in pixels. Documented in the header.
    frame_count:
        Number of frames in this receipt.
    frames:
        Per-frame box lists. ``len(frames) == frame_count``. Boxes within
        a frame may be in any order at construction; they will be sorted
        by ``box_id`` during encoding for hash stability.

    Methods
    -------
    encode() -> bytes:
        Serialize to a deterministic, hash-stable byte string.
    from_bytes(blob: bytes) -> "PerceptionReceipt":
        Parse a receipt back into a structured form.
    receipt_hash() -> str:
        Return the SHA-256 hex digest of the encoded bytes. Stable across
        conforming writers.
    """

    width: int
    height: int
    frame_count: int
    frames: tuple[tuple[Box, ...], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.frame_count < 0 or self.frame_count > 0xFFFF:
            raise ValueError(f"frame_count {self.frame_count} out of range [0, 65535]")
        if self.width < 0 or self.width > 0xFFFF:
            raise ValueError(f"width {self.width} out of range [0, 65535]")
        if self.height < 0 or self.height > 0xFFFF:
            raise ValueError(f"height {self.height} out of range [0, 65535]")
        if len(self.frames) != int(self.frame_count):
            raise ValueError(
                f"frames length {len(self.frames)} does not match frame_count {self.frame_count}"
            )

    @classmethod
    def from_frames(
        cls,
        *,
        width: int,
        height: int,
        frames: Sequence[Sequence[Box]],
    ) -> PerceptionReceipt:
        """Construct from a plain list-of-lists, coercing inner sequences to tuples."""
        frames_norm = tuple(tuple(frame) for frame in frames)
        return cls(
            width=int(width),
            height=int(height),
            frame_count=len(frames_norm),
            frames=frames_norm,
        )

    def encode(self, *, seed: int = _RECEIPT_SEED_DEFAULT) -> bytes:
        """Serialize to a deterministic byte string.

        ``seed`` is recorded in the header but does NOT change framing.
        Keeping ``seed=0`` yields the canonical hash-stable output.
        """
        return encode_receipt(self, seed=seed)

    @classmethod
    def from_bytes(cls, blob: bytes) -> PerceptionReceipt:
        """Parse a receipt from a byte string. Verifies all CRC32s."""
        return decode_receipt(blob)

    def receipt_hash(self, *, seed: int = _RECEIPT_SEED_DEFAULT) -> str:
        """Return the SHA-256 hex digest of the encoded bytes."""
        return receipt_hash(self.encode(seed=seed))


# ---------------------------------------------------------------------------
# Module-level functional API. The class methods above delegate to these.
# ---------------------------------------------------------------------------


def encode_receipt(
    receipt: PerceptionReceipt,
    *,
    seed: int = _RECEIPT_SEED_DEFAULT,
) -> bytes:
    """Encode a receipt to a deterministic byte string.

    The output is guaranteed bit-exact across conforming writers when the
    input ``PerceptionReceipt`` carries identical frame content and the
    same ``seed`` value is used. The canonical seed is 0; keep it there
    for cross-writer stability.
    """
    if seed < 0 or seed > 0xFFFFFFFF:
        raise ValueError(f"seed {seed} out of range [0, 2^32-1]")

    stream = io.BytesIO()
    stream.write(
        _HEADER_STRUCT.pack(
            WIRE_MAGIC,
            WIRE_VERSION,
            int(receipt.width),
            int(receipt.height),
            int(receipt.frame_count),
            int(seed),
        )
    )

    prev_by_id: dict[int, Box] = {}
    for frame_index, boxes in enumerate(receipt.frames):
        payload = _encode_frame_payload(boxes, prev_by_id)
        compressed = zlib.compress(payload, level=_ZLIB_LEVEL)
        crc = zlib.crc32(compressed) & 0xFFFFFFFF
        stream.write(_FRAME_STRUCT.pack(int(frame_index), 1, len(compressed), int(crc)))
        stream.write(compressed)
        # sorted canonical box state for next-frame delta base
        prev_by_id = {int(b.box_id): b for b in sorted(boxes, key=lambda b: b.box_id)}

    return stream.getvalue()


def decode_receipt(blob: bytes) -> PerceptionReceipt:
    """Decode a receipt byte string back into a structured form.

    Raises ``ReceiptCorrupted`` on:
      - bad magic / wrong version
      - truncated header or frame
      - CRC32 mismatch on any frame's compressed payload
      - zlib decompression failure
      - unknown box mode byte
    """
    if len(blob) < _HEADER_STRUCT.size:
        raise ReceiptCorrupted("receipt is shorter than the header size")
    magic, version, width, height, frame_count, _seed = _HEADER_STRUCT.unpack_from(blob, 0)
    if magic != WIRE_MAGIC:
        raise ReceiptCorrupted(f"bad magic: got {magic!r}, expected {WIRE_MAGIC!r}")
    if version != WIRE_VERSION:
        raise ReceiptCorrupted(
            f"unsupported wire version {version}; this library supports version {WIRE_VERSION}"
        )

    offset = _HEADER_STRUCT.size
    frames: list[tuple[Box, ...]] = []
    prev_by_id: dict[int, Box] = {}

    for expected_index in range(int(frame_count)):
        if offset + _FRAME_STRUCT.size > len(blob):
            raise ReceiptCorrupted(f"truncated frame header at frame {expected_index}")
        frame_index, _mode, payload_len, crc_expected = _FRAME_STRUCT.unpack_from(blob, offset)
        offset += _FRAME_STRUCT.size
        if frame_index != expected_index:
            raise ReceiptCorrupted(
                f"non-monotonic frame_index at position {expected_index}: got {frame_index}"
            )
        end = offset + int(payload_len)
        if end > len(blob):
            raise ReceiptCorrupted(f"truncated frame payload at frame {frame_index}")
        compressed = blob[offset:end]
        offset = end
        if (zlib.crc32(compressed) & 0xFFFFFFFF) != int(crc_expected):
            raise ReceiptCorrupted(f"CRC32 mismatch at frame {frame_index}")
        try:
            payload = zlib.decompress(compressed)
        except zlib.error as exc:
            raise ReceiptCorrupted(
                f"zlib decompression failed at frame {frame_index}: {exc}"
            ) from exc
        boxes = tuple(_decode_frame_payload(payload, prev_by_id))
        frames.append(boxes)
        prev_by_id = {int(b.box_id): b for b in sorted(boxes, key=lambda b: b.box_id)}

    if offset != len(blob):
        raise ReceiptCorrupted(f"trailing {len(blob) - offset} byte(s) after last frame")

    return PerceptionReceipt(
        width=int(width),
        height=int(height),
        frame_count=int(frame_count),
        frames=tuple(frames),
    )


def receipt_hash(blob: bytes) -> str:
    """Return the SHA-256 hex digest of a receipt byte string."""
    return hashlib.sha256(blob).hexdigest()


def verify_receipt(
    blob: bytes,
    *,
    expected_hash: str | None = None,
    expected_peer_blob: bytes | None = None,
) -> PerceptionReceipt:
    """Verify a receipt blob end-to-end.

    Always:
      - validates magic, version, monotonic framing, and CRC32 per frame
        (via ``decode_receipt``)

    Optional:
      - if ``expected_hash`` is given, checks that the SHA-256 of ``blob``
        matches it; raises ``CrossWriterMismatch`` on mismatch
      - if ``expected_peer_blob`` is given, checks that the two blobs are
        byte-identical; raises ``CrossWriterMismatch`` on mismatch

    Returns
    -------
    PerceptionReceipt:
        the decoded receipt, if all checks pass.
    """
    receipt = decode_receipt(blob)
    if expected_hash is not None:
        actual = receipt_hash(blob)
        if actual != expected_hash:
            raise CrossWriterMismatch(
                f"receipt hash mismatch: expected {expected_hash}, got {actual}"
            )
    if expected_peer_blob is not None:
        if blob != expected_peer_blob:
            raise CrossWriterMismatch(
                "receipt peer blob mismatch: two encoders of the same frame "
                "content produced different bytes under default settings"
            )
    return receipt


# ---------------------------------------------------------------------------
# Convenience I/O helpers
# ---------------------------------------------------------------------------


def write_receipt(
    receipt: PerceptionReceipt, path: str | Path, *, seed: int = _RECEIPT_SEED_DEFAULT
) -> int:
    """Encode a receipt and write it to disk. Returns the byte count written."""
    blob = encode_receipt(receipt, seed=seed)
    Path(path).write_bytes(blob)
    return len(blob)


def read_receipt(path: str | Path) -> PerceptionReceipt:
    """Read and verify a receipt from disk."""
    return decode_receipt(Path(path).read_bytes())


# ---------------------------------------------------------------------------
# Internal frame payload codec
# ---------------------------------------------------------------------------


def _encode_frame_payload(
    boxes: Iterable[Box],
    prev_by_id: dict[int, Box],
) -> bytes:
    """Encode one frame's box list into the uncompressed per-frame payload.

    Boxes are sorted by ``box_id`` for hash-stable output. The first
    observation of a given ``box_id`` uses absolute mode; subsequent
    observations use signed delta mode relative to the previous frame's
    canonical state.
    """
    sorted_boxes = sorted(list(boxes), key=lambda b: int(b.box_id))
    if len(sorted_boxes) > 255:
        raise ValueError(
            f"more than 255 boxes in a frame ({len(sorted_boxes)}); wire format capacity exceeded"
        )
    out = bytearray()
    out.append(len(sorted_boxes))
    for box in sorted_boxes:
        box_id = int(box.box_id) & 0xFF
        label = int(box.label) & 0xFF
        prev = prev_by_id.get(int(box.box_id))
        out.append(box_id)
        out.append(label)
        if prev is None:
            out.append(0)  # absolute
            out.extend(struct.pack("<HHHH", int(box.x), int(box.y), int(box.w), int(box.h)))
        else:
            dx = int(box.x) - int(prev.x)
            dy = int(box.y) - int(prev.y)
            if dx < -32768 or dx > 32767 or dy < -32768 or dy > 32767:
                raise ValueError(
                    f"delta dx={dx} dy={dy} out of signed-16 range for "
                    f"box_id={box_id}; fall back to absolute by using a "
                    f"new box_id"
                )
            out.append(1)  # delta
            out.extend(struct.pack("<hh", dx, dy))
            out.extend(struct.pack("<HH", int(box.w), int(box.h)))
    return bytes(out)


def _decode_frame_payload(
    payload: bytes,
    prev_by_id: dict[int, Box],
) -> list[Box]:
    """Decode one uncompressed per-frame payload."""
    if not payload:
        return []
    off = 0
    count = payload[off]
    off += 1
    boxes: list[Box] = []
    for _ in range(count):
        if off + 3 > len(payload):
            raise ReceiptCorrupted("truncated box header")
        box_id = payload[off]
        label = payload[off + 1]
        mode = payload[off + 2]
        off += 3
        if mode == 0:
            if off + 8 > len(payload):
                raise ReceiptCorrupted("truncated absolute box")
            x, y, w, h = struct.unpack_from("<HHHH", payload, off)
            off += 8
            boxes.append(Box(box_id=box_id, x=x, y=y, w=w, h=h, label=label))
        elif mode == 1:
            if off + 8 > len(payload):
                raise ReceiptCorrupted("truncated delta box")
            dx, dy = struct.unpack_from("<hh", payload, off)
            w, h = struct.unpack_from("<HH", payload, off + 4)
            off += 8
            prev = prev_by_id.get(int(box_id))
            if prev is None:
                raise ReceiptCorrupted(f"delta without prior box for id {box_id}")
            boxes.append(
                Box(
                    box_id=box_id,
                    x=int(prev.x) + int(dx),
                    y=int(prev.y) + int(dy),
                    w=w,
                    h=h,
                    label=label,
                )
            )
        else:
            raise ReceiptCorrupted(f"unknown box mode byte {mode}")
    if off != len(payload):
        raise ReceiptCorrupted(f"trailing {len(payload) - off} byte(s) in frame payload")
    return boxes
