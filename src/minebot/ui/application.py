import sys
from pathlib import Path

from PySide6.QtCore import QObject, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle


@Slot()
def _handle_start_requested() -> None:
    print("成功", flush=True)


def run_application(app: QGuiApplication, settings: QObject) -> int:
    QQuickStyle.setStyle("Basic")

    qml_file = Path(__file__).resolve().parent / "Main.qml"
    if not qml_file.is_file():
        print(f"QML 文件未找到: {qml_file}", file=sys.stderr)
        return 1

    engine = QQmlApplicationEngine(app)
    engine.setInitialProperties({"appSettings": settings})
    engine.load(qml_file.as_uri())
    if not engine.rootObjects():
        return 1

    window = engine.rootObjects()[0]
    window.startRequested.connect(_handle_start_requested)
    return app.exec()
