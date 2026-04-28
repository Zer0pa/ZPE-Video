#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shlex
import struct
import sys
import zlib
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

import measure_am_c01 as h0  # noqa: E402


@dataclass
class SparsePrimitive:
    box_id: int
    label: int
    x: int
    y: int
    w: int
    h: int
    points: list[tuple[int, int]] = field(default_factory=list)
    patch_values: list[int] = field(default_factory=list)
    patch_width: int = 0
    patch_height: int = 0
    patch_channels: int = 0
    patch_bits: int = 0


@dataclass(frozen=True)
class PatchSpec:
    width: int
    height: int
    quant_levels: int
    channels: int = 3
    margin_ratio: float = 0.0

    @property
    def quant_bits(self) -> int:
        levels = int(self.quant_levels)
        if levels <= 1 or (levels & (levels - 1)) != 0:
            raise ValueError(f"PATCH_LEVELS_MUST_BE_POWER_OF_TWO:{levels}")
        return levels.bit_length() - 1


@dataclass(frozen=True)
class PatchPlan:
    variants: tuple[tuple[int, PatchSpec], ...]

    @classmethod
    def fixed(cls, patch_spec: PatchSpec) -> PatchPlan:
        return cls(variants=((0, patch_spec),))

    def select(self, box: object) -> PatchSpec:
        box_area = int(box.w) * int(box.h)
        for min_area, patch_spec in self.variants:
            if box_area >= int(min_area):
                return patch_spec
        return self.variants[-1][1]

    def describe(self) -> str:
        parts = [
            f"{min_area}:{spec.width}x{spec.height}x{spec.channels}@{spec.quant_levels}"
            for min_area, spec in self.variants
        ]
        return ",".join(parts)


@dataclass(frozen=True)
class SparseRepresentationSpec:
    name: str
    measurement_type: str
    notes: str
    include_contour: bool
    draw_contour: bool
    patch_plan: PatchPlan | None = None
    line_thickness: int = 2


@dataclass
class RepresentationResult:
    name: str
    measurement_type: str
    frames: list[np.ndarray]
    size_bytes: int
    artifact_path: Path
    background_policy: str
    notes: str
    diagnostics: dict[str, object] = field(default_factory=dict)


_HEADER_STRUCT = struct.Struct("<8sHHH")
_FRAME_STRUCT = struct.Struct("<I")
_PRIMITIVE_STRUCT = struct.Struct("<HBBBBBBHHHH")


def _gray_array(frame_bytes: bytes, width: int, height: int) -> np.ndarray:
    return np.frombuffer(frame_bytes, dtype=np.uint8).reshape(height, width)


def _mean_value(values: list[float]) -> float:
    if not values:
        return 0.0
    return float(sum(values) / len(values))


def _compute_patch_grid(
    roi: np.ndarray, patch_spec: PatchSpec
) -> tuple[list[int], int, int, int, int]:
    import cv2  # type: ignore

    if roi.size == 0:
        return [], 0, 0, 0, 0

    if patch_spec.channels not in (1, 3):
        raise ValueError(f"UNSUPPORTED_PATCH_CHANNELS:{patch_spec.channels}")

    source = roi
    if source.ndim == 2 and patch_spec.channels == 3:
        source = np.repeat(source[:, :, None], 3, axis=2)
    elif source.ndim == 3 and patch_spec.channels == 1:
        source = np.asarray(Image.fromarray(source).convert("L"), dtype=np.uint8)

    resized = cv2.resize(
        source, (patch_spec.width, patch_spec.height), interpolation=cv2.INTER_AREA
    )
    quant_step = 255.0 / float(patch_spec.quant_levels - 1)
    quantized = np.clip(
        np.round(resized.astype(np.float32) / quant_step),
        0,
        patch_spec.quant_levels - 1,
    ).astype(np.uint8)
    return (
        [int(value) for value in quantized.reshape(-1)],
        patch_spec.width,
        patch_spec.height,
        patch_spec.channels,
        patch_spec.quant_bits,
    )


def _pack_patch_values(values: list[int], patch_bits: int) -> bytes:
    if not values or patch_bits <= 0:
        return b""
    if patch_bits == 8:
        return bytes(value & 0xFF for value in values)
    mask = (1 << patch_bits) - 1
    payload = bytearray()
    bit_buffer = 0
    buffered_bits = 0
    for value in values:
        bit_buffer = (bit_buffer << patch_bits) | (int(value) & mask)
        buffered_bits += patch_bits
        while buffered_bits >= 8:
            buffered_bits -= 8
            payload.append((bit_buffer >> buffered_bits) & 0xFF)
            bit_buffer &= (1 << buffered_bits) - 1
    if buffered_bits > 0:
        payload.append((bit_buffer << (8 - buffered_bits)) & 0xFF)
    return bytes(payload)


def _unpack_patch_values(payload: bytes, value_count: int, patch_bits: int) -> list[int]:
    if value_count <= 0 or patch_bits <= 0:
        return []
    if patch_bits == 8:
        return [int(value) for value in payload[:value_count]]
    mask = (1 << patch_bits) - 1
    values: list[int] = []
    bit_buffer = 0
    buffered_bits = 0
    for byte in payload:
        bit_buffer = (bit_buffer << 8) | int(byte)
        buffered_bits += 8
        while buffered_bits >= patch_bits and len(values) < value_count:
            buffered_bits -= patch_bits
            values.append((bit_buffer >> buffered_bits) & mask)
            bit_buffer &= (1 << buffered_bits) - 1
        if len(values) >= value_count:
            break
    if len(values) != value_count:
        raise ValueError(f"PATCH_VALUE_COUNT_MISMATCH:{len(values)}:{value_count}")
    return values


