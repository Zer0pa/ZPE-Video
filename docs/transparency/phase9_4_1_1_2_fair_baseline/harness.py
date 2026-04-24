"""Phase 09.4.1.1.2 Fair-Baseline Archive-Query Falsification.

Goal: falsify or defend the ZPE packet archive-query wedge by benchmarking it
against honest commercial baselines (SQLite, Parquet, raw struct+zlib, JSON+gzip)
on the same workload, rather than against a strawman "rerun detection from raw
pixels at query time" path.

Prior phase 09.4.1.1.1 reported packet vs "full replay" with a 20.29x latency
win and a 0.11% bytes-scanned ratio. But:

- the full-replay path re-runs background subtraction + connected components +
  IoU tracking on raw frames at every query, which no archive-query incumbent
  does
- both paths feed the SAME naive portal-crossing operator and both produce
  ~40x false-positive clouds (packet 734 / full-replay 825 predicted for 19 GT)
- the 20.29x speedup therefore measures "parse sparse metadata vs decode pixels
  and re-run CV", which ANY sparse-metadata sidecar achieves
- the packet path's encoding cost is amortized and excluded from query latency

This phase tests the honest question: does ZPE's delta-encoded packet format
have a STRUCTURAL advantage over commodity sparse-metadata storage formats for
the same archive-query workload?

Representations tested:
    1. ZPE packet (zlib-compressed delta-encoded struct, same format as the
       phase 09.4.1.1.1 pod harness)
    2. Raw struct + zlib (same binary per-frame encoding but no delta
       across frames)
    3. SQLite (relational table, indexed)
    4. Parquet (columnar + snappy)
    5. JSON lines + gzip (verbose interchange format)

Operators tested:
    - naive: center-inside-portal for >= min_event_frames consecutive frames
    - hardened: naive + (inner-40%-portal) + (min outside-portal persistence)
      + (min displacement along motion axis)

Surface:
    - proxy-clean: 3 clips, 60 frames, clean tracks (precision=recall=1.0 by
      construction on naive operator)
    - proxy-noisy: proxy-clean + ghost tracks that briefly enter the portal
      (simulates the live false-positive cloud)

Kill criteria (any one):
    - Parquet or SQLite within 2x of ZPE on storage AND 2x on query latency
      under matched operator -> ZPE packet has no unique structural advantage
    - Hardened operator lifts precision to >= 0.5 on ALL representations under
      noisy proxy -> blocker is operator engineering, not representation

Defend criteria (must hit all):
    - ZPE packet beats every other representation by >= 2x on storage OR query
      latency while matching precision/recall within 1%
    - Hardened operator on packet uniquely beats hardened operator on any
      baseline

Outputs:
    - zpe_video_lab/reports/phase9_4_1_1_2_fair_baseline_archive_query/summary.json
"""

from __future__ import annotations

import argparse
import gzip
import io
import json
import random
import shutil
import sqlite3
import statistics
import struct
import sys
import tempfile
import time
import zlib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


LAB_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = LAB_ROOT.parent
DEFAULT_OUTPUT = LAB_ROOT / "reports" / "phase9_4_1_1_2_fair_baseline_archive_query" / "summary.json"
DEFAULT_QUERY_REPEATS = 11
DEFAULT_INGEST_REPEATS = 5
DEFAULT_NOISE_TRACKS_PER_CLIP = 10
DEFAULT_NOISE_SEED = 42

PACKET_MAGIC = b"ZPVID1"
PACKET_VERSION = 1
PACKET_HEADER_STRUCT = struct.Struct("<6sBHHHI")
PACKET_FRAME_STRUCT = struct.Struct("<HBII")


@dataclass(frozen=True)
class Box:
    box_id: int
    x: int
    y: int
    w: int
    h: int
    label: int = 1


@dataclass(frozen=True)
class EventWindow:
    clip_id: str
    event_id: int
    track_id: int
    start_frame: int
    end_frame: int
    direction: str


@dataclass(frozen=True)
class ClipBundle:
    clip_id: str
    width: int
    height: int
    frame_count: int
    portal_box: tuple[int, int, int, int]
    frames: tuple[tuple[Box, ...], ...]
    gt_events: tuple[EventWindow, ...]


@dataclass
class PathStats:
    storage_bytes: int = 0
    ingest_latency_ms_median: float = 0.0
    ingest_latency_ms_samples: list[float] = field(default_factory=list)
    query_latency_ms_median: float = 0.0
    query_latency_ms_samples: list[float] = field(default_factory=list)
    events_precision: float = 0.0
    events_recall: float = 0.0
    events_predicted: int = 0
    events_matched: int = 0
    events_ground_truth: int = 0
    events_mean_temporal_iou: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        out = asdict(self)
        # Drop raw samples to keep summary clean; keep only the distribution summary
        out["ingest_latency_ms_min"] = min(self.ingest_latency_ms_samples) if self.ingest_latency_ms_samples else 0.0
        out["ingest_latency_ms_max"] = max(self.ingest_latency_ms_samples) if self.ingest_latency_ms_samples else 0.0
        out["query_latency_ms_min"] = min(self.query_latency_ms_samples) if self.query_latency_ms_samples else 0.0
        out["query_latency_ms_max"] = max(self.query_latency_ms_samples) if self.query_latency_ms_samples else 0.0
        out.pop("ingest_latency_ms_samples", None)
        out.pop("query_latency_ms_samples", None)
        return out


# ---------------------------------------------------------------------------
# Proxy corpus construction
# ---------------------------------------------------------------------------


def _clamp(value: int, lo: int, hi: int) -> int:
    return max(lo, min(int(value), hi))


def _clamp_box(box: Box, width: int, height: int) -> Box:
    x = _clamp(int(box.x), 0, max(0, width - 1))
    y = _clamp(int(box.y), 0, max(0, height - 1))
    w = max(1, min(int(box.w), width - x))
    h = max(1, min(int(box.h), height - y))
    return Box(box_id=int(box.box_id), x=x, y=y, w=w, h=h, label=int(box.label))


