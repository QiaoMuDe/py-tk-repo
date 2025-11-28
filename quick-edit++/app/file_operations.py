"""
文件操作相关的业务逻辑处理
"""

import codecs
from email import message
import os
import time
import tkinter as tk
import locale
from tkinter import filedialog, messagebox
from config.config_manager import config_manager
from .file_operation_core import FileOperationCore
from ui.simple_backup_dialog import SimpleBackupDialog, BackupActions
from ui.rename_dialog import show_rename_dialog
import shutil
from config.config_manager import CONFIG_PATH
from loguru import logger


class FileOperations:
    """处理文件操作相关的业务逻辑"""

    # 通用文件类型列表, 避免在多个方法中重复定义
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
            # 构建备份文件路径 (在原文件名后添加.bak扩展名)
            backup_path = f"{file_path}.bak"

            # 如果备份文件已存在, 先删除
            if os.path.exists(backup_path):
                os.remove(backup_path)

            # 使用copy2保留元数据
            try:
                shutil.copy2(file_path, backup_path)
                # self.root.status_bar.show_notification("已创建副本备份")
                self.root.nm.show_success(title="备份成功", message="已创建副本备份")

            except (IOError, OSError, PermissionError) as e:
                # messagebox.showerror("备份错误", f"创建副本备份失败: {str(e)}")
                self.root.nm.show_error(
                    title="备份错误", message=f"创建副本备份失败: {str(e)}"
                )

            except Exception as e:
                # messagebox.showerror("备份错误", f"创建备份时发生未知错误: {str(e)}")
                self.root.nm.show_error(
                    title="备份错误", message=f"创建备份时发生未知错误: {str(e)}"
                )

        except Exception as e:
            logger.error(f"创建备份时出错: {file_path}, 错误信息: {str(e)}")
            # messagebox.showerror("备份错误", f"备份处理失败: {str(e)}")
            self.root.nm.show_error(title="备份错误", message=f"备份处理失败: {str(e)}")

    def _generate_default_filename(self, content_prefix):
        """
        根据文本内容前缀生成默认文件名

        使用文本内容的前几个字符作为文件名前缀, 如果内容为空或只有空白字符,
        则使用"新文件"作为默认前缀

        Args:
            content_prefix: 文本内容的前缀 (已截断)

        Returns:
            str: 默认文件名 (包含.txt扩展名)
        """
        if not content_prefix:
            return "新文件.txt"

        # 去除首尾空白字符
        prefix = content_prefix.strip()

        # 如果前缀为空或只有空白字符, 使用默认名称
        if not prefix:
            return "新文件.txt"

        # 清理文件名中的非法字符
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            prefix = prefix.replace(char, "_")

        # 如果前缀以点开头, 在前面添加下划线 (避免隐藏文件)
        if prefix.startswith("."):
            prefix = "_" + prefix

        # 确保文件名不超过50个字符 (包括扩展名)
        if len(prefix) > 46:  # 46 + 4 (.txt) = 50
            prefix = prefix[:46]

        # 添加.txt扩展名
        return f"{prefix}.txt"

    def _save_file(self, file_path=None, force_save_as=False, is_auto_save=False):
        """
        统一的文件保存方法, 整合保存和另存为功能

        此方法执行以下操作:
        1. 检查文件内容和状态
        2. 根据需要显示文件选择对话框
        3. 调用核心保存方法写入文件
        4. 更新编辑器状态和界面

        Args:
            file_path (str, optional): 要保存的文件路径。如果为None且当前有文件路径, 则使用当前路径
            force_save_as (bool): 是否强制执行另存为操作, 即使已有文件路径
            is_auto_save (bool): 是否是自动保存操作, 自动保存时不显示"文件已保存"通知

        Returns:
            bool: 保存是否成功

        Note:
            - 当file_path为None且当前没有文件路径时, 会显示另存为对话框
            - 当force_save_as为True时, 即使有当前文件路径也会显示另存为对话框
            - 如果文件内容为空且没有文件路径, 会提示"没有内容可保存"
            - 如果文件未修改且不是强制另存为, 会提示"文件未修改, 无需保存"
        """
        # 获取文本框内容 (只获取一次)
        content = self.root.text_area.get("1.0", tk.END).rstrip("\n")

        # 检查是否有文件路径
        has_current_path = self.root.current_file_path is not None

        # 情况1: 没有打开文件且文本框没有内容
        if not has_current_path and not content:
            info_text = "没有内容可另存为" if force_save_as else "没有内容可保存"
            # messagebox.showinfo("提示", info_text)
            self.root.nm.show_info(message=info_text)
            return False

        # 情况2: 已经打开文件, 检查是否修改 (除非是强制另存为)
        if has_current_path and not self.root.is_modified() and not force_save_as:
            # messagebox.showinfo("提示", "文件未修改, 无需保存")
            self.root.nm.show_info(message="文件未修改, 无需保存")
            return True

        # 确定最终保存路径
        final_path = file_path
        need_to_update_current_info = True  # 是否需要更新当前文件信息

        if final_path is None:
            # 没有指定路径, 使用当前路径或显示另存为对话框
            if has_current_path and not force_save_as:
                # 使用当前文件路径, 不更新文件信息
                final_path = self.root.current_file_path
                need_to_update_current_info = False
            else:
                # 没有当前路径或强制另存为, 显示另存为对话框

                # 显示保存对话框
                # 根据force_save_as参数决定标题是"保存"还是"另存为"
                dialog_title = "另存为" if force_save_as else "保存"

                # 生成默认文件名 (只传递前30个字符, 避免大数据传递)
                default_filename = self._generate_default_filename(
                    self.root.text_area.get("1.0", "1.0+30 chars")
                )

                final_path = filedialog.asksaveasfilename(
                    title=dialog_title,
                    defaultextension=".txt",
                    filetypes=self.FILE_TYPES,
                    initialfile=default_filename,
                )

                # 如果用户取消了选择, 返回
                if not final_path:
                    return False

        # 实际的保存逻辑操作
        try:
            # 获取当前编码
            encoding = self.root.current_encoding

            # 获取当前换行符类型
            line_ending = self.root.current_line_ending

            # 使用核心类转换换行符格式
            content = self.file_core.convert_line_endings(content, line_ending)

            # 写入文件
            try:
                with codecs.open(final_path, "w", encoding=encoding) as f:
                    f.write(content)
            except (IOError, OSError, PermissionError) as e:
                logger.error(f"无法写入文件: {final_path}, 错误信息: {str(e)}")
                # messagebox.showerror("保存错误", f"无法写入文件: {str(e)}")
                self.root.nm.show_error(
                    title="保存错误", message=f"无法写入文件: {str(e)}"
                )
                return False

            except UnicodeEncodeError as e:
                logger.error(f"编码错误: {final_path}, 错误信息: {str(e)}")
                # messagebox.showerror("编码错误", f"文件编码错误: {str(e)}")
                self.root.nm.show_error(
                    title="编码错误", message=f"文件编码错误: {str(e)}"
                )
                return False

            except Exception as e:
                logger.error(f"保存文件时出错: {final_path}, 错误信息: {str(e)}")
                # messagebox.showerror("保存错误", f"保存文件时发生未知错误: {str(e)}")
                self.root.nm.show_error(
                    title="保存错误", message=f"保存文件时发生未知错误: {str(e)}"
                )
                return False

            # 文件保存成功后, 更新文件监听器缓存, 防止程序的保存被误当成修改
            if final_path and os.path.exists(final_path):
                self.root.file_watcher.update_cache_after_save(final_path)

            # 如果启用了副本备份功能, 则创建副本备份
            if self.config_manager.get("app.backup_enabled", False):
                self._create_backup_copy(final_path)

            # 如果需要, 更新当前文件信息
            if need_to_update_current_info:
                self.root.current_file_path = final_path
                self.root.current_encoding = encoding
                self.root.current_line_ending = line_ending

            # 重置修改状态
            self.root.set_modified(False)  # 清除修改状态标志
            self.root.is_new_file = False  # 清除新文件状态标志

            # 获取当前光标位置
            try:
                cursor_pos = self.root.text_area.index("insert")
                row, col = cursor_pos.split(".")
                row = int(row)
                col = int(col) + 1  # 转换为1基索引

                # 更新状态栏状态信息 (从"已修改"改为"就绪")
                self.root.status_bar.set_status_info(status="就绪", row=row, col=col)
            except Exception as e:
                logger.error(f"获取当前光标位置时出错: {str(e)}")
                # 如果获取位置失败, 使用默认值
                self.root.status_bar.set_status_info(status="就绪")

            # 显示保存通知 - 仅在非自动保存时显示
            if not is_auto_save:
                self.root.nm.show_info(message="文件已保存")
                # self.root.status_bar.show_notification(f"文件已保存")

            # 更新窗口标题
            self.root._update_window_title()

            # 应用语法高亮
            if self.root.syntax_highlighter and final_path:
                self.root.syntax_highlighter.apply_highlighting(final_path)

            # 更新状态栏文件信息
            self.root.status_bar.update_file_info()

            # 更新文件菜单状态
            self.root.update_file_menu_state()

            return True

        except Exception as e:
            logger.error(f"保存文件时出错: {final_path}, 错误信息: {str(e)}")
            # messagebox.showerror("错误", f"保存文件时出错: {str(e)}")
            self.root.nm.show_error(message=f"保存文件时出错: {str(e)}")
            return False

    def _new_file_helper(self, filename="新文件"):
        """新建文件的辅助方法

        Args:
            filename: 文件名, 默认为"新文件"
        """
        # 先调用关闭文件方法
        if not self.close_file():
            return False

        # 设置新文件特定的状态
        self.root.is_new_file = True

        # 更新窗口标题为新文件
        self.root.title(f"{filename} - QuickEdit++")

    def handle_dropped_files(self, files):
        """
        处理拖拽文件事件

        Args:
            files: 拖拽的文件列表, 可能是字节串或字符串
        """
        if not files:
            return

        # 如果拖拽了多个文件, 直接提示并返回
        if len(files) > 1:
            # messagebox.showinfo("提示", "只支持打开单个文件, 请一次只拖拽一个文件")
            self.root.nm.show_info(message="只支持打开单个文件, 请一次只拖拽一个文件")
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
                # 如果所有编码都失败, 使用替换策略
                file_path = file_path.decode("utf-8", errors="replace")

        # 检查路径是否存在
        if os.path.exists(file_path):
            # 检查是否是目录
            if os.path.isdir(file_path):
                # messagebox.showwarning(
                #     "不支持的操作", f"无法打开目录: {os.path.basename(file_path)}"
                # )
                self.root.nm.show_warning(
                    title="不支持的操作",
                    message=f"无法打开目录: {os.path.basename(file_path)}",
                )
                return

            # 延迟关闭当前文件和打开新文件, 确保在主线程中执行
            self.root.after(10, lambda: self._process_dropped_file(file_path))
        else:
            # 路径不存在, 提示用户
            # messagebox.showwarning(
            #     "文件不存在", f"无法打开文件: {os.path.basename(file_path)}"
            # )
            self.root.nm.show_warning(
                title="文件不存在",
                message=f"无法打开文件: {os.path.basename(file_path)}",
            )
            return

    def _process_dropped_file(self, file_path):
        """
        处理拖拽的文件, 确保在主线程中执行

        Args:
            file_path: 文件路径
        """
        try:
            # 关闭当前文件
            if not self.close_file():
                return False  # 用户取消了操作

            # 使用通用方法打开文件
            self._open_file(check_save=True, check_backup=True, file_path=file_path)
        except Exception as e:
            logger.error(f"处理拖拽文件时出错: {file_path}, 错误信息: {str(e)}")
            # messagebox.showerror("错误", f"处理拖拽文件时出错: {e}")
            self.root.nm.show_error(message=f"处理拖拽文件时出错: {e}")

    def _reset_editor_state(self):
        """重置编辑器状态, 包括清空内容、重置文件属性和更新状态栏"""
        # 清空编辑器内容
        self.root.text_area.delete("1.0", tk.END)

        # 更新字符数缓存, 确保_total_chars为0
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

        # 更新窗口标题
        self.root._update_window_title()

        # 清除语法高亮
        self.root.syntax_highlighter.reset_highlighting()

        # 更新文件状态
        self.root.status_bar.set_status_info("就绪")
        # 重置状态栏右侧文件信息
        self.root.status_bar.update_file_info()

        # 停止文件监听
        if self.root.file_watcher:
            self.root.file_watcher.stop_watching()

        # 更新文件菜单状态
        self.root.update_file_menu_state()

        # 使用统一的内存清理方法
        self.root.clear_memory()

    def _handle_backup_on_close(self, file_saved):
        """
        在关闭窗口或关闭文件时处理备份文件的辅助方法

        Args:
            file_saved (bool): 文件是否已保存
        """
        # 检查是否启用了备份功能
        if not self.config_manager.get("app.backup_enabled", False):
            return

        # 如果没有当前文件路径或者是新文件, 不需要处理备份
        if not self.root.current_file_path or self.root.is_new_file:
            return

        # 构建备份文件路径
        backup_path = f"{self.root.current_file_path}.bak"

        # 检查备份文件是否存在
        if not os.path.exists(backup_path):
            return

        try:
            if file_saved:
                # 文件已保存, 删除备份文件
                os.remove(backup_path)
                # self.root.status_bar.show_notification("已删除备份文件")
                self.root.nm.show_info(message="已删除备份文件")

            else:
                # 文件未保存, 保留备份文件作为未保存内容的备份
                # self.root.status_bar.show_notification("已保留备份文件")
                self.root.nm.show_info(message="已保留备份文件")

        except Exception as e:
            # 删除或处理备份文件出错, 仅记录错误不影响关闭流程
            logger.error(f"处理备份文件时出错: {backup_path}, 错误信息: {str(e)}")
            # self.root.status_bar.show_notification(f"处理备份文件时出错: {str(e)}")
            self.root.nm.show_error(message=f"处理备份文件时出错: {str(e)}")

    def close_file(self):
        """
        关闭当前文件, 重置窗口和状态栏状态
        """
        # 检查是否需要保存当前文件
        if not self.check_save_before_close():
            return False  # 用户取消了操作

        # 重置编辑器状态
        self._reset_editor_state()

        return True

    def check_save_before_close(self):
        """
        在关闭文件前检查是否需要保存

        Returns:
            bool: 如果可以继续关闭操作返回True, 如果用户取消则返回False
        """
        # 如果文件未修改, 直接返回True
        if not self.root.is_modified():
            # 文件未修改, 处理备份文件
            self._handle_backup_on_close(file_saved=True)
            return True

        # 如果文件已修改, 提示用户
        result = messagebox.askyesnocancel(
            "未保存的更改", "当前文件有未保存的更改, 是否保存？"
        )

        # 新增的备份处理逻辑
        if result is True:  # 用户选择保存
            save_success = self._save_file()
            if save_success:
                # 保存成功, 处理备份文件
                self._handle_backup_on_close(file_saved=True)
            return save_success

        elif result is False:  # 用户选择不保存
            # 不保存, 处理备份文件
            self._handle_backup_on_close(file_saved=False)
            return True

        else:  # 用户选择取消
            return False

    def check_save_before_rename(self):
        """
        在重命名文件前检查是否需要保存

        Returns:
            bool: 如果可以继续重命名操作返回True, 如果用户取消则返回False
        """
        # 如果文件未修改, 直接返回True
        if not self.root.is_modified():
            return True

        # 如果文件已修改, 提示用户
        result = messagebox.askyesnocancel(
            "文件已修改",
            "文件已被修改，是否保存后再重命名？\n\n点击'是'保存并重命名\n点击'否'直接重命名(不保存修改)\n点击'取消'放弃重命名",
        )

        if result is True:  # 用户选择保存
            return self.save_file()
        elif result is False:  # 用户选择不保存
            return True
        else:  # 用户选择取消
            return False

    def _open_file(
        self,
        file_path=None,
        select_path=False,
        check_backup=False,
        check_save=False,
        encoding=None,
        is_auto_reload=False,
    ):
        """
        打开文件核心逻辑

        Args:
            file_path (str): 文件路径
            select_path (bool): 是否需要选择文件路径界面
            check_save (bool): 是否需要检查文件是否已保存
            check_backup (bool): 是否需要检查备份
            encoding (str, optional): 指定文件编码, 如果为None则自动检测
            is_auto_reload (bool): 是否为自动重载模式

        Returns:
            bool: 如果文件成功打开返回True, 否则返回False

        Raises:
            ValueError: 当select_path=False且file_path为None或空字符串时抛出
        """
        # 参数验证: 当不需要选择路径时, 必须提供有效的文件路径
        if not select_path and not file_path:
            logger.error("打开文件时未提供有效文件路径")
            return False

        # 检查文件是否已保存
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
            logger.error(f"文件不存在: {file_path}")
            # messagebox.showerror("错误", f"文件不存在: {file_path}")
            self.root.nm.show_error(message=f"文件不存在: {file_path}")
            return False

        if not os.path.isfile(file_path):
            logger.error(f"指定路径不是文件: {file_path}")
            # messagebox.showerror("错误", f"指定路径不是文件: {file_path}")
            self.root.nm.show_error(message=f"指定路径不是文件: {file_path}")
            return False

        # 重置编辑器状态
        self._reset_editor_state()

        # 检查是否需要处理备份恢复逻辑
        if check_backup:
            if self._check_backup_recovery(file_path):
                return True  # 已处理备份恢复, 无需继续打开文件

        # 调用核心文件打开逻辑
        return self._open_file_core(file_path, encoding, is_auto_reload)

    def _open_file_core(self, file_path, encoding=None, is_auto_reload=False):
        """
        核心文件打开逻辑, 负责读取文件内容并更新编辑器状态

        此方法执行以下操作:
        1. 获取配置的最大文件大小限制
        2. 使用核心类异步读取文件内容
        3. 处理文件编码和行结束符
        4. 更新编辑器内容和状态
        5. 更新状态栏和窗口标题

        Args:
            file_path (str): 要打开的文件的绝对路径
            encoding (str, optional): 指定文件编码, 如果为None则自动检测
            is_auto_reload (bool): 是否为自动重载模式

        Returns:
            bool: 如果文件成功打开返回True, 否则返回False

        Raises:
            FileNotFoundError: 当指定的文件路径不存在时抛出
            PermissionError: 当没有足够权限读取文件时抛出
            UnicodeDecodeError: 当文件编码无法正确解码时抛出
            MemoryError: 当文件过大超出内存限制时抛出
            ValueError: 当文件路径无效时抛出

        Note:
            - 此方法会显示错误消息框来通知用户文件打开失败的原因
            - 成功打开文件后, 会重置编辑器的修改状态
            - 文件内容会被加载到编辑器的文本区域中
        """
        try:
            # 获取配置的最大文件大小
            max_file_size = self.config_manager.get(
                "app.max_file_size", 10 * 1024 * 1024
            )  # 转换为字节

            # 在状态栏显示正在读取文件的提示
            self.root.status_bar.show_notification("正在读取文件...", 500)
            # self.root.nm.show_info(message="正在读取文件...", duration=1000)

            # 使用核心类同步读取文件
            result = self.file_core.read_file_sync(file_path, max_file_size, encoding)

            # 直接处理读取结果
            if result["success"]:
                # 读取成功
                data = result["data"]
                try:
                    file_path = data["file_path"]
                    content = data["content"]
                    encoding = data["encoding"]
                    line_ending = data["line_ending"]

                    # 插入编辑器内容
                    self.root.text_area.delete("1.0", tk.END)
                    self.root.text_area.insert("1.0", content)

                    # 调用清除方法, 清除刚才插入的撤销栈
                    self.root.clear_memory()

                    # 保存当前文件路径到编辑器实例
                    self.root.current_file_path = file_path
                    self.root.current_encoding = encoding
                    self.root.current_line_ending = line_ending

                    # 重置修改状态
                    self.root.set_modified(False)  # 清除修改状态标志
                    self.root.is_new_file = False  # 清除新文件状态标志

                    # 更新缓存的字符数
                    self.root.update_char_count()

                    # 更新状态栏
                    if not is_auto_reload:
                        # self.root.status_bar.show_notification(
                        #     f"已打开: {os.path.basename(file_path)}", 500
                        # )
                        self.root.nm.show_info(
                            message=f"已打开: {os.path.basename(file_path)}"
                        )

                    # 更新窗口标题
                    self.root._update_window_title()

                    # 将文件添加到最近打开列表
                    if self.config_manager.get("recent_files.enabled", True):
                        self.config_manager.add_recent_file(file_path)
                        # 刷新最近文件菜单 (如果存在)
                        if self.root.recent_files_menu:
                            self.root.recent_files_menu.refresh()

                    # 更新文件监听器缓存
                    self.root.file_watcher.update_file_info()

                    # 启动文件监听
                    self.root.file_watcher.start_watching(file_path)

                    # 应用语法高亮
                    self.root.syntax_highlighter.apply_highlighting(file_path)

                    # 更新状态栏文件信息
                    self.root.status_bar.update_file_info()

                    # 更新文件菜单状态
                    self.root.update_file_menu_state()

                    return True

                except Exception as e:
                    logger.error(f"处理文件内容时出错: {file_path}, 错误信息: {str(e)}")
                    # messagebox.showerror("错误", f"处理文件内容时出错: {str(e)}")
                    self.root.nm.show_error(message=f"处理文件内容时出错: {str(e)}")
                    return False
            else:
                # 读取失败
                logger.error(
                    f"读取文件时出错: {file_path}, 错误信息: {result['message']}"
                )
                messagebox.showerror(result["title"], result["message"])
                # self.root.nm.show_error(title=result["title"], message=result["message"])
                return False

        except (IOError, OSError, PermissionError) as e:
            logger.error(f"启动文件读取时出错: {file_path}, 错误信息: {str(e)}")
            # messagebox.showerror("文件访问错误", f"启动文件读取时出错: {str(e)}")
            self.root.nm.show_error(
                title="文件访问错误", message=f"启动文件读取时出错: {str(e)}"
            )
            return False

        except UnicodeDecodeError as e:
            logger.error(f"启动文件读取时编码错误: {file_path}, 错误信息: {str(e)}")
            # messagebox.showerror("编码错误", f"启动文件读取时编码错误: {str(e)}")
            self.root.nm.show_error(
                title="编码错误", message=f"启动文件读取时编码错误: {str(e)}"
            )
            return False

        except MemoryError as e:
            logger.error(f"启动文件读取时内存不足: {file_path}, 错误信息: {str(e)}")
            # messagebox.showerror("内存错误", f"启动文件读取时内存不足: {str(e)}")
            self.root.nm.show_error(
                title="内存错误", message=f"启动文件读取时内存不足: {str(e)}"
            )
            return False

        except ValueError as e:
            logger.error(f"启动文件读取时参数无效: {file_path}, 错误信息: {str(e)}")
            # messagebox.showerror("参数错误", f"启动文件读取时参数无效: {str(e)}")
            self.root.nm.show_error(
                title="参数错误", message=f"启动文件读取时参数无效: {str(e)}"
            )
            return False

        except Exception as e:
            logger.error(f"启动文件读取时出错: {file_path}, 错误信息: {str(e)}")
            # messagebox.showerror("错误", f"启动文件读取时出错: {str(e)}")
            self.root.nm.show_error(
                title="错误", message=f"启动文件读取时出错: {str(e)}"
            )
            return False

    def open_config_file(self):
        """打开配置文件并加载到编辑器"""
        try:
            # 检查是否为只读模式
            if self.root.is_read_only:
                # messagebox.showinfo(
                #     "提示", "当前为只读模式，请先关闭只读模式后再打开配置文件"
                # )
                self.root.nm.show_info(
                    message="当前为只读模式，请先关闭只读模式后再打开配置文件"
                )
                return

            # 检查配置文件是否存在
            if not os.path.exists(CONFIG_PATH):
                # messagebox.showinfo(
                #     "提示", "配置文件不存在, 将在首次修改设置时自动创建"
                # )
                self.root.nm.show_info(
                    message="配置文件不存在, 将在首次修改设置时自动创建"
                )
                return

            # 使用通用文件打开方法打开配置文件
            self._open_file(
                file_path=CONFIG_PATH,
                check_save=True,
                check_backup=True,
            )
        except (ImportError, AttributeError) as e:
            logger.error(f"配置管理器导入失败: {str(e)}")
            # messagebox.showerror("配置错误", f"配置管理器导入失败: {str(e)}")
            self.root.nm.show_error(
                title="配置错误", message=f"配置管理器导入失败: {str(e)}"
            )

        except Exception as e:
            logger.error(f"打开配置文件时出错: {str(e)}")
            # messagebox.showerror("错误", f"打开配置文件时出错: {str(e)}")
            self.root.nm.show_error(
                title="错误", message=f"打开配置文件时出错: {str(e)}"
            )

    def open_log_file(self):
        """打开日志文件并加载到编辑器"""
        try:
            # 检查是否为只读模式
            if self.root.is_read_only:
                # messagebox.showinfo(
                #     "提示", "当前为只读模式，请先关闭只读模式后再打开日志文件"
                # )
                self.root.nm.show_info(
                    message="当前为只读模式，请先关闭只读模式后再打开日志文件"
                )
                return

            # 获取日志文件路径
            log_dir = self.config_manager.get("logging.log_dir")
            log_file = self.config_manager.get("logging.log_file", "app.log")
            log_path = os.path.join(log_dir, log_file)

            # 检查日志目录和文件是否存在
            if not os.path.exists(log_dir):
                # messagebox.showinfo(
                #     "提示", "日志目录不存在, 将在首次记录日志时自动创建"
                # )
                self.root.nm.show_info(
                    message="日志目录不存在, 将在首次记录日志时自动创建"
                )
                return

            if not os.path.exists(log_path):
                # messagebox.showinfo(
                #     "提示", "日志文件不存在, 将在首次记录日志时自动创建"
                # )
                self.root.nm.show_info(
                    message="日志文件不存在, 将在首次记录日志时自动创建"
                )
                return

            # 使用通用文件打开方法打开日志文件
            self._open_file(
                file_path=log_path,
                check_save=True,
                check_backup=True,
            )
        except (ImportError, AttributeError) as e:
            logger.error(f"配置管理器导入失败: {str(e)}")
            # messagebox.showerror("配置错误", f"配置管理器导入失败: {str(e)}")
            self.root.nm.show_error(
                title="配置错误", message=f"配置管理器导入失败: {str(e)}"
            )

        except Exception as e:
            logger.error(f"打开日志文件时出错: {str(e)}")
            # messagebox.showerror("错误", f"打开日志文件时出错: {str(e)}")
            self.root.nm.show_error(
                title="错误", message=f"打开日志文件时出错: {str(e)}"
            )

    def save_file_copy(self):
        """
        保存当前文件的副本

        此方法执行以下操作:
        1. 检查是否有打开的文件
        2. 如果有未保存的更改，先保存当前文件
        3. 生成带有时间戳的副本文件名
        4. 创建文件副本

        Returns:
            bool: 操作是否成功
        """
        # 检查是否有打开的文件
        if not self.root.current_file_path:
            # messagebox.showinfo("提示", "没有打开的文件，无法创建副本")
            self.root.nm.show_info(message="没有打开的文件，无法创建副本")
            return False

        # 检查是否为只读模式
        if self.root.is_read_only:
            result = messagebox.askyesno(
                "只读模式",
                "当前文件处于只读模式，是否仍要创建副本？\n\n创建副本不会修改原文件。",
            )
            if not result:
                return False

        # 如果文件已修改，先保存当前文件
        if self.root.is_modified():
            result = messagebox.askyesno(
                "未保存的更改", "当前文件有未保存的更改，是否先保存？"
            )
            if result:
                save_success = self._save_file()
                if not save_success:
                    return False
            else:
                # 用户选择不保存，但仍继续创建副本
                pass

        try:
            # 获取原文件路径和名称
            original_path = self.root.current_file_path
            dir_name = os.path.dirname(original_path)
            file_name = os.path.basename(original_path)

            # 分离文件名和扩展名
            name_without_ext, ext = os.path.splitext(file_name)

            # 生成时间戳
            timestamp = time.strftime("%Y%m%d%H%M%S")

            # 限制文件名部分最多为10个字符（包括汉字和英文字符）
            max_name_length = 10

            # 如果文件名超过最大长度，进行截断
            if len(name_without_ext) > max_name_length:
                # 截断文件名，确保不超过最大长度
                truncated_name = name_without_ext[:max_name_length]
                # 记录截断日志
                logger.debug(
                    f"文件名过长，已截断: {name_without_ext} -> {truncated_name}"
                )
                # 记录截断日志
                self.root.nm.show_warning(
                    message=f"文件名过长，已截断: {name_without_ext} -> {truncated_name}"
                )
                name_without_ext = truncated_name

            # 构建副本文件名: 文件名_时间戳_副本.扩展名
            copy_filename = f"{name_without_ext}_{timestamp}_副本{ext}"
            copy_path = os.path.join(dir_name, copy_filename)

            # 创建文件副本
            shutil.copy2(original_path, copy_path)

            # 显示成功消息
            # self.root.status_bar.show_notification(
            #     f"已创建文件副本:\n{copy_filename}", 1500
            # )
            self.root.nm.show_info(message=f"已创建文件副本:\n{copy_filename}")
            return True

        except Exception as e:
            logger.error(f"创建文件副本时出错: {str(e)}")
            # messagebox.showerror("错误", f"创建文件副本时出错: {str(e)}")
            self.root.nm.show_error(message=f"创建文件副本时出错: {str(e)}")
            return False

    def rename_file(self):
        """
        重命名当前打开的文件

        此方法执行以下操作:
        1. 检查是否有当前文件
        2. 检查是否为只读模式
        3. 检查文件是否被修改
        4. 显示重命名对话框
        5. 执行文件系统重命名操作
        6. 更新应用程序中的文件路径引用

        Returns:
            bool: 重命名是否成功
        """
        # 检查是否为只读模式
        if self.root.is_read_only:
            self.root.nm.show_info(message="当前为只读模式，无法重命名文件")
            return False

        # 检查是否有当前文件路径（新文件未保存的情况）
        if not self.root.current_file_path or self.root.is_new_file:
            # 对于新文件，直接提示另存为
            self.root.nm.show_warning(
                title="无法重命名", message="请先保存文件后再进行重命名操作"
            )
            return False

        # 检查文件是否被修改，并处理保存逻辑
        if not self.check_save_before_rename():
            return False

        # 显示重命名对话框
        new_name = show_rename_dialog(self.root, self.root.current_file_path)
        if not new_name:
            return False  # 用户取消

        # 获取当前文件路径和目录
        current_path = self.root.current_file_path
        directory = os.path.dirname(current_path)  # 获取当前文件所在目录
        new_path = os.path.join(directory, new_name)  # 构建新的文件路径

        try:
            # 重置编辑器状态
            self._reset_editor_state()

            # 执行文件系统重命名
            os.rename(current_path, new_path)

            # 直接调用_open_file方法打开重命名后的文件
            return self._open_file(file_path=new_path)

        except Exception as e:
            logger.error(
                f"重命名文件失败: {current_path} -> {new_path}, 错误: {str(e)}"
            )
            self.root.nm.show_error(
                title="重命名失败", message=f"重命名文件时出错: {str(e)}"
            )

            return False

    def _check_backup_recovery(self, file_path):
        """
        检查并处理备份恢复逻辑, 当检测到备份文件存在时提供恢复选项

        此方法执行以下操作:
        1. 检查备份功能是否启用
        2. 验证备份文件是否存在
        3. 比较原文件和备份文件的修改时间
        4. 显示备份恢复对话框
        5. 根据用户选择执行相应的恢复操作

        Args:
            file_path (str): 要打开的文件的绝对路径

        Returns:
            bool: 如果已处理备份恢复返回True, 否则返回False
                 返回True表示已处理文件打开逻辑, 调用者不应继续打开文件
                 返回False表示未处理备份恢复, 调用者应继续正常打开文件

        Raises:
            OSError: 当访问文件系统失败时抛出
            PermissionError: 当没有足够权限访问文件时抛出
            ValueError: 当文件路径无效时抛出

        Note:
            - 备份文件路径为原文件路径添加".bak"后缀
            - 备份恢复操作包括:
              * 打开原文件
              * 打开原文件并删除备份
              * 打开备份文件并重命名为原文件
              * 打开备份文件 (不重命名)
            - 所有错误都会通过消息框显示给用户
            - 如果用户取消操作或发生错误, 方法返回True阻止继续打开文件
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
                return True  # 用户取消, 不打开任何文件

            elif choice == BackupActions.OPEN_ORIGINAL:
                # 从源文件打开
                self._open_file(file_path)
                return True  # 已处理, 无需继续打开原文件

            elif choice == BackupActions.OPEN_ORIGINAL_DELETE_BACKUP:
                # 从源文件打开并删除备份文件
                try:
                    os.remove(backup_path)
                    self._open_file(file_path)
                    return True  # 已处理, 无需继续打开原文件

                except Exception as e:
                    # messagebox.showerror("错误", f"删除备份文件失败: {str(e)}")
                    self.root.nm.show_error(message=f"删除备份文件失败: {str(e)}")
                    return True  # 出错, 不打开任何文件

            elif choice == BackupActions.OPEN_BACKUP_RENAME:
                # 从备份文件打开并重命名为原文件
                try:
                    # 先删除原文件
                    os.remove(file_path)
                    # 重命名备份文件为原文件名
                    os.rename(backup_path, file_path)
                    # 打开重命名后的文件
                    self._open_file(file_path)
                    return True  # 已处理, 无需继续打开原文件
                except Exception as e:
                    # messagebox.showerror("错误", f"重命名备份文件失败: {str(e)}")
                    self.root.nm.show_error(message=f"重命名备份文件失败: {str(e)}")
                    return True  # 出错, 不打开任何文件

            elif choice == BackupActions.OPEN_BACKUP:
                # 从备份文件打开 (不重命名)
                # 直接打开备份文件
                self._open_file(backup_path)
                return True  # 已处理, 无需继续打开原文件

        except Exception as e:
            logger.error(f"处理备份文件时出错: {str(e)}")
            # messagebox.showerror("错误", f"处理备份文件时出错: {str(e)}")
            self.root.nm.show_error(message=f"处理备份文件时出错: {str(e)}")
            return True  # 出错, 不打开任何文件

        return False
