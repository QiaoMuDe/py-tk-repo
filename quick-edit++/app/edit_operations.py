#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
编辑操作类
该模块实现文本编辑的基本操作，包括撤销、重做、剪切、复制、粘贴、全选和清除等功能
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from config.config_manager import config_manager
import os
import datetime
import uuid
import base64


class EditOperations:
    """文本编辑操作类，提供基本的文本编辑功能"""

    def __init__(self):
        """初始化编辑操作"""
        pass

    def undo(self):
        """撤销上一步操作"""
        try:
            # 检查是否可以撤销
            if self.text_area.edit_undo():
                # 更新状态栏
                self._update_status_bar()
                # 更新字符计数
                self.update_char_count()
            else:
                self.status_bar.show_notification("没有可撤销的操作", 2000)
        except Exception as e:
            # 忽略撤销操作异常
            pass

    def redo(self):
        """重做上一步撤销的操作"""
        try:
            # 检查是否可以重做
            if self.text_area.edit_redo():
                # 更新状态栏
                self._update_status_bar()
                # 更新字符计数
                self.update_char_count()
            else:
                self.status_bar.show_notification("没有可重做的操作", 2000)
        except Exception as e:
            # 忽略重做操作异常
            pass

    def cut(self):
        """剪切选中的文本"""
        try:
            # 检查是否有选中的文本
            try:
                selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
                if selected_text:
                    # 将选中的文本复制到剪贴板
                    self.clipboard_clear()
                    self.clipboard_append(selected_text)
                    # 删除选中的文本
                    self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
                    # 更新状态栏
                    self._update_status_bar()
                    # 更新
                    # 更新字符计数
                    self.update_char_count()
                    # 显示通知
                    self.status_bar.show_notification(f"已剪切 {len(selected_text)} 个字符", 2000)
                else:
                    self.status_bar.show_notification("没有选中的文本", 2000)
            except tk.TclError:
                # 没有选中文本
                self.status_bar.show_notification("没有选中的文本", 2000)
        except Exception as e:
            # 忽略剪切操作异常
            pass

    def copy(self):
        """复制选中的文本"""
        try:
            # 检查是否有选中的文本
            try:
                selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
                if selected_text:
                    # 将选中的文本复制到剪贴板
                    self.clipboard_clear()
                    self.clipboard_append(selected_text)
                    # 显示通知
                    self.status_bar.show_notification(f"已复制 {len(selected_text)} 个字符", 2000)
                else:
                    self.status_bar.show_notification("没有选中的文本", 2000)
            except tk.TclError:
                # 没有选中文本
                self.status_bar.show_notification("没有选中的文本", 2000)
        except Exception as e:
            # 忽略复制操作异常
            pass

    def paste(self):
        """粘贴剪贴板中的文本"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法粘贴", 2000)
                return

            # 获取剪贴板内容
            try:
                clipboard_text = self.clipboard_get()
                if clipboard_text:
                    # 检查是否有选中的文本
                    try:
                        # 如果有选中文本，则替换选中的文本
                        self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
                        self.text_area.insert(tk.INSERT, clipboard_text)
                    except tk.TclError:
                        # 没有选中文本，在当前位置插入
                        self.text_area.insert(tk.INSERT, clipboard_text)
                    
                    # 更新状态栏
                    self._update_status_bar()
                    # 更新字符计数
                    self.update_char_count()
                    # 显示通知
                    self.status_bar.show_notification(f"已粘贴 {len(clipboard_text)} 个字符", 2000)
                else:
                    self.status_bar.show_notification("剪贴板为空", 2000)
            except tk.TclError:
                # 剪贴板为空
                self.status_bar.show_notification("剪贴板为空", 2000)
        except Exception as e:
            # 忽略粘贴操作异常
            pass

    def select_all(self):
        """全选文本"""
        try:
            # 添加选择标记
            self.text_area.tag_add(tk.SEL, "1.0", tk.END)
            # 设置光标位置到文本末尾
            self.text_area.mark_set(tk.INSERT, tk.END)
            # 确保选择可见
            self.text_area.see(tk.INSERT)
            # 更新状态栏
            self._update_status_bar()
            # 显示通知
            total_chars = self.get_char_count()
            self.status_bar.show_notification(f"已选择全部 {total_chars} 个字符", 2000)
        except Exception as e:
            # 忽略全选操作异常
            pass

    def clear_all(self):
        """清除所有文本"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法清除", 2000)
                return

            # 获取当前字符数
            total_chars = self.get_char_count()
            
            # 如果没有内容，直接返回
            if total_chars == 0:
                self.status_bar.show_notification("文本区域已经为空", 2000)
                return

            # 确认是否清除所有文本
            confirmed = messagebox.askyesno(
                "确认清除", 
                f"确定要清除所有文本吗？\n这将删除 {total_chars} 个字符。"
            )
            
            if confirmed:
                # 清除所有文本
                self.text_area.delete("1.0", tk.END)
                # 更新状态栏
                self._update_status_bar()
                # 更新字符计数
                self.update_char_count()
                # 更新修改状态
                self.set_modified(True)
                # 显示通知
                self.status_bar.show_notification(f"已清除 {total_chars} 个字符", 2000)
        except Exception as e:
            # 忽略清除操作异常
            pass

    def clear_selection(self):
        """清除选中的文本"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法清除", 2000)
                return

            # 检查是否有选中的文本
            try:
                selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
                if selected_text:
                    # 删除选中的文本
                    self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
                    # 更新状态栏
                    self._update_status_bar()
                    # 更新字符计数
                    self.update_char_count()
                    # 更新修改状态
                    self.set_modified(True)
                    # 显示通知
                    self.status_bar.show_notification(f"已清除 {len(selected_text)} 个字符", 2000)
                else:
                    self.status_bar.show_notification("没有选中的文本", 2000)
            except tk.TclError:
                # 没有选中文本
                self.status_bar.show_notification("没有选中的文本", 2000)
        except Exception as e:
            # 忽略清除操作异常
            pass

    def insert_text(self, text):
        """在光标位置插入文本"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 2000)
                return

            # 在光标位置插入文本
            self.text_area.insert(tk.INSERT, text)
            
            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)
            
            # 显示通知
            self.status_bar.show_notification(f"已插入 {len(text)} 个字符", 2000)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_shebang(self):
        """脚本的shebang行"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 2000)
                return

            # 在光标位置插入shebang行
            self.text_area.insert(tk.INSERT, "#!/usr/bin/env ")
            
            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)
            
            # 显示通知
            self.status_bar.show_notification("已插入脚本 shebang 行", 2000)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_encoding(self):
        """插入Python脚本的编码声明"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 2000)
                return

            # 在光标位置插入编码声明
            self.text_area.insert(tk.INSERT, "# -*- coding: utf-8 -*-\n")
            
            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)
            
            # 显示通知
            self.status_bar.show_notification("已插入编码声明", 2000)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_go_basic(self):
        """插入Go语言基本结构"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 2000)
                return

            # 在光标位置插入Go语言基本结构
            go_code = """package main\n\nimport "fmt"\n\nfunc main() {\n\tfmt.Println("Hello, World!")\n}"""
            self.text_area.insert(tk.INSERT, go_code)
            
            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)
            
            # 显示通知
            self.status_bar.show_notification("已插入Go语言基本结构", 2000)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_filename(self):
        """插入当前文件名"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 2000)
                return

            # 获取当前文件名
            if hasattr(self, 'current_file_path') and self.current_file_path:
                filename = os.path.basename(self.current_file_path)
                self.text_area.insert(tk.INSERT, filename)
                
                # 更新状态栏
                self._update_status_bar()
                # 更新字符计数
                self.update_char_count()
                # 更新修改状态
                self.set_modified(True)
                
                # 显示通知
                self.status_bar.show_notification(f"已插入文件名: {filename}", 2000)
            else:
                self.status_bar.show_notification("没有当前文件", 2000)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_filepath(self):
        """插入当前文件路径"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 2000)
                return

            # 获取当前文件路径
            if hasattr(self, 'current_file_path') and self.current_file_path:
                self.text_area.insert(tk.INSERT, self.current_file_path)
                
                # 更新状态栏
                self._update_status_bar()
                # 更新字符计数
                self.update_char_count()
                # 更新修改状态
                self.set_modified(True)
                
                # 显示通知
                self.status_bar.show_notification(f"已插入文件路径: {self.current_file_path}", 2000)
            else:
                self.status_bar.show_notification("没有当前文件", 2000)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_directory(self):
        """插入当前文件所在目录路径"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 2000)
                return

            # 获取当前文件所在目录
            if hasattr(self, 'current_file_path') and self.current_file_path:
                directory = os.path.dirname(self.current_file_path)
                self.text_area.insert(tk.INSERT, directory)
                
                # 更新状态栏
                self._update_status_bar()
                # 更新字符计数
                self.update_char_count()
                # 更新修改状态
                self.set_modified(True)
                
                # 显示通知
                self.status_bar.show_notification(f"已插入目录路径: {directory}", 2000)
            else:
                self.status_bar.show_notification("没有当前文件", 2000)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_date(self, format_type="ymd"):
        """插入当前日期"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 2000)
                return

            # 根据格式类型获取日期
            now = datetime.datetime.now()
            if format_type == "ymd":
                date_str = now.strftime("%Y-%m-%d")
            elif format_type == "ymd_slash":
                date_str = now.strftime("%Y/%m/%d")
            elif format_type == "dmy":
                date_str = now.strftime("%d-%m-%Y")
            elif format_type == "dmy_slash":
                date_str = now.strftime("%d/%m/%Y")
            elif format_type == "mdy":
                date_str = now.strftime("%m-%d-%Y")
            elif format_type == "mdy_slash":
                date_str = now.strftime("%m/%d/%Y")
            else:
                date_str = now.strftime("%Y-%m-%d")

            # 在光标位置插入日期
            self.text_area.insert(tk.INSERT, date_str)
            
            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)
            
            # 显示通知
            self.status_bar.show_notification(f"已插入日期: {date_str}", 2000)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_time(self, format_type="24h"):
        """插入当前时间"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 2000)
                return

            # 根据格式类型获取时间
            now = datetime.datetime.now()
            if format_type == "24h":
                time_str = now.strftime("%H:%M:%S")
            elif format_type == "12h":
                time_str = now.strftime("%I:%M:%S %p")
            elif format_type == "24h_short":
                time_str = now.strftime("%H:%M")
            elif format_type == "12h_short":
                time_str = now.strftime("%I:%M %p")
            else:
                time_str = now.strftime("%H:%M:%S")

            # 在光标位置插入时间
            self.text_area.insert(tk.INSERT, time_str)
            
            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)
            
            # 显示通知
            self.status_bar.show_notification(f"已插入时间: {time_str}", 2000)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_datetime(self, format_type="ymd_24h"):
        """插入当前日期和时间"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 2000)
                return

            # 根据格式类型获取日期时间
            now = datetime.datetime.now()
            if format_type == "ymd_24h":
                datetime_str = now.strftime("%Y-%m-%d %H:%M:%S")
            elif format_type == "ymd_12h":
                datetime_str = now.strftime("%Y-%m-%d %I:%M:%S %p")
            elif format_type == "ymd_slash_24h":
                datetime_str = now.strftime("%Y/%m/%d %H:%M:%S")
            elif format_type == "ymd_slash_12h":
                datetime_str = now.strftime("%Y/%m/%d %I:%M:%S %p")
            else:
                datetime_str = now.strftime("%Y-%m-%d %H:%M:%S")

            # 在光标位置插入日期时间
            self.text_area.insert(tk.INSERT, datetime_str)
            
            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)
            
            # 显示通知
            self.status_bar.show_notification(f"已插入日期时间: {datetime_str}", 2000)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_timestamp(self):
        """插入当前时间戳"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 2000)
                return

            # 获取当前时间戳
            timestamp = str(int(datetime.datetime.now().timestamp()))

            # 在光标位置插入时间戳
            self.text_area.insert(tk.INSERT, timestamp)
            
            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)
            
            # 显示通知
            self.status_bar.show_notification(f"已插入时间戳: {timestamp}", 2000)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_uuid_v4(self):
        """插入UUID v4"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 2000)
                return

            # 生成UUID v4
            uuid_str = str(uuid.uuid4())

            # 在光标位置插入UUID
            self.text_area.insert(tk.INSERT, uuid_str)
            
            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)
            
            # 显示通知
            self.status_bar.show_notification(f"已插入UUID v4: {uuid_str}", 2000)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_uuid_no_hyphens(self):
        """插入无连字符的UUID"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 2000)
                return

            # 生成UUID v4并移除连字符
            uuid_str = str(uuid.uuid4()).replace("-", "")

            # 在光标位置插入UUID
            self.text_area.insert(tk.INSERT, uuid_str)
            
            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)
            
            # 显示通知
            self.status_bar.show_notification(f"已插入无连字符UUID: {uuid_str}", 2000)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_uuid_uppercase(self):
        """插入大写UUID"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 2000)
                return

            # 生成UUID v4并转换为大写
            uuid_str = str(uuid.uuid4()).upper()

            # 在光标位置插入UUID
            self.text_area.insert(tk.INSERT, uuid_str)
            
            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)
            
            # 显示通知
            self.status_bar.show_notification(f"已插入大写UUID: {uuid_str}", 2000)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_uuid_uppercase_no_hyphens(self):
        """插入大写无连字符UUID"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 2000)
                return

            # 生成UUID v4，移除连字符并转换为大写
            uuid_str = str(uuid.uuid4()).replace("-", "").upper()

            # 在光标位置插入UUID
            self.text_area.insert(tk.INSERT, uuid_str)
            
            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)
            
            # 显示通知
            self.status_bar.show_notification(f"已插入大写无连字符UUID: {uuid_str}", 2000)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_uuid_with_braces(self):
        """插入带花括号的UUID"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 2000)
                return

            # 生成UUID v4并添加花括号
            uuid_str = "{" + str(uuid.uuid4()) + "}"

            # 在光标位置插入UUID
            self.text_area.insert(tk.INSERT, uuid_str)
            
            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)
            
            # 显示通知
            self.status_bar.show_notification(f"已插入带花括号的UUID: {uuid_str}", 2000)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_uuid_uppercase_with_braces(self):
        """插入带花括号的大写UUID"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 2000)
                return

            # 生成UUID v4，转换为大写并添加花括号
            uuid_str = "{" + str(uuid.uuid4()).upper() + "}"

            # 在光标位置插入UUID
            self.text_area.insert(tk.INSERT, uuid_str)
            
            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)
            
            # 显示通知
            self.status_bar.show_notification(f"已插入带花括号的大写UUID: {uuid_str}", 2000)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_uuid_base64(self):
        """插入Base64编码的UUID"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 2000)
                return

            # 生成UUID v4并转换为Base64编码
            import base64
            uuid_bytes = uuid.uuid4().bytes
            uuid_str = base64.b64encode(uuid_bytes).decode('utf-8')

            # 在光标位置插入UUID
            self.text_area.insert(tk.INSERT, uuid_str)
            
            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)
            
            # 显示通知
            self.status_bar.show_notification(f"已插入Base64编码的UUID: {uuid_str}", 2000)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_uuid_urn(self):
        """插入URN格式UUID"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 2000)
                return

            # 生成URN格式的UUID v4
            uuid_str = "urn:uuid:" + str(uuid.uuid4())

            # 在光标位置插入UUID
            self.text_area.insert(tk.INSERT, uuid_str)
            
            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)
            
            # 显示通知
            self.status_bar.show_notification(f"已插入URN格式UUID: {uuid_str}", 2000)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_uuid_v1(self):
        """插入UUID v1（基于时间）"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 2000)
                return

            # 生成UUID v1
            uuid_str = str(uuid.uuid1())

            # 在光标位置插入UUID
            self.text_area.insert(tk.INSERT, uuid_str)
            
            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)
            
            # 显示通知
            self.status_bar.show_notification(f"已插入UUID v1: {uuid_str}", 2000)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def goto_top(self):
        """转到文件顶部"""
        try:
            # 设置光标位置到文件顶部
            self.text_area.mark_set(tk.INSERT, "1.0")
            # 确保光标可见
            self.text_area.see(tk.INSERT)
            # 更新状态栏
            self._update_status_bar()
            # 显示通知
            self.status_bar.show_notification("已转到文件顶部", 2000)
        except Exception as e:
            # 忽略转到顶部操作异常
            pass

    def goto_bottom(self):
        """转到文件底部"""
        try:
            # 设置光标位置到文件底部
            self.text_area.mark_set(tk.INSERT, tk.END)
            # 确保光标可见
            self.text_area.see(tk.INSERT)
            # 更新状态栏
            self._update_status_bar()
            # 显示通知
            self.status_bar.show_notification("已转到文件底部", 2000)
        except Exception as e:
            # 忽略转到底部操作异常
            pass

    def page_up(self):
        """向上翻页"""
        try:
            # 使用yview_scroll方法执行向上翻页操作
            self.text_area.yview_scroll(-1, "pages")
            self.text_area.focus_set()
            # 更新状态栏
            self._update_status_bar()
        except Exception as e:
            # 忽略向上翻页操作异常
            pass

    def page_down(self):
        """向下翻页"""
        try:
            # 使用yview_scroll方法执行向下翻页操作
            self.text_area.yview_scroll(1, "pages")
            self.text_area.focus_set()
            # 更新状态栏
            self._update_status_bar()
        except Exception as e:
            # 忽略向下翻页操作异常
            pass

    def clear_clipboard(self):
        """清空剪贴板"""
        try:
            # 清空剪贴板
            self.clipboard_clear()
            # 显示通知
            self.status_bar.show_notification("剪贴板已清空", 2000)
        except Exception as e:
            # 忽略清空剪贴板操作异常
            pass

    def copy_filename_to_clipboard(self):
        """复制文件名到剪贴板"""
        try:
            if self.current_file_path:
                # 获取文件名
                filename = os.path.basename(self.current_file_path)
                # 清空剪贴板
                self.clipboard_clear()
                # 添加文件名到剪贴板
                self.clipboard_append(filename)
                # 显示通知
                self.status_bar.show_notification(f"已复制文件名: {filename}", 2000)
            else:
                self.status_bar.show_notification("当前没有打开的文件", 2000)
        except Exception as e:
            # 忽略复制文件名操作异常
            pass

    def copy_filepath_to_clipboard(self):
        """复制文件路径到剪贴板"""
        try:
            if self.current_file_path:
                # 清空剪贴板
                self.clipboard_clear()
                # 添加文件路径到剪贴板
                self.clipboard_append(self.current_file_path)
                # 显示通知
                self.status_bar.show_notification(f"已复制文件路径: {self.current_file_path}", 2000)
            else:
                self.status_bar.show_notification("当前没有打开的文件", 2000)
        except Exception as e:
            # 忽略复制文件路径操作异常
            pass

    def copy_directory_to_clipboard(self):
        """复制文件所在目录路径到剪贴板"""
        try:
            if self.current_file_path:
                # 获取文件所在目录路径
                directory_path = os.path.dirname(self.current_file_path)
                # 清空剪贴板
                self.clipboard_clear()
                # 添加目录路径到剪贴板
                self.clipboard_append(directory_path)
                # 显示通知
                self.status_bar.show_notification(f"已复制目录路径: {directory_path}", 2000)
            else:
                self.status_bar.show_notification("当前没有打开的文件", 2000)
        except Exception as e:
            # 忽略复制目录路径操作异常
            pass

    def copy_selected_text_info(self):
        """复制选中文本的信息（字符数、行数）"""
        try:
            # 检查是否有选中的文本
            try:
                selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
                if selected_text:
                    # 计算字符数和行数
                    char_count = len(selected_text)
                    line_count = selected_text.count('\n') + 1
                    # 构建信息文本
                    info_text = f"选中文本信息:\n字符数: {char_count}\n行数: {line_count}"
                    # 清空剪贴板
                    self.clipboard_clear()
                    # 添加信息到剪贴板
                    self.clipboard_append(info_text)
                    # 显示通知
                    self.status_bar.show_notification(f"已复制选中文本信息: {char_count} 个字符, {line_count} 行", 2000)
                else:
                    self.status_bar.show_notification("没有选中的文本", 2000)
            except tk.TclError:
                # 没有选中文本
                self.status_bar.show_notification("没有选中的文本", 2000)
        except Exception as e:
            # 忽略复制选中文本信息操作异常
            pass

    def goto_line(self):
        """
        转到指定行

        弹出对话框让用户输入行号，然后跳转到指定行
        """
        # 获取组件字体配置
        font_config = config_manager.get_font_config("components")
        font_family = font_config.get("font", "Microsoft YaHei UI")
        font_size = 15
        font_weight = "bold"

        # 创建自定义对话框窗口
        dialog = ctk.CTkToplevel(self)
        dialog.title("转到行")
        dialog.geometry("350x150")
        dialog.resizable(False, False)
        
        # 设置窗口模态
        dialog.transient(self)
        dialog.grab_set()
        
        # 创建输入框和标签
        frame = ctk.CTkFrame(dialog)
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        label = ctk.CTkLabel(frame, text="请输入行号:", font=(font_family, font_size, font_weight))
        label.pack(pady=(0, 10))
        
        entry = ctk.CTkEntry(frame, font=(font_family, font_size, font_weight))
        entry.pack(pady=(0, 10), fill="x")
        entry.focus_set()
        
        # 按钮框架
        button_frame = ctk.CTkFrame(frame)
        button_frame.pack(fill="x")
        
        def on_ok():
            """确认按钮处理函数"""
            try:
                line_num = int(entry.get())
                # 跳转到指定行
                self.text_area.mark_set("insert", f"{line_num}.0")
                self.text_area.see("insert")
                # 更新状态栏
                self._update_status_bar()
                # 关闭对话框
                dialog.destroy()
            except ValueError:
                # 显示错误消息
                error_dialog = ctk.CTkToplevel(dialog)
                error_dialog.title("错误")
                error_dialog.geometry("250x100")
                error_dialog.resizable(False, False)
                
                error_label = ctk.CTkLabel(error_dialog, text="请输入有效的行号", font=(font_family, font_size, font_weight))
                error_label.pack(pady=20)
                
                ok_button = ctk.CTkButton(error_dialog, text="确定", font=(font_family, font_size, font_weight), command=error_dialog.destroy)
                ok_button.pack(pady=10)
        
        def on_cancel():
            """取消按钮处理函数"""
            dialog.destroy()
        
        # 创建按钮
        ok_button = ctk.CTkButton(button_frame, text="确定", font=(font_family, font_size, font_weight), command=on_ok)
        ok_button.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        cancel_button = ctk.CTkButton(button_frame, text="取消", font=(font_family, font_size, font_weight), command=on_cancel)
        cancel_button.pack(side="right", fill="x", expand=True)
        
        # 绑定回车键
        entry.bind("<Return>", lambda e: on_ok())
        
        # 绑定ESC键
        dialog.bind("<Escape>", lambda e: on_cancel())
        
        # 居中显示对话框
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # 在对话框完全显示后设置焦点
        dialog.after(100, entry.focus_set)
