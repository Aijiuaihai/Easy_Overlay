from __future__ import annotations

from PySide6.QtCore import QEvent, QPoint, Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from . import ui_text
from .constants import APP_NAME, AUTHOR_NAME, GITHUB_URL


class AboutDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._drag_position: QPoint | None = None

        self.setWindowTitle(ui_text.ABOUT_TITLE)
        self.setObjectName("AboutDialog")
        self.setModal(True)
        self.setMinimumWidth(380)
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self._title_bar = QWidget()
        self._title_bar.setObjectName("DialogTitleBar")
        title_layout = QHBoxLayout(self._title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)
        self._title_label = QLabel(ui_text.ABOUT_TITLE)
        self._title_label.setObjectName("DialogTitle")
        self._title_bar.installEventFilter(self)
        self._title_label.installEventFilter(self)
        close_header_button = QPushButton("X")
        close_header_button.setObjectName("HeaderCloseButton")
        close_header_button.setToolTip(ui_text.BUTTON_CLOSE)
        close_header_button.clicked.connect(self.accept)
        title_layout.addWidget(self._title_label)
        title_layout.addStretch(1)
        title_layout.addWidget(close_header_button)

        name_label = QLabel(APP_NAME)
        name_label.setObjectName("AppNameLabel")
        author_label = QLabel(f"{ui_text.ABOUT_AUTHOR_LABEL}: {AUTHOR_NAME}")
        github_label = QLabel(f"{ui_text.ABOUT_GITHUB_LABEL}: {GITHUB_URL}")
        github_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        github_label.setWordWrap(True)

        github_button = QPushButton(ui_text.BUTTON_OPEN_GITHUB)
        github_button.clicked.connect(self._open_github)
        close_button = QPushButton(ui_text.BUTTON_CLOSE)
        close_button.setObjectName("CloseButton")
        close_button.clicked.connect(self.accept)

        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 2, 0, 0)
        button_row.setSpacing(8)
        button_row.addWidget(github_button)
        button_row.addStretch(1)
        button_row.addWidget(close_button)

        panel = QFrame()
        panel.setObjectName("AboutPanel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(18, 16, 18, 16)
        panel_layout.setSpacing(14)
        panel_layout.addWidget(self._title_bar)
        panel_layout.addWidget(name_label)
        panel_layout.addWidget(author_label)
        panel_layout.addWidget(github_label)
        panel_layout.addLayout(button_row)

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.addWidget(panel)

        self._apply_style()

    def eventFilter(self, watched: object, event: QEvent) -> bool:  # noqa: N802
        if watched not in (self._title_bar, self._title_label):
            return super().eventFilter(watched, event)

        if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            return True

        if (
            event.type() == QEvent.Type.MouseMove
            and self._drag_position is not None
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            self.move(event.globalPosition().toPoint() - self._drag_position)
            return True

        if event.type() == QEvent.Type.MouseButtonRelease:
            self._drag_position = None
            return True

        return super().eventFilter(watched, event)

    def _open_github(self) -> None:
        QDesktopServices.openUrl(QUrl(GITHUB_URL))

    def _apply_style(self) -> None:
        self.setStyleSheet(
            """
            QDialog#AboutDialog {
                background: transparent;
            }
            QFrame#AboutPanel {
                background-color: #f7f9fc;
                border: 1px solid #d5dce8;
                border-radius: 8px;
            }
            QWidget#DialogTitleBar {
                background: transparent;
            }
            QLabel#DialogTitle {
                color: #172033;
                font-size: 16px;
                font-weight: 600;
            }
            QLabel#AppNameLabel {
                color: #172033;
                font-size: 18px;
                font-weight: 700;
            }
            QLabel {
                color: #344054;
                font-size: 13px;
            }
            QPushButton {
                min-height: 30px;
                padding: 6px 12px;
                color: #172033;
                background-color: #ffffff;
                border: 1px solid #cbd4e1;
                border-radius: 8px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #eef5ff;
                border-color: #91add7;
            }
            QPushButton:pressed {
                background-color: #ddeaf8;
            }
            QPushButton#HeaderCloseButton {
                min-width: 30px;
                max-width: 30px;
                min-height: 30px;
                max-height: 30px;
                padding: 0;
                border-radius: 8px;
                font-weight: 600;
            }
            QPushButton#CloseButton {
                background-color: #162033;
                border-color: #162033;
                color: #ffffff;
            }
            QPushButton#CloseButton:hover {
                background-color: #26334a;
                border-color: #26334a;
            }
            """
        )
