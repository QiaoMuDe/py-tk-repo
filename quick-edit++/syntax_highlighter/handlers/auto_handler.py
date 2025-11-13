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
    """

    # 支持所有文件扩展名，作为默认处理器
    file_extensions = ["*"]

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
            # 注释 - 支持多种常见注释格式
            "comments": r"(?://.*?$|/\*[\s\S]*?\*/|#.*?$|<!--[\s\S]*?-->)",
            # 字符串 - 支持多种常见字符串格式
            "strings": r"(?:\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*'|`[^`]*`)",
            # 数字 - 支持常见数字格式
            "numbers": r"\b(?:0[bB][01]+|0[oO][0-7]+|0[xX][0-9a-fA-F]+|\d+(?:\.\d*)?(?:[eE][+-]?\d+)?)\b",
            # 常见关键字
            "keywords": r"\b(?:if|else|elif|for|while|do|switch|case|default|break|continue|return|goto|pass|yield|function|func|def|class|interface|struct|type|var|let|const|static|final|volatile|public|private|protected|internal|abstract|virtual|int|float|double|char|string|bool|boolean|void|null|true|false|yes|no|on|off|import|include|require|package|module|namespace|using|try|catch|finally|throw|throws|raise|except|new|delete|this|self|super|base|async|await|sync|lock|thread|parallel|in|out|ref|by|of|to|from|as|is)\b",
            # 常见操作符
            "operators": r"(\+\+|--|==|!=|<=|>=|&&|\|\||<<|>>|&\^|<-|[+\-*/%&|^=<>!.,;:\[\]{}()])",
            # 常见函数调用
            "functions": r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(",
            # 常见变量赋值
            "variables": r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*=",
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
        }
