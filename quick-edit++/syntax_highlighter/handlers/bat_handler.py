#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bat脚本语言处理器

提供Windows批处理脚本的语法识别和高亮规则
"""

import re
from typing import Dict, List, Any

from .base import LanguageHandler


class BatHandler(LanguageHandler):
    """
    Bat脚本语言处理器

    提供Windows批处理脚本的语法识别和高亮规则
    """

    # Bat文件扩展名
    file_extensions = [".bat", ".cmd"]

    def _setup_language(self):
        """设置Bat脚本的语法规则"""
        # Bat关键字
        self._keywords = [
            # 控制流关键字
            "if",
            "else",
            "for",
            "do",
            "in",
            "goto",
            "call",
            "exit",
            "pause",
            # 条件测试
            "exist",
            "errorlevel",
            "defined",
            "equ",
            "neq",
            "lss",
            "leq",
            "gtr",
            "geq",
            # 命令相关
            "echo",
            "set",
            "setlocal",
            "endlocal",
            "shift",
            # 其他关键字
            "not",
            "off",
            "on",
        ]

        # 内置命令
        builtins = [
            "cd",
            "chdir",
            "cls",
            "copy",
            "del",
            "erase",
            "dir",
            "md",
            "mkdir",
            "rd",
            "rmdir",
            "move",
            "ren",
            "rename",
            "type",
            "ver",
            "vol",
            "path",
            "prompt",
            "break",
            "attrib",
            "format",
            "diskcomp",
            "diskcopy",
            "chkdsk",
            "find",
            "more",
            "sort",
            "subst",
            "xcopy",
            "tree",
            "graphics",
            "mode",
            "recover",
            "assign",
            "backup",
            "restore",
            "command",
            "debug",
            "fdisk",
            "sys",
            "append",
            "fastopen",
            "share",
            "loadfix",
            "loadhigh",
            "nlsfunc",
            "install",
            "keyb",
            "print",
            "join",
            "replace",
            "comp",
            "fc",
        ]

        # 正则表达式模式
        self._regex_patterns = {
            # 关键字 - 使用单词边界确保匹配完整单词
            "keywords": r"\b("
            + "|".join(re.escape(k) for k in self._keywords)
            + r")\b",
            # 内置命令
            "builtins": r"\b(" + "|".join(re.escape(b) for b in builtins) + r")\b",
            # 注释 - 从rem或::开始到行尾
            "comments": r"(rem\s+.*|::.*)$",
            # 字符串 - 包括双引号字符串
            "strings": r'"(?:[^"\\]|\\.)*"',
            # 数字 - 包括整数、浮点数
            "numbers": r"\b\d+(?:\.\d+)?\b",
            # 变量 - %开头
            "variables": r"%[a-zA-Z_][a-zA-Z0-9_]*%|%%[a-zA-Z]|%\d+|%[*]",
            # 标签 - :开头
            "labels": r"^[ \t]*:[a-zA-Z_][a-zA-Z0-9_]*",
            # 操作符
            "operators": r"(\+|\-|\*|\/|%|=|==|!=|<|>|<=|>=|\|\||&&|\||&|!|\(|\))",
            # 路径 - 以\开头或包含\的字符串
            "paths": r"(\\[a-zA-Z0-9_\-\.\\]+|[a-zA-Z]:\\[a-zA-Z0-9_\-\.\\]*|[a-zA-Z0-9_\-\.\\]+\\[a-zA-Z0-9_\-\.\\]*)",
        }

        # 标签样式 - 使用适合Bat脚本的配色方案
        self._tag_styles = {
            # 关键字 - 深蓝色
            "keywords": {
                "foreground": "#000080",
            },
            # 内置命令 - 蓝色
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
            # 变量 - 紫色
            "variables": {
                "foreground": "#800080",
            },
            # 标签 - 深青色
            "labels": {
                "foreground": "#008B8B",
            },
            # 操作符 - 黑色
            "operators": {
                "foreground": "#000000",
            },
            # 路径 - 深绿色
            "paths": {
                "foreground": "#006400",
            },
        }
