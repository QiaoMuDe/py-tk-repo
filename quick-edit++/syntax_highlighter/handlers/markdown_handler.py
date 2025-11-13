#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Markdown语言处理器

提供Markdown文档的语法识别和高亮规则
"""

import re
from typing import Dict, List, Any

from .base import LanguageHandler


class MarkdownHandler(LanguageHandler):
    """
    Markdown语言处理器

    提供Markdown文档的语法识别和高亮规则
    """

    # Markdown文件扩展名
    file_extensions = [".md", ".markdown", ".mdown", ".mkd", ".mkdn"]

    def _setup_language(self):
        """设置Markdown语言的语法规则"""
        # Markdown特殊元素
        self._keywords = []  # Markdown没有传统意义上的关键字

        # 正则表达式模式
        self._regex_patterns = {
            # 标题 - # ## ### 等
            "headers": r"^(#{1,6})\s+(.+)$",
            
            # 代码块 - ```包裹的代码
            "code_blocks": r"^```[\w]*\n[\s\S]*?^```",
            
            # 行内代码 - `包裹的代码
            "inline_code": r"`([^`]+)`",
            
            # 粗体 - **text** 或 __text__
            "bold": r"(\*\*|__)(.*?)\1",
            
            # 斜体 - *text* 或 _text_
            "italic": r"(\*|_)(?!\1)(.*?)\1",
            
            # 删除线 - ~~text~~
            "strikethrough": r"(~~)(.*?)\1",
            
            # 链接 - [text](url)
            "links": r"\[([^\]]+)\]\(([^)]+)\)",
            
            # 图片 - ![alt](url)
            "images": r"!\[([^\]]*)\]\(([^)]+)\)",
            
            # 引用 - > 开头的行
            "quotes": r"^>\s+(.*)$",
            
            # 无序列表 - - 或 * 或 + 开头的行
            "unordered_lists": r"^(\s*)[-*+]\s+(.*)$",
            
            # 有序列表 - 数字. 开头的行
            "ordered_lists": r"^(\s*)\d+\.\s+(.*)$",
            
            # 水平线 - --- 或 *** 或 ___
            "horizontal_rules": r"^(\s*)([-*_]{3,})(\s*)$",
            
            # HTML标签 - <tag>...</tag>
            "html_tags": r"<(/?)(\w+)([^>]*)>",
            
            # 表格 - | 列1 | 列2 | ...
            "tables": r"^\|(.+)\|$",
            
            # 分隔符 - 表格中的分隔行 |---|---|
            "table_separators": r"^\|(\s*:?-+:?\s*\|)+\s*$",
            
            # 任务列表 - - [ ] 或 - [x]
            "task_lists": r"^(\s*)[-*+]\s+\[([ x])\]\s+(.*)$",
            
            # 脚注 - [^1]:
            "footnotes": r"\^\[([^\]]+)\]:",
            
            # 定义列表 - Term\n: Definition
            "definition_lists": r"^(.+)\n:\s+(.*)$",
            
            # 元数据 - 前置YAML
            "frontmatter": r"^---\n[\s\S]*?\n---",
            
            # 注释 - HTML注释 <!-- comment -->
            "comments": r"<!--[\s\S]*?-->",
            
            # 强调 - ==text==
            "highlight": r"(==)(.*?)\1",
            
            # 上标 - text^2
            "superscript": r"\^([^^\s]+)\^",
            
            # 下标 - text~2~
            "subscript": r"~([^~\s]+)~",
        }

        # 标签样式 - 使用适合Markdown的配色方案
        self._tag_styles = {
            # 标题 - 深蓝色，不同级别使用不同深浅
            "headers": {
                "foreground": "#000080",
            },
            # 代码块 - 浅灰色背景，深色文字
            "code_blocks": {
                "foreground": "#333333",
                "background": "#f5f5f5",
            },
            # 行内代码 - 深红色
            "inline_code": {
                "foreground": "#8B0000",
                "background": "#f0f0f0",
            },
            # 粗体 - 黑色加粗
            "bold": {
                "foreground": "#000000",
            },
            # 斜体 - 深灰色
            "italic": {
                "foreground": "#555555",
            },
            # 删除线 - 灰色
            "strikethrough": {
                "foreground": "#999999",
            },
            # 链接 - 蓝色
            "links": {
                "foreground": "#0000FF",
            },
            # 图片 - 绿色
            "images": {
                "foreground": "#008000",
            },
            # 引用 - 深紫色
            "quotes": {
                "foreground": "#4B0082",
            },
            # 无序列表 - 深青色
            "unordered_lists": {
                "foreground": "#008B8B",
            },
            # 有序列表 - 深青色
            "ordered_lists": {
                "foreground": "#008B8B",
            },
            # 水平线 - 灰色
            "horizontal_rules": {
                "foreground": "#CCCCCC",
            },
            # HTML标签 - 棕色
            "html_tags": {
                "foreground": "#8B4513",
            },
            # 表格 - 深蓝色
            "tables": {
                "foreground": "#000080",
            },
            # 表格分隔符 - 灰色
            "table_separators": {
                "foreground": "#999999",
            },
            # 任务列表 - 深青色
            "task_lists": {
                "foreground": "#008B8B",
            },
            # 脚注 - 深紫色
            "footnotes": {
                "foreground": "#4B0082",
            },
            # 定义列表 - 深蓝色
            "definition_lists": {
                "foreground": "#000080",
            },
            # 元数据 - 深灰色
            "frontmatter": {
                "foreground": "#555555",
            },
            # 注释 - 绿色
            "comments": {
                "foreground": "#00AA00",
            },
            # 强调 - 黄色背景
            "highlight": {
                "foreground": "#000000",
                "background": "#FFFF00",
            },
            # 上标 - 深蓝色
            "superscript": {
                "foreground": "#000080",
            },
            # 下标 - 深蓝色
            "subscript": {
                "foreground": "#000080",
            },
        }