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
    browse_script_file,
    browse_directory,
    browse_icon_file,
    browse_data_file,
    browse_binary_file,
    get_script_name,
    validate_data_file_format,
    format_data_file_entry,
    parse_data_file_entry,
    show_error,
    show_info,
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

        # 设置字体大小
        self.default_font = ctk.CTkFont(family=self.font_family, size=12)
        self.title_font = ctk.CTkFont(family=self.font_family, size=15, weight="bold")
        self.button_font = ctk.CTkFont(family=self.font_family, size=12, weight="bold")
        self.tab_font = ctk.CTkFont(family=self.font_family, size=14, weight="bold")
        self.primary_button_font = ctk.CTkFont(
            family=self.font_family, size=14, weight="bold"
        )
        # 输入框字体
        self.entry_font = ctk.CTkFont(family=self.font_family, size=13)
        # 输入框统一样式
        self.entry_fg_color = "#F9FAFB"
        self.entry_border_color = "#D1D5DB"
        self.entry_border_width = 1
        self.entry_corner_radius = 6

        # 列表字体
        self.listbox_font = tk_font.Font(
            family=self.font_family, size=18, weight="bold"
        )

        # 初始化配置
        self.config = PyInstallerConfig()

        # 创建界面
        self.create_ui()

    def create_ui(self):
        """创建用户界面"""
        # 创建一个无边框的主容器，完全填充父容器
        self.main_container = ctk.CTkFrame(
            self.parent, fg_color="#F8FAFC", corner_radius=0
        )
        self.main_container.pack(fill="both", expand=True, padx=0, pady=0)

        # 创建右侧内容区域，使用白色背景，添加阴影效果
        self.content_area = ctk.CTkFrame(
            self.main_container,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color="#E5E7EB",
        )
        self.content_area.pack(side="top", fill="both", expand=True, padx=15, pady=15)

        # 创建标签页按钮容器，使用水平布局
        self.tabs_container = ctk.CTkFrame(
            self.content_area, fg_color="#F9FAFB", height=50, corner_radius=8
        )
        self.tabs_container.pack(fill="x", padx=15, pady=(15, 10))
        self.tabs_container.pack_propagate(False)

        # 存储标签按钮和对应内容的映射
        self.tabs = {}
        self.active_tab = None

        # 创建水平排列的标签页按钮
        self.create_modern_tab_buttons()

        # 创建标签页内容区域
        self.tabs_content_area = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.tabs_content_area.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # 创建各个标签页内容
        self.create_all_tabs_content()

        # 默认显示第一个标签页
        self.switch_tab("basic")

    def create_modern_tab_buttons(self):
        """创建现代化的水平标签页按钮"""
        tab_configs = [
            ("basic", "基础设置", "🔧"),
            ("advanced", "高级设置", "⚙️"),
            ("files", "文件设置", "📁"),
            ("build", "构建", "🚀"),
        ]

        # 创建按钮容器框架，水平排列
        buttons_frame = ctk.CTkFrame(self.tabs_container, fg_color="transparent")
        buttons_frame.pack(fill="both", expand=True)

        for i, (tab_id, tab_name, tab_icon) in enumerate(tab_configs):
            # 创建现代化标签页按钮
            button = ctk.CTkButton(
                buttons_frame,
                text=f"{tab_icon} {tab_name}",
                font=self.tab_font,
                command=lambda id=tab_id: self.switch_tab(id),
                fg_color="transparent",
                hover_color="#E5E7EB",
                text_color="#6B7280",
                width=120,
                height=40,
                corner_radius=8,
                border_width=0,
            )

            # 使用grid布局水平排列按钮
            button.grid(row=0, column=i, padx=5, pady=5, sticky="ew")

            # 设置列权重，使按钮均匀分布
            buttons_frame.grid_columnconfigure(i, weight=1)

            # 存储按钮引用
            self.tabs[tab_id] = {"button": button, "frame": None}

    def create_all_tabs_content(self):
        """创建所有标签页内容"""
        # 创建基础设置标签页
        self.basic_frame = ctk.CTkFrame(self.tabs_content_area, fg_color="transparent")
        self.tabs["basic"]["frame"] = self.basic_frame
        self.create_basic_tab_content()

        # 创建高级设置标签页
        self.advanced_frame = ctk.CTkFrame(
            self.tabs_content_area, fg_color="transparent"
        )
        self.tabs["advanced"]["frame"] = self.advanced_frame
        self.create_advanced_tab_content()

        # 创建文件设置标签页
        self.files_frame = ctk.CTkFrame(self.tabs_content_area, fg_color="transparent")
        self.tabs["files"]["frame"] = self.files_frame
        self.create_files_tab_content()

        # 创建构建标签页
        self.build_frame = ctk.CTkFrame(self.tabs_content_area, fg_color="transparent")
        self.tabs["build"]["frame"] = self.build_frame
        self.create_build_tab_content()

    def switch_tab(self, tab_id):
        """切换标签页

        Args:
            tab_id: 要切换的标签页ID
        """
        # 隐藏所有标签页内容
        for tab_info in self.tabs.values():
            tab_info["frame"].pack_forget()
            # 重置所有按钮为未选中状态
            tab_info["button"].configure(
                fg_color="transparent",
                hover_color="#E5E7EB",
                text_color="#6B7280",
                font=ctk.CTkFont(family=self.font_family, size=13, weight="normal"),
            )

        # 显示选中的标签页内容
        self.tabs[tab_id]["frame"].pack(fill="both", expand=True)
        # 高亮选中的标签页按钮
        self.tabs[tab_id]["button"].configure(
            fg_color="#3B82F6",
            hover_color="#2563EB",
            text_color="white",
            font=ctk.CTkFont(family=self.font_family, size=13, weight="bold"),
        )
        self.active_tab = tab_id

    def create_basic_tab_content(self):
        """创建基础设置标签页内容"""
        # 创建滚动框架，设置为透明背景以与内容区域融合
        scroll_frame = ctk.CTkScrollableFrame(self.basic_frame, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # 入口文件路径
        script_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#F9FAFB",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB",
        )
        script_frame.pack(fill="x", pady=(0, 15))

        script_label = ctk.CTkLabel(
            script_frame, text="入口文件路径/启动文件路径:", font=self.title_font
        )
        script_label.pack(anchor="w", padx=15, pady=(15, 8))

        script_input_frame = ctk.CTkFrame(
            script_frame, fg_color="#F9FAFB", corner_radius=8
        )
        script_input_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.script_entry = ctk.CTkEntry(
            script_input_frame,
            placeholder_text="选择要打包的Python脚本",
            fg_color=self.entry_fg_color,
            border_color=self.entry_border_color,
            border_width=self.entry_border_width,
            corner_radius=self.entry_corner_radius,
            font=self.entry_font,
        )
        self.script_entry.pack(
            side="left", fill="x", expand=True, padx=(10, 8), pady=10
        )

        script_browse_btn = self.create_browse_button(
            script_input_frame, "浏览", self.browse_script
        )
        script_browse_btn.pack(side="right", padx=(0, 10), pady=10)

        # 应用名称
        name_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#F9FAFB",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB",
        )
        name_frame.pack(fill="x", pady=(0, 15))

        name_label = ctk.CTkLabel(name_frame, text="应用名称:", font=self.title_font)
        name_label.pack(anchor="w", padx=15, pady=(15, 8))

        self.name_entry = ctk.CTkEntry(
            name_frame,
            placeholder_text="打包后的应用名称（可选）",
            fg_color=self.entry_fg_color,
            border_color=self.entry_border_color,
            border_width=self.entry_border_width,
            corner_radius=self.entry_corner_radius,
            font=self.entry_font,
        )
        self.name_entry.pack(fill="x", padx=15, pady=(0, 15))

        # 打包模式
        mode_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#F9FAFB",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB",
        )
        mode_frame.pack(fill="x", pady=(0, 15))

        mode_label = ctk.CTkLabel(mode_frame, text="打包模式:", font=self.title_font)
        mode_label.pack(anchor="w", padx=15, pady=(15, 8))

        mode_options_frame = ctk.CTkFrame(
            mode_frame, fg_color="#F9FAFB", corner_radius=8
        )
        mode_options_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.mode_var = tk.StringVar(value="onedir")
        onedir_radio = ctk.CTkRadioButton(
            mode_options_frame,
            text="目录模式 (创建一个包含可执行文件的程序目录, 性能更好)",
            variable=self.mode_var,
            value="onedir",
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        onedir_radio.pack(anchor="w", padx=15, pady=(10, 5))

        onefile_radio = ctk.CTkRadioButton(
            mode_options_frame,
            text="单文件模式 (创建单个可执行文件, 执行时解压到系统的临时目录中, 性能较差但更易分发)",
            variable=self.mode_var,
            value="onefile",
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        onefile_radio.pack(anchor="w", padx=15, pady=(5, 10))

        # 控制台选项
        console_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#F9FAFB",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB",
        )
        console_frame.pack(fill="x", pady=(0, 15))

        console_label = ctk.CTkLabel(
            console_frame, text="控制台选项:", font=self.title_font
        )
        console_label.pack(anchor="w", padx=15, pady=(15, 8))

        console_options_frame = ctk.CTkFrame(
            console_frame, fg_color="#F9FAFB", corner_radius=8
        )
        console_options_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.console_var = tk.BooleanVar(value=False)
        console_check = ctk.CTkCheckBox(
            console_options_frame,
            text="显示控制台窗口",
            variable=self.console_var,
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        console_check.pack(anchor="w", padx=15, pady=10)

        # 输出目录
        output_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#F9FAFB",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB",
        )
        output_frame.pack(fill="x", pady=(0, 15))

        output_label = ctk.CTkLabel(
            output_frame, text="输出目录:", font=self.title_font
        )
        output_label.pack(anchor="w", padx=15, pady=(15, 8))

        output_input_frame = ctk.CTkFrame(
            output_frame, fg_color="#F9FAFB", corner_radius=8
        )
        output_input_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.output_entry = ctk.CTkEntry(
            output_input_frame,
            placeholder_text="打包后应用的输出目录（默认：./dist）",
            fg_color=self.entry_fg_color,
            border_color=self.entry_border_color,
            border_width=self.entry_border_width,
            corner_radius=self.entry_corner_radius,
            font=self.entry_font,
        )
        self.output_entry.pack(
            side="left", fill="x", expand=True, padx=(10, 8), pady=10
        )

        output_browse_btn = self.create_browse_button(
            output_input_frame, "浏览", self.browse_output
        )
        output_browse_btn.pack(side="right", padx=(0, 10), pady=10)

        # 图标文件
        icon_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#F9FAFB",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB",
        )
        icon_frame.pack(fill="x")

        icon_label = ctk.CTkLabel(icon_frame, text="图标文件:", font=self.title_font)
        icon_label.pack(anchor="w", padx=15, pady=(15, 8))

        icon_input_frame = ctk.CTkFrame(icon_frame, fg_color="#F9FAFB", corner_radius=8)
        icon_input_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.icon_entry = ctk.CTkEntry(
            icon_input_frame,
            placeholder_text="应用图标文件（可选）",
            fg_color=self.entry_fg_color,
            border_color=self.entry_border_color,
            border_width=self.entry_border_width,
            corner_radius=self.entry_corner_radius,
            font=self.entry_font,
        )
        self.icon_entry.pack(side="left", fill="x", expand=True, padx=(10, 8), pady=10)

        icon_browse_btn = self.create_browse_button(
            icon_input_frame, "浏览", self.browse_icon
        )
        icon_browse_btn.pack(side="right", padx=(0, 10), pady=10)

    def create_advanced_tab_content(self):
        """创建高级设置标签页内容"""
        # 创建滚动框架，设置为透明背景以与内容区域融合
        scroll_frame = ctk.CTkScrollableFrame(
            self.advanced_frame, fg_color="transparent"
        )
        scroll_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # 临时工作目录
        work_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#F9FAFB",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB",
        )
        work_frame.pack(fill="x", pady=(0, 15))

        work_label = ctk.CTkLabel(
            work_frame, text="临时工作目录:", font=self.title_font
        )
        work_label.pack(anchor="w", padx=15, pady=(15, 8))

        work_input_frame = ctk.CTkFrame(work_frame, fg_color="#F9FAFB", corner_radius=8)
        work_input_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.work_entry = ctk.CTkEntry(
            work_input_frame,
            placeholder_text="临时工作文件存放目录（默认：./build）",
            fg_color=self.entry_fg_color,
            border_color=self.entry_border_color,
            border_width=self.entry_border_width,
            corner_radius=self.entry_corner_radius,
            font=self.entry_font,
        )
        self.work_entry.pack(side="left", fill="x", expand=True, padx=(10, 8), pady=10)

        work_browse_btn = self.create_browse_button(
            work_input_frame, "浏览", self.browse_work
        )
        work_browse_btn.pack(side="right", padx=(0, 10), pady=10)

        # Spec文件目录
        spec_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#F9FAFB",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB",
        )
        spec_frame.pack(fill="x", pady=(0, 15))

        spec_label = ctk.CTkLabel(
            spec_frame, text="Spec文件目录:", font=self.title_font
        )
        spec_label.pack(anchor="w", padx=15, pady=(15, 8))

        spec_input_frame = ctk.CTkFrame(spec_frame, fg_color="#F9FAFB", corner_radius=8)
        spec_input_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.spec_entry = ctk.CTkEntry(
            spec_input_frame,
            placeholder_text="存放生成的.spec文件的目录（默认：当前目录）",
            fg_color=self.entry_fg_color,
            border_color=self.entry_border_color,
            border_width=self.entry_border_width,
            corner_radius=self.entry_corner_radius,
            font=self.entry_font,
        )
        self.spec_entry.pack(side="left", fill="x", expand=True, padx=(10, 8), pady=10)

        spec_browse_btn = self.create_browse_button(
            spec_input_frame, "浏览", self.browse_spec
        )
        spec_browse_btn.pack(side="right", padx=(0, 10), pady=10)

        # 日志级别
        log_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#F9FAFB",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB",
        )
        log_frame.pack(fill="x", pady=(0, 15))

        log_label = ctk.CTkLabel(log_frame, text="日志级别:", font=self.title_font)
        log_label.pack(anchor="w", padx=15, pady=(15, 8))

        self.log_var = tk.StringVar(value="INFO")
        log_options_frame = ctk.CTkFrame(log_frame, fg_color="#F9FAFB", corner_radius=8)
        log_options_frame.pack(fill="x", padx=15, pady=(0, 15))

        log_levels = ["TRACE", "DEBUG", "INFO", "WARN", "ERROR", "FATAL"]
        for i, level in enumerate(log_levels):
            log_radio = ctk.CTkRadioButton(
                log_options_frame,
                text=level,
                variable=self.log_var,
                value=level,
                font=ctk.CTkFont(family=self.font_family, size=12),
            )
            log_radio.grid(row=i // 3, column=i % 3, sticky="w", padx=15, pady=5)

        # 构建选项
        build_options_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#F9FAFB",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB",
        )
        build_options_frame.pack(fill="x", pady=(0, 15))

        build_options_label = ctk.CTkLabel(
            build_options_frame, text="构建选项:", font=self.title_font
        )
        build_options_label.pack(anchor="w", padx=15, pady=(15, 8))

        options_frame = ctk.CTkFrame(
            build_options_frame, fg_color="#F9FAFB", corner_radius=8
        )
        options_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.clean_var = tk.BooleanVar(value=False)
        clean_check = ctk.CTkCheckBox(
            options_frame,
            text="构建前清理PyInstaller缓存和临时文件",
            variable=self.clean_var,
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        clean_check.pack(anchor="w", padx=15, pady=(10, 5))

        self.yes_var = tk.BooleanVar(value=False)
        yes_check = ctk.CTkCheckBox(
            options_frame,
            text="自动确认覆盖非空输出目录",
            variable=self.yes_var,
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        yes_check.pack(anchor="w", padx=15, pady=(5, 10))

        # 额外参数
        extra_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#F9FAFB",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB",
        )
        extra_frame.pack(fill="x", pady=(0, 15))

        extra_label = ctk.CTkLabel(extra_frame, text="额外参数:", font=self.title_font)
        extra_label.pack(anchor="w", padx=15, pady=(15, 8))

        self.extra_entry = ctk.CTkTextbox(
            extra_frame,
            height=80,
            fg_color=self.entry_fg_color,
            border_color=self.entry_border_color,
            border_width=self.entry_border_width,
            corner_radius=self.entry_corner_radius,
            font=self.entry_font,
        )
        self.extra_entry.pack(fill="x", padx=15, pady=(0, 15))
        self.extra_entry.insert(
            "0.0",
            "# 在此输入额外的PyInstaller参数，每行一个\n# 例如: --upx-dir=/path/to/upx",
        )

    def create_files_tab_content(self):
        """创建文件设置标签页内容"""
        # 创建滚动框架，设置为透明背景以与内容区域融合
        scroll_frame = ctk.CTkScrollableFrame(self.files_frame, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # 隐藏导入框架
        hidden_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#F9FAFB",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB",
        )
        hidden_frame.pack(fill="x", pady=(0, 15))

        hidden_label = ctk.CTkLabel(
            hidden_frame, text="隐藏导入:", font=self.title_font
        )
        hidden_label.pack(anchor="w", padx=15, pady=(15, 8))

        hidden_input_frame = ctk.CTkFrame(
            hidden_frame, fg_color="#F9FAFB", corner_radius=8
        )
        hidden_input_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.hidden_entry = ctk.CTkEntry(
            hidden_input_frame,
            placeholder_text="输入要隐藏导入的模块名",
            fg_color=self.entry_fg_color,
            border_color=self.entry_border_color,
            border_width=self.entry_border_width,
            corner_radius=self.entry_corner_radius,
            font=self.entry_font,
        )
        self.hidden_entry.pack(
            side="left", fill="x", expand=True, padx=(10, 8), pady=10
        )

        hidden_add_btn = self.create_add_button(
            hidden_input_frame, "添加", self.add_hidden_import
        )
        hidden_add_btn.pack(side="right", padx=(0, 10), pady=10)

        # 隐藏导入列表
        hidden_list_container = ctk.CTkFrame(
            hidden_frame,
            fg_color="#FFFFFF",
            corner_radius=8,
            border_width=1,
            border_color="#D1D5DB",
        )
        hidden_list_container.pack(fill="x", padx=15, pady=(0, 15))

        self.hidden_listbox = tk.Listbox(
            hidden_list_container,  # 列表框
            height=6,  # 列表框高度
            font=self.listbox_font,  # 列表框字体
            bg="#FFFFFF",  # 列表框背景颜色
            fg="#1F2937",  # 列表框字体颜色
            selectbackground="#3B82F6",  # 选中项背景颜色
            selectforeground="#FFFFFF",  # 选中项字体颜色
            borderwidth=0,  # 移除边框
            relief="flat",  # 平坦样式
            highlightthickness=0,  # 移除高亮
            exportselection=False,
        )
        self.hidden_listbox.pack(fill="both", expand=True, padx=8, pady=8)

        hidden_list_frame = ctk.CTkFrame(
            hidden_frame, fg_color="#F9FAFB", corner_radius=8
        )
        hidden_list_frame.pack(fill="x", padx=15, pady=(0, 15))

        hidden_remove_btn = self.create_remove_button(
            hidden_list_frame, "移除选中", self.remove_hidden_import
        )
        hidden_remove_btn.pack(side="left", padx=15, pady=10)

        hidden_clear_btn = self.create_clear_button(
            hidden_list_frame, "清空全部", self.clear_hidden_imports
        )
        hidden_clear_btn.pack(side="left", padx=8, pady=10)

        # 排除模块框架
        exclude_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#F9FAFB",
            corner_radius=8,
            border_width=1,
            border_color="#E0E0E0",
        )
        exclude_frame.pack(fill="x", pady=(0, 15))

        exclude_label = ctk.CTkLabel(
            exclude_frame, text="排除模块:", font=self.title_font
        )
        exclude_label.pack(anchor="w", padx=10, pady=(10, 5))

        exclude_input_frame = ctk.CTkFrame(exclude_frame, fg_color="#F9FAFB")
        exclude_input_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.exclude_entry = ctk.CTkEntry(
            exclude_input_frame,
            placeholder_text="输入要排除的模块名",
            fg_color=self.entry_fg_color,
            border_color=self.entry_border_color,
            border_width=self.entry_border_width,
            corner_radius=self.entry_corner_radius,
            font=self.entry_font,
        )
        self.exclude_entry.pack(
            side="left", fill="x", expand=True, padx=(10, 5), pady=10
        )

        exclude_add_btn = self.create_add_button(
            exclude_input_frame, "添加", self.add_exclude_module
        )
        exclude_add_btn.pack(side="right", padx=(0, 10), pady=10)

        # 排除模块列表
        exclude_list_container = ctk.CTkFrame(
            exclude_frame,
            fg_color="#FFFFFF",
            corner_radius=8,
            border_width=1,
            border_color="#D1D5DB",
        )
        exclude_list_container.pack(fill="x", padx=10, pady=(0, 10))

        self.exclude_listbox = tk.Listbox(
            exclude_list_container,
            height=6,
            font=self.listbox_font,
            bg="#FFFFFF",
            fg="#1F2937",
            selectbackground="#3B82F6",
            selectforeground="#FFFFFF",
            borderwidth=0,
            relief="flat",
            highlightthickness=0,
            exportselection=False,
        )
        self.exclude_listbox.pack(fill="both", expand=True, padx=8, pady=8)

        exclude_remove_btn = self.create_remove_button(
            exclude_frame, "移除选中", self.remove_exclude_module
        )
        exclude_remove_btn.pack(side="left", padx=10, pady=5)

        exclude_clear_btn = self.create_clear_button(
            exclude_frame, "清空全部", self.clear_exclude_modules
        )
        exclude_clear_btn.pack(side="left", padx=5, pady=5)

    def create_build_tab_content(self):
        """创建构建标签页内容"""
        # 创建滚动框架，设置为透明背景以与内容区域融合
        scroll_frame = ctk.CTkScrollableFrame(self.build_frame, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # 配置摘要
        summary_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#FFFFFF",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB",
        )
        summary_frame.pack(fill="x", pady=(0, 15))

        summary_label = ctk.CTkLabel(
            summary_frame, text="配置摘要:", font=self.title_font
        )
        summary_label.pack(anchor="w", padx=15, pady=(15, 8))

        self.summary_text = ctk.CTkTextbox(
            summary_frame,
            height=150,
            fg_color="#F9FAFB",
            border_color="#D1D5DB",
            border_width=1,
            corner_radius=6,
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        self.summary_text.pack(fill="x", padx=15, pady=(0, 15))

        # 更新摘要按钮
        update_summary_btn = self.create_add_button(
            summary_frame, "更新配置摘要", self.update_summary
        )
        update_summary_btn.pack(fill="x", padx=15, pady=(0, 15))

        # 构建按钮
        build_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#FFFFFF",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB",
        )
        build_frame.pack(fill="x")

        build_label = ctk.CTkLabel(build_frame, text="开始构建:", font=self.title_font)
        build_label.pack(anchor="w", padx=15, pady=(15, 8))

        build_btn_frame = ctk.CTkFrame(build_frame, fg_color="#F9FAFB", corner_radius=8)
        build_btn_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.build_btn = self.create_primary_button(
            build_btn_frame, "开始打包", self.start_build, height=45
        )
        self.build_btn.pack(fill="x", padx=15, pady=15)

    def create_browse_button(self, parent, text, command, width=80):
        """创建浏览按钮（次要功能）

        Args:
            parent: 父容器
            text: 按钮文本
            command: 按钮命令
            width: 按钮宽度

        Returns:
            创建的按钮组件
        """
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
            border_color="#4F46E5",
        )

    def create_add_button(self, parent, text, command, width=80):
        """创建添加按钮（一般功能）

        Args:
            parent: 父容器
            text: 按钮文本
            command: 按钮命令
            width: 按钮宽度

        Returns:
            创建的按钮组件
        """
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
            border_color="#2563EB",
        )

    def create_remove_button(self, parent, text, command, width=100):
        """创建移除按钮（警告功能）

        Args:
            parent: 父容器
            text: 按钮文本
            command: 按钮命令
            width: 按钮宽度

        Returns:
            创建的按钮组件
        """
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
            border_color="#D97706",
        )

    def create_clear_button(self, parent, text, command, width=100):
        """创建清空按钮（危险功能）

        Args:
            parent: 父容器
            text: 按钮文本
            command: 按钮命令
            width: 按钮宽度

        Returns:
            创建的按钮组件
        """
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
            border_color="#DC2626",
        )

    def create_primary_button(self, parent, text, command, width=200, height=None):
        """创建主要按钮（最重要功能）

        Args:
            parent: 父容器
            text: 按钮文本
            command: 按钮命令
            width: 按钮宽度
            height: 按钮高度（可选）

        Returns:
            创建的按钮组件
        """
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
            border_color="#059669",
        )

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
