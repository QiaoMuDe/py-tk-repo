#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON语言处理器

提供JSON语法的识别和高亮规则
"""

import re
from typing import Dict, List, Any

from .base import LanguageHandler


class JSONHandler(LanguageHandler):
    """
    JSON语言处理器

    提供JSON语法的识别和高亮规则
    """

    # JSON文件扩展名
    file_extensions = [".json", ".jsonc", ".json5"]

    @classmethod
    def get_language_name(cls) -> str:
        """
        获取语言处理器名称

        Returns:
            str: 语言处理器名称"json"
        """
        return "json"

    def _setup_language(self):
        """
        设置JSON文件的语法高亮规则
        """
        # 定义模式处理顺序，确保字符串和注释有正确的优先级
        self._pattern_order = [
            "string",  # 字符串放在第一位，确保优先匹配
            "comment",  # 注释放在第二位
            "number",  # 数字
            "boolean",  # 布尔值
            "null",  # null值
            "key",  # JSON键
            "separator",  # 分隔符
            "whitespace",  # 空白字符
        ]
        # JSON关键字
        self._keywords = ["true", "false", "null"]

        # 正则表达式模式
        self._regex_patterns = {
            # 关键字 - 使用单词边界确保匹配完整单词
            "keywords": r"\b("
            + "|".join(re.escape(k) for k in self._keywords)
            + r")\b",
            # 字符串 - 包括单引号、双引号字符串
            "strings": r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'',
            # 数字 - 包括整数、浮点数、科学计数法
            "numbers": r"\b-?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?\b",
            # JSON标点符号
            "punctuation": r"([{}[\]:,])",
            # 注释 - JSON5支持单行和多行注释
            "comments": r"//.*$|/\*[\s\S]*?\*/",
        }

        # 标签样式 - 使用适合JSON的配色方案
        self._tag_styles = {
            # 关键字 - 蓝色
            "keywords": {
                "foreground": "#0000FF",
            },
            # 字符串 - 红色
            "strings": {
                "foreground": "#AA0000",
            },
            # 数字 - 深蓝色
            "numbers": {
                "foreground": "#0000AA",
            },
            # 标点符号 - 黑色
            "punctuation": {
                "foreground": "#000000",
            },
            # 注释 - 绿色
            "comments": {
                "foreground": "#00AA00",
            },
        }

    def get_pattern_order(self) -> List[str]:
        """
        获取模式处理顺序

        Returns:
            List[str]: 模式处理顺序列表，确保字符串和注释有正确的优先级
        """
        return self._pattern_order
