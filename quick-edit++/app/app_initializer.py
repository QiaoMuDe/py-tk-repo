#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
应用初始化模块
该模块负责处理应用程序的初始化过程，包括主题设置、窗口配置、UI组件创建等
"""

import customtkinter as ctk
import tkinter as tk
from config.config_manager import config_manager
from ui.menu import create_menu
from ui.toolbar import Toolbar
from ui.status_bar import StatusBar
from .file_operations import FileOperations
from .file_watcher import FileWatcher
from syntax_highlighter import SyntaxHighlighter


class AppInitializer:
    """应用初始化器类 - 负责应用程序的初始化过程"""

    def __init__(self, app):
        """
        初始化应用初始化器

        Args:
            app: QuickEditApp实例
        """
        self.app = app

    def init_app_theme(self):
        """初始化应用主题和外观设置"""
        # 设置应用外观模式
        theme_mode = config_manager.get("app.theme_mode", "light")
        ctk.set_appearance_mode(theme_mode)  # 可选: "light", "dark", "system"

        color_theme = config_manager.get("app.color_theme", "blue")
        ctk.set_default_color_theme(color_theme)  # 可选: "blue", "green", "dark-blue"

    def init_dpi_support(self):
        """启用DPI缩放支持"""
        try:
            from ctypes import windll

            windll.shcore.SetProcessDpiAwareness(1)
        except Exception as e:
            print(f"警告: 无法启用DPI缩放支持: {e}")

    def init_window_properties(self):
        """初始化窗口基本属性"""
        # 设置窗口标题
        self.app.title("QuickEdit++")

        # 获取窗口大小配置
        window_width = config_manager.get("app.window_width", 1200)
        window_height = config_manager.get("app.window_height", 800)

        # 设置窗口大小, 相对居中显示
        self.app.geometry(
            f"{window_width}x{window_height}+{window_width//2}+{window_height//3}"
        )

        # 设置最小窗口大小
        min_width = config_manager.get("app.min_width", 800)
        min_height = config_manager.get("app.min_height", 600)
        self.app.minsize(min_width, min_height)

        # 设置窗口关闭事件
        self.app.protocol("WM_DELETE_WINDOW", self.app._on_closing)

    def init_font_settings(self):
        """初始化字体设置"""
        font_config = config_manager.get_font_config("text_editor")
        self.app.current_font = ctk.CTkFont(
            family=font_config.get("font", "Microsoft YaHei UI"),
            size=font_config.get("font_size", 15),
            weight="bold" if font_config.get("font_bold", False) else "normal",
        )

    def init_file_attributes(self):
        """初始化文件相关属性"""
        # 初始化文件操作处理器
        self.app.file_ops = FileOperations(self.app)

        # 初始化文件监听器
        self.app.file_watcher = FileWatcher(self.app)

        # 初始化文件相关属性
        self.app.current_file_path = None  # 当前文件路径
        self.app.current_encoding = config_manager.get(
            "app.default_encoding", "UTF-8"
        )  # 当前文件编码
        self.app.current_line_ending = config_manager.get(
            "app.default_line_ending", "LF"
        )  # 从配置中读取默认换行符
        self.app.is_new_file = False  # 是否为新文件状态

        # 字符数缓存
        self.app._total_chars = 0  # 缓存的总字符数

        # 从配置文件中读取只读模式状态
        self.app.is_read_only = config_manager.get(
            "text_editor.read_only", False
        )  # 是否为只读模式

    def init_menu_variables(self):
        """初始化菜单状态变量"""
        # 初始化菜单状态变量，从配置管理器加载默认值

        # 初始化工具栏状态变量
        self.app.toolbar_var = tk.BooleanVar(
            value=config_manager.get("app.show_toolbar", True)
        )

        # 初始化自动换行状态变量
        self.app.auto_wrap_var = tk.BooleanVar(
            value=config_manager.get("text_editor.auto_wrap", True)
        )

        # 注意：auto_save_var 和 auto_save_interval_var 现在由 AutoSaveManager 类管理

        # 创建备份状态变量
        self.app.backup_var = tk.BooleanVar(
            value=config_manager.get("app.backup_enabled", False)
        )

        # 初始化窗口标题模式变量
        current_title_mode = config_manager.get("app.window_title_mode", "filename")
        self.app.title_mode_var = tk.StringVar(value=current_title_mode)

        # 初始化自动保存状态变量
        self.app.auto_save_var = tk.BooleanVar(
            value=self.app.auto_save_manager.auto_save_enabled
        )
        self.app.auto_save_interval_var = tk.StringVar(
            value=str(self.app.auto_save_manager.auto_save_interval)
        )

        # 初始化全屏模式状态
        self.app.fullscreen_var = tk.BooleanVar(value=False)  # 全屏模式状态变量
        self.app.is_fullscreen = False  # 全屏模式状态
        self.app.normal_geometry = None  # 正常窗口几何形状

        # 初始化行号显示状态变量
        self.app.line_numbers_var = tk.BooleanVar(
            value=config_manager.get("text_editor.show_line_numbers", True)
        )

    def init_window_layout(self):
        """初始化窗口布局配置"""
        # 配置主窗口的网格布局
        self.app.grid_columnconfigure(0, weight=1)
        self.app.grid_rowconfigure(1, weight=1)  # 文本区域所在行可扩展

        # 防止窗口大小变化时的重新计算，减少闪烁
        self.app.grid_propagate(False)

    def init_toolbar(self):
        """初始化工具栏"""
        # 创建工具栏
        if config_manager.get("app.show_toolbar", True):
            self.app.toolbar = Toolbar(self.app)
            self.app.toolbar.grid(row=0, column=0, sticky="ew")
        else:
            # 如果配置为不显示工具栏，仍然创建工具栏对象但不显示
            self.app.toolbar = Toolbar(self.app)
            # 不调用grid，因此工具栏不会显示

    def init_status_bar(self):
        """初始化状态栏"""
        # 创建状态栏并放置在主窗口底部，传入APP实例
        self.app.status_bar = StatusBar(self.app)
        if config_manager.get("status_bar.show_status_bar", True):
            self.app.status_bar.grid(row=2, column=0, sticky="ew")

    def init_text_area(self):
        """初始化文本编辑区域"""
        # 创建文本编辑区域框架 - 去掉圆角和内边距，避免阴影效果
        self.app.text_frame = ctk.CTkFrame(self.app)
        self.app.text_frame.grid(row=1, column=0, sticky="nsew")

        # 获取自动换行设置
        auto_wrap = config_manager.get("text_editor.auto_wrap", True)
        wrap_mode = "word" if auto_wrap else "none"

        # 创建文本编辑区域 - 去掉圆角，确保完全填充
        self.app.text_area = ctk.CTkTextbox(
            self.app.text_frame,  # 父容器
            wrap=wrap_mode,  # 换行模式
            undo=True,  # 启用撤销功能
            font=self.app.current_font,  # 字体设置
            border_spacing=3,  # 边框间距
            maxundo=config_manager.get("text_editor.max_undo", 50),  # 最大撤销次数
            spacing1=5,  # 第一行上方的额外间距
            spacing2=3,  # 行之间的额外间距
            activate_scrollbars=True,  # 启用滚动条激活
        )

        # 放置文本编辑区域
        self.app.text_area.pack(side="right", fill="both", expand=True, padx=0, pady=0)

        # 自定义滚动条宽度
        if hasattr(self.app.text_area, "_y_scrollbar"):
            self.app.text_area._y_scrollbar.configure(
                width=18
            )  # 设置垂直滚动条宽度为18像素

        # 光标行高亮相关变量
        self.app.current_highlighted_line = None

    def init_menu_bar(self):
        """初始化菜单栏"""
        # 创建菜单栏
        self.app.menu_bar = create_menu(self.app)
        self.app.config(menu=self.app.menu_bar)
        # 确保recent_files_menu属性存在于app实例中
        if not hasattr(self.app, "recent_files_menu"):
            self.app.recent_files_menu = None

    def init_read_only_mode(self):
        """设置初始只读模式状态"""
        if self.app.is_read_only:
            # 设置为只读模式
            self.app.text_area.configure(state="disabled")
            # 更新工具栏按钮外观
            self.app.toolbar.readonly_button.configure(
                fg_color="#FF6B6B", hover_color="#FF5252"
            )

    def init_syntax_highlighting(self):
        """初始化语法高亮功能"""
        # 创建语法高亮实例并关联到文本区域
        self.app.syntax_highlighter = SyntaxHighlighter(self.app.text_area)

    def initialize_app(self):
        """执行完整的应用初始化流程"""
        # 按顺序执行初始化步骤
        self.init_app_theme()
        self.init_dpi_support()

        # 初始化CTk主窗口 - 修复继承关系问题
        ctk.CTk.__init__(self.app)

        self.init_window_properties()
        self.init_font_settings()
        self.init_file_attributes()
        self.init_menu_variables()
        self.init_window_layout()
        self.init_toolbar()
        self.init_status_bar()
        self.init_text_area()
        self.init_menu_bar()
        self.init_syntax_highlighting()
        self.init_read_only_mode()

        # 注意：文件监听将在打开文件时启动，而不是在应用初始化时启动