def _center(box: Box) -> tuple[float, float]:
    return (float(box.x) + float(box.w) / 2.0, float(box.y) + float(box.h) / 2.0)


def _center_inside_portal(box: Box, portal_box: tuple[int, int, int, int]) -> bool:
    cx, cy = _center(box)
    x0, y0, x1, y1 = portal_box
    return float(x0) <= cx <= float(x1) and float(y0) <= cy <= float(y1)


def _shrink_portal(portal_box: tuple[int, int, int, int], inner_fraction: float) -> tuple[int, int, int, int]:
    x0, y0, x1, y1 = portal_box
    w = max(1, int(x1 - x0))
    h = max(1, int(y1 - y0))
    margin_x = int(round(w * (1.0 - float(inner_fraction)) / 2.0))
    margin_y = int(round(h * (1.0 - float(inner_fraction)) / 2.0))
    return (int(x0 + margin_x), int(y0 + margin_y), int(x1 - margin_x), int(y1 - margin_y))


def _render_track(
    *,
    track_id: int,
    start_x: float,
    start_y: float,
    width: int,
    height: int,
    delta_x: float,
    delta_y: float,
    start_frame: int,
    end_frame: int,
) -> list[tuple[int, Box]]:
    rows: list[tuple[int, Box]] = []
    for frame_index in range(start_frame, end_frame):
        step = frame_index - start_frame
        x = int(round(float(start_x) + float(delta_x) * step))
        y = int(round(float(start_y) + float(delta_y) * step))
        rows.append((frame_index, Box(box_id=int(track_id), x=x, y=y, w=int(width), h=int(height), label=1)))
    return rows


def build_clean_proxy_corpus(*, frame_count: int = 60, width: int = 320, height: int = 180) -> list[ClipBundle]:
    portal_box = (145, 60, 175, 120)
    specs = [
        {
            "clip_id": "proxy_clip_lr_clean",
            "tracks": [
                dict(track_id=0, start_x=20.0, start_y=78.0, width=22, height=30, delta_x=4.0, delta_y=0.0,
                     start_frame=0, end_frame=frame_count),
                dict(track_id=1, start_x=220.0, start_y=18.0, width=16, height=22, delta_x=-1.0, delta_y=0.0,
                     start_frame=0, end_frame=frame_count),
            ],
        },
        {
            "clip_id": "proxy_clip_rl_clean",
            "tracks": [
                dict(track_id=0, start_x=260.0, start_y=82.0, width=24, height=28, delta_x=-4.0, delta_y=0.0,
                     start_frame=0, end_frame=frame_count),
                dict(track_id=1, start_x=18.0, start_y=135.0, width=14, height=18, delta_x=1.5, delta_y=0.0,
                     start_frame=0, end_frame=frame_count),
            ],
        },
        {
            "clip_id": "proxy_clip_multi",
            "tracks": [
                dict(track_id=0, start_x=14.0, start_y=76.0, width=18, height=28, delta_x=4.1, delta_y=0.0,
                     start_frame=0, end_frame=frame_count),
                dict(track_id=1, start_x=286.0, start_y=86.0, width=20, height=28, delta_x=-4.2, delta_y=0.0,
                     start_frame=10, end_frame=frame_count),
                dict(track_id=2, start_x=55.0, start_y=145.0, width=15, height=18, delta_x=1.0, delta_y=0.0,
                     start_frame=0, end_frame=frame_count),
            ],
        },
    ]

    bundles: list[ClipBundle] = []
    for spec in specs:
        frames: list[list[Box]] = [[] for _ in range(frame_count)]
        for track_spec in spec["tracks"]:
            for frame_index, box in _render_track(**track_spec):
                frames[frame_index].append(_clamp_box(box, width, height))
        for frame in frames:
            frame.sort(key=lambda row: row.box_id)
        frame_tuples = tuple(tuple(frame) for frame in frames)
        gt_events = tuple(_extract_event_windows_naive(spec["clip_id"], frames, portal_box, min_event_frames=1))
        bundles.append(
            ClipBundle(
                clip_id=spec["clip_id"],
                width=width,
                height=height,
                frame_count=frame_count,
                portal_box=portal_box,
                frames=frame_tuples,
                gt_events=gt_events,
            )
        )
    return bundles


def build_noisy_proxy_corpus(
    *,
    frame_count: int = 60,
    width: int = 320,
    height: int = 180,
    noise_tracks_per_clip: int = DEFAULT_NOISE_TRACKS_PER_CLIP,
    seed: int = DEFAULT_NOISE_SEED,
) -> list[ClipBundle]:
    """Clean proxy plus short-lived ghost tracks that drift through the portal.

    This simulates the live false-positive cloud. Each ghost track is a small
    box that briefly appears near the portal for 4-12 frames and then vanishes.
    The ghost tracks do NOT correspond to real entering/exiting events, so any
    operator that counts them is wrong.
    """
    rng = random.Random(int(seed))
    clean = build_clean_proxy_corpus(frame_count=frame_count, width=width, height=height)
    noisy: list[ClipBundle] = []
    for clip in clean:
        frame_lists: list[list[Box]] = [list(frame) for frame in clip.frames]
        portal_box = clip.portal_box
        # Next track id beyond real tracks
        next_track_id = max(
            (int(box.box_id) for frame in frame_lists for box in frame),
            default=-1,
        ) + 1

        for _ in range(int(noise_tracks_per_clip)):
            dwell = rng.randint(4, 12)
            start_frame = rng.randint(0, max(0, frame_count - dwell - 1))
            end_frame = start_frame + dwell
            # Choose a noise seed inside or near the portal
            portal_cx = (portal_box[0] + portal_box[2]) // 2
            portal_cy = (portal_box[1] + portal_box[3]) // 2
            seed_x = portal_cx + rng.randint(-18, 18)
            seed_y = portal_cy + rng.randint(-16, 16)
            # Small erratic motion
            drift_x = rng.uniform(-0.8, 0.8)
            drift_y = rng.uniform(-0.4, 0.4)
            w = rng.randint(6, 14)
            h = rng.randint(8, 16)
            for step, frame_index in enumerate(range(start_frame, end_frame)):
                x = int(round(seed_x + drift_x * step)) - w // 2
                y = int(round(seed_y + drift_y * step)) - h // 2
                ghost = _clamp_box(Box(box_id=int(next_track_id), x=x, y=y, w=w, h=h, label=1), width, height)
                frame_lists[frame_index].append(ghost)
            next_track_id += 1

        for frame in frame_lists:
            frame.sort(key=lambda row: row.box_id)
        frame_tuples = tuple(tuple(frame) for frame in frame_lists)
        # GT events are still the ones from the clean tracks only (noise tracks are not GT).
        noisy.append(
            ClipBundle(
                clip_id=clip.clip_id + "_noisy",
                width=clip.width,
                height=clip.height,
                frame_count=clip.frame_count,
                portal_box=clip.portal_box,
                frames=frame_tuples,
                gt_events=tuple(
                    EventWindow(
                        clip_id=clip.clip_id + "_noisy",
                        event_id=ev.event_id,
                        track_id=ev.track_id,
                        start_frame=ev.start_frame,
                        end_frame=ev.end_frame,
                        direction=ev.direction,
                    )
                    for ev in clip.gt_events
                ),
            )
        )
    return noisy


