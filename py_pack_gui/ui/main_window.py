"""
主窗口模块
提供应用程序的主窗口界面
"""

import tkinter as tk
import customtkinter as ctk
from ui.pyinstaller_tab import PyInstallerTab
from ui.nuitka_tab import NuitkaTab
from ui.process_tab import ProcessTab
from utils.window_utils import center_window
from ctypes import windll


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
        #self.root.geometry("1200x800")
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
        self.pyinstaller_ui = PyInstallerTab(self.pyinstaller_tab, self, self.font_family)
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