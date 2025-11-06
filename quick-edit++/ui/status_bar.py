#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
状态栏界面模块
"""

import customtkinter as ctk


class StatusBar(ctk.CTkFrame):
    """状态栏类"""
    
    def __init__(self, parent):
        """初始化状态栏"""
        super().__init__(parent)
        
        # 设置状态栏高度
        self.configure(height=25)
        
        # 初始化文件信息
        self.filename = None
        self.encoding = "UTF-8"
        self.line_ending = "LF"
        self.auto_save_interval = 30  # 默认自动保存间隔30秒
        self.auto_save_enabled = True  # 默认启用自动保存
        
        # 配置网格布局权重
        self.grid_columnconfigure(0, weight=1)  # 左侧
        self.grid_columnconfigure(1, weight=1)  # 中间
        self.grid_columnconfigure(2, weight=1)  # 右侧
        
        # 创建左侧标签（行号信息和文件编辑状态）
        self.left_label = ctk.CTkLabel(
            self,
            text="就绪 | 第1行 | 第1列",
            anchor="w",
            font=("Microsoft YaHei", 12)
        )
        self.left_label.grid(row=0, column=0, padx=10, pady=2, sticky="w")
        
        # 创建中间标签（自动保存提示）- 真正居中
        self.center_label = ctk.CTkLabel(
            self,
            text=f"自动保存: 从未(间隔{self.auto_save_interval}秒)",
            anchor="center",
            font=("Microsoft YaHei", 12)
        )
        self.center_label.grid(row=0, column=1, padx=10, pady=2, sticky="ew")
        
        # 创建右侧标签（文件名、编码和换行符类型）
        self.right_label = ctk.CTkLabel(
            self,
            text=f"{self.encoding} | {self.line_ending}",
            anchor="e",
            font=("Microsoft YaHei", 12)
        )
        self.right_label.grid(row=0, column=2, padx=10, pady=2, sticky="e")
        
    def set_status_info(self, status="就绪", row=1, col=1, total_chars=None, selected_chars=None, selected_lines=None):
        """设置左侧状态信息（行号信息和文件编辑状态）"""
        if total_chars is None and selected_chars is None and selected_lines is None:
            # 默认状态
            text = f"{status} | 第{row}行 | 第{col}列"
        elif selected_chars is None and selected_lines is None:
            # 有总字符数但无选中内容
            text = f"{status} | 第{row}行 | 第{col}列 | 总字符数{total_chars}"
        else:
            # 有选中内容
            selection_text = ""
            if selected_chars is not None:
                selection_text += f"已选中{selected_chars}个字符"
            if selected_lines is not None and selected_lines > 1:
                selection_text += f"({selected_lines}行)"
            text = f"{status} | 第{row}行 | 第{col}列 | 总字符数{total_chars} | {selection_text}"
            
        self.left_label.configure(text=text)
        
    def set_auto_save_info(self, status="从未"):
        """
        设置中间自动保存信息
        status参数可以是以下值之一:
        - "禁用": 自动保存被禁用
        - "从未": 从未运行过自动保存
        - "成功": 自动保存成功
        - 其他时间字符串: 上次保存的具体时间
        """
        if not self.auto_save_enabled:
            text = "自动保存: 已禁用"
        elif status == "禁用":
            text = "自动保存: 已禁用"
        elif status == "从未":
            text = f"自动保存: 从未(间隔{self.auto_save_interval}秒)"
        elif status == "成功":
            text = f"自动保存: 成功(间隔{self.auto_save_interval}秒)"
        else:
            # 显示具体的上次保存时间
            text = f"自动保存: {status}(间隔{self.auto_save_interval}秒)"
            
        self.center_label.configure(text=text)
        
    def set_file_info(self, filename=None, encoding=None, line_ending=None):
        """设置右侧文件信息（文件名、编码和换行符类型）"""
        if filename is not None:
            self.filename = filename
        if encoding is not None:
            self.encoding = encoding
        if line_ending is not None:
            self.line_ending = line_ending
            
        if self.filename is None:
            text = f"{self.encoding} | {self.line_ending}"
        else:
            text = f"{self.filename} | {self.encoding} | {self.line_ending}"
            
        self.right_label.configure(text=text)
        
    def set_auto_save_interval(self, interval):
        """设置自动保存间隔"""
        self.auto_save_interval = interval
        # 更新显示
        self.set_auto_save_info()
        
    def set_auto_save_enabled(self, enabled):
        """设置自动保存是否启用"""
        self.auto_save_enabled = enabled
        # 更新显示
        if enabled:
            self.set_auto_save_info("从未")
        else:
            self.set_auto_save_info("禁用")