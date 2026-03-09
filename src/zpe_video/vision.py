from __future__ import annotations

from collections import deque

from .models import Box


def draw_filled_box(frame: bytearray, width: int, height: int, box: Box, value: int) -> None:
    x0 = max(0, box.x)
    y0 = max(0, box.y)
    x1 = min(width, box.x + box.w)
    y1 = min(height, box.y + box.h)
    if x0 >= x1 or y0 >= y1:
        return
    for y in range(y0, y1):
        row_offset = y * width
        for x in range(x0, x1):
            frame[row_offset + x] = value


def draw_box_edges(frame: bytearray, width: int, height: int, box: Box, value: int = 255) -> None:
    if box.w <= 0 or box.h <= 0:
        return
    x0 = max(0, box.x)
    y0 = max(0, box.y)
    x1 = min(width - 1, box.x + box.w - 1)
    y1 = min(height - 1, box.y + box.h - 1)
    if x0 > x1 or y0 > y1:
        return
    top = y0 * width
    bottom = y1 * width
    for x in range(x0, x1 + 1):
        frame[top + x] = value
        frame[bottom + x] = value
    for y in range(y0, y1 + 1):
        row = y * width
        frame[row + x0] = value
        frame[row + x1] = value


def render_sketch(width: int, height: int, boxes: list[Box]) -> bytes:
    frame = bytearray(width * height)
    for box in boxes:
        draw_box_edges(frame, width, height, box, value=255)
    return bytes(frame)


def detect_boxes_from_foreground(
    frame: bytes,
    background: bytes,
    width: int,
    height: int,
    threshold: int = 20,
    min_area: int = 12,
) -> list[Box]:
    pixel_count = width * height
    fg_mask = bytearray(pixel_count)
    for i in range(pixel_count):
        diff = frame[i] - background[i]
        if diff < 0:
            diff = -diff
        if diff >= threshold:
            fg_mask[i] = 1

    visited = bytearray(pixel_count)
    boxes: list[Box] = []
    next_id = 0

    for idx in range(pixel_count):
        if fg_mask[idx] == 0 or visited[idx] == 1:
            continue
        queue: deque[int] = deque([idx])
        visited[idx] = 1
        min_x = max_x = idx % width
        min_y = max_y = idx // width
        area = 0

        while queue:
            current = queue.popleft()
            x = current % width
            y = current // width
            area += 1
            if x < min_x:
                min_x = x
            if x > max_x:
                max_x = x
            if y < min_y:
                min_y = y
            if y > max_y:
                max_y = y

            neighbors = []
            if x > 0:
                neighbors.append(current - 1)
            if x < width - 1:
                neighbors.append(current + 1)
            if y > 0:
                neighbors.append(current - width)
            if y < height - 1:
                neighbors.append(current + width)

            for n in neighbors:
                if fg_mask[n] == 1 and visited[n] == 0:
                    visited[n] = 1
                    queue.append(n)

        if area >= min_area:
            boxes.append(
                Box(
                    box_id=next_id,
                    x=min_x,
                    y=min_y,
                    w=(max_x - min_x + 1),
                    h=(max_y - min_y + 1),
                    label=1,
                )
            )
            next_id += 1

    boxes.sort(key=lambda b: (b.x, b.y, b.w, b.h))
    return boxes


def reconstruct_frame(background: bytes, width: int, height: int, boxes: list[Box]) -> bytes:
    frame = bytearray(background)
    for i, box in enumerate(boxes):
        value = 180 + ((i * 17) % 60)
        draw_filled_box(frame, width, height, box, value=value)
    return bytes(frame)
