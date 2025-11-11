#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
查找替换对话框模块
"""

import customtkinter as ctk
from config.config_manager import ConfigManager


class FindReplaceDialog:
    """
    查找替换对话框类
    
    提供查找和替换功能的用户界面
    """
    
    def __init__(self, parent, text_widget=None):
        """
        初始化查找替换对话框
        
        Args:
            parent: 父窗口
            text_widget: 文本编辑器控件，用于执行查找替换操作
        """
        self.parent = parent
        self.text_widget = text_widget
        self.config_manager = ConfigManager()
        
        # 获取组件默认字体配置
        self.font_family = self.config_manager.get("components.font", "Microsoft YaHei UI")
        self.font_size = 15
        self.font_bold = True
        
        # 存储输入框引用和框架引用
        self.find_entry = None
        self.replace_entry = None
        self.find_textbox = None
        self.replace_textbox = None
        self.find_frame = None
        self.replace_frame = None
        
        # 创建对话框窗口
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("查找和替换")
        self.dialog.geometry(f"500x360+{(self.dialog.winfo_screenwidth()//3)}+{(self.dialog.winfo_screenheight()//4)}")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 设置窗口关闭协议
        self.dialog.protocol("WM_DELETE_WINDOW", self._close_dialog)
        
        # 绑定ESC键关闭对话框
        self.dialog.bind("<Escape>", lambda e: self._close_dialog())
        
        # 创建UI组件
        self._create_widgets()
        
        # 等待对话框关闭
        self.dialog.wait_window()
    
    def _create_widgets(self):
        """创建对话框UI组件"""
        # 主框架
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 查找区域
        find_frame = ctk.CTkFrame(main_frame)
        find_frame.pack(fill="x", pady=(0, 10))
        self.find_frame = find_frame
        
        find_label = ctk.CTkLabel(
            find_frame,
            text="查找内容:",
            font=(self.font_family, self.font_size, "bold" if self.font_bold else "normal")
        )
        find_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.find_entry = ctk.CTkEntry(
            find_frame,
            font=(self.font_family, self.font_size),
            height=35
        )
        self.find_textbox = self.find_entry
        self.find_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # 创建选项容器，用于横向排列（直接放在查找区域内部）
        options_container = ctk.CTkFrame(find_frame)
        options_container.pack(fill="x", padx=10, pady=(0, 5))
        
        self.case_sensitive_var = ctk.BooleanVar(value=False)
        case_sensitive_check = ctk.CTkCheckBox(
            options_container,
            text="区分大小写",
            variable=self.case_sensitive_var,
            font=(self.font_family, self.font_size)
        )
        case_sensitive_check.pack(side="left", padx=(0, 20))
        
        self.whole_word_var = ctk.BooleanVar(value=False)
        whole_word_check = ctk.CTkCheckBox(
            options_container,
            text="全字匹配",
            variable=self.whole_word_var,
            font=(self.font_family, self.font_size)
        )
        whole_word_check.pack(side="left", padx=(0, 20))
        
        self.regex_var = ctk.BooleanVar(value=False)
        regex_check = ctk.CTkCheckBox(
            options_container,
            text="正则表达式",
            variable=self.regex_var,
            font=(self.font_family, self.font_size)
        )
        regex_check.pack(side="left", padx=(0, 20))
        
        # 替换区域
        replace_frame = ctk.CTkFrame(main_frame)
        replace_frame.pack(fill="x", pady=(0, 20))
        self.replace_frame = replace_frame
        
        replace_label = ctk.CTkLabel(
            replace_frame,
            text="替换为:",
            font=(self.font_family, self.font_size, "bold" if self.font_bold else "normal")
        )
        replace_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.replace_entry = ctk.CTkEntry(
            replace_frame,
            font=(self.font_family, self.font_size),
            height=35
        )
        self.replace_entry.pack(fill="x", padx=10, pady=(0, 10))
        self.replace_textbox = self.replace_entry
        
        # 按钮区域
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x")
        
        # 第一行按钮
        first_row_frame = ctk.CTkFrame(button_frame)
        first_row_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        find_prev_btn = ctk.CTkButton(
            first_row_frame,
            text="查找上一个",
            font=(self.font_family, self.font_size),
            command=self._find_previous
        )
        find_prev_btn.pack(side="left", padx=(0, 5))
        
        find_next_btn = ctk.CTkButton(
            first_row_frame,
            text="查找下一个",
            font=(self.font_family, self.font_size),
            command=self._find_next
        )
        find_next_btn.pack(side="left", padx=5)
        
        find_all_btn = ctk.CTkButton(
            first_row_frame,
            text="查找全部",
            font=(self.font_family, self.font_size),
            command=self._find_all
        )
        find_all_btn.pack(side="left", padx=5)
        
        # 第二行按钮
        second_row_frame = ctk.CTkFrame(button_frame)
        second_row_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        replace_btn = ctk.CTkButton(
            second_row_frame,
            text="替换",
            font=(self.font_family, self.font_size),
            command=self._replace
        )
        replace_btn.pack(side="left", padx=(0, 5))
        
        replace_all_btn = ctk.CTkButton(
            second_row_frame,
            text="替换全部",
            font=(self.font_family, self.font_size),
            command=self._replace_all
        )
        replace_all_btn.pack(side="left", padx=5)
        
        close_btn = ctk.CTkButton(
            second_row_frame,
            text="关闭",
            font=(self.font_family, self.font_size),
            command=self._close_dialog
        )
        close_btn.pack(side="right", padx=5)
    
    def get_find_text(self):
        """获取查找文本框的内容"""
        return self.find_textbox.get() if self.find_textbox else ""
    
    def get_replace_text(self):
        """获取替换文本框的内容"""
        return self.replace_textbox.get() if self.replace_textbox else ""
    
    def _find_previous(self):
        """查找上一个匹配项"""
        # TODO: 实现查找上一个的逻辑
        print("查找上一个")
    
    def _find_next(self):
        """查找下一个匹配项"""
        # TODO: 实现查找下一个的逻辑
        print("查找下一个")
    
    def _find_all(self):
        """查找所有匹配项"""
        # TODO: 实现查找全部的逻辑
        print("查找全部")
    
    def _replace(self):
        """替换当前匹配项"""
        # TODO: 实现替换的逻辑
        print("替换")
    
    def _replace_all(self):
        """替换所有匹配项"""
        # TODO: 实现替换全部的逻辑
        print("替换全部")
    
    def _close_dialog(self):
        """关闭对话框"""
        self.dialog.destroy()


def show_find_replace_dialog(parent, text_widget=None):
    """
    显示查找替换对话框
    
    Args:
        parent: 父窗口
        text_widget: 文本编辑器控件，用于执行查找替换操作
    """
    return FindReplaceDialog(parent, text_widget)