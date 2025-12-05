#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
语法高亮主控制器模块

提供语法高亮的核心功能, 包括与Text组件的交互和高亮逻辑
"""

import tkinter as tk
from typing import Optional
from pathlib import Path
import os
import re

# 导入配置管理器
from config.config_manager import config_manager

# 导入语言处理器
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
from .handlers.gitignore_handler import GitIgnoreHandler
from .handlers.log_handler import LogHandler
from .handlers.lua_handler import LuaHandler
from .handlers.java_handler import JavaHandler
from .handlers.csv_handler import CSVHandler
from .handlers.vim_handler import VimHandler
from .handlers.auto_handler import AutoHandler

# 导入日志记录器
from loguru import logger


class SyntaxHighlighter:
    """
    语法高亮主控制器

    负责管理语言处理器, 控制高亮过程, 并提供与Text组件的接口
    """

    def __init__(self, app):
        """
        初始化语法高亮器

        Args:
            text_widget: tkinter Text组件实例
        """
        logger.debug("初始化语法高亮器")

        # 从配置管理器获取配置
        syntax_config = config_manager.get_component_config("syntax_highlighter")
        if not syntax_config:
            logger.warning("无法获取语法高亮器配置，将使用默认配置")

        # 设置初始化参数
        self.app = app
        self.text_widget = app.text_area
        self.render_visible_only = syntax_config.get("render_visible_only", False)
        self.highlight_enabled = syntax_config.get("enabled", True)
        self.max_lines_per_highlight = syntax_config.get(
            "max_lines_per_highlight", 1000
        )
        # 可见行模式下，上下扩展的行数
        self.visible_line_context = syntax_config.get("visible_line_context", 10)

        # 内部状态
        self.language_handlers = {}  # 存储不同语言的处理器
        self.registered_languages = {}  # 存储已注册的语言名称，用于统计实际语言数量
        self.current_language = None  # 当前使用的语言
        self.current_file_extension = None  # 当前文件扩展名
        self._highlight_tags = set()  # 存储已创建的高亮标签

        # 防抖机制相关属性
        self._highlight_task_id = None  # 用于执行高亮任务的任务ID
        self._debounce_delay = syntax_config.get(
            "debounce_delay", 100
        )  # 从配置获取防抖延迟时间 (毫秒)

        # 不再需要重叠检查相关的配置

        # 注册默认语言处理器
        self._register_default_handlers()

        # 绑定事件
        self._bind_events()

        logger.debug("highlighter init complete!")

    def _register_default_handlers(self):
        """注册默认的语言处理器"""
        # 定义所有需要注册的处理器及其注册方式
        # 格式: (处理器类, 是否为特殊文件处理器)
        language_handlers = [
            (PythonHandler, False),
            (JSONHandler, False),
            (IniTomlHandler, False),
            (YAMLHandler, False),
            (BashHandler, False),
            (BatHandler, False),
            (PowerShellHandler, False),
            (SQLHandler, False),
            (HTMLHandler, False),
            (XMLHandler, False),
            (CSSHandler, False),
            (JavaScriptHandler, False),
            (TypeScriptHandler, False),
            (GoHandler, False),
            (MarkdownHandler, False),
            (LogHandler, False),
            (LuaHandler, False),
            (JavaHandler, False),
            (CSVHandler, False),
            (VimHandler, True),  # Vim配置文件处理器
            (DockerfileHandler, True),  # 特殊文件处理器
            (MakefileHandler, True),  # 特殊文件处理器
            (GitIgnoreHandler, True),  # 特殊文件处理器
        ]

        # 循环注册所有处理器
        for handler_class, is_special in language_handlers:
            handler = handler_class()
            for ext in handler.get_file_extensions():
                if is_special:
                    self.register_special_file(ext, handler)
                else:
                    self.register_language(ext, handler)

        # 注册自动处理器 - 作为默认处理器
        auto_handler = AutoHandler()
        self.auto_handler = auto_handler  # 保存引用以便后续使用

        logger.debug(
            f"默认语言处理器注册完成，共注册了{len(self.registered_languages)}种语言，{len(self.language_handlers)}种文件扩展名/特殊文件名"
        )

    def register_language_handler(self, handler_class):
        """
        注册语言处理器类

        Args:
            handler_class: 语言处理器类, 继承自LanguageHandler
        """
        handler = handler_class()
        for ext in handler.get_file_extensions():
            self.register_language(ext, handler)

    def _bind_events(self):
        """绑定Text组件事件"""
        # 根据渲染模式绑定不同的事件
        if self.render_visible_only:
            # 可见行模式 - 需要响应滚动和编辑事件

            # 键盘释放事件
            self.text_widget.bind("<KeyRelease>", self._handle_event, add="+")

            # 文本修改事件(修改状态)
            self.text_widget.bind("<<Modified>>", self._handle_event, add="+")

            # 文本变化事件 - 统一处理所有文本变化(插入/删除)
            self.text_widget.bind("<<TextInsert>>", self._handle_event, add="+")
            self.text_widget.bind("<<TextDelete>>", self._handle_event, add="+")

            # 鼠标滚动事件 - 仅在只渲染可见行模式下需要
            self.text_widget.bind(
                "<Configure>", self._handle_event, add="+"
            )  # 窗口大小变化时触发
            self.text_widget.bind(
                "<MouseWheel>", self._handle_event, add="+"
            )  # 鼠标滚轮滚动时触发

            # Linux 平台下的鼠标滚轮事件
            self.text_widget.bind(
                "<Button-4>", self._handle_event, add="+"
            )  # 鼠标滚轮向上滚动时触发
            self.text_widget.bind(
                "<Button-5>", self._handle_event, add="+"
            )  # 鼠标滚轮向下滚动时触发

        else:
            # 全部渲染模式 - 不需要绑定实时更新事件
            # 只保留文件操作时的高亮, 不绑定任何实时事件
            pass

    def _register_language_name(self, language_name: str):
        """
        注册语言名称到已注册语言字典中

        Args:
            language_name: 语言名称
        """
        if language_name not in self.registered_languages:
            self.registered_languages[language_name] = True

    def register_language(self, extension: str, handler):
        """
        注册语言处理器 (用于有扩展名的文件)

        Args:
            extension: 文件扩展名, 如".py"
            handler: 语言处理器实例
        """
        # 获取语言名称并注册
        language_name = handler.get_language_name()
        self._register_language_name(language_name)

        # 注册扩展名到语言处理器字典中
        self.language_handlers[extension.lower()] = handler

    def register_special_file(self, filename: str, handler):
        """
        注册特殊文件名处理器 (用于无扩展名的文件)

        Args:
            filename: 文件名, 如"Dockerfile", "Makefile"等
            handler: 语言处理器实例
        """
        # 获取语言名称并注册
        language_name = handler.get_language_name()
        self._register_language_name(language_name)

        # 注册特殊文件名到语言处理器字典中
        self.language_handlers[filename] = handler

    def detect_language(self, file_path: Optional[str] = None) -> Optional[str]:
        """
        根据文件路径检测语言

        Args:
            file_path: 文件路径, 如果为None则尝试使用当前文件路径

        Returns:
            Optional[str]: 检测到的文件扩展名, 如果无法识别则返回"auto"
        """
        if not file_path:
            logger.debug("文件路径为空，无法检测语言")
            return None

        # 获取文件名和扩展名
        filename = Path(file_path).name
        _, ext = os.path.splitext(file_path)
        extension = ext.lower()

        logger.debug(f"检测文件语言: 文件名={filename}, 扩展名={extension}")

        # 1. 首先检查特殊文件名 (无扩展名的文件)
        # 例如: Dockerfile, Makefile, requirements.txt等
        if filename in self.language_handlers:
            logger.debug(f"检测到特殊文件名: {filename}")
            return filename

        # 2. 然后检查常规扩展名
        if extension in self.language_handlers:
            logger.debug(f"检测到扩展名: {extension}")
            return extension

        # 3. 如果没有匹配到, 返回"auto"使用自动处理器
        logger.debug(f"未识别的文件类型: {file_path}, 将使用自动处理器")
        return "auto"

    def get_language_name(self) -> str:
        """
        获取当前语言的名称

        Returns:
            str: 当前语言的名称，如果未设置语言则返回"auto"
        """
        handler = self._get_current_handler()
        if handler:
            return handler.get_language_name()
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
            self.current_language = "auto"
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

    def apply_highlighting(self, file_path: Optional[str] = None):
        """
        应用语法高亮

        Args:
            file_path: 文件路径, 如果为None则使用当前文件路径
        """
        # 如果未启用高亮, 则直接返回
        if not self.highlight_enabled:
            return

        # 确定要使用的文件路径
        target_file_path = file_path or self.app.current_file_path

        # 如果没有文件路径, 则不进行高亮
        if not target_file_path:
            logger.debug("无文件路径，跳过语法高亮")
            return

        logger.debug(f"开始应用语法高亮: {target_file_path}")

        # 设置语言处理器
        self.set_language(target_file_path)

        # 如果没有语言处理器, 则不进行高亮
        if not self.current_language:
            logger.warning(f"无法识别文件语言: {target_file_path}")
            return

        # 获取当前处理器
        handler = self._get_current_handler()
        if not handler:
            logger.error(f"无法获取语言处理器: {self.current_language}")
            return

        logger.debug(f"使用语言处理器: {handler.get_language_name()}")

        # 根据模式选择高亮方法
        try:
            if self.render_visible_only:
                self._highlight_visible_lines_with_handler(handler)
            else:
                self._highlight_full_document_with_handler(handler)
            logger.debug(f"语法高亮应用成功: {target_file_path}")
        except Exception as e:
            logger.error(f"应用语法高亮失败: {target_file_path}, 错误: {str(e)}")

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
            # 创建完整的标签名, 避免与其他标签冲突
            full_tag_name = f"syntax_{tag_name}"

            # 确保不设置任何可能导致缩放问题的属性
            safe_config = {}
            for key, value in style_config.items():
                if key != "font":  # 跳过font属性, 避免缩放问题
                    safe_config[key] = value

            self.text_widget.tag_config(full_tag_name, **safe_config)
            self._highlight_tags.add(full_tag_name)

        # 确保选中标签的优先级最高, 防止被语法高亮覆盖
        # 在所有语法高亮标签设置完成后, 提高选中标签的优先级
        self.text_widget.tag_raise("sel")

    def _setup_tags(self):
        """设置Text组件的标签样式 (使用当前语言处理器)"""
        handler = self._get_current_handler()
        if handler:
            self._setup_tags_for_handler(handler)

    def _get_visible_line_range(self):
        """
        获取当前可见的行范围（包含上下文扩展）

        Returns:
            tuple: (first_line, last_line) 可见行的起始和结束行号
        """
        # 获取可见行范围
        first_visible = self.text_widget.index("@0,0")
        last_visible = self.text_widget.index("@0,10000")

        # 扩展范围以确保覆盖所有可见内容
        first_line = int(first_visible.split(".")[0])
        last_line = int(last_visible.split(".")[0]) + 1

        # 添加上下文扩展行数
        first_line -= self.visible_line_context
        last_line += self.visible_line_context

        # 确保范围有效
        if first_line < 1:
            first_line = 1
        # 获取文档总行数, 使用end确保获取实际行数
        total_lines = int(self.text_widget.index("end").split(".")[0])
        if last_line > total_lines:
            last_line = total_lines

        # 限制高亮的行数, 不超过配置的最大值
        max_lines = self.max_lines_per_highlight
        if (last_line - first_line) > max_lines:
            last_line = first_line + max_lines

        return first_line, last_line

    def _highlight_visible_lines_with_handler(self, handler):
        """使用指定处理器高亮当前可见的行"""
        # 获取可见行范围
        first_line, last_line = self._get_visible_line_range()

        # 计算清除和添加高亮的范围
        start_index = f"{first_line}.0"
        end_index = f"{last_line}.0"

        # 只清除可见行范围的高亮
        self.clear_highlight(start_index, end_index)

        # 高亮指定范围
        self._highlight_range_with_handler(start_index, end_index, handler)

    def _highlight_full_document_with_handler(self, handler):
        """使用指定处理器高亮整个文档 (受max_lines_per_highlight限制)"""
        # 清除整个文档的高亮
        self.clear_highlight("1.0", "end")

        # 获取文档总行数, 使用end确保获取实际行数
        total_lines = int(self.text_widget.index("end").split(".")[0])

        # 限制高亮的行数, 不超过配置的最大值
        max_lines = min(total_lines, self.max_lines_per_highlight)

        # 高亮指定范围, 使用+1确保最后一行也被包含
        self._highlight_range_with_handler("1.0", f"{max_lines}.end", handler)

    # 所有重叠检查相关的方法已删除，现在直接添加所有高亮范围

    def _highlight_range_with_handler(self, start_index: str, end_index: str, handler):
        """
        使用指定处理器高亮指定范围的文本

        Args:
            start_index: 起始索引
            end_index: 结束索引
            handler: 语言处理器实例
        """
        if not handler:  # 检查处理器是否存在
            logger.error("语言处理器为空，无法进行高亮")
            return

        # 获取预编译的正则表达式模式
        compiled_patterns = handler.get_compiled_patterns()

        # 获取文本内容
        try:  # 尝试获取指定范围内的文本
            text_content = self.text_widget.get(start_index, end_index)
        except tk.TclError as e:
            # 如果索引无效, 则返回
            logger.error(f"获取文本内容失败: {str(e)}")
            return

        # 收集所有标签位置, 用于批量应用
        tag_ranges = {}

        # 按照处理器定义的顺序处理模式
        for tag_name in handler.get_pattern_order():
            if tag_name not in compiled_patterns:
                continue

            compiled_pattern = compiled_patterns[tag_name]
            full_tag_name = f"syntax_{tag_name}"
            tag_ranges[full_tag_name] = []

            # 使用预编译的正则表达式查找所有匹配项
            try:
                for match in compiled_pattern.finditer(text_content):
                    # 计算匹配的位置
                    start_pos, end_pos = self._get_text_position_range(
                        start_index, match.start(), match.end()
                    )

                    # 直接添加所有匹配的高亮范围，不进行重叠检查
                    tag_ranges[full_tag_name].append((start_pos, end_pos))

            except re.error as e:
                # 正则表达式匹配错误，记录并跳过
                logger.error(f"正则匹配 '{tag_name}' 时发生错误: {str(e)}")
                continue
            except Exception as e:
                # 其他匹配过程中出错, 跳过该模式
                logger.error(f"正则匹配 '{tag_name}' 时发生意外错误: {str(e)}")
                logger.debug(
                    f"意外错误详情: 标签名={tag_name}, 错误类型={type(e).__name__}"
                )
                continue

        # 批量应用所有标签, 减少API调用
        try:
            self._apply_tags_batch(tag_ranges)
        except Exception as e:
            logger.error(f"应用标签时出错: {str(e)}")

    # 所有重叠检查相关的方法已删除，现在直接添加所有高亮范围

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

    def _get_text_position_range(
        self, base_index: str, start_offset: int, end_offset: int
    ) -> tuple:
        """
        计算偏移量范围对应的文本位置 (优化版本, 减少重复计算)

        Args:
            base_index: 基础索引
            start_offset: 起始偏移量
            end_offset: 结束偏移量

        Returns:
            tuple: (start_pos, end_pos) 元组
        """
        start_pos = f"{base_index}+{start_offset}c"
        end_pos = f"{base_index}+{end_offset}c"
        return start_pos, end_pos

    def _apply_tags_batch(self, tag_ranges: dict):
        """
        批量应用标签到文本组件 (优化版本, 减少API调用)

        Args:
            tag_ranges: 标签范围字典, 格式为 {tag_name: [(start1, end1), (start2, end2), ...]}
        """
        # 直接使用底层的_textbox组件, 支持一次添加多个范围
        for tag_name, ranges in tag_ranges.items():
            if not ranges:
                continue

            # 展平所有范围, 准备一次性添加
            flat_ranges = []
            for start_pos, end_pos in ranges:
                flat_ranges.extend([start_pos, end_pos])

            # 直接调用底层_textbox的tag_add方法, 支持多个范围
            self.text_widget._textbox.tag_add(tag_name, *flat_ranges)

    def clear_highlight(self, start_index=None, end_index=None):
        """
        清除语法高亮, 根据当前模式决定清除范围

        Args:
            start_index: 起始索引, 如果为None则根据模式自动确定
            end_index: 结束索引, 如果为None则根据模式自动确定
        """
        # 获取Text组件中的所有标签
        all_tags = self.text_widget.tag_names()

        # 根据模式确定清除范围
        if start_index is None or end_index is None:
            if self.render_visible_only:
                # 可见行模式: 只清除可见区域的高亮
                first_line, last_line = self._get_visible_line_range()
                start_index = f"{first_line}.0"
                end_index = f"{last_line}.0"
            else:
                # 全文档模式: 清除整个文档的高亮
                start_index = "1.0"
                end_index = "end"

        # 移除所有以"syntax_"开头的标签在指定范围内的应用
        for tag_name in all_tags:
            if tag_name.startswith("syntax_"):
                self.text_widget.tag_remove(tag_name, start_index, end_index)

        # 如果是全文档清除, 则清空标签集合
        if start_index == "1.0" and end_index == "end":
            self._highlight_tags.clear()

    def _handle_event(self, event=None):
        """
        通用事件处理方法 (带防抖机制)

        Args:
            event: 事件对象
        """
        # 检查是否启用高亮
        if not self.highlight_enabled and self.app.current_file_path is None:
            logger.debug("语法高亮未启用且无当前文件路径，跳过事件处理")
            return

        # 检查当前语言
        if not self.current_language:
            logger.debug("无当前语言设置，跳过事件处理")
            return

        # 防抖机制: 取消之前的高亮任务
        if self._highlight_task_id is not None:
            self.text_widget.after_cancel(self._highlight_task_id)

        # 设置新的高亮任务, 延迟执行
        self._highlight_task_id = self.text_widget.after(
            self._debounce_delay, self._execute_highlight_task
        )

    def _execute_highlight_task(self):
        """
        实际执行高亮任务的方法

        该方法在防抖延迟后被调用, 执行实际的语法高亮操作
        """
        # 重置任务ID
        self._highlight_task_id = None

        # 使用after_idle调用高亮方法, 确保在UI空闲时执行
        self.text_widget.after_idle(self.apply_highlighting)

    def set_render_mode(self, render_visible_only: bool):
        """
        设置高亮渲染模式

        Args:
            render_visible_only: 是否只渲染可见行, False表示渲染全部, True表示只渲染可见行
        """
        self.render_visible_only = render_visible_only
        # 重新绑定事件
        self._bind_events()
        # 重新高亮
        self.apply_highlighting()

    def set_enabled(self, enabled: bool, file_path: Optional[str] = None):
        """
        设置是否启用语法高亮

        Args:
            enabled: 是否启用
            file_path: 文件路径, 如果为None则使用当前设置的语言
        """
        self.highlight_enabled = enabled
        if not enabled:
            # 如果禁用, 则重置高亮
            self.reset_highlighting()
        else:
            # 如果启用, 则重新高亮, 使用当前文件路径
            if file_path:
                self.apply_highlighting(file_path)
            elif self.current_language:
                # 如果有当前语言但没有文件路径, 也尝试高亮
                self.apply_highlighting()

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

    def reset_highlighting(self):
        """
        重置语法高亮 - 用于文件操作时关闭文件时调用
        """
        try:
            # 取消任何待执行的高亮任务
            if self._highlight_task_id is not None:
                self.text_widget.after_cancel(self._highlight_task_id)
                self._highlight_task_id = None

            self.clear_highlight("1.0", "end")
            self.current_language = None
            self.current_file_extension = None
        except Exception:
            pass
