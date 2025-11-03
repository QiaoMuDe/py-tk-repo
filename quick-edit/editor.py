import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, font
import os
import datetime
import sys
import json
import shutil
import chardet
import tkinterdnd2
import re
import threading
import queue
import codecs

# 导入我们创建的模块
from find_dialog import FindDialog
from theme_manager import ThemeManager, DEFAULT_CURSOR, CURSOR_STYLES
from insert_helper import InsertHelper
from text_processing_helper import TextProcessingHelper
import quick_edit_utils

# 导入enhanced_syntax_highlighter模块
import enhanced_syntax_highlighter
from enhanced_syntax_highlighter import get_lexer_name_by_filename
from language_dialog import LanguageDialog
from tab_settings_dialog import TabSettingsDialog

# 项目地址
PROJECT_URL = "https://gitee.com/MM-Q/py-tk-repo.git"

# 版本号
VERSION = "v0.0.8"

# 文件大小限制
MaxFileSize = 1024 * 1024 * 10  # 最大文件大小限制
SmallFileSizeThreshold = 1024 * 100  # 打开文件显示进度条的最低触发大小

# 主窗口-高
MainWindowHeight = 800

# 主窗口-宽
MainWindowWidth = 900

# 限制撤销操作数量
MaxUndo = 50

# 配置文件名
ConfigFileName = ".quick_edit_config.json"

# 配置文件路径
ConfigFilePath = os.path.join(os.path.expanduser("~"), ConfigFileName)

# 窗口标题显示格式常量
WINDOW_TITLE_FILENAME_ONLY = "filename_only"  # 仅文件名
WINDOW_TITLE_FULL_PATH = "full_path"  # 完整文件路径
WINDOW_TITLE_FILE_AND_DIRECTORY = "file_and_directory"  # 文件和目录


class AdvancedTextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("QuickEdit")

        # 初始化配置属性
        self.max_file_size = MaxFileSize  # 最大文件大小限制
        self.small_file_size_threshold = (
            SmallFileSizeThreshold  # 打开文件显示进度条的最低触发大小
        )
        self.main_window_height = MainWindowHeight  # 主窗口高度
        self.main_window_width = MainWindowWidth  # 主窗口宽度
        self.max_undo = MaxUndo  # 限制撤销操作数量
        self.config_file_name = ConfigFileName  # 配置文件名
        self.config_file_path = ConfigFilePath  # 配置文件路径

        # 设置窗口大小和位置
        quick_edit_utils.center_window(
            self.root, self.main_window_width, self.main_window_height
        )

        # 设置窗口图标
        quick_edit_utils.set_window_icon(self.root)

        # 初始化变量
        self.current_file = None  # 当前打开的文件路径
        self.font_family = "Microsoft YaHei UI"  # 默认字体
        self.font_size = 13  # 默认字体大小
        self.font_bold = False  # 默认不加粗
        self.font_italic = False  # 默认不斜体
        self.font_underline = False  # 默认无下划线
        self.font_overstrike = False  # 默认无删除线
        self.toolbar_visible = True  # 工具栏默认显示
        self.show_line_numbers = True  # 行号显示状态, 默认显示
        self.syntax_highlighting_enabled = True  # 语法高亮显示状态, 默认启用
        self.encoding = "UTF-8"  # 默认编码
        self.line_ending = "LF"  # 默认换行符
        self.readonly_mode = False  # 只读模式, 默认关闭
        self.current_theme = "light"  # 默认主题

        # 增强版语法高亮相关属性
        self.enhanced_highlighter = None  # 增强版语法高亮器实例
        self.current_lexer = "auto"  # 当前使用的词法分析器
        self.current_style = "monokai"  # 当前使用的样式

        # 自动保存相关变量
        self.auto_save_enabled = False  # 默认关闭自动保存
        self.auto_save_interval = 5  # 默认自动保存间隔5秒
        self.auto_save_timer = None  # 自动保存计时器
        self.last_auto_save_time = None  # 上次自动保存时间
        self.auto_save_var = tk.BooleanVar(
            value=self.auto_save_enabled
        )  # 自动保存菜单变量
        self.backup_enabled = False  # 默认关闭备份
        self.backup_enabled_var = tk.BooleanVar(value=self.backup_enabled)  # 备份选项
        self.save_lock = threading.RLock()  # 线程安全锁
        self.is_saving = False

        # 制表符相关设置
        self.tab_width = 4  # 默认制表符宽度
        self.use_spaces_for_tabs = False  # 默认不使用空格替代制表符

        # 快捷插入功能设置
        self.quick_insert_enabled = True  # 默认启用快捷插入功能

        # 窗口标题显示格式选项
        self.window_title_format = WINDOW_TITLE_FILENAME_ONLY  # 默认仅显示文件名

        # 光标样式配置
        self.cursor_style = DEFAULT_CURSOR  # 默认光标样式

        # 异步文件读取相关属性
        self.file_read_thread = None
        self.file_read_cancelled = False
        self.progress_window = None

        # 加载配置文件
        self.load_config()

        # 初始化主题管理器
        self.theme_manager = ThemeManager(self)

        # 初始化插入助手
        self.insert_helper = InsertHelper(self)

        # 初始化文本处理助手
        # 注意：text_area在create_widgets后才存在，这里只做占位初始化
        self.text_processing_helper = None

        # 创建主框架
        self.create_widgets()

        # 初始化文本处理助手（此时text_area已经创建）
        self.text_processing_helper = TextProcessingHelper(self.text_area)

        self.create_menu()
        # 创建工具栏
        self.create_toolbar()

        # 根据配置应用工具栏显示状态
        if not self.toolbar_visible and hasattr(self, "toolbar"):
            self.toolbar.pack_forget()

        # 设置窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 创建状态栏
        self.create_statusbar()

        # 应用当前主题 (在创建所有UI组件后应用)
        self.theme_manager.set_theme(self.current_theme)

        # 应用光标样式设置
        self.apply_cursor_styles()

        # 绑定快捷键
        self.bind_shortcuts()

        # 设置自动保存功能
        self.setup_auto_save()

        # 启用拖拽支持
        self.enable_drag_and_drop()

        # 设置窗口焦点和文本框光标位置
        self.root.focus_force()
        self.text_area.focus_set()

    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file_path):
            try:
                # 先检测配置文件的编码
                encoding, _ = quick_edit_utils.detect_file_encoding_and_line_ending(
                    self.config_file_path
                )

                # 使用检测到的编码通过codecs.open打开文件
                with codecs.open(
                    self.config_file_path, "r", encoding=encoding, errors="replace"
                ) as f:
                    config = json.load(f)
                    self.font_family = config.get("font_family", "Microsoft YaHei UI")
                    self.font_size = config.get("font_size", 12)
                    self.font_bold = config.get("font_bold", False)
                    self.font_italic = config.get("font_italic", False)
                    self.font_underline = config.get("font_underline", False)
                    self.font_overstrike = config.get("font_overstrike", False)
                    self.toolbar_visible = config.get("toolbar_visible", True)
                    # 加载行号显示状态
                    self.show_line_numbers = config.get("show_line_numbers", True)
                    # 加载语法高亮显示状态
                    self.syntax_highlighting_enabled = config.get(
                        "syntax_highlighting_enabled", True
                    )
                    # 加载主题配置
                    self.current_theme = config.get("current_theme", "light")
                    # 加载自动保存配置
                    self.auto_save_enabled = config.get("auto_save_enabled", False)
                    self.auto_save_interval = config.get("auto_save_interval", 5)
                    # 加载备份配置
                    self.backup_enabled = config.get("backup_enabled", True)
                    # 加载文本自动换行配置
                    self.word_wrap_enabled = config.get("word_wrap_enabled", True)
                    # 加载制表符设置
                    self.tab_width = config.get("tab_width", 4)
                    self.use_spaces_for_tabs = config.get("use_spaces_for_tabs", False)
                    # 加载窗口标题显示格式选项
                    self.window_title_format = config.get(
                        "window_title_format", WINDOW_TITLE_FILENAME_ONLY
                    )
                    # 加载光标样式配置
                    self.cursor_style = config.get("cursor_style", DEFAULT_CURSOR)
                    # 加载新的配置属性
                    self.max_file_size = config.get("max_file_size", MaxFileSize)
                    self.small_file_size_threshold = config.get(
                        "small_file_size_threshold", SmallFileSizeThreshold
                    )
                    self.main_window_height = config.get(
                        "main_window_height", MainWindowHeight
                    )  # 高度
                    self.main_window_width = config.get(
                        "main_window_width", MainWindowWidth
                    )  # 宽度
                    self.max_undo = config.get("max_undo", MaxUndo)  # 最大撤销次数
                    self.config_file_name = config.get(
                        "config_file_name", ConfigFileName
                    )
                    self.config_file_path = config.get(
                        "config_file_path", ConfigFilePath
                    )
                    # 加载快捷插入功能配置
                    self.quick_insert_enabled = config.get("quick_insert_enabled", True)

                # 同步更新字体样式变量的状态
                if hasattr(self, "bold_var"):
                    self.bold_var.set(self.font_bold)
                if hasattr(self, "italic_var"):
                    self.italic_var.set(self.font_italic)
                if hasattr(self, "underline_var"):
                    self.underline_var.set(self.font_underline)
                if hasattr(self, "overstrike_var"):
                    self.overstrike_var.set(self.font_overstrike)
                # 同步更新自动保存菜单变量的状态
                if hasattr(self, "auto_save_var"):
                    self.auto_save_var.set(self.auto_save_enabled)
                # 同步更新备份选项菜单变量的状态
                if hasattr(self, "backup_enabled_var"):
                    self.backup_enabled_var.set(self.backup_enabled)
                # 同步更新文本自动换行菜单变量的状态
                if hasattr(self, "word_wrap_var"):
                    self.word_wrap_var.set(self.word_wrap_enabled)

            except Exception as e:
                print(f"加载配置文件时出错: {e}")
                # 如果出错，则使用默认配置
        else:
            # 配置文件不存在，保存默认配置
            self.save_config()

    def save_config(self):
        """保存配置文件"""
        config = {
            "font_family": self.font_family,
            "font_size": self.font_size,
            "font_bold": self.font_bold,
            "font_italic": self.font_italic,
            "font_underline": self.font_underline,
            "font_overstrike": self.font_overstrike,
            "toolbar_visible": self.toolbar_visible,
            "show_line_numbers": self.show_line_numbers,
            "syntax_highlighting_enabled": self.syntax_highlighting_enabled,
            "current_theme": self.current_theme,
            "auto_save_enabled": self.auto_save_enabled,
            "auto_save_interval": self.auto_save_interval,
            "backup_enabled": self.backup_enabled,
            "word_wrap_enabled": self.word_wrap_enabled,
            "tab_width": self.tab_width,
            "use_spaces_for_tabs": self.use_spaces_for_tabs,
            "window_title_format": self.window_title_format,
            "cursor_style": self.cursor_style,
            "max_file_size": self.max_file_size,
            "small_file_size_threshold": self.small_file_size_threshold,
            "main_window_height": self.main_window_height,
            "main_window_width": self.main_window_width,
            "max_undo": self.max_undo,
            "config_file_name": self.config_file_name,
            "config_file_path": self.config_file_path,
            "quick_insert_enabled": self.quick_insert_enabled,
        }

        try:
            with open(self.config_file_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存配置文件时出错: {e}")

    def apply_syntax_highlighting(self):
        """应用语法高亮"""
        try:
            # 移除现有的语法高亮
            self.remove_syntax_highlighting()

            # 如果启用了语法高亮，使用增强版语法高亮器
            if self.syntax_highlighting_enabled:
                # 获取词法分析器名称
                lexer_name = get_lexer_name_by_filename(self.current_file)
                # 更新current_lexer变量，使语言选择对话框正确显示当前语言
                self.current_lexer = lexer_name
                # 更新language_var以保持菜单和状态同步
                self.language_var.set(lexer_name)

                # 使用enhanced_syntax_highlighter模块中的函数创建语法高亮器
                self.enhanced_highlighter = (
                    enhanced_syntax_highlighter.apply_syntax_highlighting(
                        self.text_area,
                        lexer_name=lexer_name,
                        style_name=self.current_style,
                        delay_update=200,
                    )
                )

                # 延迟触发高亮更新, 避免在UI初始化期间进行大量计算
                self.text_area.after(300, self._delayed_highlight_update)
        except Exception as e:
            # 捕获所有异常但不中断程序
            pass

    def _delayed_highlight_update(self):
        """延迟执行的高亮更新, 避免阻塞UI初始化"""
        if hasattr(self, "enhanced_highlighter") and self.enhanced_highlighter:
            try:
                self.enhanced_highlighter.update_highlighting()
            except Exception:
                # 忽略可能的错误
                pass

    def remove_syntax_highlighting(self):
        """移除语法高亮"""
        try:
            # 使用enhanced_syntax_highlighter模块中的函数移除语法高亮
            enhanced_syntax_highlighter.remove_syntax_highlighting(
                self.enhanced_highlighter
            )
            self.enhanced_highlighter = None
        except Exception:
            # 捕获所有异常但不中断程序
            pass

    def _reset_file_state(self):
        """重置文件状态的辅助方法, 用于close_file和new_file"""
        # 清空文本区域
        self.text_area.delete(1.0, tk.END)
        # 重置文件状态
        self.current_file = None
        # 根据只读模式状态设置窗口标题
        if self.readonly_mode:
            self.root.title("[只读模式] QuickEdit")
        else:
            self.root.title("QuickEdit")
        # 重置编码和换行符为默认值
        self.encoding = "UTF-8"
        self.line_ending = "LF"
        # 重置修改状态
        self.text_area.edit_modified(False)
        # 移除可能存在的语法高亮
        self.remove_syntax_highlighting()
        # 更新状态栏
        self.update_statusbar()

    def get_window_title_display_name(self):
        """获取窗口标题显示名称"""
        # 如果没有打开文件，返回None
        if not self.current_file:
            return None

        # 根据不同的显示格式设置标题
        if self.window_title_format == WINDOW_TITLE_FULL_PATH:
            # 完整文件路径
            return self.current_file
        elif self.window_title_format == WINDOW_TITLE_FILE_AND_DIRECTORY:
            # 文件和目录
            directory = os.path.dirname(self.current_file)
            file_name = os.path.basename(self.current_file)
            return f"{file_name} - {directory}"
        else:
            # 仅文件名（默认）
            return os.path.basename(self.current_file)

    def update_title_based_on_content(self):
        """根据文本框内容更新窗口标题"""
        # 优化：移除不必要的全文读取操作，改用文本比较和修改状态判断

        # 如果没有打开文件
        if not self.current_file:
            # 使用文本比较而不是读取整个内容，更高效地判断文本框是否为空
            is_empty = self.text_area.compare("end-1c", "==", "1.0")

            if is_empty:
                # 当内容为空时，重置修改状态为未修改
                self.text_area.edit_modified(False)
                if self.readonly_mode:
                    self.root.title("[只读模式] QuickEdit")
                else:
                    self.root.title("QuickEdit")
            else:
                if self.readonly_mode:
                    self.root.title("[只读模式] 未保存 - QuickEdit")
                else:
                    self.root.title("未保存 - QuickEdit")
        # 如果已经打开了文件
        else:
            # 获取显示名称
            display_name = self.get_window_title_display_name()

            # 根据只读模式状态和修改状态设置窗口标题
            if self.readonly_mode:
                if self.text_area.edit_modified():
                    self.root.title(f"[只读模式] *{display_name} - QuickEdit")
                else:
                    self.root.title(f"[只读模式] {display_name} - QuickEdit")
            else:
                if self.text_area.edit_modified():
                    self.root.title(f"*{display_name} - QuickEdit")
                else:
                    self.root.title(f"{display_name} - QuickEdit")

    def on_closing(self):
        """处理窗口关闭事件"""
        # 停止自动保存计时器
        self.stop_auto_save_timer()

        # 取消正在进行的文件读取操作
        self.file_read_cancelled = True

        # 使用公共方法检查并处理未保存的更改
        continue_operation, saved = self.check_and_handle_unsaved_changes("退出")

        if not continue_operation:
            return  # 用户取消操作

        # 检查窗口是否仍然存在再决定是否销毁
        if not self.root.winfo_exists():
            return

        # 如果启用了备份功能，并且是保存后退出或文件未被修改且有打开的文件，清理备份文件
        if self.backup_enabled and (
            (saved and self.current_file)
            or (self.current_file and not self.text_area.edit_modified())
        ):
            self.cleanup_backup()

        # 清理语法高亮器资源
        self.remove_syntax_highlighting()

        # 销毁窗口
        self.root.destroy()

    def create_widgets(self):
        """创建主要控件"""
        # 创建包含行号和文本区域的框架
        self.text_frame = tk.Frame(self.root)
        self.text_frame.pack(fill=tk.BOTH, expand=True)

        # 创建行号显示区域
        self.line_numbers = tk.Canvas(
            self.text_frame, width=60, bg="#f0f0f0", highlightthickness=0
        )
        # 根据配置决定是否显示行号
        if self.show_line_numbers:
            self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

            # 绑定鼠标事件用于点击全选
            self.line_numbers.bind("<Button-1>", self.on_line_number_click)
            # 绑定鼠标进入事件用于高亮行号
            self.line_numbers.bind("<Motion>", self.on_line_number_hover)
            # 绑定鼠标退出行号区域事件用于取消高亮
            self.line_numbers.bind("<Leave>", self.on_line_number_leave)

        # 创建文本区域和滚动条的容器
        self.text_container = tk.Frame(self.text_frame)
        self.text_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 创建垂直滚动条
        self.scrollbar = tk.Scrollbar(self.text_container, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 创建水平滚动条
        self.hscrollbar = tk.Scrollbar(self.text_container, orient=tk.HORIZONTAL)
        # 初始时隐藏水平滚动条，因为默认启用了文本自动换行
        # self.hscrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # 创建文本区域
        self.text_area = tk.Text(
            self.text_container,
            wrap=tk.WORD,  # 设置为按单词换行
            undo=True,
            yscrollcommand=self.on_text_scroll_with_line_numbers,
            xscrollcommand=self.hscrollbar.set,  # 关联水平滚动条
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)

        # 将滚动条与文本区域关联
        self.scrollbar.config(command=self.on_text_scroll)
        self.hscrollbar.config(command=self.text_area.xview)

        # 根据配置设置文本区域的换行属性和水平滚动条状态
        if hasattr(self, "word_wrap_enabled"):
            if self.word_wrap_enabled:
                self.text_area.config(wrap=tk.WORD)
                self.hscrollbar.pack_forget()  # 隐藏水平滚动条
            else:
                self.text_area.config(wrap=tk.NONE)
                self.hscrollbar.pack(side=tk.BOTTOM, fill=tk.X)  # 显示水平滚动条
        else:
            # 如果还没有加载配置，使用默认值
            self.word_wrap_enabled = True

        # 绑定滚动事件
        self.text_area.bind("<MouseWheel>", self.on_mouse_wheel)
        self.text_area.bind("<Key>", self.on_key_press)
        self.text_area.bind("<Button-4>", self.on_mouse_wheel)  # Linux鼠标滚轮支持
        self.text_area.bind("<Button-5>", self.on_mouse_wheel)  # Linux鼠标滚轮支持
        self.text_area.bind(
            "<ButtonRelease>", lambda e: self.schedule_line_number_update(50)
        )  # 鼠标释放时更新行号

        # 绑定文本变化事件, 用于更新行号
        self.text_area.bind(
            "<KeyRelease>", lambda e: self.schedule_line_number_update(50)
        )
        self.text_area.bind(
            "<<Modified>>", lambda e: self.schedule_line_number_update(50)
        )

        # 绑定鼠标右键事件，用于显示上下文菜单
        self.text_area.bind("<Button-3>", self.show_context_menu)

        # 绑定窗口配置事件, 用于在窗口大小改变时更新行号
        self.root.bind("<Configure>", self.on_window_configure)

        # 设置默认字体
        self.update_font()

        # 初始化文件相关变量
        self.total_lines = 0

        # 性能优化配置
        self.text_area.config(
            background="white",
            foreground="black",
            insertbackground="black",
            selectbackground="lightblue",
            selectforeground="black",
            maxundo=self.max_undo,  # 最大撤销次数
        )

        # 设置行号区域样式(默认为白色)
        self.line_numbers.config(bg="#f0f0f0", highlightthickness=0)

        # 应用制表符设置
        self.apply_tab_settings()

    def open_language_dialog(self):
        """打开语言选择对话框"""
        # 使用当前的词法分析器作为当前语言
        current_language = self.current_lexer

        # 创建语言选择对话框
        dialog = LanguageDialog(self.root, current_language)

        # 等待对话框关闭
        self.root.wait_window(dialog.dialog)

        # 获取选中的语言
        selected_language = dialog.get_selected_language()

        # 如果用户选择了语言
        if selected_language:
            # 更新语言变量
            self.language_var.set(selected_language)
            # 直接将选中的语言传递给change_language方法
            self.change_language(selected_language)

    def toggle_word_wrap(self):
        """切换文本自动换行功能

        当启用时，文本将在窗口边缘自动换行，水平滚动条隐藏；当禁用时，文本将水平滚动，水平滚动条显示。
        切换后会保存配置到配置文件。
        """
        # 切换换行状态
        self.word_wrap_enabled = not self.word_wrap_enabled

        # 根据状态设置文本框的wrap属性和水平滚动条的显示状态
        if self.word_wrap_enabled:
            self.text_area.config(wrap=tk.WORD)
            self.hscrollbar.pack_forget()  # 隐藏水平滚动条
        else:
            self.text_area.config(wrap=tk.NONE)
            self.hscrollbar.pack(side=tk.BOTTOM, fill=tk.X)  # 显示水平滚动条

        # 更新状态栏显示
        status = "已启用" if self.word_wrap_enabled else "已禁用"
        self.left_status.config(text=f"文本自动换行: {status}")

        # 保存配置到配置文件
        self.save_config()

    def change_language(self, selected_language=None):
        """更改语法高亮语言

        Args:
            selected_language: 要选择的语言名称，如果为None则从language_var获取
        """
        try:
            # 如果没有提供语言，则从language_var获取
            target_language = (
                selected_language
                if selected_language is not None
                else self.language_var.get()
            )
            # 使用enhanced_syntax_highlighter模块中的函数获取语言别名映射
            language_aliases = enhanced_syntax_highlighter.get_language_aliases()

            # 更新当前词法分析器
            if target_language in language_aliases:
                self.current_lexer = language_aliases[target_language]
            else:
                self.current_lexer = target_language.lower()

            # 如果有增强版语法高亮器实例，更新其词法分析器
            if self.enhanced_highlighter:
                self.enhanced_highlighter.set_lexer(self.current_lexer)

            # 更新状态栏
            self.left_status.config(text=f"语法高亮语言已更改为: {selected_language}")
        except Exception as e:
            self.left_status.config(text=f"更改语言时出错: {str(e)}")

    def create_menu(self):
        """创建菜单栏"""
        # 定义菜单字体
        menu_font = ("Microsoft YaHei UI", 10)

        menubar = tk.Menu(self.root, font=menu_font)

        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0, font=menu_font)
        file_menu.add_command(label="新建", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(
            label="打开", command=self.open_file, accelerator="Ctrl+O"
        )
        file_menu.add_command(
            label="保存", command=self.save_file, accelerator="Ctrl+S"
        )
        file_menu.add_command(
            label="另存为", command=self.save_as_file, accelerator="Ctrl+Shift+S"
        )
        file_menu.add_command(
            label="关闭文件", command=self.close_file, accelerator="Ctrl+W"
        )
        file_menu.add_separator()

        # 添加编码选择子菜单
        encoding_submenu = self.create_encoding_menu(show_common_only=True)
        file_menu.add_cascade(label="编码", menu=encoding_submenu)
        # 添加换行符选择子菜单
        line_ending_submenu = tk.Menu(file_menu, tearoff=0, font=menu_font)
        line_endings = [
            ("Linux (LF)", "LF"),
            ("Windows (CRLF)", "CRLF"),
            ("Mac (CR)", "CR"),
        ]
        for label, ending in line_endings:
            line_ending_submenu.add_command(
                label=label, command=lambda e=ending: self.set_line_ending(e)
            )
        file_menu.add_cascade(label="换行符", menu=line_ending_submenu)
        file_menu.add_separator()
        self.readonly_var = tk.BooleanVar(value=self.readonly_mode)
        file_menu.add_checkbutton(
            label="只读模式",
            command=self.toggle_readonly_mode,
            variable=self.readonly_var,
            accelerator="Ctrl+R",
        )
        file_menu.add_command(
            label="打开所在文件夹",
            command=self.open_containing_folder,
            accelerator="Ctrl+Shift+R",
        )
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.exit_app, accelerator="Ctrl+Q")
        menubar.add_cascade(label="文件", menu=file_menu)

        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0, font=menu_font)

        # 添加撤销和重做选项
        self.create_undo_menu_item(edit_menu)
        self.create_redo_menu_item(edit_menu)
        edit_menu.add_separator()

        # 添加剪切、复制、粘贴和全选选项
        self.create_cut_menu_item(edit_menu)
        self.create_copy_menu_item(edit_menu)
        self.create_paste_menu_item(edit_menu)
        edit_menu.add_separator()

        self.create_select_all_menu_item(edit_menu)
        edit_menu.add_separator()

        # 添加查找和替换选项
        self.create_find_menu_item(edit_menu)
        edit_menu.add_separator()

        # 页面导航选项
        edit_menu.add_command(
            label="向上翻页", command=self.page_up, accelerator="PgUp"
        )
        edit_menu.add_command(
            label="向下翻页", command=self.page_down, accelerator="PgDn"
        )
        edit_menu.add_command(
            label="转到文件顶部", command=self.go_to_home, accelerator="Home"
        )
        edit_menu.add_command(
            label="转到文件底部", command=self.go_to_end, accelerator="End"
        )
        edit_menu.add_command(
            label="转到行", command=self.go_to_line, accelerator="Ctrl+G"
        )
        edit_menu.add_separator()

        edit_menu.add_command(label="清空剪贴板", command=self.clear_clipboard)
        # 复制到剪贴板子菜单
        copy_to_clipboard_menu = self.create_copy_to_clipboard_menu(edit_menu)
        edit_menu.add_cascade(label="复制到剪贴板", menu=copy_to_clipboard_menu)

        # 选中文本操作子菜单
        selected_text_menu = self.create_selected_text_menu(edit_menu)
        edit_menu.add_cascade(label="选中文本操作", menu=selected_text_menu)

        # 插入子菜单
        insert_menu = self.create_insert_menu(edit_menu)
        edit_menu.add_cascade(label="插入", menu=insert_menu)
        menubar.add_cascade(label="编辑", menu=edit_menu)

        # 主题菜单
        theme_menu = tk.Menu(menubar, tearoff=0, font=menu_font)
        theme_menu.add_command(label="字体", command=self.choose_font)
        theme_menu.add_command(label="字体大小", command=self.choose_font_size)

        # 初始化字体样式变量
        theme_menu.add_separator()
        self.bold_var = tk.BooleanVar(value=self.font_bold)
        self.italic_var = tk.BooleanVar(value=self.font_italic)
        self.underline_var = tk.BooleanVar(value=self.font_underline)
        self.overstrike_var = tk.BooleanVar(value=self.font_overstrike)
        theme_menu.add_checkbutton(
            label="粗体",
            command=self.toggle_bold,
            variable=self.bold_var,
        )
        theme_menu.add_checkbutton(
            label="斜体",
            command=self.toggle_italic,
            variable=self.italic_var,
        )
        theme_menu.add_checkbutton(
            label="下划线",
            command=self.toggle_underline,
            variable=self.underline_var,
        )
        theme_menu.add_checkbutton(
            label="删除线",
            command=self.toggle_overstrike,
            variable=self.overstrike_var,
        )

        # 添加主题切换选项
        theme_menu.add_separator()
        theme_menu.add_command(
            label="切换主题", command=self.cycle_theme, accelerator="Ctrl+T"
        )
        # 主题选择子菜单
        theme_submenu = tk.Menu(theme_menu, tearoff=0, font=menu_font)
        # 使用主题管理器获取所有可用主题列表
        themes = self.theme_manager.get_theme_list()
        for label, theme_name in themes:
            theme_submenu.add_command(
                label=label, command=lambda t=theme_name: self.change_theme(t)
            )
        theme_menu.add_cascade(label="主题", menu=theme_submenu)

        # 光标样式设置子菜单
        theme_menu.add_separator()
        cursor_menu = tk.Menu(theme_menu, tearoff=0, font=menu_font)
        self.cursor_style_vars = {}  # 存储光标样式变量

        # 全局光标样式选项
        for cursor_style in CURSOR_STYLES:
            var = tk.BooleanVar(value=(self.cursor_style == cursor_style))
            self.cursor_style_vars[cursor_style] = var
            cursor_menu.add_checkbutton(
                label=cursor_style,
                variable=var,
                command=lambda s=cursor_style: self.set_cursor_style(s),
            )

        theme_menu.add_cascade(label="光标样式", menu=cursor_menu)
        menubar.add_cascade(label="主题", menu=theme_menu)

        # 语法高亮菜单
        syntax_menu = tk.Menu(menubar, tearoff=0, font=menu_font)
        # 语法高亮显示选项
        self.syntax_highlighting_var = tk.BooleanVar(
            value=self.syntax_highlighting_enabled
        )
        syntax_menu.add_checkbutton(
            label="启用语法高亮",
            command=self.toggle_syntax_highlighting,
            variable=self.syntax_highlighting_var,
            accelerator="Ctrl+Shift+K",
        )
        syntax_menu.add_separator()

        # 选择语言菜单项，点击时打开语言选择对话框，添加Ctrl+L快捷键
        syntax_menu.add_command(
            label="选择语言", command=self.open_language_dialog, accelerator="Ctrl+L"
        )
        # 绑定Ctrl+L快捷键到open_language_dialog方法
        self.root.bind("<Control-l>", lambda event: self.open_language_dialog())
        self.language_var = tk.StringVar(value=self.current_lexer)

        menubar.add_cascade(label="语法高亮", menu=syntax_menu)

        # 设置菜单
        settings_menu = tk.Menu(menubar, tearoff=0, font=menu_font)
        self.toolbar_var = tk.BooleanVar(value=self.toolbar_visible)
        settings_menu.add_checkbutton(
            label="显示工具栏", command=self.toggle_toolbar, variable=self.toolbar_var
        )
        # 行号显示选项
        self.show_line_numbers_var = tk.BooleanVar(value=self.show_line_numbers)
        settings_menu.add_checkbutton(
            label="显示行号",
            command=self.toggle_line_numbers,
            variable=self.show_line_numbers_var,
        )
        # 文本自动换行选项
        self.word_wrap_var = tk.BooleanVar(value=self.word_wrap_enabled)
        settings_menu.add_checkbutton(
            label="启用文本自动换行",
            command=self.toggle_word_wrap,
            variable=self.word_wrap_var,
        )
        # 自动保存设置
        settings_menu.add_separator()
        settings_menu.add_checkbutton(
            label="启用自动保存",
            command=self.toggle_auto_save,
            variable=self.auto_save_var,
        )
        settings_menu.add_command(
            label="设置自动保存间隔...",
            command=self.set_auto_save_interval,
        )
        # 备份选项
        self.backup_enabled_var = tk.BooleanVar(value=self.backup_enabled)
        settings_menu.add_checkbutton(
            label="开启副本备份",
            command=self.toggle_backup,
            variable=self.backup_enabled_var,
        )
        # 查看配置文件选项
        # 制表符设置
        settings_menu.add_separator()
        settings_menu.add_command(
            label="制表符设置...", command=self.open_tab_settings_dialog
        )

        # 快捷插入功能设置
        self.quick_insert_var = tk.BooleanVar(value=self.quick_insert_enabled)
        settings_menu.add_checkbutton(
            label="启用快捷插入(@)",
            command=self.toggle_quick_insert,
            variable=self.quick_insert_var,
        )

        # 窗口标题显示选项
        title_format_menu = tk.Menu(settings_menu, tearoff=0, font=menu_font)
        self.window_title_format_var = tk.StringVar(value=self.window_title_format)
        title_format_menu.add_radiobutton(
            label="仅文件名",
            variable=self.window_title_format_var,
            value=WINDOW_TITLE_FILENAME_ONLY,
            command=self.set_window_title_format,
        )
        title_format_menu.add_radiobutton(
            label="完整文件路径",
            variable=self.window_title_format_var,
            value=WINDOW_TITLE_FULL_PATH,
            command=self.set_window_title_format,
        )
        title_format_menu.add_radiobutton(
            label="文件和目录",
            variable=self.window_title_format_var,
            value=WINDOW_TITLE_FILE_AND_DIRECTORY,
            command=self.set_window_title_format,
        )
        settings_menu.add_cascade(label="窗口标题显示", menu=title_format_menu)

        # 查看配置文件选项
        settings_menu.add_separator()
        settings_menu.add_command(
            label="查看配置", command=self.open_config_file, accelerator="Ctrl+Shift+C"
        )
        menubar.add_cascade(label="设置", menu=settings_menu)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0, font=menu_font)
        help_menu.add_command(
            label="文档统计信息",
            command=self.show_document_stats,
            accelerator="Ctrl+Shift+I",
        )
        help_menu.add_separator()
        help_menu.add_command(label="关于", command=self.show_about, accelerator="F1")
        menubar.add_cascade(label="帮助", menu=help_menu)

        self.root.config(menu=menubar)

    def apply_cursor_styles(self):
        """应用光标样式设置"""
        # 应用全局光标样式到文本区域
        self.text_area.config(cursor=self.cursor_style)
        # right_status 保持手型光标用于点击操作
        self.right_status.config(cursor="hand2")

    def set_cursor_style(self, cursor_style):
        """设置全局光标样式"""
        # 更新配置
        self.cursor_style = cursor_style

        # 更新文本区域和状态栏的光标样式
        self.text_area.config(cursor=cursor_style)
        # right_status 保持手型光标用于点击操作
        self.right_status.config(cursor="hand2")

        # 更新光标样式变量状态
        for style in CURSOR_STYLES:
            if style in self.cursor_style_vars:
                self.cursor_style_vars[style].set(style == cursor_style)

        # 保存配置
        self.save_config()

        # 绑定快捷键
        self.root.bind("<Control-Shift-C>", lambda event: self.open_config_file())
        self.root.bind("<F1>", lambda event: self.show_about())

    def toggle_line_numbers(self):
        """切换行号显示"""
        # 更新变量状态
        self.show_line_numbers = self.show_line_numbers_var.get()

        if self.show_line_numbers:
            # 显示行号并设置位置
            self.line_numbers.pack(side=tk.LEFT, fill=tk.Y, before=self.text_container)
            # 设置文本容器位置
            self.text_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
            # 立即更新行号
            self.update_line_numbers()
        else:
            # 隐藏行号
            self.line_numbers.pack_forget()
            # 让文本容器占据整个空间
            self.text_container.pack(fill=tk.BOTH, expand=True)

        # 保存配置
        self.save_config()

    def toggle_syntax_highlighting(self):
        """切换语法高亮显示"""
        if self.syntax_highlighting_var.get():
            # 开启语法高亮
            self.syntax_highlighting_enabled = True
            self.left_status.config(text="语法高亮已开启")
            # 为当前打开的文件应用语法高亮
            if self.current_file:
                self.apply_syntax_highlighting()
        else:
            # 关闭语法高亮
            self.syntax_highlighting_enabled = False
            self.left_status.config(text="语法高亮已关闭")
            self.remove_syntax_highlighting()  # 移除高亮

        # 保存配置
        self.save_config()

    def toggle_auto_save(self):
        """切换自动保存功能的启用状态"""
        self.auto_save_enabled = self.auto_save_var.get()
        self.save_config()

        if self.auto_save_enabled:
            self.start_auto_save_timer()
            # 使用辅助方法格式化显示
            display_interval = quick_edit_utils.format_auto_save_interval(
                self.auto_save_interval
            )
            messagebox.showinfo("自动保存", f"已启用自动保存，间隔为{display_interval}")
        else:
            self.stop_auto_save_timer()
            messagebox.showinfo("自动保存", "已关闭自动保存")

        # 更新状态栏显示
        self.show_default_auto_save_status()

    def toggle_backup(self):
        """切换备份功能的启用状态"""
        self.backup_enabled = self.backup_enabled_var.get()
        self.save_config()

        status_text = "已启用副本备份" if self.backup_enabled else "已禁用副本备份"
        self.left_status.config(text=status_text)

    def toggle_quick_insert(self):
        """切换快捷插入功能的启用状态"""
        self.quick_insert_enabled = self.quick_insert_var.get()
        self.save_config()

        status_text = (
            "已启用快捷插入(@)" if self.quick_insert_enabled else "已禁用快捷插入(@)"
        )
        self.left_status.config(text=status_text)

    def open_config_file(self):
        """打开配置文件"""
        # 检查配置文件是否存在
        if not os.path.exists(self.config_file_path):
            # 如果配置文件不存在，复用save_config方法创建完整的配置文件
            try:
                self.save_config()
            except Exception as e:
                messagebox.showerror("错误", f"创建配置文件失败: {str(e)}")
                return

        # 调用open_file方法打开配置文件
        self.open_file(self.config_file_path)

    def open_tab_settings_dialog(self):
        """打开制表符设置对话框"""
        try:
            # 创建制表符设置对话框
            dialog = TabSettingsDialog(
                self.root,
                current_tab_width=self.tab_width,
                use_spaces_for_tabs=self.use_spaces_for_tabs,
            )

            # 等待对话框关闭
            self.root.wait_window(dialog.dialog)

            # 获取用户设置的选项
            new_tab_width, new_use_spaces = dialog.get_settings()

            # 如果设置发生了变化
            if (
                new_tab_width != self.tab_width
                or new_use_spaces != self.use_spaces_for_tabs
            ):

                # 更新设置
                self.tab_width = new_tab_width
                self.use_spaces_for_tabs = new_use_spaces

                # 应用新的制表符设置
                self.apply_tab_settings()

                # 保存配置
                self.save_config()

                # 更新状态栏
                self.update_statusbar()

        except Exception as e:
            messagebox.showerror("错误", f"设置制表符时出错: {str(e)}")

    def set_window_title_format(self):
        """设置窗口标题显示格式"""
        # 更新内部状态
        self.window_title_format = self.window_title_format_var.get()

        # 保存配置
        self.save_config()

        # 更新窗口标题
        self.update_title_based_on_content()

    def apply_tab_settings(self):
        """应用制表符设置到文本区域"""
        # 设置制表符宽度
        # 使用字体的度量来正确计算制表符宽度
        font_config = self.text_area["font"]
        try:
            import tkinter.font as tkfont

            f = tkfont.Font(font=font_config)
            char_width = f.measure("0")  # 测量一个字符的宽度
            self.text_area.config(tabs=self.tab_width * char_width)
        except:
            # 如果获取字体宽度失败，使用一个合理的默认值
            self.text_area.config(tabs=self.tab_width * 8)  # 回退到像素计算

        # 设置是否使用空格替代制表符
        if self.use_spaces_for_tabs:
            # 创建一个绑定来拦截Tab键
            def on_tab_key(event):
                # 插入空格而不是制表符
                self.text_area.insert(tk.INSERT, " " * self.tab_width)
                # 返回'break'以阻止默认的制表符行为
                return "break"

            # 先移除可能存在的绑定
            self.text_area.unbind("<Tab>")
            # 添加新的绑定
            self.text_area.bind("<Tab>", on_tab_key)
        else:
            # 移除自定义绑定，使用默认的制表符行为
            self.text_area.unbind("<Tab>")

    def set_auto_save_interval(self):
        """设置自动保存间隔"""
        try:
            # 创建自定义对话框
            dialog = tk.Toplevel(self.root)
            dialog.title("设置自动保存间隔")
            dialog.resizable(False, False)
            dialog.transient(self.root)
            dialog.grab_set()

            # 设置对话框样式
            style = ttk.Style()
            style.configure(
                "CurrentValue.TLabel", font=("Microsoft YaHei UI", 15, "bold")
            )
            style.configure("Small.TButton", font=("Microsoft YaHei UI", 10, "bold"))
            style.configure("TLabel", font=("Microsoft YaHei UI", 12, "bold"))
            style.configure("Button.TButton", font=("Microsoft YaHei UI", 12, "bold"))

            # 居中显示对话框
            quick_edit_utils.center_window(dialog, 750, 270)

            # 设置窗口图标
            quick_edit_utils.set_window_icon(dialog)

            # 创建主框架
            main_frame = ttk.Frame(dialog, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)

            # 添加说明标签
            desc_label = ttk.Label(
                main_frame, text="请选择自动保存间隔时间:", style="CurrentValue.TLabel"
            )
            desc_label.pack(pady=(0, 10))

            # 创建滑块框架
            slider_frame = ttk.Frame(main_frame)
            slider_frame.pack(fill=tk.X, pady=(0, 15))

            # 当前值显示
            current_value_label = ttk.Label(
                slider_frame,
                text=f"当前值: {self.auto_save_interval}秒({self.auto_save_interval}秒)",
                style="TLabel",
            )
            current_value_label.pack(pady=(0, 10))

            # 滑块组件
            slider = ttk.Scale(
                slider_frame,
                from_=3,  # 最小值3秒
                to=3600,  # 最大值3600秒（1小时）
                orient=tk.HORIZONTAL,
                length=500,  # 增加滑块长度
                value=self.auto_save_interval,
            )
            slider.pack(pady=(0, 5))

            # 数值显示框架
            value_frame = ttk.Frame(slider_frame)
            value_frame.pack(fill=tk.X, pady=(10, 0))

            # 最小值标签
            min_label = ttk.Label(value_frame, text="3秒", foreground="gray")
            min_label.pack(side=tk.LEFT)

            # 常用值按钮框架
            common_values_frame = ttk.Frame(value_frame)
            common_values_frame.pack(side=tk.LEFT, padx=(20, 0))

            # 添加常用值按钮
            def set_slider_value(value):
                """设置滑块值并更新显示"""
                slider.set(value)
                update_value_label(value)

            # 3秒按钮
            btn_3s = ttk.Button(
                common_values_frame,
                text="3秒",
                style="Small.TButton",
                command=lambda: set_slider_value(3),
            )
            btn_3s.pack(side=tk.LEFT, padx=(0, 5))

            # 5秒按钮
            btn_5s = ttk.Button(
                common_values_frame,
                text="5秒",
                style="Small.TButton",
                command=lambda: set_slider_value(5),
            )
            btn_5s.pack(side=tk.LEFT, padx=(0, 5))

            # 15秒按钮
            btn_15s = ttk.Button(
                common_values_frame,
                text="15秒",
                style="Small.TButton",
                command=lambda: set_slider_value(15),
            )
            btn_15s.pack(side=tk.LEFT, padx=(0, 5))

            # 30秒按钮
            btn_30s = ttk.Button(
                common_values_frame,
                text="30秒",
                style="Small.TButton",
                command=lambda: set_slider_value(30),
            )
            btn_30s.pack(side=tk.LEFT, padx=(0, 5))

            # 5分钟按钮
            btn_5m = ttk.Button(
                common_values_frame,
                text="5分钟",
                style="Small.TButton",
                command=lambda: set_slider_value(300),
            )
            btn_5m.pack(side=tk.LEFT, padx=(0, 5))

            # 15分钟按钮
            btn_15m = ttk.Button(
                common_values_frame,
                text="15分钟",
                style="Small.TButton",
                command=lambda: set_slider_value(900),
            )
            btn_15m.pack(side=tk.LEFT)

            # 最大值标签
            max_label = ttk.Label(value_frame, text="60分钟", foreground="gray")
            max_label.pack(side=tk.RIGHT)

            # 实时更新当前值显示
            def update_value_label(val):
                # 将浮点数转换为整数
                val = int(float(val))
                display_val = val

                # 根据数值大小调整显示单位
                if val >= 3600:  # 1小时或以上
                    hours = val // 3600
                    minutes = (val % 3600) // 60
                    if minutes == 0:
                        display_val = f"{hours}小时"
                    else:
                        display_val = f"{hours}小时{minutes}分钟"
                elif val >= 60:  # 1分钟或以上
                    minutes = val // 60
                    seconds = val % 60
                    if seconds == 0:
                        display_val = f"{minutes}分钟"
                    else:
                        display_val = f"{minutes}分钟{seconds}秒"
                else:  # 秒数
                    display_val = f"{val}秒"

                current_value_label.config(text=f"当前值: {display_val}({val}秒)")

            # 绑定滑块事件
            slider.configure(command=update_value_label)

            # 按钮框架
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=(10, 0))

            # 添加提示信息
            info_label = ttk.Label(
                button_frame,
                text="提示: 值越小保存越频繁，可能影响编辑器性能",
                style="TLabel",
                foreground="gray",
            )
            info_label.pack(side=tk.LEFT, pady=(0, 5))

            # 按钮子框架
            buttons_frame = ttk.Frame(button_frame)
            buttons_frame.pack(side=tk.RIGHT)

            # 确定按钮
            def on_ok():
                interval = int(slider.get())
                self.auto_save_interval = interval
                self.save_config()
                # 更新状态栏显示
                self.show_default_auto_save_status()
                if self.auto_save_enabled:
                    self.stop_auto_save_timer()
                    self.start_auto_save_timer()
                dialog.destroy()
                # 使用辅助方法格式化显示
                display_interval = quick_edit_utils.format_auto_save_interval(interval)
                messagebox.showinfo(
                    "设置成功", f"自动保存间隔已设置为{display_interval}"
                )

            # 使用之前定义的Button.TButton样式
            ok_button = ttk.Button(
                buttons_frame,
                text="确定",
                command=on_ok,
                width=10,
                style="Button.TButton",
            )
            ok_button.pack(side=tk.RIGHT, padx=(5, 0))

            # 取消按钮
            def on_cancel():
                dialog.destroy()

            cancel_button = ttk.Button(
                buttons_frame,
                text="取消",
                command=on_cancel,
                width=10,
                style="Button.TButton",
            )
            cancel_button.pack(side=tk.RIGHT)

            # 初始化显示
            update_value_label(self.auto_save_interval)

            # 等待对话框关闭
            dialog.wait_window()

        except Exception as e:
            messagebox.showerror("错误", f"设置自动保存间隔时出错: {str(e)}")

    def change_theme(self, theme_name):
        """切换主题"""
        # 设置主题
        self.theme_manager.set_theme(theme_name)
        # 更新当前主题
        self.current_theme = theme_name
        # 保存主题配置
        self.save_config()

    def cycle_theme(self):
        """循环切换主题"""
        # 从主题管理器获取所有主题，保持与菜单中一致的顺序
        theme_list = self.theme_manager.get_theme_list()
        themes = [theme_key for _, theme_key in theme_list]

        # 找到当前主题在列表中的位置
        try:
            current_index = themes.index(self.current_theme)
            # 计算下一个主题的索引
            next_index = (current_index + 1) % len(themes)
            next_theme = themes[next_index]
        except ValueError:
            # 如果当前主题不在列表中，切换到第一个主题
            next_theme = themes[0]

        # 切换到下一个主题
        self.change_theme(next_theme)

        # 在状态栏显示切换信息
        theme_name = self.theme_manager.THEMES[next_theme].get("name", next_theme)
        self.left_status.config(text=f"主题已切换到: {theme_name}")

    def on_text_scroll(self, *args):
        """处理文本区域滚动事件"""
        # 调用原始滚动方法
        self.text_area.yview(*args)

    def on_text_scroll_with_line_numbers(self, *args):
        """处理文本区域滚动事件并同步更新行号显示"""
        # 调用原始滚动方法
        try:
            self.text_area.yview(*args)
        except tk.TclError:
            # 忽略无效的滚动参数
            pass
        # 更新行号显示
        self.update_line_numbers()

    def on_mouse_wheel(self, event):
        """处理鼠标滚轮事件"""
        # 处理鼠标滚轮滚动
        if event.delta > 0:
            self.text_area.yview_scroll(-1, "units")
        else:
            self.text_area.yview_scroll(1, "units")
        # 更新行号显示
        self.update_line_numbers()
        return "break"

    def on_key_press(self, event):
        """处理键盘按键事件"""
        # 检测Ctrl+H组合键，阻止默认的退格行为
        if (event.state & 0x4) and (event.keysym == "h" or event.char == "\x08"):
            return "break"

        # 检测@符号，弹出插入菜单
        if event.char == "@" and self.quick_insert_enabled:
            # 先插入@符号
            self.text_area.insert(tk.INSERT, "@")

            # 获取当前光标位置（@符号后的位置）
            current_pos = self.text_area.index(tk.INSERT)

            # 创建插入菜单
            insert_menu = self.insert_helper.create_insert_menu(self.root)

            # 获取@符号的位置（光标前一个字符）
            at_pos = self.text_area.index(f"{current_pos}-1c")

            # 获取光标在屏幕上的坐标
            bbox = self.text_area.bbox(at_pos)

            # 保存原始菜单项命令
            original_commands = {}

            # 为所有菜单项添加标记功能
            menu_length = insert_menu.index("end")
            for index in range(menu_length + 1):
                try:
                    # 获取菜单项标签（用于识别有效菜单项）
                    label = insert_menu.entrycget(index, "label")

                    # 如果是有效的菜单项（不是分隔符）
                    if label:
                        try:
                            # 尝试获取原始命令
                            command = insert_menu.entrycget(index, "command")
                            # 保存原始命令
                            original_commands[index] = command
                        except tk.TclError:
                            # 如果没有命令，可能是子菜单或其他特殊项
                            pass

                        # 创建新命令，执行原始命令并删除@符号
                        def make_new_command(idx):
                            def new_command():
                                # 删除@符号
                                self.text_area.delete(at_pos, current_pos)

                                # 执行原始命令
                                orig_cmd = original_commands.get(idx)
                                if orig_cmd and callable(orig_cmd):
                                    orig_cmd()
                                elif orig_cmd:
                                    # 如果是字符串命令，使用eval执行（在tkinter中常见）
                                    self.root.eval(orig_cmd)

                                # 关闭菜单
                                insert_menu.unpost()

                            return new_command

                        # 设置新命令
                        insert_menu.entryconfig(index, command=make_new_command(index))
                except tk.TclError:
                    # 忽略分隔符或无效项
                    pass

            # 如果获取坐标成功
            if bbox:
                x, y, width, height = bbox
                # 计算菜单显示位置
                abs_x = self.text_area.winfo_rootx() + x
                abs_y = self.text_area.winfo_rooty() + y + height + 5

                # 显示菜单
                insert_menu.post(abs_x, abs_y)

                # 菜单消失后处理
                def on_menu_closed():
                    # 恢复原始命令
                    for index, cmd in original_commands.items():
                        try:
                            insert_menu.entryconfig(index, command=cmd)
                        except tk.TclError:
                            pass

                    # 恢复焦点
                    self.text_area.focus_set()

                # 使用after方法定期检查菜单是否关闭
                def check_menu_closed():
                    try:
                        # 尝试获取菜单状态
                        insert_menu.tk.call(insert_menu._w, "index", "active")
                        # 如果没有异常，菜单仍然打开，继续检查
                        self.root.after(100, check_menu_closed)
                    except tk.TclError:
                        # 菜单已关闭，执行后续处理
                        on_menu_closed()

                # 开始检查菜单状态
                self.root.after(100, check_menu_closed)

            # 阻止默认的@符号插入（因为我们已经手动插入了）
            return "break"

        # 在适当的时候更新行号显示
        self.root.after(10, self.update_line_numbers)
        return None

    def on_window_configure(self, event):
        """处理窗口配置事件 (大小调整等)"""
        # 只有当事件源是主窗口时才更新行号显示
        if event.widget == self.root:
            # 延迟更新行号显示, 避免频繁触发
            self.schedule_line_number_update()

    def schedule_line_number_update(self, delay=50):
        """调度行号更新，实现防抖动机制"""
        # 取消之前的计划任务
        if hasattr(self, "_line_number_update_job"):
            self.root.after_cancel(self._line_number_update_job)

        # 计划新的更新任务
        self._line_number_update_job = self.root.after(delay, self.update_line_numbers)

    def update_line_numbers(self, event=None):
        """更新行号显示"""
        # 如果没有启用行号显示，直接返回
        if not getattr(self, "show_line_numbers", True):
            return

        # 清除之前的行号和高亮矩形
        self.line_numbers.delete("all")

        # 获取文本区域的行数
        try:
            # 获取总行数 (使用end-1c来正确获取最后一行)
            last_line = self.text_area.index("end-1c").split(".")[0]
            total_lines = int(last_line)

            # 获取可见区域的第一行和最后一行
            first_visible = int(self.text_area.index("@0,0").split(".")[0])
            last_visible = int(
                self.text_area.index(f"@0,{self.text_area.winfo_height()}").split(".")[
                    0
                ]
            )

            # 确保范围有效
            first_visible = max(1, first_visible)
            last_visible = min(total_lines, last_visible + 1)

            # 计算行号区域宽度 (根据行号位数动态调整宽度)
            # 只有当行数发生变化时才重新计算宽度
            if (
                not hasattr(self, "_cached_total_lines")
                or self._cached_total_lines != total_lines
            ):
                max_line_number = total_lines
                # 根据行号位数计算宽度：增加每数字宽度和额外空间确保行号能完整显示
                digits = len(str(max_line_number))
                line_number_width = max(40, digits * 13 + 10)
                self.line_numbers.config(width=line_number_width)
                # 缓存计算结果
                self._cached_line_number_width = line_number_width
                self._cached_total_lines = total_lines
            else:
                line_number_width = self._cached_line_number_width

            # 设置字体 (如果字体发生变化则更新)
            current_font = (self.font_family, self.font_size)
            if not hasattr(self, "_cached_font") or self._cached_font != current_font:
                self._cached_font = current_font

            # 绘制可见区域的行号
            for i in range(first_visible, last_visible + 1):
                # 使用dlineinfo方法获取更准确的行位置信息
                dlineinfo = self.text_area.dlineinfo(f"{i}.0")
                if dlineinfo:
                    y_pos = dlineinfo[1]  # y坐标
                    line_height = dlineinfo[3]  # 行高
                    # 创建行号背景矩形（默认透明，鼠标悬浮时会使用悬浮颜色）
                    self.line_numbers.create_rectangle(
                        0,
                        y_pos,
                        line_number_width,
                        y_pos + line_height,
                        fill="",
                        outline="",
                        tags=("line_bg", f"line_{i}"),
                    )
                    # 在行号区域绘制行号
                    self.line_numbers.create_text(
                        line_number_width - 5,
                        y_pos + line_height // 2,  # x, y坐标
                        text=str(i),
                        font=current_font,
                        fill="gray",
                        anchor="e",  # 右对齐
                        tags=("line_number", f"line_{i}"),
                    )
                else:
                    # 如果dlineinfo不可用, 使用替代方法计算位置
                    # 这种情况在某些特殊情况下可能会发生
                    pass
        except Exception as e:
            # 忽略错误, 保持程序稳定
            print(f"Error in update_line_numbers: {e}")
            pass

    def on_line_number_hover(self, event):
        """处理鼠标悬浮在行号区域的事件，高亮对应的整个文本行"""
        try:
            # 获取鼠标在canvas中的y坐标
            y = event.y

            # 获取文本区域中对应y坐标的行号
            text_index = self.text_area.index(f"@0,{y}")
            hovered_line = text_index.split(".")[0]

            # 获取当前主题的行号悬浮背景色
            theme = self.theme_manager.get_current_theme()
            hover_bg_color = theme.get("line_numbers_hover_bg", "#e0e0e0")

            # 先清除所有之前的高亮
            self.on_line_number_leave(event)

            # 高亮当前悬停的行号背景
            for item in self.line_numbers.find_withtag(f"line_{hovered_line}"):
                if item in self.line_numbers.find_withtag("line_bg"):
                    self.line_numbers.itemconfig(item, fill=hover_bg_color)

            # 高亮整个文本行
            start_pos = f"{hovered_line}.0"
            end_pos = f"{hovered_line}.end"

            # 使用tag_add添加高亮标记
            self.text_area.tag_add("line_hover", start_pos, end_pos)
            # 配置高亮标签的背景色
            self.text_area.tag_config("line_hover", background=hover_bg_color)

        except Exception:
            # 忽略错误，保持程序稳定
            pass

    def on_line_number_leave(self, event):
        """处理鼠标退出行号区域的事件，清除所有高亮"""
        try:
            # 清除文本行高亮
            if "line_hover" in self.text_area.tag_names():
                self.text_area.tag_remove("line_hover", "1.0", "end")

            # 清除所有行号背景色
            for item in self.line_numbers.find_withtag("line_bg"):
                self.line_numbers.itemconfig(item, fill="")
        except Exception:
            # 忽略错误，保持程序稳定
            pass

    def create_toolbar(self):
        """创建工具栏"""
        # 如果已经有工具栏, 先销毁
        if hasattr(self, "toolbar"):
            self.toolbar.destroy()

        self.toolbar = ttk.Frame(self.root)
        self.toolbar.pack(fill=tk.X, before=self.text_frame)

        # 创建按钮列表以便后续更新样式
        self.toolbar_buttons = []

        # 文件操作按钮
        new_btn = ttk.Button(self.toolbar, text="新建", command=self.new_file)
        new_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(new_btn)

        open_btn = ttk.Button(self.toolbar, text="打开", command=self.open_file)
        open_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(open_btn)

        save_btn = ttk.Button(self.toolbar, text="保存", command=self.save_file)
        save_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(save_btn)

        save_as_btn = ttk.Button(self.toolbar, text="另存为", command=self.save_as_file)
        save_as_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(save_as_btn)

        # 只读模式切换按钮
        readonly_btn = ttk.Button(
            self.toolbar, text="只读模式", command=self.toggle_readonly_mode
        )
        readonly_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(readonly_btn)

        # 关闭文件按钮
        close_file_btn = ttk.Button(
            self.toolbar, text="关闭文件", command=self.close_file
        )
        close_file_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(close_file_btn)

        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=4
        )

        # 查找替换按钮
        find_replace_btn = ttk.Button(
            self.toolbar, text="查找替换", command=self.show_find_dialog
        )
        find_replace_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(find_replace_btn)

        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=4
        )

        # 编辑操作按钮
        undo_btn = ttk.Button(self.toolbar, text="撤销", command=self.undo_text)
        undo_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(undo_btn)

        redo_btn = ttk.Button(self.toolbar, text="重做", command=self.redo_text)
        redo_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(redo_btn)

        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=4
        )

        cut_btn = ttk.Button(self.toolbar, text="剪切", command=self.cut_text)
        cut_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(cut_btn)

        copy_btn = ttk.Button(self.toolbar, text="复制", command=self.copy_text)
        copy_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(copy_btn)

        paste_btn = ttk.Button(self.toolbar, text="粘贴", command=self.paste_text)
        paste_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(paste_btn)

        # 添加分隔线
        sep = ttk.Separator(self.toolbar, orient=tk.VERTICAL)
        sep.pack(side=tk.LEFT, padx=5, fill=tk.Y)

        # 字体效果按钮
        bold_btn = ttk.Button(self.toolbar, text="加粗", command=self.toggle_bold)
        bold_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(bold_btn)

        italic_btn = ttk.Button(self.toolbar, text="斜体", command=self.toggle_italic)
        italic_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(italic_btn)

        underline_btn = ttk.Button(
            self.toolbar, text="下划线", command=self.toggle_underline
        )
        underline_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(underline_btn)

        overstrike_btn = ttk.Button(
            self.toolbar, text="删除线", command=self.toggle_overstrike
        )
        overstrike_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(overstrike_btn)

        # 应用当前主题到工具栏按钮
        self.theme_manager.apply_theme()

    def create_statusbar(self):
        """创建状态栏"""
        # 获取当前主题配置
        theme = self.theme_manager.get_current_theme()

        # 创建状态栏框架, 使用主题背景色
        self.statusbar_frame = tk.Frame(
            self.root, relief=tk.SUNKEN, bd=1, bg=theme["statusbar_bg"]
        )
        self.statusbar_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # 创建独立的状态栏字体配置
        statusbar_font = font.Font(family="Microsoft YaHei UI", size=10)

        # 左侧状态信息, 使用主题背景色和前景色
        self.left_status = tk.Label(
            self.statusbar_frame,
            text="就绪 | 第1行 | 第1列",
            anchor=tk.W,
            bg=theme["statusbar_bg"],
            fg=theme["statusbar_fg"],
            font=statusbar_font,
            cursor="hand2",  # 添加手型光标表示可点击
        )
        self.left_status.pack(side=tk.LEFT, padx=5)

        # 为左侧状态栏绑定鼠标点击事件
        self.left_status.bind("<Button-1>", lambda e: self.show_document_stats())

        # 中间自动保存状态标签, 使用主题背景色和前景色
        self.center_status = tk.Label(
            self.statusbar_frame,
            text="",
            anchor=tk.CENTER,
            bg=theme["statusbar_bg"],
            fg=theme["statusbar_fg"],
            font=statusbar_font,
        )
        self.center_status.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        # 右侧状态信息 (编码和换行符类型), 使用主题背景色和前景色
        self.right_status = tk.Label(
            self.statusbar_frame,
            text="UTF-8 | LF",
            anchor=tk.E,
            cursor="hand2",
            bg=theme["statusbar_bg"],
            fg=theme["statusbar_fg"],
            font=statusbar_font,
        )
        self.right_status.pack(side=tk.RIGHT, padx=5)

        # 为状态栏绑定右键点击事件到智能菜单处理函数
        self.right_status.bind("<Button-3>", self.on_statusbar_right_click)

        # 绑定光标移动事件更新状态栏
        self.text_area.bind("<<Modified>>", self.update_statusbar)
        self.text_area.bind("<KeyRelease>", self.update_statusbar)
        self.text_area.bind("<ButtonRelease>", self.update_statusbar)
        # 绑定选中事件
        self.text_area.bind("<<Selection>>", self.update_statusbar)

    def update_statusbar(self, event=None):
        """更新状态栏信息"""
        # 根据文本内容更新窗口标题
        self.update_title_based_on_content()

        try:
            # 获取光标位置
            cursor_pos = self.text_area.index(tk.INSERT)
            row, col = cursor_pos.split(".")

            # 修正列数计算，考虑制表符宽度
            # 当使用实际制表符（非空格替代）时，计算真实显示的列数
            if not self.use_spaces_for_tabs:
                # 获取光标所在行的内容
                current_line = self.text_area.get(f"{row}.0", f"{row}.{col}")
                # 计算显示的列数
                display_col = 0
                for char in current_line:
                    if char == "\t":
                        # 制表符宽度为self.tab_width，计算到下一个制表位
                        display_col += self.tab_width - (display_col % self.tab_width)
                    else:
                        display_col += 1
                col = str(display_col)

            # 获取总字符数
            char_count = len(self.text_area.get("1.0", tk.END + "-1c"))

            # 检查是否有选中文本
            try:
                selected_text = self.text_area.selection_get()
                selected = True
                selected_char_count = len(selected_text)
                # 计算选中的行数
                selected_lines = selected_text.count("\n") + 1

                # 提升选择标记的优先级，确保选中内容背景色始终可见
                self.text_area.tag_raise("sel")
            except tk.TclError:
                selected = False
                selected_char_count = 0
                selected_lines = 0

            # 构建左侧状态信息
            if self.readonly_mode:
                status_prefix = "只读模式 | "
            else:
                status_prefix = ""

            if self.text_area.edit_modified():
                if selected:
                    status_text = f"{status_prefix}已修改 | 第{row}行 | 第{col}列 | {char_count}个字符 | 已选择{selected_char_count}个字符({selected_lines}行)"
                else:
                    status_text = f"{status_prefix}已修改 | 第{row}行 | 第{col}列 | {char_count}个字符"
            else:
                if selected:
                    status_text = f"{status_prefix}就绪 | 第{row}行 | 第{col}列 | {char_count}个字符 | 已选择{selected_char_count}个字符({selected_lines}行)"
                else:
                    status_text = f"{status_prefix}就绪 | 第{row}行 | 第{col}列 | {char_count}个字符"

            self.left_status.config(text=status_text)

            # 更新右侧状态信息 (编码和换行符类型)
            if hasattr(self, "encoding") and hasattr(self, "line_ending"):
                file_info = f"{self.encoding.upper()} | {self.line_ending}"
                if self.current_file:
                    file_name = os.path.basename(self.current_file)
                    right_text = f"{file_name} | {file_info}"
                else:
                    right_text = file_info
                self.right_status.config(text=right_text)

            # 更新行号显示
            self.update_line_numbers()

        except Exception as e:
            self.left_status.config(text="状态更新错误")

    def show_document_stats(self):
        """显示文档统计信息窗口（单例模式）"""
        # 单例模式：检查统计窗口是否已经存在
        if hasattr(self, "_stats_window") and self._stats_window.winfo_exists():
            # 如果窗口存在，将其置于前台
            self._stats_window.lift()
            self._stats_window.focus_force()
            return

        # 创建顶层窗口
        self._stats_window = tk.Toplevel(self.root)
        self._stats_window.title("文档统计信息")
        self._stats_window.resizable(False, False)

        # 居中显示窗口
        quick_edit_utils.center_window(self._stats_window, 450, 380)

        # 设置窗口图标
        quick_edit_utils.set_window_icon(self._stats_window)

        # 设置窗口模态
        self._stats_window.transient(self.root)
        self._stats_window.grab_set()

        # 获取当前主题
        theme = self.theme_manager.get_current_theme()

        # 设置窗口背景色
        self._stats_window.configure(bg=theme["statusbar_bg"])

        # 创建主框架
        main_frame = tk.Frame(self._stats_window, bg=theme["statusbar_bg"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 标题标签
        title_label = tk.Label(
            main_frame,
            text="文档统计信息",
            font=font.Font(family="Microsoft YaHei UI", size=15, weight="bold"),
            bg=theme["statusbar_bg"],
            fg=theme["statusbar_fg"],
        )
        title_label.pack(pady=(0, 20))

        # 统计信息框架
        stats_frame = tk.Frame(main_frame, bg=theme["statusbar_bg"])
        stats_frame.pack(fill=tk.X, expand=False)

        # 创建统计信息标签
        self.stats_labels = {}
        stats_info = [
            ("字符总数:", "chars_total"),
            ("字符数(不含空格):", "chars_no_spaces"),
            ("单词数:", "words_count"),
            ("行数:", "lines_count"),
            ("段落数:", "paragraphs_count"),
            ("文件大小:", "file_size"),
        ]

        for i, (label_text, key) in enumerate(stats_info):
            row_frame = tk.Frame(stats_frame, bg=theme["statusbar_bg"])
            row_frame.pack(fill=tk.X, pady=3)  # 减小垂直间距

            label = tk.Label(
                row_frame,
                text=label_text,
                font=font.Font(family="Microsoft YaHei UI", size=12),
                bg=theme["statusbar_bg"],
                fg=theme["statusbar_fg"],
                anchor=tk.W,
            )
            label.pack(side=tk.LEFT)

            value_label = tk.Label(
                row_frame,
                text="计算中...",
                font=font.Font(family="Microsoft YaHei UI", size=12, weight="bold"),
                bg=theme["statusbar_bg"],
                fg=theme["statusbar_fg"],
                anchor=tk.E,
            )
            value_label.pack(side=tk.RIGHT)

            self.stats_labels[key] = value_label

        # 进度条框架 - 完全移除顶部边距
        progress_frame = tk.Frame(main_frame, bg=theme["statusbar_bg"])
        progress_frame.pack(fill=tk.X, pady=(0, 0))

        self.progress_var = tk.StringVar(value="正在统计文档信息...")
        progress_label = tk.Label(
            progress_frame,
            textvariable=self.progress_var,
            font=font.Font(family="Microsoft YaHei UI", size=12),
            bg=theme["statusbar_bg"],
            fg=theme["statusbar_fg"],
        )
        progress_label.pack()

        # 关闭按钮 - 进一步减少顶部边距
        close_button = tk.Button(
            main_frame,
            text="关闭",
            command=self._stats_window.destroy,
            font=font.Font(family="Microsoft YaHei UI", size=12),
            bg=theme["menu_bg"],
            fg=theme["menu_fg"],
            activebackground=theme["menu_active_bg"],
            activeforeground=theme["menu_active_fg"],
        )
        close_button.pack(pady=(5, 0))

        # 启动异步统计任务
        self.start_document_stats_calculation()

        # 等待窗口关闭
        self.root.wait_window(self._stats_window)

    def start_document_stats_calculation(self):
        """启动异步文档统计计算"""
        # 创建队列用于线程间通信
        self.stats_queue = queue.Queue()

        # 在单独的线程中执行统计计算
        stats_thread = threading.Thread(target=self.calculate_document_stats)
        stats_thread.daemon = True
        stats_thread.start()

        # 定期检查统计结果
        self.check_stats_calculation()

    def calculate_document_stats(self):
        """在后台线程中计算文档统计信息"""
        try:
            # 获取文档内容
            content = self.text_area.get("1.0", tk.END + "-1c")

            # 计算各种统计信息
            chars_total = len(content)
            chars_no_spaces = len(re.sub(r"\s", "", content))
            words_count = len(re.findall(r"\b\w+\b", content))
            lines_count = content.count("\n") + 1
            paragraphs_count = len([p for p in content.split("\n\n") if p.strip()])

            # 文件大小 - 优化：如果文件已保存，直接获取文件大小；否则计算内容的UTF-8编码大小
            if self.current_file and os.path.exists(self.current_file):
                # 对于已保存的文件，直接获取文件大小
                file_size = os.path.getsize(self.current_file)
            else:
                # 对于未保存的文件，计算内容的UTF-8编码大小
                file_size = len(content.encode("utf-8"))

            if file_size < 1024:
                file_size_text = f"{file_size} 字节"
            elif file_size < 1024 * 1024:
                file_size_text = f"{file_size / 1024:.2f} KB"
            else:
                file_size_text = f"{file_size / (1024 * 1024):.2f} MB"

            # 将结果放入队列
            result = {
                "chars_total": chars_total,
                "chars_no_spaces": chars_no_spaces,
                "words_count": words_count,
                "lines_count": lines_count,
                "paragraphs_count": paragraphs_count,
                "file_size": file_size_text,
            }

            self.stats_queue.put(("success", result))
        except Exception as e:
            self.stats_queue.put(("error", str(e)))

    def check_stats_calculation(self):
        """定期检查统计计算结果并更新UI"""
        try:
            # 检查队列中是否有结果
            status, result = self.stats_queue.get_nowait()

            if status == "success":
                # 更新统计信息标签
                for key, value in result.items():
                    if key in self.stats_labels:
                        self.stats_labels[key].config(text=str(value))

                # 更新进度信息
                self.progress_var.set("统计完成")
            else:
                # 处理错误
                self.progress_var.set(f"统计出错: {result}")

        except queue.Empty:
            # 队列为空，稍后再检查
            self.root.after(100, self.check_stats_calculation)
        except Exception as e:
            self.progress_var.set(f"更新出错: {str(e)}")

    def bind_shortcuts(self):
        """绑定快捷键"""
        # 绑定Ctrl+H到空操作，覆盖默认的退格行为
        self.root.bind("<Control-h>", lambda e: "break")
        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-S>", lambda e: self.save_as_file())
        self.root.bind("<Control-w>", lambda e: self.close_file())
        self.root.bind("<Control-q>", lambda e: self.exit_app())
        self.root.bind("<Control-a>", lambda e: self.select_all())
        self.root.bind("<Control-f>", lambda e: self.show_find_dialog())
        self.root.bind("<Home>", lambda e: self.go_to_home())
        self.root.bind("<End>", lambda e: self.go_to_end())
        self.root.bind("<Control-r>", lambda e: self.toggle_readonly_mode())
        self.root.bind("<Control-g>", lambda e: self.go_to_line())
        self.root.bind("<Control-t>", lambda e: self.cycle_theme())  # 循环切换主题
        self.root.bind(
            "<Control-R>", lambda e: self.open_containing_folder()
        )  # 打开所在文件夹
        self.root.bind(
            "<Control-Shift-I>", lambda e: self.show_document_stats()
        )  # 显示文档统计信息
        # 绑定语法高亮快捷键 - 先翻转变量值再调用方法
        self.root.bind(
            "<Control-Shift-K>",
            lambda e: (
                self.syntax_highlighting_var.set(
                    not self.syntax_highlighting_var.get()
                ),
                self.toggle_syntax_highlighting(),
            )[1],
        )
        # 绑定PgUp和PgDn键用于页面滚动
        self.root.bind("<Prior>", lambda e: self.page_up())  # PgUp键
        self.root.bind("<Next>", lambda e: self.page_down())  # PgDn键

    def update_font(self):
        """更新字体设置"""
        # 使用tkinter的font模块创建字体对象
        # 创建字体对象，直接设置所有样式属性
        font_config = font.Font(
            family=self.font_family,
            size=self.font_size,
            weight="bold" if self.font_bold else "normal",
            slant="italic" if self.font_italic else "roman",
            underline=self.font_underline,
            overstrike=self.font_overstrike,
        )

        # 应用字体到文本区域
        self.text_area.config(font=font_config)

        # 刷新UI确保样式正确应用
        self.text_area.update_idletasks()

        # 更新行号显示
        self.update_line_numbers()

    def on_line_number_click(self, event):
        """处理行号区域点击事件 - 全选点击的行"""
        try:
            # 获取鼠标在canvas中的y坐标
            y = event.y

            # 获取文本区域中对应y坐标的行号
            text_index = self.text_area.index(f"@0,{y}")
            clicked_line = text_index.split(".")[0]

            # 全选该行内容
            start_pos = f"{clicked_line}.0"
            end_pos = f"{clicked_line}.end"

            # 无论行是否有内容，都执行全选操作
            self.text_area.tag_remove(tk.SEL, "1.0", tk.END)
            self.text_area.tag_add(tk.SEL, start_pos, end_pos)
            # 确保选中内容可见
            self.text_area.see(start_pos)
            # 确保文本区域获得焦点
            self.text_area.focus_set()

        except Exception as e:
            # 忽略错误, 保持程序稳定
            pass

    def on_line_ending_right_click(self, event=None):
        """处理换行符类型标签右键点击事件"""
        # 创建换行符选择菜单
        line_ending_menu = tk.Menu(self.root, tearoff=0)

        # 换行符选项
        line_endings = ["LF", "CRLF", "CR"]
        line_ending_names = {
            "LF": "Unix/Linux (LF)",
            "CRLF": "Windows (CRLF)",
            "CR": "Mac (CR)",
        }

        # 添加换行符选项到菜单
        for ending in line_endings:
            display_name = line_ending_names.get(ending, ending)
            line_ending_menu.add_command(
                label=display_name, command=lambda e=ending: self.set_line_ending(e)
            )

        # 显示菜单
        try:
            line_ending_menu.tk_popup(event.x_root, event.y_root)
        finally:
            line_ending_menu.grab_release()

    def on_statusbar_right_click(self, event=None):
        """处理状态栏右键点击事件，根据点击位置判断是编码部分还是换行符部分"""
        # 获取点击位置相对于标签的坐标
        x = event.x

        # 获取当前显示的文本
        current_text = self.right_status.cget("text")

        # 判断点击位置是在编码部分还是换行符部分
        # 文本格式为 "文件名 | 编码 | 换行符" 或 "编码 | 换行符"
        if " | " in current_text:
            # 分割文本获取各个部分
            parts = current_text.split(" | ")

            # 获取标签的宽度
            width = self.right_status.winfo_width()
            total_length = len(current_text)

            if len(parts) == 3:
                # 有文件名的情况: "文件名 | 编码 | 换行符"
                filename_part = parts[0]
                encoding_part = parts[1]
                line_ending_part = parts[2]

                # 文件名部分的长度（包含" | "）
                filename_end_pos = len(filename_part) + 3
                # 编码部分的结束位置（包含" | "）
                encoding_end_pos = filename_end_pos + len(encoding_part) + 3

                # 计算各部分的宽度位置
                if total_length > 0:
                    filename_end_x = (filename_end_pos / total_length) * width
                    encoding_end_x = (encoding_end_pos / total_length) * width
                else:
                    filename_end_x = 0
                    encoding_end_x = width / 2

                # 只在点击编码或换行符部分时显示菜单
                if filename_end_x <= x:
                    if x < encoding_end_x:
                        # 点击的是编码部分
                        self.on_encoding_click(event)
                    else:
                        # 点击的是换行符部分
                        self.on_line_ending_right_click(event)
                # 点击文件名部分时不执行任何操作
            else:
                # 没有文件名的情况: "编码 | 换行符"
                encoding_part = parts[0]
                line_ending_part = parts[1]

                # 计算编码部分的结束位置
                encoding_end_pos = len(encoding_part) + 3

                # 计算各部分的宽度位置
                if total_length > 0:
                    encoding_end_x = (encoding_end_pos / total_length) * width
                else:
                    encoding_end_x = width / 2

                # 正常处理编码和换行符部分的点击
                if x < encoding_end_x:
                    # 点击的是编码部分
                    self.on_encoding_click(event)
                else:
                    # 点击的是换行符部分
                    self.on_line_ending_right_click(event)
        else:
            # 如果没有找到分隔符，默认显示换行符菜单
            self.on_line_ending_right_click(event)

    def go_to_line(self):
        """转到指定行"""
        # 创建对话框
        line_number = simpledialog.askinteger("转到行", "请输入行号:", parent=self.root)

        # 检查用户是否输入了有效的行号
        if line_number is not None and line_number > 0:
            # 获取总行数
            total_lines = int(self.text_area.index("end-1c").split(".")[0])

            # 确保行号不超过总行数
            if line_number > total_lines:
                line_number = total_lines

            # 转到指定行
            self.text_area.mark_set(tk.INSERT, f"{line_number}.0")
            self.text_area.see(f"{line_number}.0")
            self.text_area.focus_set()

    def on_encoding_click(self, event=None):
        """处理编码标签右键点击事件"""
        # 创建编码选择菜单，只显示常用编码
        encoding_menu = self.create_encoding_menu(show_common_only=True)

        # 显示菜单
        try:
            encoding_menu.tk_popup(event.x_root, event.y_root)
        finally:
            encoding_menu.grab_release()

    def create_encoding_menu(self, show_common_only=False):
        """创建编码选择菜单

        Args:
            show_common_only (bool): 是否只显示常用编码，默认False显示完整编码列表
        """
        # 创建编码选择菜单
        encoding_menu = tk.Menu(self.root, tearoff=0)

        if show_common_only:
            # 只显示常用编码
            common_encodings = [
                "UTF-8",
                "UTF-16",
                "GBK",
                "GB2312",
                "ASCII",
                "ISO-8859-1",
            ]
            for enc in common_encodings:
                encoding_menu.add_command(
                    label=enc, command=lambda e=enc: self.change_encoding(e)
                )
            # 添加"更多"选项，点击后显示完整编码列表
            encoding_menu.add_separator()
            encoding_menu.add_command(label="更多...", command=self.show_all_encodings)
        else:
            # 显示完整编码列表
            encodings = quick_edit_utils.get_supported_encodings()
            for enc in encodings:
                encoding_menu.add_command(
                    label=enc, command=lambda e=enc: self.change_encoding(e)
                )

        return encoding_menu

    def show_all_encodings(self):
        """显示完整编码列表"""
        # 创建完整编码列表菜单
        encoding_menu = self.create_encoding_menu(show_common_only=False)

        # 显示菜单在光标位置
        try:
            # 获取当前鼠标位置
            x = self.root.winfo_pointerx()
            y = self.root.winfo_pointery()
            encoding_menu.tk_popup(x, y)
        finally:
            encoding_menu.grab_release()

    def change_encoding(self, new_encoding):
        """更改文件编码"""
        old_encoding = self.encoding
        self.encoding = new_encoding

        # 将编辑器标记为已修改状态，确保切换文件时弹出保存提示
        self.text_area.edit_modified(True)

        # 更新状态栏
        self.update_statusbar()

        # 显示提示信息
        messagebox.showinfo(
            "编码切换", f"文件编码已从 {old_encoding} 切换为: {new_encoding}"
        )

    def set_line_ending(self, new_ending):
        """设置换行符类型"""
        old_ending = self.line_ending
        self.line_ending = new_ending

        # 将编辑器标记为已修改状态，确保切换文件时弹出保存提示
        self.text_area.edit_modified(True)

        # 更新状态栏
        self.update_statusbar()

        # 显示提示信息
        ending_names = {
            "LF": "Unix/Linux (LF)",
            "CRLF": "Windows (CRLF)",
            "CR": "Mac (CR)",
        }
        old_name = ending_names.get(old_ending, old_ending)
        new_name = ending_names.get(new_ending, new_ending)
        messagebox.showinfo(
            "换行符切换", f"换行符格式已从 {old_name} 切换为: {new_name}"
        )

    def check_and_handle_unsaved_changes(self, operation_type="关闭"):
        """检查并处理未保存的更改

        Args:
            operation_type (str): 操作类型，用于在对话框中显示（如"关闭"、"退出"等）

        Returns:
            tuple: (是否继续操作, 是否已保存)
        """
        # 检查文本框是否有内容
        content = self.text_area.get(1.0, tk.END).strip()
        saved = False

        # 情况1: 如果有打开的文件
        if self.current_file:
            # 情况1a: 打开文件且已被修改
            if content and self.text_area.edit_modified():
                title = f"{operation_type}确认"
                message = f"文档已被修改, 是否保存更改？"
                if operation_type == "退出":
                    message = f"文档已被修改, 是否保存后再{operation_type}？"

                result = messagebox.askyesnocancel(title, message)
                if result is True:  # 是, 保存
                    saved = self.save_file()  # 只有保存成功才设置为True
                    # 如果用户在保存对话框中点击了取消，save_file会返回None
                    if saved is None:
                        return False, False  # 取消整个操作
                elif result is False:  # 否, 不保存
                    pass  # 不保存直接继续
                else:  # 取消
                    return False, False  # 取消操作
        else:
            # 情况2: 没有打开文件 (新建文件或直接输入内容)
            if content:
                title = f"{operation_type}确认"
                message = f"文档有内容, 是否保存？"
                if operation_type == "退出":
                    message = f"文档有内容, 是否保存后再{operation_type}？"

                result = messagebox.askyesnocancel(title, message)
                if result is True:  # 是, 保存
                    saved = self.save_file()  # 只有保存成功才设置为True
                    # 如果用户在保存对话框中点击了取消，save_file会返回None
                    if saved is None:
                        return False, False  # 取消整个操作
                elif result is False:  # 否, 不保存
                    pass  # 不保存直接继续
                else:  # 取消
                    return False, False  # 取消操作

        return True, saved

    # 文件操作方法
    def close_file(self):
        """关闭当前文件"""
        # 检查当前是否有打开的文件
        if not self.current_file:
            messagebox.showinfo("提示", "当前没有打开的文件")
            return

        # 检查是否处于只读模式
        if self.readonly_mode:
            messagebox.showinfo("提示", "当前处于只读模式，请先关闭只读模式再关闭文件")
            return

        # 使用公共方法检查并处理未保存的更改
        continue_operation, saved = self.check_and_handle_unsaved_changes("关闭")

        if not continue_operation:
            return  # 用户取消操作

        # 如果有当前文件且启用了备份功能，需要清理备份文件
        # 两种情况需要清理：1. 用户选择保存（saved=True） 2. 文件未被修改
        if self.current_file and self.backup_enabled:
            # 检查文件是否未被修改
            if saved or not self.text_area.edit_modified():
                self.cleanup_backup()

        # 使用辅助方法重置文件状态
        self._reset_file_state()

        # 显示提示信息
        messagebox.showinfo("文件关闭", "文件已成功关闭")

    def new_file(self):
        """新建文件"""
        # 检查是否有未保存的更改
        continue_operation, _ = self.check_and_handle_unsaved_changes("新建")
        if not continue_operation:
            return  # 用户取消操作

        # 清理备份文件
        self.cleanup_backup()

        # 使用辅助方法重置文件状态
        self._reset_file_state()
        # 移除状态栏更新, 因为_reset_file_state已经包含了这一步
        pass

        # 设置文本框获取焦点
        self.text_area.focus_set()

    def open_file(self, file_path=None):
        """打开文件"""
        # 检查是否有未保存的更改
        continue_operation, _ = self.check_and_handle_unsaved_changes("打开")
        if not continue_operation:
            return  # 用户取消操作

        # 如果没有提供文件路径，则通过对话框选择
        if not file_path:
            file_path = filedialog.askopenfilename(
                defaultextension=".txt",
                filetypes=[("All Files", "*.*")],
            )

            # 如果用户取消选择文件，则返回
            if not file_path:
                return

        # 检查是否存在备份文件并询问用户
        self.current_file = file_path  # 临时设置current_file以便检查备份
        if self.backup_enabled:
            backup_file = file_path + ".bak"
            if os.path.exists(backup_file):
                # 提示用户是否恢复备份
                result = messagebox.askyesnocancel(
                    "发现备份文件",
                    f"检测到文件 '{os.path.basename(file_path)}' 的备份文件\n"
                    "您想要：\n"
                    "- 是：从备份文件恢复内容\n"
                    "- 否：打开原始文件并删除备份\n"
                    "- 取消：取消打开文件操作",
                )
                if result is None:  # 取消操作
                    self.current_file = None
                    return
                elif result is True:  # 从备份恢复
                    # 先保存当前current_file以便restore_from_backup使用
                    # 然后在主线程中处理恢复
                    self.root.after(0, self._handle_backup_restore)
                    return
                # 否：继续打开原始文件，并稍后删除备份

        # 重置取消标志
        self.file_read_cancelled = False

        # 检查文件大小，如果小于100KB则不显示进度窗口
        file_size = os.path.getsize(file_path)
        show_progress = file_size >= self.small_file_size_threshold

        # 创建进度窗口（仅对大文件）
        if show_progress:
            self._create_progress_window()

        # 在新线程中读取文件
        self.file_read_thread = threading.Thread(
            target=self._async_read_file, args=(file_path, show_progress), daemon=True
        )
        self.file_read_thread.start()

    def _handle_backup_restore(self):
        """处理备份文件恢复的回调方法"""
        if self.current_file:
            backup_file = self.current_file + ".bak"
            try:
                # 先检测备份文件是否为二进制文件
                sample_data = None
                with open(backup_file, "rb") as file:
                    # 读取1KB样本数据
                    sample_data = file.read(1024)

                # 检测是否为二进制文件
                if quick_edit_utils.is_binary_file(sample_data=sample_data):
                    messagebox.showerror(
                        "恢复失败", "备份文件似乎是二进制文件，无法恢复。"
                    )
                    return

                # 使用同一样本数据检测编码和换行符
                encoding, line_ending = (
                    quick_edit_utils.detect_file_encoding_and_line_ending(
                        sample_data=sample_data
                    )
                )

                # 读取备份内容
                with codecs.open(
                    backup_file, "r", encoding=encoding, errors="replace"
                ) as f:
                    content = f.read()

                # 复用_finish_open_file方法来处理文件内容，避免代码重复
                self._finish_open_file(
                    self.current_file, content, encoding, line_ending
                )

                messagebox.showinfo("恢复成功", "已从备份文件恢复内容")

                # 只有在文件存在时才删除
                if os.path.exists(backup_file):
                    # 恢复后删除备份文件
                    try:
                        os.remove(backup_file)
                    except Exception as e:
                        print(f"删除备份文件失败: {e}")

            except Exception as e:
                messagebox.showerror("恢复失败", f"从备份文件恢复时出错: {str(e)}")
                # 恢复失败后尝试打开原始文件
                self.open_file(self.current_file)

    def _create_progress_window(self):
        """创建文件读取进度窗口"""
        if self.progress_window and self.progress_window.winfo_exists():
            self.progress_window.lift()
            return

        self.progress_window = tk.Toplevel(self.root)
        self.progress_window.title("正在打开文件...")
        self.progress_window.resizable(False, False)
        self.progress_window.transient(self.root)
        quick_edit_utils.center_window(self.progress_window, 300, 100)
        quick_edit_utils.set_window_icon(self.progress_window)

        # 设置为模态窗口，但允许主窗口响应
        self.progress_window.grab_set()

        # 添加标签和进度条
        label = ttk.Label(self.progress_window, text="正在读取文件内容...")
        label.pack(pady=10)

        self.progress_bar = ttk.Progressbar(self.progress_window, mode="indeterminate")
        self.progress_bar.pack(fill=tk.X, padx=20, pady=10)
        self.progress_bar.start()

        # 添加取消按钮
        cancel_button = ttk.Button(
            self.progress_window, text="取消", command=self._cancel_file_read
        )
        cancel_button.pack(pady=5)

        # 处理窗口关闭事件
        self.progress_window.protocol("WM_DELETE_WINDOW", self._cancel_file_read)

    def _cancel_file_read(self):
        """取消文件读取"""
        self.file_read_cancelled = True
        if self.progress_window and self.progress_window.winfo_exists():
            self.progress_window.destroy()
            self.progress_window = None

    def _close_progress_window(self):
        """关闭进度窗口"""
        if self.progress_window and self.progress_window.winfo_exists():
            self.progress_window.destroy()
        self.progress_window = None

    def _async_read_file(self, file_path, show_progress=True):
        """异步读取文件内容"""
        try:
            # 检查文件大小
            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size:
                formatted_size = quick_edit_utils.format_file_size(file_size)
                max_size = quick_edit_utils.format_file_size(self.max_file_size)

                # 确保在主线程中显示错误消息
                def show_error():
                    messagebox.showerror(
                        "文件过大",
                        f"无法打开文件: {os.path.basename(file_path)}\n"
                        f"文件大小: {formatted_size}\n"
                        f"超过最大允许大小: {max_size}\n"
                        f"请使用其他专业编辑器打开此文件。",
                    )
                    if show_progress:
                        self._close_progress_window()

                self.root.after(0, show_error)
                return

            # 只打开一次文件，读取样本数据用于所有检测
            sample_data = None
            with open(file_path, "rb") as file:
                # 读取1KB样本数据用于二进制文件检测、编码检测和换行符检测
                sample_data = file.read(1024)

            # 首先检测是否为二进制文件
            if quick_edit_utils.is_binary_file(sample_data=sample_data):

                def show_binary_error():
                    messagebox.showinfo(
                        "无法打开",
                        f"文件 '{os.path.basename(file_path)}' 似乎是二进制文件，\n"
                        f"QuickEdit是文本编辑器，不支持打开二进制文件。",
                    )
                    if show_progress:
                        self._close_progress_window()

                self.root.after(0, show_binary_error)
                return

            # 使用同一样本数据检测编码和换行符类型
            encoding, line_ending = (
                quick_edit_utils.detect_file_encoding_and_line_ending(
                    sample_data=sample_data
                )
            )

            # 分块读取文件内容以避免内存问题
            content_chunks = []
            chunk_size = 8192  # 8KB chunks

            # 使用检测到的编码打开文件
            with codecs.open(
                file_path, "r", encoding=encoding, errors="replace"
            ) as file:
                while not self.file_read_cancelled:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    content_chunks.append(chunk)

            if self.file_read_cancelled:
                if show_progress:
                    self.root.after(0, self._close_progress_window)
                return

            content = "".join(content_chunks)

            # 在主线程中更新UI
            self.root.after(
                0, self._finish_open_file, file_path, content, encoding, line_ending
            )
        except Exception as e:
            self.root.after(0, self._handle_file_read_error, str(e))
        finally:
            # 确保即使发生异常也清理线程引用
            if hasattr(self, "file_read_thread"):
                self.file_read_thread = None

    def _finish_open_file(self, file_path, content, encoding, line_ending):
        """完成文件打开过程"""
        try:
            # 关闭进度窗口
            self._close_progress_window()

            if self.file_read_cancelled:
                return

            self.text_area.delete(1.0, tk.END)  # 清空文本

            # 分块插入内容以避免GUI冻结
            self._insert_content_in_chunks(content)

            # 更新总行数
            self.total_lines = content.count("\n") + 1  # 计算总行数
            self.encoding = encoding
            self.line_ending = line_ending  # 更新换行符类型
            self.current_file = file_path  # 更新当前文件路径
            # 根据只读模式状态设置窗口标题
            if self.readonly_mode:
                self.root.title(f"[只读模式] {os.path.basename(file_path)} - QuickEdit")
            else:
                self.root.title(f"{os.path.basename(file_path)} - QuickEdit")
            self.text_area.edit_modified(False)  # 重置修改标志

            # 检查是否存在备份文件
            self.check_backup_file()

            # 如果启用了备份功能且存在备份文件，删除它
            # 这是处理用户选择"否"选项时的情况
            if self.backup_enabled:
                backup_file = file_path + ".bak"
                if os.path.exists(backup_file):
                    try:
                        os.remove(backup_file)
                    except Exception as e:
                        print(f"删除备份文件失败: {e}")

            # 如果处于只读模式, 设置文本区域为只读
            if self.readonly_mode:
                self.text_area.config(state=tk.DISABLED)
            else:
                self.text_area.config(state=tk.NORMAL)

            # 更新状态栏
            self.update_statusbar()

            # 延迟应用语法高亮以减少卡顿
            self.root.after(100, self._delayed_apply_syntax_highlighting, file_path)

            # 设置文本框获取焦点
            self.text_area.focus_set()
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件: {str(e)}")

    def _delayed_apply_syntax_highlighting(self, file_path):
        """延迟应用语法高亮"""
        try:
            # 检查是否启用了语法高亮
            if self.syntax_highlighting_enabled:
                self.apply_syntax_highlighting()
            else:
                self.remove_syntax_highlighting()

        except Exception as e:
            # 忽略语法高亮错误, 不影响文件打开
            pass

    def _insert_content_in_chunks(self, content, chunk_size=50000, update_frequency=5):
        """优化的分块插入方法

        Args:
            content: 要插入的内容
            chunk_size: 每块的大小，默认50000字符
            update_frequency: GUI更新频率，每N次插入后更新一次GUI
        """
        # 对于小文件，直接插入
        if len(content) <= chunk_size:
            self.text_area.insert(1.0, content)
            self.root.update_idletasks()
            return

        # 对于大文件，采用优化的分块插入策略
        try:
            # 1. 使用更大的块大小以减少插入次数
            start = 0
            update_counter = 0

            while start < len(content):
                end = min(start + chunk_size, len(content))
                chunk = content[start:end]

                # 2. 使用END标记进行追加插入，比计算位置更快
                self.text_area.insert(tk.END, chunk)
                start = end

                # 3. 减少GUI更新频率，按设定频率更新GUI
                update_counter += 1
                if update_counter % update_frequency == 0:
                    self.root.update_idletasks()

        finally:
            # 5. 刷新GUI
            self.root.update_idletasks()

    def _handle_file_read_error(self, error_message):
        """处理文件读取错误"""
        self._close_progress_window()
        messagebox.showerror("错误", f"无法打开文件: {error_message}")

    def _save_content_to_file(self, file_path, content, update_current_file=False):
        """将内容保存到指定文件路径的辅助方法

        Args:
            file_path: 目标文件路径
            content: 要保存的内容
            update_current_file: 是否更新当前文件路径

        Returns:
            tuple: (保存是否成功, 错误信息)
        """
        try:
            # 确保编码有效，避免使用无法处理非ASCII字符的编码
            encoding_to_use = self.encoding

            # 使用codecs.open确保编码设置被正确应用
            # 转换换行符格式
            converted_content = quick_edit_utils.convert_line_endings(
                content, self.line_ending
            )

            # 使用codecs库打开文件，确保编码被正确应用
            with codecs.open(
                file_path, "w", encoding=encoding_to_use, errors="replace"
            ) as file:
                file.write(converted_content)

            # 如果需要，更新当前文件路径和窗口标题
            if update_current_file:
                self.current_file = file_path
                # 根据只读模式状态设置窗口标题
                if self.readonly_mode:
                    self.root.title(
                        f"[只读模式] {os.path.basename(file_path)} - QuickEdit"
                    )
                else:
                    self.root.title(f"{os.path.basename(file_path)} - QuickEdit")

            return True, None
        except Exception as e:
            return False, str(e)

    def _check_save_conditions(self, silent=False):
        """检查保存条件的辅助方法

        Args:
            silent: 静默模式标志

        Returns:
            tuple: (是否可以保存, 内容)
        """
        # 检查是否处于只读模式
        if self.readonly_mode:
            if not silent:
                messagebox.showinfo("提示", "当前处于只读模式, 无法保存文件。")
            return False, None

        # 检查文档是否被修改
        if not self.text_area.edit_modified():
            if not silent:
                messagebox.showinfo("提示", "文档没有被修改，无需保存。")
            return False, None

        # 检查文本框是否有内容
        content = self.text_area.get(1.0, tk.END).strip()
        if not content:
            if not silent:
                messagebox.showinfo("提示", "文本框中没有内容, 请先输入内容再保存。")
            return False, None

        return True, content

    def save_file(self, silent=False):
        """保存文件

        Args:
            silent: 静默模式标志，为True时不显示消息提示，只更新状态栏
        """
        # 调用辅助方法检查保存条件
        can_save, content = self._check_save_conditions(silent)
        if not can_save:
            return False

        # 如果当前文件路径为空, 则调用save_as_file()方法(另存为)
        if not self.current_file:
            return self.save_as_file()

        # 调用辅助方法保存文件
        success, error_msg = self._save_content_to_file(self.current_file, content)

        if success:
            # 立即调用_post_save_operations更新UI状态
            # 不再使用延迟调用，确保及时更新
            self._post_save_operations(self.current_file, silent)
            return True
        else:
            if not silent:
                messagebox.showerror("错误", f"保存文件时出错: {error_msg}")
            return False

    def _post_save_operations(self, file_path, silent=False):
        """保存文件后的操作

        Args:
            file_path: 保存的文件路径
            silent: 静默模式标志
        """
        try:
            # 更新修改状态
            self.text_area.edit_modified(False)

            # 确保窗口标题和状态栏都得到更新
            self.update_title_based_on_content()
            self.update_statusbar()

            # 显示保存成功消息
            if not silent:
                messagebox.showinfo(
                    "保存成功",
                    f"文件已成功保存！\n编码格式: {self.encoding.upper()}\n换行符格式: {self.line_ending}",
                )

            # 检查是否启用了语法高亮
            if self.syntax_highlighting_enabled:
                self.apply_syntax_highlighting()
            else:
                self.remove_syntax_highlighting()

            # 如果启用了备份功能，更新备份文件
            if self.backup_enabled and self.current_file:
                self.auto_save_to_backup()
                # 重置自动保存计时器，避免刚保存完又触发自动保存
                self.start_auto_save_timer()

        except Exception as e:
            messagebox.showerror("错误", f"保存后处理时出错: {str(e)}")

    def save_as_file(self):
        """另存为文件"""
        # 调用辅助方法检查保存条件
        can_save, content = self._check_save_conditions()
        if not can_save:
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("All Files", "*.*")],
        )

        if file_path:
            # 调用辅助方法保存文件，并更新当前文件路径
            success, error_msg = self._save_content_to_file(
                file_path, content, update_current_file=True
            )

            if success:
                # 在Tkinter事件循环中更新UI, 避免命令冲突
                self.root.after(10, self._post_save_operations, file_path)
            else:
                messagebox.showerror("错误", f"保存文件时出错: {error_msg}")

    def setup_auto_save(self):
        """设置自动保存相关配置"""
        # 确保auto_save_var和backup_enabled_var变量已存在且值正确
        if hasattr(self, "auto_save_var"):
            self.auto_save_var.set(self.auto_save_enabled)
        if hasattr(self, "backup_enabled_var"):
            self.backup_enabled_var.set(self.backup_enabled)

        # 监听窗口焦点变化，失去焦点时自动保存
        self.root.bind("<FocusOut>", self.on_focus_out)

        # 如果配置中启用了自动保存，则启动计时器
        if self.auto_save_enabled:
            self.start_auto_save_timer()

        # 更新状态栏显示
        self.show_default_auto_save_status()

    def start_auto_save_timer(self):
        """启动自动保存计时器"""
        if self.auto_save_timer:
            self.root.after_cancel(self.auto_save_timer)

        if self.auto_save_enabled:
            self.auto_save_timer = self.root.after(
                self.auto_save_interval * 1000, self.perform_auto_save
            )

    def stop_auto_save_timer(self):
        """停止自动保存计时器"""
        if self.auto_save_timer:
            self.root.after_cancel(self.auto_save_timer)
            self.auto_save_timer = None
        # 更新状态栏显示自动保存已禁用
        self.show_default_auto_save_status()

    def perform_auto_save(self):
        """执行自动保存操作"""
        if not self.auto_save_enabled or not self.current_file or self.readonly_mode:
            return

        # 检查文件是否有修改
        if self.text_area.edit_modified():
            # 创建异步线程执行保存
            save_thread = threading.Thread(target=self.async_auto_save)
            save_thread.daemon = True
            save_thread.start()

        # 继续下一次自动保存计时
        self.start_auto_save_timer()

    def async_auto_save(self):
        """异步执行自动保存操作"""
        # 使用锁确保同一时间只有一个保存操作
        with self.save_lock:
            if self.is_saving:
                return

            self.is_saving = True
            try:
                # 执行保存操作
                success = self.save_file(silent=True)

                # 只有在自动保存启用状态下才更新自动保存状态
                if success and self.auto_save_enabled:
                    self.root.after(
                        0, lambda: self.update_auto_save_status(True, "自动保存成功")
                    )
            except Exception as e:
                print(f"自动保存时出错: {str(e)}")
                # 在主线程中显示错误
                self.root.after(
                    0, lambda: self.left_status.config(text=f"自动保存失败: {str(e)}")
                )
            finally:
                self.is_saving = False

    def auto_save_to_backup(self):
        """保存到备份文件"""
        if not self.current_file or not self.backup_enabled:
            return

        try:
            # 确保current_file是有效的字符串且文件存在
            if (
                not isinstance(self.current_file, str)
                or not self.current_file
                or not os.path.exists(self.current_file)
            ):
                raise ValueError("无效的文件路径或文件不存在")

            # 构建备份文件路径
            backup_file = self.current_file + ".bak"

            # 确保备份文件所在目录存在
            backup_dir = os.path.dirname(backup_file)
            if backup_dir and not os.path.exists(backup_dir):
                os.makedirs(backup_dir, exist_ok=True)

            # 优化：直接复制已保存的文件到备份，避免重复读取和处理内容
            # 使用shutil.copy2保留文件元数据
            shutil.copy2(self.current_file, backup_file)

            # 更新最后自动保存时间
            self.last_auto_save_time = datetime.datetime.now()

            # 只有在自动保存启用状态下才更新自动保存状态
            if self.auto_save_enabled:
                self.root.after(0, self.update_auto_save_status, True, "自动保存完成")
        except Exception as e:
            print(f"备份失败: {e}")
            error_msg = f"备份失败: {str(e)}"
            self.root.after(
                0,
                self.update_auto_save_status,
                False,
                error_msg[:30] + "..." if len(error_msg) > 30 else error_msg,
            )

    def update_auto_save_status(self, success, message):
        """更新状态栏显示自动保存状态"""
        # 如果有临时消息（如保存完成或失败）
        if hasattr(self, "center_status"):
            # 获取当前主题的背景色，确保与状态栏保持一致
            theme = self.theme_manager.get_current_theme()
            bg_color = theme["statusbar_bg"]

            if message:
                # 根据消息类型使用不同的图标和颜色
                if success:
                    temp_icon = "✓"  # 成功标记
                    color = "green"  # 成功使用绿色
                else:
                    temp_icon = "!"  # 错误标记
                    color = "red"  # 错误使用红色

                # 构建临时消息文本
                temp_text = f"自动保存: {temp_icon} {message}"
                self.center_status.config(text=temp_text, fg=color, bg=bg_color)

                # 3秒后恢复正常的自动保存状态显示
                self.root.after(3000, self.reset_center_status)
            else:
                # 显示默认的自动保存状态
                self.show_default_auto_save_status()

        # 同时移除左侧状态栏中可能存在的自动保存信息（兼容旧版本）
        if hasattr(self, "left_status"):
            current_text = self.left_status.cget("text")
            # 移除左侧状态栏中的自动保存信息
            current_text = re.sub(r" \[自动保存:.*?\]", "", current_text)
            self.left_status.config(text=current_text)

    def show_default_auto_save_status(self):
        """显示默认的自动保存状态"""
        if hasattr(self, "center_status"):
            # 获取当前主题的前景色和背景色，确保与状态栏保持一致
            theme = self.theme_manager.get_current_theme()
            default_color = theme["statusbar_fg"]
            bg_color = theme["statusbar_bg"]

            # 为不同状态设置不同的样式和图标
            if self.auto_save_enabled:
                status_icon = "●"  # 实心圆点表示启用
                time_str = (
                    self.last_auto_save_time.strftime("%H:%M:%S")
                    if self.last_auto_save_time
                    else "从未"
                )

                # 使用辅助方法格式化显示
                display_interval = quick_edit_utils.format_auto_save_interval(
                    self.auto_save_interval
                )

                # 使用简洁的格式显示自动保存状态，包含间隔信息
                auto_save_info = (
                    f"自动保存: {status_icon} {time_str} (间隔{display_interval})"
                )
            else:
                status_icon = "○"  # 空心圆点表示禁用
                auto_save_info = f"自动保存: {status_icon} 已禁用"

            # 更新居中状态栏，同时设置前景色和背景色
            self.center_status.config(
                text=auto_save_info, fg=default_color, bg=bg_color
            )

    def reset_center_status(self):
        """重置居中状态栏到默认状态"""
        self.show_default_auto_save_status()

    def on_focus_out(self, event=None):
        """窗口失去焦点时触发自动保存"""
        if self.auto_save_enabled and self.current_file and not self.readonly_mode:
            self.perform_auto_save()

    def check_backup_file(self):
        """检查是否存在备份文件"""
        # 只有在启用了备份功能时才检查备份文件
        if not self.backup_enabled or not self.current_file:
            return False

        backup_file = self.current_file + ".bak"
        return os.path.exists(backup_file)

    def restore_from_backup(self):
        """从备份文件恢复"""
        # 只有在启用了备份功能时才尝试恢复备份文件
        if not self.backup_enabled or not self.current_file:
            return False

        backup_file = self.current_file + ".bak"
        if not os.path.exists(backup_file):
            messagebox.showinfo("恢复失败", "没有找到备份文件")
            return False

        try:
            # 检测备份文件的编码和换行符
            encoding, line_ending = (
                quick_edit_utils.detect_file_encoding_and_line_ending(backup_file)
            )

            # 读取备份文件内容
            with codecs.open(
                backup_file, "r", encoding=encoding, errors="replace"
            ) as f:
                content = f.read()

            # 使用现有的convert_line_endings方法处理换行符
            content = quick_edit_utils.convert_line_endings(content, self.line_ending)

            # 清空当前文本并插入备份内容
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", content)

            # 更新UI
            self.update_line_numbers()
            self.update_statusbar()

            messagebox.showinfo("恢复成功", "已从备份文件恢复内容")
            return True
        except Exception as e:
            messagebox.showerror("恢复失败", f"从备份文件恢复时出错: {e}")
            return False

    def cleanup_backup(self):
        """清理备份文件（正常退出时）"""
        # 只有在启用了备份功能时才清理备份文件
        if not self.backup_enabled or not self.current_file:
            return

        backup_file = self.current_file + ".bak"
        if os.path.exists(backup_file):
            try:
                os.remove(backup_file)
            except Exception as e:
                print(f"清理备份文件失败: {e}")

    def exit_app(self):
        """退出应用程序"""
        # 停止自动保存计时器
        self.stop_auto_save_timer()

        # 检查文本框是否有内容
        content = self.text_area.get(1.0, tk.END).strip()

        # 情况1: 如果有打开的文件
        if self.current_file:
            # 情况1a: 打开文件且已被修改, 询问用户是否保存
            if content and self.text_area.edit_modified():
                result = messagebox.askyesnocancel(
                    "退出确认", "文档已被修改, 是否保存后再退出？"
                )
                if result is True:  # 是, 保存并退出
                    self.save_file()
                    # 保存后检查窗口是否仍然存在再决定是否销毁
                    if self.root.winfo_exists():
                        # 如果保存成功，清理备份文件
                        self.cleanup_backup()
                        self.root.destroy()
                elif result is False:  # 否, 直接退出
                    # 不保存直接退出时，保留备份文件（如果有）
                    self.root.destroy()
                # 如果点击取消, 则不执行任何操作, 继续留在编辑器中
            else:
                # 情况1b: 打开文件但未被修改, 直接退出
                # 未修改时清理备份文件
                self.cleanup_backup()
                self.root.destroy()
        else:
            # 情况2: 没有打开文件 (新建文件或直接输入内容)
            if content:
                # 情况2a: 有内容, 询问用户是否保存
                result = messagebox.askyesnocancel(
                    "退出确认", "文档有内容, 是否保存后再退出？"
                )
                if result is True:  # 是, 保存并退出
                    self.save_file()
                    # 保存后检查窗口是否仍然存在再决定是否销毁
                    if self.root.winfo_exists():
                        self.root.destroy()
                elif result is False:  # 否, 直接退出
                    self.root.destroy()
                # 如果点击取消, 则不执行任何操作, 继续留在编辑器中
            else:
                # 情况2b: 没有内容, 直接退出
                self.root.destroy()

    # 编辑操作方法
    def copy_text(self):
        """复制文本

        当没有选中内容时，捕获异常并静默处理，避免程序崩溃
        """
        try:
            # 检查是否有选中的文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                self.text_area.clipboard_clear()
                self.text_area.clipboard_append(selected_text)
        except tk.TclError:
            # 没有选中内容或选择无效时，静默处理
            pass

    def cut_text(self):
        """剪切文本

        当没有选中内容时，捕获异常并静默处理，避免程序崩溃
        """
        try:
            # 检查是否有选中的文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                self.copy_text()
                self.text_area.delete("sel.first", "sel.last")
        except tk.TclError:
            # 没有选中内容或选择无效时，静默处理
            pass

    def paste_text(self):
        """粘贴文本

        当剪贴板为空时，捕获异常并静默处理，避免程序崩溃
        """
        try:
            clipboard_text = self.text_area.clipboard_get()
            if clipboard_text:
                self.text_area.insert(tk.INSERT, clipboard_text)
        except tk.TclError:
            # 剪贴板为空或无法获取内容时，静默处理
            pass

    def undo_text(self):
        """撤销操作

        当没有可撤销的操作时，显示提示框而不是静默处理，提供更好的用户体验
        """
        try:
            self.text_area.edit_undo()

            # 检查撤销后是否为空文件且是新建文件
            if not self.current_file and self.text_area.compare("end-1c", "==", "1.0"):
                # 当内容为空时，重置修改状态为未修改
                self.text_area.edit_modified(False)
                # 确保状态更新
                self.update_statusbar()

        except tk.TclError:
            # 没有可撤销的操作时，显示提示框
            messagebox.showinfo("提示", "没有可撤销的操作")

    def redo_text(self):
        """重做操作

        当没有可重做的操作时，显示提示框而不是静默处理，提供更好的用户体验
        """
        try:
            self.text_area.edit_redo()

            # 检查重做后是否为空文件且是新建文件
            if not self.current_file and self.text_area.compare("end-1c", "==", "1.0"):
                # 当内容为空时，重置修改状态为未修改
                self.text_area.edit_modified(False)
                # 确保状态更新
                self.update_statusbar()

        except tk.TclError:
            # 没有可重做的操作时，显示提示框
            messagebox.showinfo("提示", "没有可重做的操作")

    def select_all(self):
        """全选文本"""
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, "1.0")
        self.text_area.see(tk.INSERT)

    def find_text(self):
        """查找文本"""
        find_str = simpledialog.askstring("查找", "请输入要查找的文本:")
        if find_str:
            self.text_area.tag_remove("found", "1.0", tk.END)
            start_pos = "1.0"

            while True:
                start_pos = self.text_area.search(find_str, start_pos, stopindex=tk.END)
                if not start_pos:
                    break
                end_pos = f"{start_pos}+{len(find_str)}c"
                self.text_area.tag_add("found", start_pos, end_pos)
                start_pos = end_pos

            # 使用主题管理器的颜色配置
            theme = self.theme_manager.get_current_theme()
            self.text_area.tag_configure(
                "found", background=theme["found_bg"], foreground=theme["found_fg"]
            )

            if not self.text_area.tag_ranges("found"):
                messagebox.showinfo("查找结果", "未找到指定文本")

    def go_to_end(self):
        """转到文件底部"""
        self.text_area.see(tk.END)
        self.text_area.mark_set(tk.INSERT, tk.END)
        self.text_area.focus_set()
        self.update_statusbar()

    def go_to_home(self):
        """转到文件顶部"""
        self.text_area.see("1.0")
        self.text_area.mark_set(tk.INSERT, "1.0")
        self.text_area.focus_set()
        self.update_statusbar()

    def page_up(self):
        """向上翻页"""
        self.text_area.yview_scroll(-1, "pages")
        self.text_area.focus_set()
        self.update_statusbar()

    def page_down(self):
        """向下翻页"""
        self.text_area.yview_scroll(1, "pages")
        self.text_area.focus_set()
        self.update_statusbar()

    # 格式设置方法
    def choose_font(self):
        """设置字体"""
        # 获取系统可用字体列表
        available_fonts = list(font.families())
        available_fonts.sort()  # 排序字体列表

        # 创建字体选择对话框
        font_dialog = tk.Toplevel(self.root)
        font_dialog.title("设置字体")
        font_dialog.resizable(True, True)
        font_dialog.transient(self.root)
        font_dialog.grab_set()  # 模态对话框

        # 设置窗口图标
        quick_edit_utils.set_window_icon(font_dialog)

        # 居中显示对话框
        quick_edit_utils.center_window(font_dialog, 500, 600)

        # 当前字体标签
        current_label = tk.Label(
            font_dialog,
            text=f"当前字体: {self.font_family}",
            font=("Microsoft YaHei UI", 13),
        )
        current_label.pack(pady=5)

        # 创建滚动条和列表框
        frame = tk.Frame(font_dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 字体列表框
        font_listbox = tk.Listbox(
            frame, yscrollcommand=scrollbar.set, font=("Microsoft YaHei UI", 12)
        )
        font_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=font_listbox.yview)

        # 添加字体到列表框
        for font_name in available_fonts:
            font_listbox.insert(tk.END, font_name)

        # 选中当前字体
        try:
            current_index = available_fonts.index(self.font_family)
            font_listbox.selection_set(current_index)
            font_listbox.see(current_index)
        except ValueError:
            # 如果当前字体不在列表中, 默认选中第一个
            if available_fonts:
                font_listbox.selection_set(0)
                font_listbox.see(0)

        # 实时预览字体函数
        def preview_font(event=None):
            selection = font_listbox.curselection()
            if selection:
                selected_font = font_listbox.get(selection[0])
                # 更新示例文字的字体
                sample_text.config(font=(selected_font, self.font_size))
                current_label.config(text=f"当前字体: {selected_font}")

        # 双击选择字体
        def on_font_select(event=None):
            selection = font_listbox.curselection()
            if selection:
                selected_font = font_listbox.get(selection[0])
                self.font_family = selected_font
                self.update_font()
                self.save_config()
                font_dialog.destroy()

        # 绑定双击事件
        font_listbox.bind("<Double-Button-1>", on_font_select)

        # 绑定选择变化事件，实现实时预览
        font_listbox.bind("<<ListboxSelect>>", preview_font)

        # 示例文字框架
        sample_frame = tk.LabelFrame(font_dialog, text="字体预览", padx=10, pady=10)
        sample_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=5)

        # 示例文字
        sample_text = tk.Text(sample_frame, wrap=tk.WORD, height=5)
        sample_text.pack(fill=tk.BOTH, expand=True)

        # 插入示例文字内容
        sample_content = """这是字体预览示例文字。
The quick brown fox jumps over the lazy dog.
0123456789
"""
        sample_text.insert(tk.END, sample_content)
        sample_text.config(state=tk.DISABLED)  # 设为只读

        # 应用当前字体到示例文字
        sample_text.config(font=(self.font_family, self.font_size))

        # 按钮框架
        button_frame = tk.Frame(font_dialog)
        button_frame.pack(pady=10)

        # 确定按钮
        ok_button = tk.Button(
            button_frame, text="确定", command=on_font_select, width=10
        )
        ok_button.pack(side=tk.LEFT, padx=5)

        # 取消按钮
        cancel_button = tk.Button(
            button_frame, text="取消", command=font_dialog.destroy, width=10
        )
        cancel_button.pack(side=tk.LEFT, padx=5)

        # 显示对话框
        font_dialog.update_idletasks()

    def choose_font_size(self):
        """设置字体大小"""
        # 创建字体大小设置对话框
        size_dialog = tk.Toplevel(self.root)
        size_dialog.title("设置字体大小")
        size_dialog.resizable(True, True)  # 允许调整大小
        size_dialog.transient(self.root)
        size_dialog.grab_set()  # 模态对话框

        # 居中显示对话框
        quick_edit_utils.center_window(size_dialog, 500, 300)  # 减小默认窗口高度

        # 设置窗口图标
        quick_edit_utils.set_window_icon(size_dialog)

        # 创建顶部控制区域框架
        control_frame = tk.Frame(size_dialog)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        # 当前字体大小标签
        current_label = tk.Label(
            control_frame,
            text=f"当前字体大小: {self.font_size}",
            font=("Microsoft YaHei UI", 12),
        )
        current_label.pack(side=tk.TOP, pady=5)

        # 字体大小变量
        size_var = tk.StringVar(value=str(self.font_size))

        # 输入控制框架
        input_frame = tk.Frame(control_frame)
        input_frame.pack(side=tk.TOP, pady=5)

        # 减少按钮
        def decrease_size():
            try:
                current_size = int(size_var.get())
                if current_size > 1:  # 最小字体大小为1
                    new_size = current_size - 1
                    size_var.set(str(new_size))
                    self.font_size = new_size
                    self.update_font()
                    current_label.config(text=f"当前字体大小: {self.font_size}")
                    # 更新示例文字的字体大小
                    sample_text.config(font=(self.font_family, new_size))
            except ValueError:
                pass

        decrease_btn = tk.Button(input_frame, text="-", command=decrease_size, width=3)
        decrease_btn.pack(side=tk.LEFT, padx=5)

        # 输入框
        size_entry = tk.Entry(
            input_frame,
            textvariable=size_var,
            width=10,
            justify="center",
            font=("Microsoft YaHei UI", 12),
        )
        size_entry.pack(side=tk.LEFT, padx=5)

        # 增加按钮
        def increase_size():
            try:
                current_size = int(size_var.get())
                if current_size < 100:  # 最大字体大小为100
                    new_size = current_size + 1
                    size_var.set(str(new_size))
                    self.font_size = new_size
                    self.update_font()
                    current_label.config(text=f"当前字体大小: {self.font_size}")
                    # 更新示例文字的字体大小
                    sample_text.config(font=(self.font_family, new_size))
            except ValueError:
                pass

        increase_btn = tk.Button(input_frame, text="+", command=increase_size, width=3)
        increase_btn.pack(side=tk.LEFT, padx=5)

        # 确定和取消按钮放在输入框旁边
        ok_button = tk.Button(
            input_frame, text="确定", command=lambda: apply_size(), width=8
        )
        ok_button.pack(side=tk.LEFT, padx=10)

        cancel_button = tk.Button(
            input_frame, text="取消", command=size_dialog.destroy, width=8
        )
        cancel_button.pack(side=tk.LEFT, padx=5)

        # 示例文字框架
        sample_frame = tk.LabelFrame(size_dialog, text="字体预览", padx=10, pady=5)
        sample_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 示例文字 - 降低高度
        sample_text = tk.Text(sample_frame, wrap=tk.WORD, height=4)  # 降低高度为4
        sample_text.pack(fill=tk.BOTH, expand=True)

        # 插入示例文字内容
        sample_content = """这是字体预览示例文字。
The quick brown fox jumps over the lazy dog.
0123456789
"""
        sample_text.insert(tk.END, sample_content)
        sample_text.config(state=tk.DISABLED)  # 设为只读

        # 应用当前字体大小到示例文字
        sample_text.config(font=(self.font_family, self.font_size))

        # 确定按钮功能
        def apply_size():
            try:
                new_size = int(size_var.get())
                if 1 <= new_size <= 100:  # 限制字体大小范围
                    self.font_size = new_size
                    self.update_font()
                    self.save_config()
                    size_dialog.destroy()
                else:
                    messagebox.showerror("错误", "字体大小必须在1-100之间")
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字")

        # 绑定回车键确认
        size_entry.bind("<Return>", lambda event: apply_size())
        size_entry.focus_set()

    def toggle_bold(self):
        """切换粗体 - 如果有选中文本则只应用到选中部分，否则更新全局设置"""
        # 检查是否有选中文本
        try:
            selected_text = self.text_area.tag_ranges(tk.SEL)
            if selected_text:  # 如果有选中文本
                # 获取选中文本的开始和结束位置
                start, end = selected_text

                # 获取当前选中区域的字体配置
                current_tags = self.text_area.tag_names(start)

                # 判断是否已经是粗体
                is_bold = any(tag.startswith("bold_") for tag in current_tags)

                if is_bold:  # 如果已经是粗体，则移除粗体效果
                    for tag in current_tags:
                        if tag.startswith("bold_"):
                            self.text_area.tag_remove(tag, start, end)
                else:  # 否则添加粗体效果
                    # 创建或获取粗体标签
                    bold_tag = "bold_tag"
                    if bold_tag not in self.text_area.tag_names():
                        # 配置粗体标签的字体样式
                        bold_font = font.Font(
                            self.text_area, self.text_area.cget("font")
                        )
                        bold_font.configure(weight="bold")
                        self.text_area.tag_configure(bold_tag, font=bold_font)

                    # 应用粗体标签到选中文本
                    self.text_area.tag_add(bold_tag, start, end)
            else:  # 如果没有选中文本，更新全局设置
                self.font_bold = not self.font_bold
                self.bold_var.set(self.font_bold)  # 同步更新菜单项状态
                self.update_font()
                self.save_config()
        except Exception as e:
            print(f"应用粗体效果时出错: {e}")
            # 如果出错，回退到全局设置更新
            self.font_bold = not self.font_bold
            self.bold_var.set(self.font_bold)
            self.update_font()
            self.save_config()

    def toggle_italic(self):
        """切换斜体 - 如果有选中文本则只应用到选中部分，否则更新全局设置"""
        # 检查是否有选中文本
        try:
            selected_text = self.text_area.tag_ranges(tk.SEL)
            if selected_text:  # 如果有选中文本
                # 获取选中文本的开始和结束位置
                start, end = selected_text

                # 获取当前选中区域的字体配置
                current_tags = self.text_area.tag_names(start)

                # 判断是否已经是斜体
                is_italic = any(tag.startswith("italic_") for tag in current_tags)

                if is_italic:  # 如果已经是斜体，则移除斜体效果
                    for tag in current_tags:
                        if tag.startswith("italic_"):
                            self.text_area.tag_remove(tag, start, end)
                else:  # 否则添加斜体效果
                    # 创建或获取斜体标签
                    italic_tag = "italic_tag"
                    if italic_tag not in self.text_area.tag_names():
                        # 配置斜体标签的字体样式
                        italic_font = font.Font(
                            self.text_area, self.text_area.cget("font")
                        )
                        italic_font.configure(slant="italic")
                        self.text_area.tag_configure(italic_tag, font=italic_font)

                    # 应用斜体标签到选中文本
                    self.text_area.tag_add(italic_tag, start, end)
            else:  # 如果没有选中文本，更新全局设置
                self.font_italic = not self.font_italic
                self.italic_var.set(self.font_italic)  # 同步更新菜单项状态
                self.update_font()
                self.save_config()
        except Exception as e:
            print(f"应用斜体效果时出错: {e}")
            # 如果出错，回退到全局设置更新
            self.font_italic = not self.font_italic
            self.italic_var.set(self.font_italic)
            self.update_font()
            self.save_config()

    def toggle_underline(self):
        """切换下划线 - 如果有选中文本则只应用到选中部分，否则更新全局设置"""
        # 检查是否有选中文本
        try:
            selected_text = self.text_area.tag_ranges(tk.SEL)
            if selected_text:  # 如果有选中文本
                # 获取选中文本的开始和结束位置
                start, end = selected_text

                # 获取当前选中区域的字体配置
                current_tags = self.text_area.tag_names(start)

                # 判断是否已经有下划线
                is_underlined = any(
                    tag.startswith("underline_") for tag in current_tags
                )

                if is_underlined:  # 如果已经有下划线，则移除下划线效果
                    for tag in current_tags:
                        if tag.startswith("underline_"):
                            self.text_area.tag_remove(tag, start, end)
                else:  # 否则添加下划线效果
                    # 创建或获取下划线标签
                    underline_tag = "underline_tag"
                    if underline_tag not in self.text_area.tag_names():
                        # 配置下划线标签的字体样式
                        underline_font = font.Font(
                            self.text_area, self.text_area.cget("font")
                        )
                        underline_font.configure(underline=1)
                        self.text_area.tag_configure(underline_tag, font=underline_font)

                    # 应用下划线标签到选中文本
                    self.text_area.tag_add(underline_tag, start, end)
            else:  # 如果没有选中文本，更新全局设置
                self.font_underline = not self.font_underline
                self.underline_var.set(self.font_underline)  # 同步更新菜单项状态
                self.update_font()
                self.save_config()
        except Exception as e:
            print(f"应用下划线效果时出错: {e}")
            # 如果出错，回退到全局设置更新
            self.font_underline = not self.font_underline
            self.underline_var.set(self.font_underline)
            self.update_font()
            self.save_config()

    def toggle_overstrike(self):
        """切换删除线 - 如果有选中文本则只应用到选中部分，否则更新全局设置"""
        # 检查是否有选中文本
        try:
            selected_text = self.text_area.tag_ranges(tk.SEL)
            if selected_text:  # 如果有选中文本
                # 获取选中文本的开始和结束位置
                start, end = selected_text

                # 获取当前选中区域的字体配置
                current_tags = self.text_area.tag_names(start)

                # 判断是否已经有删除线
                is_overstruck = any(
                    tag.startswith("overstrike_") for tag in current_tags
                )

                if is_overstruck:  # 如果已经有删除线，则删除删除线效果
                    for tag in current_tags:
                        if tag.startswith("overstrike_"):
                            self.text_area.tag_remove(tag, start, end)
                else:  # 否则添加删除线效果
                    # 创建或获取删除线标签
                    overstrike_tag = "overstrike_tag"
                    if overstrike_tag not in self.text_area.tag_names():
                        # 配置删除线标签的字体样式
                        overstrike_font = font.Font(
                            self.text_area, self.text_area.cget("font")
                        )
                        overstrike_font.configure(overstrike=1)
                        self.text_area.tag_configure(
                            overstrike_tag, font=overstrike_font
                        )

                    # 应用删除线标签到选中文本
                    self.text_area.tag_add(overstrike_tag, start, end)
            else:  # 如果没有选中文本，更新全局设置
                self.font_overstrike = not self.font_overstrike
                self.overstrike_var.set(self.font_overstrike)  # 同步更新菜单项状态
                self.update_font()
                self.save_config()
        except Exception as e:
            print(f"应用删除线效果时出错: {e}")
            # 如果出错，回退到全局设置更新
            self.font_overstrike = not self.font_overstrike
            self.overstrike_var.set(self.font_overstrike)
            self.update_font()
            self.save_config()

    # 帮助方法
    def toggle_toolbar(self):
        """切换工具栏显示/隐藏"""
        self.toolbar_visible = not self.toolbar_visible
        self.toolbar_var.set(self.toolbar_visible)
        if self.toolbar_visible:
            self.create_toolbar()
        else:
            # 隐藏工具栏
            if hasattr(self, "toolbar"):
                self.toolbar.pack_forget()
        self.save_config()

    def enable_drag_and_drop(self):
        """启用拖拽支持"""
        # 注册拖拽事件
        self.root.drop_target_register(tkinterdnd2.DND_FILES)
        self.root.dnd_bind("<<Drop>>", self.on_drop)

    def on_drop(self, event):
        """处理文件拖拽释放事件"""
        # 获取拖拽的文件路径
        if event.data:
            # 处理拖拽的数据
            files = self.root.tk.splitlist(event.data)
            if files:
                # 检查是否有未保存的更改
                continue_operation, _ = self.check_and_handle_unsaved_changes("打开")
                if not continue_operation:
                    return  # 用户取消操作

                # 只处理第一个文件
                file_path = files[0]
                # 检查是否为文件
                if os.path.isfile(file_path):
                    self.open_file(file_path)
                elif os.path.isdir(file_path):
                    # 如果是目录, 显示提示
                    messagebox.showinfo("提示", "拖拽的是目录, 请拖拽文件以打开")
                else:
                    messagebox.showwarning("警告", "无法识别拖拽的项目")

    def toggle_readonly_mode(self):
        """切换只读模式"""
        self.readonly_mode = not self.readonly_mode
        self.readonly_var.set(self.readonly_mode)

        # 根据只读模式状态启用或禁用文本区域
        if self.readonly_mode:
            self.text_area.config(state=tk.DISABLED)
        else:
            self.text_area.config(state=tk.NORMAL)

        # 更新窗口标题以显示只读模式状态
        if self.current_file:
            file_name = os.path.basename(self.current_file)
            if self.readonly_mode:
                self.root.title(f"[只读模式] {file_name} - QuickEdit")
            else:
                self.root.title(f"{file_name} - QuickEdit")
        else:
            if self.readonly_mode:
                self.root.title("[只读模式] QuickEdit")
            else:
                self.root.title("QuickEdit")

        # 更新状态栏提示
        self.update_statusbar()

    def show_find_dialog(self):
        """显示查找对话框"""
        # 获取文本区域中选中的文本，保持原始内容不变
        selected_text = (
            self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            if self.text_area.tag_ranges(tk.SEL)
            else ""
        )
        # 传递update_statusbar方法作为回调函数，确保替换操作后能立即更新窗口状态
        FindDialog(
            self.root,
            self.text_area,
            self.current_file,
            selected_text,
            read_only=self.readonly_mode,
            update_callback=self.update_statusbar,
        )

    def advanced_find_text(
        self, search_term, search_type="normal", match_case=True, whole_word=False
    ):
        """查找文本功能"""
        # 清除之前的高亮
        self.text_area.tag_remove("found", "1.0", tk.END)

        if not search_term:
            return []

        matches = []
        start_pos = "1.0"

        try:
            # 根据查找类型选择不同的查找方式
            if search_type == "regex":
                # 正则表达式查找
                flags = 0 if match_case else re.IGNORECASE
                pattern = search_term
                if whole_word:
                    pattern = r"\b" + re.escape(search_term) + r"\b"

                content = self.text_area.get("1.0", tk.END + "-1c")
                for match in re.finditer(pattern, content, flags):
                    start_idx = self.text_area.index(f"1.0+{match.start()}c")
                    end_idx = self.text_area.index(f"1.0+{match.end()}c")
                    matches.append((start_idx, end_idx))
            else:
                # 普通查找或完整匹配查找
                search_flags = 0
                if not match_case:
                    search_flags = tk.IGNORECASE

                while True:
                    if whole_word and search_type == "whole":
                        # 完整单词匹配
                        pattern = r"\b" + re.escape(search_term) + r"\b"
                        content = self.text_area.get(start_pos, tk.END)
                        match = re.search(
                            pattern, content, re.IGNORECASE if not match_case else 0
                        )
                        if not match:
                            break
                        # 计算实际位置
                        line_offset = content[: match.start()].count("\n")
                        char_offset = (
                            len(content[: match.start()].split("\n")[-1])
                            if "\n" in content[: match.start()]
                            else match.start()
                        )

                        current_line = int(start_pos.split(".")[0]) + line_offset
                        if line_offset == 0:
                            current_col = int(start_pos.split(".")[1]) + char_offset
                        else:
                            current_col = char_offset

                        start_idx = f"{current_line}.{current_col}"
                        end_idx = f"{current_line}.{current_col + len(search_term)}"
                    else:
                        # 普通查找
                        start_idx = self.text_area.search(
                            search_term, start_pos, tk.END, nocase=not match_case
                        )
                        if not start_idx:
                            break
                        end_idx = f"{start_idx}+{len(search_term)}c"

                    matches.append((start_idx, end_idx))
                    start_pos = f"{end_idx}+1c"
        except Exception as e:
            messagebox.showerror("查找错误", f"查找过程中发生错误: {str(e)}")
            return []

        # 高亮所有匹配项
        for start_idx, end_idx in matches:
            self.text_area.tag_add("found", start_idx, end_idx)

        self.text_area.tag_configure("found", background="yellow", foreground="black")

        return matches

    def create_undo_menu_item(self, parent_menu):
        """创建撤销菜单项"""
        parent_menu.add_command(
            label="撤销", command=self.undo_text, accelerator="Ctrl+Z"
        )

    def create_redo_menu_item(self, parent_menu):
        """创建重做菜单项"""
        parent_menu.add_command(
            label="重做", command=self.redo_text, accelerator="Ctrl+Y"
        )

    def create_cut_menu_item(self, parent_menu):
        """创建剪切菜单项"""
        parent_menu.add_command(
            label="剪切", command=self.cut_text, accelerator="Ctrl+X"
        )

    def create_copy_menu_item(self, parent_menu):
        """创建复制菜单项"""
        parent_menu.add_command(
            label="复制", command=self.copy_text, accelerator="Ctrl+C"
        )

    def create_paste_menu_item(self, parent_menu):
        """创建粘贴菜单项"""
        parent_menu.add_command(
            label="粘贴", command=self.paste_text, accelerator="Ctrl+V"
        )

    def create_select_all_menu_item(self, parent_menu):
        """创建全选菜单项"""
        parent_menu.add_command(
            label="全选", command=self.select_all, accelerator="Ctrl+A"
        )

    def create_find_menu_item(self, parent_menu):
        """创建查找替换菜单项"""
        parent_menu.add_command(
            label="查找替换", command=self.show_find_dialog, accelerator="Ctrl+F"
        )

    def create_bold_menu_item(self, parent_menu):
        """创建粗体菜单项"""
        parent_menu.add_checkbutton(
            label="粗体", command=self.toggle_bold, variable=self.bold_var
        )

    def create_italic_menu_item(self, parent_menu):
        """创建斜体菜单项"""
        parent_menu.add_checkbutton(
            label="斜体", command=self.toggle_italic, variable=self.italic_var
        )

    def create_underline_menu_item(self, parent_menu):
        """创建下划线菜单项"""
        parent_menu.add_checkbutton(
            label="下划线", command=self.toggle_underline, variable=self.underline_var
        )

    def create_overstrike_menu_item(self, parent_menu):
        """创建删除线菜单项"""
        parent_menu.add_checkbutton(
            label="删除线", command=self.toggle_overstrike, variable=self.overstrike_var
        )

    def create_copy_to_clipboard_menu(self, parent_menu):
        """创建复制到剪贴板子菜单"""
        copy_to_clipboard_menu = tk.Menu(parent_menu, tearoff=0, font=("微软雅黑", 9))
        copy_to_clipboard_menu.add_command(
            label="文件名", command=self.copy_filename_to_clipboard
        )
        copy_to_clipboard_menu.add_command(
            label="完整文件路径", command=self.copy_filepath_to_clipboard
        )
        copy_to_clipboard_menu.add_command(
            label="目录", command=self.copy_directory_to_clipboard
        )
        return copy_to_clipboard_menu

    def create_insert_menu(self, parent_menu):
        """创建插入子菜单（使用插入助手）"""
        return self.insert_helper.create_insert_menu(parent_menu)

    def create_selected_text_menu(self, parent_menu):
        """创建选中文本操作子菜单

        Args:
            parent_menu: 父菜单对象

        Returns:
            tk.Menu: 选中文本操作子菜单
        """
        # 调用text_processing_helper中的方法创建选中文本操作菜单
        # 菜单结构已优化，相关功能已组织到子菜单中
        return self.text_processing_helper.create_selected_text_menu(parent_menu)

    def show_context_menu(self, event):
        """显示上下文菜单（鼠标右键菜单）"""
        # 创建上下文菜单
        context_menu = tk.Menu(self.root, tearoff=0)

        # 添加撤销和重做选项
        self.create_undo_menu_item(context_menu)
        self.create_redo_menu_item(context_menu)
        context_menu.add_separator()

        # 添加剪切、复制、粘贴和全选选项
        self.create_cut_menu_item(context_menu)
        self.create_copy_menu_item(context_menu)
        self.create_paste_menu_item(context_menu)
        context_menu.add_separator()

        self.create_select_all_menu_item(context_menu)
        context_menu.add_separator()

        # 添加查找和替换选项
        self.create_find_menu_item(context_menu)
        context_menu.add_separator()

        # 添加字体效果选项
        self.create_bold_menu_item(context_menu)
        self.create_italic_menu_item(context_menu)
        self.create_underline_menu_item(context_menu)
        self.create_overstrike_menu_item(context_menu)
        context_menu.add_separator()

        # 添加清空剪贴板选项
        context_menu.add_command(label="清空剪贴板", command=self.clear_clipboard)

        # 添加复制到剪贴板子菜单
        copy_to_clipboard_menu = self.create_copy_to_clipboard_menu(context_menu)
        context_menu.add_cascade(label="复制到剪贴板", menu=copy_to_clipboard_menu)

        # 添加选中文本操作子菜单
        selected_text_menu = self.create_selected_text_menu(context_menu)
        context_menu.add_cascade(label="选中文本操作", menu=selected_text_menu)

        # 添加插入子菜单
        insert_menu = self.create_insert_menu(context_menu)
        context_menu.add_cascade(label="插入", menu=insert_menu)

        # 在鼠标位置显示菜单
        context_menu.post(event.x_root, event.y_root)

    def show_about(self):
        """显示关于信息"""
        messagebox.showinfo(
            "关于QuickEdit",
            "QuickEdit 是一个轻量级的文本编辑器，支持多种文件操作和编辑功能。\n\n"
            "项目地址:  " + PROJECT_URL + "\n"
            "版本号:  " + VERSION + "\n",
        )

    def clear_clipboard(self):
        """清空剪贴板"""
        try:
            self.text_area.clipboard_clear()
        except Exception as e:
            messagebox.showerror("错误", f"清空剪贴板时出错: {str(e)}")

    def copy_filename_to_clipboard(self):
        """复制文件名到剪贴板"""
        if self.current_file:
            try:
                filename = os.path.basename(self.current_file)
                self.text_area.clipboard_clear()
                self.text_area.clipboard_append(filename)
            except Exception as e:
                messagebox.showerror("错误", f"复制文件名时出错: {str(e)}")
        else:
            messagebox.showinfo("提示", "当前没有打开的文件")

    def copy_filepath_to_clipboard(self):
        """复制完整文件路径到剪贴板"""
        if self.current_file:
            try:
                self.text_area.clipboard_clear()
                self.text_area.clipboard_append(self.current_file)
            except Exception as e:
                messagebox.showerror("错误", f"复制文件路径时出错: {str(e)}")
        else:
            messagebox.showinfo("提示", "当前没有打开的文件")

    def open_containing_folder(self):
        """打开当前文件所在的文件夹"""
        if self.current_file:
            try:
                # 获取文件所在的目录
                directory = os.path.dirname(self.current_file)
                if os.path.exists(directory):
                    # 在Windows上使用explorer命令打开文件夹
                    os.startfile(directory)
                else:
                    messagebox.showerror("错误", "文件所在目录不存在")
            except Exception as e:
                messagebox.showerror("错误", f"无法打开文件所在文件夹: {str(e)}")
        else:
            messagebox.showinfo("提示", "当前没有打开的文件")

    def copy_directory_to_clipboard(self):
        """复制目录到剪贴板"""
        if self.current_file:
            try:
                directory = os.path.dirname(self.current_file)
                self.text_area.clipboard_clear()
                self.text_area.clipboard_append(directory)
            except Exception as e:
                messagebox.showerror("错误", f"复制目录时出错: {str(e)}")
        else:
            messagebox.showinfo("提示", "当前没有打开的文件")
