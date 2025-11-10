#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文档统计信息对话框模块
"""

import os
import re
import threading
import queue
import time
from datetime import datetime
from pathlib import Path
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
from config.config_manager import config_manager


class StatsCalculator:
    """文档统计计算器类"""

    def __init__(self, text_content, file_path=None):
        """
        初始化统计计算器

        Args:
            text_content (str): 要分析的文本内容
            file_path (str, optional): 文件路径，用于代码分析
        """
        self.text_content = text_content
        self.file_path = file_path
        self.file_extension = Path(file_path).suffix.lower() if file_path else ""
        self.total_lines = len(text_content.splitlines()) if text_content else 0
        self.total_chars = len(text_content) if text_content else 0

    def is_code_file(self):
        """判断是否为代码文件"""
        code_extensions = [
            ".py",
            ".js",
            ".java",
            ".c",
            ".cpp",
            ".h",
            ".hpp",
            ".cs",
            ".php",
            ".rb",
            ".go",
            ".rs",
            ".swift",
            ".kt",
            ".scala",
            ".sh",
            ".bat",
            ".html",
            ".css",
            ".scss",
            ".less",
            ".xml",
            ".json",
            ".yaml",
            ".yml",
            ".sql",
            ".pl",
            ".r",
            ".m",
            ".vb",
            ".pas",
            ".dart",
            ".ts",
        ]
        return self.file_extension in code_extensions

    def get_comment_patterns(self):
        """获取注释模式"""
        patterns = {
            ".py": [r"#.*$", r'""".*?"""', r"'''.*?'''"],
            ".js": [r"//.*$", r"/\*.*?\*/"],
            ".java": [r"//.*$", r"/\*.*?\*/"],
            ".c": [r"//.*$", r"/\*.*?\*/"],
            ".cpp": [r"//.*$", r"/\*.*?\*/"],
            ".h": [r"//.*$", r"/\*.*?\*/"],
            ".hpp": [r"//.*$", r"/\*.*?\*/"],
            ".cs": [r"//.*$", r"/\*.*?\*/"],
            ".php": [r"//.*$", r"/\*.*?\*/", r"#.*$"],
            ".rb": [r"#.*$"],
            ".go": [r"//.*$", r"/\*.*?\*/"],
            ".rs": [r"//.*$", r"/\*.*?\*/"],
            ".swift": [r"//.*$", r"/\*.*?\*/"],
            ".kt": [r"//.*$", r"/\*.*?\*/"],
            ".scala": [r"//.*$", r"/\*.*?\*/"],
            ".sh": [r"#.*$"],
            ".bat": [r"rem.*$", r"::.*$"],
            ".html": [r"<!--.*?-->"],
            ".css": [r"/\*.*?\*/"],
            ".scss": [r"//.*$", r"/\*.*?\*/"],
            ".less": [r"//.*$", r"/\*.*?\*/"],
            ".xml": [r"<!--.*?-->"],
            ".sql": [r"--.*$", r"/\*.*?\*/"],
            ".pl": [r"#.*$"],
            ".r": [r"#.*$"],
            ".m": [r"%.*$"],
            ".vb": [r"'.*"],
            ".pas": [r"\{.*?\}", r"\(\*.*?\*\)"],
            ".dart": [r"//.*$", r"/\*.*?\*/"],
            ".ts": [r"//.*$", r"/\*.*?\*/"],
        }
        return patterns.get(self.file_extension, [])

    def calculate_basic_stats(self, progress_callback=None):
        """计算基本统计信息"""
        if not self.text_content:
            return {}

        stats = {}

        # 基本统计
        stats["total_chars"] = len(self.text_content)
        stats["total_chars_no_spaces"] = len(
            self.text_content.replace(" ", "").replace("\t", "")
        )
        stats["total_lines"] = len(self.text_content.splitlines())

        # 非空行数
        non_empty_lines = 0
        for line in self.text_content.splitlines():
            if line.strip():
                non_empty_lines += 1
        stats["non_empty_lines"] = non_empty_lines

        # 字符类型统计
        chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", self.text_content))
        english_chars = len(re.findall(r"[a-zA-Z]", self.text_content))
        digit_chars = len(re.findall(r"[0-9]", self.text_content))
        space_chars = len(re.findall(r"[ \t]", self.text_content))
        punctuation_chars = len(re.findall(r"[^\w\s\u4e00-\u9fff]", self.text_content))

        stats["chinese_chars"] = chinese_chars
        stats["english_chars"] = english_chars
        stats["digit_chars"] = digit_chars
        stats["space_chars"] = space_chars
        stats["punctuation_chars"] = punctuation_chars
        stats["other_chars"] = (
            stats["total_chars"]
            - chinese_chars
            - english_chars
            - digit_chars
            - space_chars
            - punctuation_chars
        )

        # 单词统计（中英文）
        # 英文单词
        english_words = re.findall(r"\b[a-zA-Z]+\b", self.text_content)
        stats["english_words"] = len(english_words)

        # 中文单词（以中文标点或空格分隔）
        chinese_words = re.findall(r"[\u4e00-\u9fff]+", self.text_content)
        stats["chinese_words"] = len(chinese_words)
        stats["total_words"] = stats["english_words"] + stats["chinese_words"]

        # 段落统计
        paragraphs = re.split(r"\n\s*\n", self.text_content.strip())
        stats["paragraphs"] = len([p for p in paragraphs if p.strip()])

        return stats

    def calculate_code_stats(self, progress_callback=None):
        """计算代码统计信息"""
        if not self.is_code_file() or not self.text_content:
            return {}

        stats = {}
        comment_patterns = self.get_comment_patterns()

        code_lines = 0
        comment_lines = 0
        empty_lines = 0

        lines = self.text_content.splitlines()
        total_lines = len(lines)

        for i, line in enumerate(lines):
            if progress_callback:
                progress = int((i / total_lines) * 100)
                progress_callback(progress)

            stripped_line = line.strip()

            # 空行
            if not stripped_line:
                empty_lines += 1
                continue

            # 检查是否为注释行
            is_comment = False
            for pattern in comment_patterns:
                if re.search(pattern, line):
                    is_comment = True
                    break

            if is_comment:
                comment_lines += 1
            else:
                code_lines += 1

        stats["code_lines"] = code_lines
        stats["comment_lines"] = comment_lines
        stats["empty_lines"] = empty_lines
        stats["total_code_lines"] = total_lines

        return stats


class StatsWorker(threading.Thread):
    """统计工作线程类"""

    def __init__(self, calculator, result_queue, progress_queue):
        """
        初始化工作线程

        Args:
            calculator (StatsCalculator): 统计计算器实例
            result_queue (queue.Queue): 结果队列
            progress_queue (queue.Queue): 进度队列
        """
        super().__init__()
        self.calculator = calculator
        self.result_queue = result_queue
        self.progress_queue = progress_queue
        self._stop_event = threading.Event()

    def stop(self):
        """停止线程"""
        self._stop_event.set()

    def stopped(self):
        """检查线程是否已停止"""
        return self._stop_event.is_set()

    def run(self):
        """运行工作线程"""
        try:
            # 发送开始信号
            self.progress_queue.put(("start", "开始计算..."))

            # 计算基本统计
            self.progress_queue.put(("progress", 10, "计算基本统计信息..."))
            basic_stats = self.calculator.calculate_basic_stats()
            self.result_queue.put(("basic_stats", basic_stats))

            if self.stopped():
                return

            # 计算代码统计（如果是代码文件）
            if self.calculator.is_code_file():
                self.progress_queue.put(("progress", 50, "分析代码结构..."))
                code_stats = self.calculator.calculate_code_stats(
                    lambda p: self.progress_queue.put(
                        ("progress", 50 + p // 2, f"分析代码中... {p}%")
                    )
                )
                self.result_queue.put(("code_stats", code_stats))

            # 发送完成信号
            self.progress_queue.put(("progress", 100, "计算完成"))
            self.progress_queue.put(("complete", "统计完成"))

        except Exception as e:
            self.progress_queue.put(("error", f"计算错误: {str(e)}"))


class DocumentStatsDialog(ctk.CTkToplevel):
    """文档统计信息对话框类"""

    def __init__(self, parent, text_content, file_path=None):
        """
        初始化文档统计对话框

        Args:
            parent: 父窗口
            text_content (str): 要统计的文本内容
            file_path (str, optional): 文件路径
        """
        super().__init__(parent)

        self.parent = parent
        self.text_content = text_content
        self.file_path = file_path
        self.calculator = StatsCalculator(text_content, file_path)

        # 全屏状态标志
        self.is_fullscreen = False

        # 创建队列用于线程间通信
        self.result_queue = queue.Queue()
        self.progress_queue = queue.Queue()

        # 工作线程
        self.worker = None

        # 统计结果
        self.basic_stats = {}
        self.code_stats = {}

        # 初始化界面
        self._init_ui()

        # 启动工作线程
        self._start_worker()

        # 开始检查进度
        self._check_progress()

    def _init_ui(self):
        """初始化用户界面"""
        # 设置窗口属性
        self.title("文档统计信息")
        self.geometry("500x400")
        self.resizable(True, True)

        # 设置窗口模态
        self.transient(self.parent)
        self.grab_set()

        # 获取组件字体配置
        font_name = config_manager.get("components.font", "Microsoft YaHei UI")
        font_size = config_manager.get("components.font_size", 13)
        font_bold = config_manager.get("components.font_bold", False)

        # 创建主框架
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 文件信息框架
        file_frame = ctk.CTkFrame(main_frame)
        file_frame.pack(fill="x", pady=(0, 10))

        # 文件名
        file_name = os.path.basename(self.file_path) if self.file_path else "无标题"
        self.file_name_label = ctk.CTkLabel(
            file_frame,
            text=f"文件: {file_name}",
            font=ctk.CTkFont(size=font_size + 1, weight="bold", family=font_name),
        )
        self.file_name_label.pack(anchor="w", padx=10, pady=(10, 5))

        # 文件路径
        if self.file_path:
            self.file_path_label = ctk.CTkLabel(
                file_frame,
                text=f"路径: {self.file_path}",
                font=ctk.CTkFont(size=font_size - 1, family=font_name),
            )
            self.file_path_label.pack(anchor="w", padx=10, pady=(0, 5))

            # 文件大小
            try:
                file_size = os.path.getsize(self.file_path)
                file_size_str = self._format_file_size(file_size)
                self.file_size_label = ctk.CTkLabel(
                    file_frame,
                    text=f"大小: {file_size_str}",
                    font=ctk.CTkFont(size=font_size - 1, family=font_name),
                )
                self.file_size_label.pack(anchor="w", padx=10, pady=(0, 5))

                # 修改时间
                mod_time = os.path.getmtime(self.file_path)
                mod_time_str = datetime.fromtimestamp(mod_time).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                self.mod_time_label = ctk.CTkLabel(
                    file_frame,
                    text=f"修改时间: {mod_time_str}",
                    font=ctk.CTkFont(size=font_size - 1, family=font_name),
                )
                self.mod_time_label.pack(anchor="w", padx=10, pady=(0, 10))
            except:
                pass

        # 进度条
        self.progress_label = ctk.CTkLabel(
            main_frame,
            text="准备计算...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.progress_label.pack(anchor="w", padx=10, pady=(10, 5))

        self.progress_bar = ctk.CTkProgressBar(main_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=(0, 10))
        self.progress_bar.set(0)

        # 创建选项卡视图
        self.tabview = ctk.CTkTabview(main_frame)
        self.tabview.pack(fill="both", expand=True, pady=(0, 10))

        # 基本统计选项卡
        self.basic_tab = self.tabview.add("基本统计")
        self._create_basic_stats_tab()

        # 代码统计选项卡（如果是代码文件）
        if self.calculator.is_code_file():
            self.code_tab = self.tabview.add("代码统计")
            self._create_code_stats_tab()

        # 绑定双击事件到选项卡的segmented_button内部的按钮，用于切换全屏
        # 由于CTkSegmentedButton没有实现bind方法，我们需要直接访问内部的按钮
        if "基本统计" in self.tabview._segmented_button._buttons_dict:
            self.tabview._segmented_button._buttons_dict["基本统计"].bind(
                "<Double-Button-1>", self._on_tab_double_click
            )

        # 按钮框架
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x")

        # 取消按钮
        self.cancel_button = ctk.CTkButton(
            button_frame,
            text="取消",
            command=self._cancel_calculation,
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.cancel_button.pack(side="left", padx=(10, 5), pady=10)

        # 全屏按钮
        self.fullscreen_button = ctk.CTkButton(
            button_frame,
            text="全屏",
            command=self._toggle_fullscreen,
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.fullscreen_button.pack(side="left", padx=5, pady=10)

        # 导出按钮（初始禁用）
        self.export_button = ctk.CTkButton(
            button_frame,
            text="导出报告",
            command=self._export_report,
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.export_button.pack(side="right", padx=(5, 10), pady=10)
        self.export_button.configure(state="disabled")

        # 关闭按钮
        self.close_button = ctk.CTkButton(
            button_frame,
            text="关闭",
            command=self.destroy,
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.close_button.pack(side="right", padx=5, pady=10)

        # 绑定ESC键，用于退出全屏或关闭窗口
        self.bind("<Escape>", self._on_escape)

        # 居中显示窗口
        self._center_window()

    def _create_basic_stats_tab(self):
        """创建基本统计选项卡"""
        # 获取组件字体配置
        font_name = config_manager.get("components.font", "Microsoft YaHei UI")
        font_size = config_manager.get("components.font_size", 13)

        # 创建滚动框架
        scroll_frame = ctk.CTkScrollableFrame(self.basic_tab)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 字符统计框架
        char_frame = ctk.CTkFrame(scroll_frame)
        char_frame.pack(fill="x", pady=(0, 10))

        char_title = ctk.CTkLabel(
            char_frame,
            text="字符统计",
            font=ctk.CTkFont(size=font_size + 1, weight="bold", family=font_name),
        )
        char_title.pack(anchor="w", padx=10, pady=(10, 5))

        # 字符统计标签
        self.total_chars_label = ctk.CTkLabel(
            char_frame,
            text="总字符数: 计算中...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.total_chars_label.pack(anchor="w", padx=20, pady=2)

        self.total_chars_no_spaces_label = ctk.CTkLabel(
            char_frame,
            text="不含空格字符数: 计算中...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.total_chars_no_spaces_label.pack(anchor="w", padx=20, pady=2)

        self.chinese_chars_label = ctk.CTkLabel(
            char_frame,
            text="中文字符数: 计算中...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.chinese_chars_label.pack(anchor="w", padx=20, pady=2)

        self.english_chars_label = ctk.CTkLabel(
            char_frame,
            text="英文字符数: 计算中...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.english_chars_label.pack(anchor="w", padx=20, pady=2)

        self.digit_chars_label = ctk.CTkLabel(
            char_frame,
            text="数字字符数: 计算中...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.digit_chars_label.pack(anchor="w", padx=20, pady=2)

        self.space_chars_label = ctk.CTkLabel(
            char_frame,
            text="空格/制表符数: 计算中...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.space_chars_label.pack(anchor="w", padx=20, pady=2)

        self.punctuation_chars_label = ctk.CTkLabel(
            char_frame,
            text="标点符号数: 计算中...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.punctuation_chars_label.pack(anchor="w", padx=20, pady=2)

        self.other_chars_label = ctk.CTkLabel(
            char_frame,
            text="其他字符数: 计算中...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.other_chars_label.pack(anchor="w", padx=20, pady=(2, 10))

        # 行和单词统计框架
        line_word_frame = ctk.CTkFrame(scroll_frame)
        line_word_frame.pack(fill="x", pady=(0, 10))

        line_word_title = ctk.CTkLabel(
            line_word_frame,
            text="行和单词统计",
            font=ctk.CTkFont(size=font_size + 1, weight="bold", family=font_name),
        )
        line_word_title.pack(anchor="w", padx=10, pady=(10, 5))

        # 行和单词统计标签
        self.total_lines_label = ctk.CTkLabel(
            line_word_frame,
            text="总行数: 计算中...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.total_lines_label.pack(anchor="w", padx=20, pady=2)

        self.non_empty_lines_label = ctk.CTkLabel(
            line_word_frame,
            text="非空行数: 计算中...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.non_empty_lines_label.pack(anchor="w", padx=20, pady=2)

        self.total_words_label = ctk.CTkLabel(
            line_word_frame,
            text="总单词数: 计算中...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.total_words_label.pack(anchor="w", padx=20, pady=2)

        self.english_words_label = ctk.CTkLabel(
            line_word_frame,
            text="英文单词数: 计算中...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.english_words_label.pack(anchor="w", padx=20, pady=2)

        self.chinese_words_label = ctk.CTkLabel(
            line_word_frame,
            text="中文单词数: 计算中...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.chinese_words_label.pack(anchor="w", padx=20, pady=2)

        self.paragraphs_label = ctk.CTkLabel(
            line_word_frame,
            text="段落数: 计算中...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.paragraphs_label.pack(anchor="w", padx=20, pady=(2, 10))

    def _create_code_stats_tab(self):
        """创建代码统计选项卡"""
        # 获取组件字体配置
        font_name = config_manager.get("components.font", "Microsoft YaHei UI")
        font_size = config_manager.get("components.font_size", 13)

        # 创建滚动框架
        scroll_frame = ctk.CTkScrollableFrame(self.code_tab)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 代码统计框架
        code_frame = ctk.CTkFrame(scroll_frame)
        code_frame.pack(fill="x", pady=(0, 10))

        code_title = ctk.CTkLabel(
            code_frame,
            text="代码统计",
            font=ctk.CTkFont(size=font_size + 1, weight="bold", family=font_name),
        )
        code_title.pack(anchor="w", padx=10, pady=(10, 5))

        # 代码统计标签
        self.total_code_lines_label = ctk.CTkLabel(
            code_frame,
            text="总代码行数: 计算中...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.total_code_lines_label.pack(anchor="w", padx=20, pady=2)

        self.code_lines_label = ctk.CTkLabel(
            code_frame,
            text="代码行数: 计算中...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.code_lines_label.pack(anchor="w", padx=20, pady=2)

        self.comment_lines_label = ctk.CTkLabel(
            code_frame,
            text="注释行数: 计算中...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.comment_lines_label.pack(anchor="w", padx=20, pady=2)

        self.empty_lines_label = ctk.CTkLabel(
            code_frame,
            text="空行数: 计算中...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.empty_lines_label.pack(anchor="w", padx=20, pady=(2, 10))

        # 代码比例框架
        ratio_frame = ctk.CTkFrame(scroll_frame)
        ratio_frame.pack(fill="x", pady=(0, 10))

        ratio_title = ctk.CTkLabel(
            ratio_frame,
            text="代码比例",
            font=ctk.CTkFont(size=font_size + 1, weight="bold", family=font_name),
        )
        ratio_title.pack(anchor="w", padx=10, pady=(10, 5))

        # 代码比例标签
        self.code_ratio_label = ctk.CTkLabel(
            ratio_frame,
            text="代码行比例: 计算中...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.code_ratio_label.pack(anchor="w", padx=20, pady=2)

        self.comment_ratio_label = ctk.CTkLabel(
            ratio_frame,
            text="注释行比例: 计算中...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.comment_ratio_label.pack(anchor="w", padx=20, pady=2)

        self.empty_ratio_label = ctk.CTkLabel(
            ratio_frame,
            text="空行比例: 计算中...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.empty_ratio_label.pack(anchor="w", padx=20, pady=(2, 10))

    def _start_worker(self):
        """启动工作线程"""
        self.worker = StatsWorker(
            self.calculator, self.result_queue, self.progress_queue
        )
        self.worker.start()

    def _check_progress(self):
        """检查进度"""
        try:
            # 检查进度队列
            while not self.progress_queue.empty():
                progress_data = self.progress_queue.get_nowait()

                if progress_data[0] == "start":
                    self.progress_label.configure(text=progress_data[1])
                elif progress_data[0] == "progress":
                    self.progress_bar.set(progress_data[1] / 100)
                    self.progress_label.configure(text=progress_data[2])
                elif progress_data[0] == "complete":
                    self.progress_label.configure(text=progress_data[1])
                    self.cancel_button.configure(text="重新计算")
                    self.export_button.configure(state="normal")
                elif progress_data[0] == "error":
                    self.progress_label.configure(text=progress_data[1])
                    self.cancel_button.configure(text="重新计算")
                    messagebox.showerror("错误", progress_data[1])

            # 检查结果队列
            while not self.result_queue.empty():
                result_data = self.result_queue.get_nowait()

                if result_data[0] == "basic_stats":
                    self.basic_stats = result_data[1]
                    self._update_basic_stats_ui()
                elif result_data[0] == "code_stats":
                    self.code_stats = result_data[1]
                    self._update_code_stats_ui()

            # 如果工作线程还在运行，继续检查
            if self.worker and self.worker.is_alive():
                self.after(100, self._check_progress)

        except queue.Empty:
            pass

    def _update_basic_stats_ui(self):
        """更新基本统计UI"""
        # 更新字符统计
        self.total_chars_label.configure(
            text=f"总字符数: {self.basic_stats.get('total_chars', 0):,}"
        )
        self.total_chars_no_spaces_label.configure(
            text=f"不含空格字符数: {self.basic_stats.get('total_chars_no_spaces', 0):,}"
        )
        self.chinese_chars_label.configure(
            text=f"中文字符数: {self.basic_stats.get('chinese_chars', 0):,}"
        )
        self.english_chars_label.configure(
            text=f"英文字符数: {self.basic_stats.get('english_chars', 0):,}"
        )
        self.digit_chars_label.configure(
            text=f"数字字符数: {self.basic_stats.get('digit_chars', 0):,}"
        )
        self.space_chars_label.configure(
            text=f"空格/制表符数: {self.basic_stats.get('space_chars', 0):,}"
        )
        self.punctuation_chars_label.configure(
            text=f"标点符号数: {self.basic_stats.get('punctuation_chars', 0):,}"
        )
        self.other_chars_label.configure(
            text=f"其他字符数: {self.basic_stats.get('other_chars', 0):,}"
        )

        # 更新行和单词统计
        self.total_lines_label.configure(
            text=f"总行数: {self.basic_stats.get('total_lines', 0):,}"
        )
        self.non_empty_lines_label.configure(
            text=f"非空行数: {self.basic_stats.get('non_empty_lines', 0):,}"
        )
        self.total_words_label.configure(
            text=f"总单词数: {self.basic_stats.get('total_words', 0):,}"
        )
        self.english_words_label.configure(
            text=f"英文单词数: {self.basic_stats.get('english_words', 0):,}"
        )
        self.chinese_words_label.configure(
            text=f"中文单词数: {self.basic_stats.get('chinese_words', 0):,}"
        )
        self.paragraphs_label.configure(
            text=f"段落数: {self.basic_stats.get('paragraphs', 0):,}"
        )

    def _update_code_stats_ui(self):
        """更新代码统计UI"""
        # 更新代码统计
        self.total_code_lines_label.configure(
            text=f"总代码行数: {self.code_stats.get('total_code_lines', 0):,}"
        )
        self.code_lines_label.configure(
            text=f"代码行数: {self.code_stats.get('code_lines', 0):,}"
        )
        self.comment_lines_label.configure(
            text=f"注释行数: {self.code_stats.get('comment_lines', 0):,}"
        )
        self.empty_lines_label.configure(
            text=f"空行数: {self.code_stats.get('empty_lines', 0):,}"
        )

        # 计算比例
        total = self.code_stats.get("total_code_lines", 1)
        if total > 0:
            code_ratio = self.code_stats.get("code_lines", 0) / total * 100
            comment_ratio = self.code_stats.get("comment_lines", 0) / total * 100
            empty_ratio = self.code_stats.get("empty_lines", 0) / total * 100

            self.code_ratio_label.configure(text=f"代码行比例: {code_ratio:.1f}%")
            self.comment_ratio_label.configure(text=f"注释行比例: {comment_ratio:.1f}%")
            self.empty_ratio_label.configure(text=f"空行比例: {empty_ratio:.1f}%")

    def _cancel_calculation(self):
        """取消计算"""
        if self.worker and self.worker.is_alive():
            self.worker.stop()
            self.progress_label.configure(text="正在取消...")
        else:
            # 重新开始计算
            self.basic_stats = {}
            self.code_stats = {}
            self.progress_bar.set(0)
            self.progress_label.configure(text="准备计算...")
            self.cancel_button.configure(text="取消")
            self.export_button.configure(state="disabled")

            # 重置UI
            self._reset_ui()

            # 启动新的工作线程
            self._start_worker()
            self._check_progress()

    def _reset_ui(self):
        """重置UI"""
        # 重置基本统计标签
        self.total_chars_label.configure(text="总字符数: 计算中...")
        self.total_chars_no_spaces_label.configure(text="不含空格字符数: 计算中...")
        self.chinese_chars_label.configure(text="中文字符数: 计算中...")
        self.english_chars_label.configure(text="英文字符数: 计算中...")
        self.digit_chars_label.configure(text="数字字符数: 计算中...")
        self.space_chars_label.configure(text="空格/制表符数: 计算中...")
        self.punctuation_chars_label.configure(text="标点符号数: 计算中...")
        self.other_chars_label.configure(text="其他字符数: 计算中...")

        self.total_lines_label.configure(text="总行数: 计算中...")
        self.non_empty_lines_label.configure(text="非空行数: 计算中...")
        self.total_words_label.configure(text="总单词数: 计算中...")
        self.english_words_label.configure(text="英文单词数: 计算中...")
        self.chinese_words_label.configure(text="中文单词数: 计算中...")
        self.paragraphs_label.configure(text="段落数: 计算中...")

        # 重置代码统计标签（如果存在）
        if hasattr(self, "total_code_lines_label"):
            self.total_code_lines_label.configure(text="总代码行数: 计算中...")
            self.code_lines_label.configure(text="代码行数: 计算中...")
            self.comment_lines_label.configure(text="注释行数: 计算中...")
            self.empty_lines_label.configure(text="空行数: 计算中...")

            self.code_ratio_label.configure(text="代码行比例: 计算中...")
            self.comment_ratio_label.configure(text="注释行比例: 计算中...")
            self.empty_ratio_label.configure(text="空行比例: 计算中...")

    def _export_report(self):
        """导出报告"""
        # 生成预设文件名
        if self.file_path:
            # 如果有文件路径，使用文件名加上"_统计报告"后缀
            base_name = os.path.splitext(os.path.basename(self.file_path))[0]
            initial_file = f"{base_name}_统计报告.txt"
        else:
            # 如果没有文件路径，使用默认名称加上当前时间戳
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            initial_file = f"文档统计报告_{timestamp}.txt"

        # 选择保存位置
        file_path = filedialog.asksaveasfilename(
            title="保存统计报告",
            initialfile=initial_file,
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                # 写入文件信息
                f.write("=" * 50 + "\n")
                f.write("文档统计报告\n")
                f.write("=" * 50 + "\n\n")

                # 文件信息
                f.write("文件信息\n")
                f.write("-" * 30 + "\n")
                file_name = (
                    os.path.basename(self.file_path) if self.file_path else "无标题"
                )
                f.write(f"文件名: {file_name}\n")

                if self.file_path:
                    f.write(f"路径: {self.file_path}\n")
                    try:
                        file_size = os.path.getsize(self.file_path)
                        file_size_str = self._format_file_size(file_size)
                        f.write(f"大小: {file_size_str}\n")

                        mod_time = os.path.getmtime(self.file_path)
                        mod_time_str = datetime.fromtimestamp(mod_time).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                        f.write(f"修改时间: {mod_time_str}\n")
                    except:
                        pass

                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                # 基本统计
                if self.basic_stats:
                    f.write("基本统计\n")
                    f.write("-" * 30 + "\n")
                    f.write(f"总字符数: {self.basic_stats.get('total_chars', 0):,}\n")
                    f.write(
                        f"不含空格字符数: {self.basic_stats.get('total_chars_no_spaces', 0):,}\n"
                    )
                    f.write(
                        f"中文字符数: {self.basic_stats.get('chinese_chars', 0):,}\n"
                    )
                    f.write(
                        f"英文字符数: {self.basic_stats.get('english_chars', 0):,}\n"
                    )
                    f.write(f"数字字符数: {self.basic_stats.get('digit_chars', 0):,}\n")
                    f.write(
                        f"空格/制表符数: {self.basic_stats.get('space_chars', 0):,}\n"
                    )
                    f.write(
                        f"标点符号数: {self.basic_stats.get('punctuation_chars', 0):,}\n"
                    )
                    f.write(
                        f"其他字符数: {self.basic_stats.get('other_chars', 0):,}\n\n"
                    )

                    f.write("行和单词统计\n")
                    f.write("-" * 30 + "\n")
                    f.write(f"总行数: {self.basic_stats.get('total_lines', 0):,}\n")
                    f.write(
                        f"非空行数: {self.basic_stats.get('non_empty_lines', 0):,}\n"
                    )
                    f.write(f"总单词数: {self.basic_stats.get('total_words', 0):,}\n")
                    f.write(
                        f"英文单词数: {self.basic_stats.get('english_words', 0):,}\n"
                    )
                    f.write(
                        f"中文单词数: {self.basic_stats.get('chinese_words', 0):,}\n"
                    )
                    f.write(f"段落数: {self.basic_stats.get('paragraphs', 0):,}\n\n")

                # 代码统计
                if self.code_stats:
                    f.write("代码统计\n")
                    f.write("-" * 30 + "\n")
                    f.write(
                        f"总代码行数: {self.code_stats.get('total_code_lines', 0):,}\n"
                    )
                    f.write(f"代码行数: {self.code_stats.get('code_lines', 0):,}\n")
                    f.write(f"注释行数: {self.code_stats.get('comment_lines', 0):,}\n")
                    f.write(f"空行数: {self.code_stats.get('empty_lines', 0):,}\n\n")

                    # 计算比例
                    total = self.code_stats.get("total_code_lines", 1)
                    if total > 0:
                        code_ratio = self.code_stats.get("code_lines", 0) / total * 100
                        comment_ratio = (
                            self.code_stats.get("comment_lines", 0) / total * 100
                        )
                        empty_ratio = (
                            self.code_stats.get("empty_lines", 0) / total * 100
                        )

                        f.write("代码比例\n")
                        f.write("-" * 30 + "\n")
                        f.write(f"代码行比例: {code_ratio:.1f}%\n")
                        f.write(f"注释行比例: {comment_ratio:.1f}%\n")
                        f.write(f"空行比例: {empty_ratio:.1f}%\n")

            messagebox.showinfo("成功", f"统计报告已保存到:\n{file_path}")

        except Exception as e:
            messagebox.showerror("错误", f"保存报告失败:\n{str(e)}")

    def _format_file_size(self, size_bytes):
        """格式化文件大小"""
        if size_bytes < 1024:
            return f"{size_bytes} 字节"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

    def _center_window(self):
        """居中显示窗口"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = width // 2
        y = height // 6
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _toggle_fullscreen(self):
        """切换全屏模式"""
        if self.is_fullscreen:
            # 退出全屏
            self.attributes("-fullscreen", False)
            self.is_fullscreen = False
            self.fullscreen_button.configure(text="全屏")
            # 恢复原始窗口大小
            self.geometry("500x400")
            # 重新居中窗口
            self._center_window()
        else:
            # 进入全屏
            self.attributes("-fullscreen", True)
            self.is_fullscreen = True
            self.fullscreen_button.configure(text="退出全屏")

    def _on_tab_double_click(self, event):
        """处理基本统计选项卡双击事件，切换全屏"""
        # 直接切换全屏，因为事件已经绑定到基本统计按钮
        self._toggle_fullscreen()

    def _on_escape(self, event=None):
        """处理ESC键事件"""
        if self.is_fullscreen:
            # 如果是全屏模式，则退出全屏
            self._toggle_fullscreen()
        else:
            # 否则关闭对话框
            self.destroy()


def show_document_stats_dialog(parent):
    """显示文档统计信息对话框

    Args:
        parent: 父窗口
    """
    # 获取当前文本内容
    text_content = parent.text_area.get("1.0", "end-1c")
    file_path = parent.current_file_path

    # 创建并显示对话框
    dialog = DocumentStatsDialog(parent, text_content, file_path)

    # 确保窗口获得焦点
    dialog.focus_set()

    # 按ESC键关闭窗口
    dialog.bind("<Escape>", lambda e: dialog.destroy())
