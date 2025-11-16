#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
工具栏界面模块
"""

import os
import customtkinter as ctk
import tkinter as tk
from PIL import Image
from config.config_manager import config_manager
from ui.find_replace_dialog import show_find_replace_dialog


class Toolbar(ctk.CTkFrame):
    """工具栏类"""

    def __init__(self, parent):
        """初始化工具栏"""
        super().__init__(parent, height=50, corner_radius=0)

        # 保存对父窗口的引用
        self.parent = parent

        # 获取工具栏字体配置
        font_config = config_manager.get_font_config("toolbar")
        self.button_font = (
            font_config.get("font", "Microsoft YaHei"),
            font_config.get("font_size", 12),
            "bold" if font_config.get("font_bold", False) else "normal",
        )

        # 创建工具栏按钮
        self._create_buttons()

    def load_icon(self, icon_name, name, size=(20, 20)):
        """
        加载图标文件

        参数:
            icon_name (str): 图标文件名（不含扩展名）
            name (str): 按钮名称
            size (tuple): 图标尺寸，默认为(20, 20)

        返回:
            tuple: (图标对象, 按钮名称)
                - 如果图标加载成功，返回(图标对象, None)
                - 如果图标加载失败，返回(None, 按钮名称)
        """
        # 构建图标文件路径
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "icons", f"{icon_name}.png"
        )

        # 检查文件是否存在
        if not os.path.exists(icon_path):
            return None, name

        try:
            # 加载图像并创建CTkImage对象
            icon_image = Image.open(icon_path)
            return (
                ctk.CTkImage(light_image=icon_image, dark_image=icon_image, size=size),
                None,  # 图标加载成功，名称设为None
            )
        except Exception as e:
            return None, name

    def _create_buttons(self):
        """创建工具栏按钮"""
        # 加载新建按钮图标
        new_icon, new_name = self.load_icon("new_file", "新建")

        # 加载打开按钮图标
        open_icon, open_name = self.load_icon("open", "打开")

        # 保存按钮图标
        save_icon, save_name = self.load_icon("save", "保存")

        # 另存为按钮图标
        save_as_icon, save_as_name = self.load_icon("save_as", "另存为")

        # 关闭按钮图标
        close_icon, close_name = self.load_icon("close", "关闭")

        # 只读按钮图标
        readonly_icon, readonly_name = self.load_icon("read_only", "只读")

        # 撤销按钮图标
        undo_icon, undo_name = self.load_icon("undo", "撤销")

        # 重做按钮图标
        redo_icon, redo_name = self.load_icon("redo", "重做")

        # 剪切按钮图标
        cut_icon, cut_name = self.load_icon("cut", "剪切")

        # 复制按钮图标
        copy_icon, copy_name = self.load_icon("copy", "复制")

        # 粘贴按钮图标
        paste_icon, paste_name = self.load_icon("paste", "粘贴")

        # 查找按钮图标
        find_replace_icon, find_replace_name = self.load_icon("find", "查找替换")

        # 全屏按钮图标
        fullscreen_icon, fullscreen_name = self.load_icon("fullscreen", "全屏")

        # 退出按钮图标
        exit_icon, exit_name = self.load_icon("exit", "退出")

        # 新建按钮
        self.new_button = ctk.CTkButton(
            self,
            text=new_name,
            width=30 if new_name is None else 60,  # 如果有图标则减小宽度
            height=30,
            font=self.button_font,
            command=self.parent.new_file,
            image=new_icon,
        )
        self.new_button.pack(side="left", padx=2, pady=10)

        # 打开按钮
        self.open_button = ctk.CTkButton(
            self,
            text=open_name,
            width=30 if open_name is None else 60,  # 如果有图标则减小宽度
            height=30,
            font=self.button_font,
            command=self.parent.open_file,
            image=open_icon,
        )
        self.open_button.pack(side="left", padx=2, pady=10)

        # 保存按钮
        self.save_button = ctk.CTkButton(
            self,
            text=save_name,
            width=30 if save_name is None else 60,  # 如果有图标则减小宽度
            height=30,
            font=self.button_font,
            image=save_icon,
            command=self.parent.save_file,
        )
        self.save_button.pack(side="left", padx=2, pady=10)

        # 另存为按钮
        self.save_as_button = ctk.CTkButton(
            self,
            text=save_as_name,
            width=30 if save_as_name is None else 60,  # 如果有图标则减小宽度
            height=30,
            font=self.button_font,
            image=save_as_icon,
            command=self.parent.save_file_as,
        )
        self.save_as_button.pack(side="left", padx=2, pady=10)

        # 关闭按钮
        self.close_button = ctk.CTkButton(
            self,
            text=close_name,
            width=30 if close_name is None else 60,  # 如果有图标则减小宽度
            height=30,
            font=self.button_font,
            image=close_icon,
            command=self.parent.close_file,
        )
        self.close_button.pack(side="left", padx=2, pady=10)

        # 只读按钮
        self.readonly_button = ctk.CTkButton(
            self,
            text=readonly_name,
            width=30 if readonly_name is None else 60,  # 如果有图标则减小宽度
            height=30,
            font=self.button_font,
            image=readonly_icon,
            command=self.parent.toggle_read_only,
        )
        self.readonly_button.pack(side="left", padx=2, pady=10)

        # 分隔符
        separator = ctk.CTkFrame(self, width=1, height=30, fg_color="#999999")
        separator.pack(side="left", padx=10, pady=10, fill="y")

        # 撤销按钮
        self.undo_button = ctk.CTkButton(
            self,
            text=undo_name,
            width=30 if undo_name is None else 60,  # 如果有图标则减小宽度
            height=30,
            font=self.button_font,
            image=undo_icon,
            command=self.parent.undo,
        )
        self.undo_button.pack(side="left", padx=2, pady=10)

        # 重做按钮
        self.redo_button = ctk.CTkButton(
            self,
            text=redo_name,
            width=30 if redo_name is None else 60,  # 如果有图标则减小宽度
            height=30,
            font=self.button_font,
            image=redo_icon,
            command=self.parent.redo,
        )
        self.redo_button.pack(side="left", padx=2, pady=10)

        # 分隔符
        separator2 = ctk.CTkFrame(self, width=1, height=30, fg_color="#999999")
        separator2.pack(side="left", padx=10, pady=10, fill="y")

        # 剪切按钮
        self.cut_button = ctk.CTkButton(
            self,
            text=cut_name,
            width=30 if cut_name is None else 60,  # 如果有图标则减小宽度
            height=30,
            font=self.button_font,
            image=cut_icon,
            command=self.parent.cut,
        )
        self.cut_button.pack(side="left", padx=2, pady=10)

        # 复制按钮
        self.copy_button = ctk.CTkButton(
            self,
            text=copy_name,
            width=30 if copy_name is None else 60,  # 如果有图标则减小宽度
            height=30,
            font=self.button_font,
            image=copy_icon,
            command=self.parent.copy,
        )
        self.copy_button.pack(side="left", padx=2, pady=10)

        # 粘贴按钮
        self.paste_button = ctk.CTkButton(
            self,
            text=paste_name,
            width=30 if paste_name is None else 60,  # 如果有图标则减小宽度
            height=30,
            font=self.button_font,
            image=paste_icon,
            command=self.parent.paste,
        )
        self.paste_button.pack(side="left", padx=2, pady=10)

        # 分隔符
        separator3 = ctk.CTkFrame(self, width=1, height=30, fg_color="#999999")
        separator3.pack(side="left", padx=10, pady=10, fill="y")

        # 查找替换按钮
        self.find_replace_button = ctk.CTkButton(
            self,
            text=find_replace_name,
            width=30 if find_replace_name is None else 80,  # 如果有图标则减小宽度
            height=30,
            font=self.button_font,
            image=find_replace_icon,
            command=lambda: show_find_replace_dialog(
                self.parent, self.parent.text_area
            ),
        )
        self.find_replace_button.pack(side="left", padx=2, pady=10)

        # 分隔符
        separator4 = ctk.CTkFrame(self, width=1, height=30, fg_color="#999999")
        separator4.pack(side="left", padx=10, pady=10, fill="y")

        # 全屏按钮
        self.fullscreen_button = ctk.CTkButton(
            self,
            text=fullscreen_name,
            width=30 if fullscreen_name is None else 60,  # 如果有图标则减小宽度
            height=30,
            font=self.button_font,
            image=fullscreen_icon,
            command=lambda: self.toggle_fullscreen(fullscreen_name),
        )
        self.fullscreen_button.pack(side="left", padx=2, pady=10)
        # 记录全屏状态
        self.is_fullscreen = False

        # 退出按钮
        self.exit_button = ctk.CTkButton(
            self,
            text=exit_name,
            width=30 if exit_name is None else 60,  # 如果有图标则减小宽度
            height=30,
            font=self.button_font,
            image=exit_icon,
            command=self.parent._on_closing,
        )
        self.exit_button.pack(side="left", padx=2, pady=10)

    def toggle_fullscreen(self, fullscreen_name):
        """
        切换全屏模式
        调用父窗口的全屏方法并更新按钮文本

        Args:
            fullscreen_name (str): 全屏按钮的文本
        """
        # 调用父窗口的全屏方法
        is_fullscreen = self.parent.toggle_fullscreen()

        # 如果没有全屏按钮文本，不更新按钮文本
        if fullscreen_name:
            # 更新按钮文本
            self.fullscreen_button.configure(
                text="退出全屏" if is_fullscreen else "全屏"
            )
