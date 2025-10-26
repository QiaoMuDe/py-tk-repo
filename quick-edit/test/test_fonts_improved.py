import tkinter as tk
from tkinter import font

def get_system_fonts():
    """获取系统已安装的字体列表"""
    try:
        # 获取系统字体家族列表
        font_families = list(font.families())
        # 按字母顺序排序
        font_families.sort()
        return font_families
    except Exception as e:
        print(f"获取字体列表时出错: {e}")
        return []

def main():
    # 创建一个隐藏的根窗口
    root = tk.Tk()
    root.withdraw()  # 隐藏窗口
    
    # 获取字体列表
    fonts = get_system_fonts()
    
    # 将结果写入文件
    with open("system_fonts.txt", "w", encoding="utf-8") as f:
        f.write(f"系统中找到 {len(fonts)} 种字体:\n")
        f.write("=" * 50 + "\n")
        
        # 写入所有字体
        for i, font_name in enumerate(fonts):
            f.write(f"{i+1:4d}. {font_name}\n")
    
    print(f"系统字体列表已保存到 system_fonts.txt 文件中，共 {len(fonts)} 种字体")
    
    # 销毁根窗口
    root.destroy()

if __name__ == "__main__":
    main()