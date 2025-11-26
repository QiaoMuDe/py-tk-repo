#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通知组件测试模块
提供测试界面，用于测试各种通知效果
"""

import sys
import os

# 添加项目路径到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# 导入customtkinter
try:
    import customtkinter as ctk
except ImportError:
    # 如果无法导入，尝试使用本地customtkinter
    sys.path.insert(0, os.path.join(parent_dir, "customtkinter"))
    import customtkinter as ctk

from ui.notification import NotificationManager, NotificationType


class NotificationTestApp:
    """通知测试应用"""

    def __init__(self):
        # 设置外观模式和主题
        ctk.set_appearance_mode("System")  # 可选: "System", "Dark", "Light"
        ctk.set_default_color_theme("blue")  # 可选: "blue", "green", "dark-blue"

        # 创建主窗口
        self.root = ctk.CTk()
        self.root.title("通知组件测试")
        self.root.geometry("600x500")

        # 创建界面
        self.create_widgets()

        # 定时器ID
        self.timer_id = None
        self.is_timer_running = False

    def create_widgets(self):
        """创建界面组件"""
        # 标题
        title_label = ctk.CTkLabel(
            self.root, text="通知组件测试界面", font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)

        # 说明文本
        info_label = ctk.CTkLabel(
            self.root,
            text="点击下方按钮测试不同类型的通知效果",
            font=ctk.CTkFont(size=14),
        )
        info_label.pack(pady=10)

        # 按钮框架
        button_frame = ctk.CTkFrame(self.root)
        button_frame.pack(pady=20, padx=20, fill="x")

        # 成功通知按钮
        success_btn = ctk.CTkButton(
            button_frame,
            text="成功通知",
            command=self.show_success_notification,
            fg_color=("#4CAF50", "#45a049"),
            hover_color=("#45a049", "#3d8b40"),
        )
        success_btn.pack(pady=10, padx=20, fill="x")

        # 错误通知按钮
        error_btn = ctk.CTkButton(
            button_frame,
            text="错误通知",
            command=self.show_error_notification,
            fg_color=("#F44336", "#d32f2f"),
            hover_color=("#d32f2f", "#b71c1c"),
        )
        error_btn.pack(pady=10, padx=20, fill="x")

        # 警告通知按钮
        warning_btn = ctk.CTkButton(
            button_frame,
            text="警告通知",
            command=self.show_warning_notification,
            fg_color=("#FF9800", "#f57c00"),
            hover_color=("#f57c00", "#e65100"),
        )
        warning_btn.pack(pady=10, padx=20, fill="x")

        # 信息通知按钮
        info_btn = ctk.CTkButton(
            button_frame,
            text="信息通知",
            command=self.show_info_notification,
            fg_color=("#2196F3", "#1976D2"),
            hover_color=("#1976D2", "#0D47A1"),
        )
        info_btn.pack(pady=10, padx=20, fill="x")

        # 分隔线
        separator = ctk.CTkFrame(self.root, height=2)
        separator.pack(fill="x", padx=40, pady=20)

        # 自动测试框架
        auto_test_frame = ctk.CTkFrame(self.root)
        auto_test_frame.pack(pady=10, padx=20, fill="x")

        # 自动测试标题
        auto_test_label = ctk.CTkLabel(
            auto_test_frame, text="自动测试", font=ctk.CTkFont(size=18, weight="bold")
        )
        auto_test_label.pack(pady=10)

        # 自动测试说明
        auto_test_info = ctk.CTkLabel(
            auto_test_frame,
            text="点击开始按钮，每隔1秒显示一种不同类型的通知",
            font=ctk.CTkFont(size=12),
        )
        auto_test_info.pack(pady=5)

        # 自动测试按钮框架
        auto_btn_frame = ctk.CTkFrame(auto_test_frame)
        auto_btn_frame.pack(pady=10)

        # 开始自动测试按钮
        self.start_btn = ctk.CTkButton(
            auto_btn_frame,
            text="开始自动测试",
            command=self.start_auto_test,
            fg_color=("#4CAF50", "#45a049"),
            hover_color=("#45a049", "#3d8b40"),
            width=120,
        )
        self.start_btn.pack(side="left", padx=10)

        # 停止自动测试按钮
        self.stop_btn = ctk.CTkButton(
            auto_btn_frame,
            text="停止自动测试",
            command=self.stop_auto_test,
            fg_color=("#F44336", "#d32f2f"),
            hover_color=("#d32f2f", "#b71c1c"),
            width=120,
            state="disabled",
        )
        self.stop_btn.pack(side="left", padx=10)

        # 当前通知类型标签
        self.current_type_label = ctk.CTkLabel(
            auto_test_frame, text="当前通知类型: 无", font=ctk.CTkFont(size=14)
        )
        self.current_type_label.pack(pady=10)

        # 通知类型列表（用于自动测试）
        self.notification_types = [
            (NotificationType.SUCCESS, "成功通知", "操作成功完成！"),
            (NotificationType.ERROR, "错误通知", "发生了一个错误！"),
            (NotificationType.WARNING, "警告通知", "请注意这个警告！"),
            (NotificationType.INFO, "信息通知", "这是一条信息通知。"),
        ]

        # 当前通知类型索引
        self.current_type_index = 0

    def show_success_notification(self):
        """显示成功通知"""
        NotificationManager.show_success(self.root, "操作成功", "文件保存成功！")

    def show_error_notification(self):
        """显示错误通知"""
        NotificationManager.show_error(self.root, "操作失败", "无法连接到服务器！")

    def show_warning_notification(self):
        """显示警告通知"""
        NotificationManager.show_warning(self.root, "注意", "文件已存在，将被覆盖！")

    def show_info_notification(self):
        """显示信息通知"""
        NotificationManager.show_info(self.root, "提示", "新版本可用，请更新软件！")

    def start_auto_test(self):
        """开始自动测试"""
        if not self.is_timer_running:
            self.is_timer_running = True
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.show_next_notification()

    def stop_auto_test(self):
        """停止自动测试"""
        if self.is_timer_running:
            self.is_timer_running = False
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
                self.timer_id = None
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            self.current_type_label.configure(text="当前通知类型: 无")

    def show_next_notification(self):
        """显示下一个通知"""
        if self.is_timer_running:
            # 获取当前通知类型
            notification_type, title, message = self.notification_types[
                self.current_type_index
            ]

            # 更新当前类型标签
            type_name = {
                NotificationType.SUCCESS: "成功通知",
                NotificationType.ERROR: "错误通知",
                NotificationType.WARNING: "警告通知",
                NotificationType.INFO: "信息通知",
            }.get(notification_type, "未知")

            self.current_type_label.configure(text=f"当前通知类型: {type_name}")

            # 显示通知
            NotificationManager.show_notification(
                self.root,
                title,
                message,
                notification_type,
                duration=1000,  # 1秒显示时间
            )

            # 更新索引
            self.current_type_index = (self.current_type_index + 1) % len(
                self.notification_types
            )

            # 设置下一个定时器
            self.timer_id = self.root.after(1000, self.show_next_notification)

    def run(self):
        """运行应用"""
        self.root.mainloop()


if __name__ == "__main__":
    app = NotificationTestApp()
    app.run()
