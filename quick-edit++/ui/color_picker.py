#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HEX颜色代码选择器组件
提供颜色选择、预览、输入和复制功能
"""

import tkinter as tk
from tkinter import colorchooser
import customtkinter as ctk
from config.config_manager import config_manager
from loguru import logger


class HexColorPicker(ctk.CTkToplevel):
    """
    HEX颜色代码选择器对话框

    提供颜色选择、预览、输入和复制功能
    """

    def __init__(self, parent, initial_color="#000000", title="HEX颜色代码选择器"):
        """
        初始化颜色选择器对话框

        Args:
            parent: 父窗口
            initial_color: 初始颜色值，默认为黑色
            title: 对话框标题
        """
        super().__init__(parent)
        
        # 保存父窗口引用
        self.parent = parent

        # 设置对话框属性
        self.title(title)
        self.geometry("500x600")
        self.resizable(False, False)

        # 设置窗口模态
        self.transient(parent)
        self.grab_set()

        # 初始化变量
        self.selected_color = initial_color
        self.result = None  # 存储最终选择的颜色

        # 获取组件字体配置
        font_config = config_manager.get_font_config("components")
        self.font_family = font_config.get("font", "Microsoft YaHei UI")
        self.font_size = 15

        # 创建UI组件
        self._create_widgets()

        # 设置初始颜色
        self._set_color(initial_color)

        # 居中显示对话框
        self._center_dialog()

        # 绑定ESC键关闭对话框
        self.bind("<Escape>", lambda e: self._on_cancel())

        # 绑定回车键确认选择
        self.bind("<Return>", lambda e: self._on_ok())

        # 确保对话框获得焦点
        self.focus_set()

    def _create_widgets(self):
        """创建对话框UI组件"""
        # 主容器
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # 标题
        title_label = ctk.CTkLabel(
            main_container,
            text="选择颜色",
            font=(self.font_family, self.font_size + 2, "bold"),
        )
        title_label.pack(pady=(0, 15))

        # 颜色预览区域
        self._create_color_preview(main_container)

        # 系统颜色选择器按钮
        self._create_system_color_picker(main_container)

        # 预设颜色区域
        self._create_preset_colors(main_container)

        # 自定义颜色输入区域
        self._create_custom_color_input(main_container)

        # 按钮区域
        self._create_buttons(main_container)

    def _create_color_preview(self, parent):
        """创建颜色预览区域"""
        preview_frame = ctk.CTkFrame(parent)
        preview_frame.pack(fill="x", pady=(0, 15))

        # 颜色预览标签
        preview_label = ctk.CTkLabel(
            preview_frame,
            text="颜色预览",
            font=(self.font_family, self.font_size, "bold"),
        )
        preview_label.pack(side="left", padx=(10, 20))

        # 颜色预览框
        self.color_preview = ctk.CTkLabel(
            preview_frame, text="", width=150, height=50, corner_radius=5
        )
        self.color_preview.pack(side="left", padx=(0, 15))

        # HEX代码显示
        self.hex_display = ctk.CTkLabel(
            preview_frame, text="#000000", font=(self.font_family, self.font_size)
        )
        self.hex_display.pack(side="left")

    def _create_system_color_picker(self, parent):
        """创建系统颜色选择器按钮"""
        system_frame = ctk.CTkFrame(parent)
        system_frame.pack(fill="x", pady=(0, 15))

        system_button = ctk.CTkButton(
            system_frame,
            text="打开系统颜色选择器",
            font=(self.font_family, self.font_size),
            command=self._open_system_color_picker,
            fg_color=("#4A90E2", "#3A7BC8"),  # 蓝色系，表示系统功能
            hover_color=("#3A7BC8", "#2E6BA6"),
        )
        system_button.pack(pady=10)

    def _create_preset_colors(self, parent):
        """创建预设颜色区域"""
        preset_frame = ctk.CTkFrame(parent)
        preset_frame.pack(fill="both", expand=True, pady=(0, 15))

        preset_label = ctk.CTkLabel(
            preset_frame,
            text="预设颜色",
            font=(self.font_family, self.font_size, "bold"),
        )
        preset_label.pack(pady=(10, 5))

        # 预设颜色按钮容器
        colors_container = ctk.CTkFrame(preset_frame)
        colors_container.pack(fill="both", expand=True, padx=10, pady=5)

        # 预设颜色列表
        self.preset_colors = [
            # 基础颜色
            "#000000",
            "#FFFFFF",
            "#808080",
            "#C0C0C0",
            # 红色系
            "#FF0000",
            "#800000",
            "#FF6B6B",
            "#FFA07A",
            # 绿色系
            "#00FF00",
            "#008000",
            "#32CD32",
            "#90EE90",
            # 蓝色系
            "#0000FF",
            "#000080",
            "#4169E1",
            "#87CEEB",
            # 黄色系
            "#FFFF00",
            "#808000",
            "#FFD700",
            "#F0E68C",
            # 紫色系
            "#FF00FF",
            "#800080",
            "#9400D3",
            "#DDA0DD",
            # 青色系
            "#00FFFF",
            "#008080",
            "#00CED1",
            "#48D1CC",
            # 橙色系
            "#FFA500",
            "#FF8C00",
            "#FF7F50",
            "#FF6347",
            # 棕色系
            "#A52A2A",
            "#8B4513",
            "#D2691E",
            "#DEB887",
        ]

        # 创建颜色按钮网格
        for i, color in enumerate(self.preset_colors):
            row = i // 8
            col = i % 8

            color_button = ctk.CTkButton(
                colors_container,
                text="",
                width=35,
                height=35,
                fg_color=color,
                hover_color=color,
                command=lambda c=color: self._set_color(c),
                corner_radius=5,
            )
            color_button.grid(row=row, column=col, padx=3, pady=3)

    def _create_custom_color_input(self, parent):
        """创建自定义颜色输入区域"""
        input_frame = ctk.CTkFrame(parent)
        input_frame.pack(fill="x", pady=(0, 15))

        input_label = ctk.CTkLabel(
            input_frame,
            text="自定义HEX颜色代码:",
            font=(self.font_family, self.font_size, "bold"),
        )
        input_label.pack(side="left", padx=(10, 10))

        # 输入框和复制按钮容器
        input_container = ctk.CTkFrame(input_frame)
        input_container.pack(side="left", fill="x", expand=True)

        # 自定义颜色输入框
        self.color_entry = ctk.CTkEntry(
            input_container, font=(self.font_family, self.font_size), width=120
        )
        self.color_entry.pack(side="left", padx=(0, 5))
        self.color_entry.insert(0, "#000000")

        # 绑定输入变化事件
        self.color_entry.bind("<KeyRelease>", self._on_entry_change)

        # 绑定回车键确认选择
        self.color_entry.bind("<Return>", lambda e: self._on_ok())

        # 复制按钮
        copy_button = ctk.CTkButton(
            input_container,
            text="复制",
            width=50,
            font=(self.font_family, self.font_size - 1),
            command=self._copy_to_clipboard,
            fg_color="blue",
            hover_color="darkblue",
        )
        copy_button.pack(side="left")

    def _create_buttons(self, parent):
        """创建按钮区域"""
        button_frame = ctk.CTkFrame(parent)
        button_frame.pack(fill="x")

        # 确定按钮
        ok_button = ctk.CTkButton(
            button_frame,
            text="确定",
            font=(self.font_family, self.font_size, "bold"),
            command=self._on_ok,
            fg_color=("#5CB85C", "#4CAE4C"),  # 绿色系，表示确认操作
            hover_color=("#4CAE4C", "#40A540"),
        )
        ok_button.pack(side="left", padx=(0, 10), fill="x", expand=True)

        # 取消按钮
        cancel_button = ctk.CTkButton(
            button_frame,
            text="取消",
            font=(self.font_family, self.font_size, "bold"),
            command=self._on_cancel,
            fg_color=("#D9534F", "#C9302C"),  # 红色系，表示取消操作
            hover_color=("#C9302C", "#AC2925"),
        )
        cancel_button.pack(side="right", fill="x", expand=True)

    def _set_color(self, color):
        """设置当前选择的颜色"""
        if not color or not color.startswith("#") or len(color) != 7:
            return

        try:
            # 验证HEX代码
            int(color[1:], 16)

            # 更新预览
            self.color_preview.configure(fg_color=color)

            # 更新HEX代码显示
            self.hex_display.configure(text=color)

            # 更新输入框
            self.color_entry.delete(0, "end")
            self.color_entry.insert(0, color)

            # 保存当前选择的颜色
            self.selected_color = color

        except ValueError:
            pass

    def _on_entry_change(self, event=None):
        """处理输入框内容变化"""
        hex_code = self.color_entry.get()
        if hex_code.startswith("#") and len(hex_code) == 7:
            try:
                # 验证HEX代码
                int(hex_code[1:], 16)
                # 更新预览和显示
                self._set_color(hex_code)
            except ValueError:
                pass

    def _open_system_color_picker(self):
        """打开系统颜色选择器"""
        try:
            # 使用tkinter的颜色选择器
            color = colorchooser.askcolor(initialcolor=self.selected_color)
            if color[1]:  # 如果用户选择了颜色
                self._set_color(color[1])
        except Exception as e:
            logger.error(f"打开系统颜色选择器失败: {e}")

    def _copy_to_clipboard(self):
        """复制当前颜色代码到剪贴板"""
        try:
            self.clipboard_clear()
            self.clipboard_append(self.selected_color)
            self.update()

            # 显示复制成功通知
            self.parent.nm.show_success(
                "复制成功", f"颜色代码 {self.selected_color} 已复制到剪贴板"
            )
        except Exception as e:
            logger.error(f"复制到剪贴板失败: {e}")

    def _on_ok(self):
        """确定按钮处理函数"""
        self.result = self.selected_color
        self.destroy()

    def _on_cancel(self):
        """取消按钮处理函数"""
        self.result = None
        self.destroy()

    def _center_dialog(self):
        """居中显示对话框"""
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")


def show_color_picker(parent, initial_color="#000000"):
    """
    显示颜色选择器对话框并返回选择的颜色

    Args:
        parent: 父窗口
        initial_color: 初始颜色值

    Returns:
        str: 选择的HEX颜色代码，如果用户取消则返回None
    """
    dialog = HexColorPicker(parent, initial_color)
    parent.wait_window(dialog)
    return dialog.result
