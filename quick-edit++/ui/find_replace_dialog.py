#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
查找替换对话框模块
"""

import customtkinter as ctk
from config.config_manager import ConfigManager
from app.find_replace_engine import SearchOptions

class FindReplaceDialog:
    """
    查找替换对话框类
    
    提供查找和替换功能的用户界面
    """
    
    def __init__(self, parent, text_widget=None):
        """
        初始化查找替换对话框
        
        Args:
            parent: 父窗口
            text_widget: 文本编辑器控件，用于执行查找替换操作
        """
        self.parent = parent  # 父窗口
        self.text_widget = text_widget  # 文本编辑器控件
        self.config_manager = ConfigManager()  # 配置管理器
        
        # 创建查找替换引擎实例
        self.find_replace_engine = None
        
        # 获取组件默认字体配置
        self.font_family = self.config_manager.get("components.font", "Microsoft YaHei UI")
        self.font_size = 15
        self.font_bold = True
        
        # 存储输入框引用和框架引用
        self.find_entry = None # 查找输入框
        self.replace_entry = None # 替换输入框
        self.find_frame = None # 查找区域框架
        self.replace_frame = None # 替换区域框架
        
        # 当前匹配项索引
        self.current_match_index = -1
        
        # 存储搜索选项，避免每次创建新对象
        self.search_options = None
        
        # 创建对话框窗口
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("查找和替换")
        self.dialog.geometry(f"500x360+{(self.dialog.winfo_screenwidth()//3)}+{(self.dialog.winfo_screenheight()//4)}")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 设置窗口关闭协议
        self.dialog.protocol("WM_DELETE_WINDOW", self._close_dialog)
        
        # 绑定ESC键关闭对话框
        self.dialog.bind("<Escape>", lambda e: self._close_dialog())
        
        # 创建UI组件
        self._create_widgets()
        
        # 初始化搜索选项
        self._update_search_options()
        
        # 获取编辑器中的选中文本
        self._get_selected_text()
        
        # 设置焦点到查找输入框并选中所有文本
        self.dialog.after(100, self._focus_and_select)
        
        # 等待对话框关闭
        self.dialog.wait_window()
    
    def _create_widgets(self):
        """创建对话框UI组件"""
        # 主框架
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 查找区域
        find_frame = ctk.CTkFrame(main_frame)
        find_frame.pack(fill="x", pady=(0, 10))
        self.find_frame = find_frame
        
        find_label = ctk.CTkLabel(
            find_frame,
            text="查找内容:",
            font=(self.font_family, self.font_size, "bold" if self.font_bold else "normal")
        )
        find_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.find_entry = ctk.CTkEntry(
            find_frame,
            font=(self.font_family, self.font_size),
            height=35
        )
        self.find_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # 创建选项容器，用于横向排列（直接放在查找区域内部）
        options_container = ctk.CTkFrame(find_frame)
        options_container.pack(fill="x", padx=10, pady=(0, 5))
        
        self.nocase_var = ctk.BooleanVar(value=False)
        nocase_check = ctk.CTkCheckBox(
            options_container,
            text="不区分大小写",
            variable=self.nocase_var,
            font=(self.font_family, self.font_size),
            command=self._update_search_options
        )
        nocase_check.pack(side="left", padx=(0, 20))
        
        self.whole_word_var = ctk.BooleanVar(value=False)
        whole_word_check = ctk.CTkCheckBox(
            options_container,
            text="全字匹配",
            variable=self.whole_word_var,
            font=(self.font_family, self.font_size),
            command=self._update_search_options
        )
        whole_word_check.pack(side="left", padx=(0, 20))
        
        self.regex_var = ctk.BooleanVar(value=False)
        regex_check = ctk.CTkCheckBox(
            options_container,
            text="正则表达式",
            variable=self.regex_var,
            font=(self.font_family, self.font_size),
            command=self._update_search_options
        )
        regex_check.pack(side="left", padx=(0, 20))
        
        # 替换区域
        replace_frame = ctk.CTkFrame(main_frame)
        replace_frame.pack(fill="x", pady=(0, 20))
        self.replace_frame = replace_frame
        
        replace_label = ctk.CTkLabel(
            replace_frame,
            text="替换为:",
            font=(self.font_family, self.font_size, "bold" if self.font_bold else "normal")
        )
        replace_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.replace_entry = ctk.CTkEntry(
            replace_frame,
            font=(self.font_family, self.font_size),
            height=35
        )
        self.replace_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # 按钮区域
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x")
        
        # 第一行按钮
        first_row_frame = ctk.CTkFrame(button_frame)
        first_row_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        find_prev_btn = ctk.CTkButton(
            first_row_frame,
            text="查找上一个",
            font=(self.font_family, self.font_size),
            command=self._find_previous
        )
        find_prev_btn.pack(side="left", padx=(0, 5))
        
        find_next_btn = ctk.CTkButton(
            first_row_frame,
            text="查找下一个",
            font=(self.font_family, self.font_size),
            command=self._find_next
        )
        find_next_btn.pack(side="left", padx=5)
        
        find_all_btn = ctk.CTkButton(
            first_row_frame,
            text="查找全部",
            font=(self.font_family, self.font_size),
            command=self._find_all
        )
        find_all_btn.pack(side="left", padx=5)
        
        # 第二行按钮
        second_row_frame = ctk.CTkFrame(button_frame)
        second_row_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        replace_btn = ctk.CTkButton(
            second_row_frame,
            text="替换",
            font=(self.font_family, self.font_size),
            command=self._replace
        )
        replace_btn.pack(side="left", padx=(0, 5))
        
        replace_all_btn = ctk.CTkButton(
            second_row_frame,
            text="替换全部",
            font=(self.font_family, self.font_size),
            command=self._replace_all
        )
        replace_all_btn.pack(side="left", padx=5)
        
        close_btn = ctk.CTkButton(
            second_row_frame,
            text="关闭",
            font=(self.font_family, self.font_size),
            command=self._close_dialog
        )
        close_btn.pack(side="right", padx=5)
    
    def get_find_text(self):
        """获取查找输入框的内容"""
        return self.find_entry.get() if self.find_entry else ""
    
    def get_replace_text(self):
        """获取替换输入框的内容"""
        return self.replace_entry.get() if self.replace_entry else ""
    
    def _update_search_options(self):
        """
        更新搜索选项对象
        """
        # 创建SearchOptions对象
        self.search_options = SearchOptions(
            nocase=self.nocase_var.get(),
            whole_word=self.whole_word_var.get(),
            regex=self.regex_var.get()
        )
    
    def _get_search_options(self) -> SearchOptions:
        """
        获取当前的搜索选项
        
        Returns:
            SearchOptions: 搜索选项对象
        """
        return self.search_options
    
    def _show_message(self, title: str, message: str):
        """
        显示消息框
        
        Args:
            title: 消息标题
            message: 消息内容
        """
        message_box = ctk.CTkToplevel(self.dialog)
        message_box.title(title)
        message_box.geometry("300x150")
        message_box.transient(self.dialog)
        message_box.grab_set()
        
        # 居中显示
        message_box.geometry(f"+{self.dialog.winfo_rootx() + 50}+{self.dialog.winfo_rooty() + 50}")
        
        label = ctk.CTkLabel(
            message_box,
            text=message,
            font=(self.font_family, self.font_size),
            wraplength=250
        )
        label.pack(expand=True, fill="both", padx=20, pady=20)
        
        button = ctk.CTkButton(
            message_box,
            text="确定",
            command=message_box.destroy
        )
        button.pack(pady=(0, 20))
    
    def _get_selected_text(self):
        """获取编辑器中的选中文本并填充到查找输入框"""
        try:
            # 获取编辑器中的选中文本
            selected_text = self.text_widget.get("sel.first", "sel.last")
            
            # 如果有选中文本，则填充到查找输入框
            if selected_text.strip():
                self.find_entry.delete(0, "end")
                self.find_entry.insert(0, selected_text)
        except:
            # 如果没有选中文本或其他错误，不执行任何操作
            pass
            
    def _focus_and_select(self):
        """设置焦点到查找输入框并选中所有文本"""
        self.find_entry.focus_set()
        
        # 如果输入框中有文本，则选中所有文本
        if self.find_entry.get():
            self.find_entry.select_range(0, "end")
        
    def _find_all(self):
        """查找所有匹配项"""
        pass
    
    def _find_previous(self):
        """查找上一个匹配项"""
        pass
    
    def _find_next(self):
        """查找下一个匹配项"""
        pass
    
    def _replace(self):
        """替换当前匹配项"""
        pass
    
    def _replace_all(self):
        """替换所有匹配项"""
        pass
    
    def _close_dialog(self):
        """关闭对话框时清理资源"""
        # 确保在关闭时清除高亮
        if self.find_replace_engine is not None:
            try:
                # 清除高亮
                self.find_replace_engine.clear_highlights()
            except Exception as e:
                print(f"清除高亮时出错: {e}")
        
        self.dialog.destroy()


def show_find_replace_dialog(parent, text_widget=None):
    """
    显示查找替换对话框
    
    Args:
        parent: 父窗口
        text_widget: 文本编辑器控件，用于执行查找替换操作
    """
    return FindReplaceDialog(parent, text_widget)