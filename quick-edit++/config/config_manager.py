#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理模块，负责配置文件的加载和保存
"""

import os
import json
from pathlib import Path

# 默认配置文件路径：用户家目录下的.QuickEditPlus.json
CONFIG_FILE_NAME = ".QuickEditPlus.json"
CONFIG_PATH = os.path.join(str(Path.home()), CONFIG_FILE_NAME)

# 默认配置字段
DEFAULT_CONFIG = {
    # 界面设置
    "interface": {
        "show_toolbar": True,
        "window_title_format": "{filename} - QuickEdit++",
        "theme_mode": "system",  # light, dark, system
        "color_theme": "blue",  # blue, green, dark-blue
    },
    
    # 编辑设置
    "editor": {
        "auto_wrap": True,
        "tab_size": 4,
        "use_spaces": True,
        "quick_insert": True,
    },
    
    # 保存设置
    "saving": {
        "auto_save": True,
        "auto_save_interval": 300,  # 秒
        "backup_enabled": True,
    },
    
    # 字体设置
    "font": {
        "family": "Microsoft YaHei",
        "size": 10,
    },
    
    # 光标设置
    "cursor": {
        "style": "line",  # line, block, underline
        "blink_rate": 530,  # 毫秒
    },
}


def load_config():
    """
    加载配置文件
    
    Returns:
        dict: 配置字典
    
    说明：
        - 如果配置文件不存在，先保存默认配置，然后返回默认配置
        - 如果配置文件存在但解析失败，返回默认配置
    """
    # 检查配置文件是否存在
    if not os.path.exists(CONFIG_PATH):
        # 保存默认配置
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    
    try:
        # 读取配置文件
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 合并默认配置，确保所有必要字段都存在
        return merge_configs(DEFAULT_CONFIG, config)
    except (json.JSONDecodeError, IOError) as e:
        # 配置文件解析失败或读取错误，返回默认配置
        print(f"配置文件读取失败: {e}")
        return DEFAULT_CONFIG


def save_config(config):
    """
    保存配置到文件
    
    Args:
        config (dict): 要保存的配置字典
    
    Returns:
        bool: 是否保存成功
    
    说明：
        - 确保配置文件所在目录存在
        - 使用UTF-8编码保存
    """
    try:
        # 确保用户家目录存在（理论上总是存在的）
        os.makedirs(str(Path.home()), exist_ok=True)
        
        # 保存配置文件
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        return True
    except IOError as e:
        # 保存失败
        print(f"配置文件保存失败: {e}")
        return False


def merge_configs(default, custom):
    """
    合并默认配置和自定义配置
    
    Args:
        default (dict): 默认配置字典
        custom (dict): 自定义配置字典
    
    Returns:
        dict: 合并后的配置字典
    
    说明：
        - 递归合并嵌套字典
        - 只保留自定义配置中存在的键
    """
    if not isinstance(custom, dict):
        return default
    
    result = default.copy()
    
    for key, value in custom.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # 递归合并嵌套字典
            result[key] = merge_configs(result[key], value)
        elif key in result:
            # 更新已存在的键
            result[key] = value
    
    return result