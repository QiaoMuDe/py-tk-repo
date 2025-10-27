#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import subprocess
import os
from datetime import datetime
import json
from pathlib import Path
import threading
import queue


class F2DouyinGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("F2抖音数据采集工具")
        self.root.geometry("1000x800")
        self.root.minsize(800, 600)

        # 工作目录默认为空
        self.working_dir = ""

        # 线程控制变量
        self.command_process = None  # 当前执行的进程
        self.stop_flag = False  # 停止标志

        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.columnconfigure(2, weight=1)
        self.main_frame.columnconfigure(3, weight=1)

        # 创建控件
        self.create_widgets()

        # 在初始化时读取保存的配置（包括Cookie和工作目录）
        self.load_saved_config()

    def create_widgets(self):
        row = 0

        # 工作目录选择
        ttk.Label(self.main_frame, text="工作目录:").grid(
            row=row, column=0, sticky=tk.W, padx=5, pady=5
        )
        self.work_dir_entry = ttk.Entry(self.main_frame, width=60)
        self.work_dir_entry.grid(
            row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        self.work_dir_entry.insert(0, self.working_dir)

        self.select_dir_btn = ttk.Button(
            self.main_frame, text="选择目录", command=self.select_working_directory
        )
        self.select_dir_btn.grid(row=row, column=3, sticky=tk.W, padx=5, pady=5)
        row += 1

        # URL输入
        ttk.Label(self.main_frame, text="URL链接 (-u):").grid(
            row=row, column=0, sticky=tk.W, padx=5, pady=5
        )
        # 使用多行文本框替代单行输入框
        self.url_text = scrolledtext.ScrolledText(
            self.main_frame, width=80, height=3, wrap=tk.WORD
        )
        self.url_text.grid(
            row=row, column=1, columnspan=3, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        row += 1

        # 下载模式
        ttk.Label(self.main_frame, text="下载模式 (-M):").grid(
            row=row, column=0, sticky=tk.W, padx=5, pady=5
        )
        self.mode_combo = ttk.Combobox(
            self.main_frame,
            values=[
                "one - 单个作品",
                "post - 主页作品",
                "like - 点赞作品",
                "collection - 收藏作品",
                "collects - 收藏夹作品",
                "mix - 合集",
                "live - 直播",
            ],
            width=20,
        )
        self.mode_combo.current(0)
        self.mode_combo.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)

        # 显示语言
        ttk.Label(self.main_frame, text="显示语言 (-l):").grid(
            row=row, column=2, sticky=tk.W, padx=5, pady=5
        )
        self.lang_combo = ttk.Combobox(
            self.main_frame, values=["zh_CN", "en_US"], width=15
        )
        self.lang_combo.current(0)
        self.lang_combo.grid(row=row, column=3, sticky=tk.W, padx=5, pady=5)
        row += 1

        # 保存选项
        ttk.Label(self.main_frame, text="保存选项:").grid(
            row=row, column=0, sticky=tk.W, padx=5, pady=5
        )

        self.music_var = tk.BooleanVar()
        self.music_check = ttk.Checkbutton(
            self.main_frame, text="保存视频原声 (-m)", variable=self.music_var
        )
        self.music_check.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)

        self.cover_var = tk.BooleanVar()
        self.cover_check = ttk.Checkbutton(
            self.main_frame, text="保存视频封面 (-v)", variable=self.cover_var
        )
        self.cover_check.grid(row=row, column=2, sticky=tk.W, padx=5, pady=5)

        self.desc_var = tk.BooleanVar()
        self.desc_check = ttk.Checkbutton(
            self.main_frame, text="保存视频文案 (-d)", variable=self.desc_var
        )
        self.desc_check.grid(row=row, column=3, sticky=tk.W, padx=5, pady=5)
        row += 1

        self.folderize_var = tk.BooleanVar()
        self.folderize_check = ttk.Checkbutton(
            self.main_frame, text="单独文件夹保存 (-f)", variable=self.folderize_var
        )
        self.folderize_check.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        row += 1

        # 路径设置
        ttk.Label(self.main_frame, text="保存路径 (-p):").grid(
            row=row, column=0, sticky=tk.W, padx=5, pady=5
        )
        self.path_entry = ttk.Entry(self.main_frame, width=60)
        self.path_entry.grid(
            row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        # 默认保存路径设置为工作目录
        self.path_entry.insert(0, self.working_dir)

        self.select_path_btn = ttk.Button(
            self.main_frame, text="选择路径", command=self.select_save_path
        )
        self.select_path_btn.grid(row=row, column=3, sticky=tk.W, padx=5, pady=5)
        row += 1

        # Cookie
        ttk.Label(self.main_frame, text="Cookie (-k):").grid(
            row=row, column=0, sticky=tk.W, padx=5, pady=5
        )
        # 使用多行文本框替代单行输入框
        self.cookie_text = scrolledtext.ScrolledText(
            self.main_frame, width=80, height=5, wrap=tk.WORD
        )
        self.cookie_text.grid(
            row=row, column=1, columnspan=3, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        row += 1

        # 日期区间
        ttk.Label(self.main_frame, text="日期区间 (-i):").grid(
            row=row, column=0, sticky=tk.W, padx=5, pady=5
        )
        self.interval_entry = ttk.Entry(self.main_frame, width=40)
        self.interval_entry.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        self.interval_entry.insert(0, "all")
        ttk.Label(self.main_frame, text="格式: YYYY-MM-DD|YYYY-MM-DD 或 'all'").grid(
            row=row, column=2, columnspan=2, sticky=tk.W, padx=5, pady=5
        )
        row += 1

        # 网络设置
        ttk.Label(self.main_frame, text="网络设置:").grid(
            row=row, column=0, sticky=tk.W, padx=5, pady=5
        )

        ttk.Label(self.main_frame, text="超时时间 (-e):").grid(
            row=row, column=1, sticky=tk.W, padx=5, pady=5
        )
        self.timeout_entry = ttk.Entry(self.main_frame, width=10)
        self.timeout_entry.grid(row=row, column=1, sticky=tk.E, padx=5, pady=5)
        self.timeout_entry.insert(0, "10")

        ttk.Label(self.main_frame, text="重试次数 (-r):").grid(
            row=row, column=2, sticky=tk.W, padx=5, pady=5
        )
        self.retries_entry = ttk.Entry(self.main_frame, width=10)
        self.retries_entry.grid(row=row, column=2, sticky=tk.E, padx=5, pady=5)
        self.retries_entry.insert(0, "3")

        ttk.Label(self.main_frame, text="并发连接 (-x):").grid(
            row=row, column=3, sticky=tk.W, padx=5, pady=5
        )
        self.connections_entry = ttk.Entry(self.main_frame, width=10)
        self.connections_entry.grid(row=row, column=3, sticky=tk.E, padx=5, pady=5)
        self.connections_entry.insert(0, "5")
        row += 1

        # 任务设置
        ttk.Label(self.main_frame, text="任务设置:").grid(
            row=row, column=0, sticky=tk.W, padx=5, pady=5
        )

        ttk.Label(self.main_frame, text="最大任务数 (-t):").grid(
            row=row, column=1, sticky=tk.W, padx=5, pady=5
        )
        self.tasks_entry = ttk.Entry(self.main_frame, width=10)
        self.tasks_entry.grid(row=row, column=1, sticky=tk.E, padx=5, pady=5)
        self.tasks_entry.insert(0, "10")

        ttk.Label(self.main_frame, text="最大下载数 (-o):").grid(
            row=row, column=2, sticky=tk.W, padx=5, pady=5
        )
        self.counts_entry = ttk.Entry(self.main_frame, width=10)
        self.counts_entry.grid(row=row, column=2, sticky=tk.E, padx=5, pady=5)
        self.counts_entry.insert(0, "0")

        ttk.Label(self.main_frame, text="每页作品数 (-s):").grid(
            row=row, column=3, sticky=tk.W, padx=5, pady=5
        )
        self.page_counts_entry = ttk.Entry(self.main_frame, width=10)
        self.page_counts_entry.grid(row=row, column=3, sticky=tk.E, padx=5, pady=5)
        self.page_counts_entry.insert(0, "20")
        row += 1

        # 输出方式设置
        ttk.Label(self.main_frame, text="输出方式:").grid(
            row=row, column=0, sticky=tk.W, padx=5, pady=5
        )

        self.output_mode_var = tk.StringVar(value="gui")  # 默认在GUI中显示
        self.gui_output_radio = ttk.Radiobutton(
            self.main_frame,
            text="在GUI中显示输出",
            variable=self.output_mode_var,
            value="gui",
        )
        self.gui_output_radio.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)

        self.console_output_radio = ttk.Radiobutton(
            self.main_frame,
            text="在原生窗口显示输出",
            variable=self.output_mode_var,
            value="console",
        )
        self.console_output_radio.grid(row=row, column=2, sticky=tk.W, padx=5, pady=5)
        row += 1

        # 执行按钮和停止按钮
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=row, column=0, columnspan=4, pady=10)

        self.execute_btn = ttk.Button(
            button_frame, text="执行采集", command=self.execute_command
        )
        self.execute_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(
            button_frame,
            text="停止采集",
            command=self.stop_command_execution,
            state=tk.DISABLED,
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        row += 1

        # 输出区域
        ttk.Label(self.main_frame, text="执行输出:").grid(
            row=row, column=0, sticky=tk.W, padx=5, pady=5
        )
        row += 1

        self.output_text = scrolledtext.ScrolledText(
            self.main_frame, width=120, height=20, wrap=tk.WORD
        )
        self.output_text.grid(
            row=row,
            column=0,
            columnspan=4,
            sticky=(tk.W, tk.E, tk.N, tk.S),
            padx=5,
            pady=5,
        )
        self.output_text.config(state=tk.DISABLED)

        # 清空按钮
        self.clear_btn = ttk.Button(
            self.main_frame, text="清空输出", command=self.clear_output
        )
        self.clear_btn.grid(row=row + 1, column=0, sticky=tk.W, padx=5, pady=5)

        # 复制按钮
        self.copy_btn = ttk.Button(
            self.main_frame, text="复制输出", command=self.copy_output
        )
        self.copy_btn.grid(row=row + 1, column=1, sticky=tk.W, padx=5, pady=5)

        # 配置权重
        for i in range(4):
            self.main_frame.columnconfigure(i, weight=1)
        self.main_frame.rowconfigure(row, weight=1)

    def select_working_directory(self):
        """选择工作目录"""
        directory = filedialog.askdirectory()
        if directory:
            self.working_dir = directory
            self.work_dir_entry.delete(0, tk.END)
            self.work_dir_entry.insert(0, directory)
            # 同时更新保存路径为新的工作目录
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, directory)
            # 立即保存工作目录到配置文件
            self.save_config(working_dir_value=directory)

    def select_save_path(self):
        """选择保存路径"""
        directory = filedialog.askdirectory()
        if directory:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, directory)
            # 如果保存路径与工作目录相同，也更新工作目录
            if directory == self.working_dir:
                self.save_config(working_dir_value=directory)

    def append_output(self, text):
        """追加输出文本"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.root.update()

    def clear_output(self):
        """清空输出"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)

    def copy_output(self):
        """复制输出到剪贴板"""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.output_text.get(1.0, tk.END))
        self.append_output("输出已复制到剪贴板")

    def get_config_file_path(self):
        """获取配置文件路径"""
        # 获取用户家目录
        home_dir = Path.home()
        # 创建隐藏文件路径 (.f2_douyin_config.json)
        config_file = home_dir / ".f2_douyin_config.json"
        return config_file

    def save_config(self, cookie_value=None, working_dir_value=None):
        """保存配置到文件"""
        try:
            config_file = self.get_config_file_path()

            # 如果文件存在，先读取现有配置
            config_data = {}
            if config_file.exists():
                try:
                    with open(config_file, "r", encoding="utf-8") as f:
                        config_data = json.load(f)
                except Exception:
                    # 如果读取失败，使用空字典
                    config_data = {}

            # 更新配置数据
            if cookie_value is not None:
                config_data["cookie"] = cookie_value
            if working_dir_value is not None:
                config_data["working_dir"] = working_dir_value
            config_data["updated"] = datetime.now().isoformat()

            # 写入JSON文件
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            # 如果保存失败，不中断程序执行
            print(f"保存配置时出错: {e}")

    def load_saved_config(self):
        """从文件加载保存的配置"""
        try:
            config_file = self.get_config_file_path()
            # 检查文件是否存在
            if config_file.exists():
                # 读取JSON文件
                with open(config_file, "r", encoding="utf-8") as f:
                    config_data = json.load(f)

                # 获取Cookie值并填充到输入框
                cookie_value = config_data.get("cookie", "")
                if cookie_value:
                    self.cookie_text.delete("1.0", tk.END)
                    self.cookie_text.insert("1.0", cookie_value)

                # 获取工作目录值并填充到输入框
                working_dir_value = config_data.get("working_dir", "")
                if working_dir_value:
                    self.working_dir = working_dir_value
                    self.work_dir_entry.delete(0, tk.END)
                    self.work_dir_entry.insert(0, working_dir_value)
                    # 同时更新保存路径为加载的工作目录
                    self.path_entry.delete(0, tk.END)
                    self.path_entry.insert(0, working_dir_value)
        except Exception as e:
            # 如果读取失败，不中断程序执行
            print(f"加载配置时出错: {e}")

    def build_command(self):
        """构建f2命令"""
        command = ["f2", "dy"]

        # URL
        url = self.url_text.get("1.0", tk.END).strip()
        if url:
            command.extend(["-u", url])

        # 下载模式
        mode = self.mode_combo.get()
        # 只传递模式标识符部分，去除解释文本
        mode_identifier = mode.split(" - ")[0] if " - " in mode else mode
        command.extend(["-M", mode_identifier])

        # 显示语言
        lang = self.lang_combo.get()
        command.extend(["-l", lang])

        # 保存选项
        command.extend(["-m", str(self.music_var.get()).lower()])
        command.extend(["-v", str(self.cover_var.get()).lower()])
        command.extend(["-d", str(self.desc_var.get()).lower()])
        command.extend(["-f", str(self.folderize_var.get()).lower()])

        # 保存路径
        path = self.path_entry.get().strip()
        if path:
            command.extend(["-p", path])

        # Cookie
        cookie = self.cookie_text.get("1.0", tk.END).strip()
        if cookie:
            command.extend(["-k", cookie])
            # 保存Cookie
            self.save_config(cookie_value=cookie)

        # 日期区间
        interval = self.interval_entry.get().strip()
        if interval:
            command.extend(["-i", interval])

        # 网络设置
        timeout = self.timeout_entry.get().strip()
        if timeout:
            command.extend(["-e", timeout])

        retries = self.retries_entry.get().strip()
        if retries:
            command.extend(["-r", retries])

        connections = self.connections_entry.get().strip()
        if connections:
            command.extend(["-x", connections])

        # 任务设置
        tasks = self.tasks_entry.get().strip()
        if tasks:
            command.extend(["-t", tasks])

        counts = self.counts_entry.get().strip()
        if counts:
            command.extend(["-o", counts])

        page_counts = self.page_counts_entry.get().strip()
        if page_counts:
            command.extend(["-s", page_counts])

        return command

    def check_python_and_f2(self):
        """检查Python环境和F2工具是否存在"""
        try:
            # 保存当前目录
            original_dir = os.getcwd()

            # 如果未设置工作目录，提示用户先设置
            if not self.working_dir:
                self.append_output("提示: 请先设置工作目录")
                return False

            # 尝试切换到工作目录进行检查
            try:
                os.chdir(self.working_dir)
                self.append_output(f"在工作目录中检查环境: {self.working_dir}")
            except Exception as e:
                self.append_output(f"无法切换到工作目录 {self.working_dir}: {str(e)}")
                self.append_output("提示: 请检查工作目录设置是否正确")
                return False

            # 检查Python环境
            result = subprocess.run(
                ["python", "--version"], capture_output=True, text=True
            )
            if result.returncode != 0:
                # 尝试python3
                result = subprocess.run(
                    ["python3", "--version"], capture_output=True, text=True
                )
                if result.returncode != 0:
                    self.append_output("错误: 未找到Python环境")
                    os.chdir(original_dir)  # 恢复原目录
                    return False

            # 检查F2工具
            result = subprocess.run(["f2", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                self.append_output("错误: 未找到F2命令行工具，请先安装f2-douyin")
                os.chdir(original_dir)  # 恢复原目录
                return False

            # 恢复原目录
            os.chdir(original_dir)
            return True
        except Exception as e:
            self.append_output(f"检查环境时出错: {str(e)}")
            # 确保恢复原目录
            try:
                os.chdir(original_dir)
            except:
                pass
            return False

    def execute_command(self):
        """执行f2命令"""
        # 禁用执行按钮，防止重复点击
        self.execute_btn.config(state=tk.DISABLED)
        self.append_output("开始执行命令...")

        # 在新线程中执行命令
        command_thread = threading.Thread(target=self.execute_command_thread)
        command_thread.daemon = True  # 设置为守护线程，主程序退出时线程也会退出
        command_thread.start()

    def execute_command_thread(self):
        """在新线程中执行f2命令"""
        # 保存当前目录
        original_dir = os.getcwd()

        # 重置停止标志
        self.stop_flag = False

        # 获取输出方式设置
        output_mode = self.output_mode_var.get()

        try:
            # 检查Python环境和F2工具
            if not self.check_python_and_f2():
                if output_mode == "gui":
                    self.root.after(0, lambda: self.execute_btn.config(state=tk.NORMAL))
                    self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))
                else:
                    # 在控制台模式下，直接打印到控制台
                    print("错误: Python环境或F2工具检查失败")
                return

            # 验证URL
            url = self.url_text.get("1.0", tk.END).strip()
            if not url:
                if output_mode == "gui":
                    self.root.after(
                        0, lambda: self.append_output("提示: 请输入URL链接")
                    )
                    self.root.after(0, lambda: self.execute_btn.config(state=tk.NORMAL))
                    self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))
                else:
                    print("提示: 请输入URL链接")
                return

            # 验证Cookie
            cookie = self.cookie_text.get("1.0", tk.END).strip()
            if not cookie:
                if output_mode == "gui":
                    self.root.after(0, lambda: self.append_output("提示: 请输入Cookie"))
                    self.root.after(0, lambda: self.execute_btn.config(state=tk.NORMAL))
                    self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))
                else:
                    print("提示: 请输入Cookie")
                return

            # 检查工作目录是否设置
            if not self.working_dir:
                if output_mode == "gui":
                    self.root.after(
                        0, lambda: self.append_output("提示: 请先设置工作目录")
                    )
                    self.root.after(0, lambda: self.execute_btn.config(state=tk.NORMAL))
                    self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))
                else:
                    print("提示: 请先设置工作目录")
                return

            # 构建命令
            command = self.build_command()

            if output_mode == "gui":
                self.root.after(
                    0, lambda: self.append_output(f"执行命令: {' '.join(command)}")
                )
                self.root.after(
                    0, lambda: self.append_output(f"工作目录: {self.working_dir}")
                )
            else:
                print(f"执行命令: {' '.join(command)}")
                print(f"工作目录: {self.working_dir}")

            # 切换工作目录并执行命令
            try:
                os.chdir(self.working_dir)
                if output_mode == "gui":
                    self.root.after(
                        0,
                        lambda: self.append_output(
                            f"已切换到工作目录: {self.working_dir}"
                        ),
                    )
                else:
                    print(f"已切换到工作目录: {self.working_dir}")
            except Exception as e:
                if output_mode == "gui":
                    self.root.after(
                        0,
                        lambda: self.append_output(
                            f"无法切换到工作目录 {self.working_dir}: {str(e)}"
                        ),
                    )
                    self.root.after(
                        0,
                        lambda: self.append_output("提示: 请检查工作目录设置是否正确"),
                    )
                    self.root.after(0, lambda: self.execute_btn.config(state=tk.NORMAL))
                    self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))
                else:
                    print(f"无法切换到工作目录 {self.working_dir}: {str(e)}")
                    print("提示: 请检查工作目录设置是否正确")
                return

            # 根据输出方式决定如何执行命令
            if output_mode == "console":
                # 在新控制台窗口中执行命令
                try:
                    # 为控制台模式创建带引号的命令副本
                    console_command = command.copy()
                    # 查找-k参数并给其值加上双引号
                    for i in range(len(console_command)):
                        if console_command[i] == "-k" and i + 1 < len(console_command):
                            # 给cookie值加上双引号
                            cookie_value = console_command[i + 1]
                            console_command[i + 1] = f'"{cookie_value}"'
                            break

                    # 构建在新窗口中执行的命令
                    cmd_command = f'start cmd /k "cd /d "{self.working_dir}" && {" ".join(console_command)}"'
                    os.system(cmd_command)

                    # 在当前窗口提示用户已在新窗口执行
                    print(f"命令已在新控制台窗口中执行，工作目录: {self.working_dir}")
                    print(f"执行命令: {' '.join(console_command)}")

                    # 恢复原目录
                    try:
                        os.chdir(original_dir)
                    except:
                        pass

                    # 保存配置
                    self.save_config(
                        cookie_value=cookie, working_dir_value=self.working_dir
                    )
                    
                    # 恢复按钮状态
                    self.root.after(0, lambda: self.execute_btn.config(state=tk.NORMAL))
                    self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))
                    return
                except Exception as e:
                    print(f"执行错误: {str(e)}")
                    # 确保恢复原目录
                    try:
                        os.chdir(original_dir)
                    except:
                        pass
                    return
            else:
                # 在GUI中执行命令并显示输出
                # 执行命令
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )

                # 保存进程引用以便停止
                self.command_process = process

                # 启用停止按钮
                self.root.after(0, lambda: self.stop_btn.config(state=tk.NORMAL))

                # 实时输出并检查停止标志
                while True:
                    # 检查是否需要停止
                    if self.stop_flag:
                        process.terminate()  # 终止进程
                        self.root.after(
                            0, lambda: self.append_output("用户已停止采集任务")
                        )
                        break

                    # 检查进程是否已经结束
                    if process.poll() is not None:
                        break

                    # 非阻塞读取输出
                    try:
                        output = process.stdout.readline()
                        if output:
                            # 使用线程安全的方式更新UI
                            self.root.after(
                                0, lambda out=output.strip(): self.append_output(out)
                            )
                    except:
                        # 如果读取失败，稍作等待再继续
                        import time

                        time.sleep(0.1)
                        continue

                # 如果不是因为停止标志而退出，则读取剩余输出
                if not self.stop_flag:
                    # 错误输出
                    stderr = process.stderr.read()
                    if stderr:
                        self.root.after(
                            0,
                            lambda err=stderr.strip(): self.append_output(
                                f"错误输出: {err}"
                            ),
                        )

                # 恢复原目录
                try:
                    os.chdir(original_dir)
                except:
                    pass

                # 检查是否是用户停止的
                if self.stop_flag:
                    self.root.after(0, lambda: self.append_output("采集任务已停止"))
                else:
                    returncode = process.poll()
                    if returncode == 0:
                        self.root.after(0, lambda: self.append_output("命令执行完成"))
                        # 执行成功后保存配置（包括Cookie和工作目录）
                        self.save_config(
                            cookie_value=cookie, working_dir_value=self.working_dir
                        )
                    else:
                        self.root.after(
                            0,
                            lambda: self.append_output(
                                f"命令执行失败，返回码: {returncode}"
                            ),
                        )

        except Exception as e:
            if output_mode == "gui":
                self.root.after(0, lambda: self.append_output(f"执行错误: {str(e)}"))
            else:
                print(f"执行错误: {str(e)}")
            # 确保恢复原目录
            try:
                os.chdir(original_dir)
            except:
                pass
        finally:
            # 重置进程引用
            self.command_process = None
            # 重新启用执行按钮，禁用停止按钮
            if output_mode == "gui":
                self.root.after(0, lambda: self.execute_btn.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))

    def stop_command_execution(self):
        """停止当前执行的命令"""
        # 设置停止标志
        self.stop_flag = True

        # 获取输出方式设置
        output_mode = self.output_mode_var.get()

        # 如果有正在运行的进程，尝试终止它
        if self.command_process and self.command_process.poll() is None:
            try:
                self.command_process.terminate()  # 优雅终止
                if output_mode == "gui":
                    self.append_output("正在停止采集任务...")
                else:
                    print("正在停止采集任务...")
            except Exception as e:
                if output_mode == "gui":
                    self.append_output(f"停止任务时出错: {str(e)}")
                else:
                    print(f"停止任务时出错: {str(e)}")


def main():
    root = tk.Tk()
    app = F2DouyinGUI(root)

    # 设置样式
    style = ttk.Style()
    style.configure("TButton", padding=6, relief="flat", background="#ccc")
    style.configure("TLabel", padding=5)
    style.configure("TEntry", padding=5)
    style.configure("TCombobox", padding=5)

    root.mainloop()


if __name__ == "__main__":
    main()
