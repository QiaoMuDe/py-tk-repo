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

# 文件大小限制
MaxFileSize = 1024 * 1024 * 10

class AdvancedTextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("文本编辑器")
        self.root.geometry("900x800")
        self.center_window()

        # 初始化变量
        self.current_file = None # 当前打开的文件路径
        self.font_family = "Arial"  # 默认字体
        self.font_size = 12  # 默认字体大小
        self.font_bold = False  # 默认不加粗
        self.font_italic = False  # 默认不斜体
        self.font_underline = False  # 默认无下划线
        self.toolbar_visible = True  # 工具栏默认显示
        self.show_line_numbers = True  # 行号显示状态, 默认显示
        self.encoding = "UTF-8" # 默认编码
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

    def apply_syntax_highlighting(self):
        """应用语法高亮"""
        try:
            # 使用更安全的方式应用语法高亮
            self.root.after(100, self._safe_apply_syntax_highlighting)
        except Exception as e:
            # 捕获所有异常并显示警告但不中断程序
            messagebox.showwarning("语法高亮警告", f"无法应用语法高亮: {str(e)}")

    def _safe_apply_syntax_highlighting(self):
        """安全地应用语法高亮, 避免与Tkinter命令冲突"""
        try:
            # 确保文本区域仍然存在且窗口未被销毁
            if not hasattr(self, "text_area") or not self.text_area.winfo_exists():
                return

            # 检查窗口是否仍然存在
            if not self.root.winfo_exists():
                return

            # 检查是否已经应用了语法高亮
            if hasattr(self, "_syntax_highlighted") and self._syntax_highlighted:
                # 检查内容是否发生变化
                current_content = self.text_area.get("1.0", tk.END)
                if (
                    hasattr(self, "_last_content")
                    and self._last_content == current_content
                ):
                    return  # 内容未变化, 无需重新应用语法高亮

            # 使用更安全的方式实现语法高亮, 避免Percolator可能引起的冲突
            self._apply_simple_syntax_highlighting()

            # 标记已应用语法高亮并保存当前内容
            self._syntax_highlighted = True
            self._last_content = self.text_area.get("1.0", tk.END)
        except tk.TclError as e:
            # 如果出现Tkinter命令冲突, 显示警告但不中断程序
            messagebox.showwarning("语法高亮警告", f"无法应用语法高亮: {str(e)}")
        except Exception as e:
            # 其他异常也显示警告但不中断程序
            messagebox.showwarning(
                "语法高亮警告", f"应用语法高亮时出现未知错误: {str(e)}"
            )

    def _apply_simple_syntax_highlighting(self):
        """应用简化的语法高亮"""
        # 定义Python关键字
        python_keywords = {
            "and",
            "as",
            "assert",
            "break",
            "class",
            "continue",
            "def",
            "del",
            "elif",
            "else",
            "except",
            "exec",
            "finally",
            "for",
            "from",
            "global",
            "if",
            "import",
            "in",
            "is",
            "lambda",
            "not",
            "or",
            "pass",
            "print",
            "raise",
            "return",
            "try",
            "while",
            "with",
            "yield",
        }

        # 清除之前的语法高亮
        self.text_area.tag_remove("keyword", "1.0", tk.END)
        self.text_area.tag_remove("string", "1.0", tk.END)
        self.text_area.tag_remove("comment", "1.0", tk.END)
        self.text_area.tag_remove("function", "1.0", tk.END)

        # 使用主题管理器的颜色配置
        theme = self.theme_manager.get_current_theme()
        self.text_area.tag_configure("keyword", foreground=theme["keyword_fg"])
        self.text_area.tag_configure("string", foreground=theme["string_fg"])
        self.text_area.tag_configure("comment", foreground=theme["comment_fg"])
        self.text_area.tag_configure("function", foreground=theme["function_fg"])

        # 获取全部文本内容
        content = self.text_area.get("1.0", tk.END)
        lines = content.split("\n")

        # 简单的语法高亮实现
        for i, line in enumerate(lines, 1):
            # 高亮注释
            if "#" in line:
                pos = line.find("#")
                start_idx = f"{i}.{pos}"
                end_idx = f"{i}.{len(line)}"
                self.text_area.tag_add("comment", start_idx, end_idx)

            # 高亮字符串
            in_string = False
            string_char = None
            for j, char in enumerate(line):
                if char in ['"', "'"] and (j == 0 or line[j - 1] != "\\"):
                    if not in_string:
                        in_string = True
                        string_char = char
                        string_start = j
                    elif char == string_char:
                        in_string = False
                        start_idx = f"{i}.{string_start}"
                        end_idx = f"{i}.{j+1}"
                        self.text_area.tag_add("string", start_idx, end_idx)

            # 高亮关键字
            words = line.split()
            for word in words:
                if word in python_keywords:
                    # 查找关键字在行中的位置
                    pos = line.find(word)
                    while pos != -1:
                        # 确保这是完整的单词而不是其他单词的一部分
                        start_pos = pos
                        end_pos = pos + len(word)
                        # 检查前后字符是否为单词边界
                        prev_char = line[start_pos - 1] if start_pos > 0 else " "
                        next_char = line[end_pos] if end_pos < len(line) else " "
                        if not (prev_char.isalnum() or prev_char == "_") and not (
                            next_char.isalnum() or next_char == "_"
                        ):
                            start_idx = f"{i}.{start_pos}"
                            end_idx = f"{i}.{end_pos}"
                            self.text_area.tag_add("keyword", start_idx, end_idx)
                        pos = line.find(word, pos + 1)

    def remove_syntax_highlighting(self):
        """移除语法高亮"""
        try:
            # 安全地移除所有语法高亮标签
            if hasattr(self, "text_area") and self.text_area.winfo_exists():
                self.text_area.tag_remove("keyword", "1.0", tk.END)
                self.text_area.tag_remove("string", "1.0", tk.END)
                self.text_area.tag_remove("comment", "1.0", tk.END)
                self.text_area.tag_remove("function", "1.0", tk.END)

                # 重置语法高亮标记
                self._syntax_highlighted = False
                if hasattr(self, "_last_content"):
                    delattr(self, "_last_content")
        except Exception as e:
            # 捕获所有异常并显示警告但不中断程序
            messagebox.showwarning("语法高亮警告", f"移除语法高亮时出现错误: {str(e)}")

    def center_window(self):
        """将窗口居中显示"""
        # 确保窗口已经绘制完成
        self.root.update_idletasks()

        # 获取窗口的实际宽度和高度
        width = self.root.winfo_width()
        height = self.root.winfo_height()

        # 如果获取的宽高为1, 则使用初始设置的几何尺寸
        if width <= 1 or height <= 1:
            width = 900
            height = 800

        # 获取屏幕的宽度和高度
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # 计算居中位置
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        # 设置窗口位置和尺寸
        self.root.geometry(f"{width}x{height}+{x}+{y}")

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
            # 优化大文件处理
            maxundo=50,  # 限制撤销操作数量
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
        help_menu.add_command(
            label="统计信息", command=self.show_statistics, accelerator="Ctrl+T"
        )
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
        """更新行号显示 (仅可见区域)"""
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
            # 根据行号位数计算宽度：个位数15像素, 两位数25像素, 三位数35像素, 以此类推
            # 增加额外空间确保行号能完整显示
            digits = len(str(max_line_number))
            line_number_width = max(35, digits * 12 + 10)
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

        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=4
        )

        # 格式按钮
        bold_btn = ttk.Button(self.toolbar, text="粗体", command=self.toggle_bold)
        bold_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(bold_btn)

        italic_btn = ttk.Button(self.toolbar, text="斜体", command=self.toggle_italic)
        italic_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(italic_btn)

        underline_btn = ttk.Button(
            self.toolbar, text="下划线", command=self.toggle_underline
        )
        underline_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(underline_btn)

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
        # 绑定点击事件
        self.right_status.bind("<Button-1>", self.on_line_ending_click)
        # 绑定右键点击事件
        self.right_status.bind("<Button-3>", self.on_encoding_click)

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
        self.root.bind("<Control-t>", lambda e: self.show_statistics())

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
        """处理换行符类型标签点击事件"""
        # 在三种换行符格式之间循环切换
        new_ending = self.cycle_line_ending()

        # 显示提示信息
        messagebox.showinfo("换行符切换", f"换行符格式已切换为: {new_ending}")

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

    def show_statistics(self):
        """显示文件统计信息"""
        # 获取文本内容
        content = self.text_area.get("1.0", tk.END + "-1c")

        # 计算统计信息
        char_count = len(content)
        line_count = content.count("\n") + 1
        word_count = len(content.split())

        # 计算非空白字符数
        non_whitespace_count = len(
            content.replace(" ", "").replace("\n", "").replace("\t", "")
        )

        # 计算段落数 (以空行分隔)
        paragraphs = [p for p in content.split("\n\n") if p.strip()]
        paragraph_count = len(paragraphs)

        # 创建统计信息对话框
        stats_window = tk.Toplevel(self.root)
        stats_window.title("统计信息")
        stats_window.geometry("300x200")
        stats_window.resizable(False, False)

        # 居中显示对话框
        stats_window.transient(self.root)
        stats_window.grab_set()

        # 创建标签显示统计信息
        tk.Label(stats_window, text=f"字符数: {char_count}", anchor="w").pack(
            fill="x", padx=10, pady=5
        )
        tk.Label(stats_window, text=f"行数: {line_count}", anchor="w").pack(
            fill="x", padx=10, pady=5
        )
        tk.Label(stats_window, text=f"单词数: {word_count}", anchor="w").pack(
            fill="x", padx=10, pady=5
        )
        tk.Label(
            stats_window, text=f"非空白字符数: {non_whitespace_count}", anchor="w"
        ).pack(fill="x", padx=10, pady=5)
        tk.Label(stats_window, text=f"段落数: {paragraph_count}", anchor="w").pack(
            fill="x", padx=10, pady=5
        )

        # 添加关闭按钮
        tk.Button(stats_window, text="关闭", command=stats_window.destroy).pack(pady=10)

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

    def load_large_file(self, file_path):
        """读取大文件内容"""
        try:
            # 清空现有内容
            self.text_area.delete(1.0, tk.END)

            # 显示加载状态
            self.left_status.config(text=f"正在加载文件: {file_path}")
            self.root.update_idletasks()

            # 直接读取整个文件内容
            with open(file_path, "r", encoding=self.encoding) as f:
                content = f.read()

            # 插入全部内容
            self.text_area.insert(tk.END, content)

            # 更新总行数
            self.total_lines = len(content.split("\n"))

            return content
        except Exception as e:
            raise e

    def open_file(self):
        """打开文件"""
        # 检查是否有未保存的更改
        if not self.check_unsaved_changes():
            return  # 用户取消操作

        file_path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("All Files", "*.*"), ("Text Files", "*.txt")],
        )

        if file_path:
            try:
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
            filetypes=[("All Files", "*.*"), ("Text Files", "*.txt")],
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
        font_dialog.geometry("400x500")
        font_dialog.resizable(True, True)
        font_dialog.transient(self.root)
        font_dialog.grab_set()  # 模态对话框

        # 当前字体标签
        current_label = tk.Label(
            font_dialog, text=f"当前字体: {self.font_family}", font=("Arial", 10)
        )
        current_label.pack(pady=10)

        # 创建滚动条和列表框
        frame = tk.Frame(font_dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

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
        size_str = simpledialog.askstring(
            "选择字体大小", f"当前大小: {self.font_size}\n请输入新字体大小:"
        )
        if size_str:
            try:
                self.font_size = int(size_str)
                self.update_font()
                self.save_config()
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字")

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


class FindDialog:
    def __init__(self, parent, text_widget, file_path=None):
        self.parent = parent
        self.text_widget = text_widget
        self.file_path = file_path
        self.matches = []
        self.current_match_index = -1
        self.is_searching = False  # 标记是否正在进行查找操作
        self.search_thread = None  # 查找线程
        self.search_queue = queue.Queue()  # 用于线程间通信的队列
        self.cancel_search = False  # 取消查找标志
        self._last_search_term = ""  # 上次查找的词
        self.replace_entry = None  # 替换输入框引用

        # 不再使用大文件查找器
        self.large_file_searcher = None

        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("查找和替换")
        self.dialog.geometry("500x350")  # 调整大小以适应新的布局并去除底部空白
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 居中显示
        self.center_window()

        # 创建界面元素
        self.create_widgets()

        # 绑定事件
        self.bind_events()

    def center_window(self):
        """将对话框居中显示"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        """创建界面控件"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)

        # 配置主框架的网格权重, 使内容居中
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)

        # 查找内容标签和输入框
        ttk.Label(main_frame, text="查找内容:").grid(
            row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5)
        )
        self.search_entry = ttk.Entry(main_frame, width=50)
        self.search_entry.grid(
            row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15)
        )
        self.search_entry.focus()

        # 替换内容标签和输入框
        ttk.Label(main_frame, text="替换为:").grid(
            row=2, column=0, columnspan=3, sticky=tk.W, pady=(0, 5)
        )
        self.replace_entry = ttk.Entry(main_frame, width=50)
        self.replace_entry.grid(
            row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15)
        )

        # 查找选项框架
        options_frame = ttk.LabelFrame(main_frame, text="查找选项", padding="10")
        options_frame.grid(
            row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15)
        )
        options_frame.columnconfigure(0, weight=1)
        options_frame.columnconfigure(1, weight=1)
        options_frame.columnconfigure(2, weight=1)

        # 查找模式
        self.search_type = tk.StringVar(value="normal")
        ttk.Radiobutton(
            options_frame, text="普通", variable=self.search_type, value="normal"
        ).grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(
            options_frame, text="正则表达式", variable=self.search_type, value="regex"
        ).grid(row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(
            options_frame, text="完整匹配", variable=self.search_type, value="whole"
        ).grid(row=0, column=2, sticky=tk.W)

        # 其他选项
        self.match_case = tk.BooleanVar(value=True)
        self.multiline_match = tk.BooleanVar(value=False)  # 跨行匹配选项
        ttk.Checkbutton(
            options_frame, text="区分大小写", variable=self.match_case
        ).grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        ttk.Checkbutton(
            options_frame, text="跨行匹配", variable=self.multiline_match
        ).grid(row=1, column=1, sticky=tk.W, pady=(10, 0))

        # 按钮框架 - 重新设计为更平衡的布局
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(
            row=5, column=0, columnspan=3, pady=(10, 0), sticky=(tk.W, tk.E)
        )
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        button_frame.columnconfigure(3, weight=1)
        button_frame.columnconfigure(4, weight=1)
        button_frame.columnconfigure(5, weight=1)

        # 查找按钮组
        find_frame = ttk.LabelFrame(button_frame, text="查找", padding="5")
        find_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=(0, 5))
        find_frame.columnconfigure(0, weight=1)
        find_frame.columnconfigure(1, weight=1)
        find_frame.columnconfigure(2, weight=1)

        self.find_button = ttk.Button(find_frame, text="下一个", command=self.find_next)
        self.find_button.grid(row=0, column=0, padx=(0, 2), sticky=tk.W + tk.E)

        self.find_prev_button = ttk.Button(
            find_frame, text="上一个", command=self.find_previous
        )
        self.find_prev_button.grid(row=0, column=1, padx=(2, 2), sticky=tk.W + tk.E)

        self.find_all_button = ttk.Button(
            find_frame, text="查找全部", command=self.find_all
        )
        self.find_all_button.grid(row=0, column=2, padx=(2, 0), sticky=tk.W + tk.E)

        # 替换按钮组
        replace_frame = ttk.LabelFrame(button_frame, text="替换", padding="5")
        replace_frame.grid(
            row=0, column=3, columnspan=3, sticky=(tk.W, tk.E), padx=(5, 0)
        )
        replace_frame.columnconfigure(0, weight=1)
        replace_frame.columnconfigure(1, weight=1)

        self.replace_once_button = ttk.Button(
            replace_frame, text="替换一次", command=self.replace_once
        )
        self.replace_once_button.grid(row=0, column=0, padx=(0, 2), sticky=tk.W + tk.E)

        self.replace_all_button = ttk.Button(
            replace_frame, text="替换全部", command=self.replace_all
        )
        self.replace_all_button.grid(row=0, column=1, padx=(2, 0), sticky=tk.W + tk.E)

    def bind_events(self):
        """绑定事件"""
        self.search_entry.bind("<Return>", lambda e: self.find_next())
        self.search_entry.bind("<KP_Enter>", lambda e: self.find_next())

    def find_next(self):
        """查找下一个匹配项"""
        search_term = self.search_entry.get()
        if not search_term:
            messagebox.showwarning("查找", "请输入要查找的内容")
            return

        # 检查是否正在进行查找操作
        if self.is_searching:
            # 取消当前查找操作
            self.cancel_search = True
            # 等待当前查找完成
            if self.search_thread and self.search_thread.is_alive():
                self.search_thread.join(timeout=1)  # 等待最多1秒

        # 检查是否需要重新执行查找 (查找词变更或没有匹配结果)
        needs_new_search = (
            not self.matches or getattr(self, "_last_search_term", "") != search_term
        )

        if needs_new_search:
            # 执行查找
            self.matches = self.perform_search(search_term)
            self._last_search_term = search_term  # 保存当前查找词
            self.current_match_index = -1  # 重置索引

        if not self.matches:
            messagebox.showinfo("查找结果", "未找到指定内容")
            return

        # 更新当前匹配索引
        if self.current_match_index < len(self.matches) - 1:
            self.current_match_index += 1
        else:
            self.current_match_index = 0

        # 高亮当前匹配项并滚动到可视区域
        self.highlight_current_match()

    def find_previous(self):
        """查找上一个匹配项"""
        search_term = self.search_entry.get()
        if not search_term:
            messagebox.showwarning("查找", "请输入要查找的内容")
            return

        # 检查是否正在进行查找操作
        if self.is_searching:
            # 取消当前查找操作
            self.cancel_search = True
            # 等待当前查找完成
            if self.search_thread and self.search_thread.is_alive():
                self.search_thread.join(timeout=1)  # 等待最多1秒

        # 检查是否需要重新执行查找 (查找词变更或没有匹配结果)
        needs_new_search = (
            not self.matches or getattr(self, "_last_search_term", "") != search_term
        )

        if needs_new_search:
            # 执行查找
            self.matches = self.perform_search(search_term)
            self._last_search_term = search_term  # 保存当前查找词
            self.current_match_index = -1  # 重置索引

        if not self.matches:
            messagebox.showinfo("查找结果", "未找到指定内容")
            return

        # 更新当前匹配索引
        if self.current_match_index > 0:
            self.current_match_index -= 1
        else:
            self.current_match_index = len(self.matches) - 1

        # 高亮当前匹配项并滚动到可视区域
        self.highlight_current_match()

    def find_all(self):
        """查找全部匹配项"""
        search_term = self.search_entry.get()
        if not search_term:
            messagebox.showwarning("查找", "请输入要查找的内容")
            return

        # 检查是否正在进行查找操作
        if self.is_searching:
            # 取消当前查找操作
            self.cancel_search = True
            # 等待当前查找完成
            if self.search_thread and self.search_thread.is_alive():
                self.search_thread.join(timeout=1)  # 等待最多1秒

        # 执行查找
        self.matches = self.perform_search(search_term)
        self._last_search_term = search_term  # 保存当前查找词

        if not self.matches:
            messagebox.showinfo("查找结果", "未找到指定内容")
            return

        # 高亮所有匹配项
        self.highlight_all_matches()

        messagebox.showinfo("查找结果", f"找到了 {len(self.matches)} 个匹配项")

    def replace_once(self):
        """替换当前匹配项"""
        search_term = self.search_entry.get()
        replace_term = self.replace_entry.get() if self.replace_entry else ""

        if not search_term:
            messagebox.showwarning("替换", "请输入要查找的内容")
            return

        # 如果还没有查找过, 先执行查找
        if not self.matches:
            self.find_next()
            if not self.matches:
                return  # 没有找到匹配项

        # 检查是否有当前匹配项
        if self.current_match_index < 0 or self.current_match_index >= len(
            self.matches
        ):
            messagebox.showinfo("替换", "请先查找内容")
            return

        # 获取当前匹配项的位置
        start_idx, end_idx = self.matches[self.current_match_index]

        # 执行替换
        self.text_widget.delete(start_idx, end_idx)
        self.text_widget.insert(start_idx, replace_term)

        # 重新执行查找以更新匹配项列表
        self.matches = self.perform_search(search_term)
        self._last_search_term = search_term

        # 重置当前索引
        self.current_match_index = -1

        messagebox.showinfo("替换", "已替换当前匹配项")

    def replace_all(self):
        """替换所有匹配项"""
        search_term = self.search_entry.get()
        replace_term = self.replace_entry.get() if self.replace_entry else ""

        if not search_term:
            messagebox.showwarning("替换", "请输入要查找的内容")
            return

        # 执行查找获取所有匹配项
        self.matches = self.perform_search(search_term)
        self._last_search_term = search_term

        if not self.matches:
            messagebox.showinfo("替换", "未找到指定内容")
            return

        # 保存替换计数
        replaced_count = len(self.matches)

        # 从后往前替换, 避免位置偏移问题
        for i in range(len(self.matches) - 1, -1, -1):
            start_idx, end_idx = self.matches[i]
            self.text_widget.delete(start_idx, end_idx)
            self.text_widget.insert(start_idx, replace_term)

        # 清除匹配项列表和高亮
        self.matches = []
        self.current_match_index = -1
        self.text_widget.tag_remove("found", "1.0", tk.END)
        self.text_widget.tag_remove("current_match", "1.0", tk.END)

        messagebox.showinfo("替换", f"已替换 {replaced_count} 个匹配项")

    def perform_search(self, search_term):
        """执行实际的查找操作"""
        # 设置查找状态
        self.is_searching = True
        self.cancel_search = False  # 重置取消标志

        # 更新UI状态
        self.find_button.config(state=tk.DISABLED)
        self.find_prev_button.config(state=tk.DISABLED)
        self.find_all_button.config(state=tk.DISABLED)

        # 清除之前的高亮
        self.text_widget.tag_remove("found", "1.0", tk.END)
        self.text_widget.tag_remove("current_match", "1.0", tk.END)

        search_type = self.search_type.get()
        match_case = self.match_case.get()
        multiline_match = self.multiline_match.get()  # 获取跨行匹配选项

        matches = []

        try:
            if search_type == "regex":
                # 正则表达式查找
                try:
                    flags = 0
                    if not match_case:
                        flags |= re.IGNORECASE
                    if multiline_match:
                        flags |= re.DOTALL  # 启用跨行匹配
                    pattern = search_term
                    content = self.text_widget.get("1.0", tk.END + "-1c")

                    # 获取内容总长度用于进度计算
                    total_length = len(content)
                    processed_length = 0

                    # 编译正则表达式以提高性能
                    compiled_pattern = re.compile(pattern, flags)

                    for match in compiled_pattern.finditer(content):
                        # 检查是否需要取消查找
                        if self.cancel_search:
                            # 更新UI状态
                            self.find_button.config(state=tk.NORMAL)
                            self.find_prev_button.config(state=tk.NORMAL)
                            self.find_all_button.config(state=tk.NORMAL)
                            return []
                        start_idx = self.text_widget.index(f"1.0+{match.start()}c")
                        end_idx = self.text_widget.index(f"1.0+{match.end()}c")
                        matches.append((start_idx, end_idx))
                except re.error as e:
                    messagebox.showerror(
                        "正则表达式错误", f"正则表达式语法错误: {str(e)}"
                    )
                    # 更新UI状态
                    self.find_button.config(state=tk.NORMAL)
                    self.find_prev_button.config(state=tk.NORMAL)
                    self.find_all_button.config(state=tk.NORMAL)
                    return []
            else:
                # 普通查找或完整匹配
                search_flags = 0 if match_case else re.IGNORECASE

                start_pos = "1.0"
                content = self.text_widget.get("1.0", tk.END + "-1c")
                total_length = len(content)
                processed_length = 0

                while True:
                    # 检查是否需要取消查找
                    if self.cancel_search:
                        # 更新UI状态
                        self.find_button.config(state=tk.NORMAL)
                        self.find_prev_button.config(state=tk.NORMAL)
                        self.find_all_button.config(state=tk.NORMAL)
                        return []

                    if search_type == "whole":
                        # 完整单词匹配
                        pattern = r"\b" + re.escape(search_term) + r"\b"
                        content_from_start = self.text_widget.get(start_pos, tk.END)
                        flags = 0 if match_case else re.IGNORECASE
                        match = re.search(pattern, content_from_start, flags)
                        if not match:
                            break

                        # 计算实际位置
                        content_up_to_start = self.text_widget.get("1.0", start_pos)
                        full_content_up_to_match = (
                            content_up_to_start + content_from_start[: match.start()]
                        )

                        lines = full_content_up_to_match.split("\n")
                        current_line = len(lines)
                        current_col = len(lines[-1])
                        start_idx = f"{current_line}.{current_col}"
                        end_idx = f"{current_line}.{current_col + len(search_term)}"
                    else:
                        # 普通查找
                        start_idx = self.text_widget.search(
                            search_term, start_pos, tk.END, nocase=not match_case
                        )
                        if not start_idx:
                            break
                        end_idx = f"{start_idx}+{len(search_term)}c"

                    matches.append((start_idx, end_idx))
                    start_pos = f"{end_idx}+1c"

        except re.error as e:
            messagebox.showerror("正则表达式错误", f"正则表达式语法错误: {str(e)}")
            # 更新UI状态
            self.find_button.config(state=tk.NORMAL)
            self.find_prev_button.config(state=tk.NORMAL)
            self.find_all_button.config(state=tk.NORMAL)
            return []
        except Exception as e:
            messagebox.showerror("查找错误", f"查找过程中发生错误: {str(e)}")
            # 更新UI状态
            self.find_button.config(state=tk.NORMAL)
            self.find_prev_button.config(state=tk.NORMAL)
            self.find_all_button.config(state=tk.NORMAL)
            return []

            # 使用主题管理器的颜色配置
        theme = (
            self.theme_manager.get_current_theme()
            if hasattr(self, "theme_manager")
            else None
        )
        if theme is None and hasattr(self.text_widget.master.master, "theme_manager"):
            theme = self.text_widget.master.master.theme_manager.get_current_theme()

        if theme:
            self.text_widget.tag_configure(
                "found", background=theme["found_bg"], foreground=theme["found_fg"]
            )
            self.text_widget.tag_configure(
                "current_match",
                background=theme["current_match_bg"],
                foreground=theme["current_match_fg"],
            )
        else:
            # 默认颜色配置
            self.text_widget.tag_configure(
                "found", background="yellow", foreground="black"
            )
            self.text_widget.tag_configure(
                "current_match", background="orange", foreground="black"
            )

        # 重置查找状态
        self.is_searching = False

        # 更新UI状态
        self.find_button.config(state=tk.NORMAL)
        self.find_prev_button.config(state=tk.NORMAL)
        self.find_all_button.config(state=tk.NORMAL)

        # 如果不是取消操作, 显示查找结果
        if not self.cancel_search:
            pass  # 不再显示进度标签

        return matches

    def highlight_all_matches(self):
        """高亮所有匹配项"""
        # 清除之前的高亮
        self.text_widget.tag_remove("found", "1.0", tk.END)
        self.text_widget.tag_remove("current_match", "1.0", tk.END)

        # 高亮所有匹配项
        for start_idx, end_idx in self.matches:
            self.text_widget.tag_add("found", start_idx, end_idx)

    def highlight_current_match(self):
        """高亮当前匹配项"""
        if (
            not self.matches
            or self.current_match_index < 0
            or self.current_match_index >= len(self.matches)
        ):
            return

        # 获取当前匹配项
        start_idx, end_idx = self.matches[self.current_match_index]

        # 清除之前的当前匹配高亮
        self.text_widget.tag_remove("current_match", "1.0", tk.END)

        # 高亮当前匹配项
        self.text_widget.tag_add("current_match", start_idx, end_idx)

        # 滚动到可视区域
        self.text_widget.see(start_idx)

        # 设置光标位置
        self.text_widget.mark_set(tk.INSERT, start_idx)
        self.text_widget.focus_set()