def _resolve_roi_bounds(
    *,
    frame_width: int,
    frame_height: int,
    box: object,
    margin_ratio: float,
) -> tuple[int, int, int, int]:
    margin_x = int(round(float(box.w) * max(0.0, margin_ratio)))
    margin_y = int(round(float(box.h) * max(0.0, margin_ratio)))
    x0 = max(0, int(box.x) - margin_x)
    y0 = max(0, int(box.y) - margin_y)
    x1 = min(frame_width, int(box.x + box.w) + margin_x)
    y1 = min(frame_height, int(box.y + box.h) + margin_y)
    return x0, y0, x1, y1


def _rectangle_points(x0: int, y0: int, x1: int, y1: int) -> list[tuple[int, int]]:
    return [
        (x0, y0),
        (x1 - 1, y0),
        (x1 - 1, y1 - 1),
        (x0, y1 - 1),
    ]


def _extract_sparse_primitive(
    gray: np.ndarray,
    box: object,
    *,
    include_contour: bool,
    patch_plan: PatchPlan | None,
    patch_source: np.ndarray | None,
) -> SparsePrimitive | None:
    import cv2  # type: ignore

    patch_spec = patch_plan.select(box) if patch_plan is not None else None
    margin_ratio = patch_spec.margin_ratio if patch_spec is not None else 0.0
    x0, y0, x1, y1 = _resolve_roi_bounds(
        frame_width=gray.shape[1],
        frame_height=gray.shape[0],
        box=box,
        margin_ratio=margin_ratio,
    )
    if x1 <= x0 or y1 <= y0:
        return None

    points: list[tuple[int, int]] = []
    if include_contour:
        roi = gray[y0:y1, x0:x1]
        if roi.size == 0:
            return None
        blurred = cv2.GaussianBlur(roi, (3, 3), 0)
        edges = cv2.Canny(blurred, 40, 120)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        best_contour = None
        best_score = -1.0
        for contour in contours:
            area = float(abs(cv2.contourArea(contour)))
            perimeter = float(cv2.arcLength(contour, True))
            if area < 4.0 and perimeter < 16.0:
                continue
            score = max(area, perimeter)
            if score > best_score:
                best_score = score
                best_contour = contour

        if best_contour is not None:
            epsilon = max(1.0, 0.02 * float(cv2.arcLength(best_contour, True)))
            approx = cv2.approxPolyDP(best_contour, epsilon, True)
            for point in approx[:, 0, :]:
                px = x0 + int(point[0])
                py = y0 + int(point[1])
                if not points or points[-1] != (px, py):
                    points.append((px, py))
        elif patch_spec is not None:
            points = _rectangle_points(x0, y0, x1, y1)

        if len(points) == 1:
            points = []

    patch_values: list[int] = []
    patch_width = 0
    patch_height = 0
    patch_channels = 0
    patch_bits = 0
    if patch_spec is not None and patch_source is not None:
        (
            patch_values,
            patch_width,
            patch_height,
            patch_channels,
            patch_bits,
        ) = _compute_patch_grid(patch_source[y0:y1, x0:x1], patch_spec)

    if not points and not patch_values:
        return None

    return SparsePrimitive(
        box_id=int(box.box_id),
        label=int(box.label),
        x=x0,
        y=y0,
        w=max(1, x1 - x0),
        h=max(1, y1 - y0),
        points=points,
        patch_values=patch_values,
        patch_width=patch_width,
        patch_height=patch_height,
        patch_channels=patch_channels,
        patch_bits=patch_bits,
    )


def _extract_sparse_frames(
    gray_frames: list[bytes],
    source_boxes: list[list[object]],
    *,
    width: int,
    height: int,
    include_contour: bool,
    patch_plan: PatchPlan | None,
    patch_rgb_frames: list[np.ndarray] | None = None,
) -> list[list[SparsePrimitive]]:
    frames: list[list[SparsePrimitive]] = []
    for frame_idx, frame_bytes in enumerate(gray_frames):
        gray = _gray_array(frame_bytes, width, height)
        patch_source = patch_rgb_frames[frame_idx] if patch_rgb_frames is not None else None
        frame_primitives: list[SparsePrimitive] = []
        for box in source_boxes[frame_idx]:
            primitive = _extract_sparse_primitive(
                gray,
                box,
                include_contour=include_contour,
                patch_plan=patch_plan,
                patch_source=patch_source,
            )
            if primitive is None:
                continue
            frame_primitives.append(primitive)
        frames.append(frame_primitives)
    return frames


