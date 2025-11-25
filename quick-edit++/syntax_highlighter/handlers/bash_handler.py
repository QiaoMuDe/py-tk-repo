#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bash语言处理器

提供Bash脚本的语法识别和高亮规则
支持Bash 4.0+特性和常见Shell语法
"""

import re
from typing import Dict, List, Any

from .base import LanguageHandler


class BashHandler(LanguageHandler):
    """
    Bash语言处理器

    提供Bash脚本的语法识别和高亮规则
    支持Bash 4.0+特性和常见Shell语法
    """

    # Bash文件扩展名
    file_extensions = [".sh", ".bash"]

    @classmethod
    def get_language_name(cls) -> str:
        """
        获取语言处理器名称

        Returns:
            str: 语言处理器名称"bash"
        """
        return "bash"

    def get_pattern_order(self) -> List[str]:
        """
        获取高亮规则的执行顺序

        Returns:
            List[str]: 高亮规则的执行顺序列表
        """
        return self._pattern_order

    def _setup_language(self):
        """设置Bash语言的语法规则"""

        # 定义高亮规则的执行顺序
        self._pattern_order = [
            "comments",  # 注释 - 最高优先级
            "strings",  # 字符串
            "string_variables",  # 字符串中的变量引用
            "heredoc",  # Here文档
            "command_substitution",  # 命令替换
            "variables",  # 变量
            "functions",  # 函数
            "command_options",  # 命令选项
            "keywords",  # 关键字
            "builtins",  # 内置命令
            "variable_names",  # 变量名
            "numbers",  # 数字
            "arithmetic",  # 算术表达式
            "operators",  # 操作符
            "paths",  # 路径
            "redirection",  # 重定向操作符
            "wildcards",  # 通配符模式
            "array_index",  # 数组索引
            "parameter_expansion",  # 参数扩展
            "process_substitution",  # 进程替换
        ]

        # Bash关键字 - 扩展以支持更多控制流和高级特性
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
            "unset",
            # 条件测试
            "test",
            # 命令替换和执行
            "eval",
            "exec",
            "source",
            ".",
            # 其他关键字
            "time",
            "declare",
            "typeset",
            "export",
            "readonly",
            # Bash 4.0+ 关键字
            "coproc",
            "mapfile",
            "readarray",
            # 循环控制
            "break",
            "continue",
        ]

        # 操作符 - Bash脚本中的各种操作符
        self._operators = [
            "++",
            "--",
            "==",
            "!=",
            "<=",
            ">=",
            "&&",
            "||",
            "<<",
            ">>",
            "&^",
            "+",
            "-",
            "*",
            "/",
            "%",
            "=",
            "<",
            ">",
            "&",
            "!",
            "|",
            "^",
            "~",
            "?",
            ":",
            ",",
            ";",
            "(",
            ")",
            "[",
            "]",
            "{",
            "}",
        ]

        # 内置命令 - 扩展常用内置命令
        builtins = [
            # 基本命令
            "echo",
            "printf",
            "read",
            "cd",
            "pwd",
            "ls",
            "cat",
            # 文本处理
            "grep",
            "sed",
            "awk",
            "sort",
            "uniq",
            "wc",
            "head",
            "tail",
            "cut",
            "tr",
            # 文件操作
            "find",
            "mkdir",
            "rmdir",
            "rm",
            "cp",
            "mv",
            "chmod",
            "chown",
            "chgrp",
            "touch",
            # 进程管理
            "ps",
            "kill",
            "killall",
            "jobs",
            "fg",
            "bg",
            "wait",
            "sleep",
            "nohup",
            # 系统信息
            "date",
            "who",
            "whoami",
            "id",
            "uname",
            "df",
            "du",
            "free",
            # 网络工具
            "ping",
            "wget",
            "curl",
            "ssh",
            "scp",
            "rsync",
            # 其他常用命令
            "exit",
            "trap",
            "alias",
            "unalias",
            "type",
            "which",
            "whereis",
            "history",
            "clear",
            # Bash内置命令
            "set",
            "unset",
            "export",
            "readonly",
            "declare",
            "typeset",
            "local",
            "let",
            "pushd",
            "popd",
            "dirs",
            "shopt",
            "ulimit",
        ]

        # 正则表达式模式 - 优化和扩展以支持更多Bash语法
        self._regex_patterns = {
            # 关键字 - 使用单词边界确保匹配完整单词
            "keywords": r"\b("
            + "|".join(re.escape(k) for k in self._keywords)
            + r")\b",
            # 内置命令
            "builtins": r"\b(" + "|".join(re.escape(b) for b in builtins) + r")\b",
            # 注释 - 从#开始到行尾，但排除字符串中的#
            "comments": r"(?<!\")#.*$",
            # 字符串 - 包括单引号、双引号字符串，支持转义字符
            "strings": r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'',
            # 数字 - 包括整数、浮点数、十六进制、八进制
            "numbers": r"\b(?:0[xX][0-9a-fA-F]+|0[0-7]+|\d+(?:\.\d+)?[eE][+-]?\d+|\d+(?:\.\d+)?)\b",
            # 命令选项 - -x和--x形式的参数
            "command_options": r"(?:^|\s)(-{1,2}[a-zA-Z][a-zA-Z0-9_-]*)",
            # 变量名 - 赋值语句中的变量名
            "variable_names": r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*(?==)",
            # 变量 - $开头的变量，包括位置参数、特殊参数、数组
            "variables": r"\$[a-zA-Z_][a-zA-Z0-9_]*|\$\{[^}]*\}|\$[0-9]+|\$[#@*?%!\-_$]",
            # 函数定义 - function关键字或函数名后的括号
            "functions": r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\s*\)|\bfunction\s+([a-zA-Z_][a-zA-Z0-9_]*)",
            # 操作符 - 使用属性数组并转义展开
            "operators": r"("
            + "|".join(re.escape(op) for op in self._operators)
            + r")",
            # 路径 - 以/开头或包含/的字符串，包括~家目录
            "paths": r"(?:~/[a-zA-Z0-9_\-\.\/]+|/[a-zA-Z0-9_\-\.\/]+|[a-zA-Z0-9_\-\.\/]+/[a-zA-Z0-9_\-\.\/]*)",
            # 命令替换 - $(...)和`...`
            "command_substitution": r"\$\([^)]*\)|`[^`]*`",
            # 进程替换 - <(...)和>(...)
            "process_substitution": r"<\([^)]*\)|>\([^)]*\)",
            # 算术表达式 - $((...))和((...))
            "arithmetic": r"\$\(\([^)]*\)\)|\(\([^)]*\)\)",
            # Here文档 - <<和<<-
            "heredoc": r"<<[-\s]*['\"]?(\w+)['\"]?\s*$",
            # 重定向操作符
            "redirection": r"[12&]?>>>?|[12&]?<<?|&>|[12&]>>?",
            # 通配符模式
            "wildcards": r"\*|\?|\[.*?\]",
            # 数组索引 - ${array[index]}
            "array_index": r"\$\{[a-zA-Z_][a-zA-Z0-9_]*\[[^\]]+\]\}",
            # 参数扩展 - ${param#word}, ${param%word}等
            "parameter_expansion": r"\$\{[a-zA-Z_][a-zA-Z0-9_]*[#%:=+\-?*@!]\}",
        }

        # 标签样式 - 使用适合Bash的配色方案，仅修改颜色
        self._tag_styles = {
            # 关键字 - 深蓝色
            "keywords": {
                "foreground": "#0000CD",
            },
            # 内置命令 - 蓝色
            "builtins": {
                "foreground": "#4169E1",
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
            # 命令选项 - 橙色
            "command_options": {
                "foreground": "#FFA500",
            },
            # 变量名 - 深青色
            "variable_names": {
                "foreground": "#008B8B",
            },
            # 变量 - 紫色
            "variables": {
                "foreground": "#8B008B",
            },
            # 函数 - 深紫色
            "functions": {
                "foreground": "#483D8B",
            },
            # 操作符 - 灰色
            "operators": {
                "foreground": "#808080",
            },
            # 路径 - 深青色
            "paths": {
                "foreground": "#008B8B",
            },
            # 命令替换 - 深橙色
            "command_substitution": {
                "foreground": "#FF8C00",
            },
            # 进程替换 - 深粉红色
            "process_substitution": {
                "foreground": "#C71585",
            },
            # 算术表达式 - 深金色
            "arithmetic": {
                "foreground": "#B8860B",
            },
            # Here文档 - 深灰色
            "heredoc": {
                "foreground": "#696969",
            },
            # 重定向操作符 - 深青绿色
            "redirection": {
                "foreground": "#008080",
            },
            # 通配符模式 - 深橄榄色
            "wildcards": {
                "foreground": "#556B2F",
            },
            # 数组索引 - 深紫罗兰色
            "array_index": {
                "foreground": "#6A5ACD",
            },
            # 参数扩展 - 深石板蓝
            "parameter_expansion": {
                "foreground": "#708090",
            },
        }

    def get_file_extensions(self) -> List[str]:
        """
        获取文件扩展名列表

        Returns:
            List[str]: 文件扩展名列表
        """
        return self.file_extensions
