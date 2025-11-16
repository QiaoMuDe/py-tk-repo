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

    print(f"系统中找到 {len(fonts)} 种字体:")
    print("=" * 50)

    # 显示前20个字体作为示例
    for i, font_name in enumerate(fonts[:20]):
        print(f"{i+1:2d}. {font_name}")

    if len(fonts) > 20:
        print(f"... 还有 {len(fonts) - 20} 种字体")

    # 销毁根窗口
    root.destroy()


if __name__ == "__main__":
    main()