def _serialize_sparse_frames(
    sparse_frames: list[list[SparsePrimitive]],
    *,
    width: int,
    height: int,
    output_path: Path,
) -> int:
    blob = bytearray()
    blob.extend(_HEADER_STRUCT.pack(b"ZPESPR02", width, height, len(sparse_frames)))
    for frame in sparse_frames:
        payload = bytearray()
        payload.extend(struct.pack("<H", len(frame)))
        for primitive in frame:
            point_count = min(len(primitive.points), 255)
            packed_patch = _pack_patch_values(primitive.patch_values, primitive.patch_bits)
            payload.extend(
                _PRIMITIVE_STRUCT.pack(
                    primitive.box_id & 0xFFFF,
                    primitive.label & 0xFF,
                    point_count,
                    primitive.patch_width & 0xFF,
                    primitive.patch_height & 0xFF,
                    primitive.patch_channels & 0xFF,
                    primitive.patch_bits & 0xFF,
                    primitive.x,
                    primitive.y,
                    primitive.w,
                    primitive.h,
                )
            )
            for x, y in primitive.points[:point_count]:
                payload.extend(struct.pack("<HH", x, y))
            payload.extend(packed_patch)
        compressed = zlib.compress(bytes(payload), level=9)
        blob.extend(_FRAME_STRUCT.pack(len(compressed)))
        blob.extend(compressed)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(bytes(blob))
    return len(blob)


def _deserialize_sparse_frames(blob: bytes) -> tuple[int, int, list[list[SparsePrimitive]]]:
    if len(blob) < _HEADER_STRUCT.size:
        raise ValueError("SPARSE_HEADER_TRUNCATED")
    magic, width, height, frame_count = _HEADER_STRUCT.unpack_from(blob, 0)
    if magic != b"ZPESPR02":
        raise ValueError(f"BAD_SPARSE_MAGIC:{magic!r}")
    offset = _HEADER_STRUCT.size
    sparse_frames: list[list[SparsePrimitive]] = []
    for _ in range(frame_count):
        if offset + _FRAME_STRUCT.size > len(blob):
            raise ValueError("SPARSE_FRAME_HEADER_TRUNCATED")
        payload_len = _FRAME_STRUCT.unpack_from(blob, offset)[0]
        offset += _FRAME_STRUCT.size
        if offset + payload_len > len(blob):
            raise ValueError("SPARSE_PAYLOAD_TRUNCATED")
        payload = zlib.decompress(blob[offset : offset + payload_len])
        offset += payload_len
        payload_offset = 0
        if payload_offset + 2 > len(payload):
            raise ValueError("SPARSE_COUNT_TRUNCATED")
        primitive_count = struct.unpack_from("<H", payload, payload_offset)[0]
        payload_offset += 2
        frame_primitives: list[SparsePrimitive] = []
        for _ in range(primitive_count):
            if payload_offset + _PRIMITIVE_STRUCT.size > len(payload):
                raise ValueError("SPARSE_PRIMITIVE_TRUNCATED")
            (
                box_id,
                label,
                point_count,
                patch_width,
                patch_height,
                patch_channels,
                patch_bits,
                x,
                y,
                w,
                h,
            ) = _PRIMITIVE_STRUCT.unpack_from(
                payload,
                payload_offset,
            )
            payload_offset += _PRIMITIVE_STRUCT.size
            points: list[tuple[int, int]] = []
            for _ in range(point_count):
                if payload_offset + 4 > len(payload):
                    raise ValueError("SPARSE_POINT_TRUNCATED")
                px, py = struct.unpack_from("<HH", payload, payload_offset)
                payload_offset += 4
                points.append((int(px), int(py)))
            patch_value_count = int(patch_width) * int(patch_height) * int(patch_channels)
            patch_byte_len = (
                ((patch_value_count * int(patch_bits)) + 7) // 8
                if patch_value_count and patch_bits
                else 0
            )
            if payload_offset + patch_byte_len > len(payload):
                raise ValueError("SPARSE_PATCH_TRUNCATED")
            patch_values = _unpack_patch_values(
                payload[payload_offset : payload_offset + patch_byte_len],
                patch_value_count,
                int(patch_bits),
            )
            payload_offset += patch_byte_len
            frame_primitives.append(
                SparsePrimitive(
                    box_id=int(box_id),
                    label=int(label),
                    x=int(x),
                    y=int(y),
                    w=int(w),
                    h=int(h),
                    points=points,
                    patch_values=patch_values,
                    patch_width=int(patch_width),
                    patch_height=int(patch_height),
                    patch_channels=int(patch_channels),
                    patch_bits=int(patch_bits),
                )
            )
        sparse_frames.append(frame_primitives)
    return width, height, sparse_frames


def _decode_patch_array(primitive: SparsePrimitive) -> np.ndarray | None:
    if (
        not primitive.patch_values
        or primitive.patch_width <= 0
        or primitive.patch_height <= 0
        or primitive.patch_bits <= 0
    ):
        return None
    scale = 255.0 / float((1 << primitive.patch_bits) - 1)
    patch_array = np.asarray(primitive.patch_values, dtype=np.float32) * scale
    patch_array = np.clip(np.round(patch_array), 0, 255).astype(np.uint8)
    if primitive.patch_channels == 1:
        return patch_array.reshape(primitive.patch_height, primitive.patch_width)
    if primitive.patch_channels == 3:
        return patch_array.reshape(primitive.patch_height, primitive.patch_width, 3)
    raise ValueError(f"UNSUPPORTED_PATCH_CHANNELS:{primitive.patch_channels}")


