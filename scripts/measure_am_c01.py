#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from PIL import Image


def _now_utc() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _run(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=str(cwd), text=True, capture_output=True, check=False)


@dataclass
class LoadedFrame:
    name: str
    image_path: Path
    rgb: np.ndarray
    gray_bytes: bytes
    gt_boxes: list[object]


def _resolve_datasets_root(repo_root: Path) -> Path:
    import os

    override_text = os.environ.get("ZPE_VIDEO_DATASETS_ROOT")
    if override_text:
        override = Path(override_text).expanduser()
        if override.exists():
            return override
    candidates = [
        repo_root / "datasets",
        repo_root.parent / "datasets",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "No datasets root found. Checked repo and workspace dataset directories."
    )


def _load_modules(repo_root: Path) -> tuple[object, ...]:
    sys.path.insert(0, str(repo_root / "src"))
    from zpe_video.codec import decode_sequence, encode_sequence
    from zpe_video.detector import VISDRONE_TO_EVAL_LABEL, TorchvisionCocoDetector
    from zpe_video.metrics import iou
    from zpe_video.models import Box, SequenceData
    from zpe_video.vision import reconstruct_frame

    return (
        Box,
        SequenceData,
        TorchvisionCocoDetector,
        VISDRONE_TO_EVAL_LABEL,
        encode_sequence,
        decode_sequence,
        reconstruct_frame,
        iou,
    )


def _scale_box(box: object, *, scale_x: float, scale_y: float, Box: object) -> object:
    scaled_width = max(1, int(round(box.w * scale_x)))
    scaled_height = max(1, int(round(box.h * scale_y)))
    scaled_x = max(0, int(round(box.x * scale_x)))
    scaled_y = max(0, int(round(box.y * scale_y)))
    return Box(
        box_id=box.box_id,
        x=scaled_x,
        y=scaled_y,
        w=scaled_width,
        h=scaled_height,
        label=box.label,
        confidence=box.confidence,
    )


def _load_visdrone_subset(
    datasets_root: Path,
    *,
    frame_count: int,
    Box: object,
    visdrone_mapping: dict[int, int],
) -> tuple[list[LoadedFrame], int, int]:
    dataset_root = datasets_root / "VisDrone2023" / "VisDrone2019-DET-val"
    images_dir = dataset_root / "images"
    annotations_dir = dataset_root / "annotations"
    if not images_dir.exists() or not annotations_dir.exists():
        raise FileNotFoundError(f"VisDrone dataset missing at {dataset_root}")

    target_width = 0
    target_height = 0
    loaded: list[LoadedFrame] = []
    for image_path in sorted(images_dir.glob("*.jpg")):
        ann_path = annotations_dir / f"{image_path.stem}.txt"
        if not ann_path.exists():
            continue
        image = Image.open(image_path).convert("RGB")
        width, height = image.size
        boxes: list[object] = []
        for line_idx, line in enumerate(
            ann_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        ):
            parts = [part.strip() for part in line.split(",")]
            if len(parts) < 8:
                continue
            try:
                x = int(float(parts[0]))
                y = int(float(parts[1]))
                box_width = int(float(parts[2]))
                box_height = int(float(parts[3]))
                visdrone_category = int(float(parts[5]))
            except ValueError:
                continue
            eval_label = visdrone_mapping.get(visdrone_category)
            if eval_label is None or box_width <= 0 or box_height <= 0:
                continue
            boxes.append(
                Box(
                    box_id=line_idx,
                    x=x,
                    y=y,
                    w=box_width,
                    h=box_height,
                    label=eval_label,
                    confidence=1.0,
                )
            )
        if not boxes:
            continue

        if target_width == 0 or target_height == 0:
            target_width = width
            target_height = height
        elif width != target_width or height != target_height:
            scale_x = target_width / float(width)
            scale_y = target_height / float(height)
            image = image.resize((target_width, target_height), Image.BILINEAR)
            boxes = [_scale_box(box, scale_x=scale_x, scale_y=scale_y, Box=Box) for box in boxes]

        gray = image.convert("L")
        loaded.append(
            LoadedFrame(
                name=image_path.name,
                image_path=image_path,
                rgb=np.asarray(image, dtype=np.uint8),
                gray_bytes=gray.tobytes(),
                gt_boxes=boxes,
            )
        )
        if len(loaded) >= frame_count:
            break

    if len(loaded) < frame_count:
        raise RuntimeError(f"Needed {frame_count} VisDrone frames, found {len(loaded)}")
    return loaded, target_width, target_height


