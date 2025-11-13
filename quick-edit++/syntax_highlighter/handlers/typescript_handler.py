#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TypeScript语言处理器

提供TypeScript语法的识别和高亮规则
"""

import re
from typing import Dict, List, Any

from .base import LanguageHandler


class TypeScriptHandler(LanguageHandler):
    """
    TypeScript语言处理器

    提供TypeScript语法的识别和高亮规则
    """

    # TypeScript文件扩展名
    file_extensions = [".ts", ".tsx"]

    def _setup_language(self):
        """设置TypeScript语言的语法规则"""
        # TypeScript关键字
        self._keywords = [
            # JavaScript关键字
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
            "var",
            "let",
            "const",
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
            "this",
            "new",
            "typeof",
            "instanceof",
            "in",
            "of",
            "true",
            "false",
            "null",
            "undefined",
            "import",
            "export",
            "from",
            "as",
            "default",
            "delete",
            "void",
            "with",
            "debugger",
            # TypeScript特有关键字
            "type",
            "interface",
            "implements",
            "private",
            "protected",
            "public",
            "readonly",
            "abstract",
            "declare",
            "enum",
            "namespace",
            "module",
            "keyof",
            "unknown",
            "never",
            "any",
            "boolean",
            "number",
            "string",
            "symbol",
            "object",
            "unique",
            "infer",
            "is",
            "asserts",
            "satisfies",
            "override",
        ]

        # TypeScript内置类型和对象
        builtins = [
            # JavaScript内置对象
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
            # TypeScript特有类型
            "Partial",
            "Required",
            "Readonly",
            "Record",
            "Pick",
            "Omit",
            "Exclude",
            "Extract",
            "NonNullable",
            "Parameters",
            "ConstructorParameters",
            "ReturnType",
            "InstanceType",
            "ThisParameterType",
            "OmitThisParameter",
            "Uppercase",
            "Lowercase",
            "Capitalize",
            "Uncapitalize",
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
            # 正则表达式 - TypeScript正则表达式
            "regex": r"/(?![*/])(?:[^/\\\n]|\\.)+/(?:[gimsuy]*)",
            # 函数定义 - 函数名后的括号或箭头函数
            "functions": r"\b([a-zA-Z_$][a-zA-Z0-9_$]*)\s*(?=\s*\()|\b([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*(?:function|\([^)]*\)\s*=>)|\b(?:function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)|class\s+([a-zA-Z_$][a-zA-Z0-9_$]*)|interface\s+([a-zA-Z_$][a-zA-Z0-9_$]*)|type\s+([a-zA-Z_$][a-zA-Z0-9_$]*))",
            # 变量 - 变量名
            "variables": r"\b[a-zA-Z_$][a-zA-Z0-9_$]*\b",
            # 操作符
            "operators": r"(\+|\-|\*|\/|%|\*\*|=|==|===|!=|!==|<|>|<=|>=|\+\+|\-\-|<<|>>|>>>|&|\||\^|!|&&|\|\||\?|:|\(|\)|\{|\}|\[|\]|\.|,|;)",
            # 模板字符串变量 - ${variable}
            "template_variables": r"\$\{[^}]*\}",
            # TSX标签 - 如果是TSX文件
            "tsx_tags": r"<[a-zA-Z][a-zA-Z0-9]*(?:\s+[a-zA-Z][a-zA-Z0-9]*(?:\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^'\">\s]+))?)*\s*/?>|</[a-zA-Z][a-zA-Z0-9]*\s*>",
            # 类型注解 - 冒号后的类型
            "type_annotations": r":\s*([a-zA-Z_$][a-zA-Z0-9_$]*(?:\[\])?|\{[^}]*\}|(?:\([^)]*\)|[^=,)]+|\s+)*=>\s*[^=,)]+)",
            # 装饰器 - @decorator
            "decorators": r"@[a-zA-Z_$][a-zA-Z0-9_$]*",
            # 泛型 - <T>
            "generics": r"<[a-zA-Z_$][a-zA-Z0-9_$]*(?:\s+extends\s+[^>]+)?>",
        }

        # 标签样式 - 使用适合TypeScript的配色方案
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
            # TSX标签 - 深绿色
            "tsx_tags": {
                "foreground": "#008000",
            },
            # 类型注解 - 深蓝色
            "type_annotations": {
                "foreground": "#000080",
            },
            # 装饰器 - 深橙色
            "decorators": {
                "foreground": "#FF8C00",
            },
            # 泛型 - 深青色
            "generics": {
                "foreground": "#008B8B",
            },
        }