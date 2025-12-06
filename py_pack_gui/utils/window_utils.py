"""
窗口工具模块
提供窗口相关的通用功能
"""

import sys
import tkinter as tk

# Windows API 导入
if sys.platform == "win32":
    import ctypes


def get_screen_size():
    """
    获取DPI感知的真实屏幕尺寸

    Returns:
        tuple: (屏幕宽度, 屏幕高度), 如果获取失败则返回默认值(1920, 1080)
    """
    # 非Windows系统直接返回默认值
    if sys.platform != "win32":
        return 1920, 1080

    try:
        # 定义Windows API常量和结构
        user32 = ctypes.windll.user32

        # 设置进程为DPI感知, 获取真实物理分辨率
        if hasattr(user32, "SetProcessDPIAware"):
            user32.SetProcessDPIAware()

        # 使用GetSystemMetrics获取屏幕尺寸
        # SM_CXSCREEN = 0 (屏幕宽度)
        # SM_CYSCREEN = 1 (屏幕高度)
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)

        # 验证获取的值是否合理
        if screen_width > 0 and screen_height > 0:
            return screen_width, screen_height
        else:
            return 1920, 1080  # 默认值
    except Exception:
        return 1920, 1080  # 出错时返回默认值


def center_window(window, width=None, height=None):
    """
    将指定窗口居中显示的通用方法

    Args:
        window: 需要居中的窗口对象（可以是Toplevel、CTkToplevel等）
        width: 窗口宽度, 如果为None则使用窗口当前宽度
        height: 窗口高度, 如果为None则使用窗口当前高度

    Returns:
        tuple: (x坐标, y坐标) 窗口应该设置的左上角坐标
    """
    try:
        # 获取屏幕尺寸
        screen_width, screen_height = get_screen_size()

        # 如果未指定宽度或高度, 尝试从窗口获取当前尺寸
        if width is None or height is None:
            width, height = window.winfo_width(), window.winfo_height()

        # 获取窗口尺寸
        window_width = width
        window_height = height

        # 计算居中位置
        x = (screen_width // 2) - window_width
        y = (screen_height // 2) - window_height

        # 确保窗口不会超出屏幕边界
        x = max(0, min(x, screen_width - window_width))
        y = max(0, min(y, screen_height - window_height))

        # 设置窗口位置
        window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        return (x, y)
    except Exception as e:
        print(f"窗口居中失败: {e}")
        return (0, 0)