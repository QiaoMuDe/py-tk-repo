import os
import tkinter as tk
from datetime import datetime
import tkinter.messagebox as messagebox


class InsertHelper:
    """
    插入功能辅助类，提供各种文本插入功能
    """

    def __init__(self, editor):
        """
        初始化插入助手

        Args:
            editor: 编辑器实例，包含text_area、current_file等属性
        """
        self.editor = editor

    def insert_shebang(self):
        """在光标位置插入 Shebang 行"""
        try:
            self.editor.text_area.insert(tk.INSERT, "#!/usr/bin/env ")
            # 保持光标在插入文本之后
            current_cursor_pos = self.editor.text_area.index(tk.INSERT)
        except Exception as e:
            messagebox.showerror("错误", f"插入 Shebang 行时出错: {str(e)}")

    def insert_python_encoding(self):
        """在光标位置插入Python字符集声明"""
        try:
            self.editor.text_area.insert(tk.INSERT, "# -*- coding: utf-8 -*-")
        except Exception as e:
            messagebox.showerror("错误", f"插入Python字符集声明时出错: {str(e)}")

    def insert_go_package_main(self):
        """在光标位置插入Go语言基本结构"""
        try:
            go_structure = 'package main\n\nimport (\n\tfmt""\n)\n\nfunc main() {\n\tfmt.Println("Hello, World!")\n}'
            self.editor.text_area.insert(tk.INSERT, go_structure)
        except Exception as e:
            messagebox.showerror("错误", f"插入Go语言基本结构时出错: {str(e)}")

    def insert_filename(self):
        """在光标位置插入文件名"""
        if self.editor.current_file:
            try:
                filename = os.path.basename(self.editor.current_file)
                self.editor.text_area.insert(tk.INSERT, filename)
            except Exception as e:
                messagebox.showerror("错误", f"插入文件名时出错: {str(e)}")
        else:
            messagebox.showinfo("提示", "当前没有打开的文件")

    def insert_filepath(self):
        """在光标位置插入完整文件路径"""
        if self.editor.current_file:
            try:
                self.editor.text_area.insert(tk.INSERT, self.editor.current_file)
            except Exception as e:
                messagebox.showerror("错误", f"插入完整文件路径时出错: {str(e)}")
        else:
            messagebox.showinfo("提示", "当前没有打开的文件")

    def insert_directory(self):
        """在光标位置插入目录"""
        if self.editor.current_file:
            try:
                directory = os.path.dirname(self.editor.current_file)
                self.editor.text_area.insert(tk.INSERT, directory)
            except Exception as e:
                messagebox.showerror("错误", f"插入目录时出错: {str(e)}")
        else:
            messagebox.showinfo("提示", "当前没有打开的文件")

    def insert_date_yyyy_mm_dd(self):
        """在光标位置插入日期 (YYYY-MM-DD 格式)"""
        try:
            date_str = datetime.now().strftime("%Y-%m-%d")
            self.editor.text_area.insert(tk.INSERT, date_str)
        except Exception as e:
            messagebox.showerror("错误", f"插入日期时出错: {str(e)}")

    def insert_date_yyyy_slash_mm_slash_dd(self):
        """在光标位置插入日期 (YYYY/MM/DD 格式)"""
        try:
            date_str = datetime.now().strftime("%Y/%m/%d")
            self.editor.text_area.insert(tk.INSERT, date_str)
        except Exception as e:
            messagebox.showerror("错误", f"插入日期时出错: {str(e)}")

    def insert_date_dd_slash_mm_slash_yyyy(self):
        """在光标位置插入日期 (DD/MM/YYYY 格式)"""
        try:
            date_str = datetime.now().strftime("%d/%m/%Y")
            self.editor.text_area.insert(tk.INSERT, date_str)
        except Exception as e:
            messagebox.showerror("错误", f"插入日期时出错: {str(e)}")

    def insert_date_mm_slash_dd_slash_yyyy(self):
        """在光标位置插入日期 (MM/DD/YYYY 格式)"""
        try:
            date_str = datetime.now().strftime("%m/%d/%Y")
            self.editor.text_area.insert(tk.INSERT, date_str)
        except Exception as e:
            messagebox.showerror("错误", f"插入日期时出错: {str(e)}")

    def insert_datetime_full(self):
        """在光标位置插入完整日期时间 (YYYY-MM-DD HH:MM:SS 格式)"""
        try:
            datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.editor.text_area.insert(tk.INSERT, datetime_str)
        except Exception as e:
            messagebox.showerror("错误", f"插入日期时间时出错: {str(e)}")

    def insert_timestamp_yyyymmddhhmmss(self):
        """在光标位置插入时间戳 (YYYYMMDDHHMMSS 格式)"""
        try:
            timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
            self.editor.text_area.insert(tk.INSERT, timestamp_str)
        except Exception as e:
            messagebox.showerror("错误", f"插入时间戳时出错: {str(e)}")

    def insert_time_hhmmss(self):
        """在光标位置插入当前时间 (HH:MM:SS 格式)"""
        try:
            time_str = datetime.now().strftime("%H:%M:%S")
            self.editor.text_area.insert(tk.INSERT, time_str)
        except Exception as e:
            messagebox.showerror("错误", f"插入时间时出错: {str(e)}")

    def create_insert_menu(self, parent_menu):
        """创建插入子菜单

        Args:
            parent_menu: 父菜单对象

        Returns:
            创建的插入子菜单对象
        """
        insert_menu = tk.Menu(parent_menu, tearoff=0, font=("微软雅黑", 9))
        insert_menu.add_command(label="脚本 Shebang 行", command=self.insert_shebang)
        insert_menu.add_command(
            label="Python字符集声明", command=self.insert_python_encoding
        )
        insert_menu.add_command(label="pkgm", command=self.insert_go_package_main)
        insert_menu.add_separator()
        insert_menu.add_command(label="文件名", command=self.insert_filename)
        insert_menu.add_command(label="目录", command=self.insert_directory)
        insert_menu.add_command(label="完整文件路径", command=self.insert_filepath)
        insert_menu.add_separator()

        # 创建时间格式子菜单
        time_menu = tk.Menu(insert_menu, tearoff=0, font=("微软雅黑", 9))
        time_menu.add_command(label="HH:MM:SS", command=self.insert_time_hhmmss)
        time_menu.add_command(label="YYYY-MM-DD", command=self.insert_date_yyyy_mm_dd)
        time_menu.add_command(
            label="YYYY/MM/DD", command=self.insert_date_yyyy_slash_mm_slash_dd
        )
        time_menu.add_command(
            label="DD/MM/YYYY", command=self.insert_date_dd_slash_mm_slash_yyyy
        )
        time_menu.add_command(
            label="MM/DD/YYYY", command=self.insert_date_mm_slash_dd_slash_yyyy
        )
        time_menu.add_command(
            label="YYYY-MM-DD HH:MM:SS", command=self.insert_datetime_full
        )
        time_menu.add_command(
            label="YYYYMMDDHHMMSS", command=self.insert_timestamp_yyyymmddhhmmss
        )
        insert_menu.add_cascade(label="时间格式", menu=time_menu)

        return insert_menu