def _render_sparse_frames(
    sparse_frames: list[list[SparsePrimitive]],
    *,
    width: int,
    height: int,
    draw_contour: bool,
    line_thickness: int = 2,
) -> list[np.ndarray]:
    import cv2  # type: ignore

    rendered_frames: list[np.ndarray] = []
    for frame in sparse_frames:
        canvas_gray = np.full((height, width), 128, dtype=np.uint8)
        canvas_rgb = np.repeat(canvas_gray[:, :, None], 3, axis=2)
        for primitive in frame:
            x0 = max(0, min(width - 1, primitive.x))
            y0 = max(0, min(height - 1, primitive.y))
            w = max(1, min(width - x0, primitive.w))
            h = max(1, min(height - y0, primitive.h))
            patch_array = _decode_patch_array(primitive)
            if patch_array is not None:
                fill = cv2.resize(patch_array, (w, h), interpolation=cv2.INTER_LINEAR)
                if fill.ndim == 2:
                    fill = np.repeat(fill[:, :, None], 3, axis=2)
                canvas_rgb[y0 : y0 + h, x0 : x0 + w] = fill
            if draw_contour and len(primitive.points) >= 2:
                pts = np.asarray(primitive.points, dtype=np.int32).reshape((-1, 1, 2))
                cv2.polylines(
                    canvas_rgb, [pts], True, color=(245, 245, 245), thickness=line_thickness
                )
        rendered_frames.append(canvas_rgb.astype(np.uint8))
    return rendered_frames


def _run_sparse_representation(
    artifact_root: Path,
    *,
    spec: SparseRepresentationSpec,
    gray_frames: list[bytes],
    rgb_frames: list[np.ndarray] | None,
    source_boxes: list[list[object]],
    width: int,
    height: int,
) -> RepresentationResult:
    rep_root = artifact_root / "representations" / spec.name
    sparse_frames = _extract_sparse_frames(
        gray_frames,
        source_boxes,
        width=width,
        height=height,
        include_contour=spec.include_contour,
        patch_plan=spec.patch_plan,
        patch_rgb_frames=rgb_frames if spec.patch_plan is not None else None,
    )
    artifact_path = rep_root / f"{spec.name}.bin"
    size_bytes = _serialize_sparse_frames(
        sparse_frames, width=width, height=height, output_path=artifact_path
    )
    _, _, decoded_frames = _deserialize_sparse_frames(artifact_path.read_bytes())
    rendered_frames = _render_sparse_frames(
        decoded_frames,
        width=width,
        height=height,
        draw_contour=spec.draw_contour,
        line_thickness=spec.line_thickness,
    )
    patch_histogram: dict[str, int] = {}
    for frame in decoded_frames:
        for primitive in frame:
            if primitive.patch_width <= 0 or primitive.patch_height <= 0:
                continue
            key = f"{primitive.patch_width}x{primitive.patch_height}x{primitive.patch_channels}"
            patch_histogram[key] = patch_histogram.get(key, 0) + 1
    dominant_patch_grid = ""
    if patch_histogram:
        dominant_patch_grid = max(patch_histogram.items(), key=lambda item: item[1])[0]
    return RepresentationResult(
        name=spec.name,
        measurement_type=spec.measurement_type,
        frames=rendered_frames,
        size_bytes=size_bytes,
        artifact_path=artifact_path,
        background_policy="neutral_gray_128",
        notes=spec.notes,
        diagnostics={
            "frame_primitive_counts": [len(frame) for frame in decoded_frames],
            "primitive_count_mean": _mean_value([float(len(frame)) for frame in decoded_frames]),
            "include_contour": spec.include_contour,
            "draw_contour": spec.draw_contour,
            "patch_plan": spec.patch_plan.describe() if spec.patch_plan is not None else "none",
            "patch_quant_levels": spec.patch_plan.variants[0][1].quant_levels
            if spec.patch_plan is not None
            else 0,
            "patch_channels": spec.patch_plan.variants[0][1].channels
            if spec.patch_plan is not None
            else 0,
            "patch_histogram": patch_histogram,
            "dominant_patch_grid": dominant_patch_grid,
        },
    )


def _run_box_representation(
    artifact_root: Path,
    *,
    gray_frames: list[bytes],
    source_boxes: list[list[object]],
    width: int,
    height: int,
    frame_rate: int,
    SequenceData: object,
    encode_sequence: object,
    decode_sequence: object,
    reconstruct_frame: object,
    gt_frames: list[list[object]],
    iou: object,
) -> RepresentationResult:
    zpe_frames, zpe_bitrate_bytes, zpe_stream_path = h0._run_zpe_path(
        artifact_root,
        width=width,
        height=height,
        frame_rate=frame_rate,
        gray_frames=gray_frames,
        source_boxes=source_boxes,
        SequenceData=SequenceData,
        encode_sequence=encode_sequence,
        decode_sequence=decode_sequence,
        reconstruct_frame=reconstruct_frame,
    )
    decoded = decode_sequence(str(zpe_stream_path), tolerate_corruption=True)
    decoded_box_metric, _ = h0._compute_map50(
        gt_frames, decoded.decoded_boxes[: len(gt_frames)], iou=iou
    )
    source_box_metric, _ = h0._compute_map50(gt_frames, source_boxes, iou=iou)
    return RepresentationResult(
        name="box",
        measurement_type="parity_clean_h0",
        frames=zpe_frames,
        size_bytes=zpe_bitrate_bytes,
        artifact_path=zpe_stream_path,
        background_policy="neutral_gray_128",
        notes="Detector-produced boxes transported through the canonical box codec and box-fill reconstruction.",
        diagnostics={
            "decoded_box_metric": float(decoded_box_metric),
            "source_box_metric": float(source_box_metric),
            "decoded_frame_count": len(decoded.decoded_boxes),
            "decode_errors": list(decoded.errors),
            "frame_primitive_counts": [
                len(frame) for frame in decoded.decoded_boxes[: len(gt_frames)]
            ],
            "primitive_count_mean": _mean_value(
                [float(len(frame)) for frame in decoded.decoded_boxes[: len(gt_frames)]]
            ),
        },
    )


