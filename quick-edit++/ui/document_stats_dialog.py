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
import gc
from datetime import datetime
from pathlib import Path
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
from config.config_manager import config_manager


class StatsCalculator:
    """文档统计计算器类"""

    # 预编译正则表达式以提高性能
    CHINESE_CHARS_PATTERN = re.compile(r"[\u4e00-\u9fff]")
    ENGLISH_CHARS_PATTERN = re.compile(r"[a-zA-Z]")
    DIGIT_CHARS_PATTERN = re.compile(r"[0-9]")
    SPACE_CHARS_PATTERN = re.compile(r"[ \t]")
    PUNCTUATION_CHARS_PATTERN = re.compile(r"[^\w\s\u4e00-\u9fff]")
    ENGLISH_WORDS_PATTERN = re.compile(r"\b[a-zA-Z]+\b")
    CHINESE_WORDS_PATTERN = re.compile(r"[\u4e00-\u9fff]+")
    PARAGRAPH_PATTERN = re.compile(r"\n\s*\n")

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
        # 移除初始化时的耗时操作，改为按需计算
        self.total_lines = 0
        self.total_chars = 0

        # 预编译注释模式以提高性能
        self._compiled_comment_patterns = None

    # 已移除is_code_file方法 - 所有文件都被统一处理，不需要区分代码文件

    def get_comment_patterns(self):
        """
        获取注释模式
        使用通用注释模式，适用于所有文件类型
        """
        if self._compiled_comment_patterns is not None:
            return self._compiled_comment_patterns

        # 通用注释模式，适用于大多数编程语言
        patterns = [
            r"//.*$",  # C风格单行注释
            r"/\*.*?\*/",  # C风格多行注释
            r"#.*$",  # Python/Shell风格注释
            r"<!--.*?-->",  # HTML/XML注释
            r"--.*$",  # SQL注释
            r"%.*$",  # MATLAB注释
            r'""".*?"""',  # Python多行注释
            r"'''.*?'''",  # Python多行注释
            r"::.*$",  # Windows批处理注释
            r"rem.*$",  # DOS批处理注释
            r"@REM.*$",  # DOS批处理注释
            r"\{.*?\}",  # Pascal风格注释
            r"\(\*.*?\*\)",  # Pascal风格注释
        ]

        # 预编译所有模式
        self._compiled_comment_patterns = [
            re.compile(pattern, re.MULTILINE | re.DOTALL) for pattern in patterns
        ]
        return self._compiled_comment_patterns

    def _process_text_in_batches(
        self,
        text,
        batch_size,
        process_func,
        progress_callback=None,
        progress_range=(0, 100),
        progress_message="处理中...",
    ):
        """
        批处理文本的通用方法，优化内存使用

        Args:
            text (str): 要处理的文本
            batch_size (int): 每批处理的大小
            process_func (callable): 处理每批文本的函数，接收批次文本，返回处理结果
            progress_callback (callable, optional): 进度回调函数
            progress_range (tuple, optional): 进度范围 (start, end)
            progress_message (str, optional): 进度消息

        Returns:
            处理结果的汇总
        """
        total_chars = len(text)
        start_progress, end_progress = progress_range
        last_progress_update = start_progress
        result = None

        # 分批处理，减少内存占用
        for i in range(0, total_chars, batch_size):
            batch_text = text[i : i + batch_size]
            batch_result = process_func(batch_text)

            # 汇总结果
            if result is None:
                result = batch_result
            else:
                # 假设batch_result是一个字典，我们需要将值相加
                for key in batch_result:
                    if key in result:
                        result[key] += batch_result[key]

            # 清除批处理文本的引用，帮助垃圾回收
            del batch_text
            del batch_result

            # 更新进度，但减少更新频率
            if progress_callback and total_chars > 0:
                progress = start_progress + int(
                    (i + batch_size) / total_chars * (end_progress - start_progress)
                )
                # 只在进度变化超过5%时才更新
                if progress - last_progress_update >= 5:
                    progress_callback(progress, f"{progress_message} {progress}%")
                    last_progress_update = progress

                    # 在进度更新时触发垃圾回收，释放内存
                    if i % (batch_size * 5) == 0:  # 每处理5个批次触发一次垃圾回收
                        gc.collect()

        # 最终垃圾回收
        gc.collect()
        return result if result is not None else {}

    def _count_chars_in_batch(self, batch_text):
        """
        批处理统计字符类型

        Args:
            batch_text (str): 批次文本

        Returns:
            dict: 字符统计结果
        """
        return {
            "chinese_chars": len(self.CHINESE_CHARS_PATTERN.findall(batch_text)),
            "english_chars": len(self.ENGLISH_CHARS_PATTERN.findall(batch_text)),
            "digit_chars": len(self.DIGIT_CHARS_PATTERN.findall(batch_text)),
            "space_chars": len(self.SPACE_CHARS_PATTERN.findall(batch_text)),
            "punctuation_chars": len(
                self.PUNCTUATION_CHARS_PATTERN.findall(batch_text)
            ),
        }

    def _count_words_in_batch(self, batch_text):
        """
        批处理统计单词

        Args:
            batch_text (str): 批次文本

        Returns:
            dict: 单词统计结果
        """
        return {
            "english_words": len(self.ENGLISH_WORDS_PATTERN.findall(batch_text)),
            "chinese_words": len(self.CHINESE_WORDS_PATTERN.findall(batch_text)),
        }

    def _process_lines_in_batches(
        self,
        lines,
        batch_size,
        process_func,
        progress_callback=None,
        progress_range=(0, 100),
        progress_message="处理中...",
    ):
        """
        批处理行的通用方法，用于代码统计，优化内存使用和UI响应性

        Args:
            lines (list): 要处理的行列表
            batch_size (int): 每批处理的大小
            process_func (callable): 处理每批行的函数，接收批次行，返回处理结果
            progress_callback (callable, optional): 进度回调函数
            progress_range (tuple, optional): 进度范围 (start, end)
            progress_message (str, optional): 进度消息

        Returns:
            处理结果的汇总
        """
        total_lines = len(lines)
        start_progress, end_progress = progress_range
        last_progress_update = start_progress
        result = None

        # 减小批处理大小，提高进度更新频率，改善UI响应性
        adjusted_batch_size = min(batch_size, 100)  # 限制最大批处理大小为100

        # 分批处理，减少内存占用
        for i in range(0, total_lines, adjusted_batch_size):
            batch_lines = lines[i : i + adjusted_batch_size]
            batch_result = process_func(batch_lines)

            # 汇总结果
            if result is None:
                result = batch_result
            else:
                # 假设batch_result是一个字典，我们需要将值相加
                for key in batch_result:
                    if key in result:
                        result[key] += batch_result[key]

            # 清除批处理行的引用，帮助垃圾回收
            del batch_lines
            del batch_result

            # 更新进度，提高更新频率以改善UI响应性
            if progress_callback and total_lines > 0:
                progress = start_progress + int(
                    (i + adjusted_batch_size)
                    / total_lines
                    * (end_progress - start_progress)
                )
                # 降低进度更新阈值到2%，更频繁更新UI
                if progress - last_progress_update >= 2:
                    progress_callback(progress, f"{progress_message} {progress}%")
                    last_progress_update = progress

                    # 更频繁地触发垃圾回收，释放内存
                    if (
                        i % (adjusted_batch_size * 3) == 0
                    ):  # 每处理3个批次触发一次垃圾回收
                        gc.collect()

        # 最终垃圾回收
        gc.collect()
        return result if result is not None else {}

    def _count_code_lines_in_batch(self, batch_lines):
        """
        批处理统计代码行

        Args:
            batch_lines (list): 批次行列表

        Returns:
            dict: 代码行统计结果
        """
        comment_patterns = self.get_comment_patterns()
        code_lines = 0
        comment_lines = 0
        blank_lines = 0  # 重命名为blank_lines以保持与其他方法一致

        for line in batch_lines:
            stripped_line = line.strip()

            # 空行
            if not stripped_line:
                blank_lines += 1
                continue

            # 检查是否为注释行 - 使用预编译的正则表达式提高性能
            is_comment = False
            for compiled_pattern in comment_patterns:
                if compiled_pattern.search(line):
                    is_comment = True
                    break

            if is_comment:
                comment_lines += 1
            else:
                code_lines += 1

        return {
            "code_lines": code_lines,
            "comment_lines": comment_lines,
            "blank_lines": blank_lines,  # 重命名为blank_lines以保持与其他方法一致
        }

    def calculate_basic_stats(self, progress_callback=None):
        """
        计算基本统计信息

        Args:
            progress_callback: 进度回调函数

        Returns:
            dict: 包含所有基本统计信息的字典
        """
        # 处理空文档情况
        if not self.text_content:
            return {
                "total_chars": 0,
                "total_chars_no_spaces": 0,
                "total_lines": 0,
                "non_empty_lines": 0,
                "chinese_chars": 0,
                "english_chars": 0,
                "digit_chars": 0,
                "space_chars": 0,
                "punctuation_chars": 0,
                "other_chars": 0,
                "total_words": 0,
                "english_words": 0,
                "chinese_words": 0,
                "paragraphs": 0,
                "total_code_lines": 0,
                "code_lines": 0,
                "comment_lines": 0,
                "blank_lines": 0,
                "effective_lines": 0,
                "comment_ratio": 0.0,
                "blank_ratio": 0.0,
                "effective_ratio": 0.0,
            }

        stats = {}
        text = self.text_content
        total_chars = len(text)

        # 初始化基本计数
        if progress_callback:
            progress_callback(5, "初始化统计...")

        # 基本统计
        self.total_chars = total_chars
        self.total_lines = len(text.splitlines())

        stats["total_chars"] = self.total_chars
        stats["total_chars_no_spaces"] = len(text.replace(" ", "").replace("\t", ""))
        stats["total_lines"] = self.total_lines

        if progress_callback:
            progress_callback(15, "统计行数...")

        # 非空行数
        non_empty_lines = 0
        lines = text.splitlines()
        total_lines = len(lines)

        # 减小批处理大小，增加进度更新频率，改善UI响应性
        batch_size = max(100, total_lines // 20)  # 减小批处理大小，增加批次数
        last_progress_update = 0

        for i in range(0, total_lines, batch_size):
            batch_end = min(i + batch_size, total_lines)
            for j in range(i, batch_end):
                if lines[j].strip():
                    non_empty_lines += 1

            # 增加进度更新频率，只在进度变化超过2%时才更新
            if progress_callback:
                progress = 15 + int((j / total_lines) * 25)  # 15%到40%
                if progress - last_progress_update >= 2:  # 降低阈值到2%，更频繁更新
                    progress_callback(progress, f"统计行数... {progress}%")
                    last_progress_update = progress

        stats["non_empty_lines"] = non_empty_lines

        if progress_callback:
            progress_callback(40, "统计字符类型...")

        # 字符类型统计 - 使用批处理方法提高性能
        if total_chars > 50000:  # 降低阈值，更多文件使用批处理
            char_stats = self._process_text_in_batches(
                text,
                20000,
                self._count_chars_in_batch,  # 减小批处理大小
                progress_callback,
                (40, 60),
                "统计字符...",
            )
            stats.update(char_stats)
        else:
            # 小文件直接处理
            stats["chinese_chars"] = len(self.CHINESE_CHARS_PATTERN.findall(text))
            stats["english_chars"] = len(self.ENGLISH_CHARS_PATTERN.findall(text))
            stats["digit_chars"] = len(self.DIGIT_CHARS_PATTERN.findall(text))
            stats["space_chars"] = len(self.SPACE_CHARS_PATTERN.findall(text))
            stats["punctuation_chars"] = len(
                self.PUNCTUATION_CHARS_PATTERN.findall(text)
            )

        # 计算其他字符数
        stats["other_chars"] = (
            stats["total_chars"]
            - stats.get("chinese_chars", 0)
            - stats.get("english_chars", 0)
            - stats.get("digit_chars", 0)
            - stats.get("space_chars", 0)
            - stats.get("punctuation_chars", 0)
        )

        if progress_callback:
            progress_callback(60, "统计单词...")

        # 单词统计（中英文）- 使用批处理方法提高性能
        if total_chars > 50000:  # 降低阈值，更多文件使用批处理
            word_stats = self._process_text_in_batches(
                text,
                20000,
                self._count_words_in_batch,  # 减小批处理大小
                progress_callback,
                (60, 80),
                "统计单词...",
            )
            stats.update(word_stats)
            # 计算总单词数
            stats["total_words"] = word_stats.get("english_words", 0) + word_stats.get(
                "chinese_words", 0
            )
        else:
            # 小文件直接处理
            english_words = len(self.ENGLISH_WORDS_PATTERN.findall(text))
            chinese_words = len(self.CHINESE_WORDS_PATTERN.findall(text))
            stats["english_words"] = english_words
            stats["chinese_words"] = chinese_words
            # 计算总单词数
            stats["total_words"] = english_words + chinese_words

        if progress_callback:
            progress_callback(80, "统计段落...")

        # 段落统计 - 使用预编译的正则表达式提高性能
        paragraphs = self.PARAGRAPH_PATTERN.split(text.strip())
        stats["paragraphs"] = len([p for p in paragraphs if p.strip()])

        # 所有文件统一处理，不再需要代码文件标志

        if progress_callback:
            progress_callback(100, "基本统计完成")

        return stats

    def calculate_code_stats(self, progress_callback=None):
        """
        计算文档统计信息（简化版，适用于所有文件）

        Args:
            progress_callback: 进度回调函数

        Returns:
            dict: 包含所有文档统计信息的字典
        """
        # 处理空文档情况
        if not self.text_content:
            return {
                "total_code_lines": 0,
                "code_lines": 0,
                "comment_lines": 0,
                "blank_lines": 0,
                "effective_lines": 0,
                "comment_ratio": 0.0,
                "blank_ratio": 0.0,
                "effective_ratio": 0.0,
            }

        lines = self.text_content.splitlines()
        total_lines = len(lines)

        if progress_callback:
            progress_callback(0, "开始分析文档...")

        # 使用批处理方法统计文档行，减小批处理大小，增加进度更新频率
        code_stats = self._process_lines_in_batches(
            lines,
            max(50, total_lines // 20),
            self._count_code_lines_in_batch,  # 减小批处理大小，增加批次数
            progress_callback,
            (0, 100),
            "分析文档中...",
        )

        # 添加总行数
        code_stats["total_code_lines"] = total_lines

        # 计算比率
        if total_lines > 0:
            code_stats["comment_ratio"] = (
                code_stats.get("comment_lines", 0) / total_lines
            )
            code_stats["blank_ratio"] = code_stats.get("blank_lines", 0) / total_lines
            code_stats["effective_ratio"] = (
                code_stats.get("effective_lines", 0) / total_lines
            )
        else:
            code_stats["comment_ratio"] = 0.0
            code_stats["blank_ratio"] = 0.0
            code_stats["effective_ratio"] = 0.0

        if progress_callback:
            progress_callback(100, "文档分析完成")

        return code_stats


class StatsWorker(threading.Thread):
    """统计工作线程类"""

    def __init__(self, text_content, file_path, result_queue, progress_queue):
        """
        初始化工作线程

        Args:
            text_content (str): 要分析的文本内容
            file_path (str, optional): 文件路径，用于代码分析
            result_queue (queue.Queue): 结果队列
            progress_queue (queue.Queue): 进度队列
        """
        super().__init__()
        self.text_content = text_content
        self.file_path = file_path
        self.result_queue = result_queue
        self.progress_queue = progress_queue
        self._stop_event = threading.Event()
        self.calculator = None  # 延迟初始化

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

            # 延迟初始化计算器，避免在主线程中耗时
            self.progress_queue.put(("progress", 1, "初始化计算器..."))
            self.calculator = StatsCalculator(self.text_content, self.file_path)

            if self.stopped():
                return

            # 计算基本统计
            self.progress_queue.put(("progress", 5, "计算基本统计信息..."))
            basic_stats = self.calculator.calculate_basic_stats(
                lambda p, msg: self.progress_queue.put(("progress", p, msg))
            )
            self.result_queue.put(("basic_stats", basic_stats))

            if self.stopped():
                return

            # 计算文档统计（适用于所有文件）
            self.progress_queue.put(("progress", 60, "分析文档结构..."))
            code_stats = self.calculator.calculate_code_stats(
                lambda p, msg: self.progress_queue.put(
                    ("progress", 60 + p * 0.4, msg)  # 60%到100%
                )
            )
            self.result_queue.put(("code_stats", code_stats))

            # 发送完成信号
            self.progress_queue.put(("progress", 100, "计算完成"))
            self.progress_queue.put(("complete", "统计完成"))

        except Exception as e:
            # 确保异常信息也被放入队列，而不是直接调用Tkinter组件
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
        # 移除计算器的初始化，将在工作线程中创建
        self.calculator = None

        # 创建全屏状态变量
        self.fullscreen_var = tk.BooleanVar(value=False)

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

        # 强制更新窗口，确保所有UI元素都显示出来
        self.update_idletasks()
        self.update()

        # 确保窗口先显示出来，然后再开始统计计算
        self.after(100, self._start_calculation)

    def _init_ui(self):
        """初始化用户界面"""
        # 设置窗口属性
        self.title("文档统计信息")
        self.width = 700  # 宽度
        self.height = 600  # 高度
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

        # 状态标签
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="准备计算...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.status_label.pack(anchor="w", padx=10, pady=(10, 5))

        # 创建选项卡视图
        self.tabview = ctk.CTkTabview(main_frame)
        self.tabview.pack(fill="both", expand=True, pady=(0, 10))

        # 基本统计选项卡
        self.basic_tab = self.tabview.add("基本统计")
        self._create_basic_stats_tab()

        # 移除代码统计选项卡相关代码，因为已集成到基本统计中

        # 绑定双击事件到选项卡的segmented_button内部的按钮，用于切换全屏
        # 注意：现在只有基本统计选项卡，所以不需要处理代码统计选项卡的全屏切换
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

        # 绑定ESC键，用于退出全屏或关闭窗口
        self.bind("<Escape>", self._on_escape)

        # 居中显示窗口
        self.parent.center_window(self, self.width, self.height)

    def _start_calculation(self):
        """开始统计计算（确保窗口已显示）"""
        # 强制刷新UI，确保所有标签都显示出来
        self.update_idletasks()

        # 设置初始状态，确保UI能够立即响应
        self.status_label.configure(text="正在初始化计算器...")
        self.update_idletasks()
        self.update()  # 强制立即更新UI

        # 启动工作线程
        self._start_worker()

        # 开始检查进度，减少延迟，更快响应
        self.after(50, self._check_progress)  # 减少延迟，更快响应

    def _create_basic_stats_tab(self):
        """创建基本统计选项卡"""
        # 获取组件字体配置
        font_name = config_manager.get("components.font", "Microsoft YaHei UI")
        font_size = config_manager.get("components.font_size", 13)

        # 创建滚动框架用于显示统计结果，设置滚动条宽度为12像素
        scroll_frame = ctk.CTkScrollableFrame(self.basic_tab)
        # 直接设置内部滚动条的宽度
        scroll_frame._scrollbar.configure(width=18)
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

        # 单词统计框架
        word_frame = ctk.CTkFrame(scroll_frame)
        word_frame.pack(fill="x", pady=(0, 10))

        word_title = ctk.CTkLabel(
            word_frame,
            text="单词统计",
            font=ctk.CTkFont(size=font_size + 1, weight="bold", family=font_name),
        )
        word_title.pack(anchor="w", padx=10, pady=(10, 5))

        # 单词统计标签
        self.total_words_label = ctk.CTkLabel(
            word_frame,
            text="总单词数: 计算中...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.total_words_label.pack(anchor="w", padx=20, pady=2)

        self.english_words_label = ctk.CTkLabel(
            word_frame,
            text="英文单词数: 计算中...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.english_words_label.pack(anchor="w", padx=20, pady=2)

        self.chinese_words_label = ctk.CTkLabel(
            word_frame,
            text="中文单词数: 计算中...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.chinese_words_label.pack(anchor="w", padx=20, pady=(2, 10))

        # 行统计框架
        line_frame = ctk.CTkFrame(scroll_frame)
        line_frame.pack(fill="x", pady=(0, 10))

        line_title = ctk.CTkLabel(
            line_frame,
            text="行统计",
            font=ctk.CTkFont(size=font_size + 1, weight="bold", family=font_name),
        )
        line_title.pack(anchor="w", padx=10, pady=(10, 5))

        # 行统计标签
        self.total_lines_label = ctk.CTkLabel(
            line_frame,
            text="总行数: 计算中...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.total_lines_label.pack(anchor="w", padx=20, pady=2)

        self.non_empty_lines_label = ctk.CTkLabel(
            line_frame,
            text="非空行数: 计算中...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.non_empty_lines_label.pack(anchor="w", padx=20, pady=2)

        self.code_lines_label = ctk.CTkLabel(
            line_frame,
            text="有效行数: 计算中...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.code_lines_label.pack(anchor="w", padx=20, pady=2)

        self.comment_lines_label = ctk.CTkLabel(
            line_frame,
            text="注释行数: 计算中...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.comment_lines_label.pack(anchor="w", padx=20, pady=2)

        self.empty_lines_label = ctk.CTkLabel(
            line_frame,
            text="空行数: 计算中...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.empty_lines_label.pack(anchor="w", padx=20, pady=2)

        self.paragraphs_label = ctk.CTkLabel(
            line_frame,
            text="段落数: 计算中...",
            font=ctk.CTkFont(size=font_size, family=font_name),
        )
        self.paragraphs_label.pack(anchor="w", padx=20, pady=(2, 10))

    # 移除_create_code_stats_tab方法，因为已集成到基本统计中

    def _start_worker(self):
        """启动工作线程"""
        self.worker = StatsWorker(
            self.text_content, self.file_path, self.result_queue, self.progress_queue
        )
        self.worker.start()

    def _check_progress(self):
        """检查进度和结果队列 - 高度优化版本，最大程度避免阻塞UI线程"""
        # 减少UI更新频率，避免过于频繁的更新
        self.last_ui_update = getattr(self, "last_ui_update", 0)
        current_time = time.time()

        # 进一步降低UI更新频率为每100ms一次，提高响应性
        should_update_ui = current_time - self.last_ui_update >= 0.1

        # 记录上次处理的进度，避免重复更新相同的进度
        last_progress = getattr(self, "last_progress", -1)

        try:
            # 进一步限制每次处理的消息数量，最大程度避免阻塞UI线程
            max_messages_per_check = 1  # 每次只处理1条消息，立即返回
            messages_processed = 0

            # 处理进度队列中的消息，但严格限制数量
            while (
                not self.progress_queue.empty()
                and messages_processed < max_messages_per_check
            ):
                try:
                    msg_type, *msg_data = self.progress_queue.get_nowait()
                    messages_processed += 1

                    if msg_type == "start":
                        # 开始计算，总是更新UI
                        self.status_label.configure(text=msg_data[0])
                        self.last_ui_update = current_time
                    elif msg_type == "progress":
                        # 更新进度，但只在进度有显著变化时更新UI
                        progress, message = msg_data
                        if (
                            abs(progress - last_progress) >= 1
                        ):  # 进一步降低阈值到1%，最频繁更新
                            self.status_label.configure(text=message)
                            last_progress = progress
                            self.last_ui_update = current_time
                    elif msg_type == "complete":
                        # 计算完成，处理所有结果队列中的消息
                        self._process_all_results()

                        # 更新状态和按钮
                        self.status_label.configure(text=msg_data[0])
                        self.cancel_button.configure(text="关闭", command=self.destroy)
                        self.export_button.configure(state="normal")
                        return
                    elif msg_type == "error":
                        # 发生错误
                        self.status_label.configure(text=msg_data[0])
                        self.cancel_button.configure(text="关闭", command=self.destroy)
                        # 使用after在主线程中显示错误消息
                        self.after(0, lambda: messagebox.showerror("错误", msg_data[0]))
                        return
                except queue.Empty:
                    break

            # 如果还有进度消息未处理，立即再次检查，但使用after避免阻塞
            if (
                not self.progress_queue.empty()
                and messages_processed >= max_messages_per_check
            ):
                # 更短的延迟，更快响应
                self.after(10, self._check_progress)
                return

            # 处理结果队列中的消息，但严格限制数量
            messages_processed = 0
            while (
                not self.result_queue.empty()
                and messages_processed < max_messages_per_check
            ):
                try:
                    result_type, data = self.result_queue.get_nowait()
                    messages_processed += 1

                    if result_type == "basic_stats":
                        # 基本统计结果
                        self.basic_stats = data
                        # 使用after确保在主线程中更新UI
                        self.after(0, self._update_basic_stats_ui)
                    elif result_type == "code_stats":
                        # 代码统计结果
                        self.code_stats = data
                        # 使用after确保在主线程中更新UI
                        self.after(0, self._update_code_stats_ui)
                except queue.Empty:
                    break

            # 如果还有结果消息未处理，立即再次检查，但使用after避免阻塞
            if (
                not self.result_queue.empty()
                and messages_processed >= max_messages_per_check
            ):
                # 更短的延迟，更快响应
                self.after(10, self._check_progress)
                return

        except Exception as e:
            messagebox.showerror("错误", f"处理进度时发生错误: {str(e)}")

        # 更新UI时间戳和进度记录
        self.last_ui_update = current_time
        self.last_progress = last_progress

        # 继续检查进度，进一步降低频率到100ms，最大程度提高响应性
        self.after(100, self._check_progress)

    def _process_all_results(self):
        """处理所有结果队列中的消息"""
        while not self.result_queue.empty():
            try:
                result_type, data = self.result_queue.get_nowait()

                if result_type == "basic_stats":
                    # 基本统计结果
                    self.basic_stats = data
                    # 使用after确保在主线程中更新UI
                    self.after(0, self._update_basic_stats_ui)
                elif result_type == "code_stats":
                    # 代码统计结果
                    self.code_stats = data
                    # 使用after确保在主线程中更新UI
                    self.after(0, self._update_code_stats_ui)
            except queue.Empty:
                break

    def _update_basic_stats_ui(self):
        """更新基本统计UI"""
        # 确保UI更新在主线程中执行
        if not threading.current_thread() is threading.main_thread():
            self.after(0, self._update_basic_stats_ui)
            return

        # 更新字符统计
        total_chars = self.basic_stats.get("total_chars", "计算中...")
        if isinstance(total_chars, int):
            total_chars = f"{total_chars:,}"
        self.total_chars_label.configure(text=f"总字符数: {total_chars}")

        total_chars_no_spaces = self.basic_stats.get(
            "total_chars_no_spaces", "计算中..."
        )
        if isinstance(total_chars_no_spaces, int):
            total_chars_no_spaces = f"{total_chars_no_spaces:,}"
        self.total_chars_no_spaces_label.configure(
            text=f"不含空格字符数: {total_chars_no_spaces}"
        )

        chinese_chars = self.basic_stats.get("chinese_chars", "计算中...")
        if isinstance(chinese_chars, int):
            chinese_chars = f"{chinese_chars:,}"
        self.chinese_chars_label.configure(text=f"中文字符数: {chinese_chars}")

        english_chars = self.basic_stats.get("english_chars", "计算中...")
        if isinstance(english_chars, int):
            english_chars = f"{english_chars:,}"
        self.english_chars_label.configure(text=f"英文字符数: {english_chars}")

        digit_chars = self.basic_stats.get("digit_chars", "计算中...")
        if isinstance(digit_chars, int):
            digit_chars = f"{digit_chars:,}"
        self.digit_chars_label.configure(text=f"数字字符数: {digit_chars}")

        space_chars = self.basic_stats.get("space_chars", "计算中...")
        if isinstance(space_chars, int):
            space_chars = f"{space_chars:,}"
        self.space_chars_label.configure(text=f"空格/制表符数: {space_chars}")

        punctuation_chars = self.basic_stats.get("punctuation_chars", "计算中...")
        if isinstance(punctuation_chars, int):
            punctuation_chars = f"{punctuation_chars:,}"
        self.punctuation_chars_label.configure(text=f"标点符号数: {punctuation_chars}")

        other_chars = self.basic_stats.get("other_chars", "计算中...")
        if isinstance(other_chars, int):
            other_chars = f"{other_chars:,}"
        self.other_chars_label.configure(text=f"其他字符数: {other_chars}")

        # 更新行和单词统计
        total_lines = self.basic_stats.get("total_lines", "计算中...")
        if isinstance(total_lines, int):
            total_lines = f"{total_lines:,}"
        self.total_lines_label.configure(text=f"总行数: {total_lines}")

        non_empty_lines = self.basic_stats.get("non_empty_lines", "计算中...")
        if isinstance(non_empty_lines, int):
            non_empty_lines = f"{non_empty_lines:,}"
        self.non_empty_lines_label.configure(text=f"非空行数: {non_empty_lines}")

        total_words = self.basic_stats.get("total_words", "计算中...")
        if isinstance(total_words, int):
            total_words = f"{total_words:,}"
        self.total_words_label.configure(text=f"总单词数: {total_words}")

        english_words = self.basic_stats.get("english_words", "计算中...")
        if isinstance(english_words, int):
            english_words = f"{english_words:,}"
        self.english_words_label.configure(text=f"英文单词数: {english_words}")

        chinese_words = self.basic_stats.get("chinese_words", "计算中...")
        if isinstance(chinese_words, int):
            chinese_words = f"{chinese_words:,}"
        self.chinese_words_label.configure(text=f"中文单词数: {chinese_words}")

        paragraphs = self.basic_stats.get("paragraphs", "计算中...")
        if isinstance(paragraphs, int):
            paragraphs = f"{paragraphs:,}"
        self.paragraphs_label.configure(text=f"段落数: {paragraphs}")

        # 更新文档统计（如果已有数据）
        if hasattr(self, "code_stats") and self.code_stats:
            self._update_doc_stats_in_basic_tab()

        # 强制立即更新UI
        self.update_idletasks()
        # 确保UI立即刷新
        self.update()

    def _update_doc_stats_in_basic_tab(self):
        """更新基本统计选项卡中的文档统计部分"""
        if not hasattr(self, "code_stats") or not self.code_stats:
            return

        # 更新文档统计
        code_lines = self.code_stats.get("code_lines", "计算中...")
        if isinstance(code_lines, int):
            code_lines = f"{code_lines:,}"
        if hasattr(self, "code_lines_label"):
            self.code_lines_label.configure(text=f"有效行数: {code_lines}")

        comment_lines = self.code_stats.get("comment_lines", "计算中...")
        if isinstance(comment_lines, int):
            comment_lines = f"{comment_lines:,}"
        if hasattr(self, "comment_lines_label"):
            self.comment_lines_label.configure(text=f"注释行数: {comment_lines}")

        # 使用blank_lines而不是empty_lines
        empty_lines = self.code_stats.get("blank_lines", "计算中...")
        if isinstance(empty_lines, int):
            empty_lines = f"{empty_lines:,}"
        if hasattr(self, "empty_lines_label"):
            self.empty_lines_label.configure(text=f"空行数: {empty_lines}")

        # 计算比例
        total = self.code_stats.get("total_code_lines", None)
        if total and total > 0:
            code_ratio = self.code_stats.get("code_lines", 0) / total * 100
            comment_ratio = self.code_stats.get("comment_lines", 0) / total * 100
            # 使用blank_lines而不是empty_lines
            empty_ratio = self.code_stats.get("blank_lines", 0) / total * 100

            if hasattr(self, "code_ratio_label"):
                self.code_ratio_label.configure(text=f"有效行比例: {code_ratio:.1f}%")
            if hasattr(self, "comment_ratio_label"):
                self.comment_ratio_label.configure(
                    text=f"注释行比例: {comment_ratio:.1f}%"
                )
            if hasattr(self, "empty_ratio_label"):
                self.empty_ratio_label.configure(text=f"空行比例: {empty_ratio:.1f}%")
        else:
            # 空文档情况，直接使用0值而不是"计算中..."
            if hasattr(self, "code_ratio_label"):
                self.code_ratio_label.configure(text="有效行比例: 0.0%")
            if hasattr(self, "comment_ratio_label"):
                self.comment_ratio_label.configure(text="注释行比例: 0.0%")
            if hasattr(self, "empty_ratio_label"):
                self.empty_ratio_label.configure(text="空行比例: 0.0%")

    def _update_code_stats_ui(self):
        """更新代码统计UI"""
        # 确保UI更新在主线程中执行
        if not threading.current_thread() is threading.main_thread():
            self.after(0, self._update_code_stats_ui)
            return

        # 更新代码统计（移除总行数显示，避免与基本统计中的总行数重复）
        code_lines = self.code_stats.get("code_lines", "计算中...")
        if isinstance(code_lines, int):
            code_lines = f"{code_lines:,}"
        self.code_lines_label.configure(text=f"有效行数: {code_lines}")

        comment_lines = self.code_stats.get("comment_lines", "计算中...")
        if isinstance(comment_lines, int):
            comment_lines = f"{comment_lines:,}"
        self.comment_lines_label.configure(text=f"注释行数: {comment_lines}")

        # 使用blank_lines而不是empty_lines
        empty_lines = self.code_stats.get("blank_lines", "计算中...")
        if isinstance(empty_lines, int):
            empty_lines = f"{empty_lines:,}"
        self.empty_lines_label.configure(text=f"空行数: {empty_lines}")

        # 移除文档比例统计 - 不再计算和显示比例数据

        # 同时更新基本统计中的文档统计部分
        self._update_doc_stats_in_basic_tab()

        # 强制立即更新UI
        self.update_idletasks()
        # 确保UI立即刷新
        self.update()

    def _cancel_calculation(self):
        """取消计算"""
        if self.worker and self.worker.is_alive():
            self.worker.stop()
            self.status_label.configure(text="正在取消...")

            # 使用after方法在主线程中等待线程结束
            def wait_for_thread():
                if self.worker and self.worker.is_alive():
                    # 线程仍在运行，继续等待，使用更长的间隔减少CPU占用
                    self.after(200, wait_for_thread)
                else:
                    # 线程已结束，重置UI并重新开始计算
                    self._reset_ui()
                    self._start_worker()

            # 开始等待线程结束
            self.after(0, wait_for_thread)
        else:
            # 重新开始计算
            self.basic_stats = {}
            self.code_stats = {}
            self.status_label.configure(text="准备计算...")
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
        if hasattr(self, "code_lines_label"):
            self.code_lines_label.configure(text="有效行数: 计算中...")
            self.comment_lines_label.configure(text="注释行数: 计算中...")
            self.empty_lines_label.configure(text="空行数: 计算中...")

            # 文档比例标签已从UI结构中移除

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

                # 文档统计
                if self.code_stats:
                    f.write("文档统计\n")
                    f.write("-" * 30 + "\n")
                    f.write(f"有效行数: {self.code_stats.get('code_lines', 0):,}\n")
                    f.write(f"注释行数: {self.code_stats.get('comment_lines', 0):,}\n")
                    f.write(f"空行数: {self.code_stats.get('empty_lines', 0):,}\n\n")

                    # 文档比例统计已移除 - 不再导出比例数据

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

    def destroy(self):
        """销毁窗口，确保清理线程资源"""
        # 停止工作线程
        if self.worker and self.worker.is_alive():
            self.worker.stop()
            # 等待线程结束，但设置超时防止无限等待
            self.worker.join(timeout=1.0)

        # 调用父类销毁方法
        super().destroy()

    # 移除_create_code_stats_tab_async方法，因为已集成到基本统计中

    def _toggle_fullscreen(self):
        """切换全屏模式"""
        # 获取当前状态
        is_fullscreen = self.fullscreen_var.get()

        # 切换状态
        self.fullscreen_var.set(not is_fullscreen)
        new_state = self.fullscreen_var.get()

        if new_state:
            # 进入全屏
            self.attributes("-fullscreen", True)
            self.fullscreen_button.configure(text="退出全屏")
        else:
            # 退出全屏
            self.attributes("-fullscreen", False)
            self.fullscreen_button.configure(text="全屏")
            # 居中显示窗口
            self.parent.center_window(self, self.width, self.height)

    def _on_tab_double_click(self, event):
        """处理基本统计选项卡双击事件，切换全屏"""
        # 直接切换全屏，因为事件已经绑定到基本统计按钮
        self._toggle_fullscreen()

    def _on_escape(self, event=None):
        """处理ESC键事件"""
        if self.fullscreen_var.get():
            # 如果是全屏模式，则退出全屏
            self._toggle_fullscreen()
        else:
            # 否则关闭窗口
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
