import sys

from PySide6.QtGui import QGuiApplication

from .settings import AppSettings
from .ui.application import run_application


def main() -> int:
    app = QGuiApplication(sys.argv)
    app.setApplicationName("MineBot")
    app.setOrganizationName("MineBot")
    app.setApplicationVersion("0.1.0")

    return run_application(app, AppSettings())