def _prediction_count_stats(predictions: list[list[object]]) -> dict[str, float]:
    counts = [float(len(frame)) for frame in predictions]
    return {
        "mean": _mean_value(counts),
        "max": float(max(counts) if counts else 0.0),
        "min": float(min(counts) if counts else 0.0),
    }


def _image_signal_stats(frames: list[np.ndarray]) -> dict[str, float]:
    import cv2  # type: ignore

    edge_densities: list[float] = []
    gradient_energies: list[float] = []
    intensity_stds: list[float] = []
    for frame in frames:
        gray = np.asarray(Image.fromarray(frame).convert("L"), dtype=np.uint8)
        edges = cv2.Canny(gray, 40, 120)
        edge_densities.append(float(np.count_nonzero(edges)) / float(edges.size))
        grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        gradient_energies.append(float(np.mean(np.sqrt((grad_x * grad_x) + (grad_y * grad_y)))))
        intensity_stds.append(float(np.std(gray.astype(np.float32))))
    return {
        "edge_density_mean": _mean_value(edge_densities),
        "gradient_energy_mean": _mean_value(gradient_energies),
        "intensity_std_mean": _mean_value(intensity_stds),
    }


def _save_contact_sheet(
    output_path: Path,
    *,
    labels: list[str],
    frames: list[np.ndarray],
) -> None:
    if not frames:
        return
    tile_width = int(frames[0].shape[1])
    tile_height = int(frames[0].shape[0])
    sheet = Image.new("RGB", (tile_width * len(frames), tile_height + 28), color=(16, 16, 16))
    draw = ImageDraw.Draw(sheet)
    for idx, (label, frame) in enumerate(zip(labels, frames, strict=False)):
        tile = Image.fromarray(frame.astype(np.uint8))
        sheet.paste(tile, (idx * tile_width, 28))
        draw.text((idx * tile_width + 8, 6), label, fill=(245, 245, 245))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path)


def _rank_representation_items(
    representations: dict[str, dict[str, object]],
) -> list[tuple[str, dict[str, object]]]:
    return sorted(
        representations.items(),
        key=lambda item: (float(item[1]["metric"]), -float(item[1]["bitrate_ratio"])),
        reverse=True,
    )


def _best_representation_name(
    representations: dict[str, dict[str, object]],
    *,
    max_bitrate_ratio: float | None = None,
) -> str | None:
    filtered = {
        name: data
        for name, data in representations.items()
        if max_bitrate_ratio is None or float(data["bitrate_ratio"]) <= max_bitrate_ratio
    }
    ranked = _rank_representation_items(filtered)
    if not ranked:
        return None
    return ranked[0][0]


def _recommended_representation(
    representations: dict[str, dict[str, object]],
    *,
    max_bitrate_ratio: float,
) -> tuple[str, str, str | None, str]:
    ranked = _rank_representation_items(representations)
    if not ranked:
        return "box", "No sparse representations were available.", None, "none"

    best_overall_name, _ = ranked[0]
    best_under_gate_name = _best_representation_name(
        representations, max_bitrate_ratio=max_bitrate_ratio
    )
    name = best_under_gate_name or best_overall_name
    data = representations[name]
    if name.startswith("patch_q4_"):
        dominant_patch_grid = data["diagnostics"].get("dominant_patch_grid") or data[
            "diagnostics"
        ].get("patch_plan")
        return (
            name,
            f"{dominant_patch_grid} quantized ROI thumbnails are the strongest current gate-aware H2 frontier and show that appearance fidelity, not geometry transport, is now the limiting stage.",
            best_under_gate_name,
            best_overall_name,
        )
    if name == "contour_patch":
        return (
            name,
            "Adding lightweight interior support recovers more detector-relevant signal than boundary-only reconstruction.",
            best_under_gate_name,
            best_overall_name,
        )
    return (
        name,
        "Boundary geometry remains the next minimal substrate after the clean H0 fail.",
        best_under_gate_name,
        best_overall_name,
    )


