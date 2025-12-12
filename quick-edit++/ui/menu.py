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
from ui.selected_text_submenu import (
    create_formatting_submenu,
    create_encoding_decoding_submenu,
)
from ui.file_properties_dialog import show_file_properties_dialog
from ui.color_picker import show_color_picker
from config.config_manager import config_manager
from ui.utils import get_supported_encodings
from tkinter import messagebox, filedialog
from ui.insert_submenu import create_insert_submenu
from ui.selected_text_submenu import create_selected_text_submenu
from ui.notification import NotificationPosition


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

        # 按首字母分组编码
        encoding_groups = {}
        for enc in encodings_sorted:
            # 获取首字母
            first_char = enc[0].upper() if enc else "OTHER"

            # 将编码添加到对应首字母的组中
            if first_char not in encoding_groups:
                encoding_groups[first_char] = []
            encoding_groups[first_char].append(enc)

        # 为每个首字母创建子菜单
        for first_char in sorted(encoding_groups.keys()):
            group_encodings = encoding_groups[first_char]
            group_name = f"{first_char} ({len(group_encodings)}个)"
            group_menu = tk.Menu(more_encodings_menu, tearoff=0, font=font_tuple)
            more_encodings_menu.add_cascade(
                label=group_name, menu=group_menu, font=font_tuple
            )

            # 添加该组的所有编码
            for enc in group_encodings:
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
        label="重命名", command=lambda: root.rename_file(), accelerator="Ctrl+M"
    )
    root.rename_menu_index = file_menu.index(tk.END)  # 保存重命名菜单项索引
    file_menu.add_command(
        label="另存为", command=lambda: root.save_file_as(), accelerator="Ctrl+Shift+S"
    )
    file_menu.add_command(
        label="保存副本",
        command=root.save_file_copy,
        accelerator="Ctrl+Shift+B",
        font=menu_font_tuple,
    )
    root.save_copy_menu_index = file_menu.index(tk.END)  # 保存菜单项索引

    file_menu.add_command(
        label="关闭文件", command=lambda: root.close_file(), accelerator="Ctrl+W"
    )

    # 分隔符
    file_menu.add_separator()

    # 创建最近打开文件子菜单
    # 创建打开文件的回调函数
    def on_open_recent_file(file_path):
        # 检查是否为只读模式
        if root.is_read_only:
            messagebox.showinfo("提示", "当前为只读模式，请先关闭只读模式后再打开文件")
            return

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
        # 检查是否为只读模式
        if root.is_read_only:
            messagebox.showinfo(
                "提示", "当前为只读模式，请先关闭只读模式后再重新载入文件"
            )
            return

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

    # 创建文档统计信息
    file_menu.add_command(
        label="文档统计信息",
        command=lambda: show_document_stats_dialog(root),
        accelerator="F2",
    )

    # 文件属性选项
    file_menu.add_command(
        label="文件属性",
        command=lambda: show_file_properties_dialog(root, root.current_file_path),
        accelerator="F3",
    )
    # 获取文件属性菜单项索引，用于后续更新状态
    root.file_properties_menu_index = file_menu.index(tk.END)

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
        label="清除", command=lambda: root.clear_all(), accelerator="Ctrl+D"
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

    # 分隔符
    edit_menu.add_separator()

    # 创建Markdown语法子菜单
    markdown_submenu = tk.Menu(edit_menu, tearoff=0, font=menu_font_tuple)

    # 文本格式
    markdown_submenu.add_command(
        label="粗体", command=lambda: root.markdown_bold(), accelerator="Ctrl+B"
    )
    markdown_submenu.add_command(
        label="删除线",
        command=lambda: root.markdown_strikethrough(),
        accelerator="Ctrl+Shift+-",
    )
    markdown_submenu.add_command(
        label="高亮",
        command=lambda: root.markdown_highlight(),
        accelerator="Ctrl+Shift+L",
    )
    markdown_submenu.add_separator()

    # 代码格式
    markdown_submenu.add_command(
        label="行内代码",
        command=lambda: root.markdown_inline_code(),
        accelerator="Ctrl+Shift+`",
    )
    markdown_submenu.add_command(
        label="代码块",
        command=lambda: root.markdown_code_block(),
        accelerator="Ctrl+Shift+K",
    )
    markdown_submenu.add_separator()

    # 链接和图片
    markdown_submenu.add_command(label="链接", command=lambda: root.markdown_link())
    markdown_submenu.add_command(label="图片", command=lambda: root.markdown_image())
    markdown_submenu.add_separator()

    # 结构元素
    markdown_submenu.add_command(
        label="引用", command=lambda: root.markdown_quote(), accelerator="Ctrl+Shift+Q"
    )
    markdown_submenu.add_separator()

    # 标题
    markdown_submenu.add_command(
        label="一级标题",
        command=lambda: root.markdown_heading_1(),
        accelerator="Ctrl+1",
    )
    markdown_submenu.add_command(
        label="二级标题",
        command=lambda: root.markdown_heading_2(),
        accelerator="Ctrl+2",
    )
    markdown_submenu.add_command(
        label="三级标题",
        command=lambda: root.markdown_heading_3(),
        accelerator="Ctrl+3",
    )
    markdown_submenu.add_command(
        label="四级标题",
        command=lambda: root.markdown_heading_4(),
        accelerator="Ctrl+4",
    )
    markdown_submenu.add_command(
        label="五级标题",
        command=lambda: root.markdown_heading_5(),
        accelerator="Ctrl+5",
    )
    markdown_submenu.add_command(
        label="六级标题",
        command=lambda: root.markdown_heading_6(),
        accelerator="Ctrl+6",
    )

    edit_menu.add_cascade(label="Markdown语法", menu=markdown_submenu)

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
        accelerator="Alt+B",
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
    # 创建界面设置子菜单
    interface_settings_submenu = tk.Menu(settings_menu, tearoff=0, font=menu_font_tuple)

    # 工具栏显示设置
    interface_settings_submenu.add_checkbutton(
        label="显示工具栏",
        command=lambda: toggle_toolbar_visibility(root, switch_state=False),
        variable=root.toolbar_var,
        accelerator="Alt+T",
    )

    # 行号显示设置
    interface_settings_submenu.add_checkbutton(
        label="显示行号",
        command=lambda: toggle_line_numbers(root, switch_state=False),
        variable=root.line_numbers_var,
        accelerator="Alt+N",
    )

    # 全屏模式设置
    interface_settings_submenu.add_checkbutton(
        label="全屏模式",
        command=lambda: root.toggle_fullscreen(switch_state=False),
        variable=root.fullscreen_var,
        accelerator="F11",
    )

    # 创建窗口标题显示子菜单
    title_display_submenu = tk.Menu(
        interface_settings_submenu, tearoff=0, font=menu_font_tuple
    )

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

    interface_settings_submenu.add_cascade(
        label="窗口标题显示", menu=title_display_submenu
    )
    settings_menu.add_cascade(label="界面设置", menu=interface_settings_submenu)

    # 第二组：编辑设置
    # 创建编辑设置子菜单
    editor_settings_submenu = tk.Menu(settings_menu, tearoff=0, font=menu_font_tuple)

    # 自动换行设置
    editor_settings_submenu.add_checkbutton(
        label="启用自动换行",
        command=lambda: toggle_auto_wrap(root, switch_state=False),
        variable=root.auto_wrap_var,
        accelerator="Ctrl+Shift+W",
    )

    # 语法高亮设置
    editor_settings_submenu.add_checkbutton(
        label="启用语法高亮",
        command=lambda: toggle_syntax_highlight(root, switch_state=False),
        variable=root.syntax_highlight_var,
        accelerator="Ctrl+L",
    )

    # 创建语法高亮模式子菜单
    highlight_mode_submenu = tk.Menu(
        editor_settings_submenu, tearoff=0, font=menu_font_tuple
    )

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
    editor_settings_submenu.add_cascade(label="高亮模式", menu=highlight_mode_submenu)

    # 自动递增编号设置
    editor_settings_submenu.add_checkbutton(
        label="启用自动递增编号",
        command=lambda: toggle_auto_increment_number(root),
        variable=root.auto_increment_number_var,
    )

    # 光标所在行高亮设置
    editor_settings_submenu.add_checkbutton(
        label="启用光标所在行高亮",
        command=lambda: toggle_highlight_current_line(root, switch_state=False),
        variable=root.highlight_current_line_var,
        accelerator="Ctrl+Shift+H",
    )

    # 制表符设置
    editor_settings_submenu.add_checkbutton(
        label="使用空格代替制表符",
        command=lambda: toggle_use_spaces_for_tab(root),
        variable=root.use_spaces_for_tab_var,
    )

    # 创建制表符宽度子菜单
    tab_width_submenu = tk.Menu(
        editor_settings_submenu, tearoff=0, font=menu_font_tuple
    )

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

    editor_settings_submenu.add_cascade(label="制表符宽度", menu=tab_width_submenu)
    settings_menu.add_cascade(label="编辑设置", menu=editor_settings_submenu)

    # 第三组：文件设置
    # 创建文件设置子菜单
    file_settings_submenu = tk.Menu(settings_menu, tearoff=0, font=menu_font_tuple)

    # 文件变更监控设置
    file_settings_submenu.add_checkbutton(
        label="启用文件变更监控",
        command=lambda: toggle_file_monitoring(root),
        variable=root.file_monitoring_var,
    )

    # 静默重载模式设置
    file_settings_submenu.add_checkbutton(
        label="文件变更时静默重载",
        command=lambda: toggle_silent_reload(root),
        variable=root.silent_reload_var,
    )

    # 设置文件选择器初始路径
    file_settings_submenu.add_command(
        label="设置文件选择器初始路径",
        command=lambda: set_file_dialog_initial_dir(root),
    )
    settings_menu.add_cascade(label="文件设置", menu=file_settings_submenu)

    # 第四组：保存设置
    # 创建保存设置子菜单
    save_settings_submenu = tk.Menu(settings_menu, tearoff=0, font=menu_font_tuple)

    # 自动保存设置
    save_settings_submenu.add_checkbutton(
        label="启用自动保存",
        command=lambda: toggle_auto_save(root),
        variable=root.auto_save_var,
    )

    # 创建自动保存间隔子菜单
    autosave_submenu = tk.Menu(save_settings_submenu, tearoff=0, font=menu_font_tuple)

    # 获取当前自动保存间隔
    auto_save_interval = config_manager.get("app.auto_save_interval", 5)

    # 定义可用的间隔选项
    interval_options = [
        ("1秒", 1),
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
        # 如果不在列表中, 使用默认值5秒
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

    save_settings_submenu.add_cascade(label="自动保存间隔", menu=autosave_submenu)

    # 备份设置
    save_settings_submenu.add_checkbutton(
        label="启用副本备份",
        command=lambda: toggle_backup(root),
        variable=root.backup_var,
    )
    settings_menu.add_cascade(label="保存设置", menu=save_settings_submenu)

    # 第五组：通知设置
    # 创建通知设置子菜单
    notification_settings_submenu = tk.Menu(
        settings_menu, tearoff=0, font=menu_font_tuple
    )

    # 创建通知位置子菜单
    notification_position_submenu = tk.Menu(
        notification_settings_submenu, tearoff=0, font=menu_font_tuple
    )

    # 使用NotificationPosition中的位置选项配置
    for label, value in NotificationPosition.OPTIONS:
        notification_position_submenu.add_radiobutton(
            label=label,
            variable=root.notification_position_var,
            value=value,
            command=lambda pos=value: set_notification_position(pos, root),
        )

    notification_settings_submenu.add_cascade(
        label="通知位置", menu=notification_position_submenu
    )

    # 创建通知持续时间子菜单
    notification_duration_submenu = tk.Menu(
        notification_settings_submenu, tearoff=0, font=menu_font_tuple
    )

    # 定义可用的通知持续时间选项（毫秒）
    notification_duration_options = [
        ("1秒", 1000),
        ("2秒", 2000),
        ("3秒", 3000),
        ("5秒", 5000),
        ("8秒", 8000),
        ("10秒", 10000),
        ("15秒", 15000),
        ("20秒", 20000),
        ("30秒", 30000),
    ]

    # 创建通知持续时间菜单项
    for label, value in notification_duration_options:
        notification_duration_submenu.add_radiobutton(
            label=label,
            variable=root.notification_duration_var,
            value=value,
            command=lambda dur=value: set_notification_duration(dur, root),
        )

    notification_settings_submenu.add_cascade(
        label="通知持续时间", menu=notification_duration_submenu
    )
    settings_menu.add_cascade(label="通知设置", menu=notification_settings_submenu)

    # 第六组：配置管理
    # 创建配置管理子菜单
    config_settings_submenu = tk.Menu(settings_menu, tearoff=0, font=menu_font_tuple)

    # 查看配置
    config_settings_submenu.add_command(
        label="查看配置",
        command=lambda: root.file_ops.open_config_file(),
        accelerator="Ctrl+Shift+C",
    )

    # 查看日志
    config_settings_submenu.add_command(
        label="查看日志", command=lambda: root.file_ops.open_log_file()
    )

    # 重置设置
    config_settings_submenu.add_command(
        label="重置设置", command=lambda: root._reset_settings()
    )
    settings_menu.add_cascade(label="配置管理", menu=config_settings_submenu)

    # 将设置菜单添加到主菜单
    main_menu.add_cascade(label="设置", menu=settings_menu)

    # 创建工具菜单
    tools_menu = tk.Menu(main_menu, tearoff=0, font=menu_font_tuple)

    # 创建格式化子菜单
    create_formatting_submenu(tools_menu, root, menu_font_tuple)

    # 创建编码解码子菜单
    create_encoding_decoding_submenu(tools_menu, root, menu_font_tuple)

    # 添加分隔符
    tools_menu.add_separator()

    # 添加颜色选择器选项
    tools_menu.add_command(
        label="颜色选择器",
        command=lambda: show_color_picker(root),
        font=menu_font_tuple,
    )

    # 将工具菜单添加到主菜单
    main_menu.add_cascade(label="工具", menu=tools_menu)

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
    # app_instance.status_bar.show_notification(f"文件编码已更改为: {encoding}", 500)
    app_instance.nm.show_info(message=f"文件编码已更改为: {encoding}")


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
    # app_instance.status_bar.show_notification(
    #     f"换行符已更改为: {line_ending_names.get(line_ending, line_ending)}", 500
    # )
    app_instance.nm.show_info(
        message=f"换行符已更改为: {line_ending_names.get(line_ending, line_ending)}"
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
    # root.status_bar.show_notification(
    #     "已使用空格代替制表符"
    #     if root.use_spaces_for_tab_var.get()
    #     else "已使用制表符代替空格"
    # )
    root.nm.show_info(
        message=(
            "已使用空格代替制表符"
            if root.use_spaces_for_tab_var.get()
            else "已使用制表符代替空格"
        )
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
    # root.status_bar.show_notification(
    #     f"已设置制表符宽度为: {root.tab_width_var.get()}", 500
    # )
    root.nm.show_info(message=f"已设置制表符宽度为: {root.tab_width_var.get()}")


def toggle_toolbar_visibility(root, switch_state=True):
    """切换工具栏的显示/隐藏状态

    Args:
        root: 主窗口实例，用于访问工具栏组件
        switch_state (bool): 是否需要翻转状态，默认为True
                             True - 切换状态（用于快捷键）
                             False - 应用当前状态（用于菜单点击）
    """
    if switch_state:
        # 获取当前工具栏显示状态
        current_state = root.toolbar_var.get()

        # 计算新状态（当前状态的取反）
        new_state = not current_state

        # 设置新状态
        root.toolbar_var.set(new_state)
    else:
        # 应用当前状态（不翻转）
        new_state = root.toolbar_var.get()

    # 保存配置
    config_manager.set("app.show_toolbar", new_state)
    config_manager.save_config()

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
                    root.nm.show_info(message="已显示工具栏")
                else:
                    # 隐藏工具栏，但保留布局空间
                    root.toolbar.grid_remove()
                    root.nm.show_info(message="已隐藏工具栏")
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

    # 更新行高亮颜色
    root.after(60, lambda: root._setup_line_highlight(full_init=False))

    # 更新行号栏
    root.after(100, lambda: root.line_number_canvas.draw_line_numbers())

    # 更新行号栏主题
    root.after(120, lambda: root.line_number_canvas.update_theme())

    # 显示通知
    # messagebox.showinfo(
    #     "提示",
    #     f"主题模式已切换为: {mode_name}",
    # )
    root.nm.show_info(message=f"主题模式已切换为: {mode_name}")


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
    # messagebox.showinfo(
    #     "提示",
    #     f"颜色主题已切换为: {theme_name}, 请重启应用以生效",
    # )
    root.nm.show_info(message=f"颜色主题已切换为: {theme_name}, 请重启应用以生效")


def toggle_auto_wrap(root, switch_state=True):
    """切换自动换行模式

    Args:
        root: 主窗口实例，用于访问文本编辑器
        switch_state (bool): 是否需要翻转状态，默认为True
                             True - 切换状态（用于快捷键）
                             False - 应用当前状态（用于菜单点击）
    """
    if switch_state:
        # 获取当前自动换行状态
        current_state = root.auto_wrap_var.get()

        # 计算新状态（当前状态的取反）
        new_state = not current_state

        # 设置新状态
        root.auto_wrap_var.set(new_state)
    else:
        # 应用当前状态（不翻转）
        new_state = root.auto_wrap_var.get()

    # 保存配置
    config_manager.set("text_editor.auto_wrap", new_state)
    config_manager.save_config()

    # 直接设置文本框的自动换行属性
    wrap_mode = "word" if new_state else "none"
    root.text_area.configure(wrap=wrap_mode)

    # 滚动条的显示/隐藏将由app_initializer中的自动检查机制处理
    # 显示通知
    status_text = "已启用" if new_state else "已禁用"
    # root.status_bar.show_notification(f"自动换行{status_text}", 500)
    root.nm.show_info(message=f"自动换行{status_text}")


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
    # root.status_bar.show_notification(
    #     f"备份模式已切换为: {'已启用' if current_state else '已禁用'}", 500
    # )
    root.nm.show_info(
        message=f"备份模式已切换为: {'已启用' if current_state else '已禁用'}"
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
    # root.status_bar.show_notification(f"窗口标题显示模式已切换为: {mode_name}", 500)
    root.nm.show_info(message=f"窗口标题显示模式已切换为: {mode_name}")


def toggle_syntax_highlight(root, switch_state=True):
    """切换语法高亮的启用/禁用状态

    Args:
        root: 主窗口实例，用于访问语法高亮管理器
        switch_state (bool): 是否需要翻转状态，默认为True
                             True - 切换状态（用于快捷键）
                             False - 应用当前状态（用于菜单点击）
    """
    if switch_state:
        # 获取当前语法高亮状态并切换
        current_state = root.syntax_highlight_var.get()
        new_state = not current_state
        root.syntax_highlight_var.set(new_state)
    else:
        # 应用当前状态（不翻转）
        new_state = root.syntax_highlight_var.get()

    # 保存配置到配置管理器
    config_manager.set("syntax_highlighter.enabled", new_state)
    config_manager.save_config()

    # 应用设置到语法高亮管理器
    root.syntax_highlighter.set_enabled(new_state, root.current_file_path)

    # 更新文件信息
    root.status_bar.update_file_info()

    # 显示通知
    # root.status_bar.show_notification(
    #     f"语法高亮已{'启用' if new_state else '禁用'}", 500
    # )
    root.nm.show_info(message=f"语法高亮已{'启用' if new_state else '禁用'}")


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
    # messagebox.showinfo("提示", f"语法高亮模式已设置为: {mode_text}, 请重启应用以生效")
    root.nm.show_info(message=f"语法高亮模式已设置为: {mode_text}, 请重启应用以生效")


def toggle_line_numbers(root, switch_state=True):
    """
    切换行号显示状态

    Args:
        root: 主窗口实例
        switch_state (bool): 是否需要翻转状态，默认为True
                             True - 切换状态（用于快捷键）
                             False - 应用当前状态（用于菜单点击）
    """
    if switch_state:
        # 获取当前行号显示状态
        current_state = root.line_numbers_var.get()

        # 计算新状态（当前状态的取反）
        new_state = not current_state

        # 设置新状态
        root.line_numbers_var.set(new_state)
    else:
        # 应用当前状态（不翻转）
        new_state = root.line_numbers_var.get()

    # 保存配置
    config_manager.set("text_editor.show_line_numbers", new_state)
    config_manager.save_config()

    # 控制行号侧边栏的显示和隐藏
    root.line_number_canvas.toggle_visibility(new_state)

    # 显示通知
    # root.status_bar.show_notification(
    #     f"行号显示已{new_state and '启用' or '禁用'}", 500
    # )
    root.nm.show_info(message=f"行号显示已{new_state and '启用' or '禁用'}")


def toggle_auto_increment_number(root):
    """
    切换自动递增编号功能状态

    Args:
        root: 主窗口实例
    """
    # 获取当前自动递增编号状态
    new_state = root.auto_increment_number_var.get()

    # 保存配置
    config_manager.set("text_editor.auto_increment_number", new_state)
    config_manager.save_config()

    # 显示通知
    # root.status_bar.show_notification(
    #     f"自动递增编号已{new_state and '启用' or '禁用'}", 500
    # )
    root.nm.show_info(message=f"自动递增编号已{new_state and '启用' or '禁用'}")


def toggle_highlight_current_line(root, switch_state=True):
    """
    切换光标所在行高亮功能状态

    Args:
        root: 主窗口实例
        switch_state (bool): 是否需要翻转状态，默认为True
                             True - 切换状态（用于快捷键）
                             False - 应用当前状态（用于菜单点击）
    """
    if switch_state:
        # 获取当前光标所在行高亮状态
        current_state = root.highlight_current_line_var.get()

        # 计算新状态（当前状态的取反）
        new_state = not current_state

        # 设置新状态
        root.highlight_current_line_var.set(new_state)
    else:
        # 应用当前状态（不翻转）
        new_state = root.highlight_current_line_var.get()

    # 保存配置
    config_manager.set("text_editor.highlight_current_line", new_state)
    config_manager.save_config()

    # 重新初始化行高亮设置
    root._setup_line_highlight(full_init=False)

    # 如果禁用了高亮，清除当前高亮
    if not new_state and hasattr(root, "current_line_tag"):
        root.text_area.tag_remove(root.current_line_tag, "1.0", "end")

    # 显示通知
    # root.status_bar.show_notification(
    #     f"光标所在行高亮已{new_state and '启用' or '禁用'}", 500
    # )
    root.nm.show_info(message=f"光标所在行高亮已{new_state and '启用' or '禁用'}")


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
    # root.status_bar.show_notification(
    #     f"文件变更监控已{current_state and '启用' or '禁用'}", 500
    # )
    root.nm.show_info(message=f"文件变更监控已{current_state and '启用' or '禁用'}")


def toggle_silent_reload(root):
    """
    切换文件变更时静默重载模式

    Args:
        root: 主窗口实例
    """
    # 获取当前静默重载状态（此时Checkbutton已经自动切换了值）
    current_state = root.silent_reload_var.get()

    # 更新FileWatcher的静默重载设置
    root.file_watcher.set_silent_reload(current_state)

    # 显示通知
    # root.status_bar.show_notification(
    #     f"静默重载模式已{current_state and '启用' or '禁用'}", 500
    # )
    root.nm.show_info(message=f"静默重载模式已{current_state and '启用' or '禁用'}")


def set_file_dialog_initial_dir(root):
    """
    设置文件选择器的初始路径

    Args:
        root: 主窗口实例
    """
    # 获取当前初始路径
    current_dir = config_manager.get_file_dialog_initial_dir()

    # 打开目录选择对话框
    selected_dir = filedialog.askdirectory(
        title="选择文件选择器初始路径",
        initialdir=current_dir if current_dir else os.path.expanduser("~"),
        parent=root,
    )

    # 如果用户选择了目录
    if selected_dir:
        # 设置新的初始路径
        result, msg = config_manager.set_file_dialog_initial_dir(selected_dir)

        if result:
            # 显示成功通知
            root.nm.show_info(message=f"文件选择器初始路径已设置为: {selected_dir}")
        else:
            # 显示失败通知
            root.nm.show_error(message=f"设置文件选择器初始路径失败：{msg}")


def set_notification_position(position, root):
    """
    设置通知位置

    Args:
        position (str): 通知位置，可选值: top_left, top_right, bottom_left, bottom_right, top_center, center
        root: 主窗口实例
    """
    # 保存配置
    config_manager.set("notification.position", position)
    config_manager.save_config()

    # 更新通知管理器的默认位置
    root.nm.set_default_position(NotificationPosition.from_string(position))

    # 使用NotificationPosition中的位置名称映射
    position_name = NotificationPosition.NAMES.get(position, position)

    # 显示通知
    root.nm.show_info(message=f"通知位置已设置为: {position_name}")


def set_notification_duration(duration, root):
    """
    设置通知持续时间

    Args:
        duration (int): 通知持续时间（毫秒）
        root: 主窗口实例
    """
    # 保存配置
    config_manager.set("notification.duration", duration)
    config_manager.save_config()

    # 更新通知管理器的默认持续时间
    root.nm.set_default_duration(duration)

    # 将毫秒转换为秒
    seconds = duration / 1000

    # 显示通知
    root.nm.show_info(message=f"通知持续时间已设置为: {seconds}秒")
