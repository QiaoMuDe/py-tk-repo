#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import selectors
import customtkinter as ctk
from tkinter import filedialog
import subprocess
import os
from datetime import datetime
import json
from pathlib import Path
import threading
import queue
import sys
import ctypes

# 设置customtkinter外观
ctk.set_appearance_mode("System")  # 可选: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # 可选: "blue", "green", "dark-blue"


def get_screen_size():
    """
    获取DPI感知的真实屏幕尺寸

    Returns:
        tuple: (屏幕宽度, 屏幕高度), 如果获取失败则返回默认值(1920, 1080)
    """
    # 非Windows系统直接返回默认值
    if sys.platform != "win32":
        return 1920, 1080

    try:
        # 定义Windows API常量和结构
        user32 = ctypes.windll.user32

        # 设置进程为DPI感知, 获取真实物理分辨率
        if hasattr(user32, "SetProcessDPIAware"):
            user32.SetProcessDPIAware()

        # 使用GetSystemMetrics获取屏幕尺寸
        # SM_CXSCREEN = 0 (屏幕宽度)
        # SM_CYSCREEN = 1 (屏幕高度)
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)

        # 验证获取的值是否合理
        if screen_width > 0 and screen_height > 0:
            return screen_width, screen_height
        else:
            return 1920, 1080  # 默认值

    except Exception as e:
        # 如果获取失败, 返回默认值
        print(f"获取屏幕尺寸失败: {e}")
        return 1920, 1080  # 默认值


