#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
制表符设置对话框模块
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from config.config_manager import config_manager


class TabSettingsDialog:
    """
    制表符设置对话框类

    功能：
    - 设置制表符宽度（2-8个字符）
    - 选择常用宽度（2、4、8）
    - 设置是否使用空格代替制表符
    - 实时预览缩进效果
    """

    def __init__(self, parent=None, title="制表符设置"):
        """
        初始化制表符设置对话框

        Args:
            parent: 父窗口组件引用
            title: 对话框标题
        """
        self.parent = parent
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x450+650+200")  # 设置固定大小和位置
        self.dialog.resizable(False, False)  # 固定大小，不允许调整
        self.dialog.grab_set()  # 模态窗口

        # 初始化配置管理器
        self.config_manager = config_manager

        # 获取组件默认字体配置用于UI组件
        component_font_config = self.config_manager.get_font_config("components")
        self.component_font = ctk.CTkFont(
            family=component_font_config.get("font", "Microsoft YaHei UI"),
            size=component_font_config.get("font_size", 13),
            weight="bold" if component_font_config.get("font_bold", False) else "normal"
        )

        # 从配置中获取当前制表符设置
        current_tab_size = self.config_manager.get("text_editor.tab_size", 4)
        use_spaces = self.config_manager.get("text_editor.use_spaces", False)

        # 创建变量存储设置
        self.tab_size_var = tk.StringVar(value=str(current_tab_size))
        self.use_spaces_var = tk.BooleanVar(value=use_spaces)

        # 初始化UI
        self._init_ui()

        # 初始更新预览
        self._update_preview()

    def _init_ui(self):
        """
        初始化用户界面
        """
        # 设置整体字体
        ctk.set_default_font(self.component_font)

        # 创建主框架
        main_frame = ctk.CTkFrame(self.dialog, corner_radius=10)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 创建标题标签
        title_label = ctk.CTkLabel(
            main_frame,
            text="制表符设置",
            font=ctk.CTkFont(family=self.component_font.actual()["family"], size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20))

        # 制表符宽度设置区域
        width_frame = ctk.CTkFrame(main_frame, corner_radius=8)
        width_frame.pack(fill="x", padx=10, pady=(0, 15))

        width_label = ctk.CTkLabel(
            width_frame,
            text="制表符宽度 (2-8个字符):",
            font=self.component_font
        )
        width_label.pack(anchor="w", padx=15, pady=(15, 10))

        # 输入框和常用宽度按钮
        input_frame = ctk.CTkFrame(width_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.tab_size_entry = ctk.CTkEntry(
            input_frame,
            textvariable=self.tab_size_var,
            width=60,
            font=self.component_font
        )
        self.tab_size_entry.pack(side="left", padx=(0, 20))
        self.tab_size_entry.bind("<KeyRelease>", lambda e: self._validate_tab_size())

        # 常用宽度按钮
        common_widths_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        common_widths_frame.pack(side="left")

        common_widths_label = ctk.CTkLabel(
            common_widths_frame,
            text="常用宽度:",
            font=self.component_font
        )
        common_widths_label.pack(side="left", padx=(0, 10))

        # 创建常用宽度按钮 (2, 4, 8)
        for width in [2, 4, 8]:
            button = ctk.CTkButton(
                common_widths_frame,
                text=str(width),
                width=50,
                font=self.component_font,
                command=lambda w=width: self._set_common_width(w)
            )
            button.pack(side="left", padx=5)

        # 制表符行为设置区域
        behavior_frame = ctk.CTkFrame(main_frame, corner_radius=8)
        behavior_frame.pack(fill="x", padx=10, pady=(0, 15))

        behavior_label = ctk.CTkLabel(
            behavior_frame,
            text="制表符行为",
            font=self.component_font
        )
        behavior_label.pack(anchor="w", padx=15, pady=(15, 10))

        # 使用空格代替制表符复选框
        self.use_spaces_checkbox = ctk.CTkCheckBox(
            behavior_frame,
            text="使用空格替代制表符",
            variable=self.use_spaces_var,
            font=self.component_font,
            command=self._update_preview
        )
        self.use_spaces_checkbox.pack(anchor="w", padx=15, pady=(0, 15))

        # 预览区域
        preview_frame = ctk.CTkFrame(main_frame, corner_radius=8)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=(0, 15))

        preview_label = ctk.CTkLabel(
            preview_frame,
            text="预览",
            font=self.component_font
        )
        preview_label.pack(anchor="w", padx=15, pady=(15, 10))

        # 预览文本框
        self.preview_textbox = ctk.CTkTextbox(
            preview_frame,
            wrap="none",
            font=ctk.CTkFont(family="Courier New", size=14),
            height=120,
            corner_radius=6
        )
        self.preview_textbox.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        self.preview_textbox.configure(state="disabled")  # 设置为只读

        # 当前设置显示
        self.current_settings_label = ctk.CTkLabel(
            preview_frame,
            text="当前设置: 4个制表符",
            font=self.component_font
        )
        self.current_settings_label.pack(anchor="w", padx=15, pady=(0, 15))

        # 提示信息
        tip_label = ctk.CTkLabel(
            main_frame,
            text="提示: 更改将应用于新输入的文本",
            font=ctk.CTkFont(family=self.component_font.actual()["family"], size=12),
            text_color="#666666"
        )
        tip_label.pack(anchor="w", padx=10, pady=(0, 15))

        # 按钮区域
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(anchor="e", padx=10, pady=(0, 5))

        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="取消",
            width=100,
            font=self.component_font,
            command=self._on_cancel
        )
        cancel_button.pack(side="right", padx=5)

        ok_button = ctk.CTkButton(
            buttons_frame,
            text="确定",
            width=100,
            font=self.component_font,
            command=self._on_ok
        )
        ok_button.pack(side="right", padx=5)

    def _validate_tab_size(self):
        """
        验证制表符宽度输入
        """
        try:
            size = int(self.tab_size_var.get())
            if 2 <= size <= 8:
                self._update_preview()
        except ValueError:
            # 输入不是数字，不更新
            pass

    def _set_common_width(self, width):
        """
        设置常用宽度
        
        Args:
            width: 常用宽度值
        """
        self.tab_size_var.set(str(width))
        self._update_preview()

    def _update_preview(self):
        """
        更新预览效果
        """
        try:
            tab_size = int(self.tab_size_var.get())
            if not (2 <= tab_size <= 8):
                return
        except ValueError:
            return

        use_spaces = self.use_spaces_var.get()
        
        # 计算缩进字符串
        if use_spaces:
            indent = " " * tab_size
            current_settings = f"{tab_size}个空格"
        else:
            indent = "\t"
            current_settings = f"{tab_size}个制表符"

        # 更新预览文本
        self.preview_textbox.configure(state="normal")
        self.preview_textbox.delete("1.0", "end")
        self.preview_textbox.insert("end", "无缩进文本\n")
        self.preview_textbox.insert("end", f"{indent}一级缩进文本\n")
        self.preview_textbox.insert("end", f"{indent}{indent}二级缩进文本")
        self.preview_textbox.configure(state="disabled")

        # 更新当前设置标签
        self.current_settings_label.configure(text=f"当前设置: {current_settings}")

    def _on_ok(self):
        """
        确认按钮点击事件
        """
        try:
            tab_size = int(self.tab_size_var.get())
            if 2 <= tab_size <= 8:
                # 保存设置到配置管理器
                self.config_manager.set("text_editor.tab_size", tab_size)
                self.config_manager.set("text_editor.use_spaces", self.use_spaces_var.get())
                self.dialog.destroy()
        except ValueError:
            # 如果输入无效，不做任何操作
            pass

    def _on_cancel(self):
        """
        取消按钮点击事件
        """
        self.dialog.destroy()


def show_tab_settings_dialog(parent=None):
    """
    显示制表符设置对话框

    Args:
        parent: 父窗口组件引用

    Returns:
        TabSettingsDialog: 对话框实例
    """
    dialog = TabSettingsDialog(parent)
    parent.wait_window(dialog.dialog) if parent else dialog.dialog.mainloop()
    return dialog


# 命令行测试入口
if __name__ == "__main__":
    # 确保使用中文显示
    import locale
    locale.setlocale(locale.LC_ALL, '')
    
    # 初始化customtkinter
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    # 创建根窗口
    root = ctk.CTk()
    root.withdraw()  # 隐藏根窗口
    
    # 显示制表符设置对话框
    show_tab_settings_dialog(root)
    
    # 运行主循环
    root.mainloop()