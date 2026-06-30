# Easy Overlay

A minimal Windows crosshair overlay built with Python, PySide6 and pywin32.

## Features

- Transparent, frameless, always-on-top overlay window.
- 128x128 overlay centered on the primary screen.
- Click-through overlay, so mouse input continues to reach the desktop or game.
- Static crosshair drawing with no high-frequency timer or render loop.
- No game injection, no game memory reads, and no game process hooks.
- System tray menu for settings, show/hide, and quit.
- Settings window for enabling the overlay and adjusting color, opacity, length, gap, line thickness, and outline width.
- JSON settings are saved automatically and reused on the next launch.

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m easy_overlay
```

You can also use the installed command:

```powershell
easy-overlay
```

## Project Layout

```text
src/easy_overlay/
  app.py              # Application entry point.
  config.py           # Crosshair configuration model.
  config_store.py     # JSON config load/save helpers.
  overlay_window.py   # Click-through crosshair overlay.
  settings_window.py  # Small settings UI.
  tray.py             # System tray menu.
  win32_overlay.py    # Windows extended window styles.
```

The configuration model is intentionally plain and JSON-friendly, so persistent JSON settings and global hotkeys can be added without changing the overlay drawing path.
