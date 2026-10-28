import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication

from .capture import CaptureService
from .capture.console import ConsolePreview
from .recognition import (
    RecognitionModels,
    RecognitionService,
    RecognitionViewState,
)
from .settings import AppSettings
from .solver import SolverAdapter, SolverViewState
from .ui.application import run_application


def main() -> int:
    app = QGuiApplication(sys.argv)
    app.setApplicationName("MineBot")
    app.setOrganizationName("MineBot")
    app.setApplicationVersion("0.1.0")

    settings = AppSettings()
    cache_path = Path(settings.capture_cache_path)
    # 在这里串联唯一的数据管线：捕获 → 识别；识别快照同时分发给 QML 与求解器。
    capture_service = CaptureService(
        cache_path,
        settings.capture_frequency,
        app,
    )
    console_preview = ConsolePreview(cache_path, settings.capture_frequency)
    capture_service.frameCaptured.connect(console_preview.handle_frame)
    capture_service.errorRaised.connect(console_preview.handle_error)

    project_root = Path(__file__).resolve().parents[2]
    models = RecognitionModels(
        detector_model=(
            project_root
            / "models"
            / "detector"
            / "minebot-yolo26n-detector-v1.onnx"
        ),
        detector_metadata=(
            project_root
            / "models"
            / "detector"
            / "minebot-yolo26n-detector-v1.json"
        ),
        cell_model=(
            project_root
            / "models"
            / "cell_recognizer"
            / "light-cnn-64-v2"
            / "cell-recognizer-v1.onnx"
        ),
        cell_metadata=(
            project_root
            / "models"
            / "cell_recognizer"
            / "light-cnn-64-v2"
            / "model_metadata.json"
        ),
        flag_model=(
            project_root
            / "models"
            / "counter_recognizer"
            / "counter-recognizer-v3"
            / "flags"
            / "flag-recognizer-v1.onnx"
        ),
        flag_metadata=(
            project_root
            / "models"
            / "counter_recognizer"
            / "counter-recognizer-v3"
            / "flags"
            / "model_metadata.json"
        ),
        slot_model=(
            project_root
            / "models"
            / "counter_recognizer"
            / "counter-recognizer-v3"
            / "slots"
            / "slot-recognizer-v1.onnx"
        ),
        slot_metadata=(
            project_root
            / "models"
            / "counter_recognizer"
            / "counter-recognizer-v3"
            / "slots"
            / "model_metadata.json"
        ),
    )
    recognition_service = RecognitionService(
        models,
        cache_path.parent,
        settings.selected_processor,
        app,
    )
    recognition_state = RecognitionViewState(app)
    solver_state = SolverViewState(app)
    # 【求解器接入点】实现 SolverHandler 后在这里传入：
    # handler(识别快照 dict) -> SolverResult | None，返回 None 表示本帧放弃。
    # 正式求解器骨架见 src/minebot/solver/minebot_solver.py。
    solver_adapter = SolverAdapter(None, app)
    capture_service.frameCaptured.connect(recognition_service.submit_frame)
    recognition_service.snapshotReady.connect(recognition_state.set_snapshot)
    recognition_service.snapshotReady.connect(
        solver_state.set_recognition_snapshot
    )
    recognition_service.snapshotReady.connect(solver_adapter.submit_snapshot)
    solver_adapter.resultReady.connect(solver_state.set_result)
    recognition_service.processorChanged.connect(settings.set_active_processor)
    recognition_service.set_developer_mode(
        bool(settings.general.get("DeveloperMode", False))
    )
    recognition_service.errorRaised.connect(
        lambda message: print(
            f"[识别] 错误: {message}",
            file=sys.stderr,
            flush=True,
        )
    )
    solver_adapter.errorRaised.connect(
        lambda message: print(
            f"[求解] 错误: {message}",
            file=sys.stderr,
            flush=True,
        )
    )
    recognition_service.start()

    def update_detection_processor() -> None:
        recognition_service.set_processor(settings.selected_processor)

    def update_capture_frequency() -> None:
        frequency = settings.capture_frequency
        capture_service.set_frequency(frequency)
        console_preview.set_frequency(frequency)

    def update_developer_mode() -> None:
        recognition_service.set_developer_mode(
            bool(settings.general.get("DeveloperMode", False))
        )

    settings.captureFrequencyChanged.connect(update_capture_frequency)
    settings.detectorProcessorChanged.connect(update_detection_processor)
    settings.generalChanged.connect(update_developer_mode)
    app.aboutToQuit.connect(recognition_service.stop)
    app.aboutToQuit.connect(solver_adapter.stop)
    return run_application(
        app,
        settings,
        capture_service,
        recognition_state,
        solver_state,
    )
