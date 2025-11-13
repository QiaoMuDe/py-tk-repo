#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
语法高亮包

提供基于tkinter Text组件的语法高亮功能
"""

# 导出主要类
from .highlighter import SyntaxHighlighter
from .handlers import LanguageHandler
from .handlers.python_handler import PythonHandler
from .handlers.json_handler import JSONHandler

# 定义包的公共API
__all__ = ["SyntaxHighlighter", "LanguageHandler", "PythonHandler", "JSONHandler"]

# 版本信息
__version__ = "1.0.0"
