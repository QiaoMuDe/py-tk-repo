#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
菜单栏界面模块
"""

import customtkinter as ctk
from ui.dialogs.font_dialog import show_font_dialog


def on_font_confirm(font_config, text_widget=None):
    """
    字体设置确认回调函数
    
    Args:
        font_config: 字体配置字典，包含family和size
        text_widget: 文本框组件引用
    """
    # 这里实现字体设置的应用逻辑
    try:
        # 打印字体设置信息
        print(f"应用字体设置: {font_config}")
        
        # 使用CTkFont创建字体对象并应用到文本框
        if text_widget:
            from customtkinter import CTkFont
            font_obj = CTkFont(family=font_config.get("family", "Microsoft YaHei"), 
                              size=font_config.get("size", 12))
            text_widget.configure(font=font_obj)
            print(f"已成功应用字体到文本框: {font_config}")
    except Exception as e:
        print(f"应用字体设置时出错: {e}")



def create_menu(root, main_window=None):
    """创建菜单栏"""
    # 由于customtkinter没有直接的菜单栏组件，我们需要使用tkinter的菜单
    # 这里我们创建一个隐藏的tkinter菜单栏
    import tkinter as tk
    
    # 创建主菜单
    main_menu = tk.Menu(root, font=("Microsoft YaHei", 10))
    
    # 创建文件菜单
    file_menu = tk.Menu(main_menu, tearoff=0, font=("Microsoft YaHei", 10))
    
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
    encoding_submenu = tk.Menu(file_menu, tearoff=0, font=("Microsoft YaHei", 10))
    encoding_submenu.add_command(label="UTF-8", command=lambda: print("设置编码为UTF-8"))
    encoding_submenu.add_command(label="GBK", command=lambda: print("设置编码为GBK"))
    encoding_submenu.add_command(label="UTF-16", command=lambda: print("设置编码为UTF-16"))
    encoding_submenu.add_command(label="ASCII", command=lambda: print("设置编码为ASCII"))
    encoding_submenu.add_separator()
    encoding_submenu.add_command(label="其他编码...", command=lambda: print("选择其他编码"))
    
    file_menu.add_cascade(label="文件编码", menu=encoding_submenu)

    # 创建换行符子菜单
    newline_submenu = tk.Menu(file_menu, tearoff=0, font=("Microsoft YaHei", 10))
    newline_submenu.add_command(label="Windows (CRLF)", command=lambda: print("设置换行符为CRLF"))
    newline_submenu.add_command(label="Linux/Unix (LF)", command=lambda: print("设置换行符为LF"))
    newline_submenu.add_command(label="Mac (CR)", command=lambda: print("设置换行符为CR"))
    
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
    edit_menu = tk.Menu(main_menu, tearoff=0, font=("Microsoft YaHei", 10))
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
    copy_to_clipboard_submenu = tk.Menu(edit_menu, tearoff=0, font=("Microsoft YaHei", 10))
    edit_menu.add_cascade(label="复制到剪贴板", menu=copy_to_clipboard_submenu)
    
    # 创建选中文本操作子菜单
    selected_text_submenu = tk.Menu(edit_menu, tearoff=0, font=("Microsoft YaHei", 10))
    edit_menu.add_cascade(label="选中文本操作", menu=selected_text_submenu)
    
    # 创建插入子菜单
    insert_submenu = tk.Menu(edit_menu, tearoff=0, font=("Microsoft YaHei", 10))
    edit_menu.add_cascade(label="插入", menu=insert_submenu)
    
    # 将编辑菜单添加到主菜单
    main_menu.add_cascade(label="编辑", menu=edit_menu)
    
    # 创建格式菜单
    format_menu = tk.Menu(main_menu, tearoff=0, font=("Microsoft YaHei", 10))
    format_menu.add_command(label="字体", command=lambda: show_font_dialog(root, main_window.text_area if hasattr(main_window, 'text_area') else None, on_font_confirm))
    format_menu.add_command(label="背景色", command=lambda: print("设置背景色"))
    format_menu.add_separator()
    format_menu.add_command(label="加粗", command=lambda: print("设置文字加粗"))
    format_menu.add_command(label="斜体", command=lambda: print("设置文字斜体"))
    format_menu.add_command(label="下划线", command=lambda: print("设置文字下划线"))
    format_menu.add_command(label="删除线", command=lambda: print("设置文字删除线"))
    format_menu.add_separator()
    # 创建光标样式子菜单
    cursor_style_submenu = tk.Menu(format_menu, tearoff=0, font=("Microsoft YaHei", 10))
    format_menu.add_cascade(label="光标样式", menu=cursor_style_submenu)
    
    # 将格式菜单添加到主菜单
    main_menu.add_cascade(label="格式", menu=format_menu)
    
    # 创建主题菜单
    theme_menu = tk.Menu(main_menu, tearoff=0, font=("Microsoft YaHei", 10))
    
    # 外观模式分组（3种模式）
    theme_menu.add_command(label="浅色模式", command=lambda: ctk.set_appearance_mode("light"))
    theme_menu.add_command(label="深色模式", command=lambda: ctk.set_appearance_mode("dark"))
    theme_menu.add_command(label="跟随系统", command=lambda: ctk.set_appearance_mode("system"))
    theme_menu.add_separator()
    
    # 主题颜色分组（3种主题）
    theme_menu.add_command(label="蓝色主题", command=lambda: ctk.set_default_color_theme("blue"))
    theme_menu.add_command(label="绿色主题", command=lambda: ctk.set_default_color_theme("green"))
    theme_menu.add_command(label="深蓝色主题", command=lambda: ctk.set_default_color_theme("dark-blue"))
    
    # 将主题菜单添加到主菜单
    main_menu.add_cascade(label="主题", menu=theme_menu)
    
    # 创建设置菜单
    settings_menu = tk.Menu(main_menu, tearoff=0, font=("Microsoft YaHei", 10))
    
    # 第一组：界面设置
    settings_menu.add_checkbutton(label="显示工具栏", command=lambda: print("切换工具栏显示"))
    
    # 创建窗口标题显示子菜单
    title_display_submenu = tk.Menu(settings_menu, tearoff=0, font=("Microsoft YaHei", 10))
    title_display_submenu.add_checkbutton(label="显示文件名", command=lambda: print("切换文件名显示"))
    title_display_submenu.add_checkbutton(label="显示文件路径", command=lambda: print("切换文件路径显示"))
    title_display_submenu.add_checkbutton(label="显示状态信息", command=lambda: print("切换状态信息显示"))
    settings_menu.add_cascade(label="窗口标题显示", menu=title_display_submenu)
    settings_menu.add_separator()
    
    # 第二组：编辑设置
    settings_menu.add_checkbutton(label="启用自动换行", command=lambda: print("切换自动换行"))
    
    # 创建制表符设置子菜单
    tab_settings_submenu = tk.Menu(settings_menu, tearoff=0, font=("Microsoft YaHei", 10))
    tab_settings_submenu.add_command(label="制表符宽度: 2", command=lambda: print("设置制表符宽度为2"))
    tab_settings_submenu.add_command(label="制表符宽度: 4", command=lambda: print("设置制表符宽度为4"))
    tab_settings_submenu.add_command(label="制表符宽度: 8", command=lambda: print("设置制表符宽度为8"))
    tab_settings_submenu.add_separator()
    tab_settings_submenu.add_checkbutton(label="使用空格代替制表符", command=lambda: print("切换制表符替换为空格"))
    settings_menu.add_cascade(label="制表符设置", menu=tab_settings_submenu)
    
    settings_menu.add_checkbutton(label="启用快捷插入(@)", command=lambda: print("切换快捷插入功能"))
    settings_menu.add_separator()
    
    # 第三组：保存设置
    settings_menu.add_checkbutton(label="启用自动保存", command=lambda: print("切换自动保存"))
    
    # 创建自动保存间隔子菜单
    autosave_submenu = tk.Menu(settings_menu, tearoff=0, font=("Microsoft YaHei", 10))
    autosave_submenu.add_command(label="30秒", command=lambda: print("设置自动保存间隔为30秒"))
    autosave_submenu.add_command(label="1分钟", command=lambda: print("设置自动保存间隔为1分钟"))
    autosave_submenu.add_command(label="5分钟", command=lambda: print("设置自动保存间隔为5分钟"))
    autosave_submenu.add_command(label="10分钟", command=lambda: print("设置自动保存间隔为10分钟"))
    settings_menu.add_cascade(label="自动保存间隔", menu=autosave_submenu)
    
    settings_menu.add_checkbutton(label="启用副本备份", command=lambda: print("切换副本备份功能"))
    settings_menu.add_separator()
    
    # 第四组：配置管理
    settings_menu.add_command(label="查看配置", command=lambda: print("查看当前配置"))
    settings_menu.add_command(label="重置设置", command=lambda: print("重置所有设置"))
    
    # 将设置菜单添加到主菜单
    main_menu.add_cascade(label="设置", menu=settings_menu)
    
    # 创建帮助菜单
    help_menu = tk.Menu(main_menu, tearoff=0, font=("Microsoft YaHei", 10))
    help_menu.add_command(label="文档统计信息", command=lambda: print("显示文档统计信息"))
    help_menu.add_command(label="关于", command=lambda: print("显示关于信息"))
    
    # 将帮助菜单添加到主菜单
    main_menu.add_cascade(label="帮助", menu=help_menu)
    
    # 将主菜单配置到根窗口
    root.config(menu=main_menu)
    
    return main_menu