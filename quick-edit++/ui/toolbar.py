#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
工具栏界面模块
"""

import customtkinter as ctk


class Toolbar(ctk.CTkFrame):
    """工具栏类"""
    
    def __init__(self, parent):
        """初始化工具栏"""
        super().__init__(parent)
        
        # 创建工具栏按钮
        self._create_buttons()
        
    def _create_buttons(self):
        """创建工具栏按钮"""
        # 新建按钮
        self.new_button = ctk.CTkButton(
            self,
            text="新建",
            width=60,
            command=lambda: print("新建文件")
        )
        self.new_button.pack(side="left", padx=5, pady=5)
        
        # 打开按钮
        self.open_button = ctk.CTkButton(
            self,
            text="打开",
            width=60,
            command=lambda: print("打开文件")
        )
        self.open_button.pack(side="left", padx=5, pady=5)
        
        # 保存按钮
        self.save_button = ctk.CTkButton(
            self,
            text="保存",
            width=60,
            command=lambda: print("保存文件")
        )
        self.save_button.pack(side="left", padx=5, pady=5)
        
        # 分隔符
        separator = ctk.CTkFrame(self, width=2, height=30, fg_color="gray")
        separator.pack(side="left", padx=10, pady=5, fill="y")
        
        # 撤销按钮
        self.undo_button = ctk.CTkButton(
            self,
            text="撤销",
            width=60,
            command=lambda: print("撤销操作")
        )
        self.undo_button.pack(side="left", padx=5, pady=5)
        
        # 重做按钮
        self.redo_button = ctk.CTkButton(
            self,
            text="重做",
            width=60,
            command=lambda: print("重做操作")
        )
        self.redo_button.pack(side="left", padx=5, pady=5)
        
        # 分隔符
        separator2 = ctk.CTkFrame(self, width=2, height=30, fg_color="gray")
        separator2.pack(side="left", padx=10, pady=5, fill="y")
        
        # 剪切按钮
        self.cut_button = ctk.CTkButton(
            self,
            text="剪切",
            width=60,
            command=lambda: print("剪切")
        )
        self.cut_button.pack(side="left", padx=5, pady=5)
        
        # 复制按钮
        self.copy_button = ctk.CTkButton(
            self,
            text="复制",
            width=60,
            command=lambda: print("复制")
        )
        self.copy_button.pack(side="left", padx=5, pady=5)
        
        # 粘贴按钮
        self.paste_button = ctk.CTkButton(
            self,
            text="粘贴",
            width=60,
            command=lambda: print("粘贴")
        )
        self.paste_button.pack(side="left", padx=5, pady=5)