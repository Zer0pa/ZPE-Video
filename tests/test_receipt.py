"""Tests for the perception-receipt surface.

These tests pin the public wedge: cross-writer bit-exactness under
default settings, frame-level CRC32 integrity, round-trip fidelity, and
error behavior. They are self-contained (stdlib only) so they can run in
any CI or offline environment.
"""

from __future__ import annotations

import hashlib
import struct
import zlib
from pathlib import Path

import pytest

from zpe_video import (
    WIRE_MAGIC,
    WIRE_VERSION,
    Box,
    CrossWriterMismatch,
    PerceptionReceipt,
    ReceiptCorrupted,
    decode_receipt,
    encode_receipt,
    read_receipt,
    receipt_hash,
    verify_receipt,
    write_receipt,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _small_receipt() -> PerceptionReceipt:
    """3 frames, 2 tracks, mild motion. Covers absolute + delta + reordering."""
    frames = [
        # frame 0: two tracks, sorted by id
        [
            Box(box_id=1, x=10, y=20, w=40, h=60, label=1),
            Box(box_id=3, x=200, y=50, w=30, h=55, label=2),
        ],
        # frame 1: same two tracks, small motion (delta)
        [
            Box(box_id=3, x=205, y=51, w=30, h=55, label=2),  # intentionally reordered
            Box(box_id=1, x=11, y=21, w=40, h=60, label=1),
        ],
        # frame 2: only track 1 present, motion continues
        [Box(box_id=1, x=14, y=22, w=40, h=60, label=1)],
    ]
    return PerceptionReceipt.from_frames(width=1280, height=720, frames=frames)


def _empty_receipt() -> PerceptionReceipt:
    return PerceptionReceipt(width=640, height=360, frame_count=0)


def _single_frame_empty() -> PerceptionReceipt:
    return PerceptionReceipt(
        width=320,
        height=240,
        frame_count=1,
        frames=((),),
    )


# ---------------------------------------------------------------------------
# Round-trip fidelity
# ---------------------------------------------------------------------------


def test_round_trip_small():
    receipt = _small_receipt()
    blob = encode_receipt(receipt)
    back = decode_receipt(blob)
    assert back.width == receipt.width
    assert back.height == receipt.height
    assert back.frame_count == receipt.frame_count
    # frame 0 should match input sort order (by box_id)
    frame0_input = sorted(receipt.frames[0], key=lambda b: b.box_id)
    assert list(back.frames[0]) == frame0_input


def test_round_trip_empty_receipt():
    receipt = _empty_receipt()
    blob = encode_receipt(receipt)
    back = decode_receipt(blob)
    assert back.frame_count == 0
    assert back.frames == ()


def test_round_trip_single_empty_frame():
    receipt = _single_frame_empty()
    blob = encode_receipt(receipt)
    back = decode_receipt(blob)
    assert back.frame_count == 1
    assert back.frames == ((),)


# ---------------------------------------------------------------------------
# Cross-writer bit-exactness — the commercial wedge
# ---------------------------------------------------------------------------


def test_same_input_yields_same_bytes():
    """Encoding the same PerceptionReceipt twice must yield byte-identical output."""
    receipt = _small_receipt()
    blob_a = encode_receipt(receipt)
    blob_b = encode_receipt(receipt)
    assert blob_a == blob_b
    assert receipt_hash(blob_a) == receipt_hash(blob_b)


def test_reordered_input_yields_same_bytes():
    """Box order within a frame must not affect output bytes."""
    frames_a = [
        [Box(box_id=1, x=10, y=10, w=20, h=20), Box(box_id=2, x=50, y=50, w=20, h=20)],
    ]
    frames_b = [
        [Box(box_id=2, x=50, y=50, w=20, h=20), Box(box_id=1, x=10, y=10, w=20, h=20)],
    ]
    a = PerceptionReceipt.from_frames(width=320, height=240, frames=frames_a)
    b = PerceptionReceipt.from_frames(width=320, height=240, frames=frames_b)
    assert encode_receipt(a) == encode_receipt(b)


def test_cross_writer_independent_implementation_matches():
    """Hand-roll an independent minimal encoder from the spec and check byte match.

    This pins the wedge: someone implementing the spec in any language gets
    the exact same bytes as this library under default settings.
    """
    receipt = _small_receipt()
    ours = encode_receipt(receipt)

    # Independent implementation using only stdlib primitives.
    buf = bytearray()
    buf += struct.pack(
        "<6sBHHHI",
        WIRE_MAGIC,
        WIRE_VERSION,
        receipt.width,
        receipt.height,
        receipt.frame_count,
        0,
    )
    prev: dict[int, Box] = {}
    for idx, frame in enumerate(receipt.frames):
        sorted_frame = sorted(frame, key=lambda b: int(b.box_id))
        payload = bytearray()
        payload.append(len(sorted_frame))
        for box in sorted_frame:
            payload.append(int(box.box_id) & 0xFF)
            payload.append(int(box.label) & 0xFF)
            prev_box = prev.get(int(box.box_id))
            if prev_box is None:
                payload.append(0)
                payload += struct.pack("<HHHH", int(box.x), int(box.y), int(box.w), int(box.h))
            else:
                dx = int(box.x) - int(prev_box.x)
                dy = int(box.y) - int(prev_box.y)
                payload.append(1)
                payload += struct.pack("<hh", dx, dy)
                payload += struct.pack("<HH", int(box.w), int(box.h))
        compressed = zlib.compress(bytes(payload), level=9)
        crc = zlib.crc32(compressed) & 0xFFFFFFFF
        buf += struct.pack("<HBII", idx, 1, len(compressed), crc)
        buf += compressed
        prev = {int(b.box_id): b for b in sorted_frame}

    assert bytes(buf) == ours, (
        "independent implementation of the wire format diverged from "
        "this library's encoder output — the cross-writer wedge is broken"
    )


def test_receipt_hash_is_stable():
    receipt = _small_receipt()
    blob = encode_receipt(receipt)
    direct = receipt_hash(blob)
    via_class = receipt.receipt_hash()
    assert direct == via_class
    assert len(direct) == 64
    # verify against hashlib directly
    assert direct == hashlib.sha256(blob).hexdigest()


# ---------------------------------------------------------------------------
# CRC32 integrity
# ---------------------------------------------------------------------------


def test_crc_mismatch_raises():
    receipt = _small_receipt()
    blob = bytearray(encode_receipt(receipt))
    # Flip a bit in the second frame's compressed payload area. The header
    # is 15 bytes; frame 0 starts at 15. Skip past frame header (11 bytes)
    # then past frame 0's compressed bytes: easier to just corrupt the
    # very last byte, which is always in frame N-1's compressed payload.
    blob[-1] ^= 0xFF
    with pytest.raises(ReceiptCorrupted):
        decode_receipt(bytes(blob))


def test_bad_magic_raises():
    receipt = _small_receipt()
    blob = bytearray(encode_receipt(receipt))
    blob[0] = ord("X")
    with pytest.raises(ReceiptCorrupted, match="bad magic"):
        decode_receipt(bytes(blob))


def test_unsupported_version_raises():
    receipt = _small_receipt()
    blob = bytearray(encode_receipt(receipt))
    blob[6] = 99
    with pytest.raises(ReceiptCorrupted, match="unsupported wire version"):
        decode_receipt(bytes(blob))


def test_truncated_header_raises():
    with pytest.raises(ReceiptCorrupted, match="shorter than the header"):
        decode_receipt(b"\x00" * 3)


def test_trailing_bytes_raises():
    receipt = _small_receipt()
    blob = encode_receipt(receipt) + b"\xaa\xbb"
    with pytest.raises(ReceiptCorrupted, match="trailing"):
        decode_receipt(blob)


# ---------------------------------------------------------------------------
# verify_receipt helpers
# ---------------------------------------------------------------------------


def test_verify_receipt_ok():
    receipt = _small_receipt()
    blob = encode_receipt(receipt)
    h = receipt_hash(blob)
    got = verify_receipt(blob, expected_hash=h, expected_peer_blob=blob)
    assert got.frame_count == receipt.frame_count


def test_verify_receipt_hash_mismatch():
    receipt = _small_receipt()
    blob = encode_receipt(receipt)
    with pytest.raises(CrossWriterMismatch, match="hash mismatch"):
        verify_receipt(blob, expected_hash="0" * 64)


def test_verify_receipt_peer_mismatch():
    receipt = _small_receipt()
    blob = encode_receipt(receipt)
    with pytest.raises(CrossWriterMismatch, match="peer blob mismatch"):
        verify_receipt(blob, expected_peer_blob=blob + b"\x00")


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------


def test_write_and_read_roundtrip(tmp_path: Path):
    receipt = _small_receipt()
    path = tmp_path / "receipt.zpvid"
    n = write_receipt(receipt, path)
    assert n == path.stat().st_size
    back = read_receipt(path)
    assert back.frame_count == receipt.frame_count
    assert back.width == receipt.width


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def test_frame_count_mismatch_raises():
    with pytest.raises(ValueError, match="frame_count"):
        PerceptionReceipt(width=320, height=240, frame_count=2, frames=())


def test_too_many_boxes_in_frame_raises():
    # 256 boxes exceeds the 255 wire-format cap
    too_many = tuple(Box(box_id=i % 256, x=0, y=0, w=1, h=1) for i in range(256))
    receipt = PerceptionReceipt(
        width=320,
        height=240,
        frame_count=1,
        frames=(too_many,),
    )
    with pytest.raises(ValueError, match="255 boxes"):
        encode_receipt(receipt)


def test_delta_overflow_raises():
    """dx/dy must fit in signed 16; huge jumps must raise rather than corrupt."""
    frames = [
        [Box(box_id=1, x=0, y=0, w=10, h=10)],
        [Box(box_id=1, x=60000, y=0, w=10, h=10)],
    ]
    receipt = PerceptionReceipt.from_frames(width=65535, height=65535, frames=frames)
    with pytest.raises(ValueError, match="signed-16 range"):
        encode_receipt(receipt)


def test_seed_changes_bytes_but_not_content():
    """Non-default seed produces different bytes but the same decoded content."""
    receipt = _small_receipt()
    blob_default = encode_receipt(receipt, seed=0)
    blob_seeded = encode_receipt(receipt, seed=42)
    assert blob_default != blob_seeded
    back_a = decode_receipt(blob_default)
    back_b = decode_receipt(blob_seeded)
    assert list(back_a.frames[0]) == list(back_b.frames[0])
