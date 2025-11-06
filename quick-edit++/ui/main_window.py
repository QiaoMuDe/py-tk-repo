#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主窗口界面模块
"""

import customtkinter as ctk
from .toolbar import Toolbar
from .menu import create_menu
from .status_bar import StatusBar


class MainWindow(ctk.CTk):
    """主窗口类"""
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        # 设置窗口标题
        self.title("QuickEdit++")
        
        # 设置窗口大小
        self.geometry("1200x800")
        
        # 设置最小窗口大小
        self.minsize(800, 600)
        
        # 创建UI组件
        self._create_widgets()
        
        # 创建菜单栏
        self.menu_bar = create_menu(self)
        
        # 设置窗口关闭事件
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # 绑定文本区域事件
        self._bind_text_events()
        
    def _create_widgets(self):
        """创建主窗口中的各个组件"""
        # 创建主框架
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 创建工具栏
        self.toolbar = Toolbar(self.main_frame)
        self.toolbar.pack(side="top", fill="x", padx=5, pady=(5, 0))
        
        # 创建文本编辑区域框架
        self.text_frame = ctk.CTkFrame(self.main_frame)
        self.text_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 创建行号显示区域框架
        self.line_numbers_frame = ctk.CTkFrame(self.text_frame, width=50)
        self.line_numbers_frame.pack(side="left", fill="y", padx=(5, 0), pady=5)
        
        # 创建行号显示区域 (使用Canvas实现)
        self.line_numbers_canvas = ctk.CTkCanvas(
            self.line_numbers_frame,
            width=50,
            bg="white",
            highlightthickness=0
        )
        self.line_numbers_canvas.pack(fill="both", expand=True, padx=0, pady=0)
        
        # 初始化行号显示 (静态显示前50行)
        self._init_static_line_numbers()
        
        # 创建文本编辑区域
        self.text_area = ctk.CTkTextbox(
            self.text_frame,
            wrap="none",
            undo=True
        )
        self.text_area.pack(side="right", fill="both", expand=True, padx=(0, 5), pady=5)
        
    def _bind_text_events(self):
        """绑定文本区域事件"""
        # 绑定按键事件
        self.text_area.bind("<KeyRelease>", self._on_text_change)
        self.text_area.bind("<Button-1>", self._on_cursor_move)
        self.text_area.bind("<<Selection>>", self._on_selection_change)
        
        # 绑定鼠标滚轮事件
        self.text_area.bind("<MouseWheel>", self._on_cursor_move)
        
    def _on_text_change(self, event=None):
        """文本改变事件处理"""
        self._update_status_bar()
        
    def _on_cursor_move(self, event=None):
        """光标移动事件处理"""
        self._update_status_bar()
        
    def _on_selection_change(self, event=None):
        """选择内容改变事件处理"""
        self._update_status_bar()
        
    def _update_status_bar(self):
        """更新状态栏信息"""
        # 获取光标位置
        cursor_pos = self.text_area.index(ctk.INSERT)
        row, col = cursor_pos.split('.')
        row, col = int(row), int(col) + 1  # 转换为1基索引
        
        # 获取总字符数
        content = self.text_area.get("1.0", ctk.END)
        total_chars = len(content) - 1  # 减去末尾的换行符
        
        # 获取选中字符数
        try:
            selected_content = self.text_area.get(ctk.SEL_FIRST, ctk.SEL_LAST)
            selected_chars = len(selected_content)
            
            # 计算选中的行数
            selected_lines = selected_content.count('\n') + 1
        except ctk.TclError:
            # 没有选中内容
            selected_chars = None
            selected_lines = None
        
        # 更新状态栏
        if hasattr(self, 'status_bar'):
            self.status_bar.set_status_info(
                row=row, 
                col=col, 
                total_chars=total_chars, 
                selected_chars=selected_chars, 
                selected_lines=selected_lines
            )
        
    def _init_static_line_numbers(self):
        """初始化静态行号显示 (显示前50行)"""
        # 清除画布上的所有内容
        self.line_numbers_canvas.delete("all")
        
        # 获取画布尺寸
        canvas_width = self.line_numbers_canvas.winfo_reqwidth()
        canvas_height = self.line_numbers_canvas.winfo_reqheight()
        
        # 设置字体和行高，与文本框保持一致
        font = ("Consolas", 12)
        line_height = 20  # 与文本框行高保持一致
        
        # 计算可显示的行数
        max_lines = min(50, canvas_height // line_height)
        
        # 绘制行号，确保与文本框每行对齐
        for i in range(1, max_lines + 1):
            # 调整y坐标以确保行号与文本行对齐
            y_pos = (i - 1) * line_height + line_height - 4  # 减去4像素以更好地垂直对齐
            self.line_numbers_canvas.create_text(
                canvas_width - 10,  # 右对齐，距离右边10像素
                y_pos,
                text=str(i),
                fill="gray",
                font=font,
                anchor="e"  # 右对齐
            )
            
        # 绘制分隔线
        self.line_numbers_canvas.create_line(
            canvas_width - 1, 0,
            canvas_width - 1, canvas_height,
            fill="#cccccc"
        )
        
    def _on_closing(self):
        """窗口关闭事件处理"""
        # 这里可以添加保存确认等逻辑
        self.destroy()
        
    def run(self):
        """运行主窗口"""
        self.mainloop()