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
    支持现代批处理语法和增强特性
    """

    # Bat文件扩展名
    file_extensions = [".bat", ".cmd"]

    @classmethod
    def get_language_name(cls) -> str:
        """
        获取语言处理器名称

        Returns:
            str: 语言处理器名称"bat"
        """
        return "bat"

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
            "return",
            "break",
            "continue",
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
            "pushd",
            "popd",
            # 其他关键字
            "not",
            "off",
            "on",
            "enabledelayedexpansion",
            "disableextensions",
            "enableextensions",
            "start",
            "assoc",
            "ftype",
            "title",
            "color",
            # 循环控制
            "forfiles",
            "for",
            "do",
            "in",
            # 条件执行
            "choice",
            "verify",
        ]

        # 内置命令
        builtins = [
            # 文件系统操作
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
            "pushd",
            "popd",
            "tree",
            "attrib",
            "icacls",
            # 系统命令
            "prompt",
            "break",
            "format",
            "diskcomp",
            "diskcopy",
            "chkdsk",
            "find",
            "findstr",
            "more",
            "sort",
            "subst",
            "xcopy",
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
            # 网络相关
            "net",
            "ping",
            "tracert",
            "ipconfig",
            "netstat",
            "nslookup",
            "ftp",
            "telnet",
            "arp",
            "route",
            "hostname",
            # 进程管理
            "tasklist",
            "taskkill",
            "wmic",
            "sc",
            "shutdown",
            "restart",
            # 注册表操作
            "reg",
            "regedit",
            "regini",
            "regsvr32",
            # 其他实用工具
            "install",
            "keyb",
            "print",
            "join",
            "replace",
            "comp",
            "fc",
            "where",
            "whoami",
            "timeout",
            "choice",
            "robocopy",
            "cipher",
            "compact",
            "expand",
            "makecab",
            "cabarc",
            "sigverif",
            "driverquery",
            "openfiles",
            "wevtutil",
            "wevtutil",
            "eventcreate",
            "eventtriggers",
            "typeperf",
            "relog",
            "logman",
            "tracefmt",
            "tracerpt",
            "waitfor",
            "forfiles",
            "powershell",
            "cmd",
            "wscript",
            "cscript",
        ]

        # 正则表达式模式 - 优化和扩展以支持更多批处理语法
        self._regex_patterns = {
            # 关键字 - 使用单词边界确保匹配完整单词
            "keywords": r"\b("
            + "|".join(re.escape(k) for k in self._keywords)
            + r")\b",
            # 内置命令
            "builtins": r"\b(" + "|".join(re.escape(b) for b in builtins) + r")\b",
            # 注释 - 从rem或::开始到行尾，改进匹配
            "comments": r"(?i)(?:\brem\s+.*|::.*)$",
            # 字符串 - 包括双引号字符串，增强转义支持
            "strings": r'"(?:[^"\\]|\\.)*"',
            # 数字 - 包括整数、浮点数、十六进制
            "numbers": r"\b(?:0[xX][0-9a-fA-F]+|\d+(?:\.\d+)?[eE][+-]?\d+|\d+(?:\.\d+)?)\b",
            # 变量 - %开头，增强匹配
            "variables": r"%[a-zA-Z_][a-zA-Z0-9_]*%|%%[a-zA-Z]|%\d+|%[*]|%~[dpnxsfta$1-9]+|![a-zA-Z_][a-zA-Z0-9_]*!",
            # 标签 - :开头，增强匹配
            "labels": r"^[ \t]*:[a-zA-Z_][a-zA-Z0-9_]*",
            # 操作符
            "operators": r"(\+|\-|\*|\/|%|=|==|!=|<|>|<=|>=|\|\||&&|\||&|!|\(|\))",
            # 路径 - 以\开头或包含\的字符串，增强匹配
            "paths": r"(\\[a-zA-Z0-9_\-\.\\]+|[a-zA-Z]:\\[a-zA-Z0-9_\-\.\\]*|[a-zA-Z0-9_\-\.\\]+\\[a-zA-Z0-9_\-\.\\]*)",
            # 新增：环境变量 - 以%开头和结尾
            "environment_vars": r"%[A-Z_][A-Z0-9_]*%",
            # 新增：命令参数 - 以/开头的参数
            "command_args": r"/[a-zA-Z][a-zA-Z0-9\-]*",
            # 新增：重定向操作符
            "redirection": r"(?:>>|>|<|<<|2>&1|2>|1>&2)",
            # 新增：管道操作符
            "pipe": r"\|",
            # 新增：条件表达式
            "conditional": r"\b(?:if|else)\s+.*?(?=\b(?:if|else|goto|call|exit|rem|::)\b|\s*$)",
            # 新增：循环表达式
            "loop": r"\bfor\s+.*?\s+in\s+.*?\s+do\s+.*",
            # 新增：函数调用
            "function_call": r"\bcall\s+:[a-zA-Z_][a-zA-Z0-9_]*",
        }

        # 标签样式 - 使用适合Bat脚本的配色方案，仅修改颜色
        self._tag_styles = {
            # 关键字 - 深蓝色
            "keywords": {
                "foreground": "#0000CD",
            },
            # 内置命令 - 蓝色
            "builtins": {
                "foreground": "#1E90FF",
            },
            # 注释 - 绿色
            "comments": {
                "foreground": "#228B22",
            },
            # 字符串 - 棕色
            "strings": {
                "foreground": "#A0522D",
            },
            # 数字 - 深红色
            "numbers": {
                "foreground": "#B22222",
            },
            # 变量 - 紫色
            "variables": {
                "foreground": "#8B008B",
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
            # 新增：环境变量 - 深紫色
            "environment_vars": {
                "foreground": "#4B0082",
            },
            # 新增：命令参数 - 深橙色
            "command_args": {
                "foreground": "#FF8C00",
            },
            # 新增：重定向操作符 - 深蓝色
            "redirection": {
                "foreground": "#00008B",
            },
            # 新增：管道操作符 - 深灰色
            "pipe": {
                "foreground": "#696969",
            },
            # 新增：条件表达式 - 深青色
            "conditional": {
                "foreground": "#008080",
            },
            # 新增：循环表达式 - 深品红色
            "loop": {
                "foreground": "#8B008B",
            },
            # 新增：函数调用 - 深棕色
            "function_call": {
                "foreground": "#8B4513",
            },
        }
