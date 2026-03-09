from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Box:
    box_id: int
    x: int
    y: int
    w: int
    h: int
    label: int = 1

    @property
    def right(self) -> int:
        return self.x + self.w

    @property
    def bottom(self) -> int:
        return self.y + self.h


@dataclass
class SequenceData:
    name: str
    dataset_tag: str
    width: int
    height: int
    fps: int
    background: bytes
    frames: list[bytes]
    gt_boxes: list[list[Box]]
    notes: dict[str, Any] = field(default_factory=dict)

    @property
    def frame_count(self) -> int:
        return len(self.frames)


@dataclass
class EncodedSequenceResult:
    stream_path: str
    stream_bytes: int
    frame_payload_sizes: list[int]
    encode_latency_ms: list[float]
    frame_payloads: list[bytes]
    detected_boxes: list[list[Box]]


@dataclass
class DecodedSequenceResult:
    width: int
    height: int
    seed: int
    sketch_frames: list[bytes]
    decoded_boxes: list[list[Box]]
    corrupted_frames: list[int]
    errors: list[str]
    fatal_error: str | None = None
