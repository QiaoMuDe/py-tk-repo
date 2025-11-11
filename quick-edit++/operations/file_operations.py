"""
文件操作相关的业务逻辑处理
"""

import codecs
import os
import sys
import time
import tkinter as tk
import locale
from tkinter import filedialog, messagebox
from config.config_manager import config_manager
from .file_operation_core import FileOperationCore
from ui.simple_backup_dialog import SimpleBackupDialog, BackupActions
import shutil


class FileOperations:
    """处理文件操作相关的业务逻辑"""

    # 通用文件类型列表，避免在多个方法中重复定义
    FILE_TYPES = [
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
    ]

    def __init__(self, root):
        """
        初始化文件操作处理器

        Args:
            root: app实例
        """
        self.root = root  # 保存app实例引用
        self.config_manager = config_manager  # 保存配置管理器引用
        self.file_core = FileOperationCore()  # 初始化文件操作核心

    def _create_backup_copy(self, file_path):
        """
        创建文件的副本备份

        Args:
            file_path: 原文件路径
        """
        try:
            # 构建备份文件路径（在原文件名后添加.bak扩展名）
            backup_path = f"{file_path}.bak"

            # 如果备份文件已存在，先删除
            if os.path.exists(backup_path):
                os.remove(backup_path)

            # 使用copy2保留元数据
            try:
                shutil.copy2(file_path, backup_path)
                self.root.status_bar.show_notification("已创建副本备份")
            except (IOError, OSError, PermissionError) as e:
                messagebox.showerror("备份错误", f"创建副本备份失败: {str(e)}")
            except Exception as e:
                messagebox.showerror("备份错误", f"创建备份时发生未知错误: {str(e)}")

        except Exception as e:
            messagebox.showerror("备份错误", f"备份处理失败: {str(e)}")

    def _save_file(self, file_path=None, force_save_as=False):
        """
        统一的文件保存方法，整合保存和另存为功能

        此方法执行以下操作：
        1. 检查文件内容和状态
        2. 根据需要显示文件选择对话框
        3. 调用核心保存方法写入文件
        4. 更新编辑器状态和界面

        Args:
            file_path (str, optional): 要保存的文件路径。如果为None且当前有文件路径，则使用当前路径
            force_save_as (bool): 是否强制执行另存为操作，即使已有文件路径

        Returns:
            bool: 保存是否成功

        Note:
            - 当file_path为None且当前没有文件路径时，会显示另存为对话框
            - 当force_save_as为True时，即使有当前文件路径也会显示另存为对话框
            - 如果文件内容为空且没有文件路径，会提示"没有内容可保存"
            - 如果文件未修改且不是强制另存为，会提示"文件未修改，无需保存"
        """
        # 获取文本框内容（只获取一次）
        # 使用rstrip("\n")而不是strip()，因为我们需要保留文件开头的空格和制表符
        content = self.root.text_area.get("1.0", tk.END).rstrip("\n")

        # 检查是否有文件路径
        has_current_path = self.root.current_file_path is not None

        # 情况1：没有打开文件且文本框没有内容
        if not has_current_path and not content:
            messagebox.showinfo("提示", "没有内容可保存")
            return False

        # 情况2：已经打开文件，检查是否修改（除非是强制另存为）
        if has_current_path and not self.root.is_modified() and not force_save_as:
            messagebox.showinfo("提示", "文件未修改，无需保存")
            return True

        # 确定最终保存路径
        final_path = file_path
        need_to_update_current_info = True  # 是否需要更新当前文件信息

        if final_path is None:
            # 没有指定路径，使用当前路径或显示另存为对话框
            if has_current_path and not force_save_as:
                # 使用当前文件路径，不更新文件信息
                final_path = self.root.current_file_path
                need_to_update_current_info = False
            else:
                # 没有当前路径或强制另存为，显示另存为对话框

                # 显示另存为对话框
                final_path = filedialog.asksaveasfilename(
                    title="另存为",
                    defaultextension=".txt",
                    filetypes=self.FILE_TYPES,
                    initialfile="新文件.txt",
                )

                # 如果用户取消了选择，返回
                if not final_path:
                    return False

        # 实际的保存逻辑操作
        try:
            # 获取当前编码和换行符设置
            encoding = self.root.current_encoding
            # 优先使用编辑器的当前换行符设置，如果没有则使用配置中的默认换行符
            line_ending = self.root.current_line_ending

            # 使用核心类转换换行符格式
            content = self.file_core.convert_line_endings(content, line_ending)

            # 写入文件
            try:
                with codecs.open(final_path, "w", encoding=encoding) as f:
                    f.write(content)
            except (IOError, OSError, PermissionError) as e:
                messagebox.showerror("保存错误", f"无法写入文件: {str(e)}")
                return False
            except UnicodeEncodeError as e:
                messagebox.showerror("编码错误", f"文件编码错误: {str(e)}")
                return False
            except Exception as e:
                messagebox.showerror("保存错误", f"保存文件时发生未知错误: {str(e)}")
                return False

            # 如果启用了副本备份功能，则创建副本备份
            if self.config_manager.get("app.backup_enabled", False):
                self._create_backup_copy(final_path)

            # 如果需要，更新当前文件信息
            if need_to_update_current_info:
                self.root.current_file_path = final_path
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

    def _new_file_helper(self, filename="新文件"):
        """新建文件的辅助方法

        Args:
            filename: 文件名，默认为"新文件"
        """
        # 清空文本框内容
        self.root.text_area.delete("1.0", tk.END)

        # 更新字符数缓存，确保_total_chars为0
        self.root.update_char_count()

        # 设置新文件状态标志
        self.root.is_new_file = True

        # 重置文件路径
        self.root.current_file_path = None

        # 设置修改状态为False (新文件初始未修改)
        self.root.set_modified(False)

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
            # 尝试多种编码方式解码文件路径
            for encoding in ["utf-8", "gbk", "gb2312", locale.getpreferredencoding()]:
                try:
                    file_path = file_path.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                # 如果所有编码都失败，使用替换策略
                file_path = file_path.decode("utf-8", errors="replace")

        # 检查路径是否存在
        if os.path.exists(file_path):
            # 检查是否是目录
            if os.path.isdir(file_path):
                messagebox.showwarning(
                    "不支持的操作", f"无法打开目录: {os.path.basename(file_path)}"
                )
                return

            # 关闭当前文件
            self.close_file()

            # 使用通用方法打开文件
            self._open_file(check_backup=True, file_path=file_path)
        else:
            # 路径不存在，提示用户
            messagebox.showwarning(
                "文件不存在", f"无法打开文件: {os.path.basename(file_path)}"
            )

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

    def _handle_backup_on_close(self, file_saved):
        """
        在关闭窗口或关闭文件时处理备份文件的辅助方法

        Args:
            file_saved (bool): 文件是否已保存
        """
        # 检查是否启用了备份功能
        if not self.config_manager.get("app.backup_enabled", False):
            return

        # 如果没有当前文件路径或者是新文件，不需要处理备份
        if not self.root.current_file_path or self.root.is_new_file:
            return

        # 构建备份文件路径
        backup_path = f"{self.root.current_file_path}.bak"

        # 检查备份文件是否存在
        if not os.path.exists(backup_path):
            return

        try:
            if file_saved:
                # 文件已保存，删除备份文件
                os.remove(backup_path)
                self.root.status_bar.show_notification("已删除备份文件")
            else:
                # 文件未保存，保留备份文件作为未保存内容的备份
                self.root.status_bar.show_notification("已保留备份文件")
        except Exception as e:
            # 删除或处理备份文件出错，仅记录错误不影响关闭流程
            self.root.status_bar.show_notification(f"处理备份文件时出错: {str(e)}")

    def close_file(self):
        """关闭当前文件，重置窗口和状态栏状态"""
        # 检查是否需要保存当前文件
        if not self.check_save_before_close():
            return  # 用户取消了操作

        # 重置编辑器状态
        self._reset_editor_state()

    def check_save_before_close(self):
        """
        在关闭文件前检查是否需要保存

        Returns:
            bool: 如果可以继续关闭操作返回True，如果用户取消则返回False
        """
        # 如果文件未修改，直接返回True
        if not self.root.is_modified():
            # 文件未修改，处理备份文件
            self._handle_backup_on_close(file_saved=True)
            return True

        # 如果文件已修改，提示用户
        result = messagebox.askyesnocancel(
            "未保存的更改", "当前文件有未保存的更改，是否保存？"
        )

        # 新增的备份处理逻辑
        if result is True:  # 用户选择保存
            save_success = self._save_file()
            if save_success:
                # 保存成功，处理备份文件
                self._handle_backup_on_close(file_saved=True)
            return save_success

        elif result is False:  # 用户选择不保存
            # 不保存，处理备份文件
            self._handle_backup_on_close(file_saved=False)
            return True

        else:  # 用户选择取消
            return False

    def _open_file(
        self, select_path=False, check_save=False, check_backup=False, file_path=None
    ):
        """
        打开文件核心逻辑

        Args:
            select_path (bool): 是否需要选择文件路径界面
            check_save (bool): 是否需要检查文件是否为保存状态
            check_backup (bool): 是否需要检查备份
            file_path (str): 文件路径

        Returns:
            bool: 如果文件成功打开返回True，否则返回False

        Raises:
            ValueError: 当select_path=False且file_path为None或空字符串时抛出
        """
        # 参数验证：当不需要选择路径时，必须提供有效的文件路径
        if not select_path and not file_path:
            raise ValueError("当select_path=False时，必须提供有效的file_path参数")

        # 检查是否需要检查文件是否为保存状态
        if check_save:
            if not self.check_save_before_close():
                return False  # 用户取消了操作

        # 是否需要选择文件路径界面
        if select_path:
            # 打开文件选择对话框
            file_path = filedialog.askopenfilename(
                title="选择文件",
                filetypes=self.FILE_TYPES,
            )

            if not file_path:
                return False  # 用户取消了选择

        # 验证文件路径有效性
        if not os.path.exists(file_path):
            messagebox.showerror("错误", f"文件不存在: {file_path}")
            return False

        if not os.path.isfile(file_path):
            messagebox.showerror("错误", f"指定路径不是文件: {file_path}")
            return False

        # 检查是否需要处理备份恢复逻辑
        if check_backup:
            if self._check_backup_recovery(file_path):
                return True  # 已处理备份恢复，无需继续打开文件

        # 调用核心文件打开逻辑
        return self._open_file_core(file_path)

    def _open_file_core(self, file_path):
        """
        核心文件打开逻辑，负责读取文件内容并更新编辑器状态

        此方法执行以下操作：
        1. 获取配置的最大文件大小限制
        2. 使用核心类异步读取文件内容
        3. 处理文件编码和行结束符
        4. 更新编辑器内容和状态
        5. 更新状态栏和窗口标题

        Args:
            file_path (str): 要打开的文件的绝对路径

        Returns:
            bool: 如果文件成功打开返回True，否则返回False

        Raises:
            FileNotFoundError: 当指定的文件路径不存在时抛出
            PermissionError: 当没有足够权限读取文件时抛出
            UnicodeDecodeError: 当文件编码无法正确解码时抛出
            MemoryError: 当文件过大超出内存限制时抛出
            ValueError: 当文件路径无效时抛出

        Note:
            - 此方法会显示错误消息框来通知用户文件打开失败的原因
            - 成功打开文件后，会重置编辑器的修改状态
            - 文件内容会被加载到编辑器的文本区域中
        """
        try:
            # 获取配置的最大文件大小
            max_file_size = self.config_manager.get(
                "app.max_file_size", 10 * 1024 * 1024
            )  # 转换为字节

            # 在状态栏显示正在读取文件的提示
            self.root.status_bar.show_notification("正在读取文件...")

            # 使用核心类同步读取文件
            result = self.file_core.read_file_sync(file_path, max_file_size)

            # 直接处理读取结果
            if result["success"]:
                # 读取成功
                data = result["data"]
                try:
                    file_path = data["file_path"]
                    content = data["content"]
                    encoding = data["encoding"]
                    line_ending = data["line_ending"]

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

                    return True

                except Exception as e:
                    messagebox.showerror("错误", f"处理文件内容时出错: {str(e)}")
                    return False
            else:
                # 读取失败
                messagebox.showerror(result["title"], result["message"])
                return False

        except (IOError, OSError, PermissionError) as e:
            messagebox.showerror("文件访问错误", f"启动文件读取时出错: {str(e)}")
            return False
        except UnicodeDecodeError as e:
            messagebox.showerror("编码错误", f"启动文件读取时编码错误: {str(e)}")
            return False
        except MemoryError as e:
            messagebox.showerror("内存错误", f"启动文件读取时内存不足: {str(e)}")
            return False
        except ValueError as e:
            messagebox.showerror("参数错误", f"启动文件读取时参数无效: {str(e)}")
            return False
        except Exception as e:
            messagebox.showerror("错误", f"启动文件读取时出错: {str(e)}")
            return False

    def open_config_file(self):
        """打开配置文件并加载到编辑器"""
        try:
            # 获取配置文件路径
            from config.config_manager import CONFIG_PATH

            # 检查配置文件是否存在
            if not os.path.exists(CONFIG_PATH):
                messagebox.showinfo(
                    "提示", "配置文件不存在，将在首次修改设置时自动创建"
                )
                return

            # 使用通用文件打开方法打开配置文件
            self._open_file(file_path=CONFIG_PATH, check_backup=True, check_save=True)
        except (ImportError, AttributeError) as e:
            messagebox.showerror("配置错误", f"配置管理器导入失败: {str(e)}")
        except Exception as e:
            messagebox.showerror("错误", f"打开配置文件时出错: {str(e)}")

    def _check_backup_recovery(self, file_path):
        """
        检查并处理备份恢复逻辑，当检测到备份文件存在时提供恢复选项

        此方法执行以下操作：
        1. 检查备份功能是否启用
        2. 验证备份文件是否存在
        3. 比较原文件和备份文件的修改时间
        4. 显示备份恢复对话框
        5. 根据用户选择执行相应的恢复操作

        Args:
            file_path (str): 要打开的文件的绝对路径

        Returns:
            bool: 如果已处理备份恢复返回True，否则返回False
                 返回True表示已处理文件打开逻辑，调用者不应继续打开文件
                 返回False表示未处理备份恢复，调用者应继续正常打开文件

        Raises:
            OSError: 当访问文件系统失败时抛出
            PermissionError: 当没有足够权限访问文件时抛出
            ValueError: 当文件路径无效时抛出

        Note:
            - 备份文件路径为原文件路径添加".bak"后缀
            - 备份恢复操作包括：
              * 打开原文件
              * 打开原文件并删除备份
              * 打开备份文件并重命名为原文件
              * 打开备份文件（不重命名）
            - 所有错误都会通过消息框显示给用户
            - 如果用户取消操作或发生错误，方法返回True阻止继续打开文件
        """
        # 检查是否启用了备份功能
        if not self.config_manager.get("app.backup_enabled", False):
            return False

        # 构建备份文件路径
        backup_path = f"{file_path}.bak"

        # 检查备份文件是否存在
        if not os.path.exists(backup_path):
            return False

        # 获取文件和备份文件的修改时间
        try:
            file_mtime = os.path.getmtime(file_path)
            backup_mtime = os.path.getmtime(backup_path)

            # 显示备份恢复对话框
            dialog = SimpleBackupDialog(self.root, file_path, backup_path)
            choice = dialog.result["action"]

            # 处理用户选择
            if choice is None or choice == BackupActions.CANCEL:
                return True  # 用户取消，不打开任何文件

            elif choice == BackupActions.OPEN_ORIGINAL:
                # 从源文件打开
                self._open_file_core(file_path)
                return True  # 已处理，无需继续打开原文件

            elif choice == BackupActions.OPEN_ORIGINAL_DELETE_BACKUP:
                # 从源文件打开并删除备份文件
                try:
                    os.remove(backup_path)
                    self._open_file_core(file_path)
                    return True  # 已处理，无需继续打开原文件
                except Exception as e:
                    messagebox.showerror("错误", f"删除备份文件失败: {str(e)}")
                    return True  # 出错，不打开任何文件

            elif choice == BackupActions.OPEN_BACKUP_RENAME:
                # 从备份文件打开并重命名为原文件
                try:
                    # 先删除原文件
                    os.remove(file_path)
                    # 重命名备份文件为原文件名
                    os.rename(backup_path, file_path)
                    # 打开重命名后的文件
                    self._open_file_core(file_path)
                    return True  # 已处理，无需继续打开原文件
                except Exception as e:
                    messagebox.showerror("错误", f"重命名备份文件失败: {str(e)}")
                    return True  # 出错，不打开任何文件

            elif choice == BackupActions.OPEN_BACKUP:
                # 从备份文件打开（不重命名）
                # 直接打开备份文件
                self._open_file_core(backup_path)
                return True  # 已处理，无需继续打开原文件

        except Exception as e:
            messagebox.showerror("错误", f"处理备份文件时出错: {str(e)}")
            return True  # 出错，不打开任何文件

        return False
