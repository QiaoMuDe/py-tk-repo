#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Makefile语言处理器

提供Makefile文件的语法高亮支持
"""

import re
from typing import Dict, List, Any

from .base import LanguageHandler


class MakefileHandler(LanguageHandler):
    """Makefile语言处理器"""

    # Makefile通常没有扩展名，文件名就是Makefile或makefile
    file_extensions = ["Makefile", "makefile", "GNUmakefile"]

    @classmethod
    def get_language_name(cls) -> str:
        """
        获取语言处理器名称

        Returns:
            str: 语言处理器名称"makefile"
        """
        return "makefile"

    def _setup_language(self):
        """设置Makefile语言的语法规则"""
        # 定义模式处理顺序，确保字符串和注释有正确的优先级
        self._pattern_order = [
            "string",  # 字符串放在第一位，确保优先匹配
            "comment",  # 注释放在第二位
            "variable",  # 变量引用
            "target",  # 目标定义
            "command",  # 命令
            "phony",  # 伪目标声明
            "assignment",  # 变量赋值
            "autovar",  # 自动变量
            "function",  # 内置函数
            "special_target",  # 特殊目标
            "pattern",  # 模式规则
            "number",  # 数字
        ]
        # Makefile内置函数和关键字
        self._keywords = [
            "include",
            "define",
            "endef",
            "ifdef",
            "ifndef",
            "ifeq",
            "ifneq",
            "else",
            "endif",
            "export",
            "unexport",
            "override",
            "private",
            "vpath",
            "subst",
            "patsubst",
            "strip",
            "findstring",
            "filter",
            "filter-out",
            "sort",
            "word",
            "wordlist",
            "words",
            "firstword",
            "lastword",
            "dir",
            "notdir",
            "suffix",
            "basename",
            "addsuffix",
            "addprefix",
            "join",
            "wildcard",
            "realpath",
            "abspath",
            "error",
            "warning",
            "info",
            "origin",
            "flavor",
            "foreach",
            "call",
            "eval",
            "file",
            "value",
            "shell",
        ]

        # 正则表达式模式
        self._regex_patterns = {
            # 注释 (以#开头的行)
            "comment": r"(?m)^\s*#.*$",
            # 目标定义 (以冒号结尾的行)
            "target": r"(?m)^[a-zA-Z0-9_.%-]+(?=\s*:)",
            # 伪目标声明 (.PHONY)
            "phony": r"(?m)^\s*\.PHONY\s*:",
            # 变量赋值 (=, :=, ::=, ?=, +=)
            "assignment": r"(?m)^[a-zA-Z0-9_]+\s*([:]{0,2}=|\?=|\+=)",
            # 变量引用 ($VAR, $(VAR), ${VAR})
            "variable": r"\$\{[a-zA-Z0-9_]+\}|\$\([a-zA-Z0-9_]+\)|\$[a-zA-Z_][a-zA-Z0-9_]*(?![a-zA-Z0-9_])",
            # 自动变量 ($@, $^, $<, $?, $*, $%等)
            "autovar": r"\$[@^<?*%]",
            # 函数调用 $(function args)
            "function": r"\$\([a-zA-Z0-9_]+\s+",
            # 命令行 (以Tab开头的行)
            "command": r"(?m)^\t.*$",
            # 字符串 (双引号或单引号包围)
            "string": r"([\"'])(?:(?=(\\?))\2.)*?\1",
            # 数字
            "number": r"\b\d+\.?\d*\b",
            # 特殊目标 (.SUFFIXES, .DEFAULT, .PRECIOUS等)
            "special_target": r"(?m)^\s*\.[a-zA-Z]+\s*:",
            # 模式规则 (%)
            "pattern": r"(?m)^[a-zA-Z0-9_.%*-]+\s*:",
        }

        # 标签样式 - 使用简洁的配色方案
        self._tag_styles = {
            "comment": {"foreground": "#6A9955"},  # 绿色用于注释
            "target": {"foreground": "#569CD6"},  # 蓝色用于目标
            "phony": {"foreground": "#C586C0"},  # 紫色用于伪目标声明
            "assignment": {"foreground": "#4EC9B0"},  # 青色用于变量赋值
            "variable": {"foreground": "#9CDCFE"},  # 浅蓝色用于变量引用
            "autovar": {"foreground": "#DCDCAA"},  # 浅黄色用于自动变量
            "function": {"foreground": "#C586C0"},  # 紫色用于函数调用
            "command": {"foreground": "#D4D4D4"},  # 浅灰色用于命令行
            "string": {"foreground": "#CE9178"},  # 橙色用于字符串
            "number": {"foreground": "#B5CEA8"},  # 浅绿色用于数字
            "special_target": {"foreground": "#C586C0"},  # 紫色用于特殊目标
            "pattern": {"foreground": "#569CD6"},  # 蓝色用于模式规则
        }

    def get_pattern_order(self) -> List[str]:
        """
        获取模式处理顺序

        Returns:
            List[str]: 模式处理顺序列表
        """
        return self._pattern_order
