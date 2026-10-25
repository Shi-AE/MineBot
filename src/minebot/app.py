import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication

from .capture import CaptureService
from .capture.console import ConsolePreview
from .recognition import RecognitionService
from .settings import AppSettings
from .ui.application import run_application


def main() -> int:
    app = QGuiApplication(sys.argv)
    app.setApplicationName("MineBot")
    app.setOrganizationName("MineBot")
    app.setApplicationVersion("0.1.0")

    settings = AppSettings()
    cache_path = Path(settings.capture_cache_path)
    capture_service = CaptureService(
        cache_path,
        settings.capture_frequency,
        app,
    )
    console_preview = ConsolePreview(cache_path, settings.capture_frequency)
    capture_service.frameCaptured.connect(console_preview.handle_frame)
    capture_service.errorRaised.connect(console_preview.handle_error)

    project_root = Path(__file__).resolve().parents[2]
    recognition_service = RecognitionService(
        project_root / "models" / "detector" / "minebot-yolo26n-detector-v1.onnx",
        project_root
        / "models"
        / "detector"
        / "minebot-yolo26n-detector-v1.json",
        cache_path.parent,
        settings.selected_processor,
        app,
    )
    capture_service.frameCaptured.connect(recognition_service.submit_frame)
    recognition_service.processorChanged.connect(settings.set_active_processor)
    recognition_service.errorRaised.connect(
        lambda message: print(
            f"[recognition] error: {message}",
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

    settings.captureFrequencyChanged.connect(update_capture_frequency)
    settings.detectorProcessorChanged.connect(update_detection_processor)
    app.aboutToQuit.connect(recognition_service.stop)
    return run_application(app, settings, capture_service)
