from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from .config_store import load_config, save_config
from .constants import APP_NAME, ORGANIZATION_NAME
from .overlay_window import CrosshairOverlay
from .settings_window import SettingsWindow
from .tray import TrayController


def main(argv: list[str] | None = None) -> int:
    if sys.platform != "win32":
        raise SystemExit("Easy Overlay currently supports Windows only.")

    app = QApplication(sys.argv if argv is None else argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORGANIZATION_NAME)
    app.setQuitOnLastWindowClosed(False)

    config = load_config()
    overlay = CrosshairOverlay(config)
    settings = SettingsWindow(config)
    settings.config_changed.connect(overlay.set_config)
    settings.config_changed.connect(save_config)

    if config.enabled:
        overlay.show()

    tray = TrayController(app, overlay, settings)
    app.setProperty("tray_controller", tray)
    app.setProperty("settings_window", settings)

    return app.exec()
