from __future__ import annotations

from PySide6.QtCore import QEvent, QPoint, Signal, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from . import ui_text
from .color_picker_dialog import ColorPickerDialog
from .config import CrosshairConfig
from .constants import MIN_CROSSHAIR_ARM_LENGTH, WINDOW_SIZE


class SettingsWindow(QWidget):
    config_changed = Signal(object)

    def __init__(self, config: CrosshairConfig | None = None) -> None:
        super().__init__(None)
        self._config = (config or CrosshairConfig()).normalized()
        self._color = QColor(*self._config.color)
        self._syncing = False
        self._drag_position: QPoint | None = None

        self.setWindowTitle(ui_text.APP_SETTINGS_TITLE)
        self.setObjectName("SettingsWindow")
        self.setMinimumWidth(420)
        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self._enabled_checkbox = QCheckBox(ui_text.LABEL_ENABLE_CROSSHAIR)
        self._enabled_checkbox.setChecked(self._config.enabled)
        self._enabled_checkbox.stateChanged.connect(self._apply_from_controls)

        self._color_button = QPushButton(ui_text.BUTTON_PICK_COLOR)
        self._color_button.clicked.connect(self._choose_color)

        color_row = QWidget()
        color_layout = QHBoxLayout(color_row)
        color_layout.setContentsMargins(0, 0, 0, 0)
        color_layout.setSpacing(8)
        self._color_swatch = QLabel()
        self._color_swatch.setFixedSize(42, 26)
        color_layout.addWidget(self._color_swatch)
        color_layout.addWidget(self._color_button, 1)

        max_length = (WINDOW_SIZE // 2) - 4
        self._length_slider, self._length_spin, length_row = self._create_number_row(
            MIN_CROSSHAIR_ARM_LENGTH,
            max_length,
            self._config.arm_length,
        )
        self._gap_slider, self._gap_spin, gap_row = self._create_number_row(0, self._config.arm_length - 1, self._config.gap)
        self._thickness_slider, self._thickness_spin, thickness_row = self._create_number_row(1, 16, self._config.thickness)
        self._outline_slider, self._outline_spin, outline_row = self._create_number_row(0, 24, self._config.outline_thickness)
        self._opacity_slider, self._opacity_spin, opacity_row = self._create_number_row(30, 255, self._config.color[3])

        self._length_spin.valueChanged.connect(self._handle_length_changed)
        self._gap_spin.valueChanged.connect(self._apply_from_controls)
        self._thickness_spin.valueChanged.connect(self._apply_from_controls)
        self._outline_spin.valueChanged.connect(self._apply_from_controls)
        self._opacity_spin.valueChanged.connect(self._apply_from_controls)

        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(12)
        form.addRow(ui_text.LABEL_COLOR, color_row)
        form.addRow(ui_text.LABEL_LENGTH, length_row)
        form.addRow(ui_text.LABEL_GAP, gap_row)
        form.addRow(ui_text.LABEL_THICKNESS, thickness_row)
        form.addRow(ui_text.LABEL_OUTLINE, outline_row)
        form.addRow(ui_text.LABEL_OPACITY, opacity_row)

        reset_button = QPushButton(ui_text.BUTTON_RESET)
        reset_button.setObjectName("ResetButton")
        reset_button.clicked.connect(self.reset_defaults)
        close_button = QPushButton(ui_text.BUTTON_CLOSE)
        close_button.setObjectName("CloseButton")
        close_button.clicked.connect(self.hide)

        self._title_bar = QWidget()
        self._title_bar.setObjectName("TitleBar")
        title_layout = QHBoxLayout(self._title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)
        self._title_label = QLabel(ui_text.APP_SETTINGS_TITLE)
        self._title_label.setObjectName("SettingsTitle")
        self._title_bar.installEventFilter(self)
        self._title_label.installEventFilter(self)
        header_close_button = QPushButton("X")
        header_close_button.setObjectName("HeaderCloseButton")
        header_close_button.setToolTip(ui_text.BUTTON_CLOSE)
        header_close_button.clicked.connect(self.hide)
        title_layout.addWidget(self._title_label)
        title_layout.addStretch(1)
        title_layout.addWidget(header_close_button)

        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 2, 0, 0)
        button_row.setSpacing(8)
        button_row.addWidget(reset_button)
        button_row.addStretch(1)
        button_row.addWidget(close_button)

        panel = QFrame()
        panel.setObjectName("SettingsPanel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(18, 16, 18, 16)
        panel_layout.setSpacing(14)
        panel_layout.addWidget(self._title_bar)
        panel_layout.addWidget(self._enabled_checkbox)
        panel_layout.addLayout(form)
        panel_layout.addLayout(button_row)

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.addWidget(panel)

        self._update_gap_range(self._config.arm_length)
        self._update_color_swatch()
        self._apply_style()

    def current_config(self) -> CrosshairConfig:
        return self._config

    def set_overlay_enabled(self, enabled: bool) -> None:
        self._enabled_checkbox.setChecked(enabled)

    def reset_defaults(self) -> None:
        self._load_config(CrosshairConfig())
        self._emit_current_config()

    def show_settings(self) -> None:
        self.show()
        self.raise_()
        self.activateWindow()

    def eventFilter(self, watched: object, event: QEvent) -> bool:  # noqa: N802
        if not hasattr(self, "_title_label"):
            return super().eventFilter(watched, event)

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

    def _create_number_row(self, minimum: int, maximum: int, value: int) -> tuple[QSlider, QSpinBox, QWidget]:
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(minimum, maximum)
        slider.setValue(value)

        spin = QSpinBox()
        spin.setRange(minimum, maximum)
        spin.setValue(value)
        spin.setFixedWidth(72)

        slider.valueChanged.connect(spin.setValue)
        spin.valueChanged.connect(slider.setValue)

        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(slider, 1)
        layout.addWidget(spin)
        return slider, spin, row

    def _choose_color(self) -> None:
        dialog = ColorPickerDialog(self._color, self)
        if dialog.exec() != ColorPickerDialog.DialogCode.Accepted:
            return

        color = dialog.selected_color()
        color.setAlpha(self._opacity_spin.value())
        self._color = color
        self._update_color_swatch()
        self._apply_from_controls()

    def _handle_length_changed(self, *_args: object) -> None:
        self._update_gap_range(self._length_spin.value())
        self._apply_from_controls()

    def _update_gap_range(self, arm_length: int) -> None:
        max_gap = max(0, arm_length - 1)
        self._gap_slider.setMaximum(max_gap)
        self._gap_spin.setMaximum(max_gap)

    def _load_config(self, config: CrosshairConfig) -> None:
        config = config.normalized()
        self._syncing = True
        try:
            self._config = config
            self._color = QColor(*config.color)
            self._enabled_checkbox.setChecked(config.enabled)
            self._length_spin.setValue(config.arm_length)
            self._update_gap_range(config.arm_length)
            self._gap_spin.setValue(config.gap)
            self._thickness_spin.setValue(config.thickness)
            self._outline_spin.setValue(config.outline_thickness)
            self._opacity_spin.setValue(config.color[3])
            self._update_color_swatch()
        finally:
            self._syncing = False

    def _apply_from_controls(self, *_args: object) -> None:
        if self._syncing:
            return

        self._emit_current_config()

    def _emit_current_config(self) -> None:
        alpha = self._opacity_spin.value()
        self._color.setAlpha(alpha)
        self._config = CrosshairConfig(
            enabled=self._enabled_checkbox.isChecked(),
            color=(self._color.red(), self._color.green(), self._color.blue(), alpha),
            arm_length=self._length_spin.value(),
            gap=self._gap_spin.value(),
            thickness=self._thickness_spin.value(),
            outline_thickness=self._outline_spin.value(),
        ).normalized()
        self._update_color_swatch()
        self.config_changed.emit(self._config)

    def _update_color_swatch(self) -> None:
        red = self._color.red()
        green = self._color.green()
        blue = self._color.blue()
        self._color_swatch.setStyleSheet(
            "border: 1px solid #777;"
            "border-radius: 8px;"
            f"background-color: rgb({red}, {green}, {blue});"
        )

    def _apply_style(self) -> None:
        self.setStyleSheet(
            """
            QWidget#SettingsWindow {
                background: transparent;
            }
            QFrame#SettingsPanel {
                background-color: #f7f9fc;
                border: 1px solid #d5dce8;
                border-radius: 8px;
            }
            QWidget#TitleBar {
                background: transparent;
            }
            QLabel#SettingsTitle {
                color: #172033;
                font-size: 16px;
                font-weight: 600;
            }
            QLabel {
                color: #344054;
                font-size: 13px;
            }
            QCheckBox {
                color: #172033;
                font-size: 13px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #aab4c3;
                border-radius: 5px;
                background-color: #ffffff;
            }
            QCheckBox::indicator:checked {
                border-color: #0c8f5a;
                background-color: #12a66a;
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
