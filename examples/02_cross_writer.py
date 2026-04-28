"""Example 2 — cross-writer proof: two independent implementations agree.

The wedge of this library is cross-writer bit-exactness. This example
hand-rolls an independent from-spec encoder and proves it produces
byte-identical output to the library on the same input.

Run:
    python examples/02_cross_writer.py
"""

from __future__ import annotations

import struct
import zlib

from zpe_video import (
    WIRE_MAGIC,
    WIRE_VERSION,
    Box,
    PerceptionReceipt,
    encode_receipt,
    receipt_hash,
    verify_receipt,
)


def independent_encoder(receipt: PerceptionReceipt) -> bytes:
    """A minimal from-spec encoder — no zpe_video dependency except the types."""
    out = bytearray(
        struct.pack(
            "<6sBHHHI",
            WIRE_MAGIC, WIRE_VERSION,
            receipt.width, receipt.height, receipt.frame_count, 0,
        )
    )
    prev: dict[int, Box] = {}
    for idx, frame in enumerate(receipt.frames):
        frame = sorted(frame, key=lambda b: int(b.box_id))
        payload = bytearray([len(frame)])
        for box in frame:
            payload += bytes([int(box.box_id) & 0xFF, int(box.label) & 0xFF])
            p = prev.get(int(box.box_id))
            if p is None:
                payload.append(0)
                payload += struct.pack(
                    "<HHHH", int(box.x), int(box.y), int(box.w), int(box.h)
                )
            else:
                payload.append(1)
                payload += struct.pack("<hh", int(box.x) - int(p.x), int(box.y) - int(p.y))
                payload += struct.pack("<HH", int(box.w), int(box.h))
        compressed = zlib.compress(bytes(payload), level=9)
        out += struct.pack(
            "<HBII", idx, 1, len(compressed), zlib.crc32(compressed) & 0xFFFFFFFF
        )
        out += compressed
        prev = {int(b.box_id): b for b in frame}
    return bytes(out)


def main() -> None:
    receipt = PerceptionReceipt.from_frames(
        width=1280, height=720,
        frames=[
            [Box(box_id=0, x=10, y=20, w=40, h=60),
             Box(box_id=1, x=200, y=50, w=30, h=55, label=2)],
            [Box(box_id=0, x=12, y=20, w=40, h=60),
             Box(box_id=1, x=203, y=52, w=30, h=55, label=2)],
        ],
    )

    blob_library = encode_receipt(receipt)
    blob_independent = independent_encoder(receipt)

    print(f"library bytes:     {len(blob_library)}")
    print(f"independent bytes: {len(blob_independent)}")
    print(f"byte-identical:    {blob_library == blob_independent}")
    print(f"library sha256:      {receipt_hash(blob_library)}")
    print(f"independent sha256:  {receipt_hash(blob_independent)}")

    # verify_receipt can also assert this symbolically:
    verify_receipt(blob_library, expected_peer_blob=blob_independent)
    print("cross-writer wedge: VERIFIED")


if __name__ == "__main__":
    main()
