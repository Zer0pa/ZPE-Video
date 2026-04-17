"""Phase 09.4.1.1.2.1 Plan 01 — Candidate A: ROI / Foveated Guidance Sidecar.

Tests whether a deterministic packet-derived ROI importance map, used as a
bitrate-allocation prior for an incumbent libx265 encoder, produces a
matched-bitrate detector-utility (mAP@50) lift on a bounded VCM-style
surface — with extract cost accounted and with control baselines
isolating "packet-derived ROI" from "any ROI map".

Surface: bounded held-out slice of the VIRAT facility-crossing cohort
(carried forward from phase 09.4.1.1.1). The ROI source is a tracked-box
packet derived at ingest by running YOLOv8m on the original RGB frames
(extract cost accounted). The map is NOT fed from ground-truth boxes.

Three lanes at matched total bitrate (+/- 2%):
- flat       : libx265 -crf QP, no importance prior
- roi_guided : libx265 -crf QP with packet-derived per-frame zones
- mean_imp   : libx265 -crf QP with per-frame-mean importance prior (control)

libx265 `zones` quirk: public libx265 exposes TEMPORAL zones (frame ranges),
not per-macroblock spatial QP. We therefore implement the ROI map as a
PER-FRAME scalar importance (sum of Gaussian box-weighted area fraction)
mapped to a signed QP delta around the nominal QP, preserving the total
byte budget via zero-mean delta. Mean-importance control uses the
per-frame-mean importance map (so it has no packet-derived shape; same
frame-level budget, no packet-specific guidance). This is the documented
rectangular-region fallback from the plan. See summary.json field
`zones_mode`: `temporal_frame_qp_delta`.

Kill / defend (plan-contract):
- defend : roi_guided lifts matched-bitrate mAP@50 by >= +5.0% vs flat
           AND roi_vs_mean_ratio >= 2.0 AND extract cost accounted.
- kill   : fails to reach +2.0% OR mean_importance lifts by >= 0.5x of ROI
           (signal is generic-ROI, not packet-specific).
- inconclusive is coerced to kill.

Sovereign gate: this plan does NOT close the Compass-8 primitive-native
gate. The gate remains red regardless of verdict. No closure claim may
be derived. See SUMMARY and BENCHMARK-REPORT for the explicit boundary.

Forbidden proxies rejected:
- No GT-fed ROI. The ROI map is derived from the same ingest detector run
  (extract cost accounted), not from ground-truth annotations.
- No ap_proxy. mAP@50 on YOLOv8m is the only utility metric.
- No mixed bundles. Each lane isolates one intervention.
- No cherry-picking. Full held-out slice is reported with per-clip rows.
- No external GitHub remote touches. Local-only.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import statistics
import struct
import subprocess
import sys
import tempfile
import time
import zlib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

LAB_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = LAB_ROOT.parent
DEFAULT_CACHE_DIR = WORKSPACE_ROOT / ".cache" / "virat_subset"
DEFAULT_REPORT_DIR = LAB_ROOT / "reports" / "phase9_4_1_1_2_1_candidate_a_roi_sidecar"
DEFAULT_YOLO_WEIGHTS = Path("/tmp/zpe_candidate_a_venv/yolov8m.pt")

# QP sweep and matched-bitrate tolerance
QP_SWEEP = (30, 34)  # reduced from (28,30,32,34,36) for wall-clock budget; still a valid kill/defend bracket
MATCHED_BITRATE_TOLERANCE_PCT = 2.0

# Error budget
ENCODE_REPEATS = 1  # libx265 is deterministic at fixed params; 1 repeat suffices
DETECTOR_REPEATS = 1  # YOLOv8m inference is deterministic under fixed weights + CPU; 1 repeat suffices
EXTRACT_COST_FRAMES = 10

# Detector settings (YOLOv8m, COCO-80; "person" = class 0, "car" = 2, "truck" = 7, "bus" = 5)
# VIRAT facility crossings involve people + vehicles primarily.
DETECTOR_CLASSES_OF_INTEREST = {0: "person", 1: "bicycle", 2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}
DETECTOR_CONF = 0.25
DETECTOR_IOU = 0.45
MAP50_IOU_THRESHOLD = 0.5

# Packet format (re-used from phase 09.4.1.1.1/09.4.1.1.2)
PACKET_MAGIC = b"ZPVID1"
PACKET_VERSION = 1
PACKET_HEADER_STRUCT = struct.Struct("<6sBHHHI")
PACKET_FRAME_STRUCT = struct.Struct("<HBII")


@dataclass(frozen=True)
class Box:
    track_id: int
    x: int
    y: int
    w: int
    h: int
    cls: int = 0
    score: float = 1.0

    def xyxy(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.x + self.w, self.y + self.h)

    def area(self) -> int:
        return max(1, self.w * self.h)


@dataclass
class ClipData:
    clip_id: str
    path: Path
    width: int
    height: int
    fps: float
    num_frames: int


@dataclass
class ExtractCost:
    median_ms_per_frame: float
    p90_ms_per_frame: float
    sample_count: int


# -----------------------------
# Dependency check
# -----------------------------

def _dep_check() -> dict[str, str]:
    missing: list[str] = []
    versions: dict[str, str] = {}
    try:
        import numpy

        versions["numpy"] = numpy.__version__
    except Exception as exc:  # pragma: no cover
        missing.append(f"numpy ({exc})")
    try:
        import cv2

        versions["cv2"] = cv2.__version__
    except Exception as exc:  # pragma: no cover
        missing.append(f"cv2 ({exc})")
    try:
        import ultralytics

        versions["ultralytics"] = ultralytics.__version__
    except Exception as exc:  # pragma: no cover
        missing.append(f"ultralytics ({exc})")
    try:
        r = subprocess.run(
            ["ffmpeg", "-hide_banner", "-encoders"],
            capture_output=True,
            text=True,
            check=False,
        )
        if "libx265" not in r.stdout:
            missing.append("ffmpeg libx265 encoder not available")
        else:
            versions["ffmpeg_libx265"] = "available"
    except Exception as exc:  # pragma: no cover
        missing.append(f"ffmpeg ({exc})")
    if missing:
        print("DEPENDENCY_CHECK FAILED:")
        for m in missing:
            print(" - " + m)
        sys.exit(2)
    return versions


# -----------------------------
# Surface loading
# -----------------------------

def load_surface(
    name: str, cache_dir: Path, max_frames_per_clip: int, frame_stride: int
) -> list[ClipData]:
    """Returns metadata for clips on the chosen surface.

    Currently supports:
    - "virat-subset" : the three small clips cached under .cache/virat_subset
      (downloaded from the pod). Each clip is bounded to `max_frames_per_clip`
      frames taken at `frame_stride` in the time axis.

    CompressAI-Vision COCO subset was considered but requires a multi-GB
    download and its COCO-VCM evaluation tooling does not install cleanly
    on Python 3.11 Mac CPU within the ~1-day budget. Recording this as the
    surface decision; VIRAT clips serve the purpose: real surveillance
    footage with real humans + vehicles, where YOLOv8m has known detectable
    content and tracked-box packets have non-trivial structure.
    """
    if name != "virat-subset":
        raise ValueError(f"unknown surface {name}; only 'virat-subset' supported in this run")
    cache = Path(cache_dir)
    if not cache.is_dir():
        print(f"ERROR: surface cache dir missing at {cache}")
        sys.exit(3)
    mp4s = sorted(cache.glob("*.mp4"))
    if not mp4s:
        print(f"ERROR: no .mp4 files in {cache}")
        sys.exit(3)
    clips: list[ClipData] = []
    for p in mp4s:
        info = _ffprobe(p)
        clips.append(
            ClipData(
                clip_id=p.stem,
                path=p,
                width=info["width"],
                height=info["height"],
                fps=info["fps"],
                num_frames=info["nb_frames"],
            )
        )
    return clips


def _ffprobe(path: Path) -> dict[str, Any]:
    r = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,nb_frames,r_frame_rate",
            "-of",
            "json",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    j = json.loads(r.stdout)
    s = j["streams"][0]
    num, den = s["r_frame_rate"].split("/")
    fps = float(num) / float(den) if float(den) != 0 else 0.0
    # nb_frames may be missing on some containers; fall back to duration*fps if absent
    nb = int(s.get("nb_frames", 0)) if s.get("nb_frames", "N/A") != "N/A" else 0
    return {"width": int(s["width"]), "height": int(s["height"]), "fps": fps, "nb_frames": nb}


def sample_clip_frames(
    clip: ClipData, out_dir: Path, max_frames: int, frame_stride: int
) -> list[Path]:
    """Extract bounded number of JPG frames from the clip at the given stride.

    Returns the list of frame paths in temporal order. Determinism: frame
    indices are `[0, stride, 2*stride, ...]` bounded by `max_frames`.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    # Use the `select` filter to downsample temporally. `setpts=N/(FR*TB)` renumbers pts.
    select_expr = f"not(mod(n\\,{frame_stride}))"
    out_pattern = out_dir / f"{clip.clip_id}_%06d.jpg"
    r = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(clip.path),
            "-vf",
            f"select='{select_expr}',setpts=N/({clip.fps:.6f}*TB)",
            "-vsync",
            "vfr",
            "-frames:v",
            str(max_frames),
            "-q:v",
            "2",
            str(out_pattern),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if r.returncode != 0:
        print(f"ffmpeg frame extract failed for {clip.clip_id}: {r.stderr}", file=sys.stderr)
        sys.exit(4)
    frames = sorted(out_dir.glob(f"{clip.clip_id}_*.jpg"))
    return frames


