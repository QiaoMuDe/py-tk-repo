#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
应用初始化模块
该模块负责处理应用程序的初始化过程，包括主题设置、窗口配置、UI组件创建等
"""

import customtkinter as ctk
import tkinter as tk
from config.config_manager import config_manager, APP_CONFIG_DIR
from ui.menu import create_menu
from ui.toolbar import Toolbar
from ui.status_bar import StatusBar
from .file_operations import FileOperations
from .file_watcher import FileWatcher
from syntax_highlighter import SyntaxHighlighter
from ui.line_number_canvas import LineNumberCanvas
from .find_replace_engine import FindReplaceEngine
from ctypes import windll
from loguru import logger
import os
from ui.notification import NotificationManager


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

        # 初始化文件属性菜单项索引，用于更新菜单项状态
        self.app.file_properties_menu_index = None

        # 初始化文件菜单对象引用
        self.app.file_menu = None

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
        self.app.normal_geometry = None  # 正常窗口几何形状

        # 初始化行号显示状态变量
        self.app.line_numbers_var = tk.BooleanVar(
            value=config_manager.get("text_editor.show_line_numbers", True)
        )

        # 初始化语法高亮相关状态变量
        # 获取语法高亮配置
        syntax_config = config_manager.get_component_config("syntax_highlighter")
        # 创建语法高亮启用状态变量
        self.app.syntax_highlight_var = tk.BooleanVar(
            value=syntax_config.get("enabled", True)
        )
        # 创建语法高亮模式状态变量
        # True表示渲染可见行，False表示渲染全部
        self.app.syntax_highlight_mode_var = tk.BooleanVar(
            value=syntax_config.get("render_visible_only", True)
        )

        # 初始化行号显示状态变量
        self.app.line_numbers_var = tk.BooleanVar(
            value=config_manager.get("text_editor.show_line_numbers", True)
        )

        # 初始化自动递增编号功能状态变量
        self.app.auto_increment_number_var = tk.BooleanVar(
            value=config_manager.get("text_editor.auto_increment_number", True)
        )

        # 初始化光标所在行高亮功能状态变量
        self.app.highlight_current_line_var = tk.BooleanVar(
            value=config_manager.get("text_editor.highlight_current_line", True)
        )

        # 初始化文件变更监控功能状态变量
        self.app.file_monitoring_var = tk.BooleanVar(
            value=config_manager.get("file_watcher.monitoring_enabled", True)
        )

        # 初始化静默重载模式状态变量
        self.app.silent_reload_var = tk.BooleanVar(
            value=config_manager.get("file_watcher.silent_reload", False)
        )

        # 初始化使用空格代替制表符的状态变量
        self.app.use_spaces_for_tab_var = tk.BooleanVar(
            value=config_manager.get("text_editor.use_spaces_for_tab", False)
        )

        # 初始化制表符宽度状态变量
        self.app.tab_width_var = tk.IntVar(
            value=config_manager.get("text_editor.tab_width", 1)
        )

        # 重新打开文件菜单实例
        self.app.reopen_file_menu = None

        # 创建保存副本菜单项索引，用于更新菜单项状态
        self.app.save_copy_menu_index = None

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
        self.app.text_frame.grid_rowconfigure(0, weight=1)

        # 获取自动换行设置
        auto_wrap = config_manager.get("text_editor.auto_wrap", True)
        wrap_mode = "word" if auto_wrap else "none"

        # 创建文本编辑区域 - 启用内部滚动条
        self.app.text_area = ctk.CTkTextbox(
            self.app.text_frame,  # 父容器
            wrap=wrap_mode,  # 换行模式
            undo=True,  # 启用撤销功能
            font=self.app.current_font,  # 字体设置
            border_spacing=3,  # 边框间距
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

    def init_syntax_highlighting(self):
        """初始化语法高亮功能"""
        # 创建语法高亮实例并关联到文本区域
        self.app.syntax_highlighter = SyntaxHighlighter(self.app)

        # 确保选中样式优先级最高，在语法高亮初始化后调用
        # 这样可以确保语法高亮不会覆盖选中文本的样式
        self.app.text_area._textbox.tag_raise("sel")

    def init_other(self):
        """初始化其他组件"""
        # 初始化查找替换引擎
        self.app.find_replace_engine = FindReplaceEngine(self.app)

        # 初始化日志目录
        log_dir = config_manager.get("logging.log_dir", "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # 从配置管理器获取日志配置
        log_file = config_manager.get("logging.log_file", "app.log")
        log_level = config_manager.get("logging.log_level", "INFO")
        rotation_size = config_manager.get("logging.rotation_size", "5 MB")
        retention_time = config_manager.get("logging.retention_time", "7 days")

        # 构建日志文件完整路径
        log_path = os.path.join(log_dir, log_file)

        # 初始化日志记录器
        logger.add(
            log_path,  # 日志文件路径
            level=log_level,  # 日志级别
            filter="",  # 过滤器
            colorize=False,  # 是否使用颜色
            backtrace=True,  # 是否显示回溯信息
            diagnose=False,  # 是否启用诊断信息
            enqueue=False,  # 改为同步写入日志，避免GIL问题
            catch=True,  # 捕获异常，防止日志记录导致程序崩溃
            rotation=rotation_size,  # 日志文件旋转大小
            retention=retention_time,  # 日志文件保留时间
            compression="tar.gz",  # 日志文件压缩格式
            delay=True,  # 是否延迟初始化日志记录器
            watch=True,  # 关闭文件监控，减少资源占用
            encoding="utf-8",  # 日志文件编码
        )
        logger.info("logger initialized successfully!")
        logger.info(f"log file path: {log_path}")
        logger.info(f"config directory: {APP_CONFIG_DIR}")

        # 初始化通知管理器
        # self.app.nm = NotificationManager()

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
        self.init_other()

        # 初始化文件菜单部分项的状态
        self.app.update_file_menu_state()

        # 初始化后300ms绘制行号
        self.app.after(300, self.app.line_number_canvas.draw_line_numbers)

        logger.info("QuickEdit++ initialized successfully!")
