#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CSV语言处理器

提供CSV语法的识别和高亮规则
"""

import re
from typing import Dict, List, Any

from .base import LanguageHandler


class CSVHandler(LanguageHandler):
    """
    CSV语言处理器

    提供CSV语法的识别和高亮规则
    """

    # CSV文件扩展名
    file_extensions = [".csv", ".tsv"]

    @classmethod
    def get_language_name(cls) -> str:
        """
        获取语言处理器名称
        
        Returns:
            str: 语言处理器名称"csv"
        """
        return "csv"

    def _setup_language(self):
        """设置CSV语言的语法规则"""
        # CSV没有关键字，但可以有一些常见的标识符
        self._keywords = []

        # 正则表达式模式
        self._regex_patterns = {
            # 引号包围的字段 - 双引号或单引号
            "quoted_fields": r'(?:"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')',
            # 数字字段 - 纯数字
            "number_fields": r"\b-?\d+(?:\.\d+)?\b",
            # 逗号分隔符 - CSV字段分隔符
            "comma_separators": r",",
            # 制表符分隔符 - TSV字段分隔符
            "tab_separators": r"\t",
            # 分号分隔符 - 某些CSV格式使用分号
            "semicolon_separators": r";",
            # 管道分隔符 - 某些分隔文件使用管道符
            "pipe_separators": r"\|",
            # 布尔值 - 常见的布尔表示
            "boolean_values": r"\b(true|false|yes|no|on|off|1|0)\b",
            # 日期时间 - 常见的日期格式
            "datetime": r"\b\d{4}-\d{2}-\d{2}(?:[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)?\b",
            # 邮箱地址
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            # URL链接
            "url": r"\bhttps?://[^\s,;$]+\b",
            # 空字段 - 连续分隔符或引号内的空内容
            "empty_fields": r'(?:^|,|;|\t|\|)(?:""|\'\')(?=,|;|\t|\||$)|(?:^|,|;|\t|\|)(?=,|;|\t|\||$)',
        }

        # 标签样式 - 使用适合CSV的配色方案
        self._tag_styles = {
            # 引号字段 - 深绿色
            "quoted_fields": {
                "foreground": "#006400",
            },
            # 数字字段 - 深蓝色
            "number_fields": {
                "foreground": "#000080",
            },
            # 逗号分隔符 - 灰色
            "comma_separators": {
                "foreground": "#808080",
            },
            # 制表符分隔符 - 灰色
            "tab_separators": {
                "foreground": "#808080",
            },
            # 分号分隔符 - 灰色
            "semicolon_separators": {
                "foreground": "#808080",
            },
            # 管道分隔符 - 灰色
            "pipe_separators": {
                "foreground": "#808080",
            },
            # 布尔值 - 紫色
            "boolean_values": {
                "foreground": "#800080",
            },
            # 日期时间 - 深红色
            "datetime": {
                "foreground": "#8B0000",
            },
            # 邮箱地址 - 蓝色
            "email": {
                "foreground": "#0000FF",
            },
            # URL链接 - 蓝色加下划线
            "url": {
                "foreground": "#0000FF",
                "underline": True,
            },
            # 空字段 - 浅灰色背景
            "empty_fields": {
                "foreground": "#A9A9A9",
            },
        }
