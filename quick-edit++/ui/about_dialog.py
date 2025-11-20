#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
关于对话框模块
"""

import tkinter as tk
import customtkinter as ctk
import webbrowser
from config.config_manager import config_manager, APP_VERSION, PROJECT_URL


def show_about_dialog(parent):
    """显示关于对话框

    Args:
        parent: 父窗口对象
    """
    # 使用导入的常量
    version = APP_VERSION
    project_path = PROJECT_URL

    # 获取组件字体配置
    font_name = config_manager.get("components.font", "Microsoft YaHei UI")
    font_size = config_manager.get("components.font_size", 13)
    font_bold = config_manager.get("components.font_bold", False)

    # 创建关于对话框窗口
    about_window = ctk.CTkToplevel(parent)
    about_window.title("关于 QuickEdit++")
    about_window.resizable(False, False)

    # 设置窗口模态
    about_window.transient(parent)
    about_window.grab_set()

    # 居中显示
    about_window.update_idletasks()
    width = 500
    height = 550
    # 获取屏幕宽度和高度
    screen_width = about_window.winfo_screenwidth()
    screen_height = about_window.winfo_screenheight()
    # 计算居中位置
    x = screen_width // 3
    y = screen_height // 4
    about_window.geometry(f"{width}x{height}+{x}+{y}")

    # 创建主框架
    main_frame = ctk.CTkFrame(about_window)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # 应用标题
    title_label = ctk.CTkLabel(
        main_frame,
        text="QuickEdit++",
        font=ctk.CTkFont(size=font_size + 11, weight="bold", family=font_name),
    )
    title_label.pack(pady=(20, 10))

    # 版本号
    version_label = ctk.CTkLabel(
        main_frame,
        text=f"版本: {version}",
        font=ctk.CTkFont(size=font_size + 1, family=font_name),
    )
    version_label.pack(pady=(0, 20))

    # 分隔线
    separator = ctk.CTkFrame(main_frame, height=2)
    separator.pack(fill="x", padx=40, pady=(0, 20))

    # 程序简介
    intro_text = """QuickEdit++ 是一款轻量级、功能丰富的文本编辑器，
专为提高编程和文本编辑效率而设计。

主要功能：
• 支持多种文件编码格式（UTF-8、GBK、ANSI等）
• 语法高亮显示（支持30+编程语言）
• 智能书签系统（支持多书签、随机颜色标记）
• 自动保存与文件备份机制
• 可自定义界面主题（亮色/暗色/系统）
• 灵活的编辑设置（自动换行、制表符配置）
• 高级查找替换功能（正则表达式支持）
• 文件变更实时监控
• 行号显示与光标行高亮"""

    intro_label = ctk.CTkLabel(
        main_frame,
        text=intro_text,
        justify="left",
        font=ctk.CTkFont(size=font_size - 1, family=font_name),
    )
    intro_label.pack(pady=(0, 20), padx=20, anchor="w")

    # 项目地址框架
    project_frame = ctk.CTkFrame(main_frame)
    project_frame.pack(fill="x", pady=(0, 20), padx=20)

    project_label = ctk.CTkLabel(
        project_frame,
        text="项目地址:",
        font=ctk.CTkFont(size=font_size - 1, weight="bold", family=font_name),
    )
    project_label.pack(side="left", padx=(10, 5))

    project_url = ctk.CTkLabel(
        project_frame,
        text=project_path,
        font=ctk.CTkFont(size=font_size - 1, family=font_name),
        text_color=("#1E6BA8", "#4A9FE8"),  # 蓝色链接颜色
    )
    project_url.pack(side="left", padx=(0, 10))

    # 为项目地址添加点击事件
    def open_project_url(event=None):
        if project_path:
            webbrowser.open(project_path)

    project_url.bind("<Button-1>", open_project_url)
    project_url.configure(cursor="hand2")

    # 版权信息
    copyright_label = ctk.CTkLabel(
        main_frame,
        text="© 2025 QuickEdit++ 开发团队",
        font=ctk.CTkFont(size=font_size - 3, family=font_name),
    )
    copyright_label.pack(pady=(10, 0))

    # 关闭按钮
    close_button = ctk.CTkButton(
        main_frame,
        text="关闭",
        command=about_window.destroy,
        width=100,
        font=ctk.CTkFont(
            size=font_size, family=font_name, weight="bold" if font_bold else "normal"
        ),
    )
    close_button.pack(pady=(20, 0))

    # 确保窗口获得焦点
    about_window.focus_set()

    # 按ESC键关闭窗口
    about_window.bind("<Escape>", lambda e: about_window.destroy())
