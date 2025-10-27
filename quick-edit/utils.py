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


def center_window(window, default_width=None, default_height=None):
    """将窗口居中显示"""
    # 确保窗口已经绘制完成
    window.update_idletasks()

    # 获取窗口的实际宽度和高度
    width = window.winfo_width()
    height = window.winfo_height()

    # 如果获取的宽高为1且提供了默认尺寸，则使用默认尺寸
    if (width <= 1 or height <= 1) and default_width and default_height:
        width = default_width
        height = default_height

    # 获取屏幕的宽度和高度
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # 计算居中位置
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    # 设置窗口位置和尺寸
    window.geometry(f"{width}x{height}+{x}+{y}")
