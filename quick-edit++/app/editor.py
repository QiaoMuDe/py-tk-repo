#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
编辑器主应用类
该模块负责组装所有UI组件和核心功能，提供统一的应用程序接口
"""

import customtkinter as ctk
import sys
import os
import time
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config_manager import config_manager
from ui.main_window import MainWindow
from ui.menu import create_menu
from ui.toolbar import Toolbar
from ui.status_bar import StatusBar


class QuickEditApp:
    """QuickEdit++ 主应用类"""
    
    def __init__(self):
        """初始化应用"""
        # 设置应用外观模式
        theme_mode = config_manager.get("app.theme_mode", "light")
        ctk.set_appearance_mode(theme_mode)  # 可选: "light", "dark", "system"
        
        color_theme = config_manager.get("app.color_theme", "blue")
        ctk.set_default_color_theme(color_theme)  # 可选: "blue", "green", "dark-blue"
        
        # 启用DPI缩放支持
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception as e:
            print(f"警告: 无法启用DPI缩放支持: {e}")
        
        # 创建主应用窗口
        self.main_window = MainWindow(self)
        self.main_window.title("QuickEdit++")
        
        # 获取窗口大小配置
        window_width = config_manager.get("app.window_width", 1000)
        window_height = config_manager.get("app.window_height", 700)
        self.main_window.geometry(f"{window_width}x{window_height}")
        
        # 自动保存相关属性
        self.auto_save_enabled = config_manager.get("saving.auto_save", True)
        self.auto_save_interval = config_manager.get("saving.auto_save_interval", 30)  # 默认30秒
        self.last_auto_save_time = None
        self.auto_save_job = None
        
        # 创建菜单栏
        self.menu_bar = create_menu(self.main_window, self)
        self.main_window.config(menu=self.menu_bar)
        
        # 创建工具栏
        self.toolbar = Toolbar(self.main_window, self)
        if config_manager.get("toolbar.show_toolbar", True):
            self.toolbar.pack(side="top", fill="x")
        
        # 创建状态栏并放置在主窗口底部
        self.status_bar = StatusBar(self.main_window, self)
        if config_manager.get("status_bar.show_status_bar", True):
            self.status_bar.pack(side="bottom", fill="x")
        
        # 设置状态栏引用以便其他组件可以更新状态
        self.main_window.status_bar = self.status_bar
        
        # 确保文本编辑区域在工具栏和状态栏之间
        self.main_window.text_frame.pack(after=self.toolbar, before=self.status_bar, fill="both", expand=True)
        
        # 初始化状态栏显示
        self._init_status_bar()
        
        # 启动自动保存功能
        self._start_auto_save()
        
    def _init_status_bar(self):
        """初始化状态栏显示"""
        # 设置初始状态信息
        self.status_bar.set_status_info()
        
        # 设置初始自动保存信息
        self.status_bar.set_auto_save_info("从未")
        
        # 设置初始文件信息
        self.status_bar.set_file_info()
        
        # 设置自动保存间隔
        self.status_bar.set_auto_save_interval(self.auto_save_interval)
        
    def _start_auto_save(self):
        """启动自动保存功能"""
        if self.auto_save_enabled:
            self.status_bar.set_auto_save_enabled(True)
            self._schedule_auto_save()
        else:
            self.status_bar.set_auto_save_enabled(False)
            
    def _schedule_auto_save(self):
        """安排下一次自动保存"""
        if self.auto_save_enabled:
            # 取消之前的自动保存任务
            if self.auto_save_job:
                self.main_window.after_cancel(self.auto_save_job)
                
            # 安排新的自动保存任务
            self.auto_save_job = self.main_window.after(
                self.auto_save_interval * 1000,  # 转换为毫秒
                self._perform_auto_save
            )
            
    def _perform_auto_save(self):
        """执行自动保存操作"""
        if self.auto_save_enabled:
            # 这里应该实现实际的保存逻辑
            # 目前只是更新状态栏显示
            self.last_auto_save_time = datetime.now().strftime("%H:%M:%S")
            self.status_bar.set_auto_save_info("成功")
            
            # 安排下一次自动保存
            self._schedule_auto_save()
            
    def _toggle_auto_save(self):
        """切换自动保存功能"""
        self.auto_save_enabled = not self.auto_save_enabled
        if self.auto_save_enabled:
            self.status_bar.set_auto_save_enabled(True)
            self._schedule_auto_save()
        else:
            # 取消自动保存任务
            if self.auto_save_job:
                self.main_window.after_cancel(self.auto_save_job)
                self.auto_save_job = None
            self.status_bar.set_auto_save_enabled(False)
            
    def run(self):
        """运行应用"""
        self.main_window.mainloop()