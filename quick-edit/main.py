#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文本编辑器主程序
"""

import tkinter as tk
import tkinterdnd2
from editor import AdvancedTextEditor


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