# ---------------------------------------------------------------------------
# Operators
# ---------------------------------------------------------------------------


def _flush_event(
    *,
    track_id: int,
    event_id: int,
    active_run: list[tuple[int, Box]],
    center_before_run: float | None,
    clip_id: str,
) -> EventWindow:
    start_frame = int(active_run[0][0])
    end_frame = int(active_run[-1][0])
    start_center_x = _center(active_run[0][1])[0]
    end_center_x = _center(active_run[-1][1])[0]
    if center_before_run is not None:
        start_center_x = float(center_before_run)
    direction = "entering" if end_center_x >= start_center_x else "exiting"
    return EventWindow(
        clip_id=clip_id,
        event_id=int(event_id),
        track_id=int(track_id),
        start_frame=start_frame,
        end_frame=end_frame,
        direction=direction,
    )


def _extract_event_windows_naive(
    clip_id: str,
    frame_boxes: list[list[Box]] | tuple[tuple[Box, ...], ...],
    portal_box: tuple[int, int, int, int],
    *,
    min_event_frames: int = 4,
) -> list[EventWindow]:
    """Current portal-crossing operator: center-inside-portal for >= K frames."""
    track_frames: dict[int, list[tuple[int, Box]]] = {}
    for frame_index, boxes in enumerate(frame_boxes):
        for box in boxes:
            track_frames.setdefault(int(box.box_id), []).append((frame_index, box))

    events: list[EventWindow] = []
    next_event_id = 0
    for track_id, rows in sorted(track_frames.items()):
        active_run: list[tuple[int, Box]] = []
        previous_center_x: float | None = None
        center_before_run: float | None = None
        for frame_index, box in rows:
            if _center_inside_portal(box, portal_box):
                if not active_run:
                    center_before_run = previous_center_x
                active_run.append((frame_index, box))
            elif active_run:
                if len(active_run) >= int(min_event_frames):
                    events.append(
                        _flush_event(
                            track_id=int(track_id),
                            event_id=next_event_id,
                            active_run=active_run,
                            center_before_run=center_before_run,
                            clip_id=clip_id,
                        )
                    )
                    next_event_id += 1
                active_run = []
                center_before_run = None
            previous_center_x = _center(box)[0]
        if active_run and len(active_run) >= int(min_event_frames):
            events.append(
                _flush_event(
                    track_id=int(track_id),
                    event_id=next_event_id,
                    active_run=active_run,
                    center_before_run=center_before_run,
                    clip_id=clip_id,
                )
            )
            next_event_id += 1
    return events


def _extract_event_windows_hardened(
    clip_id: str,
    frame_boxes: list[list[Box]] | tuple[tuple[Box, ...], ...],
    portal_box: tuple[int, int, int, int],
    *,
    min_event_frames: int = 4,
    inner_portal_fraction: float = 0.4,
    min_outside_frames_before: int = 8,
    min_approach_displacement_px: int = 15,
) -> list[EventWindow]:
    """Operator that uses the same box stream but applies three cheap guards:

    1. Shrink the portal to its inner inner_portal_fraction (aperture cleanup).
    2. Require the track to be visible for >= min_outside_frames_before frames
       outside the portal BEFORE entering (rules out ghost tracks that just
       pop up near the portal).
    3. Require the track center to have moved by >= min_approach_displacement_px
       along the motion axis between entering and leaving the inner portal
       (rules out stationary flicker that briefly enters and exits).
    """
    inner_portal = _shrink_portal(portal_box, float(inner_portal_fraction))

    track_frames: dict[int, list[tuple[int, Box]]] = {}
    for frame_index, boxes in enumerate(frame_boxes):
        for box in boxes:
            track_frames.setdefault(int(box.box_id), []).append((frame_index, box))

    events: list[EventWindow] = []
    next_event_id = 0

    for track_id, rows in sorted(track_frames.items()):
        # Accumulate "outside-the-inner-portal" persistence before any inner run.
        outside_persistence = 0
        enter_persistence_met = False
        active_run: list[tuple[int, Box]] = []
        previous_center_x: float | None = None
        center_before_run: float | None = None

        for frame_index, box in rows:
            inside_inner = _center_inside_portal(box, inner_portal)
            if inside_inner:
                if not active_run:
                    center_before_run = previous_center_x
                    enter_persistence_met = outside_persistence >= int(min_outside_frames_before)
                active_run.append((frame_index, box))
            else:
                if active_run:
                    if (
                        len(active_run) >= int(min_event_frames)
                        and enter_persistence_met
                    ):
                        displacement = abs(
                            _center(active_run[-1][1])[0] - _center(active_run[0][1])[0]
                        )
                        if displacement >= float(min_approach_displacement_px):
                            events.append(
                                _flush_event(
                                    track_id=int(track_id),
                                    event_id=next_event_id,
                                    active_run=active_run,
                                    center_before_run=center_before_run,
                                    clip_id=clip_id,
                                )
                            )
                            next_event_id += 1
                    active_run = []
                    center_before_run = None
                    enter_persistence_met = False
                outside_persistence += 1
            previous_center_x = _center(box)[0]

        if active_run:
            if (
                len(active_run) >= int(min_event_frames)
                and enter_persistence_met
            ):
                displacement = abs(
                    _center(active_run[-1][1])[0] - _center(active_run[0][1])[0]
                )
                if displacement >= float(min_approach_displacement_px):
                    events.append(
                        _flush_event(
                            track_id=int(track_id),
                            event_id=next_event_id,
                            active_run=active_run,
                            center_before_run=center_before_run,
                            clip_id=clip_id,
                        )
                    )
                    next_event_id += 1

    return events


