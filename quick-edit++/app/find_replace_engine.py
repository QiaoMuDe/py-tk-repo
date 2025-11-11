#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
查找替换引擎模块 - 使用Python字符串搜索和re正则模块实现
"""

import re
import tkinter as tk
from typing import List, Tuple, Optional


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


class IndexConverter:
    """
    索引转换器类
    
    负责在Python字符串位置和Tkinter索引格式之间进行转换
    """
    
    def __init__(self, text_widget):
        """
        初始化索引转换器
        
        Args:
            text_widget: Tkinter文本控件
        """
        self.text_widget = text_widget # 文本控件
        self._line_offsets_cache = None  # 行偏移缓存
        self._text_content_hash = None   # 文本内容哈希
        
    def _update_line_offsets_cache(self):
        """
        更新行偏移缓存
        """
        # 获取文本内容
        text = self.text_widget.get("1.0", tk.END)
        
        # 计算文本哈希
        current_hash = hash(text)
        
        # 如果文本内容没有变化，不需要更新缓存
        if self._text_content_hash == current_hash and self._line_offsets_cache is not None:
            return
            
        # 计算每行的起始偏移量
        self._line_offsets_cache = [0]  # 第一行偏移为0
        
        # 遍历文本，记录每行的起始偏移量
        offset = 0
        for char in text:
            if char == '\n':
                self._line_offsets_cache.append(offset + 1)  # 下一行偏移为换行符后一个位置
            offset += 1
            
        # 更新文本哈希
        self._text_content_hash = current_hash
    
    def string_pos_to_tk_index(self, pos: int) -> str:
        """
        将Python字符串位置转换为Tkinter索引格式
        
        Args:
            pos: Python字符串位置(0-based)
            
        Returns:
            str: Tkinter索引格式(如"1.0")
        """
        # 更新行偏移缓存
        self._update_line_offsets_cache()
        
        # 边界情况处理
        if pos <= 0:
            return "1.0"
            
        # 获取文本内容
        text = self.text_widget.get("1.0", tk.END)
        
        # 如果位置超出文本长度，返回最后一个位置
        if pos >= len(text):
            # 计算最后一行的行号和列号
            lines = text.count('\n') + 1
            last_line_start = text.rfind('\n')
            if last_line_start == -1:
                return f"1.{len(text)}"
            else:
                return f"{lines}.{len(text) - last_line_start - 1}"
        
        # 查找位置所在的行
        line = 1
        while line < len(self._line_offsets_cache) and pos >= self._line_offsets_cache[line]:
            line += 1
        line -= 1  # 回退到正确的行号
        
        # 计算列号
        column = pos - self._line_offsets_cache[line]
        
        # 返回Tkinter索引格式
        return f"{line + 1}.{column}"
    
    def tk_index_to_string_pos(self, tk_index: str) -> int:
        """
        将Tkinter索引格式转换为Python字符串位置
        
        Args:
            tk_index: Tkinter索引格式(如"1.0")
            
        Returns:
            int: Python字符串位置(0-based)
        """
        # 更新行偏移缓存
        self._update_line_offsets_cache()
        
        # 解析Tkinter索引
        parts = tk_index.split('.')
        line = int(parts[0]) - 1  # Tkinter行号从1开始，Python从0开始
        column = int(parts[1]) if len(parts) > 1 else 0
        
        # 边界情况处理
        if line < 0:
            return 0
            
        # 如果行号超出范围，返回文本末尾位置
        if line >= len(self._line_offsets_cache):
            return len(self.text_widget.get("1.0", tk.END)) - 1  # 减去最后的换行符
        
        # 计算字符串位置
        pos = self._line_offsets_cache[line] + column
        
        # 确保位置不超出文本长度
        text_len = len(self.text_widget.get("1.0", tk.END))
        if pos >= text_len:
            pos = text_len - 1  # 减去最后的换行符
            
        return pos


class FindReplaceEngine:
    """
    查找替换引擎类

    提供文本查找和替换的核心功能，使用Python字符串搜索和re正则模块
    """

    def __init__(self, app=None):
        """
        初始化查找替换引擎

        Args:
            app: 应用程序对象
        """
        self.app = app  # 应用程序对象
        self.text_widget = app.text_area  # 文本控件
        self.index_converter = IndexConverter(self.text_widget)  # 索引转换器
        
        # 搜索状态
        self.last_search_pattern = ""  # 上次搜索模式
        self.last_search_options = None  # 上次搜索选项
        self.last_match_pos = None  # 上次匹配位置(字符串位置)
        self.all_matches = []  # 所有匹配项的字符串位置列表
        
        # 高亮相关属性
        self.highlight_tag_current = "search_highlight_current"  # 当前匹配项高亮标签
        self.highlight_tag_all = "search_highlight_all"  # 所有匹配项高亮标签
        self.highlighting_enabled = False  # 是否启用高亮
        
        # 初始化高亮
        self._init_highlight()

    def _init_highlight(self):
        """
        初始化高亮标签和颜色配置
        """
        # 配置高亮颜色 
        # 当前匹配项使用橙色，其他匹配项使用绿色
        current_highlight_color = "#feae00"  # 橙色，对眼睛友好
        all_highlight_color = "#90fe00"  # 绿色，对眼睛友好
        
        # 配置高亮标签
        self.text_widget.tag_config(
            self.highlight_tag_current,
            background=current_highlight_color,
            foreground="black"
        )
        
        self.text_widget.tag_config(
            self.highlight_tag_all,
            background=all_highlight_color,
            foreground="black"
        )
        
        # 设置当前匹配项标签的优先级高于所有匹配项标签
        self.text_widget.tag_raise(self.highlight_tag_current, self.highlight_tag_all)
        
        # 启用高亮
        self.highlighting_enabled = True

    def _prepare_search_pattern(self, pattern: str, search_options: SearchOptions) -> str:
        """
        准备搜索模式
        
        Args:
            pattern: 原始搜索模式
            search_options: 搜索选项
            
        Returns:
            str: 处理后的搜索模式
        """
        # 如果是正则表达式，直接返回
        if search_options.regex:
            return pattern
            
        # 如果是全字匹配，添加单词边界
        if search_options.whole_word:
            return r'\b' + re.escape(pattern) + r'\b'
            
        # 否则，转义特殊字符
        return re.escape(pattern)

    def _compile_regex(self, pattern: str, search_options: SearchOptions) -> re.Pattern:
        """
        编译正则表达式
        
        Args:
            pattern: 搜索模式
            search_options: 搜索选项
            
        Returns:
            re.Pattern: 编译后的正则表达式
        """
        # 准备搜索模式
        search_pattern = self._prepare_search_pattern(pattern, search_options)
        
        # 设置正则表达式标志
        flags = 0
        if search_options.nocase:
            flags |= re.IGNORECASE
            
        # 编译正则表达式
        try:
            return re.compile(search_pattern, flags)
        except re.error as e:
            # 如果正则表达式有误，抛出异常
            raise ValueError(f"正则表达式错误: {e}")

    def _find_all_matches(self, pattern: str, search_options: SearchOptions) -> List[Tuple[int, int]]:
        """
        查找所有匹配项
        
        Args:
            pattern: 搜索模式
            search_options: 搜索选项
            
        Returns:
            List[Tuple[int, int]]: 所有匹配项的字符串位置列表，每个元素为(开始位置, 结束位置)
        """
        # 获取文本内容
        text = self.text_widget.get("1.0", tk.END)
        
        # 如果文本为空，返回空列表
        if not text:
            return []
            
        # 编译正则表达式
        try:
            regex = self._compile_regex(pattern, search_options)
        except ValueError:
            # 如果正则表达式有误，返回空列表
            return []
            
        # 查找所有匹配项
        matches = []
        for match in regex.finditer(text):
            matches.append((match.start(), match.end()))
            
        return matches

    def _find_next_match(self, pattern: str, search_options: SearchOptions, start_pos: int = None) -> Optional[Tuple[int, int]]:
        """
        查找下一个匹配项
        
        Args:
            pattern: 搜索模式
            search_options: 搜索选项
            start_pos: 搜索起始位置(字符串位置)，如果为None则从当前光标位置开始
            
        Returns:
            Optional[Tuple[int, int]]: 下一个匹配项的字符串位置，如果未找到则返回None
        """
        # 获取文本内容
        text = self.text_widget.get("1.0", tk.END)
        
        # 如果文本为空，返回None
        if not text:
            return None
            
        # 确定搜索起始位置
        if start_pos is None:
            # 从当前光标位置开始
            current_index = self.text_widget.index(tk.INSERT)
            start_pos = self.index_converter.tk_index_to_string_pos(current_index)
            
        # 编译正则表达式
        try:
            regex = self._compile_regex(pattern, search_options)
        except ValueError:
            # 如果正则表达式有误，返回None
            return None
            
        # 查找下一个匹配项
        if search_options.search_up:
            # 向上搜索
            matches = []
            for match in regex.finditer(text):
                if match.end() <= start_pos:
                    matches.append((match.start(), match.end()))
            
            # 返回最后一个匹配项
            return matches[-1] if matches else None
        else:
            # 向下搜索
            for match in regex.finditer(text):
                if match.start() >= start_pos:
                    return (match.start(), match.end())
            
            # 如果没有找到，从文档开头重新搜索
            for match in regex.finditer(text):
                return (match.start(), match.end())
                
            return None

    def _find_previous_match(self, pattern: str, search_options: SearchOptions, start_pos: int = None) -> Optional[Tuple[int, int]]:
        """
        查找上一个匹配项
        
        Args:
            pattern: 搜索模式
            search_options: 搜索选项
            start_pos: 搜索起始位置(字符串位置)，如果为None则从当前光标位置开始
            
        Returns:
            Optional[Tuple[int, int]]: 上一个匹配项的字符串位置，如果未找到则返回None
        """
        # 获取文本内容
        text = self.text_widget.get("1.0", tk.END)
        
        # 如果文本为空，返回None
        if not text:
            return None
            
        # 确定搜索起始位置
        if start_pos is None:
            # 从当前光标位置开始
            current_index = self.text_widget.index(tk.INSERT)
            start_pos = self.index_converter.tk_index_to_string_pos(current_index)
            
        # 编译正则表达式
        try:
            regex = self._compile_regex(pattern, search_options)
        except ValueError:
            # 如果正则表达式有误，返回None
            return None
            
        # 查找上一个匹配项
        matches = []
        for match in regex.finditer(text):
            if match.start() < start_pos:
                matches.append((match.start(), match.end()))
        
        # 返回最后一个匹配项
        if matches:
            return matches[-1]
        else:
            # 如果没有找到，从文档末尾重新搜索
            for match in regex.finditer(text):
                matches.append((match.start(), match.end()))
            
            return matches[-1] if matches else None

    def search(self, pattern: str, search_options: SearchOptions) -> bool:
        """
        执行搜索
        
        Args:
            pattern: 搜索模式
            search_options: 搜索选项
            
        Returns:
            bool: 是否找到匹配项
        """
        if not pattern:
            return False
            
        # 保存搜索信息
        self.last_search_pattern = pattern
        self.last_search_options = search_options
        
        # 查找所有匹配项
        self.all_matches = self._find_all_matches(pattern, search_options)
        
        # 如果没有匹配项，返回False
        if not self.all_matches:
            self.last_match_pos = None
            return False
            
        # 查找下一个匹配项
        match = self._find_next_match(pattern, search_options)
        if match:
            self.last_match_pos = match[0]
            self._select_match(match)
            self._highlight_current_match(match)
            return True
        else:
            self.last_match_pos = None
            return False

    def find_next(self, pattern: str = None, search_options: SearchOptions = None) -> bool:
        """
        查找下一个匹配项
        
        Args:
            pattern: 搜索模式，如果为None则使用上次搜索模式
            search_options: 搜索选项，如果为None则使用上次搜索选项
            
        Returns:
            bool: 是否找到并选中了匹配项
        """
        # 如果没有提供搜索模式，使用上次搜索模式
        if pattern is None:
            if not self.last_search_pattern:
                return False
            pattern = self.last_search_pattern
            
        # 如果没有提供搜索选项，使用上次搜索选项
        if search_options is None:
            if self.last_search_options is None:
                # 如果没有上次搜索选项，创建默认选项（向下搜索）
                search_options = SearchOptions(search_up=False)
            else:
                search_options = self.last_search_options
                
        # 确保搜索方向是向下
        search_options.search_up = False
        
        # 保存搜索信息
        self.last_search_pattern = pattern
        self.last_search_options = search_options
        
        # 确定搜索起始位置
        start_pos = None
        if self.last_match_pos is not None:
            # 从上次匹配位置的下一个字符开始搜索
            start_pos = self.last_match_pos + 1
            
        # 查找下一个匹配项
        match = self._find_next_match(pattern, search_options, start_pos)
        if match:
            self.last_match_pos = match[0]
            self._select_match(match)
            self._highlight_current_match(match)
            return True
        else:
            # 如果从当前位置没找到，从文档开头重新搜索
            match = self._find_next_match(pattern, search_options, 0)
            if match:
                self.last_match_pos = match[0]
                self._select_match(match)
                self._highlight_current_match(match)
                return True
            else:
                # 如果没有找到任何匹配项，清除高亮
                self.clear_highlights()
                return False

    def find_previous(self, pattern: str = None, search_options: SearchOptions = None) -> bool:
        """
        查找上一个匹配项
        
        Args:
            pattern: 搜索模式，如果为None则使用上次搜索模式
            search_options: 搜索选项，如果为None则使用上次搜索选项
            
        Returns:
            bool: 是否找到并选中了匹配项
        """
        # 如果没有提供搜索模式，使用上次搜索模式
        if pattern is None:
            if not self.last_search_pattern:
                return False
            pattern = self.last_search_pattern
            
        # 如果没有提供搜索选项，使用上次搜索选项
        if search_options is None:
            if self.last_search_options is None:
                # 如果没有上次搜索选项，创建默认选项（向上搜索）
                search_options = SearchOptions(search_up=True)
            else:
                search_options = self.last_search_options
                
        # 确保搜索方向是向上
        search_options.search_up = True
        
        # 保存搜索信息
        self.last_search_pattern = pattern
        self.last_search_options = search_options
        
        # 确定搜索起始位置
        start_pos = None
        if self.last_match_pos is not None:
            # 从上次匹配位置开始搜索
            start_pos = self.last_match_pos
            
        # 查找上一个匹配项
        match = self._find_previous_match(pattern, search_options, start_pos)
        if match:
            self.last_match_pos = match[0]
            self._select_match(match)
            self._highlight_current_match(match)
            return True
        else:
            # 如果从当前位置没找到，从文档末尾重新搜索
            text = self.text_widget.get("1.0", tk.END)
            start_pos = len(text)
            match = self._find_previous_match(pattern, search_options, start_pos)
            if match:
                self.last_match_pos = match[0]
                self._select_match(match)
                self._highlight_current_match(match)
                return True
            else:
                # 如果没有找到任何匹配项，清除高亮
                self.clear_highlights()
                return False

    def find_all(self, pattern: str = None, search_options: SearchOptions = None, highlight: bool = True) -> List[Tuple[str, str]]:
        """
        查找所有匹配项
        
        Args:
            pattern: 搜索模式，如果为None则使用上次搜索模式
            search_options: 搜索选项，如果为None则使用上次搜索选项
            highlight: 是否高亮所有匹配项，默认为True
            
        Returns:
            List[Tuple[str, str]]: 所有匹配项的位置列表，每个元素为(开始位置, 结束位置)
        """
        # 如果没有提供搜索模式，使用上次搜索模式
        if pattern is None:
            if not self.last_search_pattern:
                return []
            pattern = self.last_search_pattern
            
        # 如果没有提供搜索选项，使用上次搜索选项
        if search_options is None:
            if self.last_search_options is None:
                # 如果没有上次搜索选项，创建默认选项
                search_options = SearchOptions()
            else:
                search_options = self.last_search_options
                
        # 保存搜索信息
        self.last_search_pattern = pattern
        self.last_search_options = search_options
        
        # 查找所有匹配项
        self.all_matches = self._find_all_matches(pattern, search_options)
        
        # 转换为Tkinter索引格式
        tk_matches = []
        for start_pos, end_pos in self.all_matches:
            start_index = self.index_converter.string_pos_to_tk_index(start_pos)
            end_index = self.index_converter.string_pos_to_tk_index(end_pos)
            tk_matches.append((start_index, end_index))
            
        # 如果需要高亮，高亮所有匹配项
        if highlight:
            self._highlight_all_matches(tk_matches)
            
        return tk_matches

    def _select_match(self, match: Tuple[int, int]) -> bool:
        """
        选择匹配的文本
        
        Args:
            match: 匹配位置的字符串位置元组(开始位置, 结束位置)
            
        Returns:
            bool: 是否成功选择
        """
        if not match:
            return False
            
        # 转换为Tkinter索引格式
        start_index = self.index_converter.string_pos_to_tk_index(match[0])
        end_index = self.index_converter.string_pos_to_tk_index(match[1])
        
        # 选择文本
        self.text_widget.tag_remove(tk.SEL, "1.0", tk.END)
        self.text_widget.tag_add(tk.SEL, start_index, end_index)
        self.text_widget.mark_set(tk.INSERT, start_index)
        self.text_widget.see(start_index)
        
        return True

    def _highlight_current_match(self, match: Tuple[int, int]) -> bool:
        """
        高亮当前匹配项
        
        Args:
            match: 匹配位置的字符串位置元组(开始位置, 结束位置)
            
        Returns:
            bool: 是否成功高亮
        """
        # 如果高亮未启用，先初始化
        if not self.highlighting_enabled:
            self._init_highlight()
            
        # 只清除当前匹配项的高亮，保留所有匹配项的高亮
        self.text_widget.tag_remove(self.highlight_tag_current, "1.0", tk.END)
        
        if not match:
            return False
            
        # 转换为Tkinter索引格式
        start_index = self.index_converter.string_pos_to_tk_index(match[0])
        end_index = self.index_converter.string_pos_to_tk_index(match[1])
        
        # 高亮当前匹配项
        self.text_widget.tag_add(self.highlight_tag_current, start_index, end_index)
        
        return True

    def _highlight_all_matches(self, matches: List[Tuple[str, str]]) -> bool:
        """
        高亮所有匹配项
        
        Args:
            matches: 匹配项的Tkinter索引位置列表
            
        Returns:
            bool: 是否成功高亮
        """
        # 如果高亮未启用，先初始化
        if not self.highlighting_enabled:
            self._init_highlight()
            
        # 清除之前的高亮
        self.clear_highlights()
        
        # 高亮所有匹配项
        for start_index, end_index in matches:
            self.text_widget.tag_add(self.highlight_tag_all, start_index, end_index)
            
        return True

    def clear_highlights(self):
        """
        清除所有高亮
        """
        if self.highlighting_enabled:
            self.text_widget.tag_remove(self.highlight_tag_current, "1.0", tk.END)
            self.text_widget.tag_remove(self.highlight_tag_all, "1.0", tk.END)

    def set_highlight_enabled(self, enabled: bool):
        """
        设置是否启用高亮
        
        Args:
            enabled: 是否启用高亮
        """
        self.highlighting_enabled = enabled
        
        if not enabled:
            self.clear_highlights()

    def replace(self, replacement: str) -> bool:
        """
        替换当前选中的匹配项
        
        Args:
            replacement: 替换文本
            
        Returns:
            bool: 是否成功替换
        """
        # 如果没有上次匹配位置，返回False
        if self.last_match_pos is None:
            return False
            
        # 查找当前匹配项
        if self.last_search_options:
            matches = self._find_all_matches(self.last_search_pattern, self.last_search_options)
            # 找到包含last_match_pos的匹配项
            current_match = None
            for start_pos, end_pos in matches:
                if start_pos <= self.last_match_pos < end_pos:
                    current_match = (start_pos, end_pos)
                    break
                    
            if not current_match:
                return False
                
            # 转换为Tkinter索引格式
            start_index = self.index_converter.string_pos_to_tk_index(current_match[0])
            end_index = self.index_converter.string_pos_to_tk_index(current_match[1])
            
            # 替换文本
            self.text_widget.delete(start_index, end_index)
            self.text_widget.insert(start_index, replacement)
            
            # 清除高亮
            self.clear_highlights()
            
            # 更新光标位置到替换文本的末尾
            self.text_widget.mark_set(tk.INSERT, f"{start_index}+{len(replacement)}c")
            
            return True
        else:
            return False

    def replace_all(self, pattern: str = None, replacement: str = "", search_options: SearchOptions = None) -> int:
        """
        替换所有匹配项
        
        Args:
            pattern: 搜索模式，如果为None则使用上次搜索模式
            replacement: 替换文本
            search_options: 搜索选项，如果为None则使用上次搜索选项
            
        Returns:
            int: 替换的数量
        """
        # 查找所有匹配项
        matches = self.find_all(pattern, search_options, highlight=False)
        
        # 如果没有匹配项，返回0
        if not matches:
            return 0
            
        # 从后往前替换，避免位置偏移
        replace_count = 0
        for start_index, end_index in reversed(matches):
            self.text_widget.delete(start_index, end_index)
            self.text_widget.insert(start_index, replacement)
            replace_count += 1
            
        # 清除高亮
        self.clear_highlights()
        
        return replace_count

    def update_highlight_colors(self, current_color: str = None, all_color: str = None):
        """
        更新高亮颜色
        
        Args:
            current_color: 当前匹配项的高亮颜色，格式为"#RRGGBB"
            all_color: 所有匹配项的高亮颜色，格式为"#RRGGBB"
        """
        if current_color:
            self.text_widget.tag_config(
                self.highlight_tag_current,
                background=current_color
            )
            
        if all_color:
            self.text_widget.tag_config(
                self.highlight_tag_all,
                background=all_color
            )
