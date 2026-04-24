#!/usr/bin/env python3
"""Receipt-core provenance benchmark for phase 09.4.1.1.2.2.

The benchmark is intentionally small and deterministic. It verifies the
commercial receipt-core authority metric without re-opening Phase 10:
cross-writer byte stability, fair commodity baselines, C2PA-style manifest
binding, and bounded non-claim language.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import struct
import sys
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from zpe_video import (  # noqa: E402
    WIRE_MAGIC,
    WIRE_VERSION,
    Box,
    PerceptionReceipt,
    build_receipt_manifest,
    encode_receipt,
    manifest_hash,
    receipt_hash,
    verify_manifest_binding,
    verify_receipt,
)

PHASE_ID = "09.4.1.1.2.2"
PHASE_NAME = "receipt-core-provenance-benchmark-and-c2pa-readiness"
BASELINE_COLUMNS = ["frame_index", "box_id", "label", "x", "y", "w", "h"]


@dataclass(frozen=True)
class BenchmarkCase:
    case_id: str
    content_id: str
    receipt: PerceptionReceipt
    scope: str


def _sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def _canonical_json_bytes(receipt: PerceptionReceipt) -> bytes:
    payload = {
        "frame_count": receipt.frame_count,
        "height": receipt.height,
        "width": receipt.width,
        "frames": [
            [
                {
                    "box_id": int(box.box_id),
                    "h": int(box.h),
                    "label": int(box.label),
                    "w": int(box.w),
                    "x": int(box.x),
                    "y": int(box.y),
                }
                for box in sorted(frame, key=lambda item: int(item.box_id))
            ]
            for frame in receipt.frames
        ],
    }
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )


def _raw_struct_zlib_bytes(receipt: PerceptionReceipt) -> bytes:
    payload = bytearray(struct.pack("<HHH", receipt.width, receipt.height, receipt.frame_count))
    for frame_index, frame in enumerate(receipt.frames):
        frame_payload = bytearray(struct.pack("<HB", frame_index, len(frame)))
        for box in sorted(frame, key=lambda item: int(item.box_id)):
            frame_payload += struct.pack(
                "<BBHHHH",
                int(box.box_id) & 0xFF,
                int(box.label) & 0xFF,
                int(box.x),
                int(box.y),
                int(box.w),
                int(box.h),
            )
        payload += frame_payload
    return zlib.compress(bytes(payload), level=9)


def _independent_receipt_encoder(receipt: PerceptionReceipt) -> bytes:
    out = bytearray(
        struct.pack(
            "<6sBHHHI",
            WIRE_MAGIC,
            WIRE_VERSION,
            receipt.width,
            receipt.height,
            receipt.frame_count,
            0,
        )
    )
    prev: dict[int, Box] = {}
    for frame_index, frame in enumerate(receipt.frames):
        sorted_frame = sorted(frame, key=lambda box: int(box.box_id))
        payload = bytearray([len(sorted_frame)])
        for box in sorted_frame:
            payload += bytes([int(box.box_id) & 0xFF, int(box.label) & 0xFF])
            prior = prev.get(int(box.box_id))
            if prior is None:
                payload.append(0)
                payload += struct.pack("<HHHH", int(box.x), int(box.y), int(box.w), int(box.h))
            else:
                payload.append(1)
                payload += struct.pack("<hh", int(box.x) - int(prior.x), int(box.y) - int(prior.y))
                payload += struct.pack("<HH", int(box.w), int(box.h))
        compressed = zlib.compress(bytes(payload), level=9)
        out += struct.pack(
            "<HBII",
            frame_index,
            1,
            len(compressed),
            zlib.crc32(compressed) & 0xFFFFFFFF,
        )
        out += compressed
        prev = {int(box.box_id): box for box in sorted_frame}
    return bytes(out)


def _parquet_pyarrow_bytes(receipt: PerceptionReceipt) -> tuple[bytes | None, str]:
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except Exception as exc:  # pragma: no cover - environment dependent
        return None, f"unavailable: {type(exc).__name__}: {exc}"

    rows: list[dict[str, int]] = []
    for frame_index, frame in enumerate(receipt.frames):
        for box in sorted(frame, key=lambda item: int(item.box_id)):
            rows.append(
                {
                    "frame_index": frame_index,
                    "box_id": int(box.box_id),
                    "label": int(box.label),
                    "x": int(box.x),
                    "y": int(box.y),
                    "w": int(box.w),
                    "h": int(box.h),
                }
            )
    schema = pa.schema([(name, pa.int64()) for name in BASELINE_COLUMNS])
    table = pa.Table.from_pylist(rows, schema=schema)
    sink = pa.BufferOutputStream()
    pq.write_table(table, sink)
    return sink.getvalue().to_pybytes(), "pyarrow.parquet.write_table defaults"


def _parquet_fastparquet_bytes(receipt: PerceptionReceipt) -> tuple[bytes | None, str]:
    try:
        import fastparquet
        import pandas as pd
    except Exception as exc:  # pragma: no cover - environment dependent
        return None, f"unavailable: {type(exc).__name__}: {exc}"

    rows: list[dict[str, int]] = []
    for frame_index, frame in enumerate(receipt.frames):
        for box in sorted(frame, key=lambda item: int(item.box_id)):
            rows.append(
                {
                    "frame_index": frame_index,
                    "box_id": int(box.box_id),
                    "label": int(box.label),
                    "x": int(box.x),
                    "y": int(box.y),
                    "w": int(box.w),
                    "h": int(box.h),
                }
            )
    import tempfile

    with tempfile.TemporaryDirectory() as tempdir:
        path = Path(tempdir) / "baseline.parquet"
        fastparquet.write(str(path), pd.DataFrame(rows, columns=BASELINE_COLUMNS))
        return path.read_bytes(), "fastparquet.write defaults"


def _cases() -> list[BenchmarkCase]:
    return [
        BenchmarkCase(
            case_id="candidate_b_holdout_motion",
            content_id="zpe-video://phase09.4.1.1.2.2/candidate_b_holdout_motion",
            scope="held-out object-memory motion fixture",
            receipt=PerceptionReceipt.from_frames(
                width=1280,
                height=720,
                frames=[
                    [
                        Box(box_id=7, x=24, y=80, w=44, h=90, label=1),
                        Box(box_id=2, x=400, y=120, w=80, h=64, label=3),
                    ],
                    [
                        Box(box_id=2, x=404, y=121, w=80, h=64, label=3),
                        Box(box_id=7, x=29, y=83, w=44, h=90, label=1),
                    ],
                    [Box(box_id=7, x=33, y=84, w=44, h=90, label=1)],
                ],
            ),
        ),
        BenchmarkCase(
            case_id="empty_receipt",
            content_id="zpe-video://phase09.4.1.1.2.2/empty_receipt",
            scope="empty limiting case",
            receipt=PerceptionReceipt(width=640, height=360, frame_count=0),
        ),
        BenchmarkCase(
            case_id="dense_receipt",
            content_id="zpe-video://phase09.4.1.1.2.2/dense_receipt",
            scope="dense multi-track limiting case",
            receipt=PerceptionReceipt.from_frames(
                width=1920,
                height=1080,
                frames=[
                    [
                        Box(box_id=i, x=10 + 12 * i, y=20 + 7 * i, w=30, h=40, label=i % 5)
                        for i in range(12)
                    ],
                    [
                        Box(
                            box_id=i,
                            x=12 + 12 * i,
                            y=21 + 7 * i,
                            w=30,
                            h=40,
                            label=i % 5,
                        )
                        for i in reversed(range(12))
                    ],
                ],
            ),
        ),
    ]


def _case_result(case: BenchmarkCase) -> dict[str, Any]:
    zpe_library = encode_receipt(case.receipt)
    zpe_independent = _independent_receipt_encoder(case.receipt)
    canonical_json = _canonical_json_bytes(case.receipt)
    canonical_json_zlib = zlib.compress(canonical_json, level=9)
    raw_struct_zlib = _raw_struct_zlib_bytes(case.receipt)
    parquet_pyarrow, parquet_pyarrow_note = _parquet_pyarrow_bytes(case.receipt)
    parquet_fastparquet, parquet_fastparquet_note = _parquet_fastparquet_bytes(case.receipt)

    verify_receipt(zpe_library, expected_peer_blob=zpe_independent)
    manifest = build_receipt_manifest(
        zpe_library,
        content_id=case.content_id,
        metadata={"phase": PHASE_ID, "case_id": case.case_id},
    )
    verify_manifest_binding(manifest, zpe_library, expected_content_id=case.content_id)

    baselines: dict[str, dict[str, Any]] = {
        "zpe_library": {
            "available": True,
            "bytes": len(zpe_library),
            "sha256": receipt_hash(zpe_library),
            "receipt_grade": True,
        },
        "zpe_independent": {
            "available": True,
            "bytes": len(zpe_independent),
            "sha256": receipt_hash(zpe_independent),
            "receipt_grade": True,
        },
        "canonical_json": {
            "available": True,
            "bytes": len(canonical_json),
            "sha256": _sha256_bytes(canonical_json),
            "receipt_grade": False,
            "note": "canonical and stable, but no wire version or per-frame CRC",
        },
        "canonical_json_zlib": {
            "available": True,
            "bytes": len(canonical_json_zlib),
            "sha256": _sha256_bytes(canonical_json_zlib),
            "receipt_grade": False,
            "note": "canonical and compressed, but no wire version or per-frame CRC",
        },
        "raw_struct_zlib": {
            "available": True,
            "bytes": len(raw_struct_zlib),
            "sha256": _sha256_bytes(raw_struct_zlib),
            "receipt_grade": False,
            "note": "small deterministic control, but no receipt envelope, no versioned schema, no per-frame CRC",
        },
        "parquet_pyarrow_default": _optional_baseline(parquet_pyarrow, parquet_pyarrow_note),
        "parquet_fastparquet_default": _optional_baseline(
            parquet_fastparquet, parquet_fastparquet_note
        ),
    }
    baselines["tuned_deterministic_json_control"] = baselines["canonical_json"]

    return {
        "case_id": case.case_id,
        "content_id": case.content_id,
        "scope": case.scope,
        "manifest_sha256": manifest_hash(manifest),
        "manifest_byte_length": len(manifest.to_bytes()),
        "manifest_binding_verified": True,
        "receipt_hash_stable": receipt_hash(zpe_library) == receipt_hash(zpe_independent),
        "receipt_bytes_identical": zpe_library == zpe_independent,
        "baselines": baselines,
    }


def _optional_baseline(blob: bytes | None, note: str) -> dict[str, Any]:
    if blob is None:
        return {
            "available": False,
            "bytes": None,
            "sha256": None,
            "receipt_grade": False,
            "note": note,
        }
    return {
        "available": True,
        "bytes": len(blob),
        "sha256": _sha256_bytes(blob),
        "receipt_grade": False,
        "note": note,
    }


def run_benchmark(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    cases = [_case_result(case) for case in _cases()]
    parquet_pairs_available = all(
        case["baselines"]["parquet_pyarrow_default"]["available"]
        and case["baselines"]["parquet_fastparquet_default"]["available"]
        for case in cases
    )
    parquet_default_cross_writer_all = (
        all(
            case["baselines"]["parquet_pyarrow_default"]["sha256"]
            == case["baselines"]["parquet_fastparquet_default"]["sha256"]
            for case in cases
        )
        if parquet_pairs_available
        else None
    )
    zpe_receipt_cross_writer_all = all(case["receipt_bytes_identical"] for case in cases)
    manifest_binding_all = all(case["manifest_binding_verified"] for case in cases)
    tuned_controls_close_storage_gap = any(
        case["baselines"]["raw_struct_zlib"]["bytes"] < case["baselines"]["zpe_library"]["bytes"]
        for case in cases
    )

    verdict = "pass" if zpe_receipt_cross_writer_all and manifest_binding_all else "fail"
    summary = {
        "phase": PHASE_ID,
        "phase_name": PHASE_NAME,
        "benchmark": "receipt_core_provenance_manifest_binding",
        "case_count": len(cases),
        "cases": cases,
        "summary": {
            "zpe_receipt_cross_writer_stable_all_cases": zpe_receipt_cross_writer_all,
            "manifest_binding_verified_all_cases": manifest_binding_all,
            "parquet_default_cross_writer_stable_all_cases": parquet_default_cross_writer_all,
            "parquet_pair_available_all_cases": parquet_pairs_available,
            "tuned_controls_close_storage_gap": tuned_controls_close_storage_gap,
            "tuned_controls_note": "raw struct + zlib can be smaller but is not receipt-grade; storage alone is not the receipt authority metric",
        },
        "verdict": verdict,
        "sovereign_gate_status": "red",
        "sovereign_gate_note": "This benchmark supports only the commercial receipt-core wedge. It does not execute Phase 10, prove Compass-8 primitive-native closure, or qualify Red Magic runtime.",
        "forbidden_proxies_rejected": {
            "phase_10_execution_claim": False,
            "primitive_native_closure_claim": False,
            "red_magic_runtime_claim": False,
            "storage_only_claim": False,
            "parquet_never_stable_claim": False,
        },
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    _write_baseline_table(output_dir / "baseline_table.csv", cases)
    _write_manifest_table(output_dir / "manifest_binding.json", cases)
    return summary


def _write_baseline_table(path: Path, cases: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "case_id",
                "baseline",
                "available",
                "bytes",
                "sha256",
                "receipt_grade",
                "note",
            ],
        )
        writer.writeheader()
        for case in cases:
            for name, baseline in case["baselines"].items():
                writer.writerow(
                    {
                        "case_id": case["case_id"],
                        "baseline": name,
                        "available": baseline["available"],
                        "bytes": baseline["bytes"],
                        "sha256": baseline["sha256"],
                        "receipt_grade": baseline["receipt_grade"],
                        "note": baseline.get("note", ""),
                    }
                )


def _write_manifest_table(path: Path, cases: list[dict[str, Any]]) -> None:
    payload = {
        "phase": PHASE_ID,
        "manifest_binding_verified_all_cases": all(
            case["manifest_binding_verified"] for case in cases
        ),
        "cases": [
            {
                "case_id": case["case_id"],
                "content_id": case["content_id"],
                "manifest_sha256": case["manifest_sha256"],
                "manifest_byte_length": case["manifest_byte_length"],
                "manifest_binding_verified": case["manifest_binding_verified"],
            }
            for case in cases
        ],
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT
        / "docs"
        / "transparency"
        / "phase09_4_1_1_2_2_receipt_core_provenance_benchmark",
    )
    args = parser.parse_args()
    summary = run_benchmark(args.output_dir)
    print(json.dumps({"output_dir": str(args.output_dir), "verdict": summary["verdict"]}))
    return 0 if summary["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
