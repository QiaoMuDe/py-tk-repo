"""
打包过程标签页模块
提供打包过程的显示和控制界面
"""

import tkinter as tk
import threading
import subprocess
import queue
import time
import os
import sys
from tkinter import messagebox, scrolledtext
import customtkinter as ctk
from core.pack_executor import PackExecutor
from core.pyinstaller_config import PyInstallerConfig


class ProcessTab:
    """打包过程标签页类"""

    def __init__(self, parent, main_window, font_family="Microsoft YaHei UI"):
        """初始化打包过程标签页

        Args:
            parent: 父容器
            main_window: 主窗口引用
            font_family: 字体族名称
        """
        self.parent = parent
        self.main_window = main_window
        self.font_family = font_family

        # 设置字体
        self.default_font = ctk.CTkFont(family=self.font_family, size=12)
        self.title_font = ctk.CTkFont(family=self.font_family, size=14, weight="bold")
        self.output_font = ctk.CTkFont(family=self.font_family, size=10)

        # 设置统一的颜色样式
        self.bg_color = "#F8FAFC"  # 主背景色
        self.card_bg_color = "#F9FAFB"  # 卡片背景色
        self.card_border_color = "#E5E7EB"  # 卡片边框色
        self.accent_color = "#3B82F6"  # 强调色
        self.text_color = "#1F2937"  # 文本颜色
        self.text_secondary_color = "#6B7280"  # 次要文本颜色

        # 进程相关变量
        self.process = None
        self.output_queue = queue.Queue()
        self.is_running = False

        # 初始化打包执行器
        self.executor = PackExecutor()
        self.executor.set_output_callback(self.append_output)
        self.executor.set_status_callback(self.update_status)
        self.executor.set_finish_callback(self.on_build_finished)
        self.executor.set_lock_tab_callback(self.lock_tabs)

        # 创建界面
        self.create_ui()

        # 启动输出队列监控
        self.monitor_output_queue()

    def create_ui(self):
        """创建用户界面"""
        # 创建主容器，使用浅色背景
        self.main_container = ctk.CTkFrame(
            self.parent, fg_color=self.bg_color, corner_radius=0
        )
        self.main_container.pack(fill="both", expand=True, padx=0, pady=0)

        # 创建顶部信息框架
        self.create_info_frame()

        # 创建输出文本框
        self.create_output_frame()

        # 创建控制按钮框架
        self.create_button_frame()

    def create_info_frame(self):
        """创建顶部信息框架"""
        # 创建信息卡片
        self.info_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="#FFFFFF",
            corner_radius=10,
            border_width=1,
            border_color=self.card_border_color,
        )
        self.info_frame.pack(fill="x", padx=15, pady=(15, 10))

        # 当前操作标签
        self.operation_label = ctk.CTkLabel(
            self.info_frame,
            text="当前操作: 无",
            font=self.title_font,
            text_color=self.text_color,
        )
        self.operation_label.pack(side="left", padx=15, pady=15)

        # 状态标签
        self.status_label = ctk.CTkLabel(
            self.info_frame,
            text="状态: 就绪",
            font=self.default_font,
            text_color=self.text_secondary_color,
        )
        self.status_label.pack(side="right", padx=15, pady=15)

    def create_output_frame(self):
        """创建输出文本框框架"""
        # 创建输出区域卡片
        self.output_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="#FFFFFF",
            corner_radius=10,
            border_width=1,
            border_color=self.card_border_color,
        )
        self.output_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # 输出文本框标题
        output_title = ctk.CTkLabel(
            self.output_frame,
            text="打包输出:",
            font=ctk.CTkFont(family=self.font_family, size=16, weight="bold"),
            text_color=self.text_color,
        )
        output_title.pack(anchor="w", padx=15, pady=(15, 10))

        # 输出文本框
        self.output_text = ctk.CTkTextbox(
            self.output_frame,
            wrap="none",
            font=self.output_font,
            fg_color="#F8FAFC",
            border_width=1,
            border_color=self.card_border_color,
            corner_radius=6,
        )
        self.output_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def create_button_frame(self):
        """创建控制按钮框架"""
        # 创建按钮区域卡片
        self.button_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="#FFFFFF",
            corner_radius=10,
            border_width=1,
            border_color=self.card_border_color,
        )
        self.button_frame.pack(fill="x", padx=15, pady=(0, 15))

        # 清空输出按钮 - 浅蓝色
        self.clear_btn = ctk.CTkButton(
            self.button_frame,
            text="清空输出",
            command=self.clear_output,
            width=100,
            font=self.default_font,
            fg_color="#3b8ed0",
            hover_color="#2c79b0",
            corner_radius=6,
            height=32,
        )
        self.clear_btn.pack(side="left", padx=15, pady=15)

        # 复制输出按钮 - 浅蓝色
        self.copy_btn = ctk.CTkButton(
            self.button_frame,
            text="复制输出",
            command=self.copy_output,
            width=100,
            font=self.default_font,
            fg_color="#3b8ed0",
            hover_color="#2c79b0",
            corner_radius=6,
            height=32,
        )
        self.copy_btn.pack(side="left", padx=(0, 10), pady=15)

        # 保存日志按钮 - 浅蓝色
        self.save_btn = ctk.CTkButton(
            self.button_frame,
            text="保存日志",
            command=self.save_log,
            width=100,
            font=self.default_font,
            fg_color="#3b8ed0",
            hover_color="#2c79b0",
            corner_radius=6,
            height=32,
        )
        self.save_btn.pack(side="left", padx=10, pady=15)

        # 打开输出目录按钮 - 绿色
        self.open_output_btn = ctk.CTkButton(
            self.button_frame,
            text="打开输出目录",
            command=self.open_output_directory,
            width=150,
            font=self.default_font,
            fg_color="#4CAF50",
            hover_color="#3d8b40",
            corner_radius=6,
            height=32,
        )
        self.open_output_btn.pack(side="left", padx=10, pady=15)

        # 停止打包按钮 - 红色
        self.stop_btn = ctk.CTkButton(
            self.button_frame,
            text="停止打包",
            command=self.stop_build,
            width=100,
            font=self.default_font,
            fg_color="#EF4444",
            hover_color="#DC2626",
            corner_radius=6,
            height=32,
            state="disabled",
        )
        self.stop_btn.pack(side="right", padx=15, pady=15)

    def append_output(self, text: str):
        """添加输出文本到输出框

        Args:
            text: 要添加的文本
        """
        self.output_queue.put(text)

    def lock_tabs(self, locked: bool):
        """锁定或解锁标签页切换

        Args:
            locked: 是否锁定
        """
        if locked:
            # 禁用所有标签页按钮
            for tab_info in self.main_window.tabs.values():
                tab_info["button"].configure(state="disabled")
        else:
            # 启用所有标签页按钮
            for tab_info in self.main_window.tabs.values():
                tab_info["button"].configure(state="normal")

    def on_build_finished(self, success: bool, message: str):
        """打包完成回调

        Args:
            success: 是否成功
            message: 完成消息
        """
        if success:
            self.update_operation("打包成功")
            messagebox.showinfo("成功", message)
        else:
            self.update_operation("打包失败")
            messagebox.showerror("错误", message)

        # 启用停止按钮
        self.stop_btn.configure(state="disabled")
        self.is_running = False

    def start_pyinstaller_build(self, config: PyInstallerConfig):
        """开始PyInstaller打包

        Args:
            config: PyInstaller配置对象
        """
        self.update_operation("PyInstaller打包")
        self.update_status("准备中")
        self.clear_output()

        # 使用执行器执行命令
        self.is_running = True
        self.stop_btn.configure(state="normal")

        # 执行打包命令
        self.executor.execute(config)

    def start_nuitka_build(self, config):
        """开始Nuitka打包

        Args:
            config: Nuitka配置对象
        """
        self.update_operation("Nuitka打包")
        self.update_status("准备中")
        self.clear_output()

        # 使用执行器执行命令
        self.is_running = True
        self.stop_btn.configure(state="normal")

        # 执行打包命令
        self.executor.execute(config)

    def run_build_command(self, cmd, tool_name):
        """执行打包命令

        Args:
            cmd: 要执行的命令
            tool_name: 工具名称
        """
        try:
            # 记录开始时间
            start_time = time.time()

            # 输出命令信息
            self.output_queue.put(f"开始执行 {tool_name} 打包命令...\n")
            self.output_queue.put(f"命令: {' '.join(cmd)}\n")
            self.output_queue.put(f"工作目录: {os.getcwd()}\n")
            self.output_queue.put("-" * 50 + "\n")

            # 执行命令
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
            )

            # 读取输出
            for line in self.process.stdout:
                self.output_queue.put(line)

            # 等待进程结束
            self.process.wait()
            exit_code = self.process.returncode

            # 记录结束时间
            end_time = time.time()
            elapsed_time = end_time - start_time

            # 输出结果信息
            self.output_queue.put("-" * 50 + "\n")

            if exit_code == 0:
                self.output_queue.put(f"{tool_name} 打包成功完成!\n")
                self.output_queue.put(f"耗时: {elapsed_time:.2f} 秒\n")
                self.output_queue.put(f"退出代码: {exit_code}\n")

                # 在主线程中更新状态
                self.output_queue.put(("status", "完成"))
                self.output_queue.put(("success", f"{tool_name} 打包成功完成!"))
            else:
                self.output_queue.put(f"{tool_name} 打包失败!\n")
                self.output_queue.put(f"耗时: {elapsed_time:.2f} 秒\n")
                self.output_queue.put(f"退出代码: {exit_code}\n")

                # 在主线程中更新状态
                self.output_queue.put(("status", "失败"))
                self.output_queue.put(("error", f"{tool_name} 打包失败!"))

        except Exception as e:
            self.output_queue.put(f"执行 {tool_name} 打包命令时出错: {str(e)}\n")
            self.output_queue.put(("status", "错误"))
            self.output_queue.put(
                ("error", f"执行 {tool_name} 打包命令时出错: {str(e)}")
            )
        finally:
            self.is_running = False
            self.output_queue.put(("stop", None))

    def monitor_output_queue(self):
        """监控输出队列并更新UI"""
        try:
            while True:
                # 从队列获取消息
                item = self.output_queue.get_nowait()

                # 处理不同类型的消息
                if isinstance(item, tuple):
                    # 元组类型的消息是控制命令
                    command, value = item

                    if command == "status":
                        self.update_status(value)
                    elif command == "success":
                        self.update_operation(value)
                        messagebox.showinfo("成功", value)
                    elif command == "error":
                        self.update_operation(value)
                        messagebox.showerror("错误", value)
                    elif command == "stop":
                        self.stop_btn.configure(state="disabled")
                else:
                    # 字符串类型的消息是输出文本
                    self.output_text.insert(tk.END, item)
                    self.output_text.see(tk.END)
        except queue.Empty:
            pass

        # 继续监控
        self.parent.after(100, self.monitor_output_queue)

    def stop_build(self):
        """停止打包过程"""
        if self.executor.is_executing():
            self.executor.stop()
            self.update_operation("打包已停止")
            self.is_running = False
            self.stop_btn.configure(state="disabled")

    def clear_output(self):
        """清空输出"""
        self.output_text.delete("1.0", tk.END)

    def copy_output(self):
        """复制输出到剪贴板"""
        try:
            output = self.output_text.get("1.0", tk.END)
            self.parent.clipboard_clear()
            self.parent.clipboard_append(output)
            messagebox.showinfo("成功", "输出已复制到剪贴板")
        except Exception as e:
            messagebox.showerror("错误", f"复制输出时出错: {str(e)}")

    def save_log(self):
        """保存日志到文件"""
        try:
            from tkinter import filedialog

            file_path = filedialog.asksaveasfilename(
                title="保存日志文件",
                defaultextension=".log",
                filetypes=[
                    ("日志文件", "*.log"),
                    ("文本文件", "*.txt"),
                    ("所有文件", "*.*"),
                ],
            )

            if file_path:
                output = self.output_text.get("1.0", tk.END)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(output)
                messagebox.showinfo("成功", f"日志已保存到: {file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存日志时出错: {str(e)}")

    def update_operation(self, operation):
        """更新当前操作

        Args:
            operation: 操作描述
        """
        self.operation_label.configure(text=f"当前操作: {operation}")

    def update_status(self, status):
        """更新状态

        Args:
            status: 状态描述
        """
        self.status_label.configure(text=f"状态: {status}")

    def open_output_directory(self):
        """打开输出目录"""
        if (
            not hasattr(self.executor, "current_config")
            or self.executor.current_config is None
        ):
            messagebox.showerror("错误", "没有可用的打包配置")
            return

        config = self.executor.current_config
        script_dir = os.path.dirname(os.path.abspath(config.script))

        # 根据配置类型计算输出目录
        if hasattr(config, "mode"):  # Nuitka配置
            # Nuitka的输出目录处理
            if config.output_dir:
                # 如果指定了输出目录，直接使用
                output_dir = config.output_dir

                # 如果有输出文件夹名称，需要考虑它
                if config.output_folder_name:
                    # 对于standalone模式，输出文件夹名称是最终目录的一部分
                    if config.mode == "standalone":
                        output_dir = os.path.join(output_dir, config.output_folder_name)
                    # 对于onefile模式，输出文件名可能包含在output_dir中
                    elif config.mode == "onefile":
                        # onefile模式通常直接输出到output_dir，不需要额外处理
                        pass
            else:
                # 默认输出目录是脚本所在目录
                output_dir = script_dir

                # 如果有输出文件夹名称，需要考虑它
                if config.output_folder_name:
                    output_dir = os.path.join(output_dir, config.output_folder_name)
        else:  # PyInstaller配置
            # PyInstaller的输出目录处理
            if config.output_dir:
                # 如果指定了输出目录，直接使用
                output_dir = config.output_dir
            else:
                # 默认输出目录是脚本所在目录的dist子目录
                output_dir = os.path.join(script_dir, "dist")

        # 确保输出目录是一个目录，而不是文件
        # 如果是文件，取其所在目录
        if os.path.isfile(output_dir):
            output_dir = os.path.dirname(output_dir)

        # 检查目录是否存在
        if not os.path.exists(output_dir):
            messagebox.showerror("错误", f"输出目录不存在: {output_dir}")
            return

        # 打开目录
        try:
            if sys.platform == "win32":
                # Windows系统：使用explorer命令确保打开目录
                subprocess.run(["explorer", output_dir])
            elif sys.platform == "darwin":
                # macOS系统
                subprocess.run(["open", output_dir])
            else:
                # Linux系统
                subprocess.run(["xdg-open", output_dir])
        except Exception as e:
            messagebox.showerror("错误", f"无法打开输出目录: {str(e)}")
