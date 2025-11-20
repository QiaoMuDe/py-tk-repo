#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
状态栏界面模块
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from config.config_manager import config_manager
import time
import datetime
import sys
import os
from ui.menu import create_encoding_submenu, set_file_encoding
from config.config_manager import config_manager
from ui.menu import set_file_line_ending
from ui.document_stats_dialog import show_document_stats_dialog


class StatusBar(ctk.CTkFrame):
    """状态栏类"""

    def __init__(self, parent):
        """
        初始化状态栏
        :param parent: 父容器，通常是主窗口
        """
        super().__init__(parent)

        # 设置状态栏高度
        self.configure(height=25)

        # 初始化文件信息
        self.filename = None

        # app 实例引用
        self.app = parent

        # 通知相关属性
        self.notification_active = False
        self.notification_job = None
        self.original_status_text = ""

        # 配置网格布局权重 - 调整为4个标签的布局
        self.grid_columnconfigure(0, weight=1)  # 左侧（状态信息）
        self.grid_columnconfigure(1, weight=1)  # 中间（自动保存）
        self.grid_columnconfigure(2, weight=1)  # 右侧（编码和换行符）

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

        # 设置鼠标悬停时的光标样式为手型，提示可点击
        self.left_label.configure(cursor="hand2")

        # 创建中间标签（显示自动保存状态信息）
        # 获取自动保存间隔
        auto_save_interval = self.app.auto_save_manager.auto_save_interval

        # 根据自动保存状态设置初始显示文本
        auto_save_enabled = self.app.auto_save_manager.auto_save_enabled
        if auto_save_enabled:
            initial_text = f"自动保存: 从未执行 (间隔{auto_save_interval}秒)"
        else:
            initial_text = "自动保存: 已禁用"

        # 创建标签并设置初始文本
        self.center_label = ctk.CTkLabel(
            self,
            text=initial_text,
            anchor="center",
            font=font,
        )
        self.center_label.grid(row=0, column=1, padx=10, pady=2, sticky="ew")

        # 创建右侧标签（显示文件名、编码和换行符类型）
        self.right_label = ctk.CTkLabel(
            self,
            text=f"{self.app.current_encoding} | {self.app.current_line_ending}",
            anchor="e",
            font=font,
        )
        self.right_label.grid(row=0, column=2, padx=10, pady=2, sticky="e")

        # 设置鼠标悬停时的光标样式为手型，提示可点击
        self.right_label.configure(cursor="hand2")

        # 绑定事件
        self.bind_events()

    def set_status_info(
        self,
        status="就绪",
        row=1,
        col=1,
        selected_chars=None,
        selected_lines=None,
    ):
        """
        设置左侧状态信息（行号信息和文件编辑状态）
        :param status: 状态信息，默认为"就绪"
        :param row: 当前行号，默认为1
        :param col: 当前列号，默认为1
        :param selected_chars: 选中文本的字符数，默认为None
        :param selected_lines: 选中文本的行数，默认为None
        """
        # 根据参数生成状态栏文本
        if selected_chars is None and selected_lines is None:
            # 根据是否有总字符数判断是否显示字符数
            if self.app.get_char_count() == 0:
                # 默认状态
                text = f"{status} | 第{row}行 | 第{col}列"
            else:
                # 有总字符数但无选中内容
                text = f"{status} | 第{row}行 | 第{col}列 | {self.app.get_char_count()}个字符"
        else:
            # 有选中内容
            selection_text = ""
            if selected_chars is not None:
                selection_text += f"已选中{selected_chars}个字符"
            if selected_lines is not None and selected_lines > 1:
                selection_text += f"({selected_lines}行)"
            text = f"{status} | 第{row}行 | 第{col}列 | {self.app.get_char_count()}个字符 | {selection_text}"

        self.left_label.configure(text=text)

    def set_auto_save_status(self):
        """
        设置自动保存状态信息（用于启用/禁用自动保存时显示）

        直接从应用程序获取当前的自动保存状态
        """
        # 获取应用程序中的自动保存状态
        auto_save_enabled = self.app.auto_save_manager.auto_save_enabled

        if auto_save_enabled:
            text = "自动保存: 已启用"
        else:
            text = "自动保存: 已禁用"

        self.center_label.configure(text=text)

        # 1.5秒后恢复显示正常信息
        if hasattr(self, "_auto_save_status_timer"):
            self.after_cancel(self._auto_save_status_timer)
        self._auto_save_status_timer = self.after(800, self.show_auto_save_status)

    def _format_auto_save_time(self, save_time):
        """
        格式化自动保存时间的显示格式

        根据时间差选择合适的显示格式：
        - 1分钟内：显示"X秒前"
        - 1小时内：显示"X分钟前"
        - 1天内：显示"X小时前"
        - 超过1天：显示"MM-DD HH:MM"

        Args:
            save_time (float): 上次自动保存的时间戳

        Returns:
            str: 格式化后的时间字符串
        """
        # 获取当前时间
        current_time = time.time()

        # 计算时间差
        time_diff = current_time - save_time

        # 格式化保存时间
        save_datetime = datetime.datetime.fromtimestamp(save_time)

        # 根据时间差选择合适的显示格式
        if time_diff < 60:  # 1分钟内
            return f"{int(time_diff)}秒前"
        elif time_diff < 3600:  # 1小时内
            return f"{int(time_diff // 60)}分钟前"
        elif time_diff < 86400:  # 1天内
            return f"{int(time_diff // 3600)}小时前"
        else:  # 超过1天
            return save_datetime.strftime("%m-%d %H:%M")

    def show_auto_save_countdown(self, remaining_time):
        """
        显示自动保存倒计时状态

        Args:
            remaining_time (float): 距离下次自动保存的剩余时间（秒）
        """
        # 获取自动保存间隔
        auto_save_interval = self.app.auto_save_manager.auto_save_interval

        # 显示倒计时信息，保留一位小数
        text = f"自动保存: {remaining_time:.1f}秒后保存 (间隔{auto_save_interval}秒)"
        # 设置为蓝色字体表示倒计时
        self.center_label.configure(text=text, text_color="#0066CC")

    def show_auto_save_status(self, saved=False):
        """
        显示自动保存的日常状态或保存成功状态

        Args:
            saved (bool): 是否刚刚执行了保存操作，默认为False
                           - True: 显示自动保存成功信息
                           - False: 显示日常状态信息
        """
        # 获取自动保存设置
        auto_save_enabled = self.app.auto_save_manager.auto_save_enabled
        auto_save_interval = self.app.auto_save_manager.auto_save_interval

        if not auto_save_enabled:
            text = f"自动保存: 已禁用"
            # 设置为黑色字体
            self.center_label.configure(text=text, text_color="#000000")

        elif saved:
            # 刚刚执行了保存操作，显示保存成功信息
            text = f"自动保存: 保存成功 (间隔{auto_save_interval}秒)"
            # 设置绿色文本表示成功保存
            self.center_label.configure(text=text, text_color="#00AA00")

        else:
            # 显示日常状态信息
            # 检查是否有上次自动保存时间
            if self.app.auto_save_manager.last_auto_save_time > 0:
                # 使用辅助函数格式化时间
                time_str = self._format_auto_save_time(
                    self.app.auto_save_manager.last_auto_save_time
                )
                # 构建美观的显示文本
                text = f"自动保存: {time_str} (间隔{auto_save_interval}秒)"
            else:
                # 没有上次保存时间，显示"从未"状态
                text = f"自动保存: 从未执行 (间隔{auto_save_interval}秒)"

            # 设置为黑色字体
            self.center_label.configure(text=text, text_color="#000000")

    def update_file_info(self):
        """更新右侧文件信息（编码和换行符类型）"""
        current_encoding = self.app.current_encoding.upper()  # 编码转换为大写
        current_line_ending = self.app.current_line_ending  # 换行符类型
        language_name = None  # 语言名称

        # 检查应用程序是否有语法高亮器并且打开文件
        if (
            self.app.syntax_highlighter
            and self.app.current_file_path
            and self.app.syntax_highlighter.highlight_enabled
        ):
            # 获取语言名称
            language_name = self.app.syntax_highlighter.get_language_name()

        # 根据语言名称构建显示文本
        if language_name is None:
            self.right_label.configure(
                text=f"{current_encoding} | {current_line_ending}"
            )
        else:
            # 将语言名称首字母大写
            display_language_name = (
                language_name.capitalize() if language_name else language_name
            )
            self.right_label.configure(
                text=f"{display_language_name} | {current_encoding} | {current_line_ending}"
            )

    def show_notification(self, message, duration=1000):
        """
        在状态栏左侧标签显示临时通知信息

        Args:
            message (str): 要显示的通知消息
            duration (int): 显示持续时间，单位毫秒，默认为1000毫秒(1秒)
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

        # 尝试获取当前的光标位置和字符数，而不是恢复之前保存的文本
        try:
            # 检查是否有应用程序实例和文本区域
            if self.app and hasattr(self.app, "text_area"):
                # 获取当前光标位置
                cursor_pos = self.app.text_area.index("insert")
                row, col = cursor_pos.split(".")
                row = int(row)
                col = int(col) + 1  # 转换为1基索引

                # 获取当前状态，使用app实例的is_modified属性
                status = "就绪"
                if self.app.is_modified():
                    status = "已修改"

                # 更新状态栏信息
                self.set_status_info(status=status, row=row, col=col)
            else:
                # 如果没有应用程序实例，则恢复原始文本
                self.left_label.configure(text=self.original_status_text)
        except Exception:
            # 如果获取位置失败，则恢复原始文本
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
        self.right_label.bind(
            "<Button-1>", self._on_right_click
        )  # 左键点击事件，与右键功能相同
        self.left_label.bind("<Button-1>", self._on_left_click)  # 左键点击事件
        self.left_label.bind("<Button-3>", self._on_left_click)  # 右键点击事件

    def _on_right_click(self, event):
        """处理右键点击事件，根据点击位置判断是编码还是换行符"""
        try:
            # 获取标签的文本内容
            text = self.right_label.cget("text")

            # 获取点击位置相对于标签的x坐标
            x = event.x

            # 如果没有文本，直接返回
            if not text:
                return

            # 解析状态栏文本，格式可能为: "语言名称 | 编码 | 换行符" 或 "编码 | 换行符"
            parts = [part.strip() for part in text.split("|")]

            # 获取标签的实际宽度
            label_width = self.right_label.winfo_width()

            # 添加容错范围
            tolerance = 10  # 10像素的容错范围

            if len(parts) == 3:
                # 格式为: "语言名称 | 编码 | 换行符"
                language_part = parts[0]
                encoding_part = parts[1]
                line_ending_part = parts[2]

                # 计算各部分的文本长度
                language_length = len(language_part)
                encoding_length = len(encoding_part)
                line_ending_length = len(line_ending_part)

                # 计算总文本长度（包括分隔符）
                total_text_length = (
                    language_length + encoding_length + line_ending_length + 6
                )  # 6是两个" | "分隔符的总长度

                # 计算各部分的相对位置（基于字符长度的比例）
                language_ratio = language_length / total_text_length
                encoding_ratio = encoding_length / total_text_length
                separator_ratio = 3 / total_text_length  # " | "的长度为3

                # 计算各部分的x坐标范围
                language_end = label_width * language_ratio
                encoding_start = language_end + label_width * separator_ratio
                encoding_end = encoding_start + label_width * encoding_ratio
                line_ending_start = encoding_end + label_width * separator_ratio

                # 判断点击位置
                if x >= encoding_start - tolerance and x <= encoding_end + tolerance:
                    # 点击了编码部分
                    self._show_encoding_menu(event)
                elif x >= line_ending_start - tolerance:
                    # 点击了换行符部分
                    self._show_line_ending_menu(event)

            elif len(parts) == 2:
                # 格式为: "编码 | 换行符"
                encoding_part = parts[0]
                line_ending_part = parts[1]

                # 计算各部分的文本长度
                encoding_length = len(encoding_part)
                line_ending_length = len(line_ending_part)

                # 计算总文本长度（包括分隔符）
                total_text_length = (
                    encoding_length + line_ending_length + 3
                )  # 3是" | "分隔符的长度

                # 计算各部分的相对位置（基于字符长度的比例）
                encoding_ratio = encoding_length / total_text_length
                separator_ratio = 3 / total_text_length  # " | "的长度为3

                # 计算各部分的x坐标范围
                encoding_end = label_width * encoding_ratio
                line_ending_start = encoding_end + label_width * separator_ratio

                # 判断点击位置
                if x <= encoding_end + tolerance:
                    # 点击了编码部分
                    self._show_encoding_menu(event)
                else:
                    # 点击了换行符部分
                    self._show_line_ending_menu(event)

        except Exception as e:
            messagebox.showerror("错误", f"处理右键点击事件时出错: {e}")

    def _get_text_width(self, text, font):
        """获取文本在指定字体下的显示宽度"""
        try:
            # 创建一个临时的标签来测量文本宽度
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

    def _on_left_click(self, event):
        """处理左侧标签点击事件，打开文档统计对话框"""
        try:
            # 打开文档统计对话框
            show_document_stats_dialog(self.app)
        except Exception as e:
            messagebox.showerror("错误", f"打开文档统计对话框时出错: {e}")
