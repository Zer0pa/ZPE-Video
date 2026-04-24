# Quickstart

Five minutes to a working perception receipt. No GPU, no dataset
download, no network egress. Pure-stdlib core surface.

## Install

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip uv
uv sync --extra dev
```

Optional extras:

```bash
# To ingest raw video via YOLOv8m into a receipt
uv sync --extra producer

# To run the legacy research harness
uv sync --extra research

# To regenerate the receipt-core benchmark and authority bundle
uv sync --extra benchmark

# Everything
uv sync --extra all
```

Python 3.11, 3.12, or 3.13. No OS-specific dependencies for the core
surface.

## Example 1 — Encode, decode, hash

```python
from zpe_video import Box, PerceptionReceipt, encode_receipt, decode_receipt, receipt_hash

# Build a receipt from per-frame box lists.
receipt = PerceptionReceipt.from_frames(
    width=1280, height=720,
    frames=[
        [Box(box_id=0, x=10, y=20, w=40, h=60, label=1)],
        [Box(box_id=0, x=11, y=20, w=40, h=60, label=1)],  # delta
    ],
)

# Encode to bytes. Deterministic; identical inputs produce identical bytes.
blob = encode_receipt(receipt)

# Hash is a stable reference.
h = receipt_hash(blob)
print(h)  # 64-char sha256 hex

# Round-trip.
back = decode_receipt(blob)
assert back.frame_count == 2
```

## Example 2 — Write and verify a file

```python
from zpe_video import (
    Box, PerceptionReceipt,
    write_receipt, read_receipt, verify_receipt,
    receipt_hash,
)

receipt = PerceptionReceipt.from_frames(
    width=320, height=240,
    frames=[[Box(box_id=0, x=5, y=5, w=10, h=10)]],
)
write_receipt(receipt, "scene.zpvid")

# Later / on another machine / in another process.
blob = open("scene.zpvid", "rb").read()
h = receipt_hash(blob)

# Verify CRC32 + hash match in one call.
decoded = verify_receipt(blob, expected_hash=h)
assert decoded.frame_count == 1
```

## Example 3 — Cross-writer check

This is the load-bearing wedge: two independent implementations of the
wire format, starting from the same frame content, produce identical
bytes.

```python
import struct, zlib
from zpe_video import (
    Box, PerceptionReceipt,
    WIRE_MAGIC, WIRE_VERSION,
    encode_receipt, verify_receipt,
)

# Input: the same frame content.
receipt = PerceptionReceipt.from_frames(
    width=640, height=360,
    frames=[[Box(box_id=0, x=0, y=0, w=10, h=10)],
            [Box(box_id=0, x=1, y=0, w=10, h=10)]],
)

# Implementation A: this library.
blob_a = encode_receipt(receipt)

# Implementation B: a minimal from-spec encoder (~40 lines below).
buf = bytearray(struct.pack(
    "<6sBHHHI",
    WIRE_MAGIC, WIRE_VERSION, 640, 360, 2, 0,
))
prev = {}
for idx, frame in enumerate(receipt.frames):
    frame = sorted(frame, key=lambda b: int(b.box_id))
    payload = bytearray([len(frame)])
    for box in frame:
        payload += bytes([int(box.box_id) & 0xFF, int(box.label) & 0xFF])
        p = prev.get(int(box.box_id))
        if p is None:
            payload.append(0)
            payload += struct.pack("<HHHH", int(box.x), int(box.y), int(box.w), int(box.h))
        else:
            payload.append(1)
            payload += struct.pack("<hh", int(box.x) - int(p.x), int(box.y) - int(p.y))
            payload += struct.pack("<HH", int(box.w), int(box.h))
    compressed = zlib.compress(bytes(payload), level=9)
    buf += struct.pack("<HBII", idx, 1, len(compressed), zlib.crc32(compressed) & 0xFFFFFFFF)
    buf += compressed
    prev = {int(b.box_id): b for b in frame}
blob_b = bytes(buf)

# They must be byte-identical.
assert blob_a == blob_b, "cross-writer wedge broken"

# verify_receipt can also check this symbolically.
verify_receipt(blob_a, expected_peer_blob=blob_b)
```

## Run the tests

```bash
uv run pytest tests -v
uv run python scripts/receipt_core_benchmark.py
uv run python scripts/authority_bundle.py --check
```

Expect 29 tests to pass. The benchmark should report `"verdict": "pass"`;
the authority-bundle check should report `authority packet is current`.

## Next

- [`WEDGE.md`](WEDGE.md) — why this exists.
- [`WIRE_FORMAT.md`](WIRE_FORMAT.md) — byte-level spec for re-implementation.
- [`TRANSPARENCY_JOURNEY.md`](TRANSPARENCY_JOURNEY.md) — the research history.
- [`../examples/`](../examples/) — more runnable examples.
