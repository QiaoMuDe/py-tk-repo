import os

# 图标文件路径
ICON_FILE_PATH = "./icos/QuickEdit.ico"


def format_file_size(size_bytes):
    """将字节大小转换为人性化的显示格式"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def center_window(window, width=None, height=None):
    """将窗口居中显示"""
    
    # 如果没有提供宽高参数，则获取窗口的实际宽高
    if width is None:
        width = window.winfo_width()
    if height is None:
        height = window.winfo_height()
    
    # 确保宽度和高度有效，防止异常
    if width <= 1:
        width = 500  # 默认宽度
    if height <= 1:
        height = 400  # 默认高度

    # 获取屏幕的宽度和高度
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # 计算居中位置
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    # 设置窗口位置和尺寸
    window.geometry(f"{width}x{height}+{x}+{y}")

def set_window_icon(window):
    """设置窗口图标
    
    Args:
        window: tkinter窗口对象
    """
    if os.path.exists(ICON_FILE_PATH):
        try:
            window.iconbitmap(ICON_FILE_PATH)
        except Exception:
            # 如果设置图标失败，静默忽略
            pass
