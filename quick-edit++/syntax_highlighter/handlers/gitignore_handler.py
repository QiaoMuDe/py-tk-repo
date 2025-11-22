#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Git忽略文件处理器

提供.gitignore、.dockerignore等忽略文件的语法高亮支持
"""

import re
from typing import Dict, List, Any

from .base import LanguageHandler


class GitIgnoreHandler(LanguageHandler):
    """
    Git忽略文件语言处理器

    提供.gitignore、.dockerignore、.eslintignore等忽略文件的语法高亮支持
    """

    # 忽略文件扩展名和名称
    file_extensions = [
        ".gitignore",
        ".dockerignore",
        ".eslintignore",
        ".prettierignore",
        ".npmignore",
        ".hgignore",
        ".bzrignore",
    ]

    @classmethod
    def get_language_name(cls) -> str:
        """
        获取语言处理器名称

        Returns:
            str: 语言处理器名称"gitignore"
        """
        return "gitignore"

    def _setup_language(self):
        """
        设置忽略文件的语法高亮规则
        """
        # 忽略文件的特殊标记
        self._keywords = [
            # 这些不是传统意义上的关键字，但在这里用于特殊模式的识别
        ]

        # 正则表达式模式
        self._regex_patterns = {
            # 注释 (以#开头的行)
            "comment": r"(?m)^\s*#.*$",
            # 否定模式 (以!开头的行，表示不忽略匹配的文件)
            "negation": r"(?m)^\s*!\s*.*$",
            # 目录模式 (以/结尾的行，表示只忽略目录)
            "directory": r"(?m)^[^#][^\n]*\/\s*$",
            # 绝对路径模式 (以/开头的行，表示从根目录开始匹配)
            "absolute": r"(?m)^\s*\/[^!][^\n]*$",
            # 通配符模式 (包含*或?或[]的行)
            "wildcard": r"(?m)^[^#][^\n]*[*?\[][^\n]*$",
            # 双星号模式 (包含**的特殊通配符)
            "double_asterisk": r"(?m)^[^#][^\n]*\*\*[^\n]*$",
            # 括号模式 (包含字符集[])
            "bracket_pattern": r"(?m)^[^#][^\n]*\[[^\]]*\][^\n]*$",
            # 花括号模式 (包含{}，用于扩展模式)
            "brace_pattern": r"(?m)^[^#][^\n]*\{[^}]*\}[^\n]*$",
            # 空行 (用于格式化)
            "empty_line": r"(?m)^\s*$",
            # 转义字符 (以\开头的特殊字符)
            "escaped": r"\\[#!$&()*;<>?[\\]^`{|}]",
        }

        # 定义语法高亮模式的处理顺序
        # 优先级从上到下依次降低
        self._pattern_order = [
            # 最高优先级：注释 - 优先匹配整行注释
            "comment",
            # 高优先级：空行 - 用于格式化
            "empty_line",
            # 高优先级：否定模式 - 以!开头的行，表示不忽略匹配的文件
            "negation",
            # 高优先级：转义字符 - 特殊字符的转义
            "escaped",
            # 中优先级：特殊模式 - 绝对路径、目录模式
            "absolute",
            "directory",
            # 中优先级：复杂通配符模式 - 包含特殊字符的模式
            "brace_pattern",
            "bracket_pattern",
            "double_asterisk",
            # 最低优先级：普通通配符 - 简单的通配符模式
            "wildcard",
        ]

        # 标签样式 - 使用适合忽略文件的配色方案
        self._tag_styles = {
            "comment": {"foreground": "#6A9955"},  # 绿色用于注释
            "negation": {"foreground": "#C586C0"},  # 紫色用于否定模式
            "directory": {"foreground": "#4EC9B0"},  # 青色用于目录模式
            "absolute": {"foreground": "#569CD6"},  # 蓝色用于绝对路径
            "wildcard": {"foreground": "#CE9178"},  # 橙色用于通配符
            "double_asterisk": {"foreground": "#DCDCAA"},  # 浅黄色用于双星号
            "bracket_pattern": {"foreground": "#9CDCFE"},  # 浅蓝色用于字符集
            "brace_pattern": {"foreground": "#B5CEA8"},  # 浅绿色用于花括号
            "empty_line": {"foreground": "#D4D4D4"},  # 浅灰色用于空行
            "escaped": {"foreground": "#FF7700"},  # 橙红色用于转义字符
        }

    def get_pattern_order(self):
        """
        获取语法高亮模式的处理顺序

        Returns:
            list: 包含正则表达式模式名称的列表，按照优先级排序
        """
        return self._pattern_order
