from __future__ import annotations

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QGuiApplication, QPainter, QPen
from PySide6.QtWidgets import QWidget

from .constants import (
    CROSSHAIR_ARM_LENGTH,
    CROSSHAIR_GAP,
    CROSSHAIR_OUTLINE_THICKNESS,
    CROSSHAIR_THICKNESS,
    WINDOW_SIZE,
)
from .win32_overlay import apply_overlay_window_styles


class CrosshairOverlay(QWidget):
    def __init__(self) -> None:
        super().__init__(None)
        self.setObjectName("CrosshairOverlay")
        self.setFixedSize(WINDOW_SIZE, WINDOW_SIZE)

        flags = (
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        transparent_input = getattr(Qt.WindowType, "WindowTransparentForInput", None)
        if transparent_input is not None:
            flags |= transparent_input
        self.setWindowFlags(flags)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)

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

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        center = QPointF(self.width() / 2, self.height() / 2)
        segments = (
            (QPointF(center.x() - CROSSHAIR_ARM_LENGTH, center.y()), QPointF(center.x() - CROSSHAIR_GAP, center.y())),
            (QPointF(center.x() + CROSSHAIR_GAP, center.y()), QPointF(center.x() + CROSSHAIR_ARM_LENGTH, center.y())),
            (QPointF(center.x(), center.y() - CROSSHAIR_ARM_LENGTH), QPointF(center.x(), center.y() - CROSSHAIR_GAP)),
            (QPointF(center.x(), center.y() + CROSSHAIR_GAP), QPointF(center.x(), center.y() + CROSSHAIR_ARM_LENGTH)),
        )

        outline_pen = QPen(QColor(0, 0, 0, 220), CROSSHAIR_OUTLINE_THICKNESS)
        outline_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        crosshair_pen = QPen(QColor(0, 255, 0, 235), CROSSHAIR_THICKNESS)
        crosshair_pen.setCapStyle(Qt.PenCapStyle.RoundCap)

        painter.setPen(outline_pen)
        for start, end in segments:
            painter.drawLine(start, end)

        painter.setPen(crosshair_pen)
        for start, end in segments:
            painter.drawLine(start, end)
