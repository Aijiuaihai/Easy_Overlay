from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from .constants import APP_NAME, ORGANIZATION_NAME
from .overlay_window import CrosshairOverlay
from .tray import TrayController


def main(argv: list[str] | None = None) -> int:
    if sys.platform != "win32":
        raise SystemExit("Easy Overlay currently supports Windows only.")

    app = QApplication(sys.argv if argv is None else argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORGANIZATION_NAME)
    app.setQuitOnLastWindowClosed(False)

    overlay = CrosshairOverlay()
    overlay.show()

    tray = TrayController(app, overlay)
    app.setProperty("tray_controller", tray)

    return app.exec()