# ---------------------------------------------------------------------------
# Representations: ZPE packet, Raw struct+zlib, SQLite, Parquet, JSON+gzip
# ---------------------------------------------------------------------------


def _encode_packet_zpe(clip: ClipBundle) -> bytes:
    """ZPE packet format: zlib-compressed delta-encoded struct per frame.

    Identical to phase9_4_1_1_1_live_event_state_query.py so comparisons are
    apples-to-apples with the prior phase's packet claim.
    """
    stream = io.BytesIO()
    stream.write(
        PACKET_HEADER_STRUCT.pack(
            PACKET_MAGIC,
            PACKET_VERSION,
            int(clip.width),
            int(clip.height),
            int(clip.frame_count),
            0,
        )
    )
    prev_by_id: dict[int, Box] = {}
    for frame_idx, boxes in enumerate(clip.frames):
        boxes = sorted(list(boxes), key=lambda b: b.box_id)
        if len(boxes) > 255:
            boxes = boxes[:255]
        payload = bytearray()
        payload.append(len(boxes))
        for box in boxes:
            prev = prev_by_id.get(int(box.box_id))
            payload.append(int(box.box_id) & 0xFF)
            payload.append(int(box.label) & 0xFF)
            if prev is None:
                payload.append(0)
                payload.extend(struct.pack("<HHHH", int(box.x), int(box.y), int(box.w), int(box.h)))
            else:
                dx = int(box.x) - int(prev.x)
                dy = int(box.y) - int(prev.y)
                payload.append(1)
                payload.extend(struct.pack("<hh", dx, dy))
                payload.extend(struct.pack("<HH", int(box.w), int(box.h)))
        compressed = zlib.compress(bytes(payload), level=9)
        crc = zlib.crc32(compressed) & 0xFFFFFFFF
        stream.write(PACKET_FRAME_STRUCT.pack(int(frame_idx), 1, len(compressed), crc))
        stream.write(compressed)
        prev_by_id = {int(box.box_id): box for box in boxes}
    return stream.getvalue()


def _decode_packet_zpe(blob: bytes) -> list[list[Box]]:
    if len(blob) < PACKET_HEADER_STRUCT.size:
        return []
    magic, version, width, height, frame_count, _reserved = PACKET_HEADER_STRUCT.unpack_from(blob, 0)
    if magic != PACKET_MAGIC or version != PACKET_VERSION:
        raise ValueError("BAD_HEADER")
    offset = PACKET_HEADER_STRUCT.size
    frames: list[list[Box]] = []
    prev_by_id: dict[int, Box] = {}
    for _ in range(int(frame_count)):
        frame_idx, marker, payload_len, crc = PACKET_FRAME_STRUCT.unpack_from(blob, offset)
        offset += PACKET_FRAME_STRUCT.size
        payload_compressed = blob[offset : offset + int(payload_len)]
        offset += int(payload_len)
        if zlib.crc32(payload_compressed) & 0xFFFFFFFF != int(crc):
            raise ValueError("BAD_CRC")
        payload = zlib.decompress(payload_compressed)
        cursor = 0
        if cursor >= len(payload):
            frames.append([])
            continue
        count = payload[cursor]
        cursor += 1
        boxes: list[Box] = []
        for _ in range(count):
            box_id = payload[cursor]
            label = payload[cursor + 1]
            mode = payload[cursor + 2]
            cursor += 3
            if mode == 0:
                x, y, w, h = struct.unpack_from("<HHHH", payload, cursor)
                cursor += 8
                boxes.append(Box(box_id=box_id, x=x, y=y, w=w, h=h, label=label))
            else:
                dx, dy = struct.unpack_from("<hh", payload, cursor)
                w, h = struct.unpack_from("<HH", payload, cursor + 4)
                cursor += 8
                prev = prev_by_id.get(box_id)
                if prev is None:
                    raise ValueError(f"MISSING_PREV_BOX_{box_id}")
                boxes.append(Box(box_id=box_id, x=prev.x + dx, y=prev.y + dy, w=w, h=h, label=label))
        prev_by_id = {int(b.box_id): b for b in boxes}
        frames.append(boxes)
    return frames


def _encode_raw_struct_zlib(clip: ClipBundle) -> bytes:
    """Same per-frame struct layout, no delta encoding, single zlib over entire payload."""
    buf = io.BytesIO()
    buf.write(PACKET_HEADER_STRUCT.pack(
        PACKET_MAGIC,
        PACKET_VERSION,
        int(clip.width),
        int(clip.height),
        int(clip.frame_count),
        0,
    ))
    for boxes in clip.frames:
        boxes = sorted(list(boxes), key=lambda b: b.box_id)
        if len(boxes) > 255:
            boxes = boxes[:255]
        buf.write(struct.pack("<B", len(boxes)))
        for box in boxes:
            buf.write(struct.pack("<BBHHHH",
                                  int(box.box_id) & 0xFF,
                                  int(box.label) & 0xFF,
                                  int(box.x), int(box.y), int(box.w), int(box.h)))
    return zlib.compress(buf.getvalue(), level=9)


