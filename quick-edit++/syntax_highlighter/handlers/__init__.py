#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
语言处理器模块

提供各种语言的语法高亮处理器
"""

from .base import LanguageHandler
from .python_handler import PythonHandler
from .json_handler import JSONHandler
from .ini_toml_handler import IniTomlHandler
from .yaml_handler import YAMLHandler
from .bash_handler import BashHandler
from .html_handler import HTMLHandler
from .xml_handler import XMLHandler
from .css_handler import CSSHandler
from .javascript_handler import JavaScriptHandler
from .typescript_handler import TypeScriptHandler
from .go_handler import GoHandler

# 导出所有可用的语言处理器
__all__ = [
    "LanguageHandler",
    "PythonHandler",
    "JSONHandler",
    "IniTomlHandler",
    "YAMLHandler",
    "BashHandler",
    "HTMLHandler",
    "XMLHandler",
    "CSSHandler",
    "JavaScriptHandler",
    "TypeScriptHandler",
    "GoHandler",
]
