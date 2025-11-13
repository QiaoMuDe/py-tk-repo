#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
语言处理器模块

提供各种语言的语法高亮处理器
"""

from .base import LanguageHandler
from .python_handler import PythonHandler

# 导出所有可用的语言处理器
__all__ = [
    'LanguageHandler',
    'PythonHandler',
]