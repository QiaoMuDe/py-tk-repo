#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
编辑器主应用类
该模块直接实现主窗口功能，负责组装所有UI组件和核心功能，提供统一的应用程序接口
"""

import customtkinter as ctk
import tkinter as tk
import sys
import os
import time
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config_manager import config_manager
from ui.menu import create_menu
from ui.toolbar import Toolbar
from ui.status_bar import StatusBar


class QuickEditApp(ctk.CTk):
    """QuickEdit++ 主应用类 - 直接继承ctk.CTk作为主窗口"""

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

        # 初始化CTk主窗口
        super().__init__()

        # 设置窗口标题
        self.title("QuickEdit++")

        # 获取窗口大小配置
        window_width = config_manager.get("app.window_width", 1200)
        window_height = config_manager.get("app.window_height", 800)

        # 设置窗口大小, 相对居中显示
        self.geometry(f"{window_width}x{window_height}+{window_width//2}+{window_height//3}")

        # 设置最小窗口大小
        min_width = config_manager.get("app.min_width", 800)
        min_height = config_manager.get("app.min_height", 600)
        self.minsize(min_width, min_height)

        # 初始化字体设置
        font_config = config_manager.get_font_config("text_editor")
        self.current_font = ctk.CTkFont(
            family=font_config.get("font", "Consolas"),
            size=font_config.get("font_size", 12),
            weight="bold" if font_config.get("font_bold", False) else "normal",
        )

        # 设置窗口关闭事件
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        # 自动保存相关属性
        self.auto_save_enabled = config_manager.get("saving.auto_save", True)
        self.auto_save_interval = config_manager.get(
            "saving.auto_save_interval", 5
        )  # 默认5秒
        self.last_auto_save_time = None
        self.auto_save_job = None

        # 创建文本编辑区域框架 - 去掉圆角和内边距，避免阴影效果
        self.text_frame = ctk.CTkFrame(self)

        # 创建工具栏
        self.toolbar = Toolbar(self)
        if config_manager.get("toolbar.show_toolbar", True):
            self.toolbar.pack(side="top", fill="x")

        # 创建状态栏并放置在主窗口底部
        self.status_bar = StatusBar(self)
        if config_manager.get("status_bar.show_status_bar", True):
            self.status_bar.pack(side="bottom", fill="x")

        # 创建文本编辑区域 - 去掉圆角，确保完全填充
        self.text_area = ctk.CTkTextbox(
            self.text_frame, wrap="none", undo=True, font=self.current_font
        )
        self.text_area.pack(fill="both", expand=True, padx=0, pady=0)

        # 创建菜单栏
        self.menu_bar = create_menu(self)
        self.config(menu=self.menu_bar)

        # 确保文本编辑区域在工具栏和状态栏之间
        self.text_frame.pack(
            after=self.toolbar, before=self.status_bar, fill="both", expand=True
        )

        # 绑定文本区域事件
        self._bind_text_events()

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
                self.after_cancel(self.auto_save_job)

            # 安排新的自动保存任务
            self.auto_save_job = self.after(
                self.auto_save_interval * 1000, self._perform_auto_save  # 转换为毫秒
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

    def _on_closing(self):
        """窗口关闭事件处理"""
        # 这里可以添加保存确认等逻辑
        self.destroy()

    def _toggle_auto_save(self):
        """切换自动保存功能"""
        self.auto_save_enabled = not self.auto_save_enabled
        if self.auto_save_enabled:
            self.status_bar.set_auto_save_enabled(True)
            self._schedule_auto_save()
        else:
            # 取消自动保存任务
            if self.auto_save_job:
                self.after_cancel(self.auto_save_job)
                self.auto_save_job = None
            self.status_bar.set_auto_save_enabled(False)

    def update_font(self, font_info):
        """更新字体配置并保存到配置管理器

        Args:
            font_info: 字体配置字典，包含family、size等信息
        """
        # 保存字体配置到配置管理器
        config_manager.set_font_config("text_editor", font_info)
        config_manager.save_config()

        print(f"字体配置已保存: {font_info}")

    def _bind_text_events(self):
        """绑定文本区域事件"""
        # 绑定按键事件
        self.text_area.bind("<KeyRelease>", self._on_text_change)
        self.text_area.bind("<Button-1>", self._on_cursor_move)
        self.text_area.bind("<<Selection>>", self._on_selection_change)

        # 绑定鼠标滚轮事件
        self.text_area.bind("<MouseWheel>", self._on_cursor_move)

    def _on_text_change(self, event=None):
        """文本改变事件处理"""
        self._update_status_bar()

    def _on_cursor_move(self, event=None):
        """光标移动事件处理"""
        self._update_status_bar()

    def _on_selection_change(self, event=None):
        """选择内容改变事件处理"""
        self._update_status_bar()

    def _update_status_bar(self):
        """更新状态栏信息"""
        # 获取光标位置
        cursor_pos = self.text_area.index(ctk.INSERT)
        row, col = cursor_pos.split(".")
        row, col = int(row), int(col) + 1  # 转换为1基索引

        # 获取总字符数
        content = self.text_area.get("1.0", ctk.END)
        total_chars = len(content) - 1  # 减去末尾的换行符

        # 获取选中字符数
        try:
            selected_content = self.text_area.get(ctk.SEL_FIRST, ctk.SEL_LAST)
            selected_chars = len(selected_content)

            # 计算选中的行数
            selected_lines = selected_content.count("\n") + 1
        except tk.TclError:
            # 没有选中内容
            selected_chars = None
            selected_lines = None

        # 更新状态栏
        self.status_bar.set_status_info(
            row=row,
            col=col,
            total_chars=total_chars,
            selected_chars=selected_chars,
            selected_lines=selected_lines,
        )

    def run(self):
        """运行应用"""
        self.mainloop()
