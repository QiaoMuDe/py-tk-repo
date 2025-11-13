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
    file_extensions = [".lua", ".luac", ".wlua"]  # .luac是编译后的Lua文件，.wlua是Windows Lua脚本
    
    def _setup_language(self):
        """
        设置Lua脚本的语法高亮规则
        """
        # Lua关键字
        self._keywords = [
            # 基本关键字
            "and", "break", "do", "else", "elseif", "end", "false", "for", "function", 
            "goto", "if", "in", "local", "nil", "not", "or", "repeat", "return", "then", 
            "true", "until", "while",
            
            # 元方法关键字
            "__add", "__sub", "__mul", "__div", "__mod", "__pow", "__unm", "__idiv",
            "__band", "__bor", "__bxor", "__bnot", "__shl", "__shr", "__concat", "__len",
            "__eq", "__lt", "__le", "__index", "__newindex", "__call", "__tostring",
            "__pairs", "__ipairs", "__gc", "__mode", "__name"
        ]
        
        # Lua内置函数和库
        self._builtins = [
            # 基本函数
            "assert", "collectgarbage", "dofile", "error", "getmetatable", "ipairs", "load",
            "loadfile", "next", "pairs", "pcall", "print", "rawequal", "rawget", "rawlen",
            "rawset", "select", "setmetatable", "tonumber", "tostring", "type", "xpcall",
            
            # 字符串库
            "string.byte", "string.char", "string.dump", "string.find", "string.format",
            "string.gmatch", "string.gsub", "string.len", "string.lower", "string.match",
            "string.rep", "string.reverse", "string.sub", "string.upper",
            
            # 表库
            "table.concat", "table.insert", "table.maxn", "table.pack", "table.remove",
            "table.sort", "table.unpack",
            
            # 数学库
            "math.abs", "math.acos", "math.asin", "math.atan", "math.ceil", "math.cos",
            "math.deg", "math.exp", "math.floor", "math.fmod", "math.huge", "math.log",
            "math.max", "math.maxinteger", "math.min", "math.mininteger", "math.modf",
            "math.pi", "math.rad", "math.random", "math.randomseed", "math.sin", "math.sqrt",
            "math.tan", "math.tointeger", "math.type", "math.ult",
            
            # IO库
            "io.close", "io.flush", "io.input", "io.lines", "io.open", "io.output", "io.popen",
            "io.read", "io.tmpfile", "io.type", "io.write",
            
            # 操作系统库
            "os.clock", "os.date", "os.difftime", "os.execute", "os.exit", "os.getenv",
            "os.remove", "os.rename", "os.setlocale", "os.time", "os.tmpname",
            
            # 调试库
            "debug.debug", "debug.gethook", "debug.getinfo", "debug.getlocal",
            "debug.getmetatable", "debug.getregistry", "debug.getupvalue", "debug.sethook",
            "debug.setlocal", "debug.setmetatable", "debug.setupvalue", "debug.traceback",
            
            # UTF-8库
            "utf8.char", "utf8.codepoint", "utf8.codes", "utf8.len", "utf8.offset",
            
            # 协程库
            "coroutine.create", "coroutine.isyieldable", "coroutine.resume",
            "coroutine.running", "coroutine.status", "coroutine.wrap", "coroutine.yield"
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
            
            # 操作符
            "operator": r"[+\-*/%^#=<>~&|]+",
            
            # 标签和goto
            "label": r"::[a-zA-Z_][a-zA-Z0-9_]*::",
            "goto": r"\bgoto\s+[a-zA-Z_][a-zA-Z0-9_]*\b",
            
            # 变长参数
            "vararg": r"\.\.\.",
        }
        
        # 标签样式 - 使用适合Lua脚本的配色方案
        self._tag_styles = {
            "comment": {"foreground": "#6A9955", "font": "italic"},  # 绿色斜体用于单行注释
            "multiline_comment": {"foreground": "#6A9955", "font": "italic"},  # 绿色斜体用于多行注释
            "string": {"foreground": "#CE9178"},  # 橙色用于字符串
            "multiline_string": {"foreground": "#CE9178"},  # 橙色用于多行字符串
            "number": {"foreground": "#B5CEA8"},  # 浅绿色用于数字
            "hex_number": {"foreground": "#B5CEA8"},  # 浅绿色用于十六进制数字
            "boolean": {"foreground": "#569CD6"},  # 蓝色用于布尔值
            "nil": {"foreground": "#569CD6"},  # 蓝色用于nil值
            "function_def": {"foreground": "#DCDCAA", "font": "bold"},  # 浅黄色粗体用于函数定义
            "function_call": {"foreground": "#DCDCAA"},  # 浅黄色用于函数调用
            "property_access": {"foreground": "#9CDCFE"},  # 浅蓝色用于属性访问
            "table_def": {"foreground": "#D4D4D4"},  # 浅灰色用于表定义
            "local_var": {"foreground": "#C586C0"},  # 紫色用于局部变量
            "global_var": {"foreground": "#9CDCFE"},  # 浅蓝色用于全局变量
            "operator": {"foreground": "#D4D4D4"},  # 浅灰色用于操作符
            "label": {"foreground": "#FF7700"},  # 橙色用于标签
            "goto": {"foreground": "#FF7700"},  # 橙色用于goto
            "vararg": {"foreground": "#FF7700"},  # 橙色用于变长参数
        }