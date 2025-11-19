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
    支持多种日志格式和增强特性
    """

    # 日志文件扩展名
    file_extensions = [".log", ".out", ".trace", ".debug", ".err"]

    @classmethod
    def get_language_name(cls) -> str:
        """
        获取语言处理器名称

        Returns:
            str: 语言处理器名称"log"
        """
        return "log"

    def _setup_language(self):
        """
        设置日志文件的语法高亮规则
        """
        # 日志文件的关键字
        self._keywords = [
            # 标准日志级别
            "DEBUG",
            "INFO",
            "WARN",
            "WARNING",
            "ERROR",
            "FATAL",
            "CRITICAL",
            "TRACE",
            "NOTICE",
            # 扩展日志级别
            "VERBOSE",
            "ALERT",
            "EMERGENCY",
            "PANIC",
            "SEVERE",
            "CONFIG",
            "FINE",
            "FINER",
            "FINEST",
            # 系统日志级别
            "SYSLOG",
            "KERN",
            "USER",
            "MAIL",
            "DAEMON",
            "AUTH",
            "SYSLOG",
            "LPR",
            "NEWS",
            "UUCP",
            "CRON",
            "AUTHPRIV",
            "FTP",
            # 网络日志级别
            "HTTP",
            "HTTPS",
            "TCP",
            "UDP",
            "DNS",
            "DHCP",
            "SSH",
            "SSL",
            "TLS",
            # 应用程序特定级别
            "START",
            "STOP",
            "INIT",
            "SHUTDOWN",
            "RESTART",
            "CONNECT",
            "DISCONNECT",
            "SEND",
            "RECEIVE",
            # 性能监控
            "PERF",
            "METRIC",
            "STATS",
            "MONITOR",
            "PROFILER",
            # 安全相关
            "SECURITY",
            "AUDIT",
            "LOGIN",
            "LOGOUT",
            "ACCESS",
            "DENIED",
            "PERMISSION",
            # 数据库相关
            "SQL",
            "QUERY",
            "TRANSACTION",
            "COMMIT",
            "ROLLBACK",
            "CONNECT",
            "DISCONNECT",
            # 其他常见标记
            "SUCCESS",
            "FAILURE",
            "OK",
            "FAIL",
            "PASS",
            "BEGIN",
            "END",
            "ENTRY",
            "EXIT",
        ]

        # 正则表达式模式 - 优化和扩展以支持更多日志格式
        self._regex_patterns = {
            # 时间戳 - 支持多种常见格式
            "timestamp": r"(?m)(?:\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}\.\d{2}\.\d{4})\s+(?:\d{2}:\d{2}:\d{2}(?:\.\d{3,})?)|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3,})?(?:Z|[+-]\d{2}:\d{2})?|\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}",
            # 日志级别 - 使用关键字列表
            "log_level": r"\b("
            + "|".join(re.escape(k) for k in self._keywords)
            + r")\b",
            # 线程ID/进程ID - 方括号中的数字，增强匹配
            "thread_id": r"\[(\d+)\]|\[Thread-\d+\]|\[pool-\d+-thread-\d+\]|\[TID:\d+\]|\[PID:\d+\]|\[0x[0-9a-fA-F]+\]",
            # 类名/模块名 - 通常包含点号，如com.example.ClassName，增强匹配
            "class_name": r"(?m)(?:[a-zA-Z_][a-zA-Z0-9_]*\.)+[A-Z][a-zA-Z0-9_]*|[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)+",
            # 方法名 - 通常在类名后，如Class.method()，增强匹配
            "method_name": r"[a-zA-Z_][a-zA-Z0-9_]*\s*\(",
            # 文件名和行号 - 如 (File.java:123) 或 [file.py:456]，增强匹配
            "file_location": r"\([^)]+\.\w+:\d+\)|\[[^]]+\.\w+:\d+\]|(?:\w+\.py:\d+|\w+\.java:\d+|\w+\.cpp:\d+|\w+\.c:\d+)",
            # IP地址 - IPv4和IPv6，增强匹配
            "ip_address": r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b|\[([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\]|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}",
            # URL/URI，增强匹配
            "url": r"https?://[^\s/$.?#].[^\s]*|ftp://[^\s]*|file://[^\s]*",
            # 异常/错误类型 - 通常以Exception或Error结尾，增强匹配
            "exception_type": r"\b\w*(?:Exception|Error|Throwable|Fault|Failure)\b",
            # 堆栈跟踪 - 通常包含"at"和类名，增强匹配
            "stack_trace": r"^\s+at\s+(?:[a-zA-Z_][a-zA-Z0-9_]*\.)+[A-Z][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*\([^)]*\)|^\s+Caused\s+by:.*|^\s+...\s+\d+\s+more",
            # JSON/XML内容 - 尝试识别结构化数据，增强匹配
            "structured_data": r"\{[^}]*\}|<[^>]*>|\[[^\]]*\]",
            # 用户自定义标记 - 如[INFO]、[ERROR]等，增强匹配
            "custom_marker": r"\[(?:"
            + "|".join(re.escape(k) for k in self._keywords)
            + r")\]|\[.*?\]",
            # 十六进制值 - 如内存地址，增强匹配
            "hex_value": r"0x[0-9a-fA-F]+|\b[0-9a-fA-F]{8,}\b",
            # 数字 - 整数和浮点数，增强匹配
            "number": r"\b\d+(?:\.\d+)?[eE][+-]?\d+|\b\d+(?:\.\d+)?\b",
            # 新增：HTTP状态码
            "http_status": r"\b[1-5]\d{2}\b",
            # 新增：HTTP方法
            "http_method": r"\b(?:GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH|TRACE|CONNECT)\b",
            # 新增：数据库查询语句
            "sql_query": r"(?i)\b(?:SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|TRUNCATE|FROM|WHERE|JOIN|INNER|LEFT|RIGHT|OUTER|GROUP|BY|ORDER|HAVING|UNION|DISTINCT|COUNT|SUM|AVG|MIN|MAX)\b",
            # 新增：文件路径
            "file_path": r"(?:[a-zA-Z]:)?[/\\][^\s]*|[a-zA-Z]:[\\/][^\s]*",
            # 新增：MAC地址
            "mac_address": r"\b(?:[0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}\b",
            # 新增：UUID
            "uuid": r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b",
            # 新增：性能指标
            "performance_metric": r"\b\d+(?:\.\d+)?\s*(?:ms|s|sec|seconds?|min|minutes?|h|hours?|B|KB|MB|GB|TB|bytes?)\b",
            # 新增：用户名
            "username": r"\buser[:\s]+[a-zA-Z0-9_\-\.]+\b|\b[a-zA-Z0-9_\-\.]+@.*\b",
        }

        # 标签样式 - 使用适合日志文件的配色方案，仅修改颜色
        self._tag_styles = {
            "timestamp": {"foreground": "#4A90E2"},  # 蓝色用于时间戳
            "log_level": {"foreground": "#E74C3C"},  # 红色用于日志级别
            "thread_id": {"foreground": "#9B59B6"},  # 紫色用于线程ID
            "class_name": {"foreground": "#1ABC9C"},  # 青色用于类名
            "method_name": {"foreground": "#F39C12"},  # 橙色用于方法名
            "file_location": {"foreground": "#27AE60"},  # 绿色用于文件位置
            "ip_address": {"foreground": "#8E44AD"},  # 深紫色用于IP地址
            "url": {"foreground": "#2980B9"},  # 深蓝色用于URL
            "exception_type": {"foreground": "#C0392B"},  # 深红色用于异常类型
            "stack_trace": {"foreground": "#7F8C8D"},  # 灰色用于堆栈跟踪
            "structured_data": {"foreground": "#16A085"},  # 深青色用于结构化数据
            "custom_marker": {"foreground": "#D35400"},  # 深橙色用于自定义标记
            "hex_value": {"foreground": "#27AE60"},  # 绿色用于十六进制值
            "number": {"foreground": "#2ECC71"},  # 浅绿色用于数字
            # 新增：HTTP状态码
            "http_status": {"foreground": "#E67E22"},  # 橙色用于HTTP状态码
            # 新增：HTTP方法
            "http_method": {"foreground": "#8E44AD"},  # 紫色用于HTTP方法
            # 新增：数据库查询语句
            "sql_query": {"foreground": "#2980B9"},  # 深蓝色用于SQL查询
            # 新增：文件路径
            "file_path": {"foreground": "#34495E"},  # 深灰色用于文件路径
            # 新增：MAC地址
            "mac_address": {"foreground": "#16A085"},  # 深青色用于MAC地址
            # 新增：UUID
            "uuid": {"foreground": "#9B59B6"},  # 紫色用于UUID
            # 新增：性能指标
            "performance_metric": {"foreground": "#E74C3C"},  # 红色用于性能指标
            # 新增：用户名
            "username": {"foreground": "#27AE60"},  # 绿色用于用户名
        }
