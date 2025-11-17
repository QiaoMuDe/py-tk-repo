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
            "code_blocks": r"^```(\w*)\n([\s\S]*?)^```",
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
            "italic": r"(\*)(?!\s)(.+?)(?<!\s)\1|(_)(?!\s)(.+?)(?<!\s)\3",
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
            "code_blocks",  # 代码块
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
            "italic",  # 斜体
            "strikethrough",  # 删除线
            "highlight",  # 强调
            "superscript",  # 上标
            "subscript",  # 下标
            "html_tags",  # HTML标签
        ]

        # 标签样式 - 增强版配色方案，提高对比度和视觉体验
        self._tag_styles = {
            # 前置元数据 - 深灰色背景，浅色文字
            "frontmatter": {
                "foreground": "#6A6A6A",
                "background": "#F8F8F8",
            },
            # 代码块 - 使用浅色背景，确保文字清晰可见
            "code_blocks": {
                "background": "#F6F8FA",
            },
            # 数学公式块 - 深蓝色背景，浅色文字
            "math_blocks": {
                "foreground": "#F8F8F2",
                "background": "#1E3A8A",
            },
            # Mermaid图表 - 紫色背景，浅色文字
            "mermaid": {
                "foreground": "#F8F8F2",
                "background": "#4B1B8A",
            },
            # 标题 - 蓝色前景色和浅蓝色背景，整行高亮
            "headers": {
                "foreground": "#0366D6",
                "background": "#F0F7FF",
            },
            # 水平线 - 浅灰色，更加柔和
            "horizontal_rules": {
                "foreground": "#D1D5DA",
            },
            # 引用块 - 紫色前景色和浅紫色背景，整行高亮
            "quotes": {
                "foreground": "#6F42C1",
                "background": "#F5F0FF",
            },
            # 表格分隔符 - 中灰色，更加明显
            "table_separators": {
                "foreground": "#586069",
            },
            # 表格 - 深蓝色，增强可读性
            "tables": {
                "foreground": "#24292E",
            },
            # 任务列表 - 深青色，更加明显
            "task_lists": {
                "foreground": "#0077CC",
            },
            # 无序列表 - 深绿色，更加明显
            "unordered_lists": {
                "foreground": "#22863A",
            },
            # 有序列表 - 深绿色，更加明显
            "ordered_lists": {
                "foreground": "#22863A",
            },
            # 定义列表 - 深绿色，更加明显
            "definition_lists": {
                "foreground": "#22863A",
            },
            # 脚注定义 - 深紫色，更加明显
            "footnotes": {
                "foreground": "#6F42C1",
            },
            # 脚注引用 - 深紫色，更加明显
            "footnote_refs": {
                "foreground": "#6F42C1",
            },
            # HTML注释 - 绿色，更加明显
            "comments": {
                "foreground": "#22863A",
            },
            # 行内代码 - 深红色背景，浅色文字，增强对比度
            "inline_code": {
                "foreground": "#E83E8C",
                "background": "#FFF5F5",
            },
            # 行内数学公式 - 深蓝色背景，浅色文字，增强对比度
            "inline_math": {
                "foreground": "#1E3A8A",
                "background": "#EFF6FF",
            },
            # 图片 - 深绿色，更加明显
            "images": {
                "foreground": "#22863A",
            },
            # 链接 - 深紫色，更加明显
            "links": {
                "foreground": "#6F42C1",
            },
            # 引用式链接 - 深紫色，更加明显
            "reference_links": {
                "foreground": "#6F42C1",
            },
            # 引用式链接定义 - 灰色，更加明显
            "link_definitions": {
                "foreground": "#586069",
            },
            # 粗体 - 仅使用背景色表示，避免与其他文本颜色冲突
            "bold": {
                "background": "#FFF0F0",  # 浅红色背景，标识粗体文本
            },
            # 斜体 - 深灰色，增强可读性
            "italic": {
                "foreground": "#586069",
            },
            # 删除线 - 灰色，更加明显
            "strikethrough": {
                "foreground": "#959DA5",
            },
            # 强调 - 黄色背景，深色文字，增强对比度
            "highlight": {
                "foreground": "#24292E",
                "background": "#FFF3CD",
            },
            # 上标 - 深橙色，更加明显
            "superscript": {
                "foreground": "#E36209",
            },
            # 下标 - 深橙色，更加明显
            "subscript": {
                "foreground": "#E36209",
            },
            # HTML标签 - 棕色，更加明显
            "html_tags": {
                "foreground": "#A04B1C",
            },
            # 自动链接 - 深紫色，更加明显
            "autolinks": {
                "foreground": "#6F42C1",
            },
        }
