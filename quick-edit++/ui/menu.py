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
from ui.find_replace_dialog import show_find_replace_dialog
from ui.recent_files_menu import RecentFilesMenu
from ui.reopen_file_menu import ReopenFileMenu
from ui.color_picker import show_color_picker
from ui.file_properties_dialog import show_file_properties_dialog
from config.config_manager import config_manager
from ui.utils import get_supported_encodings
from tkinter import messagebox
from ui.insert_submenu import create_insert_submenu
from ui.selected_text_submenu import create_selected_text_submenu


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
    root.file_menu = file_menu  # 保存文件菜单对象

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

    # 创建最近打开文件子菜单
    # 创建打开文件的回调函数
    def on_open_recent_file(file_path):
        # 使用现有的文件打开功能
        root.file_ops._open_file(
            file_path=file_path, check_save=True, check_backup=True
        )

    # 初始化最近文件菜单
    recent_menu = RecentFilesMenu(root, file_menu, on_open_recent_file)
    recent_menu.create_recent_files_menu()
    # 保存到root对象中，方便文件打开后刷新
    root.recent_files_menu = recent_menu

    # 创建重新载入文件子菜单
    # 创建重新载入文件的回调函数
    def on_reopen_file(file_path, encoding):
        # 使用现有的文件重新打开功能
        root.file_ops._open_file(
            file_path=file_path, encoding=encoding, check_save=True
        )

    # 初始化重新载入文件菜单
    reopen_menu = ReopenFileMenu(root, file_menu, on_reopen_file)
    reopen_menu.create_reopen_file_menu()
    # 保存到root对象中，方便文件状态更新
    root.reopen_file_menu = reopen_menu

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

    # 文件属性选项
    file_menu.add_command(
        label="文件属性",
        command=lambda: show_file_properties_dialog(root, root.current_file_path),
        accelerator="Ctrl+I",
    )
    # 获取文件属性菜单项索引，用于后续更新状态
    root.file_properties_menu_index = file_menu.index(tk.END)

    # 创建文档统计信息
    file_menu.add_command(
        label="文档统计信息",
        command=lambda: show_document_stats_dialog(root),
        accelerator="F2",
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
    edit_menu.add_command(
        label="撤销", command=lambda: root.undo(), accelerator="Ctrl+Z"
    )
    edit_menu.add_command(
        label="重做", command=lambda: root.redo(), accelerator="Ctrl+Y"
    )
    edit_menu.add_separator()
    edit_menu.add_command(
        label="剪切", command=lambda: root.cut(), accelerator="Ctrl+X"
    )
    edit_menu.add_command(
        label="复制", command=lambda: root.copy(), accelerator="Ctrl+C"
    )
    edit_menu.add_command(
        label="粘贴", command=lambda: root.paste(), accelerator="Ctrl+V"
    )
    edit_menu.add_separator()
    edit_menu.add_command(
        label="查找替换",
        command=lambda: show_find_replace_dialog(root, root.text_area),
        accelerator="Ctrl+F",
    )
    edit_menu.add_separator()

    # 全选、清除
    edit_menu.add_command(
        label="全选", command=lambda: root.select_all(), accelerator="Ctrl+A"
    )
    edit_menu.add_command(
        label="清除", command=lambda: root.clear_all(), accelerator="Ctrl+Shift+D"
    )
    edit_menu.add_separator()

    # 新增剪贴板和文本操作功能组
    edit_menu.add_command(label="清空剪贴板", command=lambda: root.clear_clipboard())

    # 创建复制到剪贴板子菜单
    copy_to_clipboard_submenu = tk.Menu(edit_menu, tearoff=0, font=menu_font_tuple)
    copy_to_clipboard_submenu.add_command(
        label="文件名", command=lambda: root.copy_filename_to_clipboard()
    )
    copy_to_clipboard_submenu.add_command(
        label="文件路径", command=lambda: root.copy_filepath_to_clipboard()
    )
    copy_to_clipboard_submenu.add_command(
        label="目录", command=lambda: root.copy_directory_to_clipboard()
    )
    edit_menu.add_cascade(label="复制到剪贴板", menu=copy_to_clipboard_submenu)

    # 创建选中文本操作子菜单
    selected_text_submenu = tk.Menu(main_menu, tearoff=0, font=menu_font_tuple)
    edit_menu.add_cascade(
        label="选中文本操作",
        menu=create_selected_text_submenu(
            selected_text_submenu, root, menu_font_tuple, True
        ),
    )

    # 创建插入子菜单
    insert_submenu = create_insert_submenu(edit_menu, root, menu_font_tuple)
    edit_menu.add_cascade(label="插入", menu=insert_submenu)

    # 将编辑菜单添加到主菜单
    main_menu.add_cascade(label="编辑", menu=edit_menu)

    # 创建导航菜单
    navigate_menu = tk.Menu(main_menu, tearoff=0, font=menu_font_tuple)

    # 文件导航功能
    navigate_menu.add_command(
        label="转到文件顶部", command=lambda: root.goto_top(), accelerator="Ctrl+Home"
    )
    navigate_menu.add_command(
        label="转到文件底部", command=lambda: root.goto_bottom(), accelerator="Ctrl+End"
    )
    navigate_menu.add_separator()

    # 页面导航功能
    navigate_menu.add_command(
        label="向上翻页", command=lambda: root.page_up(), accelerator="PgUp"
    )
    navigate_menu.add_command(
        label="向下翻页", command=lambda: root.page_down(), accelerator="PgDn"
    )
    navigate_menu.add_separator()

    # 行导航功能
    navigate_menu.add_command(
        label="转到行", command=lambda: root.goto_line(), accelerator="Ctrl+G"
    )
    navigate_menu.add_command(
        label="转到行首",
        command=lambda: root.goto_line_start(),
        accelerator="Ctrl+Shift+<",
    )
    navigate_menu.add_command(
        label="转到行尾",
        command=lambda: root.goto_line_end(),
        accelerator="Ctrl+Shift+>",
    )
    navigate_menu.add_separator()

    # 书签功能
    navigate_menu.add_command(
        label="添加/删除书签",
        command=lambda: root.toggle_bookmark(),
        accelerator="Ctrl+B",
    )
    navigate_menu.add_command(
        label="上一个书签",
        command=lambda: root.goto_previous_bookmark(),
        accelerator="Ctrl+[",
    )
    navigate_menu.add_command(
        label="下一个书签",
        command=lambda: root.goto_next_bookmark(),
        accelerator="Ctrl+]",
    )
    navigate_menu.add_command(
        label="清除所有书签",
        command=lambda: root.clear_all_bookmarks(),
        accelerator="Alt+L",
    )

    # 将导航菜单添加到主菜单
    main_menu.add_cascade(label="导航", menu=navigate_menu)

    # 创建主题菜单
    theme_menu = tk.Menu(main_menu, tearoff=0, font=menu_font_tuple)

    # 字体
    theme_menu.add_command(
        label="字体", command=lambda: show_font_dialog(root), accelerator="Ctrl+T"
    )

    # 背景色
    theme_menu.add_command(
        label="背景色",
        command=lambda: set_text_background_color(root),
        accelerator="Ctrl+Shift+B",
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

    # 行号显示设置
    settings_menu.add_checkbutton(
        label="显示行号",
        command=lambda: toggle_line_numbers(root),
        variable=root.line_numbers_var,
    )

    # 全屏模式设置
    settings_menu.add_checkbutton(
        label="全屏模式",
        command=lambda: root.toggle_fullscreen(),
        variable=root.fullscreen_var,
        accelerator="F11",
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

    # 语法高亮设置
    settings_menu.add_checkbutton(
        label="启用语法高亮",
        command=lambda: toggle_syntax_highlight_menu(root),
        variable=root.syntax_highlight_var,
        accelerator="Ctrl+L",
    )

    # 创建语法高亮模式子菜单
    highlight_mode_submenu = tk.Menu(settings_menu, tearoff=0, font=menu_font_tuple)

    # 添加语法高亮模式选项
    highlight_mode_submenu.add_radiobutton(
        label="渲染可见行",
        variable=root.syntax_highlight_mode_var,
        value=True,
        command=lambda: set_syntax_highlight_mode(True, root),
    )
    highlight_mode_submenu.add_radiobutton(
        label="渲染全部",
        variable=root.syntax_highlight_mode_var,
        value=False,
        command=lambda: set_syntax_highlight_mode(False, root),
    )
    settings_menu.add_cascade(label="高亮模式", menu=highlight_mode_submenu)

    # 自动递增编号设置
    settings_menu.add_checkbutton(
        label="启用自动递增编号",
        command=lambda: toggle_auto_increment_number(root),
        variable=root.auto_increment_number_var,
    )

    # 光标所在行高亮设置
    settings_menu.add_checkbutton(
        label="启用光标所在行高亮",
        command=lambda: toggle_highlight_current_line(root),
        variable=root.highlight_current_line_var,
    )
    settings_menu.add_separator()

    # 第三组：文件与编辑器设置
    # 文件变更监控设置
    settings_menu.add_checkbutton(
        label="启用文件变更监控",
        command=lambda: toggle_file_monitoring(root),
        variable=root.file_monitoring_var,
    )

    # 制表符设置
    settings_menu.add_checkbutton(
        label="使用空格代替制表符",
        command=lambda: toggle_use_spaces_for_tab(root),
        variable=root.use_spaces_for_tab_var,
    )

    # 创建制表符宽度子菜单
    tab_width_submenu = tk.Menu(settings_menu, tearoff=0, font=menu_font_tuple)

    # 定义可用的制表符宽度选项
    tab_width_options = [
        ("1", 1),
        ("2", 2),
        ("4", 4),
        ("6", 6),
        ("8", 8),
        ("10", 10),
        ("12", 12),
        ("14", 14),
        ("16", 16),
        ("18", 18),
        ("20", 20),
    ]

    # 创建制表符宽度菜单项
    for label, value in tab_width_options:
        tab_width_submenu.add_radiobutton(
            label=f"{label}",
            variable=root.tab_width_var,
            value=value,
            command=lambda: set_tab_width(root),
        )

    settings_menu.add_cascade(label="制表符宽度", menu=tab_width_submenu)
    settings_menu.add_separator()

    # 第四组：保存设置
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

    # 第五组：配置管理
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
        label="关于", command=lambda: show_about_dialog(root), accelerator="F1"
    )

    # 将帮助菜单添加到主菜单
    main_menu.add_cascade(label="帮助", menu=help_menu)

    # 将主菜单配置到根窗口
    root.config(menu=main_menu)

    # 绑定编辑菜单到鼠标右键
    def show_edit_menu(event):
        """显示编辑菜单（鼠标右键菜单）"""
        try:
            edit_menu.tk_popup(event.x_root, event.y_root)
        finally:
            edit_menu.grab_release()

    # 获取文本区域对象并绑定右键事件
    root.text_area.bind("<Button-3>", show_edit_menu)

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
    root.status_bar.show_notification(f"文件编码已更改为: {encoding}", 500)


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
    root.status_bar.show_notification(
        f"换行符已更改为: {line_ending_names.get(line_ending, line_ending)}", 500
    )

    # 如果有文件路径或总字符数大于0，则标记文件为已修改
    if app_instance.current_file_path or app_instance.get_char_count() > 0:
        # 标记文件为已修改
        app_instance.set_modified(True)
        # 更新状态栏
        app_instance._update_status_bar()


def toggle_use_spaces_for_tab(root):
    """切换是否使用空格代替制表符的设置

    Args:
        root: 主窗口实例，用于访问配置
    """
    # 保存配置
    config_manager.set(
        "text_editor.use_spaces_for_tab", root.use_spaces_for_tab_var.get()
    )
    config_manager.save_config()

    # 通知用户
    root.status_bar.show_notification(
        "已使用空格代替制表符"
        if root.use_spaces_for_tab_var.get()
        else "已使用制表符代替空格"
    )


def set_tab_width(root):
    """设置制表符宽度

    Args:
        root: 主窗口实例，用于访问配置
    """
    # 保存配置
    config_manager.set("text_editor.tab_width", root.tab_width_var.get())
    config_manager.save_config()

    # 通知用户
    root.status_bar.show_notification(
        f"已设置制表符宽度为: {root.tab_width_var.get()}", 500
    )


def toggle_toolbar_visibility(root):
    """切换工具栏的显示/隐藏状态

    Args:
        root: 主窗口实例，用于访问工具栏组件
    """
    # 获取当前工具栏显示状态（此时Checkbutton已经自动切换了值）
    current_state = root.toolbar_var.get()

    # 保存配置
    config_manager.set("app.show_toolbar", current_state)
    config_manager.save_config()

    # 暂时捕获所有事件，防止用户交互
    root.grab_set()

    # 使用after方法延迟执行，减少闪烁
    def toggle_toolbar():
        try:
            # 切换工具栏显示状态
            if hasattr(root, "toolbar"):
                if current_state:
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

    # 如果提供了主窗口实例，更新行高亮颜色
    if root and hasattr(root, "_setup_line_highlight"):
        root._setup_line_highlight(full_init=False)

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
    # 获取当前自动换行状态（此时Checkbutton已经自动切换了值）
    current_state = root.auto_wrap_var.get()

    # 保存配置
    config_manager.set("text_editor.auto_wrap", current_state)
    config_manager.save_config()

    # 直接设置文本框的自动换行属性
    if hasattr(root, "text_area"):
        # 设置文本框的自动换行属性
        wrap_mode = "word" if current_state else "none"
        root.text_area.configure(wrap=wrap_mode)

        # 滚动条的显示/隐藏将由app_initializer中的自动检查机制处理

        # 显示通知
        status_text = "已启用" if current_state else "已禁用"
        root.status_bar.show_notification(f"自动换行{status_text}", 500)


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
    # 获取当前备份状态（此时Checkbutton已经自动切换了值）
    current_state = root.backup_var.get()

    # 保存配置
    config_manager.set("app.backup_enabled", current_state)
    config_manager.save_config()

    # 开启的时候立即备份一次
    if current_state and root.current_file_path and not root.is_modified():
        root.file_ops._create_backup_copy(root.current_file_path)

    # 显示通知
    root.status_bar.show_notification(
        f"备份模式已切换为: {'已启用' if current_state else '已禁用'}", 500
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
    root._update_window_title()

    # 显示模式名称
    mode_names = {
        "filename": "仅显示文件名",
        "filepath": "显示完整文件路径",
        "filename_and_dir": "显示文件名和目录路径",
    }
    mode_name = mode_names.get(mode, mode)

    # 显示通知
    root.status_bar.show_notification(f"窗口标题显示模式已切换为: {mode_name}", 500)


def toggle_syntax_highlight(root):
    """切换语法高亮的启用/禁用状态(用于快捷键)

    Args:
        root: 主窗口实例，用于访问语法高亮管理器
    """
    # 获取当前语法高亮状态并切换
    current_state = root.syntax_highlight_var.get()
    new_state = not current_state
    root.syntax_highlight_var.set(new_state)

    # 保存配置到配置管理器
    config_manager.set("syntax_highlighter.enabled", new_state)
    config_manager.save_config()

    # 应用设置到语法高亮管理器
    root.syntax_highlighter.set_enabled(new_state, root.current_file_path)

    # 显示通知
    root.status_bar.show_notification(
        f"语法高亮已{'启用' if new_state else '禁用'}", 500
    )


def toggle_syntax_highlight_menu(root):
    """切换语法高亮的启用/禁用状态(用于菜单栏)

    Args:
        root: 主窗口实例，用于访问语法高亮管理器
    """
    # 获取当前语法高亮状态（此时Checkbutton已经自动切换了值）
    new_state = root.syntax_highlight_var.get()

    # 保存配置到配置管理器
    config_manager.set("syntax_highlighter.enabled", new_state)
    config_manager.save_config()

    # 应用设置到语法高亮管理器
    root.syntax_highlighter.set_enabled(new_state, root.current_file_path)

    # 显示通知
    root.status_bar.show_notification(
        f"语法高亮已{'启用' if new_state else '禁用'}", 500
    )


def set_syntax_highlight_mode(mode: bool, root):
    """设置语法高亮的渲染模式

    Args:
        mode (bool): 渲染模式，可选值: True, False
        root: 主窗口实例，用于访问语法高亮管理器
    """
    # 保存配置到配置管理器
    config_manager.set("syntax_highlighter.render_visible_only", mode)
    config_manager.save_config()

    # 应用设置到语法高亮管理器
    root.syntax_highlighter.set_render_mode(mode)

    # 应用到当前打开的文件
    if root.current_file_path:
        root.syntax_highlighter.apply_highlighting(root.current_file_path)

    # 显示通知
    mode_text = "渲染可见行" if mode else "渲染全部"
    root.status_bar.show_notification(
        f"语法高亮模式已设置为: {mode_text}, 请重启应用以生效", 500
    )


def toggle_line_numbers(root):
    """
    切换行号显示状态

    Args:
        root: 主窗口实例
    """
    # 获取当前行号显示状态（此时Checkbutton已经自动切换了值）
    current_state = root.line_numbers_var.get()

    # 保存配置
    config_manager.set("text_editor.show_line_numbers", current_state)
    config_manager.save_config()

    # 控制行号侧边栏的显示和隐藏
    root.line_number_canvas.toggle_visibility(current_state)

    # 显示通知
    root.status_bar.show_notification(
        f"行号显示已{current_state and '启用' or '禁用'}", 500
    )


def toggle_auto_increment_number(root):
    """
    切换自动递增编号功能状态

    Args:
        root: 主窗口实例
    """
    # 获取当前自动递增编号状态（此时Checkbutton已经自动切换了值）
    current_state = root.auto_increment_number_var.get()

    # 保存配置
    config_manager.set("text_editor.auto_increment_number", current_state)
    config_manager.save_config()

    # 显示通知
    root.status_bar.show_notification(
        f"自动递增编号已{current_state and '启用' or '禁用'}", 500
    )


def toggle_highlight_current_line(root):
    """
    切换光标所在行高亮功能状态

    Args:
        root: 主窗口实例
    """
    # 获取当前光标所在行高亮状态（此时Checkbutton已经自动切换了值）
    current_state = root.highlight_current_line_var.get()

    # 保存配置
    config_manager.set("text_editor.highlight_current_line", current_state)
    config_manager.save_config()

    # 重新初始化行高亮设置
    root._setup_line_highlight(full_init=False)

    # 如果禁用了高亮，清除当前高亮
    if not current_state and hasattr(root, "current_line_tag"):
        root.text_area.tag_remove(root.current_line_tag, "1.0", "end")

    # 显示通知
    root.status_bar.show_notification(
        f"光标所在行高亮已{current_state and '启用' or '禁用'}", 500
    )


def toggle_file_monitoring(root):
    """
    切换文件变更监控功能状态

    Args:
        root: 主窗口实例
    """
    # 获取当前文件变更监控状态（此时Checkbutton已经自动切换了值）
    current_state = root.file_monitoring_var.get()

    # 更新FileWatcher的监控设置
    root.file_watcher.update_monitoring_setting(current_state)

    # 显示通知
    root.status_bar.show_notification(
        f"文件变更监控已{current_state and '启用' or '禁用'}", 500
    )


def set_text_background_color(root):
    """
    设置文本编辑器背景色

    Args:
        root: 主窗口实例
    """
    # 获取当前背景色
    current_color = config_manager.get("text_editor.bg_color", "#F5F5F5")

    # 显示颜色选择器对话框
    selected_color = show_color_picker(root, current_color)

    if selected_color:
        # 保存配置
        config_manager.set("text_editor.bg_color", selected_color)
        config_manager.save_config()

        # 应用到文本编辑器
        root.text_area.configure(fg_color=selected_color)

        # 显示通知
        root.status_bar.show_notification(
            f"文本编辑器背景色已设置为: {selected_color}", 500
        )
