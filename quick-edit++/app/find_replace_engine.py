#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
查找替换引擎模块 - 使用Python字符串搜索和re正则模块实现
"""

import tkinter as tk
from typing import List, Tuple, Optional


class SearchOptions:
    """
    搜索选项类

    封装搜索时使用的各种选项, 如不区分大小写、向上搜索等
    """

    def __init__(
        self,
        nocase: bool = False,
        whole_word: bool = False,
        regex: bool = False,
        normal_search: bool = True,
        search_up: bool = False,
        single_search: bool = True,
    ):
        """
        初始化搜索选项

        Args:
            nocase: 是否不区分大小写, 默认为False
            whole_word: 是否全词匹配, 默认为False
            regex: 是否正则表达式, 默认为False
            normal_search: 是否普通搜索, 默认为True
            search_up: 是否向上搜索, 默认为False (默认向下搜索)
            single_search: 是否单次搜索, 默认为True
        """
        # 三种基础搜索模式（普通、全词、正则）互斥，但nocase可与任意一种组合
        base_modes = sum([normal_search, whole_word, regex])
        if base_modes > 1:
            # 如果同时设置了多种基础搜索模式，优先顺序：正则 > 全词 > 普通
            normal_search = False
            if whole_word and regex:
                whole_word = False
                regex = True
            elif whole_word:
                regex = False

        elif base_modes == 0:
            # 如果没有设置任何基础模式，默认使用普通搜索
            normal_search = True

        self.nocase = nocase  # 是否不区分大小写
        self.whole_word = whole_word  # 是否全词匹配
        self.regex = regex  # 是否正则表达式
        self.normal_search = normal_search  # 是否普通搜索
        self.search_up = search_up  # 是否向上搜索 (默认向下搜索)
        self.single_search = single_search  # 是否单次搜索 (默认为True)


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
        # 基本属性
        self.app = app  # 应用程序对象
        self.text_widget = app.text_area  # 文本控件
        self.current_match: Optional[Tuple[str, str]] = None  # 当前匹配项

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
            foreground="black",
        )

        self.text_widget.tag_config(
            self.highlight_tag_all, background=all_highlight_color, foreground="black"
        )

        # 设置当前匹配项标签的优先级高于所有匹配项标签
        self.text_widget.tag_raise(self.highlight_tag_current, self.highlight_tag_all)

        # 确保选中标签的优先级最高，防止被查找高亮覆盖
        self.text_widget.tag_raise("sel", self.highlight_tag_current)

        # 启用高亮
        self.highlighting_enabled = True

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

        # 清除当前匹配项
        self.current_match = None

    def find(
        self, pattern: str, search_options: SearchOptions
    ) -> List[Tuple[str, str]]:
        """
        核心查找方法 - 基于Text组件的search()方法实现

        Args:
            pattern: 搜索模式
            search_options: 搜索选项

        Returns:
            List[Tuple[str, str]]: 匹配项的Tk索引元组列表[(开始索引, 结束索引)]
        """
        if not pattern:
            return []

        # 根据搜索类型决定是否清除所有高亮
        if search_options.single_search:
            # 单次查找：只清除当前匹配项的高亮，保留其他匹配项
            if self.highlighting_enabled:
                self.text_widget.tag_remove(self.highlight_tag_current, "1.0", tk.END)
            self.current_match = None
        else:
            # 搜索全部：清除所有高亮
            self.clear_highlights()

        matches = []
        count_var = tk.StringVar()

        # 获取当前光标位置作为搜索起点，确保绝对健壮性
        try:
            # 尝试获取光标位置，但不进行复杂验证
            # 任何异常都直接使用文档顶部作为搜索起点
            current_pos = self.text_widget.index(tk.INSERT)
            # 简单验证：确保获取到的值不为空
            if not current_pos or not isinstance(current_pos, str):
                current_pos = "1.0"
        except:
            # 捕获所有可能的异常，包括TclError、ValueError等
            # 无条件使用文档顶部作为搜索起点
            current_pos = "1.0"

        # 配置搜索参数
        search_args = {"count": count_var}

        # 根据搜索模式配置参数
        # 首先处理不区分大小写参数（可与任意基础模式组合）
        if search_options.nocase:
            search_args["nocase"] = True

        # 然后处理基础搜索模式（三种模式互斥）
        if search_options.whole_word:
            # 全词匹配搜索
            search_args["regexp"] = True
            # 使用\y前后包围搜索模式实现全词匹配
            pattern = rf"\y{pattern}\y"
        elif search_options.regex:
            # 正则表达式搜索
            search_args["regexp"] = True
        elif search_options.normal_search:
            # 普通搜索模式不添加额外参数 (normal_search为True时)
            # 默认搜索模式也不添加额外参数
            pass

        # 配置搜索方向和起点
        if search_options.single_search:
            # 单次搜索使用当前光标位置作为起点
            if search_options.search_up:
                # 向上搜索
                start_pos = current_pos
                end_pos = "1.0"
                search_args["backwards"] = True
            else:
                # 向下搜索
                start_pos = current_pos
                end_pos = tk.END
                search_args["forwards"] = True
        else:
            # 搜索全部总是从文档开头开始向下搜索
            start_pos = "1.0"
            end_pos = tk.END
            search_args["forwards"] = True

        # 执行搜索
        if search_options.single_search:
            # 单次搜索
            # 第一次搜索：从当前位置到文档末尾/开头
            match_pos = self.text_widget.search(
                pattern, start_pos, end_pos, **search_args
            )

            if match_pos:  # 如果找到匹配项（返回非空字符串索引）
                # Text.search返回字符串索引格式"行.列"，找到时返回非空字符串
                count = int(count_var.get()) if count_var.get() else 0
                end_idx = self.text_widget.index(f"{match_pos}+{count}c")
                matches.append((match_pos, end_idx))
            else:
                # 没有找到匹配项，执行循环搜索
                if search_options.search_up:
                    # 向上搜索：从文档末尾搜索到当前光标位置之前
                    loop_start_pos = tk.END
                    loop_end_pos = start_pos
                else:
                    # 向下搜索：从文档开头搜索到当前光标位置之前
                    loop_start_pos = "1.0"
                    loop_end_pos = start_pos
                    # 向下搜索需要特殊处理，确保不会重复搜索当前位置
                    if loop_end_pos != "1.0":
                        # 从文档开头搜索到当前光标位置之前
                        loop_end_pos = self.text_widget.index(f"{loop_end_pos}-1c")

                # 执行循环搜索
                match_pos = self.text_widget.search(
                    pattern, loop_start_pos, loop_end_pos, **search_args
                )

                if match_pos:  # 如果找到匹配项
                    count = int(count_var.get()) if count_var.get() else 0
                    end_idx = self.text_widget.index(f"{match_pos}+{count}c")
                    matches.append((match_pos, end_idx))
        else:
            # 搜索全部
            pos = start_pos

            while True:
                match_pos = self.text_widget.search(
                    pattern, pos, end_pos, **search_args
                )

                if not match_pos:  # 没有找到匹配项（返回空字符串）
                    break

                count = int(count_var.get()) if count_var.get() else 0
                end_idx = self.text_widget.index(f"{match_pos}+{count}c")
                matches.append((match_pos, end_idx))

                # 移动到当前匹配项之后/之前继续搜索
                if search_options.search_up:
                    pos = self.text_widget.index(f"{match_pos}-1c")
                else:
                    pos = end_idx

        return matches

    def find_next(
        self, pattern: str, search_options: SearchOptions
    ) -> Optional[Tuple[str, str]]:
        """
        查找下一个匹配项

        Args:
            pattern: 搜索模式
            search_options: 搜索选项（会覆盖search_up和single_search参数）

        Returns:
            Optional[Tuple[str, str]]: 匹配项的Tk索引元组(开始索引, 结束索引)，未找到返回None
        """
        # 确保是向下搜索且单次搜索
        search_options_copy = SearchOptions(
            nocase=search_options.nocase,
            whole_word=search_options.whole_word,
            regex=search_options.regex,
            normal_search=search_options.normal_search,
            search_up=False,  # 强制向下搜索
            single_search=True,  # 强制单次搜索
        )

        # 调用核心find方法
        matches = self.find(pattern, search_options_copy)

        # 返回第一个匹配项（如果有）
        if matches:
            # 高亮当前匹配项
            self.text_widget.tag_add(
                self.highlight_tag_current, matches[0][0], matches[0][1]
            )
            # 设置当前匹配项
            self.current_match = matches[0]
            # 滚动到当前匹配项
            self.text_widget.see(matches[0][0])
            # 将光标位置移动到匹配项的结束位置，这样下次搜索会从这个位置开始
            self.text_widget.mark_set(tk.INSERT, matches[0][1])
            return matches[0]

        return None

    def replace(
        self, pattern: str, replacement: str, search_options: SearchOptions
    ) -> bool:
        """
        替换当前找到的匹配项，并高亮显示所有替换后的内容

        Args:
            pattern: 搜索模式
            replacement: 替换文本
            search_options: 搜索选项

        Returns:
            bool: 是否成功替换
        """
        # 优先使用已存在的当前匹配项
        if self.current_match:
            match = self.current_match
        else:
            # 如果没有当前匹配项，执行查找操作
            match = (
                self.find_next(pattern, search_options)
                if not search_options.search_up
                else self.find_previous(pattern, search_options)
            )

        if match:
            # 保存当前滚动位置
            scroll_pos = self.text_widget.yview()

            # 执行替换操作
            start_idx, end_idx = match
            self.text_widget.tag_remove(self.highlight_tag_current, start_idx, end_idx)
            self.text_widget.delete(start_idx, end_idx)
            self.text_widget.insert(start_idx, replacement)

            # 设置新的光标位置
            new_end_idx = self.text_widget.index(f"{start_idx}+{len(replacement)}c")
            self.text_widget.tag_add(self.highlight_tag_current, start_idx, new_end_idx)
            self.text_widget.mark_set(tk.INSERT, new_end_idx)

            # 恢复滚动位置
            self.text_widget.yview_moveto(scroll_pos[0])

            # 重新查找下一个匹配项
            if not search_options.search_up:
                self.find_next(pattern, search_options)
            else:
                self.find_previous(pattern, search_options)

            # 高亮显示所有替换后的内容
            self._highlight_replaced_content(replacement, search_options)

            return True

        return False

    def replace_all(
        self, pattern: str, replacement: str, search_options: SearchOptions
    ) -> int:
        """
        替换文档中所有匹配项，并高亮显示所有替换后的内容

        Args:
            pattern: 搜索模式
            replacement: 替换文本
            search_options: 搜索选项

        Returns:
            int: 成功替换的匹配项数量
        """
        # 保存当前光标位置
        current_pos = self.text_widget.index(tk.INSERT)

        # 创建搜索选项副本，强制向下搜索和搜索全部
        search_options_copy = SearchOptions(
            nocase=search_options.nocase,
            whole_word=search_options.whole_word,
            regex=search_options.regex,
            normal_search=search_options.normal_search,
            search_up=False,  # 替换全部时使用向下搜索
            single_search=False,  # 搜索全部
        )

        # 保存查找前的高亮状态
        was_highlighting = self.highlighting_enabled
        # 暂时禁用高亮以提高性能
        self.highlighting_enabled = False

        # 从头开始搜索
        self.text_widget.mark_set(tk.INSERT, "1.0")
        # 直接调用find_all方法获取所有匹配项
        matches = self.find(pattern, search_options_copy)

        # 恢复高亮状态
        self.highlighting_enabled = was_highlighting

        # 清除之前的高亮
        self.clear_highlights()

        # 执行替换操作 - 从后往前替换以避免索引变化问题
        replacements_count = 0
        # 反转匹配列表，从后往前替换
        for start_idx, end_idx in reversed(matches):
            try:
                # 替换文本
                self.text_widget.delete(start_idx, end_idx)
                self.text_widget.insert(start_idx, replacement)
                replacements_count += 1
            except tk.TclError:
                # 索引无效，跳过
                continue

        # 恢复光标位置
        self.text_widget.mark_set(tk.INSERT, current_pos)

        # 如果有替换成功的项，高亮显示所有替换后的内容
        if replacements_count > 0:
            self._highlight_replaced_content(replacement, search_options)

        return replacements_count

    def _highlight_replaced_content(
        self, replacement: str, search_options: SearchOptions
    ):
        """
        高亮显示所有替换后的内容

        Args:
            replacement: 替换文本
            search_options: 搜索选项
        """
        if not replacement or not self.highlighting_enabled:
            return

        # 创建搜索选项副本，用于查找替换后的内容
        # 注意：对于替换后的内容搜索，我们使用普通搜索模式，并保持不区分大小写等选项
        highlight_options = SearchOptions(
            nocase=search_options.nocase,
            whole_word=False,  # 替换后的内容不一定是完整单词
            regex=False,  # 替换后的内容使用普通搜索更合适
            normal_search=True,
            search_up=False,
            single_search=False,  # 搜索全部替换后的内容
        )

        # 清除之前的高亮，但保留逻辑上更合理的顺序
        # 首先清除当前匹配项高亮
        self.text_widget.tag_remove(self.highlight_tag_current, "1.0", tk.END)
        # 然后清除所有匹配项高亮
        self.text_widget.tag_remove(self.highlight_tag_all, "1.0", tk.END)

        # 查找所有替换后的内容
        self.text_widget.mark_set(tk.INSERT, "1.0")
        replaced_matches = self.find(replacement, highlight_options)

        # 高亮所有替换后的内容
        if replaced_matches:
            self._highlight_all_matches(replaced_matches)

            # 高亮第一个替换项作为当前匹配项
            self.text_widget.tag_add(
                self.highlight_tag_current,
                replaced_matches[0][0],
                replaced_matches[0][1],
            )
            self.current_match = replaced_matches[0]
            # 滚动到第一个替换项
            self.text_widget.see(replaced_matches[0][0])

    def find_all(
        self, pattern: str, search_options: SearchOptions
    ) -> List[Tuple[str, str]]:
        """
        查找文档中所有匹配项

        Args:
            pattern: 搜索模式
            search_options: 搜索选项（会覆盖single_search参数）

        Returns:
            List[Tuple[str, str]]: 所有匹配项的Tk索引元组列表[(开始索引, 结束索引)]
        """
        # 确保是搜索全部，并且总是从文档开头向下搜索
        search_options_copy = SearchOptions(
            nocase=search_options.nocase,
            whole_word=search_options.whole_word,
            regex=search_options.regex,
            normal_search=search_options.normal_search,
            search_up=False,  # 强制向下搜索，确保从文档开头开始
            single_search=False,  # 强制搜索全部
        )

        # 调用核心find方法
        matches = self.find(pattern, search_options_copy)

        # 高亮所有匹配项
        if matches:
            self._highlight_all_matches(matches)

            # 高亮第一个匹配项作为当前匹配项
            if matches:
                self.text_widget.tag_add(
                    self.highlight_tag_current, matches[0][0], matches[0][1]
                )
                self.current_match = matches[0]
                # 滚动到第一个匹配项
                self.text_widget.see(matches[0][0])
                # 移动光标到第一个匹配项
                self.text_widget.mark_set(tk.INSERT, matches[0][0])

        return matches

    def find_previous(
        self, pattern: str, search_options: SearchOptions
    ) -> Optional[Tuple[str, str]]:
        """
        查找上一个匹配项

        Args:
            pattern: 搜索模式
            search_options: 搜索选项（会覆盖search_up和single_search参数）

        Returns:
            Optional[Tuple[str, str]]: 匹配项的Tk索引元组(开始索引, 结束索引)，未找到返回None
        """
        # 确保是向上搜索且单次搜索
        search_options_copy = SearchOptions(
            nocase=search_options.nocase,
            whole_word=search_options.whole_word,
            regex=search_options.regex,
            normal_search=search_options.normal_search,
            search_up=True,  # 强制向上搜索
            single_search=True,  # 强制单次搜索
        )

        # 调用核心find方法
        matches = self.find(pattern, search_options_copy)

        # 返回第一个匹配项（如果有）
        if matches:
            # 高亮当前匹配项
            self.text_widget.tag_add(
                self.highlight_tag_current, matches[0][0], matches[0][1]
            )
            # 设置当前匹配项
            self.current_match = matches[0]
            # 滚动到当前匹配项
            self.text_widget.see(matches[0][0])
            # 将光标位置移动到匹配项的开始位置，这样下次搜索会从这个位置开始（向上搜索）
            self.text_widget.mark_set(tk.INSERT, matches[0][0])
            return matches[0]

        return None
