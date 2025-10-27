import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, font
import os
import sys
import json
import chardet
import tkinterdnd2
import re
import threading
import queue
from idlelib.colorizer import ColorDelegator
from idlelib.percolator import Percolator

# 导入我们创建的模块
from find_dialog import FindDialog
from theme_manager import ThemeManager
from utils import format_file_size, center_window

# 文件大小限制
MaxFileSize = 1024 * 1024 * 10

# 主窗口-高
MainWindowHeight = 800

# 主窗口-宽
MainWindowWidth = 900

# 限制撤销操作数量
MaxUndo = 20


class AdvancedTextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("文本编辑器")
        self.root.geometry(f"{MainWindowWidth}x{MainWindowHeight}")
        center_window(self.root, MainWindowWidth, MainWindowHeight)

        # 初始化变量
        self.current_file = None  # 当前打开的文件路径
        self.font_family = "Arial"  # 默认字体
        self.font_size = 12  # 默认字体大小
        self.font_bold = False  # 默认不加粗
        self.font_italic = False  # 默认不斜体
        self.font_underline = False  # 默认无下划线
        self.toolbar_visible = True  # 工具栏默认显示
        self.show_line_numbers = True  # 行号显示状态, 默认显示
        self.encoding = "UTF-8"  # 默认编码
        self.line_ending = "LF"  # 默认换行符
        self.readonly_mode = False  # 只读模式, 默认关闭
        self.current_theme = "light"  # 默认主题

        # 加载配置文件
        self.load_config()

        # 创建主框架
        self.create_widgets()

        # 初始化主题管理器
        self.theme_manager = ThemeManager(self)

        self.create_menu()
        # 创建工具栏
        self.create_toolbar()

        # 根据配置应用工具栏显示状态
        if not self.toolbar_visible and hasattr(self, "toolbar"):
            self.toolbar.pack_forget()

        # 设置窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 创建状态栏
        self.create_statusbar()

        # 应用当前主题 (在创建所有UI组件后应用)
        self.theme_manager.set_theme(self.current_theme)

        # 绑定快捷键
        self.bind_shortcuts()

        # 启用拖拽支持
        self.enable_drag_and_drop()

        # 初始化语法高亮器
        self.color_delegator = ColorDelegator()
        # 自定义标签定义，采用Monokai Dimmed配色方案
        self.color_delegator.tagdefs['COMMENT'] = {'foreground': '#999999'}     # 灰色注释 (Monokai Dimmed风格)
        self.color_delegator.tagdefs['KEYWORD'] = {'foreground': '#AE81FF'}     # 紫色关键字 (Monokai Dimmed风格)
        self.color_delegator.tagdefs['BUILTIN'] = {'foreground': '#F92672'}     # 粉红色内置函数 (Monokai Dimmed风格)
        self.color_delegator.tagdefs['STRING'] = {'foreground': '#A6E22E'}      # 绿色字符串 (Monokai Dimmed风格)
        self.color_delegator.tagdefs['DEFINITION'] = {'foreground': '#F92672'}  # 粉红色内置函数 (Monokai Dimmed风格)
        self.color_delegator.tagdefs['SYNC'] = {'foreground': '#CCCCCC'}        # 浅灰色同步标记 (Monokai Dimmed风格)
        self.color_delegator.tagdefs['TODO'] = {'foreground': '#FD971F'}        # 橙黄色待办事项 (Monokai Dimmed风格)
        self.color_delegator.tagdefs['ERROR'] = {'foreground': '#F92672'}       # 粉红色错误标记 (Monokai Dimmed风格)
        self.color_delegator.tagdefs['hit'] = {'foreground': '#66D9EF'}         # 天蓝色匹配标记 (Monokai Dimmed风格)
        self.percolator = Percolator(self.text_area)

    def apply_syntax_highlighting(self):
        """应用语法高亮"""
        try:
            # 移除现有的语法高亮
            self.remove_syntax_highlighting()

            # 应用idlelib语法高亮
            self.percolator.insertfilter(self.color_delegator)
        except Exception as e:
            # 捕获所有异常并显示警告但不中断程序
            messagebox.showwarning("语法高亮警告", f"无法应用语法高亮: {str(e)}")

    def remove_syntax_highlighting(self):
        """移除语法高亮"""
        try:
            # 安全地移除idlelib语法高亮
            if (hasattr(self, "percolator") and 
                hasattr(self, "color_delegator") and 
                hasattr(self, "text_area") and 
                self.text_area.winfo_exists()):
                # 检查过滤器是否已应用
                if self.color_delegator in self.percolator.filters:
                    self.percolator.removefilter(self.color_delegator)
        except Exception as e:
            # 捕获所有异常但不中断程序
            # 在打开新文件或拖拽文件等操作中可能会出现临时性的状态不一致
            # 这种情况下的错误可以忽略，避免干扰用户体验
            pass

    def check_unsaved_changes(self):
        """检查是否有未保存的更改"""
        # 检查文本框是否有内容
        content = self.text_area.get(1.0, tk.END).strip()

        # 情况1: 如果有打开的文件
        if self.current_file:
            # 情况1a: 打开文件且已被修改
            if content and self.text_area.edit_modified():
                result = messagebox.askyesnocancel(
                    "保存确认", "文档已被修改, 是否保存更改？"
                )
                if result is True:  # 是, 保存
                    self.save_file()
                    return True  # 继续操作
                elif result is False:  # 否, 不保存
                    return True  # 继续操作
                else:  # 取消
                    return False  # 取消操作
            else:
                # 情况1b: 打开文件但未被修改
                return True  # 继续操作
        else:
            # 情况2: 没有打开文件 (新建文件或直接输入内容)
            if content:
                # 情况2a: 有内容
                result = messagebox.askyesnocancel("保存确认", "文档有内容, 是否保存？")
                if result is True:  # 是, 保存
                    self.save_file()
                    return True  # 继续操作
                elif result is False:  # 否, 不保存
                    return True  # 继续操作
                else:  # 取消
                    return False  # 取消操作
            else:
                # 情况2b: 没有内容
                return True  # 继续操作

    def on_closing(self):
        """处理窗口关闭事件"""
        # 检查文本框是否有内容
        content = self.text_area.get(1.0, tk.END).strip()

        # 情况1: 如果有打开的文件
        if self.current_file:
            # 情况1a: 打开文件且已被修改, 询问用户是否保存
            if content and self.text_area.edit_modified():
                result = messagebox.askyesnocancel(
                    "退出确认", "文档已被修改, 是否保存后再退出？"
                )
                if result is True:  # 是, 保存并退出
                    self.save_file()
                    # 保存后检查窗口是否仍然存在再决定是否销毁
                    if self.root.winfo_exists():
                        self.root.destroy()
                elif result is False:  # 否, 直接退出
                    self.root.destroy()
                # 如果点击取消, 则不执行任何操作, 继续留在编辑器中
            else:
                # 情况1b: 打开文件但未被修改, 直接退出
                self.root.destroy()
        else:
            # 情况2: 没有打开文件 (新建文件或直接输入内容)
            if content:
                # 情况2a: 有内容, 询问用户是否保存
                result = messagebox.askyesnocancel(
                    "退出确认", "文档有内容, 是否保存后再退出？"
                )
                if result is True:  # 是, 保存并退出
                    self.save_file()
                    # 保存后检查窗口是否仍然存在再决定是否销毁
                    if self.root.winfo_exists():
                        self.root.destroy()
                elif result is False:  # 否, 直接退出
                    self.root.destroy()
                # 如果点击取消, 则不执行任何操作, 继续留在编辑器中
            else:
                # 情况2b: 没有内容, 直接退出
                self.root.destroy()

    def create_widgets(self):
        """创建主要控件"""
        # 创建包含行号和文本区域的框架
        self.text_frame = tk.Frame(self.root)
        self.text_frame.pack(fill=tk.BOTH, expand=True)

        # 创建行号显示区域
        self.line_numbers = tk.Canvas(
            self.text_frame, width=60, bg="#f0f0f0", highlightthickness=0
        )
        # 根据配置决定是否显示行号
        if self.show_line_numbers:
            self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # 创建文本区域和滚动条的容器
        text_container = tk.Frame(self.text_frame)
        text_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 创建垂直滚动条
        self.scrollbar = tk.Scrollbar(text_container, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 创建文本区域
        self.text_area = tk.Text(
            text_container,
            wrap=tk.WORD,
            undo=True,
            yscrollcommand=self.on_text_scroll_with_line_numbers,
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)

        # 将滚动条与文本区域关联
        self.scrollbar.config(command=self.on_text_scroll)

        # 绑定滚动事件
        self.text_area.bind("<MouseWheel>", self.on_mouse_wheel)
        self.text_area.bind("<Key>", self.on_key_press)
        self.text_area.bind("<Button-4>", self.on_mouse_wheel)  # Linux鼠标滚轮支持
        self.text_area.bind("<Button-5>", self.on_mouse_wheel)  # Linux鼠标滚轮支持
        self.text_area.bind(
            "<ButtonRelease>", self.update_line_numbers
        )  # 鼠标释放时更新行号

        # 绑定文本变化事件, 用于更新行号
        self.text_area.bind("<KeyRelease>", self.update_line_numbers)
        self.text_area.bind("<<Modified>>", self.update_line_numbers)

        # 绑定窗口配置事件, 用于在窗口大小改变时更新行号
        self.root.bind("<Configure>", self.on_window_configure)

        # 设置默认字体
        self.update_font()

        # 初始化文件相关变量
        self.total_lines = 0

        # 性能优化配置
        self.text_area.config(
            background="white",
            foreground="black",
            insertbackground="black",
            selectbackground="lightblue",
            selectforeground="black",
            maxundo=MaxUndo,
        )

        # 设置行号区域样式
        self.line_numbers.config(bg="#f0f0f0", highlightthickness=0)

    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)

        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="新建", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(
            label="打开", command=self.open_file, accelerator="Ctrl+O"
        )
        file_menu.add_command(
            label="保存", command=self.save_file, accelerator="Ctrl+S"
        )
        file_menu.add_command(
            label="另存为", command=self.save_as_file, accelerator="Ctrl+Shift+S"
        )
        file_menu.add_command(
            label="关闭文件", command=self.close_file, accelerator="Ctrl+W"
        )
        file_menu.add_separator()
        # 添加编码选择子菜单
        encoding_submenu = tk.Menu(file_menu, tearoff=0)
        encodings = ["UTF-8", "UTF-16", "GBK", "GB2312", "ASCII", "ISO-8859-1"]
        for enc in encodings:
            encoding_submenu.add_command(
                label=enc, command=lambda e=enc: self.change_encoding(e)
            )
        file_menu.add_cascade(label="编码", menu=encoding_submenu)
        # 添加换行符选择子菜单
        line_ending_submenu = tk.Menu(file_menu, tearoff=0)
        line_endings = [
            ("Linux (LF)", "LF"),
            ("Windows (CRLF)", "CRLF"),
            ("Mac (CR)", "CR"),
        ]
        for label, ending in line_endings:
            line_ending_submenu.add_command(
                label=label, command=lambda e=ending: self.set_line_ending(e)
            )
        file_menu.add_cascade(label="换行符", menu=line_ending_submenu)
        file_menu.add_separator()
        self.readonly_var = tk.BooleanVar(value=self.readonly_mode)
        file_menu.add_checkbutton(
            label="只读模式",
            command=self.toggle_readonly_mode,
            variable=self.readonly_var,
            accelerator="Ctrl+R",
        )
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.exit_app, accelerator="Ctrl+Q")
        menubar.add_cascade(label="文件", menu=file_menu)

        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(
            label="撤销", command=self.text_area.edit_undo, accelerator="Ctrl+Z"
        )
        edit_menu.add_command(
            label="重做", command=self.text_area.edit_redo, accelerator="Ctrl+Y"
        )
        edit_menu.add_separator()
        edit_menu.add_command(
            label="复制", command=self.copy_text, accelerator="Ctrl+C"
        )
        edit_menu.add_command(label="剪切", command=self.cut_text, accelerator="Ctrl+X")
        edit_menu.add_command(
            label="粘贴", command=self.paste_text, accelerator="Ctrl+V"
        )
        edit_menu.add_separator()
        edit_menu.add_command(
            label="全选", command=self.select_all, accelerator="Ctrl+A"
        )
        edit_menu.add_separator()
        edit_menu.add_command(
            label="查找", command=self.show_find_dialog, accelerator="Ctrl+F"
        )
        edit_menu.add_command(
            label="替换", command=self.replace_text, accelerator="Ctrl+H"
        )
        edit_menu.add_separator()
        edit_menu.add_command(
            label="转到文件顶部", command=self.go_to_home, accelerator="Ctrl+Home"
        )
        edit_menu.add_command(
            label="转到文件底部", command=self.go_to_end, accelerator="Ctrl+End"
        )
        edit_menu.add_command(
            label="转到行", command=self.go_to_line, accelerator="Ctrl+G"
        )
        menubar.add_cascade(label="编辑", menu=edit_menu)

        # 主题菜单
        theme_menu = tk.Menu(menubar, tearoff=0)
        theme_menu.add_command(label="字体", command=self.choose_font)
        theme_menu.add_command(label="字体大小", command=self.choose_font_size)
        theme_menu.add_separator()
        theme_menu.add_checkbutton(
            label="粗体",
            command=self.toggle_bold,
            variable=tk.BooleanVar(value=self.font_bold),
        )
        theme_menu.add_checkbutton(
            label="斜体",
            command=self.toggle_italic,
            variable=tk.BooleanVar(value=self.font_italic),
        )
        theme_menu.add_checkbutton(
            label="下划线",
            command=self.toggle_underline,
            variable=tk.BooleanVar(value=self.font_underline),
        )
        # 主题选择子菜单
        theme_submenu = tk.Menu(theme_menu, tearoff=0)
        themes = [
            ("浅色主题", "light"),
            ("深色主题", "dark"),
            ("蓝色主题", "blue"),
            ("羊皮卷风格", "parchment"),
            ("经典绿色", "green"),
            ("午夜紫", "midnight_purple"),
            ("日落橙", "sunset"),
        ]
        for label, theme_name in themes:
            theme_submenu.add_command(
                label=label, command=lambda t=theme_name: self.change_theme(t)
            )
        theme_menu.add_cascade(label="主题", menu=theme_submenu)
        menubar.add_cascade(label="主题", menu=theme_menu)

        # 设置菜单
        settings_menu = tk.Menu(menubar, tearoff=0)
        self.toolbar_var = tk.BooleanVar(value=self.toolbar_visible)
        settings_menu.add_checkbutton(
            label="显示工具栏", command=self.toggle_toolbar, variable=self.toolbar_var
        )
        # 行号显示选项
        self.show_line_numbers_var = tk.BooleanVar(value=self.show_line_numbers)
        settings_menu.add_checkbutton(
            label="显示行号",
            command=self.toggle_line_numbers,
            variable=self.show_line_numbers_var,
        )
        menubar.add_cascade(label="设置", menu=settings_menu)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self.show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)

        self.root.config(menu=menubar)

    def toggle_line_numbers(self):
        """切换行号显示"""
        if self.show_line_numbers_var.get():
            # 开启行号时, 下次打开文件时将显示行号
            self.show_line_numbers = True
            # 提示用户下次打开文件时将显示行号
            self.left_status.config(text="行号显示已开启, 下次打开文件时将显示行号")
        else:
            # 隐藏行号时, 取消打包
            self.line_numbers.pack_forget()
            self.show_line_numbers = False
            # 提示用户下次打开文件时将隐藏行号
            self.left_status.config(text="行号显示已关闭, 下次打开文件时将隐藏行号")

        # 保存行号显示状态到配置文件
        self.save_config()

    def change_theme(self, theme_name):
        """切换主题"""
        # 设置主题
        self.theme_manager.set_theme(theme_name)
        # 更新当前主题
        self.current_theme = theme_name
        # 保存主题配置
        self.save_config()

    def on_text_scroll(self, *args):
        """处理文本区域滚动事件"""
        # 调用原始滚动方法
        self.text_area.yview(*args)

    def on_text_scroll_with_line_numbers(self, *args):
        """处理文本区域滚动事件并同步更新行号显示"""
        # 调用原始滚动方法
        try:
            self.text_area.yview(*args)
        except tk.TclError:
            # 忽略无效的滚动参数
            pass
        # 更新行号显示
        self.update_line_numbers()

    def on_mouse_wheel(self, event):
        """处理鼠标滚轮事件"""
        # 处理鼠标滚轮滚动
        if event.delta > 0:
            self.text_area.yview_scroll(-1, "units")
        else:
            self.text_area.yview_scroll(1, "units")
        # 更新行号显示
        self.update_line_numbers()
        return "break"

    def on_key_press(self, event):
        """处理键盘按键事件"""
        # 在适当的时候更新行号显示
        self.root.after(10, self.update_line_numbers)
        return None

    def on_window_configure(self, event):
        """处理窗口配置事件 (大小调整等)"""
        # 只有当事件源是主窗口时才更新行号显示
        if event.widget == self.root:
            # 延迟更新行号显示, 避免频繁触发
            self.root.after(50, self.update_line_numbers)

    def update_line_numbers(self, event=None):
        """更新行号显示"""
        # 清除之前的行号
        self.line_numbers.delete("all")

        # 获取文本区域的行数
        try:
            # 获取总行数 (使用end-1c来正确获取最后一行)
            last_line = self.text_area.index("end-1c").split(".")[0]
            total_lines = int(last_line)

            # 获取可见区域的第一行和最后一行
            first_visible = int(self.text_area.index("@0,0").split(".")[0])
            last_visible = int(
                self.text_area.index(f"@0,{self.text_area.winfo_height()}").split(".")[
                    0
                ]
            )

            # 确保范围有效
            first_visible = max(1, first_visible)
            last_visible = min(total_lines, last_visible + 1)

            # 计算行号区域宽度 (根据行号位数动态调整宽度)
            max_line_number = total_lines
            # 根据行号位数计算宽度：增加每数字宽度和额外空间确保行号能完整显示
            digits = len(str(max_line_number))
            line_number_width = max(40, digits * 13 + 10)
            self.line_numbers.config(width=line_number_width)

            # 设置字体
            font = (self.font_family, self.font_size)

            # 绘制可见区域的行号
            for i in range(first_visible, last_visible + 1):
                # 计算行号的y坐标
                # 使用dlineinfo方法获取更准确的行位置信息
                dlineinfo = self.text_area.dlineinfo(f"{i}.0")
                if dlineinfo:
                    y_pos = dlineinfo[1]  # y坐标
                    line_height = dlineinfo[3]  # 行高
                    # 在行号区域绘制行号
                    self.line_numbers.create_text(
                        line_number_width - 5,
                        y_pos + line_height // 2,  # x, y坐标
                        text=str(i),
                        font=font,
                        fill="gray",
                        anchor="e",  # 右对齐
                    )
                else:
                    # 如果dlineinfo不可用, 使用替代方法计算位置
                    # 这种情况在某些特殊情况下可能会发生
                    pass
        except Exception as e:
            # 忽略错误, 保持程序稳定
            print(f"Error in update_line_numbers: {e}")
            pass

    def create_toolbar(self):
        """创建工具栏"""
        # 如果已经有工具栏, 先销毁
        if hasattr(self, "toolbar"):
            self.toolbar.destroy()

        self.toolbar = ttk.Frame(self.root)
        self.toolbar.pack(fill=tk.X, before=self.text_frame)

        # 创建按钮列表以便后续更新样式
        self.toolbar_buttons = []

        # 文件操作按钮
        new_btn = ttk.Button(self.toolbar, text="新建", command=self.new_file)
        new_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(new_btn)

        open_btn = ttk.Button(self.toolbar, text="打开", command=self.open_file)
        open_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(open_btn)

        save_btn = ttk.Button(self.toolbar, text="保存", command=self.save_file)
        save_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(save_btn)

        save_as_btn = ttk.Button(self.toolbar, text="另存为", command=self.save_as_file)
        save_as_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(save_as_btn)

        # 只读模式切换按钮
        readonly_btn = ttk.Button(
            self.toolbar, text="只读模式", command=self.toggle_readonly_mode
        )
        readonly_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(readonly_btn)

        # 关闭文件按钮
        close_file_btn = ttk.Button(
            self.toolbar, text="关闭文件", command=self.close_file
        )
        close_file_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(close_file_btn)

        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=4
        )

        # 查找和替换按钮
        find_replace_btn = ttk.Button(
            self.toolbar, text="查找和替换", command=self.show_find_dialog
        )
        find_replace_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(find_replace_btn)

        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=4
        )

        # 编辑操作按钮
        undo_btn = ttk.Button(
            self.toolbar, text="撤销", command=self.text_area.edit_undo
        )
        undo_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(undo_btn)

        redo_btn = ttk.Button(
            self.toolbar, text="重做", command=self.text_area.edit_redo
        )
        redo_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(redo_btn)

        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=4
        )

        cut_btn = ttk.Button(self.toolbar, text="剪切", command=self.cut_text)
        cut_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(cut_btn)

        copy_btn = ttk.Button(self.toolbar, text="复制", command=self.copy_text)
        copy_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(copy_btn)

        paste_btn = ttk.Button(self.toolbar, text="粘贴", command=self.paste_text)
        paste_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(paste_btn)

        # 应用当前主题到工具栏按钮
        self.theme_manager.apply_theme()

    def create_statusbar(self):
        """创建状态栏"""
        # 获取当前主题配置
        theme = self.theme_manager.get_current_theme()

        # 创建状态栏框架, 使用主题背景色
        self.statusbar_frame = tk.Frame(
            self.root, relief=tk.SUNKEN, bd=1, bg=theme["statusbar_bg"]
        )
        self.statusbar_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # 左侧状态信息, 使用主题背景色和前景色
        self.left_status = tk.Label(
            self.statusbar_frame,
            text="就绪 - 第1行, 第1列",
            anchor=tk.W,
            bg=theme["statusbar_bg"],
            fg=theme["statusbar_fg"],
        )
        self.left_status.pack(side=tk.LEFT, padx=5)

        # 右侧状态信息 (编码和换行符类型), 使用主题背景色和前景色
        self.right_status = tk.Label(
            self.statusbar_frame,
            text="UTF-8 | LF",
            anchor=tk.E,
            cursor="hand2",
            bg=theme["statusbar_bg"],
            fg=theme["statusbar_fg"],
        )
        self.right_status.pack(side=tk.RIGHT, padx=5)

        # 为状态栏绑定右键点击事件到智能菜单处理函数
        self.right_status.bind("<Button-3>", self.on_statusbar_right_click)

        # 绑定光标移动事件更新状态栏
        self.text_area.bind("<<Modified>>", self.update_statusbar)
        self.text_area.bind("<KeyRelease>", self.update_statusbar)
        self.text_area.bind("<ButtonRelease>", self.update_statusbar)
        # 绑定选中事件
        self.text_area.bind("<<Selection>>", self.update_statusbar)

    def bind_shortcuts(self):
        """绑定快捷键"""
        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-S>", lambda e: self.save_as_file())
        self.root.bind("<Control-w>", lambda e: self.close_file())
        self.root.bind("<Control-q>", lambda e: self.exit_app())
        self.root.bind("<Control-a>", lambda e: self.select_all())
        self.root.bind("<Control-f>", lambda e: self.show_find_dialog())
        self.root.bind("<Control-h>", lambda e: self.replace_text())
        self.root.bind("<Control-Home>", lambda e: self.go_to_home())
        self.root.bind("<Control-End>", lambda e: self.go_to_end())
        self.root.bind("<Control-r>", lambda e: self.toggle_readonly_mode())
        self.root.bind("<Control-g>", lambda e: self.go_to_line())

    def load_config(self):
        """加载配置文件"""
        config_file = os.path.join(os.path.expanduser("~"), ".quick_edit_config")
        if os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.font_family = config.get("font_family", "Arial")
                    self.font_size = config.get("font_size", 12)
                    self.font_bold = config.get("font_bold", False)
                    self.font_italic = config.get("font_italic", False)
                    self.font_underline = config.get("font_underline", False)
                    self.toolbar_visible = config.get("toolbar_visible", True)
                    # 加载行号显示状态
                    self.show_line_numbers = config.get("show_line_numbers", True)
                    # 加载主题配置
                    self.current_theme = config.get("current_theme", "light")

            except Exception as e:
                print(f"加载配置文件时出错: {e}")

    def save_config(self):
        """保存配置文件"""
        config = {
            "font_family": self.font_family,
            "font_size": self.font_size,
            "font_bold": self.font_bold,
            "font_italic": self.font_italic,
            "font_underline": self.font_underline,
            "toolbar_visible": self.toolbar_visible,
            "show_line_numbers": self.show_line_numbers,
            "current_theme": self.current_theme,
        }

        config_file = os.path.join(os.path.expanduser("~"), ".quick_edit_config")
        try:
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存配置文件时出错: {e}")

    def update_font(self):
        """更新字体设置"""
        font_style = "normal"
        if self.font_bold and self.font_italic:
            font_style = "bold italic"
        elif self.font_bold:
            font_style = "bold"
        elif self.font_italic:
            font_style = "italic"

        font = (self.font_family, self.font_size, font_style)

        # 为选中文本应用格式, 或者设置全局字体
        try:
            self.text_area.tag_add("font", "sel.first", "sel.last")
            self.text_area.tag_configure(
                "font", font=font, underline=self.font_underline
            )
        except:
            # 如果没有选中文本, 设置全局字体
            self.text_area.config(font=font)

        # 更新行号显示
        self.update_line_numbers()

    def update_statusbar(self, event=None):
        """更新状态栏信息"""
        try:
            # 获取光标位置
            cursor_pos = self.text_area.index(tk.INSERT)
            row, col = cursor_pos.split(".")

            # 获取总字符数
            char_count = len(self.text_area.get("1.0", tk.END + "-1c"))

            # 检查是否有选中文本
            try:
                selected_text = self.text_area.selection_get()
                selected = True
                selected_char_count = len(selected_text)
                # 计算选中的行数
                selected_lines = selected_text.count("\n") + 1
            except tk.TclError:
                selected = False
                selected_char_count = 0
                selected_lines = 0

            # 构建左侧状态信息
            if self.readonly_mode:
                status_prefix = "[只读模式] "
            else:
                status_prefix = ""

            if self.text_area.edit_modified():
                if selected:
                    status_text = f"{status_prefix}已修改 - 第{row}行, 第{col}列 | {char_count}个字符 | 已选择{selected_char_count}个字符({selected_lines}行)"
                else:
                    status_text = f"{status_prefix}已修改 - 第{row}行, 第{col}列 | {char_count}个字符"
            else:
                if selected:
                    status_text = f"{status_prefix}就绪 - 第{row}行, 第{col}列 | {char_count}个字符 | 已选择{selected_char_count}个字符({selected_lines}行)"
                else:
                    status_text = f"{status_prefix}就绪 - 第{row}行, 第{col}列 | {char_count}个字符"

            self.left_status.config(text=status_text)

            # 更新右侧状态信息 (编码和换行符类型)
            if hasattr(self, "encoding") and hasattr(self, "line_ending"):
                file_info = f"{self.encoding} | {self.line_ending}"
                if self.current_file:
                    file_name = os.path.basename(self.current_file)
                    right_text = f"{file_name} - {file_info}"
                else:
                    right_text = file_info
                self.right_status.config(text=right_text)

            # 更新行号显示
            self.update_line_numbers()

        except Exception as e:
            self.left_status.config(text="状态更新错误")

    def on_line_ending_click(self, event=None):
        """处理换行符类型标签左键点击事件"""
        # 在三种换行符格式之间循环切换
        new_ending = self.cycle_line_ending()

        # 显示提示信息
        messagebox.showinfo("换行符切换", f"换行符格式已切换为: {new_ending}")

    def on_line_ending_right_click(self, event=None):
        """处理换行符类型标签右键点击事件"""
        # 创建换行符选择菜单
        line_ending_menu = tk.Menu(self.root, tearoff=0)

        # 换行符选项
        line_endings = ["LF", "CRLF", "CR"]
        line_ending_names = {
            "LF": "Unix/Linux (LF)",
            "CRLF": "Windows (CRLF)",
            "CR": "Mac (CR)",
        }

        # 添加换行符选项到菜单
        for ending in line_endings:
            display_name = line_ending_names.get(ending, ending)
            line_ending_menu.add_command(
                label=display_name, command=lambda e=ending: self.set_line_ending(e)
            )

        # 显示菜单
        try:
            line_ending_menu.tk_popup(event.x_root, event.y_root)
        finally:
            line_ending_menu.grab_release()

    def on_statusbar_right_click(self, event=None):
        """处理状态栏右键点击事件，根据点击位置判断是编码部分还是换行符部分"""
        # 获取点击位置相对于标签的坐标
        x = event.x

        # 获取当前显示的文本
        current_text = self.right_status.cget("text")

        # 判断点击位置是在编码部分还是换行符部分
        # 文本格式为 "文件名 - 编码 | 换行符" 或 "编码 | 换行符"
        if " | " in current_text:
            # 找到分隔符的位置
            separator_pos = current_text.find(" | ")

            # 计算编码部分和换行符部分的大致宽度比例
            # 这是一个简化的方法，实际的宽度取决于字体和字符
            encoding_part = current_text[:separator_pos]
            line_ending_part = current_text[separator_pos + 3 :]  # 跳过" | "

            # 估算各部分的宽度比例（这是一个近似值）
            total_length = len(current_text)
            encoding_ratio = (
                len(encoding_part) / total_length if total_length > 0 else 0.5
            )

            # 获取标签的宽度
            width = self.right_status.winfo_width()

            # 根据点击位置决定是编码部分还是换行符部分
            if x < width * encoding_ratio:
                # 点击的是编码部分
                self.on_encoding_click(event)
            else:
                # 点击的是换行符部分
                self.on_line_ending_right_click(event)
        else:
            # 如果没有找到分隔符，默认显示换行符菜单
            self.on_line_ending_right_click(event)

    def go_to_line(self):
        """转到指定行"""
        # 创建对话框
        line_number = simpledialog.askinteger("转到行", "请输入行号:", parent=self.root)

        # 检查用户是否输入了有效的行号
        if line_number is not None and line_number > 0:
            # 获取总行数
            total_lines = int(self.text_area.index("end-1c").split(".")[0])

            # 确保行号不超过总行数
            if line_number > total_lines:
                line_number = total_lines

            # 转到指定行
            self.text_area.mark_set(tk.INSERT, f"{line_number}.0")
            self.text_area.see(f"{line_number}.0")
            self.text_area.focus_set()

    def on_encoding_click(self, event=None):
        """处理编码标签右键点击事件"""
        # 创建编码选择菜单
        encoding_menu = tk.Menu(self.root, tearoff=0)

        # 常用编码选项
        encodings = ["UTF-8", "UTF-16", "GBK", "GB2312", "ASCII", "ISO-8859-1"]

        # 添加编码选项到菜单
        for enc in encodings:
            encoding_menu.add_command(
                label=enc, command=lambda e=enc: self.change_encoding(e)
            )

        # 显示菜单
        try:
            encoding_menu.tk_popup(event.x_root, event.y_root)
        finally:
            encoding_menu.grab_release()

    def change_encoding(self, new_encoding):
        """更改文件编码"""
        old_encoding = self.encoding
        self.encoding = new_encoding

        # 更新状态栏
        self.update_statusbar()

        # 显示提示信息
        messagebox.showinfo(
            "编码切换", f"文件编码已从 {old_encoding} 切换为: {new_encoding}"
        )

    def set_line_ending(self, new_ending):
        """设置换行符类型"""
        old_ending = self.line_ending
        self.line_ending = new_ending

        # 更新状态栏
        self.update_statusbar()

        # 显示提示信息
        ending_names = {
            "LF": "Unix/Linux (LF)",
            "CRLF": "Windows (CRLF)",
            "CR": "Mac (CR)",
        }
        old_name = ending_names.get(old_ending, old_ending)
        new_name = ending_names.get(new_ending, new_ending)
        messagebox.showinfo(
            "换行符切换", f"换行符格式已从 {old_name} 切换为: {new_name}"
        )

    # 文件操作方法
    def close_file(self):
        """关闭当前文件"""
        # 检查是否有未保存的更改
        if not self.check_unsaved_changes():
            return  # 用户取消操作

        # 清空文本区域
        self.text_area.delete(1.0, tk.END)

        # 重置文件状态
        self.current_file = None
        self.root.title("文本编辑器")

        # 重置编码和换行符为默认值
        self.encoding = "UTF-8"
        self.line_ending = "LF"

        # 移除可能存在的语法高亮
        self.remove_syntax_highlighting()

        # 更新状态栏
        self.update_statusbar()

        # 显示提示信息
        messagebox.showinfo("文件关闭", "文件已成功关闭")

    def new_file(self):
        """新建文件"""
        # 检查是否有未保存的更改
        if not self.check_unsaved_changes():
            return  # 用户取消操作

        self.text_area.delete(1.0, tk.END)
        self.current_file = None
        self.root.title("文本编辑器")

        # 重置编码和换行符为默认值
        self.encoding = "UTF-8"
        self.line_ending = "LF"

        # 移除可能存在的语法高亮
        self.remove_syntax_highlighting()

    def detect_file_encoding_and_line_ending(self, file_path):
        """检测文件编码和换行符类型"""
        if not os.path.exists(file_path):
            return "UTF-8", "LF"  # 默认值

        try:
            # 检测编码
            with open(file_path, "rb") as file:
                raw_data = file.read(10000)  # 只读取前10KB用于检测
                if raw_data:
                    result = chardet.detect(raw_data)
                    encoding = result["encoding"] if result["encoding"] else "UTF-8"
                else:
                    encoding = "UTF-8"

            # 检测换行符类型
            with open(file_path, "rb") as file:
                content = file.read(10000)  # 只读取前10KB用于检测
                if b"\r\n" in content:
                    line_ending = "CRLF"
                elif b"\n" in content:
                    line_ending = "LF"
                elif b"\r" in content:
                    line_ending = "CR"
                else:
                    line_ending = "LF"  # 默认

            return encoding, line_ending
        except Exception as e:
            return "UTF-8", "LF"  # 出错时返回默认值

    def convert_line_endings(self, text, target_ending):
        """将文本中的换行符转换为目标格式"""
        # 先统一转换为 \n 格式 (处理混合换行符的情况)
        text = text.replace("\r\n", "\n")  # Windows -> Unix
        text = text.replace("\r", "\n")  # Mac -> Unix

        # 再转换为目标格式
        if target_ending == "CRLF":
            text = text.replace("\n", "\r\n")
        elif target_ending == "CR":
            text = text.replace("\n", "\r")
        # 如果目标是LF, 则无需转换, 因为我们已经统一为LF格式了

        return text

    def cycle_line_ending(self):
        """在三种换行符格式之间循环切换"""
        # 定义切换顺序
        cycle_order = ["LF", "CRLF", "CR"]

        # 获取当前索引
        try:
            current_index = cycle_order.index(self.line_ending)
        except ValueError:
            # 如果当前格式不在列表中, 默认从LF开始
            current_index = 0

        # 计算下一个索引
        next_index = (current_index + 1) % len(cycle_order)
        new_ending = cycle_order[next_index]

        # 更新换行符类型
        self.line_ending = new_ending

        # 更新状态栏显示
        self.update_statusbar()

        # 返回新的换行符类型
        return new_ending

    def open_file(self):
        """打开文件"""
        # 检查是否有未保存的更改
        if not self.check_unsaved_changes():
            return  # 用户取消操作

        file_path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("All Files", "*.*")],
        )

        if file_path:
            try:
                # 检查文件大小
                file_size = os.path.getsize(file_path)
                if file_size > MaxFileSize:
                    formatted_size = format_file_size(file_size)
                    max_size = format_file_size(MaxFileSize)
                    messagebox.showerror(
                        "文件过大",
                        f"无法打开文件: {os.path.basename(file_path)}\n"
                        f"文件大小: {formatted_size}\n"
                        f"超过最大允许大小: {max_size}\n"
                        f"请使用其他专业编辑器打开此文件。",
                    )
                    return

                # 检测文件编码和换行符类型
                self.encoding, self.line_ending = (
                    self.detect_file_encoding_and_line_ending(file_path)
                )

                # 直接读取文件内容 (移除了文件大小判断和分块加载逻辑)
                with open(file_path, "r", encoding=self.encoding) as file:
                    content = file.read()

                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, content)
                # 更新总行数
                self.total_lines = len(content.split("\n"))
                self.current_file = file_path
                self.root.title(f"{os.path.basename(file_path)} - 文本编辑器")
                self.text_area.edit_modified(False)

                # 检查文件扩展名, 如果是Python文件则应用语法高亮
                _, ext = os.path.splitext(file_path)
                if ext.lower() in [".py", ".pyw"]:
                    self.apply_syntax_highlighting()
                else:
                    self.remove_syntax_highlighting()

                # 如果处于只读模式, 设置文本区域为只读
                if self.readonly_mode:
                    self.text_area.config(state=tk.DISABLED)
                else:
                    self.text_area.config(state=tk.NORMAL)

                # 更新状态栏
                self.update_statusbar()
            except Exception as e:
                messagebox.showerror("错误", f"无法打开文件: {str(e)}")

    def save_file(self):
        """保存文件"""
        # 检查是否处于只读模式
        if self.readonly_mode:
            messagebox.showinfo("提示", "当前处于只读模式, 无法保存文件。")
            return

        # 检查文本框是否有内容
        content = self.text_area.get(1.0, tk.END).strip()
        if not content:
            messagebox.showinfo("提示", "文本框中没有内容, 请先输入内容再保存。")
            return

        if self.current_file:
            try:
                # 转换换行符格式
                converted_content = self.convert_line_endings(content, self.line_ending)

                with open(
                    self.current_file, "w", encoding=self.encoding.lower(), newline=""
                ) as file:
                    file.write(converted_content)

                # 在Tkinter事件循环中更新UI, 避免命令冲突
                self.root.after(10, self._post_save_operations, self.current_file)
            except Exception as e:
                messagebox.showerror("错误", f"保存文件时出错: {str(e)}")
        else:
            self.save_as_file()

    def _post_save_operations(self, file_path):
        """保存文件后的操作"""
        try:
            # 更新修改状态
            self.text_area.edit_modified(False)

            # 显示保存成功消息
            messagebox.showinfo(
                "保存成功",
                f"文件已成功保存！\n编码格式: {self.encoding}\n换行符格式: {self.line_ending}",
            )

            # 检查文件扩展名, 如果是Python文件则应用语法高亮
            _, ext = os.path.splitext(file_path)
            if ext.lower() in [".py", ".pyw"]:
                self.apply_syntax_highlighting()
            else:
                self.remove_syntax_highlighting()
        except Exception as e:
            messagebox.showerror("错误", f"保存后处理时出错: {str(e)}")

    def save_as_file(self):
        """另存为文件"""
        # 检查是否处于只读模式
        if self.readonly_mode:
            messagebox.showinfo("提示", "当前处于只读模式, 无法保存文件。")
            return

        # 检查文本框是否有内容
        content = self.text_area.get(1.0, tk.END).strip()
        if not content:
            messagebox.showinfo("提示", "文本框中没有内容, 请先输入内容再保存。")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("All Files", "*.*")],
        )

        if file_path:
            try:
                # 转换换行符格式
                converted_content = self.convert_line_endings(content, self.line_ending)

                with open(
                    file_path, "w", encoding=self.encoding.lower(), newline=""
                ) as file:
                    file.write(converted_content)
                    self.current_file = file_path
                    self.root.title(f"{os.path.basename(file_path)} - 文本编辑器")

                # 在Tkinter事件循环中更新UI, 避免命令冲突
                self.root.after(10, self._post_save_operations, file_path)
            except Exception as e:
                messagebox.showerror("错误", f"保存文件时出错: {str(e)}")

    def exit_app(self):
        """退出应用程序"""
        # 检查文本框是否有内容
        content = self.text_area.get(1.0, tk.END).strip()

        # 情况1: 如果有打开的文件
        if self.current_file:
            # 情况1a: 打开文件且已被修改, 询问用户是否保存
            if content and self.text_area.edit_modified():
                result = messagebox.askyesnocancel(
                    "退出确认", "文档已被修改, 是否保存后再退出？"
                )
                if result is True:  # 是, 保存并退出
                    self.save_file()
                    # 保存后检查窗口是否仍然存在再决定是否销毁
                    if self.root.winfo_exists():
                        self.root.destroy()
                elif result is False:  # 否, 直接退出
                    self.root.destroy()
                # 如果点击取消, 则不执行任何操作, 继续留在编辑器中
            else:
                # 情况1b: 打开文件但未被修改, 直接退出
                self.root.destroy()
        else:
            # 情况2: 没有打开文件 (新建文件或直接输入内容)
            if content:
                # 情况2a: 有内容, 询问用户是否保存
                result = messagebox.askyesnocancel(
                    "退出确认", "文档有内容, 是否保存后再退出？"
                )
                if result is True:  # 是, 保存并退出
                    self.save_file()
                    # 保存后检查窗口是否仍然存在再决定是否销毁
                    if self.root.winfo_exists():
                        self.root.destroy()
                elif result is False:  # 否, 直接退出
                    self.root.destroy()
                # 如果点击取消, 则不执行任何操作, 继续留在编辑器中
            else:
                # 情况2b: 没有内容, 直接退出
                self.root.destroy()

    # 编辑操作方法
    def copy_text(self):
        """复制文本"""
        self.text_area.clipboard_clear()
        self.text_area.clipboard_append(self.text_area.selection_get())

    def cut_text(self):
        """剪切文本"""
        self.copy_text()
        self.text_area.delete("sel.first", "sel.last")

    def paste_text(self):
        """粘贴文本"""
        self.text_area.insert(tk.INSERT, self.text_area.clipboard_get())

    def select_all(self):
        """全选文本"""
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, "1.0")
        self.text_area.see(tk.INSERT)

    def find_text(self):
        """查找文本"""
        find_str = simpledialog.askstring("查找", "请输入要查找的文本:")
        if find_str:
            self.text_area.tag_remove("found", "1.0", tk.END)
            start_pos = "1.0"

            while True:
                start_pos = self.text_area.search(find_str, start_pos, stopindex=tk.END)
                if not start_pos:
                    break
                end_pos = f"{start_pos}+{len(find_str)}c"
                self.text_area.tag_add("found", start_pos, end_pos)
                start_pos = end_pos

            # 使用主题管理器的颜色配置
            theme = self.theme_manager.get_current_theme()
            self.text_area.tag_configure(
                "found", background=theme["found_bg"], foreground=theme["found_fg"]
            )

            if not self.text_area.tag_ranges("found"):
                messagebox.showinfo("查找结果", "未找到指定文本")

    def replace_text(self):
        """替换文本"""
        # 使用新的查找和替换对话框
        FindDialog(self.root, self.text_area, self.current_file)

    def go_to_end(self):
        """转到文件底部"""
        self.text_area.see(tk.END)
        self.text_area.mark_set(tk.INSERT, tk.END)
        self.text_area.focus_set()
        self.update_statusbar()

    def go_to_home(self):
        """转到文件顶部"""
        self.text_area.see("1.0")
        self.text_area.mark_set(tk.INSERT, "1.0")
        self.text_area.focus_set()
        self.update_statusbar()

    # 格式设置方法
    def choose_font(self):
        """选择字体"""
        # 获取系统可用字体列表
        available_fonts = list(font.families())
        available_fonts.sort()  # 排序字体列表

        # 创建字体选择对话框
        font_dialog = tk.Toplevel(self.root)
        font_dialog.title("选择字体")
        font_dialog.geometry("500x600")  # 调整窗口大小以容纳示例文字
        font_dialog.resizable(True, True)
        font_dialog.transient(self.root)
        font_dialog.grab_set()  # 模态对话框

        # 当前字体标签
        current_label = tk.Label(
            font_dialog, text=f"当前字体: {self.font_family}", font=("Arial", 10)
        )
        current_label.pack(pady=5)

        # 创建滚动条和列表框
        frame = tk.Frame(font_dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 字体列表框
        font_listbox = tk.Listbox(
            frame, yscrollcommand=scrollbar.set, font=("Arial", 10)
        )
        font_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=font_listbox.yview)

        # 添加字体到列表框
        for font_name in available_fonts:
            font_listbox.insert(tk.END, font_name)

        # 选中当前字体
        try:
            current_index = available_fonts.index(self.font_family)
            font_listbox.selection_set(current_index)
            font_listbox.see(current_index)
        except ValueError:
            # 如果当前字体不在列表中, 默认选中第一个
            if available_fonts:
                font_listbox.selection_set(0)
                font_listbox.see(0)

        # 实时预览字体函数
        def preview_font(event=None):
            selection = font_listbox.curselection()
            if selection:
                selected_font = font_listbox.get(selection[0])
                # 更新示例文字的字体
                sample_text.config(font=(selected_font, self.font_size))
                current_label.config(text=f"当前字体: {selected_font}")

        # 双击选择字体
        def on_font_select(event=None):
            selection = font_listbox.curselection()
            if selection:
                selected_font = font_listbox.get(selection[0])
                self.font_family = selected_font
                self.update_font()
                self.save_config()
                font_dialog.destroy()

        # 绑定双击事件
        font_listbox.bind("<Double-Button-1>", on_font_select)

        # 绑定选择变化事件，实现实时预览
        font_listbox.bind("<<ListboxSelect>>", preview_font)

        # 示例文字框架
        sample_frame = tk.LabelFrame(font_dialog, text="字体预览", padx=10, pady=10)
        sample_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=5)

        # 示例文字
        sample_text = tk.Text(sample_frame, wrap=tk.WORD, height=8)
        sample_text.pack(fill=tk.BOTH, expand=True)

        # 插入示例文字内容
        sample_content = """这是字体预览示例文字。
The quick brown fox jumps over the lazy dog.
0123456789
"""
        sample_text.insert(tk.END, sample_content)
        sample_text.config(state=tk.DISABLED)  # 设为只读

        # 应用当前字体到示例文字
        sample_text.config(font=(self.font_family, self.font_size))

        # 按钮框架
        button_frame = tk.Frame(font_dialog)
        button_frame.pack(pady=10)

        # 确定按钮
        ok_button = tk.Button(
            button_frame, text="确定", command=on_font_select, width=10
        )
        ok_button.pack(side=tk.LEFT, padx=5)

        # 取消按钮
        cancel_button = tk.Button(
            button_frame, text="取消", command=font_dialog.destroy, width=10
        )
        cancel_button.pack(side=tk.LEFT, padx=5)

        # 居中显示对话框
        font_dialog.update_idletasks()
        x = (font_dialog.winfo_screenwidth() // 2) - (font_dialog.winfo_width() // 2)
        y = (font_dialog.winfo_screenheight() // 2) - (font_dialog.winfo_height() // 2)
        font_dialog.geometry(f"+{x}+{y}")

    def choose_font_size(self):
        """选择字体大小"""
        # 创建字体大小设置对话框
        size_dialog = tk.Toplevel(self.root)
        size_dialog.title("设置字体大小")
        size_dialog.geometry("500x400")  # 调整窗口大小以容纳示例文字
        size_dialog.resizable(True, True)  # 允许调整大小
        size_dialog.transient(self.root)
        size_dialog.grab_set()  # 模态对话框

        # 居中显示对话框
        size_dialog.update_idletasks()
        x = (size_dialog.winfo_screenwidth() // 2) - (size_dialog.winfo_width() // 2)
        y = (size_dialog.winfo_screenheight() // 2) - (size_dialog.winfo_height() // 2)
        size_dialog.geometry(f"+{x}+{y}")

        # 当前字体大小标签
        current_label = tk.Label(
            size_dialog, text=f"当前字体大小: {self.font_size}", font=("Arial", 10)
        )
        current_label.pack(pady=5)

        # 字体大小变量
        size_var = tk.StringVar(value=str(self.font_size))

        # 输入框框架
        input_frame = tk.Frame(size_dialog)
        input_frame.pack(pady=5)

        # 减少按钮
        def decrease_size():
            try:
                current_size = int(size_var.get())
                if current_size > 1:  # 最小字体大小为1
                    new_size = current_size - 1
                    size_var.set(str(new_size))
                    self.font_size = new_size
                    self.update_font()
                    current_label.config(text=f"当前字体大小: {self.font_size}")
                    # 更新示例文字的字体大小
                    sample_text.config(font=(self.font_family, new_size))
            except ValueError:
                pass

        decrease_btn = tk.Button(input_frame, text="-", command=decrease_size, width=3)
        decrease_btn.pack(side=tk.LEFT, padx=5)

        # 输入框
        size_entry = tk.Entry(
            input_frame, textvariable=size_var, width=10, justify="center"
        )
        size_entry.pack(side=tk.LEFT, padx=5)

        # 增加按钮
        def increase_size():
            try:
                current_size = int(size_var.get())
                if current_size < 100:  # 最大字体大小为100
                    new_size = current_size + 1
                    size_var.set(str(new_size))
                    self.font_size = new_size
                    self.update_font()
                    current_label.config(text=f"当前字体大小: {self.font_size}")
                    # 更新示例文字的字体大小
                    sample_text.config(font=(self.font_family, new_size))
            except ValueError:
                pass

        increase_btn = tk.Button(input_frame, text="+", command=increase_size, width=3)
        increase_btn.pack(side=tk.LEFT, padx=5)

        # 示例文字框架
        sample_frame = tk.LabelFrame(size_dialog, text="字体预览", padx=10, pady=10)
        sample_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 示例文字
        sample_text = tk.Text(sample_frame, wrap=tk.WORD, height=8)
        sample_text.pack(fill=tk.BOTH, expand=True)

        # 插入示例文字内容
        sample_content = """这是字体预览示例文字。
The quick brown fox jumps over the lazy dog.
0123456789
"""
        sample_text.insert(tk.END, sample_content)
        sample_text.config(state=tk.DISABLED)  # 设为只读

        # 应用当前字体大小到示例文字
        sample_text.config(font=(self.font_family, self.font_size))

        # 按钮框架
        button_frame = tk.Frame(size_dialog)
        button_frame.pack(pady=10)

        # 确定按钮
        def apply_size():
            try:
                new_size = int(size_var.get())
                if 1 <= new_size <= 100:  # 限制字体大小范围
                    self.font_size = new_size
                    self.update_font()
                    self.save_config()
                    size_dialog.destroy()
                else:
                    messagebox.showerror("错误", "字体大小必须在1-100之间")
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字")

        ok_button = tk.Button(button_frame, text="确定", command=apply_size, width=10)
        ok_button.pack(side=tk.LEFT, padx=5)

        # 取消按钮
        cancel_button = tk.Button(
            button_frame, text="取消", command=size_dialog.destroy, width=10
        )
        cancel_button.pack(side=tk.LEFT, padx=5)

        # 绑定回车键确认
        size_entry.bind("<Return>", lambda event: apply_size())
        size_entry.focus_set()

    def toggle_bold(self):
        """切换粗体"""
        self.font_bold = not self.font_bold
        self.update_font()
        self.save_config()

    def toggle_italic(self):
        """切换斜体"""
        self.font_italic = not self.font_italic
        self.update_font()
        self.save_config()

    def toggle_underline(self):
        """切换下划线"""
        self.font_underline = not self.font_underline
        self.update_font()
        self.save_config()

    # 帮助方法
    def toggle_toolbar(self):
        """切换工具栏显示/隐藏"""
        self.toolbar_visible = not self.toolbar_visible
        self.toolbar_var.set(self.toolbar_visible)
        if self.toolbar_visible:
            self.create_toolbar()
        else:
            # 隐藏工具栏
            if hasattr(self, "toolbar"):
                self.toolbar.pack_forget()
        self.save_config()

    def enable_drag_and_drop(self):
        """启用拖拽支持"""
        # 注册拖拽事件
        self.root.drop_target_register(tkinterdnd2.DND_FILES)
        self.root.dnd_bind("<<Drop>>", self.on_drop)

    def on_drop(self, event):
        """处理文件拖拽释放事件"""
        # 获取拖拽的文件路径
        if event.data:
            # 处理拖拽的数据
            files = self.root.tk.splitlist(event.data)
            if files:
                # 检查是否有未保存的更改
                if not self.check_unsaved_changes():
                    return  # 用户取消操作

                # 只处理第一个文件
                file_path = files[0]
                # 检查是否为文件
                if os.path.isfile(file_path):
                    self.open_file_by_path(file_path)
                elif os.path.isdir(file_path):
                    # 如果是目录, 显示提示
                    messagebox.showinfo("提示", "拖拽的是目录, 请拖拽文件以打开")
                else:
                    messagebox.showwarning("警告", "无法识别拖拽的项目")

    def open_file_by_path(self, file_path):
        """通过文件路径打开文件"""
        try:
            # 检查文件大小
            file_size = os.path.getsize(file_path)
            if file_size > MaxFileSize:
                formatted_size = format_file_size(file_size)
                max_size = format_file_size(MaxFileSize)
                messagebox.showerror(
                    "文件过大",
                    f"无法打开文件: {os.path.basename(file_path)}\n"
                    f"文件大小: {formatted_size}\n"
                    f"超过最大允许大小: {max_size}\n"
                    f"请使用其他专业编辑器打开此文件。",
                )
                return

            # 检测文件编码和换行符类型
            self.encoding, self.line_ending = self.detect_file_encoding_and_line_ending(
                file_path
            )

            # 直接读取文件内容 (移除了文件大小判断和分块加载逻辑)
            with open(file_path, "r", encoding=self.encoding) as file:
                content = file.read()

            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(1.0, content)
            # 更新总行数
            self.total_lines = len(content.split("\n"))
            self.current_file = file_path
            self.root.title(f"{os.path.basename(file_path)} - 文本编辑器")
            self.text_area.edit_modified(False)

            # 检查文件扩展名, 如果是Python文件则应用语法高亮
            _, ext = os.path.splitext(file_path)
            if ext.lower() in [".py", ".pyw"]:
                self.apply_syntax_highlighting()
            else:
                self.remove_syntax_highlighting()

            # 如果处于只读模式, 设置文本区域为只读
            if self.readonly_mode:
                self.text_area.config(state=tk.DISABLED)
            else:
                self.text_area.config(state=tk.NORMAL)

            # 更新状态栏
            self.update_statusbar()
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件: {str(e)}")

    def toggle_readonly_mode(self):
        """切换只读模式"""
        self.readonly_mode = not self.readonly_mode
        self.readonly_var.set(self.readonly_mode)

        # 根据只读模式状态启用或禁用文本区域
        if self.readonly_mode:
            self.text_area.config(state=tk.DISABLED)
        else:
            self.text_area.config(state=tk.NORMAL)

        # 更新状态栏提示
        self.update_statusbar()

    def show_find_dialog(self):
        """显示查找对话框"""
        FindDialog(self.root, self.text_area, self.current_file)

    def advanced_find_text(
        self, search_term, search_type="normal", match_case=True, whole_word=False
    ):
        """查找文本功能"""
        # 清除之前的高亮
        self.text_area.tag_remove("found", "1.0", tk.END)

        if not search_term:
            return []

        matches = []
        start_pos = "1.0"

        try:
            # 根据查找类型选择不同的查找方式
            if search_type == "regex":
                # 正则表达式查找
                flags = 0 if match_case else re.IGNORECASE
                pattern = search_term
                if whole_word:
                    pattern = r"\b" + re.escape(search_term) + r"\b"

                content = self.text_area.get("1.0", tk.END + "-1c")
                for match in re.finditer(pattern, content, flags):
                    start_idx = self.text_area.index(f"1.0+{match.start()}c")
                    end_idx = self.text_area.index(f"1.0+{match.end()}c")
                    matches.append((start_idx, end_idx))
            else:
                # 普通查找或完整匹配查找
                search_flags = 0
                if not match_case:
                    search_flags = tk.IGNORECASE

                while True:
                    if whole_word and search_type == "whole":
                        # 完整单词匹配
                        pattern = r"\b" + re.escape(search_term) + r"\b"
                        content = self.text_area.get(start_pos, tk.END)
                        match = re.search(
                            pattern, content, re.IGNORECASE if not match_case else 0
                        )
                        if not match:
                            break
                        # 计算实际位置
                        line_offset = content[: match.start()].count("\n")
                        char_offset = (
                            len(content[: match.start()].split("\n")[-1])
                            if "\n" in content[: match.start()]
                            else match.start()
                        )

                        current_line = int(start_pos.split(".")[0]) + line_offset
                        if line_offset == 0:
                            current_col = int(start_pos.split(".")[1]) + char_offset
                        else:
                            current_col = char_offset

                        start_idx = f"{current_line}.{current_col}"
                        end_idx = f"{current_line}.{current_col + len(search_term)}"
                    else:
                        # 普通查找
                        start_idx = self.text_area.search(
                            search_term, start_pos, tk.END, nocase=not match_case
                        )
                        if not start_idx:
                            break
                        end_idx = f"{start_idx}+{len(search_term)}c"

                    matches.append((start_idx, end_idx))
                    start_pos = f"{end_idx}+1c"
        except Exception as e:
            messagebox.showerror("查找错误", f"查找过程中发生错误: {str(e)}")
            return []

        # 高亮所有匹配项
        for start_idx, end_idx in matches:
            self.text_area.tag_add("found", start_idx, end_idx)

        self.text_area.tag_configure("found", background="yellow", foreground="black")

        return matches

    def show_about(self):
        """显示关于信息"""
        messagebox.showinfo(
            "关于文本编辑器",
            "功能特点:\n"
            "- 文件操作: 新建、打开、保存、另存为、关闭文件\n"
            "- 编码支持: UTF-8、UTF-16、GBK、GB2312、ASCII、ISO-8859-1\n"
            "- 换行符支持: LF、CRLF、CR\n"
            "- 编辑功能: 撤销、重做、复制、剪切、粘贴、全选\n"
            "- 查找替换: 文本查找和替换\n"
            "- 格式设置: 字体、大小、粗体、斜体、下划线\n"
            "- 快捷键支持\n\n",
        )