def _write_markdown_report(
    output_path: Path,
    *,
    summary: dict[str, object],
) -> None:
    representations = summary["representations"]
    box_rep = representations["box"]
    contour_rep = representations["contour"]
    contour_patch_rep = representations["contour_patch"]
    ranked = _rank_representation_items(representations)
    best_name = summary["recommended_next_representation"]
    best_rep = representations[best_name]
    best_overall_name = summary["best_overall_representation"]
    best_overall_rep = representations[best_overall_name]
    lines = [
        "# AM-C01 Representation Ladder Analysis",
        "",
        f"- measured_utc: {summary['measured_utc']}",
        f"- detector: {summary['detector_model']} @ threshold {summary['detector_score_threshold']}",
        f"- dataset: {summary['dataset']}",
        f"- frame_count: {summary['frame_count']}",
        "",
        "## Core Results",
        "",
        f"- baseline_metric: `{summary['baseline_metric']:.12f}`",
        f"- h265_metric: `{summary['h265_metric']:.12f}`",
        f"- box_metric: `{box_rep['metric']:.12f}`",
        f"- contour_metric: `{contour_rep['metric']:.12f}`",
        f"- contour_plus_patch_metric: `{contour_patch_rep['metric']:.12f}`",
    ]
    lines.extend([""])
    for name, data in ranked:
        lines.append(
            f"- {name}: metric `{data['metric']:.12f}` | retention `{data['detection_retention']:.12f}` | bitrate_ratio `{data['bitrate_ratio']:.12f}`"
        )
    lines.extend(
        [
            "",
            "## Scientific Pattern",
            "",
            f"- source_box_metric: `{box_rep['diagnostics']['source_box_metric']:.12f}`",
            f"- decoded_box_metric: `{box_rep['diagnostics']['decoded_box_metric']:.12f}`",
            "- The detector-produced geometry survives extraction and transport.",
            "- The collapse occurs when that geometry is rasterized back into detector-consumed imagery.",
            f"- contour_only_retention: `{contour_rep['detection_retention']:.12f}`",
            f"- contour_plus_patch_retention: `{contour_patch_rep['detection_retention']:.12f}`",
            f"- best_under_gate_representation: `{best_name}` @ `{best_rep['metric']:.12f}`",
            f"- best_overall_representation: `{best_overall_name}` @ `{best_overall_rep['metric']:.12f}`",
            "- Explicit contour overlays are not helping this detector lane once even coarse appearance is available.",
            "- Coarse natural-image thumbnails inside the ROI recover more signal than contour-first drawings.",
        ]
    )
    lines.extend(
        [
            "- If contour-only stays near zero while contour-plus-patch recovers, the missing signal is interior appearance support.",
            "- If all sparse variants stay far below H.265, the reconstruction family remains too far off the detector's natural-image manifold.",
            "",
            "## Signal Statistics",
            "",
            f"- raw_edge_density_mean: `{summary['baseline_signal']['edge_density_mean']:.12f}`",
            f"- h265_edge_density_mean: `{summary['h265_signal']['edge_density_mean']:.12f}`",
            f"- box_edge_density_mean: `{box_rep['signal']['edge_density_mean']:.12f}`",
            f"- contour_edge_density_mean: `{contour_rep['signal']['edge_density_mean']:.12f}`",
            f"- contour_plus_patch_edge_density_mean: `{contour_patch_rep['signal']['edge_density_mean']:.12f}`",
            f"- best_sparse_edge_density_mean: `{best_rep['signal']['edge_density_mean']:.12f}`",
        ]
    )
    lines.extend(
        [
            "",
            "## Recommendation",
            "",
            f"- next_best_representation: `{summary['recommended_next_representation']}`",
            f"- rationale: {summary['recommended_rationale']}",
            f"- best_overall_representation: `{summary['best_overall_representation']}`",
            "",
        ]
    )
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run AM-C01 representation ladder on the same frozen VisDrone slice."
    )
    parser.add_argument(
        "--frame-count", type=int, default=20, help="Number of VisDrone frames to evaluate."
    )
    parser.add_argument(
        "--artifact-dir",
        default="artifacts/2026-03-13_am_c01_ladder_h2_budgetfinal",
        help="Artifact directory relative to repo root.",
    )
    parser.add_argument(
        "--score-threshold", type=float, default=0.05, help="Detector score threshold."
    )
    args = parser.parse_args()

    artifact_root = (REPO_ROOT / args.artifact_dir).resolve()
    artifact_root.mkdir(parents=True, exist_ok=True)

    (
        Box,
        SequenceData,
        TorchvisionCocoDetector,
        visdrone_mapping,
        encode_sequence,
        decode_sequence,
        reconstruct_frame,
        iou,
    ) = h0._load_modules(REPO_ROOT)

    datasets_root = h0._resolve_datasets_root(REPO_ROOT)
    frames, width, height = h0._load_visdrone_subset(
        datasets_root,
        frame_count=args.frame_count,
        Box=Box,
        visdrone_mapping=visdrone_mapping,
    )
    rgb_frames = [frame.rgb for frame in frames]
    gray_frames = [frame.gray_bytes for frame in frames]
    gt_frames = [frame.gt_boxes for frame in frames]

    detector = TorchvisionCocoDetector(score_threshold=args.score_threshold)
    baseline_predictions = h0._predict_many(detector, rgb_frames)
    source_boxes = h0._assign_track_ids(baseline_predictions, Box=Box, iou=iou)
    baseline_metric, baseline_per_class = h0._compute_map50(
        gt_frames, baseline_predictions, iou=iou
    )

    h265_frames, h265_bitrate_bytes, h265_path = h0._encode_h265(
        REPO_ROOT, artifact_root, rgb_frames, frame_rate=24
    )
    h265_predictions = h0._predict_many(detector, h265_frames[: len(gt_frames)])
    h265_metric, h265_per_class = h0._compute_map50(gt_frames, h265_predictions, iou=iou)

    sparse_specs = [
        SparseRepresentationSpec(
            name="contour",
            measurement_type="parity_clean_h1_contour",
            notes="Contour/stroke reconstruction from detector-supported ROIs.",
            include_contour=True,
            draw_contour=True,
        ),
        SparseRepresentationSpec(
            name="contour_patch",
            measurement_type="parity_clean_h2_contour_patch",
            notes="Contour/stroke reconstruction with 4x4x3 quantized interior color patches from detector-supported ROIs.",
            include_contour=True,
            draw_contour=True,
            patch_plan=PatchPlan.fixed(
                PatchSpec(width=4, height=4, quant_levels=16, channels=3, margin_ratio=0.0)
            ),
        ),
        SparseRepresentationSpec(
            name="patch_q4_8",
            measurement_type="parity_clean_h2_patch_q4_8",
            notes="8x8 4-bit RGB ROI thumbnails without contour overlay.",
            include_contour=False,
            draw_contour=False,
            patch_plan=PatchPlan.fixed(
                PatchSpec(width=8, height=8, quant_levels=16, channels=3, margin_ratio=0.0)
            ),
        ),
        SparseRepresentationSpec(
            name="patch_q4_mix_8_10_area1600",
            measurement_type="parity_clean_h2_patch_q4_mix_8_10_area1600",
            notes="Area-adaptive 4-bit RGB ROI thumbnails: 10x10 for boxes at or above 1600 px area, otherwise 8x8, without contour overlay.",
            include_contour=False,
            draw_contour=False,
            patch_plan=PatchPlan(
                variants=(
                    (
                        1600,
                        PatchSpec(
                            width=10, height=10, quant_levels=16, channels=3, margin_ratio=0.0
                        ),
                    ),
                    (
                        0,
                        PatchSpec(width=8, height=8, quant_levels=16, channels=3, margin_ratio=0.0),
                    ),
                )
            ),
        ),
        SparseRepresentationSpec(
            name="patch_q4_mix_8_10_area2200",
            measurement_type="parity_clean_h2_patch_q4_mix_8_10_area2200",
            notes="Area-adaptive 4-bit RGB ROI thumbnails: 10x10 for boxes at or above 2200 px area, otherwise 8x8, without contour overlay.",
            include_contour=False,
            draw_contour=False,
            patch_plan=PatchPlan(
                variants=(
                    (
                        2200,
                        PatchSpec(
                            width=10, height=10, quant_levels=16, channels=3, margin_ratio=0.0
                        ),
                    ),
                    (
                        0,
                        PatchSpec(width=8, height=8, quant_levels=16, channels=3, margin_ratio=0.0),
                    ),
                )
            ),
        ),
        SparseRepresentationSpec(
            name="patch_q4_mix_8_10_area2500",
            measurement_type="parity_clean_h2_patch_q4_mix_8_10_area2500",
            notes="Area-adaptive 4-bit RGB ROI thumbnails: 10x10 for boxes at or above 2500 px area, otherwise 8x8, without contour overlay.",
            include_contour=False,
            draw_contour=False,
            patch_plan=PatchPlan(
                variants=(
                    (
                        2500,
                        PatchSpec(
                            width=10, height=10, quant_levels=16, channels=3, margin_ratio=0.0
                        ),
                    ),
                    (
                        0,
                        PatchSpec(width=8, height=8, quant_levels=16, channels=3, margin_ratio=0.0),
                    ),
                )
            ),
        ),
        SparseRepresentationSpec(
            name="patch_q4_10",
            measurement_type="parity_clean_h2_patch_q4_10",
            notes="10x10 4-bit RGB ROI thumbnails without contour overlay.",
            include_contour=False,
            draw_contour=False,
            patch_plan=PatchPlan.fixed(
                PatchSpec(width=10, height=10, quant_levels=16, channels=3, margin_ratio=0.0)
            ),
        ),
        SparseRepresentationSpec(
            name="patch_q4_12",
            measurement_type="parity_clean_h2_patch_q4_12",
            notes="12x12 4-bit RGB ROI thumbnails without contour overlay.",
            include_contour=False,
            draw_contour=False,
            patch_plan=PatchPlan.fixed(
                PatchSpec(width=12, height=12, quant_levels=16, channels=3, margin_ratio=0.0)
            ),
        ),
    ]

    representations = [
        _run_box_representation(
            artifact_root,
            gray_frames=gray_frames,
            source_boxes=source_boxes,
            width=width,
            height=height,
            frame_rate=24,
            SequenceData=SequenceData,
            encode_sequence=encode_sequence,
            decode_sequence=decode_sequence,
            reconstruct_frame=reconstruct_frame,
            gt_frames=gt_frames,
            iou=iou,
        ),
        *[
            _run_sparse_representation(
                artifact_root,
                spec=spec,
                gray_frames=gray_frames,
                rgb_frames=rgb_frames,
                source_boxes=source_boxes,
                width=width,
                height=height,
            )
            for spec in sparse_specs
        ],
    ]

    rep_payload: dict[str, object] = {}
    for rep in representations:
        predictions = h0._predict_many(detector, rep.frames)
        metric, per_class = h0._compute_map50(gt_frames, predictions, iou=iou)
        detection_retention = (metric / baseline_metric) if baseline_metric > 0 else 0.0
        bitrate_ratio = (
            (rep.size_bytes / float(h265_bitrate_bytes)) if h265_bitrate_bytes > 0 else float("inf")
        )
        rep_payload[rep.name] = {
            "measurement_type": rep.measurement_type,
            "metric": float(metric),
            "per_class_ap50": per_class,
            "size_bytes": int(rep.size_bytes),
            "bitrate_ratio": float(bitrate_ratio),
            "detection_retention": float(detection_retention),
            "artifact_path": str(rep.artifact_path),
            "background_policy": rep.background_policy,
            "notes": rep.notes,
            "prediction_count": _prediction_count_stats(predictions),
            "signal": _image_signal_stats(rep.frames),
            "diagnostics": rep.diagnostics,
        }

    sparse_rep_payload = {name: data for name, data in rep_payload.items() if name != "box"}
    (
        recommended_next_representation,
        recommended_rationale,
        best_under_gate_representation,
        best_overall_representation,
    ) = _recommended_representation(sparse_rep_payload, max_bitrate_ratio=0.02)

    summary = {
        "authority_metric_id": "AM-C01",
        "measurement_type": "representation_ladder",
        "measured_utc": h0._now_utc(),
        "dataset": "VisDrone2019-DET-val",
        "frame_count": len(frames),
        "frame_names": [frame.name for frame in frames],
        "detector_model": detector.model_id,
        "detector_score_threshold": float(args.score_threshold),
        "detector_model_sha256": h0._sha256_file(detector.checkpoint_path)
        if detector.checkpoint_path
        else None,
        "baseline_metric": float(baseline_metric),
        "baseline_per_class_ap50": baseline_per_class,
        "baseline_prediction_count": _prediction_count_stats(baseline_predictions),
        "baseline_signal": _image_signal_stats(rgb_frames),
        "source_box_metric": float(rep_payload["box"]["diagnostics"]["source_box_metric"]),
        "h265_metric": float(h265_metric),
        "h265_per_class_ap50": h265_per_class,
        "h265_bitrate_bytes": int(h265_bitrate_bytes),
        "h265_prediction_count": _prediction_count_stats(h265_predictions),
        "h265_signal": _image_signal_stats(h265_frames[: len(gt_frames)]),
        "representations": rep_payload,
        "representation_ranking": [
            name for name, _ in _rank_representation_items(sparse_rep_payload)
        ],
        "best_overall_representation": best_overall_representation,
        "best_under_gate_representation": best_under_gate_representation,
        "recommended_next_representation": recommended_next_representation,
        "recommended_rationale": recommended_rationale,
    }

    representation_by_name = {rep.name: rep for rep in representations}
    first_index = 0
    last_index = min(len(rgb_frames) - 1, 9)
    contact_rep_names = ["box", "contour", "contour_patch", recommended_next_representation]
    deduped_contact_rep_names: list[str] = []
    for name in contact_rep_names:
        if name not in deduped_contact_rep_names:
            deduped_contact_rep_names.append(name)
    labels = ["raw", "h265", *deduped_contact_rep_names]
    _save_contact_sheet(
        artifact_root / "contact_sheet_frame_0000.png",
        labels=labels,
        frames=[
            rgb_frames[first_index],
            h265_frames[first_index],
            *[
                representation_by_name[name].frames[first_index]
                for name in deduped_contact_rep_names
            ],
        ],
    )
    _save_contact_sheet(
        artifact_root / f"contact_sheet_frame_{last_index:04d}.png",
        labels=labels,
        frames=[
            rgb_frames[last_index],
            h265_frames[last_index],
            *[
                representation_by_name[name].frames[last_index]
                for name in deduped_contact_rep_names
            ],
        ],
    )

    command_text = " ".join(shlex.quote(arg) for arg in [sys.executable, *sys.argv])
    custody_manifest = {
        "measured_utc": summary["measured_utc"],
        "command": command_text,
        "repo_root": str(REPO_ROOT),
        "artifact_root": str(artifact_root),
        "datasets_root": str(datasets_root),
        "script_path": str(Path(__file__).resolve()),
        "script_sha256": h0._sha256_file(Path(__file__).resolve()),
        "detector_model": summary["detector_model"],
        "detector_score_threshold": summary["detector_score_threshold"],
        "detector_checkpoint_path": str(detector.checkpoint_path)
        if detector.checkpoint_path
        else None,
        "detector_checkpoint_sha256": summary["detector_model_sha256"],
        "frame_manifest": h0._frame_manifest(frames),
        "output_hashes": {
            "h265_video_path": str(h265_path),
            "h265_video_sha256": h0._sha256_file(h265_path),
            **{
                f"{name}_artifact_path": data["artifact_path"] for name, data in rep_payload.items()
            },
            **{
                f"{name}_artifact_sha256": h0._sha256_file(Path(data["artifact_path"]))
                for name, data in rep_payload.items()
            },
        },
    }

    measurement_path = artifact_root / "am_c01_ladder_measurement.json"
    custody_path = artifact_root / "am_c01_ladder_custody_manifest.json"
    report_path = artifact_root / "am_c01_ladder_analysis.md"
    measurement_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    custody_path.write_text(
        json.dumps(custody_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    _write_markdown_report(report_path, summary=summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    if any(
        bool(data["detection_retention"] >= 0.95 and data["bitrate_ratio"] <= 0.02)
        for data in rep_payload.values()
    ):
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
