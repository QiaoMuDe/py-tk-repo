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
    edit_menu.add_command(label="查找", command=lambda: print("查找"))
    edit_menu.add_command(label="替换", command=lambda: print("替换"))
    edit_menu.add_separator()

    # 全选、清除
    edit_menu.add_command(
        label="全选", command=lambda: root.select_all(), accelerator="Ctrl+A"
    )
    edit_menu.add_command(
        label="清除", command=lambda: root.clear_all(), accelerator="Ctrl+Shift+D"
    )
    edit_menu.add_separator()

    # 新增导航功能
    edit_menu.add_command(
        label="转到文件顶部", command=lambda: root.goto_top(), accelerator="Home"
    )
    edit_menu.add_command(
        label="转到文件底部", command=lambda: root.goto_bottom(), accelerator="End"
    )
    edit_menu.add_command(
        label="向上翻页", command=lambda: root.page_up(), accelerator="PageUp"
    )
    edit_menu.add_command(
        label="向下翻页", command=lambda: root.page_down(), accelerator="PageDown"
    )
    edit_menu.add_command(
        label="转到行", command=lambda: root.goto_line(), accelerator="Ctrl+G"
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
    selected_text_submenu = tk.Menu(edit_menu, tearoff=0, font=menu_font_tuple)
    edit_menu.add_cascade(label="选中文本操作", menu=selected_text_submenu)
    
    # 在选中文本操作下创建各种子菜单
    text_processing_submenu = tk.Menu(selected_text_submenu, tearoff=0, font=menu_font_tuple)
    selected_text_submenu.add_cascade(label="文本处理", menu=text_processing_submenu)
    
    # 添加空白处理菜单项
    text_processing_submenu.add_command(
        label="移除首尾空白", command=lambda: root.trim_whitespace()
    )
    text_processing_submenu.add_command(
        label="移除左侧空白", command=lambda: root.trim_left_whitespace()
    )
    text_processing_submenu.add_command(
        label="移除右侧空白", command=lambda: root.trim_right_whitespace()
    )
    text_processing_submenu.add_command(
        label="移除多余空白", command=lambda: root.remove_extra_whitespace()
    )
    text_processing_submenu.add_separator()
    
    # 创建命名转换子菜单
    naming_conversion_submenu = tk.Menu(text_processing_submenu, tearoff=0, font=menu_font_tuple)
    text_processing_submenu.add_cascade(label="命名转换", menu=naming_conversion_submenu)
    
    # 创建基本转换子菜单
    basic_conversion_submenu = tk.Menu(naming_conversion_submenu, tearoff=0, font=menu_font_tuple)
    naming_conversion_submenu.add_cascade(label="基本转换", menu=basic_conversion_submenu)
    
    # 添加基本转换菜单项
    basic_conversion_submenu.add_command(
        label="下划线转驼峰", command=lambda: root.snake_to_camel()
    )
    basic_conversion_submenu.add_command(
        label="驼峰转下划线", command=lambda: root.camel_to_snake()
    )
    
    # 创建扩展转换子菜单
    extended_conversion_submenu = tk.Menu(naming_conversion_submenu, tearoff=0, font=menu_font_tuple)
    naming_conversion_submenu.add_cascade(label="扩展转换", menu=extended_conversion_submenu)
    
    # 添加扩展转换菜单项
    extended_conversion_submenu.add_command(
        label="下划线转帕斯卡", command=lambda: root.snake_to_pascal()
    )
    extended_conversion_submenu.add_command(
        label="帕斯卡转下划线", command=lambda: root.pascal_to_snake()
    )
    extended_conversion_submenu.add_command(
        label="驼峰转帕斯卡", command=lambda: root.camel_to_pascal()
    )
    extended_conversion_submenu.add_command(
        label="帕斯卡转驼峰", command=lambda: root.pascal_to_camel()
    )
    extended_conversion_submenu.add_command(
        label="短横线转下划线", command=lambda: root.kebab_to_snake()
    )
    extended_conversion_submenu.add_command(
        label="下划线转短横线", command=lambda: root.snake_to_kebab()
    )
    extended_conversion_submenu.add_command(
        label="短横线转驼峰", command=lambda: root.kebab_to_camel()
    )
    extended_conversion_submenu.add_command(
        label="驼峰转短横线", command=lambda: root.camel_to_kebab()
    )
    
    # 创建大小写转换子菜单
    case_conversion_submenu = tk.Menu(naming_conversion_submenu, tearoff=0, font=menu_font_tuple)
    naming_conversion_submenu.add_cascade(label="大小写转换", menu=case_conversion_submenu)
    
    # 添加大小写转换菜单项
    case_conversion_submenu.add_command(
        label="转为大写", command=lambda: root.to_upper_case()
    )
    case_conversion_submenu.add_command(
        label="转为小写", command=lambda: root.to_lower_case()
    )
    case_conversion_submenu.add_command(
        label="首字母大写", command=lambda: root.to_title_case()
    )
    case_conversion_submenu.add_command(
        label="每个单词首字母大写", command=lambda: root.to_title_case()
    )
    
    # 创建分隔符转换子菜单
    separator_conversion_submenu = tk.Menu(naming_conversion_submenu, tearoff=0, font=menu_font_tuple)
    naming_conversion_submenu.add_cascade(label="分隔符转换", menu=separator_conversion_submenu)
    
    # 添加分隔符转换菜单项
    separator_conversion_submenu.add_command(
        label="空格转下划线", command=lambda: root.space_to_snake()
    )
    separator_conversion_submenu.add_command(
        label="空格转短横线", command=lambda: root.space_to_kebab()
    )
    separator_conversion_submenu.add_command(
        label="空格转驼峰", command=lambda: root.space_to_camel()
    )
    separator_conversion_submenu.add_command(
        label="下划线转空格", command=lambda: root.snake_to_space()
    )
    separator_conversion_submenu.add_command(
        label="短横线转空格", command=lambda: root.kebab_to_space()
    )
    separator_conversion_submenu.add_command(
        label="驼峰转空格", command=lambda: root.camel_to_space()
    )
    
    # 创建编程规范子菜单
    programming_convention_submenu = tk.Menu(naming_conversion_submenu, tearoff=0, font=menu_font_tuple)
    naming_conversion_submenu.add_cascade(label="编程规范", menu=programming_convention_submenu)
    
    # 添加编程规范菜单项
    programming_convention_submenu.add_command(
        label="常量命名", command=lambda: root.to_constant_case()
    )
    programming_convention_submenu.add_command(
        label="私有变量命名", command=lambda: root.to_private_variable()
    )
    programming_convention_submenu.add_command(
        label="类命名", command=lambda: root.to_class_name()
    )
    programming_convention_submenu.add_command(
        label="接口命名", command=lambda: root.to_interface_name()
    )
    programming_convention_submenu.add_command(
        label="函数命名", command=lambda: root.to_function_name()
    )
    
    # 创建数据库相关子菜单
    database_conversion_submenu = tk.Menu(naming_conversion_submenu, tearoff=0, font=menu_font_tuple)
    naming_conversion_submenu.add_cascade(label="数据库相关", menu=database_conversion_submenu)
    
    # 添加数据库相关菜单项
    database_conversion_submenu.add_command(
        label="表名转换", command=lambda: root.to_table_name()
    )
    database_conversion_submenu.add_command(
        label="列名转换", command=lambda: root.to_column_name()
    )
    database_conversion_submenu.add_command(
        label="外键命名", command=lambda: root.to_foreign_key()
    )
    
    # 创建行处理子菜单
    line_processing_submenu = tk.Menu(selected_text_submenu, tearoff=0, font=menu_font_tuple)
    selected_text_submenu.add_cascade(label="行处理", menu=line_processing_submenu)
    
    # 添加行处理菜单项
    line_processing_submenu.add_command(
        label="移除空白行", command=lambda: root.remove_empty_lines()
    )
    line_processing_submenu.add_command(
        label="合并空白行", command=lambda: root.merge_empty_lines()
    )
    line_processing_submenu.add_command(
        label="移除重复行", command=lambda: root.remove_duplicate_lines()
    )
    line_processing_submenu.add_command(
        label="合并重复行", command=lambda: root.merge_duplicate_lines()
    )
    
    # 添加分隔符
    line_processing_submenu.add_separator()
    
    # 创建排序子菜单
    sort_submenu = tk.Menu(line_processing_submenu, tearoff=0, font=menu_font_tuple)
    line_processing_submenu.add_cascade(label="排序", menu=sort_submenu)
    
    # 添加排序菜单项
    sort_submenu.add_command(
        label="升序排序", command=lambda: root.sort_lines_ascending()
    )
    sort_submenu.add_command(
        label="降序排序", command=lambda: root.sort_lines_descending()
    )
    
    # 创建反转子菜单
    reverse_submenu = tk.Menu(line_processing_submenu, tearoff=0, font=menu_font_tuple)
    line_processing_submenu.add_cascade(label="反转", menu=reverse_submenu)
    
    # 添加反转菜单项
    reverse_submenu.add_command(
        label="字符反转", command=lambda: root.reverse_characters()
    )
    reverse_submenu.add_command(
        label="行反转", command=lambda: root.reverse_lines()
    )
    
    # 创建格式化子菜单
    formatting_submenu = tk.Menu(selected_text_submenu, tearoff=0, font=menu_font_tuple)
    selected_text_submenu.add_cascade(label="格式化", menu=formatting_submenu)
    
    # 创建JSON子菜单
    json_submenu = tk.Menu(formatting_submenu, tearoff=0, font=menu_font_tuple)
    formatting_submenu.add_cascade(label="JSON", menu=json_submenu)
    
    # 添加JSON菜单项
    json_submenu.add_command(
        label="格式化JSON", command=lambda: root.format_json()
    )
    json_submenu.add_command(
        label="压缩JSON", command=lambda: root.compress_json()
    )
    
    # 添加其他格式化菜单项
    formatting_submenu.add_command(
        label="格式化XML", command=lambda: root.format_xml()
    )
    
    # 创建CSV格式化子菜单
    csv_submenu = tk.Menu(formatting_submenu, tearoff=0, font=menu_font_tuple)
    formatting_submenu.add_cascade(label="CSV", menu=csv_submenu)
    csv_submenu.add_command(
        label="格式化CSV", command=lambda: root.format_csv(compress=False)
    )
    csv_submenu.add_command(
        label="压缩CSV", command=lambda: root.format_csv(compress=True)
    )
    
    formatting_submenu.add_command(
        label="格式化INI", command=lambda: root.format_ini()
    )
    formatting_submenu.add_command(
        label="格式化Python", command=lambda: root.format_python()
    )
    formatting_submenu.add_command(
        label="格式化YAML", command=lambda: root.format_yaml()
    )
    
    # 创建注释处理子菜单
    comment_processing_submenu = tk.Menu(selected_text_submenu, tearoff=0, font=menu_font_tuple)
    selected_text_submenu.add_cascade(label="注释处理", menu=comment_processing_submenu)
    comment_processing_submenu.add_command(
        label="添加#号注释", command=lambda: root.add_hash_comment()
    )
    comment_processing_submenu.add_command(
        label="添加//注释", command=lambda: root.add_slash_comment()
    )
    comment_processing_submenu.add_command(
        label="移除行注释", command=lambda: root.remove_line_comment()
    )
    
    # 创建编码解码子菜单
    encoding_decoding_submenu = tk.Menu(selected_text_submenu, tearoff=0, font=menu_font_tuple)
    selected_text_submenu.add_cascade(label="编码解码", menu=encoding_decoding_submenu)
    
    # 添加编码解码菜单项
    encoding_decoding_submenu.add_command(label="Base64编码", command=lambda: root.base64_encode())
    encoding_decoding_submenu.add_command(label="Base64解码", command=lambda: root.base64_decode())

    # 创建插入子菜单
    insert_submenu = tk.Menu(edit_menu, tearoff=0, font=menu_font_tuple)

    # 代码相关插入
    script_submenu = tk.Menu(insert_submenu, tearoff=0, font=menu_font_tuple)
    insert_submenu.add_cascade(label="代码", menu=script_submenu)
    script_submenu.add_command(
        label="脚本 Shebang 行", command=lambda: root.insert_shebang()
    )
    script_submenu.add_command(
        label="Go语言基本结构", command=lambda: root.insert_go_basic()
    )
    script_submenu.add_command(
        label="GO函数模板", command=lambda: root.insert_go_function_template()
    )
    script_submenu.add_command(
        label="GO结构体模板", command=lambda: root.insert_go_struct_template()
    )
    script_submenu.add_command(
        label="Python编码声明", command=lambda: root.insert_encoding()
    )
    script_submenu.add_command(
        label="Python函数模板", command=lambda: root.insert_python_function_template()
    )
    script_submenu.add_command(
        label="Python类模板", command=lambda: root.insert_python_class_template()
    )
    script_submenu.add_command(
        label="HTML基本结构", command=lambda: root.insert_html_basic_structure()
    )
    script_submenu.add_command(
        label="CSS基本结构", command=lambda: root.insert_css_basic_structure()
    )
    script_submenu.add_command(
        label="JavaScript函数模板",
        command=lambda: root.insert_javascript_function_template(),
    )
    script_submenu.add_command(
        label="SQL查询模板", command=lambda: root.insert_sql_query_template()
    )

    # 文件相关插入
    file_submenu = tk.Menu(insert_submenu, tearoff=0, font=menu_font_tuple)
    insert_submenu.add_cascade(label="文件", menu=file_submenu)
    file_submenu.add_command(label="文件名", command=lambda: root.insert_filename())
    file_submenu.add_command(label="文件路径", command=lambda: root.insert_filepath())
    file_submenu.add_command(label="目录路径", command=lambda: root.insert_directory())

    # 日期相关插入
    date_submenu = tk.Menu(insert_submenu, tearoff=0, font=menu_font_tuple)
    insert_submenu.add_cascade(label="日期", menu=date_submenu)
    date_submenu.add_command(
        label="YYYY-MM-DD", command=lambda: root.insert_date("ymd")
    )
    date_submenu.add_command(
        label="YYYY/MM/DD", command=lambda: root.insert_date("ymd_slash")
    )
    date_submenu.add_command(
        label="DD-MM-YYYY", command=lambda: root.insert_date("dmy")
    )
    date_submenu.add_command(
        label="DD/MM/YYYY", command=lambda: root.insert_date("dmy_slash")
    )
    date_submenu.add_command(
        label="MM-DD-YYYY", command=lambda: root.insert_date("mdy")
    )
    date_submenu.add_command(
        label="MM/DD/YYYY", command=lambda: root.insert_date("mdy_slash")
    )

    # 时间相关插入
    time_submenu = tk.Menu(insert_submenu, tearoff=0, font=menu_font_tuple)
    insert_submenu.add_cascade(label="时间", menu=time_submenu)
    time_submenu.add_command(
        label="24小时制 (HH:MM:SS)", command=lambda: root.insert_time("24h")
    )
    time_submenu.add_command(
        label="12小时制 (HH:MM:SS AM/PM)", command=lambda: root.insert_time("12h")
    )
    time_submenu.add_command(
        label="24小时制 (HH:MM)", command=lambda: root.insert_time("24h_short")
    )
    time_submenu.add_command(
        label="12小时制 (HH:MM AM/PM)", command=lambda: root.insert_time("12h_short")
    )

    # 日期时间相关插入
    datetime_submenu = tk.Menu(insert_submenu, tearoff=0, font=menu_font_tuple)
    insert_submenu.add_cascade(label="日期时间", menu=datetime_submenu)
    datetime_submenu.add_command(
        label="YYYY-MM-DD HH:MM:SS", command=lambda: root.insert_datetime("ymd_24h")
    )
    datetime_submenu.add_command(
        label="YYYY-MM-DD HH:MM:SS AM/PM",
        command=lambda: root.insert_datetime("ymd_12h"),
    )
    datetime_submenu.add_command(
        label="YYYY/MM/DD HH:MM:SS",
        command=lambda: root.insert_datetime("ymd_slash_24h"),
    )
    datetime_submenu.add_command(
        label="YYYY/MM/DD HH:MM:SS AM/PM",
        command=lambda: root.insert_datetime("ymd_slash_12h"),
    )

    # 其他插入
    other_submenu = tk.Menu(insert_submenu, tearoff=0, font=menu_font_tuple)
    insert_submenu.add_cascade(label="其他", menu=other_submenu)
    other_submenu.add_command(label="时间戳", command=lambda: root.insert_timestamp())

    # UUID子菜单
    uuid_submenu = tk.Menu(other_submenu, tearoff=0, font=menu_font_tuple)
    other_submenu.add_cascade(label="UUID", menu=uuid_submenu)
    uuid_submenu.add_command(
        label="UUID v4 (标准格式)", command=lambda: root.insert_uuid_v4()
    )
    uuid_submenu.add_command(
        label="无连字符UUID", command=lambda: root.insert_uuid_no_hyphens()
    )
    uuid_submenu.add_command(
        label="大写UUID", command=lambda: root.insert_uuid_uppercase()
    )
    uuid_submenu.add_command(
        label="大写无连字符UUID",
        command=lambda: root.insert_uuid_uppercase_no_hyphens(),
    )
    uuid_submenu.add_command(
        label="带花括号的UUID", command=lambda: root.insert_uuid_with_braces()
    )
    uuid_submenu.add_command(
        label="带花括号的大写UUID",
        command=lambda: root.insert_uuid_uppercase_with_braces(),
    )
    uuid_submenu.add_command(
        label="Base64编码UUID", command=lambda: root.insert_uuid_base64()
    )
    uuid_submenu.add_command(
        label="URN格式UUID", command=lambda: root.insert_uuid_urn()
    )
    uuid_submenu.add_command(
        label="UUID v1 (基于时间)", command=lambda: root.insert_uuid_v1()
    )

    # 特殊字符子菜单
    special_char_submenu = tk.Menu(insert_submenu, tearoff=0, font=menu_font_tuple)
    insert_submenu.add_cascade(label="特殊字符", menu=special_char_submenu)

    # 常用特殊字符子菜单
    common_special_submenu = tk.Menu(
        special_char_submenu, tearoff=0, font=menu_font_tuple
    )
    special_char_submenu.add_cascade(label="常用特殊字符", menu=common_special_submenu)
    common_special_submenu.add_command(
        label="版权符号 ©", command=lambda: root.insert_copyright_symbol()
    )
    common_special_submenu.add_command(
        label="商标符号 ®", command=lambda: root.insert_trademark_symbol()
    )
    common_special_submenu.add_command(
        label="注册商标符号 ™",
        command=lambda: root.insert_registered_trademark_symbol(),
    )
    common_special_submenu.add_command(
        label="度数符号 °", command=lambda: root.insert_degree_symbol()
    )

    # 货币符号子菜单
    currency_submenu = tk.Menu(special_char_submenu, tearoff=0, font=menu_font_tuple)
    special_char_submenu.add_cascade(label="货币符号", menu=currency_submenu)
    currency_submenu.add_command(
        label="欧元符号 €", command=lambda: root.insert_euro_symbol()
    )
    currency_submenu.add_command(
        label="英镑符号 £", command=lambda: root.insert_pound_symbol()
    )
    currency_submenu.add_command(
        label="日元符号 ¥", command=lambda: root.insert_yen_symbol()
    )

    # 标点符号子菜单
    punctuation_submenu = tk.Menu(special_char_submenu, tearoff=0, font=menu_font_tuple)
    special_char_submenu.add_cascade(label="标点符号", menu=punctuation_submenu)
    punctuation_submenu.add_command(
        label="章节符号 §", command=lambda: root.insert_section_symbol()
    )
    punctuation_submenu.add_command(
        label="段落符号 ¶", command=lambda: root.insert_paragraph_symbol()
    )
    punctuation_submenu.add_command(
        label="省略号 …", command=lambda: root.insert_ellipsis_symbol()
    )
    punctuation_submenu.add_command(
        label="匕首符号 †", command=lambda: root.insert_dagger_symbol()
    )
    punctuation_submenu.add_command(
        label="双匕首符号 ‡", command=lambda: root.insert_double_dagger_symbol()
    )
    punctuation_submenu.add_command(
        label="圆点符号 •", command=lambda: root.insert_bullet_symbol()
    )

    # 数学符号子菜单
    math_symbol_submenu = tk.Menu(insert_submenu, tearoff=0, font=menu_font_tuple)
    insert_submenu.add_cascade(label="数学符号", menu=math_symbol_submenu)

    # 常用数学符号子菜单
    common_math_submenu = tk.Menu(math_symbol_submenu, tearoff=0, font=menu_font_tuple)
    math_symbol_submenu.add_cascade(label="常用数学符号", menu=common_math_submenu)
    common_math_submenu.add_command(
        label="正负号 ±", command=lambda: root.insert_plus_minus_symbol()
    )
    common_math_submenu.add_command(
        label="不等号 ≠", command=lambda: root.insert_not_equal_symbol()
    )
    common_math_submenu.add_command(
        label="小于等于号 ≤", command=lambda: root.insert_less_than_or_equal_symbol()
    )
    common_math_submenu.add_command(
        label="大于等于号 ≥", command=lambda: root.insert_greater_than_or_equal_symbol()
    )
    common_math_submenu.add_command(
        label="无穷符号 ∞", command=lambda: root.insert_infinity_symbol()
    )

    # 微积分符号子菜单
    calculus_submenu = tk.Menu(math_symbol_submenu, tearoff=0, font=menu_font_tuple)
    math_symbol_submenu.add_cascade(label="微积分符号", menu=calculus_submenu)
    calculus_submenu.add_command(
        label="求和符号 ∑", command=lambda: root.insert_summation_symbol()
    )
    calculus_submenu.add_command(
        label="乘积符号 ∏", command=lambda: root.insert_product_symbol()
    )
    calculus_submenu.add_command(
        label="积分符号 ∫", command=lambda: root.insert_integral_symbol()
    )
    calculus_submenu.add_command(
        label="偏导数符号 ∂", command=lambda: root.insert_partial_derivative_symbol()
    )
    calculus_submenu.add_command(
        label="梯度符号 ∇", command=lambda: root.insert_nabla_symbol()
    )

    # 根号符号子菜单
    root_submenu = tk.Menu(math_symbol_submenu, tearoff=0, font=menu_font_tuple)
    math_symbol_submenu.add_cascade(label="根号符号", menu=root_submenu)
    root_submenu.add_command(
        label="平方根符号 √", command=lambda: root.insert_square_root_symbol()
    )
    root_submenu.add_command(
        label="立方根符号 ∛", command=lambda: root.insert_cubic_root_symbol()
    )
    root_submenu.add_command(
        label="四次根符号 ∜", command=lambda: root.insert_fourth_root_symbol()
    )

    # 希腊字母子菜单
    greek_submenu = tk.Menu(math_symbol_submenu, tearoff=0, font=menu_font_tuple)
    math_symbol_submenu.add_cascade(label="希腊字母", menu=greek_submenu)

    # 小写希腊字母子菜单
    greek_lower_submenu = tk.Menu(greek_submenu, tearoff=0, font=menu_font_tuple)
    greek_submenu.add_cascade(label="小写希腊字母", menu=greek_lower_submenu)
    greek_lower_submenu.add_command(
        label="α", command=lambda: root.insert_alpha_symbol()
    )
    greek_lower_submenu.add_command(
        label="β", command=lambda: root.insert_beta_symbol()
    )
    greek_lower_submenu.add_command(
        label="γ", command=lambda: root.insert_gamma_symbol()
    )
    greek_lower_submenu.add_command(
        label="δ", command=lambda: root.insert_delta_symbol()
    )
    greek_lower_submenu.add_command(
        label="ε", command=lambda: root.insert_epsilon_symbol()
    )
    greek_lower_submenu.add_command(
        label="ζ", command=lambda: root.insert_zeta_symbol()
    )
    greek_lower_submenu.add_command(label="η", command=lambda: root.insert_eta_symbol())
    greek_lower_submenu.add_command(
        label="θ", command=lambda: root.insert_theta_symbol()
    )
    greek_lower_submenu.add_command(
        label="ι", command=lambda: root.insert_iota_symbol()
    )
    greek_lower_submenu.add_command(
        label="κ", command=lambda: root.insert_kappa_symbol()
    )
    greek_lower_submenu.add_command(
        label="λ", command=lambda: root.insert_lambda_symbol()
    )
    greek_lower_submenu.add_command(label="μ", command=lambda: root.insert_mu_symbol())
    greek_lower_submenu.add_command(label="ν", command=lambda: root.insert_nu_symbol())
    greek_lower_submenu.add_command(label="ξ", command=lambda: root.insert_xi_symbol())
    greek_lower_submenu.add_command(
        label="ο", command=lambda: root.insert_omicron_symbol()
    )
    greek_lower_submenu.add_command(label="π", command=lambda: root.insert_pi_symbol())
    greek_lower_submenu.add_command(label="ρ", command=lambda: root.insert_rho_symbol())
    greek_lower_submenu.add_command(
        label="σ", command=lambda: root.insert_sigma_symbol()
    )
    greek_lower_submenu.add_command(label="τ", command=lambda: root.insert_tau_symbol())
    greek_lower_submenu.add_command(
        label="υ", command=lambda: root.insert_upsilon_symbol()
    )
    greek_lower_submenu.add_command(label="φ", command=lambda: root.insert_phi_symbol())
    greek_lower_submenu.add_command(label="χ", command=lambda: root.insert_chi_symbol())
    greek_lower_submenu.add_command(label="ψ", command=lambda: root.insert_psi_symbol())
    greek_lower_submenu.add_command(
        label="ω", command=lambda: root.insert_omega_symbol()
    )

    # 大写希腊字母子菜单
    greek_upper_submenu = tk.Menu(greek_submenu, tearoff=0, font=menu_font_tuple)
    greek_submenu.add_cascade(label="大写希腊字母", menu=greek_upper_submenu)
    greek_upper_submenu.add_command(
        label="Α", command=lambda: root.insert_capital_alpha_symbol()
    )
    greek_upper_submenu.add_command(
        label="Β", command=lambda: root.insert_capital_beta_symbol()
    )
    greek_upper_submenu.add_command(
        label="Γ", command=lambda: root.insert_capital_gamma_symbol()
    )
    greek_upper_submenu.add_command(
        label="Δ", command=lambda: root.insert_capital_delta_symbol()
    )
    greek_upper_submenu.add_command(
        label="Ε", command=lambda: root.insert_capital_epsilon_symbol()
    )
    greek_upper_submenu.add_command(
        label="Ζ", command=lambda: root.insert_capital_zeta_symbol()
    )
    greek_upper_submenu.add_command(
        label="Η", command=lambda: root.insert_capital_eta_symbol()
    )
    greek_upper_submenu.add_command(
        label="Θ", command=lambda: root.insert_capital_theta_symbol()
    )
    greek_upper_submenu.add_command(
        label="Ι", command=lambda: root.insert_capital_iota_symbol()
    )
    greek_upper_submenu.add_command(
        label="Κ", command=lambda: root.insert_capital_kappa_symbol()
    )
    greek_upper_submenu.add_command(
        label="Λ", command=lambda: root.insert_capital_lambda_symbol()
    )
    greek_upper_submenu.add_command(
        label="Μ", command=lambda: root.insert_capital_mu_symbol()
    )
    greek_upper_submenu.add_command(
        label="Ν", command=lambda: root.insert_capital_nu_symbol()
    )
    greek_upper_submenu.add_command(
        label="Ξ", command=lambda: root.insert_capital_xi_symbol()
    )
    greek_upper_submenu.add_command(
        label="Ο", command=lambda: root.insert_capital_omicron_symbol()
    )
    greek_upper_submenu.add_command(
        label="Π", command=lambda: root.insert_capital_pi_symbol()
    )
    greek_upper_submenu.add_command(
        label="Ρ", command=lambda: root.insert_capital_rho_symbol()
    )
    greek_upper_submenu.add_command(
        label="Σ", command=lambda: root.insert_capital_sigma_symbol()
    )
    greek_upper_submenu.add_command(
        label="Τ", command=lambda: root.insert_capital_tau_symbol()
    )
    greek_upper_submenu.add_command(
        label="Υ", command=lambda: root.insert_capital_upsilon_symbol()
    )
    greek_upper_submenu.add_command(
        label="Φ", command=lambda: root.insert_capital_phi_symbol()
    )
    greek_upper_submenu.add_command(
        label="Χ", command=lambda: root.insert_capital_chi_symbol()
    )
    greek_upper_submenu.add_command(
        label="Ψ", command=lambda: root.insert_capital_psi_symbol()
    )
    greek_upper_submenu.add_command(
        label="Ω", command=lambda: root.insert_capital_omega_symbol()
    )

    # 颜色代码子菜单
    color_code_submenu = tk.Menu(insert_submenu, tearoff=0, font=menu_font_tuple)
    insert_submenu.add_cascade(label="颜色代码", menu=color_code_submenu)
    color_code_submenu.add_command(
        label="HEX颜色代码选择器", command=lambda: root.insert_hex_color_picker()
    )
    color_code_submenu.add_command(
        label="RGB颜色代码选择器", command=lambda: root.insert_rgb_color_picker()
    )

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
