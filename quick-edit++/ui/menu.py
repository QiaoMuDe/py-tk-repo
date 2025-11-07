#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
菜单栏界面模块
"""

import tkinter as tk
import customtkinter as ctk
from ui.dialogs.font_dialog import show_font_dialog
from config.config_manager import config_manager

def create_menu(root):
    """创建菜单栏"""
    # 从配置管理器获取菜单字体设置
    menu_font = config_manager.get_font_config("menu_bar")
    menu_font_family = menu_font.get("font", "Microsoft YaHei UI")
    menu_font_size = menu_font.get("font_size", 12)
    menu_font_bold = menu_font.get("font_bold", False)
    
    # 创建字体元组，用于所有菜单项
    menu_font_tuple = (menu_font_family, menu_font_size, "bold" if menu_font_bold else "normal")
    
    # 创建主菜单
    main_menu = tk.Menu(root, font=menu_font_tuple)
    
    # 创建文件菜单
    file_menu = tk.Menu(main_menu, tearoff=0, font=menu_font_tuple)
    
    # 第一组：基本文件操作
    file_menu.add_command(label="新建", command=lambda: print("新建文件"))
    file_menu.add_command(label="打开", command=lambda: print("打开文件"))
    file_menu.add_command(label="保存", command=lambda: print("保存文件"))
    file_menu.add_command(label="另存为", command=lambda: print("另存为"))
    file_menu.add_command(label="关闭文件", command=lambda: print("关闭当前文件"))
    
    # 分隔符
    file_menu.add_separator()
    
    # 第二组：文件编码
    # 创建文件编码子菜单
    encoding_submenu = tk.Menu(file_menu, tearoff=0, font=menu_font_tuple)
    
    # 获取当前编码设置
    current_encoding = config_manager.get("file.default_encoding", "UTF-8")
    encoding_options = ["UTF-8", "GBK", "UTF-16", "ASCII"]
    
    for encoding in encoding_options:
        encoding_submenu.add_command(
            label=encoding, 
            command=lambda enc=encoding: set_file_encoding(enc)
        )
    
    encoding_submenu.add_separator()
    encoding_submenu.add_command(label="其他编码...", command=lambda: print("选择其他编码"))
    
    file_menu.add_cascade(label="文件编码", menu=encoding_submenu)

    # 创建换行符子菜单
    newline_submenu = tk.Menu(file_menu, tearoff=0, font=menu_font_tuple)
    
    # 获取当前换行符设置
    current_newline = config_manager.get("file.default_line_ending", "CRLF")
    newline_options = [
        ("Windows (CRLF)", "CRLF"),
        ("Linux/Unix (LF)", "LF"),
        ("Mac (CR)", "CR")
    ]
    
    for label, value in newline_options:
        newline_submenu.add_command(
            label=label, 
            command=lambda nl=value: set_file_line_ending(nl)
        )
    
    file_menu.add_cascade(label="换行符", menu=newline_submenu)
    
    # 分隔符
    file_menu.add_separator()
    
    # 第三组：文件选项
    file_menu.add_command(label="打开文件所在目录", command=lambda: print("打开文件所在目录"))
    file_menu.add_checkbutton(label="只读模式", command=lambda: print("切换只读模式"))
    
    # 分隔符
    file_menu.add_separator()
    
    # 第四组：退出程序
    file_menu.add_command(label="退出", command=root._on_closing)
    
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
    
    # 创建格式菜单
    format_menu = tk.Menu(main_menu, tearoff=0, font=menu_font_tuple)
    format_menu.add_command(label="字体", command=lambda: show_font_dialog(root.text_area))
    format_menu.add_command(label="背景色", command=lambda: print("设置背景色"))
    
    # 将格式菜单添加到主菜单
    main_menu.add_cascade(label="格式", menu=format_menu)
    
    # 创建主题菜单
    theme_menu = tk.Menu(main_menu, tearoff=0, font=menu_font_tuple)
    
    # 外观模式分组（3种模式）
    # 获取当前外观模式
    current_theme = config_manager.get("app.theme_mode", "system")
    theme_options = [
        ("浅色模式", "light"),
        ("深色模式", "dark"),
        ("跟随系统", "system")
    ]
    
    for label, value in theme_options:
        theme_menu.add_command(
            label=label, 
            command=lambda tm=value: set_theme_mode(tm)
        )
    
    theme_menu.add_separator()
    
    # 主题颜色分组（3种主题）
    # 获取当前颜色主题
    current_color = config_manager.get("app.color_theme", "blue")
    color_options = [
        ("蓝色主题", "blue"),
        ("绿色主题", "green"),
        ("深蓝色主题", "dark-blue")
    ]
    
    for label, value in color_options:
        theme_menu.add_command(
            label=label, 
            command=lambda ct=value: set_color_theme(ct)
        )
    
    # 将主题菜单添加到主菜单
    main_menu.add_cascade(label="主题", menu=theme_menu)
    
    # 创建设置菜单
    settings_menu = tk.Menu(main_menu, tearoff=0, font=menu_font_tuple)
    
    # 第一组：界面设置
    # 获取工具栏显示状态
    show_toolbar = config_manager.get("toolbar.show_toolbar", True)
    settings_menu.add_checkbutton(
        label="显示工具栏", 
        command=lambda: toggle_toolbar()
    )
    
    # 创建窗口标题显示子菜单
    title_display_submenu = tk.Menu(settings_menu, tearoff=0, font=menu_font_tuple)
    title_display_submenu.add_checkbutton(label="显示文件名", command=lambda: print("切换文件名显示"))
    title_display_submenu.add_checkbutton(label="显示文件路径", command=lambda: print("切换文件路径显示"))
    title_display_submenu.add_checkbutton(label="显示状态信息", command=lambda: print("切换状态信息显示"))
    settings_menu.add_cascade(label="窗口标题显示", menu=title_display_submenu)
    settings_menu.add_separator()
    
    # 第二组：编辑设置
    # 获取自动换行设置
    auto_wrap = config_manager.get("text_editor.auto_wrap", True)
    settings_menu.add_checkbutton(
        label="启用自动换行", 
        command=lambda: toggle_auto_wrap()
    )
    
    # 创建制表符设置子菜单
    tab_settings_submenu = tk.Menu(settings_menu, tearoff=0, font=menu_font_tuple)
    
    # 获取当前制表符宽度
    tab_width = config_manager.get("text_editor.tab_width", 4)
    tab_options = [2, 4, 8]
    
    for width in tab_options:
        tab_settings_submenu.add_command(
            label=f"制表符宽度: {width}", 
            command=lambda w=width: set_tab_width(w)
        )
    
    tab_settings_submenu.add_separator()
    
    # 获取空格代替制表符设置
    use_spaces = config_manager.get("text_editor.use_spaces_for_tabs", False)
    tab_settings_submenu.add_checkbutton(
        label="使用空格代替制表符", 
        command=lambda: toggle_use_spaces()
    )
    
    settings_menu.add_cascade(label="制表符设置", menu=tab_settings_submenu)
    
    # 获取快捷插入设置
    quick_insert = config_manager.get("text_editor.quick_insert_enabled", True)
    settings_menu.add_checkbutton(
        label="启用快捷插入(@)", 
        command=lambda: toggle_quick_insert()
    )
    settings_menu.add_separator()
    
    # 第三组：保存设置
    # 获取自动保存设置
    auto_save = config_manager.get("saving.auto_save", True)
    settings_menu.add_checkbutton(
        label="启用自动保存", 
        command=lambda: toggle_auto_save()
    )
    
    # 创建自动保存间隔子菜单
    autosave_submenu = tk.Menu(settings_menu, tearoff=0, font=menu_font_tuple)
    
    # 获取当前自动保存间隔
    auto_save_interval = config_manager.get("saving.auto_save_interval", 60)
    interval_options = [
        ("30秒", 30),
        ("1分钟", 60),
        ("5分钟", 300),
        ("10分钟", 600)
    ]
    
    for label, value in interval_options:
        autosave_submenu.add_command(
            label=label, 
            command=lambda interval=value: set_auto_save_interval(interval)
        )
    
    settings_menu.add_cascade(label="自动保存间隔", menu=autosave_submenu)
    
    # 获取备份设置
    backup_enabled = config_manager.get("saving.backup_enabled", True)
    settings_menu.add_checkbutton(
        label="启用副本备份", 
        command=lambda: toggle_backup()
    )
    settings_menu.add_separator()
    
    # 第四组：配置管理
    settings_menu.add_command(label="查看配置", command=lambda: print("查看当前配置"))
    settings_menu.add_command(label="重置设置", command=lambda: print("重置所有设置"))
    
    # 将设置菜单添加到主菜单
    main_menu.add_cascade(label="设置", menu=settings_menu)
    
    # 创建帮助菜单
    help_menu = tk.Menu(main_menu, tearoff=0, font=menu_font_tuple)
    help_menu.add_command(label="文档统计信息", command=lambda: print("显示文档统计信息"))
    help_menu.add_command(label="关于", command=lambda: print("显示关于信息"))
    
    # 将帮助菜单添加到主菜单
    main_menu.add_cascade(label="帮助", menu=help_menu)
    
    # 将主菜单配置到根窗口
    root.config(menu=main_menu)
    
    return main_menu


def set_file_encoding(encoding):
    """设置文件编码"""
    config_manager.set("file.default_encoding", encoding)
    config_manager.save_config()
    print(f"文件编码已设置为: {encoding}")


def set_file_line_ending(line_ending):
    """设置文件换行符"""
    config_manager.set("file.default_line_ending", line_ending)
    config_manager.save_config()
    print(f"文件换行符已设置为: {line_ending}")


# 注意：已移除光标样式设置函数，使用系统默认光标样式


def set_theme_mode(mode):
    """设置主题模式"""
    config_manager.set("app.theme_mode", mode)
    config_manager.save_config()
    ctk.set_appearance_mode(mode)
    print(f"主题模式已设置为: {mode}")


def set_color_theme(theme):
    """设置颜色主题"""
    config_manager.set("app.color_theme", theme)
    config_manager.save_config()
    ctk.set_default_color_theme(theme)
    print(f"颜色主题已设置为: {theme}")


def toggle_toolbar():
    """切换工具栏显示"""
    current = config_manager.get("toolbar.show_toolbar", True)
    config_manager.set("toolbar.show_toolbar", not current)
    config_manager.save_config()
    print(f"工具栏显示已设置为: {not current}")


def toggle_auto_wrap():
    """切换自动换行"""
    current = config_manager.get("text_editor.auto_wrap", True)
    config_manager.set("text_editor.auto_wrap", not current)
    config_manager.save_config()
    print(f"自动换行已设置为: {not current}")


def set_tab_width(width):
    """设置制表符宽度"""
    config_manager.set("text_editor.tab_width", width)
    config_manager.save_config()
    print(f"制表符宽度已设置为: {width}")


def toggle_use_spaces():
    """切换使用空格代替制表符"""
    current = config_manager.get("text_editor.use_spaces_for_tabs", False)
    config_manager.set("text_editor.use_spaces_for_tabs", not current)
    config_manager.save_config()
    print(f"使用空格代替制表符已设置为: {not current}")


def toggle_quick_insert():
    """切换快捷插入"""
    current = config_manager.get("text_editor.quick_insert_enabled", True)
    config_manager.set("text_editor.quick_insert_enabled", not current)
    config_manager.save_config()
    print(f"快捷插入已设置为: {not current}")


def toggle_auto_save():
    """切换自动保存"""
    current = config_manager.get("saving.auto_save", True)
    config_manager.set("saving.auto_save", not current)
    config_manager.save_config()
    print(f"自动保存已设置为: {not current}")


def set_auto_save_interval(interval):
    """设置自动保存间隔"""
    config_manager.set("saving.auto_save_interval", interval)
    config_manager.save_config()
    print(f"自动保存间隔已设置为: {interval}秒")


def toggle_backup():
    """切换备份"""
    current = config_manager.get("saving.backup_enabled", True)
    config_manager.set("saving.backup_enabled", not current)
    config_manager.save_config()
    print(f"备份已设置为: {not current}")


def apply_menu_font(font_config=None):
    """
    应用菜单字体设置
    
    Args:
        font_config (dict, optional): 字体配置字典，包含font, font_size, font_bold
                                    如果为None，则从配置管理器获取当前配置
    """
    # 如果没有提供字体配置，则从配置管理器获取
    if font_config is None:
        font_config = config_manager.get_font_config("menu_bar")
    
    # 保存字体配置到配置管理器
    config_manager.set_font_config("menu_bar", font_config)
    config_manager.save_config()
    
    # 构建字体元组
    font_family = font_config.get("font", "Microsoft YaHei UI")
    font_size = font_config.get("font_size", 12)
    font_bold = font_config.get("font_bold", False)
    font_tuple = (font_family, font_size, "bold" if font_bold else "normal")
    
    print(f"菜单字体已更新: {font_family} {font_size}pt {'加粗' if font_bold else '常规'}")
    
    # 注意：由于tkinter菜单在创建后无法直接修改字体，
    # 这里我们只是保存了配置，实际应用需要重启应用程序
    print("菜单字体设置将在下次启动应用程序时生效")