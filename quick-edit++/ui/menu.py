#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
菜单栏界面模块
"""

import tkinter as tk
import customtkinter as ctk
from ui.font_dialog import show_font_dialog
from ui.about_dialog import show_about_dialog
from ui.document_stats_dialog import show_document_stats_dialog
from config.config_manager import config_manager
import codecs
import os
from tkinter import messagebox


def get_supported_encodings():
    """获取支持的编码列表

    Returns:
        list: 支持的编码列表，常用编码在前
    """
    # 常用编码选项
    common_encodings = [
        "UTF-8",
        "UTF-16",
        "UTF-32",
        "ASCII",
        "GB2312",
        "GBK",
        "GB18030",
        "BIG5",
        "ISO-8859-1",
        "ISO-8859-2",
        "ISO-8859-15",
        "Windows-1252",
        "Windows-1251",
        "Windows-1256",
        "Shift_JIS",
        "EUC-JP",
        "KOI8-R",
        "KOI8-U",
    ]

    try:
        # 从encodings模块获取所有支持的编码
        import encodings

        all_encodings = [
            f[:-3]  # 移除.py扩展名
            for f in os.listdir(os.path.dirname(encodings.__file__))
            if f.endswith(".py") and not f.startswith("_")
        ]

        # 合并常用编码和所有支持的编码，保持常用编码在前
        supported_encodings = common_encodings[:]
        for enc in all_encodings:
            if enc.upper() not in [e.upper() for e in supported_encodings]:
                supported_encodings.append(enc)

        return supported_encodings
    except:
        # 如果获取所有编码失败，返回常用编码列表
        return common_encodings


def create_encoding_submenu(parent_menu, root, show_common_only=False, font_tuple=None):
    """创建编码选择子菜单

    Args:
        parent_menu: 父菜单对象
        root: 根窗口对象
        show_common_only (bool): 是否只显示常用编码，默认False显示完整编码列表
        font_tuple: 字体元组，包含字体名称、大小和样式
    """
    if font_tuple is None:
        # 如果没有提供字体元组，从配置管理器获取菜单字体设置
        menu_font = config_manager.get_font_config("menu_bar")
        menu_font_family = menu_font.get("font", "Microsoft YaHei UI")
        menu_font_size = menu_font.get("font_size", 12)
        menu_font_bold = menu_font.get("font_bold", True)
        font_tuple = (
            menu_font_family,
            menu_font_size,
            "bold" if menu_font_bold else "normal",
        )

    if show_common_only:
        # 只显示常用编码
        common_encodings = ["UTF-8", "UTF-16", "GBK", "GB2312", "ASCII", "ISO-8859-1"]

        for enc in common_encodings:
            parent_menu.add_command(
                label=enc,
                command=lambda e=enc: set_file_encoding(e, root),
                font=font_tuple,
            )

        # 添加"更多"选项，点击后显示完整编码列表
        parent_menu.add_separator()

        # 创建更多编码的子菜单
        more_encodings_menu = tk.Menu(parent_menu, tearoff=0, font=font_tuple)
        parent_menu.add_cascade(
            label="更多编码...", menu=more_encodings_menu, font=font_tuple
        )

        # 填充更多编码菜单
        encodings = get_supported_encodings()
        # 按字母顺序排序
        encodings_sorted = sorted(encodings, key=lambda x: x.upper())

        # 为了避免菜单过长，将编码分成几组
        group_size = 20  # 每组20个编码
        for i in range(0, len(encodings_sorted), group_size):
            group_name = f"{encodings_sorted[i]} - {encodings_sorted[min(i+group_size-1, len(encodings_sorted)-1)]}"
            group_menu = tk.Menu(more_encodings_menu, tearoff=0, font=font_tuple)
            more_encodings_menu.add_cascade(
                label=group_name, menu=group_menu, font=font_tuple
            )

            for j in range(i, min(i + group_size, len(encodings_sorted))):
                enc = encodings_sorted[j]
                group_menu.add_command(
                    label=enc,
                    command=lambda e=enc: set_file_encoding(e, root),
                    font=font_tuple,
                )
    else:
        # 显示完整编码列表
        encodings = get_supported_encodings()
        # 按字母顺序排序
        encodings_sorted = sorted(encodings, key=lambda x: x.upper())

        for enc in encodings_sorted:
            parent_menu.add_command(
                label=enc,
                command=lambda e=enc: set_file_encoding(e, root),
                font=font_tuple,
            )


def create_menu(root):
    """创建菜单栏"""
    # 从配置管理器获取菜单字体设置
    menu_font = config_manager.get_font_config("menu_bar")
    menu_font_family = menu_font.get("font", "Microsoft YaHei UI")
    menu_font_size = menu_font.get("font_size", 12)
    menu_font_bold = menu_font.get("font_bold", False)

    # 创建字体元组，用于所有菜单项
    menu_font_tuple = (
        menu_font_family,
        menu_font_size,
        "bold" if menu_font_bold else "normal",
    )

    # 创建主菜单
    main_menu = tk.Menu(root, font=menu_font_tuple)

    # 创建文件菜单
    file_menu = tk.Menu(main_menu, tearoff=0, font=menu_font_tuple)

    # 第一组：基本文件操作
    file_menu.add_command(
        label="新建", command=lambda: root.new_file(), accelerator="Ctrl+N"
    )
    file_menu.add_command(
        label="打开", command=lambda: root.open_file(), accelerator="Ctrl+O"
    )
    file_menu.add_command(
        label="保存", command=lambda: root.save_file(), accelerator="Ctrl+S"
    )
    file_menu.add_command(
        label="另存为", command=lambda: root.save_file_as(), accelerator="Ctrl+Shift+S"
    )
    file_menu.add_command(
        label="关闭文件", command=lambda: root.close_file(), accelerator="Ctrl+W"
    )

    # 分隔符
    file_menu.add_separator()

    # 第二组：文件编码
    # 创建文件编码子菜单
    encoding_submenu = tk.Menu(file_menu, tearoff=0, font=menu_font_tuple)

    # 获取当前编码设置
    current_encoding = config_manager.get("file.default_encoding", "UTF-8")

    # 创建常用编码子菜单
    create_encoding_submenu(
        encoding_submenu, root, show_common_only=True, font_tuple=menu_font_tuple
    )

    file_menu.add_cascade(label="文件编码", menu=encoding_submenu)

    # 创建换行符子菜单
    newline_submenu = tk.Menu(file_menu, tearoff=0, font=menu_font_tuple)

    # 获取当前换行符设置
    current_newline = config_manager.get("file.default_line_ending", "CRLF")
    newline_options = [
        ("Windows (CRLF)", "CRLF"),
        ("Linux/Unix (LF)", "LF"),
        ("Mac (CR)", "CR"),
    ]

    for label, value in newline_options:
        newline_submenu.add_command(
            label=label, command=lambda nl=value: set_file_line_ending(nl, root)
        )

    file_menu.add_cascade(label="换行符", menu=newline_submenu)

    # 分隔符
    file_menu.add_separator()

    # 第三组：文件选项
    file_menu.add_command(
        label="打开文件所在目录",
        command=lambda: root.open_containing_folder(),
        accelerator="Ctrl+E",
    )
    file_menu.add_checkbutton(
        label="只读模式", command=lambda: root.toggle_read_only(), accelerator="Ctrl+R"
    )

    # 分隔符
    file_menu.add_separator()

    # 第四组：退出程序
    file_menu.add_command(label="退出", command=root._on_closing, accelerator="Ctrl+Q")

    # 将文件菜单添加到主菜单
    main_menu.add_cascade(label="文件", menu=file_menu)

    # 创建编辑菜单
    edit_menu = tk.Menu(main_menu, tearoff=0, font=menu_font_tuple)
    edit_menu.add_command(label="撤销", command=lambda: print("撤销"))
    edit_menu.add_command(label="重做", command=lambda: print("重做"))
    edit_menu.add_separator()
    edit_menu.add_command(label="剪切", command=lambda: print("剪切"))
    edit_menu.add_command(label="复制", command=lambda: print("复制"))
    edit_menu.add_command(label="粘贴", command=lambda: print("粘贴"))
    edit_menu.add_separator()
    edit_menu.add_command(label="查找", command=lambda: print("查找"))
    edit_menu.add_command(label="替换", command=lambda: print("替换"))
    edit_menu.add_separator()

    # 全选、清除
    edit_menu.add_command(label="全选", command=lambda: print("全选"))
    edit_menu.add_command(label="清除", command=lambda: print("清除"))
    edit_menu.add_separator()

    # 新增导航功能
    edit_menu.add_command(label="转到文件顶部", command=lambda: print("转到文件顶部"))
    edit_menu.add_command(label="转到文件底部", command=lambda: print("转到文件底部"))
    edit_menu.add_command(label="向上翻页", command=lambda: print("向上翻页"))
    edit_menu.add_command(label="向下翻页", command=lambda: print("向下翻页"))
    edit_menu.add_command(label="转到行", command=lambda: print("转到行"))
    edit_menu.add_separator()

    # 新增剪贴板和文本操作功能组
    edit_menu.add_command(label="清空剪贴板", command=lambda: print("清空剪贴板"))

    # 创建复制到剪贴板子菜单
    copy_to_clipboard_submenu = tk.Menu(edit_menu, tearoff=0, font=menu_font_tuple)
    edit_menu.add_cascade(label="复制到剪贴板", menu=copy_to_clipboard_submenu)

    # 创建选中文本操作子菜单
    selected_text_submenu = tk.Menu(edit_menu, tearoff=0, font=menu_font_tuple)
    edit_menu.add_cascade(label="选中文本操作", menu=selected_text_submenu)

    # 创建插入子菜单
    insert_submenu = tk.Menu(edit_menu, tearoff=0, font=menu_font_tuple)
    edit_menu.add_cascade(label="插入", menu=insert_submenu)

    # 将编辑菜单添加到主菜单
    main_menu.add_cascade(label="编辑", menu=edit_menu)

    # 创建主题菜单
    theme_menu = tk.Menu(main_menu, tearoff=0, font=menu_font_tuple)

    # 字体
    theme_menu.add_command(
        label="字体", command=lambda: show_font_dialog(root.text_area)
    )
    theme_menu.add_separator()

    # 外观模式分组（3种模式）- 使用单选按钮
    # 获取当前外观模式
    current_theme = config_manager.get("app.theme_mode", "system")
    theme_options = [
        ("浅色模式", "light"),
        ("深色模式", "dark"),
        ("跟随系统", "system"),
    ]

    # 创建外观模式变量
    theme_var = tk.StringVar(value=current_theme)

    for label, value in theme_options:
        theme_menu.add_radiobutton(
            label=label,
            variable=theme_var,
            value=value,
            command=lambda: set_theme_mode(theme_var.get(), root),
        )

    theme_menu.add_separator()

    # 主题颜色分组（3种主题）- 使用单选按钮
    # 获取当前颜色主题
    current_color = config_manager.get("app.color_theme", "blue")
    color_options = [
        ("蓝色主题", "blue"),
        ("绿色主题", "green"),
        ("深蓝色主题", "dark-blue"),
    ]

    # 创建颜色主题变量
    color_var = tk.StringVar(value=current_color)

    for label, value in color_options:
        theme_menu.add_radiobutton(
            label=label,
            variable=color_var,
            value=value,
            command=lambda: set_color_theme(color_var.get(), root),
        )

    # 将主题菜单添加到主菜单
    main_menu.add_cascade(label="主题", menu=theme_menu)

    # 创建设置菜单
    settings_menu = tk.Menu(main_menu, tearoff=0, font=menu_font_tuple)

    # 第一组：界面设置
    # 获取工具栏显示状态
    show_toolbar = config_manager.get("app.show_toolbar", True)
    # 初始化或更新APP类中的变量
    if root.toolbar_var is None:
        root.toolbar_var = tk.BooleanVar(value=show_toolbar)
    else:
        root.toolbar_var.set(show_toolbar)

    settings_menu.add_checkbutton(
        label="显示工具栏",
        command=lambda: toggle_toolbar_visibility(root),
        variable=root.toolbar_var,
    )

    # 创建窗口标题显示子菜单
    title_display_submenu = tk.Menu(settings_menu, tearoff=0, font=menu_font_tuple)

    # 添加标题显示选项
    title_display_submenu.add_radiobutton(
        label="仅显示文件名",
        variable=root.title_mode_var,
        value="filename",
        command=lambda: set_window_title_mode(root.title_mode_var.get(), root),
    )
    title_display_submenu.add_radiobutton(
        label="显示完整文件路径",
        variable=root.title_mode_var,
        value="filepath",
        command=lambda: set_window_title_mode(root.title_mode_var.get(), root),
    )
    title_display_submenu.add_radiobutton(
        label="显示文件名和目录路径",
        variable=root.title_mode_var,
        value="filename_and_dir",
        command=lambda: set_window_title_mode(root.title_mode_var.get(), root),
    )

    settings_menu.add_cascade(label="窗口标题显示", menu=title_display_submenu)
    settings_menu.add_separator()

    # 第二组：编辑设置
    # 获取自动换行设置
    auto_wrap = config_manager.get("text_editor.auto_wrap", True)
    if root.auto_wrap_var is None:
        root.auto_wrap_var = tk.BooleanVar(value=auto_wrap)
    else:
        root.auto_wrap_var.set(auto_wrap)
    settings_menu.add_checkbutton(
        label="启用自动换行",
        command=lambda: toggle_auto_wrap(root),
        variable=root.auto_wrap_var,
    )

    # 获取快捷插入设置
    quick_insert = config_manager.get("text_editor.quick_insert_enabled", True)
    if root.quick_insert_var is None:
        root.quick_insert_var = tk.BooleanVar(value=quick_insert)
    else:
        root.quick_insert_var.set(quick_insert)
    settings_menu.add_checkbutton(
        label="启用快捷插入(@)",
        command=lambda: toggle_quick_insert(root),
        variable=root.quick_insert_var,
    )
    settings_menu.add_separator()

    # 第三组：保存设置
    # 获取自动保存设置
    settings_menu.add_checkbutton(
        label="启用自动保存",
        command=lambda: toggle_auto_save(root),
        variable=root.auto_save_var,
    )

    # 创建自动保存间隔子菜单
    autosave_submenu = tk.Menu(settings_menu, tearoff=0, font=menu_font_tuple)

    # 获取当前自动保存间隔
    auto_save_interval = config_manager.get("app.auto_save_interval", 5)

    # 定义可用的间隔选项
    interval_options = [
        ("3秒", 3),
        ("5秒", 5),
        ("10秒", 10),
        ("15秒", 15),
        ("30秒", 30),
        ("45秒", 45),
        ("1分钟", 60),
        ("3分钟", 180),
        ("5分钟", 300),
    ]

    # 检查配置文件中的值是否在选项列表中
    interval_values = [value for _, value in interval_options]
    if auto_save_interval not in interval_values:
        # 如果不在列表中，使用默认值5秒
        auto_save_interval = 5

    # 设置当前选中的间隔
    root.auto_save_interval_var.set(str(auto_save_interval))

    # 创建菜单项
    for label, value in interval_options:
        autosave_submenu.add_radiobutton(
            label=label,
            variable=root.auto_save_interval_var,
            value=str(value),
            command=lambda interval=value: set_auto_save_interval(interval, root),
        )

    settings_menu.add_cascade(label="自动保存间隔", menu=autosave_submenu)

    # 获取备份设置
    settings_menu.add_checkbutton(
        label="启用副本备份",
        command=lambda: toggle_backup(root),
        variable=root.backup_var,
    )
    settings_menu.add_separator()

    # 第四组：配置管理
    settings_menu.add_command(
        label="查看配置",
        command=lambda: root.file_ops.open_config_file(),
        accelerator="Ctrl+Shift+C",
    )
    settings_menu.add_command(
        label="重置设置",
        command=lambda: root._reset_settings(),
        accelerator="Ctrl+Shift+R",
    )

    # 将设置菜单添加到主菜单
    main_menu.add_cascade(label="设置", menu=settings_menu)

    # 创建帮助菜单
    help_menu = tk.Menu(main_menu, tearoff=0, font=menu_font_tuple)
    help_menu.add_command(
        label="文档统计信息",
        command=lambda: show_document_stats_dialog(root),
        accelerator="F2",
    )
    help_menu.add_command(
        label="关于", command=lambda: show_about_dialog(root), accelerator="F1"
    )

    # 将帮助菜单添加到主菜单
    main_menu.add_cascade(label="帮助", menu=help_menu)

    # 将主菜单配置到根窗口
    root.config(menu=main_menu)

    return main_menu


def set_file_encoding(encoding, app_instance=None):
    """设置文件编码

    Args:
        encoding (str): 编码名称
    app_instance: APP类的实例，用于直接更新当前状态
    """
    # 如果没有提供APP实例，直接返回
    if not app_instance:
        return

    # 更新APP实例的当前编码
    app_instance.current_encoding = encoding

    # 更新状态栏显示
    app_instance.status_bar.update_file_info()

    # 如果有文件路径或总字符数大于0，则标记文件为已修改
    if app_instance.current_file_path or app_instance.get_char_count() > 0:
        # 标记文件为已修改
        app_instance.set_modified(True)
        # 更新状态栏
        app_instance._update_status_bar()

    # 显示通知
    messagebox.showinfo("通知", f"文件编码已更改为: {encoding}")


def set_file_line_ending(line_ending, app_instance=None):
    """设置文件换行符

    Args:
        line_ending (str): 换行符类型 ('CRLF', 'LF', 'CR')
        app_instance: APP类的实例，用于直接更新当前状态
    """
    # 如果没有提供APP实例，直接返回
    if not app_instance:
        return

    # 更新APP实例的当前换行符
    app_instance.current_line_ending = line_ending
    # 更新状态栏显示
    app_instance.status_bar.update_file_info()
    #  获取换行符名称字典
    line_ending_names = {
        "CRLF": "Windows (CRLF)",
        "LF": "Linux/Unix (LF)",
        "CR": "Mac (CR)",
    }

    # 显示通知
    messagebox.showinfo(
        "通知", f"换行符已更改为: {line_ending_names.get(line_ending, line_ending)}"
    )

    # 如果有文件路径或总字符数大于0，则标记文件为已修改
    if app_instance.current_file_path or app_instance.get_char_count() > 0:
        # 标记文件为已修改
        app_instance.set_modified(True)
        # 更新状态栏
        app_instance._update_status_bar()


def toggle_toolbar_visibility(root):
    """切换工具栏的显示/隐藏状态

    Args:
        root: 主窗口实例，用于访问工具栏组件
    """
    # 获取当前工具栏显示状态
    current_state = config_manager.get("app.show_toolbar", True)

    # 切换状态
    new_state = not current_state

    # 先更新配置管理器中的值
    config_manager.set("app.show_toolbar", new_state)
    # 然后调用保存方法
    config_manager.save_config()

    # 更新APP类中的变量
    if root.toolbar_var is not None:
        root.toolbar_var.set(new_state)

    # 暂时捕获所有事件，防止用户交互
    root.grab_set()

    # 使用after方法延迟执行，减少闪烁
    def toggle_toolbar():
        try:
            # 切换工具栏显示状态
            if hasattr(root, "toolbar"):
                if new_state:
                    # 显示工具栏
                    root.toolbar.grid(row=0, column=0, sticky="ew")
                else:
                    # 隐藏工具栏，但保留布局空间
                    root.toolbar.grid_remove()
        finally:
            # 释放事件捕获
            root.grab_release()

    # 延迟10毫秒执行，让界面有时间完成当前操作
    root.after(10, toggle_toolbar)


def set_theme_mode(mode, root=None):
    """
    设置主题模式

    Args:
        mode (str): 主题模式，可选值: "light", "dark", "system"
        root (ctk.CTk, optional): 主窗口实例。
    """
    # 保存配置
    config_manager.set("app.theme_mode", mode)
    config_manager.save_config()

    # 应用主题模式
    ctk.set_appearance_mode(mode)

    # 显示通知
    mode_text = {"light": "浅色模式", "dark": "深色模式", "system": "跟随系统"}
    mode_name = mode_text.get(mode, mode)

    # 显示通知
    messagebox.showinfo("通知", f"主题模式已切换为: {mode_name}")


def set_color_theme(theme, root=None):
    """
    设置颜色主题

    Args:
        theme (str): 颜色主题，可选值: "blue", "green", "dark-blue"
        root (ctk.CTk, optional): 主窗口实例。
    """
    # 保存配置
    config_manager.set("app.color_theme", theme)
    config_manager.save_config()

    # 应用颜色主题
    ctk.set_default_color_theme(theme)

    # 显示通知
    theme_text = {"blue": "蓝色主题", "green": "绿色主题", "dark-blue": "深蓝色主题"}
    theme_name = theme_text.get(theme, theme)

    # 显示通知
    messagebox.showinfo("通知", f"颜色主题已切换为: {theme_name}, 请重启应用以生效")


def toggle_auto_wrap(root):
    """切换自动换行模式"""
    # 获取当前自动换行状态
    current_state = config_manager.get("text_editor.auto_wrap", True)
    # 切换状态
    new_state = not current_state
    # 保存配置
    config_manager.set("text_editor.auto_wrap", new_state)
    config_manager.save_config()

    # 更新APP类中的变量
    if root.auto_wrap_var is not None:
        root.auto_wrap_var.set(new_state)

    # 直接设置文本框的自动换行属性
    if hasattr(root, "text_area"):
        # 设置文本框的自动换行属性
        wrap_mode = "word" if new_state else "none"
        root.text_area.configure(wrap=wrap_mode)

        # 显示通知
        status_text = "已启用" if new_state else "已禁用"
        messagebox.showinfo("通知", f"自动换行{status_text}")


def toggle_quick_insert(root):
    """切换快速插入模式"""
    # 获取当前快速插入状态
    current_state = config_manager.get("text_editor.quick_insert_enabled", True)
    # 切换状态
    new_state = not current_state
    # 保存配置
    config_manager.set("text_editor.quick_insert_enabled", new_state)
    config_manager.save_config()

    # 更新APP类中的变量
    if root.quick_insert_var is not None:
        root.quick_insert_var.set(new_state)

    # 获取当前活动的文本编辑器实例
    # if root.text_area:
    #    root.text_area.toggle_quick_insert(new_state)

    # 显示通知
    status_text = "已启用" if new_state else "已禁用"
    messagebox.showinfo("通知", f"快速插入{status_text}")


def toggle_auto_save(root):
    """切换自动保存模式"""
    # 使用AutoSaveManager的方法
    root.auto_save_manager.toggle_auto_save()


def set_auto_save_interval(interval, root=None):
    """设置自动保存间隔

    Args:
        interval (int): 保存间隔，单位为秒
        root: 主窗口实例，用于更新APP类中的变量
    """
    # 使用AutoSaveManager的方法
    root.auto_save_manager.set_auto_save_interval(interval)


def toggle_backup(root):
    """切换备份模式"""
    # 获取当前备份状态
    current_state = config_manager.get("app.backup_enabled", False)
    # 切换状态
    new_state = not current_state

    # 保存配置
    config_manager.set("app.backup_enabled", new_state)
    config_manager.save_config()

    # 更新APP类中的变量
    if root.backup_var is not None:
        root.backup_var.set(new_state)

    # 开启的时候立即备份一次
    if new_state and root.current_file_path and not root.is_modified():
        root.file_operations._create_backup_copy(root.current_file_path)

    # 显示通知
    messagebox.showinfo(
        "通知", f"备份模式已切换为: {'已启用' if new_state else '已禁用'}"
    )


def set_window_title_mode(mode, root):
    """
    设置窗口标题显示模式

    Args:
        mode (str): 标题显示模式，可选值: "filename", "filepath", "filename_and_dir"
        root: 主窗口实例，用于更新窗口标题
    """
    # 保存配置
    config_manager.set("app.window_title_mode", mode)
    config_manager.save_config()

    # 直接调用主窗口的更新窗口标题方法
    if hasattr(root, "_update_window_title"):
        root._update_window_title()

    # 显示模式名称
    mode_names = {
        "filename": "仅显示文件名",
        "filepath": "显示完整文件路径",
        "filename_and_dir": "显示文件名和目录路径",
    }
    mode_name = mode_names.get(mode, mode)
