import ctypes
from ctypes import wintypes

# 未公开但稳定的标志位：让 MineBot 窗口不出现在捕获画面中。
_WDA_EXCLUDEFROMCAPTURE = 0x11


class _Rect(ctypes.Structure):
    _fields_ = (
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    )


_user32 = ctypes.WinDLL("user32", use_last_error=True)
_user32.GetWindowRect.argtypes = (wintypes.HWND, ctypes.POINTER(_Rect))
_user32.GetWindowRect.restype = wintypes.BOOL
_user32.SetWindowDisplayAffinity.argtypes = (wintypes.HWND, wintypes.DWORD)
_user32.SetWindowDisplayAffinity.restype = wintypes.BOOL


def exclude_from_capture(hwnd: int) -> None:
    if not _user32.SetWindowDisplayAffinity(hwnd, _WDA_EXCLUDEFROMCAPTURE):
        raise OSError(ctypes.get_last_error(), "SetWindowDisplayAffinity 调用失败")


def window_rect(hwnd: int) -> dict[str, int]:
    rect = _Rect()
    if not _user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        raise OSError(ctypes.get_last_error(), "GetWindowRect 调用失败")

    width = rect.right - rect.left
    height = rect.bottom - rect.top
    if width <= 0 or height <= 0:
        raise RuntimeError(f"捕获尺寸无效: {width}x{height}")
    return {
        "left": rect.left,
        "top": rect.top,
        "width": width,
        "height": height,
    }
