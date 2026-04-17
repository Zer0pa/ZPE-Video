"""zpe_video — Perception receipts for video AI pipelines.

This package provides a compact, deterministic, hash-stable binary format
for recording "what a detector+tracker saw in a video". The format's
unique structural property — cross-writer bit-exactness under default
settings — makes it suitable for auditable AI-perception receipts,
chain-of-custody workflows, and integrity-guaranteed object-memory
caches for video-LLM pipelines.

See ``docs/WEDGE.md`` for the commercial-wedge rationale and
``docs/TRANSPARENCY_JOURNEY.md`` for the full research history including
negative results.

Primary API
-----------

- :class:`~zpe_video.receipt.PerceptionReceipt`
- :class:`~zpe_video.receipt.Box`
- :func:`~zpe_video.receipt.encode_receipt`
- :func:`~zpe_video.receipt.decode_receipt`
- :func:`~zpe_video.receipt.receipt_hash`
- :func:`~zpe_video.receipt.verify_receipt`
- :func:`~zpe_video.receipt.read_receipt`
- :func:`~zpe_video.receipt.write_receipt`

Internal research harness (unstable, not part of the public wedge):

- :class:`~zpe_video.pipeline.Wave1Pipeline`
"""

from __future__ import annotations

from .receipt import (
    Box,
    CrossWriterMismatch,
    PerceptionReceipt,
    ReceiptCorrupted,
    WIRE_MAGIC,
    WIRE_VERSION,
    decode_receipt,
    encode_receipt,
    read_receipt,
    receipt_hash,
    verify_receipt,
    write_receipt,
)
from .pipeline import Wave1Pipeline

__version__ = "0.1.0"

__all__ = [
    "Box",
    "CrossWriterMismatch",
    "PerceptionReceipt",
    "ReceiptCorrupted",
    "Wave1Pipeline",
    "WIRE_MAGIC",
    "WIRE_VERSION",
    "__version__",
    "decode_receipt",
    "encode_receipt",
    "read_receipt",
    "receipt_hash",
    "verify_receipt",
    "write_receipt",
]
