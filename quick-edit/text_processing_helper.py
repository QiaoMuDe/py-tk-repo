import tkinter as tk
import tkinter.messagebox as messagebox
import json
import csv
import io
import xml.etree.ElementTree as ET
from xml.dom import minidom
import black
import autopep8
from ruamel.yaml import YAML
from io import StringIO
import yaml
import re
import base64


class TextProcessingHelper:
    """文本处理助手类，提供选中文本的各种处理功能"""

    def __init__(self, text_area):
        """初始化文本处理助手

        Args:
            text_area: 文本编辑区域组件
        """
        self.text_area = text_area
        self.menu_font = ("Microsoft YaHei UI", 9)

    def _is_readonly(self):
        """检查文本区域是否处于只读模式

        Returns:
            bool: 如果文本区域处于禁用状态（只读模式）则返回True，否则返回False
        """
        return self.text_area.cget("state") == tk.DISABLED

    def _show_readonly_message(self):
        """显示只读模式下无法编辑的提示信息"""
        messagebox.showinfo("提示", "当前处于只读模式，无法进行选中文本操作。")

    def convert_to_uppercase(self):
        """将选中的文本转换为大写"""
        # 检查是否处于只读模式
        if self._is_readonly():
            self._show_readonly_message()
            return

        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                # 保存插入位置
                insert_pos = self.text_area.index("sel.first")
                # 转换为大写
                upper_text = selected_text.upper()
                # 替换选中的文本
                self.text_area.delete("sel.first", "sel.last")
                self.text_area.insert(insert_pos, upper_text)
        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass

    def convert_to_lowercase(self):
        """将选中的文本转换为小写"""
        # 检查是否处于只读模式
        if self._is_readonly():
            self._show_readonly_message()
            return

        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                # 保存插入位置
                insert_pos = self.text_area.index("sel.first")
                # 转换为小写
                lower_text = selected_text.lower()
                # 替换选中的文本
                self.text_area.delete("sel.first", "sel.last")
                self.text_area.insert(insert_pos, lower_text)
        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass

    def convert_to_title_case(self):
        """将选中的文本转换为首字母大写"""
        # 检查是否处于只读模式
        if self._is_readonly():
            self._show_readonly_message()
            return

        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                # 保存插入位置
                insert_pos = self.text_area.index("sel.first")
                # 转换为首字母大写
                title_text = selected_text.title()
                # 替换选中的文本
                self.text_area.delete("sel.first", "sel.last")
                self.text_area.insert(insert_pos, title_text)
        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass

    def trim_selection(self):
        """移除选中文本的首尾空白"""
        # 检查是否处于只读模式
        if self._is_readonly():
            self._show_readonly_message()
            return

        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                # 保存插入位置
                insert_pos = self.text_area.index("sel.first")
                # 移除首尾空白
                trimmed_text = selected_text.strip()
                # 替换选中的文本
                self.text_area.delete("sel.first", "sel.last")
                self.text_area.insert(insert_pos, trimmed_text)
        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass

    def remove_left_whitespace(self):
        """移除选中文本每行的左侧空白"""
        # 检查是否处于只读模式
        if self._is_readonly():
            self._show_readonly_message()
            return

        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                # 保存插入位置
                insert_pos = self.text_area.index("sel.first")
                # 分割成行
                lines = selected_text.split("\n")
                # 移除每行左侧空白
                processed_lines = [line.lstrip() for line in lines]
                # 重新组合文本
                result_text = "\n".join(processed_lines)
                # 替换选中的文本
                self.text_area.delete("sel.first", "sel.last")
                self.text_area.insert(insert_pos, result_text)
        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass

    def create_selected_text_menu(self, parent_menu):
        """创建选中文本操作子菜单

        Args:
            parent_menu: 父菜单对象

        Returns:
            tk.Menu: 选中文本操作子菜单
        """
        # 创建主菜单
        selected_text_menu = tk.Menu(parent_menu, tearoff=0, font=self.menu_font)

        # 添加文本转换功能子菜单
        text_conversion_menu = tk.Menu(
            selected_text_menu, tearoff=0, font=self.menu_font
        )
        text_conversion_menu.add_command(
            label="转换为大写", command=self.convert_to_uppercase
        )
        text_conversion_menu.add_command(
            label="转换为小写", command=self.convert_to_lowercase
        )
        text_conversion_menu.add_command(
            label="首字母大写", command=self.convert_to_title_case
        )
        selected_text_menu.add_cascade(label="文本转换", menu=text_conversion_menu)

        # 添加文本处理功能子菜单
        text_processing_menu = tk.Menu(
            selected_text_menu, tearoff=0, font=self.menu_font
        )
        text_processing_menu.add_command(
            label="移除首尾空白", command=self.trim_selection
        )
        text_processing_menu.add_command(
            label="移除左侧空白", command=self.remove_left_whitespace
        )
        text_processing_menu.add_command(
            label="移除右侧空白", command=self.remove_right_whitespace
        )
        text_processing_menu.add_command(
            label="移除多余空白", command=self.remove_extra_whitespace
        )
        selected_text_menu.add_cascade(label="文本处理", menu=text_processing_menu)

        # 添加行处理功能子菜单
        line_processing_menu = tk.Menu(
            selected_text_menu, tearoff=0, font=self.menu_font
        )
        line_processing_menu.add_command(
            label="移除空白行", command=self.remove_blank_lines
        )
        line_processing_menu.add_command(
            label="合并空白行", command=self.merge_blank_lines
        )
        line_processing_menu.add_command(
            label="移除重复空行", command=self.remove_duplicate_blank_lines
        )
        line_processing_menu.add_command(
            label="合并重复行", command=self.merge_duplicate_lines
        )

        # 添加排序子菜单
        sort_menu = tk.Menu(line_processing_menu, tearoff=0, font=self.menu_font)
        sort_menu.add_command(label="升序排序", command=self.sort_lines_asc)
        sort_menu.add_command(label="降序排序", command=self.sort_lines_desc)
        line_processing_menu.add_cascade(label="排序", menu=sort_menu)

        # 添加反转子菜单
        reverse_menu = tk.Menu(line_processing_menu, tearoff=0, font=self.menu_font)
        reverse_menu.add_command(label="字符反转", command=self.reverse_text)
        reverse_menu.add_command(label="行反转", command=self.reverse_lines)
        line_processing_menu.add_cascade(label="反转", menu=reverse_menu)

        # 添加命名转换子菜单
        naming_menu = tk.Menu(line_processing_menu, tearoff=0, font=self.menu_font)
        naming_menu.add_command(label="下划线转驼峰", command=self.to_camel_case)
        naming_menu.add_command(label="驼峰转下划线", command=self.to_snake_case)
        line_processing_menu.add_cascade(label="命名转换", menu=naming_menu)

        selected_text_menu.add_cascade(label="行处理", menu=line_processing_menu)

        # 添加格式化功能子菜单
        formatting_menu = tk.Menu(selected_text_menu, tearoff=0, font=self.menu_font)

        # JSON处理
        json_menu = tk.Menu(formatting_menu, tearoff=0, font=self.menu_font)
        json_menu.add_command(label="格式化JSON", command=self.format_json)
        json_menu.add_command(label="压缩JSON", command=self.compress_json)
        formatting_menu.add_cascade(label="JSON", menu=json_menu)

        # 其他格式处理
        formatting_menu.add_command(label="格式化XML", command=self.format_xml)
        formatting_menu.add_command(label="格式化CSV", command=self.format_csv)
        formatting_menu.add_command(label="格式化INI", command=self.format_ini)
        formatting_menu.add_command(label="格式化Python", command=self.format_python)
        formatting_menu.add_command(label="格式化YAML", command=self.format_yaml)

        selected_text_menu.add_cascade(label="格式化", menu=formatting_menu)

        # 添加注释相关功能子菜单
        comment_menu = tk.Menu(selected_text_menu, tearoff=0, font=self.menu_font)
        comment_menu.add_command(
            label="添加 # 注释", command=self.comment_selection_hash
        )
        comment_menu.add_command(
            label="添加 // 注释", command=self.comment_selection_slash
        )
        comment_menu.add_command(label="移除行注释", command=self.uncomment_selection)
        selected_text_menu.add_cascade(label="注释处理", menu=comment_menu)

        # 添加编码解码功能子菜单
        encoding_menu = tk.Menu(selected_text_menu, tearoff=0, font=self.menu_font)
        encoding_menu.add_command(label="Base64编码", command=self.encode_base64)
        encoding_menu.add_command(label="Base64解码", command=self.decode_base64)
        selected_text_menu.add_cascade(label="编码解码", menu=encoding_menu)

        return selected_text_menu

    def remove_right_whitespace(self):
        """移除选中文本每行的右侧空白"""
        # 检查是否处于只读模式
        if self._is_readonly():
            self._show_readonly_message()
            return

        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                # 保存插入位置
                insert_pos = self.text_area.index("sel.first")
                # 分割成行
                lines = selected_text.split("\n")
                # 移除每行右侧空白
                processed_lines = [line.rstrip() for line in lines]
                # 重新组合文本
                result_text = "\n".join(processed_lines)
                # 替换选中的文本
                self.text_area.delete("sel.first", "sel.last")
                self.text_area.insert(insert_pos, result_text)
        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass

    def remove_blank_lines(self):
        """移除选中文本中的所有空白行"""
        # 检查是否处于只读模式
        if self._is_readonly():
            self._show_readonly_message()
            return

        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                # 保存插入位置
                insert_pos = self.text_area.index("sel.first")
                # 分割成行
                lines = selected_text.split("\n")
                # 移除空白行
                processed_lines = [line for line in lines if line.strip()]
                # 重新组合文本
                result_text = "\n".join(processed_lines)
                # 替换选中的文本
                self.text_area.delete("sel.first", "sel.last")
                self.text_area.insert(insert_pos, result_text)
        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass

    def merge_blank_lines(self):
        """合并连续的空白行为单个空白行"""
        # 检查是否处于只读模式
        if self._is_readonly():
            self._show_readonly_message()
            return

        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                # 保存插入位置
                insert_pos = self.text_area.index("sel.first")
                # 分割成行
                lines = selected_text.split("\n")
                processed_lines = []
                last_was_blank = False

                for line in lines:
                    is_blank = not line.strip()
                    # 如果当前行是空白行且上一行不是空白行，则添加一个空白行
                    if is_blank:
                        if not last_was_blank:
                            processed_lines.append("")
                        last_was_blank = True
                    else:
                        processed_lines.append(line)
                        last_was_blank = False

                # 重新组合文本
                result_text = "\n".join(processed_lines)
                # 替换选中的文本
                self.text_area.delete("sel.first", "sel.last")
                self.text_area.insert(insert_pos, result_text)
        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass

    def merge_duplicate_lines(self):
        """合并重复的行（保留第一次出现的行）"""
        # 检查是否处于只读模式
        if self._is_readonly():
            self._show_readonly_message()
            return

        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                # 保存插入位置
                insert_pos = self.text_area.index("sel.first")
                # 分割成行
                lines = selected_text.split("\n")
                processed_lines = []
                seen_lines = set()

                for line in lines:
                    # 对于非空行，检查是否重复
                    if not line.strip():
                        processed_lines.append(line)
                    else:
                        if line not in seen_lines:
                            seen_lines.add(line)
                            processed_lines.append(line)

                # 重新组合文本
                result_text = "\n".join(processed_lines)
                # 替换选中的文本
                self.text_area.delete("sel.first", "sel.last")
                self.text_area.insert(insert_pos, result_text)
        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass

    def remove_duplicate_blank_lines(self):
        # 检查是否处于只读模式
        if self._is_readonly():
            self._show_readonly_message()
            return

        """移除重复的空行"""
        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                # 保存插入位置
                insert_pos = self.text_area.index("sel.first")
                # 分割成行
                lines = selected_text.split("\n")
                processed_lines = []
                last_was_blank = False

                for line in lines:
                    is_blank = not line.strip()
                    # 如果是空白行且上一行不是空白行，则添加
                    if is_blank:
                        if not last_was_blank:
                            processed_lines.append("")
                            last_was_blank = True
                    else:
                        processed_lines.append(line)
                        last_was_blank = False

                # 重新组合文本
                result_text = "\n".join(processed_lines)
                # 替换选中的文本
                self.text_area.delete("sel.first", "sel.last")
                self.text_area.insert(insert_pos, result_text)
        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass

    def format_json(self):
        """格式化JSON文本（美化）"""
        # 检查是否处于只读模式
        if self._is_readonly():
            self._show_readonly_message()
            return

        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                try:
                    # 保存插入位置
                    insert_pos = self.text_area.index("sel.first")
                    # 解析JSON
                    json_obj = json.loads(selected_text)
                    # 格式化输出（美化）
                    formatted_json = json.dumps(json_obj, ensure_ascii=False, indent=2)
                    # 替换选中的文本
                    self.text_area.delete("sel.first", "sel.last")
                    self.text_area.insert(insert_pos, formatted_json)
                except json.JSONDecodeError:
                    # 显示错误消息
                    messagebox.showerror(
                        "错误",
                        "无法解析JSON文本。请确保选择的文本是有效的JSON格式。",
                    )
        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass

    def compress_json(self):
        """压缩JSON文本（移除所有空白字符）"""
        # 检查是否处于只读模式
        if self._is_readonly():
            self._show_readonly_message()
            return

        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                try:
                    # 保存插入位置
                    insert_pos = self.text_area.index("sel.first")
                    # 解析JSON
                    json_obj = json.loads(selected_text)
                    # 压缩输出
                    compressed_json = json.dumps(
                        json_obj, ensure_ascii=False, separators=(",", ":")
                    )
                    # 替换选中的文本
                    self.text_area.delete("sel.first", "sel.last")
                    self.text_area.insert(insert_pos, compressed_json)
                except json.JSONDecodeError:
                    # 显示错误消息
                    messagebox.showerror(
                        "错误",
                        "无法解析JSON文本。请确保选择的文本是有效的JSON格式。",
                    )

        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass

    def remove_extra_whitespace(self):
        """移除选中文本中的多余空白字符（连续空格替换为单个空格）"""
        # 检查是否处于只读模式
        if self._is_readonly():
            self._show_readonly_message()
            return

        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                # 保存插入位置
                insert_pos = self.text_area.index("sel.first")
                # 移除多余空白
                # 保留换行符，只处理行内空格
                lines = selected_text.split("\n")
                processed_lines = []
                for line in lines:
                    # 替换连续空格为单个空格
                    processed_line = " ".join(line.split())
                    processed_lines.append(processed_line)
                # 重新组合文本
                result_text = "\n".join(processed_lines)
                # 替换选中的文本
                self.text_area.delete("sel.first", "sel.last")
                self.text_area.insert(insert_pos, result_text)
        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass

    def comment_selection_hash(self):
        """为选中的文本添加行注释（在每行开头添加 # ）"""
        # 检查是否处于只读模式
        if self._is_readonly():
            self._show_readonly_message()
            return

        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                # 保存插入位置
                insert_pos = self.text_area.index("sel.first")
                # 分割成行
                lines = selected_text.split("\n")
                # 为每行添加注释
                commented_lines = ["# " + line for line in lines]
                # 重新组合文本
                commented_text = "\n".join(commented_lines)
                # 替换选中的文本
                self.text_area.delete("sel.first", "sel.last")
                self.text_area.insert(insert_pos, commented_text)
        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass

    def comment_selection_slash(self):
        """为选中的文本添加行注释（在每行开头添加 // ）"""
        # 检查是否处于只读模式
        if self._is_readonly():
            self._show_readonly_message()
            return

        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                # 保存插入位置
                insert_pos = self.text_area.index("sel.first")
                # 分割成行
                lines = selected_text.split("\n")
                # 为每行添加注释
                commented_lines = ["// " + line for line in lines]
                # 重新组合文本
                commented_text = "\n".join(commented_lines)
                # 替换选中的文本
                self.text_area.delete("sel.first", "sel.last")
                self.text_area.insert(insert_pos, commented_text)
        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass

    def format_ini(self):
        """格式化INI文本（对齐键值对），保留注释"""
        # 检查是否处于只读模式
        if self._is_readonly():
            self._show_readonly_message()
            return

        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                try:
                    # 保存插入位置
                    insert_pos = self.text_area.index("sel.first")
                    # 分割成行
                    lines = selected_text.split("\n")

                    # 分析并格式化INI文件，保留注释
                    formatted_lines = []
                    max_key_lengths = {}  # 每个section中key的最大长度
                    current_section = None

                    # 第一遍扫描，找出每个section中key的最大长度
                    for line in lines:
                        line = line.rstrip()  # 移除行尾空白
                        stripped = line.lstrip()

                        # 跳过空行和注释行（在计算长度时跳过）
                        if (
                            not stripped
                            or stripped.startswith(";")
                            or stripped.startswith("#")
                        ):
                            continue

                        # 检查是否为section行
                        if stripped.startswith("[") and stripped.endswith("]"):
                            current_section = stripped[1:-1]
                            if current_section not in max_key_lengths:
                                max_key_lengths[current_section] = 0
                        elif (
                            current_section
                            and "=" in stripped
                            and not (
                                stripped.startswith(";") or stripped.startswith("#")
                            )
                        ):
                            # 这是一个键值对
                            key = stripped.split("=", 1)[0].rstrip()
                            if len(key) > max_key_lengths[current_section]:
                                max_key_lengths[current_section] = len(key)

                    # 第二遍扫描，格式化每一行
                    current_section = None
                    for line in lines:
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
                            # Section行居中或保持原格式
                            current_section = stripped[1:-1]
                            formatted_lines.append(line)
                        elif current_section and "=" in stripped:
                            # 键值对格式化
                            if stripped.startswith(";") or stripped.startswith("#"):
                                # 注释行保持原样
                                formatted_lines.append(line)
                            else:
                                # 分割键和值
                                parts = stripped.split("=", 1)
                                if len(parts) == 2:
                                    key = parts[0].rstrip()
                                    value = parts[1].lstrip()
                                    # 使用之前计算的最大key长度进行对齐
                                    padding = max_key_lengths.get(
                                        current_section, len(key)
                                    )
                                    formatted_line = (
                                        " " * leading_spaces
                                        + key.ljust(padding)
                                        + " = "
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

                    # 替换选中的文本
                    self.text_area.delete("sel.first", "sel.last")
                    self.text_area.insert(insert_pos, formatted_ini)
                except Exception as e:
                    # 显示错误消息
                    messagebox.showerror("错误", f"无法格式化INI文本: {str(e)}")

        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass

    def format_csv(self):
        """格式化CSV文本（对齐列），保持CSV格式"""
        # 检查是否处于只读模式
        if self._is_readonly():
            self._show_readonly_message()
            return

        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                try:
                    # 保存插入位置
                    insert_pos = self.text_area.index("sel.first")
                    # 使用csv模块解析CSV
                    reader = csv.reader(io.StringIO(selected_text))
                    rows = list(reader)

                    # 计算每列的最大宽度
                    col_widths = []
                    for row in rows:
                        while len(col_widths) < len(row):
                            col_widths.append(0)
                        for i, cell in enumerate(row):
                            col_widths[i] = max(col_widths[i], len(cell))

                    # 格式化输出，保持CSV格式
                    formatted_lines = []
                    for row in rows:
                        formatted_row = ""
                        for i, cell in enumerate(row):
                            if i < len(col_widths) - 1:  # 不是最后一列
                                # 保持CSV格式，使用逗号分隔，但对齐列宽
                                formatted_row += cell.ljust(col_widths[i] + 1) + ","
                            else:
                                formatted_row += cell
                        formatted_lines.append(formatted_row)

                    formatted_csv = "\n".join(formatted_lines)
                    # 替换选中的文本
                    self.text_area.delete("sel.first", "sel.last")
                    self.text_area.insert(insert_pos, formatted_csv)
                except Exception as e:
                    # 显示错误消息
                    messagebox.showerror("错误", f"无法格式化CSV文本: {str(e)}")

        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass

    def format_xml(self):
        """格式化XML文本（美化）"""
        # 检查是否处于只读模式
        if self._is_readonly():
            self._show_readonly_message()
            return

        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                try:
                    # 保存插入位置
                    insert_pos = self.text_area.index("sel.first")
                    # 解析XML
                    root = ET.fromstring(selected_text)
                    # 格式化输出（美化）
                    rough_string = ET.tostring(root, encoding="unicode")
                    reparsed = minidom.parseString(rough_string)
                    formatted_xml = reparsed.toprettyxml(indent="  ")
                    # 移除XML声明中的额外空行
                    lines = formatted_xml.split("\n")
                    formatted_xml = "\n".join([line for line in lines if line.strip()])
                    # 替换选中的文本
                    self.text_area.delete("sel.first", "sel.last")
                    self.text_area.insert(insert_pos, formatted_xml)
                except ET.ParseError:
                    # 显示错误消息
                    messagebox.showerror(
                        "错误", "无法解析XML文本。请确保选择的文本是有效的XML格式。"
                    )

        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass

    def format_python(self):
        """格式化Python代码"""
        # 检查是否处于只读模式
        if self._is_readonly():
            self._show_readonly_message()
            return

        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                try:
                    # 保存插入位置
                    insert_pos = self.text_area.index("sel.first")

                    # 尝试使用black格式化（优先使用）
                    try:
                        # 使用black格式化代码
                        formatted_code = black.format_str(
                            selected_text, mode=black.Mode()
                        )
                    except ImportError:
                        # 如果black不可用，尝试使用autopep8
                        try:
                            # 使用autopep8格式化代码
                            formatted_code = autopep8.fix_code(selected_text)
                        except ImportError:
                            # 如果都没有，显示错误消息
                            messagebox.showerror(
                                "错误",
                                "未找到Python代码格式化工具。请安装black或autopep8。",
                            )
                            return

                    # 替换选中的文本
                    self.text_area.delete("sel.first", "sel.last")
                    self.text_area.insert(insert_pos, formatted_code)
                except Exception as e:
                    # 显示错误消息
                    messagebox.showerror("错误", f"无法格式化Python代码: {str(e)}")

        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass

    def format_yaml(self):
        """格式化YAML文本（美化，保留注释）"""
        # 检查是否处于只读模式
        if self._is_readonly():
            self._show_readonly_message()
            return

        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                try:
                    # 保存插入位置
                    insert_pos = self.text_area.index("sel.first")

                    # 尝试使用ruamel.yaml保留注释格式化
                    try:
                        # 使用ruamel.yaml保留注释格式化
                        yaml = YAML()
                        yaml.preserve_quotes = True
                        yaml.width = 4096  # 防止自动换行
                        # 读取YAML
                        yaml_obj = yaml.load(selected_text)

                        # 重新格式化输出
                        string_stream = StringIO()
                        yaml.dump(yaml_obj, string_stream)
                        formatted_yaml = string_stream.getvalue()
                    except ImportError:
                        # 如果ruamel.yaml不可用，回退到原来的PyYAML（会丢失注释）
                        # 解析YAML
                        yaml_obj = yaml.safe_load(selected_text)
                        # 格式化输出（美化）
                        formatted_yaml = yaml.dump(
                            yaml_obj,
                            allow_unicode=True,
                            indent=2,
                            default_flow_style=False,
                            sort_keys=False,
                        )

                    # 替换选中的文本
                    self.text_area.delete("sel.first", "sel.last")
                    self.text_area.insert(insert_pos, formatted_yaml)
                except Exception as e:
                    # 显示错误消息
                    messagebox.showerror("错误", f"无法解析YAML文本: {str(e)}")

        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass

    def uncomment_selection(self):
        """移除选中文本中的行注释（移除每行开头的 # 或 // ）"""
        # 检查是否处于只读模式
        if self._is_readonly():
            self._show_readonly_message()
            return

        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                # 保存插入位置
                insert_pos = self.text_area.index("sel.first")
                # 分割成行
                lines = selected_text.split("\n")
                # 移除每行开头的注释符号
                uncommented_lines = []
                for line in lines:
                    # 检查并移除行开头的 # 注释
                    if line.startswith("# "):
                        uncommented_lines.append(line[2:])
                    elif line.startswith("#"):
                        uncommented_lines.append(line[1:])
                    # 检查并移除行开头的 // 注释
                    elif line.startswith("// "):
                        uncommented_lines.append(line[3:])
                    elif line.startswith("//"):
                        uncommented_lines.append(line[2:])
                    else:
                        uncommented_lines.append(line)
                # 重新组合文本
                uncommented_text = "\n".join(uncommented_lines)
                # 替换选中的文本
                self.text_area.delete("sel.first", "sel.last")
                self.text_area.insert(insert_pos, uncommented_text)
        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass

    def encode_base64(self):
        """对选中的文本进行Base64编码"""
        # 检查是否处于只读模式
        if self._is_readonly():
            self._show_readonly_message()
            return

        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                # 保存插入位置
                insert_pos = self.text_area.index("sel.first")
                # 对文本进行Base64编码
                encoded_bytes = base64.b64encode(selected_text.encode("utf-8"))
                encoded_text = encoded_bytes.decode("utf-8")
                # 替换选中的文本
                self.text_area.delete("sel.first", "sel.last")
                self.text_area.insert(insert_pos, encoded_text)
        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass

    def decode_base64(self):
        """对选中的Base64编码文本进行解码"""
        # 检查是否处于只读模式
        if self._is_readonly():
            self._show_readonly_message()
            return

        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                # 保存插入位置
                insert_pos = self.text_area.index("sel.first")
                try:
                    # 对Base64文本进行解码
                    decoded_bytes = base64.b64decode(selected_text.encode("utf-8"))
                    decoded_text = decoded_bytes.decode("utf-8")
                    # 替换选中的文本
                    self.text_area.delete("sel.first", "sel.last")
                    self.text_area.insert(insert_pos, decoded_text)
                except Exception:
                    # 显示错误消息
                    messagebox.showerror(
                        "错误",
                        "无法解码Base64文本。请确保选择的文本是有效的Base64编码。",
                    )

        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass

    def sort_lines_asc(self):
        """将选中文本的行按升序排序"""
        # 检查是否处于只读模式
        if self._is_readonly():
            self._show_readonly_message()
            return

        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                # 保存插入位置
                insert_pos = self.text_area.index("sel.first")
                # 分割成行并排序
                lines = selected_text.split("\n")
                sorted_lines = sorted(lines)
                # 重新组合文本
                result_text = "\n".join(sorted_lines)
                # 替换选中的文本
                self.text_area.delete("sel.first", "sel.last")
                self.text_area.insert(insert_pos, result_text)
        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass

    def to_camel_case(self, event=None):
        """将选中的下划线命名转换为驼峰命名"""
        # 检查是否处于只读模式
        if self._is_readonly():
            self._show_readonly_message()
            return

        try:
            # 获取选中的文本
            try:
                selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            except tk.TclError:
                messagebox.showinfo("提示", "请先选择要处理的文本")
                return

            # 将下划线命名转换为驼峰命名
            # 先按空格、换行符分割文本
            words = re.split(r"(\s+)", selected_text)

            # 处理每个单词
            converted_words = []
            for word in words:
                # 如果是空白字符，直接添加
                if re.match(r"\s+", word):
                    converted_words.append(word)
                else:
                    # 将下划线命名转换为驼峰命名
                    parts = word.split("_")
                    camel_case_word = parts[0] + "".join(
                        part.capitalize() for part in parts[1:]
                    )
                    converted_words.append(camel_case_word)

            # 将转换后的单词重新组合成字符串
            converted_text = "".join(converted_words)

            # 替换原始选中文本
            self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_area.insert(tk.INSERT, converted_text)

        except Exception as e:
            messagebox.showerror("错误", f"处理文本时出错: {str(e)}")

    def to_snake_case(self, event=None):
        """将选中的驼峰命名转换为下划线命名"""
        # 检查是否处于只读模式
        if self._is_readonly():
            self._show_readonly_message()
            return

        try:
            # 获取选中的文本
            try:
                selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            except tk.TclError:
                messagebox.showinfo("提示", "请先选择要处理的文本")
                return

            # 将驼峰命名转换为下划线命名
            # 在大写字母前添加下划线，然后转换为小写
            snake_case_text = re.sub(
                r"([a-z0-9])([A-Z])", r"\1_\2", selected_text
            ).lower()

            # 替换原始选中文本
            self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_area.insert(tk.INSERT, snake_case_text)

        except Exception as e:
            messagebox.showerror("错误", f"处理文本时出错: {str(e)}")

    def sort_lines_desc(self, event=None):
        """降序排序选中的行"""
        # 检查是否处于只读模式
        if self._is_readonly():
            self._show_readonly_message()
            return

        try:
            # 获取选中的文本
            try:
                selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            except tk.TclError:
                messagebox.showinfo("提示", "请先选择要处理的文本")
                return

            # 分割成行并降序排序
            lines = selected_text.split("\n")
            sorted_lines = sorted(lines, reverse=True)

            # 将排序后的行重新组合成字符串
            sorted_text = "\n".join(sorted_lines)

            # 替换原始选中文本
            self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_area.insert(tk.INSERT, sorted_text)

        except Exception as e:
            messagebox.showerror("错误", f"处理文本时出错: {str(e)}")

    def reverse_text(self, event=None):
        """反转选中的文本（字符级别）"""
        # 检查是否处于只读模式
        if self._is_readonly():
            self._show_readonly_message()
            return

        try:
            # 获取选中的文本
            try:
                selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            except tk.TclError:
                messagebox.showinfo("提示", "请先选择要处理的文本")
                return

            # 反转文本
            reversed_text = selected_text[::-1]

            # 替换原始选中文本
            self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_area.insert(tk.INSERT, reversed_text)

        except Exception as e:
            messagebox.showerror("错误", f"处理文本时出错: {str(e)}")

    def reverse_lines(self, event=None):
        """反转选中的行顺序"""
        # 检查是否处于只读模式
        if self._is_readonly():
            self._show_readonly_message()
            return

        try:
            # 获取选中的文本
            try:
                selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            except tk.TclError:
                messagebox.showinfo("提示", "请先选择要处理的文本")
                return

            # 分割成行并反转行顺序
            lines = selected_text.split("\n")
            reversed_lines = lines[::-1]

            # 将反转后的行重新组合成字符串
            reversed_text = "\n".join(reversed_lines)

            # 替换原始选中文本
            self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_area.insert(tk.INSERT, reversed_text)

        except Exception as e:
            messagebox.showerror("错误", f"处理文本时出错: {str(e)}")
