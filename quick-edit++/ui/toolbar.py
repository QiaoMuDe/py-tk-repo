#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
工具栏界面模块
"""

import customtkinter as ctk
from config.config_manager import config_manager


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
            width=60,
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
            command=lambda: print("撤销操作"),
        )
        self.undo_button.pack(side="left", padx=2, pady=10)

        # 重做按钮
        self.redo_button = ctk.CTkButton(
            self,
            text="重做",
            width=60,
            height=30,
            font=self.button_font,
            command=lambda: print("重做操作"),
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
            command=lambda: print("剪切"),
        )
        self.cut_button.pack(side="left", padx=2, pady=10)

        # 复制按钮
        self.copy_button = ctk.CTkButton(
            self,
            text="复制",
            width=60,
            height=30,
            font=self.button_font,
            command=lambda: print("复制"),
        )
        self.copy_button.pack(side="left", padx=2, pady=10)

        # 粘贴按钮
        self.paste_button = ctk.CTkButton(
            self,
            text="粘贴",
            width=60,
            height=30,
            font=self.button_font,
            command=lambda: print("粘贴"),
        )
        self.paste_button.pack(side="left", padx=2, pady=10)

        # 分隔符
        separator3 = ctk.CTkFrame(self, width=1, height=30, fg_color="#999999")
        separator3.pack(side="left", padx=10, pady=10, fill="y")

        # 查找按钮
        self.find_button = ctk.CTkButton(
            self,
            text="查找",
            width=60,
            height=30,
            font=self.button_font,
            command=lambda: print("查找"),
        )
        self.find_button.pack(side="left", padx=2, pady=10)

        # 替换按钮
        self.replace_button = ctk.CTkButton(
            self,
            text="替换",
            width=60,
            height=30,
            font=self.button_font,
            command=lambda: print("替换"),
        )
        self.replace_button.pack(side="left", padx=2, pady=10)

        # 分隔符
        separator4 = ctk.CTkFrame(self, width=1, height=30, fg_color="#999999")
        separator4.pack(side="left", padx=10, pady=10, fill="y")

        # 退出按钮
        self.exit_button = ctk.CTkButton(
            self,
            text="退出",
            width=60,
            height=30,
            font=self.button_font,
            command=lambda: print("退出程序"),
        )
        self.exit_button.pack(side="left", padx=2, pady=10)
