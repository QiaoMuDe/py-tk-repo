#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
YAML语言处理器

提供YAML语法的识别和高亮规则
"""

import re
from typing import Dict, List, Any

from .base import LanguageHandler


class YAMLHandler(LanguageHandler):
    """
    YAML语言处理器

    提供YAML语法的识别和高亮规则
    """

    # YAML文件扩展名
    file_extensions = [".yaml", ".yml"]

    @classmethod
    def get_language_name(cls) -> str:
        """
        获取语言处理器名称

        Returns:
            str: 语言处理器名称"yaml"
        """
        return "yaml"

    def _setup_language(self):
        """设置YAML语言的语法规则"""
        # YAML关键字和特殊值
        self._keywords = [
            # YAML特殊值
            "true",
            "false",
            "null",
            "True",
            "False",
            "Null",
            "TRUE",
            "FALSE",
            "NULL",
            "~",
            # YAML文档分隔符
            "---",
            "...",
        ]

        # 正则表达式模式
        self._regex_patterns = {
            # 关键字 - 使用单词边界确保匹配完整单词
            "keywords": r"\b("
            + "|".join(re.escape(k) for k in self._keywords)
            + r")\b",
            # 注释 - 从#开始到行尾
            "comments": r"#.*$",
            # 键名 - 不包含冒号的字符串，后跟冒号
            "keys": r"^(\s*)([a-zA-Z_][a-zA-Z0-9_\-]*)(\s*:)",
            # 字符串 - 包括单引号、双引号字符串
            "strings": r'("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')',
            # 数字 - 包括整数、浮点数、科学计数法
            "numbers": r"\b\d+\.?\d*(?:[eE][+-]?\d+)?\b",
            # 布尔值 - true/false
            "booleans": r"\b(true|false|True|False|TRUE|FALSE)\b",
            # 空值 - null/~
            "nulls": r"\b(null|Null|NULL|~)\b",
            # 列表项 - 以连字符开头的行
            "list_items": r"^(\s*)-\s",
            # 锚点和别名 - 以&或*开头
            "anchors": r"(&[a-zA-Z0-9_]+)|(\*[a-zA-Z0-9_]+)",
            # 标签和类型 - 以!!开头
            "tags": r"!![a-zA-Z0-9_]+",
            # 多行字符串指示符 - |和>
            "block_scalars": r"^[ \t]*[|>][0-9+-]*[ \t]*$",
            # 直接量 - 不带引号的字符串值
            "literals": r":\s*([a-zA-Z0-9_\-\/\.]+)",
        }

        # 标签样式 - 使用适合YAML的配色方案
        self._tag_styles = {
            # 关键字 - 深蓝色
            "keywords": {"foreground": "#000080"},
            # 注释 - 绿色
            "comments": {
                "foreground": "#008000",
            },
            # 键名 - 深紫色
            "keys": {
                "foreground": "#800080",
            },
            # 字符串 - 棕色
            "strings": {
                "foreground": "#8B4513",
            },
            # 数字 - 深红色
            "numbers": {
                "foreground": "#8B0000",
            },
            # 布尔值 - 深蓝色
            "booleans": {
                "foreground": "#0000CD",
            },
            # 空值 - 灰色
            "nulls": {
                "foreground": "#808080",
            },
            # 列表项 - 深绿色
            "list_items": {
                "foreground": "#006400",
            },
            # 锚点和别名 - 深青色
            "anchors": {
                "foreground": "#008B8B",
            },
            # 标签和类型 - 橙色
            "tags": {
                "foreground": "#FF8C00",
            },
            # 多行字符串指示符 - 紫色
            "block_scalars": {
                "foreground": "#9400D3",
            },
            # 直接量 - 深灰色
            "literals": {
                "foreground": "#2F4F4F",
            },
        }

        # 正则表达式模式顺序 - 控制语法高亮的优先级
        self._pattern_order = [
            # 注释 - 最高优先级
            "comments",
            # 特殊标记
            "block_scalars",
            "anchors",
            "tags",
            # 数据类型
            "strings",
            "numbers",
            "booleans",
            "nulls",
            # YAML结构元素
            "list_items",
            "keys",
            # 其他
            "keywords",
            "literals",
        ]

    def get_pattern_order(self):
        """
        获取语法高亮的模式匹配顺序

        Returns:
            List[str]: 模式匹配的优先级顺序列表
        """
        return self._pattern_order
