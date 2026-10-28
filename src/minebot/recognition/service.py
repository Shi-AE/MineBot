import math
import threading
import time
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QObject, QRect, QThread, Signal, Slot
from PySide6.QtGui import QImage

from .classifier import Classifier
from .counter import split_counter
from .detector import Box, DetectionResult, Detector
from .grid import detect_grid
from .types import (
    CellRecognition,
    Classification,
    CounterRecognition,
    RecognitionSnapshot,
    make_board_key,
    snapshot_to_qml,
)
from .writer import DebugFrame, DebugWriter


_THRESHOLD_VERSION = "field-uncalibrated-v1"
# 现场版始终接受 top-1 分类；阈值 0 使 UNKNOWN 仅保留给切分失败等
# 异常路径，直到基于真实游戏帧重新校准阈值。
_UNKNOWN = Classification("UNKNOWN", "UNKNOWN", 0.0, 0.0)


@dataclass(frozen=True)
class DecisionThresholds:
    confidence: float
    margin: float


_CELL_THRESHOLDS = DecisionThresholds(confidence=0.0, margin=0.0)
_FLAG_THRESHOLDS = DecisionThresholds(confidence=0.0, margin=0.0)
_SLOT_THRESHOLDS = DecisionThresholds(confidence=0.0, margin=0.0)


@dataclass(frozen=True)
class RecognitionModels:
    detector_model: Path
    detector_metadata: Path
    cell_model: Path
    cell_metadata: Path
    flag_model: Path
    flag_metadata: Path
    slot_model: Path
    slot_metadata: Path


