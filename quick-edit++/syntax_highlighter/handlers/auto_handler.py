#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通用自动语言处理器

用于处理没有特定语言处理器的文件类型，提供基本的语法高亮功能
"""

import re
from typing import Dict, List, Any
from .base import LanguageHandler


class AutoHandler(LanguageHandler):
    """
    通用自动语言处理器

    为未知文件类型提供基本的语法高亮，包括：
    - 基本的字符串高亮
    - 基本的注释高亮
    - 基本的数字高亮
    - 基本的常见关键字高亮
    - URL和链接识别
    - 邮箱地址识别
    - IP地址识别
    - ISO 8601时间戳识别
    - 简单日期格式识别
    - 时间格式识别
    - 文件路径识别
    - 十六进制和二进制值识别
    - 文件大小单位识别
    - 时间单位识别
    - 环境变量识别
    - MD5哈希识别
    - SHA哈希识别
    """

    # 支持所有文件扩展名，作为默认处理器
    file_extensions = ["*"]

    @classmethod
    def get_language_name(cls) -> str:
        """
        获取语言处理器名称

        Returns:
            str: 语言处理器名称"auto"
        """
        return "auto"

    def get_pattern_order(self) -> List[str]:
        """
        获取高亮规则的执行顺序

        Returns:
            List[str]: 高亮规则名称的列表，按执行顺序排列
        """
        return self._pattern_order

    def _setup_language(self):
        """设置通用语言的语法规则"""
        # 定义高亮规则执行顺序
        self._pattern_order = [
            "strings",  # 字符串 - 最高优先级
            "comments",  # 注释 - 高优先级
            "urls",  # URL和链接
            "variables",  # 变量赋值 - 高亮等号左边的键名
            "keywords",  # 关键字
            "timestamps",  # ISO 8601时间戳
            "dates",  # 简单日期格式
            "times",  # 时间格式
            "time_units",  # 时间单位
            "file_sizes",  # 文件大小单位
            "emails",  # 邮箱地址
            "ip_addresses",  # IP地址
            "file_paths",  # 文件路径
            "numbers",  # 数字
            "operators",  # 操作符
            "functions",  # 函数调用
            "hex_values",  # 十六进制值
            "binary_values",  # 二进制值
            "env_vars",  # 环境变量
            "md5_hashes",  # MD5哈希
            "sha_hashes",  # SHA哈希
        ]

        # 常见编程语言关键字（跨语言）
        self._keywords = [
            # 控制流关键字
            "if",
            "else",
            "elif",
            "for",
            "while",
            "do",
            "switch",
            "case",
            "default",
            "break",
            "continue",
            "return",
            "goto",
            "pass",
            "yield",
            # 函数和类定义
            "function",
            "func",
            "def",
            "class",
            "interface",
            "struct",
            "type",
            # 变量声明
            "var",
            "let",
            "const",
            "static",
            "final",
            "volatile",
            # 访问修饰符
            "public",
            "private",
            "protected",
            "internal",
            "abstract",
            "virtual",
            # 数据类型
            "int",
            "float",
            "double",
            "char",
            "string",
            "bool",
            "boolean",
            "void",
            "null",
            # 布尔值
            "true",
            "false",
            "yes",
            "no",
            "on",
            "off",
            # 其他常见关键字
            "import",
            "include",
            "require",
            "package",
            "module",
            "namespace",
            "using",
            "try",
            "catch",
            "finally",
            "throw",
            "throws",
            "raise",
            "except",
            "new",
            "delete",
            "this",
            "self",
            "super",
            "base",
            "async",
            "await",
            "sync",
            "lock",
            "thread",
            "parallel",
            "in",
            "out",
            "ref",
            "by",
            "of",
            "to",
            "from",
            "as",
            "is",
        ]

        # 正则表达式模式
        self._regex_patterns = {
            # 注释 - 只匹配井号注释
            "comments": r"#.*?$",
            # 字符串 - 支持多种常见字符串格式，包括转义字符
            "strings": r"(?:\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`)",
            # 数字 - 支持常见数字格式
            "numbers": r"\b(?:0[bB][01]+|0[oO][0-7]+|0[xX][0-9a-fA-F]+|\d+(?:\.\d*)?(?:[eE][+-]?\d+)?)\b",
            # 常见关键字
            "keywords": r"\b(?:if|else|elif|for|while|do|switch|case|default|break|continue|return|goto|pass|yield|function|func|def|class|interface|struct|type|var|let|const|static|final|volatile|public|private|protected|internal|abstract|virtual|int|float|double|char|string|bool|boolean|void|null|true|false|yes|no|on|off|import|include|require|package|module|namespace|using|try|catch|finally|throw|throws|raise|except|new|delete|this|self|super|base|async|await|sync|lock|thread|parallel|in|out|ref|by|of|to|from|as|is)\b",
            # 常见操作符
            "operators": r"(\+\+|--|==|!=|<=|>=|&&|\|\||<<|>>|&\^|<-|[+\-*/%&|^=<>!.,;:\[\]{}()])",
            # 常见函数调用
            "functions": r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(",
            # 常见变量赋值 - 支持键名中包含连字符和点号，高亮等号左边的键名
            "variables": r"\b([a-zA-Z_][a-zA-Z0-9_.-]*)\s*={1,2}",
            # URL和链接
            "urls": r"\b(?:[a-zA-Z]+://|www\.)[^\s<>\"]+",
            # 邮箱地址
            "emails": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            # IP地址
            "ip_addresses": r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",
            # ISO 8601时间戳
            "timestamps": r"\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?\b",
            # 简单日期格式
            "dates": r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b",
            # 时间格式
            "times": r"\b\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?\b",
            # 文件路径 - Windows和Unix格式，支持相对路径和绝对路径
            "file_paths": r"(?:[A-Za-z]:[/\\]|~/|/|\./|\.\.)[/\\]*[\w/\\.-]*[\w/\\.-]+|[/\\]+[\w/\\.-]+",
            # 十六进制值
            "hex_values": r"\b0[xX][0-9a-fA-F]+\b",
            # 二进制值
            "binary_values": r"\b0[bB][01]+\b",
            # 文件大小单位
            "file_sizes": r"\b\d+(?:\.\d+)?\s?(?:B|KB|MB|GB|TB|PB)\b",
            # 时间单位
            "time_units": r"\b\d+(?:\.\d+)?\s?(?:ms|s|min|h|hr|day|week|month|year)s?\b",
            # 环境变量 - %VAR% 或 $VAR 格式
            "env_vars": r"(?:%[A-Za-z0-9_]+%|\$[A-Za-z0-9_]+|\$\{[A-Za-z0-9_]+\})",
            # MD5哈希
            "md5_hashes": r"\b[a-fA-F0-9]{32}\b",
            # SHA哈希
            "sha_hashes": r"\b[a-fA-F0-9]{40}\b|\b[a-fA-F0-9]{64}\b",
        }

        # 标签样式 - 使用通用的配色方案
        self._tag_styles = {
            # 注释 - 绿色
            "comments": {
                "foreground": "#008000",  # 绿色
            },
            # 字符串 - 深红色
            "strings": {
                "foreground": "#A31515",  # 深红色
            },
            # 数字 - 深蓝色
            "numbers": {
                "foreground": "#0000FF",  # 深蓝色
            },
            # 关键字 - 深蓝色
            "keywords": {
                "foreground": "#0000FF",  # 深蓝色
            },
            # 操作符 - 深灰色
            "operators": {
                "foreground": "#696969",  # 深灰色
            },
            # 函数调用 - 深棕色
            "functions": {
                "foreground": "#795E26",  # 深棕色
            },
            # 变量赋值 - 深紫色，高亮等号左边的键名
            "variables": {
                "foreground": "#800080",  # 深紫色
            },
            # URL和链接 - 蓝色加下划线
            "urls": {
                "foreground": "#0000FF",  # 蓝色
                "underline": True,  # 下划线
            },
            # 邮箱地址 - 深蓝色
            "emails": {
                "foreground": "#0000CD",  # 深蓝色
            },
            # IP地址 - 深紫色
            "ip_addresses": {
                "foreground": "#8B008B",  # 深紫色
            },
            # ISO 8601时间戳 - 深绿色
            "timestamps": {
                "foreground": "#006400",  # 深绿色
            },
            # 简单日期 - 深绿色
            "dates": {
                "foreground": "#006400",  # 深绿色
            },
            # 时间格式 - 深绿色
            "times": {
                "foreground": "#006400",  # 深绿色
            },
            # 文件路径 - 深灰色
            "file_paths": {
                "foreground": "#696969",  # 深灰色
            },
            # 十六进制值 - 棕色
            "hex_values": {
                "foreground": "#8B4513",  # 棕色
            },
            # 二进制值 - 深蓝色
            "binary_values": {
                "foreground": "#191970",  # 深蓝色
            },
            # 文件大小单位 - 深橙色
            "file_sizes": {
                "foreground": "#FF6347",  # 深橙色
            },
            # 时间单位 - 深橙色
            "time_units": {
                "foreground": "#FF6347",  # 深橙色
            },
            # 环境变量 - 深红色
            "env_vars": {
                "foreground": "#B22222",  # 深红色
            },
            # MD5哈希 - 深紫色
            "md5_hashes": {
                "foreground": "#8B008B",  # 深紫色
            },
            # SHA哈希 - 深紫色
            "sha_hashes": {
                "foreground": "#8B008B",  # 深紫色
            },
        }
