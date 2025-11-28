#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RGB颜色选择器组件
提供RGB颜色选择功能的UI组件
"""

import customtkinter as ctk
from config.config_manager import config_manager


class RGBColorPicker:
    """RGB颜色选择器类"""

    def __init__(self, parent, callback):
        """
        初始化RGB颜色选择器

        Args:
            parent: 父窗口
            callback: 选择颜色后的回调函数，接收RGB代码作为参数
        """
        self.parent = parent  # 保存父窗口引用
        self.callback = callback  # 保存回调函数引用
        self.dialog = None  # 初始化对话框引用为None

        # 获取组件字体配置
        font_config = config_manager.get_font_config("components")
        self.font_family = font_config.get("font", "Microsoft YaHei UI")
        self.font_size = 15
        self.font_weight = "bold"

        self.show()

    def show(self):
        """显示RGB颜色选择对话框"""
        # 创建自定义对话框窗口
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("RGB颜色代码选择器")
        self.dialog.geometry("400x500")
        self.dialog.resizable(False, False)

        # 设置窗口模态
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # 创建主框架
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # 标题标签
        title_label = ctk.CTkLabel(
            main_frame,
            text="选择颜色",
            font=(self.font_family, self.font_size, self.font_weight),
        )
        title_label.pack(pady=(0, 10))

        # 颜色预览框架
        preview_frame = ctk.CTkFrame(main_frame)
        preview_frame.pack(fill="x", pady=(0, 10))

        # 颜色预览标签
        preview_label = ctk.CTkLabel(
            preview_frame,
            text="颜色预览",
            font=(self.font_family, self.font_size - 2, self.font_weight),
        )
        preview_label.pack(side="left", padx=(10, 20))

        # 颜色预览框
        self.color_preview = ctk.CTkLabel(preview_frame, text="", width=100, height=30)
        self.color_preview.pack(side="left", padx=(0, 10))
        self.color_preview.configure(fg_color="#000000")

        # RGB代码显示标签
        self.rgb_label = ctk.CTkLabel(
            preview_frame,
            text="rgb(0, 0, 0)",
            font=(self.font_family, self.font_size - 2),
        )
        self.rgb_label.pack(side="left")

        # RGB滑块框架
        slider_frame = ctk.CTkFrame(main_frame)
        slider_frame.pack(fill="both", expand=True, pady=(0, 10))

        # 红色滑块
        red_label = ctk.CTkLabel(
            slider_frame,
            text="红色 (R):",
            font=(self.font_family, self.font_size - 2, self.font_weight),
        )
        red_label.pack(anchor="w", padx=(10, 0), pady=(10, 0))

        self.red_slider = ctk.CTkSlider(
            slider_frame, from_=0, to=255, number_of_steps=255
        )
        self.red_slider.pack(fill="x", padx=(10, 10), pady=(0, 5))
        self.red_slider.set(0)

        self.red_value_label = ctk.CTkLabel(
            slider_frame, text="0", font=(self.font_family, self.font_size - 2)
        )
        self.red_value_label.pack(anchor="e", padx=(0, 10))

        # 绿色滑块
        green_label = ctk.CTkLabel(
            slider_frame,
            text="绿色 (G):",
            font=(self.font_family, self.font_size - 2, self.font_weight),
        )
        green_label.pack(anchor="w", padx=(10, 0), pady=(10, 0))

        self.green_slider = ctk.CTkSlider(
            slider_frame, from_=0, to=255, number_of_steps=255
        )
        self.green_slider.pack(fill="x", padx=(10, 10), pady=(0, 5))
        self.green_slider.set(0)

        self.green_value_label = ctk.CTkLabel(
            slider_frame, text="0", font=(self.font_family, self.font_size - 2)
        )
        self.green_value_label.pack(anchor="e", padx=(0, 10))

        # 蓝色滑块
        blue_label = ctk.CTkLabel(
            slider_frame,
            text="蓝色 (B):",
            font=(self.font_family, self.font_size - 2, self.font_weight),
        )
        blue_label.pack(anchor="w", padx=(10, 0), pady=(10, 0))

        self.blue_slider = ctk.CTkSlider(
            slider_frame, from_=0, to=255, number_of_steps=255
        )
        self.blue_slider.pack(fill="x", padx=(10, 10), pady=(0, 5))
        self.blue_slider.set(0)

        self.blue_value_label = ctk.CTkLabel(
            slider_frame, text="0", font=(self.font_family, self.font_size - 2)
        )
        self.blue_value_label.pack(anchor="e", padx=(0, 10))

        # 绑定滑块事件
        self.red_slider.configure(command=lambda v: self.update_color())
        self.green_slider.configure(command=lambda v: self.update_color())
        self.blue_slider.configure(command=lambda v: self.update_color())

        # 按钮框架
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x")

        # 创建按钮
        ok_button = ctk.CTkButton(
            button_frame,
            text="确定",
            font=(self.font_family, self.font_size, self.font_weight),
            command=self.on_ok,
            fg_color="green",
            hover_color="darkgreen",
        )
        ok_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        copy_button = ctk.CTkButton(
            button_frame,
            text="复制",
            font=(self.font_family, self.font_size, self.font_weight),
            command=self.on_copy,
            fg_color="blue",
            hover_color="darkblue",
        )
        copy_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        cancel_button = ctk.CTkButton(
            button_frame,
            text="取消",
            font=(self.font_family, self.font_size, self.font_weight),
            command=self.on_cancel,
            fg_color="red",
            hover_color="darkred",
        )
        cancel_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # 配置网格列权重，使三列均匀分布
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)

        # 居中显示对话框
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

    def update_color(self):
        """更新颜色预览和RGB代码"""
        r = int(self.red_slider.get())
        g = int(self.green_slider.get())
        b = int(self.blue_slider.get())

        # 更新值标签
        self.red_value_label.configure(text=str(r))
        self.green_value_label.configure(text=str(g))
        self.blue_value_label.configure(text=str(b))

        # 转换为HEX
        hex_color = f"#{r:02x}{g:02x}{b:02x}"

        # 更新预览
        self.color_preview.configure(fg_color=hex_color)

        # 更新RGB代码
        self.rgb_label.configure(text=f"rgb({r}, {g}, {b})")

    def on_ok(self):
        """确认按钮处理函数"""
        rgb_code = self.rgb_label.cget("text")
        if self.callback:
            self.callback(rgb_code)
        self.dialog.destroy()

    def on_cancel(self):
        """取消按钮处理函数"""
        self.dialog.destroy()

    def on_copy(self):
        """复制按钮处理函数"""
        rgb_code = self.rgb_label.cget("text")
        # 使用tkinter的剪贴板方法
        self.dialog.clipboard_clear()
        self.dialog.clipboard_append(rgb_code)

        # 设置临时父窗口引用，确保通知可以正确显示在模态对话框中
        self.parent.nm.set_next_parent(self.dialog)
        # 显示复制成功通知
        self.parent.nm.show_info(
            title="提示",
            message=f"已复制颜色代码 {rgb_code} 到剪贴板",
        )

        # self.parent.status_bar.show_notification(f"已复制颜色代码 {rgb_code} 到剪贴板")


def show_rgb_color_picker(parent, callback):
    """
    显示RGB颜色选择器的便捷函数

    Args:
        parent: 父窗口
        callback: 选择颜色后的回调函数，接收RGB代码作为参数
    """
    return RGBColorPicker(parent, callback)
