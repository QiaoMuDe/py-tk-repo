#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
编辑器主应用类
该模块直接实现主窗口功能, 负责组装所有UI组件和核心功能, 提供统一的应用程序接口
"""

import customtkinter as ctk
import gc
import tkinter as tk
import os
from ui.notification import get_screen_size
from config.config_manager import config_manager
from ui.about_dialog import show_about_dialog
from ui.document_stats_dialog import show_document_stats_dialog
from ui.find_replace_dialog import show_find_replace_dialog
from tkinter import messagebox
from app.app_initializer import AppInitializer
from app.auto_save_manager import AutoSaveManager
from app.edit_operations import EditOperations
from app.selection_operations import SelectionOperations
from app.bookmark_manager import BookmarkManager
from ui.menu import (
    toggle_syntax_highlight,
    toggle_toolbar_visibility,
    toggle_line_numbers,
)
from ui.menu import (
    toggle_auto_wrap,
    toggle_highlight_current_line,
)
from ui.font_dialog import show_font_dialog
from ui.file_properties_dialog import show_file_properties_dialog
import windnd as wd
from ui.file_properties_dialog import update_file_properties_menu_state
from loguru import logger
from customtkinter import ThemeManager
from ui.utils import truncate_string


class QuickEditApp(EditOperations, SelectionOperations, ctk.CTk):
    """QuickEdit++ 主应用类 - 直接继承ctk.CTk作为主窗口"""

    def __init__(self):
        """初始化应用"""
        # 创建自动保存管理器
        self.auto_save_manager = AutoSaveManager(self)

        # 创建应用初始化器
        self.initializer = AppInitializer(self)

        # 执行完整的应用初始化流程
        self.initializer.initialize_app()

        # 初始化书签管理器
        self.bookmark_manager = BookmarkManager(self)

        # 绑定应用程序事件和快捷方式
        self._bind_app_events()

        # 启动自动保存功能
        self.auto_save_manager.start_auto_save()

    def init_drag_drop(self):
        """
        初始化拖拽功能

        使用windnd库实现文件拖拽功能
        """
        try:
            # 注册拖拽目标, 使用编辑器的拖拽处理方法（包含只读模式检查）
            wd.hook_dropfiles(self, func=self.handle_drag_drop)

        except Exception as e:
            logger.error(f"拖拽功能初始化失败: {e}")
            self.nm.show_error(message=f"拖拽功能初始化失败: {e}")

    def handle_drag_drop(self, files):
        """
        处理文件拖拽事件, 先检查是否为只读模式, 再调用实际的拖拽处理方法

        Args:
            files: 拖拽的文件列表, 可能是字节串或字符串
        """
        # 检查是否为只读模式
        if self.is_read_only:
            # messagebox.showinfo("提示", "当前为只读模式, 无法通过拖拽打开文件")
            self.nm.show_info(message="当前为只读模式, 无法通过拖拽打开文件")
            return

        # 调用实际的拖拽处理方法
        self.file_ops.handle_dropped_files(files)

    def clear_memory(self):
        """
        清理编辑器内存的方法
        包括清空文本区域、重置编辑状态和触发垃圾回收
        """
        try:
            logger.info("触发垃圾回收...")

            # 清空撤销/重做堆栈
            self.text_area.edit_reset()

            # 手动触发垃圾回收
            gc.collect()

        except Exception as e:
            logger.error(f"内存清理过程中发生错误: {e}")
            self.nm.show_error(message=f"内存清理过程中发生错误: {e}")

    def get_screen_size(self):
        """
        获取DPI感知的真实屏幕尺寸

        Returns:
            tuple: (屏幕宽度, 屏幕高度), 如果获取失败则返回默认值(1920, 1080)
        """
        # 直接调用notification模块中的get_screen_size函数
        return get_screen_size()

    def center_window(self, window, width=None, height=None):
        """
        将指定窗口居中显示的通用方法

        Args:
            window: 需要居中的窗口对象（可以是Toplevel、CTkToplevel等）
            width: 窗口宽度, 如果为None则使用窗口当前宽度
            height: 窗口高度, 如果为None则使用窗口当前高度

        Returns:
            tuple: (x坐标, y坐标) 窗口应该设置的左上角坐标
        """
        try:
            # 获取屏幕尺寸
            screen_width, screen_height = self.get_screen_size()

            # 如果未指定宽度或高度, 尝试从窗口获取当前尺寸
            if width is None or height is None:
                width, height = window.winfo_width(), window.winfo_height()

            # 获取窗口尺寸
            window_width = width
            window_height = height

            # 计算居中位置
            x = (screen_width // 2) - window_width
            y = (screen_height // 2) - window_height

            # 确保窗口不会超出屏幕边界
            x = max(0, min(x, screen_width - window_width))
            y = max(0, min(y, screen_height - window_height))

            # 设置窗口位置
            window.geometry(f"{window_width}x{window_height}+{x}+{y}")

            return (x, y)

        except Exception as e:
            logger.error(f"窗口居中失败: {e}")
            self.nm.show_error(message=f"窗口居中失败: {e}")
            return (100, 100)

    def _on_closing(self):
        """窗口关闭事件处理"""
        # 关闭所有通知
        if hasattr(self, "nm"):
            self.nm.close_all()

        # 取消自动保存任务 (如果有)
        self.auto_save_manager.stop_auto_save()

        # 如果启用自动保存并且有当前打开的文件, 尝试自动保存
        if self.auto_save_manager.auto_save_enabled and self.current_file_path:
            self.auto_save_manager._auto_save()

        # 停止文件监听
        self.file_watcher.stop_watching()

        # 检查是否需要保存当前文件
        if self.check_save_before_close():
            self.clear_memory()  # 清理内存
            self.destroy()  # 关闭窗口
        # 如果用户取消保存, 则不关闭窗口

        logger.info("exit app...")

    def _bind_app_events(self):
        """
        绑定应用程序级别的事件和快捷方式

        包括自动保存触发事件和焦点管理事件
        """
        # 绑定按键事件
        self.text_area.bind("<Key>", self._on_key_press)  # 监听按键事件
        self.text_area.bind("<KeyRelease>", self._on_text_change)  # 监听按键释放事件
        self.text_area.bind("<Button-1>", self._on_cursor_move)  # 监听鼠标点击事件
        self.text_area.bind(
            "<Button-1>", self._on_mouse_left_click, add="+"
        )  # 额外的鼠标左击事件处理器, 用于清除高亮
        self.text_area.bind(
            "<<Selection>>", self._on_cursor_move
        )  # 监听选择内容改变事件
        self.text_area.bind("<MouseWheel>", self._on_cursor_move)  # 监听鼠标滚轮事件

        # 绑定Linux鼠标滚轮事件
        self.text_area.bind("<Button-4>", self._on_cursor_move, add="+")
        self.text_area.bind("<Button-5>", self._on_cursor_move, add="+")

        # 直接绑定回车键事件, 确保自动递增编号功能优先级最高
        self.text_area.bind("<Return>", self._on_enter_key)  # 专门处理回车键

        # 绑定Tab键事件
        self.text_area.bind("<Tab>", self._on_tab_press)  # 确保Tab键被捕获

        # 绑定文本修改事件（粘贴、剪切等）
        self.text_area.bind("<<Paste>>", self._on_text_change)  # 粘贴事件
        self.text_area.bind("<<Cut>>", self._on_text_change)  # 剪切事件
        self.text_area.bind("<<Modified>>", self._on_text_change)  # 文本修改事件

        # 绑定文本框焦点离开事件, 触发自动保存
        self.text_area.bind("<FocusOut>", self._on_text_area_focus_out)

        # 绑定文件操作快捷键
        self.bind("<Control-n>", lambda e: self.new_file())  # 文件操作快捷键
        # self.bind("<Control-o>", lambda e: self.open_file())  # 打开文件 - 已在_on_key_press中处理
        self.bind("<Control-s>", lambda e: self.save_file())  # 保存文件
        self.bind("<Control-Shift-S>", lambda e: self.save_file_as())  # 另存为
        self.bind("<Control-Shift-B>", lambda e: self.save_file_copy())  # 保存副本
        self.bind("<Control-w>", lambda e: self.close_file())  # 关闭文件
        self.bind(
            "<Control-e>", lambda e: self.open_containing_folder()
        )  # 打开文件所在目录
        self.bind("<Control-r>", lambda e: self.toggle_read_only())  # 切换只读模式
        self.bind("<Control-m>", lambda e: self.rename_file())  # 重命名文件

        # 绑定编辑操作快捷键
        # self.bind("<Control-z>", lambda e: self.undo())  # 撤销
        # self.bind("<Control-y>", lambda e: self.redo())  # 重做
        # self.bind("<Control-x>", lambda e: self.cut())  # 剪切
        # self.bind("<Control-c>", lambda e: self.copy())  # 复制
        # 移除了Ctrl+V的绑定, 使用文本框默认的粘贴行为, 避免重复粘贴
        # self.bind("<Control-v>", lambda e: self.paste())  # 粘贴
        # self.bind("<Control-a>", lambda e: self.select_all())  # 全选
        self.bind("<Control-Shift-D>", lambda e: self.clear_all())  # 清除

        # 绑定导航快捷键
        self.bind("<Home>", lambda e: self.goto_top())  # 转到文件顶部
        self.bind("<End>", lambda e: self.goto_bottom())  # 转到文件底部
        self.bind("<Prior>", lambda e: self.page_up())  # 向上翻页
        self.bind("<Next>", lambda e: self.page_down())  # 向下翻页
        self.bind("<Control-g>", lambda e: self.goto_line())  # 转到行
        # 绑定转到行首和行尾的快捷键
        self.bind(
            "<Control-Shift-less>", lambda e: self.goto_line_start()
        )  # 转到行首 Ctrl+Shift+<
        self.bind(
            "<Control-Shift-greater>", lambda e: self.goto_line_end()
        )  # 转到行尾 Ctrl+Shift+>

        # 绑定退出应用程序事件
        self.bind("<Control-q>", lambda e: self._on_closing())  # 退出应用程序

        # 书签功能快捷键
        self.bind(
            "<Control-b>", lambda e: self.bookmark_manager.toggle_bookmark()
        )  # 添加/删除书签
        self.bind_all(
            "<Control-bracketleft>", lambda e: self.handle_bookmark_navigation("up", e)
        )  # 上一个书签 (Ctrl+[)
        self.bind_all(
            "<Control-bracketright>",
            lambda e: self.handle_bookmark_navigation("down", e),
        )  # 下一个书签 (Ctrl+])
        self.bind(
            "<Alt-l>", lambda e: self.bookmark_manager.clear_all_bookmarks()
        )  # 清除所有书签

        # 绑定全屏快捷键
        self.bind(
            "<F11>", lambda e: self.toggle_fullscreen(switch_state=True)
        )  # F11切换全屏

        # 绑定配置管理快捷键
        self.bind(
            "<Control-Shift-C>", lambda e: self.file_ops.open_config_file()
        )  # 查看配置
        self.bind(
            "<Control-Shift-L>", lambda e: self.file_ops.open_log_file()
        )  # 打开日志文件
        self.bind("<Control-Shift-R>", lambda e: self._reset_settings())  # 重置配置

        # 帮助快捷键
        self.bind("<F1>", lambda e: show_about_dialog(self))  # 显示关于对话框
        self.bind(
            "<F2>", lambda e: show_document_stats_dialog(self)
        )  # 显示文档统计对话框

        # 字体设置快捷键
        # self.bind("<Control-t>", lambda e: show_font_dialog(self))  # 显示字体设置对话框

        # 文件属性快捷键
        self.bind(
            "<F3>",
            lambda e: show_file_properties_dialog(self, self.current_file_path),
        )  # 显示文件属性

        # 语法高亮快捷键
        self.bind(
            "<Control-l>",
            lambda e: toggle_syntax_highlight(self, switch_state=True),
        )  # 切换语法高亮

        # 禁用默认的Ctrl+H行为 (退格), 但不影响Ctrl+Shift+H
        self.bind("<Control-h>", lambda e: "break")

        # 查找和替换
        self.bind(
            "<Control-f>", lambda e: show_find_replace_dialog(self, self.text_area)
        )  # 查找和替换

        # 绑定设置快捷键
        self.bind(
            "<Control-Shift-T>",
            lambda e: toggle_toolbar_visibility(self, switch_state=True),
        )  # 切换工具栏显示
        self.bind(
            "<Control-Shift-N>", lambda e: toggle_line_numbers(self, switch_state=True)
        )  # 切换行号显示
        self.bind(
            "<Control-Shift-W>", lambda e: toggle_auto_wrap(self, switch_state=True)
        )  # 切换自动换行
        self.bind(
            "<Control-Shift-H>",
            lambda e: toggle_highlight_current_line(self, switch_state=True),
        )  # 切换光标所在行高亮

        # 绑定文本框的水平/垂直滚动条的鼠标点击和拖动事件
        self.text_area._y_scrollbar._canvas.bind(
            "<Button-1>", self.on_scroll_drag, add="+"
        )
        self.text_area._y_scrollbar._canvas.bind(
            "<B1-Motion>", self.on_scroll_drag, add="+"
        )
        self.text_area._x_scrollbar._canvas.bind(
            "<Button-1>", self.on_scroll_drag, add="+"
        )
        self.text_area._x_scrollbar._canvas.bind(
            "<B1-Motion>", self.on_scroll_drag, add="+"
        )

        # 设置应用程序启动后获取焦点
        self.after(200, self._on_app_startup)

    def _get_selected_lines(self):
        """获取当前选中的所有行及其索引范围

        Returns:
            list: 包含元组的列表, 每个元组为 (行号, 起始索引, 结束索引)
                例如: [(1, "1.0", "1.end"), (3, "3.0", "3.end")]
                如果没有选中文本, 返回空列表
        """
        selected_lines = []

        try:
            # 获取选中区域的起始和结束位置
            pos = self.text_area.index("sel.first")
            last_pos = self.text_area.index("sel.last")

            # 解析起始和结束行
            start_line = int(pos.split(".")[0])
            end_line = int(last_pos.split(".")[0])

            # 简化逻辑：无论选择是否连续, 都将范围内的所有行包含在内
            # 这样, 如果选中第2行和第5行, 则会将2到5行都选中缩进
            for line_num in range(start_line, end_line + 1):
                line_start = f"{line_num}.0"
                line_end = self.text_area.index(f"{line_num}.end")
                selected_lines.append((line_num, line_start, line_end))

        except Exception as e:
            # 如果获取选中行失败（比如没有选中文本）
            pass

        return selected_lines

    def _on_tab_press(self, event=None):
        """处理Tab键按下事件, 支持单行和多行缩进

        功能:
        - 无选中文本时: 在光标位置插入指定数量的空格或制表符
        - 有选中文本时: 对选中的每一行开头添加缩进（精确处理选中行）
        - 支持撤销操作组, 确保整个缩进操作可以一次性撤销
        """
        # 检查是否为只读模式
        if self.is_read_only:
            # self.status_bar.show_notification("当前为只读模式, 无法进行缩进")
            self.nm.show_info(message="当前为只读模式, 无法进行缩进")
            return "break"

        try:
            # 获取选中的行信息
            selected_lines = self._get_selected_lines()

            # 开始撤销操作组
            self.text_area.edit_separator()

            if selected_lines:
                # 有选中的文本, 对每一个选中的行进行处理
                # 保存当前光标位置
                current_pos = self.text_area.index("insert")

                # 注意：需要从大到小排序行号, 避免索引偏移问题
                # 当在前面的行插入内容后, 后面行的索引会变化
                for line_num, line_start, line_end in sorted(
                    selected_lines, reverse=True, key=lambda x: x[0]
                ):
                    # 在每行开头插入指定数量的空格或制表符
                    if self.use_spaces_for_tab_var.get():
                        self.text_area.insert(
                            line_start, " " * self.tab_width_var.get()
                        )
                    else:
                        self.text_area.insert(
                            line_start, "\t" * self.tab_width_var.get()
                        )

                # 重新选择修改后的文本
                self.text_area.tag_remove("sel", "1.0", "end")
                for line_num, line_start, line_end in selected_lines:
                    # 由于在每行开头插入了内容, 需要重新获取行结束位置
                    new_line_end = self.text_area.index(f"{line_num}.end")
                    self.text_area.tag_add("sel", f"{line_num}.0", new_line_end)

                # 恢复光标位置并向右偏移 (考虑添加的缩进)
                line, col = map(int, current_pos.split("."))
                new_col = col + (
                    self.tab_width_var.get() if self.use_spaces_for_tab_var.get() else 1
                )
                self.text_area.mark_set("insert", f"{line}.{new_col}")

            else:
                # 没有选中的文本, 在当前位置插入指定数量的制表符或空格
                if self.use_spaces_for_tab_var.get():
                    self.text_area.insert("insert", " " * self.tab_width_var.get())
                else:
                    self.text_area.insert("insert", "\t" * self.tab_width_var.get())

            # 结束撤销操作组
            self.text_area.edit_separator()

        except Exception as e:
            # 错误处理, 确保功能不中断
            logger.error(f"Tab键处理失败: {str(e)}")
            # 出现错误时至少保证默认插入行为
            try:
                self.text_area.insert("insert", "\t")
            except:
                pass

        finally:
            # 确保默认Tab键行为
            return "break"

    def on_scroll_drag(self, event=None):
        """处理滚动条拖动事件"""
        # 使用统一的更新方法
        self.update_editor_display()

    def _setup_line_highlight(self, full_init=False):
        """
        设置或更新行高亮配置(高亮光标所在行)

        Args:
            full_init (bool): 是否执行完整初始化（包括设置边距和优先级）
                              True - 应用启动时调用, 执行完整配置
                              False - 仅更新颜色（主题切换时调用）
        """
        # 如果未启用高亮功能, 直接返回
        if not self.highlight_current_line_var.get():
            # 如果之前有高亮, 清除它
            self._clear_current_line_highlight()
            return

        # 从配置管理器获取当前主题模式
        theme_mode = config_manager.get("app.theme_mode", "light")

        # 根据主题模式选择高亮颜色
        # 浅色模式使用黄色, 深色模式使用深蓝色
        highlight_color = "#fcff59" if theme_mode == "light" else "#2a4b6c"

        if full_init:
            # 完整初始化：设置所有标签属性
            self.text_area.tag_config(
                "current_line",
                background=highlight_color,
                lmargin1=0,
                lmargin2=0,
                rmargin=0,
            )

            # 设置标签优先级, 确保高亮在底层
            self.text_area.tag_lower("current_line")
        else:
            # 仅更新颜色
            self.text_area.tag_config("current_line", background=highlight_color)

            # 重新高亮当前行以应用新颜色
            self._highlight_current_line()

    def _on_app_startup(self):
        """
        应用程序启动时的焦点设置

        先让窗口获取焦点, 然后设置文本区域焦点
        """
        # 确保窗口完全显示并获取焦点
        self.focus_force()
        self.update()

        # 初始化行高亮标签配置（只执行一次）
        self._setup_line_highlight(full_init=True)

        # 初始化修改状态为未修改
        self.set_modified(False)

        # 初始化字符数
        self.update_char_count()

        # 然后设置文本区域焦点
        self._focus_text_area()

        # 初始化光标行高亮
        self._highlight_current_line()

    def _on_text_area_focus_out(self, event=None):
        """
        文本区域失去焦点事件处理

        当焦点离开文本框时, 立即执行自动保存（如果文件已修改且自动保存已启用）
        与此定时自动保存是独立的, 确保在用户切换到其他应用时也能保存
        """
        # 使用自动保存管理器处理焦点离开事件
        self.auto_save_manager.on_text_area_focus_out(event)

    def _focus_text_area(self):
        """
        将焦点设置到文本编辑区域

        如果文本区域可编辑（非只读模式）, 则将焦点设置到文本区域
        """
        if not self.is_read_only:
            # 设置焦点到文本区域
            self.text_area.focus_set()
            # 将光标移动到文本末尾或当前位置
            try:
                # 如果有内容, 将光标移动到末尾
                if self.get_char_count() > 0:
                    self.text_area.mark_set("insert", "end")
                else:
                    # 如果没有内容, 将光标设置到开始位置
                    self.text_area.mark_set("insert", "1.0")
            except:
                # 如果出现异常, 至少确保焦点在文本区域
                pass

    def _on_enter_key(self, event=None):
        """专门处理回车键事件, 实现自动递增编号功能"""
        # 检查是否启用了自动递增编号功能
        if not self.auto_increment_number_var.get():
            # 如果功能未启用, 执行默认回车行为
            return None

        # 获取当前光标位置
        cursor_pos = self.text_area.index(ctk.INSERT)
        current_line = cursor_pos.split(".", 1)[0]  # 限制分割次数

        # 获取当前行的文本内容（不strip, 减少操作）
        line_start = f"{current_line}.0"
        line_end = f"{current_line}.end"
        line_text = self.text_area.get(line_start, line_end)

        # 检查当前行是否以数字编号开头（如 "1.", "2.", "1,", "2, " 等）
        # 使用partition()方法高效分割字符串, 支持多种分隔符
        if line_text and line_text[0].isdigit():
            # 使用元组存储分隔符, 避免重复代码
            separators = (".", "、", ",", ", ")
            number_str = None
            separator = None
            rest = None

            # 遍历分隔符, 找到第一个匹配的
            for sep in separators:
                num, found_sep, r = line_text.partition(sep)
                if found_sep:  # 找到分隔符
                    number_str = num
                    separator = found_sep
                    rest = r
                    break  # 找到后立即退出循环

            # 检查是否有分隔符且数字部分有效
            if separator and number_str.isdigit():
                # 检查数字后是否有空格（可选）
                has_space = rest.startswith(" ")

                # 递增编号
                next_number = int(number_str) + 1  # 直接计算, 无需中间变量

                # 插入新行并自动添加递增编号
                if has_space:
                    self.text_area.insert(ctk.INSERT, f"\n{next_number}{separator} ")
                else:
                    self.text_area.insert(ctk.INSERT, f"\n{next_number}{separator}")

                return "break"  # 阻止默认回车行为

        # 检查常见列表格式（如 "- ",）
        if line_text and len(line_text) > 1:
            # 使用元组存储常见列表标记
            list_markers = ("-",)

            # 遍历列表标记
            for marker in list_markers:
                # 检查行首是否是列表标记
                if line_text.startswith(marker):
                    # 获取标记后的内容
                    rest_content = line_text[len(marker) :]

                    # 检查标记后是否有空格（可选）
                    has_space = rest_content.startswith(" ")

                    # 插入新行并自动添加列表标记, 保持原格式
                    if has_space:
                        self.text_area.insert(ctk.INSERT, f"\n{marker} ")
                    else:
                        self.text_area.insert(ctk.INSERT, f"\n{marker}")

                    return "break"  # 阻止默认回车行为

        # 检查单行注释格式（如 "# ", "// ", "-- "）
        if line_text and len(line_text) > 1:
            # 使用元组存储常见注释标记
            comment_markers = ("#", "//", "--")

            # 遍历注释标记
            for marker in comment_markers:
                # 对于井号, 需要确保它不是标题（即后面没有跟着#）
                if marker == "#" and (len(line_text) > 1 and line_text[1] == "#"):
                    continue

                # 检查行首是否是注释标记
                if line_text.startswith(marker):
                    # 获取标记后的内容
                    rest_content = line_text[len(marker) :]

                    # 检查标记后是否有空格（可选）
                    has_space = rest_content.startswith(" ")

                    # 插入新行并自动添加注释标记, 保持原格式
                    if has_space:
                        self.text_area.insert(ctk.INSERT, f"\n{marker} ")
                    else:
                        self.text_area.insert(ctk.INSERT, f"\n{marker}")

                    return "break"  # 阻止默认回车行为

        # 如果不是特殊格式行, 执行默认回车行为
        return None

    def _on_key_press(self, event=None):
        """按键/键盘事件处理"""

        # 检测Ctrl+H组合键（但不包括Ctrl+Shift+H）, 阻止默认的退格行为
        if (
            (event.state & 0x4)
            and not (event.state & 0x1)
            and (event.keysym == "h" or event.char == "\x08")
        ):
            return "break"

        # 检测Ctrl+O组合键, 拦截底层行为
        if (event.state & 0x4) and (event.keysym == "o"):
            self.open_file()
            return "break"

        # 检测Ctrl+I组合键, 拦截底层行为
        if (event.state & 0x4) and (event.keysym == "i"):
            # show_file_properties_dialog(self, self.current_file_path)
            return "break"

        # 检测Ctrl+T组合键, 拦截底层行为
        if (event.state & 0x4) and (event.keysym == "t"):
            show_font_dialog(self)
            return "break"

    def _on_text_change(self, event=None):
        """文本改变事件处理"""
        # 获取当前修改状态
        is_modified = self.is_modified()

        # 如果为已修改状态, 更新缓存的字符数
        if is_modified:
            self.update_char_count()

        # 如果是新文件或没有打开文件, 且文本框内容为空, 重置为未修改状态
        if (
            self.is_new_file or self.current_file_path is None
        ) and self.get_char_count() == 0:
            self.set_modified(False)

        # 使用统一的更新方法
        self.update_editor_display()

    def set_modified(self, modified=False):
        """
        设置文本区域修改状态

        Args:
            modified (bool): True表示标记为已修改, False表示标记为未修改, 默认为True
        """
        self.text_area.edit_modified(modified)

    def is_modified(self):
        """
        获取文本区域修改状态

        Returns:
            bool: True表示已修改, False表示未修改
        """
        status = self.text_area.edit_modified()
        return status != 0  # CTK返回0表示未修改, 非0表示已修改

    def update_editor_display(self):
        """
        统一更新编辑器显示元素的方法, 包括行号绘制、当前行高亮和语法高亮

        这个方法提供了一个统一的接口来更新编辑器的各种视觉元素, 避免代码重复,
        并确保在需要时可以一次性更新所有相关的显示组件。
        方法内部会根据当前的配置状态判断是否需要执行相应的更新。
        """
        try:
            # 更新行号绘制 - 只有在启用行号显示时才执行
            if self.line_numbers_var.get():
                self.after_idle(self.line_number_canvas.draw_line_numbers)

            # 更新当前行高亮 - 只有在启用当前行高亮时才执行
            if self.highlight_current_line_var.get():
                self._highlight_current_line()

            # 更新语法高亮 - 只有在启用语法高亮且使用可见区域渲染模式时才执行
            if (
                self.syntax_highlight_var.get()
                and self.syntax_highlighter.render_visible_only
            ):
                self.syntax_highlighter._handle_event()

            # 更新状态栏信息
            self._update_status_bar()

        except Exception as e:
            logger.error(f"更新编辑器显示时出错: {e}")
            self.nm.show_error(message=f"更新编辑器显示时出错: {e}")

    def _on_cursor_move(self, event=None):
        """光标移动事件处理"""
        # 使用统一的更新方法
        self.update_editor_display()

    def _clear_current_line_highlight(self):
        """
        清除当前光标所在行的高亮

        如果存在高亮的行, 则移除高亮标签并重置当前高亮行号
        """
        if self.current_highlighted_line is not None:
            self.text_area.tag_remove(
                "current_line",
                f"{self.current_highlighted_line}.0",
                f"{int(self.current_highlighted_line) + 1}.0",
            )
            self.current_highlighted_line = None

    def _highlight_current_line(self):
        """
        高亮光标所在的当前行, 包括整行宽度（含右侧空白区域）
        仅执行实际的高亮操作, 标签样式配置已在初始化时完成
        清除之前高亮的行, 并高亮当前光标所在的行
        """
        # 如果未启用高亮功能, 直接返回
        if not self.highlight_current_line_var.get():
            return

        # 先清除之前高亮的行
        self._clear_current_line_highlight()

        # 获取当前光标位置
        cursor_pos = self.text_area.index(ctk.INSERT)
        current_line = int(cursor_pos.split(".")[0])

        # 高亮当前行 - 使用从当前行首到下一行行首的范围, 确保覆盖整行宽度
        start_pos = f"{current_line}.0"
        end_pos = f"{current_line}.end+1c"  # 扩展一个字符确保右侧空白区域也被高亮
        self.text_area.tag_add("current_line", start_pos, end_pos)

        # 存储当前高亮行号
        self.current_highlighted_line = current_line

    def _on_mouse_left_click(self, event=None):
        """
        鼠标左击事件处理函数

        在左键点击时清除查找替换的高亮标签

        Args:
            event: 事件对象, 包含鼠标点击的位置信息
        """
        # 清除查找替换的高亮
        try:
            self.find_replace_engine.clear_highlights()
        except Exception as e:
            # print(f"Error in _on_mouse_left_click: {e}")
            pass

        # 确保文本框处理完点击事件后立即更新显示
        self.after_idle(self.update_editor_display)

    def _update_status_bar(self):
        """更新状态栏信息"""
        # 如果当前有通知活动, 不更新状态栏
        if not self.status_bar.can_update_status():
            return

        # 获取光标位置
        cursor_pos = self.text_area.index(ctk.INSERT)
        row, col = cursor_pos.split(".")
        row, col = int(row), int(col) + 1  # 转换为1基索引

        # 获取选中字符数
        try:
            selected_content = self.text_area.get(ctk.SEL_FIRST, ctk.SEL_LAST)
            # 计算选中内容的字符数, 不特殊处理换行符
            selected_chars = len(selected_content)

            # 获取选中的起始和结束位置
            start_pos = self.text_area.index(ctk.SEL_FIRST)
            end_pos = self.text_area.index(ctk.SEL_LAST)

            # 提取起始和结束行号
            start_row = int(start_pos.split(".")[0])
            end_row = int(end_pos.split(".")[0])

            # 计算选中的行数
            selected_lines = end_row - start_row + 1

            # 特殊情况处理：
            # 1. 如果选中内容为空, 不显示行数
            # 2. 如果全选且末尾没有字符（即end_col为0）, 则减去一行
            end_col = int(end_pos.split(".")[1])
            if selected_chars == 0:
                selected_lines = None
            elif end_col == 0 and end_row > start_row:
                # 全选情况, 末尾位置在行首, 减去一行
                selected_lines = end_row - start_row

        except tk.TclError:
            # 没有选中内容
            selected_chars = None
            selected_lines = None

        # 根据文件修改状态确定状态文本
        status = "已修改" if self.is_modified() else "就绪"

        # 更新状态栏, 不再传递total_chars参数, 让set_status_info内部获取
        self.status_bar.set_status_info(
            status=status,
            row=row,
            col=col,
            selected_chars=selected_chars,
            selected_lines=selected_lines,
        )

        # 更新窗口标题
        self._update_window_title()

    def toggle_fullscreen(self, switch_state=True):
        """
        切换全屏模式
        切换应用程序窗口的全屏/窗口模式状态

        Args:
            switch_state (bool): 是否需要翻转状态, 默认为True
                                True - 切换状态（用于快捷键）
                                False - 应用当前状态（用于菜单点击）

        Returns:
            bool: 切换后的全屏状态
        """
        # 调用工具栏的全屏切换方法
        return self.toolbar.toggle_fullscreen(switch_state)

    def _update_window_title(self):
        """根据文件修改状态更新窗口标题"""
        # 使用类属性获取窗口标题模式
        title_mode = self.title_mode_var.get()

        # 根据文件修改状态和路径构建标题
        if self.current_file_path:
            # 有文件路径的情况
            file_path = self.current_file_path
            file_name = os.path.basename(file_path)

            # 根据配置的模式构建标题
            if title_mode == "filepath":
                # 完整文件路径模式 - 使用截断函数处理长路径
                title_part = truncate_string(file_path, self.truncate_path_length)

            elif title_mode == "filename_and_dir":
                # 文件名和目录模式 - 使用截断函数处理长路径
                dir_name = os.path.dirname(file_path)
                # 截断目录名，但保留更多空间给文件名
                dir_display = (
                    truncate_string(dir_name, self.truncate_path_length // 2)
                    if dir_name
                    else ""
                )
                # 文件名也使用截断函数，但保留更多字符
                file_display = (
                    truncate_string(file_name, self.truncate_path_length // 2 + 20)
                    if file_name
                    else ""
                )
                title_part = (
                    f"{file_display} [{dir_display}]" if dir_display else file_display
                )

            else:  # 默认为 "filename" 模式
                # 文件名模式 - 也使用截断函数处理长文件名
                title_part = truncate_string(file_name, self.truncate_path_length)

        elif self.is_new_file:
            # 新文件状态, 无论内容是否为空都显示"新文件"
            title_part = "新文件"
        else:
            # 没有文件路径的情况
            if self._total_chars > 0:
                title_part = "未命名"
            else:
                title_part = None

        # 构建最终标题
        if title_part:
            # 根据修改状态添加星号
            prefix = "*" if self.is_modified() else ""
            title = f"{prefix}{title_part} - {self.app_name}"
        else:
            # 没有内容时只显示程序名
            title = self.app_name

        self.title(title)

    def open_file(self):
        """打开文件并加载到文本编辑区域"""
        # 检查是否为只读模式
        if self.is_read_only:
            # messagebox.showinfo("提示", "当前为只读模式, 请先关闭只读模式后再打开文件")
            self.nm.show_info(message="当前为只读模式, 请先关闭只读模式后再打开文件")
            return

        # 直接调用文件操作处理器的打开文件方法
        self.file_ops._open_file(check_save=True, check_backup=True, select_path=True)

    def open_file_with_path(self, file_path):
        """通过指定路径打开文件"""
        # 检查是否为只读模式
        if self.is_read_only:
            # messagebox.showinfo("只读模式", "当前处于只读模式, 无法打开新文件。")
            self.nm.show_info(message="当前处于只读模式, 无法打开新文件。")
            return

        # 直接调用文件操作处理器的打开文件方法
        self.file_ops._open_file(
            check_save=True, check_backup=True, file_path=file_path
        )

    def save_file(self):
        """保存当前文件"""
        # 检查是否为只读模式
        if self.is_read_only:
            # messagebox.showinfo("提示", "当前为只读模式, 无法保存文件")
            self.nm.show_info(message="当前为只读模式, 无法保存文件")
            return False

        # 直接调用文件操作处理器的保存文件方法
        return self.file_ops._save_file()

    def save_file_as(self):
        """另存为文件"""
        # 检查是否为只读模式
        if self.is_read_only:
            # messagebox.showinfo("提示", "当前为只读模式, 无法另存为文件")
            self.nm.show_info(message="当前为只读模式, 无法另存为文件")
            return False

        # 直接调用文件操作处理器的另存为方法
        return self.file_ops._save_file(force_save_as=True)

    def save_file_copy(self):
        """保存当前文件的副本"""
        # 直接调用文件操作处理器的保存副本方法
        return self.file_ops.save_file_copy()

    def rename_file(self):
        """重命名当前文件"""
        # 直接调用文件操作处理器的重命名方法
        return self.file_ops.rename_file()

    def close_file(self):
        """关闭当前文件"""
        # 检查是否为只读模式
        if self.is_read_only:
            # messagebox.showinfo("提示", "当前为只读模式, 请先关闭只读模式后再关闭文件")
            self.nm.show_info(message="当前为只读模式, 请先关闭只读模式后再关闭文件")
            return
        # 直接调用文件操作处理器的关闭文件方法
        self.file_ops.close_file()

    def handle_bookmark_navigation(self, direction, event):
        """
        处理书签导航的专用方法

        Args:
            direction (str): 导航方向, "up" 表示上一个书签, "down" 表示下一个书签
            event: 事件对象
        """
        if direction == "up":
            self.bookmark_manager.goto_previous_bookmark()
        elif direction == "down":
            self.bookmark_manager.goto_next_bookmark()

    def check_save_before_close(self):
        """在关闭文件前检查是否需要保存"""
        # 直接调用文件操作处理器的检查保存方法
        return self.file_ops.check_save_before_close()

    def new_file(self):
        """创建新文件"""
        # 检查是否为只读模式
        if self.is_read_only:
            # messagebox.showinfo(
            #     "提示", "当前为只读模式, 请先关闭只读模式后再创建新文件"
            # )
            self.nm.show_info(message="当前为只读模式, 请先关闭只读模式后再创建新文件")
            return

        # 调用新建文件辅助方法
        self.file_ops._new_file_helper()

    def toggle_read_only(self):
        """切换只读模式"""
        self.is_read_only = not self.is_read_only

        # 保存只读模式状态到配置文件
        config_manager.set("text_editor.read_only", self.is_read_only)
        config_manager.save_config()

        # 根据只读模式状态设置文本编辑区域
        if self.is_read_only:
            # 设置为只读模式
            self.text_area.configure(state="disabled")
            # self.status_bar.show_notification("已切换到只读模式")
            self.nm.show_info(message="已切换到只读模式")

            # 更新工具栏按钮外观
            self.toolbar.readonly_button.configure(
                fg_color="#FF6B6B", hover_color="#FF5252"
            )
        else:
            # 设置为编辑模式
            self.text_area.configure(state="normal")
            # self.status_bar.show_notification("已切换到编辑模式")
            self.nm.show_info(message="已切换到编辑模式")

            # 恢复工具栏按钮默认外观
            default_fg_color = ThemeManager.theme["CTkButton"]["fg_color"]
            default_hover_color = ThemeManager.theme["CTkButton"]["hover_color"]
            self.toolbar.readonly_button.configure(
                fg_color=default_fg_color, hover_color=default_hover_color
            )

    def open_containing_folder(self):
        """打开当前文件所在的文件夹"""
        if self.current_file_path:
            try:
                # 获取文件所在的目录
                directory = os.path.dirname(self.current_file_path)
                if os.path.exists(directory):
                    # 在Windows上使用explorer命令打开文件夹
                    os.startfile(directory)
                else:
                    # messagebox.showerror("错误", "文件所在目录不存在")
                    self.nm.show_error(message="文件所在目录不存在")
            except Exception as e:
                logger.error(f"无法打开文件所在文件夹: {str(e)}")
                # messagebox.showerror("错误", f"无法打开文件所在文件夹: {str(e)}")
                self.nm.show_error(message=f"无法打开文件所在文件夹: {str(e)}")
        else:
            # messagebox.showinfo("提示", "当前没有打开的文件")
            self.nm.show_info(message="当前没有打开的文件")

    def open_program_directory(self):
        """打开程序所在的目录"""
        try:
            # 获取程序所在的目录
            program_dir = os.path.dirname(os.path.abspath(__file__))
            # 在Windows上使用explorer命令打开文件夹
            os.startfile(program_dir)

        except Exception as e:
            logger.error(f"无法打开程序所在目录: {str(e)}")
            self.nm.show_error(message=f"无法打开程序所在目录: {str(e)}")

    def get_char_count(self):
        """
        获取文本区域的字符数, 使用缓存机制提高性能

        Returns:
            int: 文本区域的字符数
        """
        return self._total_chars

    def update_char_count(self):
        """
        更新缓存的字符数

        在文件内容发生变化时调用此方法
        """
        # 使用end-1c获取文本, 这会自动排除末尾的换行符
        self._total_chars = len(self.text_area.get("1.0", "end-1c"))

    def _reset_settings(self):
        """
        重置所有设置到默认值

        功能：
        - 获取用户确认
        - 调用配置管理器重置配置
        - 显示操作结果提示
        - 提示用户重启应用以应用更改
        """
        # 弹出确认对话框
        confirmed = messagebox.askyesno(
            "确认重置", "确定要将所有设置重置为默认值吗？\n此操作不可撤销。"
        )

        if confirmed:
            # 调用配置管理器重置配置
            success = config_manager.reset()

            if success:
                messagebox.showinfo(
                    "重置成功",
                    "设置已成功重置为默认值！\n请重启应用程序以应用所有更改。",
                )
            else:
                messagebox.showerror("重置失败", "设置重置失败, 请检查配置文件权限。")

    def update_file_menu_state(self):
        """
        更新文件菜单的打开文件相关的逻辑
        """
        # 更新重新打开菜单状态（初始状态下没有打开文件, 应该禁用）
        if self.reopen_file_menu is not None:
            self.reopen_file_menu.update_menu_state()

        if self.file_menu is not None:
            # 更新文件属性菜单状态（初始状态下没有打开文件, 应该禁用）
            update_file_properties_menu_state(self)

            # 更新保存副本菜单状态
            has_current_file = self.current_file_path
            state = "normal" if has_current_file else "disabled"

            # 使用保存的索引直接禁用或启用保存副本菜单项
            if self.save_copy_menu_index is not None:
                try:
                    self.file_menu.entryconfig(self.save_copy_menu_index, state=state)
                except Exception as e:
                    # 如果通过索引更新失败, 打印错误信息
                    logger.error(
                        f"更新“保存副本”菜单状态时出错（索引 {self.save_copy_menu_index}）: {e}"
                    )

            # 更新重命名菜单状态
            if self.rename_menu_index is not None:
                try:
                    self.file_menu.entryconfig(self.rename_menu_index, state=state)
                except Exception as e:
                    # 如果通过索引更新失败, 打印错误信息
                    logger.error(
                        f"更新“重命名”菜单状态时出错（索引 {self.rename_menu_index}）: {e}"
                    )

    # 书签功能方法
    def toggle_bookmark(self):
        """切换当前行的书签状态"""
        self.bookmark_manager.toggle_bookmark()

    def goto_next_bookmark(self):
        """跳转到下一个书签"""
        self.bookmark_manager.goto_next_bookmark()

    def goto_previous_bookmark(self):
        """跳转到上一个书签"""
        self.bookmark_manager.goto_previous_bookmark()

    def clear_all_bookmarks(self):
        """清除所有书签"""
        self.bookmark_manager.clear_all_bookmarks()

    def run(self):
        """运行应用"""
        self.mainloop()
