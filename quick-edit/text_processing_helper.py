import tkinter as tk

class TextProcessingHelper:
    """文本处理助手类，提供选中文本的各种处理功能"""
    
    def __init__(self, text_area):
        """初始化文本处理助手
        
        Args:
            text_area: 文本编辑区域组件
        """
        self.text_area = text_area
    
    def convert_to_uppercase(self):
        """将选中的文本转换为大写"""
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
        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                # 保存插入位置
                insert_pos = self.text_area.index("sel.first")
                # 分割成行
                lines = selected_text.split('\n')
                # 移除每行左侧空白
                processed_lines = [line.lstrip() for line in lines]
                # 重新组合文本
                result_text = '\n'.join(processed_lines)
                # 替换选中的文本
                self.text_area.delete("sel.first", "sel.last")
                self.text_area.insert(insert_pos, result_text)
        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass
    
    def remove_right_whitespace(self):
        """移除选中文本每行的右侧空白"""
        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                # 保存插入位置
                insert_pos = self.text_area.index("sel.first")
                # 分割成行
                lines = selected_text.split('\n')
                # 移除每行右侧空白
                processed_lines = [line.rstrip() for line in lines]
                # 重新组合文本
                result_text = '\n'.join(processed_lines)
                # 替换选中的文本
                self.text_area.delete("sel.first", "sel.last")
                self.text_area.insert(insert_pos, result_text)
        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass
    
    def remove_blank_lines(self):
        """移除选中文本中的所有空白行"""
        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                # 保存插入位置
                insert_pos = self.text_area.index("sel.first")
                # 分割成行
                lines = selected_text.split('\n')
                # 移除空白行
                processed_lines = [line for line in lines if line.strip()]
                # 重新组合文本
                result_text = '\n'.join(processed_lines)
                # 替换选中的文本
                self.text_area.delete("sel.first", "sel.last")
                self.text_area.insert(insert_pos, result_text)
        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass
    
    def merge_blank_lines(self):
        """合并连续的空白行为单个空白行"""
        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                # 保存插入位置
                insert_pos = self.text_area.index("sel.first")
                # 分割成行
                lines = selected_text.split('\n')
                processed_lines = []
                last_was_blank = False
                
                for line in lines:
                    is_blank = not line.strip()
                    # 如果当前行是空白行且上一行不是空白行，则添加一个空白行
                    if is_blank:
                        if not last_was_blank:
                            processed_lines.append('')
                        last_was_blank = True
                    else:
                        processed_lines.append(line)
                        last_was_blank = False
                
                # 重新组合文本
                result_text = '\n'.join(processed_lines)
                # 替换选中的文本
                self.text_area.delete("sel.first", "sel.last")
                self.text_area.insert(insert_pos, result_text)
        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass
    
    def merge_duplicate_lines(self):
        """合并重复的行（保留第一次出现的行）"""
        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                # 保存插入位置
                insert_pos = self.text_area.index("sel.first")
                # 分割成行
                lines = selected_text.split('\n')
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
                result_text = '\n'.join(processed_lines)
                # 替换选中的文本
                self.text_area.delete("sel.first", "sel.last")
                self.text_area.insert(insert_pos, result_text)
        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass
    
    def remove_duplicate_blank_lines(self):
        """移除重复的空行"""
        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                # 保存插入位置
                insert_pos = self.text_area.index("sel.first")
                # 分割成行
                lines = selected_text.split('\n')
                processed_lines = []
                last_was_blank = False
                
                for line in lines:
                    is_blank = not line.strip()
                    # 如果是空白行且上一行不是空白行，则添加
                    if is_blank:
                        if not last_was_blank:
                            processed_lines.append('')
                            last_was_blank = True
                    else:
                        processed_lines.append(line)
                        last_was_blank = False
                
                # 重新组合文本
                result_text = '\n'.join(processed_lines)
                # 替换选中的文本
                self.text_area.delete("sel.first", "sel.last")
                self.text_area.insert(insert_pos, result_text)
        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass
    
    def format_json(self):
        """格式化JSON文本（美化）"""
        try:
            import json
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
                    if hasattr(self.text_area, 'master') and hasattr(self.text_area.master, 'master'):
                        root = self.text_area.master.master
                        if hasattr(root, 'show_message'):
                            root.show_message("错误", "无法解析JSON文本。请确保选择的文本是有效的JSON格式。")
                    else:
                        # 如果找不到show_message方法，使用tkinter的messagebox
                        import tkinter.messagebox as messagebox
                        messagebox.showerror("错误", "无法解析JSON文本。请确保选择的文本是有效的JSON格式。")
        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass
    
    def compress_json(self):
        """压缩JSON文本（移除所有空白字符）"""
        try:
            import json
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                try:
                    # 保存插入位置
                    insert_pos = self.text_area.index("sel.first")
                    # 解析JSON
                    json_obj = json.loads(selected_text)
                    # 压缩输出
                    compressed_json = json.dumps(json_obj, ensure_ascii=False, separators=(',', ':'))
                    # 替换选中的文本
                    self.text_area.delete("sel.first", "sel.last")
                    self.text_area.insert(insert_pos, compressed_json)
                except json.JSONDecodeError:
                    # 显示错误消息
                    if hasattr(self.text_area, 'master') and hasattr(self.text_area.master, 'master'):
                        root = self.text_area.master.master
                        if hasattr(root, 'show_message'):
                            root.show_message("错误", "无法解析JSON文本。请确保选择的文本是有效的JSON格式。")
                    else:
                        # 如果找不到show_message方法，使用tkinter的messagebox
                        import tkinter.messagebox as messagebox
                        messagebox.showerror("错误", "无法解析JSON文本。请确保选择的文本是有效的JSON格式。")
        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass
    
    def remove_extra_whitespace(self):
        """移除选中文本中的多余空白字符（连续空格替换为单个空格）"""
        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                # 保存插入位置
                insert_pos = self.text_area.index("sel.first")
                # 移除多余空白
                # 保留换行符，只处理行内空格
                lines = selected_text.split('\n')
                processed_lines = []
                for line in lines:
                    # 替换连续空格为单个空格
                    processed_line = ' '.join(line.split())
                    processed_lines.append(processed_line)
                # 重新组合文本
                result_text = '\n'.join(processed_lines)
                # 替换选中的文本
                self.text_area.delete("sel.first", "sel.last")
                self.text_area.insert(insert_pos, result_text)
        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass
    
    def comment_selection(self):
        """为选中的文本添加行注释（在每行开头添加 # ）"""
        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                # 保存插入位置
                insert_pos = self.text_area.index("sel.first")
                # 分割成行
                lines = selected_text.split('\n')
                # 为每行添加注释
                commented_lines = ['# ' + line for line in lines]
                # 重新组合文本
                commented_text = '\n'.join(commented_lines)
                # 替换选中的文本
                self.text_area.delete("sel.first", "sel.last")
                self.text_area.insert(insert_pos, commented_text)
        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass
    
    def format_ini(self):
        """格式化INI文本（对齐键值对）"""
        try:
            import configparser
            import io
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                try:
                    # 保存插入位置
                    insert_pos = self.text_area.index("sel.first")
                    # 使用configparser解析INI
                    config = configparser.ConfigParser()
                    config.read_string(selected_text)
                    
                    # 格式化输出
                    output = io.StringIO()
                    config.write(output)
                    formatted_ini = output.getvalue()
                    output.close()
                    
                    # 替换选中的文本
                    self.text_area.delete("sel.first", "sel.last")
                    self.text_area.insert(insert_pos, formatted_ini)
                except Exception as e:
                    # 显示错误消息
                    if hasattr(self.text_area, 'master') and hasattr(self.text_area.master, 'master'):
                        root = self.text_area.master.master
                        if hasattr(root, 'show_message'):
                            root.show_message("错误", f"无法解析INI文本: {str(e)}")
                    else:
                        # 如果找不到show_message方法，使用tkinter的messagebox
                        import tkinter.messagebox as messagebox
                        messagebox.showerror("错误", f"无法解析INI文本: {str(e)}")
        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass

    def format_csv(self):
        """格式化CSV文本（对齐列）"""
        try:
            import csv
            import io
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
                    
                    # 格式化输出
                    formatted_lines = []
                    for row in rows:
                        formatted_row = ""
                        for i, cell in enumerate(row):
                            if i < len(col_widths) - 1:  # 不是最后一列
                                formatted_row += cell.ljust(col_widths[i] + 2)  # 用空格填充并添加间隔
                            else:
                                formatted_row += cell
                        formatted_lines.append(formatted_row)
                    
                    formatted_csv = '\n'.join(formatted_lines)
                    # 替换选中的文本
                    self.text_area.delete("sel.first", "sel.last")
                    self.text_area.insert(insert_pos, formatted_csv)
                except Exception as e:
                    # 显示错误消息
                    if hasattr(self.text_area, 'master') and hasattr(self.text_area.master, 'master'):
                        root = self.text_area.master.master
                        if hasattr(root, 'show_message'):
                            root.show_message("错误", f"无法解析CSV文本: {str(e)}")
                    else:
                        # 如果找不到show_message方法，使用tkinter的messagebox
                        import tkinter.messagebox as messagebox
                        messagebox.showerror("错误", f"无法解析CSV文本: {str(e)}")
        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass

    def format_xml(self):
        """格式化XML文本（美化）"""
        try:
            import xml.etree.ElementTree as ET
            from xml.dom import minidom
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                try:
                    # 保存插入位置
                    insert_pos = self.text_area.index("sel.first")
                    # 解析XML
                    root = ET.fromstring(selected_text)
                    # 格式化输出（美化）
                    rough_string = ET.tostring(root, encoding='unicode')
                    reparsed = minidom.parseString(rough_string)
                    formatted_xml = reparsed.toprettyxml(indent="  ")
                    # 移除XML声明中的额外空行
                    lines = formatted_xml.split('\n')
                    formatted_xml = '\n'.join([line for line in lines if line.strip()])
                    # 替换选中的文本
                    self.text_area.delete("sel.first", "sel.last")
                    self.text_area.insert(insert_pos, formatted_xml)
                except ET.ParseError:
                    # 显示错误消息
                    if hasattr(self.text_area, 'master') and hasattr(self.text_area.master, 'master'):
                        root = self.text_area.master.master
                        if hasattr(root, 'show_message'):
                            root.show_message("错误", "无法解析XML文本。请确保选择的文本是有效的XML格式。")
                    else:
                        # 如果找不到show_message方法，使用tkinter的messagebox
                        import tkinter.messagebox as messagebox
                        messagebox.showerror("错误", "无法解析XML文本。请确保选择的文本是有效的XML格式。")
        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass

    def uncomment_selection(self):
        """移除选中文本中的行注释（移除每行开头的 # ）"""
        try:
            # 获取选中文本
            selected_text = self.text_area.selection_get()
            if selected_text:
                # 保存插入位置
                insert_pos = self.text_area.index("sel.first")
                # 分割成行
                lines = selected_text.split('\n')
                # 移除每行开头的注释符号
                uncommented_lines = []
                for line in lines:
                    # 移除行开头的 # 和可能的空格
                    if line.startswith('# '):
                        uncommented_lines.append(line[2:])
                    elif line.startswith('#'):
                        uncommented_lines.append(line[1:])
                    else:
                        uncommented_lines.append(line)
                # 重新组合文本
                uncommented_text = '\n'.join(uncommented_lines)
                # 替换选中的文本
                self.text_area.delete("sel.first", "sel.last")
                self.text_area.insert(insert_pos, uncommented_text)
        except tk.TclError:
            # 没有选中文本时不做任何操作
            pass