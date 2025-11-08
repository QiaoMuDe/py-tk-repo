#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
编辑器主应用类
该模块直接实现主窗口功能，负责组装所有UI组件和核心功能，提供统一的应用程序接口
"""

import customtkinter as ctk
import tkinter as tk
import sys
import os
import time
from datetime import datetime
from config.config_manager import config_manager
from ui.menu import create_menu
from ui.toolbar import Toolbar
from ui.status_bar import StatusBar
from operations.file_operations import FileOperations
from tkinter import messagebox


class QuickEditApp(ctk.CTk):
    """QuickEdit++ 主应用类 - 直接继承ctk.CTk作为主窗口"""

    def __init__(self):
        """初始化应用"""
        # 设置应用外观模式
        theme_mode = config_manager.get("app.theme_mode", "light")
        ctk.set_appearance_mode(theme_mode)  # 可选: "light", "dark", "system"

        color_theme = config_manager.get("app.color_theme", "blue")
        ctk.set_default_color_theme(color_theme)  # 可选: "blue", "green", "dark-blue"

        # 启用DPI缩放支持
        try:
            from ctypes import windll

            windll.shcore.SetProcessDpiAwareness(1)
        except Exception as e:
            print(f"警告: 无法启用DPI缩放支持: {e}")

        # 初始化CTk主窗口
        super().__init__()

        # 设置窗口标题
        self.title("QuickEdit++")

        # 获取窗口大小配置
        window_width = config_manager.get("app.window_width", 1200)
        window_height = config_manager.get("app.window_height", 800)

        # 设置窗口大小, 相对居中显示
        self.geometry(
            f"{window_width}x{window_height}+{window_width//2}+{window_height//3}"
        )

        # 设置最小窗口大小
        min_width = config_manager.get("app.min_width", 800)
        min_height = config_manager.get("app.min_height", 600)
        self.minsize(min_width, min_height)

        # 初始化字体设置
        font_config = config_manager.get_font_config("text_editor")
        self.current_font = ctk.CTkFont(
            family=font_config.get("font", "Consolas"),
            size=font_config.get("font_size", 12),
            weight="bold" if font_config.get("font_bold", False) else "normal",
        )

        # 设置窗口关闭事件
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        # 自动保存相关属性
        self.auto_save_enabled = config_manager.get(
            "saving.auto_save", False
        )  # 是否启用自动保存
        self.auto_save_interval = config_manager.get(
            "saving.auto_save_interval", 5
        )  # 自动保存间隔，单位秒
        self.last_auto_save_time = 0  # 上次自动保存时间
        self._auto_save_job = None  # 自动保存任务ID

        # 初始化文件操作处理器
        self.file_ops = FileOperations(self)

        # 初始化文件相关属性
        self.current_file_path = None  # 当前文件路径
        self.current_encoding = "UTF-8"  # 当前文件编码
        self.current_line_ending = config_manager.get(
            "app.default_line_ending", "LF"
        )  # 从配置中读取默认换行符
        self.is_modified = False  # 文件修改状态，False表示未修改，True表示已修改
        self.is_new_file = False  # 是否为新文件状态
        
        # 字符数缓存
        self._total_chars = 0  # 缓存的总字符数

        # 从配置文件中读取只读模式状态
        self.is_read_only = config_manager.get(
            "text_editor.read_only", False
        )  # 是否为只读模式

        # 初始化菜单状态变量
        self.toolbar_var = None
        self.auto_wrap_var = None
        self.quick_insert_var = None
        self.auto_save_var = None
        self.backup_var = None
        self.auto_save_interval_var = None

        # 初始化窗口标题模式变量
        current_title_mode = config_manager.get("app.window_title_mode", "filename")
        self.title_mode_var = tk.StringVar(value=current_title_mode)

        # 配置主窗口的网格布局
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # 文本区域所在行可扩展

        # 防止窗口大小变化时的重新计算，减少闪烁
        self.grid_propagate(False)

        # 创建工具栏
        if config_manager.get("app.show_toolbar", True):
            self.toolbar = Toolbar(self)
            self.toolbar.grid(row=0, column=0, sticky="ew")
        else:
            # 如果配置为不显示工具栏，仍然创建工具栏对象但不显示
            self.toolbar = Toolbar(self)
            # 不调用grid，因此工具栏不会显示

        # 创建状态栏并放置在主窗口底部，传入APP实例
        self.status_bar = StatusBar(self, app=self)
        if config_manager.get("status_bar.show_status_bar", True):
            self.status_bar.grid(row=2, column=0, sticky="ew")

        # 创建文本编辑区域框架 - 去掉圆角和内边距，避免阴影效果
        self.text_frame = ctk.CTkFrame(self)
        self.text_frame.grid(row=1, column=0, sticky="nsew")

        # 获取自动换行设置
        auto_wrap = config_manager.get("text_editor.auto_wrap", True)
        wrap_mode = "word" if auto_wrap else "none"

        # 创建文本编辑区域 - 去掉圆角，确保完全填充
        self.text_area = ctk.CTkTextbox(
            self.text_frame, wrap=wrap_mode, undo=True, font=self.current_font
        )
        self.text_area.pack(fill="both", expand=True, padx=0, pady=0)

        # 创建菜单栏
        self.menu_bar = create_menu(self)
        self.config(menu=self.menu_bar)
        
        # 设置初始只读模式状态
        if self.is_read_only:
            # 设置为只读模式
            self.text_area.configure(state="disabled")
            # 更新工具栏按钮外观
            self.toolbar.readonly_button.configure(
                fg_color="#FF6B6B", hover_color="#FF5252"
            )

        # 绑定应用程序事件和快捷方式
        self._bind_app_events()

        # 初始化状态栏显示
        self._init_status_bar()

        # 启动自动保存功能
        self._start_auto_save()

    def _init_status_bar(self):
        """初始化状态栏显示"""
        # 设置初始状态信息
        self.status_bar.set_status_info()

        # 暂时隐藏自动保存信息，因为功能尚未开发完成
        # self.status_bar.set_auto_save_info("从未")

        # 设置初始文件信息，包括默认换行符
        self.status_bar.set_file_info(
            filename=None,
            encoding=self.current_encoding,
            line_ending=self.current_line_ending,
        )

        # 暂时隐藏自动保存间隔，因为功能尚未开发完成
        # self.status_bar.set_auto_save_interval(self.auto_save_interval)

    def _on_closing(self):
        """窗口关闭事件处理"""
        # 取消自动保存任务（如果有）
        if hasattr(self, "_auto_save_job") and self._auto_save_job is not None:
            self.after_cancel(self._auto_save_job)
            self._auto_save_job = None

        # 检查是否需要保存当前文件
        if self.check_save_before_close():
            self.destroy()
        # 如果用户取消保存，则不关闭窗口

    def _bind_app_events(self):
        """
        绑定应用程序级别的事件和快捷方式
        
        包括自动保存触发事件和焦点管理事件
        """
        # 绑定文本框焦点离开事件，触发自动保存
        self.text_area.bind("<FocusOut>", self._on_text_area_focus_out)
         # 绑定按键事件
        self.text_area.bind("<KeyRelease>", self._on_text_change)  # 监听文本改变事件
        self.text_area.bind("<Button-1>", self._on_cursor_move)  # 监听鼠标点击事件
        self.text_area.bind(
            "<<Selection>>", self._on_selection_change
        )  # 监听选择内容改变事件
        self.text_area.bind("<MouseWheel>", self._on_cursor_move)  # 监听鼠标滚轮事件
        
        # 绑定文件操作快捷键
        self.bind("<Control-n>", lambda e: self.new_file())  # 新建文件
        self.bind("<Control-o>", lambda e: self.open_file())  # 打开文件
        self.bind("<Control-s>", lambda e: self.save_file())  # 保存文件
        self.bind("<Control-Shift-S>", lambda e: self.save_file_as())  # 另存为
        self.bind("<Control-w>", lambda e: self.close_file())  # 关闭文件
        self.bind("<Control-e>", lambda e: self.open_containing_folder())  # 打开文件所在目录
        self.bind("<Control-r>", lambda e: self.toggle_read_only())  # 切换只读模式
        
        # 设置应用程序启动后获取焦点
        self.after(100, self._on_app_startup)
    
    def _on_app_startup(self):
        """
        应用程序启动时的焦点设置
        
        先让窗口获取焦点，然后设置文本区域焦点
        """
        # 确保窗口完全显示并获取焦点
        self.focus_force()
        self.update()
        
        # 然后设置文本区域焦点
        self._focus_text_area()
    
    def _on_text_area_focus_out(self, event=None):
        """
        文本区域失去焦点事件处理
        
        当焦点离开文本框时，调用自动保存方法
        所有检查逻辑都在_auto_save方法内部处理
        """
        # 直接调用自动保存方法，内部会检查是否需要保存
        self._auto_save()
    
    def _focus_text_area(self):
        """
        将焦点设置到文本编辑区域
        
        如果文本区域可编辑（非只读模式），则将焦点设置到文本区域
        """
        if not self.is_read_only:
            # 确保窗口已经完全显示
            # self.update()
            # 设置焦点到文本区域
            self.text_area.focus_set()
            # 将光标移动到文本末尾或当前位置
            try:
                # 如果有内容，将光标移动到末尾
                content = self.text_area.get("1.0", "end-1c")
                if content:
                    self.text_area.mark_set("insert", "end")
                else:
                    # 如果没有内容，将光标设置到开始位置
                    self.text_area.mark_set("insert", "1.0")
            except:
                # 如果出现异常，至少确保焦点在文本区域
                pass

    def _on_text_change(self, event=None):
        """文本改变事件处理"""
        # 如果当前有文件路径，则标记为已修改
        # 如果没有文件路径（新文件），只有当内容不为空时才标记为已修改
        if self.current_file_path:
            self.is_modified = True
        else:
            content = self.text_area.get("1.0", ctk.END).strip()
            self.is_modified = len(content) > 0

        # 更新缓存的字符数
        self.update_char_count()

        self._update_status_bar()

    def _on_cursor_move(self, event=None):
        """光标移动事件处理"""
        self._update_status_bar()

    def _on_selection_change(self, event=None):
        """选择内容改变事件处理"""
        self._update_status_bar()

    def _update_status_bar(self):
        """更新状态栏信息"""
        # 如果当前有通知活动，不更新状态栏
        if not self.status_bar.can_update_status():
            return

        # 获取光标位置
        cursor_pos = self.text_area.index(ctk.INSERT)
        row, col = cursor_pos.split(".")
        row, col = int(row), int(col) + 1  # 转换为1基索引

        # 获取选中字符数
        try:
            selected_content = self.text_area.get(ctk.SEL_FIRST, ctk.SEL_LAST)
            # 计算选中内容的字符数，不特殊处理换行符
            selected_chars = len(selected_content)

            # 获取选中的起始和结束位置
            start_pos = self.text_area.index(ctk.SEL_FIRST)
            end_pos = self.text_area.index(ctk.SEL_LAST)

            # 提取起始和结束行号
            start_row = int(start_pos.split(".")[0])
            end_row = int(end_pos.split(".")[0])

            # 计算选中的行数
            selected_lines = end_row - start_row + 1

            # 特殊情况处理：
            # 1. 如果选中内容为空，不显示行数
            # 2. 如果全选且末尾没有字符（即end_col为0），则减去一行
            end_col = int(end_pos.split(".")[1])
            if selected_chars == 0:
                selected_lines = None
            elif end_col == 0 and end_row > start_row:
                # 全选情况，末尾位置在行首，减去一行
                selected_lines = end_row - start_row

        except tk.TclError:
            # 没有选中内容
            selected_chars = None
            selected_lines = None

        # 根据文件修改状态确定状态文本
        status = "已修改" if self.is_modified else "就绪"

        # 更新状态栏，不再传递total_chars参数，让set_status_info内部获取
        self.status_bar.set_status_info(
            status=status,
            row=row,
            col=col,
            selected_chars=selected_chars,
            selected_lines=selected_lines,
        )

        # 更新窗口标题
        self._update_window_title()

    def _update_window_title(self):
        """根据文件修改状态更新窗口标题"""
        # 使用类属性获取窗口标题模式
        title_mode = self.title_mode_var.get()

        # 根据文件修改状态和路径构建标题
        if self.current_file_path:
            # 有文件路径的情况
            file_path = self.current_file_path
            file_name = os.path.basename(file_path)

            # 根据配置的模式构建标题
            if title_mode == "filepath":
                # 完整文件路径模式
                title_part = file_path
            elif title_mode == "filename_and_dir":
                # 文件名和目录模式
                dir_name = os.path.dirname(file_path)
                title_part = f"{file_name} [{dir_name}]" if dir_name else file_name
            else:  # 默认为 "filename" 模式
                title_part = file_name
        elif self.is_new_file:
            # 新文件状态，无论内容是否为空都显示"新文件"
            title_part = "新文件"
        else:
            # 没有文件路径的情况
            content = self.text_area.get("1.0", ctk.END).strip()
            if content:
                title_part = "未命名"
            else:
                title_part = None

        # 构建最终标题
        if title_part:
            # 根据修改状态添加星号
            prefix = "*" if self.is_modified else ""
            title = f"{prefix}{title_part} - QuickEdit++"
        else:
            # 没有内容时只显示程序名
            title = "QuickEdit++"

        self.title(title)

    def open_file(self):
        """打开文件并加载到文本编辑区域"""
        # 检查是否为只读模式
        if self.is_read_only:
            from tkinter import messagebox

            messagebox.showinfo("提示", "当前为只读模式，请先关闭只读模式后再打开文件")
            return
        # 直接调用文件操作处理器的打开文件方法
        self.file_ops.open_file()
    
    def open_file_with_path(self, file_path):
        """通过指定路径打开文件"""
        # 设置当前文件路径
        self.current_file_path = file_path
        
        # 调用FileOperations类中的辅助方法
        self.file_ops._open_file_with_path_helper(file_path)

    def save_file(self):
        """保存当前文件"""
        # 检查是否为只读模式
        if self.is_read_only:
            from tkinter import messagebox

            messagebox.showinfo("提示", "当前为只读模式，无法保存文件")
            return False
        # 直接调用文件操作处理器的保存文件方法
        return self.file_ops.save_file()

    def save_file_as(self):
        """另存为文件"""
        # 检查是否为只读模式
        if self.is_read_only:
            from tkinter import messagebox

            messagebox.showinfo("提示", "当前为只读模式，无法另存为文件")
            return False
        # 直接调用文件操作处理器的另存为方法
        return self.file_ops.save_file_as()

    def close_file(self):
        """关闭当前文件"""
        # 检查是否为只读模式
        if self.is_read_only:
            from tkinter import messagebox

            messagebox.showinfo("提示", "当前为只读模式，请先关闭只读模式后再关闭文件")
            return
        # 直接调用文件操作处理器的关闭文件方法
        self.file_ops.close_file()

    def check_save_before_close(self):
        """在关闭文件前检查是否需要保存"""
        # 直接调用文件操作处理器的检查保存方法
        return self.file_ops.check_save_before_close()

    def new_file(self):
        """创建新文件"""
        # 检查是否为只读模式
        if self.is_read_only:
            messagebox.showinfo(
                "提示", "当前为只读模式，请先关闭只读模式后再创建新文件"
            )
            return
        # 直接调用文件操作处理器的新建文件方法
        self.file_ops.new_file()
    
    def new_file_with_path(self, file_path):
        """通过指定路径创建新文件"""
        # 调用FileOperations类的新方法
        self.file_ops.new_file_with_path(file_path)

    def toggle_read_only(self):
        """切换只读模式"""
        self.is_read_only = not self.is_read_only

        # 保存只读模式状态到配置文件
        from config.config_manager import config_manager

        config_manager.set("text_editor.read_only", self.is_read_only)
        config_manager.save_config()

        # 根据只读模式状态设置文本编辑区域
        if self.is_read_only:
            # 设置为只读模式
            self.text_area.configure(state="disabled")
            self.status_bar.show_notification("已切换到只读模式")
            # 更新工具栏按钮外观
            self.toolbar.readonly_button.configure(
                fg_color="#FF6B6B", hover_color="#FF5252"
            )
        else:
            # 设置为编辑模式
            self.text_area.configure(state="normal")
            self.status_bar.show_notification("已切换到编辑模式")
            # 恢复工具栏按钮默认外观
            from customtkinter import ThemeManager

            default_fg_color = ThemeManager.theme["CTkButton"]["fg_color"]
            default_hover_color = ThemeManager.theme["CTkButton"]["hover_color"]
            self.toolbar.readonly_button.configure(
                fg_color=default_fg_color, hover_color=default_hover_color
            )

    def open_containing_folder(self):
        """打开当前文件所在的文件夹"""
        if self.current_file_path:
            try:
                # 获取文件所在的目录
                directory = os.path.dirname(self.current_file_path)
                if os.path.exists(directory):
                    # 在Windows上使用explorer命令打开文件夹
                    os.startfile(directory)
                else:
                    from tkinter import messagebox
                    messagebox.showerror("错误", "文件所在目录不存在")
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("错误", f"无法打开文件所在文件夹: {str(e)}")
        else:
            from tkinter import messagebox
            messagebox.showinfo("提示", "当前没有打开的文件")

    def _stop_auto_save(self):
        """
        停止自动保存功能

        取消现有的自动保存任务（如果有）
        """
        if hasattr(self, "_auto_save_job") and self._auto_save_job is not None:
            self.after_cancel(self._auto_save_job)
            self._auto_save_job = None

    def _start_auto_save(self):
        """
        启动自动保存功能

        创建一个定时任务，根据设定的间隔时间自动保存文件内容
        """
        # 先停止现有的自动保存任务
        self._stop_auto_save()

        # 立即执行一次自动保存，所有检查逻辑都在_auto_save方法内部
        self._auto_save()

    def _auto_save(self):
        """
        执行自动保存操作

        集中处理所有自动保存相关的检查逻辑：
        1. 检查是否启用了自动保存功能
        2. 检查文件是否已修改
        3. 检查是否有文件路径
        4. 如果满足条件，则保存文件并更新状态
        5. 无论是否保存，都调度下一次自动保存
        """
        #  检查是否启用了自动保存功能
        if not self.auto_save_enabled:
            return
        
        # 检查文件是否已修改且持有文件路径
        if  self.is_modified and self.current_file_path:
            # 执行保存操作
            self.save_file()
            # 更新上次自动保存时间
            self.last_auto_save_time = time.time()
            # 更新状态栏的自动保存信息，显示具体的保存时间
            self.status_bar.show_auto_save_status(file_modified=True)
        else:
            # 文件未修改、没有文件路径，仅更新状态栏显示上次执行时间
            self.status_bar.show_auto_save_status(file_modified=False)

        # 调度下一次自动保存
        self._auto_save_job = self.after(
            self.auto_save_interval * 1000, self._auto_save
        )

    def get_char_count(self):
        """
        获取文本区域的字符数，使用缓存机制提高性能
        
        Returns:
            int: 文本区域的字符数
        """
        return self._total_chars
    
    def update_char_count(self):
        """
        更新缓存的字符数
        
        在文件内容发生变化时调用此方法
        """
        # 使用end-1c获取文本，这会自动排除末尾的换行符
        self._total_chars = len(self.text_area.get("1.0", "end-1c"))

    def run(self):
        """运行应用"""
        self.mainloop()
