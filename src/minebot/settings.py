import configparser
import math
import re
import sys
from pathlib import Path

from PySide6.QtCore import (
    QIODevice,
    QObject,
    Property,
    QSaveFile,
    QStandardPaths,
    Signal,
    Slot,
)

from .processors import detect_processor_options

_COLOR_ENTRIES = (
    ("Accent", "#4BD4DE", "主强调色，用于按钮、选中状态和焦点强调。"),
    ("AccentText", "#08282A", "强调色按钮上的文字颜色，应注意与 Accent 保持对比度。"),
    ("PageBackground", "#091118", "窗口最底层背景色。"),
    ("AppBackground", "#0E171F", "主内容区背景色。"),
    ("Surface", "#111C25", "卡片和普通控件表面颜色。"),
    ("SurfaceAlt", "#0C161D", "次级表面、输入框和空状态背景色。"),
    ("SidebarTop", "#12303D", "左侧导航栏顶部渐变颜色。"),
    ("SidebarBottom", "#08151D", "左侧导航栏底部渐变颜色。"),
    ("Border", "#223641", "普通边框和分隔线颜色。"),
    ("BorderStrong", "#34505E", "强调边框和悬停边框颜色。"),
    ("TextPrimary", "#EEF7FA", "主要文字颜色。"),
    ("TextMuted", "#91A7B2", "次要文字和说明文字颜色。"),
    ("TextFaint", "#657B87", "弱提示、单位与时间戳颜色。"),
    ("Danger", "#FF7F89", "错误、停止和危险操作颜色。"),
    ("DangerSoft", "#3A1D23", "危险操作的浅色背景。"),
    ("Success", "#56D7BD", "连接成功和正常运行状态颜色。"),
    ("Warning", "#F1B95E", "等待和功能未接入状态颜色。"),
)

_GENERAL_ENTRIES = (
    ("WindowAlwaysOnTop", True, "运行时将控制台窗口保持在其他窗口上方。"),
    ("PreserveDashboard", True, "结束任务后保留数据看板中的本次任务内容。"),
    ("RegionMaskVisible", True, "显示扫雷区域蒙版。"),
    ("DeveloperMode", False, "Asynchronously save recognition crops for development."),
)

_DEFAULT_MASK_OPACITY = 0.5
_DEFAULT_CAPTURE_FREQUENCY = 2.0
_MIN_CAPTURE_FREQUENCY = 0.1
_MAX_CAPTURE_FREQUENCY = 10.0
_HEX_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")