def _predict_many(detector: object, frames: list[np.ndarray]) -> list[list[object]]:
    return [detector.predict(frame) for frame in frames]


def _assign_track_ids(
    predictions: list[list[object]], *, Box: object, iou: object, match_threshold: float = 0.3
) -> list[list[object]]:
    tracked: list[list[object]] = []
    previous: list[object] = []
    next_box_id = 0
    for frame_predictions in predictions:
        current: list[object] = []
        unused_previous = set(range(len(previous)))
        ordered_predictions = sorted(
            frame_predictions, key=lambda box: (-float(box.confidence), box.label, box.x, box.y)
        )
        for box in ordered_predictions:
            best_prev_idx = -1
            best_score = 0.0
            for prev_idx, prev_box in enumerate(previous):
                if prev_idx not in unused_previous or prev_box.label != box.label:
                    continue
                score = float(iou(prev_box, box))
                if score > best_score:
                    best_score = score
                    best_prev_idx = prev_idx
            if best_prev_idx >= 0 and best_score >= match_threshold:
                box_id = previous[best_prev_idx].box_id
                unused_previous.remove(best_prev_idx)
            else:
                box_id = next_box_id
                next_box_id += 1
            current.append(
                Box(
                    box_id=box_id,
                    x=box.x,
                    y=box.y,
                    w=box.w,
                    h=box.h,
                    label=box.label,
                    confidence=box.confidence,
                )
            )
        current.sort(key=lambda item: item.box_id)
        tracked.append(current)
        previous = current
    return tracked


def _compute_average_precision(tp: np.ndarray, fp: np.ndarray, total_gt: int) -> float:
    if total_gt <= 0 or tp.size == 0:
        return 0.0
    tp_cumulative = np.cumsum(tp)
    fp_cumulative = np.cumsum(fp)
    recalls = tp_cumulative / float(total_gt)
    precisions = tp_cumulative / np.maximum(tp_cumulative + fp_cumulative, 1.0)
    recall_points = np.linspace(0.0, 1.0, 101)
    precision_envelope: list[float] = []
    for recall_threshold in recall_points:
        eligible = precisions[recalls >= recall_threshold]
        precision_envelope.append(float(np.max(eligible)) if eligible.size else 0.0)
    return float(np.mean(np.asarray(precision_envelope, dtype=np.float64)))


