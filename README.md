# Easy Overlay

[中文](#中文说明) | [English](#english)

## 中文说明

Easy Overlay 是一个 Windows 本地外置准星 Overlay 工具，基于 Python、PySide6 和 pywin32。

### 功能

- 透明、无边框、置顶的准星窗口。
- 128x128 Overlay，默认居中显示在主屏幕。
- 鼠标穿透，不影响点击游戏或桌面。
- 静态绘制准星，不使用高频 Timer 或渲染循环。
- 不注入游戏、不读取游戏内存、不 Hook 游戏进程。
- 系统托盘支持设置、显示/隐藏和退出。
- 设置窗口支持开启/关闭准星、调整颜色、透明度、长度、中心间隙、线条粗细和描边宽度。
- 配置会自动保存为 JSON，下次启动沿用上次设置。
- 设置窗口内提供“关于”窗口，显示作者和 GitHub 地址。

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

- Transparent, frameless, always-on-top overlay window.
- 128x128 overlay centered on the primary screen.
- Click-through overlay, so mouse input continues to reach the desktop or game.
- Static crosshair drawing with no high-frequency timer or render loop.
- No game injection, no game memory reads, and no game process hooks.
- System tray menu for settings, show/hide, and quit.
- Settings window for enabling the overlay and adjusting color, opacity, length, gap, line thickness, and outline width.
- JSON settings are saved automatically and reused on the next launch.
- About window in settings with author and GitHub information.

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
