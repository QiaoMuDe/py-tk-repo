#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
书签功能模块
提供简单的书签添加、删除、导航和清除功能
"""

import tkinter as tk
from typing import List, Tuple, Optional
import random
from loguru import logger


class BookmarkManager:
    """书签管理器"""

    def __init__(self, editor):
        """
        初始化书签管理器

        Args:
            editor: 编辑器实例
        """
        self.editor = editor
        self.bookmarks: List[Tuple[int, int, int, int]] = (
            []
        )  # 存储书签的起始行号、起始列号、结束行号、结束列号
        self.bookmark_tags = []  # 存储书签的标签名

        # 定义书签背景色颜色集合
        self.bookmark_colors = [
            "#E6F3FF",  # 浅蓝色
            "#E6FFE6",  # 浅绿色
            "#F0E6FF",  # 浅紫色
            "#FFE6CC",  # 浅橙色
            "#F0F0F0",  # 浅灰色
            "#FFE6E6",  # 浅红色
            "#FFFFE6",  # 浅黄色
            "#E6FFFF",  # 浅青色
            "#FFE6F0",  # 浅粉色
            "#E6F7FF",  # 天蓝色
            "#F0FFE6",  # 淡绿色
            "#FFE6F7",  # 玫瑰色
            "#F7E6FF",  # 淡紫色
            "#E6FFF0",  # 薄荷绿
            "#FFF0E6",  # 淡桃色
            "#F0FFF0",  # 蜜瓜色
            "#FFF0F7",  # 淡粉红
            "#E6F0FF",  # 淡蓝紫
            "#F7FFE6",  # 淡黄绿
            "#FFE6F0",  # 淡珊瑚色
            "#E6FFFA",  # 淡青绿
            "#FAE6FF",  # 淡紫罗兰
            "#E6FAFF",  # 淡天蓝
            "#FFE6FA",  # 淡粉紫
            "#FAFFE6",  # 淡柠檬绿
            "#F5F5DC",  # 米色
            "#F0FFFF",  # 浅青色
            "#F5FFFA",  # 薄荷白
            "#FFF8DC",  # 米黄色
            "#F8F8FF",  # 幽灵白
            "#FFF5EE",  # 海贝壳色
            "#F0FFF8",  # 蜜瓜白
            "#FFF0F5",  # 薰衣草红
            "#F5F5FF",  # 淡紫白
            "#E6FFF5",  # 淡薄荷绿
            "#FFF5E6",  # 淡杏色
            "#E6E6FF",  # 淡紫蓝
            "#F0E6FF",  # 淡紫罗兰
            "#E6FFE0",  # 淡黄绿
            "#E0FFE6",  # 淡青绿
            "#FFE0E6",  # 淡粉红
            "#E6E0FF",  # 淡紫蓝
            "#E0E6FF",  # 淡蓝紫
            "#FFE0F0",  # 淡粉紫
            "#F0E0FF",  # 淡紫
            "#E0FFF0",  # 淡青绿
            "#F0FFE0",  # 淡黄绿
            "#E0F0FF",  # 淡天蓝
            "#FFE0E0",  # 淡红
            "#F0F0E0",  # 淡黄
            "#E0F0F0",  # 淡青
            "#F0E0F0",  # 淡粉
            "#E0E0F0",  # 淡紫
            "#F5F5DC",  # 米色
            "#FFE4C4",  # 鹿皮色
            "#FFE4B5",  # 莫卡辛色
            "#FFDEAD",  # 纳瓦霍白
            "#F5DEB3",  # 小麦色
            "#DEB887",  # 原木色
            "#D2B48C",  # 棕褐色
            "#BC8F8F",  # 玫瑰棕色
            "#F4A460",  # 沙棕色
            "#DAA520",  # 金菊色
            "#B8860B",  # 深金菊色
            "#CD853F",  # 秘鲁色
            "#D2691E",  # 巧克力色
            "#8B4513",  # 马鞍棕色
            "#A0522D",  # 赭色
            "#A52A2A",  # 棕色
            "#800000",  # 栗色
            "#808000",  # 橄榄色
            "#008000",  # 绿色
            "#008080",  # 青色
            "#000080",  # 海军蓝
            "#800080",  # 紫色
        ]

        # 随机选择一个背景色
        self.bookmark_bg_color = random.choice(self.bookmark_colors)

    def _parse_index(self, index_str: str) -> Tuple[int, int]:
        """
        解析文本索引字符串为行号和列号

        Args:
            index_str: 文本索引字符串，格式为 "行.列"

        Returns:
            Tuple[int, int]: (行号, 列号)

        Raises:
            ValueError: 当索引字符串格式不正确时
        """
        try:
            parts = index_str.split(".")
            if len(parts) != 2:
                raise ValueError(f"无效的索引格式: {index_str}")
            return int(parts[0]), int(parts[1])
        except (ValueError, AttributeError) as e:
            logger.error(f"解析索引字符串失败: {index_str}, 错误: {str(e)}")
            raise ValueError(f"解析索引字符串失败: {index_str}, 错误: {str(e)}")

    def _get_cursor_position(self) -> Tuple[int, int]:
        """
        获取当前光标位置

        Returns:
            Tuple[int, int]: (行号, 列号)

        Raises:
            ValueError: 当无法获取光标位置时
        """
        try:
            cursor_pos = self.editor.text_area.index(tk.INSERT)
            return self._parse_index(cursor_pos)
        except Exception as e:
            logger.error(f"获取光标位置失败: {str(e)}")
            raise ValueError(f"获取光标位置失败: {str(e)}")

    def _is_position_in_bookmark(
        self, line: int, col: int, bookmark: Tuple[int, int, int, int]
    ) -> bool:
        """
        检查指定位置是否在书签范围内

        Args:
            line: 行号
            col: 列号
            bookmark: 书签元组 (起始行, 起始列, 结束行, 结束列)

        Returns:
            bool: 如果位置在书签范围内返回True，否则返回False
        """
        start_line, start_col, end_line, end_col = bookmark
        if line < start_line or line > end_line:
            return False
        if line == start_line and col < start_col:
            return False
        if line == end_line and col > end_col:
            return False
        return True

    def _find_bookmark_at_position(self, line: int, col: int) -> Optional[int]:
        """
        查找指定位置的书签索引

        Args:
            line: 行号
            col: 列号

        Returns:
            Optional[int]: 如果找到书签返回索引，否则返回None
        """
        for i, bookmark in enumerate(self.bookmarks):
            if self._is_position_in_bookmark(line, col, bookmark):
                return i
        return None

    def toggle_bookmark(self):
        """
        切换书签状态（添加或删除）

        根据是否有选中的文本决定书签添加方式：
        - 如果有选中的文本，为选中的内容添加书签
        - 如果没有选中的文本，为当前行添加书签

        删除逻辑：
        - 如果有选中的文本，检查选中范围内是否有书签，有则删除
        - 如果没有选中的文本，检查当前光标位置是否有书签，有则删除

        Returns:
            bool: 添加书签返回True，删除书签返回False
        """
        # 检查是否有选中的文本
        try:
            selected_range = self.editor.text_area.tag_ranges(tk.SEL)
            if selected_range:
                # 有选中文本，为选中内容添加书签
                start_index = str(selected_range[0])
                end_index = str(selected_range[1])
                start_line, start_col = self._parse_index(start_index)
                end_line, end_col = self._parse_index(end_index)

                # 检查是否已存在该书签
                for i, bookmark in enumerate(self.bookmarks):
                    s_line, s_col, e_line, e_col = bookmark
                    if (
                        s_line == start_line
                        and s_col == start_col
                        and e_line == end_line
                        and e_col == end_col
                    ):
                        # 存在则删除
                        self._remove_bookmark_at_index(i)
                        return False

                # 检查选中范围内是否有其他书签
                for i, bookmark in enumerate(self.bookmarks):
                    s_line, s_col, e_line, e_col = bookmark
                    # 如果书签完全在选中范围内，删除它
                    if (
                        s_line >= start_line
                        and e_line <= end_line
                        and (s_line > start_line or s_col >= start_col)
                        and (e_line < end_line or e_col <= end_col)
                    ):
                        self._remove_bookmark_at_index(i)
                        return False

                # 不存在则添加
                self._add_bookmark_range(start_line, start_col, end_line, end_col)
                return True
            else:
                # 没有选中文本，为当前光标位置添加书签
                line_num, column_num = self._get_cursor_position()

                # 检查是否已存在该书签
                bookmark_index = self._find_bookmark_at_position(line_num, column_num)
                if bookmark_index is not None:
                    # 存在则删除
                    self._remove_bookmark_at_index(bookmark_index)
                    return False

                # 不存在则添加
                self._add_bookmark(line_num, column_num)
                return True
        except tk.TclError as e:
            # 处理Tkinter文本选择相关的错误
            logger.error(f"获取文本选择时出错: {str(e)}")
            # 没有选中文本，为当前光标位置添加书签
            try:
                line_num, column_num = self._get_cursor_position()

                # 检查是否已存在该书签
                bookmark_index = self._find_bookmark_at_position(line_num, column_num)
                if bookmark_index is not None:
                    # 存在则删除
                    self._remove_bookmark_at_index(bookmark_index)
                    return False

                # 不存在则添加
                self._add_bookmark(line_num, column_num)
                return True
            except Exception as inner_e:
                # 处理获取光标位置时的错误
                logger.error(f"书签操作失败: {str(inner_e)}")
                # self.editor.status_bar.show_notification(
                #     f"书签操作失败: {str(inner_e)}", 1000
                # )
                self.editor.nm.show_error(message=f"书签操作失败: {str(inner_e)}")
                return False

        except Exception as e:
            # 处理其他未预期的错误
            logger.error(f"书签操作失败: {str(e)}")
            # self.editor.status_bar.show_notification(f"书签操作失败: {str(e)}", 1000)
            self.editor.nm.show_error(message=f"书签操作失败: {str(e)}")
            return False

    def _generate_unique_tag_name(
        self, start_line: int, start_col: int, end_line: int = None, end_col: int = None
    ) -> str:
        """
        生成唯一的书签标签名

        Args:
            start_line: 起始行号
            start_col: 起始列号
            end_line: 结束行号（可选）
            end_col: 结束列号（可选）

        Returns:
            str: 唯一的标签名
        """
        if end_line is None:
            end_line = start_line
        if end_col is None:
            end_col = start_col

        # 使用UUID确保唯一性，同时包含位置信息便于调试
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        return f"bookmark_{unique_id}_{start_line}_{start_col}_{end_line}_{end_col}"

    def _add_bookmark(self, line_num: int, column_num: int):
        """
        添加书签并设置高亮

        Args:
            line_num: 行号
            column_num: 列号
        """
        # 添加到书签列表（使用范围格式，起始和结束位置相同）
        self.bookmarks.append((line_num, column_num, line_num, column_num))

        # 按行号排序
        self.bookmarks.sort(key=lambda x: x[0])

        # 创建唯一标签名并设置高亮背景
        tag_name = self._generate_unique_tag_name(line_num, column_num)
        self.bookmark_tags.append(tag_name)

        # 设置书签行的背景色
        self.editor.text_area.tag_add(tag_name, f"{line_num}.0", f"{line_num}.end")
        self.editor.text_area.tag_config(tag_name, background=self.bookmark_bg_color)

        # 显示提示信息
        self.editor.status_bar.show_notification(f"已添加书签: 行 {line_num}", 500)
        # self.editor.nm.show_info(message=f"已添加书签: 行 {line_num}")

    def _add_bookmark_range(
        self, start_line: int, start_col: int, end_line: int, end_col: int
    ):
        """
        添加范围书签并设置高亮

        Args:
            start_line: 起始行号
            start_col: 起始列号
            end_line: 结束行号
            end_col: 结束列号
        """
        # 添加到书签列表
        self.bookmarks.append((start_line, start_col, end_line, end_col))

        # 按行号排序
        self.bookmarks.sort(key=lambda x: x[0])

        # 创建唯一标签名并设置高亮背景
        tag_name = self._generate_unique_tag_name(
            start_line, start_col, end_line, end_col
        )
        self.bookmark_tags.append(tag_name)

        # 设置书签范围的背景色
        self.editor.text_area.tag_add(
            tag_name, f"{start_line}.{start_col}", f"{end_line}.{end_col}"
        )
        self.editor.text_area.tag_config(tag_name, background=self.bookmark_bg_color)

        # 显示提示信息
        if start_line == end_line:
            self.editor.status_bar.show_notification(
                f"已添加书签: 行 {start_line}", 500
            )
            # self.editor.nm.show_info(message=f"已添加书签: 行 {start_line}")

        else:
            self.editor.status_bar.show_notification(
                f"已添加书签: 行 {start_line}-{end_line}", 500
            )
            # self.editor.nm.show_info(message=f"已添加书签: 行 {start_line}-{end_line}")

    def _remove_bookmark_at_index(self, index: int):
        """
        根据索引删除书签

        Args:
            index: 书签在列表中的索引

        Returns:
            bool: 成功删除返回True，否则返回False
        """
        if not (0 <= index < len(self.bookmarks)):
            return False

        try:
            start_line, start_col, end_line, end_col = self.bookmarks[index]

            # 从列表中删除
            del self.bookmarks[index]

            # 删除对应的标签
            tag_name = (
                self.bookmark_tags[index] if index < len(self.bookmark_tags) else None
            )
            if tag_name:
                self.bookmark_tags.remove(tag_name)
                self.editor.text_area.tag_delete(tag_name)

            # 显示提示信息
            if start_line == end_line:
                self.editor.status_bar.show_notification(
                    f"已删除书签: 行 {start_line}", 500
                )
                # self.editor.nm.show_info(message=f"已删除书签: 行 {start_line}")
            else:
                self.editor.status_bar.show_notification(
                    f"已删除书签: 行 {start_line}-{end_line}", 500
                )
                # self.editor.nm.show_info(message=f"已删除书签: 行 {start_line}-{end_line}")

            return True
        except Exception as e:
            logger.error(f"删除书签失败: {str(e)}")
            # self.editor.status_bar.show_notification(f"删除书签失败: {str(e)}", 1000)
            self.editor.nm.show_error(message=f"删除书签失败: {str(e)}")
            return False

    def _find_bookmarks_on_line(self, line_num: int) -> List[Tuple[int, int, int, int]]:
        """
        查找指定行上的所有书签

        Args:
            line_num: 行号

        Returns:
            List[Tuple[int, int, int, int]]: 该行上的所有书签列表
        """
        return [
            bookmark
            for bookmark in self.bookmarks
            if bookmark[0] <= line_num <= bookmark[2]
        ]

    def _find_next_bookmark(
        self, current_line: int, current_col: int
    ) -> Optional[Tuple[int, int]]:
        """
        查找下一个书签

        Args:
            current_line: 当前行号
            current_col: 当前列号

        Returns:
            Optional[Tuple[int, int]]: 下一个书签的(行号, 列号)，如果没有找到返回None
        """
        # 首先检查当前行是否有在当前列之后的书签
        current_line_bookmarks = self._find_bookmarks_on_line(current_line)
        for start_line, start_col, _, _ in sorted(
            current_line_bookmarks, key=lambda x: x[1]
        ):
            if start_col > current_col:
                return (start_line, start_col)

        # 如果当前行没有，查找下一行的书签
        for start_line, start_col, _, _ in self.bookmarks:
            if start_line > current_line:
                return (start_line, start_col)

        # 如果没有找到，循环到第一个书签
        if self.bookmarks:
            start_line, start_col, _, _ = sorted(
                self.bookmarks, key=lambda x: (x[0], x[1])
            )[0]
            return (start_line, start_col)

        return None

    def _find_previous_bookmark(
        self, current_line: int, current_col: int
    ) -> Optional[Tuple[int, int]]:
        """
        查找上一个书签

        Args:
            current_line: 当前行号
            current_col: 当前列号

        Returns:
            Optional[Tuple[int, int]]: 上一个书签的(行号, 列号)，如果没有找到返回None
        """
        # 首先检查当前行是否有在当前列之前的书签
        current_line_bookmarks = self._find_bookmarks_on_line(current_line)
        for start_line, start_col, _, _ in sorted(
            current_line_bookmarks, key=lambda x: x[1], reverse=True
        ):
            if start_col < current_col:
                return (start_line, start_col)

        # 如果当前行没有，查找上一行的书签
        for start_line, start_col, _, _ in sorted(
            self.bookmarks, key=lambda x: (x[0], x[1]), reverse=True
        ):
            if start_line < current_line:
                return (start_line, start_col)

        # 如果没有找到，循环到最后一个书签
        if self.bookmarks:
            start_line, start_col, _, _ = sorted(
                self.bookmarks, key=lambda x: (x[0], x[1]), reverse=True
            )[0]
            return (start_line, start_col)

        return None

    def goto_next_bookmark(self):
        """
        跳转到下一个书签（循环查找）

        Returns:
            bool: 成功跳转返回True，否则返回False
        """
        if not self.bookmarks:
            self.editor.status_bar.show_notification("没有书签可跳转", 500)
            # self.editor.nm.show_info(message="没有书签可跳转")
            return False

        # 获取当前光标位置
        try:
            current_pos = self.editor.text_area.index(tk.INSERT)
            current_line, current_col = self._parse_index(current_pos)
        except Exception as e:
            logger.error(f"获取当前光标位置失败: {str(e)}")
            current_line, current_col = 1, 0

        # 查找下一个书签
        next_bookmark = self._find_next_bookmark(current_line, current_col)

        # 跳转到书签位置
        if next_bookmark:
            line, col = next_bookmark
            self._jump_to_position(line, col)
            return True

        return False

    def goto_previous_bookmark(self):
        """
        跳转到上一个书签（循环查找）

        Returns:
            bool: 成功跳转返回True，否则返回False
        """
        if not self.bookmarks:
            self.editor.status_bar.show_notification("没有书签可跳转", 500)
            # self.editor.nm.show_info(message="没有书签可跳转")
            return False

        # 获取当前光标位置
        try:
            current_pos = self.editor.text_area.index(tk.INSERT)
            current_line, current_col = self._parse_index(current_pos)
        except Exception as e:
            logger.error(f"获取当前光标位置失败: {str(e)}")
            current_line, current_col = 1, 0

        # 查找上一个书签
        prev_bookmark = self._find_previous_bookmark(current_line, current_col)

        # 跳转到书签位置
        if prev_bookmark:
            line, col = prev_bookmark
            self._jump_to_position(line, col)
            return True

        return False

    def clear_all_bookmarks(self):
        """清除所有书签"""
        if not self.bookmarks:
            self.editor.status_bar.show_notification("没有书签可清除", 500)
            # self.editor.nm.show_info(message="没有书签可清除")
            return

        # 清除所有标签
        for tag_name in self.bookmark_tags:
            self.editor.text_area.tag_delete(tag_name)

        # 清空列表
        self.bookmarks.clear()
        self.bookmark_tags.clear()

        # 重新随机选择一个背景色
        self.bookmark_bg_color = random.choice(self.bookmark_colors)

        # 显示提示信息
        self.editor.status_bar.show_notification("已清除所有书签", 500)
        # self.editor.nm.show_info(message="已清除所有书签")

    def _jump_to_position(self, line_num: int, column_num: int):
        """
        跳转到指定位置

        Args:
            line_num: 行号
            column_num: 列号
        """
        try:
            # 设置光标位置
            self.editor.text_area.mark_set(tk.INSERT, f"{line_num}.{column_num}")
            self.editor.text_area.see(tk.INSERT)
            self.editor.text_area.focus_set()

            # 显示提示信息
            self.editor.status_bar.show_notification(
                f"已跳转到书签: 行 {line_num}", 500
            )

        except Exception as e:
            logger.error(
                f"跳转到位置失败: 行 {line_num}, 列 {column_num}, 错误: {str(e)}"
            )
            # self.editor.status_bar.show_notification(f"跳转到书签失败: {str(e)}", 1000)
            self.editor.nm.show_error(message=f"跳转到书签失败: {str(e)}")

    def refresh_bookmarks(self):
        """刷新书签显示（在文件内容发生变化时调用）"""
        try:
            # 保存当前书签位置
            current_bookmarks = self.bookmarks.copy()

            # 清除所有标签
            for tag_name in self.bookmark_tags:
                self.editor.text_area.tag_delete(tag_name)
            self.bookmark_tags.clear()

            # 重新添加标签
            self.bookmarks = []
            for start_line, start_col, end_line, end_col in current_bookmarks:
                # 检查行号是否仍然有效（文件可能已被修改）
                last_line = int(self.editor.text_area.index("end-1c").split(".")[0])
                if start_line <= last_line:
                    # 如果是范围书签，检查结束行是否有效
                    if end_line > last_line:
                        # 调整结束行到文件末尾
                        end_line = last_line
                        end_col = len(
                            self.editor.text_area.get(
                                f"{end_line}.0", f"{end_line}.end"
                            )
                        )

                    # 重新添加书签
                    if start_line == end_line and start_col == end_col:
                        # 单点书签
                        self._add_bookmark(start_line, start_col)
                    else:
                        # 范围书签
                        self._add_bookmark_range(
                            start_line, start_col, end_line, end_col
                        )
        except Exception as e:
            logger.error(f"刷新书签失败: {str(e)}")
            # self.editor.status_bar.show_notification(f"刷新书签失败: {str(e)}", 1000)
            self.editor.nm.show_error(message=f"刷新书签失败: {str(e)}")
