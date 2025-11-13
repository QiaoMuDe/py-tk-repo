#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Go语言处理器

提供Go语法的识别和高亮规则
"""

import re
from typing import Dict, List, Any

from .base import LanguageHandler


class GoHandler(LanguageHandler):
    """
    Go语言处理器

    提供Go语法的识别和高亮规则
    """

    # Go文件扩展名
    file_extensions = [".go"]

    def _setup_language(self):
        """设置Go语言的语法规则"""
        # Go关键字
        self._keywords = [
            # 控制流关键字
            "break",
            "case",
            "continue",
            "default",
            "defer",
            "else",
            "fallthrough",
            "for",
            "go",
            "goto",
            "if",
            "range",
            "return",
            "select",
            "switch",
            # 类型声明
            "chan",
            "const",
            "func",
            "interface",
            "map",
            "struct",
            "type",
            "var",
            # 其他关键字
            "import",
            "package",
        ]

        # Go内置类型和函数
        builtins = [
            # 内置类型
            "bool",
            "byte",
            "complex64",
            "complex128",
            "error",
            "float32",
            "float64",
            "int",
            "int8",
            "int16",
            "int32",
            "int64",
            "rune",
            "string",
            "uint",
            "uint8",
            "uint16",
            "uint32",
            "uint64",
            "uintptr",
            # 内置函数
            "append",
            "cap",
            "close",
            "complex",
            "copy",
            "delete",
            "imag",
            "len",
            "make",
            "new",
            "panic",
            "print",
            "println",
            "real",
            "recover",
            # 常用包
            "fmt",
            "os",
            "io",
            "strings",
            "strconv",
            "math",
            "time",
            "http",
            "json",
            "xml",
            "regexp",
            "bytes",
            "bufio",
            "filepath",
            "log",
            "sort",
            "sync",
            "context",
            "reflect",
            "unsafe",
        ]

        # 正则表达式模式
        self._regex_patterns = {
            # 注释 - 单行和多行注释，优化匹配
            "comments": r"//.*?(?=\n)|/\*[^*]*\*+(?:[^/*][^*]*\*+)*/",
            # 字符串 - Go特有的字符串字面量，包括原始字符串
            "strings": r"(?:\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*'|`[^`]*`)",
            # 数字 - 优化Go数字字面量匹配，包括虚数
            "numbers": r"\b(?:0[bB][01_]+|0[oO][0-7_]+|0[xX][0-9a-fA-F_]+|\d+(?:_\d+)*(?:\.\d*(?:_\d+)*)?(?:[eE][+-]?\d+(?:_\d+)*)?[i]?)\b",
            # 关键字 - 使用单词边界确保匹配完整单词
            "keywords": r"\b(?:break|case|chan|const|continue|default|defer|else|fallthrough|for|func|go|goto|if|import|interface|map|package|range|return|select|struct|switch|type|var)\b",
            # 内置类型和函数 - 优化匹配
            "builtins": r"\b(?:bool|byte|complex64|complex128|error|float32|float64|int|int8|int16|int32|int64|rune|string|uint|uint8|uint16|uint32|uint64|uintptr|true|false|iota|nil|append|cap|close|complex|copy|delete|imag|len|make|new|panic|print|println|real|recover)\b",
            # 常用包 - 优化包名匹配
            "packages": r"\b(?:fmt|os|io|strings|strconv|math|time|http|json|xml|regexp|bytes|bufio|filepath|log|sort|sync|context|reflect|unsafe)\b",
            # 函数定义 - 优化函数定义匹配，包括接收器
            "functions": r"\bfunc\s+(?:\([^)]*\)\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*\(",
            # 方法调用 - 优化方法调用匹配
            "method_calls": r"([a-zA-Z_][a-zA-Z0-9_]*)\s*\(",
            # 结构体字段 - 优化结构体字段匹配
            "struct_fields": r"([a-zA-Z_][a-zA-Z0-9_]*)\s*:",
            # 接口方法 - 优化接口方法匹配
            "interface_methods": r"([a-zA-Z_][a-zA-Z0-9_]*)\s*\(",
            # 标签 - 优化结构体标签匹配
            "tags": r"`([^`]*)`",
            # 包导入 - 修复可变长度后向查找问题
            "imports": r"\bimport\s+(?:\"[^\"]*\"|\([^)]*\))",
            # 格式化动词 - 优化格式化动词匹配
            "format_verbs": r"%[#0+-]*[0-9]*\.?[0-9]*[tT]?[vbcdoqxXUeEfFgGspw%]",
            # 操作符 - 优化操作符匹配
            "operators": r"(\+\+|--|==|!=|<=|>=|&&|\|\||<<|>>|&\^|<-|[+\-*/%&|^=<>!.,;:\[\]{}()])",
            # 类型断言 - 优化类型断言匹配
            "type_assertions": r"\.\s*\([a-zA-Z_][a-zA-Z0-9_]*\)",
            # 通道操作 - 优化通道操作匹配
            "channel_ops": r"<-",
        }

        # 标签样式 - 使用更适合浅色模式的深色系配色
        self._tag_styles = {
            # 注释 - 绿色
            "comments": {
                "foreground": "#00c400",  # 绿色
            },
            # 字符串 - 深红色
            "strings": {
                "foreground": "#A31515",  # 深红色
            },
            # 数字 - 深绿色
            "numbers": {
                "foreground": "#098658",  # 深绿色
            },
            # 关键字 - 深蓝色
            "keywords": {
                "foreground": "#0000FF",  # 深蓝色
            },
            # 内置类型和函数 - 深青色
            "builtins": {
                "foreground": "#008080",  # 深青色
            },
            # 常用包 - 紫色
            "packages": {
                "foreground": "#800080",  # 紫色
            },
            # 函数定义 - 深紫色
            "functions": {
                "foreground": "#800080",  # 深紫色
            },
            # 方法调用 - 深橙色
            "method_calls": {
                "foreground": "#FF6B35",  # 深橙色
            },
            # 结构体字段 - 深青色
            "struct_fields": {
                "foreground": "#008080",  # 深青色
            },
            # 接口方法 - 深蓝绿色
            "interface_methods": {
                "foreground": "#008B8B",  # 深蓝绿色
            },
            # 标签 - 深红色
            "tags": {
                "foreground": "#A31515",  # 深红色
            },
            # 包导入 - 深蓝色
            "imports": {
                "foreground": "#0000CD",  # 深蓝色
            },
            # 格式化动词 - 深红色
            "format_verbs": {
                "foreground": "#A31515",  # 深红色
            },
            # 操作符 - 黑色
            "operators": {
                "foreground": "#000000",  # 黑色
            },
            # 类型断言 - 深蓝色
            "type_assertions": {
                "foreground": "#0000FF",  # 深蓝色
            },
            # 通道操作 - 深蓝色
            "channel_ops": {
                "foreground": "#0000FF",  # 深蓝色
            },
        }