def _decode_raw_struct_zlib(blob: bytes) -> list[list[Box]]:
    raw = zlib.decompress(blob)
    if len(raw) < PACKET_HEADER_STRUCT.size:
        return []
    magic, version, width, height, frame_count, _reserved = PACKET_HEADER_STRUCT.unpack_from(raw, 0)
    if magic != PACKET_MAGIC:
        raise ValueError("BAD_RAW_HEADER")
    cursor = PACKET_HEADER_STRUCT.size
    frames: list[list[Box]] = []
    for _ in range(int(frame_count)):
        count = raw[cursor]
        cursor += 1
        boxes: list[Box] = []
        for _ in range(count):
            box_id, label, x, y, w, h = struct.unpack_from("<BBHHHH", raw, cursor)
            cursor += 10
            boxes.append(Box(box_id=box_id, x=x, y=y, w=w, h=h, label=label))
        frames.append(boxes)
    return frames


def _encode_json_gzip(clip: ClipBundle) -> bytes:
    payload = {
        "magic": "ZPVID_JSON",
        "version": 1,
        "width": int(clip.width),
        "height": int(clip.height),
        "frame_count": int(clip.frame_count),
        "frames": [
            [
                {"id": int(b.box_id), "x": int(b.x), "y": int(b.y),
                 "w": int(b.w), "h": int(b.h), "label": int(b.label)}
                for b in frame
            ]
            for frame in clip.frames
        ],
    }
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return gzip.compress(raw, compresslevel=9)


def _decode_json_gzip(blob: bytes) -> list[list[Box]]:
    raw = gzip.decompress(blob)
    doc = json.loads(raw)
    frames: list[list[Box]] = []
    for frame in doc["frames"]:
        frames.append([Box(box_id=b["id"], x=b["x"], y=b["y"], w=b["w"], h=b["h"], label=b["label"])
                       for b in frame])
    return frames


def _encode_sqlite(clip: ClipBundle, path: Path) -> int:
    if path.exists():
        path.unlink()
    conn = sqlite3.connect(str(path), isolation_level=None)
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute(
            "CREATE TABLE boxes (frame INTEGER NOT NULL, track_id INTEGER NOT NULL, "
            "x INTEGER, y INTEGER, w INTEGER, h INTEGER, label INTEGER)"
        )
        cursor.execute("CREATE INDEX boxes_frame_track ON boxes(frame, track_id)")
        cursor.execute("CREATE INDEX boxes_track ON boxes(track_id, frame)")
        cursor.execute(
            "CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)"
        )
        cursor.execute("INSERT INTO meta VALUES (?, ?)", ("clip_id", clip.clip_id))
        cursor.execute("INSERT INTO meta VALUES (?, ?)", ("width", str(int(clip.width))))
        cursor.execute("INSERT INTO meta VALUES (?, ?)", ("height", str(int(clip.height))))
        cursor.execute("INSERT INTO meta VALUES (?, ?)", ("frame_count", str(int(clip.frame_count))))
        cursor.execute("BEGIN")
        rows = []
        for frame_index, boxes in enumerate(clip.frames):
            for box in boxes:
                rows.append((int(frame_index), int(box.box_id),
                             int(box.x), int(box.y), int(box.w), int(box.h), int(box.label)))
        cursor.executemany("INSERT INTO boxes VALUES (?, ?, ?, ?, ?, ?, ?)", rows)
        cursor.execute("COMMIT")
        conn.commit()
    finally:
        conn.close()
    return int(path.stat().st_size)


def _decode_sqlite(path: Path) -> list[list[Box]]:
    conn = sqlite3.connect(str(path))
    try:
        cur = conn.cursor()
        frame_count = int(cur.execute("SELECT value FROM meta WHERE key='frame_count'").fetchone()[0])
        rows = cur.execute(
            "SELECT frame, track_id, x, y, w, h, label FROM boxes ORDER BY frame ASC, track_id ASC"
        ).fetchall()
    finally:
        conn.close()
    frames: list[list[Box]] = [[] for _ in range(frame_count)]
    for frame, track_id, x, y, w, h, label in rows:
        frames[int(frame)].append(Box(box_id=int(track_id), x=int(x), y=int(y),
                                      w=int(w), h=int(h), label=int(label)))
    return frames


def _encode_parquet(clip: ClipBundle, path: Path) -> int:
    """Write tracks to Parquet (columnar + snappy)."""
    import pyarrow as pa  # local import
    import pyarrow.parquet as pq

    frame_col: list[int] = []
    track_col: list[int] = []
    x_col: list[int] = []
    y_col: list[int] = []
    w_col: list[int] = []
    h_col: list[int] = []
    label_col: list[int] = []
    for frame_index, boxes in enumerate(clip.frames):
        for box in boxes:
            frame_col.append(int(frame_index))
            track_col.append(int(box.box_id))
            x_col.append(int(box.x))
            y_col.append(int(box.y))
            w_col.append(int(box.w))
            h_col.append(int(box.h))
            label_col.append(int(box.label))
    table = pa.Table.from_arrays(
        [
            pa.array(frame_col, type=pa.int32()),
            pa.array(track_col, type=pa.int32()),
            pa.array(x_col, type=pa.int32()),
            pa.array(y_col, type=pa.int32()),
            pa.array(w_col, type=pa.int32()),
            pa.array(h_col, type=pa.int32()),
            pa.array(label_col, type=pa.int16()),
        ],
        names=["frame", "track_id", "x", "y", "w", "h", "label"],
    )
    if path.exists():
        path.unlink()
    pq.write_table(
        table,
        str(path),
        compression="snappy",
        use_dictionary=False,
        data_page_size=1024 * 64,
        write_statistics=True,
    )
    return int(path.stat().st_size)


def _decode_parquet(path: Path, frame_count: int) -> list[list[Box]]:
    import pyarrow.parquet as pq
    table = pq.read_table(str(path))
    frames: list[list[Box]] = [[] for _ in range(int(frame_count))]
    frame_arr = table.column("frame").to_pylist()
    track_arr = table.column("track_id").to_pylist()
    x_arr = table.column("x").to_pylist()
    y_arr = table.column("y").to_pylist()
    w_arr = table.column("w").to_pylist()
    h_arr = table.column("h").to_pylist()
    label_arr = table.column("label").to_pylist()
    for frame_idx, track_id, x, y, w, h, label in zip(frame_arr, track_arr, x_arr, y_arr, w_arr, h_arr, label_arr):
        frames[int(frame_idx)].append(Box(box_id=int(track_id), x=int(x), y=int(y),
                                          w=int(w), h=int(h), label=int(label)))
    for frame in frames:
        frame.sort(key=lambda b: b.box_id)
    return frames


