#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
对话框模块初始化文件
"""

# 从font_dialog模块导出关键函数和类
from .font_dialog import (
    FontDialog,
    show_font_dialog
)

__all__ = [
    'FontDialog',
    'show_font_dialog'
]