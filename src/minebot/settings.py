import configparser
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
)

_HEX_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")


class AppSettings(QObject):
    colorsChanged = Signal()
    generalChanged = Signal()

    def __init__(self, config_path: Path | None = None, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._path = config_path or self._default_path()
        self._colors = {key: value for key, value, _ in _COLOR_ENTRIES}
        self._general = {key: value for key, value, _ in _GENERAL_ENTRIES}

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

    @Property(str, constant=True)
    def config_path(self) -> str:
        return str(self._path)

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