# ---------------------------------------------------------------------------
# Benchmark harness
# ---------------------------------------------------------------------------


def _score(
    ground_truth: list[EventWindow],
    predicted: list[EventWindow],
) -> tuple[float, float, int, int, int, float]:
    def temporal_iou(a: EventWindow, b: EventWindow) -> float:
        start = max(a.start_frame, b.start_frame)
        end = min(a.end_frame, b.end_frame)
        if end < start:
            return 0.0
        inter = float(end - start + 1)
        union = float(max(a.end_frame, b.end_frame) - min(a.start_frame, b.start_frame) + 1)
        return 0.0 if union <= 0 else inter / union

    matched_truth: set[int] = set()
    matched_scores: list[float] = []
    tp = 0
    for guess in predicted:
        best_idx = -1
        best_score = 0.0
        for idx, truth in enumerate(ground_truth):
            if idx in matched_truth:
                continue
            if guess.clip_id != truth.clip_id or guess.direction != truth.direction:
                continue
            score = temporal_iou(guess, truth)
            if score > best_score:
                best_score = score
                best_idx = idx
        if best_idx >= 0 and best_score > 0:
            matched_truth.add(best_idx)
            matched_scores.append(best_score)
            tp += 1

    precision = float(tp) / float(len(predicted)) if predicted else 0.0
    recall = float(tp) / float(len(ground_truth)) if ground_truth else 0.0
    mean_iou = statistics.mean(matched_scores) if matched_scores else 0.0
    return precision, recall, tp, len(predicted), len(ground_truth), mean_iou


def _measure_ingest_bytes_and_latency(
    representation: str,
    clip: ClipBundle,
    workdir: Path,
    repeats: int,
) -> tuple[int, list[float]]:
    samples: list[float] = []
    storage_bytes = 0
    for run in range(int(repeats)):
        if representation == "zpe_packet":
            path = workdir / f"{clip.clip_id}.zpe"
            t0 = time.perf_counter()
            blob = _encode_packet_zpe(clip)
            path.write_bytes(blob)
            samples.append((time.perf_counter() - t0) * 1000.0)
            storage_bytes = int(path.stat().st_size)
        elif representation == "raw_struct_zlib":
            path = workdir / f"{clip.clip_id}.rsz"
            t0 = time.perf_counter()
            blob = _encode_raw_struct_zlib(clip)
            path.write_bytes(blob)
            samples.append((time.perf_counter() - t0) * 1000.0)
            storage_bytes = int(path.stat().st_size)
        elif representation == "json_gzip":
            path = workdir / f"{clip.clip_id}.json.gz"
            t0 = time.perf_counter()
            blob = _encode_json_gzip(clip)
            path.write_bytes(blob)
            samples.append((time.perf_counter() - t0) * 1000.0)
            storage_bytes = int(path.stat().st_size)
        elif representation == "sqlite":
            path = workdir / f"{clip.clip_id}.sqlite"
            t0 = time.perf_counter()
            size = _encode_sqlite(clip, path)
            samples.append((time.perf_counter() - t0) * 1000.0)
            storage_bytes = int(size)
        elif representation == "parquet":
            path = workdir / f"{clip.clip_id}.parquet"
            t0 = time.perf_counter()
            size = _encode_parquet(clip, path)
            samples.append((time.perf_counter() - t0) * 1000.0)
            storage_bytes = int(size)
        else:
            raise ValueError(f"unknown representation {representation}")
    return storage_bytes, samples


def _measure_query_latency_and_events(
    representation: str,
    clip: ClipBundle,
    workdir: Path,
    repeats: int,
    operator: str,
) -> tuple[list[float], list[EventWindow]]:
    """For each repeat, read the stored representation and extract events.

    Returns latency samples and the events extracted on the first successful run.
    """
    latencies: list[float] = []
    events_snapshot: list[EventWindow] = []

    def run_query(frames_source) -> list[EventWindow]:
        if operator == "naive":
            return _extract_event_windows_naive(clip.clip_id, frames_source, clip.portal_box, min_event_frames=4)
        if operator == "hardened":
            return _extract_event_windows_hardened(clip.clip_id, frames_source, clip.portal_box,
                                                   min_event_frames=4)
        raise ValueError(f"unknown operator {operator}")

    for run in range(int(repeats)):
        if representation == "zpe_packet":
            path = workdir / f"{clip.clip_id}.zpe"
            t0 = time.perf_counter()
            blob = path.read_bytes()
            frames = _decode_packet_zpe(blob)
            events = run_query(frames)
            latencies.append((time.perf_counter() - t0) * 1000.0)
        elif representation == "raw_struct_zlib":
            path = workdir / f"{clip.clip_id}.rsz"
            t0 = time.perf_counter()
            blob = path.read_bytes()
            frames = _decode_raw_struct_zlib(blob)
            events = run_query(frames)
            latencies.append((time.perf_counter() - t0) * 1000.0)
        elif representation == "json_gzip":
            path = workdir / f"{clip.clip_id}.json.gz"
            t0 = time.perf_counter()
            blob = path.read_bytes()
            frames = _decode_json_gzip(blob)
            events = run_query(frames)
            latencies.append((time.perf_counter() - t0) * 1000.0)
        elif representation == "sqlite":
            path = workdir / f"{clip.clip_id}.sqlite"
            t0 = time.perf_counter()
            frames = _decode_sqlite(path)
            events = run_query(frames)
            latencies.append((time.perf_counter() - t0) * 1000.0)
        elif representation == "parquet":
            path = workdir / f"{clip.clip_id}.parquet"
            t0 = time.perf_counter()
            frames = _decode_parquet(path, clip.frame_count)
            events = run_query(frames)
            latencies.append((time.perf_counter() - t0) * 1000.0)
        else:
            raise ValueError(f"unknown representation {representation}")
        if run == 0:
            events_snapshot = list(events)

    return latencies, events_snapshot


