import math
import os
import threading
from pathlib import Path

from PySide6.QtCore import QObject, QRect, QThread, Signal, Slot
from PySide6.QtGui import QImage

from .detector import Box, DetectionResult, Detector


class _RecognitionThread(QThread):
    detectionSaved = Signal(int, object)
    processorChanged = Signal(str)
    errorRaised = Signal(str)

    def __init__(
        self,
        model_path: Path,
        metadata_path: Path,
        output_dir: Path,
        processor: str,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._model_path = model_path
        self._metadata_path = metadata_path
        self._output_dir = output_dir
        self._processor = processor
        self._condition = threading.Condition()
        self._pending: tuple[int, QImage] | None = None
        self._stopping = False

    def submit(self, frame_number: int, image: QImage) -> None:
        with self._condition:
            self._pending = (frame_number, image.copy())
            self._condition.notify()

    def stop(self) -> None:
        with self._condition:
            self._stopping = True
            self._pending = None
            self._condition.notify()

    def run(self) -> None:
        try:
            detector = Detector(
                self._model_path,
                self._metadata_path,
                self._processor,
            )
        except Exception as error:
            self.errorRaised.emit(f"failed to initialize detector: {error}")
            return
        self.processorChanged.emit(detector.processor)

        while True:
            with self._condition:
                while self._pending is None and not self._stopping:
                    self._condition.wait()
                if self._stopping:
                    return
                frame_number, image = self._pending
                self._pending = None

            try:
                result = detector.detect(image)
                if result is None:
                    continue
                self._save_crops(image, result)
                self.detectionSaved.emit(frame_number, result)
            except Exception as error:
                self.errorRaised.emit(f"frame {frame_number}: {error}")

    def _save_crops(self, image: QImage, result: DetectionResult) -> None:
        self._output_dir.mkdir(parents=True, exist_ok=True)
        minefield = _expand_box(
            result.minefield,
            image.width(),
            image.height(),
            fraction=0.01,
        )
        crops = [("minefield.png", minefield)]
        crops.extend(
            (f"counter_{index}.png", box)
            for index, box in enumerate(result.remaining_counters, start=1)
        )

        pending: list[tuple[Path, Path]] = []
        try:
            for name, box in crops:
                target = self._output_dir / name
                temporary = self._output_dir / f".{name}.tmp"
                crop = image.copy(
                    _box_to_rect(box, image.width(), image.height())
                )
                if not crop.save(str(temporary), "PNG"):
                    raise OSError(f"failed to save {temporary}")
                pending.append((temporary, target))

            for temporary, target in pending:
                os.replace(temporary, target)
        finally:
            for temporary, _ in pending:
                temporary.unlink(missing_ok=True)


class RecognitionService(QObject):
    detectionSaved = Signal(int, object)
    processorChanged = Signal(str)
    errorRaised = Signal(str)

    def __init__(
        self,
        model_path: Path,
        metadata_path: Path,
        output_dir: Path,
        processor: str = "auto",
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._model_path = model_path
        self._metadata_path = metadata_path
        self._output_dir = output_dir
        self._processor = processor
        self._thread: _RecognitionThread | None = None

    @Slot()
    def start(self) -> None:
        if self._thread is not None and self._thread.isRunning():
            return

        thread = _RecognitionThread(
            self._model_path,
            self._metadata_path,
            self._output_dir,
            self._processor,
            self,
        )
        thread.detectionSaved.connect(self.detectionSaved)
        thread.processorChanged.connect(self.processorChanged)
        thread.errorRaised.connect(self._on_error)
        thread.finished.connect(lambda: self._recognition_finished(thread))
        thread.finished.connect(thread.deleteLater)
        self._thread = thread
        thread.start()

    @Slot(str)
    def set_processor(self, processor: str) -> None:
        if processor == self._processor:
            return
        self._processor = processor
        if self._thread is not None and self._thread.isRunning():
            self.stop()
            self.start()

    @Slot(int, QImage, object)
    def submit_frame(
        self,
        frame_number: int,
        image: QImage,
        _rect: object,
    ) -> None:
        if self._thread is None or not self._thread.isRunning():
            return
        self._thread.submit(frame_number, image)

    @Slot()
    def stop(self) -> None:
        thread = self._thread
        if thread is None:
            return

        self._thread = None
        thread.stop()
        if not thread.wait(2000):
            self.errorRaised.emit("recognition worker did not stop in time")

    @Slot(str)
    def _on_error(self, message: str) -> None:
        self.errorRaised.emit(message)

    def _recognition_finished(self, thread: _RecognitionThread) -> None:
        if self._thread is thread:
            self._thread = None


def _expand_box(
    box: Box,
    image_width: int,
    image_height: int,
    fraction: float,
) -> Box:
    pad_x = (box.x2 - box.x1) * fraction
    pad_y = (box.y2 - box.y1) * fraction
    return Box(
        class_id=box.class_id,
        confidence=box.confidence,
        x1=max(0.0, box.x1 - pad_x),
        y1=max(0.0, box.y1 - pad_y),
        x2=min(float(image_width), box.x2 + pad_x),
        y2=min(float(image_height), box.y2 + pad_y),
    )


def _box_to_rect(box: Box, image_width: int, image_height: int) -> QRect:
    x1 = max(0, min(image_width - 1, math.floor(box.x1)))
    y1 = max(0, min(image_height - 1, math.floor(box.y1)))
    x2 = max(x1 + 1, min(image_width, math.ceil(box.x2)))
    y2 = max(y1 + 1, min(image_height, math.ceil(box.y2)))
    return QRect(x1, y1, x2 - x1, y2 - y1)