def _compute_map50(
    gt_frames: list[list[object]], pred_frames: list[list[object]], *, iou: object
) -> tuple[float, dict[str, float]]:
    class_labels = sorted({box.label for frame in gt_frames for box in frame})
    per_class_ap: dict[str, float] = {}
    for label in class_labels:
        gt_by_frame: list[list[object]] = []
        total_gt = 0
        for frame_boxes in gt_frames:
            class_boxes = [box for box in frame_boxes if box.label == label]
            gt_by_frame.append(class_boxes)
            total_gt += len(class_boxes)

        predictions: list[tuple[int, float, object]] = []
        for frame_idx, frame_boxes in enumerate(pred_frames):
            for box in frame_boxes:
                if box.label == label:
                    predictions.append((frame_idx, float(box.confidence), box))
        predictions.sort(key=lambda item: item[1], reverse=True)

        matched = {
            frame_idx: [False] * len(frame_boxes)
            for frame_idx, frame_boxes in enumerate(gt_by_frame)
        }
        tp: list[float] = []
        fp: list[float] = []
        for frame_idx, _, prediction in predictions:
            best_iou = 0.0
            best_gt_idx = -1
            for gt_idx, gt_box in enumerate(gt_by_frame[frame_idx]):
                if matched[frame_idx][gt_idx]:
                    continue
                score = float(iou(prediction, gt_box))
                if score > best_iou:
                    best_iou = score
                    best_gt_idx = gt_idx
            if best_gt_idx >= 0 and best_iou >= 0.5:
                matched[frame_idx][best_gt_idx] = True
                tp.append(1.0)
                fp.append(0.0)
            else:
                tp.append(0.0)
                fp.append(1.0)
        per_class_ap[str(label)] = _compute_average_precision(
            np.asarray(tp, dtype=np.float64),
            np.asarray(fp, dtype=np.float64),
            total_gt=total_gt,
        )

    if not per_class_ap:
        return 0.0, {}
    return float(sum(per_class_ap.values()) / len(per_class_ap)), per_class_ap


def _write_rgb_frames(frame_dir: Path, frames: list[np.ndarray]) -> None:
    frame_dir.mkdir(parents=True, exist_ok=True)
    for stale in frame_dir.glob("*"):
        stale.unlink()
    for index, frame in enumerate(frames):
        Image.fromarray(frame).save(frame_dir / f"frame_{index:04d}.png")


def _load_png_frames(frame_dir: Path) -> list[np.ndarray]:
    frames: list[np.ndarray] = []
    for frame_path in sorted(frame_dir.glob("frame_*.png")):
        frames.append(np.asarray(Image.open(frame_path).convert("RGB"), dtype=np.uint8))
    if not frames:
        raise RuntimeError(f"No PNG frames found in {frame_dir}")
    return frames


def _encode_h265(
    repo_root: Path, artifact_root: Path, rgb_frames: list[np.ndarray], *, frame_rate: int
) -> tuple[list[np.ndarray], int, Path]:
    tmp_root = artifact_root / "tmp" / "h265"
    input_dir = tmp_root / "in_frames"
    output_dir = tmp_root / "out_frames"
    video_path = tmp_root / "baseline_h265.mp4"
    if tmp_root.exists():
        shutil.rmtree(tmp_root)
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_rgb_frames(input_dir, rgb_frames)

    encode_result = _run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-framerate",
            str(frame_rate),
            "-i",
            str(input_dir / "frame_%04d.png"),
            "-c:v",
            "libx265",
            "-x265-params",
            f"qp=22:keyint={frame_rate}:min-keyint={frame_rate}:scenecut=0",
            "-pix_fmt",
            "yuv420p",
            str(video_path),
        ],
        cwd=repo_root,
    )
    if encode_result.returncode != 0:
        raise RuntimeError(
            encode_result.stderr.strip() or encode_result.stdout.strip() or "H265_ENCODE_FAILED"
        )

    decode_result = _run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(video_path),
            str(output_dir / "frame_%04d.png"),
        ],
        cwd=repo_root,
    )
    if decode_result.returncode != 0:
        raise RuntimeError(
            decode_result.stderr.strip() or decode_result.stdout.strip() or "H265_DECODE_FAILED"
        )

    return _load_png_frames(output_dir), int(video_path.stat().st_size), video_path


def _neutral_background(width: int, height: int, *, value: int = 128) -> bytes:
    return bytes([value]) * (width * height)


