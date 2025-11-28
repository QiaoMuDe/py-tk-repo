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


class RGBColorPicker:
    """统一颜色选择器类 - 基于RGBColorPicker优化版"""

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
        self.title_font = (self.font_family, self.font_size + 2, self.font_weight)  # 标题字体，稍大
        self.label_font = (self.font_family, self.font_size, self.font_weight)      # 标签字体，加粗
        self.button_font = (self.font_family, self.font_size, self.font_weight)     # 按钮字体，加粗
        self.entry_font = (self.font_family, self.font_size)                       # 输入框字体，正常
        self.info_font = (self.font_family, self.font_size - 2)                     # 信息字体，稍小

        self.show()

    def show(self):
        """显示统一颜色选择对话框"""
        # 创建自定义对话框窗口
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("颜色选择器")
        self.width = 500
        self.height = 600
        self.dialog.resizable(False, False)

        # 设置窗口模态
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # 创建主框架
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 1. 颜色预览区和颜色代码显示区
        preview_frame = ctk.CTkFrame(main_frame)
        preview_frame.pack(fill="x", pady=(0, 10))
        
        # 颜色预览区
        self.color_preview = ctk.CTkCanvas(preview_frame, width=150, height=100, highlightthickness=0)
        self.color_preview.pack(side="left", padx=10, pady=10)
        
        # 颜色代码显示区
        code_frame = ctk.CTkFrame(preview_frame)
        code_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # RGB代码显示和复制
        rgb_frame = ctk.CTkFrame(code_frame)
        rgb_frame.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(rgb_frame, text="RGB:", font=self.label_font).pack(side="left", padx=(0, 5))
        self.rgb_entry = ctk.CTkEntry(rgb_frame, width=150, font=self.entry_font)
        self.rgb_entry.pack(side="left", padx=(0, 5))
        self.rgb_entry.bind("<KeyRelease>", self.on_rgb_entry_change)
        self.rgb_entry.bind("<Return>", self.on_rgb_entry_change)
        self.rgb_entry.bind("<FocusOut>", self.on_rgb_entry_change)
        
        self.rgb_copy_btn = ctk.CTkButton(rgb_frame, text="复制", width=50, font=self.button_font, command=self.copy_rgb)
        self.rgb_copy_btn.pack(side="left")
        
        # HEX代码显示和复制
        hex_frame = ctk.CTkFrame(code_frame)
        hex_frame.pack(fill="x")
        
        ctk.CTkLabel(hex_frame, text="HEX:", font=self.label_font).pack(side="left", padx=(0, 5))
        self.hex_entry = ctk.CTkEntry(hex_frame, width=150, font=self.entry_font)
        self.hex_entry.pack(side="left", padx=(0, 5))
        self.hex_entry.bind("<KeyRelease>", self.on_hex_entry_change)
        self.hex_entry.bind("<Return>", self.on_hex_entry_change)
        self.hex_entry.bind("<FocusOut>", self.on_hex_entry_change)
        
        self.hex_copy_btn = ctk.CTkButton(hex_frame, text="复制", width=50, font=self.button_font, command=self.copy_hex)
        self.hex_copy_btn.pack(side="left")

        # 2. RGB滑块调整区
        slider_frame = ctk.CTkFrame(main_frame)
        slider_frame.pack(fill="x", pady=(0, 10))
        
        # 红色滑块
        red_frame = ctk.CTkFrame(slider_frame)
        red_frame.pack(fill="x", padx=10, pady=5)
        
        # 将标签背景色设为红色，文字为白色以确保可读性
        ctk.CTkLabel(red_frame, text="R", width=20, font=self.label_font, text_color="white", fg_color="red").pack(side="left", padx=(0, 5))
        # 红色滑块，设置按钮颜色为红色系，增加高度提升视觉效果
        self.red_slider = ctk.CTkSlider(
            red_frame, 
            from_=0, 
            to=255, 
            number_of_steps=255, 
            command=self.on_slider_change,
            height=20,  # 增加滑块高度
            button_color="#FF6B6B",  # 滑块按钮颜色
            button_hover_color="#FF3B30",  # 悬停颜色
            fg_color="#F0F0F0"  # 滑块背景色
        )
        self.red_slider.pack(side="left", fill="x", expand=True, padx=(0, 5))
        # 优化数值标签样式，增加边框和内边距提升可读性
        self.red_value_label = ctk.CTkLabel(
            red_frame, 
            text="0", 
            width=40, 
            font=self.label_font,
            corner_radius=5,
            fg_color="#F5F5F5",
            text_color="#333333"
        )
        self.red_value_label.pack(side="left")
        
        # 绿色滑块
        green_frame = ctk.CTkFrame(slider_frame)
        green_frame.pack(fill="x", padx=10, pady=5)
        
        # 将标签背景色设为绿色，文字为白色以确保可读性
        ctk.CTkLabel(green_frame, text="G", width=20, font=self.label_font, text_color="white", fg_color="green").pack(side="left", padx=(0, 5))
        # 绿色滑块，设置按钮颜色为绿色系，增加高度提升视觉效果
        self.green_slider = ctk.CTkSlider(
            green_frame, 
            from_=0, 
            to=255, 
            number_of_steps=255, 
            command=self.on_slider_change,
            height=20,  # 增加滑块高度
            button_color="#4CAF50",  # 滑块按钮颜色
            button_hover_color="#388E3C",  # 悬停颜色
            fg_color="#F0F0F0"  # 滑块背景色
        )
        self.green_slider.pack(side="left", fill="x", expand=True, padx=(0, 5))
        # 优化数值标签样式，增加边框和内边距提升可读性
        self.green_value_label = ctk.CTkLabel(
            green_frame, 
            text="0", 
            width=40, 
            font=self.label_font,
            corner_radius=5,
            fg_color="#F5F5F5",
            text_color="#333333"
        )
        self.green_value_label.pack(side="left")
        
        # 蓝色滑块
        blue_frame = ctk.CTkFrame(slider_frame)
        blue_frame.pack(fill="x", padx=10, pady=5)
        
        # 将标签背景色设为蓝色，文字为白色以确保可读性
        ctk.CTkLabel(blue_frame, text="B", width=20, font=self.label_font, text_color="white", fg_color="blue").pack(side="left", padx=(0, 5))
        # 蓝色滑块，设置按钮颜色为蓝色系，增加高度提升视觉效果
        self.blue_slider = ctk.CTkSlider(
            blue_frame, 
            from_=0, 
            to=255, 
            number_of_steps=255, 
            command=self.on_slider_change,
            height=20,  # 增加滑块高度
            button_color="#2196F3",  # 滑块按钮颜色
            button_hover_color="#1976D2",  # 悬停颜色
            fg_color="#F0F0F0"  # 滑块背景色
        )
        self.blue_slider.pack(side="left", fill="x", expand=True, padx=(0, 5))
        # 优化数值标签样式，增加边框和内边距提升可读性
        self.blue_value_label = ctk.CTkLabel(
            blue_frame, 
            text="0", 
            width=40, 
            font=self.label_font,
            corner_radius=5,
            fg_color="#F5F5F5",
            text_color="#333333"
        )
        self.blue_value_label.pack(side="left")

        # 3. 预设颜色区
        preset_frame = ctk.CTkFrame(main_frame)
        preset_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        ctk.CTkLabel(preset_frame, text="预设颜色:", font=self.title_font).pack(anchor="w", padx=10, pady=(5, 0))
        
        # 预设颜色画布
        self.preset_canvas = tk.Canvas(preset_frame, height=100, bg="#F0F0F0", highlightthickness=0)
        self.preset_canvas.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 创建预设颜色按钮
        self.create_preset_colors()

        # 4. 底部按钮区
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x")
        
        pick_button = ctk.CTkButton(
            button_frame,
            text="拾取颜色",
            font=self.button_font,
            command=self.on_pick_color,
            fg_color="purple",
            hover_color="darkviolet",
        )
        pick_button.pack(side="left", padx=10, pady=10)
        
        system_button = ctk.CTkButton(
            button_frame,
            text="系统颜色",
            font=self.button_font,
            command=self.choose_system_color,
            fg_color="blue",
            hover_color="darkblue",
        )
        system_button.pack(side="left", padx=10, pady=10)
        
        close_button = ctk.CTkButton(
            button_frame,
            text="关闭",
            font=self.button_font,
            command=self.on_close,
            fg_color="red",
            hover_color="darkred",
        )
        close_button.pack(side="right", padx=10, pady=10)
        
        # 初始化颜色显示
        self.update_color_display()
        
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
        
        # 更新颜色预览
        self.color_preview.delete("all")
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        self.color_preview.create_rectangle(0, 0, 150, 100, fill=hex_color, outline="")
        
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
        
        # 更新颜色预览
        self.color_preview.delete("all")
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        self.color_preview.create_rectangle(0, 0, 150, 100, fill=hex_color, outline="")
        
        # 更新RGB滑块和标签
        self.red_slider.set(r)
        self.green_slider.set(g)
        self.blue_slider.set(b)
        self.red_value_label.configure(text=str(r))
        self.green_value_label.configure(text=str(g))
        self.blue_value_label.configure(text=str(b))
        
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
        match = re.match(r'\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)', text)
        
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
        match = re.match(r'#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$', text)
        
        # 当输入内容匹配HEX颜色格式时更新颜色
        if match:
            hex_color = match.group(1)
            
            # 如果是简写格式 #RGB，扩展为 #RRGGBB
            if len(hex_color) == 3:
                hex_color = ''.join([c*2 for c in hex_color])
            
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
        """创建预设颜色按钮"""
        # 预设颜色列表
        preset_colors = [
            # 第一行 - 基础颜色
            "#000000", "#FFFFFF", "#808080", "#800000", "#008000", "#000080", "#808000", "#800080", "#008080", "#C0C0C0",
            # 第二行 - 扩展颜色
            "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF", "#FFA500", "#A52A2A", "#800080", "#008080",
            # 第三行 - 柔和颜色
            "#FFCCCB", "#FFE4B5", "#F0E68C", "#E6E6FA", "#D8BFD8", "#FFB6C1", "#F5DEB3", "#FFDAB9", "#B0E0E6", "#98FB98"
        ]
        
        # 计算每个颜色块的大小和位置
        canvas_width = 460  # 预估宽度
        canvas_height = 100
        color_size = 30
        padding = 5
        cols = 10  # 每行10个颜色
        rows = 3   # 3行
        
        # 计算起始位置使颜色块居中
        total_width = cols * (color_size + padding) - padding
        start_x = (canvas_width - total_width) // 2
        start_y = (canvas_height - rows * (color_size + padding)) // 2
        
        # 创建颜色按钮
        for i, color in enumerate(preset_colors):
            row = i // cols
            col = i % cols
            
            x = start_x + col * (color_size + padding)
            y = start_y + row * (color_size + padding)
            
            # 创建颜色按钮
            btn = tk.Button(
                self.preset_canvas,
                bg=color,
                width=color_size,
                height=color_size,
                relief=tk.RAISED,
                bd=1,
                command=lambda c=color: self.on_preset_color_click(c)
            )
            btn.place(x=x, y=y)
            
            # 添加悬停效果
            btn.bind("<Enter>", lambda e, b=btn: b.config(relief=tk.SUNKEN))
            btn.bind("<Leave>", lambda e, b=btn: b.config(relief=tk.RAISED))
            
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
        self.dialog.after(1000, lambda: self.rgb_copy_btn.configure(
            text=original_text, 
            fg_color=original_fg_color
        ))
        
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
        self.dialog.after(1000, lambda: self.hex_copy_btn.configure(
            text=original_text, 
            fg_color=original_fg_color
        ))
        
    def choose_system_color(self):
        """调用系统颜色选择器"""
        # 隐藏当前对话框
        self.dialog.withdraw()
        
        # 打开系统颜色选择器
        color = colorchooser.askcolor(initialcolor=f"#{self.current_color[0]:02x}{self.current_color[1]:02x}{self.current_color[2]:02x}")
        
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
            self.pick_window.attributes('-alpha', 0.2)  # 设置窗口透明度
            self.pick_window.attributes('-fullscreen', True)  # 全屏
            self.pick_window.attributes('-topmost', True)  # 置顶
            self.pick_window.config(cursor="crosshair")  # 设置十字光标
            self.pick_window.config(bg='black')
            
            # 绑定鼠标事件
            self.pick_window.bind('<Button-1>', self._on_pick_click)
            self.pick_window.bind('<Escape>', self._on_pick_cancel)
            
            # 创建一个框架来容纳所有标签，这样可以避免标签重叠
            self.info_frame = tk.Frame(
                self.pick_window,
                bg='white',  # 白色背景确保内容清晰可见
                padx=10,
                pady=10,
                relief='solid',  # 添加边框
                bd=2
            )
            self.info_frame.place(x=10, y=10)
            
            # 添加提示标签
            self.pick_label = tk.Label(
                self.info_frame,
                text="点击拾取颜色, 按ESC取消",
                font=(self.font_family, self.font_size, self.font_weight),
                bg='white',
                fg='black'
            )
            self.pick_label.pack(anchor='w', pady=(0, 10))
            
            # 添加当前颜色预览
            self.color_preview_label = tk.Label(
                self.info_frame,
                text="当前颜色预览",
                font=(self.font_family, self.font_size, self.font_weight),
                bg='white',
                fg='black'
            )
            self.color_preview_label.pack(anchor='w', pady=(0, 5))
            
            self.color_display = tk.Label(
                self.info_frame,
                text="",
                width=20,
                height=2,
                bg='black',
                relief='solid',
                bd=1
            )
            self.color_display.pack(anchor='w', pady=(0, 10))
            
            self.color_info_label = tk.Label(
                self.info_frame,
                text="RGB: (0, 0, 0)\nHEX: #000000",
                font=(self.font_family, self.font_size, self.font_weight),
                bg='white',
                fg='black',
                justify='left'
            )
            self.color_info_label.pack(anchor='w')
            
            # 简化鼠标移动事件处理，减少性能消耗
            self.pick_window.bind('<Motion>', self._on_mouse_move)
            
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
            screen = ImageGrab.grab(bbox=(x, y, x+1, y+1))
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
        if hasattr(self, 'pick_window') and self.pick_window:
            self.pick_window.destroy()
            self.pick_window = None
        
        # 重新显示主对话框
        self.dialog.deiconify()


def show_rgb_color_picker(parent, callback=None):
    """
    显示RGB颜色选择器的便捷函数

    Args:
        parent: 父窗口
        callback: 不再使用，保留为向后兼容
    """
    return RGBColorPicker(parent, callback)