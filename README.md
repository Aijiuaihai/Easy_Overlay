# Easy Overlay

Windows 本地外置准星 Overlay，基于 Python、PySide6 和 pywin32。依赖使用更轻量的 `PySide6-Essentials`，代码仍然使用 `PySide6` 模块命名空间。

## 功能

- 透明、无边框、置顶窗口
- 128x128 主屏幕居中显示
- 鼠标穿透，不影响点击游戏或桌面
- 绿色十字准星，带黑色描边
- 系统托盘支持显示、隐藏和退出
- 静态绘制，不使用高频 Timer 或渲染循环
- 不注入游戏、不读取游戏内存、不 Hook 游戏进程

## 运行

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m easy_overlay
```

也可以安装为本地命令：

```powershell
python -m pip install -e .
easy-overlay
```

## 结构

```text
src/easy_overlay/
  app.py              # 应用入口
  overlay_window.py   # 准星窗口和静态绘制
  tray.py             # 系统托盘菜单
  win32_overlay.py    # Windows 扩展窗口样式
```

后续可在此基础上加入 JSON 配置、全局热键和更多准星样式。
