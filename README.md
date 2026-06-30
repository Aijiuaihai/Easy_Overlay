# Easy Overlay

[中文](#中文说明) | [English](#english)

## 中文说明

Easy Overlay 是一个 Windows 本地外置准星 Overlay 工具，基于 Python、PySide6 和 pywin32。

### 功能

- 透明、无边框、置顶的外置游戏准星。
- 不注入游戏、不读取游戏内存、不 Hook 游戏进程。
- 静态绘制准星，低性能损耗。

### 运行

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m easy_overlay
```

也可以使用安装后的命令：

```powershell
easy-overlay
```

### 配置路径

默认配置文件位于：

```text
%APPDATA%\Aijiuaihai\Easy Overlay\config.json
```

### 作者

- 作者：Aijiuaihai
- GitHub：https://github.com/Aijiuaihai/Easy_Overlay

## English

A minimal Windows crosshair overlay built with Python, PySide6 and pywin32.

### Features

- Transparent, frameless, always-on-top external game crosshair.
- No game injection, no game memory reads, and no game process hooks.
- Static crosshair drawing with low performance overhead.

### Run

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

### Project Layout

```text
src/easy_overlay/
  about_dialog.py        # Rounded About dialog.
  app.py                 # Application entry point.
  color_picker_dialog.py # Rounded color picker dialog.
  config.py              # Crosshair configuration model.
  config_store.py        # JSON config load/save helpers.
  overlay_window.py      # Click-through crosshair overlay.
  settings_window.py     # Settings UI.
  tray.py                # System tray menu.
  win32_overlay.py       # Windows extended window styles.
```

The configuration model is intentionally plain and JSON-friendly, so persistent JSON settings and global hotkeys can be extended without changing the overlay drawing path.
