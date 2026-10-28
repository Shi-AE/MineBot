import sys
from pathlib import Path

from PySide6.QtCore import QObject, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QQmlComponent
from PySide6.QtQuickControls2 import QQuickStyle

from ..capture import CaptureService, CaptureTarget
from ..recognition import RecognitionViewState
from ..solver import SolverViewState
from .region import RegionWindowController


def run_application(
    app: QGuiApplication,
    settings: QObject,
    capture_service: CaptureService,
    recognition_state: RecognitionViewState,
    solver_state: SolverViewState,
) -> int:
    QQuickStyle.setStyle("Basic")

    qml_file = Path(__file__).resolve().parent / "Main.qml"
    if not qml_file.is_file():
        print(f"QML 文件未找到: {qml_file}", file=sys.stderr)
        return 1

    engine = QQmlApplicationEngine(app)
    region_window_controller = RegionWindowController(engine)
    engine.setInitialProperties(
        {
            "appSettings": settings,
            "recognitionState": recognition_state,
            "solverState": solver_state,
        }
    )
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
            "recognitionState": recognition_state,
            "solverState": solver_state,
        }
    )
    if region_mask is None:
        return 1

    region_window_controller.set_region_mask(component, region_mask)
    window = engine.rootObjects()[0]
    window.startRequested.connect(region_window_controller.show_region_mask)
    region_window_controller.regionShown.connect(
        lambda frame_hwnd, mask_hwnd: capture_service.start(
            CaptureTarget(frame_hwnd, mask_hwnd)
        )
    )
    window.stopRequested.connect(capture_service.stop)
    window.stopRequested.connect(region_window_controller.hide_region_mask)
    app.aboutToQuit.connect(capture_service.stop)
    return app.exec()
