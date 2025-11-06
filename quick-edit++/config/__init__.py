#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理模块初始化文件
"""

# 从config_manager模块导出关键函数和常量
from .config_manager import (
    load_config,
    save_config,
    CONFIG_PATH,
    DEFAULT_CONFIG,
    merge_configs
)

__all__ = [
    'load_config',
    'save_config',
    'CONFIG_PATH',
    'DEFAULT_CONFIG',
    'merge_configs'
]