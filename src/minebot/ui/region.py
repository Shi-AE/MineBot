from PySide6.QtCore import QMetaObject, QObject, QRect, QTimer, Signal, Slot
from PySide6.QtGui import QGuiApplication, QRegion, QWindow
from PySide6.QtQml import QQmlComponent


class RegionWindowController(QObject):
    """持有框选外框/蒙版窗口，并发布它们的 HWND。"""

    regionShown = Signal(int, int)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._component: QQmlComponent | None = None
        self._region_mask: QObject | None = None
        self._shown = False

    @Slot(QObject, int)
    def apply_frame_region(self, window: QObject, edge_size: int) -> None:
        if not isinstance(window, QWindow):
            return

        width = window.width()
        height = window.height()
        edge = max(1, min(edge_size, width // 2, height // 2))
        # 蒙版只保留边框可见：外框可点击拖动，中心透明露出游戏画面。
        if edge <= 0:
            return

        region = QRegion(QRect(0, 0, width, edge))
        region = region.united(QRegion(QRect(0, height - edge, width, edge)))
        region = region.united(QRegion(QRect(0, edge, edge, height - edge * 2)))
        region = region.united(
            QRegion(QRect(width - edge, edge, edge, height - edge * 2))
        )
        window.setMask(region)

    def set_region_mask(
            self, component: QQmlComponent, region_mask: QObject
    ) -> None:
        self._component = component
        self._region_mask = region_mask

    @Slot()
    def show_region_mask(self) -> None:
        if self._region_mask is None:
            return

        self._shown = True
        QMetaObject.invokeMethod(self._region_mask, "open")
        QTimer.singleShot(120, self._publish_capture_target)

    @Slot()
    def hide_region_mask(self) -> None:
        self._shown = False
        if self._region_mask is not None:
            QMetaObject.invokeMethod(self._region_mask, "closeMask")

    @Slot()
    def _publish_capture_target(self) -> None:
        if not self._shown:
            return

        windows = {
            window.objectName(): window
            for window in QGuiApplication.topLevelWindows()
        }
        # 窗口显示后 winId() 才稳定；短暂延迟等待 QML 完成创建，再启动捕获。
        try:
            frame_window = windows["frameWindow"]
            mask_window = windows["maskWindow"]
            self.regionShown.emit(
                int(frame_window.winId()),
                int(mask_window.winId()),
            )
        except KeyError as error:
            print(
                f"[ui] region window not found: {error.args[0]}",
                flush=True,
            )