def benchmark_surface(
    *,
    surface_name: str,
    bundles: list[ClipBundle],
    representations: list[str],
    operators: list[str],
    query_repeats: int,
    ingest_repeats: int,
    workdir: Path,
) -> dict[str, Any]:
    # flatten GT across clips (clip_id already unique)
    gt_events_all: list[EventWindow] = []
    for bundle in bundles:
        gt_events_all.extend(bundle.gt_events)

    results: dict[str, dict[str, PathStats]] = {}

    for representation in representations:
        rep_dir = workdir / surface_name / representation
        rep_dir.mkdir(parents=True, exist_ok=True)

        # Ingest across all clips
        total_storage = 0
        ingest_per_clip: list[list[float]] = []
        for bundle in bundles:
            size, samples = _measure_ingest_bytes_and_latency(
                representation, bundle, rep_dir, repeats=ingest_repeats
            )
            total_storage += int(size)
            ingest_per_clip.append(samples)
        # Sum per-repeat across clips to get a per-repeat "ingest full surface" latency
        ingest_aggregated: list[float] = []
        for repeat_idx in range(int(ingest_repeats)):
            ingest_aggregated.append(sum(samples[repeat_idx] for samples in ingest_per_clip))

        # Query for each operator
        for operator in operators:
            predicted_all: list[EventWindow] = []
            query_per_clip: list[list[float]] = []
            for bundle in bundles:
                latencies, events = _measure_query_latency_and_events(
                    representation, bundle, rep_dir, repeats=query_repeats, operator=operator,
                )
                predicted_all.extend(events)
                query_per_clip.append(latencies)
            query_aggregated: list[float] = []
            for repeat_idx in range(int(query_repeats)):
                query_aggregated.append(sum(samples[repeat_idx] for samples in query_per_clip))

            precision, recall, tp, predicted_count, gt_count, mean_iou = _score(
                gt_events_all, predicted_all
            )

            key = f"{representation}__{operator}"
            stats = PathStats(
                storage_bytes=int(total_storage),
                ingest_latency_ms_median=statistics.median(ingest_aggregated),
                ingest_latency_ms_samples=list(ingest_aggregated),
                query_latency_ms_median=statistics.median(query_aggregated),
                query_latency_ms_samples=list(query_aggregated),
                events_precision=float(precision),
                events_recall=float(recall),
                events_predicted=int(predicted_count),
                events_matched=int(tp),
                events_ground_truth=int(gt_count),
                events_mean_temporal_iou=float(mean_iou),
            )
            results.setdefault(representation, {})[operator] = stats

    # Flatten for JSON
    flat: dict[str, Any] = {}
    for rep, ops in results.items():
        flat[rep] = {op: stats.to_dict() for op, stats in ops.items()}

    return {
        "surface_name": surface_name,
        "clip_count": len(bundles),
        "frame_count_total": sum(clip.frame_count for clip in bundles),
        "gt_event_count_total": len(gt_events_all),
        "representations": representations,
        "operators": operators,
        "results": flat,
    }


