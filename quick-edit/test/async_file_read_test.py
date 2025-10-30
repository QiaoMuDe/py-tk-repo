#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
异步文件读取功能测试脚本
"""

import tkinter as tk
from tkinter import ttk
import os
import sys
import threading
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import center_window, format_file_size

class AsyncFileReaderTest:
    def __init__(self, root):
        self.root = root
        self.root.title("异步文件读取测试")
        center_window(self.root, 600, 400)
        
        # 测试文件路径
        self.test_file_path = "large_test_file.txt"
        
        self.create_widgets()
        
    def create_widgets(self):
        """创建界面控件"""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="异步文件读取功能测试", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 文件大小输入
        size_frame = ttk.Frame(main_frame)
        size_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(size_frame, text="测试文件大小 (MB):").pack(side=tk.LEFT)
        self.size_var = tk.StringVar(value="5")
        size_entry = ttk.Entry(size_frame, textvariable=self.size_var, width=10)
        size_entry.pack(side=tk.LEFT, padx=10)
        
        # 创建文件按钮
        self.create_btn = ttk.Button(main_frame, text="创建测试文件", command=self.create_test_file)
        self.create_btn.pack(pady=10)
        
        # 文件信息显示
        self.info_text = tk.Text(main_frame, height=8, width=70)
        self.info_text.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(self.info_text, command=self.info_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text.config(yscrollcommand=scrollbar.set)
        
        # 测试按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.test_sync_btn = ttk.Button(button_frame, text="同步读取测试", command=self.test_sync_read)
        self.test_sync_btn.pack(side=tk.LEFT, padx=5)
        
        self.test_async_btn = ttk.Button(button_frame, text="异步读取测试", command=self.test_async_read)
        self.test_async_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(button_frame, text="清除文件", command=self.clear_test_file)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=10)
        
        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.pack()
        
    def log_message(self, message):
        """记录消息到文本框"""
        self.info_text.insert(tk.END, f"{message}\n")
        self.info_text.see(tk.END)
        self.root.update_idletasks()
        
    def create_test_file(self):
        """创建测试文件"""
        try:
            size_mb = int(self.size_var.get())
            size_bytes = size_mb * 1024 * 1024
            
            self.status_var.set(f"正在创建 {size_mb}MB 测试文件...")
            self.progress.start()
            self.root.update_idletasks()
            
            # 创建测试内容（重复的文本行）
            line_content = "这是测试文件的一行内容，用于测试大文件读取性能。\n"
            lines_needed = size_bytes // len(line_content)
            
            with open(self.test_file_path, "w", encoding="utf-8") as f:
                for i in range(lines_needed):
                    f.write(f"{line_content}")
                    
            file_size = os.path.getsize(self.test_file_path)
            self.log_message(f"测试文件创建成功: {self.test_file_path}")
            self.log_message(f"文件大小: {format_file_size(file_size)}")
            
            self.status_var.set("测试文件创建完成")
            self.progress.stop()
            
        except Exception as e:
            self.log_message(f"创建测试文件时出错: {str(e)}")
            self.status_var.set("创建文件失败")
            self.progress.stop()
            
    def test_sync_read(self):
        """测试同步文件读取"""
        if not os.path.exists(self.test_file_path):
            self.log_message("请先创建测试文件")
            return
            
        self.status_var.set("正在同步读取文件...")
        self.progress.start()
        self.root.update_idletasks()
        
        start_time = time.time()
        try:
            with open(self.test_file_path, "r", encoding="utf-8") as f:
                content = f.read()
            end_time = time.time()
            
            read_time = end_time - start_time
            self.log_message(f"同步读取完成，耗时: {read_time:.4f} 秒")
            self.log_message(f"读取内容大小: {format_file_size(len(content.encode('utf-8')))}")
            
        except Exception as e:
            self.log_message(f"同步读取时出错: {str(e)}")
        finally:
            self.status_var.set("同步读取完成")
            self.progress.stop()
            
    def async_read_worker(self):
        """异步读取工作线程"""
        start_time = time.time()
        try:
            content_chunks = []
            chunk_size = 8192
            
            with open(self.test_file_path, "r", encoding="utf-8") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    content_chunks.append(chunk)
                    
            content = ''.join(content_chunks)
            end_time = time.time()
            
            read_time = end_time - start_time
            # 在主线程中更新UI
            self.root.after(0, self.on_async_read_complete, read_time, len(content.encode('utf-8')))
            
        except Exception as e:
            self.root.after(0, self.on_async_read_error, str(e))
            
    def on_async_read_complete(self, read_time, content_size):
        """异步读取完成回调"""
        self.log_message(f"异步读取完成，耗时: {read_time:.4f} 秒")
        self.log_message(f"读取内容大小: {format_file_size(content_size)}")
        self.status_var.set("异步读取完成")
        self.progress.stop()
        
    def on_async_read_error(self, error_message):
        """异步读取出错回调"""
        self.log_message(f"异步读取时出错: {error_message}")
        self.status_var.set("异步读取失败")
        self.progress.stop()
            
    def test_async_read(self):
        """测试异步文件读取"""
        if not os.path.exists(self.test_file_path):
            self.log_message("请先创建测试文件")
            return
            
        self.status_var.set("正在异步读取文件...")
        self.progress.start()
        self.root.update_idletasks()
        
        # 在新线程中读取文件
        thread = threading.Thread(target=self.async_read_worker, daemon=True)
        thread.start()
        
    def clear_test_file(self):
        """清除测试文件"""
        if os.path.exists(self.test_file_path):
            try:
                os.remove(self.test_file_path)
                self.log_message("测试文件已清除")
                self.status_var.set("测试文件已清除")
            except Exception as e:
                self.log_message(f"清除测试文件时出错: {str(e)}")
        else:
            self.log_message("测试文件不存在")

def main():
    root = tk.Tk()
    app = AsyncFileReaderTest(root)
    root.mainloop()

if __name__ == "__main__":
    main()