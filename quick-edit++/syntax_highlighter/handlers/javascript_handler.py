#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JavaScript语言处理器

提供JavaScript语法的识别和高亮规则
"""

import re
from typing import Dict, List, Any

from .base import LanguageHandler


class JavaScriptHandler(LanguageHandler):
    """
    JavaScript语言处理器

    提供JavaScript语法的识别和高亮规则
    """

    # JavaScript文件扩展名
    file_extensions = [".js", ".jsx", ".mjs", ".cjs"]

    @classmethod
    def get_language_name(cls) -> str:
        """
        获取语言处理器名称

        Returns:
            str: 语言处理器名称"javascript"
        """
        return "javascript"

    def _setup_language(self):
        """
        设置JavaScript语言的语法规则
        """
        # 定义模式处理顺序，确保字符串和注释有正确的优先级
        self._pattern_order = [
            "strings",  # 字符串放在第一位，确保优先匹配
            "comments",  # 注释放在第二位
            "regex",  # 正则表达式放在第三位
            "template_variables",  # 模板变量
            "keywords",  # 关键字
            "builtins",  # 内置对象和函数
            "numbers",  # 数字
            "functions",  # 函数定义
            "variables",  # 变量
            "operators",  # 操作符
            "jsx_tags",  # JSX标签
            "decorators",  # 装饰器
        ]
        # JavaScript关键字
        self._keywords = [
            # 控制流关键字
            "if",
            "else",
            "for",
            "while",
            "do",
            "switch",
            "case",
            "default",
            "break",
            "continue",
            "return",
            "throw",
            "try",
            "catch",
            "finally",
            # 变量声明
            "var",
            "let",
            "const",
            # 函数相关
            "function",
            "async",
            "await",
            "yield",
            "class",
            "extends",
            "super",
            "constructor",
            "static",
            "get",
            "set",
            # 对象相关
            "this",
            "new",
            "typeof",
            "instanceof",
            "in",
            "of",
            # 逻辑关键字
            "true",
            "false",
            "null",
            "undefined",
            # 模块相关
            "import",
            "export",
            "from",
            "as",
            "default",
            # 其他关键字
            "delete",
            "void",
            "with",
            "debugger",
        ]

        # JavaScript内置对象和函数
        builtins = [
            # 全局对象
            "Object",
            "Function",
            "Boolean",
            "Symbol",
            "Error",
            "EvalError",
            "InternalError",
            "RangeError",
            "ReferenceError",
            "SyntaxError",
            "TypeError",
            "URIError",
            "Number",
            "Math",
            "Date",
            "String",
            "RegExp",
            "Array",
            "Int8Array",
            "Uint8Array",
            "Uint8ClampedArray",
            "Int16Array",
            "Uint16Array",
            "Int32Array",
            "Uint32Array",
            "Float32Array",
            "Float64Array",
            "Map",
            "Set",
            "WeakMap",
            "WeakSet",
            "ArrayBuffer",
            "SharedArrayBuffer",
            "Atomics",
            "DataView",
            "JSON",
            "Promise",
            "Generator",
            "GeneratorFunction",
            "AsyncFunction",
            "Reflect",
            "Proxy",
            # 全局函数
            "eval",
            "isFinite",
            "isNaN",
            "parseFloat",
            "parseInt",
            "decodeURI",
            "decodeURIComponent",
            "encodeURI",
            "encodeURIComponent",
            "escape",
            "unescape",
            # 常用方法
            "console",
            "alert",
            "confirm",
            "prompt",
            "setTimeout",
            "clearTimeout",
            "setInterval",
            "clearInterval",
            "requestAnimationFrame",
            "cancelAnimationFrame",
        ]

        # 正则表达式模式
        self._regex_patterns = {
            # 关键字 - 使用单词边界确保匹配完整单词
            "keywords": r"\b("
            + "|".join(re.escape(k) for k in self._keywords)
            + r")\b",
            # 内置对象和函数
            "builtins": r"\b(" + "|".join(re.escape(b) for b in builtins) + r")\b",
            # 注释 - 单行和多行注释
            "comments": r"//.*$|/\*[\s\S]*?\*/",
            # 字符串 - 包括单引号、双引号、模板字符串
            "strings": r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'|`(?:[^`\\]|\\.)*`)',
            # 数字 - 包括整数、浮点数、科学计数法、二进制、八进制、十六进制
            "numbers": r"\b(?:0[bB][01]+|0[oO][0-7]+|0[xX][0-9a-fA-F]+|\d+(?:\.\d*)?(?:[eE][+-]?\d+)?)\b",
            # 正则表达式 - JavaScript正则表达式
            "regex": r"/(?![*/])(?:[^/\\\n]|\\.)+/(?:[gimsuy]*)",
            # 函数定义 - 函数名后的括号或箭头函数
            "functions": r"\b([a-zA-Z_$][a-zA-Z0-9_$]*)\s*(?=\s*\()|\b([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*(?:function|\([^)]*\)\s*=>)|\b(?:function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)|class\s+([a-zA-Z_$][a-zA-Z0-9_$]*))",
            # 变量 - 变量名
            "variables": r"\b[a-zA-Z_$][a-zA-Z0-9_$]*\b",
            # 操作符
            "operators": r"(\+|\-|\*|\/|%|\*\*|=|==|===|!=|!==|<|>|<=|>=|\+\+|\-\-|<<|>>|>>>|&|\||\^|!|&&|\|\||\?|:|\(|\)|\{|\}|\[|\]|\.|,|;)",
            # 模板字符串变量 - ${variable}
            "template_variables": r"\$\{[^}]*\}",
            # JSX标签 - 如果是JSX文件
            "jsx_tags": r"<[a-zA-Z][a-zA-Z0-9]*(?:\s+[a-zA-Z][a-zA-Z0-9]*(?:\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^'\">\s]+))?)*\s*/?>|</[a-zA-Z][a-zA-Z0-9]*\s*>",
            # 装饰器 - @decorator
            "decorators": r"@[a-zA-Z_$][a-zA-Z0-9_$]*",
        }

        # 标签样式 - 使用适合JavaScript语言的配色方案
        self._tag_styles = {
            # 关键字 - 深蓝色
            "keywords": {
                "foreground": "#000080",
            },
            # 内置对象和函数 - 蓝色
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
            # 正则表达式 - 深紫色
            "regex": {
                "foreground": "#4B0082",
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
            # 模板字符串变量 - 深青色
            "template_variables": {
                "foreground": "#008B8B",
            },
            # JSX标签 - 深绿色
            "jsx_tags": {
                "foreground": "#008000",
            },
            # 装饰器 - 深橙色
            "decorators": {
                "foreground": "#FF8C00",
            },
        }

    def get_pattern_order(self) -> List[str]:
        """
        获取模式处理顺序

        Returns:
            List[str]: 模式处理顺序列表，确保字符串和注释有正确的优先级
        """
        return self._pattern_order
