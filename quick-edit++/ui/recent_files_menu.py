#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
最近打开文件菜单组件
负责显示和处理最近打开的文件列表
"""

import os
import tkinter as tk
from tkinter import messagebox
from config.config_manager import config_manager


class RecentFilesMenu:
    """
    最近打开文件菜单类
    负责创建和管理最近打开文件的子菜单
    """

    def __init__(self, root, parent_menu, on_open_file_callback):
        """
        初始化最近打开文件菜单

        Args:
            root: 主应用实例
            parent_menu: 父菜单对象（通常是文件菜单）
            on_open_file_callback: 打开文件的回调函数
        """
        self.root = root
        self.parent_menu = parent_menu
        self.on_open_file_callback = on_open_file_callback
        self.recent_menu = None

    def create_recent_files_menu(self):
        """
        创建最近打开文件的子菜单

        Returns:
            tk.Menu: 创建的最近文件子菜单
        """
        # 检查最近文件功能是否启用
        if not config_manager.get("recent_files.enabled", True):
            return None

        # 获取菜单栏字体配置
        menu_font_config = config_manager.get_font_config("menu_bar")
        menu_font = menu_font_config.get("font", "Microsoft YaHei UI")
        menu_font_size = menu_font_config.get("font_size", 12)
        menu_font_bold = menu_font_config.get("font_bold", False)

        # 创建字体元组
        menu_font_tuple = (
            menu_font,
            menu_font_size,
            "bold" if menu_font_bold else "normal",
        )

        # 创建子菜单，使用配置的字体
        self.recent_menu = tk.Menu(self.parent_menu, tearoff=0, font=menu_font_tuple)

        # 添加上下文菜单项
        self._update_recent_files_menu()

        # 将子菜单添加到父菜单
        self.parent_menu.add_cascade(label="最近打开", menu=self.recent_menu)

        return self.recent_menu

    def _update_recent_files_menu(self):
        """
        更新最近打开文件菜单的内容
        清除现有项目并添加当前的最近文件列表
        """
        if not self.recent_menu:
            return

        # 清除所有现有菜单项
        self.recent_menu.delete(0, tk.END)

        # 获取最近打开的文件列表
        recent_files = config_manager.get_recent_files()

        # 如果没有最近文件，添加禁用的提示项
        if not recent_files:
            self.recent_menu.add_command(label="无最近打开的文件", state="disabled")
            return

        # 添加最近文件项
        for i, file_path in enumerate(recent_files):
            # 限制显示的文件名长度，过长时截断
            display_name = os.path.basename(file_path)
            full_display = f"{i+1}. {display_name} ({file_path})"

            # 确保文件名不超过80个字符（避免菜单过宽）
            if len(full_display) > 80:
                # 保留序号和文件名，截断路径部分
                path_part = f"...{file_path[-30:]}"
                full_display = f"{i+1}. {display_name} ({path_part})"

            # 添加菜单项，绑定点击事件
            self.recent_menu.add_command(
                label=full_display,
                command=lambda fp=file_path: self._on_recent_file_click(fp),
            )

        # 添加分隔符和清除历史菜单项
        self.recent_menu.add_separator()
        self.recent_menu.add_command(label="清除历史", command=self._clear_recent_files)

    def _on_recent_file_click(self, file_path):
        """
        当点击最近文件菜单项时的处理函数

        Args:
            file_path: 点击的文件路径
        """
        # 检查文件是否存在
        if not os.path.exists(file_path):
            # 任务5：文件不存在时的弹窗提示
            result = messagebox.askyesno(
                "文件不存在",
                f"文件 '{os.path.basename(file_path)}' 不存在或已被移动。\n\n是否从最近打开列表中移除？",
            )

            # 如果用户确认移除，则从最近列表中删除
            if result:
                self._remove_file_from_recent(file_path)
            return

        # 调用回调函数打开文件
        if self.on_open_file_callback:
            self.on_open_file_callback(file_path)

    def _remove_file_from_recent(self, file_path):
        """
        从最近打开列表中移除指定文件

        Args:
            file_path: 要移除的文件路径
        """
        # 使用配置管理器提供的方法移除文件
        if config_manager.remove_recent_file(file_path):
            # 移除成功后更新菜单显示
            self._update_recent_files_menu()

    def _clear_recent_files(self):
        """
        清除所有最近打开的文件历史
        """
        # 确认对话框
        result = messagebox.askyesno("确认操作", "确定要清除所有最近打开的文件历史吗？")

        if result:
            # 调用配置管理器的方法清空历史
            config_manager.clear_recent_files()
            # 更新菜单显示
            self._update_recent_files_menu()

    def refresh(self):
        """
        刷新最近文件菜单
        当最近文件列表发生变化时调用此方法
        """
        self._update_recent_files_menu()
