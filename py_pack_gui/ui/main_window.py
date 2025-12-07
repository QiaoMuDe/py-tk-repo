"""
主窗口模块
提供应用程序的主窗口界面
"""

import tkinter as tk
import os
import customtkinter as ctk
import windnd as wd
from ui.pyinstaller_tab import PyInstallerTab
from ui.nuitka_tab import NuitkaTab
from ui.process_tab import ProcessTab
from utils.window_utils import center_window
from ctypes import windll
import tkinter.messagebox as messagebox

# 版本号
VERSION = "v1.0.0"


class MainWindow:
    """主窗口类"""

    def __init__(self):
        """初始化主窗口"""
        # 设置字体族
        self.font_family = "Microsoft YaHei UI"

        # 设置CTK主题
        ctk.set_appearance_mode("light")  # 可选: "light", "dark", "system"
        ctk.set_default_color_theme("dark-blue")  # 可选: "blue", "green", "dark-blue"

        # 创建主窗口
        self.root = ctk.CTk()
        self.root.title("Python GUI 打包编译工具")
        # self.root.geometry("1200x800")
        self.root.minsize(1000, 600)

        # 设置字体（必须在CTk()创建之后）
        self.default_font = ctk.CTkFont(family=self.font_family, size=13)
        self.title_font = ctk.CTkFont(family=self.font_family, size=16, weight="bold")
        self.tab_font = ctk.CTkFont(family=self.font_family, size=15, weight="bold")

        """启用DPI缩放支持"""
        try:
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception as e:
            print(f"警告: 无法启用DPI缩放支持: {e}")

        # 将窗口居中显示
        center_window(self.root, 1200, 800)

        # 创建主框架
        self.main_frame = ctk.CTkFrame(self.root, fg_color="#F8FAFC", corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)

        # 创建状态栏
        self.create_status_bar()

        # 创建主要内容区域
        self.create_main_content()

        # 当前标签页
        self.current_tab = None

        # 注册拖拽事件
        self.register_drag_events()

    def register_drag_events(self):
        """注册拖拽事件"""
        try:
            # 使用windnd库注册拖拽事件
            wd.hook_dropfiles(self.root, func=self.handle_drag_drop)
        except Exception as e:
            print(f"拖拽功能初始化失败: {e}")
            if hasattr(self, "status_label"):
                self.status_label.configure(text=f"拖拽功能初始化失败: {str(e)}")

    def handle_drag_drop(self, files):
        """处理拖拽文件

        Args:
            files: 拖拽的文件路径列表
        """
        try:
            # 检查是否只拖拽了一个文件
            if len(files) > 1:
                messagebox.showwarning("警告", "一次只能拖拽一个文件")
                return

            # 获取第一个文件的路径并解码
            file_path = files[0].decode("gbk")

            # 检查是否为文件
            if not os.path.isfile(file_path):
                messagebox.showerror("错误", "请拖拽文件，而不是目录")
                return

            # 检查是否为Python文件
            if not file_path.lower().endswith(".py"):
                messagebox.showerror("错误", "请拖拽Python脚本文件(.py)")
                return

            # 提取文件名作为应用名称（去除.py后缀）
            app_name = os.path.splitext(os.path.basename(file_path))[0]

            # 设置到PyInstaller配置
            self.pyinstaller_ui.script_entry.delete(0, tk.END)
            self.pyinstaller_ui.script_entry.insert(0, file_path)
            self.pyinstaller_ui.name_entry.delete(0, tk.END)
            self.pyinstaller_ui.name_entry.insert(0, app_name)

            # 设置到Nuitka配置
            self.nuitka_ui.script_entry.delete(0, tk.END)
            self.nuitka_ui.script_entry.insert(0, file_path)
            self.nuitka_ui.name_entry.delete(0, tk.END)
            self.nuitka_ui.name_entry.insert(0, app_name)

            # 更新状态栏
            if hasattr(self, "status_label"):
                self.status_label.configure(
                    text=f"已加载Python脚本: {os.path.basename(file_path)}"
                )

            # 显示成功提示
            messagebox.showinfo(
                "成功", f"已成功加载Python脚本: {os.path.basename(file_path)}"
            )

        except Exception as e:
            error_msg = f"处理拖拽文件时出错: {str(e)}"
            print(error_msg)
            if hasattr(self, "status_label"):
                self.status_label.configure(text=f"加载脚本失败: {str(e)}")
            messagebox.showerror("错误", error_msg)

    def create_main_content(self):
        """创建主要内容区域"""
        # 创建内容框架
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="#F8FAFC")
        self.content_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # 创建顶部导航栏
        self.navbar = ctk.CTkFrame(
            self.content_frame, fg_color="#1F2937", height=60, corner_radius=0
        )
        self.navbar.pack(fill="x", padx=0, pady=(0, 10))
        self.navbar.pack_propagate(False)  # 防止导航栏被内容撑大

        # 创建导航栏标题
        nav_title = ctk.CTkLabel(
            self.navbar,
            text="Python GUI 打包编译工具",
            font=ctk.CTkFont(family=self.font_family, size=18, weight="bold"),
            text_color="#F9FAFB",
        )
        nav_title.pack(side="left", padx=20, pady=15)

        # 创建标签页按钮容器
        self.tabs_container = ctk.CTkFrame(self.navbar, fg_color="transparent")
        self.tabs_container.pack(
            side="right", fill="both", expand=True, padx=(0, 20), pady=10
        )

        # 存储标签按钮和对应内容的映射
        self.tabs = {}
        self.active_tab = None

        # 创建水平排列的标签页按钮
        self.create_modern_tab_buttons()

        # 创建标签页内容区域
        self.tabs_content_area = ctk.CTkFrame(
            self.content_frame,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color="#E5E7EB",
        )
        self.tabs_content_area.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # 创建各个标签页内容
        self.create_all_tabs_content()

        # 默认显示第一个标签页
        self.switch_tab("pyinstaller")

    def create_modern_tab_buttons(self):
        """创建现代化的水平标签页按钮"""
        tab_configs = [
            ("pyinstaller", "PyInstaller", "🔧"),
            ("nuitka", "Nuitka", "⚡"),
            ("process", "打包过程", "📦"),
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
                hover_color="#374151",
                text_color="#D1D5DB",
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
        # 创建PyInstaller标签页
        self.pyinstaller_frame = ctk.CTkFrame(
            self.tabs_content_area, fg_color="transparent"
        )
        self.tabs["pyinstaller"]["frame"] = self.pyinstaller_frame
        self.pyinstaller_ui = PyInstallerTab(
            self.pyinstaller_frame, self, self.font_family
        )

        # 创建Nuitka标签页
        self.nuitka_frame = ctk.CTkFrame(self.tabs_content_area, fg_color="transparent")
        self.tabs["nuitka"]["frame"] = self.nuitka_frame
        self.nuitka_ui = NuitkaTab(self.nuitka_frame, self, self.font_family)

        # 创建打包过程标签页
        self.process_frame = ctk.CTkFrame(
            self.tabs_content_area, fg_color="transparent"
        )
        self.tabs["process"]["frame"] = self.process_frame
        self.process_ui = ProcessTab(self.process_frame, self, self.font_family)

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
                hover_color="#374151",
                text_color="#D1D5DB",
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

        # 更新状态栏（如果状态标签已初始化）
        if hasattr(self, "status_label"):
            if tab_id == "pyinstaller":
                self.status_label.configure(text="PyInstaller 打包配置")
            elif tab_id == "nuitka":
                self.status_label.configure(text="Nuitka 编译配置")
            elif tab_id == "process":
                self.status_label.configure(text="打包过程")

    def switch_to_process_tab(self):
        """切换到打包过程标签页"""
        self.switch_tab("process")

    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = ctk.CTkFrame(
            self.root, height=40, fg_color="#F8FAFC", corner_radius=0
        )
        self.status_bar.pack(fill="x", side="bottom", padx=0, pady=0)
        self.status_bar.pack_propagate(False)

        # 添加分隔线
        separator = ctk.CTkFrame(self.status_bar, height=1, fg_color="#E5E7EB")
        separator.pack(fill="x", side="top", padx=0, pady=0)

        # 状态标签
        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="就绪",
            font=ctk.CTkFont(family=self.font_family, size=12),
            text_color="#6B7280",
        )
        self.status_label.pack(side="left", padx=20, pady=10)

        # 版本标签
        self.version_label = ctk.CTkLabel(
            self.status_bar,
            text=VERSION,
            font=ctk.CTkFont(family=self.font_family, size=12),
            text_color="#9CA3AF",
        )
        self.version_label.pack(side="right", padx=20, pady=10)

    def switch_to_process_tab(self):
        """切换到打包过程标签页"""
        self.switch_tab("process")

    def run(self):
        """运行主窗口"""
        self.root.mainloop()


# if __name__ == "__main__":
#     app = MainWindow()
#     app.run()
