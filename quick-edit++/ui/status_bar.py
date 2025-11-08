#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
状态栏界面模块
"""

import customtkinter as ctk
from config.config_manager import config_manager


class StatusBar(ctk.CTkFrame):
    """状态栏类"""

    def __init__(self, parent, app=None):
        """
        初始化状态栏
        :param parent: 父容器，通常是主窗口
        :param app: APP类实例，用于获取自动保存相关属性
        """
        super().__init__(parent)

        # 设置状态栏高度
        self.configure(height=25)

        # 从配置管理器获取初始设置
        self.encoding = config_manager.get("file.default_encoding", "UTF-8")
        self.line_ending = config_manager.get("file.default_line_ending", "LF")

        # 保存APP类实例引用
        self.app = app

        # 初始化文件信息
        self.filename = None

        # 通知相关属性
        self.notification_active = False
        self.notification_job = None
        self.original_status_text = ""

        # 配置网格布局权重
        self.grid_columnconfigure(0, weight=1)  # 左侧
        self.grid_columnconfigure(1, weight=1)  # 中间
        self.grid_columnconfigure(2, weight=1)  # 右侧

        # 获取状态栏字体配置
        font_config = config_manager.get_font_config("status_bar")
        font = (
            font_config.get("font", "Microsoft YaHei UI"),
            font_config.get("font_size", 12),
            "bold" if font_config.get("font_bold", False) else "normal",
        )

        # 创建左侧标签（显示行号、列号和临时通知信息）
        self.left_label = ctk.CTkLabel(
            self, text="就绪 | 第1行 | 第1列", anchor="w", font=font
        )
        self.left_label.grid(row=0, column=0, padx=10, pady=2, sticky="w")

        # 创建中间标签（显示自动保存状态信息）
        # 获取自动保存间隔，如果APP实例不可用则使用默认值
        auto_save_interval = (
            self.app.auto_save_interval
            if self.app
            else config_manager.get("saving.auto_save_interval", 30)
        )
        self.center_label = ctk.CTkLabel(
            self,
            text=f"自动保存: 从未(间隔{auto_save_interval}秒)",
            anchor="center",
            font=font,
        )
        self.center_label.grid(row=0, column=1, padx=10, pady=2, sticky="ew")

        # 创建右侧标签（显示文件名、编码和换行符类型）
        self.right_label = ctk.CTkLabel(
            self, text=f"{self.encoding} | {self.line_ending}", anchor="e", font=font
        )
        self.right_label.grid(row=0, column=2, padx=10, pady=2, sticky="e")

        # 绑定事件
        self.bind_events()

    def set_status_info(
        self,
        status="就绪",
        row=1,
        col=1,
        total_chars=None,
        selected_chars=None,
        selected_lines=None,
    ):
        """设置左侧状态信息（行号信息和文件编辑状态）"""
        if not config_manager.get("status_bar.show_line_info", True):
            self.left_label.configure(text="")
            return

        if total_chars is None and selected_chars is None and selected_lines is None:
            # 默认状态
            text = f"{status} | 第{row}行 | 第{col}列"
        elif selected_chars is None and selected_lines is None:
            # 有总字符数但无选中内容
            text = f"{status} | 第{row}行 | 第{col}列 | {total_chars}个字符"
        else:
            # 有选中内容
            selection_text = ""
            if selected_chars is not None:
                selection_text += f"已选中{selected_chars}个字符"
            if selected_lines is not None and selected_lines > 1:
                selection_text += f"({selected_lines}行)"
            text = f"{status} | 第{row}行 | 第{col}列 | {total_chars}个字符 | {selection_text}"

        self.left_label.configure(text=text)

    def set_auto_save_status(self):
        """
        设置自动保存状态信息（用于启用/禁用自动保存时显示）

        直接从应用程序获取当前的自动保存状态
        """
        # 获取应用程序中的自动保存状态
        auto_save_enabled = (
            self.app.auto_save_enabled
            if self.app
            else config_manager.get("saving.auto_save", False)
        )

        if auto_save_enabled:
            text = "自动保存: 已启用"
        else:
            text = "自动保存: 已禁用"

        self.center_label.configure(text=text)

        # 1.5秒后恢复显示正常信息
        if hasattr(self, "_auto_save_status_timer"):
            self.after_cancel(self._auto_save_status_timer)
        self._auto_save_status_timer = self.after(
            1500, self._show_auto_save_normal_status
        )

    def show_auto_save_status(self):
        """
        辅助方法：显示自动保存的日常状态

        根据自动保存启用状态和上次保存时间显示相应的信息
        格式为: "自动保存: 从未(间隔时间)" 或 "自动保存: 成功(间隔时间)"
        """
        if not config_manager.get("status_bar.show_auto_save_info", True):
            self.center_label.configure(text="")
            return

        # 获取自动保存设置
        auto_save_enabled = (
            self.app.auto_save_enabled
            if self.app
            else config_manager.get("saving.auto_save", False)
        )
        auto_save_interval = (
            self.app.auto_save_interval
            if self.app
            else config_manager.get("saving.auto_save_interval", 30)
        )

        if not auto_save_enabled:
            text = "自动保存: 已禁用"
        else:
            # 检查是否有上次自动保存时间
            if (
                hasattr(self.app, "last_auto_save_time")
                and self.app.last_auto_save_time > 0
            ):
                # 有上次保存时间，显示具体的保存时间
                import time

                save_time = time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(self.app.last_auto_save_time)
                )
                text = f"自动保存: 上次执行于{save_time}(间隔{auto_save_interval}秒)"
            else:
                # 没有上次保存时间，显示"从未"状态
                text = f"自动保存: 从未(间隔{auto_save_interval}秒)"

        self.center_label.configure(text=text)

    def set_file_info(self, filename=None, encoding=None, line_ending=None):
        """设置右侧文件信息（文件名、编码和换行符类型）"""
        if not config_manager.get("status_bar.show_file_info", True):
            self.right_label.configure(text="")
            return

        # 总是更新这些值，即使它们是None
        self.filename = filename
        if encoding is not None:
            self.encoding = encoding
        if line_ending is not None:
            self.line_ending = line_ending

        # 使用当前值构建显示文本
        current_encoding = encoding if encoding is not None else self.encoding
        current_line_ending = (
            line_ending if line_ending is not None else self.line_ending
        )

        if self.filename is None or self.filename == "":
            text = f"{current_encoding} | {current_line_ending}"
        else:
            text = f"{self.filename} | {current_encoding} | {current_line_ending}"

        self.right_label.configure(text=text)

    def show_notification(self, message, duration=2000):
        """
        在状态栏左侧标签显示临时通知信息

        Args:
            message (str): 要显示的通知消息
            duration (int): 显示持续时间，单位毫秒，默认为2000毫秒(2秒)
        """
        # 取消之前的定时器
        if self.notification_job:
            self.after_cancel(self.notification_job)
            self.notification_job = None

        # 保存当前状态栏左侧内容
        self.original_status_text = self.left_label.cget("text")

        # 设置通知活动标志
        self.notification_active = True

        # 显示通知消息
        self.left_label.configure(text=message)

        # 设置定时器，在指定时间后恢复原始内容
        self.notification_job = self.after(
            duration, self._restore_status_after_notification
        )

    def _restore_status_after_notification(self):
        """恢复状态栏左侧标签内容并重置通知状态"""
        self.notification_active = False
        self.notification_job = None

        # 恢复左侧标签的原始内容
        self.left_label.configure(text=self.original_status_text)

    def can_update_status(self):
        """
        检查是否可以更新状态栏信息

        Returns:
            bool: 如果当前没有通知活动，返回True；否则返回False
        """
        return not self.notification_active

    def bind_events(self):
        """绑定事件"""
        self.right_label.bind("<Button-3>", self._on_right_click)  # 右键点击事件

    def _on_right_click(self, event):
        """处理右键点击事件，根据点击位置判断是编码还是换行符"""
        try:
            # 获取标签的文本内容
            text = self.right_label.cget("text")

            # 获取点击位置相对于标签的x坐标
            x = event.x

            # 获取标签的字体信息
            font = self.right_label.cget("font")

            # 如果没有文本，直接返回
            if not text:
                return

            # 解析状态栏文本，判断格式
            # 格式可能是: "文件名 | 编码 | 换行符" 或 "编码 | 换行符"
            parts = [part.strip() for part in text.split("|")]

            if len(parts) == 3:
                # 有文件名的情况: "文件名 | 编码 | 换行符"
                filename_part = parts[0]
                encoding_part = parts[1]
                line_ending_part = parts[2]

                # 使用更精确的方法计算各部分的宽度
                # 获取标签的实际宽度
                label_width = self.right_label.winfo_width()

                # 计算各部分文本的相对宽度比例
                total_text_length = (
                    len(filename_part) + len(encoding_part) + len(line_ending_part) + 6
                )  # 6是两个" | "分隔符的总长度

                # 计算各部分的相对位置（基于字符长度的比例）
                filename_ratio = len(filename_part) / total_text_length
                encoding_ratio = len(encoding_part) / total_text_length
                separator_ratio = 3 / total_text_length  # " | "的长度为3

                # 计算各部分的x坐标范围
                filename_end = label_width * filename_ratio
                encoding_start = filename_end + label_width * separator_ratio
                encoding_end = encoding_start + label_width * encoding_ratio
                line_ending_start = encoding_end + label_width * separator_ratio

                # 添加一些容错范围
                tolerance = 10  # 10像素的容错范围

                # 判断点击位置
                if encoding_start - tolerance <= x <= encoding_end + tolerance:
                    # 点击了编码部分
                    self._show_encoding_menu(event)
                elif x >= line_ending_start - tolerance:
                    # 点击了换行符部分
                    self._show_line_ending_menu(event)

            elif len(parts) == 2:
                # 没有文件名的情况: "编码 | 换行符"
                encoding_part = parts[0]
                line_ending_part = parts[1]

                # 使用更精确的方法计算各部分的宽度
                # 获取标签的实际宽度
                label_width = self.right_label.winfo_width()

                # 计算各部分文本的相对宽度比例
                total_text_length = (
                    len(encoding_part) + len(line_ending_part) + 3
                )  # 3是" | "分隔符的长度

                # 计算各部分的相对位置（基于字符长度的比例）
                encoding_ratio = len(encoding_part) / total_text_length
                separator_ratio = 3 / total_text_length  # " | "的长度为3

                # 计算各部分的x坐标范围
                encoding_end = label_width * encoding_ratio
                line_ending_start = encoding_end + label_width * separator_ratio

                # 添加一些容错范围
                tolerance = 10  # 10像素的容错范围

                # 判断点击位置
                if x <= encoding_end + tolerance:
                    # 点击了编码部分
                    self._show_encoding_menu(event)
                else:
                    # 点击了换行符部分
                    self._show_line_ending_menu(event)

        except Exception as e:
            print(f"处理右键点击事件时出错: {e}")

    def _get_text_width(self, text, font):
        """获取文本在指定字体下的显示宽度"""
        try:
            # 创建一个临时的标签来测量文本宽度
            import tkinter as tk

            temp_label = tk.Label(self.right_label.master, text=text, font=font)
            width = temp_label.winfo_reqwidth()
            # 如果宽度为0（例如因为标签还没有被渲染），则使用估算值
            if width <= 0:
                # 估算每个字符的平均宽度（这个值可能需要根据实际字体调整）
                avg_char_width = 8
                width = len(text) * avg_char_width
            return width
        except Exception:
            # 如果获取宽度宽度失败，则使用估算值
            avg_char_width = 8
            return len(text) * avg_char_width

    def _show_encoding_menu(self, event):
        """显示编码选择菜单，复用文件菜单中的编码菜单逻辑"""
        try:
            # 导入必要的模块
            import sys
            import os
            import tkinter as tk

            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

            from ui.menu import create_encoding_submenu, set_file_encoding
            from config.config_manager import config_manager

            # 创建弹出菜单
            popup_menu = tk.Menu(self.right_label, tearoff=0)

            # 获取菜单字体配置
            menu_font_config = config_manager.get_font_config("menu_bar")
            menu_font_tuple = (
                menu_font_config.get("font", "Microsoft YaHei UI"),
                menu_font_config.get("font_size", 12),
                "bold" if menu_font_config.get("font_bold", False) else "normal",
            )

            # 设置菜单字体
            popup_menu.configure(font=menu_font_tuple)

            # 获取应用实例
            app_instance = self.master

            # 直接创建编码子菜单，使用与文件菜单相同的逻辑
            create_encoding_submenu(
                popup_menu,
                app_instance,
                show_common_only=True,
                font_tuple=menu_font_tuple,
            )

            # 在鼠标位置显示菜单
            try:
                popup_menu.tk_popup(event.x_root, event.y_root)
            finally:
                # 确保菜单能够被正确释放
                popup_menu.grab_release()

        except Exception as e:
            print(f"显示编码菜单时出错: {e}")

    def _show_line_ending_menu(self, event):
        """显示换行符选择菜单，复用文件菜单中的换行符菜单逻辑"""
        try:
            # 导入必要的模块
            import sys
            import os
            import tkinter as tk

            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

            from ui.menu import set_file_line_ending
            from config.config_manager import config_manager

            # 创建弹出菜单
            popup_menu = tk.Menu(self.right_label, tearoff=0)

            # 获取菜单字体配置
            menu_font_config = config_manager.get_font_config("menu_bar")
            menu_font_tuple = (
                menu_font_config.get("font", "Microsoft YaHei UI"),
                menu_font_config.get("font_size", 12),
                "bold" if menu_font_config.get("font_bold", False) else "normal",
            )

            # 设置菜单字体
            popup_menu.configure(font=menu_font_tuple)

            # 获取应用实例
            app_instance = self.master

            # 换行符选项，与文件菜单中的选项保持一致
            newline_options = [
                ("Windows (CRLF)", "CRLF"),
                ("Linux/Unix (LF)", "LF"),
                ("Mac (CR)", "CR"),
            ]

            # 添加换行符选项，使用与文件菜单相同的处理函数
            for label, value in newline_options:
                popup_menu.add_command(
                    label=label,
                    command=lambda nl=value: set_file_line_ending(nl, app_instance),
                    font=menu_font_tuple,
                )

            # 在鼠标位置显示菜单
            try:
                popup_menu.tk_popup(event.x_root, event.y_root)
            finally:
                # 确保菜单能够被正确释放
                popup_menu.grab_release()

        except Exception as e:
            print(f"显示换行符菜单时出错: {e}")
