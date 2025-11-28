#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文件属性对话框模块
"""

import os
import time
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from config.config_manager import config_manager
from loguru import logger


class FilePropertiesDialog(ctk.CTkToplevel):
    """文件属性对话框类"""

    def __init__(self, parent, file_path):
        """
        初始化文件属性对话框

        Args:
            parent: 父窗口
            file_path: 文件路径
        """
        super().__init__(parent)
        self.parent = parent
        self.file_path = file_path

        # 获取配置管理器中的字体设置
        self.font_family = config_manager.get("components.font", "Microsoft YaHei UI")
        self.font_size = config_manager.get("components.font_size", 13)
        self.font_bold = config_manager.get("components.font_bold", False)
        self.title_font_size = self.font_size + 1  # 标题字体稍大一些

        # 设置窗口属性
        self.title("文件属性")

        # 居中显示窗口
        self.width = 700  # 宽度
        self.height = 600  # 高度
        self.parent.center_window(self, self.width, self.height)

        # 设置窗口非可调整大小
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # 设置窗口标题字体
        self.option_add(
            "*TLabel.font",
            ctk.CTkFont(
                family=self.font_family, size=self.title_font_size, weight="bold"
            ),
        )

        # 绑定ESC键关闭窗口
        self.bind("<Escape>", lambda e: self.destroy())

        # 创建界面
        self._create_widgets()

        # 加载文件属性
        self._load_file_properties()

    def _create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # 文件路径框架
        path_frame = ctk.CTkFrame(main_frame)
        path_frame.pack(fill="x", pady=(0, 10))

        path_label = ctk.CTkLabel(
            path_frame,
            text="文件路径:",
            font=ctk.CTkFont(
                size=self.title_font_size, weight="bold", family=self.font_family
            ),
        )
        path_label.pack(anchor="w", padx=10, pady=(10, 5))

        self.path_value = ctk.CTkLabel(
            path_frame,
            text="",
            font=ctk.CTkFont(size=self.font_size, family=self.font_family),
        )
        self.path_value.pack(anchor="w", padx=10, pady=(0, 10))

        # 基本属性框架
        basic_frame = ctk.CTkFrame(main_frame)
        basic_frame.pack(fill="x", pady=(0, 10))

        basic_label = ctk.CTkLabel(
            basic_frame,
            text="基本属性",
            font=ctk.CTkFont(
                size=self.title_font_size, weight="bold", family=self.font_family
            ),
        )
        basic_label.pack(anchor="w", padx=10, pady=(10, 5))

        # 文件名
        name_frame = ctk.CTkFrame(basic_frame)
        name_frame.pack(fill="x", padx=10, pady=(0, 5))
        name_label = ctk.CTkLabel(
            name_frame,
            text="文件名:",
            width=100,
            font=ctk.CTkFont(size=self.font_size, family=self.font_family),
        )
        name_label.pack(side="left", padx=(0, 10))
        self.name_value = ctk.CTkLabel(name_frame, text="")
        name_value_frame = ctk.CTkFrame(name_frame, fg_color="transparent")
        name_value_frame.pack(side="left", fill="x", expand=True)
        self.name_value = ctk.CTkLabel(
            name_value_frame,
            text="",
            font=ctk.CTkFont(size=self.font_size, family=self.font_family),
        )
        self.name_value.pack(side="left")

        # 文件类型
        type_frame = ctk.CTkFrame(basic_frame)
        type_frame.pack(fill="x", padx=10, pady=(0, 5))
        type_label = ctk.CTkLabel(
            type_frame,
            text="文件类型:",
            width=100,
            font=ctk.CTkFont(size=self.font_size, family=self.font_family),
        )
        type_label.pack(side="left", padx=(0, 10))
        self.type_value = ctk.CTkLabel(
            type_frame,
            text="",
            font=ctk.CTkFont(size=self.font_size, family=self.font_family),
        )
        self.type_value.pack(side="left")

        # 文件大小
        size_frame = ctk.CTkFrame(basic_frame)
        size_frame.pack(fill="x", padx=10, pady=(0, 5))
        size_label = ctk.CTkLabel(
            size_frame,
            text="文件大小:",
            width=100,
            font=ctk.CTkFont(size=self.font_size, family=self.font_family),
        )
        size_label.pack(side="left", padx=(0, 10))
        self.size_value = ctk.CTkLabel(
            size_frame,
            text="",
            font=ctk.CTkFont(size=self.font_size, family=self.font_family),
        )
        self.size_value.pack(side="left")

        # 时间属性框架
        time_frame = ctk.CTkFrame(main_frame)
        time_frame.pack(fill="x", pady=(0, 10))

        time_label = ctk.CTkLabel(
            time_frame,
            text="时间属性",
            font=ctk.CTkFont(
                size=self.title_font_size, weight="bold", family=self.font_family
            ),
        )
        time_label.pack(anchor="w", padx=10, pady=(10, 5))

        # 创建时间
        created_frame = ctk.CTkFrame(time_frame)
        created_frame.pack(fill="x", padx=10, pady=(0, 5))
        created_label = ctk.CTkLabel(
            created_frame,
            text="创建时间:",
            width=100,
            font=ctk.CTkFont(size=self.font_size, family=self.font_family),
        )
        created_label.pack(side="left", padx=(0, 10))
        self.created_value = ctk.CTkLabel(
            created_frame,
            text="",
            font=ctk.CTkFont(size=self.font_size, family=self.font_family),
        )
        self.created_value.pack(side="left")

        # 修改时间
        modified_frame = ctk.CTkFrame(time_frame)
        modified_frame.pack(fill="x", padx=10, pady=(0, 5))
        modified_label = ctk.CTkLabel(
            modified_frame,
            text="修改时间:",
            width=100,
            font=ctk.CTkFont(size=self.font_size, family=self.font_family),
        )
        modified_label.pack(side="left", padx=(0, 10))
        self.modified_value = ctk.CTkLabel(
            modified_frame,
            text="",
            font=ctk.CTkFont(size=self.font_size, family=self.font_family),
        )
        self.modified_value.pack(side="left")

        # 访问时间
        accessed_frame = ctk.CTkFrame(time_frame)
        accessed_frame.pack(fill="x", padx=10, pady=(0, 10))
        accessed_label = ctk.CTkLabel(
            accessed_frame,
            text="访问时间:",
            width=100,
            font=ctk.CTkFont(size=self.font_size, family=self.font_family),
        )
        accessed_label.pack(side="left", padx=(0, 10))
        self.accessed_value = ctk.CTkLabel(
            accessed_frame,
            text="",
            font=ctk.CTkFont(size=self.font_size, family=self.font_family),
        )
        self.accessed_value.pack(side="left")

        # 其他属性框架
        other_frame = ctk.CTkFrame(main_frame)
        other_frame.pack(fill="x", pady=(0, 10))

        other_label = ctk.CTkLabel(
            other_frame,
            text="其他属性",
            font=ctk.CTkFont(
                size=self.title_font_size, weight="bold", family=self.font_family
            ),
        )
        other_label.pack(anchor="w", padx=10, pady=(10, 5))

        # 只读属性
        readonly_frame = ctk.CTkFrame(other_frame)
        readonly_frame.pack(fill="x", padx=10, pady=(0, 5))
        readonly_label = ctk.CTkLabel(
            readonly_frame,
            text="只读属性:",
            width=100,
            font=ctk.CTkFont(size=self.font_size, family=self.font_family),
        )
        readonly_label.pack(side="left", padx=(0, 10))
        self.readonly_value = ctk.CTkLabel(
            readonly_frame,
            text="",
            font=ctk.CTkFont(size=self.font_size, family=self.font_family),
        )
        self.readonly_value.pack(side="left")

        # 隐藏属性
        hidden_frame = ctk.CTkFrame(other_frame)
        hidden_frame.pack(fill="x", padx=10, pady=(0, 10))
        hidden_label = ctk.CTkLabel(
            hidden_frame,
            text="隐藏属性:",
            width=100,
            font=ctk.CTkFont(size=self.font_size, family=self.font_family),
        )
        hidden_label.pack(side="left", padx=(0, 10))
        self.hidden_value = ctk.CTkLabel(
            hidden_frame,
            text="",
            font=ctk.CTkFont(size=self.font_size, family=self.font_family),
        )
        self.hidden_value.pack(side="left")

        # 按钮框架
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=(5, 0))

        # 提示标签
        hint_label = ctk.CTkLabel(
            button_frame,
            text="提示: 文件属性信息仅供参考，实际属性可能因系统而异",
            font=ctk.CTkFont(size=self.font_size - 1, family=self.font_family),
            text_color=("gray50", "gray60"),
        )
        hint_label.pack(side="left", padx=10, pady=5)

        # 关闭按钮
        close_button = ctk.CTkButton(
            button_frame,
            text="关闭",
            command=self.destroy,
            font=ctk.CTkFont(size=self.font_size, family=self.font_family),
        )
        close_button.pack(side="right", padx=10, pady=5)

    def _load_file_properties(self):
        """加载文件属性"""
        try:
            # 文件路径
            self.path_value.configure(text=self.file_path)

            # 文件名
            file_name = os.path.basename(self.file_path)
            self.name_value.configure(text=file_name)

            # 文件类型
            if os.path.isdir(self.file_path):
                file_type = "文件夹"
            else:
                _, ext = os.path.splitext(file_name)
                file_type = ext if ext else "未知类型"
            self.type_value.configure(text=file_type)

            # 文件大小
            if os.path.isdir(self.file_path):
                size_text = "文件夹"
            else:
                size_bytes = os.path.getsize(self.file_path)
                size_text = self._format_size(size_bytes)
            self.size_value.configure(text=size_text)

            # 时间属性
            if os.name == "nt":  # Windows
                created_time = os.path.getctime(self.file_path)
                modified_time = os.path.getmtime(self.file_path)
                accessed_time = os.path.getatime(self.file_path)
            else:  # Unix/Linux/Mac
                stat = os.stat(self.file_path)
                created_time = stat.st_ctime
                modified_time = stat.st_mtime
                accessed_time = stat.st_atime

            self.created_value.configure(text=self._format_time(created_time))
            self.modified_value.configure(text=self._format_time(modified_time))
            self.accessed_value.configure(text=self._format_time(accessed_time))

            # 其他属性
            if os.name == "nt":  # Windows
                import stat

                file_stat = os.stat(self.file_path)
                is_readonly = not (file_stat.st_mode & stat.S_IWRITE)
                is_hidden = (
                    file_stat.st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN
                    if hasattr(file_stat, "st_file_attributes")
                    else False
                )
            else:  # Unix/Linux/Mac
                import stat

                file_stat = os.stat(self.file_path)
                is_readonly = not (file_stat.st_mode & stat.S_IWUSR)
                is_hidden = file_name.startswith(".")

            self.readonly_value.configure(text="是" if is_readonly else "否")
            self.hidden_value.configure(text="是" if is_hidden else "否")

        except Exception as e:
            messagebox.showerror("错误", f"无法获取文件属性:\n{str(e)}")
            self.destroy()

    def _format_size(self, size_bytes):
        """
        格式化文件大小

        Args:
            size_bytes: 文件大小（字节）

        Returns:
            格式化后的文件大小字符串
        """
        if size_bytes < 1024:
            return f"{size_bytes} 字节"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

    def _format_time(self, timestamp):
        """
        格式化时间戳

        Args:
            timestamp: 时间戳

        Returns:
            格式化后的时间字符串
        """
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")


def show_file_properties_dialog(parent, file_path):
    """
    显示文件属性对话框

    Args:
        parent: 父窗口
        file_path: 文件路径
    """
    if not file_path or not os.path.exists(file_path):
        messagebox.showerror("错误", "当前没有打开文件")
        return

    dialog = FilePropertiesDialog(parent, file_path)
    return dialog


def update_file_properties_menu_state(app):
    """
    更新文件属性菜单项的状态（启用/禁用）
    根据是否有当前打开的文件来决定菜单项是否可用

    Args:
        app: 应用程序实例，包含以下属性：
            - file_menu: 文件菜单对象
            - file_properties_menu_index: 文件属性菜单项的索引
            - current_file_path: 当前打开文件的路径
    """
    has_current_file = app.current_file_path

    # 设置菜单状态
    state = "normal" if has_current_file else "disabled"

    # 使用保存的索引直接禁用或启用文件属性菜单项
    if app.file_menu and app.file_properties_menu_index is not None:
        try:
            app.file_menu.entryconfig(app.file_properties_menu_index, state=state)
        except Exception as e:
            # 如果通过索引更新失败，打印错误信息
            logger.error(
                f"Error updating file properties menu state at index {app.file_properties_menu_index}: {e}"
            )
