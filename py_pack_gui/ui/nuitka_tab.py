"""
Nuitka标签页模块
提供Nuitka打包参数配置界面
"""

import tkinter as tk
from tkinter import filedialog
from tkinter import font as tk_font
import customtkinter as ctk
from core.nuitka_config import NuitkaConfig
from utils.pyinstaller_utils import (
    browse_script_file,
    browse_directory,
    browse_icon_file,
    get_script_name,
    show_error,
)


class NuitkaTab:
    """Nuitka标签页类"""

    def __init__(self, parent, main_window, font_family="Microsoft YaHei UI"):
        """初始化Nuitka标签页

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

        # 预定义的Nuitka插件列表 (包含名称和说明)
        self.available_plugins = [
            "anti-bloat - 从广泛使用的库模块源代码中剔除愚蠢的导入",
            "data-files - 包含由包配置文件指定的数据文件",
            "delvewheel - 独立模式下支持使用 'delvewheel' 的包所需",
            "dill-compat - 为 'dill' 包和 'cloudpickle' 兼容性所需",
            "dll-files - 根据包配置文件包含 DLL 文件",
            "enum-compat - 为 Python2 和 'enum' 包所需",
            "eventlet - 支持包含 'eventlet' 依赖项及其对 'dns' 包猴子补丁的需求",
            "gevent - 由 'gevent' 包所需",
            "gi - 支持 GI 包 typelib 依赖项",
            "glfw - 独立模式下为 'OpenGL' (PyOpenGL) 和 'glfw' 包所需",
            "implicit-imports - 根据包配置文件提供包的隐式导入",
            "kivy - 由 'kivy' 包所需",
            "matplotlib - 为 'matplotlib' 模块所需",
            "multiprocessing - 由 Python 的 'multiprocessing' 模块所需",
            "no-qt - 禁用所有 Qt 绑定的包含",
            "options-nanny - 根据包配置文件向用户通知潜在问题",
            "pbr-compat - 独立模式下由 'pbr' 包所需",
            "pkg-resources - 为 'pkg_resources' 提供变通方法",
            "playwright - 由 'playwright' 包所需",
            "pmw-freezer - 由 'Pmw' 包所需",
            "pylint-warnings - 支持 PyLint / PyDev 源代码标记检查",
            "pyqt5 - 由 PyQt5 包所需",
            "pyqt6 - 由 PyQt6 包在独立模式下所需",
            "pyside2 - 由 PySide2 包所需",
            "pyside6 - 由 PySide6 包在独立模式下所需",
            "pywebview - 由 'webview' 包 (PyPI 上的 pywebview) 所需",
            "spacy - 由 'spacy' 包所需",
            "tk-inter - 由 Python 的 Tk 模块所需",
            "transformers - 为 transformers 包提供隐式导入",
            "upx - 自动使用 UPX 压缩创建的二进制文件",
        ]

        # 初始化配置
        self.config = NuitkaConfig()

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
            placeholder_text="打包后的应用名称 (可选) ",
            fg_color=self.entry_fg_color,
            border_color=self.entry_border_color,
            border_width=self.entry_border_width,
            corner_radius=self.entry_corner_radius,
            font=self.entry_font,
        )
        self.name_entry.pack(fill="x", padx=15, pady=(0, 15))

        # 图标文件
        icon_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#F9FAFB",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB",
        )
        icon_frame.pack(fill="x", pady=(0, 15))

        icon_label = ctk.CTkLabel(icon_frame, text="图标文件:", font=self.title_font)
        icon_label.pack(anchor="w", padx=15, pady=(15, 8))

        icon_input_frame = ctk.CTkFrame(icon_frame, fg_color="#F9FAFB", corner_radius=8)
        icon_input_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.icon_entry = ctk.CTkEntry(
            icon_input_frame,
            placeholder_text="应用图标文件 (可选) ",
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

        # 编译模式
        mode_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#F9FAFB",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB",
        )
        mode_frame.pack(fill="x", pady=(0, 15))

        mode_label = ctk.CTkLabel(mode_frame, text="编译模式:", font=self.title_font)
        mode_label.pack(anchor="w", padx=15, pady=(15, 8))

        mode_options_frame = ctk.CTkFrame(
            mode_frame, fg_color="#F9FAFB", corner_radius=8
        )
        mode_options_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.mode_var = tk.StringVar(value="standalone")
        accelerated_radio = ctk.CTkRadioButton(
            mode_options_frame,
            text="加速模式 (在您当前Python安装中运行并依赖之)",
            variable=self.mode_var,
            value="accelerated",
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        accelerated_radio.pack(anchor="w", padx=15, pady=(10, 5))

        standalone_radio = ctk.CTkRadioButton(
            mode_options_frame,
            text="独立文件夹 (生成含可执行文件的独立文件夹)",
            variable=self.mode_var,
            value="standalone",
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        standalone_radio.pack(anchor="w", padx=15, pady=(5, 5))

        onefile_radio = ctk.CTkRadioButton(
            mode_options_frame,
            text="单文件 (生成单文件自解压可执行文件)",
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

        self.console_var = tk.StringVar(value="force")
        force_radio = ctk.CTkRadioButton(
            console_options_frame,
            text="启用控制台",
            variable=self.console_var,
            value="force",
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        force_radio.pack(anchor="w", padx=15, pady=(10, 5))

        disable_radio = ctk.CTkRadioButton(
            console_options_frame,
            text="禁用控制台",
            variable=self.console_var,
            value="disable",
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        disable_radio.pack(anchor="w", padx=15, pady=(5, 5))

        attach_radio = ctk.CTkRadioButton(
            console_options_frame,
            text="附加已有控制台",
            variable=self.console_var,
            value="attach",
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        attach_radio.pack(anchor="w", padx=15, pady=(5, 5))

        hide_radio = ctk.CTkRadioButton(
            console_options_frame,
            text="隐藏新控制台",
            variable=self.console_var,
            value="hide",
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        hide_radio.pack(anchor="w", padx=15, pady=(5, 10))

    def create_advanced_tab_content(self):
        """创建高级设置标签页内容"""
        # 创建滚动框架，设置为透明背景以与内容区域融合
        scroll_frame = ctk.CTkScrollableFrame(
            self.advanced_frame, fg_color="transparent"
        )
        scroll_frame.pack(fill="both", expand=True, padx=0, pady=0)

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
            output_frame,
            text="输出目录 (所有输出文件的顶级目录):",
            font=self.title_font,
        )
        output_label.pack(anchor="w", padx=15, pady=(15, 8))

        output_input_frame = ctk.CTkFrame(
            output_frame, fg_color="#F9FAFB", corner_radius=8
        )
        output_input_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.output_entry = ctk.CTkEntry(
            output_input_frame,
            placeholder_text="指定中间及最终输出位置 (默认：当前目录) ",
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

        # 输出文件夹名称
        folder_name_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#F9FAFB",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB",
        )
        folder_name_frame.pack(fill="x", pady=(0, 15))

        folder_name_label = ctk.CTkLabel(
            folder_name_frame,
            text="输出文件夹名称 (实际编译结果所在子文件夹):",
            font=self.title_font,
        )
        folder_name_label.pack(anchor="w", padx=15, pady=(15, 8))

        self.folder_name_entry = ctk.CTkEntry(
            folder_name_frame,
            placeholder_text="指定发布文件夹 (standalone) 或 app 包 (macOS) 名称。默认主模块基名加 '.dist' 或 '.app'",
            fg_color=self.entry_fg_color,
            border_color=self.entry_border_color,
            border_width=self.entry_border_width,
            corner_radius=self.entry_corner_radius,
            font=self.entry_font,
        )
        self.folder_name_entry.pack(fill="x", padx=15, pady=(0, 15))

        # 进度条模式
        progress_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#F9FAFB",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB",
        )
        progress_frame.pack(fill="x", pady=(0, 15))

        progress_label = ctk.CTkLabel(
            progress_frame, text="进度条模式:", font=self.title_font
        )
        progress_label.pack(anchor="w", padx=15, pady=(15, 8))

        progress_options_frame = ctk.CTkFrame(
            progress_frame, fg_color="#F9FAFB", corner_radius=8
        )
        progress_options_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.progress_var = tk.StringVar(value="auto")
        auto_radio = ctk.CTkRadioButton(
            progress_options_frame,
            text="自动 (优先tqdm，其次rich)",
            variable=self.progress_var,
            value="auto",
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        auto_radio.pack(anchor="w", padx=15, pady=(10, 5))

        tqdm_radio = ctk.CTkRadioButton(
            progress_options_frame,
            text="tqdm",
            variable=self.progress_var,
            value="tqdm",
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        tqdm_radio.pack(anchor="w", padx=15, pady=(5, 5))

        rich_radio = ctk.CTkRadioButton(
            progress_options_frame,
            text="rich",
            variable=self.progress_var,
            value="rich",
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        rich_radio.pack(anchor="w", padx=15, pady=(5, 5))

        none_radio = ctk.CTkRadioButton(
            progress_options_frame,
            text="不显示进度条",
            variable=self.progress_var,
            value="none",
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        none_radio.pack(anchor="w", padx=15, pady=(5, 10))

        # 编译选项
        compile_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#F9FAFB",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB",
        )
        compile_frame.pack(fill="x", pady=(0, 15))

        compile_label = ctk.CTkLabel(
            compile_frame, text="编译选项:", font=self.title_font
        )
        compile_label.pack(anchor="w", padx=15, pady=(15, 8))

        options_frame = ctk.CTkFrame(compile_frame, fg_color="#F9FAFB", corner_radius=8)
        options_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.remove_output_var = tk.BooleanVar(value=False)
        remove_output_check = ctk.CTkCheckBox(
            options_frame,
            text="生成模块或exe后删除build目录",
            variable=self.remove_output_var,
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        remove_output_check.pack(anchor="w", padx=15, pady=(10, 5))

        self.show_memory_var = tk.BooleanVar(value=False)
        show_memory_check = ctk.CTkCheckBox(
            options_frame,
            text="提供内存使用信息",
            variable=self.show_memory_var,
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        show_memory_check.pack(anchor="w", padx=15, pady=(5, 10))

        # 并行任务数
        jobs_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#F9FAFB",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB",
        )
        jobs_frame.pack(fill="x", pady=(0, 15))

        jobs_label = ctk.CTkLabel(jobs_frame, text="并行任务数:", font=self.title_font)
        jobs_label.pack(anchor="w", padx=15, pady=(15, 8))

        jobs_input_frame = ctk.CTkFrame(jobs_frame, fg_color="#F9FAFB", corner_radius=8)
        jobs_input_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.jobs_entry = ctk.CTkEntry(
            jobs_input_frame,
            placeholder_text="并行C编译任务数 (0表示自动，负值表示CPU核数减去N) ",
            fg_color=self.entry_fg_color,
            border_color=self.entry_border_color,
            border_width=self.entry_border_width,
            corner_radius=self.entry_corner_radius,
            font=self.entry_font,
        )
        self.jobs_entry.pack(fill="x", padx=15, pady=10)

        # 链接时优化
        lto_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#F9FAFB",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB",
        )
        lto_frame.pack(fill="x", pady=(0, 15))

        lto_label = ctk.CTkLabel(lto_frame, text="链接时优化:", font=self.title_font)
        lto_label.pack(anchor="w", padx=15, pady=(15, 8))

        lto_options_frame = ctk.CTkFrame(lto_frame, fg_color="#F9FAFB", corner_radius=8)
        lto_options_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.lto_var = tk.StringVar(value="auto")
        lto_auto_radio = ctk.CTkRadioButton(
            lto_options_frame,
            text="自动",
            variable=self.lto_var,
            value="auto",
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        lto_auto_radio.pack(anchor="w", padx=15, pady=(10, 5))

        lto_yes_radio = ctk.CTkRadioButton(
            lto_options_frame,
            text="启用",
            variable=self.lto_var,
            value="yes",
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        lto_yes_radio.pack(anchor="w", padx=15, pady=(5, 5))

        lto_no_radio = ctk.CTkRadioButton(
            lto_options_frame,
            text="禁用",
            variable=self.lto_var,
            value="no",
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        lto_no_radio.pack(anchor="w", padx=15, pady=(5, 10))

        # 静态链接Python库
        static_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#F9FAFB",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB",
        )
        static_frame.pack(fill="x", pady=(0, 15))

        static_label = ctk.CTkLabel(
            static_frame, text="静态链接Python库:", font=self.title_font
        )
        static_label.pack(anchor="w", padx=15, pady=(15, 8))

        static_options_frame = ctk.CTkFrame(
            static_frame, fg_color="#F9FAFB", corner_radius=8
        )
        static_options_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.static_libpython_var = tk.StringVar(value="auto")
        static_auto_radio = ctk.CTkRadioButton(
            static_options_frame,
            text="自动",
            variable=self.static_libpython_var,
            value="auto",
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        static_auto_radio.pack(anchor="w", padx=15, pady=(10, 5))

        static_yes_radio = ctk.CTkRadioButton(
            static_options_frame,
            text="启用",
            variable=self.static_libpython_var,
            value="yes",
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        static_yes_radio.pack(anchor="w", padx=15, pady=(5, 5))

        static_no_radio = ctk.CTkRadioButton(
            static_options_frame,
            text="禁用",
            variable=self.static_libpython_var,
            value="no",
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        static_no_radio.pack(anchor="w", padx=15, pady=(5, 10))

        # Onefile选项
        onefile_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#F9FAFB",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB",
        )
        onefile_frame.pack(fill="x", pady=(0, 15))

        onefile_label = ctk.CTkLabel(
            onefile_frame, text="Onefile选项:", font=self.title_font
        )
        onefile_label.pack(anchor="w", padx=15, pady=(15, 8))

        onefile_options_frame = ctk.CTkFrame(
            onefile_frame, fg_color="#F9FAFB", corner_radius=8
        )
        onefile_options_frame.pack(fill="x", padx=15, pady=(0, 15))

        # 解压目录规范
        tempdir_frame = ctk.CTkFrame(onefile_options_frame, fg_color="#F9FAFB")
        tempdir_frame.pack(fill="x", pady=(0, 10))

        tempdir_label = ctk.CTkLabel(
            tempdir_frame,
            text="解压目录规范:",
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        tempdir_label.pack(side="left", padx=(0, 10), pady=10)

        self.tempdir_entry = ctk.CTkEntry(
            tempdir_frame,
            placeholder_text="默认 '{TEMP}/onefile_{PID}_{TIME}'",
            fg_color=self.entry_fg_color,
            border_color=self.entry_border_color,
            border_width=self.entry_border_width,
            corner_radius=self.entry_corner_radius,
            font=self.entry_font,
        )
        self.tempdir_entry.pack(
            side="left", fill="x", expand=True, padx=(0, 15), pady=10
        )

        # 缓存模式
        cache_frame = ctk.CTkFrame(onefile_options_frame, fg_color="#F9FAFB")
        cache_frame.pack(fill="x", pady=(0, 10))

        cache_label = ctk.CTkLabel(
            cache_frame,
            text="缓存模式:",
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        cache_label.pack(side="left", padx=(0, 10), pady=10)

        self.cache_entry = ctk.CTkEntry(
            cache_frame,
            placeholder_text="temporary 或 cached",
            fg_color=self.entry_fg_color,
            border_color=self.entry_border_color,
            border_width=self.entry_border_width,
            corner_radius=self.entry_corner_radius,
            font=self.entry_font,
        )
        self.cache_entry.pack(side="left", fill="x", expand=True, padx=(0, 15), pady=10)

        onefile_options_check_frame = ctk.CTkFrame(
            onefile_frame, fg_color="#F9FAFB", corner_radius=8
        )
        onefile_options_check_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.archive_var = tk.BooleanVar(value=False)
        archive_check = ctk.CTkCheckBox(
            onefile_options_check_frame,
            text="使用可手动解压的归档格式",
            variable=self.archive_var,
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        archive_check.pack(anchor="w", padx=15, pady=(10, 5))

        self.no_dll_var = tk.BooleanVar(value=False)
        no_dll_check = ctk.CTkCheckBox(
            onefile_options_check_frame,
            text="强制使用可执行文件而非DLL",
            variable=self.no_dll_var,
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        no_dll_check.pack(anchor="w", padx=15, pady=(5, 10))

        # 警告控制
        warnings_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#F9FAFB",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB",
        )
        warnings_frame.pack(fill="x", pady=(0, 15))

        warnings_label = ctk.CTkLabel(
            warnings_frame, text="警告控制:", font=self.title_font
        )
        warnings_label.pack(anchor="w", padx=15, pady=(15, 8))

        warnings_options_frame = ctk.CTkFrame(
            warnings_frame, fg_color="#F9FAFB", corner_radius=8
        )
        warnings_options_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.warn_implicit_exceptions_var = tk.BooleanVar(value=False)
        warn_implicit_exceptions_check = ctk.CTkCheckBox(
            warnings_options_frame,
            text="对隐式异常发出警告",
            variable=self.warn_implicit_exceptions_var,
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        warn_implicit_exceptions_check.pack(anchor="w", padx=15, pady=(10, 5))

        self.warn_unusual_code_var = tk.BooleanVar(value=False)
        warn_unusual_code_check = ctk.CTkCheckBox(
            warnings_options_frame,
            text="对异常代码发出警告",
            variable=self.warn_unusual_code_var,
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        warn_unusual_code_check.pack(anchor="w", padx=15, pady=(5, 5))

        self.assume_yes_for_downloads_var = tk.BooleanVar(value=False)
        assume_yes_for_downloads_check = ctk.CTkCheckBox(
            warnings_options_frame,
            text="允许自动下载外部代码",
            variable=self.assume_yes_for_downloads_var,
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        assume_yes_for_downloads_check.pack(anchor="w", padx=15, pady=(5, 10))

        # 缓存控制
        cache_control_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#F9FAFB",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB",
        )
        cache_control_frame.pack(fill="x", pady=(0, 15))

        cache_control_label = ctk.CTkLabel(
            cache_control_frame, text="缓存控制:", font=self.title_font
        )
        cache_control_label.pack(anchor="w", padx=15, pady=(15, 8))

        cache_control_options_frame = ctk.CTkFrame(
            cache_control_frame, fg_color="#F9FAFB", corner_radius=8
        )
        cache_control_options_frame.pack(fill="x", padx=15, pady=(0, 15))

        # 清理缓存
        clean_cache_frame = ctk.CTkFrame(
            cache_control_options_frame, fg_color="#F9FAFB"
        )
        clean_cache_frame.pack(fill="x", pady=(0, 10))

        clean_cache_label = ctk.CTkLabel(
            clean_cache_frame,
            text="清理缓存:",
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        clean_cache_label.pack(side="left", padx=(0, 10), pady=10)

        self.clean_cache_entry = ctk.CTkEntry(
            clean_cache_frame,
            placeholder_text="要清理的缓存名 (可选) ",
            fg_color=self.entry_fg_color,
            border_color=self.entry_border_color,
            border_width=self.entry_border_width,
            corner_radius=self.entry_corner_radius,
            font=self.entry_font,
        )
        self.clean_cache_entry.pack(
            side="left", fill="x", expand=True, padx=(0, 15), pady=10
        )

        self.force_dll_dependency_cache_update_var = tk.BooleanVar(value=False)
        force_dll_dependency_cache_update_check = ctk.CTkCheckBox(
            cache_control_options_frame,
            text="强制更新DLL依赖缓存",
            variable=self.force_dll_dependency_cache_update_var,
            font=ctk.CTkFont(family=self.font_family, size=12),
        )
        force_dll_dependency_cache_update_check.pack(anchor="w", padx=15, pady=(5, 10))

    def create_files_tab_content(self):
        """创建文件设置标签页内容"""
        # 创建滚动框架，设置为透明背景以与内容区域融合
        scroll_frame = ctk.CTkScrollableFrame(self.files_frame, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # 包含的包
        include_packages_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#F9FAFB",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB",
        )
        include_packages_frame.pack(fill="x", pady=(0, 15))

        include_packages_label = ctk.CTkLabel(
            include_packages_frame, text="包含的包:", font=self.title_font
        )
        include_packages_label.pack(anchor="w", padx=15, pady=(15, 8))

        include_packages_input_frame = ctk.CTkFrame(
            include_packages_frame, fg_color="#F9FAFB", corner_radius=8
        )
        include_packages_input_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.include_packages_entry = ctk.CTkEntry(
            include_packages_input_frame,
            placeholder_text="输入要包含的包名",
            fg_color=self.entry_fg_color,
            border_color=self.entry_border_color,
            border_width=self.entry_border_width,
            corner_radius=self.entry_corner_radius,
            font=self.entry_font,
        )
        self.include_packages_entry.pack(
            side="left", fill="x", expand=True, padx=(10, 8), pady=10
        )

        include_packages_add_btn = self.create_add_button(
            include_packages_input_frame, "添加", self.add_include_package
        )
        include_packages_add_btn.pack(side="right", padx=(0, 10), pady=10)

        # 包含的包列表
        include_packages_list_container = ctk.CTkFrame(
            include_packages_frame,
            fg_color="#FFFFFF",
            corner_radius=8,
            border_width=1,
            border_color="#D1D5DB",
        )
        include_packages_list_container.pack(fill="x", padx=15, pady=(0, 15))

        self.include_packages_listbox = tk.Listbox(
            include_packages_list_container,
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
        self.include_packages_listbox.pack(fill="both", expand=True, padx=8, pady=8)

        include_packages_list_frame = ctk.CTkFrame(
            include_packages_frame, fg_color="#F9FAFB", corner_radius=8
        )
        include_packages_list_frame.pack(fill="x", padx=15, pady=(0, 15))

        include_packages_remove_btn = self.create_remove_button(
            include_packages_list_frame, "移除选中", self.remove_include_package
        )
        include_packages_remove_btn.pack(side="left", padx=15, pady=10)

        include_packages_clear_btn = self.create_clear_button(
            include_packages_list_frame, "清空全部", self.clear_include_packages
        )
        include_packages_clear_btn.pack(side="left", padx=8, pady=10)

        # 包含的模块
        include_modules_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#F9FAFB",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB",
        )
        include_modules_frame.pack(fill="x", pady=(0, 15))

        include_modules_label = ctk.CTkLabel(
            include_modules_frame, text="包含的模块:", font=self.title_font
        )
        include_modules_label.pack(anchor="w", padx=15, pady=(15, 8))

        include_modules_input_frame = ctk.CTkFrame(
            include_modules_frame, fg_color="#F9FAFB", corner_radius=8
        )
        include_modules_input_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.include_modules_entry = ctk.CTkEntry(
            include_modules_input_frame,
            placeholder_text="输入要包含的模块名",
            fg_color=self.entry_fg_color,
            border_color=self.entry_border_color,
            border_width=self.entry_border_width,
            corner_radius=self.entry_corner_radius,
            font=self.entry_font,
        )
        self.include_modules_entry.pack(
            side="left", fill="x", expand=True, padx=(10, 8), pady=10
        )

        include_modules_add_btn = self.create_add_button(
            include_modules_input_frame, "添加", self.add_include_module
        )
        include_modules_add_btn.pack(side="right", padx=(0, 10), pady=10)

        # 包含的模块列表
        include_modules_list_container = ctk.CTkFrame(
            include_modules_frame,
            fg_color="#FFFFFF",
            corner_radius=8,
            border_width=1,
            border_color="#D1D5DB",
        )
        include_modules_list_container.pack(fill="x", padx=15, pady=(0, 15))

        self.include_modules_listbox = tk.Listbox(
            include_modules_list_container,
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
        self.include_modules_listbox.pack(fill="both", expand=True, padx=8, pady=8)

        include_modules_list_frame = ctk.CTkFrame(
            include_modules_frame, fg_color="#F9FAFB", corner_radius=8
        )
        include_modules_list_frame.pack(fill="x", padx=15, pady=(0, 15))

        include_modules_remove_btn = self.create_remove_button(
            include_modules_list_frame, "移除选中", self.remove_include_module
        )
        include_modules_remove_btn.pack(side="left", padx=15, pady=10)

        include_modules_clear_btn = self.create_clear_button(
            include_modules_list_frame, "清空全部", self.clear_include_modules
        )
        include_modules_clear_btn.pack(side="left", padx=8, pady=10)

        # 包含的插件目录
        include_plugin_dirs_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#F9FAFB",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB",
        )
        include_plugin_dirs_frame.pack(fill="x", pady=(0, 15))

        include_plugin_dirs_label = ctk.CTkLabel(
            include_plugin_dirs_frame, text="包含的插件目录:", font=self.title_font
        )
        include_plugin_dirs_label.pack(anchor="w", padx=15, pady=(15, 8))

        include_plugin_dirs_input_frame = ctk.CTkFrame(
            include_plugin_dirs_frame, fg_color="#F9FAFB", corner_radius=8
        )
        include_plugin_dirs_input_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.include_plugin_dirs_entry = ctk.CTkEntry(
            include_plugin_dirs_input_frame,
            placeholder_text="输入要包含的插件目录路径",
            fg_color=self.entry_fg_color,
            border_color=self.entry_border_color,
            border_width=self.entry_border_width,
            corner_radius=self.entry_corner_radius,
            font=self.entry_font,
        )
        self.include_plugin_dirs_entry.pack(
            side="left", fill="x", expand=True, padx=(10, 8), pady=10
        )

        include_plugin_dirs_add_btn = self.create_add_button(
            include_plugin_dirs_input_frame, "添加", self.add_include_plugin_dir
        )
        include_plugin_dirs_add_btn.pack(side="right", padx=(0, 10), pady=10)

        # 包含的插件目录列表
        include_plugin_dirs_list_container = ctk.CTkFrame(
            include_plugin_dirs_frame,
            fg_color="#FFFFFF",
            corner_radius=8,
            border_width=1,
            border_color="#D1D5DB",
        )
        include_plugin_dirs_list_container.pack(fill="x", padx=15, pady=(0, 15))

        self.include_plugin_dirs_listbox = tk.Listbox(
            include_plugin_dirs_list_container,
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
        self.include_plugin_dirs_listbox.pack(fill="both", expand=True, padx=8, pady=8)

        include_plugin_dirs_list_frame = ctk.CTkFrame(
            include_plugin_dirs_frame, fg_color="#F9FAFB", corner_radius=8
        )
        include_plugin_dirs_list_frame.pack(fill="x", padx=15, pady=(0, 15))

        include_plugin_dirs_remove_btn = self.create_remove_button(
            include_plugin_dirs_list_frame, "移除选中", self.remove_include_plugin_dir
        )
        include_plugin_dirs_remove_btn.pack(side="left", padx=15, pady=10)

        include_plugin_dirs_clear_btn = self.create_clear_button(
            include_plugin_dirs_list_frame, "清空全部", self.clear_include_plugin_dirs
        )
        include_plugin_dirs_clear_btn.pack(side="left", padx=8, pady=10)

        # 启用的插件
        enable_plugins_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#F9FAFB",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB",
        )
        enable_plugins_frame.pack(fill="x", pady=(0, 15))

        enable_plugins_label = ctk.CTkLabel(
            enable_plugins_frame, text="启用的插件:", font=self.title_font
        )
        enable_plugins_label.pack(anchor="w", padx=15, pady=(15, 8))

        enable_plugins_input_frame = ctk.CTkFrame(
            enable_plugins_frame, fg_color="#F9FAFB", corner_radius=8
        )
        enable_plugins_input_frame.pack(fill="x", padx=15, pady=(0, 15))

        # 创建插件下拉菜单
        self.enable_plugins_combobox = ctk.CTkComboBox(
            enable_plugins_input_frame,
            values=self.available_plugins,
            fg_color=self.entry_fg_color,
            border_color=self.entry_border_color,
            border_width=self.entry_border_width,
            corner_radius=self.entry_corner_radius,
            font=self.entry_font,
            dropdown_font=self.entry_font,
        )
        self.enable_plugins_combobox.pack(
            side="left", fill="x", expand=True, padx=(10, 8), pady=10
        )
        self.enable_plugins_combobox.set("选择要启用的插件")

        enable_plugins_add_btn = self.create_add_button(
            enable_plugins_input_frame, "添加", self.add_enable_plugin
        )
        enable_plugins_add_btn.pack(side="right", padx=(0, 10), pady=10)

        # 启用的插件列表
        enable_plugins_list_container = ctk.CTkFrame(
            enable_plugins_frame,
            fg_color="#FFFFFF",
            corner_radius=8,
            border_width=1,
            border_color="#D1D5DB",
        )
        enable_plugins_list_container.pack(fill="x", padx=15, pady=(0, 15))

        self.enable_plugins_listbox = tk.Listbox(
            enable_plugins_list_container,
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
        self.enable_plugins_listbox.pack(fill="both", expand=True, padx=8, pady=8)

        enable_plugins_list_frame = ctk.CTkFrame(
            enable_plugins_frame, fg_color="#F9FAFB", corner_radius=8
        )
        enable_plugins_list_frame.pack(fill="x", padx=15, pady=(0, 15))

        enable_plugins_remove_btn = self.create_remove_button(
            enable_plugins_list_frame, "移除选中", self.remove_enable_plugin
        )
        enable_plugins_remove_btn.pack(side="left", padx=15, pady=10)

        enable_plugins_clear_btn = self.create_clear_button(
            enable_plugins_list_frame, "清空全部", self.clear_enable_plugins
        )
        enable_plugins_clear_btn.pack(side="left", padx=8, pady=10)

        # 禁用的插件
        disable_plugins_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#F9FAFB",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB",
        )
        disable_plugins_frame.pack(fill="x", pady=(0, 15))

        disable_plugins_label = ctk.CTkLabel(
            disable_plugins_frame, text="禁用的插件:", font=self.title_font
        )
        disable_plugins_label.pack(anchor="w", padx=15, pady=(15, 8))

        disable_plugins_input_frame = ctk.CTkFrame(
            disable_plugins_frame, fg_color="#F9FAFB", corner_radius=8
        )
        disable_plugins_input_frame.pack(fill="x", padx=15, pady=(0, 15))

        # 创建插件下拉菜单
        self.disable_plugins_combobox = ctk.CTkComboBox(
            disable_plugins_input_frame,
            values=self.available_plugins,
            fg_color=self.entry_fg_color,
            border_color=self.entry_border_color,
            border_width=self.entry_border_width,
            corner_radius=self.entry_corner_radius,
            font=self.entry_font,
            dropdown_font=self.entry_font,
        )
        self.disable_plugins_combobox.pack(
            side="left", fill="x", expand=True, padx=(10, 8), pady=10
        )
        self.disable_plugins_combobox.set("选择要禁用的插件")

        disable_plugins_add_btn = self.create_add_button(
            disable_plugins_input_frame, "添加", self.add_disable_plugin
        )
        disable_plugins_add_btn.pack(side="right", padx=(0, 10), pady=10)

        # 禁用的插件列表
        disable_plugins_list_container = ctk.CTkFrame(
            disable_plugins_frame,
            fg_color="#FFFFFF",
            corner_radius=8,
            border_width=1,
            border_color="#D1D5DB",
        )
        disable_plugins_list_container.pack(fill="x", padx=15, pady=(0, 15))

        self.disable_plugins_listbox = tk.Listbox(
            disable_plugins_list_container,
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
        self.disable_plugins_listbox.pack(fill="both", expand=True, padx=8, pady=8)

        disable_plugins_list_frame = ctk.CTkFrame(
            disable_plugins_frame, fg_color="#F9FAFB", corner_radius=8
        )
        disable_plugins_list_frame.pack(fill="x", padx=15, pady=(0, 15))

        disable_plugins_remove_btn = self.create_remove_button(
            disable_plugins_list_frame, "移除选中", self.remove_disable_plugin
        )
        disable_plugins_remove_btn.pack(side="left", padx=15, pady=10)

        disable_plugins_clear_btn = self.create_clear_button(
            disable_plugins_list_frame, "清空全部", self.clear_disable_plugins
        )
        disable_plugins_clear_btn.pack(side="left", padx=8, pady=10)

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
        """创建浏览按钮 (次要功能)

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
        """创建添加按钮 (一般功能)

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
        """创建移除按钮 (警告功能)

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
        """创建清空按钮 (危险功能)

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
        """创建主要按钮 (最重要功能)

        Args:
            parent: 父容器
            text: 按钮文本
            command: 按钮命令
            width: 按钮宽度
            height: 按钮高度 (可选)

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

    def browse_icon(self):
        """浏览图标文件"""
        file_path = browse_icon_file(self.parent)
        if file_path:
            self.icon_entry.delete(0, tk.END)
            self.icon_entry.insert(0, file_path)

    # 包含的包方法
    def add_include_package(self):
        """添加包含的包"""
        package_name = self.include_packages_entry.get().strip()
        if package_name:
            self.include_packages_listbox.insert(tk.END, package_name)
            self.include_packages_entry.delete(0, tk.END)

    def remove_include_package(self):
        """移除选中的包含的包"""
        selection = self.include_packages_listbox.curselection()
        if selection:
            self.include_packages_listbox.delete(selection[0])

    def clear_include_packages(self):
        """清空所有包含的包"""
        self.include_packages_listbox.delete(0, tk.END)

    # 包含的模块方法
    def add_include_module(self):
        """添加包含的模块"""
        module_name = self.include_modules_entry.get().strip()
        if module_name:
            self.include_modules_listbox.insert(tk.END, module_name)
            self.include_modules_entry.delete(0, tk.END)

    def remove_include_module(self):
        """移除选中的包含的模块"""
        selection = self.include_modules_listbox.curselection()
        if selection:
            self.include_modules_listbox.delete(selection[0])

    def clear_include_modules(self):
        """清空所有包含的模块"""
        self.include_modules_listbox.delete(0, tk.END)

    # 包含的插件目录方法
    def add_include_plugin_dir(self):
        """添加包含的插件目录"""
        plugin_dir = self.include_plugin_dirs_entry.get().strip()
        if plugin_dir:
            self.include_plugin_dirs_listbox.insert(tk.END, plugin_dir)
            self.include_plugin_dirs_entry.delete(0, tk.END)

    def remove_include_plugin_dir(self):
        """移除选中的包含的插件目录"""
        selection = self.include_plugin_dirs_listbox.curselection()
        if selection:
            self.include_plugin_dirs_listbox.delete(selection[0])

    def clear_include_plugin_dirs(self):
        """清空所有包含的插件目录"""
        self.include_plugin_dirs_listbox.delete(0, tk.END)

    # 启用的插件方法
    def add_enable_plugin(self):
        """添加启用的插件"""
        plugin_full_name = self.enable_plugins_combobox.get().strip()
        if plugin_full_name and plugin_full_name != "选择要启用的插件":
            # 从完整字符串中提取插件名称（" - "前面的部分）
            plugin_name = plugin_full_name.split(" - ")[0]
            # 检查是否已存在
            existing_items = self.enable_plugins_listbox.get(0, tk.END)
            if plugin_name not in existing_items:
                self.enable_plugins_listbox.insert(tk.END, plugin_name)
            # 重置下拉菜单
            self.enable_plugins_combobox.set("选择要启用的插件")

    def remove_enable_plugin(self):
        """移除选中的启用的插件"""
        selection = self.enable_plugins_listbox.curselection()
        if selection:
            self.enable_plugins_listbox.delete(selection[0])

    def clear_enable_plugins(self):
        """清空所有启用的插件"""
        self.enable_plugins_listbox.delete(0, tk.END)

    # 禁用的插件方法
    def add_disable_plugin(self):
        """添加禁用的插件"""
        plugin_full_name = self.disable_plugins_combobox.get().strip()
        if plugin_full_name and plugin_full_name != "选择要禁用的插件":
            # 从完整字符串中提取插件名称（" - "前面的部分）
            plugin_name = plugin_full_name.split(" - ")[0]
            # 检查是否已存在
            existing_items = self.disable_plugins_listbox.get(0, tk.END)
            if plugin_name not in existing_items:
                self.disable_plugins_listbox.insert(tk.END, plugin_name)
            # 重置下拉菜单
            self.disable_plugins_combobox.set("选择要禁用的插件")

    def remove_disable_plugin(self):
        """移除选中的禁用的插件"""
        selection = self.disable_plugins_listbox.curselection()
        if selection:
            self.disable_plugins_listbox.delete(selection[0])

    def clear_disable_plugins(self):
        """清空所有禁用的插件"""
        self.disable_plugins_listbox.delete(0, tk.END)

    # 获取配置方法
    def get_include_packages(self):
        """获取包含的包列表"""
        return list(self.include_packages_listbox.get(0, tk.END))

    def get_include_modules(self):
        """获取包含的模块列表"""
        return list(self.include_modules_listbox.get(0, tk.END))

    def get_include_plugin_dirs(self):
        """获取包含的插件目录列表"""
        return list(self.include_plugin_dirs_listbox.get(0, tk.END))

    def get_enable_plugins(self):
        """获取启用的插件列表"""
        return list(self.enable_plugins_listbox.get(0, tk.END))

    def get_disable_plugins(self):
        """获取禁用的插件列表"""
        return list(self.disable_plugins_listbox.get(0, tk.END))

    # 配置相关方法
    def update_config(self):
        """更新配置对象"""
        self.config.script = self.script_entry.get()
        self.config.output_dir = self.output_entry.get()
        self.config.output_filename = self.name_entry.get()
        self.config.output_folder_name = self.folder_name_entry.get()
        self.config.icon = self.icon_entry.get()
        self.config.mode = self.mode_var.get()
        self.config.console_mode = self.console_var.get()
        self.config.progress_bar = self.progress_var.get()
        self.config.remove_output = self.remove_output_var.get()
        self.config.show_memory = self.show_memory_var.get()

        # 获取并行任务数
        jobs_text = self.jobs_entry.get().strip()
        self.config.jobs = int(jobs_text) if jobs_text else 0

        self.config.lto = self.lto_var.get()
        self.config.static_libpython = self.static_libpython_var.get()

        # 包含
        self.config.include_packages = self.get_include_packages()
        self.config.include_modules = self.get_include_modules()
        self.config.include_plugin_dirs = self.get_include_plugin_dirs()
        self.config.enable_plugins = self.get_enable_plugins()
        self.config.disable_plugins = self.get_disable_plugins()

        # onefile选项
        self.config.onefile_tempdir_spec = self.tempdir_entry.get()
        self.config.onefile_cache_mode = self.cache_entry.get()
        self.config.onefile_as_archive = self.archive_var.get()
        self.config.onefile_no_dll = self.no_dll_var.get()

        # 警告控制
        self.config.warn_implicit_exceptions = self.warn_implicit_exceptions_var.get()
        self.config.warn_unusual_code = self.warn_unusual_code_var.get()
        self.config.assume_yes_for_downloads = self.assume_yes_for_downloads_var.get()

        # 缓存控制
        self.config.clean_cache = self.clean_cache_entry.get()
        self.config.force_dll_dependency_cache_update = (
            self.force_dll_dependency_cache_update_var.get()
        )

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
        self.main_window.process_ui.start_nuitka_build(self.config)

    def load_config(self, config):
        """加载配置到UI

        Args:
            config: NuitkaConfig对象
        """
        self.config = config

        # 基础设置
        self.script_entry.delete(0, tk.END)
        self.script_entry.insert(0, config.script)

        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, config.output_filename)

        self.folder_name_entry.delete(0, tk.END)
        self.folder_name_entry.insert(0, config.output_folder_name)

        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, config.output_dir)

        self.icon_entry.delete(0, tk.END)
        self.icon_entry.insert(0, config.icon)

        self.mode_var.set(config.mode)
        self.console_var.set(config.console_mode)

        # 高级设置
        self.progress_var.set(config.progress_bar)
        self.remove_output_var.set(config.remove_output)
        self.show_memory_var.set(config.show_memory)

        self.jobs_entry.delete(0, tk.END)
        self.jobs_entry.insert(0, str(config.jobs) if config.jobs != 0 else "")

        self.lto_var.set(config.lto)
        self.static_libpython_var.set(config.static_libpython)

        # 包含
        self.include_packages_listbox.delete(0, tk.END)
        for package in config.include_packages:
            self.include_packages_listbox.insert(tk.END, package)

        self.include_modules_listbox.delete(0, tk.END)
        for module in config.include_modules:
            self.include_modules_listbox.insert(tk.END, module)

        self.include_plugin_dirs_listbox.delete(0, tk.END)
        for plugin_dir in config.include_plugin_dirs:
            self.include_plugin_dirs_listbox.insert(tk.END, plugin_dir)

        self.enable_plugins_listbox.delete(0, tk.END)
        for plugin in config.enable_plugins:
            self.enable_plugins_listbox.insert(tk.END, plugin)

        self.disable_plugins_listbox.delete(0, tk.END)
        for plugin in config.disable_plugins:
            self.disable_plugins_listbox.insert(tk.END, plugin)

        # onefile选项
        self.tempdir_entry.delete(0, tk.END)
        self.tempdir_entry.insert(0, config.onefile_tempdir_spec)

        self.cache_entry.delete(0, tk.END)
        self.cache_entry.insert(0, config.onefile_cache_mode)

        self.archive_var.set(config.onefile_as_archive)
        self.no_dll_var.set(config.onefile_no_dll)

        # 警告控制
        self.warn_implicit_exceptions_var.set(config.warn_implicit_exceptions)
        self.warn_unusual_code_var.set(config.warn_unusual_code)
        self.assume_yes_for_downloads_var.set(config.assume_yes_for_downloads)

        # 缓存控制
        self.clean_cache_entry.delete(0, tk.END)
        self.clean_cache_entry.insert(0, config.clean_cache)

        self.force_dll_dependency_cache_update_var.set(
            config.force_dll_dependency_cache_update
        )

        # 更新摘要
        self.update_summary()

    def reset_config(self):
        """重置配置为默认值"""
        self.config.reset_config()
        self.load_config(self.config)
