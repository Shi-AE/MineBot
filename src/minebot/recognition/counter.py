from dataclasses import dataclass

import numpy as np
from PySide6.QtGui import QImage

from ..constants import SLOT_COUNT


@dataclass(frozen=True)
class CounterParts:
    """旗帜图像与四个固定 LED 槽位裁图。"""

    flag: QImage
    slots: tuple[QImage, ...]


def split_counter(image: QImage) -> CounterParts:
    """把余雷区裁图切分为旗帜区域和四个 LED 槽位。

    LED 面板由暗色背景与红色 LED 字形共同确定；仅凭暗色会误匹配旗帜区域。
    """
    rgb = _qimage_to_rgb(image)
    red = rgb[:, :, 0]
    green = rgb[:, :, 1]
    blue = rgb[:, :, 2]
    dark = rgb.max(axis=2) < 70
    red_led = (red > 60) & (red > green * 1.4) & (red > blue * 1.4)
    panel = dark | red_led

    column_coverage = panel.mean(axis=0)
    # LED 面板至少占裁图宽度的四分之一，而旗帜图标达不到该宽度。
    minimum_width = max(12, image.width() // 4)
    runs: list[tuple[int, int]] = []
    start: int | None = None
    for column, covered in enumerate(column_coverage >= 0.65):
        if covered and start is None:
            start = column
        if start is not None and (
            not covered or column == len(column_coverage) - 1
        ):
            end = (
                column
                if covered and column == len(column_coverage) - 1
                else column - 1
            )
            if end - start + 1 >= minimum_width:
                runs.append((start, end))
            start = None
    if not runs:
        raise ValueError("无法检测 LED 显示面板")

    left, right = max(runs, key=lambda run: (run[1] - run[0], run[1]))
    rows = np.flatnonzero(panel[:, left : right + 1].mean(axis=1) >= 0.55)
    if rows.size == 0:
        raise ValueError("无法检测 LED 显示行范围")
    top, bottom = int(rows.min()), int(rows.max())
    if left < image.width() // 5:
        raise ValueError("LED 面板宽度异常")

    boundaries = [
        left + round(index * (right - left + 1) / SLOT_COUNT)
        for index in range(SLOT_COUNT + 1)
    ]
    slots = tuple(
        _rgb_to_qimage(rgb[top : bottom + 1, boundaries[index] : boundaries[index + 1]])
        for index in range(SLOT_COUNT)
    )
    return CounterParts(
        flag=_rgb_to_qimage(rgb[:, :left]),
        slots=slots,
    )


def _qimage_to_rgb(image: QImage) -> np.ndarray:
    rgb_image = image.convertToFormat(QImage.Format.Format_RGB888)
    width = rgb_image.width()
    height = rgb_image.height()
    raw = np.frombuffer(
        rgb_image.constBits(),
        dtype=np.uint8,
        count=rgb_image.sizeInBytes(),
    ).reshape(height, rgb_image.bytesPerLine())
    return raw[:, : width * 3].reshape(height, width, 3).copy()


def _rgb_to_qimage(rgb: np.ndarray) -> QImage:
    contiguous = np.ascontiguousarray(rgb)
    height, width, _ = contiguous.shape
    return QImage(
        contiguous.data,
        width,
        height,
        width * 3,
        QImage.Format.Format_RGB888,
    ).copy()
