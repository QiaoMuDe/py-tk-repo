"""
简化的备份恢复对话框
"""

import os
import tkinter as tk
from tkinter import messagebox
from datetime import datetime


class SimpleBackupDialog:
    """简化的备份恢复对话框"""
    
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
        
        # 创建对话框窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("发现备份文件")
        self.dialog.geometry("500x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示对话框
        self._center_dialog()
        
        # 创建UI
        self._create_widgets()
        
        # 等待对话框关闭
        self.dialog.wait_window()
    
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
    
    def _center_dialog(self):
        """将对话框居中显示"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """创建对话框组件"""
        # 标题
        title_label = tk.Label(
            self.dialog, 
            text="发现备份文件", 
            font=("Arial", 12, "bold")
        )
        title_label.pack(pady=10)
        
        # 提示信息
        info_label = tk.Label(
            self.dialog, 
            text=f"在文件 {os.path.basename(self.file_path)} 所在目录发现了备份文件",
            wraplength=450
        )
        info_label.pack(pady=5)
        
        # 文件信息框架
        file_frame = tk.LabelFrame(self.dialog, text="文件信息", padx=10, pady=10)
        file_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # 原文件信息
        original_label = tk.Label(
            file_frame, 
            text=f"原文件: {os.path.basename(self.file_path)}\n修改时间: {self.original_mtime}",
            justify="left",
            anchor="w"
        )
        original_label.pack(fill="x", pady=5)
        
        # 备份文件信息
        backup_label = tk.Label(
            file_frame, 
            text=f"备份文件: {os.path.basename(self.backup_path)}\n修改时间: {self.backup_mtime}",
            justify="left",
            anchor="w"
        )
        backup_label.pack(fill="x", pady=5)
        
        # 按钮框架
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        # 第一行按钮
        button_row1 = tk.Frame(button_frame)
        button_row1.pack(fill="x", pady=5)
        
        # 从源文件打开按钮
        open_original_btn = tk.Button(
            button_row1, 
            text="从源文件打开",
            command=self._open_original,
            width=15
        )
        open_original_btn.pack(side="left", padx=5)
        
        # 从备份文件打开按钮
        open_backup_btn = tk.Button(
            button_row1, 
            text="从备份文件打开",
            command=self._open_backup,
            width=15
        )
        open_backup_btn.pack(side="left", padx=5)
        
        # 第二行按钮
        button_row2 = tk.Frame(button_frame)
        button_row2.pack(fill="x", pady=5)
        
        # 从源文件打开并删除备份按钮
        open_original_del_btn = tk.Button(
            button_row2, 
            text="从源文件打开并删除备份",
            command=self._open_original_delete_backup,
            width=20
        )
        open_original_del_btn.pack(side="left", padx=5)
        
        # 从备份文件打开并重命名按钮
        open_backup_rename_btn = tk.Button(
            button_row2, 
            text="从备份文件打开并重命名",
            command=self._open_backup_rename,
            width=20
        )
        open_backup_rename_btn.pack(side="left", padx=5)
        
        # 第三行按钮
        button_row3 = tk.Frame(button_frame)
        button_row3.pack(fill="x", pady=5)
        
        # 取消按钮
        cancel_btn = tk.Button(
            button_row3, 
            text="取消",
            command=self._cancel,
            width=10
        )
        cancel_btn.pack(side="right", padx=5)
    
    def _open_original(self):
        """从源文件打开"""
        self.result["action"] = "open_original"
        self.dialog.destroy()
    
    def _open_backup(self):
        """从备份文件打开"""
        self.result["action"] = "open_backup"
        self.dialog.destroy()
    
    def _open_original_delete_backup(self):
        """从源文件打开并删除备份"""
        self.result["action"] = "open_original_delete_backup"
        self.dialog.destroy()
    
    def _open_backup_rename(self):
        """从备份文件打开并重命名为原文件"""
        self.result["action"] = "open_backup_rename"
        self.dialog.destroy()
    
    def _cancel(self):
        """取消操作"""
        self.result["action"] = "cancel"
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