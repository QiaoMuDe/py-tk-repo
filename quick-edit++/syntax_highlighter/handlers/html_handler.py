#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML语言处理器

提供HTML语法的识别和高亮规则
"""

import re
from typing import Dict, List, Any

from .base import LanguageHandler


class HTMLHandler(LanguageHandler):
    """
    HTML语言处理器

    提供HTML语法的识别和高亮规则
    """

    # HTML文件扩展名
    file_extensions = [".html", ".htm", ".xhtml"]

    def _setup_language(self):
        """设置HTML语言的语法规则"""
        # HTML关键字
        self._keywords = [
            # 文档结构
            "html",
            "head",
            "title",
            "body",
            "meta",
            "link",
            "style",
            "script",
            # 文本格式
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "p",
            "br",
            "hr",
            "span",
            "div",
            "section",
            "article",
            "header",
            "footer",
            "nav",
            "main",
            "aside",
            # 列表
            "ul",
            "ol",
            "li",
            "dl",
            "dt",
            "dd",
            # 表格
            "table",
            "thead",
            "tbody",
            "tfoot",
            "tr",
            "th",
            "td",
            "caption",
            "col",
            "colgroup",
            # 表单
            "form",
            "input",
            "button",
            "select",
            "option",
            "optgroup",
            "textarea",
            "label",
            "fieldset",
            "legend",
            # 媒体
            "img",
            "audio",
            "video",
            "source",
            "canvas",
            "svg",
            # 链接
            "a",
            "area",
            # 其他
            "iframe",
            "embed",
            "object",
            "param",
            "map",
            "noscript",
        ]

        # HTML属性
        attributes = [
            "id",
            "class",
            "style",
            "name",
            "value",
            "type",
            "src",
            "href",
            "alt",
            "title",
            "width",
            "height",
            "action",
            "method",
            "target",
            "rel",
            "charset",
            "content",
            "http-equiv",
            "data-*",
            "role",
            "aria-*",
        ]

        # 正则表达式模式
        self._regex_patterns = {
            # 标签 - 匹配开始和结束标签
            "tags": r"</?[a-zA-Z][a-zA-Z0-9]*(?:\s+[a-zA-Z_:][a-zA-Z0-9_:.-]*(?:\s*=\s*(?:\".*?\"|'.*?'|[^'\">\s]+))?)*\s*/?>",
            # 关键字 - 在标签中的HTML关键字
            "keywords": r"</?\s*("
            + "|".join(re.escape(k) for k in self._keywords)
            + r")\b",
            # 属性 - 标签中的属性
            "attributes": r"\s+(id|class|style|name|value|type|src|href|alt|title|width|height|action|method|target|rel|charset|content|http-equiv|role|aria-[a-zA-Z-]+|data-[a-zA-Z-]+|[a-zA-Z_:][a-zA-Z0-9_:.-]*)\s*=",
            # 属性值 - 属性的值
            "attribute_values": r"=\s*(?:\"([^\"]*)\"|'([^']*)')",
            # 注释 - HTML注释
            "comments": r"<!--[\s\S]*?-->",
            # DOCTYPE - 文档类型声明
            "doctype": r"<!DOCTYPE[^>]*>",
            # CDATA - CDATA部分
            "cdata": r"<!\[CDATA\[[\s\S]*?\]\]>",
            # 字符串 - 属性值中的字符串
            "strings": r"(?:\"[^\"]*\"|'[^']*')",
            # CSS样式 - style属性中的内容
            "css_styles": r"style\s*=\s*(?:\"([^\"]*)\"|'([^']*)')",
            # JavaScript - script标签中的内容
            "javascript": r"<script[^>]*>([\s\S]*?)</script>",
            # 实体 - HTML实体
            "entities": r"&[a-zA-Z][a-zA-Z0-9]*;|&#\d+;|&#x[0-9a-fA-F]+;",
        }

        # 标签样式 - 使用适合HTML的配色方案
        self._tag_styles = {
            # 标签 - 深蓝色
            "tags": {
                "foreground": "#000080",
            },
            # 关键字 - 蓝色
            "keywords": {
                "foreground": "#0000FF",
            },
            # 属性 - 深绿色
            "attributes": {
                "foreground": "#008000",
            },
            # 属性值 - 棕色
            "attribute_values": {
                "foreground": "#8B4513",
            },
            # 注释 - 绿色
            "comments": {
                "foreground": "#00AA00",
            },
            # DOCTYPE - 紫色
            "doctype": {
                "foreground": "#800080",
            },
            # CDATA - 深紫色
            "cdata": {
                "foreground": "#4B0082",
            },
            # 字符串 - 棕色
            "strings": {
                "foreground": "#8B4513",
            },
            # CSS样式 - 深红色
            "css_styles": {
                "foreground": "#8B0000",
            },
            # JavaScript - 深蓝色
            "javascript": {
                "foreground": "#0000CD",
            },
            # 实体 - 深青色
            "entities": {
                "foreground": "#008B8B",
            },
        }
