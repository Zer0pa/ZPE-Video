from __future__ import annotations

import json

import pytest

from zpe_video import (
    Box,
    PerceptionReceipt,
    ReceiptManifest,
    build_receipt_manifest,
    decode_manifest,
    encode_receipt,
    manifest_hash,
    receipt_hash,
    verify_manifest_binding,
)


def _receipt_blob() -> bytes:
    receipt = PerceptionReceipt.from_frames(
        width=640,
        height=360,
        frames=[
            [Box(box_id=2, x=30, y=40, w=20, h=30, label=1)],
            [Box(box_id=2, x=31, y=41, w=20, h=30, label=1)],
        ],
    )
    return encode_receipt(receipt)


def test_manifest_binds_receipt_without_mutating_receipt_bytes():
    blob = _receipt_blob()
    before_hash = receipt_hash(blob)

    manifest = build_receipt_manifest(blob, content_id="video://case-001")

    assert receipt_hash(blob) == before_hash
    assert manifest.receipt_sha256 == before_hash
    assert manifest.receipt_byte_length == len(blob)
    assert verify_manifest_binding(manifest, blob).content_id == "video://case-001"


def test_manifest_canonical_bytes_are_stable_across_metadata_order():
    blob = _receipt_blob()
    a = build_receipt_manifest(
        blob,
        content_id="video://case-001",
        metadata={"writer": "reference", "benchmark": "receipt-core"},
    )
    b = build_receipt_manifest(
        blob,
        content_id="video://case-001",
        metadata={"benchmark": "receipt-core", "writer": "reference"},
    )

    assert a.to_bytes() == b.to_bytes()
    assert manifest_hash(a) == manifest_hash(b)


def test_manifest_json_contains_hash_not_receipt_payload():
    blob = _receipt_blob()
    manifest = build_receipt_manifest(blob, content_id="video://case-001")
    payload = json.loads(manifest.to_bytes().decode("utf-8"))

    assert payload["receipt_sha256"] == receipt_hash(blob)
    assert payload["receipt_byte_length"] == len(blob)
    assert "receipt_blob" not in payload
    assert "payload" not in payload


def test_decode_manifest_accepts_noncanonical_json_but_rehashes_canonical():
    blob = _receipt_blob()
    manifest = build_receipt_manifest(blob, content_id="video://case-001")
    raw = json.dumps(manifest.to_dict(), indent=2).encode("utf-8")

    decoded = decode_manifest(raw)

    assert decoded == manifest
    assert manifest_hash(raw) == manifest_hash(manifest)


def test_manifest_binding_rejects_wrong_receipt():
    blob = _receipt_blob()
    other = encode_receipt(
        PerceptionReceipt.from_frames(
            width=640,
            height=360,
            frames=[[Box(box_id=2, x=99, y=40, w=20, h=30, label=1)]],
        )
    )
    manifest = build_receipt_manifest(blob, content_id="video://case-001")

    with pytest.raises(Exception, match="hash mismatch"):
        verify_manifest_binding(manifest, other)


def test_manifest_binding_rejects_wrong_content_id():
    blob = _receipt_blob()
    manifest = build_receipt_manifest(blob, content_id="video://case-001")

    with pytest.raises(ValueError, match="content_id mismatch"):
        verify_manifest_binding(manifest, blob, expected_content_id="video://case-002")


def test_manifest_constructor_validates_sha256():
    with pytest.raises(ValueError, match="SHA-256"):
        ReceiptManifest(
            receipt_sha256="not-a-digest",
            receipt_byte_length=10,
            content_id="video://case-001",
        )
