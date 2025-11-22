#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dockerfile语言处理器

提供Dockerfile文件的语法高亮支持
"""

import re
from typing import Dict, List, Any

from .base import LanguageHandler


class DockerfileHandler(LanguageHandler):
    """Dockerfile语言处理器"""

    # Dockerfile通常没有扩展名，文件名就是Dockerfile
    file_extensions = ["Dockerfile", "dockerfile"]

    @classmethod
    def get_language_name(cls) -> str:
        """
        获取语言处理器名称

        Returns:
            str: 语言处理器名称"dockerfile"
        """
        return "dockerfile"

    def get_pattern_order(self) -> List[str]:
        """
        获取高亮规则的执行顺序

        Returns:
            List[str]: 高亮规则名称的列表，按照执行顺序排列
        """
        return self._pattern_order

    def _setup_language(self):
        """
        设置Dockerfile语言的语法高亮规则
        """
        # 定义高亮规则的执行顺序
        self._pattern_order = [
            "string",  # 字符串 - 双引号或单引号包围
            "comment",  # 注释 - 以#开头的行
            "instruction",  # Dockerfile指令 - 大写字母开头，后跟空格
            "image",  # 镜像名称 - 在FROM指令后
            "variable",  # 变量引用 - $VAR或${VAR}
            "number",  # 数字
            "key_value_pairs",  # 配置类指令的键值对 - LABEL, ENV, ARG, EXPOSE
            "health_option",  # 健康检查选项
            "shell_option",  # Shell选项
        ]

        # Dockerfile指令关键字
        self._keywords = [
            "FROM",
            "MAINTAINER",
            "RUN",
            "CMD",
            "LABEL",
            "EXPOSE",
            "ENV",
            "ADD",
            "COPY",
            "ENTRYPOINT",
            "VOLUME",
            "USER",
            "WORKDIR",
            "ARG",
            "ONBUILD",
            "STOPSIGNAL",
            "HEALTHCHECK",
            "SHELL",
        ]

        # 正则表达式模式
        self._regex_patterns = {
            # 注释 (以#开头的行)
            "comment": r"(?m)^\s*#.*$",
            # Dockerfile指令 (大写字母开头，后跟空格)
            "instruction": r"(?m)^\s*(FROM|MAINTAINER|RUN|CMD|LABEL|EXPOSE|ENV|ADD|COPY|ENTRYPOINT|VOLUME|USER|WORKDIR|ARG|ONBUILD|STOPSIGNAL|HEALTHCHECK|SHELL)\b",
            # 字符串 (双引号或单引号包围)
            "string": r"([\"'])(?:(?=(\\?))\2.)*?\1",
            # 数字
            "number": r"\b\d+\.?\d*\b",
            # 变量引用 ($VAR或${VAR}) - 更精确的匹配
            "variable": r"\$\{[a-zA-Z0-9_]+\}|\$[a-zA-Z_][a-zA-Z0-9_]*(?![a-zA-Z0-9_])",
            # 镜像名称 (在FROM指令后)
            "image": r"(?m)^\s*FROM\s+([a-zA-Z0-9/_.-]+)",
            # 配置类指令的键值对 (LABEL, ENV, ARG, EXPOSE)
            "key_value_pairs": r"(?m)^\s*(LABEL|ENV|ARG|EXPOSE)\s+([^=\s]+)(\s*=\s*([^\s#]+)|\s+(\d+))",
            # 健康检查选项
            "health_option": r"(--interval=|--timeout=|--start-period=|--retries=)",
            # Shell选项
            "shell_option": r"(--shell=)",
        }

        # 标签样式 - 使用更鲜明的配色方案，适合浅色模式
        self._tag_styles = {
            "comment": {"foreground": "#008000"},  # 深绿色用于注释
            "instruction": {"foreground": "#0000FF"},  # 深蓝色用于所有指令关键字
            "string": {"foreground": "#FF8C00"},  # 深橙色用于字符串
            "number": {"foreground": "#008000"},  # 深绿色用于数字
            "variable": {"foreground": "#FF00FF"},  # 紫色用于变量
            "image": {"foreground": "#FF8C00"},  # 深橙色用于镜像名称
            "key_value_pairs": {
                "foreground": "#008080"
            },  # 深青色用于配置类指令的键值对和端口
            "health_option": {"foreground": "#800000"},  # 深红色用于选项
            "shell_option": {"foreground": "#800000"},  # 深红色用于选项
        }
