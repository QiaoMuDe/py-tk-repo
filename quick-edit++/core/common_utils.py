"""
公共工具函数模块

提供应用程序中常用的工具函数，如窗口居中显示等。
"""

import tkinter as tk
import customtkinter as ctk


def center_window(window, width=None, height=None):
    """
    将窗口居中显示，支持tkinter和customtkinter窗口
    
    Args:
        window: 要居中的窗口对象（tkinter.Toplevel或customtkinter.CTkToplevel）
        width: 窗口宽度，如果为None则使用窗口当前宽度
        height: 窗口高度，如果为None则使用窗口当前高度
    """
    # 如果没有提供宽高参数，则获取窗口的实际宽高
    if width is None:
        width = window.winfo_width()
    if height is None:
        height = window.winfo_height()

    # 确保宽度和高度有效，防止异常
    if width <= 1:
        width = 500  # 默认宽度
    if height <= 1:
        height = 400  # 默认高度

    # 获取屏幕的宽度和高度
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # 计算居中位置
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    # 设置窗口位置和尺寸
    window.geometry(f"{width}x{height}+{x}+{y}")


def set_window_min_size(window, min_width, min_height):
    """
    设置窗口的最小尺寸
    
    Args:
        window: 窗口对象
        min_width: 最小宽度
        min_height: 最小高度
    """
    window.minsize(min_width, min_height)


def set_window_max_size(window, max_width, max_height):
    """
    设置窗口的最大尺寸
    
    Args:
        window: 窗口对象
        max_width: 最大宽度
        max_height: 最大高度
    """
    window.maxsize(max_width, max_height)


def configure_window_resizable(window, width_resizable=True, height_resizable=True):
    """
    配置窗口是否可调整大小
    
    Args:
        window: 窗口对象
        width_resizable: 宽度是否可调整
        height_resizable: 高度是否可调整
    """
    window.resizable(width_resizable, height_resizable)