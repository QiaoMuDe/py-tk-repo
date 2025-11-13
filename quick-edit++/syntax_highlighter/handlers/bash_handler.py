#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bash语言处理器

提供Bash脚本的语法识别和高亮规则
"""

import re
from typing import Dict, List, Any

from .base import LanguageHandler


class BashHandler(LanguageHandler):
    """
    Bash语言处理器

    提供Bash脚本的语法识别和高亮规则
    """

    # Bash文件扩展名
    file_extensions = [".sh", ".bash", ".zsh", ".fish", ".ksh"]

    def _setup_language(self):
        """设置Bash语言的语法规则"""
        # Bash关键字
        self._keywords = [
            # 控制流关键字
            "if",
            "then",
            "else",
            "elif",
            "fi",
            "for",
            "while",
            "until",
            "do",
            "done",
            "case",
            "esac",
            "select",
            "in",
            # 函数相关
            "function",
            "return",
            "local",
            # 条件测试
            "test",
            "[",
            "]",
            # 命令替换
            "eval",
            "exec",
            # 其他关键字
            "time",
            "declare",
            "typeset",
            "export",
            "readonly",
            "unset",
            "source",
            ".",
        ]

        # 内置命令
        builtins = [
            "echo",
            "printf",
            "read",
            "cd",
            "pwd",
            "ls",
            "cat",
            "grep",
            "sed",
            "awk",
            "sort",
            "uniq",
            "wc",
            "head",
            "tail",
            "find",
            "mkdir",
            "rmdir",
            "rm",
            "cp",
            "mv",
            "chmod",
            "chown",
            "ps",
            "kill",
            "sleep",
            "exit",
            "trap",
            "wait",
            "jobs",
            "fg",
            "bg",
            "alias",
            "unalias",
            "type",
            "which",
            "whereis",
            "history",
        ]

        # 正则表达式模式
        self._regex_patterns = {
            # 关键字 - 使用单词边界确保匹配完整单词
            "keywords": r"\b("
            + "|".join(re.escape(k) for k in self._keywords)
            + r")\b",
            # 内置命令
            "builtins": r"\b(" + "|".join(re.escape(b) for b in builtins) + r")\b",
            # 注释 - 从#开始到行尾
            "comments": r"#.*$",
            # 字符串 - 包括单引号、双引号字符串
            "strings": r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'',
            # 数字 - 包括整数、浮点数
            "numbers": r"\b\d+(?:\.\d+)?\b",
            # 变量 - $开头
            "variables": r"\$[a-zA-Z_][a-zA-Z0-9_]*|\$\{[^}]*\}",
            # 函数定义 - function关键字或函数名后的括号
            "functions": r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\s*\)|\bfunction\s+([a-zA-Z_][a-zA-Z0-9_]*)",
            # 操作符
            "operators": r"(\+|\-|\*|\/|%|=|==|!=|<|>|<=|>=|\|\||&&|\||&|!|\(|\))",
            # 路径 - 以/开头或包含/的字符串
            "paths": r"(/[a-zA-Z0-9_\-\.\/]+|[a-zA-Z0-9_\-\.\/]+/[a-zA-Z0-9_\-\.\/]*)",
        }

        # 标签样式 - 使用适合Bash的配色方案
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
            # 函数 - 深紫色
            "functions": {
                "foreground": "#4B0082",
            },
            # 操作符 - 黑色
            "operators": {
                "foreground": "#000000",
            },
            # 路径 - 深青色
            "paths": {
                "foreground": "#008B8B",
            },
        }
