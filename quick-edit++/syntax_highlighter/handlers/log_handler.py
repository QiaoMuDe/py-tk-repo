#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志文件处理器

提供.log、.out等日志文件的语法高亮支持
"""

import re
from typing import Dict, List, Any

from .base import LanguageHandler


class LogHandler(LanguageHandler):
    """
    日志文件语言处理器
    
    提供.log、.out等日志文件的语法高亮支持
    """
    
    # 日志文件扩展名
    file_extensions = [".log", ".out", ".trace"]
    
    def _setup_language(self):
        """
        设置日志文件的语法高亮规则
        """
        # 日志文件的关键字
        self._keywords = [
            "DEBUG", "INFO", "WARN", "WARNING", "ERROR", "FATAL", "CRITICAL", "TRACE", "NOTICE"
        ]
        
        # 正则表达式模式
        self._regex_patterns = {
            # 时间戳 - 支持多种常见格式
            "timestamp": r"(?m)(?:\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})\s+(?:\d{2}:\d{2}:\d{2}(?:\.\d{3,})?)|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3,})?(?:Z|[+-]\d{2}:\d{2})?",
            
            # 日志级别 - 使用关键字列表
            "log_level": r"\b(" + "|".join(re.escape(k) for k in self._keywords) + r")\b",
            
            # 线程ID/进程ID - 方括号中的数字
            "thread_id": r"\[(\d+)\]|\[Thread-\d+\]|\[pool-\d+-thread-\d+\]",
            
            # 类名/模块名 - 通常包含点号，如com.example.ClassName
            "class_name": r"(?m)(?:[a-zA-Z_][a-zA-Z0-9_]*\.)+[A-Z][a-zA-Z0-9_]*",
            
            # 方法名 - 通常在类名后，如Class.method()
            "method_name": r"[a-zA-Z_][a-zA-Z0-9_]*\s*\(",
            
            # 文件名和行号 - 如 (File.java:123) 或 [file.py:456]
            "file_location": r"\([^)]+\.\w+:\d+\)|\[[^]]+\.\w+:\d+\]",
            
            # IP地址 - IPv4和IPv6
            "ip_address": r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b|\[([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\]",
            
            # URL/URI
            "url": r"https?://[^\s/$.?#].[^\s]*",
            
            # 异常/错误类型 - 通常以Exception或Error结尾
            "exception_type": r"\b\w*(?:Exception|Error|Throwable)\b",
            
            # 堆栈跟踪 - 通常包含"at"和类名
            "stack_trace": r"^\s+at\s+(?:[a-zA-Z_][a-zA-Z0-9_]*\.)+[A-Z][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*\([^)]*\)",
            
            # JSON/XML内容 - 尝试识别结构化数据
            "structured_data": r"\{[^}]*\}|<[^>]*>",
            
            # 用户自定义标记 - 如[INFO]、[ERROR]等
            "custom_marker": r"\[(?:DEBUG|INFO|WARN|WARNING|ERROR|FATAL|CRITICAL|TRACE|NOTICE)\]",
            
            # 十六进制值 - 如内存地址
            "hex_value": r"0x[0-9a-fA-F]+",
            
            # 数字 - 整数和浮点数
            "number": r"\b\d+(?:\.\d+)?\b",
        }
        
        # 标签样式 - 使用适合日志文件的配色方案
        self._tag_styles = {
            "timestamp": {"foreground": "#569CD6"},  # 蓝色用于时间戳
            "log_level": {"foreground": "#FF7700"},  # 橙色用于日志级别
            "thread_id": {"foreground": "#9CDCFE"},  # 浅蓝色用于线程ID
            "class_name": {"foreground": "#4EC9B0"},  # 青色用于类名
            "method_name": {"foreground": "#DCDCAA"},  # 浅黄色用于方法名
            "file_location": {"foreground": "#B5CEA8"},  # 浅绿色用于文件位置
            "ip_address": {"foreground": "#C586C0"},  # 紫色用于IP地址
            "url": {"foreground": "#CE9178"},  # 橙色用于URL
            "exception_type": {"foreground": "#F44747"},  # 红色用于异常类型
            "stack_trace": {"foreground": "#D4D4D4"},  # 浅灰色用于堆栈跟踪
            "structured_data": {"foreground": "#6A9955"},  # 绿色用于结构化数据
            "custom_marker": {"foreground": "#FF7700"},  # 橙色用于自定义标记
            "hex_value": {"foreground": "#B5CEA8"},  # 浅绿色用于十六进制值
            "number": {"foreground": "#B5CEA8"},  # 浅绿色用于数字
        }