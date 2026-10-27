import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PySide6.QtGui import QImage

from .runtime import create_session


@dataclass(frozen=True)
class Box:
    class_id: int
    confidence: float
    x1: float
    y1: float
    x2: float
    y2: float


@dataclass(frozen=True)
class DetectionResult:
    minefield: Box
    remaining_counters: tuple[Box, ...]


class Detector:
    def __init__(
        self,
        model_path: Path,
        metadata_path: Path,
        processor: str = "auto",
    ) -> None:
        self._metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        expected_hash = self._metadata["model"]["sha256"]
        actual_hash = hashlib.sha256(model_path.read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            raise RuntimeError("detector model checksum does not match metadata")

        self._session, self.processor = create_session(model_path, processor)
        self._input_name = self._session.get_inputs()[0].name
        self._output_name = self._session.get_outputs()[0].name
        self._input_size = int(self._metadata["input"]["shape"][2])
        self._confidence = float(
            self._metadata["runtime"]["confidence_threshold"]
        )
        self._iou_threshold = float(
            self._metadata["runtime"]["nms_iou_threshold"]
        )
        self._max_detections = int(
            self._metadata["runtime"]["max_detections"]
        )
        self._minefield_id = next(
            int(class_id)
            for class_id, name in self._metadata["classes"].items()
            if name == "minefield"
        )
        self._counter_id = next(
            int(class_id)
            for class_id, name in self._metadata["classes"].items()
            if name == "remaining_counter"
        )

    def detect(self, image: QImage) -> DetectionResult | None:
        if image.isNull():
            raise ValueError("cannot detect an empty image")

        tensor, ratio, pad_left, pad_top = self._prepare(image)
        output = self._session.run(
            [self._output_name],
            {self._input_name: tensor},
        )[0]
        boxes = self._decode(
            output,
            image.width(),
            image.height(),
            ratio,
            pad_left,
            pad_top,
        )

        minefields = [box for box in boxes if box.class_id == self._minefield_id]
        counters = [box for box in boxes if box.class_id == self._counter_id]
        if len(minefields) != 1 or len(counters) != 4:
            return None

        counters.sort(key=lambda box: (box.y1, box.x1))
        return DetectionResult(minefields[0], tuple(counters))

    def _prepare(self, image: QImage) -> tuple[np.ndarray, float, int, int]:
        rgb_image = image.convertToFormat(QImage.Format.Format_RGB888)
        width = rgb_image.width()
        height = rgb_image.height()
        raw = np.frombuffer(
            rgb_image.constBits(),
            dtype=np.uint8,
            count=rgb_image.sizeInBytes(),
        ).reshape(height, rgb_image.bytesPerLine())
        rgb = raw[:, : width * 3].reshape(height, width, 3)

        ratio = min(self._input_size / width, self._input_size / height)
        new_width = max(round(width * ratio), 1)
        new_height = max(round(height * ratio), 1)
        pad_width = self._input_size - new_width
        pad_height = self._input_size - new_height
        pad_left = round(pad_width / 2 - 0.1)
        pad_top = round(pad_height / 2 - 0.1)

        resized = cv2.resize(
            rgb,
            (new_width, new_height),
            interpolation=cv2.INTER_LINEAR,
        )
        padded = np.full(
            (self._input_size, self._input_size, 3),
            int(self._metadata["input"]["padding_value"]),
            dtype=np.uint8,
        )
        padded[
            pad_top : pad_top + new_height,
            pad_left : pad_left + new_width,
        ] = resized
        tensor = padded.transpose(2, 0, 1)[None]
        tensor = np.ascontiguousarray(tensor, dtype=np.float32) / 255.0
        return tensor, ratio, pad_left, pad_top

    def _decode(
        self,
        output: np.ndarray,
        image_width: int,
        image_height: int,
        ratio: float,
        pad_left: int,
        pad_top: int,
    ) -> list[Box]:
        predictions = np.asarray(output, dtype=np.float32)
        if predictions.ndim != 3 or predictions.shape[0] != 1:
            raise RuntimeError(f"unexpected detector output shape: {predictions.shape}")

        predictions = predictions[0].T
        class_scores = predictions[:, 4:]
        class_ids = class_scores.argmax(axis=1)
        confidences = class_scores.max(axis=1)
        keep = confidences >= self._confidence
        if not np.any(keep):
            return []

        centers = predictions[keep, :4]
        confidences = confidences[keep]
        class_ids = class_ids[keep]
        boxes = np.empty_like(centers)
        boxes[:, 0] = centers[:, 0] - centers[:, 2] / 2
        boxes[:, 1] = centers[:, 1] - centers[:, 3] / 2
        boxes[:, 2] = centers[:, 0] + centers[:, 2] / 2
        boxes[:, 3] = centers[:, 1] + centers[:, 3] / 2

        selected = self._nms(boxes, confidences, class_ids)
        boxes = boxes[selected]
        confidences = confidences[selected]
        class_ids = class_ids[selected]

        boxes[:, [0, 2]] = (boxes[:, [0, 2]] - pad_left) / ratio
        boxes[:, [1, 3]] = (boxes[:, [1, 3]] - pad_top) / ratio
        boxes[:, [0, 2]] = boxes[:, [0, 2]].clip(0, image_width)
        boxes[:, [1, 3]] = boxes[:, [1, 3]].clip(0, image_height)

        return [
            Box(
                class_id=int(class_id),
                confidence=float(confidence),
                x1=float(box[0]),
                y1=float(box[1]),
                x2=float(box[2]),
                y2=float(box[3]),
            )
            for box, confidence, class_id in zip(
                boxes,
                confidences,
                class_ids,
            )
        ]

    def _nms(
        self,
        boxes: np.ndarray,
        scores: np.ndarray,
        class_ids: np.ndarray,
    ) -> list[int]:
        areas = (
            (boxes[:, 2] - boxes[:, 0]).clip(0)
            * (boxes[:, 3] - boxes[:, 1]).clip(0)
        )
        selected: list[int] = []
        for class_id in np.unique(class_ids):
            indexes = np.flatnonzero(class_ids == class_id)
            indexes = indexes[np.argsort(scores[indexes])[::-1]]
            while indexes.size:
                current = int(indexes[0])
                selected.append(current)
                if indexes.size == 1 or len(selected) >= self._max_detections:
                    break

                rest = indexes[1:]
                overlap_x1 = np.maximum(boxes[current, 0], boxes[rest, 0])
                overlap_y1 = np.maximum(boxes[current, 1], boxes[rest, 1])
                overlap_x2 = np.minimum(boxes[current, 2], boxes[rest, 2])
                overlap_y2 = np.minimum(boxes[current, 3], boxes[rest, 3])
                overlap_area = (
                    (overlap_x2 - overlap_x1).clip(0)
                    * (overlap_y2 - overlap_y1).clip(0)
                )
                union_area = areas[current] + areas[rest] - overlap_area
                overlap = np.divide(
                    overlap_area,
                    union_area,
                    out=np.zeros_like(overlap_area),
                    where=union_area > 0,
                )
                indexes = rest[overlap <= self._iou_threshold]

        selected.sort(key=lambda index: scores[index], reverse=True)
        return selected[: self._max_detections]
