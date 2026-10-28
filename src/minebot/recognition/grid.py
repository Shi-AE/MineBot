from dataclasses import dataclass

import cv2
import numpy as np
from PySide6.QtCore import QRect
from PySide6.QtGui import QImage


@dataclass(frozen=True)
class Grid:
    """雷区裁图像素坐标系下的网格线位置。"""

    x_lines: tuple[int, ...]
    y_lines: tuple[int, ...]

    @property
    def columns(self) -> int:
        return len(self.x_lines) - 1

    @property
    def rows(self) -> int:
        return len(self.y_lines) - 1

    def cell_rect(self, row: int, column: int) -> QRect:
        if not 0 <= row < self.rows or not 0 <= column < self.columns:
            raise IndexError(f"格子越界: 行={row}, 列={column}")
        x1 = self.x_lines[column]
        x2 = self.x_lines[column + 1]
        y1 = self.y_lines[row]
        y2 = self.y_lines[row + 1]
        return QRect(x1, y1, x2 - x1, y2 - y1)


def detect_grid(image: QImage) -> Grid | None:
    """基于 Sobel 边缘投影检测行列分隔线。"""
    if image.isNull() or image.width() < 16 or image.height() < 16:
        return None

    gray_image = image.convertToFormat(QImage.Format.Format_Grayscale8)
    raw = np.frombuffer(
        gray_image.constBits(),
        dtype=np.uint8,
        count=gray_image.sizeInBytes(),
    ).reshape(gray_image.height(), gray_image.bytesPerLine())
    gray = raw[:, : gray_image.width()].copy()

    horizontal_edges = np.abs(cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3))
    vertical_edges = np.abs(cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3))
    x_lines = _detect_lines(horizontal_edges.mean(axis=0))
    y_lines = _detect_lines(vertical_edges.mean(axis=1))
    if x_lines is None or y_lines is None:
        return None
    return Grid(x_lines, y_lines)


def _detect_lines(profile: np.ndarray) -> tuple[int, ...] | None:
    if profile.size < 32:
        return None

    smoothed = np.convolve(profile, np.ones(3) / 3, mode="same")
    pitch = _detect_pitch(smoothed)
    if pitch is None:
        return None

    offsets = range(min(pitch, smoothed.size))
    offset = max(
        offsets,
        key=lambda candidate: float(smoothed[candidate::pitch].mean()),
    )
    # 把每条预期线吸附到容差内最强的边缘，避免格距漂移在整行累积。
    tolerance = max(2, pitch // 5)
    lines: list[int] = []
    for expected in range(offset, smoothed.size, pitch):
        lower = max(0, expected - tolerance)
        upper = min(smoothed.size, expected + tolerance + 1)
        lines.append(lower + int(np.argmax(smoothed[lower:upper])))

    if len(lines) < 3:
        return None

    differences = np.diff(lines)
    # 拒绝间距不合理或不稳定的投影。
    if np.median(differences) < 12:
        return None
    if np.mean(np.abs(differences - pitch) <= 2) < 0.8:
        return None
    return tuple(lines)


def _detect_pitch(profile: np.ndarray) -> int | None:
    centered = profile - profile.mean()
    maximum = min(64, profile.size // 3)
    scores: list[float] = []
    for lag in range(12, maximum + 1):
        left = centered[:-lag]
        right = centered[lag:]
        denominator = float(np.linalg.norm(left) * np.linalg.norm(right))
        scores.append(
            float(np.dot(left, right) / denominator) if denominator else 0.0
        )
    if not scores:
        return None
    best = max(scores)
    candidates = [
        index
        for index, score in enumerate(scores)
        if score >= best * 0.98
    ]
    return 12 + candidates[0]
