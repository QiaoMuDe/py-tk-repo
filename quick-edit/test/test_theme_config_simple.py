import tkinter as tk
from QuickEdit import ThemeManager
import os
import json

def test_theme_config():
    # 创建一个简单的测试窗口
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    # 创建一个简单的编辑器模拟类
    class SimpleEditor:
        def __init__(self):
            self.current_theme = "light"
            self.toolbar_buttons = []
            
        def dummy_method(self):
            pass
            
        # 添加一些必要的属性和方法来模拟AdvancedTextEditor
        text_area = tk.Text(root)
        line_numbers = tk.Canvas(root)
        
        def update_line_numbers(self):
            pass
            
        def _apply_simple_syntax_highlighting(self):
            pass
    
    # 创建简单编辑器实例
    editor = SimpleEditor()
    
    # 创建主题管理器实例
    theme_manager = ThemeManager(editor)
    
    # 打印初始配置
    print("初始主题:", theme_manager.current_theme)
    
    # 测试切换到深色主题
    print("切换到深色主题...")
    theme_manager.set_theme("dark")
    print("切换后主题:", theme_manager.current_theme)
    
    # 清理
    root.destroy()
    
    print("测试完成")

if __name__ == "__main__":
    test_theme_config()