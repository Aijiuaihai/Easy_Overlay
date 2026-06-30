from __future__ import annotations

from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from . import ui_text
from .constants import APP_NAME
from .overlay_window import CrosshairOverlay
from .settings_window import SettingsWindow


class TrayController(QObject):
    def __init__(self, app: QApplication, overlay: CrosshairOverlay, settings: SettingsWindow) -> None:
        super().__init__(app)
        self._app = app
        self._overlay = overlay
        self._settings = settings

        self._tray = QSystemTrayIcon(create_tray_icon(), self)
        self._tray.setToolTip(APP_NAME)
        self._tray.setContextMenu(self._create_menu())
        self._tray.activated.connect(self._handle_activation)
        self._settings.config_changed.connect(self._handle_config_changed)
        self._tray.show()
        self._refresh_toggle_text()

    def _create_menu(self) -> QMenu:
        menu = QMenu()

        settings_action = QAction(ui_text.ACTION_SETTINGS, self)
        settings_action.triggered.connect(self._settings.show_settings)
        menu.addAction(settings_action)

        self._toggle_action = QAction(self)
        self._toggle_action.triggered.connect(self.toggle_overlay)
        menu.addAction(self._toggle_action)

        quit_action = QAction(ui_text.ACTION_QUIT, self)
        quit_action.triggered.connect(self.quit)
        menu.addAction(quit_action)

        return menu

    def _handle_activation(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            self._settings.show_settings()

    def toggle_overlay(self) -> None:
        self._settings.set_overlay_enabled(not self._overlay.isVisible())
        self._refresh_toggle_text()

    def _handle_config_changed(self, _config: object) -> None:
        self._refresh_toggle_text()

    def _refresh_toggle_text(self) -> None:
        if self._overlay.isVisible():
            self._toggle_action.setText(ui_text.ACTION_HIDE_CROSSHAIR)
        else:
            self._toggle_action.setText(ui_text.ACTION_SHOW_CROSSHAIR)

    def quit(self) -> None:
        self._tray.hide()
        self._app.quit()


def create_tray_icon() -> QIcon:
    pixmap = QPixmap(64, 64)
    pixmap.fill(QColor(0, 0, 0, 0))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    outline_pen = QPen(QColor(0, 0, 0, 230), 8)
    outline_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    green_pen = QPen(QColor(0, 255, 0, 235), 4)
    green_pen.setCapStyle(Qt.PenCapStyle.RoundCap)

    lines = (
        (10, 32, 25, 32),
        (39, 32, 54, 32),
        (32, 10, 32, 25),
        (32, 39, 32, 54),
    )

    painter.setPen(outline_pen)
    for x1, y1, x2, y2 in lines:
        painter.drawLine(x1, y1, x2, y2)

    painter.setPen(green_pen)
    for x1, y1, x2, y2 in lines:
        painter.drawLine(x1, y1, x2, y2)

    painter.end()
    return QIcon(pixmap)
