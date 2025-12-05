#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UI初始化模块
该模块负责处理应用程序UI组件的初始化过程, 包括主题设置、窗口配置、UI组件创建等
"""

import customtkinter as ctk
import tkinter as tk
from config.config_manager import config_manager
from ui.menu import create_menu
from ui.toolbar import Toolbar
from ui.status_bar import StatusBar
from ui.line_number_canvas import LineNumberCanvas
from ui.notification import Notification, NotificationPosition


class UIInitializer:
    """UI初始化器类 - 负责应用程序UI组件的初始化过程"""

    def __init__(self, app):
        """
        初始化UI初始化器

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

    def init_window_properties(self):
        """初始化窗口基本属性"""
        # 设置窗口标题
        self.app.title("QuickEdit++")

        # 获取窗口大小配置
        window_width = config_manager.get("app.window_width", 1000)
        window_height = config_manager.get("app.window_height", 700)

        # 设置居中显示
        self.app.center_window(self.app, window_width, window_height)

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
        """初始化文本编辑区域 - 使用内部滚动条"""
        # 创建文本编辑区域框架
        self.app.text_frame = ctk.CTkFrame(self.app)
        self.app.text_frame.grid(row=1, column=0, sticky="nsew")
        # 设置网格权重，确保子组件能够正确填充
        self.app.text_frame.grid_columnconfigure(1, weight=1)  # 文本区域列可扩展
        self.app.text_frame.grid_columnconfigure(0, weight=0)  # 行号列固定
        self.app.text_frame.grid_rowconfigure(0, weight=1)  # 文本区域行可扩展

        # 获取自动换行设置
        auto_wrap = config_manager.get("text_editor.auto_wrap", True)
        wrap_mode = "word" if auto_wrap else "none"

        # 创建文本编辑区域 - 启用内部滚动条
        self.app.text_area = ctk.CTkTextbox(
            self.app.text_frame,  # 父容器
            wrap=wrap_mode,  # 换行模式
            undo=True,  # 启用撤销功能
            font=self.app.current_font,  # 字体设置
            border_spacing=5,  # 边框间距
            maxundo=config_manager.get("text_editor.max_undo", 50),  # 最大撤销次数
            spacing1=5,  # 第一行上方的额外间距
            spacing2=3,  # 行之间的额外间距
            activate_scrollbars=True,  # 启用内置滚动条
            insertwidth=config_manager.get(
                "text_editor.cursor_width", 5
            ),  # 光标宽度设置
        )

        # 设置初始滚动条检查更新显示时间为50毫秒
        self.app.text_area._scrollbar_update_time = 50

        # 设置内部垂直滚动条的宽度为20像素
        self.app.text_area._y_scrollbar.configure(width=20)
        # 设置内部水平滚动条的高度为15像素
        self.app.text_area._x_scrollbar.configure(height=15)

        # 光标行高亮相关变量
        self.app.current_highlighted_line = None

        # 创建行号侧边栏
        self.app.line_number_canvas = LineNumberCanvas(
            self.app.text_frame,
            text_widget=self.app.text_area,
            width=60,  # 增加初始宽度，与LineNumberCanvas默认值保持一致
        )

        # 放置行号侧边栏和文本编辑区域 - 使用grid布局
        self.app.line_number_canvas.grid(row=0, column=0, sticky="nsw")
        self.app.text_area.grid(row=0, column=1, sticky="nsew")

        # 确保文本框完全填充，没有额外的边距
        self.app.text_area.configure(border_width=0)
        self.app.text_frame.configure(border_width=0)

        # 设置选中背景色为最高优先级，防止被其他背景色覆盖
        # 使用底层textbox的tag_configure方法设置sel标签的背景色
        # sel标签是Text组件内置的选中标签, 设置为最高优先级
        self.app.text_area._textbox.tag_configure(
            "sel",
            background="#0078D7",  # Windows风格的选中蓝色
            foreground="white",  # 选中文字为白色
        )

        # 再次设置选中样式，确保优先级最高（在所有语法高亮标签之后）
        # 这个调用会在语法高亮设置之后执行，确保选中样式始终可见
        def ensure_selection_visibility():
            """确保选中文本始终可见，不被语法高亮覆盖"""
            self.app.text_area._textbox.tag_raise("sel")

        # 绑定事件，确保在选中状态改变时提高选中标签的优先级
        self.app.text_area._textbox.bind(
            "<<Selection>>", lambda e: ensure_selection_visibility()
        )

        # 初始调用一次，确保初始状态下选中样式优先级最高
        ensure_selection_visibility()

        # 根据配置决定是否显示行号栏
        if self.app.line_numbers_var.get():
            self.app.line_number_canvas.grid(row=0, column=0, sticky="nsw")
        else:
            self.app.line_number_canvas.grid_forget()

    def init_menu_bar(self):
        """初始化菜单栏"""
        # 创建菜单栏
        self.app.menu_bar = create_menu(self.app)
        self.app.config(menu=self.app.menu_bar)

    def init_read_only_mode(self):
        """设置初始只读模式状态"""
        if self.app.is_read_only:
            # 设置为只读模式
            self.app.text_area.configure(state="disabled")
            # 更新工具栏按钮外观
            self.app.toolbar.readonly_button.configure(
                fg_color="#FF6B6B", hover_color="#FF5252"
            )

    def init_notification(self):
        """初始化通知组件"""
        # 初始化通知组件，设置为编辑器的属性
        self.app.nm = Notification

        # 从配置管理器获取通知配置并应用到通知组件
        notification_config = config_manager.get_component_config("notification")
        if notification_config:
            # 设置通知位置
            position = notification_config.get("position", "bottom_right")
            # 使用NotificationPosition.from_string方法将字符串转换为枚举值
            Notification.set_default_position(
                NotificationPosition.from_string(position)
            )

            # 设置通知持续时间
            duration = notification_config.get("duration", 3000)
            Notification.set_default_duration(duration)

    def initialize_ui(self):
        """执行完整的UI初始化流程"""
        # 按顺序执行UI初始化步骤
        self.init_app_theme()
        self.init_window_properties()
        self.init_font_settings()
        self.init_window_layout()
        self.init_toolbar()
        self.init_status_bar()
        self.init_text_area()
        self.init_menu_bar()
        self.init_read_only_mode()
        self.init_notification()

        # 初始化后300ms绘制行号
        self.app.after(300, self.app.line_number_canvas.draw_line_numbers)
