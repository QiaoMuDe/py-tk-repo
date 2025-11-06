#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
字体设置对话框模块
"""

import tkinter as tk
from tkinter import ttk, font
import customtkinter as ctk
from typing import Callable


class FontDialog:
    """
    字体设置对话框类
    
    功能：
    - 显示系统中所有可用字体
    - 提供字体搜索功能
    - 提供字体大小选择
    - 实时预览字体效果
    - 设置文本框的字体
    """
    
    def __init__(self, parent, text_widget=None, title="字体设置"):
        """
        初始化字体设置对话框
        
        Args:
            parent: 父窗口组件
            text_widget: 文本框组件引用
            title: 对话框标题
        """
        self.parent = parent
        self.text_widget = text_widget
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("700x500")  # 简化后的尺寸
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)  # 设置为主窗口的子窗口
        self.dialog.grab_set()  # 模态窗口
        
        # 初始字体设置
        self.current_font = {
            "family": "Microsoft YaHei",
            "size": 12
        }
        self.font_list = []
        self.filtered_fonts = []
        
        # 绑定确认和取消按钮的回调函数
        self.on_confirm = None
        
        # 初始化UI
        self._init_ui()
        
        # 加载系统字体
        self._load_system_fonts()
        
        # 默认选择第一个字体 - 使用标签高亮
        if self.filtered_fonts:
            self.font_listbox.tag_config("selected_font", background="#3a7ebf", foreground="white")
            self.font_listbox.tag_add("selected_font", "1.0", "1.end")
            self.font_listbox.see("1.0")
            self._update_preview()
        else:
            # 确保即使没有字体被选中也会更新预览
            self._update_preview()
    
    def _init_ui(self):
        """
        初始化用户界面（简化版）
        """
        # 整体布局使用网格布局
        self.dialog.grid_columnconfigure(0, weight=1)
        self.dialog.grid_rowconfigure(0, weight=1)
        self.dialog.grid_rowconfigure(1, weight=1)
        
        # 上半部分：字体和字体大小设置区域
        top_frame = ctk.CTkFrame(self.dialog)
        top_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_columnconfigure(1, weight=1)
        top_frame.grid_rowconfigure(0, weight=1)
        
        # 左侧：字体设置
        left_frame = ctk.CTkFrame(top_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(0, weight=0)
        left_frame.grid_rowconfigure(1, weight=0)
        left_frame.grid_rowconfigure(2, weight=1)
        
        # 字体标题
        font_label = ctk.CTkLabel(left_frame, text="字体", font=ctk.CTkFont(size=14))
        font_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        # 字体搜索区域
        search_frame = ctk.CTkFrame(left_frame)
        search_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=0)
        search_frame.grid_columnconfigure(0, weight=1)
        
        self.search_var = tk.StringVar()
        self.search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, placeholder_text="搜索字体...", font=ctk.CTkFont(size=12))
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.search_entry.bind("<KeyRelease>", self._on_search)
        
        self.search_button = ctk.CTkButton(search_frame, text="搜索", width=80, command=self._on_search, font=ctk.CTkFont(size=12))
        self.search_button.grid(row=0, column=1, padx=5, pady=5)
        
        # 字体列表 - 使用CTkTextbox替代tk.Listbox
        self.font_listbox = ctk.CTkTextbox(left_frame, wrap="none", font=ctk.CTkFont(family="Microsoft YaHei", size=12))
        self.font_listbox.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        
        # 滚动条 - 使用CTkScrollbar替代ttk.Scrollbar
        font_scrollbar = ctk.CTkScrollbar(left_frame, orientation="vertical", command=self.font_listbox.yview)
        font_scrollbar.grid(row=2, column=1, sticky="ns")
        self.font_listbox.configure(yscrollcommand=font_scrollbar.set)
        
        # 绑定列表选择事件 - 需要修改为适应CTkTextbox
        self.font_listbox.bind("<Button-1>", self._on_font_select)
        self.font_listbox.bind("<KeyRelease>", self._on_font_select)
        
        # 右侧：字体大小设置
        right_frame = ctk.CTkFrame(top_frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(0, weight=0)
        right_frame.grid_rowconfigure(1, weight=0)
        right_frame.grid_rowconfigure(2, weight=0)
        
        # 字体大小标题
        size_label = ctk.CTkLabel(right_frame, text="字体大小", font=ctk.CTkFont(size=16))
        size_label.grid(row=0, column=0, columnspan=3, sticky="w", padx=5, pady=5)
        
        # 字体大小输入框和按钮
        size_frame = ctk.CTkFrame(right_frame)
        size_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        size_frame.grid_columnconfigure(1, weight=1)
        
        # 减小字体按钮
        self.size_decrease_btn = ctk.CTkButton(
            size_frame, 
            text="-", 
            width=30, 
            command=self._decrease_font_size,
            font=ctk.CTkFont(size=18)
        )
        self.size_decrease_btn.grid(row=0, column=0, padx=5, pady=5)
        
        # 字体大小输入框
        self.size_var = tk.StringVar(value="12")
        self.size_entry = ctk.CTkEntry(
            size_frame, 
            textvariable=self.size_var, 
            width=60,
            font=ctk.CTkFont(size=16)
        )
        self.size_entry.grid(row=0, column=1, padx=5, pady=5)
        self.size_entry.bind("<KeyRelease>", self._on_size_change)
        
        # 增大字体按钮
        self.size_increase_btn = ctk.CTkButton(
            size_frame, 
            text="+", 
            width=30, 
            command=self._increase_font_size,
            font=ctk.CTkFont(size=18)
        )
        self.size_increase_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # 字体大小范围提示
        size_hint = ctk.CTkLabel(right_frame, text="范围: 8-72", font=ctk.CTkFont(size=14))
        size_hint.grid(row=2, column=0, columnspan=3, sticky="w", padx=5, pady=0)
        
        # 下半部分：预览区域
        bottom_frame = ctk.CTkFrame(self.dialog)
        bottom_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_rowconfigure(0, weight=0)
        bottom_frame.grid_rowconfigure(1, weight=1)
        bottom_frame.grid_rowconfigure(2, weight=0)
        
        # 预览标签
        preview_label = ctk.CTkLabel(bottom_frame, text="字体预览：", font=ctk.CTkFont(size=14))
        preview_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        # 使用CTkTextbox作为预览文本框
        self.preview_text = ctk.CTkTextbox(bottom_frame, wrap="word", height=100, font=ctk.CTkFont(family="Microsoft YaHei", size=12))
        self.preview_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # 插入预览文本
        self.preview_text.insert("0.0", "这是字体预览文本\nABCDEFGHIJKLMNOPQRSTUVWXYZ\nabcdefghijklmnopqrstuvwxyz\n1234567890\n!@#$%^&*()")
        self.preview_text.configure(state="disabled")
        
        # 按钮区域
        button_frame = ctk.CTkFrame(bottom_frame)
        button_frame.grid(row=2, column=0, sticky="e", padx=5, pady=10)
        
        self.ok_button = ctk.CTkButton(button_frame, text="确定", command=self._on_ok, font=ctk.CTkFont(size=12))
        self.ok_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.cancel_button = ctk.CTkButton(button_frame, text="取消", command=self._on_cancel, font=ctk.CTkFont(size=12))
        self.cancel_button.grid(row=0, column=1, padx=5, pady=5)
    
    def _load_system_fonts(self):
        """
        加载系统中所有可用的字体
        """
        try:
            # 获取系统中所有可用的字体
            available_fonts = font.families()
            
            # 按字母顺序排序
            self.font_list = sorted(available_fonts)
            self.filtered_fonts = self.font_list.copy()
            
            # 填充字体列表到CTkTextbox
            for i, font_name in enumerate(self.filtered_fonts):
                self.font_listbox.insert(f"{i+1}.0", f"{font_name}\n")
        except Exception as e:
            # 如果获取系统字体失败，使用一些常见字体作为备选
            fallback_fonts = ["Arial", "Helvetica", "Times New Roman", "Courier New", "Microsoft YaHei", "SimHei", "SimSun"]
            self.font_list = fallback_fonts
            self.filtered_fonts = fallback_fonts.copy()
            
            # 将备选字体添加到CTkTextbox中
            for i, font_name in enumerate(self.filtered_fonts):
                self.font_listbox.insert(f"{i+1}.0", f"{font_name}\n")
        
        # 默认选择第一个字体 - 使用标签高亮
        if self.filtered_fonts:
            self.font_listbox.tag_config("selected_font", background="#3a7ebf", foreground="white")
            self.font_listbox.tag_add("selected_font", "1.0", "1.end")
            self.font_listbox.see("1.0")
    
    def _decrease_font_size(self):
        """减小字体大小"""
        try:
            current_size = int(self.size_var.get())
            if current_size > 8:  # 最小字体大小为8
                self.size_var.set(str(current_size - 1))
                self._update_preview()
        except ValueError:
            self.size_var.set("12")
            self._update_preview()
    
    def _increase_font_size(self):
        """增大字体大小"""
        try:
            current_size = int(self.size_var.get())
            if current_size < 72:  # 最大字体大小为72
                self.size_var.set(str(current_size + 1))
                self._update_preview()
        except ValueError:
            self.size_var.set("12")
            self._update_preview()
    
    def _on_size_change(self, event=None):
        """处理字体大小输入变化"""
        try:
            size = int(self.size_var.get())
            if 8 <= size <= 72:  # 限制字体大小范围
                self._update_preview()
            else:
                # 如果超出范围，恢复为12
                self.size_var.set("12")
                self._update_preview()
        except ValueError:
            # 如果不是有效数字，恢复为12
            self.size_var.set("12")
            self._update_preview()
    
    def _on_font_select(self, event=None):
        """
        处理字体选择事件
        
        Args:
            event: 事件对象
        """
        # 获取光标位置
        cursor_pos = self.font_listbox.index(ctk.INSERT)
        line_num = int(cursor_pos.split('.')[0])
        
        # 确保行号在有效范围内
        if 1 <= line_num <= len(self.filtered_fonts):
            # 移除之前的选中标签
            self.font_listbox.tag_remove("selected_font", "1.0", tk.END)
            
            # 添加新的选中标签
            self.font_listbox.tag_config("selected_font", background="#3a7ebf", foreground="white")
            self.font_listbox.tag_add("selected_font", f"{line_num}.0", f"{line_num}.end")
            
            # 更新预览
            self._update_preview()
    
    def _on_search(self, event=None):
        """
        处理字体搜索
        
        Args:
            event: 事件对象（键盘事件）
        """
        search_text = self.search_var.get().lower()
        
        # 清空当前列表
        self.font_listbox.delete("1.0", tk.END)
        
        # 过滤字体列表
        self.filtered_fonts = [font_name for font_name in self.font_list if search_text in font_name.lower()]
        
        # 填充过滤后的字体列表到CTkTextbox
        for i, font_name in enumerate(self.filtered_fonts):
            self.font_listbox.insert(f"{i+1}.0", f"{font_name}\n")
        
        # 自动选择第一个匹配的字体
        if self.filtered_fonts:
            self.font_listbox.tag_config("selected_font", background="#3a7ebf", foreground="white")
            self.font_listbox.tag_add("selected_font", "1.0", "1.end")
            self.font_listbox.see("1.0")
            self._update_preview()
    
    def _update_preview(self, event=None):
        """
        更新预览文本框的字体样式
        
        Args:
            event: 事件对象（列表选择事件）
        """
        # 获取选中的字体
        try:
            # 获取所有带有selected_font标签的内容
            selected_ranges = self.font_listbox.tag_ranges("selected_font")
            if selected_ranges:
                # 获取选中范围的第一行内容
                font_line = self.font_listbox.get(selected_ranges[0], selected_ranges[1]).strip()
                font_name = font_line
            else:
                font_name = "Microsoft YaHei"
        except:
            font_name = "Microsoft YaHei"
        
        # 获取字体大小从输入框
        try:
            font_size = int(self.size_var.get())
            if font_size < 8:
                font_size = 8
            elif font_size > 72:
                font_size = 72
        except:
            font_size = 12
        
        # 更新预览文本框 - 直接配置整个文本框的字体，而不是使用tag
        self.preview_text.configure(state="normal")
        # 创建CTkFont对象并应用到整个文本框
        preview_font = ctk.CTkFont(family=font_name, size=font_size)
        self.preview_text.configure(font=preview_font)
        # 重新设置为disabled状态
        self.preview_text.configure(state="disabled")
        
        # 保存当前选择
        self.current_font = {
            "family": font_name,
            "size": font_size
        }
    

    
    def _on_ok(self):
        """
        确认字体设置并关闭对话框
        """
        if self.on_confirm:
            # 确保current_font包含必要的字体信息
            if not hasattr(self, 'current_font') or 'family' not in self.current_font:
                # 设置默认字体
                self.current_font = {
                    "family": "Microsoft YaHei",
                    "size": 12
                }
            
            # 应用字体设置
            self.on_confirm(self.current_font)
        self.dialog.destroy()
    
    def _on_cancel(self):
        """
        取消字体设置并关闭对话框
        """
        self.dialog.destroy()
    
    def set_confirm_callback(self, callback: Callable[[dict], None]):
        """
        设置确认回调函数
        
        Args:
            callback: 回调函数，接收字体设置字典
        """
        self.on_confirm = callback


def show_font_dialog(parent, text_widget=None, confirm_callback=None):
    """
    显示字体设置对话框的便捷函数
    
    Args:
        parent: 父窗口组件
        text_widget: 文本框组件引用
        confirm_callback: 确认回调函数
    """
    dialog = FontDialog(parent, text_widget)
    if confirm_callback:
        # 创建一个新的回调函数，将文本框引用传递给原始回调函数
        def wrapped_callback(font_config):
            if text_widget:
                confirm_callback(font_config, text_widget=text_widget)
            else:
                confirm_callback(font_config)
        dialog.set_confirm_callback(wrapped_callback)
    parent.wait_window(dialog.dialog)
    return dialog.current_font if dialog.current_font else None