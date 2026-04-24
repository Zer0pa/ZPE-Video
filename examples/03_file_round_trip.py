"""Example 3 — write a receipt to disk, verify it end-to-end on read.

Run:
    python examples/03_file_round_trip.py
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from zpe_video import (
    Box,
    PerceptionReceipt,
    read_receipt,
    receipt_hash,
    verify_receipt,
    write_receipt,
)


def main() -> None:
    receipt = PerceptionReceipt.from_frames(
        width=640, height=360,
        frames=[
            [Box(box_id=0, x=5, y=5, w=10, h=10),
             Box(box_id=1, x=50, y=50, w=10, h=10)],
            [Box(box_id=0, x=7, y=5, w=10, h=10),
             Box(box_id=1, x=49, y=51, w=10, h=10)],
        ],
    )

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "scene.zpvid"
        written_bytes = write_receipt(receipt, path)
        disk_blob = path.read_bytes()
        disk_hash = receipt_hash(disk_blob)
        print(f"written bytes:        {written_bytes}")
        print(f"disk hash (sha256):   {disk_hash}")

        # Full structural + hash verification in one call.
        back = verify_receipt(disk_blob, expected_hash=disk_hash)
        print(f"verified frame_count: {back.frame_count}")

        # Or just read + implicit CRC check.
        plain_back = read_receipt(path)
        print(f"read  frame_count:    {plain_back.frame_count}")


if __name__ == "__main__":
    main()