class AppSettings(QObject):
    colorsChanged = Signal()
    generalChanged = Signal()
    maskOpacityChanged = Signal()
    captureFrequencyChanged = Signal()
    detectorProcessorChanged = Signal()
    activeProcessorChanged = Signal()

    def __init__(self, config_path: Path | None = None, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._path = config_path or self._default_path()
        self._colors = {key: value for key, value, _ in _COLOR_ENTRIES}
        self._general = {key: value for key, value, _ in _GENERAL_ENTRIES}
        self._mask_opacity = _DEFAULT_MASK_OPACITY
        self._capture_frequency = _DEFAULT_CAPTURE_FREQUENCY
        self._processor_options = detect_processor_options()
        self._selected_processor = "auto"
        self._active_processor_value = ""
        self._active_processor_label = "等待识别服务"

        if self._path.is_file():
            self._load()
        else:
            self._save()

    @staticmethod
    def _default_path() -> Path:
        config_directory = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppConfigLocation
        )
        return Path(config_directory) / "settings.ini"

    @Property("QVariantMap", notify=colorsChanged)
    def colors(self) -> dict[str, str]:
        return dict(self._colors)

    @Property("QVariantMap", notify=generalChanged)
    def general(self) -> dict[str, bool]:
        return dict(self._general)

    @Property(float, notify=maskOpacityChanged)
    def region_mask_opacity(self) -> float:
        return self._mask_opacity

    @Property(float, notify=captureFrequencyChanged)
    def capture_frequency(self) -> float:
        return self._capture_frequency

    @Property("QVariantList", notify=detectorProcessorChanged)
    def processor_options(self) -> list[dict[str, object]]:
        return [dict(option) for option in self._processor_options]

    @Property(str, notify=detectorProcessorChanged)
    def selected_processor(self) -> str:
        return self._selected_processor

    @Property(str, notify=activeProcessorChanged)
    def active_processor_label(self) -> str:
        return self._active_processor_label

    @Property(str, constant=True)
    def config_path(self) -> str:
        return str(self._path)

    @Property(str, constant=True)
    def capture_cache_path(self) -> str:
        cache_directory = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.CacheLocation
        )
        return str(Path(cache_directory) / "captures" / "latest.png")

    @Slot(str, str)
    def set_color(self, key: str, value: str) -> None:
        if key not in self._colors or _HEX_COLOR.fullmatch(value) is None:
            return

        normalized = value.upper()
        if self._colors[key] == normalized:
            return

        self._colors[key] = normalized
        self._save()
        self.colorsChanged.emit()

    @Slot(str, bool)
    def set_general(self, key: str, value: bool) -> None:
        if key not in self._general or self._general[key] == value:
            return

        self._general[key] = value
        self._save()
        self.generalChanged.emit()

    @Slot(float)
    def set_region_mask_opacity(self, value: float) -> None:
        normalized = min(max(value, 0.0), 1.0)
        if abs(self._mask_opacity - normalized) < 0.0001:
            return

        self._mask_opacity = normalized
        self._save()
        self.maskOpacityChanged.emit()

    @Slot(float)
    def set_capture_frequency(self, value: float) -> None:
        if not math.isfinite(value):
            return
        normalized = min(
            max(round(value, 2), _MIN_CAPTURE_FREQUENCY),
            _MAX_CAPTURE_FREQUENCY,
        )
        if abs(self._capture_frequency - normalized) < 0.0001:
            return

        self._capture_frequency = normalized
        self._save()
        self.captureFrequencyChanged.emit()

    @Slot(str)
    def set_detector_processor(self, value: str) -> None:
        if value not in self._processor_values():
            return
        if self._selected_processor == value:
            return

        self._selected_processor = value
        self._active_processor_label = "正在切换处理器"
        self._save()
        self.detectorProcessorChanged.emit()
        self.activeProcessorChanged.emit()

    @Slot(str)
    def set_active_processor(self, value: str) -> None:
        label = next(
            (
                str(option["label"])
                for option in self._processor_options
                if option["value"] == value
            ),
            value,
        )
        if (
            value == self._active_processor_value
            and label == self._active_processor_label
        ):
            return

        self._active_processor_value = value
        self._active_processor_label = label
        self.activeProcessorChanged.emit()

    def _processor_values(self) -> set[str]:
        return {str(option["value"]) for option in self._processor_options}

    def _load(self) -> None:
        parser = configparser.ConfigParser(interpolation=None)
        parser.optionxform = str
        try:
            parser.read(self._path, encoding="utf-8")
        except (OSError, configparser.Error):
            return

        for key, default, _ in _COLOR_ENTRIES:
            value = parser.get("colors", key, fallback=default)
            self._colors[key] = value.upper() if _HEX_COLOR.fullmatch(value) else default

        for key, default, _ in _GENERAL_ENTRIES:
            try:
                self._general[key] = parser.getboolean("general", key, fallback=default)
            except ValueError:
                self._general[key] = default

        try:
            opacity = parser.getfloat(
                "general", "RegionMaskOpacity", fallback=_DEFAULT_MASK_OPACITY
            )
            self._mask_opacity = min(max(opacity, 0.0), 1.0)
        except ValueError:
            self._mask_opacity = _DEFAULT_MASK_OPACITY

        try:
            frequency = parser.getfloat(
                "general",
                "CaptureFrequency",
                fallback=_DEFAULT_CAPTURE_FREQUENCY,
            )
            if not math.isfinite(frequency):
                frequency = _DEFAULT_CAPTURE_FREQUENCY
            self._capture_frequency = min(
                max(round(frequency, 2), _MIN_CAPTURE_FREQUENCY),
                _MAX_CAPTURE_FREQUENCY,
            )
        except ValueError:
            self._capture_frequency = _DEFAULT_CAPTURE_FREQUENCY

        processor = parser.get("general", "DetectionProcessor", fallback="auto")
        if processor not in self._processor_values():
            processor = "auto"
        self._selected_processor = processor

    def _save(self) -> None:
        content = [
            "# MineBot 用户配置",
            "# 界面内修改会立即保存；手动修改后请重启 MineBot 生效。",
            "# 颜色格式为 #RRGGBB，缺失或非法值会回退到内置默认色。",
            "",
            "[colors]",
        ]

        for key, _, description in _COLOR_ENTRIES:
            content.extend((f"# {description}", f"{key}={self._colors[key]}"))

        content.extend(("", "[general]"))
        for key, _, description in _GENERAL_ENTRIES:
            value = "true" if self._general[key] else "false"
            content.extend((f"# {description}", f"{key}={value}"))

        content.extend(
            (
                "# 扫雷区域蒙版不透明度，范围 0.0 到 1.0。",
                f"RegionMaskOpacity={self._mask_opacity:.2f}",
                "# 捕获频率，单位 FPS，范围 0.1 到 10.0。",
                f"CaptureFrequency={self._capture_frequency:.2f}",
                "# Detector processor: auto, cpu, or cuda:<GPU index>.",
                f"DetectionProcessor={self._selected_processor}",
            )
        )

        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            save_file = QSaveFile(str(self._path))
            if not save_file.open(QIODevice.OpenModeFlag.WriteOnly):
                raise OSError(save_file.errorString())
            save_file.write(("\n".join(content) + "\n").encode("utf-8"))
            if not save_file.commit():
                raise OSError(save_file.errorString())
        except OSError as error:
            print(f"无法保存配置 {self._path}: {error}", file=sys.stderr)
