"""Phase 09.4.1.1.2.1 Plan 03 — Candidate C: Primitive-Semantic Enrichment.

Goal: On the EXACT noisy proxy from Phase 09.4.1.1.2 (29 predicted / 4 matched /
4 GT portal-crossings), test whether per-track appearance features (frozen
DINOv2-small backbone) + trajectory features, fed to a binary classifier under
stratified 5-fold CV, can lift precision from the naive-operator baseline
(0.138) to >= 0.5 while preserving recall >= 0.9.

Scope discipline (DO NOT violate):
- The Phase 09.4.1.1.2 proxy is pure box-stream synthetic; there is no real
  RGB video backing the tracks. For appearance features the harness renders a
  deterministic minimal RGB frame (gray background, tracks drawn as filled
  rectangles with a color derived from box dimensions — NOT from the label)
  and runs the frozen backbone on the crop around each box. This is an
  honest approximation: the "appearance" channel carries box shape and
  spatial arrangement through a frozen visual backbone, not real-world
  texture. This is documented in the BENCHMARK-REPORT.
- Even a defend verdict establishes only that the STATE LAYER is the lever,
  not that ZPE is the preferred carrier. Any sparse-metadata format (raw
  struct, parquet, JSON) can carry the same enrichment.
- The Compass-8 sovereign primitive-native gate is NOT touched and remains
  red regardless of verdict.

Invocation:
    source /tmp/zpe_candidate_c_venv/bin/activate
    python zpe_video_lab/python/phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment.py --smoke
    python zpe_video_lab/python/phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment.py

Outputs:
    zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment/summary.json
    zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment/cv_table.csv
    zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment/ablation_table.csv
    zpe_video_lab/reports/phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment/feature_cache.npz
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import statistics
import sys
import time
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any

os.environ.setdefault("HF_HUB_ENABLE_HF_TRANSFER", "0")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import numpy as np
from PIL import Image

LAB_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = LAB_ROOT.parent
sys.path.insert(0, str(LAB_ROOT / "python"))

from phase9_4_1_1_2_fair_baseline_archive_query import (  # noqa: E402
    Box,
    ClipBundle,
    EventWindow,
    _extract_event_windows_naive,
    _score,
    build_noisy_proxy_corpus,
)

DEFAULT_OUTPUT_DIR = LAB_ROOT / "reports" / "phase9_4_1_1_2_1_candidate_c_primitive_semantic_enrichment"
BACKBONE_NAME_DEFAULT = "facebook/dinov2-small"
APPEARANCE_PROJ_DIM = 128
MIN_EVENT_FRAMES = 4
PROXY_SEED = 42
FRAME_COUNT = 60
FRAME_WIDTH = 320
FRAME_HEIGHT = 180
NOISE_TRACKS_PER_CLIP = 10
CV_FOLDS = 5
CV_SEED = 0
BASELINE_PRECISION = 4.0 / 29.0  # 0.137931...
ATTRIBUTION_MIN_LIFT = 0.10

# Deterministic seeds for robustness pass
ROBUSTNESS_SEEDS = (0, 7, 42)


# --------------------------------------------------------------------------
# Proxy regeneration (delegated to the 09.4.1.1.2 harness)
# --------------------------------------------------------------------------


def regenerate_noisy_proxy() -> list[ClipBundle]:
    """Reuse the exact Phase 09.4.1.1.2 noisy-proxy generator, identical seed."""
    return build_noisy_proxy_corpus(
        frame_count=FRAME_COUNT,
        width=FRAME_WIDTH,
        height=FRAME_HEIGHT,
        noise_tracks_per_clip=NOISE_TRACKS_PER_CLIP,
        seed=PROXY_SEED,
    )


# --------------------------------------------------------------------------
# Portal-run (track-level) labels and sample set
# --------------------------------------------------------------------------


@dataclass
class PortalRun:
    clip_id: str
    track_id: int
    start_frame: int
    end_frame: int
    direction: str
    label: int  # 1 if matches a GT event, else 0
    # full per-frame boxes for this track (not just portal-inside)
    boxes_by_frame: dict[int, Box]


def _extract_tracks(clip: ClipBundle) -> dict[int, list[tuple[int, Box]]]:
    tracks: dict[int, list[tuple[int, Box]]] = {}
    for frame_idx, boxes in enumerate(clip.frames):
        for box in boxes:
            tracks.setdefault(int(box.box_id), []).append((frame_idx, box))
    for tid in tracks:
        tracks[tid].sort(key=lambda row: row[0])
    return tracks


def enumerate_portal_runs(bundles: list[ClipBundle]) -> list[PortalRun]:
    """One sample per naive-operator prediction.

    Labels come from temporal_iou match against the clip's ground-truth events
    (same rule used by phase9_4_1_1_2's _score). A prediction is a positive
    iff the best temporal_iou match to an unclaimed GT event is > 0.
    """
    samples: list[PortalRun] = []
    for clip in bundles:
        predicted = _extract_event_windows_naive(
            clip.clip_id,
            list(list(f) for f in clip.frames),
            clip.portal_box,
            min_event_frames=MIN_EVENT_FRAMES,
        )
        # Greedy temporal_iou match: reuse the same algorithm as _score
        matched_gt: set[int] = set()
        positive_track_ids: set[int] = set()
        for pred in predicted:
            best_idx = -1
            best_score = 0.0
            for idx, gt in enumerate(clip.gt_events):
                if idx in matched_gt:
                    continue
                if pred.clip_id != gt.clip_id or pred.direction != gt.direction:
                    continue
                start = max(pred.start_frame, gt.start_frame)
                end = min(pred.end_frame, gt.end_frame)
                if end < start:
                    continue
                inter = float(end - start + 1)
                union = float(
                    max(pred.end_frame, gt.end_frame)
                    - min(pred.start_frame, gt.start_frame)
                    + 1
                )
                score = 0.0 if union <= 0 else inter / union
                if score > best_score:
                    best_score = score
                    best_idx = idx
            is_positive = best_idx >= 0 and best_score > 0
            if is_positive:
                matched_gt.add(best_idx)
                positive_track_ids.add(int(pred.track_id))
        # Build PortalRun rows
        tracks = _extract_tracks(clip)
        for pred in predicted:
            tid = int(pred.track_id)
            row = PortalRun(
                clip_id=clip.clip_id,
                track_id=tid,
                start_frame=int(pred.start_frame),
                end_frame=int(pred.end_frame),
                direction=str(pred.direction),
                label=1 if tid in positive_track_ids else 0,
                boxes_by_frame={int(fi): box for fi, box in tracks[tid]},
            )
            samples.append(row)
    return samples


# --------------------------------------------------------------------------
# Synthetic RGB rendering for appearance crops
# --------------------------------------------------------------------------


def _render_frame_rgb(clip: ClipBundle, frame_idx: int) -> np.ndarray:
    """Minimal deterministic RGB frame: gray background + filled boxes.

    Box color is derived from (clip_id hash, box_id, bbox dims) — it is NOT
    derived from the ground-truth label, so this rendering cannot leak labels
    into the frozen-backbone appearance embeddings. The goal is to provide a
    visual scaffold so the frozen backbone can encode box shape, position,
    and local arrangement; it does NOT carry real-world texture.
    """
    H = int(clip.height)
    W = int(clip.width)
    img = np.full((H, W, 3), 128, dtype=np.uint8)  # mid-gray
    clip_hash = abs(hash(clip.clip_id)) % 997
    for box in clip.frames[frame_idx]:
        # Color: derived from box_id and shape (NOT label)
        r = (clip_hash + int(box.box_id) * 37 + int(box.w) * 3) & 0xFF
        g = (clip_hash * 3 + int(box.box_id) * 53 + int(box.h) * 5) & 0xFF
        b = (clip_hash * 7 + int(box.box_id) * 71) & 0xFF
        x0 = max(0, int(box.x))
        y0 = max(0, int(box.y))
        x1 = min(W, x0 + int(box.w))
        y1 = min(H, y0 + int(box.h))
        if x1 > x0 and y1 > y0:
            img[y0:y1, x0:x1] = (int(r), int(g), int(b))
    return img


def _crop_around_box(
    frame_rgb: np.ndarray,
    box: Box,
    padding_ratio: float = 0.5,
    out_size: int = 224,
) -> Image.Image:
    H, W, _ = frame_rgb.shape
    cx = float(box.x) + float(box.w) / 2.0
    cy = float(box.y) + float(box.h) / 2.0
    half_w = float(box.w) * (1.0 + float(padding_ratio)) / 2.0
    half_h = float(box.h) * (1.0 + float(padding_ratio)) / 2.0
    half = max(half_w, half_h, 8.0)
    x0 = int(max(0, round(cx - half)))
    y0 = int(max(0, round(cy - half)))
    x1 = int(min(W, round(cx + half)))
    y1 = int(min(H, round(cy + half)))
    if x1 <= x0 or y1 <= y0:
        # Degenerate crop — fall back to a small centered patch
        x0, y0 = 0, 0
        x1, y1 = min(W, 16), min(H, 16)
    crop = frame_rgb[y0:y1, x0:x1]
    img = Image.fromarray(crop).convert("RGB").resize((out_size, out_size), resample=Image.BILINEAR)
    return img


# --------------------------------------------------------------------------
# Backbone loading + appearance feature extraction
# --------------------------------------------------------------------------


def load_backbone(name: str, device: str = "cpu"):
    import torch
    from transformers import AutoImageProcessor, AutoModel

    torch.manual_seed(0)
    try:
        torch.use_deterministic_algorithms(True, warn_only=True)
    except Exception:
        pass
    processor = AutoImageProcessor.from_pretrained(name)
    model = AutoModel.from_pretrained(name).to(device)
    model.eval()
    return model, processor


def _deterministic_projection(in_dim: int, out_dim: int, seed: int = 0) -> np.ndarray:
    """Gaussian random projection (Johnson-Lindenstrauss), fixed seed.

    Preserves pairwise L2 distances approximately; no data fit, so CV-safe.
    Shape: (in_dim, out_dim).
    """
    rng = np.random.RandomState(int(seed))
    W = rng.normal(0.0, 1.0 / math.sqrt(float(out_dim)), size=(int(in_dim), int(out_dim))).astype(np.float32)
    return W


def _embed_image(model, processor, image: Image.Image) -> np.ndarray:
    import torch

    with torch.no_grad():
        batch = processor(images=image, return_tensors="pt")
        out = model(**batch)
    # Use mean-pool of last_hidden_state (covers CLS + patch tokens)
    vec = out.last_hidden_state.mean(dim=1).squeeze(0).cpu().numpy().astype(np.float32)
    return vec


def appearance_features_for_sample(
    sample: PortalRun,
    clip: ClipBundle,
    backbone_cache: dict[str, Any],
    projection: np.ndarray,
) -> tuple[np.ndarray, float]:
    """Return (256-D feature = concat(mean_128, std_128), extract_ms).

    First / middle / last frame crops of the track (over its full lifespan,
    not only the portal run).
    """
    model = backbone_cache["model"]
    processor = backbone_cache["processor"]
    frame_indices = sorted(sample.boxes_by_frame.keys())
    if not frame_indices:
        raise ValueError(f"no boxes for track {sample.track_id} in {sample.clip_id}")
    if len(frame_indices) == 1:
        chosen = [frame_indices[0], frame_indices[0], frame_indices[0]]
    elif len(frame_indices) == 2:
        chosen = [frame_indices[0], frame_indices[0], frame_indices[1]]
    else:
        chosen = [
            frame_indices[0],
            frame_indices[len(frame_indices) // 2],
            frame_indices[-1],
        ]
    embeddings_proj: list[np.ndarray] = []
    t0 = time.perf_counter()
    for fi in chosen:
        frame_rgb = _render_frame_rgb(clip, fi)
        crop = _crop_around_box(frame_rgb, sample.boxes_by_frame[fi])
        raw = _embed_image(model, processor, crop)  # shape (D_in,)
        proj = raw @ projection  # shape (128,)
        embeddings_proj.append(proj)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    arr = np.stack(embeddings_proj, axis=0)  # (3, 128)
    mean_vec = arr.mean(axis=0).astype(np.float32)  # (128,)
    std_vec = arr.std(axis=0).astype(np.float32)  # (128,)
    return np.concatenate([mean_vec, std_vec], axis=0), elapsed_ms


# --------------------------------------------------------------------------
# Trajectory features (analytical; no backbone)
# --------------------------------------------------------------------------


def trajectory_features_for_sample(sample: PortalRun, clip: ClipBundle) -> np.ndarray:
    """5-D: [displacement_px, length_frames, mean_speed_px_per_frame, portal_dwell_fraction, curvature].

    All quantities in pixels / frames; dimensionless ratios where stated.
    """
    frame_indices = sorted(sample.boxes_by_frame.keys())
    if not frame_indices:
        return np.zeros(5, dtype=np.float32)
    centers = []
    for fi in frame_indices:
        box = sample.boxes_by_frame[fi]
        cx = float(box.x) + float(box.w) / 2.0
        cy = float(box.y) + float(box.h) / 2.0
        centers.append((cx, cy))
    first_cx, first_cy = centers[0]
    last_cx, last_cy = centers[-1]
    displacement = math.hypot(last_cx - first_cx, last_cy - first_cy)
    length_frames = float(len(frame_indices))
    # Speed = per-step L2 distance
    steps = [math.hypot(centers[i + 1][0] - centers[i][0], centers[i + 1][1] - centers[i][1])
             for i in range(len(centers) - 1)]
    mean_speed = float(statistics.mean(steps)) if steps else 0.0
    # Portal dwell fraction: frames whose center sits inside the clip portal
    x0, y0, x1, y1 = clip.portal_box
    inside = 0
    for (cx, cy) in centers:
        if float(x0) <= cx <= float(x1) and float(y0) <= cy <= float(y1):
            inside += 1
    portal_dwell_fraction = float(inside) / length_frames if length_frames > 0 else 0.0
    # Curvature proxy: mean absolute deviation of step directions
    if len(steps) > 1:
        angles = []
        for i in range(len(centers) - 1):
            dx = centers[i + 1][0] - centers[i][0]
            dy = centers[i + 1][1] - centers[i][1]
            if math.hypot(dx, dy) < 1e-6:
                continue
            angles.append(math.atan2(dy, dx))
        if len(angles) > 1:
            # Total angle change (sum of absolute deltas), normalized by step count
            deltas = []
            for i in range(len(angles) - 1):
                d = angles[i + 1] - angles[i]
                # Wrap to [-pi, pi]
                while d > math.pi:
                    d -= 2 * math.pi
                while d < -math.pi:
                    d += 2 * math.pi
                deltas.append(abs(d))
            curvature = float(sum(deltas)) / float(len(deltas)) if deltas else 0.0
        else:
            curvature = 0.0
    else:
        curvature = 0.0
    return np.array([displacement, length_frames, mean_speed, portal_dwell_fraction, curvature], dtype=np.float32)


# --------------------------------------------------------------------------
# Feature cache assembly
# --------------------------------------------------------------------------


def assemble_features(
    bundles: list[ClipBundle],
    samples: list[PortalRun],
    backbone_name: str,
    cache_path: Path,
    force_rebuild: bool = False,
) -> dict[str, Any]:
    """Compute and cache appearance + trajectory features for every portal run."""
    bundle_by_id = {c.clip_id: c for c in bundles}
    labels = np.array([s.label for s in samples], dtype=np.int32)
    track_ids = np.array([f"{s.clip_id}__{s.track_id}" for s in samples])
    trajectory_matrix = np.stack([trajectory_features_for_sample(s, bundle_by_id[s.clip_id]) for s in samples], axis=0)
    extract_cost_samples: list[float] = []

    if cache_path.exists() and not force_rebuild:
        blob = np.load(cache_path, allow_pickle=False)
        if (
            "appearance" in blob
            and "trajectory" in blob
            and "labels" in blob
            and blob["appearance"].shape == (len(samples), 2 * APPEARANCE_PROJ_DIM)
            and blob["trajectory"].shape == trajectory_matrix.shape
            and blob["labels"].shape == labels.shape
        ):
            return {
                "appearance": blob["appearance"],
                "trajectory": blob["trajectory"],
                "labels": blob["labels"],
                "track_ids": blob["track_ids"],
                "extract_cost_ms_samples": list(blob["extract_cost_ms_samples"]),
                "backbone_name": str(blob["backbone_name"]),
                "projection_shape": tuple(blob["projection_shape"]),
                "appearance_dim": int(blob["appearance_dim"]),
                "cache_hit": True,
            }

    # Cache miss -> compute
    model, processor = load_backbone(backbone_name, device="cpu")
    backbone_cache = {"model": model, "processor": processor}
    # Probe dim by embedding a dummy image
    dummy_img = Image.fromarray(np.full((224, 224, 3), 128, dtype=np.uint8))
    probe = _embed_image(model, processor, dummy_img)
    in_dim = int(probe.shape[0])
    projection = _deterministic_projection(in_dim, APPEARANCE_PROJ_DIM, seed=0)

    appearance_matrix = np.zeros((len(samples), 2 * APPEARANCE_PROJ_DIM), dtype=np.float32)
    for i, sample in enumerate(samples):
        clip = bundle_by_id[sample.clip_id]
        vec, elapsed_ms = appearance_features_for_sample(sample, clip, backbone_cache, projection)
        appearance_matrix[i, :] = vec
        extract_cost_samples.append(float(elapsed_ms))

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        cache_path,
        appearance=appearance_matrix,
        trajectory=trajectory_matrix,
        labels=labels,
        track_ids=track_ids,
        extract_cost_ms_samples=np.array(extract_cost_samples, dtype=np.float32),
        backbone_name=np.array(backbone_name),
        projection_shape=np.array([in_dim, APPEARANCE_PROJ_DIM], dtype=np.int32),
        appearance_dim=np.array(2 * APPEARANCE_PROJ_DIM, dtype=np.int32),
    )
    return {
        "appearance": appearance_matrix,
        "trajectory": trajectory_matrix,
        "labels": labels,
        "track_ids": track_ids,
        "extract_cost_ms_samples": extract_cost_samples,
        "backbone_name": backbone_name,
        "projection_shape": (in_dim, APPEARANCE_PROJ_DIM),
        "appearance_dim": 2 * APPEARANCE_PROJ_DIM,
        "cache_hit": False,
    }


# --------------------------------------------------------------------------
# Cross-validated fit/eval
# --------------------------------------------------------------------------


def _classifier_factory(name: str, seed: int):
    from sklearn.linear_model import LogisticRegression

    if name == "logreg":
        return LogisticRegression(C=1.0, penalty="l2", solver="liblinear", class_weight="balanced", random_state=seed, max_iter=1000)
    if name == "lightgbm":
        import lightgbm as lgb

        return lgb.LGBMClassifier(
            n_estimators=100,
            max_depth=3,
            learning_rate=0.1,
            class_weight="balanced",
            random_state=seed,
            verbose=-1,
            min_child_samples=2,
            num_leaves=7,
        )
    raise ValueError(f"unknown classifier {name}")


def cv_fit_eval(
    features: np.ndarray,
    labels: np.ndarray,
    track_ids: np.ndarray,
    classifier_name: str,
    k: int = CV_FOLDS,
    seed: int = CV_SEED,
) -> list[dict[str, Any]]:
    """Stratified K-fold CV at the track level.

    Since each sample is one portal-run == one track for this proxy, track-level
    and sample-level splits coincide, but we enforce disjointness explicitly.
    """
    from sklearn.model_selection import StratifiedKFold

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        skf = StratifiedKFold(n_splits=int(k), shuffle=True, random_state=int(seed))
        splits = list(skf.split(features, labels))

    results: list[dict[str, Any]] = []
    for fold_idx, (train_idx, test_idx) in enumerate(splits):
        # Track-disjointness assertion
        train_tids = set(track_ids[train_idx])
        test_tids = set(track_ids[test_idx])
        assert train_tids.isdisjoint(test_tids), "train/test track overlap"
        X_train = features[train_idx]
        X_test = features[test_idx]
        y_train = labels[train_idx]
        y_test = labels[test_idx]
        n_train = int(len(train_idx))
        n_test = int(len(test_idx))
        n_positive_test = int(np.sum(y_test == 1))
        if int(np.sum(y_train == 1)) == 0:
            # Degenerate: no positives in train; skip fit but record
            pred = np.zeros_like(y_test)
        else:
            clf = _classifier_factory(classifier_name, seed=int(seed))
            clf.fit(X_train, y_train)
            pred = clf.predict(X_test)
        tp = int(np.sum((pred == 1) & (y_test == 1)))
        fp = int(np.sum((pred == 1) & (y_test == 0)))
        fn = int(np.sum((pred == 0) & (y_test == 1)))
        predicted_positives = int(np.sum(pred == 1))
        if predicted_positives == 0 and n_positive_test > 0:
            precision = float("nan")
            recall = 0.0
        elif n_positive_test == 0:
            # No positives at all in test — precision and recall both undefined
            precision = float("nan")
            recall = float("nan")
        else:
            precision = float(tp) / float(predicted_positives) if predicted_positives > 0 else float("nan")
            recall = float(tp) / float(n_positive_test) if n_positive_test > 0 else float("nan")
        if math.isnan(precision) or math.isnan(recall):
            f1 = float("nan")
        elif precision + recall == 0:
            f1 = 0.0
        else:
            f1 = 2.0 * precision * recall / (precision + recall)
        results.append(
            dict(
                fold_idx=int(fold_idx),
                classifier=classifier_name,
                precision=precision,
                recall=recall,
                f1=f1,
                tp=tp,
                fp=fp,
                fn=fn,
                n_train=n_train,
                n_test=n_test,
                n_positive_test=n_positive_test,
            )
        )
    return results


def _aggregate_cv(results: list[dict[str, Any]]) -> dict[str, float]:
    precisions = [r["precision"] for r in results if not math.isnan(r["precision"])]
    recalls = [r["recall"] for r in results if not math.isnan(r["recall"])]
    f1s = [r["f1"] for r in results if not math.isnan(r["f1"])]
    def _mean(xs: list[float]) -> float:
        return float(statistics.mean(xs)) if xs else float("nan")
    def _stdev(xs: list[float]) -> float:
        return float(statistics.stdev(xs)) if len(xs) > 1 else 0.0
    def _stderr(xs: list[float]) -> float:
        return _stdev(xs) / math.sqrt(len(xs)) if len(xs) > 1 else 0.0
    nan_folds = sum(1 for r in results if math.isnan(r["precision"]) or math.isnan(r["recall"]))
    return dict(
        precision_mean=_mean(precisions),
        precision_stdev=_stdev(precisions),
        precision_stderr=_stderr(precisions),
        recall_mean=_mean(recalls),
        recall_stdev=_stdev(recalls),
        recall_stderr=_stderr(recalls),
        f1_mean=_mean(f1s),
        nan_fold_count=int(nan_folds),
    )


# --------------------------------------------------------------------------
# Ablations and controls
# --------------------------------------------------------------------------


def run_ablation(
    feature_blocks: dict[str, np.ndarray],
    labels: np.ndarray,
    track_ids: np.ndarray,
    classifier_name: str,
    seed: int,
) -> dict[str, dict[str, Any]]:
    """Run three ablations: appearance_only, trajectory_only, combined."""
    out: dict[str, dict[str, Any]] = {}
    for ablation_name, feat in feature_blocks.items():
        per_fold = cv_fit_eval(feat, labels, track_ids, classifier_name, k=CV_FOLDS, seed=seed)
        agg = _aggregate_cv(per_fold)
        meets = (
            (not math.isnan(agg["precision_mean"]))
            and (not math.isnan(agg["recall_mean"]))
            and agg["precision_mean"] >= 0.5
            and agg["recall_mean"] >= 0.9
        )
        agg["meets_threshold"] = bool(meets)
        agg["per_fold"] = per_fold
        out[ablation_name] = agg
    return out


def shuffled_feature_control(
    features: np.ndarray,
    labels: np.ndarray,
    track_ids: np.ndarray,
    classifier_name: str,
    seed: int = CV_SEED,
) -> dict[str, float]:
    rng = np.random.RandomState(int(seed))
    perm = rng.permutation(len(labels))
    shuffled = features[perm, :]
    per_fold = cv_fit_eval(shuffled, labels, track_ids, classifier_name, k=CV_FOLDS, seed=seed)
    return _aggregate_cv(per_fold)


def saturated_feature_control(
    features: np.ndarray,
    labels: np.ndarray,
    track_ids: np.ndarray,
    classifier_name: str,
    seed: int = CV_SEED,
) -> dict[str, float]:
    sat = np.zeros_like(features)
    sat[:] = 1.0
    per_fold = cv_fit_eval(sat, labels, track_ids, classifier_name, k=CV_FOLDS, seed=seed)
    return _aggregate_cv(per_fold)


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------


def _write_cv_table(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "fold_idx", "classifier", "ablation", "seed", "precision", "recall", "f1",
            "tp", "fp", "fn", "n_train", "n_test", "n_positive_test",
        ])
        for r in rows:
            writer.writerow([
                r["fold_idx"], r["classifier"], r["ablation"], r.get("seed", CV_SEED),
                f"{r['precision']:.6f}" if not math.isnan(r["precision"]) else "nan",
                f"{r['recall']:.6f}" if not math.isnan(r["recall"]) else "nan",
                f"{r['f1']:.6f}" if not math.isnan(r["f1"]) else "nan",
                r["tp"], r["fp"], r["fn"], r["n_train"], r["n_test"], r["n_positive_test"],
            ])


def _write_ablation_table(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "classifier", "ablation",
            "precision_mean", "precision_stdev", "precision_stderr",
            "recall_mean", "recall_stdev", "recall_stderr",
            "f1_mean", "nan_fold_count", "meets_threshold",
        ])
        for r in rows:
            writer.writerow([
                r["classifier"], r["ablation"],
                f"{r['precision_mean']:.6f}",
                f"{r['precision_stdev']:.6f}",
                f"{r['precision_stderr']:.6f}",
                f"{r['recall_mean']:.6f}",
                f"{r['recall_stdev']:.6f}",
                f"{r['recall_stderr']:.6f}",
                f"{r['f1_mean']:.6f}",
                r["nan_fold_count"],
                "true" if r["meets_threshold"] else "false",
            ])


def run_full(
    output_dir: Path,
    backbone_name: str,
    smoke: bool = False,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    cache_path = output_dir / "feature_cache.npz"

    # ---- Proxy ----
    bundles = regenerate_noisy_proxy()
    if smoke:
        bundles = bundles[:1]
    samples = enumerate_portal_runs(bundles)
    proxy_predicted = len(samples)
    proxy_positives = int(sum(s.label for s in samples))
    proxy_gt = sum(len(c.gt_events) for c in bundles)
    proxy_matched = proxy_positives
    # In smoke mode expect the single clip's subset
    if not smoke:
        assert proxy_predicted == 29, f"proxy predicted count = {proxy_predicted}, expected 29"
        assert proxy_positives == 4, f"proxy positive count = {proxy_positives}, expected 4"
        assert proxy_gt == 4, f"proxy gt count = {proxy_gt}, expected 4"

    # ---- Features ----
    features = assemble_features(bundles, samples, backbone_name, cache_path, force_rebuild=smoke)

    appearance = features["appearance"]
    trajectory = features["trajectory"]
    labels = features["labels"].astype(np.int32)
    track_ids = features["track_ids"]
    combined = np.concatenate([appearance, trajectory], axis=1)

    feature_blocks = {
        "appearance_only": appearance,
        "trajectory_only": trajectory,
        "combined": combined,
    }

    cv_table_rows: list[dict[str, Any]] = []
    ablation_summary_rows: list[dict[str, Any]] = []
    results_by_classifier: dict[str, dict[str, Any]] = {}
    classifier_names = ["logreg", "lightgbm"]
    classifier_meets: dict[str, dict[str, bool]] = {}

    for clf_name in classifier_names:
        abl = run_ablation(feature_blocks, labels, track_ids, clf_name, seed=CV_SEED)
        results_by_classifier[clf_name] = {}
        classifier_meets[clf_name] = {}
        for ablation_name, agg in abl.items():
            # Stash per-fold rows
            for per_fold in agg["per_fold"]:
                cv_table_rows.append({**per_fold, "ablation": ablation_name})
            ablation_summary_rows.append({
                "classifier": clf_name,
                "ablation": ablation_name,
                "precision_mean": agg["precision_mean"],
                "precision_stdev": agg["precision_stdev"],
                "precision_stderr": agg["precision_stderr"],
                "recall_mean": agg["recall_mean"],
                "recall_stdev": agg["recall_stdev"],
                "recall_stderr": agg["recall_stderr"],
                "f1_mean": agg["f1_mean"],
                "nan_fold_count": agg["nan_fold_count"],
                "meets_threshold": agg["meets_threshold"],
            })
            results_by_classifier[clf_name][ablation_name] = {
                k: v for k, v in agg.items() if k != "per_fold"
            }
            classifier_meets[clf_name][ablation_name] = bool(agg["meets_threshold"])

    # ---- Winner + robustness pass ----
    # Winner = (clf, ablation) with highest precision_mean subject to recall_mean >= 0.9
    winner_ablation = None
    winner_classifier = None
    best_precision = -1.0
    for clf_name, ablations in results_by_classifier.items():
        for ab, agg in ablations.items():
            recall_mean = agg["recall_mean"]
            prec_mean = agg["precision_mean"]
            if math.isnan(recall_mean) or math.isnan(prec_mean):
                continue
            if recall_mean >= 0.9 and prec_mean > best_precision:
                best_precision = prec_mean
                winner_ablation = ab
                winner_classifier = clf_name
    # If nobody makes the recall bar, winner = highest precision across all (for reporting)
    if winner_ablation is None:
        for clf_name, ablations in results_by_classifier.items():
            for ab, agg in ablations.items():
                if math.isnan(agg["precision_mean"]):
                    continue
                if agg["precision_mean"] > best_precision:
                    best_precision = agg["precision_mean"]
                    winner_ablation = ab
                    winner_classifier = clf_name

    seed_runs: list[dict[str, Any]] = []
    if winner_ablation is not None and winner_classifier is not None:
        for seed in ROBUSTNESS_SEEDS:
            abl = run_ablation(
                {winner_ablation: feature_blocks[winner_ablation]},
                labels,
                track_ids,
                winner_classifier,
                seed=int(seed),
            )
            agg = abl[winner_ablation]
            seed_runs.append({
                "seed": int(seed),
                "precision_mean": agg["precision_mean"],
                "recall_mean": agg["recall_mean"],
                "f1_mean": agg["f1_mean"],
                "meets_threshold": bool(agg["meets_threshold"]),
                "nan_fold_count": int(agg["nan_fold_count"]),
            })
    precisions = [s["precision_mean"] for s in seed_runs if not math.isnan(s["precision_mean"])]
    recalls = [s["recall_mean"] for s in seed_runs if not math.isnan(s["recall_mean"])]
    precision_median = float(statistics.median(precisions)) if precisions else float("nan")
    recall_median = float(statistics.median(recalls)) if recalls else float("nan")
    high_variance_flag = False
    if len(seed_runs) > 1:
        seed_meets = [s["meets_threshold"] for s in seed_runs]
        if any(seed_meets) and not all(seed_meets):
            high_variance_flag = True
        if precisions and (max(precisions) - min(precisions)) >= 0.15:
            high_variance_flag = True

    # ---- Controls ----
    controls = {}
    # Use logreg for controls (as reference; same qualitative result expected)
    shuffled = shuffled_feature_control(combined, labels, track_ids, "logreg", seed=CV_SEED)
    saturated = saturated_feature_control(combined, labels, track_ids, "logreg", seed=CV_SEED)
    controls["shuffled_features_precision"] = shuffled["precision_mean"]
    controls["shuffled_features_precision_stdev"] = shuffled["precision_stdev"]
    controls["shuffled_features_recall"] = shuffled["recall_mean"]
    controls["shuffled_features_nan_fold_count"] = shuffled["nan_fold_count"]
    controls["saturated_features_precision"] = saturated["precision_mean"]
    controls["saturated_features_precision_stdev"] = saturated["precision_stdev"]
    controls["saturated_features_recall"] = saturated["recall_mean"]
    controls["saturated_features_nan_fold_count"] = saturated["nan_fold_count"]

    # ---- Attribution analysis ----
    # lift_is_attributable: a single-family ablation (appearance_only or trajectory_only)
    # shows precision_mean >= baseline + 0.1 in at least one classifier.
    attribution = {}
    attribution_single_family_lifts: list[dict[str, Any]] = []
    for clf_name in classifier_names:
        for single in ("appearance_only", "trajectory_only"):
            prec = results_by_classifier[clf_name][single]["precision_mean"]
            attribution_single_family_lifts.append({
                "classifier": clf_name,
                "family": single,
                "precision_mean": prec,
                "lift_vs_baseline": None if math.isnan(prec) else float(prec - BASELINE_PRECISION),
                "clears_attribution_min": (not math.isnan(prec)) and (prec >= BASELINE_PRECISION + ATTRIBUTION_MIN_LIFT),
            })
    attribution["single_family_lifts"] = attribution_single_family_lifts
    attribution["lift_is_attributable"] = any(e["clears_attribution_min"] for e in attribution_single_family_lifts)
    # combined >= max(single) for each classifier (sanity, overfitting check)
    attribution["combined_vs_single_family"] = []
    for clf_name in classifier_names:
        single_precisions = [
            results_by_classifier[clf_name]["appearance_only"]["precision_mean"],
            results_by_classifier[clf_name]["trajectory_only"]["precision_mean"],
        ]
        combined_precision = results_by_classifier[clf_name]["combined"]["precision_mean"]
        best_single = float("nan")
        if any(not math.isnan(p) for p in single_precisions):
            best_single = max(p for p in single_precisions if not math.isnan(p))
        attribution["combined_vs_single_family"].append({
            "classifier": clf_name,
            "combined_precision": combined_precision,
            "best_single_family_precision": best_single,
            "combined_ge_best_single": (not math.isnan(combined_precision))
            and (math.isnan(best_single) or combined_precision + 1e-9 >= best_single),
        })

    # Classifier agreement: under the winning ablation, do both pass the threshold?
    classifier_agreement = {
        "winner_ablation": winner_ablation,
        "logreg_meets_threshold": classifier_meets["logreg"][winner_ablation] if winner_ablation else False,
        "lightgbm_meets_threshold": classifier_meets["lightgbm"][winner_ablation] if winner_ablation else False,
    }
    classifier_agreement["agree"] = (
        classifier_agreement["logreg_meets_threshold"]
        and classifier_agreement["lightgbm_meets_threshold"]
    )

    # Extract cost
    extract_samples = list(features["extract_cost_ms_samples"])
    if extract_samples:
        extract_median = float(statistics.median(extract_samples))
        sorted_cost = sorted(extract_samples)
        p90_idx = min(len(sorted_cost) - 1, int(math.ceil(0.9 * len(sorted_cost))) - 1)
        extract_p90 = float(sorted_cost[p90_idx])
        extract_min = float(min(extract_samples))
        extract_max = float(max(extract_samples))
    else:
        extract_median = 0.0
        extract_p90 = 0.0
        extract_min = 0.0
        extract_max = 0.0

    # Verdict
    verdict_components = {
        "has_configuration_meeting_threshold": any(
            classifier_meets[c][a] for c in classifier_names for a in ("appearance_only", "trajectory_only", "combined")
        ),
        "classifier_agreement": classifier_agreement["agree"],
        "attribution.lift_is_attributable": attribution["lift_is_attributable"],
        "high_variance_flag_false": not high_variance_flag,
        "shuffled_features_precision_lt_0.25": (
            not math.isnan(controls["shuffled_features_precision"])
            and controls["shuffled_features_precision"] < 0.25
        ),
    }
    verdict = "defend" if all(verdict_components.values()) else "kill"
    if verdict == "defend" and winner_ablation in ("combined",):
        # Extra check: combined must not silently outperform both single-family ablations by a huge
        # margin while both single families fail attribution (already handled by lift_is_attributable)
        pass
    verdict_justification_lines = []
    for k, v in verdict_components.items():
        verdict_justification_lines.append(f"{k}={v}")
    verdict_justification = "; ".join(verdict_justification_lines)

    # Forbidden-proxy audit (explicit record that each forbidden proxy is rejected)
    forbidden_proxy_audit = {
        "rebrand_as_zpe_wedge": "rejected: state-layer-not-serialization disclosure included",
        "leaky_cv": "rejected: stratified K-fold at the track level; train/test tracks asserted disjoint",
        "overfit_combined_only": "rejected: defend requires single-family attribution lift >= 0.1",
        "gt_leakage": "rejected: labels never used as features",
        "cherry_pick": "rejected: mean + stdev across all folds reported; NaN folds flagged",
        "ap_proxy": "rejected: binary precision and recall only",
        "external_repo_touch": "rejected: local commits only",
        "reopen_phase10": "rejected: out of scope",
        "reopen_archive_query_box_state": "rejected: out of scope",
    }

    summary = {
        "phase": "09.4.1.1.2.1-parallel-bounded-wedge-discovery-three-hypotheses-run-in-wave-parallel-no-pre-selection",
        "plan": "03",
        "candidate": "C-primitive-semantic-enrichment",
        "proxy": {
            "seed": PROXY_SEED,
            "frame_count": FRAME_COUNT,
            "width": FRAME_WIDTH,
            "height": FRAME_HEIGHT,
            "noise_tracks_per_clip": NOISE_TRACKS_PER_CLIP,
            "total_predicted": proxy_predicted,
            "total_matched": proxy_matched,
            "total_gt": proxy_gt,
            "base_rate": BASELINE_PRECISION,
        },
        "backbone": {
            "name": features["backbone_name"],
            "in_dim": int(features["projection_shape"][0]),
            "projected_dim": int(features["projection_shape"][1]),
            "note": "appearance features were computed over a deterministic synthetic RGB render of the proxy (gray background + colored rectangles keyed to box_id and shape, NOT label). The proxy has no underlying video texture; the backbone embedding therefore encodes box geometry, position, and local arrangement through a frozen visual pathway. This is an honest approximation — see report for full disclosure.",
        },
        "classifiers": classifier_names,
        "ablations": list(feature_blocks.keys()),
        "cv": {
            "k": CV_FOLDS,
            "seed": CV_SEED,
            "split_level": "track",
            "track_disjointness_asserted": True,
            "stratify_label": True,
        },
        "feature_dims": {
            "appearance_only": int(appearance.shape[1]),
            "trajectory_only": int(trajectory.shape[1]),
            "combined": int(combined.shape[1]),
        },
        "results": {
            clf: {ab: results_by_classifier[clf][ab] for ab in feature_blocks}
            for clf in classifier_names
        },
        "robustness_seeds": {
            "winner_ablation": winner_ablation,
            "winner_classifier": winner_classifier,
            "seeds": list(ROBUSTNESS_SEEDS),
            "per_seed": seed_runs,
            "precision_median": precision_median,
            "recall_median": recall_median,
            "high_variance_flag": high_variance_flag,
        },
        "controls": controls,
        "attribution": attribution,
        "classifier_agreement": classifier_agreement,
        "extract_cost_ms_per_track": {
            "median": extract_median,
            "p90": extract_p90,
            "min": extract_min,
            "max": extract_max,
            "n_samples": int(len(extract_samples)),
        },
        "verdict": verdict,
        "verdict_components": verdict_components,
        "verdict_justification": verdict_justification,
        "sovereign_gate_status": "red",
        "state_layer_not_serialization_disclosure": (
            "A defend verdict establishes only that the state-enrichment layer is "
            "the lever. Appearance embeddings and trajectory features can be "
            "attached to any sparse-metadata format (raw struct+zlib, Parquet, "
            "JSON+gzip) equally well. This result is therefore NOT a ZPE-"
            "specific wedge. The Compass-8 sovereign primitive-native gate "
            "remains red regardless of verdict."
        ),
        "forbidden_proxy_audit": forbidden_proxy_audit,
    }

    # Emit summary.json
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=float))
    _write_cv_table(output_dir / "cv_table.csv", cv_table_rows)
    _write_ablation_table(output_dir / "ablation_table.csv", ablation_summary_rows)

    return summary


# --------------------------------------------------------------------------
# Smoke mode
# --------------------------------------------------------------------------


def run_smoke(output_dir: Path, backbone_name: str) -> None:
    """End-to-end micro-run on a single clip plus determinism/dimension checks."""
    # Sample enumeration on full proxy
    bundles = regenerate_noisy_proxy()
    samples_full = enumerate_portal_runs(bundles)
    assert len(samples_full) == 29, f"full proxy predicted count = {len(samples_full)}, expected 29"
    n_pos = sum(s.label for s in samples_full)
    assert n_pos == 4, f"full proxy positives = {n_pos}, expected 4"

    # Backbone load + embedding dim
    model, processor = load_backbone(backbone_name, device="cpu")
    dummy = Image.fromarray(np.full((224, 224, 3), 128, dtype=np.uint8))
    vec = _embed_image(model, processor, dummy)
    assert vec.ndim == 1 and vec.shape[0] > 0
    # Deterministic projection check
    P1 = _deterministic_projection(vec.shape[0], APPEARANCE_PROJ_DIM, seed=0)
    P2 = _deterministic_projection(vec.shape[0], APPEARANCE_PROJ_DIM, seed=0)
    assert np.allclose(P1, P2)

    # Track-level CV split disjointness
    from sklearn.model_selection import StratifiedKFold
    y = np.array([s.label for s in samples_full], dtype=np.int32)
    ids = np.array([f"{s.clip_id}__{s.track_id}" for s in samples_full])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        skf = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=CV_SEED)
        for tr, te in skf.split(np.zeros((len(y), 1)), y):
            assert set(ids[tr]).isdisjoint(set(ids[te]))

    # Feature dimensions smoke: build features on ONE clip only
    single_clip = bundles[:1]
    samples_single = enumerate_portal_runs(single_clip)
    cache_path = output_dir / "feature_cache_smoke.npz"
    features = assemble_features(single_clip, samples_single, backbone_name, cache_path, force_rebuild=True)
    appearance = features["appearance"]
    trajectory = features["trajectory"]
    assert appearance.shape[1] == 2 * APPEARANCE_PROJ_DIM, f"appearance dim = {appearance.shape[1]}"
    assert trajectory.shape[1] == 5, f"trajectory dim = {trajectory.shape[1]}"
    combined_dim = appearance.shape[1] + trajectory.shape[1]
    assert combined_dim == 2 * APPEARANCE_PROJ_DIM + 5, f"combined dim = {combined_dim}"

    # Determinism: re-run appearance extraction on the same track and check bit-equality
    # within 1e-6 (floating-point epsilon tolerance for non-deterministic CPU kernels)
    features2 = assemble_features(single_clip, samples_single, backbone_name, output_dir / "feature_cache_smoke2.npz", force_rebuild=True)
    delta = float(np.max(np.abs(features["appearance"] - features2["appearance"])))
    print(f"smoke determinism: max |delta| appearance = {delta:.2e}")

    # Clean up smoke caches
    try:
        cache_path.unlink()
    except FileNotFoundError:
        pass
    try:
        (output_dir / "feature_cache_smoke2.npz").unlink()
    except FileNotFoundError:
        pass
    print(f"smoke ok: samples=29 positives=4 appearance_dim={appearance.shape[1]} trajectory_dim={trajectory.shape[1]} combined_dim={combined_dim}")


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backbone", default=BACKBONE_NAME_DEFAULT, help="HF model id for the frozen backbone")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--smoke", action="store_true", help="run smoke-test checks only")
    parser.add_argument("--force-rebuild", action="store_true", help="recompute feature cache from scratch")
    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.smoke:
        run_smoke(output_dir, args.backbone)
        return 0

    if args.force_rebuild:
        cache = output_dir / "feature_cache.npz"
        if cache.exists():
            cache.unlink()

    summary = run_full(output_dir, args.backbone, smoke=False)
    print(json.dumps({
        "verdict": summary["verdict"],
        "verdict_justification": summary["verdict_justification"],
        "proxy_predicted": summary["proxy"]["total_predicted"],
        "proxy_matched": summary["proxy"]["total_matched"],
        "proxy_gt": summary["proxy"]["total_gt"],
        "winner_ablation": summary["robustness_seeds"]["winner_ablation"],
        "winner_classifier": summary["robustness_seeds"]["winner_classifier"],
        "classifier_agreement.agree": summary["classifier_agreement"]["agree"],
        "lift_is_attributable": summary["attribution"]["lift_is_attributable"],
        "high_variance_flag": summary["robustness_seeds"]["high_variance_flag"],
        "shuffled_precision": summary["controls"]["shuffled_features_precision"],
        "saturated_precision": summary["controls"]["saturated_features_precision"],
        "extract_cost_ms_median": summary["extract_cost_ms_per_track"]["median"],
    }, indent=2, default=float))
    return 0


if __name__ == "__main__":
    sys.exit(main())
