#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSS语言处理器

提供CSS语法的识别和高亮规则
"""

import re
from typing import Dict, List, Any

from .base import LanguageHandler


class CSSHandler(LanguageHandler):
    """
    CSS语言处理器

    提供CSS语法的识别和高亮规则
    """

    # CSS文件扩展名
    file_extensions = [".css", ".scss", ".sass", ".less"]

    @classmethod
    def get_language_name(cls) -> str:
        """
        获取语言处理器名称
        
        Returns:
            str: 语言处理器名称"css"
        """
        return "css"

    def _setup_language(self):
        """设置CSS语言的语法规则"""
        # CSS关键字
        self._keywords = [
            # 布局属性
            "display",
            "position",
            "top",
            "right",
            "bottom",
            "left",
            "float",
            "clear",
            "z-index",
            "overflow",
            "visibility",
            "opacity",
            # 盒模型属性
            "width",
            "height",
            "min-width",
            "max-width",
            "min-height",
            "max-height",
            "margin",
            "margin-top",
            "margin-right",
            "margin-bottom",
            "margin-left",
            "padding",
            "padding-top",
            "padding-right",
            "padding-bottom",
            "padding-left",
            "border",
            "border-top",
            "border-right",
            "border-bottom",
            "border-left",
            "border-width",
            "border-style",
            "border-color",
            "border-radius",
            # 背景属性
            "background",
            "background-color",
            "background-image",
            "background-repeat",
            "background-attachment",
            "background-position",
            "background-size",
            # 字体属性
            "font",
            "font-family",
            "font-size",
            "font-weight",
            "font-style",
            "font-variant",
            "line-height",
            "letter-spacing",
            "word-spacing",
            "text-align",
            "text-decoration",
            "text-indent",
            "text-transform",
            "white-space",
            # 颜色属性
            "color",
            # 列表属性
            "list-style",
            "list-style-type",
            "list-style-image",
            "list-style-position",
            # 表格属性
            "border-collapse",
            "border-spacing",
            "caption-side",
            "empty-cells",
            # 动画属性
            "transition",
            "transition-property",
            "transition-duration",
            "transition-timing-function",
            "transition-delay",
            "animation",
            "animation-name",
            "animation-duration",
            "animation-timing-function",
            "animation-delay",
            "animation-iteration-count",
            "animation-direction",
            "animation-play-state",
            "animation-fill-mode",
            # 变换属性
            "transform",
            "transform-origin",
            # 弹性布局
            "flex",
            "flex-direction",
            "flex-wrap",
            "flex-flow",
            "justify-content",
            "align-items",
            "align-content",
            "align-self",
            "order",
            "flex-grow",
            "flex-shrink",
            "flex-basis",
            # 网格布局
            "grid",
            "grid-template-columns",
            "grid-template-rows",
            "grid-template-areas",
            "grid-auto-columns",
            "grid-auto-rows",
            "grid-auto-flow",
            "grid-gap",
            "grid-row-gap",
            "grid-column-gap",
            "grid-area",
            "grid-row",
            "grid-column",
            "grid-row-start",
            "grid-row-end",
            "grid-column-start",
            "grid-column-end",
            # 其他常用属性
            "cursor",
            "box-shadow",
            "text-shadow",
            "content",
            "outline",
            "user-select",
            "pointer-events",
        ]

        # CSS伪类和伪元素
        pseudo_classes = [
            "hover",
            "active",
            "focus",
            "visited",
            "link",
            "first-child",
            "last-child",
            "nth-child",
            "nth-last-child",
            "first-of-type",
            "last-of-type",
            "nth-of-type",
            "nth-last-of-type",
            "only-child",
            "only-of-type",
            "empty",
            "root",
            "target",
            "enabled",
            "disabled",
            "checked",
            "not",
            "before",
            "after",
            "first-line",
            "first-letter",
            "selection",
        ]

        # CSS单位
        units = [
            "px",
            "em",
            "rem",
            "pt",
            "pc",
            "in",
            "cm",
            "mm",
            "ex",
            "ch",
            "vw",
            "vh",
            "vmin",
            "vmax",
            "%",
            "deg",
            "rad",
            "grad",
            "turn",
            "ms",
            "s",
            "Hz",
            "kHz",
            "dpi",
            "dpcm",
            "dppx",
        ]

        # 正则表达式模式
        self._regex_patterns = {
            # 注释 - CSS注释
            "comments": r"/\*[\s\S]*?\*/",
            # 选择器 - 包括元素选择器、类选择器、ID选择器等
            "selectors": r"([a-zA-Z][a-zA-Z0-9]*|\.[a-zA-Z_][a-zA-Z0-9_-]*|#[a-zA-Z_][a-zA-Z0-9_-]*|\*|\[.*?\]|:[a-zA-Z-]+|::[a-zA-Z-]+)(?=\s*[{,])",
            # 关键字 - CSS属性
            "keywords": r"\b("
            + "|".join(re.escape(k) for k in self._keywords)
            + r")\b",
            # 伪类和伪元素
            "pseudo_classes": r":("
            + "|".join(re.escape(p) for p in pseudo_classes)
            + r")",
            # 属性值 - 包括颜色、尺寸等
            "values": r":\s*([^;{}]+)(?=;)",
            # 颜色 - 十六进制、RGB、RGBA、HSL、HSLA颜色
            "colors": r"(#[0-9a-fA-F]{3,6}|rgb\s*\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)|rgba\s*\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[\d.]+\s*\)|hsl\s*\(\s*\d+\s*,\s*\d+%\s*,\s*\d+%\s*\)|hsla\s*\(\s*\d+\s*,\s*\d+%\s*,\s*\d+%\s*,\s*[\d.]+\s*\))",
            # 字符串 - 引号中的字符串
            "strings": r"(\"[^\"]*\"|'[^']*')",
            # 数字 - 包括整数和浮点数
            "numbers": r"\b\d+(?:\.\d+)?\b",
            # 单位 - CSS单位
            "units": r"\b(" + "|".join(re.escape(u) for u in units) + r")\b",
            # URL - url()函数
            "urls": r"url\s*\(\s*(\"[^\"]*\"|'[^']*'|[^)]+)\s*\)",
            # 重要标记 - !important
            "important": r"!\s*important",
            # 媒体查询 - @media
            "media_queries": r"@[a-zA-Z-]+\s+[^{]*",
            # @规则 - @import, @charset等
            "at_rules": r"@[a-zA-Z-]+\b",
            # 函数 - calc(), attr(), var()等
            "functions": r"[a-zA-Z-]+\s*\([^)]*\)",
        }

        # 标签样式 - 使用适合CSS的配色方案
        self._tag_styles = {
            # 注释 - 绿色
            "comments": {
                "foreground": "#00AA00",
            },
            # 选择器 - 深蓝色
            "selectors": {
                "foreground": "#000080",
            },
            # 关键字 - 蓝色
            "keywords": {
                "foreground": "#0000FF",
            },
            # 伪类和伪元素 - 深紫色
            "pseudo_classes": {
                "foreground": "#4B0082",
            },
            # 属性值 - 黑色
            "values": {
                "foreground": "#000000",
            },
            # 颜色 - 深红色
            "colors": {
                "foreground": "#8B0000",
            },
            # 字符串 - 棕色
            "strings": {
                "foreground": "#8B4513",
            },
            # 数字 - 深青色
            "numbers": {
                "foreground": "#008B8B",
            },
            # 单位 - 深绿色
            "units": {
                "foreground": "#008000",
            },
            # URL - 紫色
            "urls": {
                "foreground": "#800080",
            },
            # 重要标记 - 红色
            "important": {
                "foreground": "#FF0000",
            },
            # 媒体查询 - 深橙色
            "media_queries": {
                "foreground": "#FF8C00",
            },
            # @规则 - 深橙色
            "at_rules": {
                "foreground": "#FF8C00",
            },
            # 函数 - 深灰色
            "functions": {
                "foreground": "#696969",
            },
        }
