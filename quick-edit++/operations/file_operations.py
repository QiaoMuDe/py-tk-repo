"""
文件操作相关的业务逻辑处理
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from customtkinter import CTk

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config_manager import config_manager
from .file_operation_core import FileOperationCore


class FileOperations:
    """处理文件操作相关的业务逻辑"""
    
    def __init__(self, root: CTk, editor_instance):
        """
        初始化文件操作处理器
        
        Args:
            root: 主窗口实例
            editor_instance: 编辑器实例，用于更新UI
        """
        self.root = root
        self.editor = editor_instance
        self.config_manager = config_manager
        self.file_core = FileOperationCore()  # 初始化文件操作核心
        
    def open_file(self):
        """打开文件并加载到编辑器"""
        # 检查是否需要保存当前文件
        if not self.check_save_before_close():
            return  # 用户取消了操作
            
        try:
            # 获取配置的最大文件大小
            max_file_size = self.config_manager.get("max_file_size", 10) * 1024 * 1024  # 转换为字节
            
            # 打开文件选择对话框
            file_path = filedialog.askopenfilename(
                title="选择文件",
                filetypes=[
                    ("文本文件", "*.txt"),
                    ("Python文件", "*.py"),
                    ("所有文件", "*.*")
                ]
            )
            
            if not file_path:
                return  # 用户取消了选择
            
            # 使用核心类异步读取文件
            self.file_core.async_read_file(
                file_path=file_path,
                callback=self._on_file_read_complete,
                error_callback=self._on_file_read_error,
                max_file_size=max_file_size
            )
            
        except Exception as e:
            messagebox.showerror("错误", f"打开文件时出错: {str(e)}")
    
    def _on_file_read_complete(self, file_path, content, encoding, line_ending):
        """文件读取完成回调"""
        try:
            # 更新编辑器内容
            self.editor.text_area.delete("1.0", tk.END)
            self.editor.text_area.insert("1.0", content)
            
            # 保存当前文件路径到编辑器实例
            self.editor.current_file_path = file_path
            self.editor.current_encoding = encoding
            self.editor.current_line_ending = line_ending
            
            # 重置修改状态
            self.editor.is_modified = False  # 清除修改状态标志
            self.editor.is_new_file = False  # 清除新文件状态标志
            
            # 更新状态栏文件信息
            file_name = os.path.basename(file_path)
            self.editor.status_bar.set_file_info(
                filename=file_name, # 显示文件名
                encoding=encoding, # 显示编码
                line_ending=line_ending # 显示换行符类型
            )
            
            # 更新状态栏
            self.editor.status_bar.set_status_info(f"已打开: {file_name}")
            
            # 更新窗口标题
            self.editor._update_window_title()
            
        except Exception as e:
            messagebox.showerror("错误", f"处理文件内容时出错: {str(e)}")
    
    def _on_file_read_error(self, error_message):
        """文件读取错误回调"""
        messagebox.showerror("错误", f"无法打开文件: {error_message}")
    
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
                messagebox.showinfo("提示", "配置文件不存在，将在首次修改设置时自动创建")
                return
            
            # 获取配置的最大文件大小
            max_file_size = self.config_manager.get("max_file_size", 10) * 1024 * 1024  # 转换为字节
            
            # 直接使用配置文件路径，不显示文件选择对话框
            file_path = CONFIG_PATH
            
            # 使用核心类异步读取文件
            self.file_core.async_read_file(
                file_path=file_path,
                callback=self._on_file_read_complete,
                error_callback=self._on_file_read_error,
                max_file_size=max_file_size
            )
            
        except Exception as e:
            messagebox.showerror("错误", f"打开配置文件时出错: {str(e)}")
    
    def save_file(self):
        """保存当前文件"""
        # 获取文本框内容
        content = self.editor.text_area.get("1.0", tk.END).strip()
        
        # 检查是否有文件路径
        has_file_path = hasattr(self.editor, 'current_file_path') and self.editor.current_file_path
        
        # 情况1：没有打开文件且文本框没有内容
        if not has_file_path and not content:
            from tkinter import messagebox
            messagebox.showinfo("提示", "没有内容可保存")
            return False
            
        # 情况2：已经打开文件，检查是否修改
        if has_file_path and not self.editor.is_modified:
            from tkinter import messagebox
            messagebox.showinfo("提示", "文件未修改，无需保存")
            return True
            
        if not self.editor.current_file_path:
            # 如果没有当前文件路径，则执行另存为
            return self.save_file_as()
        
        try:
            # 获取编辑器内容
            content = self.editor.text_area.get("1.0", tk.END).rstrip('\n')
            
            # 获取当前编码和换行符设置
            encoding = getattr(self.editor, 'current_encoding', 'UTF-8')
            # 优先使用编辑器的当前换行符设置，如果没有则使用配置中的默认换行符
            line_ending = getattr(self.editor, 'current_line_ending', self.config_manager.get("app.default_line_ending", "LF"))
            
            # 使用核心类转换换行符格式
            content = self.file_core.convert_line_endings(content, line_ending)
            
            # 写入文件
            with open(self.editor.current_file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            # 更新状态栏
            self.editor.status_bar.set_status_info("文件已保存")
            
            # 更新状态栏文件信息（包括换行符）
            if self.editor.current_file_path:
                file_name = os.path.basename(self.editor.current_file_path)
                self.editor.status_bar.set_file_info(
                    filename=file_name,
                    encoding=encoding,
                    line_ending=line_ending  # 确保状态栏显示正确的换行符
                )
            
            # 重置修改状态
            self.editor.is_modified = False  # 清除修改状态标志
            self.editor.is_new_file = False  # 清除新文件状态标志
            
            # 更新窗口标题
            self.editor._update_window_title()
            
            return True
            
        except Exception as e:
            messagebox.showerror("错误", f"保存文件时出错: {str(e)}")
            return False
    
    def save_file_as(self):
        """另存为文件"""
        # 获取文本框内容
        content = self.editor.text_area.get("1.0", tk.END).strip()
        
        # 检查是否有文件路径
        has_file_path = hasattr(self.editor, 'current_file_path') and self.editor.current_file_path
        
        # 情况1：没有打开文件且文本框没有内容
        if not has_file_path and not content:
            from tkinter import messagebox
            messagebox.showinfo("提示", "没有内容可保存")
            return False
            
        # 情况2：已经打开文件，检查是否修改
        if has_file_path and not self.editor.is_modified:
            from tkinter import messagebox
            messagebox.showinfo("提示", "文件未修改，无需保存")
            return True
            
        try:
            # 打开另存为对话框
            file_path = filedialog.asksaveasfilename(
                title="另存为",
                defaultextension=".txt",
                filetypes=[
                    ("文本文件", "*.txt"),
                    ("Python文件", "*.py"),
                    ("所有文件", "*.*")
                ]
            )
            
            if not file_path:
                return False  # 用户取消了选择
            
            # 获取编辑器内容
            content = self.editor.text_area.get("1.0", tk.END).rstrip('\n')
            
            # 获取当前编码和换行符设置
            encoding = getattr(self.editor, 'current_encoding', 'UTF-8')
            # 优先使用编辑器的当前换行符设置，如果没有则使用配置中的默认换行符
            line_ending = getattr(self.editor, 'current_line_ending', self.config_manager.get("app.default_line_ending", "LF"))
            
            # 使用核心类转换换行符格式
            content = self.file_core.convert_line_endings(content, line_ending)
            
            # 写入文件
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            # 保存当前文件路径到编辑器实例
            self.editor.current_file_path = file_path
            self.editor.current_encoding = encoding
            self.editor.current_line_ending = line_ending
            
            # 重置修改状态
            self.editor.is_modified = False  # 清除修改状态标志
            self.editor.is_new_file = False  # 清除新文件状态标志
            
            # 更新状态栏文件信息
            file_name = os.path.basename(file_path)
            self.editor.status_bar.set_file_info(
                filename=file_name,
                encoding=encoding,
                line_ending=line_ending  # 确保状态栏显示正确的换行符
            )
            
            # 更新状态栏
            self.editor.status_bar.set_status_info("文件已保存")
            
            # 更新窗口标题
            self.editor._update_window_title()
            
            return True
            
        except Exception as e:
            messagebox.showerror("错误", f"另存为文件时出错: {str(e)}")
            return False
    
    def new_file(self):
        """创建新文件"""
        # 检查是否需要保存当前文件
        if not self.check_save_before_close():
            return  # 用户取消了操作
            
        # 关闭当前文件
        self.close_file()
        
        # 设置新文件状态标志
        self.editor.is_new_file = True
        
        # 获取配置中的默认换行符和编码
        default_line_ending = self.config_manager.get("app.default_line_ending", "LF")
        default_encoding = self.config_manager.get("app.default_encoding", "UTF-8")
        
        # 更新编辑器的当前换行符和编码
        self.editor.current_line_ending = default_line_ending
        self.editor.current_encoding = default_encoding
        
        # 更新状态栏为新文件状态
        self.editor.status_bar.set_status_info("新文件")
        self.editor.status_bar.set_file_info(
            filename="新文件",
            encoding=default_encoding,
            line_ending=default_line_ending  # 确保状态栏显示默认换行符
        )
        
        # 更新窗口标题为新文件
        self.editor.title("新文件 - QuickEdit++")
    
    def close_file(self):
        """关闭当前文件，重置窗口和状态栏状态"""
        # 检查是否需要保存当前文件
        if not self.check_save_before_close():
            return  # 用户取消了操作
            
        # 清空编辑器内容
        self.editor.text_area.delete("1.0", tk.END)
        
        # 获取配置中的默认换行符和编码
        default_line_ending = self.config_manager.get("app.default_line_ending", "LF")
        default_encoding = self.config_manager.get("app.default_encoding", "UTF-8")
        
        # 重置文件相关属性
        self.editor.current_file_path = None
        self.editor.current_encoding = default_encoding  # 重置为配置中的默认编码
        self.editor.current_line_ending = default_line_ending  # 重置为配置中的默认换行符
        self.editor.is_modified = False
        self.editor.is_new_file = False  # 清除新文件状态标志
        
        # 更新状态栏
        self.editor.status_bar.set_status_info("就绪")
        # 重置状态栏右侧文件信息，传递空字符串作为文件名，这样会显示默认的编码和换行符
        self.editor.status_bar.set_file_info(filename="", encoding=default_encoding, line_ending=default_line_ending)
        
        # 更新窗口标题
        self.editor._update_window_title()
        
    def check_save_before_close(self):
        """在关闭文件前检查是否需要保存
        
        Returns:
            bool: 如果可以继续关闭操作返回True，如果用户取消则返回False
        """
        # 如果文件未修改，直接返回True
        if not self.editor.is_modified:
            return True
            
        # 如果文件已修改，提示用户
        from tkinter import messagebox
        result = messagebox.askyesnocancel(
            "未保存的更改",
            "当前文件有未保存的更改，是否保存？"
        )
        
        if result is True:  # 用户选择保存
            return self.save_file()
        elif result is False:  # 用户选择不保存
            return True
        else:  # 用户选择取消
            return False