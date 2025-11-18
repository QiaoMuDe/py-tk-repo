#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理模块，负责配置文件的加载和保存
"""

import os
import json
from tkinter import messagebox
from pathlib import Path

# 应用程序常量
APP_VERSION = "v0.0.19"  # 版本号
PROJECT_URL = "https://gitee.com/MM-Q/py-tk-repo.git"  # 项目地址

# 默认配置文件路径：用户家目录下的.QuickEditPlus.json
CONFIG_FILE_NAME = ".QuickEditPlus.json"
CONFIG_PATH = os.path.join(str(Path.home()), CONFIG_FILE_NAME)

# 默认配置字段
DEFAULT_CONFIG = {
    # 应用程序全局设置
    "app": {
        "theme_mode": "light",  # light, dark, system 主题模式
        "color_theme": "blue",  # blue, green, dark-blue 颜色主题
        "window_width": 1000,  # 窗口宽度
        "window_height": 700,  # 窗口高度
        "min_width": 800,  # 最小窗口宽度
        "min_height": 600,  # 最小窗口高度
        "auto_save": False,  # 是否自动保存
        "auto_save_interval": 5,  # 秒 默认自动保存间隔
        "backup_enabled": False,  # 是否启用副本备份功能
        "default_encoding": "UTF-8",  # 默认编码
        "default_line_ending": "LF",  # 默认行结束符：LF
        "max_file_size": 10485760,  # 最大打开文件大小：10MB
        "show_toolbar": True,  # 是否显示工具栏
        "window_title_mode": "filename",  # 窗口标题显示模式：filename, filepath, filename_and_dir
    },
    # 文件监听器配置
    "file_watcher": {
        "check_interval": 3,  # 文件变更检查间隔（秒）
        "save_buffer": 1.0,  # 保存后的缓冲时间（秒），在此期间内不提示文件变更
        "readonly_notify_delay": 30,  # 只读模式下通知重置延迟（秒）
        "edit_notify_delay": 120,  # 编辑模式下通知重置延迟（秒）
    },
    # 最近打开文件配置
    "recent_files": {
        "enabled": True,  # 是否启用最近打开文件功能
        "max_items": 9,  # 最大存储条数
        "history": [],  # 文件历史列表
    },
    # 文本编辑器配置
    "text_editor": {
        "font": "Microsoft YaHei UI",  # 字体
        "font_size": 15,  # 字体大小
        "font_bold": False,  # 是否使用粗体
        "auto_wrap": True,  # 是否自动换行
        "read_only": False,  # 是否只读模式
        "bg_color": "#FFFFFF",  # 文本编辑器背景色
        "line_number_bg_color": "#cccccc",  # 行号背景色
        "line_number_font_color": "#2b91af",  # 行号字体颜色
        "max_undo": 50,  # 最大撤销次数
        "show_line_numbers": True,  # 是否显示行号
        "auto_increment_number": True,  # 是否启用自动递增编号功能
        "highlight_current_line": True,  # 是否启用光标所在行高亮
        "cursor_width": 5,  # 光标宽度（像素）
    },
    # 工具栏配置
    "toolbar": {
        "font": "Microsoft YaHei UI",
        "font_size": 12,
        "font_bold": True,
    },
    # 菜单栏配置
    "menu_bar": {
        "font": "Microsoft YaHei UI",
        "font_size": 12,
        "font_bold": True,
    },
    # 状态栏配置
    "status_bar": {
        "font": "Microsoft YaHei UI",
        "font_size": 12,
        "font_bold": True,
    },
    # 组件默认字体配置
    "components": {
        "font": "Microsoft YaHei UI",
        "font_size": 13,
        "font_bold": False,
    },
    # 语法高亮配置
    "syntax_highlighter": {
        "enabled": False,  # 默认关闭语法高亮
        "render_visible_only": True,  # false: 渲染全部(受max_lines_per_highlight限制), true: 只渲染可见行
        "max_lines_per_highlight": 1000,  # 渲染全部时的最大行数限制
    },
}


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


class ConfigManager:
    """
    配置管理器类，提供配置的加载、保存和访问接口
    """

    def __init__(self):
        """初始化配置管理器"""
        # 加载配置文件
        self.config = self.load_config()

        # 图标路径
        self.ICON_PATH = "ico/QuickEdit++.ico"

    def load_config(self):
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
            self.save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()

        try:
            # 读取配置文件
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)

            # 合并默认配置，确保所有必要字段都存在
            return merge_configs(DEFAULT_CONFIG, config)
        except (json.JSONDecodeError, IOError) as e:
            # 配置文件解析失败或读取错误，返回默认配置
            messagebox.showerror(
                "配置文件错误", f"配置文件读取失败，已返回默认配置\n错误信息: {str(e)}"
            )
            return DEFAULT_CONFIG.copy()

    def save_config(self, config=None):
        """
        保存配置到文件

        Args:
            config (dict, optional): 要保存的配置字典，如果为None则保存当前配置

        Returns:
            bool: 是否保存成功

        说明：
            - 确保配置文件所在目录存在
            - 使用UTF-8编码保存
        """
        try:
            # 使用传入的配置或当前配置
            config_to_save = config if config is not None else self.config

            # 确保用户家目录存在（理论上总是存在的）
            os.makedirs(str(Path.home()), exist_ok=True)

            # 保存配置文件
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(config_to_save, f, ensure_ascii=False, indent=2)

            # 如果保存的是当前配置，则更新内部状态
            if config is None:
                self.config = config_to_save

            return True
        except IOError as e:
            # 保存失败
            print(f"配置文件保存失败: {e}")
            return False

    def get(self, key_path, default=None):
        """
        获取配置项

        Args:
            key_path (str): 配置键路径，如 "app.theme_mode" 或 "text_editor.font_size"
            default: 默认值，如果配置项不存在则返回

        Returns:
            配置值或默认值
        """
        keys = key_path.split(".")
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path, value):
        """
        设置配置项

        Args:
            key_path (str): 配置键路径，如 "app.theme_mode" 或 "text_editor.font_size"
            value: 配置值

        Returns:
            bool: 是否设置成功
        """
        keys = key_path.split(".")
        config = self.config

        # 遍历除最后一个键外的所有键
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            elif not isinstance(config[key], dict):
                return False
            config = config[key]

        # 设置最后一个键的值
        config[keys[-1]] = value
        return True

    def get_component_config(self, component_name):
        """
        获取组件配置

        Args:
            component_name (str): 组件名称，如 "app", "text_editor", "toolbar" 等

        Returns:
            dict: 组件配置字典
        """
        return self.get(component_name, {})

    def set_component_config(self, component_name, config_dict):
        """
        设置组件配置

        Args:
            component_name (str): 组件名称，如 "app", "text_editor", "toolbar" 等
            config_dict (dict): 组件配置字典

        Returns:
            bool: 是否设置成功
        """
        return self.set(component_name, config_dict)

    def get_font_config(self, component_name):
        """
        获取组件字体配置

        Args:
            component_name (str): 组件名称，如 "text_editor", "toolbar", "menu_bar", "status_bar"

        Returns:
            dict: 字体配置字典，包含 font, font_size, font_bold
        """
        component_config = self.get_component_config(component_name)
        if not component_config:
            return {}

        return {
            "font": component_config.get("font", "Microsoft YaHei UI"),
            "font_size": component_config.get("font_size", 12),
            "font_bold": component_config.get("font_bold", False),
        }

    def set_font_config(self, component_name, font_config):
        """
        设置组件字体配置

        Args:
            component_name (str): 组件名称，如 "text_editor", "toolbar", "menu_bar", "status_bar"
            font_config (dict): 字体配置字典，包含 font, font_size, font_bold

        Returns:
            bool: 是否设置成功
        """
        component_config = self.get_component_config(component_name)
        if not component_config:
            component_config = {}

        component_config["font"] = font_config.get("font", "Microsoft YaHei UI")
        component_config["font_size"] = font_config.get("font_size", 12)
        component_config["font_bold"] = font_config.get("font_bold", False)

        return self.set_component_config(component_name, component_config)

    def reset(self):
        """
        重置配置为默认值

        Returns:
            bool: 是否重置成功
        """
        self.config = DEFAULT_CONFIG.copy()
        return self.save_config()

    def get_full_config(self):
        """
        获取完整配置字典

        Returns:
            dict: 完整配置字典的副本
        """
        return self.config.copy()

    def get_recent_files(self):
        """
        获取最近打开的文件列表

        Returns:
            list: 最近打开的文件路径列表
        """
        return self.get("recent_files.history", [])

    def add_recent_file(self, file_path):
        """
        添加文件到最近打开列表

        Args:
            file_path (str): 文件路径

        Returns:
            bool: 是否添加成功
        """
        if not file_path or not os.path.exists(file_path):
            return False

        recent_files = self.get_recent_files()
        max_items = self.get("recent_files.max_items", 10)

        # 如果文件已存在于列表中，先移除
        if file_path in recent_files:
            recent_files.remove(file_path)

        # 添加到列表开头
        recent_files.insert(0, file_path)

        # 限制列表长度
        if len(recent_files) > max_items:
            recent_files = recent_files[:max_items]

        # 更新配置
        self.set("recent_files.history", recent_files)
        return self.save_config()

    def clear_recent_files(self):
        """
        清空最近打开的文件列表

        Returns:
            bool: 是否清空成功
        """
        self.set("recent_files.history", [])
        return self.save_config()

    def remove_recent_file(self, file_path):
        """
        从最近打开文件列表中移除指定文件

        Args:
            file_path: 要移除的文件路径

        Returns:
            bool: 是否移除成功
        """
        recent_files = self.get_recent_files()
        if file_path in recent_files:
            recent_files.remove(file_path)
            self.set("recent_files.history", recent_files)
            return self.save_config()
        return False


# 创建全局配置管理器实例
config_manager = ConfigManager()
