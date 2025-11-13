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
            # 关键字 - 使用单词边界确保匹配完整单词
            "keywords": r"\b("
            + "|".join(re.escape(k) for k in self._keywords)
            + r")\b",
            # 内置类型和函数
            "builtins": r"\b(" + "|".join(re.escape(b) for b in builtins) + r")\b",
            # 注释 - 单行和多行注释
            "comments": r"//.*$|/\*[\s\S]*?\*/",
            # 字符串 - 包括单引号、双引号、反引号
            "strings": r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'|`(?:[^`\\]|\\.)*`)',
            # 数字 - 包括整数、浮点数、科学计数法、十六进制、八进制、二进制
            "numbers": r"\b(?:0[bB][01]+|0[oO][0-7]+|0[xX][0-9a-fA-F]+|\d+(?:\.\d*)?(?:[eE][+-]?\d+)?)\b",
            # 函数定义 - func关键字后的函数名
            "functions": r"\bfunc\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(",
            # 变量 - 变量名
            "variables": r"\b[a-zA-Z_][a-zA-Z0-9_]*\b",
            # 操作符
            "operators": r"(\+|\-|\*|\/|%|&|\||\^|<<|>>|&\^|=|==|!=|<|>|<=|>=|&&|\|\||!|\+\+|\-\-|<-|\(|\)|\{|\}|\[|\]|\.|,|;|:)",
            # 结构体字段 - 结构体中的字段名
            "struct_fields": r"[a-zA-Z_][a-zA-Z0-9_]*\s*:",
            # 接口方法 - 接口中的方法名
            "interface_methods": r"[a-zA-Z_][a-zA-Z0-9_]*\s*\(",
            # 标签 - 结构体字段后的标签
            "tags": r"`[^`]*`",
            # 包导入 - import语句中的包名
            "imports": r"import\s+\"[^\"]*\"|import\s*\([^)]*\)",
            # 格式化动词 - fmt.Printf等函数中的格式化动词
            "format_verbs": r"%[+#-0]*[0-9]*\.?[0-9]*[vTtbcdoqxXUeEfFgGsSp%]",
        }

        # 标签样式 - 使用适合Go的配色方案
        self._tag_styles = {
            # 关键字 - 深蓝色
            "keywords": {
                "foreground": "#000080",
            },
            # 内置类型和函数 - 蓝色
            "builtins": {
                "foreground": "#0000FF",
            },
            # 注释 - 绿色
            "comments": {
                "foreground": "#00AA00",
            },
            # 字符串 - 棕色
            "strings": {
                "foreground": "#8B4513",
            },
            # 数字 - 深红色
            "numbers": {
                "foreground": "#8B0000",
            },
            # 函数 - 紫色
            "functions": {
                "foreground": "#800080",
            },
            # 变量 - 黑色
            "variables": {
                "foreground": "#000000",
            },
            # 操作符 - 黑色
            "operators": {
                "foreground": "#000000",
            },
            # 结构体字段 - 深绿色
            "struct_fields": {
                "foreground": "#008000",
            },
            # 接口方法 - 深青色
            "interface_methods": {
                "foreground": "#008B8B",
            },
            # 标签 - 深橙色
            "tags": {
                "foreground": "#FF8C00",
            },
            # 包导入 - 深紫色
            "imports": {
                "foreground": "#4B0082",
            },
            # 格式化动词 - 深红色
            "format_verbs": {
                "foreground": "#8B0000",
            },
        }