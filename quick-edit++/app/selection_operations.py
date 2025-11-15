#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
选中文本操作类
该模块实现与选中文本相关的操作功能
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import base64
import json
import xml.dom.minidom as minidom
import black
from ruamel.yaml import YAML
import sqlparse


class SelectionOperations:
    """选中文本操作类, 提供与选中文本相关的功能"""

    def __init__(self):
        """初始化选中文本操作"""
        pass

    def has_selection(self):
        """
        检查是否有选中的文本

        Returns:
            bool: 如果有选中文本返回True, 否则返回False
        """
        try:
            selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            return bool(selected_text)
        except tk.TclError:
            return False

    def get_selected_text(self):
        """
        获取选中的文本

        Returns:
            str: 选中的文本, 如果没有选中文本返回空字符串
        """
        try:
            return self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            return ""

    def get_selection_range(self):
        """
        获取选中文本的范围

        Returns:
            tuple: (start_index, end_index) 选中文本的起始和结束位置
                  如果没有选中文本返回(None, None)
        """
        try:
            start_index = self.text_area.index(tk.SEL_FIRST)
            end_index = self.text_area.index(tk.SEL_LAST)
            return (start_index, end_index)
        except tk.TclError:
            return (None, None)

    def get_selection_length(self):
        """
        获取选中文本的长度

        Returns:
            int: 选中文本的字符数, 如果没有选中文本返回0
        """
        return len(self.get_selected_text())

    def _check_editable_selection(self, operation_name="操作"):
        """
        检查是否可以进行选中文本编辑操作

        Args:
            operation_name (str): 操作名称, 用于提示信息

        Returns:
            bool: 如果可以编辑返回True, 否则返回False
        """
        # 检查是否为只读模式
        if self.is_read_only:
            messagebox.showwarning("警告", "当前为只读模式, 无法修改内容")
            return False

        # 检查是否有选中文本
        if not self.has_selection():
            messagebox.showwarning("警告", f"请先选中要{operation_name}的文本")
            return False

        return True

    def add_hash_comment(self):
        """
        为选中的每行文本添加#号注释

        检查是否有选中文本和是否为只读模式, 然后为每行添加#号注释
        """
        # 检查是否可以进行编辑操作
        if not self._check_editable_selection("添加注释"):
            return

        try:
            # 获取选中文本和范围
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 将选中文本按行分割
            lines = selected_text.split("\n")

            # 为每行添加#号注释
            commented_lines = [f"# {line}" if line.strip() else line for line in lines]

            # 替换选中文本
            commented_text = "\n".join(commented_lines)
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, commented_text)

            # 重新选中修改后的文本
            line_count = len(commented_lines)
            end_line = int(start_index.split(".")[0]) + line_count - 1
            end_column = len(commented_lines[-1])
            new_end_index = f"{end_line}.{end_column}"
            self.text_area.tag_add(tk.SEL, start_index, new_end_index)

        except Exception as e:
            messagebox.showerror("错误", f"添加注释时出错: {str(e)}")

    def add_slash_comment(self):
        """
        为选中的每行文本添加//注释

        检查是否有选中文本和是否为只读模式, 然后为每行添加//注释
        """
        # 检查是否可以进行编辑操作
        if not self._check_editable_selection("添加注释"):
            return

        try:
            # 获取选中文本和范围
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 将选中文本按行分割
            lines = selected_text.split("\n")

            # 为每行添加//注释
            commented_lines = [f"// {line}" if line.strip() else line for line in lines]

            # 替换选中文本
            commented_text = "\n".join(commented_lines)
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, commented_text)

            # 重新选中修改后的文本
            line_count = len(commented_lines)
            end_line = int(start_index.split(".")[0]) + line_count - 1
            end_column = len(commented_lines[-1])
            new_end_index = f"{end_line}.{end_column}"
            self.text_area.tag_add(tk.SEL, start_index, new_end_index)

        except Exception as e:
            messagebox.showerror("错误", f"添加注释时出错: {str(e)}")

    def remove_line_comment(self):
        """
        移除选中每行文本的行首注释符号(#或//)

        检查是否有选中文本和是否为只读模式, 然后移除每行开头的#或//注释
        """
        # 检查是否可以进行编辑操作
        if not self._check_editable_selection("移除注释"):
            return

        try:
            # 获取选中文本和范围
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 将选中文本按行分割
            lines = selected_text.split("\n")

            # 移除每行的注释符号
            uncommented_lines = []
            for line in lines:
                stripped = line.lstrip()
                if stripped.startswith("# "):
                    # 移除# 号注释
                    uncommented_lines.append(line.replace("# ", "", 1))
                elif stripped.startswith("// "):
                    # 移除// 注释
                    uncommented_lines.append(line.replace("// ", "", 1))
                elif stripped.startswith("#"):
                    # 移除#号注释
                    uncommented_lines.append(line.replace("#", "", 1))
                elif stripped.startswith("//"):
                    # 移除//注释
                    uncommented_lines.append(line.replace("//", "", 1))
                else:
                    # 没有注释符号, 保持原样
                    uncommented_lines.append(line)

            # 替换选中文本
            uncommented_text = "\n".join(uncommented_lines)
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, uncommented_text)

            # 重新选中修改后的文本
            line_count = len(uncommented_lines)
            end_line = int(start_index.split(".")[0]) + line_count - 1
            end_column = len(uncommented_lines[-1])
            new_end_index = f"{end_line}.{end_column}"
            self.text_area.tag_add(tk.SEL, start_index, new_end_index)

        except Exception as e:
            messagebox.showerror("错误", f"移除注释时出错: {str(e)}")

    def base64_encode(self):
        """
        对选中文本进行Base64编码

        检查是否有选中文本和是否为只读模式, 然后对选中文本进行Base64编码
        """
        # 检查是否可以进行编辑操作
        if not self._check_editable_selection("Base64编码"):
            return

        try:
            # 获取选中文本和范围
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 对选中文本进行Base64编码
            encoded_text = base64.b64encode(selected_text.encode("utf-8")).decode(
                "utf-8"
            )

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, encoded_text)

            # 重新选中编码后的文本
            end_line = int(start_index.split(".")[0])
            end_column = len(encoded_text)
            new_end_index = f"{end_line}.{end_column}"
            self.text_area.tag_add(tk.SEL, start_index, new_end_index)

        except Exception as e:
            messagebox.showerror("错误", f"Base64编码时出错: {str(e)}")

    def base64_decode(self):
        """
        对选中文本进行Base64解码

        检查是否有选中文本和是否为只读模式, 然后对选中文本进行Base64解码
        """
        # 检查是否可以进行编辑操作
        if not self._check_editable_selection("Base64解码"):
            return

        try:
            # 获取选中文本和范围
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 对选中文本进行Base64解码
            try:
                decoded_text = base64.b64decode(selected_text.encode("utf-8")).decode(
                    "utf-8"
                )
            except Exception:
                # 如果解码失败, 尝试忽略无效字符
                decoded_text = base64.b64decode(
                    selected_text.encode("utf-8"), validate=False
                ).decode("utf-8")

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, decoded_text)

            # 重新选中解码后的文本
            end_line = int(start_index.split(".")[0])
            end_column = len(decoded_text)
            new_end_index = f"{end_line}.{end_column}"
            self.text_area.tag_add(tk.SEL, start_index, new_end_index)

        except Exception as e:
            messagebox.showerror(
                "错误",
                f"Base64解码时出错: {str(e)}\n请确保选中的文本是有效的Base64编码",
            )

    def to_upper_case(self):
        """
        将选中文本转换为大写

        检查是否有选中文本和是否为只读模式, 然后将选中文本转换为大写
        """
        # 检查是否可以进行编辑操作
        if not self._check_editable_selection("转为大写"):
            return

        try:
            # 获取选中文本和范围
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 将选中文本转换为大写
            upper_text = selected_text.upper()

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, upper_text)

            # 重新选中修改后的文本
            end_line = int(start_index.split(".")[0])
            end_column = len(upper_text)
            new_end_index = f"{end_line}.{end_column}"
            self.text_area.tag_add(tk.SEL, start_index, new_end_index)

        except Exception as e:
            messagebox.showerror("错误", f"转为大写时出错: {str(e)}")

    def to_lower_case(self):
        """
        将选中文本转换为小写

        检查是否有选中文本和是否为只读模式, 然后将选中文本转换为小写
        """
        # 检查是否可以进行编辑操作
        if not self._check_editable_selection("转为小写"):
            return

        try:
            # 获取选中文本和范围
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 将选中文本转换为小写
            lower_text = selected_text.lower()

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, lower_text)

            # 重新选中修改后的文本
            end_line = int(start_index.split(".")[0])
            end_column = len(lower_text)
            new_end_index = f"{end_line}.{end_column}"
            self.text_area.tag_add(tk.SEL, start_index, new_end_index)

        except Exception as e:
            messagebox.showerror("错误", f"转为小写时出错: {str(e)}")

    def to_title_case(self):
        """
        将选中文本转换为首字母大写

        检查是否有选中文本和是否为只读模式, 然后将选中文本转换为首字母大写
        """
        # 检查是否可以进行编辑操作
        if not self._check_editable_selection("首字母大写"):
            return

        try:
            # 获取选中文本和范围
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 将选中文本转换为首字母大写
            title_text = selected_text.title()

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, title_text)

            # 重新选中修改后的文本
            end_line = int(start_index.split(".")[0])
            end_column = len(title_text)
            new_end_index = f"{end_line}.{end_column}"
            self.text_area.tag_add(tk.SEL, start_index, new_end_index)

        except Exception as e:
            messagebox.showerror("错误", f"首字母大写时出错: {str(e)}")

    def trim_whitespace(self):
        """
        移除选中文本的首尾空白

        检查是否有选中文本和是否为只读模式, 然后移除选中文本的首尾空白
        """
        # 检查是否可以进行编辑操作
        if not self._check_editable_selection("移除首尾空白"):
            return

        try:
            # 获取选中文本和范围
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 移除选中文本的首尾空白
            trimmed_text = selected_text.strip()

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, trimmed_text)

            # 重新选中修改后的文本
            end_line = int(start_index.split(".")[0])
            end_column = len(trimmed_text)
            new_end_index = f"{end_line}.{end_column}"
            self.text_area.tag_add(tk.SEL, start_index, new_end_index)

        except Exception as e:
            messagebox.showerror("错误", f"移除首尾空白时出错: {str(e)}")

    def trim_left_whitespace(self):
        """
        移除选中文本的左侧空白

        检查是否有选中文本和是否为只读模式, 然后移除选中文本的左侧空白
        """
        # 检查是否可以进行编辑操作
        if not self._check_editable_selection("移除左侧空白"):
            return

        try:
            # 获取选中文本和范围
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 移除选中文本的左侧空白
            trimmed_text = selected_text.lstrip()

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, trimmed_text)

            # 重新选中修改后的文本
            end_line = int(start_index.split(".")[0])
            end_column = len(trimmed_text)
            new_end_index = f"{end_line}.{end_column}"
            self.text_area.tag_add(tk.SEL, start_index, new_end_index)

        except Exception as e:
            messagebox.showerror("错误", f"移除左侧空白时出错: {str(e)}")

    def trim_right_whitespace(self):
        """
        移除选中文本的右侧空白

        检查是否有选中文本和是否为只读模式, 然后移除选中文本的右侧空白
        """
        # 检查是否可以进行编辑操作
        if not self._check_editable_selection("移除右侧空白"):
            return

        try:
            # 获取选中文本和范围
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 移除选中文本的右侧空白
            trimmed_text = selected_text.rstrip()

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, trimmed_text)

            # 重新选中修改后的文本
            end_line = int(start_index.split(".")[0])
            end_column = len(trimmed_text)
            new_end_index = f"{end_line}.{end_column}"
            self.text_area.tag_add(tk.SEL, start_index, new_end_index)

        except Exception as e:
            messagebox.showerror("错误", f"移除右侧空白时出错: {str(e)}")

    def remove_extra_whitespace(self):
        """
        移除选中文本中的多余空白

        检查是否有选中文本和是否为只读模式, 然后移除选中文本中的多余空白
        """
        # 检查是否可以进行编辑操作
        if not self._check_editable_selection("移除多余空白"):
            return

        try:
            # 获取选中文本和范围
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 移除选中文本中的多余空白
            # 使用split()分割所有空白字符, 然后用单个空格连接
            cleaned_text = " ".join(selected_text.split())

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, cleaned_text)

            # 重新选中修改后的文本
            end_line = int(start_index.split(".")[0])
            end_column = len(cleaned_text)
            new_end_index = f"{end_line}.{end_column}"
            self.text_area.tag_add(tk.SEL, start_index, new_end_index)

        except Exception as e:
            messagebox.showerror("错误", f"移除多余空白时出错: {str(e)}")

    def remove_empty_lines(self):
        """
        移除选中文本中的空白行

        检查是否有选中文本和是否为只读模式, 然后移除选中文本中的空白行
        """
        # 检查是否可以进行编辑操作
        if not self._check_editable_selection("移除空白行"):
            return

        try:
            # 获取选中文本和范围
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 移除选中文本中的空白行
            # 分割为行, 过滤掉空行或只包含空白字符的行
            lines = selected_text.split("\n")
            non_empty_lines = [line for line in lines if line.strip() != ""]
            cleaned_text = "\n".join(non_empty_lines)

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, cleaned_text)

            # 重新选中修改后的文本
            end_line = int(start_index.split(".")[0])
            end_column = len(cleaned_text)
            new_end_index = f"{end_line}.{end_column}"
            self.text_area.tag_add(tk.SEL, start_index, new_end_index)

        except Exception as e:
            messagebox.showerror("错误", f"移除空白行时出错: {str(e)}")

    def merge_empty_lines(self):
        """
        合并选中文本中的连续空白行

        检查是否有选中文本和是否为只读模式, 然后合并选中文本中的连续空白行
        """
        # 检查是否可以进行编辑操作
        if not self._check_editable_selection("合并空白行"):
            return

        try:
            # 获取选中文本和范围
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 合并选中文本中的连续空白行
            # 分割为行, 处理连续的空白行
            lines = selected_text.split("\n")
            result_lines = []
            prev_empty = False

            for line in lines:
                current_empty = line.strip() == ""
                if current_empty and prev_empty:
                    # 跳过连续的空白行
                    continue
                result_lines.append(line)
                prev_empty = current_empty

            cleaned_text = "\n".join(result_lines)

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, cleaned_text)

            # 重新选中修改后的文本
            end_line = int(start_index.split(".")[0])
            end_column = len(cleaned_text)
            new_end_index = f"{end_line}.{end_column}"
            self.text_area.tag_add(tk.SEL, start_index, new_end_index)

        except Exception as e:
            messagebox.showerror("错误", f"合并空白行时出错: {str(e)}")

    def remove_duplicate_lines(self):
        """
        移除选中文本中的重复行

        检查是否有选中文本和是否为只读模式, 然后移除选中文本中的重复行
        """
        # 检查是否可以进行编辑操作
        if not self._check_editable_selection("移除重复行"):
            return

        try:
            # 获取选中文本和范围
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 移除选中文本中的重复行
            # 分割为行, 使用集合去重, 但保持原始顺序
            lines = selected_text.split("\n")
            seen_lines = set()
            unique_lines = []

            for line in lines:
                if line not in seen_lines:
                    seen_lines.add(line)
                    unique_lines.append(line)

            cleaned_text = "\n".join(unique_lines)

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, cleaned_text)

            # 重新选中修改后的文本
            end_line = int(start_index.split(".")[0])
            end_column = len(cleaned_text)
            new_end_index = f"{end_line}.{end_column}"
            self.text_area.tag_add(tk.SEL, start_index, new_end_index)

        except Exception as e:
            messagebox.showerror("错误", f"移除重复行时出错: {str(e)}")

    def merge_duplicate_lines(self):
        """
        合并选中文本中的重复行

        检查是否有选中文本和是否为只读模式, 然后合并选中文本中的重复行
        """
        # 检查是否可以进行编辑操作
        if not self._check_editable_selection("合并重复行"):
            return

        try:
            # 获取选中文本和范围
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 合并选中文本中的重复行
            # 分割为行, 统计每行出现的次数, 然后只保留一次
            lines = selected_text.split("\n")
            seen_lines = set()
            merged_lines = []

            for line in lines:
                if line not in seen_lines:
                    seen_lines.add(line)
                    merged_lines.append(line)

            cleaned_text = "\n".join(merged_lines)

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, cleaned_text)

            # 重新选中修改后的文本
            end_line = int(start_index.split(".")[0])
            end_column = len(cleaned_text)
            new_end_index = f"{end_line}.{end_column}"
            self.text_area.tag_add(tk.SEL, start_index, new_end_index)

        except Exception as e:
            messagebox.showerror("错误", f"合并重复行时出错: {str(e)}")

    def sort_lines_ascending(self):
        """
        对选中文本按升序排序

        检查是否有选中文本和是否为只读模式, 然后对选中文本按升序排序
        """
        # 检查是否可以进行编辑操作
        if not self._check_editable_selection("升序排序"):
            return

        try:
            # 获取选中文本和范围
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 分割为行并按升序排序
            lines = selected_text.split("\n")
            sorted_lines = sorted(lines)
            sorted_text = "\n".join(sorted_lines)

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, sorted_text)

            # 重新选中修改后的文本
            end_line = int(start_index.split(".")[0])
            end_column = len(sorted_text)
            new_end_index = f"{end_line}.{end_column}"
            self.text_area.tag_add(tk.SEL, start_index, new_end_index)

        except Exception as e:
            messagebox.showerror("错误", f"升序排序时出错: {str(e)}")

    def sort_lines_descending(self):
        """
        对选中文本按降序排序

        检查是否有选中文本和是否为只读模式, 然后对选中文本按降序排序
        """
        # 检查是否可以进行编辑操作
        if not self._check_editable_selection("降序排序"):
            return

        try:
            # 获取选中文本和范围
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 分割为行并按降序排序
            lines = selected_text.split("\n")
            sorted_lines = sorted(lines, reverse=True)
            sorted_text = "\n".join(sorted_lines)

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, sorted_text)

            # 重新选中修改后的文本
            end_line = int(start_index.split(".")[0])
            end_column = len(sorted_text)
            new_end_index = f"{end_line}.{end_column}"
            self.text_area.tag_add(tk.SEL, start_index, new_end_index)

        except Exception as e:
            messagebox.showerror("错误", f"降序排序时出错: {str(e)}")

    def reverse_characters(self):
        """
        反转选中文本中的字符顺序

        检查是否有选中文本和是否为只读模式, 然后反转选中文本中的字符顺序
        """
        # 检查是否可以进行编辑操作
        if not self._check_editable_selection("反转字符"):
            return

        try:
            # 获取选中文本和范围
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 反转字符顺序
            reversed_text = selected_text[::-1]

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, reversed_text)

            # 重新选中修改后的文本
            end_line = int(start_index.split(".")[0])
            end_column = len(reversed_text)
            new_end_index = f"{end_line}.{end_column}"
            self.text_area.tag_add(tk.SEL, start_index, new_end_index)

        except Exception as e:
            messagebox.showerror("错误", f"反转字符时出错: {str(e)}")

    def reverse_lines(self):
        """
        反转选中文本中的行顺序

        检查是否有选中文本和是否为只读模式, 然后反转选中文本中的行顺序
        """
        # 检查是否可以进行编辑操作
        if not self._check_editable_selection("反转行"):
            return

        try:
            # 获取选中文本和范围
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 按行分割文本
            lines = selected_text.split("\n")

            # 反转行顺序
            reversed_lines = lines[::-1]
            reversed_text = "\n".join(reversed_lines)

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, reversed_text)

            # 重新选中修改后的文本
            end_line = int(start_index.split(".")[0])
            end_column = len(reversed_text)
            new_end_index = f"{end_line}.{end_column}"
            self.text_area.tag_add(tk.SEL, start_index, new_end_index)

        except Exception as e:
            messagebox.showerror("错误", f"反转行时出错: {str(e)}")

    # 基本命名转换方法
    def snake_to_camel(self):
        """
        下划线转驼峰：snake_case → camelCase
        """
        if not self._check_editable_selection("下划线转驼峰"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 转换逻辑
            parts = selected_text.split("_")
            camel_case = parts[0].lower()
            for part in parts[1:]:
                if part:  # 忽略空部分
                    camel_case += part.capitalize()

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, camel_case)

            # 重新选中文本
            self._reselect_text(start_index, len(camel_case))

        except Exception as e:
            messagebox.showerror("错误", f"下划线转驼峰时出错: {str(e)}")

    def camel_to_snake(self):
        """
        驼峰转下划线：camelCase → snake_case
        """
        if not self._check_editable_selection("驼峰转下划线"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 转换逻辑
            import re

            snake_case = re.sub(r"(?<!^)(?=[A-Z])", "_", selected_text).lower()

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, snake_case)

            # 重新选中文本
            self._reselect_text(start_index, len(snake_case))

        except Exception as e:
            messagebox.showerror("错误", f"驼峰转下划线时出错: {str(e)}")

    # 扩展命名转换方法
    def snake_to_pascal(self):
        """
        下划线转帕斯卡：snake_case → PascalCase
        """
        if not self._check_editable_selection("下划线转帕斯卡"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 转换逻辑
            parts = selected_text.split("_")
            pascal_case = "".join(part.capitalize() for part in parts if part)

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, pascal_case)

            # 重新选中文本
            self._reselect_text(start_index, len(pascal_case))

        except Exception as e:
            messagebox.showerror("错误", f"下划线转帕斯卡时出错: {str(e)}")

    def pascal_to_snake(self):
        """
        帕斯卡转下划线：PascalCase → snake_case
        """
        if not self._check_editable_selection("帕斯卡转下划线"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 转换逻辑
            import re

            snake_case = re.sub(r"(?<!^)(?=[A-Z])", "_", selected_text).lower()

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, snake_case)

            # 重新选中文本
            self._reselect_text(start_index, len(snake_case))

        except Exception as e:
            messagebox.showerror("错误", f"帕斯卡转下划线时出错: {str(e)}")

    def camel_to_pascal(self):
        """
        驼峰转帕斯卡：camelCase → PascalCase
        """
        if not self._check_editable_selection("驼峰转帕斯卡"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 转换逻辑
            pascal_case = (
                selected_text[0].upper() + selected_text[1:] if selected_text else ""
            )

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, pascal_case)

            # 重新选中文本
            self._reselect_text(start_index, len(pascal_case))

        except Exception as e:
            messagebox.showerror("错误", f"驼峰转帕斯卡时出错: {str(e)}")

    def pascal_to_camel(self):
        """
        帕斯卡转驼峰：PascalCase → camelCase
        """
        if not self._check_editable_selection("帕斯卡转驼峰"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 转换逻辑
            camel_case = (
                selected_text[0].lower() + selected_text[1:] if selected_text else ""
            )

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, camel_case)

            # 重新选中文本
            self._reselect_text(start_index, len(camel_case))

        except Exception as e:
            messagebox.showerror("错误", f"帕斯卡转驼峰时出错: {str(e)}")

    def kebab_to_snake(self):
        """
        短横线转下划线：kebab-case → snake_case
        """
        if not self._check_editable_selection("短横线转下划线"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 转换逻辑
            snake_case = selected_text.replace("-", "_")

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, snake_case)

            # 重新选中文本
            self._reselect_text(start_index, len(snake_case))

        except Exception as e:
            messagebox.showerror("错误", f"短横线转下划线时出错: {str(e)}")

    def snake_to_kebab(self):
        """
        下划线转短横线：snake_case → kebab-case
        """
        if not self._check_editable_selection("下划线转短横线"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 转换逻辑
            kebab_case = selected_text.replace("_", "-")

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, kebab_case)

            # 重新选中文本
            self._reselect_text(start_index, len(kebab_case))

        except Exception as e:
            messagebox.showerror("错误", f"下划线转短横线时出错: {str(e)}")

    def kebab_to_camel(self):
        """
        短横线转驼峰：kebab-case → camelCase
        """
        if not self._check_editable_selection("短横线转驼峰"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 转换逻辑
            parts = selected_text.split("-")
            camel_case = parts[0].lower()
            for part in parts[1:]:
                if part:  # 忽略空部分
                    camel_case += part.capitalize()

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, camel_case)

            # 重新选中文本
            self._reselect_text(start_index, len(camel_case))

        except Exception as e:
            messagebox.showerror("错误", f"短横线转驼峰时出错: {str(e)}")

    def camel_to_kebab(self):
        """
        驼峰转短横线：camelCase → kebab-case
        """
        if not self._check_editable_selection("驼峰转短横线"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 转换逻辑
            import re

            kebab_case = re.sub(r"(?<!^)(?=[A-Z])", "-", selected_text).lower()

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, kebab_case)

            # 重新选中文本
            self._reselect_text(start_index, len(kebab_case))

        except Exception as e:
            messagebox.showerror("错误", f"驼峰转短横线时出错: {str(e)}")

    # 大小写转换方法
    def to_title_case(self):
        """
        每个单词首字母大写（标题格式）
        """
        if not self._check_editable_selection("标题格式"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 转换逻辑
            title_case = selected_text.title()

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, title_case)

            # 重新选中文本
            self._reselect_text(start_index, len(title_case))

        except Exception as e:
            messagebox.showerror("错误", f"标题格式转换时出错: {str(e)}")

    # 空格处理方法
    def space_to_snake(self):
        """
        空格转下划线：space separated → space_separated
        """
        if not self._check_editable_selection("空格转下划线"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 转换逻辑
            snake_case = selected_text.replace(" ", "_")

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, snake_case)

            # 重新选中文本
            self._reselect_text(start_index, len(snake_case))

        except Exception as e:
            messagebox.showerror("错误", f"空格转下划线时出错: {str(e)}")

    def space_to_kebab(self):
        """
        空格转短横线：space separated → space-separated
        """
        if not self._check_editable_selection("空格转短横线"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 转换逻辑
            kebab_case = selected_text.replace(" ", "-")

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, kebab_case)

            # 重新选中文本
            self._reselect_text(start_index, len(kebab_case))

        except Exception as e:
            messagebox.showerror("错误", f"空格转短横线时出错: {str(e)}")

    def space_to_camel(self):
        """
        空格转驼峰：space separated → spaceSeparated
        """
        if not self._check_editable_selection("空格转驼峰"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 转换逻辑
            parts = selected_text.split(" ")
            camel_case = parts[0].lower()
            for part in parts[1:]:
                if part:  # 忽略空部分
                    camel_case += part.capitalize()

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, camel_case)

            # 重新选中文本
            self._reselect_text(start_index, len(camel_case))

        except Exception as e:
            messagebox.showerror("错误", f"空格转驼峰时出错: {str(e)}")

    def snake_to_space(self):
        """
        下划线转空格：snake_case → snake case
        """
        if not self._check_editable_selection("下划线转空格"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 转换逻辑
            space_case = selected_text.replace("_", " ")

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, space_case)

            # 重新选中文本
            self._reselect_text(start_index, len(space_case))

        except Exception as e:
            messagebox.showerror("错误", f"下划线转空格时出错: {str(e)}")

    def kebab_to_space(self):
        """
        短横线转空格：kebab-case → kebab case
        """
        if not self._check_editable_selection("短横线转空格"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 转换逻辑
            space_case = selected_text.replace("-", " ")

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, space_case)

            # 重新选中文本
            self._reselect_text(start_index, len(space_case))

        except Exception as e:
            messagebox.showerror("错误", f"短横线转空格时出错: {str(e)}")

    def camel_to_space(self):
        """
        驼峰转空格：camelCase → camel case
        """
        if not self._check_editable_selection("驼峰转空格"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 转换逻辑
            import re

            space_case = re.sub(r"(?<!^)(?=[A-Z])", " ", selected_text)

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, space_case)

            # 重新选中文本
            self._reselect_text(start_index, len(space_case))

        except Exception as e:
            messagebox.showerror("错误", f"驼峰转空格时出错: {str(e)}")

    # 编程特定转换方法
    def to_constant_case(self):
        """
        常量命名：text → TEXT（全大写+下划线）
        """
        if not self._check_editable_selection("常量命名"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 转换逻辑
            import re

            # 先将驼峰转换为下划线, 然后转为大写
            constant_case = re.sub(r"(?<!^)(?=[A-Z])", "_", selected_text).upper()
            # 替换空格和短横线为下划线
            constant_case = constant_case.replace(" ", "_").replace("-", "_")

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, constant_case)

            # 重新选中文本
            self._reselect_text(start_index, len(constant_case))

        except Exception as e:
            messagebox.showerror("错误", f"常量命名转换时出错: {str(e)}")

    def to_private_variable(self):
        """
        私有变量命名：text → _text
        """
        if not self._check_editable_selection("私有变量命名"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 转换逻辑
            private_var = (
                "_" + selected_text
                if not selected_text.startswith("_")
                else selected_text
            )

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, private_var)

            # 重新选中文本
            self._reselect_text(start_index, len(private_var))

        except Exception as e:
            messagebox.showerror("错误", f"私有变量命名转换时出错: {str(e)}")

    def to_class_name(self):
        """
        类命名：text → TextClass（帕斯卡+Class后缀）
        """
        if not self._check_editable_selection("类命名"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 转换逻辑
            import re

            # 先将各种格式转换为帕斯卡
            pascal_case = (
                re.sub(r"(?<!^)(?=[A-Z])", "_", selected_text)
                .replace("_", " ")
                .replace("-", " ")
                .title()
                .replace(" ", "")
            )
            # 添加Class后缀
            class_name = pascal_case + "Class"

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, class_name)

            # 重新选中文本
            self._reselect_text(start_index, len(class_name))

        except Exception as e:
            messagebox.showerror("错误", f"类命名转换时出错: {str(e)}")

    def to_interface_name(self):
        """
        接口命名：text → IText（I前缀+帕斯卡）
        """
        if not self._check_editable_selection("接口命名"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 转换逻辑
            import re

            # 先将各种格式转换为帕斯卡
            pascal_case = (
                re.sub(r"(?<!^)(?=[A-Z])", "_", selected_text)
                .replace("_", " ")
                .replace("-", " ")
                .title()
                .replace(" ", "")
            )
            # 添加I前缀
            interface_name = "I" + pascal_case

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, interface_name)

            # 重新选中文本
            self._reselect_text(start_index, len(interface_name))

        except Exception as e:
            messagebox.showerror("错误", f"接口命名转换时出错: {str(e)}")

    def to_function_name(self):
        """
        函数命名：text → getText()（驼峰+括号）
        """
        if not self._check_editable_selection("函数命名"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 转换逻辑
            import re

            # 先将各种格式转换为驼峰
            snake_case = (
                re.sub(r"(?<!^)(?=[A-Z])", "_", selected_text).lower().replace("-", "_")
            )
            parts = snake_case.split("_")
            camel_case = parts[0].lower()
            for part in parts[1:]:
                if part:  # 忽略空部分
                    camel_case += part.capitalize()
            # 添加get前缀和括号
            function_name = "get" + camel_case[0].upper() + camel_case[1:] + "()"

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, function_name)

            # 重新选中文本
            self._reselect_text(start_index, len(function_name))

        except Exception as e:
            messagebox.showerror("错误", f"函数命名转换时出错: {str(e)}")

    # 数据库相关转换方法
    def to_table_name(self):
        """
        表名转换：text → texts（复数形式）
        """
        if not self._check_editable_selection("表名转换"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 转换逻辑
            # 简单的复数形式转换
            if selected_text.endswith("y"):
                table_name = selected_text[:-1] + "ies"
            elif selected_text.endswith(("s", "sh", "ch", "x", "z")):
                table_name = selected_text + "es"
            else:
                table_name = selected_text + "s"

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, table_name)

            # 重新选中文本
            self._reselect_text(start_index, len(table_name))

        except Exception as e:
            messagebox.showerror("错误", f"表名转换时出错: {str(e)}")

    def to_column_name(self):
        """
        列名转换：text → text_id（添加_id后缀）
        """
        if not self._check_editable_selection("列名转换"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 转换逻辑
            column_name = selected_text + "_id"

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, column_name)

            # 重新选中文本
            self._reselect_text(start_index, len(column_name))

        except Exception as e:
            messagebox.showerror("错误", f"列名转换时出错: {str(e)}")

    def to_foreign_key(self):
        """
        外键命名：text → text_id（添加_id后缀）
        """
        if not self._check_editable_selection("外键命名"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 转换逻辑
            foreign_key = selected_text + "_id"

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, foreign_key)

            # 重新选中文本
            self._reselect_text(start_index, len(foreign_key))

        except Exception as e:
            messagebox.showerror("错误", f"外键命名转换时出错: {str(e)}")

    def _reselect_text(self, start_index, text_length):
        """
        重新选中文本的辅助方法

        Args:
            start_index: 开始索引
            text_length: 文本长度
        """
        end_line = int(start_index.split(".")[0])
        new_end_index = f"{end_line}.{text_length}"
        self.text_area.tag_add(tk.SEL, start_index, new_end_index)

    # JSON处理方法
    def format_json(self):
        """
        格式化JSON字符串, 使其更易读
        """
        if not self._check_editable_selection("格式化JSON"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 尝试解析JSON
            try:
                json_data = json.loads(selected_text)
                # 格式化JSON, 缩进为2个空格
                formatted_json = json.dumps(json_data, indent=2, ensure_ascii=False)
            except json.JSONDecodeError as e:
                messagebox.showerror("JSON解析错误", f"无效的JSON格式: {str(e)}")
                return

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, formatted_json)

            # 重新选中文本
            # self._reselect_text(start_index, len(formatted_json))

        except Exception as e:
            messagebox.showerror("错误", f"格式化JSON时出错: {str(e)}")

    def compress_json(self):
        """
        压缩JSON字符串, 移除所有空白字符
        """
        if not self._check_editable_selection("压缩JSON"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 尝试解析JSON
            try:
                json_data = json.loads(selected_text)
                # 压缩JSON, 不添加任何缩进
                compressed_json = json.dumps(
                    json_data, separators=(",", ":"), ensure_ascii=False
                )
            except json.JSONDecodeError as e:
                messagebox.showerror("JSON解析错误", f"无效的JSON格式: {str(e)}")
                return

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, compressed_json)

            # 重新选中文本
            # self._reselect_text(start_index, len(compressed_json))

        except Exception as e:
            messagebox.showerror("错误", f"压缩JSON时出错: {str(e)}")

    def format_xml(self):
        """
        格式化XML字符串, 使其更易读
        """
        if not self._check_editable_selection("格式化XML"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 尝试解析XML
            try:
                # 解析XML
                dom = minidom.parseString(selected_text)

                # 格式化XML，使用缩进
                formatted_xml = dom.toprettyxml(indent="  ")

                # 去除空行
                formatted_xml = "\n".join(
                    [line for line in formatted_xml.split("\n") if line.strip()]
                )

            except Exception as e:
                messagebox.showerror("XML解析错误", f"无效的XML格式: {str(e)}")
                return

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, formatted_xml)

            # 重新选中文本
            # self._reselect_text(start_index, len(formatted_xml))

        except Exception as e:
            messagebox.showerror("错误", f"格式化XML时出错: {str(e)}")

    def format_csv(self, compress=False):
        """
        格式化CSV文本，支持压缩和展开两种模式

        Args:
            compress (bool): True为压缩格式化，False为展开格式化
        """
        if not self._check_editable_selection("格式化CSV"):
            return

        try:
            # 获取选中文本
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 使用自定义CSV格式化器
            try:
                formatted_csv = self._custom_csv_formatter(selected_text, compress)
            except Exception as e:
                messagebox.showerror("CSV解析错误", f"无效的CSV格式: {str(e)}")
                return

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, formatted_csv)

            # 重新选中文本
            # self._reselect_text(start_index, len(formatted_csv))

        except Exception as e:
            messagebox.showerror("错误", f"格式化CSV时出错: {str(e)}")

    def _custom_csv_formatter(self, csv_text, compress=False):
        """
        自定义CSV格式化器

        Args:
            csv_text (str): 要格式化的CSV文本
            compress (bool): True为压缩格式化，False为展开格式化

        Returns:
            str: 格式化后的CSV文本
        """
        if not csv_text:
            return csv_text

        # 分割行
        lines = csv_text.split("\n")
        formatted_lines = []

        for line in lines:
            # 跳过空行
            if not line.strip():
                formatted_lines.append("")
                continue

            # 解析行中的字段
            fields = self._parse_csv_line(line)

            # 格式化行
            if compress:
                # 压缩格式：移除所有不必要的空格
                formatted_line = ",".join(fields)
            else:
                # 展开格式：每个逗号后添加2个空格
                formatted_line = ",  ".join(fields)

            formatted_lines.append(formatted_line)

        return "\n".join(formatted_lines)

    def _parse_csv_line(self, line):
        """
        解析CSV行，正确处理引号和转义字符，并自动补全逗号

        Args:
            line (str): CSV行文本

        Returns:
            list: 解析后的字段列表
        """
        fields = []
        current_field = ""
        in_quotes = False
        i = 0
        line_length = len(line)

        while i < line_length:
            char = line[i]

            if char == '"':
                # 处理引号
                if in_quotes and i + 1 < line_length and line[i + 1] == '"':
                    # 转义的引号（两个连续引号）
                    current_field += '"'
                    i += 2
                    continue
                else:
                    # 开始或结束引号
                    in_quotes = not in_quotes
                    i += 1
                    continue
            elif char == "," and not in_quotes:
                # 字段分隔符
                fields.append(current_field)
                current_field = ""
                i += 1
                continue
            elif char == " " and not in_quotes:
                # 处理引号外的空格
                # 检查是否是字段间的空格（用于自动补逗号）
                if (
                    current_field
                    and i + 1 < line_length
                    and line[i + 1] != ","
                    and line[i + 1] != " "
                ):
                    # 可能是字段间的空格，先保留，稍后处理
                    current_field += char
                    i += 1
                    continue
                elif (
                    not current_field
                    and i + 1 < line_length
                    and line[i + 1] != ","
                    and line[i + 1] != " "
                ):
                    # 可能是字段间的空格，先保留，稍后处理
                    current_field += char
                    i += 1
                    continue
                else:
                    # 跳过其他空格
                    i += 1
                    continue
            else:
                # 普通字符
                current_field += char
                i += 1

        # 添加最后一个字段
        fields.append(current_field)

        # 处理可能由空格分隔的字段（自动补逗号）
        processed_fields = []
        for field in fields:
            if " " in field and not field.startswith('"') and not field.endswith('"'):
                # 检查是否是由空格分隔的多个字段
                sub_fields = field.split()
                if len(sub_fields) > 1:
                    # 如果是数字或简单文本，认为是多个字段
                    is_multiple_fields = True
                    for sub_field in sub_fields:
                        # 如果包含非字母数字字符，可能不是简单字段
                        if not sub_field.replace("_", "").replace("-", "").isalnum():
                            is_multiple_fields = False
                            break

                    if is_multiple_fields:
                        processed_fields.extend(sub_fields)
                    else:
                        processed_fields.append(field)
                else:
                    processed_fields.append(field)
            else:
                processed_fields.append(field)

        return processed_fields

    def format_ini(self):
        """格式化INI文本（对齐键值对），保留注释，确保节之间有空行分隔。
        支持等号(=)和冒号(:)作为键值对分隔符，支持分号(;)和井号(#)作为注释符号"""
        if not self._check_editable_selection("格式化INI"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 分割成行
            lines = selected_text.split("\n")

            # 分析并格式化INI文件，保留注释
            formatted_lines = []
            max_key_lengths = {}  # 每个section中key的最大长度
            current_section = None
            section_positions = []  # 记录每个section的位置

            # 第一遍扫描，找出每个section中key的最大长度
            for i, line in enumerate(lines):
                line = line.rstrip()  # 移除行尾空白
                stripped = line.lstrip()

                # 跳过空行和注释行（在计算长度时跳过）
                if not stripped or stripped.startswith(";") or stripped.startswith("#"):
                    continue

                # 检查是否为section行
                if stripped.startswith("[") and stripped.endswith("]"):
                    current_section = stripped[1:-1]
                    section_positions.append((i, current_section))
                    if current_section not in max_key_lengths:
                        max_key_lengths[current_section] = 0
                elif (
                    current_section
                    and ("=" in stripped or ":" in stripped)
                    and not (stripped.startswith(";") or stripped.startswith("#"))
                ):
                    # 这是一个键值对，支持等号和冒号
                    if "=" in stripped:
                        key = stripped.split("=", 1)[0].rstrip()
                    else:  # 使用冒号分隔
                        key = stripped.split(":", 1)[0].rstrip()

                    if len(key) > max_key_lengths[current_section]:
                        max_key_lengths[current_section] = len(key)

            # 第二遍扫描，格式化每一行
            current_section = None
            last_section_index = -1
            for i, line in enumerate(lines):
                line = line.rstrip()  # 移除行尾空白
                stripped = line.lstrip()
                leading_spaces = len(line) - len(stripped)

                # 保留空行和注释行
                if not stripped:
                    formatted_lines.append("")
                elif stripped.startswith(";") or stripped.startswith("#"):
                    # 保留注释行的原始格式
                    formatted_lines.append(line)
                elif stripped.startswith("[") and stripped.endswith("]"):
                    # Section行
                    current_section = stripped[1:-1]

                    # 检查是否需要添加空行分隔节
                    if last_section_index >= 0:
                        # 检查两个节之间是否已经有空行
                        has_empty_line = False
                        for j in range(last_section_index + 1, i):
                            if not lines[j].strip():
                                has_empty_line = True
                                break

                        # 如果没有空行，添加一个空行
                        if not has_empty_line and formatted_lines:
                            formatted_lines.append("")

                    last_section_index = i
                    formatted_lines.append(line)
                elif current_section and ("=" in stripped or ":" in stripped):
                    # 键值对格式化，支持等号和冒号
                    if stripped.startswith(";") or stripped.startswith("#"):
                        # 注释行保持原样
                        formatted_lines.append(line)
                    else:
                        # 确定分隔符类型
                        separator = " = " if "=" in stripped else " : "

                        # 分割键和值
                        if "=" in stripped:
                            parts = stripped.split("=", 1)
                        else:  # 使用冒号分隔
                            parts = stripped.split(":", 1)

                        if len(parts) == 2:
                            key = parts[0].rstrip()
                            value = parts[1].lstrip()
                            # 使用之前计算的最大key长度进行对齐
                            padding = max_key_lengths.get(current_section, len(key))
                            formatted_line = (
                                " " * leading_spaces
                                + key.ljust(padding)
                                + separator
                                + value
                            )
                            formatted_lines.append(formatted_line)
                        else:
                            # 不是标准键值对，保持原样
                            formatted_lines.append(line)
                else:
                    # 其他行保持原样
                    formatted_lines.append(line)

            # 重新组合文本
            formatted_ini = "\n".join(formatted_lines)

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, formatted_ini)

            # 重新选中文本
            # self._reselect_text(start_index, len(formatted_ini))

        except Exception as e:
            messagebox.showerror("错误", f"格式化INI时出错: {str(e)}")

    def format_python(self):
        """
        格式化Python代码
        """
        if not self._check_editable_selection("格式化Python"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 尝试使用black格式化
            try:
                # 创建模式对象，设置行长度
                mode = black.FileMode(line_length=88)

                # 使用black格式化代码
                formatted_code = black.format_str(selected_text, mode=mode)

            except ImportError:
                messagebox.showerror(
                    "Black库缺失", "未安装black库，无法格式化Python代码"
                )
                return
            except SyntaxError as e:
                messagebox.showerror("Python语法错误", f"无效的Python代码: {str(e)}")
                return
            except Exception as e:
                messagebox.showerror(
                    "Python格式化错误", f"格式化Python代码时出错: {str(e)}"
                )
                return

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, formatted_code)

            # 重新选中文本
            # self._reselect_text(start_index, len(formatted_code))

        except Exception as e:
            messagebox.showerror("错误", f"格式化Python代码时出错: {str(e)}")

    def format_yaml(self):
        """
        格式化YAML字符串, 使其更易读，保留注释
        """
        if not self._check_editable_selection("格式化YAML"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 尝试解析YAML
            try:
                # 创建YAML对象，设置保留注释
                yaml_obj = YAML()
                yaml_obj.indent(mapping=2, sequence=4, offset=2)
                yaml_obj.width = 4096  # 设置一个很大的值，避免自动换行

                # 解析YAML
                data = yaml_obj.load(selected_text)

                # 格式化YAML，保留注释
                from io import StringIO

                string_stream = StringIO()
                yaml_obj.dump(data, string_stream)
                formatted_yaml = string_stream.getvalue()

            except ImportError:
                messagebox.showerror(
                    "YAML库缺失", "未安装ruamel.yaml库，无法格式化YAML"
                )
                return
            except Exception as e:
                messagebox.showerror("YAML解析错误", f"无效的YAML格式: {str(e)}")
                return

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, formatted_yaml)

            # 重新选中文本
            # self._reselect_text(start_index, len(formatted_yaml))

        except Exception as e:
            messagebox.showerror("错误", f"格式化YAML时出错: {str(e)}")

    def format_sql_upper(self):
        """
        将SQL关键字转换为大写
        """
        if not self._check_editable_selection("SQL关键字大写"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 使用sqlparse解析SQL
            try:
                parsed = sqlparse.parse(selected_text)[0]
                # 将关键字转换为大写
                formatted_sql = sqlparse.format(
                    str(parsed), 
                    keyword_case='upper',
                    identifier_case=None,
                    strip_comments=False,
                    reindent=False,
                    indent_width=2
                )
            except Exception as e:
                messagebox.showerror("SQL解析错误", f"无效的SQL格式: {str(e)}")
                return

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, formatted_sql)

        except Exception as e:
            messagebox.showerror("错误", f"SQL关键字大写时出错: {str(e)}")

    def format_sql_lower(self):
        """
        将SQL关键字转换为小写
        """
        if not self._check_editable_selection("SQL关键字小写"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 使用sqlparse解析SQL
            try:
                parsed = sqlparse.parse(selected_text)[0]
                # 将关键字转换为小写
                formatted_sql = sqlparse.format(
                    str(parsed), 
                    keyword_case='lower',
                    identifier_case=None,
                    strip_comments=False,
                    reindent=False,
                    indent_width=2
                )
            except Exception as e:
                messagebox.showerror("SQL解析错误", f"无效的SQL格式: {str(e)}")
                return

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, formatted_sql)

        except Exception as e:
            messagebox.showerror("错误", f"SQL关键字小写时出错: {str(e)}")

    def format_sql(self):
        """
        格式化SQL语句，使其更易读
        """
        if not self._check_editable_selection("格式化SQL"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 使用sqlparse解析SQL
            try:
                parsed = sqlparse.parse(selected_text)[0]
                # 格式化SQL，关键字大写，添加缩进
                formatted_sql = sqlparse.format(
                    str(parsed), 
                    keyword_case='upper',
                    identifier_case=None,
                    strip_comments=False,
                    reindent=True,
                    indent_width=2
                )
            except Exception as e:
                messagebox.showerror("SQL解析错误", f"无效的SQL格式: {str(e)}")
                return

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, formatted_sql)

        except Exception as e:
            messagebox.showerror("错误", f"格式化SQL时出错: {str(e)}")

    def compress_sql(self):
        """
        压缩SQL语句，移除不必要的空白字符
        """
        if not self._check_editable_selection("压缩SQL"):
            return

        try:
            selected_text = self.get_selected_text()
            start_index, end_index = self.get_selection_range()

            # 使用sqlparse解析SQL
            try:
                parsed = sqlparse.parse(selected_text)[0]
                # 压缩SQL，移除多余空格和换行
                formatted_sql = sqlparse.format(
                    str(parsed), 
                    keyword_case=None,
                    identifier_case=None,
                    strip_comments=True,
                    reindent=False,
                    strip_whitespace=True
                )
            except Exception as e:
                messagebox.showerror("SQL解析错误", f"无效的SQL格式: {str(e)}")
                return

            # 替换选中文本
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, formatted_sql)

        except Exception as e:
            messagebox.showerror("错误", f"压缩SQL时出错: {str(e)}")
