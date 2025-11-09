"""
文件操作相关的业务逻辑处理
"""

import codecs
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from customtkinter import CTk
from config.config_manager import config_manager
from .file_operation_core import FileOperationCore


class FileOperations:
    """处理文件操作相关的业务逻辑"""

    def __init__(self, root):
        """
        初始化文件操作处理器

        Args:
            root: app实例
        """
        self.root = root
        self.config_manager = config_manager
        self.file_core = FileOperationCore()  # 初始化文件操作核心

    def open_file(self):
        """打开文件并加载到编辑器"""
        # 检查是否需要保存当前文件
        if not self.check_save_before_close():
            return  # 用户取消了操作

        try:
            # 打开文件选择对话框
            file_path = filedialog.askopenfilename(
                title="选择文件",
                filetypes=[
                    ("所有文件", "*.*"),
                    ("文本文件", "*.txt"),
                    ("Python文件", "*.py"),
                    ("Markdown文件", "*.md"),
                    ("JSON文件", "*.json"),
                    ("YAML文件", "*.yaml"),
                    ("INI文件", "*.ini"),
                    ("XML文件", "*.xml"),
                    ("HTML文件", "*.html"),
                    ("CSS文件", "*.css"),
                    ("JavaScript文件", "*.js"),
                    ("TypeScript文件", "*.ts"),
                    ("C文件", "*.c"),
                    ("Go文件", "*.go"),
                ],
            )

            if not file_path:
                return  # 用户取消了选择

            # 获取配置的最大文件大小
            max_file_size = self.config_manager.get(
                "app.max_file_size", 10 * 1024 * 1024
            )  # 转换为字节

            # 使用核心类异步读取文件
            self.file_core.async_read_file(
                file_path=file_path,
                callback=self._on_file_read_complete,
                error_callback=self._on_file_read_error,
                max_file_size=max_file_size,
            )

        except Exception as e:
            messagebox.showerror("错误", f"打开文件时出错: {str(e)}")

    def _on_file_read_complete(self, file_path, content, encoding, line_ending):
        """
        文件读取完成回调

        Args:
            file_path: 文件路径
            content: 文件内容
            encoding: 文件编码
            line_ending: 文件换行符类型
        """
        try:
            # 更新编辑器内容
            self.root.text_area.delete("1.0", tk.END)
            self.root.text_area.insert("1.0", content)

            # 保存当前文件路径到编辑器实例
            self.root.current_file_path = file_path
            self.root.current_encoding = encoding
            self.root.current_line_ending = line_ending

            # 重置修改状态
            self.root.set_modified(False)  # 清除修改状态标志
            self.root.is_new_file = False  # 清除新文件状态标志

            # 更新缓存的字符数
            self.root.update_char_count()

            # 更新状态栏文件信息
            self.root.status_bar.update_file_info()

            # 更新状态栏
            self.root.status_bar.set_status_info(
                f"已打开: {os.path.basename(file_path)}"
            )

            # 更新窗口标题
            self.root._update_window_title()

        except Exception as e:
            messagebox.showerror("错误", f"处理文件内容时出错: {str(e)}")

    def _on_file_read_error(self, title_or_message, message=None):
        """
        文件读取错误回调

        Args:
            title_or_message: 错误标题，或者如果message为None，则作为完整的错误消息（兼容旧版本）
            message: 错误详细信息，可选
        """
        # 兼容旧版本的单参数调用方式
        if message is None:
            # 如果只有一个参数，则使用默认标题"错误"
            messagebox.showerror("错误", title_or_message)
        else:
            # 如果有两个参数，则分别作为标题和内容
            messagebox.showerror(title_or_message, message)

    def open_config_file(self):
        """打开配置文件并加载到编辑器"""
        # 检查是否需要保存当前文件
        if not self.check_save_before_close():
            return  # 用户取消了操作

        try:
            # 获取配置文件路径
            from config.config_manager import CONFIG_PATH

            # 检查配置文件是否存在
            if not os.path.exists(CONFIG_PATH):
                from tkinter import messagebox

                messagebox.showinfo(
                    "提示", "配置文件不存在，将在首次修改设置时自动创建"
                )
                return

            # 获取配置的最大文件大小
            max_file_size = self.config_manager.get(
                "app.max_file_size", 10 * 1024 * 1024
            )  # 转换为字节

            # 直接使用配置文件路径，不显示文件选择对话框
            file_path = CONFIG_PATH

            # 使用核心类异步读取文件
            self.file_core.async_read_file(
                file_path=file_path,
                callback=self._on_file_read_complete,
                error_callback=self._on_file_read_error,
                max_file_size=max_file_size,
            )

        except Exception as e:
            messagebox.showerror("错误", f"打开配置文件时出错: {str(e)}")

    def _save_file_content(self, file_path, update_current_file_info=True):
        """
        保存文件内容的通用方法

        Args:
            file_path: 要保存的文件路径
            update_current_file_info: 是否更新当前文件信息（路径、编码等）

        Returns:
            bool: 保存是否成功
        """
        try:
            # 获取编辑器内容
            content = self.root.text_area.get("1.0", tk.END).rstrip("\n")

            # 获取当前编码和换行符设置
            encoding = self.root.current_encoding
            # 优先使用编辑器的当前换行符设置，如果没有则使用配置中的默认换行符
            line_ending = self.root.current_line_ending

            # 使用核心类转换换行符格式
            content = self.file_core.convert_line_endings(content, line_ending)

            # 写入文件
            with codecs.open(file_path, "w", encoding=encoding) as f:
                f.write(content)

            # 如果需要，更新当前文件信息
            if update_current_file_info:
                self.root.current_file_path = file_path
                self.root.current_encoding = encoding
                self.root.current_line_ending = line_ending

            # 重置修改状态
            self.root.set_modified(False)  # 清除修改状态标志
            self.root.is_new_file = False  # 清除新文件状态标志

            # 更新状态栏文件信息
            self.root.status_bar.update_file_info()

            # 获取当前光标位置
            try:
                cursor_pos = self.root.text_area.index("insert")
                row, col = cursor_pos.split(".")
                row = int(row)
                col = int(col) + 1  # 转换为1基索引

                # 更新状态栏状态信息（从"已修改"改为"就绪"）
                self.root.status_bar.set_status_info(status="就绪", row=row, col=col)
            except Exception:
                # 如果获取位置失败，使用默认值
                self.root.status_bar.set_status_info(status="就绪")

            # 显示保存通知
            self.root.status_bar.show_notification(f"文件已保存")

            # 更新窗口标题
            self.root._update_window_title()

            return True

        except Exception as e:
            messagebox.showerror("错误", f"保存文件时出错: {str(e)}")
            return False

    def save_file(self):
        """保存当前文件"""
        # 获取文本框内容
        content = self.root.text_area.get("1.0", tk.END).strip()

        # 检查是否有文件路径
        has_file_path = (
            hasattr(self.root, "current_file_path") and self.root.current_file_path
        )

        # 情况1：没有打开文件且文本框没有内容
        if not has_file_path and not content:
            messagebox.showinfo("提示", "没有内容可保存")
            return False

        # 情况2：已经打开文件，检查是否修改
        if has_file_path and not self.root.is_modified():
            messagebox.showinfo("提示", "文件未修改，无需保存")
            return True

        if not self.root.current_file_path:
            # 如果没有当前文件路径，则执行另存为
            return self.save_file_as()

        # 使用通用保存方法，不更新当前文件信息（因为已经是当前文件）
        return self._save_file_content(
            self.root.current_file_path, update_current_file_info=False
        )

    def save_file_as(self):
        """另存为文件"""
        # 获取文本框内容
        content = self.root.text_area.get("1.0", tk.END).strip()

        # 检查是否有文件路径
        has_file_path = (
            hasattr(self.root, "current_file_path") and self.root.current_file_path
        )

        # 情况1：没有打开文件且文本框没有内容
        if not has_file_path and not content:
            messagebox.showinfo("提示", "没有内容可保存")
            return False

        # 情况2：已经打开文件，检查是否修改
        if has_file_path and not self.root.is_modified():
            messagebox.showinfo("提示", "文件未修改，无需保存")
            return True

        try:
            # 打开另存为对话框
            file_path = filedialog.asksaveasfilename(
                title="另存为",
                defaultextension=".txt",
                filetypes=[
                    ("所有文件", "*.*"),
                    ("文本文件", "*.txt"),
                    ("Python文件", "*.py"),
                    ("Markdown文件", "*.md"),
                    ("JSON文件", "*.json"),
                    ("YAML文件", "*.yaml"),
                    ("INI文件", "*.ini"),
                    ("XML文件", "*.xml"),
                    ("HTML文件", "*.html"),
                    ("CSS文件", "*.css"),
                    ("JavaScript文件", "*.js"),
                    ("TypeScript文件", "*.ts"),
                    ("C文件", "*.c"),
                    ("Go文件", "*.go"),
                ],
            )

            if not file_path:
                return False  # 用户取消了选择

            # 使用通用保存方法，更新当前文件信息（因为是另存为）
            return self._save_file_content(file_path, update_current_file_info=True)

        except Exception as e:
            messagebox.showerror("错误", f"另存为文件时出错: {str(e)}")
            return False

    def _new_file_helper(self, filename="新文件"):
        """新建文件的辅助方法

        Args:
            filename: 文件名，默认为"新文件"
        """
        # 设置新文件状态标志
        self.root.is_new_file = True

        # 获取配置中的默认换行符和编码
        default_line_ending = self.config_manager.get("app.default_line_ending", "LF")
        default_encoding = self.config_manager.get("app.default_encoding", "UTF-8")

        # 更新编辑器的当前换行符和编码
        self.root.current_line_ending = default_line_ending
        self.root.current_encoding = default_encoding

        # 更新状态栏为新文件状态
        self.root.status_bar.update_file_info()

        # 更新窗口标题为新文件
        self.root.title(f"{filename} - QuickEdit++")

    def new_file(self):
        """创建新文件"""
        self.close_file()

        # 使用辅助方法创建新文件
        self._new_file_helper()

    def _open_file_with_path_helper(self, file_path):
        """通过指定路径打开文件的辅助方法"""
        try:
            # 获取配置的最大文件大小
            max_file_size = self.config_manager.get(
                "app.max_file_size", 10 * 1024 * 1024
            )  # 转换为字节

            # 异步读取文件
            self.file_core.async_read_file(
                file_path=file_path,
                callback=self._on_file_read_complete,
                error_callback=self._on_file_read_error,
                max_file_size=max_file_size,
            )

        except Exception as e:
            messagebox.showerror("错误", f"打开文件时出错: {str(e)}")

    def handle_dropped_files(self, files):
        """
        处理拖拽文件事件

        Args:
            files: 拖拽的文件列表，可能是字节串或字符串
        """
        if not files:
            return

        # 如果拖拽了多个文件，直接提示并返回
        if len(files) > 1:
            messagebox.showinfo("提示", "只支持打开单个文件，请一次只拖拽一个文件")
            return

        # 解码文件路径
        file_path = files[0]
        if isinstance(file_path, bytes):
            file_path = file_path.decode("gbk")

        # 检查路径是否存在
        if os.path.exists(file_path):
            # 检查是否是目录
            if os.path.isdir(file_path):
                messagebox.showwarning(
                    "不支持的操作", f"无法打开目录: {os.path.basename(file_path)}"
                )
                return

            # 检查是否需要保存当前文件
            if not self.check_save_before_close():
                return  # 用户取消了操作

            # 文件存在，直接打开
            self._open_file_with_path_helper(file_path)
        else:
            # 文件不存在，检查上级目录是否存在
            dir_path = os.path.dirname(file_path)
            if dir_path and not os.path.exists(dir_path):
                messagebox.showerror("错误", f"该文件的上级目录不存在: {dir_path}")
                return

            # 检查是否需要保存当前文件
            if not self.check_save_before_close():
                return  # 用户取消了操作

            # 作为新文件创建
            self.new_file_with_path(file_path)

    def new_file_with_path(self, file_path):
        """通过指定路径创建新文件"""
        # 设置当前文件路径
        self.root.current_file_path = file_path

        # 使用辅助方法创建新文件，传入文件名
        filename = os.path.basename(file_path)
        self._new_file_helper(filename)

    def _reset_editor_state(self):
        """重置编辑器状态，包括清空内容、重置文件属性和更新状态栏"""
        # 清空编辑器内容
        self.root.text_area.delete("1.0", tk.END)

        # 更新字符数缓存，确保_total_chars为0
        self.root.update_char_count()

        # 获取配置中的默认换行符和编码
        default_line_ending = self.config_manager.get("app.default_line_ending", "LF")
        default_encoding = self.config_manager.get("app.default_encoding", "UTF-8")

        # 重置文件相关属性
        self.root.current_file_path = None
        self.root.current_encoding = default_encoding  # 重置为配置中的默认编码
        self.root.current_line_ending = default_line_ending  # 重置为配置中的默认换行符
        self.root.set_modified(False)  # 重置文件修改状态
        self.root.is_new_file = False  # 清除新文件状态标志

        # 更新状态栏
        self.root.status_bar.set_status_info("就绪")
        # 重置状态栏右侧文件信息
        self.root.status_bar.update_file_info()

        # 更新窗口标题
        self.root._update_window_title()

    def close_file(self):
        """关闭当前文件，重置窗口和状态栏状态"""
        # 检查是否需要保存当前文件
        if not self.check_save_before_close():
            return  # 用户取消了操作

        # 重置编辑器状态
        self._reset_editor_state()

    def check_save_before_close(self):
        """在关闭文件前检查是否需要保存

        Returns:
            bool: 如果可以继续关闭操作返回True，如果用户取消则返回False
        """
        # 如果文件未修改，直接返回True
        if not self.root.is_modified():
            return True

        # 如果文件已修改，提示用户
        result = messagebox.askyesnocancel(
            "未保存的更改", "当前文件有未保存的更改，是否保存？"
        )

        if result is True:  # 用户选择保存
            return self.save_file()

        elif result is False:  # 用户选择不保存
            return True

        else:  # 用户选择取消
            return False
