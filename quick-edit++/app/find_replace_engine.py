#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
查找替换引擎模块
"""

import re
from typing import Dict


class SearchOptions:
    """
    搜索选项类

    封装搜索时使用的各种选项, 如不区分大小写、全字匹配、正则表达式等
    """

    def __init__(
        self,
        nocase: bool = False,
        whole_word: bool = False,
        regex: bool = False,
        search_up: bool = False,
    ):
        """
        初始化搜索选项

        Args:
            nocase: 是否不区分大小写, 默认为False
            whole_word: 是否全字匹配, 默认为False
            regex: 是否使用正则表达式, 默认为False
            search_up: 是否向上搜索, 默认为False (默认向下搜索)
        """
        self.nocase = nocase  # 是否不区分大小写
        self.whole_word = whole_word  # 是否全字匹配
        self.regex = regex  # 是否使用正则表达式
        self.search_up = search_up  # 是否向上搜索 (默认向下搜索)

    def __str__(self) -> str:
        """
        返回搜索选项的字符串表示

        Returns:
            str: 搜索选项的字符串表示
        """
        options = []
        if self.nocase:
            options.append("不区分大小写")
        if self.whole_word:
            options.append("全字匹配")
        if self.regex:
            options.append("正则表达式")
        if self.search_up:
            options.append("向上搜索")

        return ", ".join(options) if options else "默认搜索"

    def get_opts(self) -> Dict[str, any]:
        """
        获取tk.Text搜索方法所需的选项参数

        Returns:
            Dict[str, any]: 包含tk.Text搜索方法所需选项的字典
        """
        options = {}

        # 设置搜索方向
        if self.search_up:
            options["backwards"] = True  # 向上搜索
        else:
            options["forwards"] = True  # 向下搜索

        # 正则表达式匹配
        if self.regex:
            options["regexp"] = True

        # 设置全字匹配
        if self.whole_word:
            options["exact"] = True

        # 设置不区分大小写
        if self.nocase:
            options["nocase"] = True

        return options
