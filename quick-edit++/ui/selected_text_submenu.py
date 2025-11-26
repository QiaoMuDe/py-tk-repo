#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk

"""
选中文本子菜单
"""


def create_selected_text_submenu(
    selected_text_submenu, root, menu_font_tuple, return_instance=False
):
    """
    创建选中内容操作菜单项

    Args:
        parent_menu (tkinter.Menu): 父菜单实例
        root: 主窗口实例
        menu_font_tuple (tuple): 菜单字体元组
        return_instance (bool): 是否返回实例
    """
    # 在选中文本操作下创建各种子菜单
    text_processing_submenu = tk.Menu(
        selected_text_submenu, tearoff=0, font=menu_font_tuple
    )
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

    # 创建基本转换子菜单
    basic_conversion_submenu = tk.Menu(
        text_processing_submenu, tearoff=0, font=menu_font_tuple
    )
    text_processing_submenu.add_cascade(label="基本转换", menu=basic_conversion_submenu)

    # 添加基本转换菜单项
    basic_conversion_submenu.add_command(
        label="下划线转驼峰", command=lambda: root.snake_to_camel()
    )
    basic_conversion_submenu.add_command(
        label="驼峰转下划线", command=lambda: root.camel_to_snake()
    )

    # 创建扩展转换子菜单
    extended_conversion_submenu = tk.Menu(
        text_processing_submenu, tearoff=0, font=menu_font_tuple
    )
    text_processing_submenu.add_cascade(
        label="扩展转换", menu=extended_conversion_submenu
    )

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
    case_conversion_submenu = tk.Menu(
        text_processing_submenu, tearoff=0, font=menu_font_tuple
    )
    text_processing_submenu.add_cascade(
        label="大小写转换", menu=case_conversion_submenu
    )

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
    separator_conversion_submenu = tk.Menu(
        text_processing_submenu, tearoff=0, font=menu_font_tuple
    )
    text_processing_submenu.add_cascade(
        label="分隔符转换", menu=separator_conversion_submenu
    )

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
    programming_convention_submenu = tk.Menu(
        text_processing_submenu, tearoff=0, font=menu_font_tuple
    )
    text_processing_submenu.add_cascade(
        label="编程规范", menu=programming_convention_submenu
    )

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
    database_conversion_submenu = tk.Menu(
        text_processing_submenu, tearoff=0, font=menu_font_tuple
    )
    text_processing_submenu.add_cascade(
        label="数据库相关", menu=database_conversion_submenu
    )

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
    line_processing_submenu = tk.Menu(
        selected_text_submenu, tearoff=0, font=menu_font_tuple
    )
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
    reverse_submenu.add_command(label="行反转", command=lambda: root.reverse_lines())

    # 创建格式化子菜单
    formatting_submenu = tk.Menu(selected_text_submenu, tearoff=0, font=menu_font_tuple)
    selected_text_submenu.add_cascade(label="格式化", menu=formatting_submenu)

    # 创建JSON子菜单
    json_submenu = tk.Menu(formatting_submenu, tearoff=0, font=menu_font_tuple)
    formatting_submenu.add_cascade(label="JSON", menu=json_submenu)

    # 添加JSON菜单项
    json_submenu.add_command(label="格式化JSON", command=lambda: root.format_json())
    json_submenu.add_command(label="压缩JSON", command=lambda: root.compress_json())

    # 创建CSV格式化子菜单
    csv_submenu = tk.Menu(formatting_submenu, tearoff=0, font=menu_font_tuple)
    formatting_submenu.add_cascade(label="CSV", menu=csv_submenu)
    csv_submenu.add_command(
        label="格式化CSV", command=lambda: root.format_csv(compress=False)
    )
    csv_submenu.add_command(
        label="压缩CSV", command=lambda: root.format_csv(compress=True)
    )

    # 创建SQL格式化子菜单
    sql_submenu = tk.Menu(formatting_submenu, tearoff=0, font=menu_font_tuple)
    formatting_submenu.add_cascade(label="SQL", menu=sql_submenu)

    # 添加SQL菜单项
    sql_submenu.add_command(label="关键字大写", command=lambda: root.format_sql_upper())
    sql_submenu.add_command(label="关键字小写", command=lambda: root.format_sql_lower())
    sql_submenu.add_command(label="格式化SQL", command=lambda: root.format_sql())
    sql_submenu.add_command(label="压缩SQL", command=lambda: root.compress_sql())

    # 创建HTML格式化子菜单
    html_submenu = tk.Menu(formatting_submenu, tearoff=0, font=menu_font_tuple)
    formatting_submenu.add_cascade(label="HTML", menu=html_submenu)

    # 添加HTML菜单项
    html_submenu.add_command(label="格式化HTML", command=lambda: root.format_html())
    html_submenu.add_command(label="压缩HTML", command=lambda: root.compress_html())

    # 创建CSS格式化子菜单
    css_submenu = tk.Menu(formatting_submenu, tearoff=0, font=menu_font_tuple)
    formatting_submenu.add_cascade(label="CSS", menu=css_submenu)

    # 添加CSS菜单项
    css_submenu.add_command(label="格式化CSS", command=lambda: root.format_css())
    css_submenu.add_command(label="压缩CSS", command=lambda: root.compress_css())

    # 创建JavaScript格式化子菜单
    js_submenu = tk.Menu(formatting_submenu, tearoff=0, font=menu_font_tuple)
    formatting_submenu.add_cascade(label="JavaScript", menu=js_submenu)

    # 添加JavaScript菜单项
    js_submenu.add_command(
        label="格式化JavaScript", command=lambda: root.format_javascript()
    )
    js_submenu.add_command(
        label="压缩JavaScript", command=lambda: root.compress_javascript()
    )

    # 添加其他格式化菜单项
    formatting_submenu.add_command(label="格式化XML", command=lambda: root.format_xml())

    formatting_submenu.add_command(label="格式化INI", command=lambda: root.format_ini())
    formatting_submenu.add_command(
        label="格式化Python", command=lambda: root.format_python()
    )
    formatting_submenu.add_command(
        label="格式化YAML", command=lambda: root.format_yaml()
    )

    # 创建注释处理子菜单
    comment_processing_submenu = tk.Menu(
        selected_text_submenu, tearoff=0, font=menu_font_tuple
    )
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
    encoding_decoding_submenu = tk.Menu(
        selected_text_submenu, tearoff=0, font=menu_font_tuple
    )
    selected_text_submenu.add_cascade(label="编码解码", menu=encoding_decoding_submenu)

    # 添加编码解码菜单项
    encoding_decoding_submenu.add_command(
        label="Base64编码", command=lambda: root.base64_encode()
    )
    encoding_decoding_submenu.add_command(
        label="Base64解码", command=lambda: root.base64_decode()
    )

    # 根据参数选择返回菜单项
    if return_instance:
        return selected_text_submenu
