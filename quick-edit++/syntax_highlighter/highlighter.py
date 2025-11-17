#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
语法高亮主控制器模块

提供语法高亮的核心功能，包括与Text组件的交互和高亮逻辑
"""

import re
import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional, Any
from pathlib import Path
import os

# 导入配置管理器
from config.config_manager import config_manager

# 导入语言处理器
from .handlers import LanguageHandler
from .handlers.python_handler import PythonHandler
from .handlers.json_handler import JSONHandler
from .handlers.ini_toml_handler import IniTomlHandler
from .handlers.yaml_handler import YAMLHandler
from .handlers.bash_handler import BashHandler
from .handlers.bat_handler import BatHandler
from .handlers.powershell_handler import PowerShellHandler
from .handlers.sql_handler import SQLHandler
from .handlers.html_handler import HTMLHandler
from .handlers.xml_handler import XMLHandler
from .handlers.css_handler import CSSHandler
from .handlers.javascript_handler import JavaScriptHandler
from .handlers.typescript_handler import TypeScriptHandler
from .handlers.go_handler import GoHandler
from .handlers.markdown_handler import MarkdownHandler
from .handlers.dockerfile_handler import DockerfileHandler
from .handlers.makefile_handler import MakefileHandler
from .handlers.env_handler import EnvHandler
from .handlers.gitignore_handler import GitIgnoreHandler
from .handlers.log_handler import LogHandler
from .handlers.lua_handler import LuaHandler
from .handlers.java_handler import JavaHandler
from .handlers.rust_handler import RustHandler
from .handlers.php_handler import PHPHandler
from .handlers.cpp_handler import CppHandler
from .handlers.csv_handler import CSVHandler
from .handlers.vim_handler import VimHandler
from .handlers.auto_handler import AutoHandler


class SyntaxHighlighter:
    """
    语法高亮主控制器

    负责管理语言处理器，控制高亮过程，并提供与Text组件的接口
    """

    def __init__(self, app):
        """
        初始化语法高亮器

        Args:
            text_widget: tkinter Text组件实例
        """
        # 从配置管理器获取配置
        syntax_config = config_manager.get_component_config("syntax_highlighter")

        # 设置初始化参数
        self.app = app
        self.text_widget = app.text_area
        self.render_visible_only = syntax_config.get("render_visible_only", False)
        self.highlight_enabled = syntax_config.get("enabled", True)
        self.max_lines_per_highlight = syntax_config.get(
            "max_lines_per_highlight", 1000
        )

        # 内部状态
        self.language_handlers = {}  # 存储不同语言的处理器
        self.current_language = None  # 当前使用的语言
        self.current_file_extension = None  # 当前文件扩展名
        self._highlight_tags = set()  # 存储已创建的高亮标签

        # 注册默认语言处理器
        self._register_default_handlers()

        # 绑定事件
        self._bind_events()

    def _register_default_handlers(self):
        """注册默认的语言处理器"""
        # 注册Python处理器
        python_handler = PythonHandler()
        for ext in python_handler.get_file_extensions():
            self.register_language(ext, python_handler)

        # 注册JSON处理器
        json_handler = JSONHandler()
        for ext in json_handler.get_file_extensions():
            self.register_language(ext, json_handler)

        # 注册INI/TOML处理器
        ini_toml_handler = IniTomlHandler()
        for ext in ini_toml_handler.get_file_extensions():
            self.register_language(ext, ini_toml_handler)

        # 注册YAML处理器
        yaml_handler = YAMLHandler()
        for ext in yaml_handler.get_file_extensions():
            self.register_language(ext, yaml_handler)

        # 注册Bash处理器
        bash_handler = BashHandler()
        for ext in bash_handler.get_file_extensions():
            self.register_language(ext, bash_handler)

        # 注册Bat处理器
        bat_handler = BatHandler()
        for ext in bat_handler.get_file_extensions():
            self.register_language(ext, bat_handler)

        # 注册PowerShell处理器
        powershell_handler = PowerShellHandler()
        for ext in powershell_handler.file_extensions:
            self.register_language(ext, powershell_handler)

        # 注册SQL处理器
        sql_handler = SQLHandler()
        for ext in sql_handler.file_extensions:
            self.register_language(ext, sql_handler)

        # 注册HTML处理器
        html_handler = HTMLHandler()
        for ext in html_handler.get_file_extensions():
            self.register_language(ext, html_handler)

        # 注册XML处理器
        xml_handler = XMLHandler()
        for ext in xml_handler.get_file_extensions():
            self.register_language(ext, xml_handler)

        # 注册CSS处理器
        css_handler = CSSHandler()
        for ext in css_handler.get_file_extensions():
            self.register_language(ext, css_handler)

        # 注册JavaScript处理器
        javascript_handler = JavaScriptHandler()
        for ext in javascript_handler.get_file_extensions():
            self.register_language(ext, javascript_handler)

        # 注册TypeScript处理器
        typescript_handler = TypeScriptHandler()
        for ext in typescript_handler.get_file_extensions():
            self.register_language(ext, typescript_handler)

        # 注册Go处理器
        go_handler = GoHandler()
        for ext in go_handler.get_file_extensions():
            self.register_language(ext, go_handler)

        # 注册Markdown处理器
        markdown_handler = MarkdownHandler()
        for ext in markdown_handler.file_extensions:
            self.register_language(ext, markdown_handler)

        # 注册Dockerfile处理器（特殊文件名）
        dockerfile_handler = DockerfileHandler()
        for ext in dockerfile_handler.get_file_extensions():
            self.register_special_file(ext, dockerfile_handler)

        # 注册Makefile处理器
        makefile_handler = MakefileHandler()
        for ext in makefile_handler.get_file_extensions():
            self.register_special_file(ext, makefile_handler)

        # 注册Env处理器
        env_handler = EnvHandler()
        for ext in env_handler.get_file_extensions():
            self.register_language(ext, env_handler)

        # 注册GitIgnore处理器
        gitignore_handler = GitIgnoreHandler()
        for ext in gitignore_handler.get_file_extensions():
            self.register_special_file(ext, gitignore_handler)

        # 注册Log处理器
        log_handler = LogHandler()
        for ext in log_handler.get_file_extensions():
            self.register_language(ext, log_handler)

        # 注册Lua处理器
        lua_handler = LuaHandler()
        for ext in lua_handler.get_file_extensions():
            self.register_language(ext, lua_handler)

        # 注册Java处理器
        java_handler = JavaHandler()
        for ext in java_handler.get_file_extensions():
            self.register_language(ext, java_handler)

        # 注册Rust处理器
        rust_handler = RustHandler()
        for ext in rust_handler.get_file_extensions():
            self.register_language(ext, rust_handler)

        # 注册PHP处理器
        php_handler = PHPHandler()
        for ext in php_handler.get_file_extensions():
            self.register_language(ext, php_handler)

        # 注册C++处理器
        cpp_handler = CppHandler()
        for ext in cpp_handler.get_file_extensions():
            self.register_language(ext, cpp_handler)

        # 注册CSV处理器
        csv_handler = CSVHandler()
        for ext in csv_handler.get_file_extensions():
            self.register_language(ext, csv_handler)

        # 注册Vim处理器
        vim_handler = VimHandler()
        for ext in vim_handler.get_file_extensions():
            # 对于无扩展名的特殊文件名（如vimrc, gvimrc），使用register_special_file
            if ext.startswith("."):
                self.register_language(ext, vim_handler)
            else:
                self.register_special_file(ext, vim_handler)

        # 注册自动处理器 - 作为默认处理器
        auto_handler = AutoHandler()
        self.auto_handler = auto_handler  # 保存引用以便后续使用

    def register_language_handler(self, handler_class):
        """
        注册语言处理器类

        Args:
            handler_class: 语言处理器类，继承自LanguageHandler
        """
        handler = handler_class()
        for ext in handler.get_file_extensions():
            self.register_language(ext, handler)

    def _bind_events(self):
        """绑定Text组件事件"""
        # 根据渲染模式绑定不同的事件
        if self.render_visible_only:
            # 可见行模式 - 需要响应滚动和编辑事件
            # 文本修改事件 - 使用add='+'参数避免覆盖editor中的事件绑定
            self.text_widget.bind("<<Modified>>", self._handle_event, add="+")

            # 滚动事件 - 仅在只渲染可见行模式下需要
            self.text_widget.bind(
                "<Configure>", self._handle_event, add="+"
            )  # 窗口大小变化时触发
            self.text_widget.bind(
                "<MouseWheel>", self._handle_event, add="+"
            )  # 鼠标滚轮滚动时触发

            # 键盘事件 - 只绑定释放事件，减少触发频率
            self.text_widget.bind("<KeyRelease>", self._handle_event, add="+")

            # 建议添加的事件绑定
            self.text_widget.bind("<<TextInsert>>", self._handle_event, add="+")
            self.text_widget.bind("<<TextDelete>>", self._handle_event, add="+")
        else:
            # 全部渲染模式 - 不需要绑定实时更新事件
            # 只保留文件操作时的高亮，不绑定任何实时事件
            pass

    def register_language(self, extension: str, handler):
        """
        注册语言处理器（用于有扩展名的文件）

        Args:
            extension: 文件扩展名，如".py"
            handler: 语言处理器实例
        """
        # 不再在注册时编译，将在使用时编译
        # if hasattr(handler, "_compile_patterns"):
        #     handler._compile_patterns()

        self.language_handlers[extension.lower()] = handler

    def register_special_file(self, filename: str, handler):
        """
        注册特殊文件名处理器（用于无扩展名的文件）

        Args:
            filename: 文件名，如"Dockerfile", "Makefile"等
            handler: 语言处理器实例
        """
        # 不再在注册时编译，将在使用时编译
        # if hasattr(handler, "_compile_patterns"):
        #     handler._compile_patterns()

        self.language_handlers[filename] = handler

    def detect_language(self, file_path: Optional[str] = None) -> Optional[str]:
        """
        根据文件路径检测语言

        Args:
            file_path: 文件路径，如果为None则尝试使用当前文件路径

        Returns:
            Optional[str]: 检测到的文件扩展名，如果无法识别则返回"auto"
        """
        if not file_path:
            return None

        # 获取文件名和扩展名
        filename = Path(file_path).name
        _, ext = os.path.splitext(file_path)
        extension = ext.lower()

        # 1. 首先检查特殊文件名（无扩展名的文件）
        # 例如：Dockerfile, Makefile, requirements.txt等
        if filename in self.language_handlers:
            return filename

        # 2. 然后检查常规扩展名
        if extension in self.language_handlers:
            return extension

        # 3. 如果没有匹配到，返回"auto"使用自动处理器
        return "auto"

    def set_language(self, file_path: Optional[str] = None):
        """
        设置当前语言

        Args:
            file_path: 文件路径
        """
        extension = self.detect_language(file_path)
        if extension:
            self.current_language = extension
            self.current_file_extension = extension

            # 获取处理器并初始化标签样式
            handler = self._get_current_handler()
            if handler:
                self._setup_tags_for_handler(handler)
        else:
            self.current_language = None
            self.current_file_extension = None

    def _get_current_handler(self):
        """
        获取当前语言处理器

        Returns:
            LanguageHandler: 当前语言处理器实例
        """
        handler = None
        if self.current_language == "auto":
            handler = self.auto_handler
        else:
            handler = self.language_handlers.get(self.current_language)
        
        # 确保处理器已编译
        if handler:
            handler.ensure_compiled()
            
        return handler

    def highlight(self, file_path: Optional[str] = None):
        """
        执行语法高亮

        Args:
            file_path: 文件路径，如果为None则使用当前文件路径
        """
        # 如果未启用高亮，则直接返回
        if not self.highlight_enabled:
            return

        # 确定要使用的文件路径
        target_file_path = file_path or self.app.current_file_path

        # 如果没有文件路径，则不进行高亮
        if not target_file_path:
            return

        # 设置语言处理器
        self.set_language(target_file_path)

        # 如果没有语言处理器，则不进行高亮
        if not self.current_language:
            return

        # 获取当前处理器
        handler = self._get_current_handler()
        if not handler:
            return

        # 根据模式选择高亮方法
        if self.render_visible_only:
            self._highlight_visible_lines_with_handler(handler)
        else:
            self._highlight_full_document_with_handler(handler)

    def _setup_tags_for_handler(self, handler):
        """
        设置Text组件的标签样式

        Args:
            handler: 语言处理器实例
        """
        if not handler:
            return

        tag_styles = handler.get_tag_styles()

        # 为每种样式创建标签
        for tag_name, style_config in tag_styles.items():
            # 创建完整的标签名，避免与其他标签冲突
            full_tag_name = f"syntax_{tag_name}"

            # 确保不设置任何可能导致缩放问题的属性
            safe_config = {}
            for key, value in style_config.items():
                if key != "font":  # 跳过font属性，避免缩放问题
                    safe_config[key] = value

            self.text_widget.tag_config(full_tag_name, **safe_config)
            self._highlight_tags.add(full_tag_name)

    def _setup_tags(self):
        """设置Text组件的标签样式（使用当前语言处理器）"""
        if not self.current_language:
            return

        handler = self._get_current_handler()
        if handler:
            self._setup_tags_for_handler(handler)

    def _highlight_visible_lines_with_handler(self, handler):
        """使用指定处理器高亮当前可见的行"""
        # 获取可见行范围
        first_visible = self.text_widget.index("@0,0")
        last_visible = self.text_widget.index("@0,10000")

        # 扩展范围以确保覆盖所有可见内容
        first_line = int(first_visible.split(".")[0])
        last_line = int(last_visible.split(".")[0]) + 1

        # 确保范围有效
        if first_line < 1:
            first_line = 1
        # 获取文档总行数，使用end确保获取实际行数
        total_lines = int(self.text_widget.index("end").split(".")[0])
        if last_line > total_lines:
            last_line = total_lines

        # 限制高亮的行数，不超过配置的最大值
        max_lines = self.max_lines_per_highlight
        if (last_line - first_line) > max_lines:
            last_line = first_line + max_lines

        # 计算清除和添加高亮的范围
        start_index = f"{first_line}.0"
        end_index = f"{last_line}.0"

        # 只清除可见行范围的高亮
        self.clear_highlight(start_index, end_index)

        # 高亮指定范围
        self._highlight_range_with_handler(start_index, end_index, handler)

    def _highlight_full_document(self):
        """高亮整个文档（受max_lines_per_highlight限制）"""
        handler = self._get_current_handler()
        if handler:
            self._highlight_full_document_with_handler(handler)

    def _highlight_full_document_with_handler(self, handler):
        """使用指定处理器高亮整个文档（受max_lines_per_highlight限制）"""
        # 清除整个文档的高亮
        self.clear_highlight("1.0", "end")

        # 获取文档总行数，使用end确保获取实际行数
        total_lines = int(self.text_widget.index("end").split(".")[0])

        # 限制高亮的行数，不超过配置的最大值
        max_lines = min(total_lines, self.max_lines_per_highlight)

        # 高亮指定范围，使用+1确保最后一行也被包含
        self._highlight_range_with_handler("1.0", f"{max_lines}.end", handler)

    def _highlight_range(self, start_index: str, end_index: str):
        """
        高亮指定范围的文本

        Args:
            start_index: 起始索引
            end_index: 结束索引
        """
        if not self.current_language:
            return

        handler = self._get_current_handler()
        if handler:
            self._highlight_range_with_handler(start_index, end_index, handler)

    def _highlight_range_with_handler(self, start_index: str, end_index: str, handler):
        """
        使用指定处理器高亮指定范围的文本

        Args:
            start_index: 起始索引
            end_index: 结束索引
            handler: 语言处理器实例
        """
        if not handler:
            return

        # 获取预编译的正则表达式模式
        compiled_patterns = handler.get_compiled_patterns()

        # 获取文本内容
        try:
            text_content = self.text_widget.get(start_index, end_index)
        except tk.TclError:
            # 如果索引无效，则返回
            return

        # 对每种模式进行匹配和高亮
        for tag_name, compiled_pattern in compiled_patterns.items():
            full_tag_name = f"syntax_{tag_name}"

            # 使用预编译的正则表达式查找所有匹配项
            try:
                # 如果是预编译的正则表达式对象
                if hasattr(compiled_pattern, "finditer"):
                    for match in compiled_pattern.finditer(text_content):
                        # 计算匹配项在Text组件中的位置
                        start_pos = self._get_text_position(start_index, match.start())
                        end_pos = self._get_text_position(start_index, match.end())

                        # 应用标签
                        self.text_widget.tag_add(full_tag_name, start_pos, end_pos)
                else:
                    # 如果是原始字符串模式（编译失败的情况）
                    for match in re.finditer(
                        compiled_pattern, text_content, re.MULTILINE
                    ):
                        # 计算匹配项在Text组件中的位置
                        start_pos = self._get_text_position(start_index, match.start())
                        end_pos = self._get_text_position(start_index, match.end())

                        # 应用标签
                        self.text_widget.tag_add(full_tag_name, start_pos, end_pos)
            except Exception as e:
                # 如果匹配过程中出错，跳过该模式
                print(f"警告: 正则匹配 '{tag_name}' 时出错: {e}")
                continue

    def _get_text_position(self, base_index: str, offset: int) -> str:
        """
        根据基础索引和偏移量计算Text组件中的位置

        Args:
            base_index: 基础索引
            offset: 字符偏移量

        Returns:
            str: 计算后的位置索引
        """
        return f"{base_index}+{offset}c"

    def clear_highlight(self, start_index=None, end_index=None):
        """
        清除语法高亮，根据当前模式决定清除范围

        Args:
            start_index: 起始索引，如果为None则根据模式自动确定
            end_index: 结束索引，如果为None则根据模式自动确定
        """
        # 获取Text组件中的所有标签
        all_tags = self.text_widget.tag_names()

        # 根据模式确定清除范围
        if start_index is None or end_index is None:
            if self.render_visible_only:
                # 可见行模式：只清除可见区域的高亮
                first_visible = self.text_widget.index("@0,0")
                last_visible = self.text_widget.index("@0,10000")

                # 扩展范围以确保覆盖所有可见内容
                first_line = int(first_visible.split(".")[0])
                last_line = int(last_visible.split(".")[0]) + 1

                # 确保范围有效
                if first_line < 1:
                    first_line = 1
                total_lines = int(self.text_widget.index("end").split(".")[0])
                if last_line > total_lines:
                    last_line = total_lines

                start_index = f"{first_line}.0"
                end_index = f"{last_line}.0"
            else:
                # 全文档模式：清除整个文档的高亮
                start_index = "1.0"
                end_index = "end"

        # 移除所有以"syntax_"开头的标签在指定范围内的应用
        for tag_name in all_tags:
            if tag_name.startswith("syntax_"):
                self.text_widget.tag_remove(tag_name, start_index, end_index)

        # 如果是全文档清除，则清空标签集合
        if start_index == "1.0" and end_index == "end":
            self._highlight_tags.clear()

    def _handle_event(self, event=None):
        """
        通用事件处理方法

        Args:
            event: 事件对象
        """
        # 检查是否启用高亮
        if not self.highlight_enabled and self.app.current_file_path is None:
            return

        # 检查当前语言
        if not self.current_language:
            return

        # 对于所有事件，统一调用highlight方法，它内部会根据模式选择合适的高亮方式
        self.text_widget.after_idle(self.highlight)

    def set_render_mode(self, render_visible_only: bool):
        """
        设置高亮渲染模式

        Args:
            render_visible_only: 是否只渲染可见行，False表示渲染全部，True表示只渲染可见行
        """
        self.render_visible_only = render_visible_only
        # 重新绑定事件
        self._bind_events()
        # 重新高亮
        self.highlight()

    def set_enabled(self, enabled: bool, file_path: Optional[str] = None):
        """
        设置是否启用语法高亮

        Args:
            enabled: 是否启用
            file_path: 文件路径，如果为None则使用当前设置的语言
        """
        self.highlight_enabled = enabled
        if not enabled:
            # 如果禁用，则重置高亮
            self.reset_highlighting()
        else:
            # 如果启用，则重新高亮，使用当前文件路径
            if file_path:
                self.highlight(file_path)
            elif self.current_language:
                # 如果有当前语言但没有文件路径，也尝试高亮
                self.highlight()

    def is_enabled(self) -> bool:
        """
        检查语法高亮是否启用

        Returns:
            bool: 是否启用
        """
        return self.highlight_enabled

    def get_current_language(self) -> Optional[str]:
        """
        获取当前语言

        Returns:
            Optional[str]: 当前语言的文件扩展名
        """
        return self.current_language

    def apply_highlighting(self, file_path: Optional[str] = None):
        """
        应用语法高亮 - 别名方法，与highlight方法功能相同

        Args:
            file_path: 文件路径，如果为None则使用当前设置的语言
        """
        self.highlight(file_path)

    def reset_highlighting(self):
        """
        重置语法高亮 - 用于文件操作时关闭文件时调用
        """
        try:
            self.clear_highlight("1.0", "end")
            self.current_language = None
            self.current_file_extension = None
        except Exception as e:
            pass
