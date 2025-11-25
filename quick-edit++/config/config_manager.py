#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理模块，负责配置文件的加载和保存
"""

import os
import json
from tkinter import messagebox
from pathlib import Path
from loguru import logger

# 应用程序常量
APP_VERSION = "v0.0.29"  # 版本号
PROJECT_URL = "https://gitee.com/MM-Q/py-tk-repo.git"  # 项目地址

# 创建应用程序配置目录
APP_CONFIG_DIR = os.path.join(str(Path.home()), ".QuickEditPlus")

# 默认配置文件路径: 配置目录下的config.json
CONFIG_FILE_NAME = "config.json"
CONFIG_PATH = os.path.join(APP_CONFIG_DIR, CONFIG_FILE_NAME)

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
        "monitoring_enabled": True,  # 是否启用文件变更监控
        "silent_reload": False,  # 是否静默自动重载（False=弹窗提示，True=静默重载）
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
        "line_number_bg_color": "#cccccc",  # 行号背景色（浅色模式）
        "line_number_bg_color_dark": "#2b2b2b",  # 行号背景色（深色模式）
        "line_number_font_color": "#2b91af",  # 行号字体颜色
        "max_undo": 50,  # 最大撤销次数
        "show_line_numbers": True,  # 是否显示行号
        "auto_increment_number": True,  # 是否启用自动递增编号功能
        "highlight_current_line": True,  # 是否启用光标所在行高亮
        "cursor_width": 5,  # 光标宽度（像素）
        "tab_width": 1,  # 制表符宽度（空格数）
        "use_spaces_for_tab": False,  # 是否使用空格代替制表符
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
        "disable_highlight_file_size": 1048576,  # 禁用语法高亮的文件大小阈值 (1MB)
        "debounce_delay": 100,  # 语法高亮防抖延迟时间 (毫秒)
        "visible_line_context": 10,  # 可见行模式下，上下扩展的行数
    },
    # 日志配置
    "logging": {
        "log_dir": os.path.join(
            APP_CONFIG_DIR, "logs"
        ),  # 日志目录：配置目录下的logs子目录
        "log_file": "app.log",  # 日志文件名
        "log_level": "WARNING",  # 日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL
        "rotation_size": "5 MB",  # 日志文件旋转大小
        "retention_time": "7 days",  # 日志文件保留时间
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

        logger.info("config manager initialized successfully!")
        logger.info(f"config file path: {CONFIG_PATH}")

    def load_config(self):
        """
        加载配置文件

        Returns:
            dict: 配置字典

        说明：
            - 如果配置目录不存在，先创建配置目录
            - 如果配置文件不存在，先保存默认配置，然后返回默认配置
            - 如果配置文件存在但解析失败，返回默认配置
        """
        # 确保配置目录存在
        if not os.path.exists(APP_CONFIG_DIR):
            os.makedirs(APP_CONFIG_DIR, exist_ok=True)

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
            logger.error(f"配置文件加载失败: {str(e)}，使用默认配置")
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
            - 确保配置目录存在
            - 使用UTF-8编码保存
        """
        try:
            # 使用传入的配置或当前配置
            config_to_save = config if config is not None else self.config

            # 确保配置目录存在
            os.makedirs(APP_CONFIG_DIR, exist_ok=True)

            # 保存配置文件
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(config_to_save, f, ensure_ascii=False, indent=2)

            # 如果保存的是当前配置，则更新内部状态
            if config is None:
                self.config = config_to_save
            return True

        except IOError as e:
            # 保存失败
            logger.error(f"配置文件保存失败: {e}")
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
                logger.warning(
                    f"配置路径 {key_path} 中间节点 {key} 不是字典类型，设置失败"
                )
                return False
            config = config[key]

        # 设置最后一个键的值
        old_value = config.get(keys[-1]) if keys[-1] in config else None
        config[keys[-1]] = value

        # 记录配置变更
        if old_value is None:
            logger.debug(f"新增配置项 {key_path} = {value}")
        else:
            logger.debug(f"更新配置项 {key_path}: {old_value} -> {value}")

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
        logger.info("开始重置配置为默认值")
        self.config = DEFAULT_CONFIG.copy()
        result = self.save_config()

        if result:
            logger.info("配置重置成功并已保存")
        else:
            logger.error("配置重置失败，无法保存到文件")

        return result

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
            logger.warning(f"添加最近文件失败，文件路径无效或文件不存在: {file_path}")
            return False

        recent_files = self.get_recent_files()
        max_items = self.get("recent_files.max_items", 10)
        file_existed = file_path in recent_files

        # 如果文件已存在于列表中，先移除
        if file_existed:
            recent_files.remove(file_path)
            logger.debug(f"文件已存在于最近列表中，更新位置: {file_path}")

        # 添加到列表开头
        recent_files.insert(0, file_path)

        # 限制列表长度
        if len(recent_files) > max_items:
            removed_files = recent_files[max_items:]
            recent_files = recent_files[:max_items]
            logger.debug(f"最近文件列表超出限制，移除文件: {removed_files}")

        # 更新配置
        self.set("recent_files.history", recent_files)
        result = self.save_config()

        if result:
            action = "更新" if file_existed else "添加"
            logger.info(f"{action}最近文件成功: {file_path}")
        else:
            logger.error(f"保存最近文件列表失败: {file_path}")

        return result

    def clear_recent_files(self):
        """
        清空最近打开的文件列表

        Returns:
            bool: 是否清空成功
        """
        recent_files = self.get_recent_files()
        file_count = len(recent_files)

        if file_count == 0:
            logger.debug("最近文件列表已经为空，无需清空")
            return True

        self.set("recent_files.history", [])
        result = self.save_config()

        if result:
            logger.info(f"成功清空最近文件列表，共移除 {file_count} 个文件")
        else:
            logger.error("清空最近文件列表失败，无法保存配置")

        return result

    def remove_recent_file(self, file_path):
        """
        从最近打开文件列表中移除指定文件

        Args:
            file_path: 要移除的文件路径

        Returns:
            bool: 是否移除成功
        """
        recent_files = self.get_recent_files()

        if file_path not in recent_files:
            logger.debug(f"文件不在最近列表中，无需移除: {file_path}")
            return False

        recent_files.remove(file_path)
        self.set("recent_files.history", recent_files)
        result = self.save_config()

        if result:
            logger.info(f"成功从最近文件列表中移除文件: {file_path}")
        else:
            logger.error(f"移除最近文件失败，无法保存配置: {file_path}")

        return result


# 创建全局配置管理器实例
config_manager = ConfigManager()
