from __future__ import annotations

import ctypes
import ctypes.wintypes
import sys

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QGuiApplication, QPainter, QPen
from PySide6.QtWidgets import QWidget

from .config import CrosshairConfig, qcolor_from_tuple
from .constants import WINDOW_SIZE
from .win32_overlay import apply_overlay_window_styles


class CrosshairOverlay(QWidget):
    def __init__(self, config: CrosshairConfig | None = None) -> None:
        super().__init__(None)
        self._config = (config or CrosshairConfig()).normalized()
        self.setObjectName("CrosshairOverlay")
        self.setFixedSize(WINDOW_SIZE, WINDOW_SIZE)

        flags = (
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setWindowFlags(flags)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)

    def nativeEvent(self, event_type, message):  # noqa: N802
        if sys.platform == "win32":
            import win32con

            msg = ctypes.wintypes.MSG.from_address(int(message))
            if msg.message == win32con.WM_NCHITTEST:
                return True, win32con.HTTRANSPARENT

        return super().nativeEvent(event_type, message)

    def set_config(self, config: CrosshairConfig) -> None:
        self._config = config.normalized()
        if not self._config.enabled:
            self.hide()
            return

        self.center_on_primary_screen()
        if not self.isVisible():
            self.show()
        self.update()

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self.center_on_primary_screen()
        apply_overlay_window_styles(int(self.winId()))

    def center_on_primary_screen(self) -> None:
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return

        screen_geometry = screen.geometry()
        x = screen_geometry.x() + (screen_geometry.width() - self.width()) // 2
        y = screen_geometry.y() + (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def paintEvent(self, event) -> None:  # noqa: N802
        super().paintEvent(event)
        if not self._config.enabled:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        config = self._config
        center = QPointF(self.width() / 2, self.height() / 2)
        segments = (
            (QPointF(center.x() - config.arm_length, center.y()), QPointF(center.x() - config.gap, center.y())),
            (QPointF(center.x() + config.gap, center.y()), QPointF(center.x() + config.arm_length, center.y())),
            (QPointF(center.x(), center.y() - config.arm_length), QPointF(center.x(), center.y() - config.gap)),
            (QPointF(center.x(), center.y() + config.gap), QPointF(center.x(), center.y() + config.arm_length)),
        )

        if config.outline_thickness > 0:
            outline_pen = QPen(qcolor_from_tuple(config.outline_color), config.outline_thickness)
            outline_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(outline_pen)
            for start, end in segments:
                painter.drawLine(start, end)

        crosshair_pen = QPen(qcolor_from_tuple(config.color), config.thickness)
        crosshair_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(crosshair_pen)
        for start, end in segments:
            painter.drawLine(start, end)
