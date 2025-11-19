#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Go语言处理器

提供Go语法的识别和高亮规则，支持Go 1.21+语法特性
"""

import re
from typing import Dict, List, Any

from .base import LanguageHandler


class GoHandler(LanguageHandler):
    """
    Go语言处理器

    提供Go语法的识别和高亮规则，包括：
    - 基本语法元素（关键字、注释、字符串等）
    - Go特有语法（通道、goroutine、接口等）
    - 结构体、接口、方法定义
    - 泛型支持（Go 1.18+）
    - 类型参数和约束
    - 内置函数和常用包
    """

    # Go文件扩展名
    file_extensions = [".go"]

    @classmethod
    def get_language_name(cls) -> str:
        """
        获取语言处理器名称

        Returns:
            str: 语言处理器名称"go"
        """
        return "go"

    def _setup_language(self):
        """设置Go语言的语法规则"""
        # Go关键字 - 按功能分类组织
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

        # Go内置类型、函数和常量 - 按类别分组
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
            # 内置常量
            "true",
            "false",
            "iota",
            "nil",
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
            # 常用标准库包
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
            "net",
            "net/http",
            "encoding/json",
            "encoding/xml",
            "database/sql",
            "runtime",
            "testing",
            "errors",
            "math/rand",
            "crypto",
        ]

        # 正则表达式模式 - 优化匹配性能和准确性
        self._regex_patterns = {
            # 注释 - 单行和多行注释，优化匹配，避免贪婪匹配
            "comments": r"//.*?(?=\n)|/\*[^*]*\*+(?:[^/*][^*]*\*+)*/",
            # 字符串 - Go特有的字符串字面量，包括原始字符串和转义序列
            "strings": r"(?:\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*'|`[^`]*`)",
            # 数字 - 优化Go数字字面量匹配，包括二进制、八进制、十六进制、浮点数、虚数和下划线分隔
            "numbers": r"\b(?:0[bB][01_]+|0[oO][0-7_]+|0[xX][0-9a-fA-F_]+|\d+(?:_\d+)*(?:\.\d*(?:_\d+)*)?(?:[eE][+-]?\d+(?:_\d+)*)?[i]?)\b",
            # 关键字 - 使用单词边界确保匹配完整单词
            "keywords": r"\b(?:break|case|chan|const|continue|default|defer|else|fallthrough|for|func|go|goto|if|import|interface|map|package|range|return|select|struct|switch|type|var)\b",
            # 内置类型和函数 - 优化匹配，包括预定义常量
            "builtins": r"\b(?:bool|byte|complex64|complex128|error|float32|float64|int|int8|int16|int32|int64|rune|string|uint|uint8|uint16|uint32|uint64|uintptr|true|false|iota|nil|append|cap|close|complex|copy|delete|imag|len|make|new|panic|print|println|real|recover)\b",
            # 常用包 - 优化包名匹配，包括子包
            "packages": r"\b(?:fmt|os|io|strings|strconv|math|time|http|json|xml|regexp|bytes|bufio|filepath|log|sort|sync|context|reflect|unsafe|net|encoding|database|runtime|testing|errors|crypto)\b",
            # 函数定义 - 优化函数定义匹配，包括接收器和泛型类型参数
            "functions": r"\bfunc\s+(?:\([^)]*\)\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:\[.*?\])?\s*\(",
            # 方法调用 - 优化方法调用匹配，包括链式调用
            "method_calls": r"([a-zA-Z_][a-zA-Z0-9_]*)\s*\(",
            # 结构体字段 - 优化结构体字段匹配，包括标签
            "struct_fields": r"([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:`[^`]*`)?\s*:",
            # 接口方法 - 优化接口方法匹配，包括泛型约束
            "interface_methods": r"([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:\[.*?\])?\s*\(",
            # 结构体标签 - 优化结构体标签匹配
            "tags": r"`([^`]*)`",
            # 包导入 - 优化包导入匹配，包括别名和点导入
            "imports": r"\bimport\s+(?:\([^)]*\)|\s*(?:[a-zA-Z_][a-zA-Z0-9_]*\s+)?\"[^\"]*\")",
            # 格式化动词 - 优化格式化动词匹配，包括所有Go格式化选项
            "format_verbs": r"%[#0+\- ]*[0-9]*\.?[0-9]*[tT]?[vbcdoqxXUeEfFgGspw%]",
            # 操作符 - 优化操作符匹配，包括所有Go操作符
            "operators": r"(\+\+|--|==|!=|<=|>=|&&|\|\||<<|>>|&\^|<-|[+\-*/%&|^=<>!.,;:\[\]{}()])",
            # 类型断言 - 优化类型断言匹配，包括类型开关
            "type_assertions": r"\.\s*\([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*\)",
            # 通道操作 - 优化通道操作匹配，包括发送和接收
            "channel_ops": r"<-",
            # 泛型类型参数 - 新增泛型类型参数匹配
            "type_parameters": r"\[([a-zA-Z_][a-zA-Z0-9_]*(?:\s*,\s*[a-zA-Z_][a-zA-Z0-9_]*)*)\s*(?:[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*(?:\s*\|\s*[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)*)?\]",
            # 泛型实例化 - 新增泛型实例化匹配
            "generic_instantiation": r"([a-zA-Z_][a-zA-Z0-9_]*)\[.*?\]",
            # Goroutine - 新增goroutine关键字匹配
            "goroutines": r"\bgo\s+([a-zA-Z_][a-zA-Z0-9_]*)",
            # Select语句 - 新增select语句匹配
            "select_statements": r"\bselect\s*\{",
            # Defer语句 - 新增defer语句匹配
            "defer_statements": r"\bdefer\s+([a-zA-Z_][a-zA-Z0-9_]*)",
            # 常量定义 - 新增常量定义匹配
            "constants": r"\bconst\s+(?:\([^)]*\)|([a-zA-Z_][a-zA-Z0-9_]*))",
            # 变量定义 - 新增变量定义匹配
            "variables": r"\bvar\s+(?:\([^)]*\)|([a-zA-Z_][a-zA-Z0-9_]*))",
            # 类型定义 - 新增类型定义匹配
            "type_definitions": r"\btype\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+(?:struct|interface|func|\[.*?\]|[a-zA-Z_][a-zA-Z0-9_]*)",
            # 接口定义 - 新增接口定义匹配
            "interface_definitions": r"\btype\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+interface\s*\{",
            # 结构体定义 - 新增结构体定义匹配
            "struct_definitions": r"\btype\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+struct\s*\{",
        }

        # 标签样式 - 优化颜色方案，提高可读性和区分度，仅修改颜色
        self._tag_styles = {
            # 注释 - 绿色，使用更柔和的色调
            "comments": {
                "foreground": "#008000",  # 深绿色
            },
            # 字符串 - 深红色，保持原色
            "strings": {
                "foreground": "#A31515",  # 深红色
            },
            # 数字 - 深绿色，使用更鲜明的色调
            "numbers": {
                "foreground": "#098658",  # 深绿色
            },
            # 关键字 - 深蓝色，使用更醒目的色调
            "keywords": {
                "foreground": "#0000FF",  # 深蓝色
            },
            # 内置类型和函数 - 深青色，使用更鲜明的色调
            "builtins": {
                "foreground": "#008080",  # 深青色
            },
            # 常用包 - 紫色，使用更鲜明的色调
            "packages": {
                "foreground": "#800080",  # 紫色
            },
            # 函数定义 - 深紫色，使用更鲜明的色调
            "functions": {
                "foreground": "#795E26",  # 深棕色
            },
            # 方法调用 - 深橙色，保持原色
            "method_calls": {
                "foreground": "#FF6B35",  # 深橙色
            },
            # 结构体字段 - 深青色，使用更鲜明的色调
            "struct_fields": {
                "foreground": "#001080",  # 深蓝色
            },
            # 接口方法 - 深蓝绿色，使用更鲜明的色调
            "interface_methods": {
                "foreground": "#008B8B",  # 深蓝绿色
            },
            # 标签 - 深红色，使用更柔和的色调
            "tags": {
                "foreground": "#CE9178",  # 浅棕色
            },
            # 包导入 - 深蓝色，使用更鲜明的色调
            "imports": {
                "foreground": "#0000CD",  # 深蓝色
            },
            # 格式化动词 - 深红色，使用更鲜明的色调
            "format_verbs": {
                "foreground": "#A31515",  # 深红色
            },
            # 操作符 - 黑色，保持原色
            "operators": {
                "foreground": "#000000",  # 黑色
            },
            # 类型断言 - 深蓝色，使用更鲜明的色调
            "type_assertions": {
                "foreground": "#0000FF",  # 深蓝色
            },
            # 通道操作 - 深蓝色，使用更鲜明的色调
            "channel_ops": {
                "foreground": "#0000FF",  # 深蓝色
            },
            # 泛型类型参数 - 新增泛型类型参数样式
            "type_parameters": {
                "foreground": "#267F99",  # 深青色
            },
            # 泛型实例化 - 新增泛型实例化样式
            "generic_instantiation": {
                "foreground": "#267F99",  # 深青色
            },
            # Goroutine - 新增goroutine样式
            "goroutines": {
                "foreground": "#AF00DB",  # 紫色
            },
            # Select语句 - 新增select语句样式
            "select_statements": {
                "foreground": "#0000FF",  # 深蓝色
            },
            # Defer语句 - 新增defer语句样式
            "defer_statements": {
                "foreground": "#0000FF",  # 深蓝色
            },
            # 常量定义 - 新增常量定义样式
            "constants": {
                "foreground": "#098658",  # 深绿色
            },
            # 变量定义 - 新增变量定义样式
            "variables": {
                "foreground": "#001080",  # 深蓝色
            },
            # 类型定义 - 新增类型定义样式
            "type_definitions": {
                "foreground": "#0000FF",  # 深蓝色
            },
            # 接口定义 - 新增接口定义样式
            "interface_definitions": {
                "foreground": "#0000FF",  # 深蓝色
            },
            # 结构体定义 - 新增结构体定义样式
            "struct_definitions": {
                "foreground": "#0000FF",  # 深蓝色
            },
        }
