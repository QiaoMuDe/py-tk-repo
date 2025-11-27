#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通知组件模块
提供各种通知样式的UI组件，包括成功通知、错误通知、警告通知等
"""

import customtkinter as ctk
from config.config_manager import config_manager


class NotificationType:
    """通知类型枚举"""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class NotificationManager:
    """通知管理器，负责显示各种类型的通知"""

    # 通知组件字体大小配置
    ICON_FONT_SIZE = 25  # 图标字体大小
    TITLE_FONT_SIZE = 18  # 标题字体大小
    MESSAGE_FONT_SIZE = 15  # 消息字体大小

    @staticmethod
    def show_notification(
        parent,
        title,
        message,
        notification_type=NotificationType.SUCCESS,
        duration=3000,
    ):
        """
        显示浮动通知

        Args:
            parent: 父窗口
            title: 通知标题
            message: 通知消息内容
            notification_type: 通知类型，默认为成功通知
            duration: 通知显示持续时间（毫秒），默认为3秒
        """
        # 创建通知窗口
        notification = ctk.CTkToplevel(parent)
        notification.title("")
        notification.geometry("320x100")
        notification.resizable(False, False)

        # 设置窗口属性
        notification.overrideredirect(True)  # 移除窗口边框
        notification.attributes("-topmost", True)  # 始终置顶
        
        # 设置窗口背景为透明（使用tkinter的属性）
        notification.attributes("-transparentcolor", notification["bg"])

        # 获取父窗口位置和尺寸
        parent.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        # parent_height = parent.winfo_height()

        # 计算通知窗口位置（在父窗口上方居中）
        notification_width = 320
        notification_height = 100
        
        # 计算父窗口的中心点
        parent_center_x = parent_x + parent_width // 2
        
        # 计算通知窗口的x坐标（使其在父窗口上水平居中）
        x = parent_center_x - notification_width // 2
        
        # 计算通知窗口的y坐标（在父窗口上方，留出20像素的间距）
        y = parent_y - notification_height - 20
        
        # 如果通知窗口会超出屏幕顶部，则显示在父窗口内部顶部
        if y < 0:
            y = 20  # 距离屏幕顶部20像素

        # 确保通知窗口不会超出屏幕左右边界
        screen_width = parent.winfo_screenwidth()
        if x < 10:
            x = 10
        elif x + notification_width > screen_width - 10:
            x = screen_width - notification_width - 10

        # 设置窗口位置
        notification.geometry(f"{notification_width}x{notification_height}+{x}+{y}")

        # 创建通知内容
        font_config = config_manager.get_font_config("components")
        font_family = font_config.get("font", "Microsoft YaHei UI")

        # 根据通知类型获取颜色配置
        colors = NotificationManager._get_notification_colors(notification_type)

        # 主框架 - 使用圆角设计，设置为透明背景
        main_frame = ctk.CTkFrame(
            notification,
            corner_radius=15,
            fg_color="transparent",
            border_width=0,
        )
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # 内容框架 - 实际的通知容器
        content_frame = ctk.CTkFrame(
            main_frame,
            corner_radius=15,
            fg_color=colors["bg"],
            border_width=2,
            border_color=colors["border"],
        )
        content_frame.pack(fill="both", expand=True)

        # 内部内容框架 - 包含图标、标题和消息
        inner_content_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        inner_content_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # 左侧彩色指示条 - 垂直条，与内容框架高度一致
        indicator_frame = ctk.CTkFrame(
            inner_content_frame, 
            width=5, 
            corner_radius=3, 
            fg_color=colors["indicator"]
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
            font=(font_family, NotificationManager.ICON_FONT_SIZE, "bold"),
            text_color=colors["icon_color"],
        )
        icon_label.pack(side="left", padx=(0, 10))

        # 标题标签
        title_label = ctk.CTkLabel(
            header_frame,
            text=title,
            font=(font_family, NotificationManager.TITLE_FONT_SIZE, "bold"),
            text_color=colors["title"],
        )
        title_label.pack(side="left")

        # 消息标签
        msg_label = ctk.CTkLabel(
            right_content_frame,
            text=message,
            font=(font_family, NotificationManager.MESSAGE_FONT_SIZE),
            text_color=colors["message"],
            wraplength=250,
        )
        msg_label.pack(anchor="w", pady=(5, 0))

        # 设置窗口初始透明度为0（完全透明）
        notification.attributes("-alpha", 0)

        # 淡入效果
        def fade_in(step=0):
            if step <= 10:
                notification.attributes("-alpha", step / 10)
                notification.after(30, lambda: fade_in(step + 1))
            else:
                # 淡入完成后，等待指定时间后淡出
                notification.after(duration, fade_out)

        # 淡出效果
        def fade_out(step=10):
            if step > 0:
                notification.attributes("-alpha", step / 10)
                notification.after(30, lambda: fade_out(step - 1))
            else:
                # 完全透明后销毁窗口
                notification.destroy()

        # 开始淡入动画
        fade_in()

    @staticmethod
    def _get_notification_colors(notification_type):
        """
        根据通知类型获取颜色配置

        Args:
            notification_type: 通知类型

        Returns:
            dict: 包含各种颜色配置的字典
        """
        if notification_type == NotificationType.SUCCESS:
            return {
                "bg": ("#ffffff", "#1e1e1e"),
                "border": ("#d0d0d0", "#505050"),
                "indicator": ("#4CAF50", "#45a049"),
                "icon": "✓",
                "icon_color": ("#4CAF50", "#45a049"),
                "title": ("#212121", "#ffffff"),
                "message": ("#424242", "#e0e0e0"),
            }
        elif notification_type == NotificationType.ERROR:
            return {
                "bg": ("#ffffff", "#1e1e1e"),
                "border": ("#d0d0d0", "#505050"),
                "indicator": ("#F44336", "#d32f2f"),
                "icon": "✕",
                "icon_color": ("#F44336", "#d32f2f"),
                "title": ("#212121", "#ffffff"),
                "message": ("#424242", "#e0e0e0"),
            }
        elif notification_type == NotificationType.WARNING:
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

    @staticmethod
    def show_success(parent, title, message, duration=3000):
        """显示成功通知"""
        NotificationManager.show_notification(
            parent, title, message, NotificationType.SUCCESS, duration
        )

    @staticmethod
    def show_error(parent, title, message, duration=3000):
        """显示错误通知"""
        NotificationManager.show_notification(
            parent, title, message, NotificationType.ERROR, duration
        )

    @staticmethod
    def show_warning(parent, title, message, duration=3000):
        """显示警告通知"""
        NotificationManager.show_notification(
            parent, title, message, NotificationType.WARNING, duration
        )

    @staticmethod
    def show_info(parent, title, message, duration=3000):
        """显示信息通知"""
        NotificationManager.show_notification(
            parent, title, message, NotificationType.INFO, duration
        )
