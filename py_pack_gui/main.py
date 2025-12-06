"""
Python GUI 打包编译工具
主程序入口文件
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from ui.main_window import MainWindow


def main():
    """主函数"""
    # 创建并运行主窗口
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()
