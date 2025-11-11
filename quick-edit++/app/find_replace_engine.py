#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
查找替换引擎模块
"""

import re
import tkinter as tk
from typing import Dict, Optional, Tuple, List


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

        # 注意：全字匹配不在这里设置，而是在FindReplaceEngine中手动处理
        # 因为Tkinter的exact选项不是真正的全字匹配

        # 设置不区分大小写
        if self.nocase:
            options["nocase"] = True

        return options


class FindReplaceEngine:
    """
    查找替换引擎类

    提供文本查找和替换的核心功能
    """

    def __init__(self, app=None):
        """
        初始化查找替换引擎

        Args:
            app: 应用程序对象
        """
        self.app = app  # 应用程序对象
        self.text_widget = app.text_area  # 文本控件
        self.last_search_pattern = ""  # 上次搜索模式
        self.last_search_options = None  # 上次搜索选项
        self.last_match_index = None  # 上次匹配位置索引
        
        # 高亮相关属性
        self.highlight_tag_current = "search_highlight_current"  # 当前匹配项高亮标签
        self.highlight_tag_all = "search_highlight_all"  # 所有匹配项高亮标签
        self.highlighting_enabled = False  # 是否启用高亮
        
        # 初始化高亮
        self._init_highlight()

    def _search_whole_word(
        self,
        pattern: str,
        search_options: SearchOptions,
        start_index: Optional[str] = None,
        stop_index: Optional[str] = None,
    ) -> Optional[str]:
        """
        执行全字匹配搜索，使用普通搜索+边界检查
        
        Args:
            pattern: 搜索模式
            search_options: 搜索选项对象
            start_index: 搜索起始位置，默认为当前插入位置
            stop_index: 搜索结束位置，默认为文档开头或结尾
            
        Returns:
            Optional[str]: 找到的匹配位置索引，如果未找到则返回None
        """
        # 确定搜索范围
        if start_index is None:
            # 如果没有指定起始位置，使用当前插入位置
            start_index = self.text_widget.index(tk.INSERT)

        if stop_index is None:
            # 如果没有指定结束位置，根据搜索方向设置
            if search_options.search_up:
                # 向上搜索，结束位置为文档开头
                stop_index = "1.0"
            else:
                # 向下搜索，结束位置为文档结尾
                stop_index = tk.END
        
        # 创建不包含whole_word选项的搜索选项
        options = search_options.get_opts()
        # 移除可能存在的whole_word相关选项
        if "whole_word" in options:
            del options["whole_word"]
        
        # 执行搜索
        try:
            print(f"全字匹配搜索模式: '{pattern}'")
            print(f"搜索选项: {options}")
            print(f"起始位置: {start_index}, 结束位置: {stop_index}")
            
            # 循环查找所有可能的匹配，直到找到全字匹配
            while True:
                match_index = self.text_widget.search(
                    pattern, start_index, stop_index, **options
                )
                
                if not match_index:
                    # 没有找到匹配项
                    print("未找到匹配项")
                    self.last_match_index = None
                    return None
                
                # 检查是否是全字匹配
                if self._is_whole_word_match(match_index, pattern):
                    print(f"找到全字匹配: {match_index}")
                    self.last_match_index = match_index
                    return match_index
                
                # 不是全字匹配，继续搜索
                # 更新起始位置为当前匹配位置的下一个字符
                start_index = self.text_widget.index(f"{match_index}+1c")
                print(f"不是全字匹配，更新起始位置为: {start_index}")
                
                # 如果已经搜索到文档末尾，停止搜索
                if not search_options.search_up and self.text_widget.compare(start_index, ">=", stop_index):
                    print("已到达文档末尾")
                    self.last_match_index = None
                    return None
                
                # 如果向上搜索且已经到达文档开头，停止搜索
                if search_options.search_up and self.text_widget.compare(start_index, "<=", stop_index):
                    print("已到达文档开头")
                    self.last_match_index = None
                    return None
                    
        except tk.TclError as e:
            # 处理正则表达式错误
            print(f"搜索错误: {e}")
            self.last_match_index = None
            return None
    
    def _is_whole_word_match(self, match_index: str, pattern: str) -> bool:
        """
        检查匹配项是否是全字匹配
        
        Args:
            match_index: 匹配位置的索引
            pattern: 搜索模式
            
        Returns:
            bool: 是否是全字匹配
        """
        # 获取匹配文本的结束位置
        end_index = f"{match_index}+{len(pattern)}c"
        end_index = self.text_widget.index(end_index)  # 确保索引格式正确
        
        # 获取匹配前后的字符
        try:
            # 获取匹配前一个字符
            prev_char = ""
            if self.text_widget.compare(match_index, ">", "1.0"):
                prev_index = self.text_widget.index(f"{match_index}-1c")
                prev_char = self.text_widget.get(prev_index, match_index)
            
            # 获取匹配后一个字符
            next_char = ""
            next_index = self.text_widget.index(f"{end_index}+1c")
            next_char = self.text_widget.get(end_index, next_index)
            
            # 检查前后字符是否都是单词边界（非单词字符）
            # 单词字符定义为字母、数字和下划线
            is_prev_boundary = not prev_char or not (prev_char.isalnum() or prev_char == "_")
            is_next_boundary = not next_char or not (next_char.isalnum() or next_char == "_")
            
            print(f"匹配位置: {match_index}, 前字符: '{prev_char}', 后字符: '{next_char}'")
            print(f"前边界: {is_prev_boundary}, 后边界: {is_next_boundary}")
            
            return is_prev_boundary and is_next_boundary
            
        except tk.TclError:
            # 如果获取字符时出错，假设是全字匹配
            return True
    


    def test_exact_match(self, pattern: str, text: str) -> bool:
        """
        测试精准匹配功能
        
        Args:
            pattern: 搜索模式
            text: 测试文本
            
        Returns:
            bool: 精准匹配是否正常工作
        """
        # 创建一个临时Text控件进行测试
        test_widget = tk.Text(self.app.root if self.app else None)
        test_widget.insert("1.0", text)
        
        # 使用精准匹配选项搜索
        options = {"exact": True, "forwards": True}
        match_index = test_widget.search(pattern, "1.0", tk.END, **options)
        
        # 获取匹配文本
        if match_index:
            end_index = f"{match_index}+{len(pattern)}c"
            matched_text = test_widget.get(match_index, end_index)
            # 销毁临时控件
            test_widget.destroy()
            return matched_text == pattern
        else:
            # 销毁临时控件
            test_widget.destroy()
            return False

    def search(
        self,
        pattern: str,
        search_options: SearchOptions,
        start_index: Optional[str] = None,
        stop_index: Optional[str] = None,
    ) -> Optional[str]:
        """
        执行单次搜索任务

        Args:
            pattern: 搜索模式
            search_options: 搜索选项对象
            start_index: 搜索起始位置，默认为当前插入位置
            stop_index: 搜索结束位置，默认为文档开头或结尾

        Returns:
            Optional[str]: 找到的匹配位置索引，如果未找到则返回None
        """
        if not pattern:
            return None

        # 保存当前搜索信息
        self.last_search_pattern = pattern  # 上次搜索模式
        self.last_search_options = search_options  # 上次搜索选项

        # 对于全字匹配，我们需要特殊处理
        if search_options.whole_word:
            return self._search_whole_word(pattern, search_options, start_index, stop_index)
        
        # 普通搜索
        search_pattern = pattern  # 搜索模式
        options = search_options.get_opts()  # 搜索选项参数

        # 确定搜索范围
        if start_index is None:
            # 如果没有指定起始位置，使用当前插入位置
            start_index = self.text_widget.index(tk.INSERT)

        if stop_index is None:
            # 如果没有指定结束位置，根据搜索方向设置
            if search_options.search_up:
                # 向上搜索，结束位置为文档开头
                stop_index = "1.0"
            else:
                # 向下搜索，结束位置为文档结尾
                stop_index = tk.END

        # 执行搜索
        try:
            # 添加调试信息
            print(f"搜索模式: '{search_pattern}'")
            print(f"搜索选项: {options}")
            
            match_index = self.text_widget.search(
                search_pattern, start_index, stop_index, **options
            )
            
            print(f"匹配结果: {match_index}")

            # 处理搜索结果
            if match_index:
                # 如果找到匹配项，更新上次匹配位置索引
                self.last_match_index = match_index
                
                # 获取匹配文本进行验证
                end_index = f"{match_index}+{len(search_pattern)}c"
                matched_text = self.text_widget.get(match_index, end_index)
                print(f"匹配文本: '{matched_text}'")
                
                return match_index
            
            else:
                # 如果未找到匹配项，清空上次匹配位置索引
                self.last_match_index = None
                return None

        except tk.TclError as e:
            # 处理正则表达式错误
            print(f"搜索错误: {e}")
            self.last_match_index = None
            return None

    def get_match_range(self, match_index: str) -> Tuple[str, str]:
        """
        获取匹配文本的范围

        Args:
            match_index: 匹配位置的索引

        Returns:
            Tuple[str, str]: 匹配文本的开始和结束位置
        """
        if not match_index:
            return "", ""

        # 获取匹配文本的结束位置
        if self.last_search_options and self.last_search_options.regex:
            # 对于正则表达式，使用正则匹配确定长度
            end_index = f"{match_index}+1c"
        else:
            # 对于普通文本，使用模式长度确定结束位置
            pattern_len = len(self.last_search_pattern)
            end_index = f"{match_index}+{pattern_len}c"

        return match_index, end_index

    def select_match(self, match_index: str) -> bool:
        """
        选择匹配的文本

        Args:
            match_index: 匹配位置的索引

        Returns:
            bool: 是否成功选择
        """
        if not match_index:
            return False

        start_index, end_index = self.get_match_range(match_index)

        # 选择文本
        self.text_widget.tag_remove(tk.SEL, "1.0", tk.END)
        self.text_widget.tag_add(tk.SEL, start_index, end_index)
        self.text_widget.mark_set(tk.INSERT, start_index)
        self.text_widget.see(start_index)

        return True
    
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
        
        # 确定搜索起始位置
        if self.last_match_index:
            # 如果有上次匹配位置，从匹配位置的下一个字符开始搜索
            start_index, end_index = self.get_match_range(self.last_match_index)
            # 使用text_widget.index()将位置转换为正确的索引格式
            start_index = self.text_widget.index(end_index)
        else:
            # 如果没有上次匹配位置，从当前光标位置开始搜索
            start_index = self.text_widget.index(tk.INSERT)
            
        # 执行搜索
        match_index = self.search(pattern, search_options, start_index)
        
        # 如果找到匹配项，选中它
        if match_index:
            self.select_match(match_index)
            # 只高亮当前匹配项
            self.highlight_current_match(match_index)
            return True
        else:
            # 如果从当前位置没找到，从文档开头重新搜索
            if start_index != "1.0":
                match_index = self.search(pattern, search_options, "1.0", start_index)
                if match_index:
                    self.select_match(match_index)
                    # 只高亮当前匹配项
                    self.highlight_current_match(match_index)
                    return True
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
        
        # 确定搜索起始位置
        if self.last_match_index:
            # 如果有上次匹配位置，从匹配位置开始搜索（不包括匹配文本）
            start_index = self.text_widget.index(self.last_match_index)
        else:
            # 如果没有上次匹配位置，从当前光标位置开始搜索
            start_index = self.text_widget.index(tk.INSERT)
            
        # 执行搜索
        match_index = self.search(pattern, search_options, start_index)
        
        # 如果找到匹配项，选中它
        if match_index:
            self.select_match(match_index)
            # 只高亮当前匹配项
            self.highlight_current_match(match_index)
            return True
        else:
            # 如果从当前位置没找到，从文档结尾重新搜索
            if start_index != tk.END:
                match_index = self.search(pattern, search_options, tk.END, start_index)
                if match_index:
                    self.select_match(match_index)
                    # 只高亮当前匹配项
                    self.highlight_current_match(match_index)
                    return True
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
                
        # 创建搜索选项的副本，确保向下搜索
        search_options = SearchOptions(
            nocase=search_options.nocase,
            whole_word=search_options.whole_word,
            regex=search_options.regex,
            search_up=False  # 总是向下搜索
        )
        
        # 保存原始搜索选项
        original_options = self.last_search_options
        self.last_search_options = search_options
        
        # 从文档开头开始搜索
        start_index = "1.0"
        matches = []
        
        while True:
            # 执行搜索
            match_index = self.search(pattern, search_options, start_index)
            
            if not match_index:
                break
                
            # 获取匹配范围
            start_pos, end_pos = self.get_match_range(match_index)
            matches.append((start_pos, end_pos))
            
            # 更新搜索起始位置为匹配结束位置
            start_index = end_pos
            
            # 防止无限循环
            if start_index == tk.END:
                break
                
        # 恢复原始搜索选项
        self.last_search_options = original_options
        
        # 如果需要高亮，高亮所有匹配项
        if highlight:
            self.highlight_all_matches(pattern, search_options)
        
        return matches
    
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
        # 在Tkinter中，标签的优先级决定了重叠时的显示顺序
        # 优先级数值越小，显示层级越高
        self.text_widget.tag_raise(self.highlight_tag_current, self.highlight_tag_all)
        
        # 启用高亮
        self.highlighting_enabled = True
    
    def highlight_all_matches(self, pattern: str = None, search_options: SearchOptions = None) -> List[Tuple[str, str]]:
        """
        高亮所有匹配项
        
        Args:
            pattern: 搜索模式，如果为None则使用上次搜索模式
            search_options: 搜索选项，如果为None则使用上次搜索选项
            
        Returns:
            List[Tuple[str, str]]: 所有匹配项的位置列表，每个元素为(开始位置, 结束位置)
        """
        # 如果高亮未启用，先初始化
        if not self.highlighting_enabled:
            self._init_highlight()
        
        # 清除之前的高亮
        self.clear_highlights()
        
        # 使用提供的参数或默认值
        if pattern is None:
            pattern = self.last_search_pattern
        if search_options is None:
            search_options = self.last_search_options
            
        # 如果没有搜索模式，返回空列表
        if not pattern:
            return []
        
        # 调用find_all查找所有匹配项，传递highlight=False避免递归
        matches = self.find_all(pattern, search_options, highlight=False)
        
        # 高亮所有匹配项
        for start_pos, end_pos in matches:
            self.text_widget.tag_add(self.highlight_tag_all, start_pos, end_pos)
        
        return matches
    
    def highlight_current_match(self, match_index: str = None) -> bool:
        """
        高亮当前匹配项
        
        Args:
            match_index: 匹配位置的索引，如果为None则使用上次匹配位置
            
        Returns:
            bool: 是否成功高亮
        """
        # 如果高亮未启用，先初始化
        if not self.highlighting_enabled:
            self._init_highlight()
        
        # 只清除当前匹配项的高亮，保留所有匹配项的高亮
        self.text_widget.tag_remove(self.highlight_tag_current, "1.0", tk.END)
        
        # 如果没有提供匹配索引，使用上次匹配位置
        if match_index is None:
            match_index = self.last_match_index
            
        if not match_index:
            return False
            
        # 获取匹配范围
        start_pos, end_pos = self.get_match_range(match_index)
        
        # 高亮当前匹配项
        self.text_widget.tag_add(self.highlight_tag_current, start_pos, end_pos)
        
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
        if not self.last_match_index:
            return False
            
        # 获取匹配范围
        start_pos, end_pos = self.get_match_range(self.last_match_index)
        
        # 替换文本
        self.text_widget.delete(start_pos, end_pos)
        self.text_widget.insert(start_pos, replacement)
        
        # 清除高亮
        self.clear_highlights()
        
        return True
    
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
        matches = self.find_all(pattern, search_options)
        
        # 如果没有匹配项，返回0
        if not matches:
            return 0
            
        # 从后往前替换，避免位置偏移
        replace_count = 0
        for start_pos, end_pos in reversed(matches):
            self.text_widget.delete(start_pos, end_pos)
            self.text_widget.insert(start_pos, replacement)
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
