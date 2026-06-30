from __future__ import annotations

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from . import ui_text
from .config import CrosshairConfig
from .constants import MIN_CROSSHAIR_ARM_LENGTH, WINDOW_SIZE


class SettingsWindow(QWidget):
    config_changed = Signal(object)

    def __init__(self, config: CrosshairConfig | None = None) -> None:
        super().__init__(None)
        self._config = (config or CrosshairConfig()).normalized()
        self._color = QColor(*self._config.color)
        self._syncing = False

        self.setWindowTitle(ui_text.APP_SETTINGS_TITLE)
        self.setObjectName("SettingsWindow")
        self.setMinimumWidth(360)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

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
        self._color_swatch.setFixedSize(36, 24)
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
        form.addRow(ui_text.LABEL_COLOR, color_row)
        form.addRow(ui_text.LABEL_LENGTH, length_row)
        form.addRow(ui_text.LABEL_GAP, gap_row)
        form.addRow(ui_text.LABEL_THICKNESS, thickness_row)
        form.addRow(ui_text.LABEL_OUTLINE, outline_row)
        form.addRow(ui_text.LABEL_OPACITY, opacity_row)

        reset_button = QPushButton(ui_text.BUTTON_RESET)
        reset_button.clicked.connect(self.reset_defaults)
        close_button = QPushButton(ui_text.BUTTON_CLOSE)
        close_button.clicked.connect(self.hide)

        button_row = QHBoxLayout()
        button_row.addWidget(reset_button)
        button_row.addStretch(1)
        button_row.addWidget(close_button)

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(12)
        root.addWidget(self._enabled_checkbox)
        root.addLayout(form)
        root.addLayout(button_row)

        self._update_gap_range(self._config.arm_length)
        self._update_color_swatch()

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
        color = QColorDialog.getColor(self._color, self, ui_text.COLOR_DIALOG_TITLE)
        if not color.isValid():
            return

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
            "border-radius: 3px;"
            f"background-color: rgb({red}, {green}, {blue});"
        )