class F2DouyinGUI:
    """
    F2抖音数据采集工具GUI类
    使用customtkinter库实现现代化界面
    """

    def __init__(self, root):
        """
        初始化GUI界面

        Args:
            root: 根窗口对象
        """
        self.root = root
        self.root.title("F2抖音数据采集工具")
        self.root.geometry("1200x900")
        self.root.width = 1200
        self.root.height = 900
        self.root.minsize(900, 700)

        # 设置标题字体
        self.root.title_font = ctk.CTkFont(
            family="Microsoft YaHei UI", size=16, weight="bold"
        )

        # 工作目录默认为空
        self.working_dir = ""

        # 线程控制变量
        self.command_process = None  # 当前执行的进程
        self.stop_flag = False  # 停止标志

        # 创建主框架
        self.main_frame = ctk.CTkFrame(root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 创建选项卡视图
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # 设置选项卡字体
        tab_font = ctk.CTkFont(family="Microsoft YaHei UI", size=13, weight="bold")

        # 创建选项卡
        self.tab_basic = self.tabview.add("基本设置")
        self.tab_advanced = self.tabview.add("高级设置")
        self.tab_output = self.tabview.add("输出显示")

        # 设置选项卡标签字体
        self.tabview._segmented_button._buttons_dict["基本设置"].configure(
            font=tab_font
        )
        self.tabview._segmented_button._buttons_dict["高级设置"].configure(
            font=tab_font
        )
        self.tabview._segmented_button._buttons_dict["输出显示"].configure(
            font=tab_font
        )

        # 创建控件
        self.create_widgets()

        # 在初始化时读取保存的配置（包括Cookie和工作目录）
        self.load_saved_config()

        # 窗口居中显示
        self.center_window()

    def center_window(self):
        """
        将指定窗口居中显示的通用方法

        Args:
            window: 需要居中的窗口对象（可以是Toplevel、CTkToplevel等）
            width: 窗口宽度, 如果为None则使用窗口当前宽度
            height: 窗口高度, 如果为None则使用窗口当前高度

        Returns:
            tuple: (x坐标, y坐标) 窗口应该设置的左上角坐标
        """
        try:
            # 获取屏幕尺寸
            screen_width, screen_height = get_screen_size()

            # 如果未指定宽度或高度, 尝试从窗口获取当前尺寸
            width, height = self.root.width, self.root.height

            # 获取窗口尺寸
            window_width = width
            window_height = height

            # 计算居中位置
            x = (screen_width // 2) - window_width
            y = (screen_height // 2) - window_height - 50

            # 确保窗口不会超出屏幕边界
            x = max(0, min(x, screen_width - window_width))
            y = max(0, min(y, screen_height - window_height))

            # 设置窗口位置
            self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

            return (x, y)

        except Exception as e:
            print(f"窗口居中失败: {e}")
            return (100, 100)

    def create_widgets(self):
        """创建所有UI控件"""
        self.create_basic_tab_widgets()
        self.create_advanced_tab_widgets()
        self.create_output_tab_widgets()
        self.create_action_buttons()

    def create_basic_tab_widgets(self):
        """创建基本设置选项卡的控件"""
        # 工作目录选择 - 使用更简洁的布局
        dir_frame = ctk.CTkFrame(self.tab_basic, fg_color="transparent")
        dir_frame.pack(fill="x", padx=10, pady=5)

        dir_label = ctk.CTkLabel(
            dir_frame,
            text="工作目录:",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=14, weight="bold"),
        )
        dir_label.pack(anchor="w", padx=10, pady=(5, 2))

        dir_entry_frame = ctk.CTkFrame(dir_frame, fg_color="transparent")
        dir_entry_frame.pack(fill="x", padx=10, pady=(0, 5))

        self.work_dir_entry = ctk.CTkEntry(
            dir_entry_frame,
            placeholder_text="选择工作目录",
            border_width=1,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        )
        self.work_dir_entry.pack(
            side="left", fill="x", expand=True, padx=(10, 5), pady=5
        )
        self.work_dir_entry.insert(0, self.working_dir)

        self.select_dir_btn = ctk.CTkButton(
            dir_entry_frame,
            text="选择目录",
            command=self.select_working_directory,
            width=100,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            text_color="white",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        )
        self.select_dir_btn.pack(side="right", padx=(5, 10), pady=5)

        # URL输入 - 减少内边距
        url_frame = ctk.CTkFrame(self.tab_basic, fg_color="transparent")
        url_frame.pack(fill="x", padx=10, pady=5)

        url_label = ctk.CTkLabel(
            url_frame,
            text="URL链接 (-u):",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=14, weight="bold"),
        )
        url_label.pack(anchor="w", padx=10, pady=(5, 2))

        self.url_text = ctk.CTkTextbox(
            url_frame,
            height=80,
            border_width=1,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        )
        self.url_text.pack(fill="x", padx=10, pady=(0, 5))

        # 下载模式和显示语言 - 简化布局
        mode_lang_frame = ctk.CTkFrame(self.tab_basic, fg_color="transparent")
        mode_lang_frame.pack(fill="x", padx=10, pady=5)

        mode_lang_label = ctk.CTkLabel(
            mode_lang_frame,
            text="下载与显示设置:",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=14, weight="bold"),
        )
        mode_lang_label.pack(anchor="w", padx=10, pady=(5, 2))

        mode_frame = ctk.CTkFrame(mode_lang_frame, fg_color="transparent")
        mode_frame.pack(fill="x", padx=10, pady=(0, 5))

        mode_label = ctk.CTkLabel(
            mode_frame,
            text="下载模式 (-M):",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12, weight="bold"),
        )
        mode_label.pack(side="left", padx=(10, 5), pady=5)

        self.mode_combo = ctk.CTkComboBox(
            mode_frame,
            values=[
                "one - 单个作品",
                "post - 主页作品",
                "like - 点赞作品",
                "collection - 收藏作品",
                "collects - 收藏夹作品",
                "mix - 合集",
                "live - 直播",
            ],
            width=200,
            border_width=1,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12, weight="bold"),
        )
        self.mode_combo.pack(side="left", padx=(0, 10), pady=5)
        self.mode_combo.set("one - 单个作品")  # 默认值

        lang_label = ctk.CTkLabel(
            mode_frame,
            text="显示语言 (-l):",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12, weight="bold"),
        )
        lang_label.pack(side="left", padx=(0, 5), pady=5)

        self.lang_combo = ctk.CTkComboBox(
            mode_frame,
            values=["zh_CN", "en_US"],
            width=100,
            border_width=1,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        )
        self.lang_combo.pack(side="left", padx=(0, 10), pady=5)
        self.lang_combo.set("zh_CN")

        # 保存选项 - 简化复选框区域
        save_frame = ctk.CTkFrame(self.tab_basic, fg_color="transparent")
        save_frame.pack(fill="x", padx=10, pady=5)

        save_label = ctk.CTkLabel(
            save_frame,
            text="保存选项:",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=14, weight="bold"),
        )
        save_label.pack(anchor="w", padx=10, pady=(5, 2))

        save_options_frame = ctk.CTkFrame(save_frame, fg_color="transparent")
        save_options_frame.pack(fill="x", padx=10, pady=(0, 5))

        # 使用网格布局排列复选框，减少垂直空间
        self.music_var = ctk.BooleanVar()
        self.music_check = ctk.CTkCheckBox(
            save_options_frame,
            text="保存视频原声 (-m)",
            variable=self.music_var,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        )
        self.music_check.grid(row=0, column=0, sticky="w", padx=10, pady=2)

        self.cover_var = ctk.BooleanVar()
        self.cover_check = ctk.CTkCheckBox(
            save_options_frame,
            text="保存视频封面 (-v)",
            variable=self.cover_var,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        )
        self.cover_check.grid(row=0, column=1, sticky="w", padx=10, pady=2)

        self.desc_var = ctk.BooleanVar()
        self.desc_check = ctk.CTkCheckBox(
            save_options_frame,
            text="保存视频文案 (-d)",
            variable=self.desc_var,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        )
        self.desc_check.grid(row=1, column=0, sticky="w", padx=10, pady=2)

        self.folderize_var = ctk.BooleanVar()
        self.folderize_check = ctk.CTkCheckBox(
            save_options_frame,
            text="单独文件夹保存 (-f)",
            variable=self.folderize_var,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        )
        self.folderize_check.grid(row=1, column=1, sticky="w", padx=10, pady=2)

        # 路径设置 - 减少内边距
        path_frame = ctk.CTkFrame(self.tab_basic, fg_color="transparent")
        path_frame.pack(fill="x", padx=10, pady=5)

        path_label = ctk.CTkLabel(
            path_frame,
            text="保存路径 (-p):",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=14, weight="bold"),
        )
        path_label.pack(anchor="w", padx=10, pady=(5, 2))

        path_entry_frame = ctk.CTkFrame(path_frame, fg_color="transparent")
        path_entry_frame.pack(fill="x", padx=10, pady=(0, 5))

        self.path_entry = ctk.CTkEntry(
            path_entry_frame,
            placeholder_text="选择保存路径",
            border_width=1,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=5)
        # 默认保存路径设置为工作目录
        self.path_entry.insert(0, self.working_dir)

        self.select_path_btn = ctk.CTkButton(
            path_entry_frame,
            text="选择路径",
            command=self.select_save_path,
            width=100,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            text_color="white",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        )
        self.select_path_btn.pack(side="right", padx=(5, 10), pady=5)

        # Cookie - 减少内边距和边框
        cookie_frame = ctk.CTkFrame(self.tab_basic, fg_color="transparent")
        cookie_frame.pack(fill="x", padx=10, pady=5)

        cookie_label = ctk.CTkLabel(
            cookie_frame,
            text="Cookie (-k):",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=14, weight="bold"),
        )
        cookie_label.pack(anchor="w", padx=10, pady=(5, 2))

        self.cookie_text = ctk.CTkTextbox(
            cookie_frame,
            height=120,
            border_width=1,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        )
        self.cookie_text.pack(fill="x", padx=10, pady=(0, 5))

    def create_advanced_tab_widgets(self):
        """创建高级设置选项卡的控件"""
        # 日期区间 - 减少边框和内边距
        interval_frame = ctk.CTkFrame(self.tab_advanced, fg_color="transparent")
        interval_frame.pack(fill="x", padx=10, pady=5)

        interval_label = ctk.CTkLabel(
            interval_frame,
            text="日期区间 (-i):",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=14, weight="bold"),
        )
        interval_label.pack(anchor="w", padx=10, pady=(5, 2))

        interval_entry_frame = ctk.CTkFrame(interval_frame, fg_color="transparent")
        interval_entry_frame.pack(fill="x", padx=10, pady=(0, 5))

        self.interval_entry = ctk.CTkEntry(
            interval_entry_frame,
            placeholder_text="日期区间",
            border_width=1,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        )
        self.interval_entry.pack(
            side="left", fill="x", expand=True, padx=(10, 5), pady=5
        )
        self.interval_entry.insert(0, "all")

        interval_help = ctk.CTkLabel(
            interval_frame,
            text="格式: YYYY-MM-DD|YYYY-MM-DD 或 'all'",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=11),
        )
        interval_help.pack(anchor="w", padx=10, pady=(0, 5))

        # 网络设置 - 简化布局
        network_frame = ctk.CTkFrame(self.tab_advanced, fg_color="transparent")
        network_frame.pack(fill="x", padx=10, pady=5)

        network_label = ctk.CTkLabel(
            network_frame,
            text="网络设置:",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=14, weight="bold"),
        )
        network_label.pack(anchor="w", padx=10, pady=(5, 2))

        network_options_frame = ctk.CTkFrame(network_frame, fg_color="transparent")
        network_options_frame.pack(fill="x", padx=10, pady=(0, 5))

        # 超时时间、重试次数、并发连接 - 使用网格布局
        timeout_frame = ctk.CTkFrame(network_options_frame, fg_color="transparent")
        timeout_frame.pack(fill="x", pady=5)

        timeout_label = ctk.CTkLabel(
            timeout_frame,
            text="超时时间 (-e):",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        )
        timeout_label.grid(row=0, column=0, sticky="w", padx=(10, 5), pady=2)

        self.timeout_entry = ctk.CTkEntry(
            timeout_frame,
            width=100,
            border_width=1,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        )
        self.timeout_entry.grid(row=0, column=1, sticky="w", padx=(0, 20), pady=2)
        self.timeout_entry.insert(0, "10")

        retries_label = ctk.CTkLabel(
            timeout_frame,
            text="重试次数 (-r):",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        )
        retries_label.grid(row=0, column=2, sticky="w", padx=(0, 5), pady=2)

        self.retries_entry = ctk.CTkEntry(
            timeout_frame,
            width=100,
            border_width=1,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        )
        self.retries_entry.grid(row=0, column=3, sticky="w", padx=(0, 20), pady=2)
        self.retries_entry.insert(0, "3")

        connections_label = ctk.CTkLabel(
            timeout_frame,
            text="并发连接 (-x):",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        )
        connections_label.grid(row=0, column=4, sticky="w", padx=(0, 5), pady=2)

        self.connections_entry = ctk.CTkEntry(
            timeout_frame,
            width=100,
            border_width=1,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        )
        self.connections_entry.grid(row=0, column=5, sticky="w", padx=(0, 10), pady=2)
        self.connections_entry.insert(0, "5")

        # 任务设置 - 简化布局
        task_frame = ctk.CTkFrame(self.tab_advanced, fg_color="transparent")
        task_frame.pack(fill="x", padx=10, pady=5)

        task_label = ctk.CTkLabel(
            task_frame,
            text="任务设置:",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=14, weight="bold"),
        )
        task_label.pack(anchor="w", padx=10, pady=(5, 2))

        task_options_frame = ctk.CTkFrame(task_frame, fg_color="transparent")
        task_options_frame.pack(fill="x", padx=10, pady=(0, 5))

        # 最大任务数、最大下载数、每页作品数 - 使用网格布局
        tasks_frame = ctk.CTkFrame(task_options_frame, fg_color="transparent")
        tasks_frame.pack(fill="x", pady=5)

        tasks_label = ctk.CTkLabel(
            tasks_frame,
            text="最大任务数 (-t):",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        )
        tasks_label.grid(row=0, column=0, sticky="w", padx=(10, 5), pady=2)

        self.tasks_entry = ctk.CTkEntry(
            tasks_frame,
            width=100,
            border_width=1,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        )
        self.tasks_entry.grid(row=0, column=1, sticky="w", padx=(0, 20), pady=2)
        self.tasks_entry.insert(0, "10")

        counts_label = ctk.CTkLabel(
            tasks_frame,
            text="最大下载数 (-o):",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        )
        counts_label.grid(row=0, column=2, sticky="w", padx=(0, 5), pady=2)

        self.counts_entry = ctk.CTkEntry(
            tasks_frame,
            width=100,
            border_width=1,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        )
        self.counts_entry.grid(row=0, column=3, sticky="w", padx=(0, 20), pady=2)
        self.counts_entry.insert(0, "0")

        page_counts_label = ctk.CTkLabel(
            tasks_frame,
            text="每页作品数 (-s):",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        )
        page_counts_label.grid(row=0, column=4, sticky="w", padx=(0, 5), pady=2)

        self.page_counts_entry = ctk.CTkEntry(
            tasks_frame,
            width=100,
            border_width=1,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        )
        self.page_counts_entry.grid(row=0, column=5, sticky="w", padx=(0, 10), pady=2)
        self.page_counts_entry.insert(0, "20")

    def create_output_tab_widgets(self):
        """创建输出显示选项卡的控件"""
        # 输出区域 - 减少边框和内边距
        output_frame = ctk.CTkFrame(self.tab_output, fg_color="transparent")
        output_frame.pack(fill="both", expand=True, padx=10, pady=5)

        output_label = ctk.CTkLabel(
            output_frame,
            text="执行输出:",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=14, weight="bold"),
        )
        output_label.pack(anchor="w", padx=10, pady=(5, 2))

        output_buttons_frame = ctk.CTkFrame(output_frame, fg_color="transparent")
        output_buttons_frame.pack(fill="x", padx=10, pady=(0, 5))

        self.clear_btn = ctk.CTkButton(
            output_buttons_frame,
            text="清空输出",
            command=self.clear_output,
            width=100,
            fg_color="#f59e0b",
            hover_color="#d97706",
            text_color="white",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        )
        self.clear_btn.pack(side="left", padx=(10, 5), pady=5)

        self.copy_btn = ctk.CTkButton(
            output_buttons_frame,
            text="复制输出",
            command=self.copy_output,
            width=100,
            fg_color="#f59e0b",
            hover_color="#d97706",
            text_color="white",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        )
        self.copy_btn.pack(side="left", padx=5, pady=5)

        self.output_text = ctk.CTkTextbox(
            output_frame,
            border_width=1,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
            wrap="none",  # 禁用自动换行，保持原始格式
        )
        self.output_text.pack(fill="both", expand=True, padx=10, pady=(0, 5))

    def create_action_buttons(self):
        """创建执行和停止按钮"""
        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=5)

        self.execute_btn = ctk.CTkButton(
            button_frame,
            text="执行采集",
            command=self.execute_command,
            fg_color="#10b981",
            hover_color="#059669",
            text_color="white",
            height=40,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=14, weight="bold"),
        )
        self.execute_btn.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=5)

        self.stop_btn = ctk.CTkButton(
            button_frame,
            text="停止采集",
            command=self.stop_command_execution,
            state="disabled",
            fg_color="red",
            hover_color="darkred",
            height=40,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=14, weight="bold"),
        )
        self.stop_btn.pack(side="left", fill="x", expand=True, padx=(5, 10), pady=5)

    def select_working_directory(self):
        """
        选择工作目录

        通过文件对话框选择工作目录，并更新相关输入框
        """
        directory = filedialog.askdirectory()
        if directory:
            self.working_dir = directory
            self.work_dir_entry.delete(0, "end")
            self.work_dir_entry.insert(0, directory)
            # 同时更新保存路径为新的工作目录
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, directory)
            # 如果工作目录不存在，则创建它
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory)
                    self.append_output(f"已创建工作目录: {directory}")
                except Exception as e:
                    self.append_output(f"创建工作目录失败: {str(e)}")
            # 立即保存工作目录到配置文件
            self.save_config(working_dir_value=directory)

    def select_save_path(self):
        """
        选择保存路径

        通过文件对话框选择保存路径，并更新相关输入框
        """
        directory = filedialog.askdirectory()
        if directory:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, directory)
            # 如果保存路径与工作目录相同，也更新工作目录
            if directory == self.working_dir:
                self.save_config(working_dir_value=directory)

    def append_output(self, text):
        """
        追加输出文本到输出区域

        Args:
            text: 要追加的文本
        """
        # 不自动添加换行符，因为调用方已经处理了换行
        self.output_text.insert("end", text)
        self.output_text.see("end")
        self.root.update()

    def clear_output(self):
        """清空输出区域"""
        self.output_text.delete("1.0", "end")

    def copy_output(self):
        """复制输出内容到剪贴板"""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.output_text.get("1.0", "end"))
        self.append_output("输出已复制到剪贴板")

    def get_config_file_path(self):
        """
        获取配置文件路径

        Returns:
            Path: 配置文件的路径
        """
        # 获取用户家目录
        home_dir = Path.home()
        # 创建隐藏文件路径 (.f2_douyin_config.json)
        config_file = home_dir / ".f2_douyin_config.json"
        return config_file

    def save_config(self, cookie_value=None, working_dir_value=None):
        """
        保存配置到文件

        Args:
            cookie_value: Cookie值
            working_dir_value: 工作目录值
        """
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
                    self.cookie_text.delete("1.0", "end")
                    self.cookie_text.insert("1.0", cookie_value)

                # 获取工作目录值并填充到输入框
                working_dir_value = config_data.get("working_dir", "")
                if working_dir_value:
                    self.working_dir = working_dir_value
                    self.work_dir_entry.delete(0, "end")
                    self.work_dir_entry.insert(0, working_dir_value)
                    # 同时更新保存路径为加载的工作目录
                    self.path_entry.delete(0, "end")
                    self.path_entry.insert(0, working_dir_value)
        except Exception as e:
            # 如果读取失败，不中断程序执行
            print(f"加载配置时出错: {e}")

    def build_command(self):
        """
        构建f2命令

        Returns:
            list: 构建好的命令参数列表
        """
        command = ["f2", "dy"]

        # URL
        url = self.url_text.get("1.0", "end").strip()
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
        cookie = self.cookie_text.get("1.0", "end").strip()
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
        """
        检查Python环境和F2工具是否存在

        Returns:
            bool: 检查结果，True表示环境正常，False表示环境异常
        """
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

    def restore_buttons_state(self):
        """恢复按钮状态"""
        self.execute_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")

    def stop_command_execution(self):
        """停止当前执行的命令"""
        # 设置停止标志
        self.stop_flag = True

        # 如果有正在运行的进程，尝试终止它
        if self.command_process and self.command_process.poll() is None:
            try:
                self.command_process.terminate()  # 优雅终止
                self.append_output("正在停止采集任务...")
            except Exception as e:
                self.append_output(f"停止任务时出错: {str(e)}")

    def execute_command(self):
        """执行f2命令"""
        # 禁用执行按钮，启用停止按钮
        self.execute_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.append_output("开始执行命令...")

        # 自动切换到输出显示选项卡，以便用户查看执行结果
        self.tabview.set("输出显示")

        # 在新线程中执行命令
        command_thread = threading.Thread(target=self.execute_command_thread)
        command_thread.daemon = True  # 设置为守护线程，主程序退出时线程也会退出
        command_thread.start()

    def execute_command_thread(self):
        """在后台线程中执行命令"""
        try:
            # 检查Python和f2是否安装
            if not self.check_python_and_f2():
                return

            # 构建命令
            command = self.build_command()
            if not command:
                return

            # GUI模式：在当前进程中运行命令并捕获输出
            self.append_output(f"开始执行命令...\n")
            self.append_output(f"工作目录: {self.working_dir}\n")
            self.append_output(f"命令: {' '.join(command)}\n")
            self.append_output("-" * 50 + "\n")

            # 执行命令并实时读取输出
            self.command_process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=self.working_dir,
            )

            # 实时读取输出
            for line in iter(self.command_process.stdout.readline, ""):
                if line:
                    # 保留原始行的换行符，确保正确换行显示
                    self.append_output(line)
                    print(line)
                # 检查是否需要停止
                if self.stop_flag:
                    break

            # 等待进程结束
            self.command_process.wait()

            if self.stop_flag:
                self.append_output("\n命令已手动停止")
            else:
                self.append_output(
                    f"\n命令执行完成，退出码: {self.command_process.returncode}"
                )

            self.command_process = None
        except Exception as e:
            self.append_output(f"执行命令时出错: {str(e)}")
        finally:
            # 恢复按钮状态
            self.root.after(0, self.restore_buttons_state)
            self.stop_flag = False


def main():
    """主函数，创建并运行应用程序"""
    root = ctk.CTk()
    app = F2DouyinGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
