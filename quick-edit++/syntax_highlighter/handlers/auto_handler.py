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
    - MAC地址识别
    - ISO 8601时间戳识别
    - 简单日期格式识别
    - 时间格式识别
    - 文件路径识别
    - URL参数识别
    - 十六进制和二进制值识别
    - 语义化版本号识别
    - Git提交哈希识别
    - UUID识别
    - 文件大小单位识别
    - 时间单位识别
    - 环境变量识别
    - 日志级别识别
    - 颜色代码识别
    - 箭头符号识别
    - 数学符号识别
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

    def _setup_language(self):
        """设置通用语言的语法规则"""
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
            # 常见变量赋值 - 支持键名中包含连字符和点号
            "variables": r"\b([a-zA-Z_][a-zA-Z0-9_.-]*)\s*=",
            # 键值对格式 - 支持 key=value 格式，特别关注配置文件中的键值对
            "key_value_pairs": r"^(\s*)([a-zA-Z_][a-zA-Z0-9_.-]*)(\s*=\s*)([^#\n]+)",
            # URL和链接
            "urls": r"\b(?:https?://|ftp://|file://|www\.)[^\s<>\"]+",
            # 邮箱地址
            "emails": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            # IP地址
            "ip_addresses": r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",
            # MAC地址
            "mac_addresses": r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b",
            # ISO 8601时间戳
            "timestamps": r"\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?\b",
            # 简单日期格式
            "dates": r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b",
            # 时间格式
            "times": r"\b\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?\b",
            # 文件路径 - Windows和Unix格式
            "file_paths": r"(?:[A-Za-z]:[/\\]|~/|/)[\w/\\.-]*[\w/\\.-]*[\w/\\.-]+",
            # URL参数（键值对）
            "url_params": r"[?&][\w-]+=[\w%.-]+",
            # 十六进制值
            "hex_values": r"\b0[xX][0-9a-fA-F]+\b",
            # 二进制值
            "binary_values": r"\b0[bB][01]+\b",
            # 语义化版本号
            "versions": r"\b\d+\.\d+\.\d+(?:-[a-zA-Z0-9]+)?\b",
            # Git提交哈希
            "git_hashes": r"\b[0-9a-fA-F]{7,40}\b",
            # UUID格式
            "uuids": r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b",
            # 文件大小单位
            "file_sizes": r"\b\d+(?:\.\d+)?\s?(?:B|KB|MB|GB|TB|PB)\b",
            # 时间单位
            "time_units": r"\b\d+(?:\.\d+)?\s?(?:ms|s|min|h|hr|day|week|month|year)s?\b",
            # 环境变量 - %VAR% 或 $VAR 格式
            "env_vars": r"(?:%[A-Za-z0-9_]+%|\$[A-Za-z0-9_]+|\$\{[A-Za-z0-9_]+\})",
            # 错误级别 - ERROR, WARN, INFO, DEBUG等
            "log_levels": r"\b(?:TRACE|DEBUG|INFO|NOTICE|WARN|WARNING|ERROR|FATAL|CRITICAL)\b",
            # 颜色代码 - #RRGGBB或#RGB格式
            "color_codes": r"#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?\b",
            # 箭头符号
            "arrows": r"→|←|↔|↑|↓|=>|<=|<->",
            # 数学符号
            "math_symbols": r"±|×|÷|≠|≤|≥|≈|∞|∑|∏|∫",
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
            # 操作符 - 黑色
            "operators": {
                "foreground": "#000000",  # 黑色
            },
            # 函数调用 - 深棕色
            "functions": {
                "foreground": "#795E26",  # 深棕色
            },
            # 变量赋值 - 深青色
            "variables": {
                "foreground": "#008080",  # 深青色
            },
            # 键值对 - 键名使用深紫色，等号使用黑色，值使用深蓝色
            "key_value_pairs": {
                "foreground": "#800080",  # 深紫色（用于键名）
            },
            # URL和链接 - 蓝色加下划线
            "urls": {
                "foreground": "#0000FF",  # 蓝色
                "underline": True,  # 下划线
            },
            # URL参数 - 深蓝色
            "url_params": {
                "foreground": "#0000CD",  # 深蓝色
            },
            # 邮箱地址 - 深蓝色
            "emails": {
                "foreground": "#0000CD",  # 深蓝色
            },
            # IP地址 - 深紫色
            "ip_addresses": {
                "foreground": "#8B008B",  # 深紫色
            },
            # MAC地址 - 深紫色
            "mac_addresses": {
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
            # 语义化版本号 - 橙色
            "versions": {
                "foreground": "#FF8C00",  # 橙色
            },
            # Git提交哈希 - 深紫色
            "git_hashes": {
                "foreground": "#8B008B",  # 深紫色
            },
            # UUID - 深灰色
            "uuids": {
                "foreground": "#2F4F4F",  # 深灰色
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
            # 日志级别 - 红色系，根据级别区分
            "log_levels": {
                "foreground": "#DC143C",  # 深红色
            },
            # 颜色代码 - 对应的颜色
            "color_codes": {
                "foreground": "#FF00FF",  # 紫色
            },
            # 箭头符号 - 深蓝色
            "arrows": {
                "foreground": "#000080",  # 深蓝色
            },
            # 数学符号 - 深紫色
            "math_symbols": {
                "foreground": "#800080",  # 深紫色
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
