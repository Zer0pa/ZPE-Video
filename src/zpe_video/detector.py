from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

import numpy as np
from PIL import Image

from .models import Box

COCO_TO_EVAL_LABEL = {
    1: 1,  # person
    2: 2,  # bicycle
    3: 3,  # car
    4: 4,  # motorcycle
    6: 5,  # bus
    8: 6,  # truck
}

VISDRONE_TO_EVAL_LABEL = {
    1: 1,   # pedestrian
    2: 1,   # people
    3: 2,   # bicycle
    4: 3,   # car
    5: 3,   # van
    6: 6,   # truck
    7: 2,   # tricycle
    8: 2,   # awning-tricycle
    9: 5,   # bus
    10: 4,  # motor
}


class TorchvisionCocoDetector:
    def __init__(self, *, score_threshold: float = 0.25) -> None:
        import torch
        from torchvision.models.detection import (
            FasterRCNN_MobileNet_V3_Large_320_FPN_Weights,
            fasterrcnn_mobilenet_v3_large_320_fpn,
        )

        weights = FasterRCNN_MobileNet_V3_Large_320_FPN_Weights.DEFAULT
        self._weights = weights
        self._torch = torch
        self._to_tensor = weights.transforms()
        self._device = torch.device("cpu")
        torch.set_num_threads(max(1, min(8, torch.get_num_threads())))
        self._model = fasterrcnn_mobilenet_v3_large_320_fpn(weights=weights, box_score_thresh=score_threshold)
        self._model.eval()
        self._model.to(self._device)
        self.score_threshold = score_threshold

    @property
    def checkpoint_path(self) -> Path | None:
        filename = Path(urlparse(self._weights.url).path).name
        if not filename:
            return None
        return Path(self._torch.hub.get_dir()) / "checkpoints" / filename

    @property
    def model_id(self) -> str:
        return "torchvision_fasterrcnn_mobilenet_v3_large_320_fpn_coco"

    def predict(self, image: np.ndarray) -> list[Box]:
        if image.ndim != 3 or image.shape[2] != 3:
            raise ValueError(f"Expected RGB image, got shape {image.shape}")
        tensor = self._to_tensor(Image.fromarray(image)).to(self._device)
        with self._torch.inference_mode():
            output = self._model([tensor])[0]
        boxes: list[Box] = []
        next_box_id = 0
        predicted_boxes = output["boxes"].detach().cpu().numpy()
        predicted_labels = output["labels"].detach().cpu().numpy()
        predicted_scores = output["scores"].detach().cpu().numpy()
        height, width = image.shape[:2]
        for coords, coco_label, score in zip(predicted_boxes, predicted_labels, predicted_scores):
            if float(score) < self.score_threshold:
                continue
            eval_label = COCO_TO_EVAL_LABEL.get(int(coco_label))
            if eval_label is None:
                continue
            x0, y0, x1, y1 = [float(value) for value in coords]
            left = max(0, min(width - 1, int(round(x0))))
            top = max(0, min(height - 1, int(round(y0))))
            right = max(left + 1, min(width, int(round(x1))))
            bottom = max(top + 1, min(height, int(round(y1))))
            boxes.append(
                Box(
                    box_id=next_box_id,
                    x=left,
                    y=top,
                    w=right - left,
                    h=bottom - top,
                    label=eval_label,
                    confidence=float(score),
                )
            )
            next_box_id += 1
        return boxes
