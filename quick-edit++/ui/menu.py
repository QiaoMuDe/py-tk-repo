#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
菜单栏界面模块
"""

import customtkinter as ctk


def create_menu(root):
    """创建菜单栏"""
    # 由于customtkinter没有直接的菜单栏组件，我们需要使用tkinter的菜单
    # 这里我们创建一个隐藏的tkinter菜单栏
    import tkinter as tk
    
    # 创建主菜单
    main_menu = tk.Menu(root, font=("Microsoft YaHei", 10))
    
    # 创建文件菜单
    file_menu = tk.Menu(main_menu, tearoff=0, font=("Microsoft YaHei", 10))
    file_menu.add_command(label="新建", command=lambda: print("新建文件"))
    file_menu.add_command(label="打开", command=lambda: print("打开文件"))
    file_menu.add_command(label="保存", command=lambda: print("保存文件"))
    file_menu.add_command(label="另存为", command=lambda: print("另存为"))
    file_menu.add_separator()
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
    
    # 将编辑菜单添加到主菜单
    main_menu.add_cascade(label="编辑", menu=edit_menu)
    
    # 创建工具菜单
    tools_menu = tk.Menu(main_menu, tearoff=0, font=("Microsoft YaHei", 10))
    tools_menu.add_checkbutton(label="自动保存", command=lambda: print("切换自动保存"))
    
    # 创建自动保存子菜单
    autosave_submenu = tk.Menu(tools_menu, tearoff=0, font=("Microsoft YaHei", 10))
    autosave_submenu.add_command(label="30秒", command=lambda: print("设置自动保存间隔为30秒"))
    autosave_submenu.add_command(label="1分钟", command=lambda: print("设置自动保存间隔为1分钟"))
    autosave_submenu.add_command(label="5分钟", command=lambda: print("设置自动保存间隔为5分钟"))
    autosave_submenu.add_command(label="10分钟", command=lambda: print("设置自动保存间隔为10分钟"))
    
    tools_menu.add_cascade(label="自动保存间隔", menu=autosave_submenu)
    
    # 将工具菜单添加到主菜单
    main_menu.add_cascade(label="工具", menu=tools_menu)
    
    # 创建视图菜单
    view_menu = tk.Menu(main_menu, tearoff=0, font=("Microsoft YaHei", 10))
    view_menu.add_checkbutton(label="工具栏", command=lambda: print("切换工具栏"))
    view_menu.add_checkbutton(label="状态栏", command=lambda: print("切换状态栏"))
    
    # 将视图菜单添加到主菜单
    main_menu.add_cascade(label="视图", menu=view_menu)
    
    # 创建帮助菜单
    help_menu = tk.Menu(main_menu, tearoff=0, font=("Microsoft YaHei", 10))
    help_menu.add_command(label="关于", command=lambda: print("关于"))
    
    # 将帮助菜单添加到主菜单
    main_menu.add_cascade(label="帮助", menu=help_menu)
    
    # 将主菜单配置到根窗口
    root.config(menu=main_menu)
    
    return main_menu