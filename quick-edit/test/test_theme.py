import tkinter as tk
from QuickEdit import ThemeManager, AdvancedTextEditor
import os
import json


def test_theme_saving():
    # 创建一个简单的测试窗口
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    # 创建编辑器实例
    editor = AdvancedTextEditor(root)

    # 测试切换到深色主题
    print("切换到深色主题...")
    editor.change_theme("dark")

    # 检查配置文件是否创建并包含正确的主题设置
    config_file = os.path.join(os.path.expanduser("~"), ".quick_edit_config.json")
    if os.path.exists(config_file):
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
            print(f"配置文件内容: {config}")
            if config.get("current_theme") == "dark":
                print("✓ 主题正确保存到配置文件")
            else:
                print("✗ 主题未正确保存到配置文件")
    else:
        print("✗ 配置文件未创建")

    # 清理
    root.destroy()


if __name__ == "__main__":
    test_theme_saving()