def _run_zpe_path(
    artifact_root: Path,
    *,
    width: int,
    height: int,
    frame_rate: int,
    gray_frames: list[bytes],
    source_boxes: list[list[object]],
    SequenceData: object,
    encode_sequence: object,
    decode_sequence: object,
    reconstruct_frame: object,
) -> tuple[list[np.ndarray], int, Path]:
    samples_root = artifact_root / "samples"
    samples_root.mkdir(parents=True, exist_ok=True)
    neutral_background = _neutral_background(width, height)
    sequence = SequenceData(
        name="visdrone2019_det_val_h0",
        dataset_tag="VISDRONE2019_DET_VAL_REAL_H0",
        width=width,
        height=height,
        fps=frame_rate,
        background=neutral_background,
        frames=gray_frames,
        gt_boxes=[],
        notes={
            "codec_input_source": "torchvision_coco_detector_predictions_with_iou_tracking",
            "background_policy": "neutral_gray_128",
        },
    )

    stream_path = samples_root / "visdrone2019_det_val_h0.zpvid"
    encoded = encode_sequence(
        sequence,
        str(stream_path),
        seed=20260313,
        use_gt_boxes=False,
        source_boxes=source_boxes,
    )
    decoded = decode_sequence(str(stream_path), tolerate_corruption=True)
    if decoded.errors:
        raise RuntimeError(f"ZPE decode errors: {decoded.errors}")
    reconstructed_rgb: list[np.ndarray] = []
    for decoded_boxes in decoded.decoded_boxes:
        reconstructed = reconstruct_frame(neutral_background, width, height, decoded_boxes)
        gray = np.frombuffer(reconstructed, dtype=np.uint8).reshape(height, width)
        reconstructed_rgb.append(np.repeat(gray[:, :, None], 3, axis=2))
    if len(reconstructed_rgb) != len(gray_frames):
        raise RuntimeError("ZPE decoded frame count mismatch")
    return reconstructed_rgb, int(encoded.stream_bytes), stream_path


