#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通知组件模块
提供各种通知样式的UI组件, 包括成功通知、错误通知、警告通知等
"""

import customtkinter as ctk


class NotificationType:
    """通知类型枚举"""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class NotificationManager:
    """通知管理器, 负责显示各种类型的通知"""

    # 通知组件字体大小配置
    ICON_FONT_SIZE = 25  # 图标字体大小
    TITLE_FONT_SIZE = 18  # 标题字体大小
    MESSAGE_FONT_SIZE = 15  # 消息字体大小

    @staticmethod
    def show_notification(
        title="",
        message="",
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
        """
        # 创建通知窗口
        notification = ctk.CTkToplevel()
        notification.title("")
        notification.geometry("320x100")
        notification.resizable(False, False)

        # 设置窗口属性
        notification.overrideredirect(True)  # 移除窗口边框
        notification.attributes("-topmost", True)  # 始终置顶

        # 计算通知窗口位置 (在屏幕上方居中) 
        screen_width = notification.winfo_screenwidth()
        screen_height = notification.winfo_screenheight()
        
        notification_width = 320
        notification_height = 100
        x = (screen_width // 2) - (notification_width // 2)
        y = 50  # 距离屏幕顶部50像素

        # 设置窗口位置
        notification.geometry(f"{notification_width}x{notification_height}+{x}+{y}")

        # 创建通知内容框架
        font_family = "Microsoft YaHei UI"

        # 根据通知类型获取颜色配置
        colors = NotificationManager._get_notification_colors(notification_type)

        # 主框架 - 使用圆角设计
        main_frame = ctk.CTkFrame(
            notification,
            corner_radius=15,
            fg_color=colors["bg"],
            border_width=2,
            border_color=colors["border"],
        )
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # 顶部彩色指示条
        indicator_frame = ctk.CTkFrame(
            main_frame, height=5, corner_radius=0, fg_color=colors["indicator"]
        )
        indicator_frame.pack(fill="x", ipady=0)
        indicator_frame.pack_propagate(False)

        # 内容框架
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # 图标和标题框架
        header_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
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
            content_frame,
            text=message,
            font=(font_family, NotificationManager.MESSAGE_FONT_SIZE),
            text_color=colors["message"],
            wraplength=280,
        )
        msg_label.pack(anchor="w", pady=(5, 0))

        # 设置窗口初始透明度为0 (完全透明) 
        notification.attributes("-alpha", 0)

        # 开始淡入动画
        NotificationManager._fade_in(notification, duration)

    @staticmethod
    def _fade_in(notification, duration, step=0):
        """
        淡入动画效果

        Args:
            notification: 通知窗口对象
            duration: 通知显示持续时间 (毫秒) 
            step: 当前淡入步骤
        """
        if step <= 10:
            notification.attributes("-alpha", step / 10)
            notification.after(30, lambda: NotificationManager._fade_in(notification, duration, step + 1))
        else:
            # 淡入完成后, 等待指定时间后淡出
            notification.after(duration, lambda: NotificationManager._fade_out(notification))

    @staticmethod
    def _fade_out(notification, step=10):
        """
        淡出动画效果

        Args:
            notification: 通知窗口对象
            step: 当前淡出步骤
        """
        if step > 0:
            notification.attributes("-alpha", step / 10)
            notification.after(30, lambda: NotificationManager._fade_out(notification, step - 1))
        else:
            # 完全透明后销毁窗口
            notification.destroy()

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
    def show_success(title="成功", message="操作成功完成", duration=3000):
        """
        显示成功通知

        Args:
            title: 通知标题, 默认为"成功"
            message: 通知消息内容, 默认为"操作成功完成"
            duration: 通知显示持续时间 (毫秒) , 默认为3秒
        """
        NotificationManager.show_notification(title, message, NotificationType.SUCCESS, duration)

    @staticmethod
    def show_error(title="错误", message="操作发生错误", duration=3000):
        """
        显示错误通知

        Args:
            title: 通知标题, 默认为"错误"
            message: 通知消息内容, 默认为"操作发生错误"
            duration: 通知显示持续时间 (毫秒) , 默认为3秒
        """
        NotificationManager.show_notification(title, message, NotificationType.ERROR, duration)

    @staticmethod
    def show_warning(title="警告", message="请注意潜在问题", duration=3000):
        """
        显示警告通知

        Args:
            title: 通知标题, 默认为"警告"
            message: 通知消息内容, 默认为"请注意潜在问题"
            duration: 通知显示持续时间 (毫秒) , 默认为3秒
        """
        NotificationManager.show_notification(title, message, NotificationType.WARNING, duration)

    @staticmethod
    def show_info(title="信息", message="请查看此信息", duration=3000):
        """
        显示信息通知

        Args:
            title: 通知标题, 默认为"信息"
            message: 通知消息内容, 默认为"请查看此信息"
            duration: 通知显示持续时间 (毫秒) , 默认为3秒
        """
        NotificationManager.show_notification(title, message, NotificationType.INFO, duration)