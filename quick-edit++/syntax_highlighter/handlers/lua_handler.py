#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Lua脚本处理器

提供.lua文件的语法高亮支持
"""

import re
from typing import Dict, List, Any

from .base import LanguageHandler


class LuaHandler(LanguageHandler):
    """
    Lua脚本语言处理器

    提供.lua文件的语法高亮支持
    """

    # Lua文件扩展名
    file_extensions = [
        ".lua",
        ".luac",
        ".wlua",
    ]  # .luac是编译后的Lua文件，.wlua是Windows Lua脚本

    @classmethod
    def get_language_name(cls) -> str:
        """
        获取语言处理器名称

        Returns:
            str: 语言处理器名称"lua"
        """
        return "lua"

    def _setup_language(self):
        """
        设置Lua脚本的语法高亮规则
        """
        # 定义模式处理顺序，确保字符串和注释有正确的优先级
        self._pattern_order = [
            "string",  # 字符串放在第一位，确保优先匹配
            "multiline_string",  # 多行字符串放在第二位
            "comment",  # 单行注释放在第三位
            "multiline_comment",  # 多行注释放在第四位
            "number",  # 数字
            "hex_number",  # 十六进制数字
            "boolean",  # 布尔值
            "nil",  # nil值
            "function_def",  # 函数定义
            "function_call",  # 函数调用
            "property_access",  # 属性访问
            "table_def",  # 表定义
            "local_var",  # 局部变量
            "global_var",  # 全局变量
            "operator",  # 操作符
            "label",  # 标签
            "goto",  # goto
            "vararg",  # 变长参数
        ]
        # Lua关键字
        self._keywords = [
            # 基本关键字
            "and",
            "break",
            "do",
            "else",
            "elseif",
            "end",
            "false",
            "for",
            "function",
            "goto",
            "if",
            "in",
            "local",
            "nil",
            "not",
            "or",
            "repeat",
            "return",
            "then",
            "true",
            "until",
            "while",
            # 元方法关键字
            "__add",
            "__sub",
            "__mul",
            "__div",
            "__mod",
            "__pow",
            "__unm",
            "__idiv",
            "__band",
            "__bor",
            "__bxor",
            "__bnot",
            "__shl",
            "__shr",
            "__concat",
            "__len",
            "__eq",
            "__lt",
            "__le",
            "__index",
            "__newindex",
            "__call",
            "__tostring",
            "__pairs",
            "__ipairs",
            "__gc",
            "__mode",
            "__name",
        ]

        # Lua内置函数和库
        self._builtins = [
            # 基本函数
            "assert",
            "collectgarbage",
            "dofile",
            "error",
            "getmetatable",
            "ipairs",
            "load",
            "loadfile",
            "next",
            "pairs",
            "pcall",
            "print",
            "rawequal",
            "rawget",
            "rawlen",
            "rawset",
            "select",
            "setmetatable",
            "tonumber",
            "tostring",
            "type",
            "xpcall",
            # 字符串库
            "string.byte",
            "string.char",
            "string.dump",
            "string.find",
            "string.format",
            "string.gmatch",
            "string.gsub",
            "string.len",
            "string.lower",
            "string.match",
            "string.rep",
            "string.reverse",
            "string.sub",
            "string.upper",
            # 表库
            "table.concat",
            "table.insert",
            "table.maxn",
            "table.pack",
            "table.remove",
            "table.sort",
            "table.unpack",
            # 数学库
            "math.abs",
            "math.acos",
            "math.asin",
            "math.atan",
            "math.ceil",
            "math.cos",
            "math.deg",
            "math.exp",
            "math.floor",
            "math.fmod",
            "math.huge",
            "math.log",
            "math.max",
            "math.maxinteger",
            "math.min",
            "math.mininteger",
            "math.modf",
            "math.pi",
            "math.rad",
            "math.random",
            "math.randomseed",
            "math.sin",
            "math.sqrt",
            "math.tan",
            "math.tointeger",
            "math.type",
            "math.ult",
            # IO库
            "io.close",
            "io.flush",
            "io.input",
            "io.lines",
            "io.open",
            "io.output",
            "io.popen",
            "io.read",
            "io.tmpfile",
            "io.type",
            "io.write",
            # 操作系统库
            "os.clock",
            "os.date",
            "os.difftime",
            "os.execute",
            "os.exit",
            "os.getenv",
            "os.remove",
            "os.rename",
            "os.setlocale",
            "os.time",
            "os.tmpname",
            # 调试库
            "debug.debug",
            "debug.gethook",
            "debug.getinfo",
            "debug.getlocal",
            "debug.getmetatable",
            "debug.getregistry",
            "debug.getupvalue",
            "debug.sethook",
            "debug.setlocal",
            "debug.setmetatable",
            "debug.setupvalue",
            "debug.traceback",
            # UTF-8库
            "utf8.char",
            "utf8.codepoint",
            "utf8.codes",
            "utf8.len",
            "utf8.offset",
            # 协程库
            "coroutine.create",
            "coroutine.isyieldable",
            "coroutine.resume",
            "coroutine.running",
            "coroutine.status",
            "coroutine.wrap",
            "coroutine.yield",
        ]

        # Lua操作符 - 按类型分类组织
        self._operators = [
            # 算术操作符
            "+",
            "-",
            "*",
            "/",
            "%",
            "^",
            "#",
            # 比较操作符
            "==",
            "~=",
            "<",
            ">",
            "<=",
            ">=",
            # 逻辑操作符
            "and",
            "or",
            "not",
            # 连接操作符
            "..",
            # 赋值操作符
            "=",
            # 分隔符
            "(",
            ")",
            "{",
            "}",
            "[",
            "]",
            ";",
            ",",
            # 其他操作符
            ":",
            ".",
        ]

        # 正则表达式模式
        self._regex_patterns = {
            # 注释
            "comment": r"--.*$",
            # 多行注释
            "multiline_comment": r"--\[\[.*?\]\]",
            # 字符串
            "string": r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'',
            # 多行字符串
            "multiline_string": r"\[\[.*?\]\]",
            # 数字
            "number": r"\b\d+\.?\d*([eE][+-]?\d+)?\b",
            # 十六进制数字
            "hex_number": r"0[xX][0-9a-fA-F]+\.?[0-9a-fA-F]*([pP][+-]?\d+)?\b",
            # 布尔值
            "boolean": r"\b(true|false)\b",
            # nil值
            "nil": r"\bnil\b",
            # 函数定义
            "function_def": r"\bfunction\s+([a-zA-Z_][a-zA-Z0-9_]*\s*[:.]\s*)?[a-zA-Z_][a-zA-Z0-9_]*\s*\(",
            # 函数调用
            "function_call": r"\b[a-zA-Z_][a-zA-Z0-9_]*\s*\(",
            # 属性访问
            "property_access": r"[a-zA-Z_][a-zA-Z0-9_]*\s*[.:]\s*[a-zA-Z_][a-zA-Z0-9_]*",
            # 表定义
            "table_def": r"\{.*?\}",
            # 局部变量声明
            "local_var": r"\blocal\s+[a-zA-Z_][a-zA-Z0-9_]*\b",
            # 全局变量
            "global_var": r"\b[a-zA-Z_][a-zA-Z0-9_]*\b",
            # 操作符 - 使用属性数组并转义展开
            "operator": r"(" + "|".join(re.escape(op) for op in self._operators) + r")",
            # 标签和goto
            "label": r"::[a-zA-Z_][a-zA-Z0-9_]*::",
            "goto": r"\bgoto\s+[a-zA-Z_][a-zA-Z0-9_]*\b",
            # 变长参数
            "vararg": r"\.\.\.",
        }

        # 标签样式 - 使用适合Lua脚本的深色配色方案
        self._tag_styles = {
            "comment": {
                "foreground": "#008000",
            },  # 深绿色用于单行注释
            "multiline_comment": {
                "foreground": "#008000",
            },  # 深绿色用于多行注释
            "string": {"foreground": "#A31515"},  # 深红色用于字符串
            "multiline_string": {"foreground": "#A31515"},  # 深红色用于多行字符串
            "number": {"foreground": "#098658"},  # 深绿色用于数字
            "hex_number": {"foreground": "#098658"},  # 深绿色用于十六进制数字
            "boolean": {"foreground": "#0000FF"},  # 纯蓝色用于布尔值
            "nil": {"foreground": "#0000FF"},  # 纯蓝色用于nil值
            "function_def": {
                "foreground": "#795E26",
            },  # 深棕色用于函数定义
            "function_call": {"foreground": "#795E26"},  # 深棕色用于函数调用
            "property_access": {"foreground": "#001080"},  # 深蓝色用于属性访问
            "table_def": {"foreground": "#333333"},  # 深灰色用于表定义
            "local_var": {"foreground": "#800080"},  # 深紫色用于局部变量
            "global_var": {"foreground": "#001080"},  # 深蓝色用于全局变量
            "operator": {"foreground": "#808080"},  # 灰色用于操作符
            "label": {"foreground": "#CC6600"},  # 深橙色用于标签
            "goto": {"foreground": "#CC6600"},  # 深橙色用于goto
            "vararg": {"foreground": "#CC6600"},  # 深橙色用于变长参数
        }

    def get_pattern_order(self) -> List[str]:
        """
        获取模式处理顺序

        Returns:
            List[str]: 模式处理顺序列表，确保字符串和注释有正确的优先级
        """
        return self._pattern_order
