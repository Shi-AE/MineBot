import json
from pathlib import Path

import cv2
import numpy as np
from PySide6.QtGui import QImage

from .runtime import create_session
from .types import Classification


class Classifier:
    def __init__(
        self,
        model_path: Path,
        metadata_path: Path,
        processor: str,
        *,
        confidence_threshold: float = 0.0,
        margin_threshold: float = 0.0,
    ) -> None:
        self._metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        self._classes = tuple(str(name) for name in self._metadata["classes"])
        self._input_name = str(self._metadata["input_name"])
        self._output_name = str(self._metadata["output_name"])
        input_shape = self._metadata["input_shape"]
        self._width = int(input_shape[3])
        self._height = int(input_shape[2])
        self._confidence_threshold = confidence_threshold
        self._margin_threshold = margin_threshold
        self._session, self.processor = create_session(model_path, processor)

    def predict(self, images: list[QImage]) -> list[Classification]:
        if not images:
            return []

        batch = np.stack(
            [self._prepare_image(image) for image in images],
            axis=0,
        )
        logits = self._session.run(
            [self._output_name],
            {self._input_name: batch},
        )[0]
        probabilities = _softmax(np.asarray(logits, dtype=np.float32))
        if probabilities.ndim != 2 or probabilities.shape[1] != len(self._classes):
            raise RuntimeError(
                f"unexpected classifier output shape: {probabilities.shape}"
            )

        best_indexes = probabilities.argmax(axis=1)
        top_probabilities = probabilities[
            np.arange(probabilities.shape[0]),
            best_indexes,
        ]
        second_probabilities = probabilities.copy()
        second_probabilities[
            np.arange(second_probabilities.shape[0]),
            best_indexes,
        ] = -1.0
        second_indexes = second_probabilities.argmax(axis=1)

        results: list[Classification] = []
        for row, best_index in enumerate(best_indexes):
            confidence = float(top_probabilities[row])
            margin = confidence - float(
                probabilities[row, second_indexes[row]]
            )
            best_kind = self._classes[int(best_index)]
            accepted = (
                confidence >= self._confidence_threshold
                and margin >= self._margin_threshold
            )
            results.append(
                Classification(
                    kind=best_kind if accepted else "UNKNOWN",
                    best_kind=best_kind,
                    confidence=confidence,
                    margin=margin,
                )
            )
        return results

    def _prepare_image(self, image: QImage) -> np.ndarray:
        if image.isNull():
            raise ValueError("cannot classify an empty image")

        rgb_image = image.convertToFormat(QImage.Format.Format_RGB888)
        width = rgb_image.width()
        height = rgb_image.height()
        raw = np.frombuffer(
            rgb_image.constBits(),
            dtype=np.uint8,
            count=rgb_image.sizeInBytes(),
        ).reshape(height, rgb_image.bytesPerLine())
        rgb = raw[:, : width * 3].reshape(height, width, 3)
        resized = cv2.resize(
            rgb,
            (self._width, self._height),
            interpolation=cv2.INTER_LINEAR,
        )
        tensor = resized.transpose(2, 0, 1)
        return np.ascontiguousarray(tensor, dtype=np.float32) / 255.0


def _softmax(logits: np.ndarray) -> np.ndarray:
    shifted = logits - logits.max(axis=1, keepdims=True)
    exponential = np.exp(shifted)
    return exponential / exponential.sum(axis=1, keepdims=True)
