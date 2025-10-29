import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, font
import os
import datetime
import sys
import json
import shutil
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
from utils import format_file_size, center_window, is_supported_file

# 文件大小限制
MaxFileSize = 1024 * 1024 * 10

# 主窗口-高
MainWindowHeight = 800

# 主窗口-宽
MainWindowWidth = 900

# 限制撤销操作数量
MaxUndo = 20

# 支持的文件后缀列表
SupportedExtensions = [
    ".py",
    ".pyw",
]

# 配置文件名
ConfigFileName = ".quick_edit_config.json"

# 配置文件路径
ConfigFilePath = os.path.join(os.path.expanduser("~"), ConfigFileName)


class AdvancedTextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("QuickEdit")
        self.root.geometry(f"{MainWindowWidth}x{MainWindowHeight}")
        center_window(self.root, MainWindowWidth, MainWindowHeight)

        # 初始化变量
        self.current_file = None  # 当前打开的文件路径
        self.font_family = "Arial"  # 默认字体
        self.font_size = 12  # 默认字体大小
        self.font_bold = False  # 默认不加粗
        self.font_italic = False  # 默认不斜体
        self.font_underline = False  # 默认无下划线
        self.font_overstrike = False  # 默认无删除线
        self.toolbar_visible = True  # 工具栏默认显示
        self.show_line_numbers = True  # 行号显示状态, 默认显示
        self.syntax_highlighting_enabled = True  # 语法高亮显示状态, 默认启用
        self.encoding = "UTF-8"  # 默认编码
        self.line_ending = "LF"  # 默认换行符
        self.readonly_mode = False  # 只读模式, 默认关闭
        self.current_theme = "light"  # 默认主题

        # 自动保存相关变量
        self.auto_save_enabled = False  # 默认关闭自动保存
        self.auto_save_interval = 5  # 默认自动保存间隔5秒
        self.auto_save_timer = None  # 自动保存计时器
        self.last_auto_save_time = None  # 上次自动保存时间
        self.auto_save_var = tk.BooleanVar(
            value=self.auto_save_enabled
        )  # 自动保存菜单变量
        self.backup_enabled = False  # 默认关闭备份
        self.backup_enabled_var = tk.BooleanVar(value=self.backup_enabled)  # 备份选项
        self.save_lock = threading.RLock()  # 线程安全锁
        self.is_saving = False

        # 异步文件读取相关属性
        self.file_read_thread = None
        self.file_read_cancelled = False
        self.progress_window = None

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

        # 设置自动保存功能
        self.setup_auto_save()

        # 启用拖拽支持
        self.enable_drag_and_drop()
        self.percolator = Percolator(self.text_area)

    def apply_syntax_highlighting(self):
        """应用语法高亮"""
        try:
            # 移除现有的语法高亮
            self.remove_syntax_highlighting()

            # 初始化ColorDelegator以避免delegate冲突
            self.color_delegator = ColorDelegator()
            # 应用自定义标签定义，采用Monokai Dimmed配色方案
            self.color_delegator.tagdefs["COMMENT"] = {
                "foreground": "#999999"
            }  # 灰色注释 (Monokai Dimmed风格)
            self.color_delegator.tagdefs["KEYWORD"] = {
                "foreground": "#AE81FF"
            }  # 紫色关键字 (Monokai Dimmed风格)
            self.color_delegator.tagdefs["BUILTIN"] = {
                "foreground": "#F92672"
            }  # 粉红色内置函数 (Monokai Dimmed风格)
            self.color_delegator.tagdefs["STRING"] = {
                "foreground": "#A6E22E"
            }  # 绿色字符串 (Monokai Dimmed风格)
            self.color_delegator.tagdefs["DEFINITION"] = {
                "foreground": "#F92672"
            }  # 粉红色内置函数 (Monokai Dimmed风格)
            self.color_delegator.tagdefs["SYNC"] = {
                "foreground": "#CCCCCC"
            }  # 浅灰色同步标记 (Monokai Dimmed风格)
            self.color_delegator.tagdefs["TODO"] = {
                "foreground": "#FD971F"
            }  # 橙黄色待办事项 (Monokai Dimmed风格)
            self.color_delegator.tagdefs["ERROR"] = {
                "foreground": "#F92672"
            }  # 粉红色错误标记 (Monokai Dimmed风格)
            self.color_delegator.tagdefs["hit"] = {
                "foreground": "#66D9EF"
            }  # 天蓝色匹配标记 (Monokai Dimmed风格)

            # 应用idlelib语法高亮
            self.percolator.insertfilter(self.color_delegator)
        except Exception as e:
            # 捕获所有异常但不中断程序
            # 在打开新文件或拖拽文件等操作中可能会出现临时性的状态不一致
            # 这种情况下的错误可以忽略，避免干扰用户体验
            pass

    def remove_syntax_highlighting(self):
        """移除语法高亮"""
        try:
            # 移除idlelib语法高亮
            self.percolator.removefilter(self.color_delegator)
        except Exception:
            # 捕获所有异常但不中断程序
            pass

    def _reset_file_state(self):
        """重置文件状态的辅助方法，用于close_file和new_file"""
        # 清空文本区域
        self.text_area.delete(1.0, tk.END)
        # 重置文件状态
        self.current_file = None
        self.root.title("QuickEdit")
        # 重置编码和换行符为默认值
        self.encoding = "UTF-8"
        self.line_ending = "LF"
        # 重置修改状态
        self.text_area.edit_modified(False)
        # 移除可能存在的语法高亮
        self.remove_syntax_highlighting()
        # 更新状态栏
        self.update_statusbar()

    def on_closing(self):
        """处理窗口关闭事件"""
        # 停止自动保存计时器
        self.stop_auto_save_timer()

        # 取消正在进行的文件读取操作
        self.file_read_cancelled = True

        # 只需设置取消标志，daemon线程会在主程序退出时自动终止
        # 不需要显式等待，因为这可能导致界面响应延迟

        # 使用公共方法检查并处理未保存的更改
        continue_operation, saved = self.check_and_handle_unsaved_changes("退出")

        if not continue_operation:
            return  # 用户取消操作

        # 检查窗口是否仍然存在再决定是否销毁
        if not self.root.winfo_exists():
            return

        # 如果启用了备份功能，并且是保存后退出或文件未被修改且有打开的文件，清理备份文件
        if self.backup_enabled and (
            (saved and self.current_file)
            or (self.current_file and not self.text_area.edit_modified())
        ):
            self.cleanup_backup()

        # 销毁窗口
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

            # 绑定鼠标事件用于悬停高亮
            self.line_numbers.bind("<Motion>", self.on_line_number_hover)
            self.line_numbers.bind("<Leave>", self.on_line_number_leave)

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
            "<ButtonRelease>", lambda e: self.schedule_line_number_update(50)
        )  # 鼠标释放时更新行号

        # 绑定文本变化事件, 用于更新行号
        self.text_area.bind(
            "<KeyRelease>", lambda e: self.schedule_line_number_update(50)
        )
        self.text_area.bind(
            "<<Modified>>", lambda e: self.schedule_line_number_update(50)
        )

        # 绑定光标移动事件, 用于高亮光标所在行
        self.text_area.bind("<KeyRelease>", self.highlight_cursor_line, add="+")
        self.text_area.bind("<ButtonRelease>", self.highlight_cursor_line, add="+")

        # 绑定鼠标右键事件，用于显示上下文菜单
        self.text_area.bind("<Button-3>", self.show_context_menu)

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
            label="向上翻页", command=self.page_up, accelerator="PgUp"
        )
        edit_menu.add_command(
            label="向下翻页", command=self.page_down, accelerator="PgDn"
        )
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
        theme_menu.add_command(
            label="切换主题", command=self.cycle_theme, accelerator="Ctrl+T"
        )
        theme_menu.add_separator()
        # 初始化字体样式变量
        self.bold_var = tk.BooleanVar(value=self.font_bold)
        self.italic_var = tk.BooleanVar(value=self.font_italic)
        self.underline_var = tk.BooleanVar(value=self.font_underline)
        self.overstrike_var = tk.BooleanVar(value=self.font_overstrike)

        theme_menu.add_checkbutton(
            label="粗体",
            command=self.toggle_bold,
            variable=self.bold_var,
        )
        theme_menu.add_checkbutton(
            label="斜体",
            command=self.toggle_italic,
            variable=self.italic_var,
        )
        theme_menu.add_checkbutton(
            label="下划线",
            command=self.toggle_underline,
            variable=self.underline_var,
        )
        theme_menu.add_checkbutton(
            label="删除线",
            command=self.toggle_overstrike,
            variable=self.overstrike_var,
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
        # 语法高亮显示选项
        self.syntax_highlighting_var = tk.BooleanVar(
            value=self.syntax_highlighting_enabled
        )
        settings_menu.add_checkbutton(
            label="语法高亮",
            command=self.toggle_syntax_highlighting,
            variable=self.syntax_highlighting_var,
        )
        # 自动保存设置
        settings_menu.add_separator()
        settings_menu.add_checkbutton(
            label="启用自动保存",
            command=self.toggle_auto_save,
            variable=self.auto_save_var,
        )
        settings_menu.add_command(
            label="设置自动保存间隔...",
            command=self.set_auto_save_interval,
        )
        # 备份选项
        self.backup_enabled_var = tk.BooleanVar(value=self.backup_enabled)
        settings_menu.add_checkbutton(
            label="开启副本备份",
            command=self.toggle_backup,
            variable=self.backup_enabled_var,
        )
        # 查看配置文件选项
        settings_menu.add_separator()
        settings_menu.add_command(
            label="查看配置",
            command=self.open_config_file,
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

    def toggle_syntax_highlighting(self):
        """切换语法高亮显示"""
        if self.syntax_highlighting_var.get():
            # 开启语法高亮
            self.syntax_highlighting_enabled = True
            self.left_status.config(text="语法高亮已开启")
            # 为当前打开的文件应用语法高亮
            if self.current_file and is_supported_file(
                SupportedExtensions, self.current_file
            ):
                self.apply_syntax_highlighting()
        else:
            # 关闭语法高亮
            self.syntax_highlighting_enabled = False
            self.left_status.config(text="语法高亮已关闭")
            # 移除当前文件的语法高亮
            self.remove_syntax_highlighting()

        # 保存配置
        self.save_config()

    def format_auto_save_interval(self, interval):
        """格式化自动保存间隔显示

        Args:
            interval: 自动保存间隔（秒）

        Returns:
            格式化后的间隔字符串（如"5分钟", "1小时30分钟"等）
        """
        if interval >= 3600:  # 1小时或以上
            hours = interval // 3600
            minutes = (interval % 3600) // 60
            if minutes == 0:
                return f"{hours}小时"
            else:
                return f"{hours}小时{minutes}分钟"
        elif interval >= 60:  # 1分钟或以上
            minutes = interval // 60
            seconds = interval % 60
            if seconds == 0:
                return f"{minutes}分钟"
            else:
                return f"{minutes}分钟{seconds}秒"
        else:  # 秒数
            return f"{interval}秒"

    def toggle_auto_save(self):
        """切换自动保存功能的启用状态"""
        self.auto_save_enabled = self.auto_save_var.get()
        self.save_config()

        if self.auto_save_enabled:
            self.start_auto_save_timer()
            # 使用辅助方法格式化显示
            display_interval = self.format_auto_save_interval(self.auto_save_interval)
            messagebox.showinfo("自动保存", f"已启用自动保存，间隔为{display_interval}")
        else:
            self.stop_auto_save_timer()
            messagebox.showinfo("自动保存", "已关闭自动保存")

    def toggle_backup(self):
        """切换备份功能的启用状态"""
        self.backup_enabled = self.backup_enabled_var.get()
        self.save_config()

        status_text = "已启用副本备份" if self.backup_enabled else "已禁用副本备份"
        self.left_status.config(text=status_text)

    def open_config_file(self):
        """打开配置文件"""
        # 检查配置文件是否存在
        if not os.path.exists(ConfigFilePath):
            # 如果配置文件不存在，复用save_config方法创建完整的配置文件
            try:
                self.save_config()
            except Exception as e:
                messagebox.showerror("错误", f"创建配置文件失败: {str(e)}")
                return

        # 调用open_file方法打开配置文件
        self.open_file(ConfigFilePath)

    def set_auto_save_interval(self):
        """设置自动保存间隔"""
        try:
            # 创建自定义对话框
            dialog = tk.Toplevel(self.root)
            dialog.title("设置自动保存间隔")
            dialog.geometry("700x300")  # 增加窗口大小以更好地显示所有元素
            dialog.resizable(False, False)
            dialog.transient(self.root)
            dialog.grab_set()

            # 使用用户设置的字体
            user_font = (self.font_family, 10, "bold")
            user_font_bold = (self.font_family, 10, "bold")
            user_font_small = (self.font_family, 10, "bold")

            # 设置对话框样式
            style = ttk.Style()
            style.configure("AutoSaveDialog.TLabel", font=user_font)
            style.configure("CurrentValue.TLabel", font=user_font_bold)
            style.configure("Small.TButton", font=(self.font_family, 8))

            # 居中显示对话框
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
            y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")

            # 创建主框架
            main_frame = ttk.Frame(dialog, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)

            # 添加说明标签
            title_label = ttk.Label(
                main_frame, text="自动保存间隔设置", style="AutoSaveDialog.TLabel"
            )
            title_label.pack(pady=(0, 15))

            # 添加说明标签
            desc_label = ttk.Label(main_frame, text="请选择自动保存间隔时间:")
            desc_label.pack(pady=(0, 10))

            # 创建滑块框架
            slider_frame = ttk.Frame(main_frame)
            slider_frame.pack(fill=tk.X, pady=(0, 15))

            # 当前值显示
            current_value_label = ttk.Label(
                slider_frame,
                text=f"当前值: {self.auto_save_interval}秒({self.auto_save_interval}秒)",
                style="CurrentValue.TLabel",
            )
            current_value_label.pack(pady=(0, 10))

            # 滑块组件
            slider = ttk.Scale(
                slider_frame,
                from_=3,  # 最小值3秒
                to=3600,  # 最大值3600秒（1小时）
                orient=tk.HORIZONTAL,
                length=500,  # 增加滑块长度
                value=self.auto_save_interval,
            )
            slider.pack(pady=(0, 5))

            # 数值显示框架
            value_frame = ttk.Frame(slider_frame)
            value_frame.pack(fill=tk.X, pady=(10, 0))

            # 最小值标签
            min_label = ttk.Label(value_frame, text="3秒", foreground="gray")
            min_label.pack(side=tk.LEFT)

            # 常用值按钮框架
            common_values_frame = ttk.Frame(value_frame)
            common_values_frame.pack(side=tk.LEFT, padx=(20, 0))

            # 添加常用值按钮
            def set_slider_value(value):
                """设置滑块值并更新显示"""
                slider.set(value)
                update_value_label(value)

            # 3秒按钮
            btn_3s = ttk.Button(
                common_values_frame,
                text="3秒",
                style="Small.TButton",
                command=lambda: set_slider_value(3),
            )
            btn_3s.pack(side=tk.LEFT, padx=(0, 5))

            # 5秒按钮
            btn_5s = ttk.Button(
                common_values_frame,
                text="5秒",
                style="Small.TButton",
                command=lambda: set_slider_value(5),
            )
            btn_5s.pack(side=tk.LEFT, padx=(0, 5))

            # 15秒按钮
            btn_15s = ttk.Button(
                common_values_frame,
                text="15秒",
                style="Small.TButton",
                command=lambda: set_slider_value(15),
            )
            btn_15s.pack(side=tk.LEFT, padx=(0, 5))

            # 30秒按钮
            btn_30s = ttk.Button(
                common_values_frame,
                text="30秒",
                style="Small.TButton",
                command=lambda: set_slider_value(30),
            )
            btn_30s.pack(side=tk.LEFT, padx=(0, 5))

            # 5分钟按钮
            btn_5m = ttk.Button(
                common_values_frame,
                text="5分钟",
                style="Small.TButton",
                command=lambda: set_slider_value(300),
            )
            btn_5m.pack(side=tk.LEFT, padx=(0, 5))

            # 15分钟按钮
            btn_15m = ttk.Button(
                common_values_frame,
                text="15分钟",
                style="Small.TButton",
                command=lambda: set_slider_value(900),
            )
            btn_15m.pack(side=tk.LEFT)

            # 最大值标签
            max_label = ttk.Label(value_frame, text="60分钟", foreground="gray")
            max_label.pack(side=tk.RIGHT)

            # 实时更新当前值显示
            def update_value_label(val):
                # 将浮点数转换为整数
                val = int(float(val))
                display_val = val

                # 根据数值大小调整显示单位
                if val >= 3600:  # 1小时或以上
                    hours = val // 3600
                    minutes = (val % 3600) // 60
                    if minutes == 0:
                        display_val = f"{hours}小时"
                    else:
                        display_val = f"{hours}小时{minutes}分钟"
                elif val >= 60:  # 1分钟或以上
                    minutes = val // 60
                    seconds = val % 60
                    if seconds == 0:
                        display_val = f"{minutes}分钟"
                    else:
                        display_val = f"{minutes}分钟{seconds}秒"
                else:  # 秒数
                    display_val = f"{val}秒"

                current_value_label.config(text=f"当前值: {display_val}({val}秒)")

            # 绑定滑块事件
            slider.configure(command=update_value_label)

            # 按钮框架
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=(10, 0))

            # 添加提示信息
            info_label = ttk.Label(
                button_frame,
                text="提示: 值越小保存越频繁，可能影响编辑器性能",
                font=user_font_small,
                foreground="gray",
            )
            info_label.pack(side=tk.LEFT, pady=(0, 5))

            # 按钮子框架
            buttons_frame = ttk.Frame(button_frame)
            buttons_frame.pack(side=tk.RIGHT)

            # 确定按钮
            def on_ok():
                interval = int(slider.get())
                self.auto_save_interval = interval
                self.save_config()
                # 更新状态栏显示
                self.show_default_auto_save_status()
                if self.auto_save_enabled:
                    self.stop_auto_save_timer()
                    self.start_auto_save_timer()
                dialog.destroy()
                # 使用辅助方法格式化显示
                display_interval = self.format_auto_save_interval(interval)
                messagebox.showinfo(
                    "设置成功", f"自动保存间隔已设置为{display_interval}"
                )

            ok_button = ttk.Button(buttons_frame, text="确定", command=on_ok, width=10)
            ok_button.pack(side=tk.RIGHT, padx=(5, 0))

            # 取消按钮
            def on_cancel():
                dialog.destroy()

            cancel_button = ttk.Button(
                buttons_frame, text="取消", command=on_cancel, width=10
            )
            cancel_button.pack(side=tk.RIGHT)

            # 初始化显示
            update_value_label(self.auto_save_interval)

            # 等待对话框关闭
            dialog.wait_window()

        except Exception as e:
            messagebox.showerror("错误", f"设置自动保存间隔时出错: {str(e)}")

    def change_theme(self, theme_name):
        """切换主题"""
        # 设置主题
        self.theme_manager.set_theme(theme_name)
        # 更新当前主题
        self.current_theme = theme_name
        # 保存主题配置
        self.save_config()

    def cycle_theme(self):
        """循环切换主题"""
        # 定义主题列表，保持与菜单中一致的顺序
        themes = [
            "light",
            "dark",
            "blue",
            "parchment",
            "green",
            "midnight_purple",
            "sunset",
        ]

        # 找到当前主题在列表中的位置
        try:
            current_index = themes.index(self.current_theme)
            # 计算下一个主题的索引
            next_index = (current_index + 1) % len(themes)
            next_theme = themes[next_index]
        except ValueError:
            # 如果当前主题不在列表中，切换到第一个主题
            next_theme = themes[0]

        # 切换到下一个主题
        self.change_theme(next_theme)

        # 在状态栏显示切换信息
        theme_name = self.theme_manager.THEMES[next_theme].get("name", next_theme)
        self.left_status.config(text=f"主题已切换到: {theme_name}")

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
            self.schedule_line_number_update()

    def schedule_line_number_update(self, delay=50):
        """调度行号更新，实现防抖动机制"""
        # 取消之前的计划任务
        if hasattr(self, "_line_number_update_job"):
            self.root.after_cancel(self._line_number_update_job)

        # 计划新的更新任务
        self._line_number_update_job = self.root.after(delay, self.update_line_numbers)

    def update_line_numbers(self, event=None):
        """更新行号显示"""
        # 如果没有启用行号显示，直接返回
        if not getattr(self, "show_line_numbers", True):
            return

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
            # 只有当行数发生变化时才重新计算宽度
            if (
                not hasattr(self, "_cached_total_lines")
                or self._cached_total_lines != total_lines
            ):
                max_line_number = total_lines
                # 根据行号位数计算宽度：增加每数字宽度和额外空间确保行号能完整显示
                digits = len(str(max_line_number))
                line_number_width = max(40, digits * 13 + 10)
                self.line_numbers.config(width=line_number_width)
                # 缓存计算结果
                self._cached_line_number_width = line_number_width
                self._cached_total_lines = total_lines
            else:
                line_number_width = self._cached_line_number_width

            # 设置字体 (如果字体发生变化则更新)
            current_font = (self.font_family, self.font_size)
            if not hasattr(self, "_cached_font") or self._cached_font != current_font:
                self._cached_font = current_font

            # 绘制可见区域的行号
            for i in range(first_visible, last_visible + 1):
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
                        font=current_font,
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

        # 添加分隔线
        sep = ttk.Separator(self.toolbar, orient=tk.VERTICAL)
        sep.pack(side=tk.LEFT, padx=5, fill=tk.Y)

        # 字体效果按钮
        bold_btn = ttk.Button(self.toolbar, text="加粗", command=self.toggle_bold)
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

        overstrike_btn = ttk.Button(
            self.toolbar, text="删除线", command=self.toggle_overstrike
        )
        overstrike_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar_buttons.append(overstrike_btn)

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

        # 中间自动保存状态标签, 使用主题背景色和前景色
        self.center_status = tk.Label(
            self.statusbar_frame,
            text="",
            anchor=tk.CENTER,
            bg=theme["statusbar_bg"],
            fg=theme["statusbar_fg"],
        )
        self.center_status.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

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

                # 提升选择标记的优先级，确保选中内容背景色始终可见
                self.text_area.tag_raise("sel")
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

            # 高亮光标所在行
            self.highlight_cursor_line()

        except Exception as e:
            self.left_status.config(text="状态更新错误")

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
        self.root.bind("<Control-t>", lambda e: self.cycle_theme())  # 循环切换主题
        # 绑定PgUp和PgDn键用于页面滚动
        self.root.bind("<Prior>", lambda e: self.page_up())  # PgUp键
        self.root.bind("<Next>", lambda e: self.page_down())  # PgDn键

    def load_config(self):
        """加载配置文件"""
        if os.path.exists(ConfigFilePath):
            try:
                with open(ConfigFilePath, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.font_family = config.get("font_family", "Arial")
                    self.font_size = config.get("font_size", 12)
                    self.font_bold = config.get("font_bold", False)
                    self.font_italic = config.get("font_italic", False)
                    self.font_underline = config.get("font_underline", False)
                    self.font_overstrike = config.get("font_overstrike", False)
                    self.toolbar_visible = config.get("toolbar_visible", True)
                    # 加载行号显示状态
                    self.show_line_numbers = config.get("show_line_numbers", True)
                    # 加载语法高亮显示状态
                    self.syntax_highlighting_enabled = config.get(
                        "syntax_highlighting_enabled", True
                    )
                    # 加载主题配置
                    self.current_theme = config.get("current_theme", "light")
                    # 加载自动保存配置
                    self.auto_save_enabled = config.get("auto_save_enabled", False)
                    self.auto_save_interval = config.get("auto_save_interval", 5)
                    # 加载备份配置
                    self.backup_enabled = config.get("backup_enabled", True)

                # 同步更新字体样式变量的状态
                if hasattr(self, "bold_var"):
                    self.bold_var.set(self.font_bold)
                if hasattr(self, "italic_var"):
                    self.italic_var.set(self.font_italic)
                if hasattr(self, "underline_var"):
                    self.underline_var.set(self.font_underline)
                if hasattr(self, "overstrike_var"):
                    self.overstrike_var.set(self.font_overstrike)
                # 同步更新自动保存菜单变量的状态
                if hasattr(self, "auto_save_var"):
                    self.auto_save_var.set(self.auto_save_enabled)
                # 同步更新备份选项菜单变量的状态
                if hasattr(self, "backup_enabled_var"):
                    self.backup_enabled_var.set(self.backup_enabled)

            except Exception as e:
                print(f"加载配置文件时出错: {e}")
        else:
            # 配置文件不存在，保存默认配置
            self.save_config()

    def save_config(self):
        """保存配置文件"""
        config = {
            "font_family": self.font_family,
            "font_size": self.font_size,
            "font_bold": self.font_bold,
            "font_italic": self.font_italic,
            "font_underline": self.font_underline,
            "font_overstrike": self.font_overstrike,
            "toolbar_visible": self.toolbar_visible,
            "show_line_numbers": self.show_line_numbers,
            "syntax_highlighting_enabled": self.syntax_highlighting_enabled,
            "current_theme": self.current_theme,
            "auto_save_enabled": self.auto_save_enabled,
            "auto_save_interval": self.auto_save_interval,
            "backup_enabled": self.backup_enabled,
        }

        try:
            with open(ConfigFilePath, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存配置文件时出错: {e}")

    def update_font(self):
        """更新字体设置"""
        # 使用tkinter的font模块创建字体对象
        # 创建字体对象，直接设置所有样式属性
        font_config = font.Font(
            family=self.font_family,
            size=self.font_size,
            weight="bold" if self.font_bold else "normal",
            slant="italic" if self.font_italic else "roman",
            underline=self.font_underline,
            overstrike=self.font_overstrike,
        )

        # 应用字体到文本区域
        self.text_area.config(font=font_config)

        # 刷新UI确保样式正确应用
        self.text_area.update_idletasks()

        # 更新行号显示
        self.update_line_numbers()

    def highlight_cursor_line(self, event=None):
        """高亮光标所在行"""
        try:
            # 移除之前的光标行高亮
            self.text_area.tag_remove("cursor_line", "1.0", tk.END)

            # 获取光标当前位置
            cursor_pos = self.text_area.index(tk.INSERT)
            row, col = cursor_pos.split(".")

            # 为整行添加高亮标记（从行首到行尾+1字符，确保覆盖整行）
            start_pos = f"{row}.0"
            end_pos = f"{int(row)+1}.0"
            self.text_area.tag_add("cursor_line", start_pos, end_pos)
        except Exception as e:
            # 忽略错误, 保持程序稳定
            pass

    def on_line_number_hover(self, event):
        """处理行号区域鼠标悬停事件"""
        # 获取鼠标在canvas中的y坐标
        y = event.y

        # 获取文本区域中对应y坐标的行号
        text_index = self.text_area.index(f"@0,{y}")
        hovered_line = text_index.split(".")[0]

        # 高亮悬停行
        self.highlight_hovered_line(hovered_line)

    def on_line_number_leave(self, event):
        """处理鼠标离开行号区域事件"""
        # 移除悬停行高亮
        self.text_area.tag_remove("hover_line", "1.0", tk.END)
        # 移除行号区域的高亮矩形
        self.line_numbers.delete("hover_highlight")

    def highlight_hovered_line(self, line_number):
        """高亮鼠标悬停的行"""
        try:
            # 移除之前的悬停行高亮
            self.text_area.tag_remove("hover_line", "1.0", tk.END)

            # 移除行号区域之前的高亮矩形
            self.line_numbers.delete("hover_highlight")

            # 获取当前主题的悬停行背景色
            theme = self.theme_manager.get_current_theme()
            hover_bg = theme.get("hover_line_bg", "#e0e0e0")

            # 获取行号区域的宽度
            line_number_width = self.line_numbers.winfo_width()

            # 获取文本区域中该行的位置信息
            dlineinfo = self.text_area.dlineinfo(f"{line_number}.0")
            if dlineinfo:
                y_pos = dlineinfo[1]  # y坐标
                line_height = dlineinfo[3]  # 行高

                # 在行号区域绘制高亮矩形（覆盖整行宽度）
                self.line_numbers.create_rectangle(
                    0,
                    y_pos,
                    line_number_width,
                    y_pos + line_height,
                    fill=hover_bg,
                    outline=hover_bg,
                    tags="hover_highlight",
                )

            # 为文本区域整行添加悬停高亮标记
            start_pos = f"{line_number}.0"
            end_pos = f"{line_number}.end"
            self.text_area.tag_add("hover_line", start_pos, end_pos)
        except Exception as e:
            # 忽略错误, 保持程序稳定
            pass

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

    def check_and_handle_unsaved_changes(self, operation_type="关闭"):
        """检查并处理未保存的更改

        Args:
            operation_type (str): 操作类型，用于在对话框中显示（如"关闭"、"退出"等）

        Returns:
            tuple: (是否继续操作, 是否已保存)
        """
        # 检查文本框是否有内容
        content = self.text_area.get(1.0, tk.END).strip()
        saved = False

        # 情况1: 如果有打开的文件
        if self.current_file:
            # 情况1a: 打开文件且已被修改
            if content and self.text_area.edit_modified():
                title = f"{operation_type}确认"
                message = f"文档已被修改, 是否保存更改？"
                if operation_type == "退出":
                    message = f"文档已被修改, 是否保存后再{operation_type}？"

                result = messagebox.askyesnocancel(title, message)
                if result is True:  # 是, 保存
                    self.save_file()
                    saved = True
                elif result is False:  # 否, 不保存
                    pass  # 不保存直接继续
                else:  # 取消
                    return False, False  # 取消操作
        else:
            # 情况2: 没有打开文件 (新建文件或直接输入内容)
            if content:
                title = f"{operation_type}确认"
                message = f"文档有内容, 是否保存？"
                if operation_type == "退出":
                    message = f"文档有内容, 是否保存后再{operation_type}？"

                result = messagebox.askyesnocancel(title, message)
                if result is True:  # 是, 保存
                    self.save_file()
                    saved = True
                elif result is False:  # 否, 不保存
                    pass  # 不保存直接继续
                else:  # 取消
                    return False, False  # 取消操作

        return True, saved

    # 文件操作方法
    def close_file(self):
        """关闭当前文件"""
        # 使用公共方法检查并处理未保存的更改
        continue_operation, saved = self.check_and_handle_unsaved_changes("关闭")

        if not continue_operation:
            return  # 用户取消操作

        # 只有在用户选择保存时才清理备份文件
        if saved and self.current_file and self.auto_save_enabled:
            self.cleanup_backup()

        # 使用辅助方法重置文件状态
        self._reset_file_state()

        # 显示提示信息
        messagebox.showinfo("文件关闭", "文件已成功关闭")

    def new_file(self):
        """新建文件"""
        # 检查是否有未保存的更改
        continue_operation, _ = self.check_and_handle_unsaved_changes("新建")
        if not continue_operation:
            return  # 用户取消操作

        # 清理备份文件
        self.cleanup_backup()

        # 使用辅助方法重置文件状态
        self._reset_file_state()
        # 移除状态栏更新，因为_reset_file_state已经包含了这一步
        pass

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

    def open_file(self, file_path=None):
        """打开文件"""
        # 检查是否有未保存的更改
        continue_operation, _ = self.check_and_handle_unsaved_changes("打开")
        if not continue_operation:
            return  # 用户取消操作

        # 如果没有提供文件路径，则通过对话框选择
        if not file_path:
            file_path = filedialog.askopenfilename(
                defaultextension=".txt",
                filetypes=[("All Files", "*.*")],
            )

            # 如果用户取消选择文件，则返回
            if not file_path:
                return

        # 检查是否存在备份文件并询问用户
        self.current_file = file_path  # 临时设置current_file以便检查备份
        if self.backup_enabled:
            backup_file = file_path + ".bak"
            if os.path.exists(backup_file):
                # 提示用户是否恢复备份
                result = messagebox.askyesnocancel(
                    "发现备份文件",
                    f"检测到文件 '{os.path.basename(file_path)}' 的备份文件\n"
                    "您想要：\n"
                    "- 是：从备份文件恢复内容\n"
                    "- 否：打开原始文件并删除备份\n"
                    "- 取消：取消打开文件操作",
                )
                if result is None:  # 取消操作
                    self.current_file = None
                    return
                elif result is True:  # 从备份恢复
                    # 先保存当前current_file以便restore_from_backup使用
                    # 然后在主线程中处理恢复
                    self.root.after(0, self._handle_backup_restore)
                    return
                # 否：继续打开原始文件，并稍后删除备份

        # 重置取消标志
        self.file_read_cancelled = False

        # 创建进度窗口
        self._create_progress_window()

        # 在新线程中读取文件
        self.file_read_thread = threading.Thread(
            target=self._async_read_file, args=(file_path,), daemon=True
        )
        self.file_read_thread.start()

    def _handle_backup_restore(self):
        """处理备份文件恢复的回调方法"""
        if self.current_file:
            backup_file = self.current_file + ".bak"
            try:
                # 检测备份文件的编码和换行符
                encoding, line_ending = self.detect_file_encoding_and_line_ending(
                    backup_file
                )

                # 读取备份内容
                with open(backup_file, "r", encoding=encoding) as f:
                    content = f.read()

                # 复用_finish_open_file方法来处理文件内容，避免代码重复
                self._finish_open_file(
                    self.current_file, content, encoding, line_ending
                )

                messagebox.showinfo("恢复成功", "已从备份文件恢复内容")

                # 只有在文件存在时才删除
                if os.path.exists(backup_file):
                    # 恢复后删除备份文件
                    try:
                        os.remove(backup_file)
                    except Exception as e:
                        print(f"删除备份文件失败: {e}")

            except Exception as e:
                messagebox.showerror("恢复失败", f"从备份文件恢复时出错: {str(e)}")
                # 恢复失败后尝试打开原始文件
                self.open_file(self.current_file)

    def _create_progress_window(self):
        """创建文件读取进度窗口"""
        if self.progress_window and self.progress_window.winfo_exists():
            self.progress_window.lift()
            return

        self.progress_window = tk.Toplevel(self.root)
        self.progress_window.title("正在打开文件...")
        self.progress_window.geometry("300x100")
        self.progress_window.resizable(False, False)
        self.progress_window.transient(self.root)
        center_window(self.progress_window, 300, 100)

        # 设置为模态窗口，但允许主窗口响应
        self.progress_window.grab_set()

        # 添加标签和进度条
        label = ttk.Label(self.progress_window, text="正在读取文件内容...")
        label.pack(pady=10)

        self.progress_bar = ttk.Progressbar(self.progress_window, mode="indeterminate")
        self.progress_bar.pack(fill=tk.X, padx=20, pady=10)
        self.progress_bar.start()

        # 添加取消按钮
        cancel_button = ttk.Button(
            self.progress_window, text="取消", command=self._cancel_file_read
        )
        cancel_button.pack(pady=5)

        # 处理窗口关闭事件
        self.progress_window.protocol("WM_DELETE_WINDOW", self._cancel_file_read)

    def _cancel_file_read(self):
        """取消文件读取"""
        self.file_read_cancelled = True
        if self.progress_window and self.progress_window.winfo_exists():
            self.progress_window.destroy()
            self.progress_window = None

    def _close_progress_window(self):
        """关闭进度窗口"""
        if self.progress_window and self.progress_window.winfo_exists():
            self.progress_window.destroy()
        self.progress_window = None

    def _async_read_file(self, file_path):
        """异步读取文件内容"""
        try:
            # 检查文件大小
            file_size = os.path.getsize(file_path)
            if file_size > MaxFileSize:
                formatted_size = format_file_size(file_size)
                max_size = format_file_size(MaxFileSize)

                # 确保在主线程中显示错误消息
                def show_error():
                    messagebox.showerror(
                        "文件过大",
                        f"无法打开文件: {os.path.basename(file_path)}\n"
                        f"文件大小: {formatted_size}\n"
                        f"超过最大允许大小: {max_size}\n"
                        f"请使用其他专业编辑器打开此文件。",
                    )
                    self._close_progress_window()

                self.root.after(0, show_error)
                return

            # 检测文件编码和换行符类型
            encoding, line_ending = self.detect_file_encoding_and_line_ending(file_path)

            # 分块读取文件内容以避免内存问题
            content_chunks = []
            chunk_size = 8192  # 8KB chunks

            with open(file_path, "r", encoding=encoding) as file:
                while not self.file_read_cancelled:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    content_chunks.append(chunk)

            if self.file_read_cancelled:
                self.root.after(0, self._close_progress_window)
                return

            content = "".join(content_chunks)

            # 在主线程中更新UI
            self.root.after(
                0, self._finish_open_file, file_path, content, encoding, line_ending
            )
        except Exception as e:
            self.root.after(0, self._handle_file_read_error, str(e))
        finally:
            # 确保即使发生异常也清理线程引用
            if hasattr(self, "file_read_thread"):
                self.file_read_thread = None

    def _finish_open_file(self, file_path, content, encoding, line_ending):
        """完成文件打开过程"""
        try:
            # 关闭进度窗口
            self._close_progress_window()

            if self.file_read_cancelled:
                return

            self.text_area.delete(1.0, tk.END)  # 清空文本

            # 分块插入内容以避免GUI冻结
            self._insert_content_in_chunks(content)

            # 更新总行数
            self.total_lines = content.count("\n") + 1  # 计算总行数
            self.encoding = encoding
            self.line_ending = line_ending  # 更新换行符类型
            self.current_file = file_path  # 更新当前文件路径
            self.root.title(f"{os.path.basename(file_path)} - QuickEdit")
            self.text_area.edit_modified(False)  # 重置修改标志

            # 检查是否存在备份文件
            self.check_backup_file()

            # 如果启用了备份功能且存在备份文件，删除它
            # 这是处理用户选择"否"选项时的情况
            if self.backup_enabled:
                backup_file = file_path + ".bak"
                if os.path.exists(backup_file):
                    try:
                        os.remove(backup_file)
                    except Exception as e:
                        print(f"删除备份文件失败: {e}")

            # 如果处于只读模式, 设置文本区域为只读
            if self.readonly_mode:
                self.text_area.config(state=tk.DISABLED)
            else:
                self.text_area.config(state=tk.NORMAL)

            # 更新状态栏
            self.update_statusbar()

            # 延迟应用语法高亮以减少卡顿
            self.root.after(100, self._delayed_apply_syntax_highlighting, file_path)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件: {str(e)}")

    def _delayed_apply_syntax_highlighting(self, file_path):
        """延迟应用语法高亮"""
        try:
            # 检查是否启用了语法高亮并且是Python文件
            if self.syntax_highlighting_enabled and is_supported_file(
                SupportedExtensions, file_path
            ):
                self.apply_syntax_highlighting()
            else:
                self.remove_syntax_highlighting()
        except Exception as e:
            # 忽略语法高亮错误, 不影响文件打开
            pass

    def _insert_content_in_chunks(self, content, chunk_size=50000, update_frequency=5):
        """优化的分块插入方法

        Args:
            content: 要插入的内容
            chunk_size: 每块的大小，默认50000字符
            update_frequency: GUI更新频率，每N次插入后更新一次GUI
        """
        # 对于小文件，直接插入
        if len(content) <= chunk_size:
            self.text_area.insert(1.0, content)
            self.root.update_idletasks()
            return

        # 对于大文件，采用优化的分块插入策略
        try:
            # 1. 使用更大的块大小以减少插入次数
            start = 0
            update_counter = 0

            while start < len(content):
                end = min(start + chunk_size, len(content))
                chunk = content[start:end]

                # 2. 使用END标记进行追加插入，比计算位置更快
                self.text_area.insert(tk.END, chunk)
                start = end

                # 3. 减少GUI更新频率，按设定频率更新GUI
                update_counter += 1
                if update_counter % update_frequency == 0:
                    self.root.update_idletasks()

        finally:
            # 5. 刷新GUI
            self.root.update_idletasks()

    def _handle_file_read_error(self, error_message):
        """处理文件读取错误"""
        self._close_progress_window()
        messagebox.showerror("错误", f"无法打开文件: {error_message}")

    def _save_content_to_file(self, file_path, content, update_current_file=False):
        """将内容保存到指定文件路径的辅助方法

        Args:
            file_path: 目标文件路径
            content: 要保存的内容
            update_current_file: 是否更新当前文件路径

        Returns:
            bool: 保存是否成功
        """
        try:
            # 转换换行符格式
            converted_content = self.convert_line_endings(content, self.line_ending)
            with open(
                file_path, "w", encoding=self.encoding.lower(), newline=""
            ) as file:
                file.write(converted_content)

            # 如果需要，更新当前文件路径和窗口标题
            if update_current_file:
                self.current_file = file_path
                self.root.title(f"{os.path.basename(file_path)} - QuickEdit")

            return True, None
        except Exception as e:
            return False, str(e)

    def _check_save_conditions(self, silent=False):
        """检查保存条件的辅助方法

        Args:
            silent: 静默模式标志

        Returns:
            tuple: (是否可以保存, 内容)
        """
        # 检查是否处于只读模式
        if self.readonly_mode:
            if not silent:
                messagebox.showinfo("提示", "当前处于只读模式, 无法保存文件。")
            return False, None

        # 检查文本框是否有内容
        content = self.text_area.get(1.0, tk.END).strip()
        if not content:
            if not silent:
                messagebox.showinfo("提示", "文本框中没有内容, 请先输入内容再保存。")
            return False, None

        return True, content

    def save_file(self, silent=False):
        """保存文件

        Args:
            silent: 静默模式标志，为True时不显示消息提示，只更新状态栏
        """
        # 调用辅助方法检查保存条件
        can_save, content = self._check_save_conditions(silent)
        if not can_save:
            return False

        # 如果当前文件路径为空, 则调用save_as_file()方法(另存为)
        if not self.current_file:
            return self.save_as_file()

        # 调用辅助方法保存文件
        success, error_msg = self._save_content_to_file(self.current_file, content)

        if success:
            # 在Tkinter事件循环中更新UI, 避免命令冲突
            self.root.after(
                10, lambda: self._post_save_operations(self.current_file, silent)
            )
            return True
        else:
            if not silent:
                messagebox.showerror("错误", f"保存文件时出错: {error_msg}")
            return False

    def _post_save_operations(self, file_path, silent=False):
        """保存文件后的操作

        Args:
            file_path: 保存的文件路径
            silent: 静默模式标志
        """
        try:
            # 更新修改状态
            self.text_area.edit_modified(False)

            # 显示保存成功消息
            if not silent:
                messagebox.showinfo(
                    "保存成功",
                    f"文件已成功保存！\n编码格式: {self.encoding}\n换行符格式: {self.line_ending}",
                )
            else:
                # 静默模式下，只在状态栏显示简短信息
                self.update_statusbar()

            # 检查是否启用了语法高亮并且是Python文件
            if self.syntax_highlighting_enabled and is_supported_file(
                SupportedExtensions, file_path
            ):
                self.apply_syntax_highlighting()
            else:
                self.remove_syntax_highlighting()

            # 如果启用了备份功能，更新备份文件
            if self.backup_enabled and self.current_file:
                self.auto_save_to_backup()
                # 重置自动保存计时器，避免刚保存完又触发自动保存
                self.start_auto_save_timer()

        except Exception as e:
            messagebox.showerror("错误", f"保存后处理时出错: {str(e)}")

    def save_as_file(self):
        """另存为文件"""
        # 调用辅助方法检查保存条件
        can_save, content = self._check_save_conditions()
        if not can_save:
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("All Files", "*.*")],
        )

        if file_path:
            # 调用辅助方法保存文件，并更新当前文件路径
            success, error_msg = self._save_content_to_file(
                file_path, content, update_current_file=True
            )

            if success:
                # 在Tkinter事件循环中更新UI, 避免命令冲突
                self.root.after(10, self._post_save_operations, file_path)
            else:
                messagebox.showerror("错误", f"保存文件时出错: {error_msg}")

    def setup_auto_save(self):
        """设置自动保存相关配置"""
        # 确保auto_save_var和backup_enabled_var变量已存在且值正确
        if hasattr(self, "auto_save_var"):
            self.auto_save_var.set(self.auto_save_enabled)
        if hasattr(self, "backup_enabled_var"):
            self.backup_enabled_var.set(self.backup_enabled)

        # 监听窗口焦点变化，失去焦点时自动保存
        self.root.bind("<FocusOut>", self.on_focus_out)

        # 如果配置中启用了自动保存，则启动计时器
        if self.auto_save_enabled:
            self.start_auto_save_timer()

    def start_auto_save_timer(self):
        """启动自动保存计时器"""
        if self.auto_save_timer:
            self.root.after_cancel(self.auto_save_timer)

        if self.auto_save_enabled:
            self.auto_save_timer = self.root.after(
                self.auto_save_interval * 1000, self.perform_auto_save
            )

    def stop_auto_save_timer(self):
        """停止自动保存计时器"""
        if self.auto_save_timer:
            self.root.after_cancel(self.auto_save_timer)
            self.auto_save_timer = None

    def perform_auto_save(self):
        """执行自动保存操作"""
        if not self.auto_save_enabled or not self.current_file or self.readonly_mode:
            return

        # 检查文件是否有修改
        if self.text_area.edit_modified():
            # 创建异步线程执行保存
            save_thread = threading.Thread(target=self.async_auto_save)
            save_thread.daemon = True
            save_thread.start()

        # 继续下一次自动保存计时
        self.start_auto_save_timer()

    def async_auto_save(self):
        """异步执行自动保存操作"""
        # 使用锁确保同一时间只有一个保存操作
        with self.save_lock:
            if self.is_saving:
                return

            self.is_saving = True
            try:
                # 执行保存操作
                success = self.save_file(silent=True)

                # 更新UI状态（需要在主线程中执行）
                if success:
                    self.root.after(
                        0, lambda: self.update_auto_save_status(True, "自动保存成功")
                    )
            except Exception as e:
                print(f"自动保存时出错: {str(e)}")
                # 在主线程中显示错误
                self.root.after(
                    0, lambda: self.left_status.config(text=f"自动保存失败: {str(e)}")
                )
            finally:
                self.is_saving = False

    def auto_save_to_backup(self):
        """保存到备份文件"""
        if not self.current_file or not self.backup_enabled:
            return

        try:
            # 确保current_file是有效的字符串且文件存在
            if (
                not isinstance(self.current_file, str)
                or not self.current_file
                or not os.path.exists(self.current_file)
            ):
                raise ValueError("无效的文件路径或文件不存在")

            # 构建备份文件路径
            backup_file = self.current_file + ".bak"

            # 确保备份文件所在目录存在
            backup_dir = os.path.dirname(backup_file)
            if backup_dir and not os.path.exists(backup_dir):
                os.makedirs(backup_dir, exist_ok=True)

            # 优化：直接复制已保存的文件到备份，避免重复读取和处理内容
            # 使用shutil.copy2保留文件元数据
            shutil.copy2(self.current_file, backup_file)

            # 更新最后自动保存时间
            self.last_auto_save_time = datetime.datetime.now()

            # 在主线程更新状态栏
            self.root.after(0, self.update_auto_save_status, True, "自动保存完成")
        except Exception as e:
            print(f"备份失败: {e}")
            error_msg = f"备份失败: {str(e)}"
            self.root.after(
                0,
                self.update_auto_save_status,
                False,
                error_msg[:30] + "..." if len(error_msg) > 30 else error_msg,
            )

    def update_auto_save_status(self, success, message):
        """更新状态栏显示自动保存状态"""
        # 如果有临时消息（如保存完成或失败）
        if hasattr(self, "center_status"):
            # 获取当前主题的背景色，确保与状态栏保持一致
            theme = self.theme_manager.get_current_theme()
            bg_color = theme["statusbar_bg"]

            if message:
                # 根据消息类型使用不同的图标和颜色
                if success:
                    temp_icon = "✓"  # 成功标记
                    color = "green"  # 成功使用绿色
                else:
                    temp_icon = "!"  # 错误标记
                    color = "red"  # 错误使用红色

                # 构建临时消息文本
                temp_text = f"自动保存: {temp_icon} {message}"
                self.center_status.config(text=temp_text, fg=color, bg=bg_color)

                # 3秒后恢复正常的自动保存状态显示
                self.root.after(3000, self.reset_center_status)
            else:
                # 显示默认的自动保存状态
                self.show_default_auto_save_status()

        # 同时移除左侧状态栏中可能存在的自动保存信息（兼容旧版本）
        if hasattr(self, "left_status"):
            current_text = self.left_status.cget("text")
            # 移除左侧状态栏中的自动保存信息
            current_text = re.sub(r" \[自动保存:.*?\]", "", current_text)
            self.left_status.config(text=current_text)

    def show_default_auto_save_status(self):
        """显示默认的自动保存状态"""
        if hasattr(self, "center_status"):
            # 获取当前主题的前景色和背景色，确保与状态栏保持一致
            theme = self.theme_manager.get_current_theme()
            default_color = theme["statusbar_fg"]
            bg_color = theme["statusbar_bg"]

            # 为不同状态设置不同的样式和图标
            if self.auto_save_enabled:
                status_icon = "●"  # 实心圆点表示启用
                time_str = (
                    self.last_auto_save_time.strftime("%H:%M:%S")
                    if self.last_auto_save_time
                    else "从未"
                )

                # 使用辅助方法格式化显示
                display_interval = self.format_auto_save_interval(
                    self.auto_save_interval
                )

                # 使用简洁的格式显示自动保存状态，包含间隔信息
                auto_save_info = (
                    f"自动保存: {status_icon} {time_str} (间隔{display_interval})"
                )
            else:
                status_icon = "○"  # 空心圆点表示禁用
                auto_save_info = f"自动保存: {status_icon} 已禁用"

            # 更新居中状态栏，同时设置前景色和背景色
            self.center_status.config(
                text=auto_save_info, fg=default_color, bg=bg_color
            )

    def reset_center_status(self):
        """重置居中状态栏到默认状态"""
        self.show_default_auto_save_status()

    def on_focus_out(self, event=None):
        """窗口失去焦点时触发自动保存"""
        if self.auto_save_enabled and self.current_file and not self.readonly_mode:
            self.perform_auto_save()

    def check_backup_file(self):
        """检查是否存在备份文件"""
        # 只有在启用了备份功能时才检查备份文件
        if not self.backup_enabled or not self.current_file:
            return False

        backup_file = self.current_file + ".bak"
        return os.path.exists(backup_file)

    def restore_from_backup(self):
        """从备份文件恢复"""
        # 只有在启用了备份功能时才尝试恢复备份文件
        if not self.backup_enabled or not self.current_file:
            return False

        backup_file = self.current_file + ".bak"
        if not os.path.exists(backup_file):
            messagebox.showinfo("恢复失败", "没有找到备份文件")
            return False

        try:
            # 读取备份文件内容
            with open(backup_file, "r", encoding=self.encoding) as f:
                content = f.read()

            # 处理换行符
            if self.line_ending == "LF":
                content = content.replace("\r\n", "\n").replace("\r", "\n")
            elif self.line_ending == "CRLF":
                content = (
                    content.replace("\r\n", "\n")
                    .replace("\r", "\n")
                    .replace("\n", "\r\n")
                )
            elif self.line_ending == "CR":
                content = (
                    content.replace("\r\n", "\n")
                    .replace("\r", "\n")
                    .replace("\n", "\r")
                )

            # 清空当前文本并插入备份内容
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", content)

            # 更新UI
            self.update_line_numbers()
            self.update_statusbar()

            messagebox.showinfo("恢复成功", "已从备份文件恢复内容")
            return True
        except Exception as e:
            messagebox.showerror("恢复失败", f"从备份文件恢复时出错: {e}")
            return False

    def cleanup_backup(self):
        """清理备份文件（正常退出时）"""
        # 只有在启用了备份功能时才清理备份文件
        if not self.backup_enabled or not self.current_file:
            return

        backup_file = self.current_file + ".bak"
        if os.path.exists(backup_file):
            try:
                os.remove(backup_file)
            except Exception as e:
                print(f"清理备份文件失败: {e}")

    def exit_app(self):
        """退出应用程序"""
        # 停止自动保存计时器
        self.stop_auto_save_timer()

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
                        # 如果保存成功，清理备份文件
                        self.cleanup_backup()
                        self.root.destroy()
                elif result is False:  # 否, 直接退出
                    # 不保存直接退出时，保留备份文件（如果有）
                    self.root.destroy()
                # 如果点击取消, 则不执行任何操作, 继续留在编辑器中
            else:
                # 情况1b: 打开文件但未被修改, 直接退出
                # 未修改时清理备份文件
                self.cleanup_backup()
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

    def page_up(self):
        """向上翻页"""
        self.text_area.yview_scroll(-1, "pages")
        self.text_area.focus_set()
        self.update_statusbar()

    def page_down(self):
        """向下翻页"""
        self.text_area.yview_scroll(1, "pages")
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
        """切换粗体 - 如果有选中文本则只应用到选中部分，否则更新全局设置"""
        # 检查是否有选中文本
        try:
            selected_text = self.text_area.tag_ranges(tk.SEL)
            if selected_text:  # 如果有选中文本
                # 获取选中文本的开始和结束位置
                start, end = selected_text

                # 获取当前选中区域的字体配置
                current_tags = self.text_area.tag_names(start)

                # 判断是否已经是粗体
                is_bold = any(tag.startswith("bold_") for tag in current_tags)

                if is_bold:  # 如果已经是粗体，则移除粗体效果
                    for tag in current_tags:
                        if tag.startswith("bold_"):
                            self.text_area.tag_remove(tag, start, end)
                else:  # 否则添加粗体效果
                    # 创建或获取粗体标签
                    bold_tag = "bold_tag"
                    if bold_tag not in self.text_area.tag_names():
                        # 配置粗体标签的字体样式
                        bold_font = font.Font(
                            self.text_area, self.text_area.cget("font")
                        )
                        bold_font.configure(weight="bold")
                        self.text_area.tag_configure(bold_tag, font=bold_font)

                    # 应用粗体标签到选中文本
                    self.text_area.tag_add(bold_tag, start, end)
            else:  # 如果没有选中文本，更新全局设置
                self.font_bold = not self.font_bold
                self.bold_var.set(self.font_bold)  # 同步更新菜单项状态
                self.update_font()
                self.save_config()
        except Exception as e:
            print(f"应用粗体效果时出错: {e}")
            # 如果出错，回退到全局设置更新
            self.font_bold = not self.font_bold
            self.bold_var.set(self.font_bold)
            self.update_font()
            self.save_config()

    def toggle_italic(self):
        """切换斜体 - 如果有选中文本则只应用到选中部分，否则更新全局设置"""
        # 检查是否有选中文本
        try:
            selected_text = self.text_area.tag_ranges(tk.SEL)
            if selected_text:  # 如果有选中文本
                # 获取选中文本的开始和结束位置
                start, end = selected_text

                # 获取当前选中区域的字体配置
                current_tags = self.text_area.tag_names(start)

                # 判断是否已经是斜体
                is_italic = any(tag.startswith("italic_") for tag in current_tags)

                if is_italic:  # 如果已经是斜体，则移除斜体效果
                    for tag in current_tags:
                        if tag.startswith("italic_"):
                            self.text_area.tag_remove(tag, start, end)
                else:  # 否则添加斜体效果
                    # 创建或获取斜体标签
                    italic_tag = "italic_tag"
                    if italic_tag not in self.text_area.tag_names():
                        # 配置斜体标签的字体样式
                        italic_font = font.Font(
                            self.text_area, self.text_area.cget("font")
                        )
                        italic_font.configure(slant="italic")
                        self.text_area.tag_configure(italic_tag, font=italic_font)

                    # 应用斜体标签到选中文本
                    self.text_area.tag_add(italic_tag, start, end)
            else:  # 如果没有选中文本，更新全局设置
                self.font_italic = not self.font_italic
                self.italic_var.set(self.font_italic)  # 同步更新菜单项状态
                self.update_font()
                self.save_config()
        except Exception as e:
            print(f"应用斜体效果时出错: {e}")
            # 如果出错，回退到全局设置更新
            self.font_italic = not self.font_italic
            self.italic_var.set(self.font_italic)
            self.update_font()
            self.save_config()

    def toggle_underline(self):
        """切换下划线 - 如果有选中文本则只应用到选中部分，否则更新全局设置"""
        # 检查是否有选中文本
        try:
            selected_text = self.text_area.tag_ranges(tk.SEL)
            if selected_text:  # 如果有选中文本
                # 获取选中文本的开始和结束位置
                start, end = selected_text

                # 获取当前选中区域的字体配置
                current_tags = self.text_area.tag_names(start)

                # 判断是否已经有下划线
                is_underlined = any(
                    tag.startswith("underline_") for tag in current_tags
                )

                if is_underlined:  # 如果已经有下划线，则移除下划线效果
                    for tag in current_tags:
                        if tag.startswith("underline_"):
                            self.text_area.tag_remove(tag, start, end)
                else:  # 否则添加下划线效果
                    # 创建或获取下划线标签
                    underline_tag = "underline_tag"
                    if underline_tag not in self.text_area.tag_names():
                        # 配置下划线标签的字体样式
                        underline_font = font.Font(
                            self.text_area, self.text_area.cget("font")
                        )
                        underline_font.configure(underline=1)
                        self.text_area.tag_configure(underline_tag, font=underline_font)

                    # 应用下划线标签到选中文本
                    self.text_area.tag_add(underline_tag, start, end)
            else:  # 如果没有选中文本，更新全局设置
                self.font_underline = not self.font_underline
                self.underline_var.set(self.font_underline)  # 同步更新菜单项状态
                self.update_font()
                self.save_config()
        except Exception as e:
            print(f"应用下划线效果时出错: {e}")
            # 如果出错，回退到全局设置更新
            self.font_underline = not self.font_underline
            self.underline_var.set(self.font_underline)
            self.update_font()
            self.save_config()

    def toggle_overstrike(self):
        """切换删除线 - 如果有选中文本则只应用到选中部分，否则更新全局设置"""
        # 检查是否有选中文本
        try:
            selected_text = self.text_area.tag_ranges(tk.SEL)
            if selected_text:  # 如果有选中文本
                # 获取选中文本的开始和结束位置
                start, end = selected_text

                # 获取当前选中区域的字体配置
                current_tags = self.text_area.tag_names(start)

                # 判断是否已经有删除线
                is_overstruck = any(
                    tag.startswith("overstrike_") for tag in current_tags
                )

                if is_overstruck:  # 如果已经有删除线，则删除删除线效果
                    for tag in current_tags:
                        if tag.startswith("overstrike_"):
                            self.text_area.tag_remove(tag, start, end)
                else:  # 否则添加删除线效果
                    # 创建或获取删除线标签
                    overstrike_tag = "overstrike_tag"
                    if overstrike_tag not in self.text_area.tag_names():
                        # 配置删除线标签的字体样式
                        overstrike_font = font.Font(
                            self.text_area, self.text_area.cget("font")
                        )
                        overstrike_font.configure(overstrike=1)
                        self.text_area.tag_configure(
                            overstrike_tag, font=overstrike_font
                        )

                    # 应用删除线标签到选中文本
                    self.text_area.tag_add(overstrike_tag, start, end)
            else:  # 如果没有选中文本，更新全局设置
                self.font_overstrike = not self.font_overstrike
                self.overstrike_var.set(self.font_overstrike)  # 同步更新菜单项状态
                self.update_font()
                self.save_config()
        except Exception as e:
            print(f"应用删除线效果时出错: {e}")
            # 如果出错，回退到全局设置更新
            self.font_overstrike = not self.font_overstrike
            self.overstrike_var.set(self.font_overstrike)
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
                continue_operation, _ = self.check_and_handle_unsaved_changes("打开")
                if not continue_operation:
                    return  # 用户取消操作

                # 只处理第一个文件
                file_path = files[0]
                # 检查是否为文件
                if os.path.isfile(file_path):
                    self.open_file(file_path)
                elif os.path.isdir(file_path):
                    # 如果是目录, 显示提示
                    messagebox.showinfo("提示", "拖拽的是目录, 请拖拽文件以打开")
                else:
                    messagebox.showwarning("警告", "无法识别拖拽的项目")

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

    def show_context_menu(self, event):
        """显示上下文菜单（鼠标右键菜单）"""
        # 创建上下文菜单
        context_menu = tk.Menu(self.root, tearoff=0)

        # 添加撤销和重做选项
        context_menu.add_command(
            label="撤销", command=self.text_area.edit_undo, accelerator="Ctrl+Z"
        )
        context_menu.add_command(
            label="重做", command=self.text_area.edit_redo, accelerator="Ctrl+Y"
        )
        context_menu.add_separator()

        # 添加剪切、复制、粘贴和全选选项
        context_menu.add_command(
            label="剪切", command=self.cut_text, accelerator="Ctrl+X"
        )
        context_menu.add_command(
            label="复制", command=self.copy_text, accelerator="Ctrl+C"
        )
        context_menu.add_command(
            label="粘贴", command=self.paste_text, accelerator="Ctrl+V"
        )
        context_menu.add_separator()

        context_menu.add_command(
            label="全选", command=self.select_all, accelerator="Ctrl+A"
        )
        context_menu.add_separator()

        # 添加查找和替换选项
        context_menu.add_command(
            label="查找", command=self.show_find_dialog, accelerator="Ctrl+F"
        )
        context_menu.add_command(
            label="替换", command=self.replace_text, accelerator="Ctrl+H"
        )
        context_menu.add_separator()

        # 添加字体效果选项
        context_menu.add_checkbutton(
            label="粗体", command=self.toggle_bold, variable=self.bold_var
        )
        context_menu.add_checkbutton(
            label="斜体", command=self.toggle_italic, variable=self.italic_var
        )
        context_menu.add_checkbutton(
            label="下划线", command=self.toggle_underline, variable=self.underline_var
        )
        context_menu.add_checkbutton(
            label="删除线", command=self.toggle_overstrike, variable=self.overstrike_var
        )

        # 在鼠标位置显示菜单
        context_menu.post(event.x_root, event.y_root)

    def show_about(self):
        """显示关于信息"""
        messagebox.showinfo(
            "关于QuickEdit",
            "功能特点:\n"
            "- 文件操作: 新建、打开、保存、另存为、关闭文件\n"
            "- 编码支持: UTF-8、UTF-16、GBK、GB2312、ASCII、ISO-8859-1\n"
            "- 换行符支持: LF、CRLF、CR\n"
            "- 编辑功能: 撤销、重做、复制、剪切、粘贴、全选\n"
            "- 查找替换: 文本查找和替换\n"
            "- 格式设置: 字体、大小、粗体、斜体、下划线\n"
            "- 快捷键支持\n\n",
        )
