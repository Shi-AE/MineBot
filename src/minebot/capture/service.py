import threading
import time
from dataclasses import dataclass
from pathlib import Path

import mss
from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtGui import QImage

from .windows import exclude_from_capture, window_rect


@dataclass(frozen=True)
class CaptureTarget:
    frame_hwnd: int
    mask_hwnd: int


class _CaptureThread(QThread):
    frameCaptured = Signal(int, QImage, object)
    errorRaised = Signal(str)

    def __init__(
        self,
        mask_hwnd: int,
        frequency: float,
        cache_path: Path,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._mask_hwnd = mask_hwnd
        self._interval = 1.0 / frequency
        self._cache_path = cache_path
        self._stop_event = threading.Event()

    def stop(self) -> None:
        self._stop_event.set()

    def run(self) -> None:
        try:
            self._cache_path.parent.mkdir(parents=True, exist_ok=True)
            with mss.mss() as capture:
                frame_number = 0
                while not self._stop_event.is_set():
                    started_at = time.monotonic()
                    rect = window_rect(self._mask_hwnd)
                    shot = capture.grab(rect)
                    image = QImage(
                        shot.bgra,
                        shot.width,
                        shot.height,
                        shot.width * 4,
                        QImage.Format.Format_RGB32,
                    ).copy()

                    if not image.save(str(self._cache_path), "PNG"):
                        raise OSError(f"failed to save capture: {self._cache_path}")

                    frame_number += 1
                    self.frameCaptured.emit(frame_number, image, rect)
                    wait_time = self._interval - (time.monotonic() - started_at)
                    if wait_time > 0:
                        self._stop_event.wait(wait_time)
        except Exception as error:
            self.errorRaised.emit(str(error))


class CaptureService(QObject):
    frameCaptured = Signal(int, QImage, object)
    errorRaised = Signal(str)

    def __init__(
        self,
        cache_path: Path,
        frequency: float,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._cache_path = cache_path
        self._frequency = frequency
        self._capture_thread: _CaptureThread | None = None
        self._active_target: CaptureTarget | None = None

    @Slot(object)
    def start(self, target: CaptureTarget) -> None:
        if not isinstance(target, CaptureTarget):
            self.errorRaised.emit("CaptureService.start requires CaptureTarget")
            return

        self.stop()
        try:
            exclude_from_capture(target.frame_hwnd)
            exclude_from_capture(target.mask_hwnd)
            window_rect(target.mask_hwnd)
        except (OSError, RuntimeError) as error:
            self.errorRaised.emit(str(error))
            return

        thread = _CaptureThread(
            target.mask_hwnd,
            self._frequency,
            self._cache_path,
            self,
        )
        thread.frameCaptured.connect(self.frameCaptured)
        thread.errorRaised.connect(self._on_error)
        thread.finished.connect(lambda: self._capture_finished(thread))
        thread.finished.connect(thread.deleteLater)
        self._capture_thread = thread
        self._active_target = target
        thread.start()

    @Slot()
    def stop(self) -> None:
        self._active_target = None
        thread = self._capture_thread
        if thread is None:
            return

        self._capture_thread = None
        thread.stop()
        if not thread.wait(1500):
            self.errorRaised.emit("capture worker did not stop within 1.5 seconds")

    @Slot(float)
    def set_frequency(self, frequency: float) -> None:
        self._frequency = frequency
        target = self._active_target
        if target is None or self._capture_thread is None:
            return
        self.start(target)

    def _capture_finished(self, thread: _CaptureThread) -> None:
        if self._capture_thread is thread:
            self._capture_thread = None
            self._active_target = None

    @Slot(str)
    def _on_error(self, message: str) -> None:
        self.errorRaised.emit(message)
