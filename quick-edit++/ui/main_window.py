#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主窗口界面模块
"""

import customtkinter as ctk
import tkinter as tk
from config.config_manager import config_manager
from .toolbar import Toolbar
from .status_bar import StatusBar
from core.common_utils import set_window_min_size


class MainWindow(ctk.CTk):
    """主窗口类"""
    
    def __init__(self, app):
        """初始化主窗口"""
        super().__init__()
        
        # 保存应用实例引用
        self.app = app
        
        # 设置窗口标题
        self.title("QuickEdit++")
        
        # 获取窗口大小配置
        window_width = config_manager.get("app.window_width", 1200)
        window_height = config_manager.get("app.window_height", 800)
        
        # 设置窗口大小
        self.geometry(f"{window_width}x{window_height}")
        
        # 设置最小窗口大小
        min_width = config_manager.get("app.min_width", 800)
        min_height = config_manager.get("app.min_height", 600)
        set_window_min_size(self, min_width, min_height)
        
        # 初始化字体设置
        font_config = config_manager.get_font_config("text_editor")
        self.current_font = ctk.CTkFont(
            family=font_config.get("font", "Consolas"),
            size=font_config.get("font_size", 12),
            weight="bold" if font_config.get("font_bold", False) else "normal"
        )
        
        # 创建UI组件
        self._create_widgets()
        
        # 设置窗口关闭事件
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
    def _create_widgets(self):
        """创建主窗口中的基础框架"""
        # 创建文本编辑区域框架 - 去掉圆角和内边距，避免阴影效果
        self.text_frame = ctk.CTkFrame(self)
        self.text_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
    def _on_closing(self):
        """窗口关闭事件处理"""
        # 这里可以添加保存确认等逻辑
        self.destroy()
        
    def run(self):
        """运行主窗口"""
        self.mainloop()