import shutil
import sys
import time
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage


class ConsolePreview:
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
        now = time.monotonic()
        if frame_number > 1 and now - self._last_preview_at < 0.5:
            return

        self._last_preview_at = now
        self._print_frame(frame_number, image, rect)

    def handle_error(self, message: str) -> None:
        print(f"[capture] error: {message}", file=sys.stderr, flush=True)

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
            f"[frame {frame_number:05d}] "
            f"rect=({rect['left']},{rect['top']},{rect['width']},{rect['height']}) "
            f"mean=({mean.red()},{mean.green()},{mean.blue()}) "
            f"fps={self._frequency:.2f} cache={self._cache_path}"
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
