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

# 导入配置管理器
from config.config_manager import config_manager

# 导入语言处理器
from .handlers import LanguageHandler


class SyntaxHighlighter:
    """
    语法高亮主控制器

    负责管理语言处理器，控制高亮过程，并提供与Text组件的接口
    """

    def __init__(self, text_widget: tk.Text):
        """
        初始化语法高亮器

        Args:
            text_widget: tkinter Text组件实例
        """
        # 从配置管理器获取配置
        syntax_config = config_manager.get_component_config("syntax_highlighter")

        # 设置初始化参数
        self.text_widget = text_widget
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
        # 导入Python处理器
        from .handlers.python_handler import PythonHandler

        # 注册Python处理器
        python_handler = PythonHandler()
        for ext in python_handler.get_file_extensions():
            self.register_language(ext, python_handler)

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
        # 文本修改事件 - 使用add='+'参数避免覆盖editor中的事件绑定
        self.text_widget.bind("<<Modified>>", self._handle_event, add="+")

        # 滚动事件 - 仅在只渲染可见行模式下需要，使用add='+'参数避免覆盖editor中的事件绑定
        if self.render_visible_only:
            self.text_widget.bind("<Configure>", self._handle_event, add="+")
            self.text_widget.bind("<MouseWheel>", self._handle_event, add="+")

        # 键盘事件 - 检测按键输入，使用add='+'参数避免覆盖editor中的事件绑定
        self.text_widget.bind("<Key>", self._handle_event, add="+")

        # 鼠标事件 - 检测鼠标点击和选择，使用add='+'参数避免覆盖editor中的事件绑定
        self.text_widget.bind("<Button-1>", self._handle_event, add="+")  # 左键点击
        self.text_widget.bind(
            "<ButtonRelease-1>", self._handle_event, add="+"
        )  # 左键释放

    def register_language(self, extension: str, handler):
        """
        注册语言处理器

        Args:
            extension: 文件扩展名，如".py"
            handler: 语言处理器实例
        """
        self.language_handlers[extension.lower()] = handler

    def detect_language(self, file_path: Optional[str] = None) -> Optional[str]:
        """
        根据文件路径检测语言

        Args:
            file_path: 文件路径，如果为None则尝试使用当前文件路径

        Returns:
            Optional[str]: 检测到的文件扩展名，如果无法识别则返回None
        """
        if not file_path:
            return None

        extension = Path(file_path).suffix.lower()
        if extension in self.language_handlers:
            return extension
        return None

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
            # 初始化标签样式
            self._setup_tags()
        else:
            self.current_language = None
            self.current_file_extension = None

    def _setup_tags(self):
        """设置Text组件的标签样式"""
        if not self.current_language:
            return

        handler = self.language_handlers[self.current_language]
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

    def highlight(self, file_path: Optional[str] = None):
        """
        执行语法高亮

        Args:
            file_path: 文件路径，如果为None则使用当前设置的语言
        """
        if not self.highlight_enabled:
            return

        # 设置语言
        if file_path:
            self.set_language(file_path)

        # 如果没有语言处理器，则不进行高亮
        if not self.current_language:
            return

        # 根据模式选择高亮方法
        if self.render_visible_only:
            self._highlight_visible_lines()
        else:
            self._highlight_full_document()

    def _highlight_visible_lines(self):
        """高亮当前可见的行"""
        # 清除现有高亮
        self._clear_highlight()

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

        # 高亮指定范围
        self._highlight_range(f"{first_line}.0", f"{last_line}.0")

    def _highlight_full_document(self):
        """高亮整个文档（受max_lines_per_highlight限制）"""
        # 清除现有高亮
        self._clear_highlight()

        # 获取文档总行数，使用end确保获取实际行数
        total_lines = int(self.text_widget.index("end").split(".")[0])

        # 限制高亮的行数，不超过配置的最大值
        max_lines = min(total_lines, self.max_lines_per_highlight)

        # 高亮指定范围，使用+1确保最后一行也被包含
        self._highlight_range("1.0", f"{max_lines}.end")

    def _highlight_range(self, start_index: str, end_index: str):
        """
        高亮指定范围的文本

        Args:
            start_index: 起始索引
            end_index: 结束索引
        """
        if not self.current_language:
            return

        handler = self.language_handlers[self.current_language]
        patterns = handler.get_regex_patterns()

        # 获取文本内容
        try:
            text_content = self.text_widget.get(start_index, end_index)
        except tk.TclError:
            # 如果索引无效，则返回
            return

        # 对每种模式进行匹配和高亮
        for tag_name, pattern in patterns.items():
            full_tag_name = f"syntax_{tag_name}"

            # 使用正则表达式查找所有匹配项
            for match in re.finditer(pattern, text_content, re.MULTILINE):
                # 计算匹配项在Text组件中的位置
                start_pos = self._get_text_position(start_index, match.start())
                end_pos = self._get_text_position(start_index, match.end())

                # 应用标签
                self.text_widget.tag_add(full_tag_name, start_pos, end_pos)

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

    def _clear_highlight(self):
        """清除所有语法高亮"""
        for tag_name in self._highlight_tags:
            self.text_widget.tag_remove(tag_name, "1.0", "end")

    def _handle_event(self, event=None):
        """
        通用事件处理方法

        Args:
            event: 事件对象
        """
        # 检查是否启用高亮和当前语言
        if not self.highlight_enabled or not self.current_language:
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

    def set_enabled(self, enabled: bool):
        """
        设置是否启用语法高亮

        Args:
            enabled: 是否启用
        """
        self.highlight_enabled = enabled
        if not enabled:
            self._clear_highlight()
        else:
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
