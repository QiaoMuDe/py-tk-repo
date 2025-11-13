#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.env文件语言处理器

提供.env文件的语法高亮支持
"""

import re
from typing import Dict, List, Any

from .base import LanguageHandler


class EnvHandler(LanguageHandler):
    """.env和Properties文件语言处理器"""

    # .env和.properties文件扩展名
    file_extensions = [".env", ".properties"]

    def _setup_language(self):
        """
        设置.env文件的语法高亮规则
        """
        # .env文件的关键字和特殊标记
        self._keywords = ["export", "set", "unset"]

        # 正则表达式模式
        self._regex_patterns = {
            # 注释 (以#开头的行)
            "comment": r"(?m)^\s*#.*$",
            # 变量赋值 (KEY=VALUE格式，支持包含小数点的key)
            "assignment": r"(?m)^[a-zA-Z_.][a-zA-Z0-9_.]*\s*=",
            # 变量名 (赋值号前面的部分，支持包含小数点的key)
            "variable": r"(?m)^[a-zA-Z_.][a-zA-Z0-9_.]*(?=\s*=)",
            # 变量引用 (${VAR}或$VAR，支持包含小数点的变量名)
            "reference": r"\$\{[a-zA-Z0-9_.]+\}|\$[a-zA-Z_.][a-zA-Z0-9_.]*(?![a-zA-Z0-9_.])",
            # 字符串值 (双引号或单引号包围的值)
            "string": r"=\s*([\"'])(?:(?=(\\?))\2.)*?\1",
            # 布尔值 (true/false)
            "boolean": r"=\s*(true|false)\s*$",
            # 数字值
            "number": r"=\s*\b\d+\.?\d*\b",
            # 导出语句 (支持包含小数点的变量名)
            "export": r"(?m)^\s*export\s+[a-zA-Z_.][a-zA-Z0-9_.]*",
            # 特殊标记 (如#|用于多行字符串)
            "multiline": r"=\s*#\|",
        }

        # 标签样式 - 使用简洁的配色方案
        self._tag_styles = {
            "comment": {"foreground": "#6A9955"},  # 绿色用于注释
            "assignment": {"foreground": "#D4D4D4"},  # 浅灰色用于赋值符号
            "variable": {"foreground": "#4EC9B0"},  # 青色用于变量名
            "reference": {"foreground": "#9CDCFE"},  # 浅蓝色用于变量引用
            "string": {"foreground": "#CE9178"},  # 橙色用于字符串
            "boolean": {"foreground": "#569CD6"},  # 蓝色用于布尔值
            "number": {"foreground": "#B5CEA8"},  # 浅绿色用于数字
            "export": {"foreground": "#C586C0"},  # 紫色用于导出语句
            "multiline": {"foreground": "#DCDCAA"},  # 浅黄色用于多行标记
        }
