#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试通知组件处理长消息的能力
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
from ui.notification import NotificationManager

# 设置主题
ctk.set_appearance_mode("System")  # 可选: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")

class NotificationLongMessageTestApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 配置窗口
        self.title("通知长消息测试")
        self.geometry("700x500")
        
        # 创建主框架
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ctk.CTkLabel(
            main_frame,
            text="通知长消息测试",
            font=("Microsoft YaHei UI", 24, "bold")
        )
        title_label.pack(pady=(20, 30))
        
        # 说明文本
        info_label = ctk.CTkLabel(
            main_frame,
            text="点击按钮测试不同长度的消息通知\n通知将根据消息长度自动调整大小",
            font=("Microsoft YaHei UI", 14),
            text_color=("gray50", "gray50")
        )
        info_label.pack(pady=(0, 20))
        
        # 按钮框架
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=10)
        
        # 短消息按钮
        short_btn = ctk.CTkButton(
            button_frame,
            text="短消息",
            command=self.show_short_message,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        short_btn.pack(side="left", padx=10, pady=10)
        
        # 中等长度消息按钮
        medium_btn = ctk.CTkButton(
            button_frame,
            text="中等长度消息",
            command=self.show_medium_message,
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        medium_btn.pack(side="left", padx=10, pady=10)
        
        # 长消息按钮
        long_btn = ctk.CTkButton(
            button_frame,
            text="长消息",
            command=self.show_long_message,
            fg_color="#FF9800",
            hover_color="#f57c00"
        )
        long_btn.pack(side="left", padx=10, pady=10)
        
        # 超长消息按钮
        very_long_btn = ctk.CTkButton(
            button_frame,
            text="超长消息",
            command=self.show_very_long_message,
            fg_color="#F44336",
            hover_color="#d32f2f"
        )
        very_long_btn.pack(side="left", padx=10, pady=10)
        
        # 多行消息按钮
        multiline_btn = ctk.CTkButton(
            button_frame,
            text="多行消息",
            command=self.show_multiline_message,
            fg_color="#9C27B0",
            hover_color="#7B1FA2"
        )
        multiline_btn.pack(side="left", padx=10, pady=10)
    
    def show_short_message(self):
        """显示短消息"""
        NotificationManager.show_success(
            self,
            "操作成功",
            "文件已保存。"
        )
    
    def show_medium_message(self):
        """显示中等长度消息"""
        NotificationManager.show_info(
            self,
            "系统提示",
            "您有新的更新可用，建议您尽快更新以获得更好的体验和安全性。"
        )
    
    def show_long_message(self):
        """显示长消息"""
        NotificationManager.show_warning(
            self,
            "注意",
            "检测到系统资源使用率较高，建议关闭不必要的应用程序以释放资源。如果问题持续存在，请考虑重启系统或联系技术支持。"
        )
    
    def show_very_long_message(self):
        """显示超长消息"""
        NotificationManager.show_error(
            self,
            "严重错误",
            "系统遇到了一个严重错误，无法继续执行当前操作。错误代码：0x80070005。这可能是由于权限不足、文件损坏或系统配置问题导致的。请尝试以管理员身份运行应用程序，检查文件完整性，或重新安装应用程序。如果问题仍然存在，请收集错误日志并联系技术支持团队获取帮助。在问题解决之前，请避免执行可能影响系统稳定性的操作。"
        )
    
    def show_multiline_message(self):
        """显示多行消息"""
        NotificationManager.show_success(
            self,
            "操作完成",
            "以下操作已成功完成：\n1. 文件已保存到指定位置\n2. 备份已创建\n3. 日志已记录\n\n您可以继续使用应用程序。"
        )

if __name__ == "__main__":
    app = NotificationLongMessageTestApp()
    app.mainloop()