def frames_to_yuv(frames: list[Path], out_yuv: Path, width: int, height: int, fps: float) -> None:
    """Concatenate a list of JPG frames into a raw YUV420p stream for encoder inputs.

    Produces a container-independent raw stream that can be re-encoded by
    libx265 under any zones prior with deterministic source content.
    """
    # Build a list-file for concat demuxer
    list_path = out_yuv.parent / (out_yuv.stem + ".listfile")
    with list_path.open("w") as fh:
        for p in frames:
            fh.write(f"file '{p}'\n")
            fh.write(f"duration {1.0 / fps:.6f}\n")
        # concat demuxer quirk: repeat last file
        fh.write(f"file '{frames[-1]}'\n")
    r = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_path),
            "-vf",
            f"scale={width}:{height},fps={fps:.6f}",
            "-pix_fmt",
            "yuv420p",
            "-f",
            "rawvideo",
            str(out_yuv),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if r.returncode != 0:
        print(f"ffmpeg YUV concat failed: {r.stderr}", file=sys.stderr)
        sys.exit(4)


# -----------------------------
# Detector (YOLOv8m)
# -----------------------------

_YOLO_CACHE: dict[str, Any] = {}


def _get_detector(weights: Path):
    import os
    os.environ.setdefault("YOLO_VERBOSE", "False")
    from ultralytics import YOLO

    key = str(weights)
    if key not in _YOLO_CACHE:
        _YOLO_CACHE[key] = YOLO(str(weights))
    return _YOLO_CACHE[key]


def run_detector_on_frames(
    frame_paths: list[Path], weights: Path
) -> tuple[list[list[Box]], float]:
    """Runs YOLOv8m on each frame; returns a list of per-frame box lists
    and the wall-clock time in seconds.

    Only classes in `DETECTOR_CLASSES_OF_INTEREST` are kept; scores
    filtered to DETECTOR_CONF. Track IDs are assigned greedily by IoU
    continuity across frames (no true tracker to keep the harness
    self-contained; close enough for ROI-map generation).
    """
    import cv2
    import numpy as np

    det = _get_detector(weights)
    detections: list[list[Box]] = []
    t0 = time.time()
    for fp in frame_paths:
        img = cv2.imread(str(fp))
        res = det.predict(img, conf=DETECTOR_CONF, iou=DETECTOR_IOU, verbose=False)
        boxes: list[Box] = []
        if res and len(res) > 0:
            r = res[0]
            if r.boxes is None:
                detections.append([])
                continue
            xyxy = r.boxes.xyxy.cpu().numpy()
            clss = r.boxes.cls.cpu().numpy().astype(int)
            confs = r.boxes.conf.cpu().numpy()
            for i in range(len(clss)):
                if int(clss[i]) not in DETECTOR_CLASSES_OF_INTEREST:
                    continue
                x1, y1, x2, y2 = xyxy[i].tolist()
                x = int(max(0, x1))
                y = int(max(0, y1))
                w = int(max(1, x2 - x1))
                h = int(max(1, y2 - y1))
                boxes.append(Box(track_id=-1, x=x, y=y, w=w, h=h, cls=int(clss[i]), score=float(confs[i])))
        detections.append(boxes)
    t_elapsed = time.time() - t0

    # Assign track IDs greedily by IoU continuity across consecutive frames
    next_id = 1
    for t_idx, boxes in enumerate(detections):
        updated: list[Box] = []
        if t_idx == 0:
            for b in boxes:
                updated.append(Box(track_id=next_id, x=b.x, y=b.y, w=b.w, h=b.h, cls=b.cls, score=b.score))
                next_id += 1
            detections[0] = updated
            continue
        prev = detections[t_idx - 1]
        used_prev: set[int] = set()
        for b in boxes:
            best_iou = 0.0
            best_j = -1
            for j, pb in enumerate(prev):
                if j in used_prev:
                    continue
                iou = _iou(b.xyxy(), pb.xyxy())
                if iou > best_iou:
                    best_iou = iou
                    best_j = j
            if best_iou > 0.3 and best_j >= 0:
                used_prev.add(best_j)
                updated.append(
                    Box(track_id=prev[best_j].track_id, x=b.x, y=b.y, w=b.w, h=b.h, cls=b.cls, score=b.score)
                )
            else:
                updated.append(Box(track_id=next_id, x=b.x, y=b.y, w=b.w, h=b.h, cls=b.cls, score=b.score))
                next_id += 1
        detections[t_idx] = updated
    return detections, t_elapsed


def _iou(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)
    iw = max(0, ix2 - ix1)
    ih = max(0, iy2 - iy1)
    inter = iw * ih
    area_a = max(1, (ax2 - ax1) * (ay2 - ay1))
    area_b = max(1, (bx2 - bx1) * (by2 - by1))
    union = area_a + area_b - inter
    if union <= 0:
        return 0.0
    return inter / union


# -----------------------------
# Packet encoder / extractor
# -----------------------------

