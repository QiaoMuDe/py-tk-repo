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
from .bat_handler import BatHandler
from .powershell_handler import PowerShellHandler
from .sql_handler import SQLHandler
from .html_handler import HTMLHandler
from .xml_handler import XMLHandler
from .css_handler import CSSHandler
from .javascript_handler import JavaScriptHandler
from .typescript_handler import TypeScriptHandler
from .go_handler import GoHandler
from .markdown_handler import MarkdownHandler
from .dockerfile_handler import DockerfileHandler
from .makefile_handler import MakefileHandler
from .gitignore_handler import GitIgnoreHandler
from .log_handler import LogHandler
from .lua_handler import LuaHandler
from .java_handler import JavaHandler
from .csv_handler import CSVHandler
from .vim_handler import VimHandler

# 导出所有可用的语言处理器
__all__ = [
    "LanguageHandler",
    "PythonHandler",
    "JSONHandler",
    "IniTomlHandler",
    "YAMLHandler",
    "BashHandler",
    "BatHandler",
    "PowerShellHandler",
    "SQLHandler",
    "HTMLHandler",
    "XMLHandler",
    "CSSHandler",
    "JavaScriptHandler",
    "TypeScriptHandler",
    "GoHandler",
    "MarkdownHandler",
    "DockerfileHandler",
    "MakefileHandler",
    "GitIgnoreHandler",
    "LogHandler",
    "LuaHandler",
    "JavaHandler",
    "CSVHandler",
    "VimHandler",
]
