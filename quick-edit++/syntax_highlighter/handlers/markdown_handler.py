#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Markdown语言处理器

提供Markdown文档的语法识别和高亮规则，支持现代Markdown扩展语法
包括GitHub Flavored Markdown (GFM)、数学公式、Mermaid图表等
"""

import re
from typing import Dict, List, Any

from .base import LanguageHandler


class MarkdownHandler(LanguageHandler):
    """
    Markdown语言处理器

    提供Markdown文档的语法识别和高亮规则，支持现代Markdown扩展语法
    包括GitHub Flavored Markdown (GFM)、数学公式、Mermaid图表等
    """

    # Markdown文件扩展名
    file_extensions = [".md", ".markdown", ".mdown", ".mkd", ".mkdn"]

    def _setup_language(self):
        """设置Markdown语言的语法规则"""
        # Markdown特殊元素
        self._keywords = []  # Markdown没有传统意义上的关键字

        # 正则表达式模式 - 优化后的版本，提高准确性和性能
        self._regex_patterns = {
            # 前置元数据 - YAML前置内容，优先级最高
            "frontmatter": r"^---\n[\s\S]*?\n---",
            # 代码块
            # "code_blocks": r"^```(\w*)\n([\s\S]*?)^```",
            # 数学公式块 - LaTeX数学公式
            "math_blocks": r"^\$\$([\s\S]*?)^\$\$",
            # Mermaid图表 - 流程图和图表，优化版本
            "mermaid": r"^```mermaid\n([\s\S]*?)^```",
            # 标题 - 改进版本，更精确匹配
            "headers": r"^(#{1,6})(\s+)(.+)$",
            # 水平线 - 改进版本，更精确匹配
            "horizontal_rules": r"^(\s*)([-*_]{3,})(\s*)$",
            # 引用块 - 支持多级引用
            "quotes": r"^(>{1,3})(\s+)(.*)$",
            # 表格分隔符 - 改进版本，更精确匹配对齐方式
            "table_separators": r"^\|(\s*:?-+:?\s*\|)+\s*$",
            # 表格 - 改进版本，更精确匹配表格内容
            "tables": r"^\|(.+)\|$",
            # 任务列表 - 改进版本，更精确匹配状态
            "task_lists": r"^(\s*)([-*+])(\s+)(\[([ x])\])(\s+)(.*)$",
            # 无序列表 - 改进版本，支持嵌套
            "unordered_lists": r"^(\s*)([-*+])(\s+)(.*)$",
            # 有序列表 - 改进版本，支持嵌套和更精确匹配
            "ordered_lists": r"^(\s*)(\d+)(\.)(\s+)(.*)$",
            # 定义列表 - 改进版本
            "definition_lists": r"^(.+)\n:\s+(.*)$",
            # 脚注定义 - 改进版本
            "footnotes": r"^\^\[([^\]]+)\]:\s*(.*)$",
            # 脚注引用 - 新增
            "footnote_refs": r"\^\[([^\]]+)\]",
            # HTML注释 - 改进版本
            "comments": r"<!--[\s\S]*?-->",
            # 行内代码 - 改进版本，支持包含下划线的内容
            "inline_code": r"(?<!`)`([^`\n]*?)`(?!`)",
            # 行内数学公式 - 新增
            "inline_math": r"\$([^$\n]+)\$",
            # 图片 - 改进版本，支持标题属性
            "images": r"!\[([^\]]*)\]\(([^)]+)(?:\s+\"([^\"]+)\")?\)",
            # 链接 - 改进版本，支持标题属性和引用式链接
            "links": r"\[([^\]]+)\]\(([^)]+)(?:\s+\"([^\"]+)\")?\)",
            # 引用式链接 - 新增
            "reference_links": r"\[([^\]]+)\]\[([^\]]*)\]",
            # 引用式链接定义 - 新增
            "link_definitions": r"^\s*\[([^\]]+)\]:\s*(.*)$",
            # 粗体 - 优化版本，确保完整匹配包括结束标记
            "bold": r"\*\*(?!\s)(.+?)(?<!\s)\*\*",
            # 斜体 - 改进版本，避免与粗体冲突
            # "italic": r"(\*)(?!\s)(.+?)(?<!\s)\1|(_)(?!\s)(.+?)(?<!\s)\3",
            # 删除线 - 改进版本
            "strikethrough": r"(~~)(?!\s)(.+?)(?<!\s)\1",
            # 强调 - 改进版本
            "highlight": r"(==)(?!\s)(.+?)(?<!\s)\1",
            # 上标 - 改进版本
            "superscript": r"\^([^^\s]+)\^",
            # 下标 - 改进版本
            "subscript": r"~([^~\s]+)~",
            # HTML标签 - 改进版本，更精确匹配
            "html_tags": r"<(/?)([a-zA-Z][a-zA-Z0-9]*)(?:\s+[^>]*)?>",
            # 自动链接 - 新增
            "autolinks": r"<(https?://[^>]+)>",
        }

        # 模式处理顺序 - 定义高亮优先级，确保正确的嵌套处理
        self._pattern_order = [
            # 优先处理块级元素
            "frontmatter",  # 前置元数据
            # "code_blocks",  # 代码块
            "math_blocks",  # 数学公式块
            "mermaid",  # Mermaid图表
            "comments",  # HTML注释
            # 然后处理行级元素
            "headers",  # 标题
            "horizontal_rules",  # 水平线
            "quotes",  # 引用块
            "table_separators",  # 表格分隔符
            "tables",  # 表格
            "task_lists",  # 任务列表
            "unordered_lists",  # 无序列表
            "ordered_lists",  # 有序列表
            "definition_lists",  # 定义列表
            "footnotes",  # 脚注定义
            "link_definitions",  # 引用式链接定义
            # 最后处理内联元素
            "footnote_refs",  # 脚注引用
            "inline_code",  # 行内代码
            "inline_math",  # 行内数学公式
            "images",  # 图片
            "links",  # 链接
            "reference_links",  # 引用式链接
            "autolinks",  # 自动链接
            "bold",  # 粗体
            # "italic",  # 斜体
            "strikethrough",  # 删除线
            "highlight",  # 强调
            "superscript",  # 上标
            "subscript",  # 下标
            "html_tags",  # HTML标签
        ]

        # 标签样式 - 仅使用前景色方案，避免与查找界面标签冲突
        self._tag_styles = {
            # 前置元数据 - 深灰色文字
            "frontmatter": {
                "foreground": "#6A6A6A",
            },
            # 代码块 - 深蓝色文字
            # "code_blocks": {
            #    "foreground": "#0366D6",
            # },
            # 数学公式块 - 深靛蓝色文字
            "math_blocks": {
                "foreground": "#1E3A8A",
            },
            # Mermaid图表 - 紫色文字
            "mermaid": {
                "foreground": "#4B1B8A",
            },
            # 标题 - 深蓝色文字
            "headers": {
                "foreground": "#0969DA",
            },
            # 水平线 - 浅灰色文字
            "horizontal_rules": {
                "foreground": "#D1D5DA",
            },
            # 引用块 - 深紫色文字
            "quotes": {
                "foreground": "#8B5CF6",
            },
            # 表格分隔符 - 中灰色文字
            "table_separators": {
                "foreground": "#586069",
            },
            # 表格 - 深蓝色文字
            "tables": {
                "foreground": "#24292E",
            },
            # 任务列表 - 青色文字
            "task_lists": {
                "foreground": "#1B80E2",
            },
            # 无序列表 - 绿色文字
            "unordered_lists": {
                "foreground": "#1F883D",
            },
            # 有序列表 - 深绿色文字
            "ordered_lists": {
                "foreground": "#22863A",
            },
            # 定义列表 - 橄榄绿色文字
            "definition_lists": {
                "foreground": "#6B7280",
            },
            # 脚注定义 - 紫红色文字
            "footnotes": {
                "foreground": "#A433FF",
            },
            # 脚注引用 - 紫色文字
            "footnote_refs": {
                "foreground": "#9333EA",
            },
            # HTML注释 - 深绿色文字
            "comments": {
                "foreground": "#0E7C57",
            },
            # 行内代码 - 粉红色文字
            "inline_code": {
                "foreground": "#E83E8C",
            },
            # 行内数学公式 - 深蓝色文字
            "inline_math": {
                "foreground": "#1E40AF",
            },
            # 图片 - 深绿色文字
            "images": {
                "foreground": "#0D7377",
            },
            # 链接 - 蓝色文字
            "links": {
                "foreground": "#0A5EBD",
            },
            # 引用式链接 - 深蓝色文字
            "reference_links": {
                "foreground": "#1E40AF",
            },
            # 引用式链接定义 - 中灰色文字
            "link_definitions": {
                "foreground": "#6B7280",
            },
            # 粗体 - 深红色文字
            "bold": {
                "foreground": "#CF222E",
            },
            # 斜体 - 深灰色文字
            # "italic": {
            #    "foreground": "#586069",
            # },
            # 删除线 - 灰色文字
            "strikethrough": {
                "foreground": "#8B949E",
            },
            # 强调 - 橙色文字
            "highlight": {
                "foreground": "#FB8500",
            },
            # 上标 - 橘红色文字
            "superscript": {
                "foreground": "#F97316",
            },
            # 下标 - 琥珀色文字
            "subscript": {
                "foreground": "#F59E0B",
            },
            # HTML标签 - 棕色文字
            "html_tags": {
                "foreground": "#A04B1C",
            },
            # 自动链接 - 深蓝色文字
            "autolinks": {
                "foreground": "#0969DA",
            },
        }