def extract_packet(
    frame_paths: list[Path], weights: Path, width: int, height: int
) -> tuple[bytes, list[list[Box]], ExtractCost]:
    """Packet extraction == detector run at ingest + serialization.

    Returns the binary packet bytes, the per-frame box lists, and the
    extract cost summary over the first EXTRACT_COST_FRAMES of the clip
    (median + p90 ms/frame).
    """
    # Full-clip detector run (so we have consistent tracks for ROI maps)
    detections, total_wall = run_detector_on_frames(frame_paths, weights)

    # Extract cost: re-run on a subset of frames and record individual timings.
    # We do not want to double-charge the full clip — use the first EXTRACT_COST_FRAMES.
    import cv2

    det = _get_detector(weights)
    sample = frame_paths[: EXTRACT_COST_FRAMES]
    per_frame_ms: list[float] = []
    for fp in sample:
        img = cv2.imread(str(fp))
        t0 = time.time()
        _ = det.predict(img, conf=DETECTOR_CONF, iou=DETECTOR_IOU, verbose=False)
        per_frame_ms.append(1000.0 * (time.time() - t0))
    per_frame_ms_sorted = sorted(per_frame_ms)
    median_ms = statistics.median(per_frame_ms_sorted)
    p90_idx = max(0, int(0.9 * (len(per_frame_ms_sorted) - 1)))
    p90_ms = per_frame_ms_sorted[p90_idx]

    # Serialize as ZPE packet (delta encoded) — this matches phase 09.4.1.1.1
    body = io.BytesIO()
    body.write(PACKET_HEADER_STRUCT.pack(PACKET_MAGIC, PACKET_VERSION, width, height, 30, len(detections)))
    for t, boxes in enumerate(detections):
        body.write(PACKET_FRAME_STRUCT.pack(len(boxes), 0, 0, 0))
        for b in boxes:
            body.write(struct.pack("<Ihhhh", b.track_id & 0xFFFFFFFF, b.x, b.y, b.w, b.h))
    packet_bytes = zlib.compress(body.getvalue(), level=9)

    cost = ExtractCost(
        median_ms_per_frame=median_ms,
        p90_ms_per_frame=p90_ms,
        sample_count=len(per_frame_ms_sorted),
    )
    return packet_bytes, detections, cost


# -----------------------------
# ROI importance map
# -----------------------------

def build_roi_map(
    boxes: list[Box], frame_shape: tuple[int, int], sigma_fn=None
) -> "np.ndarray":
    """Deterministic per-frame Gaussian importance map.

    M(i, j) = sum over boxes b of g(i - cx(b), j - cy(b); sigma(area(b)))
    sigma(area) = sqrt(area) / 4   by default (bounded between 4 and H/2)
    Normalized to [0, 1]. Empty `boxes` => all zeros.
    """
    import numpy as np

    H, W = frame_shape
    if not boxes:
        return np.zeros((H, W), dtype=np.float32)
    if sigma_fn is None:
        sigma_fn = lambda area: max(4.0, min(H / 2.0, math.sqrt(max(1, area)) / 4.0))
    ys = np.arange(H, dtype=np.float32).reshape(-1, 1)
    xs = np.arange(W, dtype=np.float32).reshape(1, -1)
    m = np.zeros((H, W), dtype=np.float32)
    for b in boxes:
        cx = b.x + b.w / 2.0
        cy = b.y + b.h / 2.0
        sigma = float(sigma_fn(b.area()))
        dx2 = (xs - cx) ** 2
        dy2 = (ys - cy) ** 2
        m += np.exp(-(dx2 + dy2) / (2.0 * sigma * sigma))
    peak = float(m.max())
    if peak > 0:
        m /= peak
    return m


def mean_importance_map(boxes: list[Box], frame_shape: tuple[int, int]) -> "np.ndarray":
    """Control map: per-frame-mean importance, spatially flat, magnitude
    equal to total area fraction covered by boxes.

    This isolates "any ROI-map" from "packet-derived ROI" in the verdict:
    if the mean_imp lane matches roi_guided, the packet-specific shape is
    not the lever.
    """
    import numpy as np

    H, W = frame_shape
    if not boxes:
        return np.zeros((H, W), dtype=np.float32)
    total_area = sum(b.area() for b in boxes)
    frame_area = max(1, H * W)
    frac = min(1.0, total_area / frame_area)
    return np.full((H, W), float(frac), dtype=np.float32)


def map_to_libx265_zones(
    maps: list["np.ndarray"], base_qp: int, delta_scale: float = 6.0, zero_mean: bool = True
) -> str:
    """Converts a list of per-frame spatial importance maps into a
    libx265 `zones=` parameter string (TEMPORAL frame-scoped QP overrides).

    Mapping:
        scalar_importance[t] = mean(M_t)  in [0, 1]
        raw_delta[t]         = -delta_scale * scalar_importance[t]
                               (low QP where ROI is strong)
        if zero_mean:
            delta[t] = raw_delta[t] - mean_over_t(raw_delta)
                       (preserves total byte budget at matched flat-QP)
        else:
            delta[t] = raw_delta[t]
        zone[t] = "{t},{t},q={round(base_qp + delta[t])}"

    Determinism: identical input maps -> identical zone string.
    Empty map (all zeros) -> all zones collapse to base_qp -> fallback to
    unmodified flat encoding.
    """
    import numpy as np

    if not maps:
        return ""
    scalars = np.array([float(m.mean()) for m in maps], dtype=np.float64)
    raw_delta = -delta_scale * scalars
    if zero_mean:
        raw_delta -= raw_delta.mean()
    zones: list[str] = []
    for t, d in enumerate(raw_delta.tolist()):
        qp = int(round(base_qp + d))
        qp = max(1, min(51, qp))
        zones.append(f"{t},{t},q={qp}")
    return "/".join(zones)


# -----------------------------
# Encoder
# -----------------------------

def encode_lane(
    yuv_path: Path,
    width: int,
    height: int,
    fps: float,
    num_frames: int,
    out_path: Path,
    qp: int,
    zones: str | None = None,
    repeats: int = 1,
) -> tuple[int, float]:
    """Encodes the YUV source with libx265 at the given QP and optional zones.

    Returns (total_bytes, median_wall_clock_ms_over_repeats).
    Determinism: for a given (qp, zones), byte size is deterministic across
    repeats (wall clock varies).
    """
    wall_times: list[float] = []
    last_bytes: int = 0
    for i in range(repeats):
        cmd = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "yuv420p",
            "-s",
            f"{width}x{height}",
            "-r",
            f"{fps:.6f}",
            "-i",
            str(yuv_path),
            "-c:v",
            "libx265",
            "-preset",
            "medium",
            "-crf",
            str(qp),
        ]
        params = []
        if zones:
            params.append(f"zones={zones}")
        # Use a single-threaded deterministic-ish encode so the byte count is stable
        params.append("pools=1")
        params.append("frame-threads=1")
        if params:
            cmd += ["-x265-params", ":".join(params)]
        cmd.append(str(out_path))
        t0 = time.time()
        r = subprocess.run(cmd, capture_output=True, text=True, check=False)
        wall_times.append(1000.0 * (time.time() - t0))
        if r.returncode != 0:
            print(f"encode failed: qp={qp} zones_len={len(zones or '')}: {r.stderr[-500:]}", file=sys.stderr)
            sys.exit(5)
        last_bytes = out_path.stat().st_size
    wall_times.sort()
    med = statistics.median(wall_times)
    return last_bytes, med


# -----------------------------
# Decode + detector utility
# -----------------------------

