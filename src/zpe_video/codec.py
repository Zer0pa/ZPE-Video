from __future__ import annotations

import io
import struct
import time
import zlib

from .models import Box, DecodedSequenceResult, EncodedSequenceResult, SequenceData
from .vision import detect_boxes_from_foreground, render_sketch

MAGIC = b"ZPVID1"
VERSION = 1

HEADER_STRUCT = struct.Struct("<6sBHHHI")
FRAME_STRUCT = struct.Struct("<HBII")

def _encode_payload(boxes: list[Box], prev_by_id: dict[int, Box]) -> bytes:
    payload = bytearray()
    if len(boxes) > 255:
        boxes = boxes[:255]
    payload.append(len(boxes))
    for box in sorted(boxes, key=lambda b: b.box_id):
        prev = prev_by_id.get(box.box_id)
        payload.append(box.box_id & 0xFF)
        payload.append(box.label & 0xFF)
        if prev is None:
            payload.append(0)  # absolute
            payload.extend(struct.pack("<HHHH", box.x, box.y, box.w, box.h))
            continue
        dx = box.x - prev.x
        dy = box.y - prev.y
        payload.append(1)  # delta
        payload.extend(struct.pack("<hh", dx, dy))
        payload.extend(struct.pack("<HH", box.w, box.h))
    return bytes(payload)


def _decode_payload(payload: bytes, prev_by_id: dict[int, Box]) -> list[Box]:
    if not payload:
        return []
    offset = 0
    count = payload[offset]
    offset += 1
    boxes: list[Box] = []
    for _ in range(count):
        if offset + 3 > len(payload):
            raise ValueError("TRUNCATED_BOX_HEADER")
        box_id = payload[offset]
        label = payload[offset + 1]
        mode = payload[offset + 2]
        offset += 3
        if mode == 0:
            if offset + 8 > len(payload):
                raise ValueError("TRUNCATED_ABS_BOX")
            x, y, w, h = struct.unpack_from("<HHHH", payload, offset)
            offset += 8
            box = Box(box_id=box_id, x=x, y=y, w=w, h=h, label=label)
            boxes.append(box)
        elif mode == 1:
            if offset + 8 > len(payload):
                raise ValueError("TRUNCATED_DELTA_BOX")
            dx, dy = struct.unpack_from("<hh", payload, offset)
            w, h = struct.unpack_from("<HH", payload, offset + 4)
            offset += 8
            prev = prev_by_id.get(box_id)
            if prev is None:
                raise ValueError(f"MISSING_PREV_BOX_{box_id}")
            box = Box(box_id=box_id, x=prev.x + dx, y=prev.y + dy, w=w, h=h, label=label)
            boxes.append(box)
        else:
            raise ValueError(f"UNKNOWN_BOX_MODE_{mode}")
    return boxes


def encode_sequence(
    sequence: SequenceData,
    output_path: str,
    seed: int,
    use_gt_boxes: bool = True,
) -> EncodedSequenceResult:
    frame_payload_sizes: list[int] = []
    encode_latency_ms: list[float] = []
    frame_payloads: list[bytes] = []
    detected_boxes: list[list[Box]] = []
    prev_by_id: dict[int, Box] = {}

    stream = io.BytesIO()
    stream.write(
        HEADER_STRUCT.pack(
            MAGIC,
            VERSION,
            sequence.width,
            sequence.height,
            sequence.frame_count,
            seed,
        )
    )

    for frame_idx, frame in enumerate(sequence.frames):
        start = time.perf_counter()
        if use_gt_boxes and sequence.gt_boxes:
            boxes = sequence.gt_boxes[frame_idx]
        else:
            boxes = detect_boxes_from_foreground(
                frame,
                sequence.background,
                sequence.width,
                sequence.height,
            )
        raw_payload = _encode_payload(boxes, prev_by_id)
        compressed = zlib.compress(raw_payload, level=9)
        crc = zlib.crc32(compressed) & 0xFFFFFFFF
        stream.write(FRAME_STRUCT.pack(frame_idx, 1, len(compressed), crc))
        stream.write(compressed)
        elapsed_ms = (time.perf_counter() - start) * 1000.0

        frame_payload_sizes.append(len(compressed))
        encode_latency_ms.append(elapsed_ms)
        frame_payloads.append(compressed)
        detected_boxes.append(list(boxes))
        prev_by_id = {box.box_id: box for box in boxes}

    stream_bytes = stream.getvalue()
    with open(output_path, "wb") as f:
        f.write(stream_bytes)

    return EncodedSequenceResult(
        stream_path=output_path,
        stream_bytes=len(stream_bytes),
        frame_payload_sizes=frame_payload_sizes,
        encode_latency_ms=encode_latency_ms,
        frame_payloads=frame_payloads,
        detected_boxes=detected_boxes,
    )


