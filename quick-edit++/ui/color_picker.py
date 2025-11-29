#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一颜色选择器组件
集RGB滑块、预设颜色、颜色拾取和系统颜色选择器于一体的颜色选择工具
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import colorchooser
from PIL import ImageGrab
from config.config_manager import config_manager
import re


class UnifiedColorPicker:
    """统一颜色选择器类 - 集RGB滑块、预设颜色、颜色拾取和系统颜色选择器于一体的颜色选择工具"""

    def __init__(self, parent, callback):
        """
        初始化统一颜色选择器

        Args:
            parent: 父窗口
            callback: 选择颜色后的回调函数，接收RGB代码作为参数
        """
        self.parent = parent  # 保存父窗口引用
        self.callback = callback  # 保存回调函数引用
        self.dialog = None  # 初始化对话框引用为None
        self.picking_color = False  # 标记是否正在拾取颜色
        self.current_color = (0, 0, 0)  # 默认黑色

        # 获取组件字体配置
        font_config = config_manager.get_font_config("components")
        self.font_family = font_config.get("font", "Microsoft YaHei UI")
        self.font_size = 15
        self.font_weight = "bold"

        # 定义不同组件的字体组合
        self.title_font = (
            self.font_family,
            self.font_size + 2,
            self.font_weight,
        )  # 标题字体，稍大
        self.label_font = (
            self.font_family,
            self.font_size,
            self.font_weight,
        )  # 标签字体，加粗
        self.button_font = (
            self.font_family,
            self.font_size,
            self.font_weight,
        )  # 按钮字体，加粗
        self.entry_font = (self.font_family, self.font_size)  # 输入框字体，正常
        self.info_font = (self.font_family, self.font_size - 2)  # 信息字体，稍小

        self.show()

    def show(self):
        """显示统一颜色选择对话框"""
        # 创建自定义对话框窗口
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("颜色选择器")
        self.width = 550
        self.height = 800
        self.dialog.resizable(False, False)

        # 设置窗口模态
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # 创建主框架，铺满整个窗口
        main_frame = ctk.CTkFrame(self.dialog, fg_color="#FFFFFF")
        main_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # 1. 颜色预览区和颜色代码显示区 - 使用现代化卡片式布局
        preview_frame = ctk.CTkFrame(main_frame, fg_color="#F8F9FA", corner_radius=15)
        preview_frame.pack(fill="x", padx=15, pady=(15, 10))

        # 改进布局：进一步调整列权重比例，确保右侧代码显示区有足够空间
        preview_frame.grid_columnconfigure(0, weight=1, minsize=200)  # 设置最小尺寸
        preview_frame.grid_columnconfigure(1, weight=3, minsize=300)  # 设置最小尺寸

        # 左侧：颜色预览区，进一步减小最大宽度
        preview_container = ctk.CTkFrame(preview_frame, fg_color="transparent")
        preview_container.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        preview_container.grid_columnconfigure(0, weight=1)
        preview_container.grid_propagate(False)  # 阻止容器根据内容调整大小
        preview_container.configure(width=150)  # 减小最大宽度限制

        # 预览标题
        ctk.CTkLabel(preview_container, text="颜色预览", font=self.title_font).pack(
            pady=(0, 10)
        )

        # 画布大小
        self.preview_width = 200
        self.preview_height = 200

        # 颜色预览画布 - 设置固定尺寸，确保不会过大
        self.color_preview = ctk.CTkCanvas(
            preview_container,
            highlightthickness=0,
            width=self.preview_width,
            height=self.preview_height,
        )
        self.color_preview.pack(pady=10)
        # 添加配置事件监听器，当画布大小改变时重新绘制颜色
        self.color_preview.bind("<Configure>", self.on_preview_configure)

        # 右侧：颜色代码显示区
        code_container = ctk.CTkFrame(preview_frame, fg_color="transparent")
        code_container.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        code_container.grid_columnconfigure(0, weight=1)

        # 代码标题
        ctk.CTkLabel(code_container, text="颜色代码", font=self.title_font).pack(
            pady=(0, 15)
        )

        # RGB代码显示和复制 - 现代化输入框设计
        rgb_frame = ctk.CTkFrame(
            code_container,
            fg_color="#FFFFFF",
            corner_radius=10,
            border_width=1,
            border_color="#E0E0E0",
        )
        rgb_frame.pack(fill="x", pady=(0, 10))

        # RGB标签和输入框容器
        rgb_input_container = ctk.CTkFrame(rgb_frame, fg_color="transparent")
        rgb_input_container.pack(fill="x", padx=15, pady=10)

        # RGB标签
        ctk.CTkLabel(
            rgb_input_container, text="RGB:", font=self.label_font, text_color="#495057"
        ).pack(side="left", padx=(0, 10))

        # RGB输入框
        self.rgb_entry = ctk.CTkEntry(
            rgb_input_container,
            width=180,
            font=self.entry_font,
            border_width=1,
            corner_radius=8,
        )
        self.rgb_entry.pack(side="left", padx=(0, 10))
        self.rgb_entry.bind("<KeyRelease>", self.on_rgb_entry_change)
        self.rgb_entry.bind("<Return>", self.on_rgb_entry_change)
        self.rgb_entry.bind("<FocusOut>", self.on_rgb_entry_change)

        # RGB复制按钮 - 现代化按钮设计
        self.rgb_copy_btn = ctk.CTkButton(
            rgb_input_container,
            text="复制",
            width=60,
            font=self.button_font,
            command=self.copy_rgb,
            corner_radius=8,
            fg_color="#007BFF",
            hover_color="#0056B3",
            hover=False,
        )
        self.rgb_copy_btn.pack(side="left")

        # HEX代码显示和复制 - 现代化输入框设计
        hex_frame = ctk.CTkFrame(
            code_container,
            fg_color="#FFFFFF",
            corner_radius=10,
            border_width=1,
            border_color="#E0E0E0",
        )
        hex_frame.pack(fill="x")

        # HEX标签和输入框容器
        hex_input_container = ctk.CTkFrame(hex_frame, fg_color="transparent")
        hex_input_container.pack(fill="x", padx=15, pady=10)

        # HEX标签
        ctk.CTkLabel(
            hex_input_container, text="HEX:", font=self.label_font, text_color="#495057"
        ).pack(side="left", padx=(0, 10))

        # HEX输入框
        self.hex_entry = ctk.CTkEntry(
            hex_input_container,
            width=180,
            font=self.entry_font,
            border_width=1,
            corner_radius=8,
        )
        self.hex_entry.pack(side="left", padx=(0, 10))
        self.hex_entry.bind("<KeyRelease>", self.on_hex_entry_change)
        self.hex_entry.bind("<Return>", self.on_hex_entry_change)
        self.hex_entry.bind("<FocusOut>", self.on_hex_entry_change)

        # HEX复制按钮 - 现代化按钮设计
        self.hex_copy_btn = ctk.CTkButton(
            hex_input_container,
            text="复制",
            width=60,
            font=self.button_font,
            command=self.copy_hex,
            corner_radius=8,
            fg_color="#007BFF",
            hover_color="#0056B3",
            hover=False,
        )
        self.hex_copy_btn.pack(side="left")

        # 2. RGB滑块调整区 - 现代化卡片式布局
        slider_frame = ctk.CTkFrame(main_frame, fg_color="#F8F9FA", corner_radius=15)
        slider_frame.pack(fill="x", padx=15, pady=(0, 10))

        # 滑块区域标题
        ctk.CTkLabel(slider_frame, text="颜色调整", font=self.title_font).pack(
            anchor="w", padx=15, pady=(15, 10)
        )

        # 红色滑块 - 现代化设计
        red_container = ctk.CTkFrame(
            slider_frame,
            fg_color="#FFFFFF",
            corner_radius=10,
            border_width=1,
            border_color="#E0E0E0",
        )
        red_container.pack(fill="x", padx=15, pady=(0, 10))

        red_frame = ctk.CTkFrame(red_container, fg_color="transparent")
        red_frame.pack(fill="x", padx=15, pady=12)

        # 红色标签 - 现代化设计
        red_label = ctk.CTkFrame(
            red_frame, width=40, height=40, corner_radius=8, fg_color="#FF5252"
        )
        red_label.pack(side="left", padx=(0, 10))
        red_label.pack_propagate(False)  # 防止标签大小受内容影响
        ctk.CTkLabel(
            red_label, text="R", font=self.label_font, text_color="white"
        ).pack(expand=True)

        # 红色滑块 - 现代化设计
        self.red_slider = ctk.CTkSlider(
            red_frame,
            from_=0,
            to=255,
            number_of_steps=255,
            command=self.on_slider_change,
            height=24,  # 增加滑块高度
            button_color="#FF5252",  # 滑块按钮颜色
            button_hover_color="#FF1744",  # 悬停颜色
            progress_color="#FF5252",  # 进度条颜色
            fg_color="#F5F5F5",  # 滑块背景色
        )
        self.red_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # 红色数值标签 - 现代化设计
        self.red_value_label = ctk.CTkLabel(
            red_frame,
            text="0",
            width=50,
            font=self.label_font,
            corner_radius=8,
            fg_color="#F5F5F5",
            text_color="#333333",
        )
        self.red_value_label.pack(side="left")

        # 绿色滑块 - 现代化设计
        green_container = ctk.CTkFrame(
            slider_frame,
            fg_color="#FFFFFF",
            corner_radius=10,
            border_width=1,
            border_color="#E0E0E0",
        )
        green_container.pack(fill="x", padx=15, pady=(0, 10))

        green_frame = ctk.CTkFrame(green_container, fg_color="transparent")
        green_frame.pack(fill="x", padx=15, pady=12)

        # 绿色标签 - 现代化设计
        green_label = ctk.CTkFrame(
            green_frame, width=40, height=40, corner_radius=8, fg_color="#4CAF50"
        )
        green_label.pack(side="left", padx=(0, 10))
        green_label.pack_propagate(False)  # 防止标签大小受内容影响
        ctk.CTkLabel(
            green_label, text="G", font=self.label_font, text_color="white"
        ).pack(expand=True)

        # 绿色滑块 - 现代化设计
        self.green_slider = ctk.CTkSlider(
            green_frame,
            from_=0,
            to=255,
            number_of_steps=255,
            command=self.on_slider_change,
            height=24,  # 增加滑块高度
            button_color="#4CAF50",  # 滑块按钮颜色
            button_hover_color="#388E3C",  # 悬停颜色
            progress_color="#4CAF50",  # 进度条颜色
            fg_color="#F5F5F5",  # 滑块背景色
        )
        self.green_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # 绿色数值标签 - 现代化设计
        self.green_value_label = ctk.CTkLabel(
            green_frame,
            text="0",
            width=50,
            font=self.label_font,
            corner_radius=8,
            fg_color="#F5F5F5",
            text_color="#333333",
        )
        self.green_value_label.pack(side="left")

        # 蓝色滑块 - 现代化设计
        blue_container = ctk.CTkFrame(
            slider_frame,
            fg_color="#FFFFFF",
            corner_radius=10,
            border_width=1,
            border_color="#E0E0E0",
        )
        blue_container.pack(fill="x", padx=15, pady=(0, 10))

        blue_frame = ctk.CTkFrame(blue_container, fg_color="transparent")
        blue_frame.pack(fill="x", padx=15, pady=12)

        # 蓝色标签 - 现代化设计
        blue_label = ctk.CTkFrame(
            blue_frame, width=40, height=40, corner_radius=8, fg_color="#2196F3"
        )
        blue_label.pack(side="left", padx=(0, 10))
        blue_label.pack_propagate(False)  # 防止标签大小受内容影响
        ctk.CTkLabel(
            blue_label, text="B", font=self.label_font, text_color="white"
        ).pack(expand=True)

        # 蓝色滑块 - 现代化设计
        self.blue_slider = ctk.CTkSlider(
            blue_frame,
            from_=0,
            to=255,
            number_of_steps=255,
            command=self.on_slider_change,
            height=24,  # 增加滑块高度
            button_color="#2196F3",  # 滑块按钮颜色
            button_hover_color="#1976D2",  # 悬停颜色
            progress_color="#2196F3",  # 进度条颜色
            fg_color="#F5F5F5",  # 滑块背景色
        )
        self.blue_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # 蓝色数值标签 - 现代化设计
        self.blue_value_label = ctk.CTkLabel(
            blue_frame,
            text="0",
            width=50,
            font=self.label_font,
            corner_radius=8,
            fg_color="#F5F5F5",
            text_color="#333333",
        )
        self.blue_value_label.pack(side="left")

        # 3. 预设颜色区 - 现代化卡片式布局
        preset_frame = ctk.CTkFrame(main_frame, fg_color="#F8F9FA", corner_radius=15)
        preset_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        # 预设颜色标题
        ctk.CTkLabel(preset_frame, text="预设颜色", font=self.title_font).pack(
            anchor="w", padx=15, pady=(15, 10)
        )

        # 预设颜色画布容器 - 现代化设计
        canvas_container = ctk.CTkFrame(
            preset_frame,
            fg_color="#FFFFFF",
            corner_radius=10,
            border_width=1,
            border_color="#E0E0E0",
        )
        canvas_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # 预设颜色画布 - 使用tk.Canvas替代CTkCanvas以避免兼容性问题
        self.preset_canvas = tk.Canvas(
            canvas_container, height=200, bg="#FFFFFF", highlightthickness=0
        )
        self.preset_canvas.pack(fill="both", expand=True, padx=15, pady=15)

        # 创建预设颜色按钮
        self.create_preset_colors()

        # 4. 底部按钮区 - 现代化卡片式布局
        button_frame = ctk.CTkFrame(main_frame, fg_color="#F8F9FA", corner_radius=15)
        button_frame.pack(fill="x", padx=15, pady=(0, 15))

        # 按钮容器 - 现代化设计
        button_container = ctk.CTkFrame(button_frame, fg_color="transparent")
        button_container.pack(fill="x", padx=15, pady=15)

        # 拾取颜色按钮 - 现代化设计
        pick_button = ctk.CTkButton(
            button_container,
            text="拾取颜色",
            font=self.button_font,
            command=self.on_pick_color,
            height=45,
            corner_radius=10,
            fg_color="#9C27B0",
            hover_color="#7B1FA2",
            border_width=0,
        )
        pick_button.pack(side="left", fill="x", expand=True, padx=(0, 5))

        # 系统颜色按钮 - 现代化设计
        system_button = ctk.CTkButton(
            button_container,
            text="系统颜色",
            font=self.button_font,
            command=self.choose_system_color,
            height=45,
            corner_radius=10,
            fg_color="#2196F3",
            hover_color="#1976D2",
            border_width=0,
        )
        system_button.pack(side="left", fill="x", expand=True, padx=5)

        # 关闭按钮 - 现代化设计
        close_button = ctk.CTkButton(
            button_container,
            text="关闭",
            font=self.button_font,
            command=self.on_close,
            height=45,
            corner_radius=10,
            fg_color="#F44336",
            hover_color="#d32f2f",
            border_width=0,
        )
        close_button.pack(side="left", fill="x", expand=True, padx=(5, 0))

        # 初始化颜色显示
        self.update_color_display()

        # 绑定ESC键到关闭功能
        self.dialog.bind("<Escape>", lambda event: self.on_close())

        # 居中显示对话框
        self.parent.center_window(self.dialog, self.width, self.height)

    def update_color(self):
        """更新颜色预览和RGB代码"""
        r = int(self.red_slider.get())
        g = int(self.green_slider.get())
        b = int(self.blue_slider.get())
        self.current_color = (r, g, b)
        self.update_color_display()

    def update_color_display(self):
        """更新所有颜色显示组件"""
        r, g, b = self.current_color

        # 更新颜色预览 - 使用固定画布尺寸
        self.color_preview.delete("all")
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        # 使用固定的画布尺寸
        width, height = self.preview_width, self.preview_height
        self.color_preview.create_rectangle(
            0, 0, width - 1, height - 1, fill=hex_color, outline=""
        )

        # 更新RGB滑块和标签
        self.red_slider.set(r)
        self.green_slider.set(g)
        self.blue_slider.set(b)
        self.red_value_label.configure(text=str(r))
        self.green_value_label.configure(text=str(g))
        self.blue_value_label.configure(text=str(b))

        # 更新RGB输入框
        rgb_text = f"({r}, {g}, {b})"
        self.rgb_entry.delete(0, tk.END)
        self.rgb_entry.insert(0, rgb_text)

        # 更新HEX输入框
        hex_text = hex_color.upper()
        self.hex_entry.delete(0, tk.END)
        self.hex_entry.insert(0, hex_text)

    def _update_color_display_except_entry(self):
        """更新除了输入框以外的所有颜色显示组件，避免循环更新"""
        r, g, b = self.current_color

        # 更新颜色预览 - 使用固定画布尺寸
        self.color_preview.delete("all")
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        # 使用固定的画布尺寸
        width, height = self.preview_width, self.preview_height
        self.color_preview.create_rectangle(
            0, 0, width - 1, height - 1, fill=hex_color, outline=""
        )

        # 更新RGB滑块和标签
        self.red_slider.set(r)
        self.green_slider.set(g)
        self.blue_slider.set(b)
        self.red_value_label.configure(text=str(r))
        self.green_value_label.configure(text=str(g))
        self.blue_value_label.configure(text=str(b))

    def on_preview_configure(self, event=None):
        """预览画布大小改变事件处理

        Args:
            event: 配置事件对象
        """
        # 重新绘制颜色预览以适应新的画布尺寸
        self._update_color_display_except_entry()

    def on_slider_change(self, value=None):
        """滑块值改变事件处理"""
        r = int(self.red_slider.get())
        g = int(self.green_slider.get())
        b = int(self.blue_slider.get())
        self.current_color = (r, g, b)
        self.update_color_display()

    def on_rgb_entry_change(self, event=None):
        """RGB输入框内容改变事件处理

        Args:
            event: 事件对象，包含事件类型和触发方式
        """
        text = self.rgb_entry.get().strip()

        # 使用正则表达式匹配RGB格式 (r, g, b)
        match = re.match(r"\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)", text)

        # 只有当输入内容完全匹配格式时才更新颜色
        if match:
            try:
                r = int(match.group(1))
                g = int(match.group(2))
                b = int(match.group(3))

                # 验证RGB值范围
                if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
                    # 保存当前光标位置
                    cursor_pos = self.rgb_entry.index(tk.INSERT)
                    self.current_color = (r, g, b)

                    # 更新滑块和预览区
                    self._update_color_display_except_entry()

                    # 更新HEX输入框
                    hex_color = f"#{r:02x}{g:02x}{b:02x}".upper()
                    self.hex_entry.delete(0, tk.END)
                    self.hex_entry.insert(0, hex_color)

                    # 恢复光标位置
                    self.rgb_entry.icursor(cursor_pos)
            except ValueError:
                pass  # 忽略无效输入

    def on_hex_entry_change(self, event=None):
        """HEX输入框内容改变事件处理

        Args:
            event: 事件对象，包含事件类型和触发方式
        """
        text = self.hex_entry.get().strip()

        # 改进的正则表达式，确保正确识别标准HEX颜色格式 #RRGGBB 或 #RGB
        # 允许前面有#号，后面是3位或6位十六进制字符
        match = re.match(r"#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$", text)

        # 当输入内容匹配HEX颜色格式时更新颜色
        if match:
            hex_color = match.group(1)

            # 如果是简写格式 #RGB，扩展为 #RRGGBB
            if len(hex_color) == 3:
                hex_color = "".join([c * 2 for c in hex_color])

            try:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)

                # 验证RGB值范围
                if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
                    # 保存当前光标位置
                    cursor_pos = self.hex_entry.index(tk.INSERT)
                    self.current_color = (r, g, b)

                    # 更新滑块和预览区
                    self._update_color_display_except_entry()

                    # 更新RGB输入框
                    rgb_text = f"({r}, {g}, {b})"
                    self.rgb_entry.delete(0, tk.END)
                    self.rgb_entry.insert(0, rgb_text)

                    # 恢复光标位置
                    self.hex_entry.icursor(cursor_pos)
            except ValueError:
                pass  # 忽略无效输入

    def create_preset_colors(self):
        """创建预设颜色按钮 - 现代化设计"""
        # 预设颜色数据 - 扩展到50种颜色（5行）
        self.preset_colors = [
            # 第一行 - 基础颜色
            "#FF0000",
            "#FF4500",
            "#FFA500",
            "#FFFF00",
            "#00FF00",
            "#00FFFF",
            "#0000FF",
            "#4B0082",
            "#9400D3",
            "#FF1493",
            # 第二行 - 粉色和紫色系
            "#FFC0CB",
            "#FFB6C1",
            "#FF69B4",
            "#FF1493",
            "#C71585",
            "#8B008B",
            "#4B0082",
            "#6A0DAD",
            "#7B68EE",
            "#9370DB",
            # 第三行 - 棕色和灰色系
            "#8B4513",
            "#A0522D",
            "#D2691E",
            "#DEB887",
            "#F5DEB3",
            "#808080",
            "#A9A9A9",
            "#C0C0C0",
            "#D3D3D3",
            "#DCDCDC",
            # 第四行 - 深色调
            "#800000",
            "#8B0000",
            "#B22222",
            "#DC143C",
            "#CD5C5C",
            "#008000",
            "#006400",
            "#228B22",
            "#32CD32",
            "#3CB371",
            # 第五行 - 鲜艳色调
            "#FF4500",
            "#FF6347",
            "#FF7F50",
            "#FFA07A",
            "#FFB6C1",
            "#1E90FF",
            "#00BFFF",
            "#87CEEB",
            "#87CEFA",
            "#00CED1",
        ]

        # 预设颜色按钮列表
        self.preset_buttons = []

        # 绘制预设颜色 - 调整为5行布局
        self.draw_preset_colors()

        # 绑定画布大小变化事件
        self.preset_canvas.bind("<Configure>", lambda e: self.draw_preset_colors())

    def draw_preset_colors(self):
        """绘制预设颜色按钮"""
        # 清除现有的颜色按钮
        self.preset_canvas.delete("all")
        self.preset_buttons = []

        # 获取画布宽度
        canvas_width = self.preset_canvas.winfo_width()
        if canvas_width <= 1:  # 画布尚未初始化
            canvas_width = 600  # 默认宽度

        # 计算颜色块大小和间距 - 现代化设计
        padding = 15  # 添加一些间距
        color_size = 40  # 增大颜色块尺寸
        spacing = 10  # 增加间距

        # 计算5行布局
        rows = 5
        cols = 10  # 每行10个颜色

        # 计算起始位置使颜色块居中
        total_width = cols * color_size + (cols - 1) * spacing
        start_x = (canvas_width - total_width) // 2

        # 创建颜色按钮
        for i, color in enumerate(self.preset_colors):
            row = i // cols
            col = i % cols

            x = start_x + col * (color_size + spacing)
            y = padding + row * (color_size + spacing)

            # 创建圆角矩形背景 - 现代化设计
            self.preset_canvas.create_oval(
                x + 2,
                y + 2,
                x + color_size + 2,
                y + color_size + 2,
                fill="#E0E0E0",
                outline="",
            )

            # 创建颜色矩形 - 使用CTkCanvas的create_rectangle方法
            self.preset_canvas.create_rectangle(
                x,
                y,
                x + color_size,
                y + color_size,
                fill=color,
                outline="#CCCCCC",
                width=1,
                tags=("color", f"color_{i}", color),
            )

            # 绑定点击事件
            self.preset_canvas.tag_bind(
                f"color_{i}",
                "<Button-1>",
                lambda e, c=color: self.on_preset_color_click(c),
            )

            # 绑定悬停效果
            self.preset_canvas.tag_bind(
                f"color_{i}",
                "<Enter>",
                lambda e, tag=f"color_{i}": self.preset_canvas.itemconfig(
                    tag, width=2, outline="#888888"
                ),
            )

            self.preset_canvas.tag_bind(
                f"color_{i}",
                "<Leave>",
                lambda e, tag=f"color_{i}": self.preset_canvas.itemconfig(
                    tag, width=1, outline="#CCCCCC"
                ),
            )

    def on_preset_color_click(self, hex_color):
        """预设颜色点击事件处理"""
        # 将HEX颜色转换为RGB
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)

        self.current_color = (r, g, b)
        self.update_color_display()

    def copy_rgb(self):
        """复制RGB颜色代码"""
        r, g, b = self.current_color
        rgb_text = f"rgb({r}, {g}, {b})"

        # 复制到剪贴板
        self.dialog.clipboard_clear()
        self.dialog.clipboard_append(rgb_text)

        # 保存原始按钮配置
        original_text = self.rgb_copy_btn.cget("text")
        original_fg_color = self.rgb_copy_btn.cget("fg_color")

        # 临时改变按钮文本和背景色作为反馈
        self.rgb_copy_btn.configure(text="已复制", fg_color="green")

        # 设置定时器恢复原始状态
        self.dialog.after(
            1000,
            lambda: self.rgb_copy_btn.configure(
                text=original_text, fg_color=original_fg_color
            ),
        )

    def copy_hex(self):
        """复制HEX颜色代码"""
        r, g, b = self.current_color
        hex_text = f"#{r:02x}{g:02x}{b:02x}".upper()

        # 复制到剪贴板
        self.dialog.clipboard_clear()
        self.dialog.clipboard_append(hex_text)

        # 保存原始按钮配置
        original_text = self.hex_copy_btn.cget("text")
        original_fg_color = self.hex_copy_btn.cget("fg_color")

        # 临时改变按钮文本和背景色作为反馈
        self.hex_copy_btn.configure(text="已复制", fg_color="green")

        # 设置定时器恢复原始状态
        self.dialog.after(
            1000,
            lambda: self.hex_copy_btn.configure(
                text=original_text, fg_color=original_fg_color
            ),
        )

    def choose_system_color(self):
        """调用系统颜色选择器"""
        # 隐藏当前对话框
        self.dialog.withdraw()

        # 打开系统颜色选择器
        color = colorchooser.askcolor(
            initialcolor=f"#{self.current_color[0]:02x}{self.current_color[1]:02x}{self.current_color[2]:02x}"
        )

        # 显示主对话框
        self.dialog.deiconify()

        # 如果用户选择了颜色
        if color[0]:
            r, g, b = [int(c) for c in color[0]]
            self.current_color = (r, g, b)
            self.update_color_display()

    def on_close(self):
        """关闭按钮处理函数"""
        self.dialog.destroy()

    def on_copy(self):
        """复制按钮处理函数"""
        # 直接调用复制RGB的方法
        self.copy_rgb()

    def on_pick_color(self):
        """颜色拾取按钮处理函数"""
        # 隐藏对话框
        self.dialog.withdraw()

        # 延迟一小段时间，确保对话框完全隐藏
        self.dialog.after(200, self._start_color_pick)

    def _start_color_pick(self):
        """开始颜色拾取"""
        try:
            # 创建全屏透明窗口用于拾取颜色
            self.picking_color = True
            self.pick_window = tk.Toplevel(self.dialog)
            self.pick_window.attributes(
                "-alpha", 0.01
            )  # 设置窗口几乎完全透明，但保持可交互性
            self.pick_window.attributes("-fullscreen", True)  # 全屏
            self.pick_window.attributes("-topmost", True)  # 置顶
            self.pick_window.config(cursor="crosshair")  # 设置十字光标
            self.pick_window.config(bg="black")

            # 创建一个不透明的信息窗口
            self.info_window = tk.Toplevel(self.dialog)
            self.info_window.attributes("-topmost", True)  # 置顶
            self.info_window.geometry("650x320+10+10")  # 设置窗口大小和位置
            self.info_window.overrideredirect(True)  # 无边框窗口
            self.info_window.config(bg="white")

            # 绑定鼠标事件
            self.pick_window.bind("<Button-1>", self._on_pick_click)
            self.pick_window.bind("<Escape>", self._on_pick_cancel)

            # 创建一个框架来容纳所有标签，这样可以避免标签重叠
            self.info_frame = tk.Frame(
                self.info_window,
                bg="white",  # 白色背景确保内容清晰可见
                padx=15,
                pady=15,
                relief="solid",  # 添加边框
                bd=2,
            )
            self.info_frame.pack(fill="both", expand=True)

            # 标题 - 提示信息
            self.pick_label = tk.Label(
                self.info_frame,
                text="点击拾取颜色, 按ESC取消",
                font=(self.font_family, self.font_size, "bold"),
                bg="white",
                fg="#333333",
            )
            self.pick_label.grid(
                row=0, column=0, columnspan=2, sticky="w", pady=(0, 10)
            )

            # 左侧 - 颜色预览
            self.color_preview_label = tk.Label(
                self.info_frame,
                text="预览",
                font=(self.font_family, self.font_size - 1, "bold"),
                bg="white",
                fg="#333333",
            )
            self.color_preview_label.grid(row=1, column=0, sticky="w", padx=(0, 10))

            self.color_display = tk.Label(
                self.info_frame,
                text="",
                width=10,
                height=4,
                bg="black",
                relief="solid",
                bd=1,
            )
            self.color_display.grid(
                row=2, column=0, sticky="w", padx=(0, 10), pady=(0, 10)
            )

            # 右侧 - 颜色值信息
            self.color_info_label = tk.Label(
                self.info_frame,
                text="RGB: (0, 0, 0)\nHEX: #000000",
                font=(self.font_family, self.font_size),
                bg="white",
                fg="#333333",
                justify="left",
                anchor="w",  # 文本左对齐
                # wraplength=350  # 设置文本换行宽度，确保内容完整显示
            )
            self.color_info_label.grid(
                row=1, column=1, rowspan=2, sticky="n", padx=(10, 0)
            )

            # 简化鼠标移动事件处理，减少性能消耗
            self.pick_window.bind("<Motion>", self._on_mouse_move)

        except Exception as e:
            print(f"颜色拾取失败: {e}")
            self._finish_color_pick()

    def _on_mouse_move(self, event):
        """鼠标移动事件处理，显示当前颜色信息"""
        if not self.picking_color:
            return

        try:
            # 获取鼠标位置的颜色
            x, y = event.x_root, event.y_root

            # 获取当前鼠标位置的颜色
            current_color = self._get_pixel_color(x, y)
            r, g, b = current_color

            # 转换为HEX
            hex_color = f"#{r:02x}{g:02x}{b:02x}"

            # 更新颜色预览
            self.color_display.config(bg=hex_color)

            # 更新颜色信息
            self.color_info_label.config(
                text=f"RGB: ({r}, {g}, {b})\nHEX: {hex_color.upper()}"
            )

        except Exception as e:
            print(f"鼠标移动处理失败: {e}")

    def _get_pixel_color(self, x, y):
        """获取指定位置的像素颜色"""
        try:
            # 使用ImageGrab获取屏幕截图
            screen = ImageGrab.grab(bbox=(x, y, x + 1, y + 1))
            pixel = screen.getpixel((0, 0))

            # 确保返回的是RGB元组
            if len(pixel) == 3:
                return pixel
            elif len(pixel) == 4:  # RGBA
                return pixel[:3]
            else:
                return (0, 0, 0)  # 默认黑色
        except Exception as e:
            print(f"获取像素颜色失败: {e}")
            return (0, 0, 0)  # 默认黑色

    def _on_pick_click(self, event):
        """颜色拾取点击事件处理"""
        if not self.picking_color:
            return

        try:
            # 获取点击位置的颜色
            x, y = event.x_root, event.y_root
            r, g, b = self._get_pixel_color(x, y)

            # 更新当前颜色
            self.current_color = (r, g, b)

            # 更新颜色显示
            self.update_color_display()

        except Exception as e:
            print(f"颜色拾取失败: {e}")
        finally:
            self._finish_color_pick()

    def _on_pick_cancel(self, event):
        """颜色拾取取消事件处理"""
        self._finish_color_pick()

    def _finish_color_pick(self):
        """完成颜色拾取"""
        self.picking_color = False

        # 关闭拾取窗口
        if hasattr(self, "pick_window") and self.pick_window:
            self.pick_window.destroy()
            self.pick_window = None

        # 关闭信息窗口
        if hasattr(self, "info_window") and self.info_window:
            self.info_window.destroy()
            self.info_window = None

        # 重新显示主对话框
        self.dialog.deiconify()


def show_color_picker(parent, callback=None):
    """
    显示统一颜色选择器的便捷函数

    Args:
        parent: 父窗口
        callback: 颜色选择后的回调函数，接收RGB代码作为参数
    """
    return UnifiedColorPicker(parent, callback)
