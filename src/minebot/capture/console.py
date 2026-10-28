import shutil
import sys
import time
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage


class ConsolePreview:
    """带限速的终端帧预览。"""

    def __init__(self, cache_path: Path, frequency: float) -> None:
        self._frequency = frequency
        self._cache_path = cache_path
        self._last_preview_at = 0.0

    def set_frequency(self, frequency: float) -> None:
        self._frequency = frequency

    def handle_frame(
        self,
        frame_number: int,
        image: QImage,
        rect: dict[str, int],
    ) -> None:
        # 帧率高于 2 FPS 时跳过完整 ANSI 重绘。
        now = time.monotonic()
        if frame_number > 1 and now - self._last_preview_at < 0.5:
            return

        self._last_preview_at = now
        self._print_frame(frame_number, image, rect)

    def handle_error(self, message: str) -> None:
        print(f"[捕获] 错误: {message}", file=sys.stderr, flush=True)

    def _print_frame(
        self,
        frame_number: int,
        image: QImage,
        rect: dict[str, int],
    ) -> None:
        mean = image.scaled(
            1,
            1,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        ).pixelColor(0, 0)
        header = (
            f"[帧 {frame_number:05d}] "
            f"区域=({rect['left']},{rect['top']},{rect['width']},{rect['height']}) "
            f"均值=({mean.red()},{mean.green()},{mean.blue()}) "
            f"FPS={self._frequency:.2f} 缓存={self._cache_path}"
        )

        if not sys.stdout.isatty():
            print(header, flush=True)
            return

        terminal = shutil.get_terminal_size(fallback=(80, 24))
        columns = max(20, min(96, terminal.columns - 2))
        rows = max(1, round(columns * image.height() / (2 * image.width())))
        max_rows = max(1, terminal.lines - 4)
        if rows > max_rows:
            columns = max(10, round(columns * max_rows / rows))
            rows = max_rows

        preview = image.scaled(
            columns,
            rows * 2,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        lines = ["\x1b[2J\x1b[H", header, ""]
        for y in range(0, rows * 2, 2):
            line = []
            for x in range(columns):
                top = preview.pixelColor(x, y)
                bottom = preview.pixelColor(x, y + 1)
                line.append(
                    f"\x1b[38;2;{top.red()};{top.green()};{top.blue()}m"
                    f"\x1b[48;2;{bottom.red()};{bottom.green()};{bottom.blue()}m"
                    "▀"
                )
            lines.append("".join(line) + "\x1b[0m")

        print("\n".join(lines), flush=True)
