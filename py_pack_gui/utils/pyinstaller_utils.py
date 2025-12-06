"""
PyInstaller工具函数模块
提供PyInstaller相关的工具函数
"""

import os
from tkinter import filedialog, messagebox


def browse_script_file(parent=None):
    """浏览脚本文件

    Args:
        parent: 父窗口

    Returns:
        str: 选择的文件路径，如果取消则返回空字符串
    """
    file_path = filedialog.askopenfilename(
        parent=parent,
        title="选择Python脚本",
        filetypes=[("Python文件", "*.py"), ("所有文件", "*.*")],
    )
    return file_path


def browse_directory(parent=None, title="选择目录"):
    """浏览目录

    Args:
        parent: 父窗口
        title: 对话框标题

    Returns:
        str: 选择的目录路径，如果取消则返回空字符串
    """
    dir_path = filedialog.askdirectory(parent=parent, title=title)
    return dir_path


def browse_icon_file(parent=None):
    """浏览图标文件

    Args:
        parent: 父窗口

    Returns:
        str: 选择的文件路径，如果取消则返回空字符串
    """
    file_path = filedialog.askopenfilename(
        parent=parent,
        title="选择图标文件",
        filetypes=[
            ("图标文件", "*.ico"),
            ("可执行文件", "*.exe"),
            ("图像文件", "*.png *.jpg *.jpeg *.gif *.bmp"),
            ("所有文件", "*.*"),
        ],
    )
    return file_path


def browse_data_file(parent=None):
    """浏览数据文件

    Args:
        parent: 父窗口

    Returns:
        str: 选择的文件路径，如果取消则返回空字符串
    """
    file_path = filedialog.askopenfilename(
        parent=parent, title="选择数据文件", filetypes=[("所有文件", "*.*")]
    )
    return file_path


def browse_binary_file(parent=None):
    """浏览二进制文件

    Args:
        parent: 父窗口

    Returns:
        str: 选择的文件路径，如果取消则返回空字符串
    """
    file_path = filedialog.askopenfilename(
        parent=parent,
        title="选择二进制文件",
        filetypes=[
            ("动态链接库", "*.dll *.so *.dylib"),
            ("可执行文件", "*.exe"),
            ("所有文件", "*.*"),
        ],
    )
    return file_path


def get_script_name(script_path):
    """从脚本路径获取脚本名称

    Args:
        script_path: 脚本路径

    Returns:
        str: 脚本名称（不含扩展名）
    """
    if not script_path:
        return ""
    return os.path.splitext(os.path.basename(script_path))[0]


def validate_data_file_format(file_path, dest_path):
    """验证数据文件格式

    Args:
        file_path: 源文件路径
        dest_path: 目标路径

    Returns:
        tuple: (is_valid, error_message)
    """
    if not file_path:
        return False, "源文件路径不能为空"

    if not dest_path:
        return False, "目标路径不能为空"

    if not os.path.exists(file_path):
        return False, f"源文件不存在: {file_path}"

    return True, ""


def format_data_file_entry(file_path, dest_path):
    """格式化数据文件条目

    Args:
        file_path: 源文件路径
        dest_path: 目标路径

    Returns:
        str: 格式化后的条目
    """
    return f"{file_path}:{dest_path}"


def parse_data_file_entry(entry):
    """解析数据文件条目

    Args:
        entry: 数据文件条目

    Returns:
        tuple: (file_path, dest_path)
    """
    if ":" not in entry:
        return entry, ""

    parts = entry.split(":", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    else:
        return parts[0], ""


def show_error(parent, title, message):
    """显示错误对话框

    Args:
        parent: 父窗口
        title: 对话框标题
        message: 错误消息
    """
    messagebox.showerror(title, message, parent=parent)


def show_info(parent, title, message):
    """显示信息对话框

    Args:
        parent: 父窗口
        title: 对话框标题
        message: 信息消息
    """
    messagebox.showinfo(title, message, parent=parent)


def show_warning(parent, title, message):
    """显示警告对话框

    Args:
        parent: 父窗口
        title: 对话框标题
        message: 警告消息
    """
    messagebox.showwarning(title, message, parent=parent)


def ask_yes_no(parent, title, message):
    """显示是/否对话框

    Args:
        parent: 父窗口
        title: 对话框标题
        message: 询问消息

    Returns:
        bool: True表示是，False表示否
    """
    return messagebox.askyesno(title, message, parent=parent)
