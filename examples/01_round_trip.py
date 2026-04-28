"""Example 1 — encode a receipt, hash it, round-trip it, print the size.

Run:
    python examples/01_round_trip.py
"""

from __future__ import annotations

from zpe_video import Box, PerceptionReceipt, encode_receipt, decode_receipt, receipt_hash


def main() -> None:
    receipt = PerceptionReceipt.from_frames(
        width=1280,
        height=720,
        frames=[
            [Box(box_id=0, x=10, y=20, w=40, h=60, label=1),
             Box(box_id=1, x=200, y=50, w=30, h=55, label=2)],
            # delta from previous frame for box 0; box 1 moved a bit
            [Box(box_id=0, x=12, y=20, w=40, h=60, label=1),
             Box(box_id=1, x=203, y=52, w=30, h=55, label=2)],
            # only box 0 survives
            [Box(box_id=0, x=15, y=20, w=40, h=60, label=1)],
        ],
    )

    blob = encode_receipt(receipt)
    print(f"frame_count:   {receipt.frame_count}")
    print(f"blob bytes:    {len(blob)}")
    print(f"sha256:        {receipt_hash(blob)}")

    # Round trip.
    back = decode_receipt(blob)
    print(f"round-trip frame_count: {back.frame_count}")
    print(f"round-trip frame 0 len: {len(back.frames[0])}")


if __name__ == "__main__":
    main()
