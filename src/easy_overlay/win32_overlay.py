from __future__ import annotations

import sys


def apply_overlay_window_styles(hwnd: int) -> None:
    """Apply Windows styles required for a click-through topmost overlay."""
    if sys.platform != "win32":
        return

    import win32con
    import win32gui

    if not hwnd or not win32gui.IsWindow(hwnd):
        return

    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    ex_style |= win32con.WS_EX_LAYERED
    ex_style |= win32con.WS_EX_TOOLWINDOW
    ex_style |= getattr(win32con, "WS_EX_NOACTIVATE", 0x08000000)

    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)
    win32gui.SetWindowPos(
        hwnd,
        win32con.HWND_TOPMOST,
        0,
        0,
        0,
        0,
        win32con.SWP_NOMOVE
        | win32con.SWP_NOSIZE
        | win32con.SWP_NOACTIVATE
        | win32con.SWP_SHOWWINDOW,
    )
