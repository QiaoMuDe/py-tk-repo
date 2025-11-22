#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XML语言处理器

提供XML语法的识别和高亮规则
"""

import re
from typing import Dict, List, Any

from .base import LanguageHandler


class XMLHandler(LanguageHandler):
    """
    XML语言处理器

    提供XML语法的识别和高亮规则
    """

    # XML文件扩展名
    file_extensions = [
        ".xml",
        ".xsl",
        ".xslt",
        ".xsd",
        ".svg",
        ".rss",
        ".atom",
        ".plist",
        ".mxml",
        ".xaml",
        ".wsdl",
        ".xul",
    ]

    @classmethod
    def get_language_name(cls) -> str:
        """
        获取语言处理器名称

        Returns:
            str: 语言处理器名称"xml"
        """
        return "xml"

    def _setup_language(self):
        """设置XML语言的语法规则"""
        # 正则表达式模式
        self._regex_patterns = {
            # 标签 - 匹配开始和结束标签
            "tags": r"</?[a-zA-Z_][a-zA-Z0-9_\-]*(?:\s+[a-zA-Z_:][a-zA-Z0-9_\-:.]*(?:\s*=\s*(?:\".*?\"|'.*?'|[^'\">\s]+))?)*\s*/?>",
            # 注释 - XML注释
            "comments": r"<!--[\s\S]*?-->",
            # CDATA - CDATA部分
            "cdata": r"<!\[CDATA\[[\s\S]*?\]\]>",
            # DOCTYPE - 文档类型声明
            "doctype": r"<!DOCTYPE[^>]*>",
            # 处理指令 - 如<?xml version="1.0"?>
            "processing_instructions": r"<\?[a-zA-Z_][a-zA-Z0-9_\-]*(?:\s+[a-zA-Z_][a-zA-Z0-9_\-]*(?:\s*=\s*(?:\".*?\"|'.*?'|[^'\">\s]+))?)*\s*\?>",
            # 属性 - 标签中的属性
            "attributes": r"\s+([a-zA-Z_:][a-zA-Z0-9_\-:.]*)\s*=",
            # 属性值 - 属性的值
            "attribute_values": r"=\s*(?:\"([^\"]*)\"|'([^']*)')",
            # 字符串 - 属性值中的字符串
            "strings": r"(?:\"[^\"]*\"|'[^']*')",
            # 实体 - XML实体
            "entities": r"&[a-zA-Z][a-zA-Z0-9]*;|&#\d+;|&#x[0-9a-fA-F]+;",
            # 命名空间 - xmlns声明
            "namespaces": r"xmlns(?::[a-zA-Z_][a-zA-Z0-9_\-]*)?\s*=",
            # 文本内容 - 标签之间的文本
            "text_content": r">(.*?)<",
        }

        # 标签样式 - 使用适合XML的配色方案
        self._tag_styles = {
            # 标签 - 深蓝色
            "tags": {
                "foreground": "#000080",
            },
            # 注释 - 绿色
            "comments": {
                "foreground": "#00AA00",
            },
            # CDATA - 深紫色
            "cdata": {
                "foreground": "#4B0082",
            },
            # DOCTYPE - 紫色
            "doctype": {
                "foreground": "#800080",
            },
            # 处理指令 - 深青色
            "processing_instructions": {
                "foreground": "#008B8B",
            },
            # 属性 - 深绿色
            "attributes": {
                "foreground": "#008000",
            },
            # 属性值 - 棕色
            "attribute_values": {
                "foreground": "#8B4513",
            },
            # 字符串 - 棕色
            "strings": {
                "foreground": "#8B4513",
            },
            # 实体 - 深红色
            "entities": {
                "foreground": "#8B0000",
            },
            # 命名空间 - 深蓝色
            "namespaces": {
                "foreground": "#0000CD",
            },
            # 文本内容 - 黑色
            "text_content": {
                "foreground": "#000000",
            },
        }

        # 语法高亮模式优先级顺序
        self._pattern_order = [
            "comments",
            "cdata",
            "doctype",
            "processing_instructions",
            "strings",
            "attribute_values",
            "entities",
            "namespaces",
            "attributes",
            "tags",
            "text_content",
        ]

    def get_pattern_order(self):
        """
        获取语法高亮模式的优先级顺序

        Returns:
            List[str]: 模式名称列表，表示语法高亮的处理顺序
        """
        return self._pattern_order