def decode_sequence(stream_path: str, tolerate_corruption: bool = True) -> DecodedSequenceResult:
    sketch_frames: list[bytes] = []
    decoded_boxes: list[list[Box]] = []
    corrupted_frames: list[int] = []
    errors: list[str] = []

    try:
        with open(stream_path, "rb") as f:
            blob = f.read()
        if len(blob) < HEADER_STRUCT.size:
            return DecodedSequenceResult(
                width=0,
                height=0,
                seed=0,
                sketch_frames=[],
                decoded_boxes=[],
                corrupted_frames=[-1],
                errors=["TRUNCATED_HEADER"],
                fatal_error="TRUNCATED_HEADER",
            )

        magic, version, width, height, frame_count, seed = HEADER_STRUCT.unpack_from(blob, 0)
        if magic != MAGIC or version != VERSION:
            return DecodedSequenceResult(
                width=width,
                height=height,
                seed=seed,
                sketch_frames=[],
                decoded_boxes=[],
                corrupted_frames=[-1],
                errors=[f"BAD_MAGIC_OR_VERSION:{magic!r}:{version}"],
                fatal_error="BAD_MAGIC_OR_VERSION",
            )

        offset = HEADER_STRUCT.size
        prev_by_id: dict[int, Box] = {}
        fallback_boxes: list[Box] = []

        for frame_idx in range(frame_count):
            if offset + FRAME_STRUCT.size > len(blob):
                errors.append(f"TRUNCATED_FRAME_HEADER_{frame_idx}")
                corrupted_frames.append(frame_idx)
                if tolerate_corruption:
                    sketch_frames.append(render_sketch(width, height, fallback_boxes))
                    decoded_boxes.append(list(fallback_boxes))
                    continue
                break

            parsed_idx, flags, payload_len, crc = FRAME_STRUCT.unpack_from(blob, offset)
            offset += FRAME_STRUCT.size

            if parsed_idx != frame_idx:
                errors.append(f"FRAME_INDEX_MISMATCH_{frame_idx}_{parsed_idx}")

            if offset + payload_len > len(blob):
                errors.append(f"TRUNCATED_PAYLOAD_{frame_idx}")
                corrupted_frames.append(frame_idx)
                if tolerate_corruption:
                    sketch_frames.append(render_sketch(width, height, fallback_boxes))
                    decoded_boxes.append(list(fallback_boxes))
                    continue
                break

            payload_compressed = blob[offset : offset + payload_len]
            offset += payload_len

            payload_crc = zlib.crc32(payload_compressed) & 0xFFFFFFFF
            if payload_crc != crc:
                errors.append(f"CRC_MISMATCH_{frame_idx}")
                corrupted_frames.append(frame_idx)
                if tolerate_corruption:
                    sketch_frames.append(render_sketch(width, height, fallback_boxes))
                    decoded_boxes.append(list(fallback_boxes))
                    continue
                break

            try:
                if flags & 0x1:
                    payload = zlib.decompress(payload_compressed)
                else:
                    payload = payload_compressed
                boxes = _decode_payload(payload, prev_by_id)
            except Exception as exc:
                errors.append(f"PAYLOAD_PARSE_ERROR_{frame_idx}:{exc}")
                corrupted_frames.append(frame_idx)
                if tolerate_corruption:
                    sketch_frames.append(render_sketch(width, height, fallback_boxes))
                    decoded_boxes.append(list(fallback_boxes))
                    continue
                break

            prev_by_id = {box.box_id: box for box in boxes}
            fallback_boxes = list(boxes)
            sketch_frames.append(render_sketch(width, height, boxes))
            decoded_boxes.append(list(boxes))

        return DecodedSequenceResult(
            width=width,
            height=height,
            seed=seed,
            sketch_frames=sketch_frames,
            decoded_boxes=decoded_boxes,
            corrupted_frames=corrupted_frames,
            errors=errors,
        )
    except Exception as exc:  # pragma: no cover - safety envelope for corrupted inputs
        return DecodedSequenceResult(
            width=0,
            height=0,
            seed=0,
            sketch_frames=sketch_frames,
            decoded_boxes=decoded_boxes,
            corrupted_frames=corrupted_frames,
            errors=errors + [f"UNCAUGHT_EXCEPTION:{exc}"],
            fatal_error=str(exc),
        )


def decode_payload_for_machine_mode(payload_compressed: bytes, prev_by_id: dict[int, Box]) -> list[Box]:
    payload = zlib.decompress(payload_compressed)
    return _decode_payload(payload, prev_by_id)
