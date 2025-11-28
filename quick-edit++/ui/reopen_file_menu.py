#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
重新载入文件菜单组件
负责处理使用不同编码重新打开当前文件的功能
"""

import tkinter as tk
from tkinter import messagebox
from config.config_manager import config_manager
from ui.utils import get_supported_encodings
from loguru import logger


class ReopenFileMenu:
    """
    重新载入文件菜单类
    负责创建和管理重新载入文件的子菜单
    """

    def __init__(self, root, parent_menu, on_reopen_file_callback):
        """
        初始化重新载入文件菜单

        Args:
            root: 主应用实例
            parent_menu: 父菜单对象（通常是文件菜单）
            on_reopen_file_callback: 重新打开文件的回调函数
        """
        self.root = root
        self.parent_menu = parent_menu
        self.on_reopen_file_callback = on_reopen_file_callback
        self.reopen_menu = None

    def create_reopen_file_menu(self):
        """
        创建重新载入文件的子菜单

        Returns:
            tk.Menu: 创建的重新载入文件子菜单
        """
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
        self.reopen_menu = tk.Menu(self.parent_menu, tearoff=0, font=menu_font_tuple)

        # 添加使用默认编码打开的菜单项
        self.reopen_menu.add_command(
            label="使用默认编码打开",
            command=self._reopen_with_default_encoding,
            font=menu_font_tuple,
        )

        # 添加使用UTF-8编码打开的菜单项
        self.reopen_menu.add_command(
            label="使用UTF-8编码打开",
            command=lambda: self._reopen_with_encoding("UTF-8"),
            font=menu_font_tuple,
        )

        # 添加使用GBK编码打开的菜单项
        self.reopen_menu.add_command(
            label="使用GBK编码打开",
            command=lambda: self._reopen_with_encoding("GBK"),
            font=menu_font_tuple,
        )

        # 添加分隔符
        self.reopen_menu.add_separator()

        # 创建指定编码的子菜单
        self.specified_encoding_menu = tk.Menu(
            self.reopen_menu, tearoff=0, font=menu_font_tuple
        )
        self.reopen_menu.add_cascade(
            label="使用指定编码打开",
            menu=self.specified_encoding_menu,
            font=menu_font_tuple,
        )

        # 填充指定编码菜单
        self._populate_specified_encoding_menu(menu_font_tuple)

        # 将子菜单添加到父菜单
        # 获取即将添加的菜单项索引
        self.menu_index = self.parent_menu.index(tk.END) + 1
        self.parent_menu.add_cascade(label="重新载入", menu=self.reopen_menu)

        return self.reopen_menu

    def _populate_specified_encoding_menu(self, menu_font_tuple):
        """
        填充指定编码菜单的内容

        Args:
            menu_font_tuple: 菜单字体元组
        """
        # 获取支持的编码列表
        encodings = get_supported_encodings()
        # 按字母顺序排序
        encodings_sorted = sorted(encodings, key=lambda x: x.upper())

        # 为了避免菜单过长，将编码分成几组
        group_size = 20  # 每组20个编码
        for i in range(0, len(encodings_sorted), group_size):
            group_name = f"{encodings_sorted[i]} - {encodings_sorted[min(i+group_size-1, len(encodings_sorted)-1)]}"
            group_menu = tk.Menu(
                self.specified_encoding_menu, tearoff=0, font=menu_font_tuple
            )
            self.specified_encoding_menu.add_cascade(
                label=group_name, menu=group_menu, font=menu_font_tuple
            )

            for j in range(i, min(i + group_size, len(encodings_sorted))):
                enc = encodings_sorted[j]
                group_menu.add_command(
                    label=enc,
                    command=lambda e=enc: self._reopen_with_encoding(e),
                    font=menu_font_tuple,
                )

    def _reopen_with_default_encoding(self):
        """
        使用默认编码重新载入当前文件
        """
        default_encoding = config_manager.get("app.default_encoding", "UTF-8")
        self._reopen_with_encoding(default_encoding)

    def _reopen_with_encoding(self, encoding):
        """
        使用指定编码重新载入当前文件

        Args:
            encoding (str): 要使用的文件编码
        """
        # 检查是否有当前打开的文件
        if not self.root.current_file_path:
            # messagebox.showinfo("提示", "没有当前打开的文件，无法重新载入。")
            self.root.nm.show_info(message="没有当前打开的文件，无法重新载入。")
            return

        # 调用回调函数重新载入文件
        if self.on_reopen_file_callback:
            self.on_reopen_file_callback(self.root.current_file_path, encoding)

    def update_menu_state(self):
        """
        更新菜单项的状态（启用/禁用）
        根据是否有当前打开的文件来决定菜单项是否可用
        """
        has_current_file = self.root.current_file_path

        # 设置菜单状态
        state = "normal" if has_current_file else "disabled"

        # 使用保存的索引直接禁用或启用整个重新打开菜单
        if self.parent_menu and self.menu_index is not None:
            try:
                self.parent_menu.entryconfig(self.menu_index, state=state)
            except tk.TclError:
                # 如果通过索引更新失败，打印错误信息
                logger.error(
                    f"Error updating menu state at index {self.menu_index}: {tk.TclError}"
                )