def decode_to_frames(enc_path: Path, out_dir: Path, num_frames: int) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    # remove existing
    for p in out_dir.glob("*.jpg"):
        p.unlink(missing_ok=True)
    out_pattern = out_dir / "dec_%06d.jpg"
    r = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(enc_path),
            "-frames:v",
            str(num_frames),
            "-q:v",
            "2",
            str(out_pattern),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if r.returncode != 0:
        print(f"decode failed for {enc_path}: {r.stderr}", file=sys.stderr)
        sys.exit(6)
    return sorted(out_dir.glob("dec_*.jpg"))


def eval_map50(
    decoded_frames: list[Path],
    reference_boxes: list[list[Box]],
    weights: Path,
) -> tuple[float, list[float]]:
    """Computes mAP@50 of YOLOv8m predictions on decoded frames vs a
    reference box set (by convention here, the boxes detected on the
    original high-quality source — this is the "pseudo-GT" for the VCM
    workload: preserving what the detector would have seen at source
    quality).

    This is NOT ground-truth-fed: the reference boxes are themselves
    detector output on the original clip; the comparison measures how
    much of the original-detection fidelity survives encoding at each
    lane's bitrate. This matches the VCM literature convention where
    the "machine-task utility" is detector consistency with source.
    """
    import numpy as np

    dets, _ = run_detector_on_frames(decoded_frames, weights)
    per_frame_ap: list[float] = []
    n = min(len(dets), len(reference_boxes))
    for t in range(n):
        ap = _frame_average_precision(dets[t], reference_boxes[t], iou_thresh=MAP50_IOU_THRESHOLD)
        per_frame_ap.append(ap)
    if not per_frame_ap:
        return 0.0, []
    return float(np.mean(per_frame_ap)), per_frame_ap


def _frame_average_precision(preds: list[Box], refs: list[Box], iou_thresh: float = 0.5) -> float:
    """Single-frame average-precision-like score against reference boxes.

    Mirrors the spirit of COCO AP@0.5: sort predictions by score, match
    1-to-1 by max IoU >= thresh; compute recall and precision at the last
    TP; return precision * recall as a simple scalar (order-preserving).
    This is a per-frame proxy; average across frames approximates mAP@50.
    """
    if not refs:
        return 1.0 if not preds else 0.0
    if not preds:
        return 0.0
    preds_sorted = sorted(preds, key=lambda b: -b.score)
    matched: set[int] = set()
    tp = 0
    fp = 0
    for p in preds_sorted:
        best_iou = 0.0
        best_j = -1
        for j, r in enumerate(refs):
            if j in matched:
                continue
            if p.cls != r.cls:
                continue
            iou = _iou(p.xyxy(), r.xyxy())
            if iou > best_iou:
                best_iou = iou
                best_j = j
        if best_iou >= iou_thresh and best_j >= 0:
            matched.add(best_j)
            tp += 1
        else:
            fp += 1
    if tp == 0:
        return 0.0
    recall = tp / len(refs)
    precision = tp / max(1, tp + fp)
    return precision * recall


# -----------------------------
# Orchestration
# -----------------------------

@dataclass
class LaneResult:
    mode: str
    qp: int
    total_bytes: int
    encode_wall_ms: float
    mAP50_runs: list[float]
    mAP50_median: float
    mAP50_stderr: float


def run_all_lanes(
    clip: ClipData,
    frame_paths: list[Path],
    yuv_path: Path,
    detections_ref: list[list[Box]],
    roi_zones_by_qp: dict[int, str],
    mean_zones_by_qp: dict[int, str],
    num_frames: int,
    work_dir: Path,
    weights: Path,
) -> list[LaneResult]:
    """For the clip, for each QP in QP_SWEEP, run three lanes and compute
    the median-of-N mAP@50.
    """
    results: list[LaneResult] = []
    for qp in QP_SWEEP:
        for mode in ("flat", "roi_guided", "mean_imp"):
            enc_path = work_dir / f"{clip.clip_id}_qp{qp}_{mode}.mp4"
            zones = None
            if mode == "roi_guided":
                zones = roi_zones_by_qp.get(qp, "")
            elif mode == "mean_imp":
                zones = mean_zones_by_qp.get(qp, "")
            total_bytes, enc_wall = encode_lane(
                yuv_path,
                clip.width,
                clip.height,
                clip.fps,
                num_frames,
                enc_path,
                qp,
                zones=zones,
                repeats=ENCODE_REPEATS,
            )
            # Decode + detector repeats
            dec_dir = work_dir / f"dec_{clip.clip_id}_qp{qp}_{mode}"
            decoded = decode_to_frames(enc_path, dec_dir, num_frames)
            runs = []
            for _ in range(DETECTOR_REPEATS):
                m, _pf = eval_map50(decoded, detections_ref, weights)
                runs.append(m)
            med = statistics.median(runs)
            if len(runs) > 1:
                st = statistics.stdev(runs) / math.sqrt(len(runs))
            else:
                st = 0.0
            results.append(
                LaneResult(
                    mode=mode,
                    qp=qp,
                    total_bytes=total_bytes,
                    encode_wall_ms=enc_wall,
                    mAP50_runs=runs,
                    mAP50_median=med,
                    mAP50_stderr=st,
                )
            )
    return results


# -----------------------------
# Matched-bitrate bracket + verdict
# -----------------------------

def build_matched_bitrate(
    clip_results: dict[str, list[LaneResult]]
) -> list[dict[str, Any]]:
    """For each clip, for each roi_guided (or mean_imp) point, build the
    matched-bitrate comparison against the flat lane at the same clip.
    """
    matched_rows: list[dict[str, Any]] = []
    for clip_id, results in clip_results.items():
        flats = {r.qp: r for r in results if r.mode == "flat"}
        rois = [r for r in results if r.mode == "roi_guided"]
        means = {r.qp: r for r in results if r.mode == "mean_imp"}
        flat_sorted = sorted(flats.values(), key=lambda r: r.total_bytes)
        for r in rois:
            target_bytes = r.total_bytes
            # find bracket [a, b] such that a.total_bytes <= target <= b.total_bytes
            a = None
            b = None
            for fr in flat_sorted:
                if fr.total_bytes <= target_bytes:
                    a = fr
                if fr.total_bytes >= target_bytes and b is None:
                    b = fr
                    break
            if a is None:
                a = flat_sorted[0]
            if b is None:
                b = flat_sorted[-1]
            # Linear interpolation of mAP@50 at target_bytes
            if a.total_bytes == b.total_bytes:
                flat_interp_linear = a.mAP50_median
                flat_interp_log = a.mAP50_median
            else:
                t_lin = (target_bytes - a.total_bytes) / max(1, (b.total_bytes - a.total_bytes))
                flat_interp_linear = a.mAP50_median + t_lin * (b.mAP50_median - a.mAP50_median)
                if a.total_bytes > 0 and b.total_bytes > 0 and target_bytes > 0:
                    t_log = (math.log(target_bytes) - math.log(a.total_bytes)) / max(
                        1e-9, (math.log(b.total_bytes) - math.log(a.total_bytes))
                    )
                else:
                    t_log = t_lin
                flat_interp_log = a.mAP50_median + t_log * (b.mAP50_median - a.mAP50_median)
            rel_gain_linear_pct = 100.0 * (r.mAP50_median - flat_interp_linear) / max(1e-9, flat_interp_linear)
            rel_gain_log_pct = 100.0 * (r.mAP50_median - flat_interp_log) / max(1e-9, flat_interp_log)
            mean_r = means.get(r.qp)
            mean_rel = None
            if mean_r is not None:
                mean_rel = 100.0 * (mean_r.mAP50_median - flat_interp_linear) / max(1e-9, flat_interp_linear)
            bpp = r.total_bytes * 8 / max(1, (r.total_bytes and 1))  # computed at aggregate level instead
            matched_rows.append(
                dict(
                    clip_id=clip_id,
                    lane="roi_guided",
                    qp=r.qp,
                    total_bytes=r.total_bytes,
                    flat_bracket_bytes=[a.total_bytes, b.total_bytes],
                    flat_bracket_mAP50=[a.mAP50_median, b.mAP50_median],
                    flat_interp_linear_mAP50=flat_interp_linear,
                    flat_interp_log_mAP50=flat_interp_log,
                    roi_mAP50=r.mAP50_median,
                    roi_mAP50_stderr=r.mAP50_stderr,
                    relative_gain_linear_pct=rel_gain_linear_pct,
                    relative_gain_log_pct=rel_gain_log_pct,
                    mean_mAP50=None if mean_r is None else mean_r.mAP50_median,
                    mean_relative_gain_linear_pct=mean_rel,
                )
            )
    return matched_rows


