import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication

from .capture import CaptureService
from .capture.console import ConsolePreview
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

    def update_capture_frequency() -> None:
        frequency = settings.capture_frequency
        capture_service.set_frequency(frequency)
        console_preview.set_frequency(frequency)

    settings.captureFrequencyChanged.connect(update_capture_frequency)
    return run_application(app, settings, capture_service)
