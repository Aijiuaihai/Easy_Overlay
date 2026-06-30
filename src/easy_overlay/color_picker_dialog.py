from __future__ import annotations

from PySide6.QtCore import QEvent, QPoint, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from . import ui_text

PRESET_COLORS = (
    (0, 255, 0),
    (255, 64, 64),
    (64, 128, 255),
    (0, 220, 255),
    (255, 220, 0),
    (255, 80, 220),
    (255, 255, 255),
    (0, 0, 0),
)


class ColorPickerDialog(QDialog):
    def __init__(self, color: QColor, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._color = QColor(color)
        self._drag_position: QPoint | None = None
        self._syncing = False

        self.setWindowTitle(ui_text.COLOR_DIALOG_TITLE)
        self.setObjectName("ColorPickerDialog")
        self.setModal(True)
        self.setMinimumWidth(360)
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
        self._title_label = QLabel(ui_text.COLOR_DIALOG_TITLE)
        self._title_label.setObjectName("DialogTitle")
        self._title_bar.installEventFilter(self)
        self._title_label.installEventFilter(self)
        close_button = QPushButton("X")
        close_button.setObjectName("HeaderCloseButton")
        close_button.setToolTip(ui_text.BUTTON_CANCEL)
        close_button.clicked.connect(self.reject)
        title_layout.addWidget(self._title_label)
        title_layout.addStretch(1)
        title_layout.addWidget(close_button)

        self._preview = QLabel()
        self._preview.setObjectName("ColorPreview")
        self._preview.setFixedHeight(42)

        preset_grid = QGridLayout()
        preset_grid.setContentsMargins(0, 0, 0, 0)
        preset_grid.setHorizontalSpacing(8)
        preset_grid.setVerticalSpacing(8)
        for index, rgb in enumerate(PRESET_COLORS):
            button = QPushButton()
            button.setObjectName("PresetButton")
            button.setFixedSize(32, 28)
            button.clicked.connect(lambda _checked=False, selected=rgb: self._set_rgb(selected))
            button.setStyleSheet(
                "QPushButton#PresetButton {"
                f"background-color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]});"
                "border: 1px solid #b8c2d0;"
                "border-radius: 8px;"
                "}"
                "QPushButton#PresetButton:hover {"
                "border: 2px solid #12a66a;"
                "}"
            )
            preset_grid.addWidget(button, index // 4, index % 4)

        self._red_slider, self._red_spin, red_row = self._create_number_row(self._color.red())
        self._green_slider, self._green_spin, green_row = self._create_number_row(self._color.green())
        self._blue_slider, self._blue_spin, blue_row = self._create_number_row(self._color.blue())

        self._red_spin.valueChanged.connect(self._apply_from_controls)
        self._green_spin.valueChanged.connect(self._apply_from_controls)
        self._blue_spin.valueChanged.connect(self._apply_from_controls)

        controls = QGridLayout()
        controls.setContentsMargins(0, 0, 0, 0)
        controls.setHorizontalSpacing(12)
        controls.setVerticalSpacing(10)
        controls.addWidget(QLabel(ui_text.LABEL_RED), 0, 0)
        controls.addWidget(red_row, 0, 1)
        controls.addWidget(QLabel(ui_text.LABEL_GREEN), 1, 0)
        controls.addWidget(green_row, 1, 1)
        controls.addWidget(QLabel(ui_text.LABEL_BLUE), 2, 0)
        controls.addWidget(blue_row, 2, 1)

        cancel_button = QPushButton(ui_text.BUTTON_CANCEL)
        cancel_button.clicked.connect(self.reject)
        confirm_button = QPushButton(ui_text.BUTTON_CONFIRM)
        confirm_button.setObjectName("ConfirmButton")
        confirm_button.clicked.connect(self.accept)

        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 2, 0, 0)
        button_row.setSpacing(8)
        button_row.addStretch(1)
        button_row.addWidget(cancel_button)
        button_row.addWidget(confirm_button)

        panel = QFrame()
        panel.setObjectName("ColorDialogPanel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(18, 16, 18, 16)
        panel_layout.setSpacing(14)
        panel_layout.addWidget(self._title_bar)
        panel_layout.addWidget(self._preview)
        panel_layout.addLayout(preset_grid)
        panel_layout.addLayout(controls)
        panel_layout.addLayout(button_row)

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.addWidget(panel)

        self._apply_style()
        self._update_preview()

    def selected_color(self) -> QColor:
        return QColor(self._color)

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

    def _create_number_row(self, value: int) -> tuple[QSlider, QSpinBox, QWidget]:
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(0, 255)
        slider.setValue(value)

        spin = QSpinBox()
        spin.setRange(0, 255)
        spin.setValue(value)
        spin.setFixedWidth(70)

        slider.valueChanged.connect(spin.setValue)
        spin.valueChanged.connect(slider.setValue)

        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(slider, 1)
        layout.addWidget(spin)
        return slider, spin, row

    def _set_rgb(self, rgb: tuple[int, int, int]) -> None:
        self._syncing = True
        try:
            self._red_spin.setValue(rgb[0])
            self._green_spin.setValue(rgb[1])
            self._blue_spin.setValue(rgb[2])
        finally:
            self._syncing = False
        self._apply_from_controls()

    def _apply_from_controls(self, *_args: object) -> None:
        if self._syncing:
            return

        alpha = self._color.alpha()
        self._color = QColor(
            self._red_spin.value(),
            self._green_spin.value(),
            self._blue_spin.value(),
            alpha,
        )
        self._update_preview()

    def _update_preview(self) -> None:
        self._preview.setStyleSheet(
            "QLabel#ColorPreview {"
            f"background-color: rgb({self._color.red()}, {self._color.green()}, {self._color.blue()});"
            "border: 1px solid #cbd4e1;"
            "border-radius: 8px;"
            "}"
        )

    def _apply_style(self) -> None:
        self.setStyleSheet(
            """
            QDialog#ColorPickerDialog {
                background: transparent;
            }
            QFrame#ColorDialogPanel {
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
            QPushButton#ConfirmButton {
                background-color: #162033;
                border-color: #162033;
                color: #ffffff;
            }
            QPushButton#ConfirmButton:hover {
                background-color: #26334a;
                border-color: #26334a;
            }
            QSpinBox {
                min-height: 28px;
                padding: 2px 7px;
                color: #172033;
                background-color: #ffffff;
                border: 1px solid #cbd4e1;
                border-radius: 8px;
                selection-background-color: #12a66a;
            }
            QSpinBox:focus {
                border-color: #12a66a;
            }
            QSlider::groove:horizontal {
                height: 6px;
                border-radius: 3px;
                background-color: #d7dee9;
            }
            QSlider::sub-page:horizontal {
                border-radius: 3px;
                background-color: #12a66a;
            }
            QSlider::handle:horizontal {
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border: 2px solid #ffffff;
                border-radius: 8px;
                background-color: #12a66a;
            }
            QSlider::handle:horizontal:hover {
                background-color: #0c8f5a;
            }
            """
        )