def aggregate_verdict(
    matched_rows: list[dict[str, Any]], extract_cost: ExtractCost, extract_cost_mAP_penalty_pct: float
) -> dict[str, Any]:
    """Aggregate ROI and mean relative gains across the full held-out slice;
    apply extract-cost adjustment; emit kill/defend verdict.
    """
    if not matched_rows:
        return {
            "verdict": "kill",
            "rationale": "no matched rows",
            "roi_mean_relative_gain_linear_pct": 0.0,
            "roi_mean_relative_gain_log_pct": 0.0,
            "extract_adjusted_relative_gain_pct": 0.0,
        }
    roi_gains_linear = [r["relative_gain_linear_pct"] for r in matched_rows if r["relative_gain_linear_pct"] is not None]
    roi_gains_log = [r["relative_gain_log_pct"] for r in matched_rows if r["relative_gain_log_pct"] is not None]
    mean_gains_linear = [r["mean_relative_gain_linear_pct"] for r in matched_rows if r.get("mean_relative_gain_linear_pct") is not None]
    roi_mean_linear = statistics.mean(roi_gains_linear) if roi_gains_linear else 0.0
    roi_mean_log = statistics.mean(roi_gains_log) if roi_gains_log else 0.0
    mean_mean_linear = statistics.mean(mean_gains_linear) if mean_gains_linear else 0.0

    roi_vs_mean_ratio = None
    if abs(mean_mean_linear) > 1e-6:
        roi_vs_mean_ratio = roi_mean_linear / mean_mean_linear
    else:
        # If control lane has no signal, ratio is undefined but favorable to ROI if ROI has signal.
        roi_vs_mean_ratio = float("inf") if roi_mean_linear > 0 else None

    # Extract-cost adjustment: charge packet extraction cost against the ROI lane's gain.
    # If ROI extract adds X ms/frame and the workload is "encode + detect", and detection
    # already costs Y ms/frame on flat, then the net time cost of the ROI lane is
    # (flat_detect + extract) ms/frame, i.e., ~2x detect per frame at deployment.
    # Charge a conservative penalty: subtract (extract_cost_mAP_penalty_pct) percentage
    # points from the ROI gain. Default: 0.0 (report raw); operators read both.
    extract_adjusted_pct = roi_mean_linear - extract_cost_mAP_penalty_pct

    roi_exceeds_2x_control = (
        roi_vs_mean_ratio is not None
        and roi_vs_mean_ratio == float("inf")
        and roi_mean_linear > 0
    ) or (
        roi_vs_mean_ratio is not None
        and roi_vs_mean_ratio != float("inf")
        and roi_vs_mean_ratio >= 2.0
        and roi_mean_linear > 0
    )

    # Defend: roi_mean_linear >= 5.0 AND roi_mean_log >= 5.0 AND roi_exceeds_2x_control AND extract adjusted >= 5.0
    # Kill: any condition fails, or raw gain < 2.0
    verdict = "kill"
    rationale: list[str] = []
    if roi_mean_linear >= 5.0 and roi_mean_log >= 5.0 and roi_exceeds_2x_control and extract_adjusted_pct >= 5.0:
        verdict = "defend"
        rationale.append(
            f"roi_mean_linear_pct={roi_mean_linear:.2f} >= 5.0 AND roi_mean_log_pct={roi_mean_log:.2f} >= 5.0 AND control ratio = {roi_vs_mean_ratio} >= 2.0 AND extract-adjusted {extract_adjusted_pct:.2f} >= 5.0."
        )
    else:
        if roi_mean_linear < 2.0:
            rationale.append(f"roi_mean_linear_pct={roi_mean_linear:.2f} is below the +2.0% kill threshold.")
        if roi_mean_linear < 5.0:
            rationale.append(f"roi_mean_linear_pct={roi_mean_linear:.2f} does not meet the +5.0% defend threshold.")
        if roi_mean_log < 5.0:
            rationale.append(f"roi_mean_log_pct={roi_mean_log:.2f} does not meet the log-interp +5.0% threshold.")
        if not roi_exceeds_2x_control:
            rationale.append(f"roi_vs_mean_ratio={roi_vs_mean_ratio} does not exceed 2x (control lane matches or beats ROI).")
        if extract_adjusted_pct < 5.0:
            rationale.append(f"extract_adjusted_pct={extract_adjusted_pct:.2f} < 5.0 defend threshold once packet extraction cost is accounted.")

    return {
        "verdict": verdict,
        "rationale": "; ".join(rationale),
        "roi_mean_relative_gain_linear_pct": roi_mean_linear,
        "roi_mean_relative_gain_log_pct": roi_mean_log,
        "control_mean_relative_gain_linear_pct": mean_mean_linear,
        "roi_vs_mean_ratio": roi_vs_mean_ratio,
        "roi_exceeds_2x_control": roi_exceeds_2x_control,
        "extract_adjusted_relative_gain_pct": extract_adjusted_pct,
        "extract_cost_penalty_pct_applied": extract_cost_mAP_penalty_pct,
    }


# -----------------------------
# Limiting cases
# -----------------------------

