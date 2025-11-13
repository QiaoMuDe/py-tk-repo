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
    
    def _setup_language(self):
        """
        设置Dockerfile语言的语法高亮规则
        """
        # Dockerfile指令关键字
        self._keywords = [
            "FROM", "MAINTAINER", "RUN", "CMD", "LABEL", "EXPOSE", "ENV", 
            "ADD", "COPY", "ENTRYPOINT", "VOLUME", "USER", "WORKDIR", 
            "ARG", "ONBUILD", "STOPSIGNAL", "HEALTHCHECK", "SHELL"
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
            
            # 端口号 (在EXPOSE指令后)
            "port": r"(?m)^\s*EXPOSE\s+\b(\d+)\b",
            
            # 镜像名称 (在FROM指令后)
            "image": r"(?m)^\s*FROM\s+([a-zA-Z0-9/_.-]+)",
            
            # 健康检查选项
            "health_option": r"(--interval=|--timeout=|--start-period=|--retries=)",
            
            # Shell选项
            "shell_option": r"(--shell=)",
            
            # 标签键值对
            "label": r"(?m)^\s*LABEL\s+([^=]+)=(.*)",
            
            # 环境变量键值对
            "env": r"(?m)^\s*ENV\s+([^=]+)=(.*)",
            
            # ARG键值对
            "arg": r"(?m)^\s*ARG\s+([^=]+)=(.*)",
        }
        
        # 标签样式 - 使用简洁的配色方案
        self._tag_styles = {
            "comment": {"foreground": "#6A9955"},  # 绿色用于注释
            "instruction": {"foreground": "#569CD6"},  # 蓝色用于所有指令关键字
            "string": {"foreground": "#CE9178"},  # 橙色用于字符串
            "number": {"foreground": "#B5CEA8"},  # 浅绿色用于数字
            "variable": {"foreground": "#9CDCFE"},  # 浅蓝色用于变量
            "port": {"foreground": "#B5CEA8"},  # 浅绿色用于端口号
            "image": {"foreground": "#CE9178"},  # 橙色用于镜像名称
            "health_option": {"foreground": "#D4D4D4"},  # 浅灰色用于选项
            "shell_option": {"foreground": "#D4D4D4"},  # 浅灰色用于选项
            "label": {"foreground": "#569CD6"},  # 蓝色用于标签
            "env": {"foreground": "#4EC9B0"},  # 青色用于环境变量
            "arg": {"foreground": "#569CD6"},  # 蓝色用于参数
        }