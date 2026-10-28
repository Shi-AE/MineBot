import os
import threading
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtGui import QImage


@dataclass(frozen=True)
class DebugFrame:
    """开发者模式开启时需要保存的裁图。"""

    minefield: QImage
    counters: tuple[QImage, ...]
    cells: tuple[QImage, ...]
    rows: int
    columns: int


class DebugWriter:
    """后台写入器，只保留最新一帧调试数据。

    识别线程提交后立即返回；单一待写槽位使磁盘延迟不影响识别。
    """

    def __init__(
        self,
        output_dir: Path,
        on_error,
    ) -> None:
        self._output_dir = output_dir
        self._on_error = on_error
        self._condition = threading.Condition()
        self._pending: DebugFrame | None = None
        self._enabled = False
        self._stopping = False
        self._thread = threading.Thread(
            target=self._run,
            name="minebot-debug-writer",
            daemon=True,
        )
        self._thread.start()

    def set_enabled(self, enabled: bool) -> None:
        with self._condition:
            self._enabled = enabled
            if not enabled:
                self._pending = None

    def is_enabled(self) -> bool:
        with self._condition:
            return self._enabled and not self._stopping

    def submit(self, frame: DebugFrame) -> None:
        with self._condition:
            if not self._enabled or self._stopping:
                return
            self._pending = frame
            self._condition.notify()

    def stop(self) -> None:
        with self._condition:
            self._stopping = True
            self._pending = None
            self._condition.notify()
        self._thread.join(timeout=2.0)

    def _run(self) -> None:
        while True:
            with self._condition:
                while self._pending is None and not self._stopping:
                    self._condition.wait()
                if self._stopping:
                    return
                frame = self._pending
                self._pending = None
            try:
                self._write(frame)
            except Exception as error:
                self._on_error(f"保存开发者截图失败: {error}")

    def _write(self, frame: DebugFrame) -> None:
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._save_atomic(frame.minefield, self._output_dir / "minefield.png")
        expected_counters = set()
        for index, image in enumerate(frame.counters, start=1):
            name = f"counter_{index}.png"
            expected_counters.add(name)
            self._save_atomic(image, self._output_dir / name)
        for stale in self._output_dir.glob("counter_*.png"):
            if stale.name not in expected_counters:
                stale.unlink(missing_ok=True)

        cells_dir = self._output_dir / "cells"
        cells_dir.mkdir(parents=True, exist_ok=True)
        expected_cells = set()
        for index, image in enumerate(frame.cells):
            row, column = divmod(index, frame.columns)
            name = f"row_{row + 1:03d}_col_{column + 1:03d}.png"
            expected_cells.add(name)
            self._save_atomic(image, cells_dir / name)
        for stale in cells_dir.glob("row_*_col_*.png"):
            if stale.name not in expected_cells:
                stale.unlink(missing_ok=True)

    @staticmethod
    def _save_atomic(image: QImage, target: Path) -> None:
        # 先写入隐藏临时文件，读取方不会看到损坏的 PNG。
        temporary = target.with_name(f".{target.name}.tmp")
        if not image.save(str(temporary), "PNG"):
            raise OSError(f"保存失败: {temporary}")
        os.replace(temporary, target)
