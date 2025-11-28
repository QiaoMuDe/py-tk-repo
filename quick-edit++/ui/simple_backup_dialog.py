import os
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import customtkinter as ctk
from config.config_manager import config_manager


# 备份恢复操作常量定义
class BackupActions:
    """备份恢复操作常量类"""

    # 操作类型常量
    CANCEL = "cancel"  # 取消操作
    OPEN_ORIGINAL = "open_original"  # 从源文件打开
    OPEN_ORIGINAL_DELETE_BACKUP = (
        "open_original_delete_backup"  # 从源文件打开并删除备份
    )
    OPEN_BACKUP_RENAME = "open_backup_rename"  # 从备份文件打开并重命名为原文件
    OPEN_BACKUP = "open_backup"  # 从备份文件打开（不重命名）

    # 所有可用操作的列表，可用于验证
    ALL_ACTIONS = [
        CANCEL,
        OPEN_ORIGINAL,
        OPEN_ORIGINAL_DELETE_BACKUP,
        OPEN_BACKUP_RENAME,
        OPEN_BACKUP,
    ]


class SimpleBackupDialog:
    """简化的备份恢复对话框 - 使用CustomTkinter实现"""

    def __init__(self, parent, file_path, backup_path):
        """
        初始化备份恢复对话框

        Args:
            parent: 父窗口
            file_path: 原文件路径
            backup_path: 备份文件路径
        """
        self.parent = parent
        self.file_path = file_path
        self.backup_path = backup_path
        self.result = {"action": None}  # 存储用户选择的结果

        # 获取文件修改时间
        self.original_mtime = self._get_mtime(file_path)
        self.backup_mtime = self._get_mtime(backup_path)

        # 获取文件大小
        self.original_size = self._get_file_size(file_path)
        self.backup_size = self._get_file_size(backup_path)

        # 获取组件字体配置
        self.font_config = config_manager.get_font_config("components")
        self.font = (
            self.font_config.get("font", "Microsoft YaHei UI"),
            self.font_config.get("font_size", 13),
            "bold" if self.font_config.get("font_bold", False) else "normal",
        )

        # 获取主题配置
        self.theme_mode = config_manager.get("app.theme_mode", "light")
        ctk.set_appearance_mode(self.theme_mode)

        # 创建对话框窗口
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("发现备份文件")
        self.width = 700
        self.height = 700
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 先隐藏窗口，避免图标闪烁
        self.dialog.withdraw()

        # 设置窗口关闭协议，点击x按钮时视为取消操作
        self.dialog.protocol("WM_DELETE_WINDOW", self._cancel)

        # 居中显示对话框
        self.parent.center_window(self.dialog, self.width, self.height)

        # 创建UI
        self._create_widgets()

        # 延迟显示窗口，确保图标已设置
        self.dialog.after(250, self._show_dialog)

        # 等待对话框关闭
        self.dialog.wait_window()

    def _show_dialog(self):
        """显示对话框，确保图标已设置"""
        self.dialog.deiconify()
        self.dialog.focus_force()

    def _get_mtime(self, file_path):
        """
        获取文件修改时间

        Args:
            file_path: 文件路径

        Returns:
            str: 格式化后的修改时间
        """
        try:
            mtime = os.path.getmtime(file_path)
            return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return "未知时间"

    def _get_file_size(self, file_path):
        """
        获取文件大小

        Args:
            file_path: 文件路径

        Returns:
            str: 格式化后的文件大小
        """
        try:
            size = os.path.getsize(file_path)
            # 转换为更友好的显示格式
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                size_kb = size / 1024
                return f"{size_kb:.2f} KB" if size_kb % 1 else f"{int(size_kb)} KB"
            else:
                size_mb = size / (1024 * 1024)
                return f"{size_mb:.2f} MB" if size_mb % 1 else f"{int(size_mb)} MB"
        except Exception:
            return "未知大小"

    def _create_widgets(self):
        """创建对话框组件"""
        # 主框架 - 使用transparent颜色移除背景
        main_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 标题
        title_label = ctk.CTkLabel(
            main_frame,
            text="发现备份文件",
            font=(self.font[0], self.font[1] + 2, "bold"),
            text_color="#1E90FF" if self.theme_mode == "light" else "#4A9EFF",
        )
        title_label.pack(pady=(10, 20))

        # 提示信息
        info_text = f"在文件 {os.path.basename(self.file_path)} 所在目录发现了备份文件"
        info_label = ctk.CTkLabel(
            main_frame, text=info_text, font=self.font, wraplength=500
        )
        info_label.pack(pady=(0, 20))

        # 文件信息框架 - 使用transparent颜色移除背景
        file_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        file_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 文件信息标题
        file_info_title = ctk.CTkLabel(
            file_frame,
            text="文件信息",
            font=(self.font[0], self.font[1] + 1, "bold"),
            text_color="#1E90FF" if self.theme_mode == "light" else "#4A9EFF",
        )
        file_info_title.pack(pady=(15, 10))

        # 原文件信息 - 使用更深的颜色以增强视觉效果
        original_frame = ctk.CTkFrame(
            file_frame, fg_color="#E0E0E0" if self.theme_mode == "light" else "#2A2A2A"
        )
        original_frame.pack(fill="x", padx=20, pady=8)

        # 原文件标题行 - 使用transparent颜色移除背景
        original_title_frame = ctk.CTkFrame(original_frame, fg_color="transparent")
        original_title_frame.pack(fill="x", padx=10, pady=(10, 5))

        original_title = ctk.CTkLabel(
            original_title_frame,
            text="原文件:",
            font=(self.font[0], self.font[1], "bold"),
            anchor="w",
        )
        original_title.pack(fill="x", side="left")

        # 原文件名
        original_name = ctk.CTkLabel(
            original_frame,
            text=os.path.basename(self.file_path),
            font=self.font,
            anchor="w",
        )
        original_name.pack(fill="x", padx=20, pady=(0, 5))

        # 原文件信息行 - 使用transparent颜色移除背景
        original_info_frame = ctk.CTkFrame(original_frame, fg_color="transparent")
        original_info_frame.pack(fill="x", padx=10, pady=(0, 10))

        # 修改时间
        original_time = ctk.CTkLabel(
            original_info_frame,
            text=f"修改时间: {self.original_mtime}",
            font=(self.font[0], self.font[1] - 1),
            text_color="gray60",
            anchor="w",
        )
        original_time.pack(fill="x", side="left", expand=True, padx=(0, 10))

        # 文件大小
        original_size = ctk.CTkLabel(
            original_info_frame,
            text=f"大小: {self.original_size}",
            font=(self.font[0], self.font[1] - 1),
            text_color="gray60",
            anchor="e",
        )
        original_size.pack(fill="x", side="right", expand=True, padx=(10, 0))

        # 备份文件信息 - 使用更深的颜色以增强视觉效果
        backup_frame = ctk.CTkFrame(
            file_frame, fg_color="#E0E0E0" if self.theme_mode == "light" else "#2A2A2A"
        )
        backup_frame.pack(fill="x", padx=20, pady=8)

        # 备份文件标题行 - 使用transparent颜色移除背景
        backup_title_frame = ctk.CTkFrame(backup_frame, fg_color="transparent")
        backup_title_frame.pack(fill="x", padx=10, pady=(10, 5))

        backup_title = ctk.CTkLabel(
            backup_title_frame,
            text="备份文件:",
            font=(self.font[0], self.font[1], "bold"),
            anchor="w",
        )
        backup_title.pack(fill="x", side="left")

        # 备份文件名
        backup_name = ctk.CTkLabel(
            backup_frame,
            text=os.path.basename(self.backup_path),
            font=self.font,
            anchor="w",
        )
        backup_name.pack(fill="x", padx=20, pady=(0, 5))

        # 备份文件信息行 - 使用transparent颜色移除背景
        backup_info_frame = ctk.CTkFrame(backup_frame, fg_color="transparent")
        backup_info_frame.pack(fill="x", padx=10, pady=(0, 10))

        # 修改时间
        backup_time = ctk.CTkLabel(
            backup_info_frame,
            text=f"修改时间: {self.backup_mtime}",
            font=(self.font[0], self.font[1] - 1),
            text_color="gray60",
            anchor="w",
        )
        backup_time.pack(fill="x", side="left", expand=True, padx=(0, 10))

        # 文件大小
        backup_size = ctk.CTkLabel(
            backup_info_frame,
            text=f"大小: {self.backup_size}",
            font=(self.font[0], self.font[1] - 1),
            text_color="gray60",
            anchor="e",
        )
        backup_size.pack(fill="x", side="right", expand=True, padx=(10, 0))

        # 按钮框架 - 使用transparent颜色移除背景
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=20)

        # 第一行按钮 - 使用transparent颜色移除背景
        button_row1 = ctk.CTkFrame(button_frame, fg_color="transparent")
        button_row1.pack(fill="x", pady=5)

        # 从源文件打开按钮
        open_original_btn = ctk.CTkButton(
            button_row1,
            text="从源文件打开",
            command=self._open_original,
            width=180,
            height=35,
            font=self.font,
        )
        open_original_btn.pack(side="left", padx=8, expand=True)

        # 从备份文件打开按钮
        open_backup_btn = ctk.CTkButton(
            button_row1,
            text="从备份文件打开",
            command=self._open_backup,
            width=180,
            height=35,
            font=self.font,
        )
        open_backup_btn.pack(side="left", padx=8, expand=True)

        # 第二行按钮 - 使用transparent颜色移除背景
        button_row2 = ctk.CTkFrame(button_frame, fg_color="transparent")
        button_row2.pack(fill="x", pady=5)

        # 从源文件打开并删除备份按钮
        open_original_del_btn = ctk.CTkButton(
            button_row2,
            text="从源文件打开并删除备份",
            command=self._open_original_delete_backup,
            width=180,
            height=35,
            font=self.font,
            fg_color="#FF6B6B",
            hover_color="#FF5252",
        )
        open_original_del_btn.pack(side="left", padx=8, expand=True)

        # 从备份文件打开并重命名按钮
        open_backup_rename_btn = ctk.CTkButton(
            button_row2,
            text="从备份文件打开并重命名",
            command=self._open_backup_rename,
            width=180,
            height=35,
            font=self.font,
            fg_color="#4ECDC4",
            hover_color="#3DBBB3",
        )
        open_backup_rename_btn.pack(side="left", padx=8, expand=True)

        # 取消按钮
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="取消",
            command=self._cancel,
            width=100,
            height=35,
            font=self.font,
            fg_color="gray60",
            hover_color="gray50",
        )
        cancel_btn.pack(pady=8)

    def _open_original(self):
        """从源文件打开"""
        self.result["action"] = BackupActions.OPEN_ORIGINAL
        self.dialog.destroy()

    def _open_backup(self):
        """从备份文件打开"""
        self.result["action"] = BackupActions.OPEN_BACKUP
        self.dialog.destroy()

    def _open_original_delete_backup(self):
        """从源文件打开并删除备份"""
        self.result["action"] = BackupActions.OPEN_ORIGINAL_DELETE_BACKUP
        self.dialog.destroy()

    def _open_backup_rename(self):
        """从备份文件打开并重命名为原文件"""
        self.result["action"] = BackupActions.OPEN_BACKUP_RENAME
        self.dialog.destroy()

    def _cancel(self):
        """取消操作"""
        self.result["action"] = BackupActions.CANCEL
        self.dialog.destroy()


def show_simple_backup_dialog(parent, file_path, backup_path):
    """
    显示简化的备份恢复对话框

    Args:
        parent: 父窗口
        file_path: 原文件路径
        backup_path: 备份文件路径

    Returns:
        dict: 用户选择的结果，包含action字段
    """
    dialog = SimpleBackupDialog(parent, file_path, backup_path)
    return dialog.result
