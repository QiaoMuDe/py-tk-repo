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


def is_binary_file(file_path=None, sample_data=None, sample_size=1024):
    """检测文件是否为二进制文件

    原理：通过检查文件中是否包含非文本字符（控制字符）来判断

    Args:
        file_path: 文件路径（如果提供了sample_data，则忽略此参数）
        sample_data: 已读取的文件样本数据（字节类型）
        sample_size: 用于检测的样本大小（字节）

    Returns:
        bool: 如果是二进制文件返回True，否则返回False
    """
    try:
        # 如果提供了样本数据，直接使用
        if sample_data is not None:
            sample = sample_data
        else:
            # 否则从文件中读取样本
            with open(file_path, "rb") as file:
                sample = file.read(sample_size)

        # 如果文件为空，不视为二进制文件
        if not sample:
            return False

        # 统计控制字符的数量（除了换行符、回车符和制表符）
        control_chars = 0
        for byte in sample:
            # 检查是否为控制字符（ASCII值小于32的字符）
            # 排除换行符(10)、回车符(13)和制表符(9)
            if byte < 32 and byte not in (9, 10, 13):
                control_chars += 1

        # 如果控制字符占比超过5%，认为是二进制文件
        # 这个阈值可以根据需要调整
        return control_chars / len(sample) > 0.05
    except Exception:
        # 如果读取文件出错，保守地认为可能是二进制文件
        return True
