"""C2PA-style manifest binding for ZPE perception receipts.

The receipt blob stays the authority surface. A manifest is an external
envelope that references the receipt by SHA-256 and byte length, so it can
be signed or embedded by a downstream C2PA pipeline without changing the
receipt bytes.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from .receipt import WIRE_MAGIC, WIRE_VERSION, receipt_hash, verify_receipt

MANIFEST_PROFILE = "zpe-video.perception-receipt-manifest.v1"
MANIFEST_ASSERTION = "org.zer0pa.zpe.video.perception_receipt"

__all__ = [
    "MANIFEST_ASSERTION",
    "MANIFEST_PROFILE",
    "ReceiptManifest",
    "build_receipt_manifest",
    "decode_manifest",
    "manifest_hash",
    "verify_manifest_binding",
]


def _canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    """Serialize as deterministic JSON suitable for hashing/signing."""
    return json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _validate_sha256(value: str, field_name: str) -> None:
    if len(value) != 64:
        raise ValueError(f"{field_name} must be a 64-character SHA-256 hex digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a SHA-256 hex digest") from exc


@dataclass(frozen=True)
class ReceiptManifest:
    """External manifest reference for one perception receipt.

    The manifest intentionally stores the receipt hash, byte length, and
    wire-format identity, but never embeds raw receipt bytes or mutable
    writer/runtime metadata in the receipt authority surface.
    """

    receipt_sha256: str
    receipt_byte_length: int
    content_id: str
    assertion: str = MANIFEST_ASSERTION
    profile: str = MANIFEST_PROFILE
    hash_algorithm: str = "sha256"
    wire_magic: str = WIRE_MAGIC.decode("ascii")
    wire_version: int = WIRE_VERSION
    media_sha256: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_sha256(self.receipt_sha256, "receipt_sha256")
        if self.media_sha256 is not None:
            _validate_sha256(self.media_sha256, "media_sha256")
        if self.receipt_byte_length < 0:
            raise ValueError("receipt_byte_length must be non-negative")
        if not self.content_id:
            raise ValueError("content_id must be non-empty")
        if self.hash_algorithm != "sha256":
            raise ValueError("hash_algorithm must be sha256")
        if self.wire_magic != WIRE_MAGIC.decode("ascii"):
            raise ValueError(f"wire_magic must be {WIRE_MAGIC.decode('ascii')}")
        if self.wire_version != WIRE_VERSION:
            raise ValueError(f"wire_version must be {WIRE_VERSION}")

    def to_dict(self) -> dict[str, Any]:
        """Return the manifest as plain JSON-compatible data."""
        payload: dict[str, Any] = {
            "assertion": self.assertion,
            "content_id": self.content_id,
            "hash_algorithm": self.hash_algorithm,
            "profile": self.profile,
            "receipt_byte_length": int(self.receipt_byte_length),
            "receipt_sha256": self.receipt_sha256,
            "wire_magic": self.wire_magic,
            "wire_version": int(self.wire_version),
        }
        if self.media_sha256 is not None:
            payload["media_sha256"] = self.media_sha256
        if self.metadata:
            payload["metadata"] = dict(sorted(self.metadata.items()))
        return payload

    def to_bytes(self) -> bytes:
        """Return deterministic canonical JSON bytes."""
        return _canonical_json_bytes(self.to_dict())

    @classmethod
    def from_bytes(cls, blob: bytes) -> ReceiptManifest:
        """Parse canonical or non-canonical JSON manifest bytes."""
        try:
            data = json.loads(blob.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"manifest is not valid UTF-8 JSON: {exc}") from exc
        if not isinstance(data, dict):
            raise ValueError("manifest root must be a JSON object")
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> ReceiptManifest:
        """Construct a manifest from mapping data."""
        metadata = data.get("metadata", {})
        if metadata is None:
            metadata = {}
        if not isinstance(metadata, Mapping):
            raise ValueError("metadata must be an object when present")
        return cls(
            receipt_sha256=str(data["receipt_sha256"]),
            receipt_byte_length=int(data["receipt_byte_length"]),
            content_id=str(data["content_id"]),
            assertion=str(data.get("assertion", MANIFEST_ASSERTION)),
            profile=str(data.get("profile", MANIFEST_PROFILE)),
            hash_algorithm=str(data.get("hash_algorithm", "sha256")),
            wire_magic=str(data.get("wire_magic", WIRE_MAGIC.decode("ascii"))),
            wire_version=int(data.get("wire_version", WIRE_VERSION)),
            media_sha256=(None if data.get("media_sha256") is None else str(data["media_sha256"])),
            metadata={str(k): str(v) for k, v in metadata.items()},
        )


def build_receipt_manifest(
    receipt_blob: bytes,
    *,
    content_id: str,
    media_sha256: str | None = None,
    metadata: Mapping[str, str] | None = None,
) -> ReceiptManifest:
    """Build a manifest that binds to ``receipt_blob`` by hash and length."""
    verify_receipt(receipt_blob)
    return ReceiptManifest(
        receipt_sha256=receipt_hash(receipt_blob),
        receipt_byte_length=len(receipt_blob),
        content_id=content_id,
        media_sha256=media_sha256,
        metadata={} if metadata is None else dict(metadata),
    )


def decode_manifest(blob: bytes) -> ReceiptManifest:
    """Parse manifest JSON into a validated ``ReceiptManifest``."""
    return ReceiptManifest.from_bytes(blob)


def manifest_hash(manifest: ReceiptManifest | bytes) -> str:
    """Return the SHA-256 of canonical manifest bytes."""
    if isinstance(manifest, ReceiptManifest):
        return receipt_hash(manifest.to_bytes())
    return receipt_hash(decode_manifest(manifest).to_bytes())


def verify_manifest_binding(
    manifest: ReceiptManifest | bytes,
    receipt_blob: bytes,
    *,
    expected_content_id: str | None = None,
) -> ReceiptManifest:
    """Verify that ``manifest`` references ``receipt_blob`` exactly."""
    decoded = decode_manifest(manifest) if isinstance(manifest, bytes) else manifest
    verify_receipt(receipt_blob, expected_hash=decoded.receipt_sha256)
    if decoded.receipt_byte_length != len(receipt_blob):
        raise ValueError(
            "manifest receipt_byte_length mismatch: "
            f"expected {decoded.receipt_byte_length}, got {len(receipt_blob)}"
        )
    if expected_content_id is not None and decoded.content_id != expected_content_id:
        raise ValueError(
            "manifest content_id mismatch: "
            f"expected {expected_content_id!r}, got {decoded.content_id!r}"
        )
    return decoded
