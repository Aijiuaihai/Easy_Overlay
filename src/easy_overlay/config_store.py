from __future__ import annotations

import json
import os
from pathlib import Path

from .config import CrosshairConfig
from .constants import APP_NAME, ORGANIZATION_NAME

CONFIG_ENV_VAR = "EASY_OVERLAY_CONFIG_DIR"
CONFIG_FILENAME = "config.json"


def config_path() -> Path:
    override = os.getenv(CONFIG_ENV_VAR)
    if override:
        return Path(override) / CONFIG_FILENAME

    appdata = os.getenv("APPDATA") or os.getenv("LOCALAPPDATA")
    if appdata:
        return Path(appdata) / ORGANIZATION_NAME / APP_NAME / CONFIG_FILENAME

    return Path.home() / ".easy-overlay" / CONFIG_FILENAME


def load_config(path: Path | None = None) -> CrosshairConfig:
    target = path or config_path()
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return CrosshairConfig()

    if not isinstance(data, dict):
        return CrosshairConfig()

    return CrosshairConfig.from_dict(data)


def save_config(config: CrosshairConfig, path: Path | None = None) -> None:
    target = path or config_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    temp_path = target.with_suffix(".tmp")
    temp_path.write_text(
        json.dumps(config.normalized().to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    temp_path.replace(target)
