#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通知系统测试程序
用于测试notification.py中各种通知功能
"""

import customtkinter as ctk
import sys
import os
import time

# 添加ui目录到路径，以便导入notification模块
sys.path.append(os.path.join(os.path.dirname(__file__), 'ui'))
from notification import Notification, NotificationType, NotificationPosition


class NotificationTestApp:
    """通知测试应用程序"""
    
    def __init__(self):
        """初始化测试应用程序"""
        # 设置窗口
        self.root = ctk.CTk()
        self.root.title("通知系统测试")
        self.root.geometry("400x500")
        
        # 设置主题
        ctk.set_appearance_mode("System")  # 可选: "Light", "Dark", "System"
        ctk.set_default_color_theme("blue")  # 可选: "blue", "green", "dark-blue"
        
        # 防抖机制相关变量
        self.last_notification_time = 0
        self.debounce_interval = 0.5  # 500毫秒防抖间隔
        
        # 创建UI
        self.create_widgets()
    
    def create_widgets(self):
        """创建UI组件"""
        # 标题
        title_label = ctk.CTkLabel(
            self.root, 
            text="通知系统测试", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # 说明文本
        info_label = ctk.CTkLabel(
            self.root, 
            text="点击下方按钮测试不同类型的通知\n（已添加防抖机制，防止快速点击）", 
            font=ctk.CTkFont(size=14)
        )
        info_label.pack(pady=10)
        
        # 自定义消息输入框框架
        input_frame = ctk.CTkFrame(self.root)
        input_frame.pack(pady=10, padx=20, fill="x")
        
        # 输入框标签
        input_label = ctk.CTkLabel(input_frame, text="自定义消息内容:")
        input_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # 自定义消息输入框
        self.message_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="输入自定义通知消息...",
            height=30
        )
        self.message_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # 按钮框架
        button_frame = ctk.CTkFrame(self.root)
        button_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # 成功通知按钮
        success_btn = ctk.CTkButton(
            button_frame,
            text="成功通知",
            command=self.test_success_notification,
            height=40,
            corner_radius=8,
            fg_color=("green", "darkgreen"),
            hover_color=("darkgreen", "green")
        )
        success_btn.pack(pady=10, padx=20, fill="x")
        
        # 错误通知按钮
        error_btn = ctk.CTkButton(
            button_frame,
            text="错误通知",
            command=self.test_error_notification,
            height=40,
            corner_radius=8,
            fg_color=("red", "darkred"),
            hover_color=("darkred", "red")
        )
        error_btn.pack(pady=10, padx=20, fill="x")
        
        # 警告通知按钮
        warning_btn = ctk.CTkButton(
            button_frame,
            text="警告通知",
            command=self.test_warning_notification,
            height=40,
            corner_radius=8,
            fg_color=("orange", "darkorange"),
            hover_color=("darkorange", "orange")
        )
        warning_btn.pack(pady=10, padx=20, fill="x")
        
        # 信息通知按钮
        info_btn = ctk.CTkButton(
            button_frame,
            text="信息通知",
            command=self.test_info_notification,
            height=40,
            corner_radius=8,
            fg_color=("blue", "darkblue"),
            hover_color=("darkblue", "blue")
        )
        info_btn.pack(pady=10, padx=20, fill="x")
        
        # 多通知测试按钮
        multi_btn = ctk.CTkButton(
            button_frame,
            text="多通知测试",
            command=self.test_multiple_notifications,
            height=40,
            corner_radius=8,
            fg_color=("purple", "darkviolet"),
            hover_color=("darkviolet", "purple")
        )
        multi_btn.pack(pady=10, padx=20, fill="x")
        
        # 清除所有通知按钮
        clear_btn = ctk.CTkButton(
            button_frame,
            text="清除所有通知",
            command=self.clear_all_notifications,
            height=40,
            corner_radius=8,
            fg_color=("gray", "darkgray"),
            hover_color=("darkgray", "gray")
        )
        clear_btn.pack(pady=10, padx=20, fill="x")
        
        # 设置框架
        settings_frame = ctk.CTkFrame(self.root)
        settings_frame.pack(pady=10, padx=20, fill="x")
        
        # 通知位置选择
        position_label = ctk.CTkLabel(settings_frame, text="通知位置:")
        position_label.pack(side="left", padx=10)
        
        self.position_var = ctk.StringVar(value="BOTTOM_RIGHT")
        position_menu = ctk.CTkOptionMenu(
            settings_frame,
            values=["TOP_LEFT", "TOP_CENTER", "TOP_RIGHT", "BOTTOM_LEFT", "BOTTOM_RIGHT", "CENTER"],
            variable=self.position_var,
            command=self.change_notification_position
        )
        position_menu.pack(side="left", padx=10)
    
    def _check_debounce(self):
        """检查防抖机制，返回是否允许创建新通知"""
        current_time = time.time()
        if current_time - self.last_notification_time < self.debounce_interval:
            return False
        self.last_notification_time = current_time
        return True
    
    def test_success_notification(self):
        """测试成功通知"""
        if not self._check_debounce():
            return
        # 获取自定义消息，如果为空则使用默认消息
        custom_message = self.message_entry.get().strip()
        message = custom_message if custom_message else "文件已成功保存到磁盘。"
        Notification.show_success("操作成功", message)
    
    def test_error_notification(self):
        """测试错误通知"""
        if not self._check_debounce():
            return
        # 获取自定义消息，如果为空则使用默认消息
        custom_message = self.message_entry.get().strip()
        message = custom_message if custom_message else "无法保存文件，请检查磁盘空间和文件权限。"
        Notification.show_error("操作失败", message)
    
    def test_warning_notification(self):
        """测试警告通知"""
        if not self._check_debounce():
            return
        # 获取自定义消息，如果为空则使用默认消息
        custom_message = self.message_entry.get().strip()
        message = custom_message if custom_message else "文件已存在，继续操作将覆盖原有内容。"
        Notification.show_warning("注意", message)
    
    def test_info_notification(self):
        """测试信息通知"""
        if not self._check_debounce():
            return
        # 获取自定义消息，如果为空则使用默认消息
        custom_message = self.message_entry.get().strip()
        message = custom_message if custom_message else "您可以使用快捷键 Ctrl+S 快速保存文件。"
        Notification.show_info("提示", message)
    
    def test_multiple_notifications(self):
        """测试多个通知同时显示"""
        # 设置最大通知数量为5，以便测试
        Notification.set_max_notifications(5)
        
        # 创建多个不同类型的通知
        Notification.show_success("多通知测试 1", "这是第一个通知")
        Notification.show_error("多通知测试 2", "这是第二个通知")
        Notification.show_warning("多通知测试 3", "这是第三个通知")
        Notification.show_info("多通知测试 4", "这是第四个通知")
        Notification.show_success("多通知测试 5", "这是第五个通知")
        
        # 恢复默认最大通知数量
        Notification.set_max_notifications(3)
    
    def clear_all_notifications(self):
        """清除所有通知"""
        Notification.close_all()
    
    def change_notification_position(self, position):
        """更改通知位置"""
        if position == "TOP_LEFT":
            Notification.set_default_position(NotificationPosition.TOP_LEFT)
        elif position == "TOP_CENTER":
            Notification.set_default_position(NotificationPosition.TOP_CENTER)
        elif position == "TOP_RIGHT":
            Notification.set_default_position(NotificationPosition.TOP_RIGHT)
        elif position == "BOTTOM_LEFT":
            Notification.set_default_position(NotificationPosition.BOTTOM_LEFT)
        elif position == "BOTTOM_RIGHT":
            Notification.set_default_position(NotificationPosition.BOTTOM_RIGHT)
        elif position == "CENTER":
            Notification.set_default_position(NotificationPosition.CENTER)
    
    def run(self):
        """运行应用程序"""
        self.root.mainloop()


if __name__ == "__main__":
    # 创建并运行测试应用程序
    app = NotificationTestApp()
    app.run()