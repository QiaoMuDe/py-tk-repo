#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
字体设置对话框模块
"""

import tkinter as tk
from tkinter import font
import customtkinter as ctk
from config.config_manager import config_manager


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

    def __init__(self, root=None, title="字体设置"):
        """
        初始化字体设置对话框

        Args:
            root: 父窗口对象
            title: 对话框标题
        """
        self.root = root
        self.text_widget = root.text_area
        self.dialog = ctk.CTkToplevel()
        self.dialog.title(title)

        # 居中显示
        self.width = 850
        self.height = 500
        root.center_window(self.dialog, self.width, self.height)

        self.dialog.resizable(False, False)  # 固定大小，不允许调整
        self.dialog.grab_set()  # 模态窗口
        self.dialog.attributes("-topmost", True)  # 始终置顶

        # 使用导入的配置管理器实例
        self.config_manager = config_manager

        # 获取编辑器文本框字体配置
        editor_font_config = self.config_manager.get_font_config("text_editor")

        # 创建临时字体对象，基于主窗口文本框字体配置
        self.temp_font = {
            "family": editor_font_config.get("font", "Microsoft YaHei UI"),
            "size": editor_font_config.get("font_size", 13),
            "weight": (
                "bold" if editor_font_config.get("font_bold", False) else "normal"
            ),
        }

        # 保存原始字体配置，用于取消时恢复
        self.original_font = self.temp_font.copy()

        # 获取组件默认字体配置用于UI组件
        component_font_config = self.config_manager.get_font_config("components")
        self.component_font = {
            "family": component_font_config.get("font", "Microsoft YaHei UI"),
            "size": component_font_config.get("font_size", 12),
            "weight": (
                "bold" if component_font_config.get("font_bold", False) else "normal"
            ),
        }

        self.font_list = []
        self.filtered_fonts = []

        # 初始化UI
        self._init_ui()

        # 加载系统字体
        self._load_system_fonts()

        # 默认选择临时字体
        if self.temp_font["family"] in self.filtered_fonts:
            # 如果临时字体在列表中，选择它
            index = self.filtered_fonts.index(self.temp_font["family"])
            self.font_listbox.selection_set(index)
            self.font_listbox.see(index)
        elif self.filtered_fonts:
            # 否则选择第一个字体
            self.font_listbox.selection_set(0)
            self.font_listbox.see(0)
            self._update_preview()
        else:
            # 确保即使没有字体被选中也会更新预览
            self._update_preview()

    def _init_ui(self):
        """
        初始化用户界面
        """
        # 获取组件默认字体配置
        component_font_config = self.config_manager.get_font_config("components")
        component_font = ctk.CTkFont(
            family=component_font_config.get("font", "Microsoft YaHei UI"),
            size=component_font_config.get("font_size", 12),
            weight=(
                "bold" if component_font_config.get("font_bold", False) else "normal"
            ),
        )

        # 创建标题字体，比组件字体大2号并加粗
        title_font = ctk.CTkFont(
            family=component_font_config.get("font", "Microsoft YaHei UI"),
            size=component_font_config.get("font_size", 12) + 2,
            weight="bold",
        )

        # 整体布局使用网格布局
        self.dialog.grid_columnconfigure(0, weight=1)
        self.dialog.grid_rowconfigure(0, weight=1)

        # 主框架：分为左右两部分 - 使用透明背景，与窗体融为一体
        main_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # 左侧：字体设置区域 - 透明背景，与窗体融为一体
        left_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=0)
        left_frame.grid_rowconfigure(2, weight=1)
        left_frame.grid_rowconfigure(3, weight=0)

        # 字体标题
        font_label = ctk.CTkLabel(left_frame, text="字体", font=title_font)
        font_label.grid(row=0, column=0, sticky="w", padx=5, pady=(5, 2))

        # 字体搜索区域 - 透明背景，与窗体融为一体
        search_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        search_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        search_frame.grid_columnconfigure(0, weight=1)

        self.search_var = tk.StringVar()
        self.search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="搜索字体...",
            font=component_font,
            corner_radius=4,
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.search_entry.bind("<KeyRelease>", self._on_search)

        self.search_button = ctk.CTkButton(
            search_frame,
            text="搜索",
            width=80,
            command=self._on_search,
            font=component_font,
            corner_radius=4,
        )
        self.search_button.grid(row=0, column=1, padx=(0, 5), pady=5)

        # 字体列表容器 - 透明背景，与窗体融为一体
        list_container = ctk.CTkFrame(
            left_frame, fg_color="transparent", border_width=1
        )
        list_container.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        list_container.grid_columnconfigure(0, weight=1)
        list_container.grid_rowconfigure(0, weight=1)

        # 字体列表框架 - 将列表和滚动条放在同一个框架中
        list_frame = ctk.CTkFrame(list_container, fg_color="transparent")
        list_frame.grid(row=0, column=0, sticky="nsew", padx=3, pady=3)
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)

        # 字体列表 - 使用tk.Listbox + CTkScrollbar
        # 创建tkinter兼容的字体元组
        listbox_font = (
            component_font_config.get("font", "Microsoft YaHei UI"),
            component_font_config.get("font_size", 12),
            "bold" if component_font_config.get("font_bold", False) else "normal",
        )
        self.font_listbox = tk.Listbox(
            list_frame,
            exportselection=False,
            activestyle="none",
            selectmode="single",
            font=listbox_font,
            borderwidth=0,
            relief="flat",
            highlightthickness=0,
        )
        self.font_listbox.grid(row=0, column=0, sticky="nsew")

        # 滚动条 - 使用CTkScrollbar
        font_scrollbar = ctk.CTkScrollbar(
            list_frame,
            orientation="vertical",
            command=self.font_listbox.yview,
            corner_radius=4,
        )
        font_scrollbar.grid(row=0, column=1, sticky="ns")
        self.font_listbox.configure(yscrollcommand=font_scrollbar.set)

        # 绑定列表选择事件
        self.font_listbox.bind("<<ListboxSelect>>", self._on_font_select)

        # 字体设置区域 - 透明背景，与窗体融为一体
        size_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        size_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=(5, 8))

        # 配置列权重，让布局更加灵活
        size_frame.grid_columnconfigure(0, weight=0)
        size_frame.grid_columnconfigure(1, weight=0)
        size_frame.grid_columnconfigure(2, weight=0)
        size_frame.grid_columnconfigure(3, weight=0)
        size_frame.grid_columnconfigure(4, weight=1)
        size_frame.grid_columnconfigure(5, weight=0)

        # 字体设置标题 - 居中显示，包含大小范围信息
        size_title_label = ctk.CTkLabel(
            size_frame, text="字体设置 (大小范围: 8-72)", font=title_font
        )
        size_title_label.grid(
            row=0, column=0, columnspan=6, sticky="ew", padx=10, pady=(8, 8)
        )

        # 字体大小标签
        size_label = ctk.CTkLabel(size_frame, text="大小:", font=component_font)
        size_label.grid(row=1, column=0, padx=(10, 10), pady=(5, 10), sticky="w")

        # 减小字体按钮
        self.size_decrease_btn = ctk.CTkButton(
            size_frame,
            text="-",
            width=40,
            height=30,
            command=self._decrease_font_size,
            font=component_font,
            corner_radius=4,
        )
        self.size_decrease_btn.grid(row=1, column=1, padx=(0, 5), pady=(5, 10))

        # 字体大小输入框
        self.size_var = tk.StringVar(value=str(self.temp_font["size"]))
        self.size_entry = ctk.CTkEntry(
            size_frame,
            textvariable=self.size_var,
            width=70,
            height=30,
            font=component_font,
            justify="center",
            corner_radius=4,
        )
        self.size_entry.grid(row=1, column=2, padx=(0, 5), pady=(5, 10))
        self.size_entry.bind("<KeyRelease>", self._on_size_change)

        # 增大字体按钮
        self.size_increase_btn = ctk.CTkButton(
            size_frame,
            text="+",
            width=40,
            height=30,
            command=self._increase_font_size,
            font=component_font,
            corner_radius=4,
        )
        self.size_increase_btn.grid(row=1, column=3, padx=(0, 10), pady=(5, 10))

        # 加粗选项 - 放在右侧并居中对齐
        self.bold_var = tk.BooleanVar(value=(self.temp_font["weight"] == "bold"))
        self.bold_checkbox = ctk.CTkCheckBox(
            size_frame,
            text="加粗",
            variable=self.bold_var,
            command=self._update_preview,
            font=component_font,
            corner_radius=4,
        )
        self.bold_checkbox.grid(row=1, column=5, padx=(0, 10), pady=(5, 10), sticky="e")

        # 右侧：预览区域 - 透明背景，与窗体融为一体
        right_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 8), pady=8)
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_rowconfigure(2, weight=0)

        # 预览标签
        preview_label = ctk.CTkLabel(right_frame, text="字体预览", font=title_font)
        preview_label.grid(row=0, column=0, sticky="w", padx=10, pady=(8, 5))

        # 预览文本容器 - 透明背景，与窗体融为一体
        preview_container = ctk.CTkFrame(right_frame, fg_color="transparent")
        preview_container.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        preview_container.grid_columnconfigure(0, weight=1)
        preview_container.grid_rowconfigure(0, weight=1)

        # 使用临时字体作为预览文本框的字体
        preview_font = ctk.CTkFont(
            family=self.temp_font["family"],
            size=self.temp_font["size"],
            weight=self.temp_font["weight"],
        )

        # 使用CTkTextbox作为预览文本框
        self.preview_text = ctk.CTkTextbox(
            preview_container,
            wrap="word",
            font=preview_font,
            corner_radius=6,
            border_width=1,
            border_color="#343638",
        )
        self.preview_text.grid(row=0, column=0, sticky="nsew", padx=3, pady=3)

        # 插入预览文本
        self.preview_text.insert(
            "0.0",
            "这是字体预览文本\nThe quick brown fox jumps over the lazy dog\nABCDEFGHIJKLMNOPQRSTUVWXYZ\nabcdefghijklmnopqrstuvwxyz\n1234567890\n!@#$%^&*()",
        )
        self.preview_text.configure(state="disabled")

        # 按钮区域 - 透明背景，与窗体融为一体
        button_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 8))
        button_frame.grid_columnconfigure(0, weight=1)

        # 按钮容器，用于居中按钮
        button_container = ctk.CTkFrame(button_frame, fg_color="transparent")
        button_container.grid(row=0, column=0, pady=8)

        self.ok_button = ctk.CTkButton(
            button_container,
            text="确定",
            command=self._on_ok,
            font=component_font,
            width=100,
            height=32,
            corner_radius=6,
        )
        self.ok_button.grid(row=0, column=0, padx=(10, 5), pady=5)

        self.cancel_button = ctk.CTkButton(
            button_container,
            text="取消",
            command=self._on_cancel,
            font=component_font,
            width=100,
            height=32,
            corner_radius=6,
        )
        self.cancel_button.grid(row=0, column=1, padx=(5, 10), pady=5)

        # 绑定ESC键到取消，Enter键到确定
        self.dialog.bind("<Escape>", lambda e: self._on_cancel())
        self.dialog.bind("<Return>", lambda e: self._on_ok())

        # 绑定上下箭头键导航字体列表
        self.dialog.bind("<Up>", self._on_font_list_up)
        self.dialog.bind("<Down>", self._on_font_list_down)

        # 确保字体列表框可以接收焦点
        self.font_listbox.bind("<Button-1>", self._on_font_list_click)

    def _on_font_list_up(self, event=None):
        """处理字体列表向上导航"""
        try:
            # 确保字体列表框有焦点
            self.font_listbox.focus_set()

            current_selection = self.font_listbox.curselection()
            if current_selection:
                current_index = current_selection[0]
                if current_index > 0:
                    # 选择上一项
                    self.font_listbox.selection_clear(current_index)
                    self.font_listbox.selection_set(current_index - 1)
                    self.font_listbox.see(current_index - 1)
                    self._update_preview()
            else:
                # 如果没有选中项，选择第一项
                if self.filtered_fonts:
                    self.font_listbox.selection_set(0)
                    self.font_listbox.see(0)
                    self._update_preview()
        except:
            pass
        return "break"  # 阻止默认行为

    def _on_font_list_down(self, event=None):
        """处理字体列表向下导航"""
        try:
            # 确保字体列表框有焦点
            self.font_listbox.focus_set()

            current_selection = self.font_listbox.curselection()
            if current_selection:
                current_index = current_selection[0]
                if current_index < len(self.filtered_fonts) - 1:
                    # 选择下一项
                    self.font_listbox.selection_clear(current_index)
                    self.font_listbox.selection_set(current_index + 1)
                    self.font_listbox.see(current_index + 1)
                    self._update_preview()
            else:
                # 如果没有选中项，选择第一项
                if self.filtered_fonts:
                    self.font_listbox.selection_set(0)
                    self.font_listbox.see(0)
                    self._update_preview()
        except:
            pass
        return "break"  # 阻止默认行为

    def _on_font_list_click(self, event=None):
        """处理字体列表点击事件，确保焦点正确设置"""
        # 让列表框获取焦点，这样上下箭头键可以正常工作
        self.font_listbox.focus_set()

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

            # 填充字体列表到tk.Listbox
            for font_name in self.filtered_fonts:
                self.font_listbox.insert(tk.END, font_name)
        except Exception as e:
            # 如果获取系统字体失败，使用一些常见字体作为备选
            fallback_fonts = [
                "Arial",
                "Helvetica",
                "Times New Roman",
                "Courier New",
                "Microsoft YaHei UI",
                "SimHei",
                "SimSun",
            ]
            self.font_list = fallback_fonts
            self.filtered_fonts = fallback_fonts.copy()

            # 将备选字体添加到tk.Listbox中
            for font_name in self.filtered_fonts:
                self.font_listbox.insert(tk.END, font_name)

        # 默认选择临时字体
        if self.temp_font["family"] in self.filtered_fonts:
            # 如果临时字体在列表中，选择它
            index = self.filtered_fonts.index(self.temp_font["family"])
            self.font_listbox.selection_set(index)
            self.font_listbox.see(index)
        elif self.filtered_fonts:
            # 否则选择第一个字体
            self.font_listbox.selection_set(0)
            self.font_listbox.see(0)

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
        # 获取选中的索引
        selected_indices = self.font_listbox.curselection()

        # 确保有选中的项
        if selected_indices:
            # 获取选中项的索引
            index = selected_indices[0]

            # 确保索引在有效范围内
            if 0 <= index < len(self.filtered_fonts):
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
        self.font_listbox.delete(0, tk.END)

        # 过滤字体列表
        self.filtered_fonts = [
            font_name
            for font_name in self.font_list
            if search_text in font_name.lower()
        ]

        # 填充过滤后的字体列表到tk.Listbox
        for font_name in self.filtered_fonts:
            self.font_listbox.insert(tk.END, font_name)

        # 自动选择第一个匹配的字体
        if self.filtered_fonts:
            self.font_listbox.selection_set(0)
            self.font_listbox.see(0)
            self._update_preview()

    def _update_preview(self, event=None):
        """
        更新预览文本框的字体样式

        Args:
            event: 事件对象（列表选择事件）
        """
        # 获取选中的字体
        try:
            # 获取选中的索引
            selected_indices = self.font_listbox.curselection()
            if selected_indices:
                # 获取选中项的索引
                index = selected_indices[0]
                # 确保索引在有效范围内
                if 0 <= index < len(self.filtered_fonts):
                    # 获取选中的字体名称
                    font_name = self.filtered_fonts[index]
                else:
                    font_name = self.temp_font["family"]
            else:
                font_name = self.temp_font["family"]
        except:
            font_name = self.temp_font["family"]

        # 获取字体大小从输入框
        try:
            font_size = int(self.size_var.get())
            if font_size < 8:
                font_size = 8
            elif font_size > 72:
                font_size = 72
        except:
            font_size = self.temp_font["size"]

        # 获取字体粗细
        font_weight = "bold" if self.bold_var.get() else "normal"

        # 更新临时字体
        self.temp_font = {"family": font_name, "size": font_size, "weight": font_weight}

        # 更新预览文本框的字体
        preview_font = ctk.CTkFont(family=font_name, size=font_size, weight=font_weight)
        self.preview_text.configure(font=preview_font)

    def _on_ok(self):
        """
        确认字体设置并关闭对话框
        """
        # 更新配置管理器中的文本框字体配置
        self.config_manager.set("text_editor.font", self.temp_font["family"])
        self.config_manager.set("text_editor.font_size", self.temp_font["size"])
        self.config_manager.set(
            "text_editor.font_bold", (self.temp_font["weight"] == "bold")
        )

        # 保存配置
        self.config_manager.save_config()

        # 更新文本框字体
        text_font = ctk.CTkFont(
            family=self.temp_font["family"],
            size=self.temp_font["size"],
            weight=self.temp_font["weight"],
        )
        self.text_widget.configure(font=text_font)

        # 更新行号栏字体
        if hasattr(self.root, "line_number_canvas"):
            self.root.line_number_canvas.update_font(
                font_family=self.temp_font["family"], font_size=self.temp_font["size"]
            )

        # 显示通知
        font_weight_text = "加粗" if self.temp_font["weight"] == "bold" else "常规"
        # self.root.status_bar.show_notification(
        #     f"字体设置成功: {self.temp_font['family']} {self.temp_font['size']}pt {font_weight_text}"
        # )
        self.root.nm.show_info(
            message=f"字体设置成功: {self.temp_font['family']} {self.temp_font['size']}pt {font_weight_text}"
        )

        # 延迟关闭对话框，确保回调函数执行完毕
        self.dialog.after(100, self.dialog.destroy)

    def _on_cancel(self):
        """
        取消字体设置并关闭对话框
        """
        # 恢复临时字体为原始字体
        self.temp_font = self.original_font.copy()

        # 延迟关闭对话框，确保回调函数执行完毕
        self.dialog.after(100, self.dialog.destroy)


def show_font_dialog(root):
    """
    显示字体设置对话框的便捷函数

    Args:
        root: app.QuickEditApp实例
    """
    dialog = FontDialog(root)
