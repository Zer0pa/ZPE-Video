from __future__ import annotations

import random
from dataclasses import dataclass

from .constants import GLOBAL_SEED
from .models import Box, SequenceData
from .vision import draw_filled_box


@dataclass
class _MovingObject:
    box_id: int
    x: float
    y: float
    w: int
    h: int
    dx: float
    dy: float


def _clamp(v: int) -> int:
    if v < 0:
        return 0
    if v > 255:
        return 255
    return v


def _make_background(width: int, height: int, seed: int, roughness: int = 32) -> bytes:
    rng = random.Random(seed)
    frame = bytearray(width * height)
    for y in range(height):
        row = y * width
        for x in range(width):
            base = (x * 11 + y * 17 + seed) % 96
            texture = rng.randint(0, roughness)
            frame[row + x] = _clamp(48 + base + texture)
    return bytes(frame)


def _render_frame(
    background: bytes,
    width: int,
    height: int,
    boxes: list[Box],
    luminance_shift: int = 0,
    invert: bool = False,
) -> bytes:
    frame = bytearray(background)
    if invert or luminance_shift:
        for i, px in enumerate(frame):
            value = 255 - px if invert else px
            value = _clamp(value + luminance_shift)
            frame[i] = value
    for i, box in enumerate(boxes):
        value = _clamp(170 + (i * 23))
        draw_filled_box(frame, width, height, box, value)
    return bytes(frame)


def _step_objects(
    objects: list[_MovingObject],
    width: int,
    height: int,
    frame_idx: int,
    adversarial: bool,
    rng: random.Random,
) -> list[Box]:
    boxes: list[Box] = []
    for obj in objects:
        if frame_idx > 0:
            obj.x += obj.dx
            obj.y += obj.dy
            if obj.x < 2 or obj.x + obj.w >= width - 2:
                obj.dx *= -1
                obj.x += obj.dx * 2
            if obj.y < 2 or obj.y + obj.h >= height - 2:
                obj.dy *= -1
                obj.y += obj.dy * 2

        if adversarial and frame_idx % 11 == 0 and obj.box_id == 0:
            obj.dx = rng.choice([-5.0, -4.0, 4.0, 5.0])
            obj.dy = rng.choice([-4.0, -3.0, 3.0, 4.0])

        box = Box(
            box_id=obj.box_id,
            x=max(0, min(width - obj.w, int(round(obj.x)))),
            y=max(0, min(height - obj.h, int(round(obj.y)))),
            w=obj.w,
            h=obj.h,
            label=1,
        )
        boxes.append(box)
    boxes.sort(key=lambda b: b.box_id)
    return boxes


def _generate_sequence(
    *,
    name: str,
    dataset_tag: str,
    width: int,
    height: int,
    fps: int,
    frame_count: int,
    object_count: int,
    size_range: tuple[int, int],
    velocity_range: tuple[float, float],
    seed: int,
    adversarial: bool = False,
) -> SequenceData:
    rng = random.Random(seed)
    background = _make_background(width, height, seed=seed + 9, roughness=48 if adversarial else 28)

    objects: list[_MovingObject] = []
    for box_id in range(object_count):
        w = rng.randint(size_range[0], size_range[1])
        h = rng.randint(size_range[0], size_range[1])
        x = rng.uniform(2.0, float(max(3, width - w - 3)))
        y = rng.uniform(2.0, float(max(3, height - h - 3)))
        speed = rng.uniform(velocity_range[0], velocity_range[1])
        dx = speed * rng.choice([-1.0, 1.0])
        dy = speed * rng.choice([-1.0, 1.0])
        objects.append(_MovingObject(box_id=box_id, x=x, y=y, w=w, h=h, dx=dx, dy=dy))

    frames: list[bytes] = []
    gt_boxes: list[list[Box]] = []

    for frame_idx in range(frame_count):
        boxes = _step_objects(objects, width, height, frame_idx, adversarial=adversarial, rng=rng)
        if adversarial:
            invert = frame_idx % 9 == 0
            shift = 42 if frame_idx % 7 == 0 else 0
        else:
            invert = False
            shift = 0
        frame = _render_frame(
            background, width, height, boxes, luminance_shift=shift, invert=invert
        )
        frames.append(frame)
        gt_boxes.append(boxes)

    return SequenceData(
        name=name,
        dataset_tag=dataset_tag,
        width=width,
        height=height,
        fps=fps,
        background=background,
        frames=frames,
        gt_boxes=gt_boxes,
        notes={
            "adversarial": adversarial,
            "seed": seed,
            "object_count": object_count,
            "size_range": list(size_range),
            "velocity_range": list(velocity_range),
        },
    )


def generate_proxy_corpus(seed: int = GLOBAL_SEED) -> dict[str, SequenceData]:
    return {
        "virat_proxy": _generate_sequence(
            name="virat_proxy_static_bg",
            dataset_tag="VIRAT_PROXY",
            width=640,
            height=360,
            fps=24,
            frame_count=36,
            object_count=3,
            size_range=(26, 48),
            velocity_range=(1.0, 2.0),
            seed=seed + 101,
            adversarial=False,
        ),
        "visdrone_proxy": _generate_sequence(
            name="visdrone_proxy_drone_view",
            dataset_tag="VISDRONE_PROXY",
            width=640,
            height=360,
            fps=24,
            frame_count=36,
            object_count=7,
            size_range=(10, 22),
            velocity_range=(1.5, 3.0),
            seed=seed + 202,
            adversarial=False,
        ),
        "uvg_proxy": _generate_sequence(
            name="uvg_proxy_quality",
            dataset_tag="UVG_PROXY",
            width=640,
            height=360,
            fps=24,
            frame_count=24,
            object_count=4,
            size_range=(18, 36),
            velocity_range=(0.8, 2.2),
            seed=seed + 303,
            adversarial=False,
        ),
        "ctc_proxy": _generate_sequence(
            name="ctc_proxy_motion",
            dataset_tag="HEVC_CTC_PROXY",
            width=640,
            height=360,
            fps=24,
            frame_count=30,
            object_count=5,
            size_range=(16, 30),
            velocity_range=(2.0, 4.0),
            seed=seed + 404,
            adversarial=False,
        ),
        "adversarial_proxy": _generate_sequence(
            name="adversarial_rapid_scene_change",
            dataset_tag="ADVERSARIAL_PROXY",
            width=640,
            height=360,
            fps=24,
            frame_count=40,
            object_count=6,
            size_range=(12, 32),
            velocity_range=(2.0, 5.0),
            seed=seed + 505,
            adversarial=True,
        ),
        "latency_proxy": _generate_sequence(
            name="latency_proxy_cpu",
            dataset_tag="LATENCY_PROXY",
            width=320,
            height=180,
            fps=30,
            frame_count=60,
            object_count=4,
            size_range=(12, 26),
            velocity_range=(1.5, 3.5),
            seed=seed + 606,
            adversarial=False,
        ),
    }
