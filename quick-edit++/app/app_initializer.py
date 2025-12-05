#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
应用初始化模块
该模块负责处理应用程序的初始化过程, 包括主题设置、窗口配置、UI组件创建等
"""

import customtkinter as ctk
import tkinter as tk
from config.config_manager import config_manager, APP_CONFIG_DIR
from ui.ui_initializer import UIInitializer
from .file_operations import FileOperations
from .file_watcher import FileWatcher
from syntax_highlighter import SyntaxHighlighter
from .find_replace_engine import FindReplaceEngine
from ctypes import windll
from loguru import logger
import os


class AppInitializer:
    """应用初始化器类 - 负责应用程序的初始化过程"""

    def __init__(self, app):
        """
        初始化应用初始化器

        Args:
            app: QuickEditApp实例
        """
        self.app = app
        # 创建UI初始化器实例
        self.ui_initializer = UIInitializer(app)

    def init_dpi_support(self):
        """启用DPI缩放支持"""
        try:
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception as e:
            print(f"警告: 无法启用DPI缩放支持: {e}")

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

        # 初始化文件路径截断长度
        self.app.truncate_path_length = config_manager.get(
            "app.truncate_path_length", 50
        )

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

        # 创建重命名菜单项索引，用于更新菜单项状态
        self.app.rename_menu_index = None

        # 初始化通知位置状态变量
        current_notification_position = config_manager.get(
            "notification.position", "bottom_right"
        )
        self.app.notification_position_var = tk.StringVar(
            value=current_notification_position
        )

        # 初始化通知持续时间状态变量
        current_notification_duration = config_manager.get(
            "notification.duration", 3000
        )
        self.app.notification_duration_var = tk.IntVar(
            value=current_notification_duration
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

    def initialize_app(self):
        """执行完整的应用初始化流程"""
        # 按顺序执行初始化步骤
        self.init_dpi_support()

        # 初始化CTk主窗口 - 修复继承关系问题
        ctk.CTk.__init__(self.app)

        # 初始化菜单变量 (需要在UI初始化之前)
        self.init_menu_variables()

        # 初始化文件属性 (需要在UI初始化之前)
        self.init_file_attributes()

        # 初始化UI组件
        self.ui_initializer.initialize_ui()

        # 初始化语法高亮
        self.init_syntax_highlighting()

        # 初始化其他组件
        self.init_other()

        # 初始化文件菜单部分项的状态
        self.app.update_file_menu_state()

        logger.info("QuickEdit++ initialized successfully!")
