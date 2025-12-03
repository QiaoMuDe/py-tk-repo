#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文件重命名对话框模块
提供用户友好的文件重命名界面
"""

import os
import customtkinter as ctk
from tkinter import messagebox


class RenameDialog(ctk.CTkToplevel):
    """文件重命名对话框类"""

    def __init__(self, parent, current_file_path):
        """
        初始化重命名对话框

        Args:
            parent: 父窗口
            current_file_path: 当前文件路径
        """
        super().__init__(parent)

        # 设置对话框属性
        self.title("重命名文件")
        self.resizable(False, False)

        # 字体配置
        self._setup_fonts()

        # 设置为模态对话框
        self.transient(parent)
        self.grab_set()
        self.attributes("-topmost", True)  # 始终置顶

        # 居中显示
        width = 700  # 窗口宽度
        height = 380  # 窗口高度
        self.master.center_window(self, width, height)

        # 保存当前文件路径
        self.current_file_path = current_file_path
        self.directory = os.path.dirname(current_file_path)
        self.current_name = os.path.basename(current_file_path)
        self.name_without_ext, self.extension = os.path.splitext(self.current_name)

        # 结果变量
        self.result = None

        # 创建UI组件
        self._create_widgets()

        # 设置焦点到输入框
        self.name_entry.focus_set()

        # 选中文件名（不含扩展名）
        self.name_entry.select_range(0, len(self.name_without_ext))

        # 绑定回车键和ESC键
        self.bind("<Return>", lambda e: self._on_confirm())
        self.bind("<Escape>", lambda e: self._on_cancel())

    def _setup_fonts(self):
        """设置对话框中使用的各种字体样式"""
        # 标准字体
        self.font_normal = ctk.CTkFont(family="Microsoft YaHei UI", size=16)
        # 小号字体
        self.font_small = ctk.CTkFont(family="Microsoft YaHei UI", size=14)
        # 粗体字体
        self.font_bold = ctk.CTkFont(
            family="Microsoft YaHei UI", size=15, weight="bold"
        )

    def _create_widgets(self):
        """创建对话框UI组件"""
        # 主框架 - 使用更现代的圆角设计和透明背景
        main_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=25, pady=25)

        # 内容卡片 - 添加轻微的背景色和圆角
        content_card = ctk.CTkFrame(
            main_frame, corner_radius=12, fg_color=("gray95", "gray10")
        )
        content_card.pack(fill="both", expand=True)

        # 当前文件信息
        info_frame = ctk.CTkFrame(
            content_card, corner_radius=8, fg_color=("gray90", "gray15")
        )
        info_frame.pack(fill="x", padx=15, pady=(15, 10))

        ctk.CTkLabel(
            info_frame,
            text="当前文件:",
            font=self.font_bold,
            text_color=("gray10", "gray90"),
        ).pack(anchor="w", padx=15, pady=(12, 0))

        ctk.CTkLabel(
            info_frame,
            text=self.current_name,
            font=self.font_small,
            text_color=("gray30", "gray70"),
        ).pack(anchor="w", padx=15, pady=(5, 12))

        # 新文件名输入区域
        input_frame = ctk.CTkFrame(
            content_card, corner_radius=8, fg_color=("gray90", "gray15")
        )
        input_frame.pack(fill="x", padx=15, pady=(5, 10))

        ctk.CTkLabel(
            input_frame,
            text="新文件名:",
            font=self.font_bold,
            text_color=("gray10", "gray90"),
        ).pack(anchor="w", padx=15, pady=(12, 10))

        # 输入框框架 - 使用透明背景
        entry_frame = ctk.CTkFrame(input_frame, corner_radius=6, fg_color="transparent")
        entry_frame.pack(fill="x", padx=15, pady=(0, 20))

        # 文件名输入框
        self.name_entry = ctk.CTkEntry(
            entry_frame,
            font=self.font_normal,
            placeholder_text="请输入新的文件名",
            corner_radius=6,
            height=36,
        )
        self.name_entry.pack(side="left", fill="x", expand=True, padx=(0, 5), pady=8)
        self.name_entry.insert(0, self.name_without_ext)

        # 扩展名标签
        if self.extension:
            self.extension_label = ctk.CTkLabel(
                entry_frame,
                text=self.extension,
                font=self.font_normal,
                text_color=("gray40", "gray60"),
            )
            self.extension_label.pack(side="right", padx=(0, 0), pady=8)

        # 按钮区域
        button_frame = ctk.CTkFrame(
            content_card, corner_radius=8, fg_color=("gray90", "gray15")
        )
        button_frame.pack(fill="x", padx=15, pady=(5, 15))

        # 提示标签
        hint_label = ctk.CTkLabel(
            button_frame,
            text="提示: 文件名不能包含特殊字符",
            font=self.font_small,
            text_color=("gray50", "gray60"),
        )
        hint_label.pack(side="left", padx=(15, 0), pady=12)

        # 按钮容器
        button_container = ctk.CTkFrame(button_frame, fg_color="transparent")
        button_container.pack(side="right")

        # 确认按钮
        confirm_button = ctk.CTkButton(
            button_container,
            text="确认",
            command=self._on_confirm,
            width=100,
            font=self.font_bold,
            corner_radius=6,
            height=32,
        )
        confirm_button.pack(side="right", padx=(10, 0), pady=12)

        # 取消按钮
        cancel_button = ctk.CTkButton(
            button_container,
            text="取消",
            command=self._on_cancel,
            width=100,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90"),
            font=self.font_bold,
            corner_radius=6,
            height=32,
        )
        cancel_button.pack(side="right", pady=12)

    def _on_confirm(self):
        """确认按钮点击事件"""
        new_name = self.name_entry.get().strip()

        # 检查是否为空
        if not new_name:
            messagebox.showerror("错误", "文件名不能为空")
            return

        # 添加扩展名（如果有）
        if self.extension and not new_name.endswith(self.extension):
            new_name += self.extension

        # 检查是否与当前文件名相同
        if new_name == self.current_name:
            messagebox.showinfo("提示", "新文件名与当前文件名相同")
            return

        # 检查文件名是否有效
        if not self._is_valid_filename(new_name):
            messagebox.showerror("错误", "文件名包含无效字符或为保留名称")
            return

        # 检查文件是否已存在
        new_path = os.path.join(self.directory, new_name)
        if os.path.exists(new_path):
            messagebox.showerror("错误", f"文件名'{new_name}'已存在，请选择其他名称")
            return

        # 设置结果并关闭对话框
        self.result = new_name
        self.destroy()

    def _on_cancel(self):
        """取消按钮点击事件"""
        self.result = None
        self.destroy()

    def _is_valid_filename(self, filename):
        """
        检查文件名是否有效

        Args:
            filename: 要检查的文件名

        Returns:
            bool: 文件名是否有效
        """
        # Windows系统不允许的字符
        invalid_chars = '<>:"/\\|?*'

        # 检查是否包含无效字符
        for char in invalid_chars:
            if char in filename:
                return False

        # 检查是否为空或只包含空格
        if not filename or filename.isspace():
            return False

        # 检查是否为保留名称（Windows）
        name_without_ext = os.path.splitext(filename)[0].upper()
        reserved_names = [
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "COM2",
            "COM3",
            "COM4",
            "COM5",
            "COM6",
            "COM7",
            "COM8",
            "COM9",
            "LPT1",
            "LPT2",
            "LPT3",
            "LPT4",
            "LPT5",
            "LPT6",
            "LPT7",
            "LPT8",
            "LPT9",
        ]

        if name_without_ext in reserved_names:
            return False

        return True

    def get_result(self):
        """
        获取对话框结果

        Returns:
            str: 新文件名，如果用户取消则返回None
        """
        return self.result


def show_rename_dialog(parent, current_file_path):
    """
    显示重命名对话框的便捷函数

    Args:
        parent: 父窗口
        current_file_path: 当前文件路径

    Returns:
        str: 新文件名，如果用户取消则返回None
    """
    dialog = RenameDialog(parent, current_file_path)
    dialog.wait_window()
    return dialog.get_result()
