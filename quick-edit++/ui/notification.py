#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通知组件模块
提供各种通知样式的UI组件, 包括成功通知、错误通知、警告通知等
"""

import customtkinter as ctk
import sys
import os

# Windows API 导入
if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes


def get_screen_size():
    """
    获取DPI感知的真实屏幕尺寸
    
    Returns:
        tuple: (屏幕宽度, 屏幕高度)，如果获取失败则返回默认值(1920, 1080)
    """
    # 非Windows系统直接返回默认值
    if sys.platform != "win32":
        return 1920, 1080
    
    try:
        # 定义Windows API常量和结构
        user32 = ctypes.windll.user32
        
        # 设置进程为DPI感知，获取真实物理分辨率
        if hasattr(user32, 'SetProcessDPIAware'):
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
            
    except Exception as e:
        # 如果获取失败，返回默认值
        print(f"获取屏幕尺寸失败: {e}")
        return 1920, 1080  # 默认值


class NotificationType:
    """通知类型枚举"""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class NotificationPosition:
    """通知位置枚举"""

    TOP_CENTER = "top_center"  # 屏幕上方居中显示
    TOP_RIGHT = "top_right"    # 屏幕右上角显示
    BOTTOM_RIGHT = "bottom_right"  # 屏幕右下角显示
    CENTER = "center"  # 屏幕居中显示


class Notification:
    """单个通知类, 负责创建和管理一个通知窗口"""

    # 通知组件字体大小配置
    ICON_FONT_SIZE = 25  # 图标字体大小
    TITLE_FONT_SIZE = 18  # 标题字体大小
    MESSAGE_FONT_SIZE = 15  # 消息字体大小

    # 通知窗口配置
    DEFAULT_WIDTH = 320  # 默认宽度
    MIN_HEIGHT = 100  # 最小高度
    MAX_HEIGHT = 200  # 最大高度
    LINE_HEIGHT = 27  # 每行高度估算
    CHAR_PER_LINE = 40  # 每行字符数估算
    CORNER_RADIUS = 15  # 圆角半径
    BORDER_WIDTH = 2  # 边框宽度
    INDICATOR_WIDTH = 5  # 指示条宽度

    # 动画配置
    FADE_STEPS = 10  # 淡入淡出步数
    FADE_DELAY = 30  # 淡入淡出延迟 (毫秒)

    def __init__(
        self,
        title,
        message,
        notification_type=NotificationType.SUCCESS,
        duration=3000,
        position=NotificationPosition.BOTTOM_RIGHT,
        manager=None,
    ):
        """
        初始化通知

        Args:
            title: 通知标题
            message: 通知消息内容
            notification_type: 通知类型, 默认为成功通知
            duration: 通知显示持续时间 (毫秒) , 默认为3秒
            position: 通知位置, 默认为屏幕右上角显示
            manager: 通知管理器引用, 用于通知销毁时回调
        """
        self.title = title
        self.message = message
        self.notification_type = notification_type
        self.duration = duration
        self.position = position
        self.font_family = "Microsoft YaHei UI"
        self.manager = manager  # 保存管理器引用

        # 状态变量
        self.fade_out_job = None  # 存储淡出任务的ID
        self.auto_hide_job = None  # 存储自动隐藏任务的ID

        # 创建通知窗口 - 不再依赖父窗口
        self.notification = ctk.CTkToplevel()
        self.notification.title("")
        self.notification.resizable(False, False)

        # 设置窗口属性
        self.notification.overrideredirect(True)  # 移除窗口边框
        self.notification.attributes("-topmost", True)  # 始终置顶
        self.notification.attributes("-transparentcolor", self.notification["bg"])

        # 设置通知窗口位置和大小
        self._set_notification_geometry()

        # 创建通知内容
        self._create_notification_content()

        # 开始淡入动画
        self._fade_in()

    def _set_notification_geometry(self):
        """设置通知窗口的位置和大小"""
        # 获取屏幕尺寸
        screen_width, screen_height = get_screen_size()

        # 根据消息长度动态计算通知窗口大小
        estimated_lines = max(1, len(self.message) // self.CHAR_PER_LINE)
        notification_height = max(
            self.MIN_HEIGHT,
            min(self.MAX_HEIGHT, self.MIN_HEIGHT + estimated_lines * self.LINE_HEIGHT),
        )
        notification_width = self.DEFAULT_WIDTH

        # 根据通知位置计算x, y坐标
        if self.position == NotificationPosition.TOP_CENTER:
            # 屏幕上方居中显示
            x = (screen_width - notification_width) // 2
            y = 50  # 距离屏幕顶部50像素

        elif self.position == NotificationPosition.TOP_RIGHT:
            # 屏幕右上角显示
            x = screen_width - notification_width - 20  # 距离屏幕右边20像素
            y = 50  # 距离屏幕顶部50像素

        elif self.position == NotificationPosition.BOTTOM_RIGHT:
            # 屏幕右下角显示
            x = screen_width - notification_width - 20  # 距离屏幕右边20像素
            y = screen_height - notification_height - 50  # 距离屏幕底部50像素

        elif self.position == NotificationPosition.CENTER:
            # 屏幕居中显示
            x = (screen_width - notification_width) // 2
            y = (screen_height - notification_height) // 2

        else:
            # 默认屏幕右下角显示
            x = screen_width - notification_width - 20  # 距离屏幕右边20像素
            y = screen_height - notification_height - 50  # 距离屏幕底部50像素

        # 确保通知窗口不会超出屏幕边界
        if x < 10:
            x = 10
        elif x + notification_width > screen_width - 10:
            x = screen_width - notification_width - 10

        if y < 10:
            y = 10
        elif y + notification_height > screen_height - 10:
            y = screen_height - notification_height - 10

        # 设置窗口位置和大小
        self.notification.geometry(
            f"{notification_width}x{notification_height}+{x}+{y}"
        )

        # 保存尺寸供其他方法使用
        self.notification_width = notification_width
        self.notification_height = notification_height

    def _create_notification_content(self):
        """创建通知内容"""
        # 根据通知类型获取颜色配置
        colors = self._get_notification_colors()

        # 主框架 - 使用圆角设计, 设置为透明背景
        main_frame = ctk.CTkFrame(
            self.notification,
            corner_radius=self.CORNER_RADIUS,
            fg_color="transparent",
            border_width=0,
        )
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # 内容框架 - 实际的通知容器
        content_frame = ctk.CTkFrame(
            main_frame,
            corner_radius=self.CORNER_RADIUS,
            fg_color=colors["bg"],
            border_width=self.BORDER_WIDTH,
            border_color=colors["border"],
        )
        content_frame.pack(fill="both", expand=True)

        # 内部内容框架 - 包含图标、标题和消息
        inner_content_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        inner_content_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # 左侧彩色指示条 - 垂直条, 与内容框架高度一致
        indicator_frame = ctk.CTkFrame(
            inner_content_frame,
            width=self.INDICATOR_WIDTH,
            corner_radius=3,
            fg_color=colors["indicator"],
        )
        indicator_frame.pack(side="left", fill="y", padx=(0, 10))
        indicator_frame.pack_propagate(False)

        # 右侧内容区域 - 包含图标、标题和消息
        right_content_frame = ctk.CTkFrame(inner_content_frame, fg_color="transparent")
        right_content_frame.pack(side="left", fill="both", expand=True)

        # 图标和标题框架
        header_frame = ctk.CTkFrame(right_content_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 5))

        # 通知图标
        icon_label = ctk.CTkLabel(
            header_frame,
            text=colors["icon"],
            font=(self.font_family, self.ICON_FONT_SIZE, "bold"),
            text_color=colors["icon_color"],
        )
        icon_label.pack(side="left", padx=(0, 10))

        # 标题标签
        title_label = ctk.CTkLabel(
            header_frame,
            text=self.title,
            font=(self.font_family, self.TITLE_FONT_SIZE, "bold"),
            text_color=colors["title"],
        )
        title_label.pack(side="left")

        # 消息标签 - 设置为可滚动文本区域以处理长消息
        msg_frame = ctk.CTkFrame(right_content_frame, fg_color="transparent")
        msg_frame.pack(fill="both", expand=True, pady=(5, 0))

        # 创建可滚动的文本框
        self.msg_text = ctk.CTkTextbox(
            msg_frame,
            font=(self.font_family, self.MESSAGE_FONT_SIZE),
            text_color=colors["message"],
            fg_color="transparent",
            border_width=0,
            wrap="word",
            height=self.notification_height - 80,  # 根据通知高度调整文本框高度
        )
        self.msg_text.pack(fill="both", expand=True)

        # 插入消息内容并设置为只读
        self.msg_text.insert("0.0", self.message)
        self.msg_text.configure(state="disabled")

    def _get_notification_colors(self):
        """
        根据通知类型获取颜色配置

        Returns:
            dict: 包含各种颜色配置的字典
        """
        if self.notification_type == NotificationType.SUCCESS:
            return {
                "bg": ("#ffffff", "#1e1e1e"),
                "border": ("#d0d0d0", "#505050"),
                "indicator": ("#4CAF50", "#45a049"),
                "icon": "✓",
                "icon_color": ("#4CAF50", "#45a049"),
                "title": ("#212121", "#ffffff"),
                "message": ("#424242", "#e0e0e0"),
            }
        elif self.notification_type == NotificationType.ERROR:
            return {
                "bg": ("#ffffff", "#1e1e1e"),
                "border": ("#d0d0d0", "#505050"),
                "indicator": ("#F44336", "#d32f2f"),
                "icon": "✕",
                "icon_color": ("#F44336", "#d32f2f"),
                "title": ("#212121", "#ffffff"),
                "message": ("#424242", "#e0e0e0"),
            }
        elif self.notification_type == NotificationType.WARNING:
            return {
                "bg": ("#ffffff", "#1e1e1e"),
                "border": ("#d0d0d0", "#505050"),
                "indicator": ("#FF9800", "#f57c00"),
                "icon": "⚠",
                "icon_color": ("#FF9800", "#f57c00"),
                "title": ("#212121", "#ffffff"),
                "message": ("#424242", "#e0e0e0"),
            }
        else:  # INFO
            return {
                "bg": ("#ffffff", "#1e1e1e"),
                "border": ("#d0d0d0", "#505050"),
                "indicator": ("#2196F3", "#1976D2"),
                "icon": "ℹ",
                "icon_color": ("#2196F3", "#1976D2"),
                "title": ("#212121", "#ffffff"),
                "message": ("#424242", "#e0e0e0"),
            }

    def _fade_in(self, step=0):
        """淡入效果"""
        if step <= self.FADE_STEPS:
            self.notification.attributes("-alpha", step / self.FADE_STEPS)
            self.notification.after(self.FADE_DELAY, lambda: self._fade_in(step + 1))
        else:
            # 淡入完成后, 等待指定时间后淡出
            self.auto_hide_job = self.notification.after(
                self.duration, self._start_fade_out
            )

    def _start_fade_out(self):
        """开始淡出的函数"""
        self._fade_out()

    def _fade_out(self, step=None):
        """淡出效果"""
        if step is None:
            step = self.FADE_STEPS

        if step > 0:
            self.notification.attributes("-alpha", step / self.FADE_STEPS)
            self.fade_out_job = self.notification.after(
                self.FADE_DELAY, lambda: self._fade_out(step - 1)
            )
        else:
            # 完全透明后销毁窗口
            self.notification.destroy()

            # 通知管理器当前通知已销毁
            if self.manager is not None:
                self.manager.current_notification = None

    def close(self):
        """立即关闭通知"""
        if self.notification.winfo_exists():
            self.notification.destroy()

            # 通知管理器当前通知已销毁
            if self.manager is not None:
                self.manager.current_notification = None


class NotificationManager:
    """通知管理器, 负责创建和管理通知"""

    def __init__(self, position=NotificationPosition.BOTTOM_RIGHT):
        """
        初始化通知管理器

        Args:
            position: 默认通知位置，默认为屏幕右下角显示
        """
        self.position = position # 默认通知位置
        self.current_notification = None  # 当前显示的通知对象

    def show_notification(
        self,
        title,
        message,
        notification_type=NotificationType.SUCCESS,
        duration=3000,
    ):
        """
        显示浮动通知

        Args:
            title: 通知标题
            message: 通知消息内容
            notification_type: 通知类型, 默认为成功通知
            duration: 通知显示持续时间 (毫秒) , 默认为3秒

        Returns:
            Notification: 创建的通知对象
        """
        # 如果已有通知存在，先关闭它
        if self.current_notification is not None:
            self.current_notification.close()

        # 创建新通知，并传入管理器引用
        self.current_notification = Notification(
            title,
            message,
            notification_type,
            duration,
            self.position,
            self,
        )

    def show_success(self, title, message, duration=3000):
        """显示成功通知"""
        return self.show_notification(
            title, message, NotificationType.SUCCESS, duration
        )

    def show_error(self, title, message, duration=3000):
        """显示错误通知"""
        return self.show_notification(
            title, message, NotificationType.ERROR, duration
        )

    def show_warning(self, title, message, duration=3000):
        """显示警告通知"""
        return self.show_notification(
            title, message, NotificationType.WARNING, duration
        )

    def show_info(self, title, message, duration=3000):
        """显示信息通知"""
        return self.show_notification(
            title, message, NotificationType.INFO, duration
        )