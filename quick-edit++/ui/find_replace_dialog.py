#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
查找替换对话框模块
"""

from turtle import width
from loguru import logger
import customtkinter as ctk
from config.config_manager import ConfigManager
from app.find_replace_engine import SearchOptions


class FindReplaceDialog:
    """
    查找替换对话框类

    提供查找和替换功能的用户界面
    """

    # 类变量，用于跟踪当前活动的对话框实例
    _instance = None

    def __new__(cls, parent, text_widget=None):
        """
        创建新实例前检查是否已有实例存在

        Args:
            parent: 父窗口
            text_widget: 文本编辑器控件，用于执行查找替换操作

        Returns:
            FindReplaceDialog: 对话框实例
        """
        # 如果已有实例存在，则关闭旧实例
        if cls._instance is not None:
            try:
                cls._instance.dialog.destroy()
            except:
                pass  # 忽略关闭旧实例时可能出现的错误

        # 创建新实例
        cls._instance = super(FindReplaceDialog, cls).__new__(cls)
        return cls._instance

    def __init__(self, parent, text_widget=None):
        """
        初始化查找替换对话框

        Args:
            parent: 父窗口
            text_widget: 文本编辑器控件，用于执行查找替换操作
        """
        # 避免重复初始化
        if hasattr(self, "_initialized"):
            return

        self.parent = parent  # 父窗口
        self.text_widget = text_widget  # 文本编辑器控件
        self.config_manager = ConfigManager()  # 配置管理器

        # 使用编辑器实例的查找替换引擎，而不是创建新的
        self.find_replace_engine = parent.find_replace_engine

        # 标记为已初始化
        self._initialized = True

        # 获取组件默认字体配置
        self.font_family = self.config_manager.get(
            "components.font", "Microsoft YaHei UI"
        )
        self.font_size = 15
        self.font_bold = "bold"

        # 存储输入框引用和框架引用
        self.find_entry = None  # 查找输入框
        self.replace_entry = None  # 替换输入框
        self.find_frame = None  # 查找区域框架
        self.replace_frame = None  # 替换区域框架

        # 当前匹配项索引
        self.current_match_index = -1

        # 存储搜索选项，避免每次创建新对象
        self.search_options = None
        # 搜索模式变量 (0:普通模式, 1:全词匹配, 2:正则表达式)
        self.search_mode_var = None

        # 创建对话框窗口
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("查找和替换")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 初始隐藏窗口，等待组件绘制完成后再显示
        self.dialog.withdraw()  # 隐藏窗口

        # 设置窗口关闭协议
        self.dialog.protocol("WM_DELETE_WINDOW", self._close_dialog)

        # 创建UI组件
        self._create_widgets()

        # 初始化搜索选项
        self._update_search_options()

        # 获取编辑器中的选中文本
        self._get_selected_text()

        # 设置焦点到查找输入框并选中所有文本
        self.dialog.after(100, self._focus_and_select)

        # 绑定所有事件和快捷键
        self._bind_events_and_shortcuts()

        # 延迟显示窗口，确保所有组件绘制完成
        self.dialog.after(200, self._show_dialog_delayed)

        # 等待对话框关闭
        self.dialog.wait_window()

    def _create_widgets(self):
        """创建对话框UI组件"""
        # 设置对话框为更现代的尺寸
        self.width = 600
        self.height = 390
        self.parent.center_window(self.dialog, self.width, self.height)

        # 主框架 - 铺满整个窗口背景，统一颜色
        main_frame = ctk.CTkFrame(self.dialog, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # 输入区域 - 使用更现代的卡片式布局
        input_frame = ctk.CTkFrame(main_frame, fg_color="transparent", corner_radius=12, border_width=1, border_color="#444444")
        input_frame.pack(fill="x", padx=15, pady=(15, 15))

        # 查找输入区域
        find_container = ctk.CTkFrame(input_frame, fg_color="transparent")
        find_container.pack(fill="x", pady=(10, 5), padx=10)

        find_label = ctk.CTkLabel(
            find_container,
            text="查找内容:",
            font=(self.font_family, self.font_size, "bold"),
            width=70,
            anchor="w",
        )
        find_label.pack(side="left", padx=(15, 10), pady=10)

        self.find_entry = ctk.CTkEntry(
            find_container,
            font=(self.font_family, self.font_size - 1),
            height=32,
            placeholder_text="输入要查找的文本...",
        )
        self.find_entry.pack(side="left", fill="x", expand=True, padx=(0, 15), pady=10)

        # 替换输入区域
        replace_container = ctk.CTkFrame(input_frame, fg_color="transparent")
        replace_container.pack(fill="x", padx=10, pady=(5, 10))

        replace_label = ctk.CTkLabel(
            replace_container,
            text="替换为:",
            font=(self.font_family, self.font_size, "bold"),
            width=70,
            anchor="w",
        )
        replace_label.pack(side="left", padx=(15, 10), pady=10)

        self.replace_entry = ctk.CTkEntry(
            replace_container,
            font=(self.font_family, self.font_size - 1),
            height=32,
            placeholder_text="输入替换的文本...",
        )
        self.replace_entry.pack(
            side="left", fill="x", expand=True, padx=(0, 15), pady=10
        )

        # 选项区域 - 使用更现代的开关式设计
        options_frame = ctk.CTkFrame(main_frame, fg_color="transparent", corner_radius=12, border_width=1, border_color="#555555")
        options_frame.pack(fill="x", padx=15, pady=(0, 15))

        options_label = ctk.CTkLabel(
            options_frame,
            text="搜索选项",
            font=(self.font_family, self.font_size, "bold"),
        )
        options_label.pack(anchor="w", padx=10, pady=(10, 5))

        # 选项容器 - 使用水平布局
        options_container = ctk.CTkFrame(options_frame, fg_color="transparent")
        options_container.pack(fill="x", padx=10, pady=(0, 10))

        # 搜索模式选项 - 使用分段控件
        self.search_mode_var = ctk.StringVar(value="普通")
        mode_segmented = ctk.CTkSegmentedButton(
            options_container,
            values=["普通", "全词匹配", "正则表达式"],
            variable=self.search_mode_var,
            font=(self.font_family, self.font_size - 2),
            command=self._update_search_options,
            dynamic_resizing=False,
            selected_color="#1a5fb4",
            unselected_color="#343638",
        )
        mode_segmented.pack(fill="x", pady=(0, 10))

        # 不区分大小写选项和提示信息 - 使用水平布局
        switch_container = ctk.CTkFrame(options_container, fg_color="transparent")
        switch_container.pack(fill="x")

        self.nocase_var = ctk.BooleanVar(value=False)
        nocase_switch = ctk.CTkSwitch(
            switch_container,
            text="不区分大小写",
            variable=self.nocase_var,
            font=(self.font_family, self.font_size - 2),
            command=self._update_search_options,
            onvalue=True,
            offvalue=False,
        )
        nocase_switch.pack(side="left")

        # 添加提示标签
        regex_hint_label = ctk.CTkLabel(
            switch_container,
            text="提示: 正则表达式为Tkinter特有语法, 非完整正则",
            font=(self.font_family, self.font_size - 3),
            text_color="#888888",
        )
        regex_hint_label.pack(side="right", padx=(10, 0))

        # 按钮区域 - 使用更现代的布局
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=15, pady=(0, 15))

        # 查找按钮行 - 按比例分配空间
        find_buttons = ctk.CTkFrame(button_frame, fg_color="transparent")
        find_buttons.pack(fill="x", pady=(0, 8))

        # 使用网格布局来实现按钮按比例分配
        find_buttons.columnconfigure(0, weight=1)
        find_buttons.columnconfigure(1, weight=1)
        find_buttons.columnconfigure(2, weight=1)

        find_prev_btn = ctk.CTkButton(
            find_buttons,
            text="▲ 上一个",
            font=(self.font_family, self.font_size - 2),
            height=35,
            command=self._find_previous,
            fg_color="#3584e4",
            hover_color="#1c71d8",
        )
        find_prev_btn.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        find_next_btn = ctk.CTkButton(
            find_buttons,
            text="▼ 下一个",
            font=(self.font_family, self.font_size - 2),
            height=35,
            command=self._find_next,
            fg_color="#3584e4",
            hover_color="#1c71d8",
        )
        find_next_btn.grid(row=0, column=1, padx=4, sticky="ew")

        find_all_btn = ctk.CTkButton(
            find_buttons,
            text="查找全部",
            font=(self.font_family, self.font_size - 2),
            height=35,
            command=self._find_all,
            fg_color="#26a269",
            hover_color="#2ec27e",
        )
        find_all_btn.grid(row=0, column=2, padx=(4, 0), sticky="ew")

        # 替换按钮行 - 按比例分配空间
        replace_buttons = ctk.CTkFrame(button_frame, fg_color="transparent")
        replace_buttons.pack(fill="x")

        # 使用网格布局来实现按钮按比例分配
        replace_buttons.columnconfigure(0, weight=1)
        replace_buttons.columnconfigure(1, weight=1)
        replace_buttons.columnconfigure(2, weight=1)

        replace_btn = ctk.CTkButton(
            replace_buttons,
            text="替换",
            font=(self.font_family, self.font_size - 2),
            height=35,
            command=self._replace,
            fg_color="#e01b24",
            hover_color="#c01c28",
        )
        replace_btn.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        replace_all_btn = ctk.CTkButton(
            replace_buttons,
            text="全部替换",
            font=(self.font_family, self.font_size - 2),
            height=35,
            command=self._replace_all,
            fg_color="#e01b24",
            hover_color="#c01c28",
        )
        replace_all_btn.grid(row=0, column=1, padx=4, sticky="ew")

        close_btn = ctk.CTkButton(
            replace_buttons,
            text="关闭",
            font=(self.font_family, self.font_size - 2),
            height=35,
            command=self._close_dialog,
            fg_color="#5e5c64",
            hover_color="#4a484e",
        )
        close_btn.grid(row=0, column=2, padx=(4, 0), sticky="ew")

    def _bind_events_and_shortcuts(self):
        """
        绑定所有事件和快捷键

        集中管理所有的事件绑定和快捷键绑定，便于维护和修改
        """
        # 绑定ESC键关闭对话框
        self.dialog.bind("<Escape>", lambda e: self._close_dialog())

        # 绑定查找输入框内容变化事件
        self.find_entry.bind("<KeyRelease>", self._on_find_entry_change)

        # 绑定回车键到查找全部功能 - 绑定到整个对话框
        self.dialog.bind("<Return>", lambda e: self._find_all())

        # 绑定上下键到查找上一个和查找下一个功能 - 绑定到整个对话框
        self.dialog.bind("<Up>", lambda e: (self._find_previous(), "break")[1])
        self.dialog.bind("<Down>", lambda e: (self._find_next(), "break")[1])

    def _on_find_entry_change(self, event=None):
        """
        查找输入框内容变化事件处理

        当输入框内容为空或变化时，清除高亮

        Args:
            event: 事件对象（可选）
        """
        # 获取当前输入框内容
        current_text = self.get_find_text()

        # 如果内容为空，清除高亮
        if not current_text:
            self.find_replace_engine.clear_highlights()
            return

        # 如果有上次搜索文本记录且内容不同，清除高亮
        if (
            hasattr(self, "_last_search_text")
            and current_text != self._last_search_text
        ):
            self.find_replace_engine.clear_highlights()

    def get_find_text(self):
        """获取查找输入框的内容"""
        return self.find_entry.get() if self.find_entry else ""

    def get_replace_text(self):
        """获取替换输入框的内容"""
        return self.replace_entry.get() if self.replace_entry else ""

    def _update_search_options(self, value=None):
        """
        更新搜索选项对象

        根据用户在UI界面上选择的搜索模式和不区分大小写选项，
        动态创建并更新SearchOptions对象，用于后续的查找替换操作。

        Args:
            value: 分段按钮传递的值（可选）

        搜索模式映射关系：
        - "普通": 普通模式 - 简单文本匹配，不启用特殊选项
        - "全词匹配": 全词匹配 - 仅匹配完整单词，不启用正则表达式
        - "正则表达式": 正则表达式 - 使用正则表达式语法进行复杂匹配
        """
        # 获取当前选择的搜索模式
        search_mode = self.search_mode_var.get()

        # 使用简洁的条件赋值设置选项参数
        # "普通": 普通模式 - whole_word=False, regex=False
        # "全词匹配": 全词匹配 - whole_word=True, regex=False
        # "正则表达式": 正则表达式 - whole_word=False, regex=True
        normal_search = search_mode == "普通"
        whole_word = search_mode == "全词匹配"
        regex = search_mode == "正则表达式"

        # 创建并更新搜索选项对象，集成不区分大小写设置
        self.search_options = SearchOptions(
            nocase=self.nocase_var.get(),  # 不区分大小写
            normal_search=normal_search,  # 普通模式
            whole_word=whole_word,  # 全词匹配
            regex=regex,  # 正则表达式
        )

    def _get_search_options(self) -> SearchOptions:
        """
        获取当前搜索选项配置

        根据用户在界面上的选择，返回预先创建的SearchOptions对象，
        该对象包含搜索模式（普通、全词匹配、正则表达式）和大小写敏感设置。
        选项会通过_update_search_options方法在用户更改设置时自动更新。

        Returns:
            SearchOptions: 包含当前搜索配置的对象
        """
        return self.search_options

    def _show_message(self, title: str, message: str):
        """
        显示消息框

        Args:
            title: 消息标题
            message: 消息内容
        """
        message_box = ctk.CTkToplevel(self.dialog)
        message_box.title(title)
        message_box.transient(self.dialog)
        message_box.grab_set()

        # 居中显示
        width = 300
        height = 150
        # 居中显示
        self.parent.center_window(message_box, width, height)

        label = ctk.CTkLabel(
            message_box,
            text=message,
            font=(self.font_family, self.font_size),
            wraplength=250,
        )
        label.pack(expand=True, fill="both", padx=20, pady=20)

        button = ctk.CTkButton(message_box, text="确定", command=message_box.destroy)
        button.pack(pady=(0, 20))

    def _get_selected_text(self):
        """获取编辑器中的选中文本并填充到查找输入框"""
        try:
            # 获取编辑器中的选中文本
            selected_text = self.text_widget.get("sel.first", "sel.last")

            # 如果有选中文本，则填充到查找输入框
            if selected_text.strip():
                self.find_entry.delete(0, "end")
                self.find_entry.insert(0, selected_text)
        except:
            # 如果没有选中文本或其他错误，不执行任何操作
            pass

    def _focus_and_select(self):
        """设置焦点到查找输入框并选中所有文本"""
        self.find_entry.focus_set()

        # 如果输入框中有文本，则选中所有文本
        if self.find_entry.get():
            self.find_entry.select_range(0, "end")

    def _find_all(self):
        """查找文档中所有匹配项

        调用find_replace_engine.find_all方法查找并高亮所有匹配项，
        然后显示匹配项数量的提示信息。
        """
        # 获取查找文本并验证
        find_text = self.get_find_text()
        if not find_text:
            # self._show_message("提示", "请输入要查找的内容")
            self.parent.nm.show_info(message="请输入要查找的内容")
            return

        # 记录搜索内容并获取搜索选项
        self._last_search_text = find_text
        search_options = self._get_search_options()

        # 使用查找替换引擎查找所有匹配项
        matches = self.find_replace_engine.find_all(find_text, search_options)

        # 如果找到匹配项，更新行号和语法高亮
        if matches:
            # 更新行号和语法高亮
            self._update_line_numbers_and_syntax_highlighting()

            # 显示查找结果
            # self._show_message("查找结果", f"找到 {len(matches)} 个匹配项")
            self.parent.nm.show_info(message=f"找到 {len(matches)} 个匹配项")
        else:
            # self._show_message("查找结果", "未找到匹配项")
            self.parent.nm.show_info(message="未找到匹配项")

    def _find_previous(self):
        """查找上一个匹配项

        调用find_replace_engine.find_previous方法向上查找匹配项，
        如果找到则高亮显示并滚动到该位置，否则显示提示信息。
        """
        # 获取查找文本并验证
        find_text = self.get_find_text()
        if not find_text:
            # self._show_message("提示", "请输入要查找的内容")
            self.parent.nm.show_info(message="请输入要查找的内容")
            return

        # 记录搜索内容并获取搜索选项
        self._last_search_text = find_text
        search_options = self._get_search_options()

        # 使用查找替换引擎查找上一个匹配项
        found = self.find_replace_engine.find_previous(find_text, search_options)

        # 如果找到匹配项，更新行号和语法高亮
        if found:
            self._update_line_numbers_and_syntax_highlighting()

        # 如果未找到匹配项，显示提示信息
        if not found:
            # self._show_message("查找结果", "未找到匹配项")
            self.parent.nm.show_info(message="未找到匹配项")

    def _find_next(self):
        """查找下一个匹配项

        调用find_replace_engine.find_next方法向下查找匹配项，
        如果找到则高亮显示并滚动到该位置，否则显示提示信息。
        """
        # 获取查找文本并验证
        find_text = self.get_find_text()
        if not find_text:
            # self._show_message("提示", "请输入要查找的内容")
            self.parent.nm.show_info(message="请输入要查找的内容")
            return

        # 记录搜索内容并获取搜索选项
        self._last_search_text = find_text
        search_options = self._get_search_options()

        # 使用查找替换引擎查找下一个匹配项
        found = self.find_replace_engine.find_next(find_text, search_options)

        # 如果找到匹配项，更新行号和语法高亮
        if found:
            self._update_line_numbers_and_syntax_highlighting()

        # 如果未找到匹配项，显示提示信息
        if not found:
            # self._show_message("查找结果", "未找到匹配项")
            self.parent.nm.show_info(message="未找到匹配项")

    def _update_line_numbers_and_syntax_highlighting(self):
        """
        更新行号绘制和语法高亮

        在查找上一个/下一个匹配项后调用此方法，确保行号和语法高亮与当前光标位置同步
        """
        try:
            # 使用父窗口的统一更新方法
            self.parent.update_editor_display()

        except Exception as e:
            # 如果出现异常，记录日志但不中断程序
            logger.error(f"更新行号和语法高亮时出错: {str(e)}")

    def _replace(self):
        """替换当前匹配项

        调用find_replace_engine.replace方法替换当前高亮的匹配项，
        该方法优先使用已存在的当前匹配项进行替换，
        替换完成后显示操作结果提示信息。
        """
        # 获取查找文本和替换文本
        find_text = self.get_find_text()
        replace_text = self.get_replace_text()

        # 验证查找文本不为空
        if not find_text:
            # self._show_message("提示", "请输入要查找的内容")    
            self.parent.nm.show_info(message="请输入要查找的内容")
            return

        # 记录搜索内容并获取搜索选项
        self._last_search_text = find_text
        search_options = self._get_search_options()

        # 调用替换引擎的replace方法执行替换操作
        success = self.find_replace_engine.replace(
            find_text, replace_text, search_options
        )

        if success:
            # self._show_message("替换结果", "替换成功")
            self.parent.nm.show_info(message="替换成功")
        else:
            # self._show_message("替换结果", "未找到匹配项")
            self.parent.nm.show_info(message="未找到匹配项")

    def _replace_all(self):
        """替换文档中所有匹配项

        调用find_replace_engine.replace_all方法替换文档中所有匹配项，
        该方法会从后往前替换以避免索引变化问题，替换完成后会重新高亮所有匹配项，
        最后显示替换结果的提示信息。
        """
        # 获取查找文本和替换文本
        find_text = self.get_find_text()
        replace_text = self.get_replace_text()

        # 验证查找文本不为空
        if not find_text:
            # self._show_message("提示", "请输入要查找的内容")
            self.parent.nm.show_info(message="请输入要查找的内容")
            return

        # 记录搜索内容并获取搜索选项
        self._last_search_text = find_text
        search_options = self._get_search_options()

        # 调用替换引擎的replace_all方法执行替换操作
        count = self.find_replace_engine.replace_all(
            find_text, replace_text, search_options
        )

        # 显示替换结果
        if count > 0:
            # self._show_message("替换结果", f"已替换 {count} 处")
            self.parent.nm.show_info(message=f"已替换 {count} 处")
        else:
            # self._show_message("替换结果", "未找到匹配项")
            self.parent.nm.show_info(message="未找到匹配项")

    def _show_dialog_delayed(self):
        """延迟显示对话框，确保所有组件绘制完成"""
        self.dialog.deiconify()  # 显示窗口
        self.dialog.lift()  # 将窗口提升到前台
        self.dialog.focus_force()  # 强制获取焦点

    def _close_dialog(self):
        """关闭对话框时清理资源"""
        # 不再自动清除高亮，保留高亮直到用户右键点击清除

        # 清除类变量引用
        FindReplaceDialog._instance = None

        self.dialog.destroy()


def show_find_replace_dialog(parent, text_widget=None):
    """
    显示查找替换对话框

    Args:
        parent: 父窗口
        text_widget: 文本编辑器控件，用于执行查找替换操作
    """
    return FindReplaceDialog(parent, text_widget)
