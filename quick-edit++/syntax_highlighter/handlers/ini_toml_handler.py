#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INI/TOML语言处理器

提供INI和TOML语法的识别和高亮规则
"""

import re
from typing import Dict, List, Any

from .base import LanguageHandler


class IniTomlHandler(LanguageHandler):
    """
    INI/TOML语言处理器

    提供INI和TOML语法的识别和高亮规则
    """

    # 支持的文件扩展名
    file_extensions = [".ini", ".toml"]

    @classmethod
    def get_language_name(cls) -> str:
        """
        获取语言处理器名称

        Returns:
            str: 语言处理器名称"ini_toml"
        """
        return "ini_toml"

    def get_pattern_order(self):
        """
        获取模式处理顺序

        Returns:
            list: 模式处理顺序列表
        """
        return self._pattern_order

    def _setup_language(self):
        """
        设置INI/TOML语言的语法高亮规则
        """
        # 定义模式处理顺序，确保字符串和注释有正确的优先级
        self._pattern_order = [
            "string",  # 字符串放在第一位，确保优先匹配
            "comment",  # 注释放在第二位
            "section",  # 节标题
            "key",  # 键名
            "value",  # 值
            "boolean",  # 布尔值
            "number",  # 数字
            "date",  # 日期时间
            "array",  # 数组
            "inline_table",  # 内联表
            "multiline_string",  # 多行字符串
            "raw_string",  # 原始字符串
            "operator",  # 操作符
        ]
        # INI/TOML关键字（实际上INI/TOML没有太多关键字，主要是保留字）
        self._keywords = []

        # 正则表达式模式
        self._regex_patterns = {
            # 注释 - INI使用;，TOML使用#
            "comments": r";.*$|#.*$",
            # 字符串 - 支持单引号和双引号
            "strings": r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'',
            # 章节 - INI: [Section], TOML: [Section], [Section.Sub], [[Array]]
            "sections": r"\[(?:[^]]+)\]",
            # 日期时间 - TOML支持的日期时间格式
            "dates": r"\b\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)?\b",
            # 布尔值 - true/false (TOML)
            "booleans": r"\b(?:true|false)\b",
            # 数字 - 整数、浮点数、科学计数法
            "numbers": r"\b-?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?\b",
            # 键名 - 匹配等号前的键
            "keys": r"\b[a-zA-Z0-9_.]+(?=\s*=)",
            # 标点符号 - []、{}、.、,、=
            "punctuation": r"([\[\]\.\{\},=])",
        }

        # 标签样式 - 使用适合INI/TOML的配色方案
        self._tag_styles = {
            # 注释 - 绿色
            "comments": {
                "foreground": "#00AA00",
            },
            # 字符串 - 红色
            "strings": {
                "foreground": "#AA0000",
            },
            # 章节 - 蓝色
            "sections": {
                "foreground": "#0000FF",
            },
            # 日期时间 - 橙色
            "dates": {
                "foreground": "#FF8800",
            },
            # 布尔值 - 蓝色（与关键字同色）
            "booleans": {
                "foreground": "#0000FF",
            },
            # 数字 - 深蓝色
            "numbers": {
                "foreground": "#0000AA",
            },
            # 键名 - 青色
            "keys": {
                "foreground": "#00AAAA",
            },
            # 标点符号 - 黑色
            "punctuation": {
                "foreground": "#000000",
            },
        }
