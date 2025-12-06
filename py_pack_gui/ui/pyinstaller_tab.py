"""
PyInstaller标签页模块
提供PyInstaller打包参数配置界面
"""

import tkinter as tk
from tkinter import filedialog
from tkinter import font as tk_font
import customtkinter as ctk
from core.pyinstaller_config import PyInstallerConfig
from utils.pyinstaller_utils import (
    browse_script_file, browse_directory, browse_icon_file, 
    browse_data_file, browse_binary_file, get_script_name,
    validate_data_file_format, format_data_file_entry, parse_data_file_entry,
    show_error, show_info
)


class PyInstallerTab:
    """PyInstaller标签页类"""
    
    def __init__(self, parent, main_window, font_family="Microsoft YaHei UI"):
        """初始化PyInstaller标签页
        
        Args:
            parent: 父容器
            main_window: 主窗口引用
            font_family: 字体族名称
        """
        self.parent = parent
        self.main_window = main_window
        self.font_family = font_family
        
        # 设置字体
        self.default_font = ctk.CTkFont(family=self.font_family, size=12)
        self.title_font = ctk.CTkFont(family=self.font_family, size=14, weight="bold")
        self.button_font = ctk.CTkFont(family=self.font_family, size=12, weight="bold")
        self.primary_button_font = ctk.CTkFont(family=self.font_family, size=14, weight="bold")
        
        # 列表字体
        self.listbox_font = tk_font.Font(family=self.font_family, size=18, weight="bold")
        
        # 初始化配置
        self.config = PyInstallerConfig()
        
        # 创建界面
        self.create_ui()
    
    def create_ui(self):
        """创建用户界面"""
        # 创建选项卡视图
        self.tabview = ctk.CTkTabview(self.parent)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 设置子标签页标题字体
        self.tabview._segmented_button.configure(font=self.title_font)
        
        # 创建基础选项卡
        self.create_basic_tab()
        
        # 创建高级选项卡
        self.create_advanced_tab()
        
        # 创建文件选项卡
        self.create_files_tab()
        
        # 创建构建选项卡
        self.create_build_tab()
    
    def create_browse_button(self, parent, text, command, width=80):
        """创建浏览按钮（次要功能）"""
        return ctk.CTkButton(
            parent, 
            text=text, 
            command=command, 
            width=width,
            font=self.button_font,
            fg_color="#6366F1",  # 紫蓝色背景
            hover_color="#4F46E5",  # 悬停时更深的紫蓝色
            text_color="white",
            border_width=1,
            border_color="#4F46E5"
        )
    
    def create_add_button(self, parent, text, command, width=80):
        """创建添加按钮（一般功能）"""
        return ctk.CTkButton(
            parent, 
            text=text, 
            command=command, 
            width=width,
            font=self.button_font,
            fg_color="#3B82F6",  # 蓝色背景
            hover_color="#2563EB",  # 悬停时更深的蓝色
            text_color="white",
            border_width=1,
            border_color="#2563EB"
        )
    
    def create_remove_button(self, parent, text, command, width=100):
        """创建移除按钮（警告功能）"""
        return ctk.CTkButton(
            parent, 
            text=text, 
            command=command, 
            width=width,
            font=self.button_font,
            fg_color="#F59E0B",  # 橙色背景
            hover_color="#D97706",  # 悬停时更深的橙色
            text_color="white",
            border_width=1,
            border_color="#D97706"
        )
    
    def create_clear_button(self, parent, text, command, width=100):
        """创建清空按钮（危险功能）"""
        return ctk.CTkButton(
            parent, 
            text=text, 
            command=command, 
            width=width,
            font=self.button_font,
            fg_color="#EF4444",  # 红色背景
            hover_color="#DC2626",  # 悬停时更深的红色
            text_color="white",
            border_width=1,
            border_color="#DC2626"
        )
    
    def create_primary_button(self, parent, text, command, width=200, height=None):
        """创建主要按钮（最重要功能）"""
        return ctk.CTkButton(
            parent, 
            text=text, 
            command=command, 
            width=width,
            height=height,
            font=self.primary_button_font,
            fg_color="#10B981",  # 绿色背景
            hover_color="#059669",  # 悬停时更深的绿色
            text_color="white",
            border_width=2,
            border_color="#059669"
        )
    
    def create_basic_tab(self):
        """创建基础选项卡"""
        self.basic_tab = self.tabview.add("基础设置")
        
        # 创建滚动框架，设置为浅灰色背景
        scroll_frame = ctk.CTkScrollableFrame(self.basic_tab, fg_color="#F5F5F5")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 入口文件路径
        script_frame = ctk.CTkFrame(scroll_frame, fg_color="white", corner_radius=8, border_width=1, border_color="#E0E0E0")
        script_frame.pack(fill="x", pady=(0, 15))
        
        script_label = ctk.CTkLabel(script_frame, text="入口文件路径/启动文件路径:", font=self.title_font)
        script_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        script_input_frame = ctk.CTkFrame(script_frame, fg_color="white")
        script_input_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.script_entry = ctk.CTkEntry(script_input_frame, placeholder_text="选择要打包的Python脚本")
        self.script_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        
        script_browse_btn = self.create_browse_button(script_input_frame, "浏览", self.browse_script)
        script_browse_btn.pack(side="right", padx=(0, 10), pady=10)
        
        # 应用名称
        name_frame = ctk.CTkFrame(scroll_frame, fg_color="white", corner_radius=8, border_width=1, border_color="#E0E0E0")
        name_frame.pack(fill="x", pady=(0, 15))
        
        name_label = ctk.CTkLabel(name_frame, text="应用名称:", font=self.title_font)
        name_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.name_entry = ctk.CTkEntry(name_frame, placeholder_text="打包后的应用名称（可选）")
        self.name_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # 打包模式
        mode_frame = ctk.CTkFrame(scroll_frame, fg_color="white", corner_radius=8, border_width=1, border_color="#E0E0E0")
        mode_frame.pack(fill="x", pady=(0, 15))
        
        mode_label = ctk.CTkLabel(mode_frame, text="打包模式:", font=self.title_font)
        mode_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        mode_options_frame = ctk.CTkFrame(mode_frame, fg_color="white")
        mode_options_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.mode_var = tk.StringVar(value="onedir")
        onedir_radio = ctk.CTkRadioButton(mode_options_frame, text="目录模式 (创建一个包含可执行文件的程序目录, 性能更好)", variable=self.mode_var, value="onedir")
        onedir_radio.pack(anchor="w", padx=10, pady=5)
        
        onefile_radio = ctk.CTkRadioButton(mode_options_frame, text="单文件模式 (创建单个可执行文件, 执行时解压到系统的临时目录中, 性能较差但更易分发)", variable=self.mode_var, value="onefile")
        onefile_radio.pack(anchor="w", padx=10, pady=5)
        
        # 控制台选项
        console_frame = ctk.CTkFrame(scroll_frame, fg_color="white", corner_radius=8, border_width=1, border_color="#E0E0E0")
        console_frame.pack(fill="x", pady=(0, 15))
        
        console_label = ctk.CTkLabel(console_frame, text="控制台选项:", font=self.title_font)
        console_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        console_options_frame = ctk.CTkFrame(console_frame, fg_color="white")
        console_options_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.console_var = tk.BooleanVar(value=False)
        console_check = ctk.CTkCheckBox(console_options_frame, text="显示控制台窗口", variable=self.console_var)
        console_check.pack(anchor="w", padx=10, pady=5)
        
        # 输出目录
        output_frame = ctk.CTkFrame(scroll_frame, fg_color="white", corner_radius=8, border_width=1, border_color="#E0E0E0")
        output_frame.pack(fill="x", pady=(0, 15))
        
        output_label = ctk.CTkLabel(output_frame, text="输出目录:", font=self.title_font)
        output_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        output_input_frame = ctk.CTkFrame(output_frame, fg_color="white")
        output_input_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.output_entry = ctk.CTkEntry(output_input_frame, placeholder_text="打包后应用的输出目录（默认：./dist）")
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        
        output_browse_btn = self.create_browse_button(output_input_frame, "浏览", self.browse_output)
        output_browse_btn.pack(side="right", padx=(0, 10), pady=10)
        
        # 图标文件
        icon_frame = ctk.CTkFrame(scroll_frame, fg_color="white", corner_radius=8, border_width=1, border_color="#E0E0E0")
        icon_frame.pack(fill="x")
        
        icon_label = ctk.CTkLabel(icon_frame, text="图标文件:", font=self.title_font)
        icon_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        icon_input_frame = ctk.CTkFrame(icon_frame, fg_color="white")
        icon_input_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.icon_entry = ctk.CTkEntry(icon_input_frame, placeholder_text="应用图标文件（可选）")
        self.icon_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        
        icon_browse_btn = self.create_browse_button(icon_input_frame, "浏览", self.browse_icon)
        icon_browse_btn.pack(side="right", padx=(0, 10), pady=10)
    
    def create_advanced_tab(self):
        """创建高级选项卡"""
        self.advanced_tab = self.tabview.add("高级设置")
        
        # 创建滚动框架，设置为浅灰色背景
        scroll_frame = ctk.CTkScrollableFrame(self.advanced_tab, fg_color="#F5F5F5")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 临时工作目录
        work_frame = ctk.CTkFrame(scroll_frame, fg_color="white", corner_radius=8, border_width=1, border_color="#E0E0E0")
        work_frame.pack(fill="x", pady=(0, 15))
        
        work_label = ctk.CTkLabel(work_frame, text="临时工作目录:", font=self.title_font)
        work_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        work_input_frame = ctk.CTkFrame(work_frame, fg_color="white")
        work_input_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.work_entry = ctk.CTkEntry(work_input_frame, placeholder_text="临时工作文件存放目录（默认：./build）")
        self.work_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        
        work_browse_btn = self.create_browse_button(work_input_frame, "浏览", self.browse_work)
        work_browse_btn.pack(side="right", padx=(0, 10), pady=10)
        
        # Spec文件目录
        spec_frame = ctk.CTkFrame(scroll_frame, fg_color="white", corner_radius=8, border_width=1, border_color="#E0E0E0")
        spec_frame.pack(fill="x", pady=(0, 15))
        
        spec_label = ctk.CTkLabel(spec_frame, text="Spec文件目录:", font=self.title_font)
        spec_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        spec_input_frame = ctk.CTkFrame(spec_frame, fg_color="white")
        spec_input_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.spec_entry = ctk.CTkEntry(spec_input_frame, placeholder_text="存放生成的.spec文件的目录（默认：当前目录）")
        self.spec_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        
        spec_browse_btn = self.create_browse_button(spec_input_frame, "浏览", self.browse_spec)
        spec_browse_btn.pack(side="right", padx=(0, 10), pady=10)
        
        # 日志级别
        log_frame = ctk.CTkFrame(scroll_frame, fg_color="white", corner_radius=8, border_width=1, border_color="#E0E0E0")
        log_frame.pack(fill="x", pady=(0, 15))
        
        log_label = ctk.CTkLabel(log_frame, text="日志级别:", font=self.title_font)
        log_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.log_var = tk.StringVar(value="INFO")
        log_options_frame = ctk.CTkFrame(log_frame, fg_color="white")
        log_options_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        log_levels = ["TRACE", "DEBUG", "INFO", "WARN", "ERROR", "FATAL"]
        for i, level in enumerate(log_levels):
            log_radio = ctk.CTkRadioButton(log_options_frame, text=level, variable=self.log_var, value=level)
            log_radio.grid(row=i//3, column=i%3, sticky="w", padx=10, pady=5)
        
        # 构建选项
        build_options_frame = ctk.CTkFrame(scroll_frame, fg_color="white", corner_radius=8, border_width=1, border_color="#E0E0E0")
        build_options_frame.pack(fill="x")
        
        build_options_label = ctk.CTkLabel(build_options_frame, text="构建选项:", font=self.title_font)
        build_options_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        options_frame = ctk.CTkFrame(build_options_frame, fg_color="white")
        options_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.clean_var = tk.BooleanVar(value=False)
        clean_check = ctk.CTkCheckBox(options_frame, text="构建前清理PyInstaller缓存和临时文件", variable=self.clean_var)
        clean_check.pack(anchor="w", padx=10, pady=5)
        
        self.yes_var = tk.BooleanVar(value=False)
        yes_check = ctk.CTkCheckBox(options_frame, text="自动确认覆盖非空输出目录", variable=self.yes_var)
        yes_check.pack(anchor="w", padx=10, pady=5)
        
        # 额外参数
        extra_frame = ctk.CTkFrame(scroll_frame, fg_color="white", corner_radius=8, border_width=1, border_color="#E0E0E0")
        extra_frame.pack(fill="x", pady=(0, 15))
        
        extra_label = ctk.CTkLabel(extra_frame, text="额外参数:", font=self.title_font)
        extra_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.extra_entry = ctk.CTkTextbox(extra_frame, height=60, fg_color="#F5F5F5")
        self.extra_entry.pack(fill="x", padx=10, pady=(0, 10))
        self.extra_entry.insert("0.0", "# 在此输入额外的PyInstaller参数，每行一个\n# 例如: --upx-dir=/path/to/upx")
    
    def create_files_tab(self):
        """创建文件选项卡"""
        self.files_tab = self.tabview.add("文件设置")
        
        # 创建滚动框架，设置为浅灰色背景
        scroll_frame = ctk.CTkScrollableFrame(self.files_tab, fg_color="#F5F5F5")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 隐藏导入框架
        hidden_frame = ctk.CTkFrame(scroll_frame, fg_color="white", corner_radius=8, border_width=1, border_color="#E0E0E0")
        hidden_frame.pack(fill="x", pady=(0, 15))
        
        hidden_label = ctk.CTkLabel(hidden_frame, text="隐藏导入:", font=self.title_font)
        hidden_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        hidden_input_frame = ctk.CTkFrame(hidden_frame, fg_color="white")
        hidden_input_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.hidden_entry = ctk.CTkEntry(hidden_input_frame, placeholder_text="输入要隐藏导入的模块名")
        self.hidden_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        
        hidden_add_btn = self.create_add_button(hidden_input_frame, "添加", self.add_hidden_import)
        hidden_add_btn.pack(side="right", padx=(0, 10), pady=10)
        
        # 隐藏导入列表
        self.hidden_listbox = tk.Listbox(hidden_frame, height=6, font=self.listbox_font)
        self.hidden_listbox.pack(fill="x", padx=10, pady=(0, 10))
        
        hidden_list_frame = ctk.CTkFrame(hidden_frame, fg_color="white")
        hidden_list_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        hidden_remove_btn = self.create_remove_button(hidden_list_frame, "移除选中", self.remove_hidden_import)
        hidden_remove_btn.pack(side="left", padx=10, pady=5)
        
        hidden_clear_btn = self.create_clear_button(hidden_list_frame, "清空全部", self.clear_hidden_imports)
        hidden_clear_btn.pack(side="left", padx=5, pady=5)
        
        # 排除模块框架
        exclude_frame = ctk.CTkFrame(scroll_frame, fg_color="white", corner_radius=8, border_width=1, border_color="#E0E0E0")
        exclude_frame.pack(fill="x", pady=(0, 15))
        
        exclude_label = ctk.CTkLabel(exclude_frame, text="排除模块:", font=self.title_font)
        exclude_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        exclude_input_frame = ctk.CTkFrame(exclude_frame, fg_color="white")
        exclude_input_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.exclude_entry = ctk.CTkEntry(exclude_input_frame, placeholder_text="输入要排除的模块名")
        self.exclude_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        
        exclude_add_btn = self.create_add_button(exclude_input_frame, "添加", self.add_exclude_module)
        exclude_add_btn.pack(side="right", padx=(0, 10), pady=10)
        
        # 排除模块列表
        self.exclude_listbox = tk.Listbox(exclude_frame, height=6, font=self.listbox_font)
        self.exclude_listbox.pack(fill="x", padx=10, pady=(0, 10))
        
        exclude_list_frame = ctk.CTkFrame(exclude_frame, fg_color="white")
        exclude_list_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        exclude_remove_btn = self.create_remove_button(exclude_list_frame, "移除选中", self.remove_exclude_module)
        exclude_remove_btn.pack(side="left", padx=10, pady=5)
        
        exclude_clear_btn = self.create_clear_button(exclude_list_frame, "清空全部", self.clear_exclude_modules)
        exclude_clear_btn.pack(side="left", padx=5, pady=5)
        
    def create_build_tab(self):
        """创建构建选项卡"""
        self.build_tab = self.tabview.add("构建")
        
        # 创建滚动框架，设置为浅灰色背景
        scroll_frame = ctk.CTkScrollableFrame(self.build_tab, fg_color="#F5F5F5")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 配置摘要
        summary_frame = ctk.CTkFrame(scroll_frame, fg_color="white", corner_radius=8, border_width=1, border_color="#E0E0E0")
        summary_frame.pack(fill="x", pady=(0, 15))
        
        summary_label = ctk.CTkLabel(summary_frame, text="配置摘要:", font=self.title_font)
        summary_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.summary_text = ctk.CTkTextbox(summary_frame, height=150)
        self.summary_text.pack(fill="x", padx=10, pady=(0, 10))
        
        # 更新摘要按钮
        update_summary_btn = self.create_add_button(summary_frame, "更新配置摘要", self.update_summary)
        update_summary_btn.pack(fill="x", padx=10, pady=(0, 10))
        
        # 构建按钮
        build_frame = ctk.CTkFrame(scroll_frame, fg_color="white", corner_radius=8, border_width=1, border_color="#E0E0E0")
        build_frame.pack(fill="x", pady=(0, 15))
        
        build_label = ctk.CTkLabel(build_frame, text="开始构建:", font=self.title_font)
        build_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        build_btn_frame = ctk.CTkFrame(build_frame, fg_color="white")
        build_btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.build_btn = self.create_primary_button(
            build_btn_frame,
            "开始打包",
            self.start_build,
            height=40
        )
        self.build_btn.pack(fill="x", pady=10)
    
    # 浏览文件方法
    def browse_script(self):
        """浏览脚本文件"""
        file_path = browse_script_file(self.parent)
        if file_path:
            self.script_entry.delete(0, tk.END)
            self.script_entry.insert(0, file_path)
            
            # 如果应用名称为空，使用脚本文件名
            if not self.name_entry.get():
                script_name = get_script_name(file_path)
                self.name_entry.insert(0, script_name)
    
    def browse_output(self):
        """浏览输出目录"""
        dir_path = browse_directory(self.parent, "选择输出目录")
        if dir_path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, dir_path)
    
    def browse_work(self):
        """浏览临时工作目录"""
        dir_path = browse_directory(self.parent, "选择临时工作目录")
        if dir_path:
            self.work_entry.delete(0, tk.END)
            self.work_entry.insert(0, dir_path)
    
    def browse_spec(self):
        """浏览Spec文件目录"""
        dir_path = browse_directory(self.parent, "选择Spec文件目录")
        if dir_path:
            self.spec_entry.delete(0, tk.END)
            self.spec_entry.insert(0, dir_path)
    
    def browse_icon(self):
        """浏览图标文件"""
        file_path = browse_icon_file(self.parent)
        if file_path:
            self.icon_entry.delete(0, tk.END)
            self.icon_entry.insert(0, file_path)
    
    # 隐藏导入和排除模块方法
    def add_hidden_import(self):
        """添加隐藏导入"""
        import_name = self.hidden_entry.get().strip()
        if import_name:
            self.hidden_listbox.insert(tk.END, import_name)
            self.hidden_entry.delete(0, tk.END)
    
    def remove_hidden_import(self):
        """移除选中的隐藏导入"""
        selection = self.hidden_listbox.curselection()
        if selection:
            self.hidden_listbox.delete(selection[0])
    
    def clear_hidden_imports(self):
        """清空所有隐藏导入"""
        self.hidden_listbox.delete(0, tk.END)
    
    def add_exclude_module(self):
        """添加排除模块"""
        module_name = self.exclude_entry.get().strip()
        if module_name:
            self.exclude_listbox.insert(tk.END, module_name)
            self.exclude_entry.delete(0, tk.END)
    
    def remove_exclude_module(self):
        """移除选中的排除模块"""
        selection = self.exclude_listbox.curselection()
        if selection:
            self.exclude_listbox.delete(selection[0])
    
    def clear_exclude_modules(self):
        """清空所有排除模块"""
        self.exclude_listbox.delete(0, tk.END)
    
    # 获取配置方法
    def get_hidden_imports(self):
        """获取隐藏导入列表"""
        return list(self.hidden_listbox.get(0, tk.END))
    
    def get_exclude_modules(self):
        """获取排除模块列表"""
        return list(self.exclude_listbox.get(0, tk.END))
    
    # 配置相关方法
    def update_config(self):
        """更新配置对象"""
        self.config.script = self.script_entry.get()
        self.config.name = self.name_entry.get()
        self.config.output_dir = self.output_entry.get()
        self.config.work_dir = self.work_entry.get()
        self.config.spec_dir = self.spec_entry.get()
        self.config.icon = self.icon_entry.get()
        self.config.mode = self.mode_var.get()
        self.config.console = self.console_var.get()
        self.config.clean = self.clean_var.get()
        self.config.yes = self.yes_var.get()
        self.config.log_level = self.log_var.get()
        self.config.hidden_imports = self.get_hidden_imports()
        self.config.exclude_modules = self.get_exclude_modules()
        self.config.extra_args = self.extra_entry.get("1.0", tk.END).strip()
    
    def update_summary(self):
        """更新配置摘要"""
        self.update_config()
        summary = self.config.get_summary()
        self.summary_text.delete("1.0", tk.END)
        self.summary_text.insert("1.0", summary)
    
    def set_script_path(self, path):
        """设置脚本路径"""
        self.script_entry.delete(0, tk.END)
        self.script_entry.insert(0, path)
        
        # 如果应用名称为空，使用脚本文件名
        if not self.name_entry.get():
            script_name = get_script_name(path)
            self.name_entry.insert(0, script_name)
    
    def start_build(self):
        """开始打包"""
        # 更新配置
        self.update_config()
        
        # 验证配置
        is_valid, error_message = self.config.validate()
        if not is_valid:
            show_error(self.parent, "配置错误", error_message)
            return
        
        # 切换到打包过程标签页
        self.main_window.switch_to_process_tab()
        
        # 将配置传递给打包过程标签页
        self.main_window.process_ui.start_pyinstaller_build(self.config)