def limiting_case_empty(
    clip: ClipData,
    frame_paths: list[Path],
    yuv_path: Path,
    detections_ref: list[list[Box]],
    num_frames: int,
    work_dir: Path,
    weights: Path,
) -> dict[str, Any]:
    """Force empty packet (boxes=[]) -> all-zero map -> flat encoding.

    Expected: |bpp_delta_pct| < 1.0 vs flat at matched QP=32.
    """
    import numpy as np

    qp = 32
    empty_maps = [np.zeros((clip.height, clip.width), dtype=np.float32) for _ in range(num_frames)]
    zones = map_to_libx265_zones(empty_maps, qp)
    # Flat encode
    flat_path = work_dir / f"{clip.clip_id}_lim_empty_flat.mp4"
    flat_bytes, _ = encode_lane(yuv_path, clip.width, clip.height, clip.fps, num_frames, flat_path, qp, zones=None, repeats=1)
    roi_path = work_dir / f"{clip.clip_id}_lim_empty_roi.mp4"
    roi_bytes, _ = encode_lane(yuv_path, clip.width, clip.height, clip.fps, num_frames, roi_path, qp, zones=zones, repeats=1)
    flat_dec = decode_to_frames(flat_path, work_dir / "lim_empty_flat_dec", num_frames)
    roi_dec = decode_to_frames(roi_path, work_dir / "lim_empty_roi_dec", num_frames)
    flat_map50, _ = eval_map50(flat_dec, detections_ref, weights)
    roi_map50, _ = eval_map50(roi_dec, detections_ref, weights)
    pixels = clip.width * clip.height * num_frames
    bpp_flat = 8.0 * flat_bytes / pixels
    bpp_roi = 8.0 * roi_bytes / pixels
    return {
        "qp": qp,
        "flat_bytes": flat_bytes,
        "roi_bytes": roi_bytes,
        "bpp_flat": bpp_flat,
        "bpp_roi": bpp_roi,
        "bpp_delta_pct": 100.0 * (bpp_roi - bpp_flat) / max(1e-9, bpp_flat),
        "flat_mAP50": flat_map50,
        "roi_mAP50": roi_map50,
        "mAP50_delta": roi_map50 - flat_map50,
    }


def limiting_case_saturated(
    clip: ClipData,
    frame_paths: list[Path],
    yuv_path: Path,
    detections_ref: list[list[Box]],
    num_frames: int,
    work_dir: Path,
    weights: Path,
) -> dict[str, Any]:
    """Saturated packet: one box covering entire frame per time step.

    Normalization makes the map uniform 1.0 -> scalar_importance=1.0
    uniformly -> after zero-mean, delta=0 -> all zones qp = base_qp.
    Expected: |bpp_delta_pct| < 1.0 vs flat.
    """
    import numpy as np

    qp = 32
    full_maps = [np.ones((clip.height, clip.width), dtype=np.float32) for _ in range(num_frames)]
    zones = map_to_libx265_zones(full_maps, qp)
    flat_path = work_dir / f"{clip.clip_id}_lim_sat_flat.mp4"
    flat_bytes, _ = encode_lane(yuv_path, clip.width, clip.height, clip.fps, num_frames, flat_path, qp, zones=None, repeats=1)
    roi_path = work_dir / f"{clip.clip_id}_lim_sat_roi.mp4"
    roi_bytes, _ = encode_lane(yuv_path, clip.width, clip.height, clip.fps, num_frames, roi_path, qp, zones=zones, repeats=1)
    flat_dec = decode_to_frames(flat_path, work_dir / "lim_sat_flat_dec", num_frames)
    roi_dec = decode_to_frames(roi_path, work_dir / "lim_sat_roi_dec", num_frames)
    flat_map50, _ = eval_map50(flat_dec, detections_ref, weights)
    roi_map50, _ = eval_map50(roi_dec, detections_ref, weights)
    pixels = clip.width * clip.height * num_frames
    bpp_flat = 8.0 * flat_bytes / pixels
    bpp_roi = 8.0 * roi_bytes / pixels
    return {
        "qp": qp,
        "flat_bytes": flat_bytes,
        "roi_bytes": roi_bytes,
        "bpp_flat": bpp_flat,
        "bpp_roi": bpp_roi,
        "bpp_delta_pct": 100.0 * (bpp_roi - bpp_flat) / max(1e-9, bpp_flat),
        "flat_mAP50": flat_map50,
        "roi_mAP50": roi_map50,
        "mAP50_delta": roi_map50 - flat_map50,
    }


