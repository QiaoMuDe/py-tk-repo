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
    file_extensions = ['.ini', '.toml']

    def _setup_language(self):
        """
        设置INI/TOML语言的语法规则

        实现了对INI和TOML共同元素的识别:
        - 注释（INI: ;，TOML: #）
        - 字符串（单引号和双引号）
        - 章节（INI: [Section], TOML: [Section], [Section.Sub], [[Array]]）
        - 日期时间（TOML）
        - 布尔值（TOML）
        - 数字
        - 键名
        - 标点符号
        """
        # 关键字列表（INI无关键字，TOML关键字由其他模式处理）
        self._keywords = []

        # 正则表达式模式
        self._regex_patterns = {
            # 注释 - INI使用;，TOML使用#
            "comments": r';.*$|#.*$',
            # 字符串 - 支持单引号和双引号
            "strings": r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'',
            # 章节 - INI: [Section], TOML: [Section], [Section.Sub], [[Array]]
            "sections": r'\[(?:[^]]+)\]',
            # 日期时间 - TOML支持的日期时间格式
            "dates": r'\b\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)?\b',
            # 布尔值 - true/false (TOML)
            "booleans": r'\b(?:true|false)\b',
            # 数字 - 整数、浮点数、科学计数法
            "numbers": r'\b-?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?\b',
            # 键名 - 匹配等号前的键
            "keys": r'\b[a-zA-Z0-9_.]+(?=\s*=)',
            # 标点符号 - []、{}、.、,、=
            "punctuation": r'([[\].{},=])',
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