class LargeFileSearcher:
    """大文件查找器, 用于处理大文件的增量查找"""

    def __init__(self, file_path, text_widget, encoding="utf-8"):
        self.file_path = file_path
        self.text_widget = text_widget
        self.encoding = encoding
        self.file_content_lines = []
        self.total_lines = 0
        self.chunk_size = 8192  # 8KB chunks
        self.matches = []
        self.is_searching = False
        self.cancel_search = False

        # 如果是大文件, 预先加载行信息
        if file_path and os.path.exists(file_path):
            self._load_file_info()

    def _load_file_info(self):
        """加载文件信息但不加载全部内容"""
        try:
            # 使用chardet检测文件编码
            with open(self.file_path, "rb") as f:
                raw_data = f.read(10000)  # 读取前10KB用于编码检测
                result = chardet.detect(raw_data)
                detected_encoding = result["encoding"]

                # 如果检测到的编码更可靠, 则使用检测到的编码
                if result["confidence"] > 0.7:  # 置信度大于70%
                    self.encoding = detected_encoding

            # 只读取行数信息, 不加载全部内容到内存
            with open(
                self.file_path, "r", encoding=self.encoding, errors="ignore"
            ) as f:
                line_count = 0
                for line in f:
                    line_count += 1
                self.total_lines = line_count
        except Exception as e:
            print(f"加载文件信息时出错: {e}")

    def search_in_loaded_content(
        self, search_term, search_type="normal", match_case=True, whole_word=False
    ):
        """在已加载的内容中查找"""
        # 清除之前的高亮
        self.text_widget.tag_remove("found", "1.0", tk.END)
        self.text_widget.tag_remove("current_match", "1.0", tk.END)

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

                content = self.text_widget.get("1.0", tk.END + "-1c")
                for match in re.finditer(pattern, content, flags):
                    start_idx = self.text_widget.index(f"1.0+{match.start()}c")
                    end_idx = self.text_widget.index(f"1.0+{match.end()}c")
                    matches.append((start_idx, end_idx))
            else:
                # 普通查找或完整匹配查找
                while True:
                    if self.cancel_search:
                        return []

                    if whole_word and search_type == "whole":
                        # 完整单词匹配
                        pattern = r"\b" + re.escape(search_term) + r"\b"
                        content = self.text_widget.get(start_pos, tk.END)
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
                        start_idx = self.text_widget.search(
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

        # 保存匹配结果
        self.matches = matches

        # 高亮所有匹配项
        for start_idx, end_idx in matches:
            self.text_widget.tag_add("found", start_idx, end_idx)

        # 使用主题管理器的颜色配置
        theme = (
            self.theme_manager.get_current_theme()
            if hasattr(self, "theme_manager")
            else None
        )
        if theme is None and hasattr(self.text_widget.master.master, "theme_manager"):
            theme = self.text_widget.master.master.theme_manager.get_current_theme()

        if theme:
            self.text_widget.tag_configure(
                "found", background=theme["found_bg"], foreground=theme["found_fg"]
            )
            self.text_widget.tag_configure(
                "current_match",
                background=theme["current_match_bg"],
                foreground=theme["current_match_fg"],
            )
        else:
            # 默认颜色配置
            self.text_widget.tag_configure(
                "found", background="yellow", foreground="black"
            )
            self.text_widget.tag_configure(
                "current_match", background="orange", foreground="black"
            )

        return matches

    def search_in_file(
        self, search_term, search_type="normal", match_case=True, whole_word=False
    ):
        """在整个文件中查找 (增量查找)"""
        # 清除之前的高亮
        self.text_widget.tag_remove("found", "1.0", tk.END)
        self.text_widget.tag_remove("current_match", "1.0", tk.END)

        if not search_term:
            return []

        self.is_searching = True
        self.cancel_search = False
        matches = []

        try:
            # 获取文件大小用于进度计算
            file_size = (
                os.path.getsize(self.file_path)
                if self.file_path and os.path.exists(self.file_path)
                else 0
            )
            processed_size = 0

            # 根据查找类型选择不同的查找方式
            if search_type == "regex":
                # 正则表达式查找
                flags = 0 if match_case else re.IGNORECASE
                pattern = search_term
                if whole_word:
                    pattern = r"\b" + re.escape(search_term) + r"\b"

                # 编译正则表达式以提高性能
                compiled_pattern = re.compile(pattern, flags)

                # 分块读取文件进行查找
                with open(
                    self.file_path, "r", encoding=self.encoding, errors="ignore"
                ) as f:
                    content = ""
                    line_offset = 0

                    while True:
                        if self.cancel_search:
                            break

                        chunk = f.read(self.chunk_size)
                        if not chunk:
                            break

                        # 更新已处理大小
                        processed_size += len(chunk.encode(self.encoding))

                        content += chunk

                        # 查找匹配项
                        for match in compiled_pattern.finditer(content):
                            if self.cancel_search:
                                break

                            # 计算实际行号和列号
                            match_start = match.start()
                            match_end = match.end()

                            # 计算匹配项在文件中的实际位置
                            lines_up_to_match = content[:match_start].count("\n")
                            line_number = line_offset + lines_up_to_match + 1

                            if "\n" in content[:match_start]:
                                last_newline = content[:match_start].rfind("\n")
                                col_number = match_start - last_newline - 1
                            else:
                                col_number = match_start

                            start_idx = f"{line_number}.{col_number}"
                            end_idx = f"{line_number}.{col_number + (match_end - match_start)}"
                            matches.append((start_idx, end_idx))

                        # 保留部分内容以处理跨块匹配
                        if len(content) > self.chunk_size:
                            # 保留最后可能包含部分匹配的内容
                            last_newline = content.rfind("\n", -self.chunk_size)
                            if last_newline != -1:
                                line_offset += content[:last_newline].count("\n") + 1
                                content = content[last_newline + 1 :]

                                # 更新进度
                        if file_size > 0 and hasattr(self, "parent_dialog"):
                            progress = min(100, (processed_size / file_size) * 100)
                            self.parent_dialog.progress_var.set(progress)

            else:
                # 普通查找或完整匹配查找
                search_flags = 0 if match_case else re.IGNORECASE

                # 分块读取文件进行查找
                with open(
                    self.file_path, "r", encoding=self.encoding, errors="ignore"
                ) as f:
                    content = ""
                    line_offset = 0

                    while True:
                        if self.cancel_search:
                            break

                        chunk = f.read(self.chunk_size)
                        if not chunk:
                            break

                        # 更新已处理大小
                        processed_size += len(chunk.encode(self.encoding))

                        content += chunk

                        # 查找匹配项
                        pattern = search_term
                        if whole_word and search_type == "whole":
                            pattern = r"\b" + re.escape(search_term) + r"\b"

                        # 使用正则表达式进行查找
                        compiled_pattern = re.compile(pattern, search_flags)
                        for match in compiled_pattern.finditer(content):
                            if self.cancel_search:
                                break

                            # 计算实际行号和列号
                            match_start = match.start()
                            match_end = match.end()

                            # 计算匹配项在文件中的实际位置
                            lines_up_to_match = content[:match_start].count("\n")
                            line_number = line_offset + lines_up_to_match + 1

                            if "\n" in content[:match_start]:
                                last_newline = content[:match_start].rfind("\n")
                                col_number = match_start - last_newline - 1
                            else:
                                col_number = match_start

                            start_idx = f"{line_number}.{col_number}"
                            end_idx = f"{line_number}.{col_number + (match_end - match_start)}"
                            matches.append((start_idx, end_idx))

                        # 保留部分内容以处理跨块匹配
                        if len(content) > self.chunk_size:
                            # 保留最后可能包含部分匹配的内容
                            last_newline = content.rfind("\n", -self.chunk_size)
                            if last_newline != -1:
                                line_offset += content[:last_newline].count("\n") + 1
                                content = content[last_newline + 1 :]
        except Exception as e:
            messagebox.showerror("查找错误", f"查找过程中发生错误: {str(e)}")
            return []
        finally:
            self.is_searching = False

        # 保存匹配结果
        self.matches = matches

        # 高亮所有匹配项 (仅在当前可见区域)
        self.highlight_matches_in_view()

        return matches

    def highlight_matches_in_view(self):
        """高亮当前视图中的匹配项"""
        # 获取当前可见区域
        try:
            first_line = int(self.text_widget.index("@0,0").split(".")[0])
            last_line = int(
                self.text_widget.index(f"@0,{self.text_widget.winfo_height()}").split(
                    "."
                )[0]
            )

            # 高亮在可见区域内的匹配项
            for start_idx, end_idx in self.matches:
                start_line = int(start_idx.split(".")[0])
                if first_line <= start_line <= last_line:
                    self.text_widget.tag_add("found", start_idx, end_idx)
        except Exception:
            # 如果无法获取可见区域, 高亮所有匹配项
            for start_idx, end_idx in self.matches:
                self.text_widget.tag_add("found", start_idx, end_idx)

        # 使用主题管理器的颜色配置
        theme = (
            self.theme_manager.get_current_theme()
            if hasattr(self, "theme_manager")
            else None
        )
        if theme is None and hasattr(self.text_widget.master.master, "theme_manager"):
            theme = self.text_widget.master.master.theme_manager.get_current_theme()

        if theme:
            self.text_widget.tag_configure(
                "found", background=theme["found_bg"], foreground=theme["found_fg"]
            )
            self.text_widget.tag_configure(
                "current_match",
                background=theme["current_match_bg"],
                foreground=theme["current_match_fg"],
            )
        else:
            # 默认颜色配置
            self.text_widget.tag_configure(
                "found", background="yellow", foreground="black"
            )
            self.text_widget.tag_configure(
                "current_match", background="orange", foreground="black"
            )


class ThemeManager:
    """主题管理器类"""

    # 预定义的主题
    THEMES = {
        "light": {
            "name": "浅色主题",
            "text_bg": "white",
            "text_fg": "black",
            "text_insert_bg": "black",
            "text_select_bg": "lightblue",
            "text_select_fg": "black",
            "line_numbers_bg": "#f0f0f0",
            "line_numbers_fg": "gray",
            "found_bg": "yellow",
            "found_fg": "black",
            "current_match_bg": "orange",
            "current_match_fg": "black",
            "keyword_fg": "orange",
            "string_fg": "green",
            "comment_fg": "red",
            "function_fg": "blue",
            "menu_bg": "#f0f0f0",
            "menu_fg": "black",
            "menu_active_bg": "#316AC5",
            "menu_active_fg": "white",
            "toolbar_bg": "#f0f0f0",
            "toolbar_active_bg": "#d0d0d0",
            "toolbar_pressed_bg": "#c0c0c0",
            "toolbar_button_fg": "black",
            "statusbar_bg": "#f0f0f0",
            "statusbar_fg": "black",
        },
        "dark": {
            "name": "深色主题",
            "text_bg": "#2d2d2d",
            "text_fg": "#ffffff",
            "text_insert_bg": "#ffffff",
            "text_select_bg": "#3a6ea5",
            "text_select_fg": "#ffffff",
            "line_numbers_bg": "#3a3a3a",
            "line_numbers_fg": "#aaaaaa",
            "found_bg": "#ffff00",
            "found_fg": "#000000",
            "current_match_bg": "#ffa500",
            "current_match_fg": "#000000",
            "keyword_fg": "#ff9966",
            "string_fg": "#66cc66",
            "comment_fg": "#ff6666",
            "function_fg": "#6699ff",
            "menu_bg": "#3a3a3a",
            "menu_fg": "#ffffff",
            "menu_active_bg": "#094771",
            "menu_active_fg": "#ffffff",
            "toolbar_bg": "#3a3a3a",
            "toolbar_active_bg": "#4a4a4a",
            "toolbar_pressed_bg": "#5a5a5a",
            "toolbar_button_fg": "black",
            "statusbar_bg": "#3a3a3a",
            "statusbar_fg": "#ffffff",
        },
        "blue": {
            "name": "蓝色主题",
            "text_bg": "#e6f3ff",
            "text_fg": "#003366",
            "text_insert_bg": "#003366",
            "text_select_bg": "#99ccff",
            "text_select_fg": "#003366",
            "line_numbers_bg": "#cce6ff",
            "line_numbers_fg": "#0066cc",
            "found_bg": "#ffff99",
            "found_fg": "#003366",
            "current_match_bg": "#ffcc66",
            "current_match_fg": "#003366",
            "keyword_fg": "#cc6600",
            "string_fg": "#009900",
            "comment_fg": "#cc0000",
            "function_fg": "#0066cc",
            "menu_bg": "#cce6ff",
            "menu_fg": "#003366",
            "menu_active_bg": "#003366",
            "menu_active_fg": "#ffffff",
            "toolbar_bg": "#cce6ff",
            "toolbar_active_bg": "#99ccff",
            "toolbar_pressed_bg": "#6699cc",
            "toolbar_button_fg": "#003366",
            "statusbar_bg": "#cce6ff",
            "statusbar_fg": "#003366",
        },
        "parchment": {
            "name": "羊皮卷主题",
            "text_bg": "#f5e9d0",
            "text_fg": "#5a4a3f",
            "text_insert_bg": "#5a4a3f",
            "text_select_bg": "#e0c8a0",
            "text_select_fg": "#5a4a3f",
            "line_numbers_bg": "#e6d5b8",
            "line_numbers_fg": "#8c7a63",
            "found_bg": "#ffd700",
            "found_fg": "#5a4a3f",
            "current_match_bg": "#ff8c00",
            "current_match_fg": "#ffffff",
            "keyword_fg": "#8b4513",
            "string_fg": "#228b22",
            "comment_fg": "#a0522d",
            "function_fg": "#4b0082",
            "menu_bg": "#e6d5b8",
            "menu_fg": "#5a4a3f",
            "menu_active_bg": "#d0b895",
            "menu_active_fg": "#ffffff",
            "toolbar_bg": "#e6d5b8",
            "toolbar_active_bg": "#d0b895",
            "toolbar_pressed_bg": "#c0a885",
            "toolbar_button_fg": "#5a4a3f",
            "statusbar_bg": "#e6d5b8",
            "statusbar_fg": "#5a4a3f",
        },
        "green": {
            "name": "经典绿色主题",
            "text_bg": "#e6ffe6",  # 更浅的绿色背景
            "text_fg": "#006600",  # 深绿色文字
            "text_insert_bg": "#006600",
            "text_select_bg": "#99cc99",
            "text_select_fg": "#000000",
            "line_numbers_bg": "#ccffcc",
            "line_numbers_fg": "#006600",
            "found_bg": "#ffff99",
            "found_fg": "#000000",
            "current_match_bg": "#ffcc66",
            "current_match_fg": "#000000",
            "keyword_fg": "#009900",
            "string_fg": "#006633",
            "comment_fg": "#339933",
            "function_fg": "#0066cc",
            "menu_bg": "#ccffcc",
            "menu_fg": "#006600",
            "menu_active_bg": "#006600",
            "menu_active_fg": "#ffffff",
            "toolbar_bg": "#ccffcc",
            "toolbar_active_bg": "#99cc99",
            "toolbar_pressed_bg": "#669966",
            "toolbar_button_fg": "#006600",
            "statusbar_bg": "#ccffcc",
            "statusbar_fg": "#006600",
        },
        "midnight_purple": {
            "name": "午夜紫主题",
            "text_bg": "#f0e6ff",  # 更浅的紫色背景
            "text_fg": "#330066",  # 深紫色文字
            "text_insert_bg": "#330066",
            "text_select_bg": "#cc99ff",
            "text_select_fg": "#000000",
            "line_numbers_bg": "#e0d6f0",
            "line_numbers_fg": "#6600cc",
            "found_bg": "#ffcc99",
            "found_fg": "#000000",
            "current_match_bg": "#ff9966",
            "current_match_fg": "#000000",
            "keyword_fg": "#9900cc",
            "string_fg": "#006699",
            "comment_fg": "#9966cc",
            "function_fg": "#009966",
            "menu_bg": "#e0d6f0",
            "menu_fg": "#330066",
            "menu_active_bg": "#6600cc",
            "menu_active_fg": "#ffffff",
            "toolbar_bg": "#e0d6f0",
            "toolbar_active_bg": "#cc99ff",
            "toolbar_pressed_bg": "#9966cc",
            "toolbar_button_fg": "#330066",
            "statusbar_bg": "#e0d6f0",
            "statusbar_fg": "#330066",
        },
        "sunset": {
            "name": "日落橙主题",
            "text_bg": "#fff0e1",
            "text_fg": "#d35400",
            "text_insert_bg": "#d35400",
            "text_select_bg": "#f39c12",
            "text_select_fg": "#ffffff",
            "line_numbers_bg": "#f5d1b0",
            "line_numbers_fg": "#e67e22",
            "found_bg": "#f1c40f",
            "found_fg": "#d35400",
            "current_match_bg": "#e67e22",
            "current_match_fg": "#ffffff",
            "keyword_fg": "#2980b9",
            "string_fg": "#27ae60",
            "comment_fg": "#7f8c8d",
            "function_fg": "#8e44ad",
            "menu_bg": "#f5d1b0",
            "menu_fg": "#d35400",
            "menu_active_bg": "#e67e22",
            "menu_active_fg": "#ffffff",
            "toolbar_bg": "#f5d1b0",
            "toolbar_active_bg": "#ebbc91",
            "toolbar_pressed_bg": "#e0a87d",
            "toolbar_button_fg": "#d35400",
            "statusbar_bg": "#f5d1b0",
            "statusbar_fg": "#d35400",
        },
    }

    def __init__(self, editor):
        self.editor = editor
        self.current_theme = "light"

    def get_current_theme(self):
        """获取当前主题配置"""
        return self.THEMES.get(self.current_theme, self.THEMES["light"])

    def set_theme(self, theme_name):
        """设置主题"""
        if theme_name in self.THEMES:
            self.current_theme = theme_name
            self.apply_theme()
            return True
        return False

    def apply_theme(self):
        """应用当前主题到所有UI元素"""
        theme = self.get_current_theme()

        # 应用文本区域样式
        self.editor.text_area.config(
            bg=theme["text_bg"],
            fg=theme["text_fg"],
            insertbackground=theme["text_insert_bg"],
            selectbackground=theme["text_select_bg"],
            selectforeground=theme["text_select_fg"],
        )

        # 应用行号区域样式
        if hasattr(self.editor, "line_numbers"):
            self.editor.line_numbers.config(bg=theme["line_numbers_bg"])
            # 更新行号颜色
            self.editor.update_line_numbers()

        # 应用查找高亮样式
        self.editor.text_area.tag_configure(
            "found", background=theme["found_bg"], foreground=theme["found_fg"]
        )
        self.editor.text_area.tag_configure(
            "current_match",
            background=theme["current_match_bg"],
            foreground=theme["current_match_fg"],
        )

        # 应用语法高亮样式
        self.editor.text_area.tag_configure("keyword", foreground=theme["keyword_fg"])
        self.editor.text_area.tag_configure("string", foreground=theme["string_fg"])
        self.editor.text_area.tag_configure("comment", foreground=theme["comment_fg"])
        self.editor.text_area.tag_configure("function", foreground=theme["function_fg"])

        # 应用菜单样式
        try:
            # 配置菜单样式
            menu_bg = theme.get("menu_bg", theme["toolbar_bg"])
            menu_fg = theme.get("menu_fg", "black")
            menu_active_bg = theme.get("menu_active_bg", theme["toolbar_bg"])
            menu_active_fg = theme.get("menu_active_fg", "white")

            # 使用tk.Menu配置菜单样式
            if hasattr(self.editor, "root") and self.editor.root:
                self.editor.root.option_add("*Menu.Background", menu_bg)
                self.editor.root.option_add("*Menu.Foreground", menu_fg)
                self.editor.root.option_add("*Menu.ActiveBackground", menu_active_bg)
                self.editor.root.option_add("*Menu.ActiveForeground", menu_active_fg)

                # 重新创建菜单以应用新样式
                self.editor.create_menu()
        except Exception as e:
            print(f"应用菜单样式时出错: {e}")

        # 应用工具栏样式
        if hasattr(self.editor, "toolbar"):
            # 使用ttk.Style配置工具栏样式
            style = ttk.Style()
            # 创建一个唯一的样式名称
            toolbar_style = f"Toolbar_{self.current_theme.replace(' ', '_')}.TFrame"
            style.configure(toolbar_style, background=theme["toolbar_bg"])
            self.editor.toolbar.configure(style=toolbar_style)

            # 配置工具栏按钮样式
            button_style = (
                f"ToolbarButton_{self.current_theme.replace(' ', '_')}.TButton"
            )
            # 使用主题配置中的按钮文字颜色
            button_fg = theme.get("toolbar_button_fg", "black")

            style.configure(
                button_style, background=theme["toolbar_bg"], foreground=button_fg
            )
            # 配置按钮在不同状态下的样式
            style.map(
                button_style,
                background=[
                    (
                        "active",
                        (
                            theme["toolbar_active_bg"]
                            if "toolbar_active_bg" in theme
                            else theme["toolbar_bg"]
                        ),
                    ),
                    (
                        "pressed",
                        (
                            theme["toolbar_pressed_bg"]
                            if "toolbar_pressed_bg" in theme
                            else theme["toolbar_bg"]
                        ),
                    ),
                ],
                foreground=[("active", button_fg), ("pressed", button_fg)],
            )

            # 更新所有工具栏按钮的样式
            if hasattr(self.editor, "toolbar_buttons"):
                for btn in self.editor.toolbar_buttons:
                    btn.configure(style=button_style)

        # 应用状态栏样式
        if hasattr(self.editor, "statusbar_frame"):
            self.editor.statusbar_frame.config(bg=theme["statusbar_bg"])
        if hasattr(self.editor, "left_status"):
            self.editor.left_status.config(
                bg=theme["statusbar_bg"], fg=theme["statusbar_fg"]
            )
        if hasattr(self.editor, "right_status"):
            self.editor.right_status.config(
                bg=theme["statusbar_bg"], fg=theme["statusbar_fg"]
            )

        # 重新应用语法高亮
        self.editor._apply_simple_syntax_highlighting()


def main():
    """主函数"""
    # 使用tkinterdnd2创建支持拖拽的根窗口
    root = tkinterdnd2.Tk()
    app = AdvancedTextEditor(root)

    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        # 检查文件是否存在
        if os.path.exists(file_path):
            # 文件存在, 打开它
            app.open_file_by_path(file_path)
        else:
            # 文件不存在, 创建新文件
            app.current_file = file_path
            app.root.title(f"{os.path.basename(file_path)} - 文本编辑器")

    root.mainloop()


if __name__ == "__main__":
    main()
