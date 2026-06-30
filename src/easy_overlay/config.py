from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from PySide6.QtGui import QColor

from .constants import (
    DEFAULT_CROSSHAIR_ARM_LENGTH,
    DEFAULT_CROSSHAIR_GAP,
    DEFAULT_CROSSHAIR_OUTLINE_THICKNESS,
    DEFAULT_CROSSHAIR_THICKNESS,
    MIN_CROSSHAIR_ARM_LENGTH,
    WINDOW_SIZE,
)

ColorTuple = tuple[int, int, int, int]


def clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, value))


@dataclass(frozen=True, slots=True)
class CrosshairConfig:
    enabled: bool = True
    color: ColorTuple = (0, 255, 0, 235)
    outline_color: ColorTuple = (0, 0, 0, 220)
    arm_length: int = DEFAULT_CROSSHAIR_ARM_LENGTH
    gap: int = DEFAULT_CROSSHAIR_GAP
    thickness: int = DEFAULT_CROSSHAIR_THICKNESS
    outline_thickness: int = DEFAULT_CROSSHAIR_OUTLINE_THICKNESS

    def normalized(self) -> CrosshairConfig:
        max_length = (WINDOW_SIZE // 2) - 4
        arm_length = clamp(self.arm_length, MIN_CROSSHAIR_ARM_LENGTH, max_length)
        gap = clamp(self.gap, 0, max(0, arm_length - 1))

        return CrosshairConfig(
            enabled=self.enabled,
            color=normalize_color(self.color),
            outline_color=normalize_color(self.outline_color),
            arm_length=arm_length,
            gap=gap,
            thickness=clamp(self.thickness, 1, 16),
            outline_thickness=clamp(self.outline_thickness, 0, 24),
        )

    def to_dict(self) -> dict[str, Any]:
        config = self.normalized()
        return {
            "enabled": config.enabled,
            "color": list(config.color),
            "outline_color": list(config.outline_color),
            "arm_length": config.arm_length,
            "gap": config.gap,
            "thickness": config.thickness,
            "outline_thickness": config.outline_thickness,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CrosshairConfig:
        defaults = cls()
        return cls(
            enabled=data.get("enabled") if isinstance(data.get("enabled"), bool) else defaults.enabled,
            color=color_from_value(data.get("color"), defaults.color),
            outline_color=color_from_value(data.get("outline_color"), defaults.outline_color),
            arm_length=int_from_value(data.get("arm_length"), defaults.arm_length),
            gap=int_from_value(data.get("gap"), defaults.gap),
            thickness=int_from_value(data.get("thickness"), defaults.thickness),
            outline_thickness=int_from_value(data.get("outline_thickness"), defaults.outline_thickness),
        ).normalized()


def normalize_color(color: ColorTuple) -> ColorTuple:
    red, green, blue, alpha = color
    return (
        clamp(red, 0, 255),
        clamp(green, 0, 255),
        clamp(blue, 0, 255),
        clamp(alpha, 0, 255),
    )


def qcolor_from_tuple(color: ColorTuple) -> QColor:
    return QColor(*normalize_color(color))


def int_from_value(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def color_from_value(value: Any, default: ColorTuple) -> ColorTuple:
    if not isinstance(value, (list, tuple)) or len(value) != 4:
        return default

    try:
        return normalize_color((int(value[0]), int(value[1]), int(value[2]), int(value[3])))
    except (TypeError, ValueError):
        return default
