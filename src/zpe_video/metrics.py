from __future__ import annotations

import hashlib
import math
from statistics import mean

from .models import Box


def iou(a: Box, b: Box) -> float:
    x0 = max(a.x, b.x)
    y0 = max(a.y, b.y)
    x1 = min(a.x + a.w, b.x + b.w)
    y1 = min(a.y + a.h, b.y + b.h)
    iw = x1 - x0
    ih = y1 - y0
    if iw <= 0 or ih <= 0:
        return 0.0
    inter = iw * ih
    union = (a.w * a.h) + (b.w * b.h) - inter
    if union <= 0:
        return 0.0
    return inter / union


def _match_frame(gt: list[Box], pred: list[Box], iou_threshold: float = 0.5) -> tuple[int, int, int]:
    gt_used = [False] * len(gt)
    pred_used = [False] * len(pred)
    matches = 0

    for pred_idx, p in enumerate(pred):
        best_gt_idx = -1
        best_iou = 0.0
        for gt_idx, g in enumerate(gt):
            if gt_used[gt_idx]:
                continue
            score = iou(g, p)
            if score > best_iou:
                best_iou = score
                best_gt_idx = gt_idx
        if best_gt_idx >= 0 and best_iou >= iou_threshold:
            gt_used[best_gt_idx] = True
            pred_used[pred_idx] = True
            matches += 1

    tp = matches
    fp = len(pred) - matches
    fn = len(gt) - matches
    return tp, fp, fn


def ap_proxy(gt_frames: list[list[Box]], pred_frames: list[list[Box]], iou_threshold: float = 0.5) -> float:
    if not gt_frames:
        return 0.0
    frame_scores: list[float] = []
    for idx, gt in enumerate(gt_frames):
        pred = pred_frames[idx] if idx < len(pred_frames) else []
        tp, fp, fn = _match_frame(gt, pred, iou_threshold=iou_threshold)
        precision = tp / (tp + fp) if (tp + fp) else 1.0
        recall = tp / (tp + fn) if (tp + fn) else 1.0
        if precision + recall == 0.0:
            score = 0.0
        else:
            score = (2.0 * precision * recall) / (precision + recall)
        frame_scores.append(score)
    return mean(frame_scores)


def mse(a: bytes, b: bytes) -> float:
    if len(a) != len(b) or not a:
        return float("inf")
    total = 0.0
    for i in range(len(a)):
        d = a[i] - b[i]
        total += float(d * d)
    return total / float(len(a))


def psnr(a: bytes, b: bytes) -> float:
    m = mse(a, b)
    if m == 0.0:
        return 99.0
    if math.isinf(m):
        return 0.0
    return 10.0 * math.log10((255.0 * 255.0) / m)


def mse_percent(a: bytes, b: bytes) -> float:
    m = mse(a, b)
    if math.isinf(m):
        return 100.0
    return (m / (255.0 * 255.0)) * 100.0


def lpips_proxy(a: bytes, b: bytes, width: int, height: int) -> float:
    if len(a) != len(b) or len(a) != width * height:
        return 1.0
    # L1 pixel difference + simple gradient delta as a lightweight LPIPS stand-in.
    pixel_total = 0.0
    grad_total = 0.0
    grad_count = 0
    for y in range(height):
        row = y * width
        for x in range(width):
            idx = row + x
            pixel_total += abs(a[idx] - b[idx]) / 255.0
            if x + 1 < width:
                grad_count += 1
                a_grad = abs(a[idx + 1] - a[idx]) / 255.0
                b_grad = abs(b[idx + 1] - b[idx]) / 255.0
                grad_total += abs(a_grad - b_grad)
    pixel_score = pixel_total / float(width * height)
    grad_score = grad_total / float(grad_count) if grad_count else 0.0
    return (0.6 * pixel_score) + (0.4 * grad_score)


def mean_value(values: list[float]) -> float:
    if not values:
        return 0.0
    return mean(values)


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    if pct <= 0:
        return min(values)
    if pct >= 100:
        return max(values)
    ordered = sorted(values)
    idx = int(round((pct / 100.0) * (len(ordered) - 1)))
    return ordered[idx]


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()