class _RecognitionThread(QThread):
    """单工作线程，跨帧复用模型会话。

    等待队列只有一个槽位，实现“最新帧覆盖”：识别进行中时，新帧直接覆盖
    待处理帧而不堆积。
    """

    snapshotReady = Signal(object)
    processorChanged = Signal(str)
    errorRaised = Signal(str)

    def __init__(
        self,
        models: RecognitionModels,
        processor: str,
        debug_writer: DebugWriter,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._models = models
        self._processor = processor
        self._debug_writer = debug_writer
        self._condition = threading.Condition()
        self._pending: tuple[int, QImage, dict[str, int]] | None = None
        self._stopping = False

    def submit(
        self,
        frame_number: int,
        image: QImage,
        rect: dict[str, int],
    ) -> None:
        with self._condition:
            # QImage 可能共享底层缓冲区，入队前必须复制。
            self._pending = (frame_number, image.copy(), dict(rect))
            self._condition.notify()

    def stop(self) -> None:
        with self._condition:
            self._stopping = True
            self._pending = None
            self._condition.notify()

    def run(self) -> None:
        try:
            detector = Detector(
                self._models.detector_model,
                self._models.detector_metadata,
                self._processor,
            )
            cell_classifier = self._classifier(
                self._models.cell_model,
                self._models.cell_metadata,
                _CELL_THRESHOLDS,
            )
            flag_classifier = self._classifier(
                self._models.flag_model,
                self._models.flag_metadata,
                _FLAG_THRESHOLDS,
            )
            slot_classifier = self._classifier(
                self._models.slot_model,
                self._models.slot_metadata,
                _SLOT_THRESHOLDS,
            )
        except Exception as error:
            self.errorRaised.emit(f"识别模型初始化失败: {error}")
            return

        processors = {
            detector.processor,
            cell_classifier.processor,
            flag_classifier.processor,
            slot_classifier.processor,
        }
        self.processorChanged.emit(
            processors.pop() if len(processors) == 1 else "mixed"
        )

        while True:
            with self._condition:
                while self._pending is None and not self._stopping:
                    self._condition.wait()
                if self._stopping:
                    return
                frame_number, image, rect = self._pending
                self._pending = None

            try:
                snapshot = self._recognize(
                    frame_number,
                    image,
                    rect,
                    detector,
                    cell_classifier,
                    flag_classifier,
                    slot_classifier,
                )
                if snapshot is not None:
                    self.snapshotReady.emit(snapshot_to_qml(snapshot))
            except Exception as error:
                self.errorRaised.emit(f"第 {frame_number} 帧: {error}")

    def _classifier(
        self,
        model_path: Path,
        metadata_path: Path,
        thresholds: DecisionThresholds,
    ) -> Classifier:
        return Classifier(
            model_path,
            metadata_path,
            self._processor,
            confidence_threshold=thresholds.confidence,
            margin_threshold=thresholds.margin,
        )

    def _recognize(
        self,
        frame_number: int,
        image: QImage,
        rect: dict[str, int],
        detector: Detector,
        cell_classifier: Classifier,
        flag_classifier: Classifier,
        slot_classifier: Classifier,
    ) -> RecognitionSnapshot | None:
        """执行一次完整识别；画面不可用时返回 None。"""
        started_at = time.perf_counter()
        detection_started_at = time.perf_counter()
        detection = detector.detect(image)
        detection_ms = _elapsed_ms(detection_started_at)
        if detection is None:
            return None

        minefield_box = _expand_box(
            detection.minefield,
            image.width(),
            image.height(),
            fraction=0.01,
        )
        # 向外轻微外扩，保证边缘格子完整包含在裁图中。
        minefield_rect = _box_to_rect(
            minefield_box,
            image.width(),
            image.height(),
        )
        minefield = image.copy(minefield_rect)
        counter_images = tuple(
            image.copy(_box_to_rect(box, image.width(), image.height()))
            for box in detection.remaining_counters
        )

        grid_started_at = time.perf_counter()
        grid = detect_grid(minefield)
        grid_ms = _elapsed_ms(grid_started_at)
        if grid is None:
            return None

        cell_images: list[QImage] = []
        for row in range(grid.rows):
            for column in range(grid.columns):
                cell_images.append(minefield.copy(grid.cell_rect(row, column)))

        if self._debug_writer.is_enabled():
            self._debug_writer.submit(
                DebugFrame(
                    minefield=minefield,
                    counters=counter_images,
                    cells=tuple(cell_images),
                    rows=grid.rows,
                    columns=grid.columns,
                )
            )

        cells_started_at = time.perf_counter()
        cell_predictions = cell_classifier.predict(cell_images)
        cells_ms = _elapsed_ms(cells_started_at)
        cells = tuple(
            CellRecognition(
                row=index // grid.columns,
                column=index % grid.columns,
                classification=prediction,
            )
            for index, prediction in enumerate(cell_predictions)
        )

        counters_started_at = time.perf_counter()
        counters = self._recognize_counters(
            detection,
            counter_images,
            flag_classifier,
            slot_classifier,
        )
        counters_ms = _elapsed_ms(counters_started_at)
        total_ms = _elapsed_ms(started_at)
        board_key = make_board_key(grid.rows, grid.columns, cells, counters)
        # 归一化边界让提示层随蒙版窗口移动/缩放；像素坐标会立即失效。
        column_edges = tuple(
            min(
                1.0,
                max(0.0, (minefield_rect.x() + edge) / image.width()),
            )
            for edge in grid.x_lines
        )
        row_edges = tuple(
            min(
                1.0,
                max(0.0, (minefield_rect.y() + edge) / image.height()),
            )
            for edge in grid.y_lines
        )

        return RecognitionSnapshot(
            frame_number=frame_number,
            board_key=board_key,
            captured_at=time.time(),
            capture_rect=dict(rect),
            provider=detector.processor,
            rows=grid.rows,
            columns=grid.columns,
            column_edges=column_edges,
            row_edges=row_edges,
            cells=cells,
            counters=counters,
            timings_ms={
                "detection": detection_ms,
                "grid": grid_ms,
                "cells": cells_ms,
                "counters": counters_ms,
                "total": total_ms,
            },
            thresholds=_threshold_map(),
            threshold_version=_THRESHOLD_VERSION,
        )

    @staticmethod
    def _recognize_counters(
        detection: DetectionResult,
        images: tuple[QImage, ...],
        flag_classifier: Classifier,
        slot_classifier: Classifier,
    ) -> tuple[CounterRecognition, ...]:
        """识别四个余雷区，容忍单个切分失败。"""
        parts = []
        for image in images:
            try:
                parts.append(split_counter(image))
            except ValueError:
                # 单个 LED 切分失败时退化为 UNKNOWN 槽位，
                # 而不是丢弃整个快照。
                parts.append(None)

        valid_flag_indexes = [
            index for index, item in enumerate(parts) if item is not None
        ]
        flag_predictions = flag_classifier.predict(
            [parts[index].flag for index in valid_flag_indexes]
        )
        flags = {
            index: prediction
            for index, prediction in zip(
                valid_flag_indexes,
                flag_predictions,
                strict=True,
            )
        }

        slot_images: list[QImage] = []
        slot_owners: list[tuple[int, int]] = []
        for index, item in enumerate(parts):
            if item is None:
                continue
            for slot_index, image in enumerate(item.slots):
                slot_images.append(image)
                slot_owners.append((index, slot_index))
        slot_predictions = slot_classifier.predict(slot_images)
        slots_by_counter: dict[int, list[Classification]] = {
            index: [] for index in valid_flag_indexes
        }
        for (counter_index, _), prediction in zip(
            slot_owners,
            slot_predictions,
            strict=True,
        ):
            slots_by_counter[counter_index].append(prediction)

        counters: list[CounterRecognition] = []
        for index, box in enumerate(detection.remaining_counters):
            counters.append(
                CounterRecognition(
                    position=index + 1,
                    box=_box_dict(box),
                    flag=flags.get(index),
                    slots=tuple(slots_by_counter.get(index, [_UNKNOWN] * 4)),
                )
            )
        return tuple(counters)


class RecognitionService(QObject):
    """面向 QML 的服务，持有识别工作线程与调试写入器。"""

    snapshotReady = Signal(object)
    processorChanged = Signal(str)
    errorRaised = Signal(str)

    def __init__(
        self,
        models: RecognitionModels,
        output_dir: Path,
        processor: str = "auto",
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._models = models
        self._processor = processor
        self._thread: _RecognitionThread | None = None
        self._debug_writer = DebugWriter(output_dir, self._on_error)

    @Slot()
    def start(self) -> None:
        if self._thread is not None and self._thread.isRunning():
            return

        thread = _RecognitionThread(
            self._models,
            self._processor,
            self._debug_writer,
            self,
        )
        thread.snapshotReady.connect(self.snapshotReady)
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
            # 会话无法在线切换 Provider；重启工作线程，
            # 让四个模型在新 Provider 上重建。
            self.stop_thread()
            self.start()

    @Slot(bool)
    def set_developer_mode(self, enabled: bool) -> None:
        self._debug_writer.set_enabled(enabled)

    @Slot(int, QImage, object)
    def submit_frame(
        self,
        frame_number: int,
        image: QImage,
        rect: object,
    ) -> None:
        if self._thread is None or not self._thread.isRunning():
            return
        if not isinstance(rect, dict):
            return
        self._thread.submit(frame_number, image, rect)

    @Slot()
    def stop_thread(self) -> None:
        thread = self._thread
        if thread is None:
            return

        self._thread = None
        thread.stop()
        if not thread.wait(15000):
            self.errorRaised.emit("识别线程未能在时限内停止")

    @Slot()
    def stop(self) -> None:
        self.stop_thread()
        self._debug_writer.stop()

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


def _box_dict(box: Box) -> dict[str, float]:
    return {
        "x1": box.x1,
        "y1": box.y1,
        "x2": box.x2,
        "y2": box.y2,
        "confidence": box.confidence,
    }


def _elapsed_ms(started_at: float) -> float:
    return (time.perf_counter() - started_at) * 1000.0


def _threshold_map() -> dict[str, dict[str, float]]:
    return {
        name: {
            "confidence": thresholds.confidence,
            "margin": thresholds.margin,
        }
        for name, thresholds in (
            ("cell", _CELL_THRESHOLDS),
            ("flag", _FLAG_THRESHOLDS),
            ("slot", _SLOT_THRESHOLDS),
        )
    }