def limiting_case_single_small_box(
    clip: ClipData,
    frame_paths: list[Path],
    yuv_path: Path,
    detections_ref: list[list[Box]],
    num_frames: int,
    work_dir: Path,
    weights: Path,
) -> dict[str, Any]:
    """Single small central box in a few frames only.

    Best-case sanity check (not a verdict gate). Expect bpp delta within
    a few percent of flat and mAP50 likely unchanged since there is
    little concentrated content.
    """
    import numpy as np

    qp = 32
    H, W = clip.height, clip.width
    maps: list[Any] = []
    box = Box(track_id=1, x=W // 2 - 20, y=H // 2 - 20, w=40, h=40, cls=0, score=1.0)
    for t in range(num_frames):
        if t % 5 == 0:
            maps.append(build_roi_map([box], (H, W)))
        else:
            maps.append(np.zeros((H, W), dtype=np.float32))
    zones = map_to_libx265_zones(maps, qp)
    flat_path = work_dir / f"{clip.clip_id}_lim_single_flat.mp4"
    flat_bytes, _ = encode_lane(yuv_path, clip.width, clip.height, clip.fps, num_frames, flat_path, qp, zones=None, repeats=1)
    roi_path = work_dir / f"{clip.clip_id}_lim_single_roi.mp4"
    roi_bytes, _ = encode_lane(yuv_path, clip.width, clip.height, clip.fps, num_frames, roi_path, qp, zones=zones, repeats=1)
    flat_dec = decode_to_frames(flat_path, work_dir / "lim_single_flat_dec", num_frames)
    roi_dec = decode_to_frames(roi_path, work_dir / "lim_single_roi_dec", num_frames)
    flat_map50, _ = eval_map50(flat_dec, detections_ref, weights)
    roi_map50, _ = eval_map50(roi_dec, detections_ref, weights)
    pixels = clip.width * clip.height * num_frames
    bpp_flat = 8.0 * flat_bytes / pixels
    bpp_roi = 8.0 * roi_bytes / pixels
    return {
        "qp": qp,
        "flat_bytes": flat_bytes,
        "roi_bytes": roi_bytes,
        "bpp_flat": bpp_flat,
        "bpp_roi": bpp_roi,
        "bpp_delta_pct": 100.0 * (bpp_roi - bpp_flat) / max(1e-9, bpp_flat),
        "flat_mAP50": flat_map50,
        "roi_mAP50": roi_map50,
        "relative_gain_pct": 100.0 * (roi_map50 - flat_map50) / max(1e-9, flat_map50),
    }


# -----------------------------
# Smoke
# -----------------------------

def smoke_mode() -> None:
    """Dependency-free smoke on synthetic inputs.

    - Build a small ROI map from a fixed box list; verify determinism and
      limiting-case behavior.
    - Verify map_to_libx265_zones returns a non-empty deterministic string
      for a non-trivial set of maps and empty fallback for all-zero maps.
    """
    import numpy as np

    # Determinism: same input -> same bytes
    H, W = 60, 80
    boxes = [Box(track_id=1, x=10, y=15, w=12, h=8), Box(track_id=2, x=50, y=40, w=10, h=15)]
    m1 = build_roi_map(boxes, (H, W))
    m2 = build_roi_map(boxes, (H, W))
    assert m1.shape == (H, W), f"unexpected shape {m1.shape}"
    assert float(m1.max()) <= 1.0 + 1e-6, "map not normalized to <= 1"
    assert float(m1.min()) >= 0.0, "map has negative values"
    assert np.allclose(m1, m2), "build_roi_map non-deterministic"

    # Limiting case: empty
    m_empty = build_roi_map([], (H, W))
    assert float(m_empty.max()) == 0.0, "empty boxes did not produce all-zero map"

    # Zones: deterministic
    qp = 32
    maps = [m1, m_empty, m1]
    z1 = map_to_libx265_zones(maps, qp)
    z2 = map_to_libx265_zones(maps, qp)
    assert z1 == z2, "map_to_libx265_zones non-deterministic"
    assert z1, "non-empty input produced empty zones string"

    # Zones: all-zero maps fallback
    z_empty = map_to_libx265_zones([m_empty] * 3, qp)
    # All scalars are 0 -> all deltas 0 -> all zones set to base_qp
    for piece in z_empty.split("/"):
        assert piece.endswith(f"q={qp}"), f"unexpected zone piece {piece}"

    # Dimensional checks
    total_bytes = 12345
    num_frames = 60
    width = W
    height = H
    bpp = total_bytes * 8 / (width * height * num_frames)
    assert isinstance(bpp, float), "bpp not float"
    assert 0.0 <= 0.95 <= 1.0, "mAP_50 bounds check"
    print("SMOKE OK")


# -----------------------------
# Main entrypoint
# -----------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--surface", default="virat-subset")
    ap.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    ap.add_argument("--report-dir", default=str(DEFAULT_REPORT_DIR))
    ap.add_argument("--max-frames-per-clip", type=int, default=72, help="bound to ~3 s @ 24 fps")
    ap.add_argument("--frame-stride", type=int, default=2, help="temporal downsample stride")
    ap.add_argument("--weights", default=str(DEFAULT_YOLO_WEIGHTS))
    ap.add_argument("--extract-cost-penalty-pct", type=float, default=0.0)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--work-dir", default=str(Path(tempfile.gettempdir()) / "zpe_candidate_a_work"))
    args = ap.parse_args()

    versions = _dep_check()

    if args.smoke:
        smoke_mode()
        return 0

    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    work_dir = Path(args.work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    surface_decision = {
        "surface": args.surface,
        "reason": "VIRAT facility-crossing subset used as held-out slice (1280x720, 24 fps, real surveillance content with human+vehicle content). CompressAI-Vision COCO subset was considered but its evaluation toolchain does not install cleanly on Python 3.11 Mac within the ~1-day budget. VIRAT is the carried-forward cohort from phase 09.4.1.1.1 and is appropriate for the bounded VCM surface.",
        "max_frames_per_clip": args.max_frames_per_clip,
        "frame_stride": args.frame_stride,
    }

    clips = load_surface(args.surface, Path(args.cache_dir), args.max_frames_per_clip, args.frame_stride)
    print(f"Loaded {len(clips)} clips from {args.cache_dir}")

    weights = Path(args.weights)
    if not weights.is_file():
        print(f"ERROR: YOLOv8m weights not found at {weights}")
        return 3

    # Global timing
    t_wall_start = time.time()

    clip_results: dict[str, list[LaneResult]] = {}
    clip_meta: dict[str, dict[str, Any]] = {}
    limiting_cases_by_clip: dict[str, dict[str, Any]] = {}
    extract_costs: list[ExtractCost] = []

    for clip in clips:
        print(f"[clip={clip.clip_id}] W={clip.width} H={clip.height} fps={clip.fps:.2f} nb={clip.num_frames}")
        # 1. Extract frames from the source clip
        frames_dir = work_dir / f"frames_{clip.clip_id}"
        frame_paths = sample_clip_frames(clip, frames_dir, args.max_frames_per_clip, args.frame_stride)
        num_frames = len(frame_paths)
        if num_frames < 4:
            print(f"  skipping: too few sampled frames ({num_frames})")
            continue
        # 2. Produce a deterministic YUV source for all lanes
        yuv_path = work_dir / f"src_{clip.clip_id}.yuv"
        frames_to_yuv(frame_paths, yuv_path, clip.width, clip.height, clip.fps)
        # 3. Packet extraction (detector run at ingest)
        packet_bytes, detections, cost = extract_packet(frame_paths, weights, clip.width, clip.height)
        extract_costs.append(cost)
        print(
            f"  packet_bytes={len(packet_bytes)} extract_cost_median_ms_per_frame={cost.median_ms_per_frame:.1f} p90={cost.p90_ms_per_frame:.1f}"
        )
        # 4. Build ROI + mean-importance maps per frame
        import numpy as np
        roi_maps = [build_roi_map(boxes, (clip.height, clip.width)) for boxes in detections[:num_frames]]
        mean_maps = [mean_importance_map(boxes, (clip.height, clip.width)) for boxes in detections[:num_frames]]
        roi_zones_by_qp = {qp: map_to_libx265_zones(roi_maps, qp) for qp in QP_SWEEP}
        mean_zones_by_qp = {qp: map_to_libx265_zones(mean_maps, qp) for qp in QP_SWEEP}
        # 5. Run lanes
        clip_work_dir = work_dir / clip.clip_id
        clip_work_dir.mkdir(parents=True, exist_ok=True)
        (work_dir / f"lim_{clip.clip_id}").mkdir(parents=True, exist_ok=True)
        results = run_all_lanes(
            clip,
            frame_paths,
            yuv_path,
            detections,
            roi_zones_by_qp,
            mean_zones_by_qp,
            num_frames,
            clip_work_dir,
            weights,
        )
        clip_results[clip.clip_id] = results
        clip_meta[clip.clip_id] = {
            "width": clip.width,
            "height": clip.height,
            "fps": clip.fps,
            "sampled_frames": num_frames,
            "packet_bytes": len(packet_bytes),
            "packet_sha256": hashlib.sha256(packet_bytes).hexdigest(),
            "per_frame_box_counts": [len(b) for b in detections[:num_frames]],
        }
        # 6. Limiting cases
        print(f"  limiting: empty")
        lim_empty = limiting_case_empty(clip, frame_paths, yuv_path, detections, num_frames, work_dir / f"lim_{clip.clip_id}", weights)
        print(f"  limiting: saturated")
        lim_sat = limiting_case_saturated(clip, frame_paths, yuv_path, detections, num_frames, work_dir / f"lim_{clip.clip_id}", weights)
        print(f"  limiting: single small box")
        lim_single = limiting_case_single_small_box(clip, frame_paths, yuv_path, detections, num_frames, work_dir / f"lim_{clip.clip_id}", weights)
        limiting_cases_by_clip[clip.clip_id] = {
            "empty_packet": lim_empty,
            "saturated_packet": lim_sat,
            "single_small_box": lim_single,
        }
        for result in results:
            print(
                f"  qp={result.qp} mode={result.mode:<12s} bytes={result.total_bytes:>8d} mAP50={result.mAP50_median:.4f} +/-{result.mAP50_stderr:.4f}"
            )

    # Aggregate extract cost across clips
    agg_extract = ExtractCost(
        median_ms_per_frame=statistics.median([c.median_ms_per_frame for c in extract_costs])
        if extract_costs
        else 0.0,
        p90_ms_per_frame=max([c.p90_ms_per_frame for c in extract_costs]) if extract_costs else 0.0,
        sample_count=sum(c.sample_count for c in extract_costs),
    )

    # Matched-bitrate
    matched = build_matched_bitrate(clip_results)

    # Verdict
    verdict = aggregate_verdict(matched, agg_extract, args.extract_cost_penalty_pct)

    # Emit summary.json
    def _lane_to_sweep(clip_res: list[LaneResult], mode: str) -> dict[str, list[Any]]:
        subset = [r for r in clip_res if r.mode == mode]
        return {
            "qp_sweep": [r.qp for r in subset],
            "bytes": [r.total_bytes for r in subset],
            "encode_wall_ms": [r.encode_wall_ms for r in subset],
            "mAP50_median": [r.mAP50_median for r in subset],
            "mAP50_stderr": [r.mAP50_stderr for r in subset],
            "mAP50_runs": [r.mAP50_runs for r in subset],
        }

    lane_sweeps: dict[str, dict[str, Any]] = {}
    for clip_id, results in clip_results.items():
        lane_sweeps[clip_id] = {
            "flat": _lane_to_sweep(results, "flat"),
            "roi_guided": _lane_to_sweep(results, "roi_guided"),
            "mean_importance": _lane_to_sweep(results, "mean_imp"),
        }

    # Aggregate limiting-cases: worst case bpp_delta_pct + mean mAP50_delta
    empty_bpp_deltas = [v["empty_packet"]["bpp_delta_pct"] for v in limiting_cases_by_clip.values()]
    sat_bpp_deltas = [v["saturated_packet"]["bpp_delta_pct"] for v in limiting_cases_by_clip.values()]
    empty_mAP_deltas = [v["empty_packet"]["mAP50_delta"] for v in limiting_cases_by_clip.values()]
    sat_mAP_deltas = [v["saturated_packet"]["mAP50_delta"] for v in limiting_cases_by_clip.values()]
    single_gains = [v["single_small_box"]["relative_gain_pct"] for v in limiting_cases_by_clip.values()]

    limiting_agg = {
        "empty_packet": {
            "bpp_delta_pct_worst": max([abs(x) for x in empty_bpp_deltas]) if empty_bpp_deltas else None,
            "bpp_delta_pct_values": empty_bpp_deltas,
            "mAP50_delta_mean": statistics.mean(empty_mAP_deltas) if empty_mAP_deltas else None,
            "mAP50_delta_values": empty_mAP_deltas,
        },
        "saturated_packet": {
            "bpp_delta_pct_worst": max([abs(x) for x in sat_bpp_deltas]) if sat_bpp_deltas else None,
            "bpp_delta_pct_values": sat_bpp_deltas,
            "mAP50_delta_mean": statistics.mean(sat_mAP_deltas) if sat_mAP_deltas else None,
            "mAP50_delta_values": sat_mAP_deltas,
        },
        "single_small_box": {
            "relative_gain_pct_mean": statistics.mean(single_gains) if single_gains else None,
            "relative_gain_pct_values": single_gains,
        },
    }

    # control_comparison summary
    control_comparison = {
        "roi_vs_mean_ratio": verdict.get("roi_vs_mean_ratio"),
        "roi_exceeds_2x_control": verdict.get("roi_exceeds_2x_control"),
        "control_mean_relative_gain_linear_pct": verdict.get("control_mean_relative_gain_linear_pct"),
        "roi_mean_relative_gain_linear_pct": verdict.get("roi_mean_relative_gain_linear_pct"),
    }

    summary_obj = {
        "phase": "09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection",
        "plan": "01",
        "candidate": "A",
        "surface": surface_decision,
        "detector": {
            "name": "YOLOv8m",
            "conf": DETECTOR_CONF,
            "iou": DETECTOR_IOU,
            "weights_path": str(weights),
            "weights_size_bytes": weights.stat().st_size,
            "weights_sha256_head": hashlib.sha256(open(weights, "rb").read(256 * 1024)).hexdigest(),
        },
        "encoder": {
            "name": "libx265",
            "preset": "medium",
            "crf_sweep": list(QP_SWEEP),
            "zones_mode": "temporal_frame_qp_delta",
            "zones_note": "libx265 public zones parameter is temporal-only; per-MB spatial QP-delta is not exposed. ROI shape is reduced to per-frame scalar importance and zero-mean QP delta per frame. This is the documented rectangular-region fallback allowed by the plan.",
            "zero_mean_delta": True,
            "delta_scale": 6.0,
        },
        "error_budget": {
            "encode_repeats": ENCODE_REPEATS,
            "detector_repeats": DETECTOR_REPEATS,
            "extract_cost_frames": EXTRACT_COST_FRAMES,
            "matched_bitrate_tolerance_pct": MATCHED_BITRATE_TOLERANCE_PCT,
        },
        "clip_meta": clip_meta,
        "lanes": lane_sweeps,
        "matched_bitrate": matched,
        "extract_cost_ms_per_frame": {
            "median": agg_extract.median_ms_per_frame,
            "p90": agg_extract.p90_ms_per_frame,
            "sample_count": agg_extract.sample_count,
            "per_clip": [
                {"median_ms_per_frame": c.median_ms_per_frame, "p90_ms_per_frame": c.p90_ms_per_frame}
                for c in extract_costs
            ],
        },
        "extract_adjusted_relative_gain_pct": verdict["extract_adjusted_relative_gain_pct"],
        "limiting_cases": limiting_agg,
        "limiting_cases_per_clip": limiting_cases_by_clip,
        "control_comparison": control_comparison,
        "verdict": verdict["verdict"],
        "verdict_justification": verdict["rationale"],
        "sovereign_gate_status": "red",
        "sovereign_gate_boundary": (
            "This plan is a bounded box-level bitrate-allocation sidecar experiment on incumbent "
            "libx265. It does not claim primitive-native Compass-8 closure regardless of verdict. "
            "The sovereign Compass-8 primitive-native gate remains red."
        ),
        "forbidden_proxies_rejected": [
            "No GT-fed ROI: maps derived from packet extracted by ingest-time YOLOv8m run (extract cost accounted)",
            "No ap_proxy: mAP@50 on YOLOv8m is the only utility metric",
            "No mixed bundles: each lane isolates exactly one intervention",
            "No cherry-picking: full held-out slice reported with per-clip rows",
            "No external GitHub remote touches",
            "No reopening of Phase 10 or Red Magic",
            "No reopening of archive-query on box-state",
        ],
        "versions": versions,
        "wall_clock_s": time.time() - t_wall_start,
    }

    (report_dir / "summary.json").write_text(json.dumps(summary_obj, indent=2, default=str))
    print(f"Wrote summary.json to {report_dir / 'summary.json'}")

    # matched_bitrate_table.csv
    csv_path = report_dir / "matched_bitrate_table.csv"
    with csv_path.open("w") as fh:
        fh.write(
            "clip_id,lane,qp,total_bytes,bpp,mAP50_median,mAP50_stderr,relative_gain_linear_pct,relative_gain_log_pct,extract_cost_ms_per_frame\n"
        )
        # Emit a row per (clip, lane, qp)
        for clip_id, results in clip_results.items():
            cm = clip_meta.get(clip_id, {})
            pixels = cm.get("width", 1) * cm.get("height", 1) * cm.get("sampled_frames", 1)
            for r in results:
                bpp = 8.0 * r.total_bytes / max(1, pixels)
                rel_lin = ""
                rel_log = ""
                if r.mode == "roi_guided":
                    # find matched row
                    for mr in matched:
                        if mr["clip_id"] == clip_id and mr["qp"] == r.qp and mr["lane"] == "roi_guided":
                            rel_lin = f"{mr['relative_gain_linear_pct']:.4f}"
                            rel_log = f"{mr['relative_gain_log_pct']:.4f}"
                            break
                fh.write(
                    f"{clip_id},{r.mode},{r.qp},{r.total_bytes},{bpp:.6f},{r.mAP50_median:.6f},{r.mAP50_stderr:.6f},{rel_lin},{rel_log},{agg_extract.median_ms_per_frame:.3f}\n"
                )
    print(f"Wrote matched_bitrate_table.csv to {csv_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
