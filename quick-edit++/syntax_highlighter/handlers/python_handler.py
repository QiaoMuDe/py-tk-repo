#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Python语言处理器

提供Python语法的识别和高亮规则
"""

import re
from typing import Dict, List, Any

from .base import LanguageHandler


class PythonHandler(LanguageHandler):
    """
    Python语言处理器
    
    提供Python语法的识别和高亮规则
    """
    
    # Python文件扩展名
    file_extensions = ['.py', '.pyw', '.pyi']
    
    def _setup_language(self):
        """设置Python语言的语法规则"""
        # Python关键字
        self._keywords = [
            # 控制流关键字
            'if', 'elif', 'else', 'for', 'while', 'break', 'continue', 'pass',
            # 函数和类定义
            'def', 'class', 'return', 'yield', 'lambda',
            # 异常处理
            'try', 'except', 'finally', 'raise', 'assert',
            # 导入模块
            'import', 'from', 'as',
            # 逻辑运算符
            'and', 'or', 'not', 'in', 'is',
            # 其他关键字
            'global', 'nonlocal', 'del', 'with', 'async', 'await'
        ]
        
        # 内置函数和类型
        builtins = [
            'abs', 'all', 'any', 'bin', 'bool', 'bytearray', 'bytes', 'callable',
            'chr', 'classmethod', 'compile', 'complex', 'delattr', 'dict', 'dir',
            'divmod', 'enumerate', 'eval', 'exec', 'filter', 'float', 'format',
            'frozenset', 'getattr', 'globals', 'hasattr', 'hash', 'help', 'hex',
            'id', 'input', 'int', 'isinstance', 'issubclass', 'iter', 'len',
            'list', 'locals', 'map', 'max', 'memoryview', 'min', 'next',
            'object', 'oct', 'open', 'ord', 'pow', 'print', 'property',
            'range', 'repr', 'reversed', 'round', 'set', 'setattr', 'slice',
            'sorted', 'staticmethod', 'str', 'sum', 'super', 'tuple', 'type',
            'vars', 'zip'
        ]
        
        # 正则表达式模式
        self._regex_patterns = {
            # 关键字 - 使用单词边界确保匹配完整单词
            'keywords': r'\b(' + '|'.join(re.escape(k) for k in self._keywords) + r')\b',
            # 内置函数
            'builtins': r'\b(' + '|'.join(re.escape(b) for b in builtins) + r')\b',
            # 注释 - 从#开始到行尾
            'comments': r'#.*$',
            # 字符串 - 包括单引号、双引号、三引号字符串
            'strings': r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')',
            # 数字 - 包括整数、浮点数、科学计数法
            'numbers': r'\b\d+\.?\d*(?:[eE][+-]?\d+)?\b',
            # 函数定义 - 函数名后的括号
            'functions': r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*(?=\()',
            # 装饰器 - @开头的行
            'decorators': r'@\s*[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*',
            # 操作符
            'operators': r'(\+|\-|\*|\/|\/\/|%|\*\*|=|==|!=|<|>|<=|>=|<>)',
        }
        
        # 标签样式 - 使用适合Python的配色方案
        self._tag_styles = {
            # 关键字 - 橙色
            'keywords': {
                'foreground': '#FF7700'
            },
            # 内置函数 - 蓝色
            'builtins': {
                'foreground': '#0000FF',
            },
            # 注释 - 绿色
            'comments': {
                'foreground': '#00AA00',
            },
            # 字符串 - 红色
            'strings': {
                'foreground': '#AA0000',
            },
            # 数字 - 深蓝色
            'numbers': {
                'foreground': '#0000AA',
            },
            # 函数 - 紫色
            'functions': {
                'foreground': '#800080',
            },
            # 装饰器 - 棕色
            'decorators': {
                'foreground': '#8B4513',
            },
            # 操作符 - 黑色
            'operators': {
                'foreground': '#000000',
            },
        }