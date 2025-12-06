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
        self.default_font = ctk.CTkFont(family=self.font_family, size=12)
        self.title_font = ctk.CTkFont(family=self.font_family, size=16, weight="bold")

        """启用DPI缩放支持"""
        try:
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception as e:
            print(f"警告: 无法启用DPI缩放支持: {e}")

        # 将窗口居中显示
        center_window(self.root, 1200, 800)

        # 创建主框架
        self.main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)

        # 创建主要内容区域
        self.create_main_content()

        # 创建状态栏
        self.create_status_bar()

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
            self.status_label.configure(text=f"加载脚本失败: {str(e)}")
            messagebox.showerror("错误", error_msg)

    def create_main_content(self):
        """创建主要内容区域"""
        # 创建内容框架
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # 创建标签页控件
        self.tab_view = ctk.CTkTabview(self.content_frame)
        self.tab_view.pack(fill="both", expand=True, padx=5, pady=5)

        # 创建三个标签页
        self.pyinstaller_tab = self.tab_view.add("PyInstaller")
        self.nuitka_tab = self.tab_view.add("Nuitka")
        self.process_tab = self.tab_view.add("打包过程")

        # 设置标签页标题字体
        self.tab_view._segmented_button.configure(font=self.title_font)

        # 初始化标签页内容
        self.pyinstaller_ui = PyInstallerTab(
            self.pyinstaller_tab, self, self.font_family
        )
        self.nuitka_ui = NuitkaTab(self.nuitka_tab, self, self.font_family)
        self.process_ui = ProcessTab(self.process_tab, self, self.font_family)

        # 默认显示第一个标签页
        self.tab_view.set("PyInstaller")

    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = ctk.CTkFrame(self.root, height=30, fg_color="transparent")
        self.status_bar.pack(fill="x", side="bottom", padx=5, pady=5)
        self.status_bar.pack_propagate(False)

        # 状态标签
        self.status_label = ctk.CTkLabel(self.status_bar, text="就绪")
        self.status_label.pack(side="left", padx=10, pady=5)

        # 版本标签
        self.version_label = ctk.CTkLabel(self.status_bar, text="v1.0.0")
        self.version_label.pack(side="right", padx=10, pady=5)

    def switch_to_process_tab(self):
        """切换到打包过程标签页"""
        self.tab_view.set("打包过程")
        self.status_label.configure(text="打包过程")

    def run(self):
        """运行主窗口"""
        self.root.mainloop()


# if __name__ == "__main__":
#     app = MainWindow()
#     app.run()
