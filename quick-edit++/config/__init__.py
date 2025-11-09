#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理模块初始化文件
"""

# 从config_manager模块导出ConfigManager类和全局实例
from .config_manager import (
    ConfigManager,
    config_manager,
    CONFIG_PATH,
    DEFAULT_CONFIG,
    merge_configs,
)

__all__ = [
    "ConfigManager",
    "config_manager",
    "CONFIG_PATH",
    "DEFAULT_CONFIG",
    "merge_configs",
]
