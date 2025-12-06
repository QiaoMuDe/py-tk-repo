"""
Nuitka标签页模块
提供Nuitka打包参数配置界面
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk


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
        
        # 设置字体
        self.default_font = ctk.CTkFont(family=self.font_family, size=12)
        self.title_font = ctk.CTkFont(family=self.font_family, size=14, weight="bold")
        
        # 创建界面
        self.create_ui()
    
    def create_ui(self):
        """创建用户界面"""
        # 创建滚动框架
        self.scroll_frame = ctk.CTkScrollableFrame(self.parent)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 基础参数区域
        self.create_basic_params()
        
        # 高级参数区域
        self.create_advanced_params()
        
        # 操作按钮区域
        self.create_action_buttons()
    
    def create_basic_params(self):
        """创建基础参数区域"""
        # 基础参数标题
        basic_title = ctk.CTkLabel(self.scroll_frame, text="基础参数", font=self.title_font)
        basic_title.pack(pady=(0, 10), anchor="w")
        
        # 脚本路径
        script_frame = ctk.CTkFrame(self.scroll_frame)
        script_frame.pack(fill="x", pady=5)
        
        script_label = ctk.CTkLabel(script_frame, text="脚本路径:", width=100)
        script_label.pack(side="left", padx=(10, 5), pady=10)
        
        self.script_entry = ctk.CTkEntry(script_frame)
        self.script_entry.pack(side="left", fill="x", expand=True, padx=(0, 5), pady=10)
        
        script_browse_btn = ctk.CTkButton(script_frame, text="浏览", width=60, command=self.browse_script)
        script_browse_btn.pack(side="right", padx=(0, 10), pady=10)
        
        # 输出目录
        output_frame = ctk.CTkFrame(self.scroll_frame)
        output_frame.pack(fill="x", pady=5)
        
        output_label = ctk.CTkLabel(output_frame, text="输出目录:", width=100)
        output_label.pack(side="left", padx=(10, 5), pady=10)
        
        self.output_entry = ctk.CTkEntry(output_frame)
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(0, 5), pady=10)
        
        output_browse_btn = ctk.CTkButton(output_frame, text="浏览", width=60, command=self.browse_output)
        output_browse_btn.pack(side="right", padx=(0, 10), pady=10)
        
        # 应用名称
        name_frame = ctk.CTkFrame(self.scroll_frame)
        name_frame.pack(fill="x", pady=5)
        
        name_label = ctk.CTkLabel(name_frame, text="应用名称:", width=100)
        name_label.pack(side="left", padx=(10, 5), pady=10)
        
        self.name_entry = ctk.CTkEntry(name_frame)
        self.name_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=10)
        
        # 图标文件
        icon_frame = ctk.CTkFrame(self.scroll_frame)
        icon_frame.pack(fill="x", pady=5)
        
        icon_label = ctk.CTkLabel(icon_frame, text="图标文件:", width=100)
        icon_label.pack(side="left", padx=(10, 5), pady=10)
        
        self.icon_entry = ctk.CTkEntry(icon_frame)
        self.icon_entry.pack(side="left", fill="x", expand=True, padx=(0, 5), pady=10)
        
        icon_browse_btn = ctk.CTkButton(icon_frame, text="浏览", width=60, command=self.browse_icon)
        icon_browse_btn.pack(side="right", padx=(0, 10), pady=10)
        
        # 打包模式
        mode_frame = ctk.CTkFrame(self.scroll_frame)
        mode_frame.pack(fill="x", pady=5)
        
        mode_label = ctk.CTkLabel(mode_frame, text="打包模式:", width=100)
        mode_label.pack(side="left", padx=(10, 5), pady=10)
        
        self.standalone_var = tk.BooleanVar(value=True)
        standalone_check = ctk.CTkCheckBox(mode_frame, text="独立可执行文件", variable=self.standalone_var)
        standalone_check.pack(side="left", pady=10)
        
        # 控制台模式
        console_frame = ctk.CTkFrame(self.scroll_frame)
        console_frame.pack(fill="x", pady=5)
        
        console_label = ctk.CTkLabel(console_frame, text="控制台模式:", width=100)
        console_label.pack(side="left", padx=(10, 5), pady=10)
        
        self.console_var = tk.BooleanVar(value=True)
        console_check = ctk.CTkCheckBox(console_frame, text="显示控制台", variable=self.console_var)
        console_check.pack(side="left", pady=10)
    
    def create_advanced_params(self):
        """创建高级参数区域"""
        # 高级参数标题
        advanced_title = ctk.CTkLabel(self.scroll_frame, text="高级参数", font=self.title_font)
        advanced_title.pack(pady=(20, 10), anchor="w")
        
        # 包含模块
        include_frame = ctk.CTkFrame(self.scroll_frame)
        include_frame.pack(fill="x", pady=5)
        
        include_label = ctk.CTkLabel(include_frame, text="包含模块:", width=100)
        include_label.pack(side="left", padx=(10, 5), pady=10)
        
        self.include_entry = ctk.CTkEntry(include_frame)
        self.include_entry.pack(side="left", fill="x", expand=True, padx=(0, 5), pady=10)
        
        include_add_btn = ctk.CTkButton(include_frame, text="添加", width=60, command=self.add_include_module)
        include_add_btn.pack(side="right", padx=(0, 10), pady=10)
        
        # 包含模块列表
        self.include_listbox = tk.Listbox(include_frame, height=4)
        self.include_listbox.pack(fill="x", padx=(115, 10), pady=(0, 10))
        
        # 包含数据文件
        data_frame = ctk.CTkFrame(self.scroll_frame)
        data_frame.pack(fill="x", pady=5)
        
        data_label = ctk.CTkLabel(data_frame, text="数据文件:", width=100)
        data_label.pack(side="left", padx=(10, 5), pady=10)
        
        self.data_entry = ctk.CTkEntry(data_frame)
        self.data_entry.pack(side="left", fill="x", expand=True, padx=(0, 5), pady=10)
        
        data_browse_btn = ctk.CTkButton(data_frame, text="浏览", width=60, command=self.browse_data_file)
        data_browse_btn.pack(side="right", padx=(0, 10), pady=10)
        
        # 数据文件列表
        self.data_listbox = tk.Listbox(data_frame, height=4)
        self.data_listbox.pack(fill="x", padx=(115, 10), pady=(0, 10))
        
        # 附加参数
        extra_frame = ctk.CTkFrame(self.scroll_frame)
        extra_frame.pack(fill="x", pady=5)
        
        extra_label = ctk.CTkLabel(extra_frame, text="附加参数:", width=100)
        extra_label.pack(side="left", padx=(10, 5), pady=10)
        
        self.extra_entry = ctk.CTkEntry(extra_frame)
        self.extra_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=10)
        
        # 优化选项
        optimize_frame = ctk.CTkFrame(self.scroll_frame)
        optimize_frame.pack(fill="x", pady=5)
        
        optimize_label = ctk.CTkLabel(optimize_frame, text="优化选项:", width=100)
        optimize_label.pack(side="left", padx=(10, 5), pady=10)
        
        self.optimize_var = tk.StringVar(value="O1")
        o0_radio = ctk.CTkRadioButton(optimize_frame, text="O0 (无优化)", variable=self.optimize_var, value="O0")
        o0_radio.pack(side="left", padx=(0, 10), pady=10)
        
        o1_radio = ctk.CTkRadioButton(optimize_frame, text="O1 (默认)", variable=self.optimize_var, value="O1")
        o1_radio.pack(side="left", padx=(0, 10), pady=10)
        
        o2_radio = ctk.CTkRadioButton(optimize_frame, text="O2 (更多)", variable=self.optimize_var, value="O2")
        o2_radio.pack(side="left", pady=10)
    
    def create_action_buttons(self):
        """创建操作按钮区域"""
        # 按钮框架
        button_frame = ctk.CTkFrame(self.scroll_frame)
        button_frame.pack(fill="x", pady=20)
        
        # 开始打包按钮
        self.build_btn = ctk.CTkButton(
            button_frame,
            text="开始打包",
            command=self.start_build,
            height=40,
            font=ctk.CTkFont(size=16)
        )
        self.build_btn.pack(pady=20)
    
    def browse_script(self):
        """浏览脚本文件"""
        file_path = filedialog.askopenfilename(
            title="选择Python脚本",
            filetypes=[("Python文件", "*.py"), ("所有文件", "*.*")]
        )
        if file_path:
            self.script_entry.delete(0, tk.END)
            self.script_entry.insert(0, file_path)
            
            # 如果应用名称为空，使用脚本文件名
            if not self.name_entry.get():
                import os
                script_name = os.path.splitext(os.path.basename(file_path))[0]
                self.name_entry.insert(0, script_name)
    
    def browse_output(self):
        """浏览输出目录"""
        dir_path = filedialog.askdirectory(title="选择输出目录")
        if dir_path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, dir_path)
    
    def browse_icon(self):
        """浏览图标文件"""
        file_path = filedialog.askopenfilename(
            title="选择图标文件",
            filetypes=[("图标文件", "*.ico"), ("所有文件", "*.*")]
        )
        if file_path:
            self.icon_entry.delete(0, tk.END)
            self.icon_entry.insert(0, file_path)
    
    def browse_data_file(self):
        """浏览数据文件"""
        file_path = filedialog.askopenfilename(
            title="选择数据文件",
            filetypes=[("所有文件", "*.*")]
        )
        if file_path:
            self.data_entry.delete(0, tk.END)
            self.data_entry.insert(0, file_path)
            self.add_data_file()
    
    def add_include_module(self):
        """添加包含模块"""
        module_name = self.include_entry.get().strip()
        if module_name:
            self.include_listbox.insert(tk.END, module_name)
            self.include_entry.delete(0, tk.END)
    
    def add_data_file(self):
        """添加数据文件"""
        file_path = self.data_entry.get().strip()
        if file_path:
            self.data_listbox.insert(tk.END, file_path)
            self.data_entry.delete(0, tk.END)
    
    def get_include_modules(self):
        """获取包含模块列表"""
        return list(self.include_listbox.get(0, tk.END))
    
    def get_data_files(self):
        """获取数据文件列表"""
        return list(self.data_listbox.get(0, tk.END))
    
    def set_script_path(self, path):
        """设置脚本路径"""
        self.script_entry.delete(0, tk.END)
        self.script_entry.insert(0, path)
        
        # 如果应用名称为空，使用脚本文件名
        if not self.name_entry.get():
            import os
            script_name = os.path.splitext(os.path.basename(path))[0]
            self.name_entry.insert(0, script_name)
    
    def start_build(self):
        """开始打包"""
        # 验证必填字段
        if not self.script_entry.get():
            messagebox.showerror("错误", "请选择脚本文件")
            return
        
        if not self.output_entry.get():
            messagebox.showerror("错误", "请选择输出目录")
            return
        
        # 切换到打包过程标签页
        self.main_window.switch_to_process_tab()
        
        # 获取配置参数
        config = {
            "script": self.script_entry.get(),
            "output": self.output_entry.get(),
            "name": self.name_entry.get() or "",
            "icon": self.icon_entry.get() or "",
            "standalone": self.standalone_var.get(),
            "console": self.console_var.get(),
            "include_modules": self.get_include_modules(),
            "data_files": self.get_data_files(),
            "optimize": self.optimize_var.get(),
            "extra_args": self.extra_entry.get() or ""
        }
        
        # 将配置传递给打包过程标签页
        self.main_window.process_ui.start_nuitka_build(config)