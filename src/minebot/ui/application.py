import sys
from pathlib import Path

from PySide6.QtCore import QMetaObject, QObject, QRect, QUrl, Slot
from PySide6.QtGui import QGuiApplication, QRegion, QWindow
from PySide6.QtQml import QQmlApplicationEngine, QQmlComponent
from PySide6.QtQuickControls2 import QQuickStyle


class RegionWindowController(QObject):
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._component: QQmlComponent | None = None
        self._region_mask: QObject | None = None

    @Slot(QObject, int)
    def apply_frame_region(self, window: QObject, edge_size: int) -> None:
        if not isinstance(window, QWindow):
            return

        width = window.width()
        height = window.height()
        edge = max(1, min(edge_size, width // 2, height // 2))
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
        if self._region_mask is not None:
            QMetaObject.invokeMethod(self._region_mask, "open")

    @Slot()
    def hide_region_mask(self) -> None:
        if self._region_mask is not None:
            QMetaObject.invokeMethod(self._region_mask, "closeMask")


def run_application(app: QGuiApplication, settings: QObject) -> int:
    QQuickStyle.setStyle("Basic")

    qml_file = Path(__file__).resolve().parent / "Main.qml"
    if not qml_file.is_file():
        print(f"QML 文件未找到: {qml_file}", file=sys.stderr)
        return 1

    engine = QQmlApplicationEngine(app)
    region_window_controller = RegionWindowController(engine)
    engine.setInitialProperties({"appSettings": settings})
    engine.load(qml_file.as_uri())
    if not engine.rootObjects():
        return 1

    region_mask_file = qml_file.parent / "components" / "RegionMask.qml"
    component = QQmlComponent(engine, QUrl.fromLocalFile(str(region_mask_file)))
    if component.isError():
        for error in component.errors():
            print(error.toString(), file=sys.stderr)
        return 1

    region_mask = component.createWithInitialProperties(
        {
            "controller": region_window_controller,
            "settings": settings,
        }
    )
    if region_mask is None:
        return 1

    region_window_controller.set_region_mask(component, region_mask)
    window = engine.rootObjects()[0]
    window.startRequested.connect(region_window_controller.show_region_mask)
    window.stopRequested.connect(region_window_controller.hide_region_mask)
    return app.exec()
