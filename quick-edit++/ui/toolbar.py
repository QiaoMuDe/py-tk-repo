#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
工具栏界面模块
"""

import customtkinter as ctk
from config.config_manager import config_manager
from ui.find_replace_dialog import show_find_replace_dialog


class Toolbar(ctk.CTkFrame):
    """工具栏类"""

    def __init__(self, parent):
        """初始化工具栏"""
        super().__init__(parent, height=50, corner_radius=0)

        # 保存对父窗口的引用
        self.parent = parent

        # 获取工具栏字体配置
        font_config = config_manager.get_font_config("toolbar")
        self.button_font = (
            font_config.get("font", "Microsoft YaHei"),
            font_config.get("font_size", 12),
            "bold" if font_config.get("font_bold", False) else "normal",
        )

        # 创建工具栏按钮
        self._create_buttons()

    def _create_buttons(self):
        """创建工具栏按钮"""
        # 新建按钮
        self.new_button = ctk.CTkButton(
            self,
            text="新建",
            width=60,
            height=30,
            font=self.button_font,
            command=self.parent.new_file,
        )
        self.new_button.pack(side="left", padx=2, pady=10)

        # 打开按钮
        self.open_button = ctk.CTkButton(
            self,
            text="打开",
            width=60,
            height=30,
            font=self.button_font,
            command=self.parent.open_file,
        )
        self.open_button.pack(side="left", padx=2, pady=10)

        # 保存按钮
        self.save_button = ctk.CTkButton(
            self,
            text="保存",
            width=60,
            height=30,
            font=self.button_font,
            command=self.parent.save_file,
        )
        self.save_button.pack(side="left", padx=2, pady=10)

        # 另存为按钮
        self.save_as_button = ctk.CTkButton(
            self,
            text="另存为",
            width=70,
            height=30,
            font=self.button_font,
            command=self.parent.save_file_as,
        )
        self.save_as_button.pack(side="left", padx=2, pady=10)

        # 关闭按钮
        self.close_button = ctk.CTkButton(
            self,
            text="关闭",
            width=60,
            height=30,
            font=self.button_font,
            command=self.parent.close_file,
        )
        self.close_button.pack(side="left", padx=2, pady=10)

        # 只读按钮
        self.readonly_button = ctk.CTkButton(
            self,
            text="只读",
            width=60,
            height=30,
            font=self.button_font,
            command=self.parent.toggle_read_only,
        )
        self.readonly_button.pack(side="left", padx=2, pady=10)

        # 分隔符
        separator = ctk.CTkFrame(self, width=1, height=30, fg_color="#999999")
        separator.pack(side="left", padx=10, pady=10, fill="y")

        # 撤销按钮
        self.undo_button = ctk.CTkButton(
            self,
            text="撤销",
            width=60,
            height=30,
            font=self.button_font,
            command=self.parent.undo,
        )
        self.undo_button.pack(side="left", padx=2, pady=10)

        # 重做按钮
        self.redo_button = ctk.CTkButton(
            self,
            text="重做",
            width=60,
            height=30,
            font=self.button_font,
            command=self.parent.redo,
        )
        self.redo_button.pack(side="left", padx=2, pady=10)

        # 分隔符
        separator2 = ctk.CTkFrame(self, width=1, height=30, fg_color="#999999")
        separator2.pack(side="left", padx=10, pady=10, fill="y")

        # 剪切按钮
        self.cut_button = ctk.CTkButton(
            self,
            text="剪切",
            width=60,
            height=30,
            font=self.button_font,
            command=self.parent.cut,
        )
        self.cut_button.pack(side="left", padx=2, pady=10)

        # 复制按钮
        self.copy_button = ctk.CTkButton(
            self,
            text="复制",
            width=60,
            height=30,
            font=self.button_font,
            command=self.parent.copy,
        )
        self.copy_button.pack(side="left", padx=2, pady=10)

        # 粘贴按钮
        self.paste_button = ctk.CTkButton(
            self,
            text="粘贴",
            width=60,
            height=30,
            font=self.button_font,
            command=self.parent.paste,
        )
        self.paste_button.pack(side="left", padx=2, pady=10)

        # 分隔符
        separator3 = ctk.CTkFrame(self, width=1, height=30, fg_color="#999999")
        separator3.pack(side="left", padx=10, pady=10, fill="y")

        # 查找替换按钮
        self.find_replace_button = ctk.CTkButton(
            self,
            text="查找替换",
            width=80,
            height=30,
            font=self.button_font,
            command=lambda: show_find_replace_dialog(
                self.parent, self.parent.text_area
            ),
        )
        self.find_replace_button.pack(side="left", padx=2, pady=10)

        # 分隔符
        separator4 = ctk.CTkFrame(self, width=1, height=30, fg_color="#999999")
        separator4.pack(side="left", padx=10, pady=10, fill="y")

        # 全屏按钮
        self.fullscreen_button = ctk.CTkButton(
            self,
            text="全屏",
            width=60,
            height=30,
            font=self.button_font,
            command=lambda: self.toggle_fullscreen(),
        )
        self.fullscreen_button.pack(side="left", padx=2, pady=10)

        # 退出按钮
        self.exit_button = ctk.CTkButton(
            self,
            text="退出",
            width=60,
            height=30,
            font=self.button_font,
            command=self.parent._on_closing,
        )
        self.exit_button.pack(side="left", padx=2, pady=10)

    def toggle_fullscreen(self, switch_state=True):
        """
        切换全屏模式
        切换应用程序窗口的全屏/窗口模式状态

        Args:
            switch_state (bool): 是否需要翻转状态，默认为True
                                True - 切换状态（用于快捷键和按钮）
                                False - 应用当前状态（用于菜单点击）

        Returns:
            bool: 切换后的全屏状态
        """
        if switch_state:
            # 获取当前全屏状态
            current_state = self.parent.fullscreen_var.get()
            # 计算新状态（当前状态的取反）
            new_state = not current_state
            # 设置新状态
            self.parent.fullscreen_var.set(new_state)
        else:
            # 应用当前状态（不翻转）
            new_state = self.parent.fullscreen_var.get()

        # 设置窗口全屏属性
        if new_state:
            # 保存当前窗口状态
            self.parent.normal_geometry = self.parent.geometry()
            # 设置全屏
            self.parent.attributes("-fullscreen", True)
            # 对于某些平台可能需要额外处理
            self.parent.update_idletasks()
        else:
            # 恢复正常窗口状态
            self.parent.attributes("-fullscreen", False)
            # 恢复原来的窗口大小和位置
            if self.parent.normal_geometry:
                self.parent.geometry(self.parent.normal_geometry)
            # 确保窗口可见
            self.parent.update_idletasks()

        # 更新按钮文本
        self.fullscreen_button.configure(text="退出全屏" if new_state else "全屏")

        return new_state