def _frame_manifest(frames: list[LoadedFrame]) -> list[dict[str, object]]:
    manifest: list[dict[str, object]] = []
    for frame in frames:
        manifest.append(
            {
                "name": frame.name,
                "image_path": str(frame.image_path),
                "image_sha256": _sha256_file(frame.image_path),
                "gray_sha256": _sha256_bytes(frame.gray_bytes),
                "gt_box_count": len(frame.gt_boxes),
            }
        )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run parity-clean AM-C01 H0 measurement on Mac CPU."
    )
    parser.add_argument(
        "--frame-count", type=int, default=20, help="Number of VisDrone frames to evaluate."
    )
    parser.add_argument(
        "--artifact-dir",
        default="artifacts/2026-03-13_am_c01_h0",
        help="Artifact directory relative to repo root.",
    )
    parser.add_argument(
        "--score-threshold", type=float, default=0.05, help="Detector score threshold."
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    artifact_root = (repo_root / args.artifact_dir).resolve()
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
    ) = _load_modules(repo_root)

    datasets_root = _resolve_datasets_root(repo_root)
    frames, width, height = _load_visdrone_subset(
        datasets_root,
        frame_count=args.frame_count,
        Box=Box,
        visdrone_mapping=visdrone_mapping,
    )
    rgb_frames = [frame.rgb for frame in frames]
    gray_frames = [frame.gray_bytes for frame in frames]
    gt_frames = [frame.gt_boxes for frame in frames]

    detector = TorchvisionCocoDetector(score_threshold=args.score_threshold)
    baseline_predictions = _predict_many(detector, rgb_frames)
    source_boxes = _assign_track_ids(baseline_predictions, Box=Box, iou=iou)

    baseline_map50, baseline_per_class = _compute_map50(gt_frames, baseline_predictions, iou=iou)
    h265_frames, h265_bitrate_bytes, h265_path = _encode_h265(
        repo_root, artifact_root, rgb_frames, frame_rate=24
    )
    h265_predictions = _predict_many(detector, h265_frames[: len(gt_frames)])
    h265_map50, h265_per_class = _compute_map50(gt_frames, h265_predictions, iou=iou)

    zpe_frames, zpe_bitrate_bytes, zpe_stream_path = _run_zpe_path(
        artifact_root,
        width=width,
        height=height,
        frame_rate=24,
        gray_frames=gray_frames,
        source_boxes=source_boxes,
        SequenceData=SequenceData,
        encode_sequence=encode_sequence,
        decode_sequence=decode_sequence,
        reconstruct_frame=reconstruct_frame,
    )
    zpe_predictions = _predict_many(detector, zpe_frames)
    zpe_map50, zpe_per_class = _compute_map50(gt_frames, zpe_predictions, iou=iou)

    detection_retention = (zpe_map50 / baseline_map50) if baseline_map50 > 0 else 0.0
    bitrate_ratio = (
        (zpe_bitrate_bytes / float(h265_bitrate_bytes)) if h265_bitrate_bytes > 0 else float("inf")
    )
    passed = detection_retention >= 0.95 and bitrate_ratio <= 0.02

    script_path = Path(__file__).resolve()
    model_path = detector.checkpoint_path
    measurement = {
        "authority_metric_id": "AM-C01",
        "measurement_type": "parity_clean_h0",
        "measured_utc": _now_utc(),
        "dataset": "VisDrone2019-DET-val",
        "frame_count": len(frames),
        "frame_names": [frame.name for frame in frames],
        "detector_model": detector.model_id,
        "detector_score_threshold": float(args.score_threshold),
        "detector_model_sha256": _sha256_file(model_path)
        if model_path and model_path.exists()
        else None,
        "metric_name": "mAP@50",
        "baseline_metric": float(baseline_map50),
        "baseline_per_class_ap50": baseline_per_class,
        "h265_metric": float(h265_map50),
        "h265_per_class_ap50": h265_per_class,
        "zpe_metric": float(zpe_map50),
        "zpe_per_class_ap50": zpe_per_class,
        "h265_bitrate_bytes": int(h265_bitrate_bytes),
        "zpe_bitrate_bytes": int(zpe_bitrate_bytes),
        "detection_retention": float(detection_retention),
        "bitrate_ratio": float(bitrate_ratio),
        "pass": bool(passed),
        "codec_input_source": "torchvision_coco_detector_predictions_with_iou_tracking",
        "background_policy": "neutral_gray_128",
        "script_sha256": _sha256_file(script_path),
        "notes": (
            "Single frozen CPU detector across baseline, H.265, and ZPE. "
            "ZPE codec input uses detector-produced boxes with IoU tracking, not GT and not foreground subtraction."
        ),
    }

    command_text = " ".join(shlex.quote(arg) for arg in [sys.executable, *sys.argv])
    custody_manifest = {
        "measured_utc": measurement["measured_utc"],
        "command": command_text,
        "repo_root": str(repo_root),
        "artifact_root": str(artifact_root),
        "datasets_root": str(datasets_root),
        "script_path": str(script_path),
        "script_sha256": measurement["script_sha256"],
        "detector_model": measurement["detector_model"],
        "detector_score_threshold": measurement["detector_score_threshold"],
        "detector_checkpoint_path": str(model_path) if model_path else None,
        "detector_checkpoint_sha256": measurement["detector_model_sha256"],
        "frame_manifest": _frame_manifest(frames),
        "output_hashes": {
            "h265_video_path": str(h265_path),
            "h265_video_sha256": _sha256_file(h265_path),
            "zpe_stream_path": str(zpe_stream_path),
            "zpe_stream_sha256": _sha256_file(zpe_stream_path),
        },
        "measurement_summary": {
            "baseline_metric": measurement["baseline_metric"],
            "h265_metric": measurement["h265_metric"],
            "zpe_metric": measurement["zpe_metric"],
            "detection_retention": measurement["detection_retention"],
            "bitrate_ratio": measurement["bitrate_ratio"],
            "pass": measurement["pass"],
        },
    }

    measurement_path = artifact_root / "am_c01_measurement.json"
    custody_path = artifact_root / "am_c01_custody_manifest.json"
    measurement_path.write_text(
        json.dumps(measurement, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    custody_path.write_text(
        json.dumps(custody_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(measurement, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