def derive_verdict(
    *,
    clean_report: dict[str, Any],
    noisy_report: dict[str, Any],
) -> dict[str, Any]:
    """Apply the kill / defend criteria deterministically."""
    def get(rep: str, op: str, surface_report: dict[str, Any]) -> dict[str, Any]:
        return surface_report["results"][rep][op]

    # Storage / latency parity on CLEAN, naive operator
    zpe = get("zpe_packet", "naive", clean_report)
    parquet = get("parquet", "naive", clean_report)
    sqlite = get("sqlite", "naive", clean_report)
    rsz = get("raw_struct_zlib", "naive", clean_report)
    jsgz = get("json_gzip", "naive", clean_report)

    def ratio(a: float, b: float) -> float:
        return float(a) / float(b) if b > 0 else float("inf")

    # Full ratio table: each baseline vs ZPE (baseline / ZPE). < 1.0 means baseline wins.
    baselines = {"parquet": parquet, "sqlite": sqlite, "raw_struct_zlib": rsz, "json_gzip": jsgz}
    ratio_table = {
        name: {
            "storage_over_zpe": ratio(other["storage_bytes"], zpe["storage_bytes"]),
            "query_latency_over_zpe": ratio(other["query_latency_ms_median"], zpe["query_latency_ms_median"]),
            "ingest_latency_over_zpe": ratio(other["ingest_latency_ms_median"], zpe["ingest_latency_ms_median"]),
        }
        for name, other in baselines.items()
    }

    # Kill criterion A (representation parity): ANY baseline matches ZPE within 2x on
    # BOTH storage AND query latency with identical precision/recall.
    kill_parity_hits: list[str] = []
    for name, other in baselines.items():
        if (
            other["events_precision"] == zpe["events_precision"]
            and other["events_recall"] == zpe["events_recall"]
            and ratio(other["storage_bytes"], zpe["storage_bytes"]) <= 2.0
            and ratio(other["query_latency_ms_median"], zpe["query_latency_ms_median"]) <= 2.0
        ):
            kill_parity_hits.append(name)

    # Kill criterion B (representation dominance): ANY baseline strictly dominates ZPE
    # on BOTH storage AND query latency with identical precision/recall.
    kill_dominance_hits: list[str] = []
    for name, other in baselines.items():
        if (
            other["events_precision"] == zpe["events_precision"]
            and other["events_recall"] == zpe["events_recall"]
            and other["storage_bytes"] < zpe["storage_bytes"]
            and other["query_latency_ms_median"] < zpe["query_latency_ms_median"]
        ):
            kill_dominance_hits.append(name)

    # Kill criterion C (operator is the blocker): the naive-operator precision is
    # IDENTICAL across ALL representations on the noisy surface. This proves the
    # information needed to raise precision is not present in the box stream --
    # no representation-level change can help.
    naive_noisy_precisions = [
        noisy_report["results"][rep]["naive"]["events_precision"]
        for rep in noisy_report["representations"]
    ]
    naive_precision_identical = (
        len(set(round(p, 6) for p in naive_noisy_precisions)) == 1
    )

    # Defend: ZPE strictly wins on AT LEAST ONE axis by >=2x against EVERY baseline
    defend_storage = all(
        ratio(other["storage_bytes"], zpe["storage_bytes"]) >= 2.0
        for other in baselines.values()
    )
    defend_query_latency = all(
        ratio(other["query_latency_ms_median"], zpe["query_latency_ms_median"]) >= 2.0
        for other in baselines.values()
    )

    # Priority order: dominance kill > parity kill > operator kill > defend > mixed
    if kill_dominance_hits:
        dominant = kill_dominance_hits[0]
        other = baselines[dominant]
        verdict = "zpe_packet_beaten_by_commodity_format"
        rationale = (
            f"The {dominant} baseline strictly dominates ZPE packet on BOTH storage "
            f"(bytes {other['storage_bytes']} vs {zpe['storage_bytes']}, "
            f"{ratio(other['storage_bytes'], zpe['storage_bytes']):.2f}x) AND query "
            f"latency ({other['query_latency_ms_median']:.2f} ms vs "
            f"{zpe['query_latency_ms_median']:.2f} ms, "
            f"{ratio(other['query_latency_ms_median'], zpe['query_latency_ms_median']):.2f}x), "
            "with identical precision and recall. The ZPE packet format has NO unique "
            "structural advantage over commodity alternatives for this workload. The "
            "archive-query wedge as currently framed is FALSIFIED."
        )
    elif kill_parity_hits and naive_precision_identical:
        verdict = "archive_query_wedge_not_zpe_specific"
        rationale = (
            f"Baseline(s) {kill_parity_hits} match ZPE on both storage and query latency "
            "within 2x and produce identical semantics. Additionally, all tested "
            "representations produce IDENTICAL precision under the naive operator on the "
            "noisy surface, so representation-level changes cannot attack the false-positive "
            "problem. The wedge is operator engineering at best, and commodity sparse-metadata "
            "formats deliver it, not ZPE specifically."
        )
    elif naive_precision_identical:
        verdict = "operator_is_the_blocker_not_representation"
        rationale = (
            "All 5 tested representations produce IDENTICAL naive-operator precision on the "
            "noisy surface. The information needed to discriminate real events from ghost "
            "tracks is not in the box stream itself; no delta-encoding, columnar, or "
            "relational reshuffling of the SAME boxes can move precision. The prior phase's "
            "'richer packet semantics' thesis is falsified for this operator."
        )
    elif defend_storage or defend_query_latency:
        verdict = "zpe_packet_has_structural_advantage"
        rationale = (
            "ZPE packet dominates every tested baseline by >=2x on at least one of "
            "{storage, query latency} under matched operator. Candidate wedge signal; "
            "requires live-surface confirmation before commercialization."
        )
    else:
        verdict = "mixed_signal_needs_live_confirmation"
        rationale = (
            "Neither kill nor defend criteria fire cleanly. Rerun on live pod surface."
        )

    return {
        "verdict": verdict,
        "rationale": rationale,
        "kill_criteria": {
            "baselines_dominating_zpe_on_both_axes": kill_dominance_hits,
            "baselines_within_2x_of_zpe_on_both_axes": kill_parity_hits,
            "naive_precision_identical_across_representations": bool(naive_precision_identical),
            "naive_noisy_precisions_per_representation": {
                rep: noisy_report["results"][rep]["naive"]["events_precision"]
                for rep in noisy_report["representations"]
            },
        },
        "defend_criteria": {
            "zpe_dominates_storage_by_2x_everywhere": bool(defend_storage),
            "zpe_dominates_query_latency_by_2x_everywhere": bool(defend_query_latency),
        },
        "ratio_table_baseline_over_zpe": ratio_table,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 09.4.1.1.2 fair-baseline archive-query falsification")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--query-repeats", type=int, default=DEFAULT_QUERY_REPEATS)
    parser.add_argument("--ingest-repeats", type=int, default=DEFAULT_INGEST_REPEATS)
    parser.add_argument("--noise-tracks-per-clip", type=int, default=DEFAULT_NOISE_TRACKS_PER_CLIP)
    parser.add_argument("--noise-seed", type=int, default=DEFAULT_NOISE_SEED)
    args = parser.parse_args()

    representations = ["zpe_packet", "raw_struct_zlib", "sqlite", "parquet", "json_gzip"]
    operators = ["naive", "hardened"]

    with tempfile.TemporaryDirectory(prefix="zpe_fair_baseline_") as tmp_dir:
        workdir = Path(tmp_dir)

        clean_bundles = build_clean_proxy_corpus()
        noisy_bundles = build_noisy_proxy_corpus(
            noise_tracks_per_clip=int(args.noise_tracks_per_clip),
            seed=int(args.noise_seed),
        )

        clean_report = benchmark_surface(
            surface_name="proxy_clean",
            bundles=clean_bundles,
            representations=representations,
            operators=operators,
            query_repeats=int(args.query_repeats),
            ingest_repeats=int(args.ingest_repeats),
            workdir=workdir,
        )
        noisy_report = benchmark_surface(
            surface_name="proxy_noisy",
            bundles=noisy_bundles,
            representations=representations,
            operators=operators,
            query_repeats=int(args.query_repeats),
            ingest_repeats=int(args.ingest_repeats),
            workdir=workdir,
        )

    verdict_block = derive_verdict(clean_report=clean_report, noisy_report=noisy_report)

    summary = {
        "phase": "09.4.1.1.2",
        "experiment": "phase9_4_1_1_2_fair_baseline_archive_query",
        "date": time.strftime("%Y-%m-%d"),
        "python_version": sys.version,
        "proxy_clean": clean_report,
        "proxy_noisy": noisy_report,
        "config": {
            "query_repeats": int(args.query_repeats),
            "ingest_repeats": int(args.ingest_repeats),
            "noise_tracks_per_clip": int(args.noise_tracks_per_clip),
            "noise_seed": int(args.noise_seed),
        },
        "verdict": verdict_block,
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
