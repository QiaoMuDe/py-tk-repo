import os
import re
import sqlite3
import subprocess as sp
import sys
import threading as thd
import time
import tkinter as tk
import tkinter.filedialog as fdl
import tkinter.ttk as ttk
from tkinter import messagebox as msg

import customtkinter as ctk
import windnd as wd
from loguru import logger


class TextSearchApp:
    def __init__(self, root, main_text):
        self.root = root
        self.main_text = main_text
        self.search_window = None
        self.search_entry = None
        self.search_button = None
        self.prev_button = None
        self.next_button = None
        self.stats_button = None
        self.close_button = None

        # 搜索状态
        self.search_key = ""
        self.matches = []
        self.current_match_index = -1

    def show_search_window(self):
        """
        显示搜索窗口
        """
        # 如果搜索窗口已经存在，则先销毁它
        if not self.search_window is None:
            self.search_window.destroy()
            # 搜索窗口已经存在, 已重新创建
            logger.warning("搜索窗口已经存在, 已重新创建")

        # 创建搜索窗口
        self.search_window = ctk.CTkToplevel(self.root)
        self.search_window.title("搜索")
        self.search_window.geometry("500x100+1000+450")  # 设置窗口大小
        self.search_window.resizable(False, False)  # 禁止调整窗口大小
        self.search_window.attributes("-topmost", True)  # 始终在最顶层显示
        # 设置窗口图标
        if os.path.isfile("./image/GoLite.ico"):
            self.search_window.iconbitmap("./image/GoLite.ico")
            logger.debug("搜索窗口图标已设置, 路径为: ./image/GoLite.ico")
        else:
            logger.warning(
                "搜索窗口图标未设置, 路径不存在, 请检查路径: ./image/GoLite.ico"
            )

        # 创建搜索框和按钮
        self.search_entry = ctk.CTkEntry(
            self.search_window, font=("微软雅黑", 25, "bold")
        )
        self.search_entry.place(x=5, y=0, relwidth=0.75, relheight=0.4)
        self.search_button = ctk.CTkButton(
            self.search_window,
            text="搜索",
            command=self._text_search,
            font=("微软雅黑", 25, "bold"),
        )
        self.search_button.place(x=390, y=0, relwidth=0.2, relheight=0.4)
        self.prev_button = ctk.CTkButton(
            self.search_window,
            text="上一个",
            command=self._prev_search,
            font=("微软雅黑", 25, "bold"),
        )
        self.prev_button.place(x=5, y=50, relwidth=0.23, relheight=0.4)
        self.next_button = ctk.CTkButton(
            self.search_window,
            text="下一个",
            command=self._next_search,
            font=("微软雅黑", 25, "bold"),
        )
        self.next_button.place(x=130, y=50, relwidth=0.23, relheight=0.4)
        self.stats_button = ctk.CTkButton(
            self.search_window,
            text="统计",
            command=self._show_stats,
            font=("微软雅黑", 25, "bold"),
        )
        self.stats_button.place(x=255, y=50, relwidth=0.23, relheight=0.4)
        self.close_button = ctk.CTkButton(
            self.search_window,
            text="关闭",
            command=self.close_search_window,
            font=("微软雅黑", 25, "bold"),
        )
        self.close_button.place(x=375, y=50, relwidth=0.23, relheight=0.4)

        # 设置搜索框焦点
        self.main_text.after(100, self.search_entry.focus_set)

        # 修改窗口绑定
        self.search_window.protocol("WM_DELETE_WINDOW", self.close_search_window)

        # 绑定回车到搜索按钮
        self.search_window.bind("<Return>", lambda event: self._text_search())

        # 日志记录
        logger.debug("搜索窗口已创建")

    def close_search_window(self):
        # 关闭搜索窗口
        if not self.search_window is None:
            # 关闭搜索窗口
            self.search_window.destroy()

            # 删除之前的高亮标签
            self.main_text.tag_remove("found", "1.0", tk.END)
            self.main_text.tag_remove("highlight", "1.0", tk.END)

            # 搜索窗口已关闭
            self.search_window = None

            # 日志记录
            logger.debug("搜索窗口已关闭")

    def _text_search(self):
        key = self.search_entry.get().strip()
        if not key:
            msg.showwarning("提示", "未输入查找内容")
            return

        # 配置关键字高亮样式
        self.main_text.tag_config("found", background="yellow")

        # 删除之前的高亮标签
        self.main_text.tag_remove("found", "1.0", tk.END)
        self.main_text.tag_remove("highlight", "1.0", tk.END)

        # 查找所有匹配项
        self.matches = []
        text = self.main_text.get("1.0", tk.END)
        pattern = re.compile(re.escape(key), re.IGNORECASE)
        for match in pattern.finditer(text):
            start_index = f"1.0+{match.start()}c"
            end_index = f"1.0+{match.end()}c"
            self.matches.append((start_index, end_index))
            self.main_text.tag_add("found", start_index, end_index)

        # 更新搜索状态
        self.search_key = key
        self.current_match_index = -1

        # 提示搜索结果数量
        num_matches = len(self.matches)
        if num_matches == 0:
            msg.showinfo("提示", f"未找到'{key}'相关的匹配项")
        else:
            msg.showinfo("提示", f"找到 '{key}' 的 {num_matches} 个匹配项")

    def _next_search(self):
        if not self.matches:
            msg.showinfo("提示", "没有匹配项")
            return

        self.current_match_index += 1
        if self.current_match_index >= len(self.matches):
            self.current_match_index = 0

        self._jump_to_match()

    def _prev_search(self):
        if not self.matches:
            msg.showinfo("提示", "没有匹配项")
            return

        self.current_match_index -= 1
        if self.current_match_index < 0:
            self.current_match_index = len(self.matches) - 1

        self._jump_to_match()

    def _jump_to_match(self):
        start_index, end_index = self.matches[self.current_match_index]
        self.main_text.tag_remove("highlight", "1.0", tk.END)
        self.main_text.tag_add("highlight", start_index, end_index)
        self.main_text.tag_config("highlight", background="green", foreground="white")
        self.main_text.see(start_index)
        self.main_text.focus_set()
        self.main_text.mark_set(tk.INSERT, start_index)
        self.main_text.see(tk.INSERT)
        msg.showinfo(
            "提示",
            f"找到 '{self.search_key}' 的第 {self.current_match_index + 1} 个匹配项",
        )

    def _show_stats(self):
        num_matches = len(self.matches)
        if num_matches == 0:
            msg.showwarning("警告", "请先输入要搜索的关键词")
            return
        msg.showinfo("统计", f"共找到 '{self.search_key}' 的 {num_matches} 个匹配项")


class GoLite(ctk.CTk):
    def __init__(self):
        super().__init__()
        # 版本号
        self.version = "1.3.2"
        # 最后更新时间
        self.latest_update_time = "2025-01-04"
        # 设置窗口的标题
        self.title("GoLite")
        # 设置程序窗口的宽度和高度
        self.window_width = 800
        self.window_height = 600
        # 设置窗口居中显示的x和y坐标
        self.x = 800
        self.y = 300
        # 设置窗口的大小和位置
        self.geometry(f"{self.window_width}x{self.window_height}+{self.x}+{self.y}")
        # 设置窗口是否可调整大小
        self.resizable(True, True)
        # 图标
        if os.path.isfile("./image/GoLite.ico"):
            self.iconbitmap("./image/GoLite.ico")

        # 初始化环境
        self._init_env()

        # 创建Text组件
        self.main_text = ctk.CTkTextbox(
            self,
            font=self.main_text_font,
            undo=True,
            fg_color="#FFFFFF",
            text_color="#000000",
        )
        self.main_text.place(relx=0, rely=0, relwidth=1, relheight=1)

        # 实例化搜索类
        app_search = TextSearchApp(self, self.main_text)

        # 创建主菜单栏
        self.menu = tk.Menu(self, tearoff=False, font=("微软雅黑", 30, "bold"))
        # 创建子菜单栏
        self.sub_menu = tk.Menu(self.menu, tearoff=False, font=("微软雅黑", 25, "bold"))
        # 创建弹出菜单对象
        self.popupmenu = tk.Menu(self, tearoff=False, font=("微软雅黑", 25, "bold"))

        # 主菜单项
        self.menu.add_cascade(label="文件", menu=self.sub_menu)
        self.menu.add_command(label="编译", command=self._compiler_code)
        self.menu.add_command(label="运行", command=self._run_code)
        self.menu.add_command(label="格式化", command=self._format_code)
        self.menu.add_command(label="关于", command=self._show_version)
        self.menu.add_command(label="Help", command=lambda: self._show_help())
        self.menu.add_command(label="退出", command=self._quit_program)
        # 子菜单项
        self.sub_menu.add_command(label="编译", command=self._compiler_code)
        self.sub_menu.add_command(label="运行", command=self._run_code)
        self.sub_menu.add_command(label="格式化", command=self._format_code)
        self.sub_menu.add_separator()
        self.sub_menu.add_command(label="新建", command=self._new_file)
        self.sub_menu.add_command(label="打开", command=self._open_file)
        self.sub_menu.add_command(label="保存", command=self._save_file)
        self.sub_menu.add_command(label="另存为", command=self._save_as_file)
        self.sub_menu.add_separator()
        self.sub_menu.add_command(label="设置", command=self._settings)
        self.sub_menu.add_command(label="退出", command=self._quit_program)
        # 弹出式菜单项
        self.popupmenu.add_command(label="搜索", command=app_search.show_search_window)
        self.popupmenu.add_separator()
        self.popupmenu.add_command(label="剪切", command=self._cutJob)
        self.popupmenu.add_command(label="复制", command=self._copyJob)
        self.popupmenu.add_command(label="粘贴", command=self._pasteJob)
        self.popupmenu.add_separator()
        self.popupmenu.add_command(label="撤销", command=self._undoJob)
        self.popupmenu.add_command(label="重做", command=self._redoJob)

        # 将菜单栏添加到窗口中
        self.config(menu=self.menu)

        # 绑定快捷键
        # 绑定键盘释放事件到高亮函数
        self.main_text.bind("<KeyRelease>", lambda event: self._highlight_syntax(event))
        # 快捷打开
        self.bind("<Control-o>", lambda event: self._open_file())
        # 快捷保存
        self.bind("<Control-s>", lambda event: self._save_file())
        # 快捷新建
        self.bind("<Control-n>", lambda event: self._new_file())
        # 快捷编译
        self.bind("<Control-b>", lambda event: self._compiler_code())
        # 快捷运行
        self.bind("<Control-r>", lambda event: self._run_code())
        # 快捷格式化
        self.bind("<Control-f>", lambda event: self._format_code())
        # 快捷设置
        self.bind("<Control-g>", lambda event: self._settings())
        # 快捷退出
        self.bind("<Control-q>", lambda event: self._quit_program())
        # 绑定右键菜单
        self.bind("<Button-3>", self._showPopupMenu)
        # 快捷撤回
        self.bind("<Control-z>", lambda event: self._undoJob())
        # 快捷重做
        self.bind("<Control-y>", lambda event: self._redoJob())
        # 快捷帮助
        self.bind("<Control-h>", lambda event: self._show_help())
        # 快捷另存为
        self.bind("<Control-j>", lambda event: self._save_as_file())
        # 快捷查找
        self.bind("<Control-l>", lambda event: app_search.show_search_window())

        # 设置文件拖拽
        wd.hook_dropfiles(self, func=lambda files: self._on_drop(files=files))

        # 修改窗口绑定
        self.protocol("WM_DELETE_WINDOW", self._quit_program)

    def _show_version(self):
        """
        显示版本信息
        """
        msg.showinfo(
            f"版本信息 - GoLite v{self.version}",
            f"更新时间: {self.latest_update_time} \n最新版本: {self.version}",
        )
        logger.debug("用户获取了版本信息")

    def _highlight_syntax(self, event: tk.Event = None):
        """
        Go语法高亮渲染
        """
        # 如果关闭了高亮渲染, 则直接返回
        if not self.hl_sx:
            # 设置文件状态为未保存
            self.is_save = False
            return

        # 配置高亮样式
        self.main_text.tag_config("keyword", foreground="#8959A8")  # 紫色为关键字高亮
        self.main_text.tag_config("comment", foreground="#228B22")  # 深宝石绿为注释高亮
        # self.main_text.tag_config("string", foreground="#3E999F")  # 蓝绿色为特殊字符高亮
        self.main_text.tag_config("string", foreground="#FF4500")  # 白色为特殊字符高亮
        self.main_text.tag_config(
            "datatype", foreground="#4271AE"
        )  # 深蓝色为数据类型高亮
        self.main_text.tag_config("func", foreground="#D33682")  # 浅蓝色为函数高亮
        self.main_text.tag_config(
            "ped", foreground="#00BFFF"
        )  # 亮蓝色为格式化占位符高亮
        self.main_text.tag_config("struct", foreground="#005F6B")  # 深青色为结构体高亮

        # 定义Go语言的关键字列表
        keyword = [
            "break",
            "default",
            "func",
            "interface",
            "select",
            "case",
            "defer",
            "go",
            "map",
            "struct",
            "chan",
            "else",
            "goto",
            "package",
            "switch",
            "const",
            "fallthrough",
            "if",
            "range",
            "type",
            "continue",
            "for",
            "import",
            "return",
            "var",
        ]

        # 定义Go语言的特殊字符列表
        sc_strs = [
            "`",
            "!",
            "&",
            "*",
            "+",
            "-",
            "=",
            ";",
            "<",
            ">",
            ":=",
            "_",
        ]

        # 定义Go语言的数据类型列表
        datatype_list = [
            "int",
            "int8",
            "int16",
            "int32",
            "int64",
            "uint",
            "uint8",
            "uint16",
            "uint32",
            "uint64",
            "uintptr",
            "float32",
            "float64",
            "complex64",
            "complex128",
            "bool",
            "byte",
            "rune",
            "string",
            "error",
            "nil",
            "true",
            "false",
        ]

        # 定义Go语言的格式化占位符列表
        ped_str = [
            "%d",
            "%f",
            "%s",
            "%c",
            "%v",
            "%t",
            "%p",
            "%q",
            "%x",
            "%X",
            "%e",
            "%E",
            "%g",
            "%G",
            "%b",
            "%o",
            "%U",
            "%#U",
            "%#x",
            "%#X",
            "%#o",
            "%#q",
            "%#v",
        ]

        # 定义Go语言的转义字符列表
        esc_str = [
            "\\n",
            "\\t",
            "\\r",
            "\\v",
            "\\f",
            "\\a",
            "\\b",
            "\\e",
            "\\0",
            "\\x",
            "\\u",
            "\\U",
            "\\'",
            '\\"',
            "\\?",
        ]

        # 移除所有已存在的关键字高亮标签
        self.main_text.tag_remove("keyword", "1.0", "end")
        self.main_text.tag_remove("comment", "1.0", "end")
        self.main_text.tag_remove("string", "1.0", "end")
        self.main_text.tag_remove("datatype", "1.0", "end")

        # 获取最后一行的索引
        last_line_index = self.main_text.index("end-1c")

        # 分割索引字符串，获取行号
        last_line_number = int(last_line_index.split(".")[0])

        # 如果文件行数大于600, 则关闭语法高亮
        if last_line_number > 600:
            msg.showwarning("警告", "文件行数过多, 已关闭渲染语法!")
            logger.warning("文件行数过多, 已关闭渲染语法!")
            # 关闭语法高亮
            self.hl_sx = False

        # 获取文本框中的所有内容
        text_content = self.main_text.get("1.0", "end")

        # 提示开始渲染
        logger.info("正在渲染语法高亮...")
        start_time = time.time()

        # 关键字高亮
        # 转义关键字中可能存在的正则表达式特殊字符
        escaped_keywords = [re.escape(keyword_id) for keyword_id in keyword]
        # 构建正则表达式，使用 '|' 来表示逻辑或，匹配任意一个关键字
        kw_pattern = r"\b(" + "|".join(escaped_keywords) + r")\b"
        # 使用 re.finditer 来迭代匹配所有的关键字
        for match in re.finditer(kw_pattern, text_content):
            start, end = match.span()
            # 计算索引位置
            index1 = f"1.0 + {start} chars"
            index2 = f"1.0 + {end} chars"
            # 添加高亮标签
            self.main_text.tag_add("keyword", index1, index2)

        # 高亮单行注释
        single_line_comment_pattern = r"//.*?$"
        single_line_comments = re.finditer(
            single_line_comment_pattern, text_content, re.MULTILINE
        )
        for comment in single_line_comments:
            start = comment.start()
            end = comment.end()
            index1 = f"1.0 + {start} chars"
            index2 = f"1.0 + {end} chars"
            self.main_text.tag_add("comment", index1, index2)

        # 高亮多行注释
        multi_line_comment_pattern = r"/\*.*?\*/"
        multi_line_comments = re.finditer(
            multi_line_comment_pattern, text_content, re.DOTALL
        )
        for comment in multi_line_comments:
            start = comment.start()
            end = comment.end()
            index1 = f"1.0 + {start} chars"
            index2 = f"1.0 + {end} chars"
            self.main_text.tag_add("comment", index1, index2)

        # 特殊字符高亮
        for sc_str in sc_strs:
            sc_str_pattern = re.escape(sc_str)
            sc_str_line_comments = re.finditer(sc_str_pattern, text_content, re.DOTALL)
            for comment in sc_str_line_comments:
                start = comment.start()
                end = comment.end()
                if sc_str == "*":
                    # 检查是否是 */ 或 /* 的一部分
                    if (
                        start > 0
                        and text_content[start - 1] == "/"
                        or end < len(text_content)
                        and text_content[end] == "/"
                    ):
                        continue
                index1 = f"1.0 + {start} chars"
                index2 = f"1.0 + {end} chars"
                self.main_text.tag_add("string", index1, index2)

        # 数据类型高亮
        for data_id in datatype_list:
            es_data_id = re.escape(data_id)
            data_id_pattern = r"(?<![A-Za-z0-9_]){0}(?![A-Za-z0-9_])".format(es_data_id)
            data_id_line_comments = re.finditer(
                data_id_pattern, text_content, re.DOTALL
            )
            for comment in data_id_line_comments:
                start = comment.start()
                end = comment.end()
                index1 = f"1.0 + {start} chars"
                index2 = f"1.0 + {end} chars"
                self.main_text.tag_add("datatype", index1, index2)

        # 函数高亮
        es_func_pattern = r"\s+([a-zA-Z_]\w*)\s*\("
        func_line_comments = re.finditer(es_func_pattern, text_content, re.DOTALL)
        for comment in func_line_comments:
            is_keyword = comment.group(1)
            if is_keyword in keyword:
                continue
            start = comment.start()
            end = comment.end() - 1  # 去掉括号
            index1 = f"1.0 + {start} chars"
            index2 = f"1.0 + {end} chars"
            self.main_text.tag_add("func", index1, index2)

        # 格式化占位符高亮
        for ped_str_id in ped_str:
            es_ped_str_id = re.escape(ped_str_id)
            ped_str_id_pattern = r"(?<![A-Za-z0-9_]){0}(?![A-Za-z0-9_])".format(
                es_ped_str_id
            )
            ped_str_id_line_comments = re.finditer(
                ped_str_id_pattern, text_content, re.DOTALL
            )
            for comment in ped_str_id_line_comments:
                start = comment.start()
                end = comment.end()
                index1 = f"1.0 + {start} chars"
                index2 = f"1.0 + {end} chars"
                self.main_text.tag_add("ped", index1, index2)

        # 转义字符高亮
        for esc_str_id in esc_str:
            esc_str_id_pattern = re.escape(esc_str_id)
            esc_str_id_line_comments = re.finditer(
                esc_str_id_pattern, text_content, re.DOTALL
            )
            for comment in esc_str_id_line_comments:
                start = comment.start()
                end = comment.end()
                index1 = f"1.0 + {start} chars"
                index2 = f"1.0 + {end} chars"
                self.main_text.tag_add("string", index1, index2)

        # 结构体高亮
        es_stru_pattern = r"\s+([a-zA-Z_]\w*)\s*\{"
        stru_line_comments = re.finditer(es_stru_pattern, text_content, re.DOTALL)
        for comment in stru_line_comments:
            is_stru = comment.group(1)
            # 检查是否是关键字
            if is_stru in keyword:
                continue
            # 检查是否是数据类型
            if is_stru in datatype_list:
                continue
            start = comment.start()
            end = comment.end() - 1  # 去掉括号
            index1 = f"1.0 + {start} chars"
            index2 = f"1.0 + {end} chars"
            self.main_text.tag_add("struct", index1, index2)

        # 数组高亮
        es_array_pattern = r"\b(\*?[a-zA-Z_][a-zA-Z0-9_]*)\[\s*([a-zA-Z0-9_.,]*)\s*\]"
        array_line_comments = re.finditer(es_array_pattern, text_content, re.DOTALL)
        for comment in array_line_comments:
            is_array = comment.group(1)
            # 检查是否是关键字
            if is_array in keyword:
                continue
            # 检查是否是数据类型
            if is_array in datatype_list:
                continue
            start = comment.start()
            end = comment.end()
            index1 = f"1.0 + {start} chars"
            index2 = f"1.0 + {end} chars"
            self.main_text.tag_add("datatype", index1, index2)

        # 提示信息
        end_time = time.time()
        logger.success(f"渲染语法完成, 耗时: {round(end_time - start_time, 1)}秒")

        # 设置文件状态为未保存
        self.is_save = False

    def _init_env(self):
        """
        初始化环境
        """

        def restore_code():
            # 检查code_history表是否存在上次保存的文件
            result_code_history = self._exec_sql(
                "SELECT code FROM code_history limit 1", sql_param=(), return_data=True
            )
            if len(result_code_history) == 0:
                # 如果数据库中没有, 则跳过
                logger.debug("数据库中没有上次保存的文件, 跳过加载")
            else:
                # 如果数据库中有, 则弹出提示框, 是否加载上次保存的文件
                result = msg.askyesno("提示", "检测到上次编辑的文件, 是否加载?")
                if result:
                    # 如果选择是, 则加载上次保存的文件
                    self.main_text.delete("1.0", "end")
                    self.main_text.insert("1.0", result_code_history[0][0])
                    logger.success("上次保存的文件已加载")
                    # 渲染内容, 并设置文件状态为未保存
                    self._highlight_syntax()
                    # 清理code_history表
                    self._exec_sql(
                        "DELETE FROM code_history", sql_param=(), return_data=False
                    )
                    logger.info("已加载上次保存的文件, 清理上次保存的文件")
                else:
                    # 如果选择否, 则跳过
                    logger.info("用户选择不加载上次保存的文件")

        # 检查程序运行的工作目录是否都存在
        if not os.path.isdir("data"):
            os.mkdir("data")
        if not os.path.isdir("logs"):
            os.mkdir("logs")
        if not os.path.isdir("image"):
            os.mkdir("image")
        if not os.path.isdir("lib"):
            os.mkdir("lib")

        # 初始化注册日志
        self._init_log()

        # 初始化数据库
        self.db_path = self._create_table()

        # 公共变量, 用于存储文件路径,不用的时候设置为None
        self.file_path = None

        # 获取工作空间, 未设置则为None
        result_gopath = self._exec_sql(
            "SELECT value FROM system_cfg where name = ?",
            sql_param=("go_path",),
            return_data=True,
        )
        if len(result_gopath) == 0:
            # 如果数据库中没有设置, 则设置为None
            self.GOPATH = None
            logger.warning("未设置工作空间, 请在设置中设置工作空间")
        else:
            self.GOPATH = result_gopath[0][0]
            logger.success(f"从数据库中获取工作空间成功, 工作空间为: {self.GOPATH}")

        # 获取GO编译器根目录
        result_goroot = self._exec_sql(
            "SELECT value FROM system_cfg where name = ?",
            sql_param=("go_root",),
            return_data=True,
        )
        if len(result_goroot) == 0:
            # 如果数据库中没有设置, 则设置为None
            self.GOROOT = None
            logger.warning("未设置GO编译器根目录, 请在设置中设置GO编译器根目录")
        else:
            self.GOROOT = result_goroot[0][0]
            logger.success(
                f"从数据库中获取GO编译器根目录成功, GO编译器根目录为: {self.GOROOT}"
            )

        # 初始化设置界面的存活变量
        self.settings_window = None

        # 初始化帮助界面的存活变量
        self.help_window = None

        # 初始化字体对象
        result_font = self._exec_sql(
            "SELECT name,value FROM system_cfg where name in (?,?,?)",
            sql_param=("font_family", "font_size", "font_weight"),
            return_data=True,
        )
        if len(result_font) == 0:
            # 如果数据库中没有设置, 则使用默认字体
            font_family = "微软雅黑"
            font_size = 25
            font_weight = "bold"
            # 将默认字体保存到数据库中
            self._exec_sql(
                "INSERT INTO system_cfg (name,value) VALUES (?,?)",
                sql_param=("font_family", font_family),
            )
            self._exec_sql(
                "INSERT INTO system_cfg (name,value) VALUES (?,?)",
                sql_param=("font_size", font_size),
            )
            self._exec_sql(
                "INSERT INTO system_cfg (name,value) VALUES (?,?)",
                sql_param=("font_weight", font_weight),
            )
            self.main_text_font = ctk.CTkFont(
                family=font_family, size=int(font_size), weight=font_weight
            )
            logger.warning("数据初次运行没有设置字体, 正在初始化字体设置...")
            logger.success(
                f"初始化字体设置成功, 字体为: {font_family}, {font_size}, {font_weight}"
            )
        else:
            logger.success(
                f"从数据库中获取字体设置成功, 字体为: {result_font[0][1]}, {result_font[1][1]}, {result_font[2][1]}"
            )
            self.main_text_font = ctk.CTkFont(
                family=result_font[0][1],
                size=int(result_font[1][1]),
                weight=result_font[2][1],
            )

        # 默认开启渲染语法高亮
        self.hl_sx = True

        # 全局变量---用于判断文件是否保存 默认为None
        self.is_save = None

        # 检查是否有上次保存的文件 1秒后执行
        self.after(1000, restore_code)

        # 获取自动保存时间间隔
        result_auto_save_time = self._exec_sql(
            "SELECT value FROM system_cfg where name = ?",
            sql_param=("auto_save_time",),
            return_data=True,
        )
        if len(result_auto_save_time) == 0:
            # 如果数据库中没有设置, 则跳过
            logger.warning("数据库中没有设置自动保存时间, 跳过运行自动保存")
            # 关闭自动保存
            self.enable_auto_save = False
        else:
            # 如果数据库中有, 则获取自动保存时间
            self.auto_save_time = int(result_auto_save_time[0][0])
            logger.success(
                f"从数据库中获取自动保存时间成功, 自动保存时间为: {self.auto_save_time}秒"
            )

            # 是否运行自动保存
            result_auto_save = self._exec_sql(
                "SELECT value FROM system_cfg where name = ?",
                sql_param=("auto_save",),
                return_data=True,
            )
            if len(result_auto_save) == 0:
                # 如果数据库中没有设置, 则跳过
                logger.warning("检索数据库, 查询到没有开启自动保存, 跳过运行自动保存")
                # 没开启自动保存, 跳过
                self.enable_auto_save = False
            else:
                if result_auto_save[0][0] == "True":
                    # 初始化一个全局变量, 用于判断是否开启自动保存
                    self.enable_auto_save = True
                    # 开启自动保存 5秒后执行
                    self.after(5000, lambda: self._exec_auto_save(auto=True))
                    logger.success(
                        f"自动保存已开始运行, 运行间隔{self.auto_save_time}秒"
                    )
                else:
                    # 没开启自动保存, 跳过
                    self.enable_auto_save = False
                    logger.warning("自动保存未开启, 跳过运行自动保存")

    def _on_drop(self, files):
        """
        文件拖拽处理
        :param files: 文件列表
        """
        # 检查文件数量
        if len(files) > 1:
            # 如果文件数量大于1, 则弹出提示框
            msg.showwarning("警告", "每次只能打开一个文件")
            logger.warning("用户拖拽打开多个文件, 已取消")
            return

        # 获取文件列表元素
        file_path = files[0].decode("gbk")

        # 检查拖拽进来是不是目录
        if os.path.isdir(file_path):
            # 如果是目录, 则弹出提示框
            msg.showwarning("警告", "不能打开目录")
            logger.warning("用户拖拽打开目录, 已取消")
            return

        # 检查文件后缀
        if not file_path.endswith(".go"):
            # 如果不是go文件, 则弹出提示框
            msg.showwarning("警告", "只能打开go文件")
            logger.warning("用户拖拽打开非go文件, 已取消")
            return

        # 检查一下Text组件是否为空
        if self.main_text.get("1.0", tk.END).strip() != "":
            # 如果不为空, 则弹出提示框
            msg.showwarning("警告", "当前文件未保存, 请先保存")
            logger.warning("用户拖拽打开文件, 当前文件未保存, 已取消")
            return

        # 设置文件名
        file_name = os.path.basename(file_path)

        # 设置窗口标题
        self.title(f"{file_name} - GoLite")

        # 打开文件处理
        try:
            # 打开文件并读取内容
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                logger.info(f"文件 {file_path} 成功打开,编码格式为UTF-8")
        except UnicodeDecodeError:
            # 如果文件编码格式不是UTF-8, 则使用GBK编码格式打开文件
            try:
                logger.warning("文件编码不是UTF-8, 尝试使用GBK编码格式打开文件")
                with open(file_path, "r", encoding="gbk") as file:
                    content = file.read()
                    logger.info(f"文件 {file_path} 成功打开,编码格式为GBK")
            except UnicodeDecodeError:
                logger.error("打开文件时发生错误, 文件编码不是UTF-8或GBK")
                return
        except Exception as e:
            logger.error(f"打开文件时发生错误: {e}")
            return

        # 将文件内容插入到Text组件中
        self.main_text.delete("1.0", tk.END)
        logger.info(f"文件打开成功, 正在清空Text组件...")
        self.main_text.insert("1.0", content)
        logger.info(f"文件 {file_path} 成功打开,内容已插入到Text组件中")

        # 设置Text组件的焦点
        self.main_text.focus_set()
        logger.info("设置Text组件的焦点...")

        # 设置文件路径
        self.file_path = file_path
        logger.debug(f"文件路径已设置为 {file_path}")

        # 打开新文件时, 开启语法高亮
        self.hl_sx = True

        # 渲染语法高亮
        self._highlight_syntax()

        # 设置文件保存状态为未保存
        self.is_save = False

    def _showPopupMenu(self, event):
        """
        右键菜单
        :param event: 事件对象
        :return: None
        """
        self.popupmenu.post(event.x_root, event.y_root)

    def _undoJob(self):
        """
        撤销undo方法
        """
        try:
            self.main_text.edit_undo()
        except:
            logger.warning("先前未有动作")
            msg.showwarning("警告", "先前未有动作")

    # 重做redo方法
    def _redoJob(self):
        """
        重做redo方法
        """
        try:
            self.main_text.edit_redo()
        except:
            logger.warning("先前未有动作")
            msg.showwarning("警告", "先前未有动作")

    def _cutJob(self):
        """
        剪切方法
        :return: None
        """
        try:
            self.main_text.clipboard_clear()  # 清除剪贴板
            copyText = self.main_text.get("sel.first", "sel.last")  # 复制选取区域
            self.main_text.clipboard_append(copyText)  # 写入剪贴板
            self.main_text.delete("sel.first", "sel.last")  # 删除选取文字
        except tk.TclError:
            msg.showwarning("警告", "没有选择")
            logger.warning("没有选择")
        except Exception as e:
            logger.error(f"剪切时发生错误: {e}")
            msg.showwarning("警告", "剪切时发生错误")
        else:
            logger.success("剪切成功")

    def _copyJob(self):
        """
        复制方法
        :return: None
        """
        try:
            self.main_text.clipboard_clear()  # 清除剪贴板
            copyText = self.main_text.get("sel.first", "sel.last")  # 复制选取区域
            self.main_text.clipboard_append(copyText)  # 写入剪贴板
        except tk.TclError:
            msg.showwarning("警告", "没有选择")
            logger.warning("没有选择")
        except Exception as e:
            logger.error(f"复制时发生错误: {e}")
            msg.showwarning("警告", "复制时发生错误")
        else:
            logger.success("复制成功")

    def _pasteJob(self):
        """
        粘贴方法
        :return: None
        """
        try:
            copyText = self.main_text.clipboard_get()  # 读取剪贴板内容
            self.main_text.insert("insert", copyText)  # 插入内容
        except tk.TclError:
            msg.showwarning("警告", "剪贴板没有数据")
            logger.warning("剪贴板没有数据")
        except Exception as e:
            logger.error(f"粘贴时发生错误: {e}")
            msg.showwarning("警告", "粘贴时发生错误")
        else:
            logger.success("粘贴成功")

    def _new_file(self):
        """
        新建文件
        """
        try:
            logger.info("正在新建文件...")

            # 设置文件名
            self.file_name = "Untitled"
            logger.info("设置文件名...")

            # 设置窗口标题
            self.title(f"{self.file_name} - GoLite")
            logger.info("设置窗口标题为 {self.file_name} - GoLite")

            # 清空Text组件的内容
            self.main_text.delete("1.0", tk.END)
            logger.info("清空Text组件的内容...")

            # 设置Text组件的焦点
            self.main_text.focus_set()
            logger.info("设置Text组件的焦点...")

        except Exception as e:
            logger.error(f"新建文件时发生错误: {e}")
        else:
            logger.success("新建文件成功!")
            # 设置文件是否保存为False
            self.is_save = False
            # 设置文件路径
            self.file_path = None
            # 清理code_history表
            self._exec_sql("DELETE FROM code_history", ())

    def _open_file(self):
        # 打开文件对话框, 选择要打开的文件
        file_path = fdl.askopenfilename(
            defaultextension=".go",
            filetypes=[("Go files", "*.go"), ("All files", "*.*")],
            # initialfile="新建文件.go",
            initialdir=os.path.join(os.path.expanduser("~"), "Desktop"),
            title="打开文件",
        )
        if file_path:
            # 检查文件是否以".go"结尾
            if not file_path.endswith(".go"):
                msg.showerror("错误", f"文件不是以'.go'结尾: \n{file_path}")
                logger.error(f"文件不是以'.go'结尾: \n{file_path}")
                return

            # 设置文件名
            self.file_name = os.path.basename(file_path)

            # 设置窗口标题
            self.title(f"{self.file_name} - GoLite")

            try:
                # 打开文件并读取内容
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    logger.info(f"文件 {file_path} 成功打开,编码格式为UTF-8")
            except UnicodeDecodeError:
                # 如果文件编码格式不是UTF-8, 则使用GBK编码格式打开文件
                try:
                    logger.warning("文件编码不是UTF-8, 尝试使用GBK编码格式打开文件")
                    with open(file_path, "r", encoding="gbk") as file:
                        content = file.read()
                        logger.info(f"文件 {file_path} 成功打开,编码格式为GBK")
                except UnicodeDecodeError:
                    logger.error("打开文件时发生错误, 文件编码不是UTF-8或GBK")
                    return
            except Exception as e:
                logger.error(f"打开文件时发生错误: {e}")
                return

            # 将文件内容插入到Text组件中
            self.main_text.delete("1.0", tk.END)
            logger.info(f"文件打开成功, 正在清空Text组件...")
            self.main_text.insert("1.0", content)
            logger.info(f"文件 {file_path} 成功打开,内容已插入到Text组件中")

            # 设置Text组件的焦点
            self.main_text.focus_set()
            logger.info("设置Text组件的焦点...")

            # 设置文件路径
            self.file_path = file_path
            logger.info(f"文件路径已设置为 {file_path}")

            # 打开新文件时, 开启语法高亮
            self.hl_sx = True

            # 渲染语法高亮
            self._highlight_syntax()

            # 设置文件保存状态为未保存
            self.is_save = False
        else:
            logger.info("用户取消了打开文件!")

    def _save_file(self):
        # 获取Text组件中的内容
        content = self.main_text.get("1.0", tk.END)
        # 判断Text组件是否为空
        if content.strip() == "":
            logger.info("Text组件为空, 无需保存文件!")
            msg.showinfo("提示", "Text组件为空, 无需保存文件!")
            return
        # 判断是否已经保存过文件
        if self.file_path is None:
            # 保存文件对话框, 选择要保存的文件
            file_path = fdl.asksaveasfilename(
                defaultextension=".go",
                filetypes=[("Go files", "*.go"), ("All files", "*.*")],
                initialfile="新建文件.go",
                initialdir=os.path.join(os.path.expanduser("~"), "Desktop"),
                title="保存文件",
            )
        else:
            # 如果已经保存过文件, 则直接保存
            file_path = self.file_path
        # 判断是否选择了文件
        if file_path:
            try:
                # 检查文件是否以".go"结尾
                if not file_path.endswith(".go"):
                    msg.showerror("错误", f"文件不是以'.go'结尾: \n{file_path}")
                    logger.error(f"文件不是以'.go'结尾: \n{file_path}")
                    return

                # 将内容保存到文件中
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)
            except Exception as e:
                logger.error(f"保存文件时发生错误: \n{e}")
                msg.showerror("错误", f"保存文件时发生错误: \n{e}")
            else:
                logger.info(f"文件 {file_path} 成功保存,编码格式为UTF-8")

                # 更新文件名
                self.file_name = os.path.basename(file_path)

                # 更新窗口标题
                self.title(f"{self.file_name} - GoLite")

                # 更新文件路径
                self.file_path = file_path

                # 设置文件保存状态为已保存
                self.is_save = True

                # 清理code_history表
                self._exec_sql("DELETE FROM code_history", ())

                # 获取最后一行的索引
                last_line_index = self.main_text.index("end-1c")

                # 分割索引字符串，获取行号
                last_line_number = int(last_line_index.split(".")[0])

                # 如果文件行数大于600, 则关闭语法高亮
                if last_line_number > 600:
                    logger.warning("文件行数过多, 已关闭渲染语法!")
                    # 关闭语法高亮
                    self.hl_sx = False
                else:
                    # 开启语法高亮
                    self.hl_sx = True

                # 显示提示信息
                msg.showinfo("提示", f"文件 {self.file_name} 成功保存")
        else:
            logger.info("用户取消了保存文件!")

    def _save_as_file(self):
        # 获取Text组件中的内容
        content = self.main_text.get("1.0", tk.END)
        # 判断Text组件是否为空
        if content.strip() == "":
            logger.info("Text组件为空, 无需保存文件!")
            msg.showinfo("提示", "Text组件为空, 无需保存文件!")
            return
        # 保存文件对话框, 选择要保存的文件
        file_path = fdl.asksaveasfilename(
            defaultextension=".go",
            filetypes=[("Go files", "*.go"), ("All files", "*.*")],
            initialfile="新建文件.go",
            initialdir=os.path.join(os.path.expanduser("~"), "Desktop"),
            title="另存为",
        )
        # 判断是否选择了文件
        if file_path:
            try:
                # 检查文件是否以".go"结尾
                if not file_path.endswith(".go"):
                    msg.showerror("错误", f"文件不是以'.go'结尾: \n{file_path}")
                    logger.error(f"文件不是以'.go'结尾: \n{file_path}")
                    return

                # 将内容保存到文件中
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)
            except Exception as e:
                logger.error(f"另存为文件时发生错误: \n{e}")
                msg.showerror("错误", f"另存为文件时发生错误: \n{e}")
            else:
                logger.info(f"文件 {file_path} 成功保存,编码格式为UTF-8")
                # 更新文件名
                self.file_name = os.path.basename(file_path)

                # 更新窗口标题
                self.title(f"{self.file_name} - GoLite")

                # 更新文件路径
                self.file_path = file_path

                # 设置文件保存状态为已保存
                self.is_save = True

                # 清理code_history表
                self._exec_sql("DELETE FROM code_history", ())

                # 获取最后一行的索引
                last_line_index = self.main_text.index("end-1c")

                # 分割索引字符串，获取行号
                last_line_number = int(last_line_index.split(".")[0])

                # 如果文件行数大于600, 则关闭语法高亮
                if last_line_number > 600:
                    logger.warning("文件行数过多, 已关闭渲染语法!")
                    # 关闭语法高亮
                    self.hl_sx = False
                else:
                    # 开启语法高亮
                    self.hl_sx = True

                # 显示提示信息
                msg.showinfo("提示", f"文件 {self.file_name} 成功保存")
        else:
            logger.info("用户取消了另存为文件!")

    def _init_log(self, log_path: str = r".\logs\app.log"):
        # 注册日志
        try:
            logger.add(
                log_path,
                level="INFO",
                filter="",
                colorize=False,
                backtrace=True,
                diagnose=False,
                enqueue=True,
                catch=False,
                rotation="1 MB",
                retention="7 days",
                compression="zip",
                delay=True,
                watch=True,
                encoding="utf-8",
            )
        except Exception as e:
            try:
                with open("error.log", "w", encoding="utf-8") as f:
                    f.write(f"日志注册失败: \n{e}")
                    f.write("程序退出...")
            except Exception as e:
                print("日志注册失败, 请检查日志路径是否正确", e)
            finally:
                sys.exit(1)
        else:
            logger.info("日志注册成功")
            logger.info("程序开始运行...")

    def _exec_cmd(self, cmd: list, return_output: bool = False) -> list:
        """
        执行命令并根据需要返回输出
        :param cmd: 命令和参数的列表或字符串
        :param return_output: 是否返回命令的输出，默认为 False
        :return: 标准输出或错误输出, 返回一个列表, 第一个元素是状态，第二个元素是内容
        """
        try:
            result = sp.run(
                cmd,
                # shell=True if isinstance(cmd, str) else False,
                shell=True,
                stderr=sp.PIPE,
                stdout=sp.PIPE,
                # timeout=5,
                universal_newlines=True,
                check=True,
                encoding="utf-8",
            )
        # except sp.TimeoutExpired as e:
        #    print(f"命令执行超时: {e}")
        #    return None
        except sp.CalledProcessError as e:
            logger.error(f"命令执行失败: \n{e}")
            return (
                [False, e.stderr]
                if return_output
                else [
                    None,
                ]
            )
        except Exception as e:
            logger.error(f"执行命令时出现错误: \n{e}")
            return (
                [False, e.stderr]
                if return_output
                else [
                    None,
                ]
            )
        else:
            logger.success(f"命令执行成功,以下是输出结果: \n{result.stdout}")
            return (
                [True, result.stdout]
                if return_output
                else [
                    None,
                ]
            )

    def _quit_program(self):
        """
        退出程序
        """
        logger.debug(self.is_save)

        # 如果未编辑过文件, 直接关闭窗口
        if self.is_save is None:
            # 关闭窗口
            logger.info("程序退出...")
            self.quit()
            # 提前返回, 防止后面的代码执行
            return

        # 编辑过文件, 则检查文件是否保存
        if not self.is_save:
            result = msg.askyesnocancel("退出", "代码还未保存, 是否保存?")
            # 检查用户选择
            if result:
                # 调用保存文件的方法
                self._save_file()
            elif result is None:
                logger.info("用户选择了取消退出!")
                return
            else:
                # 用户选择了不保存文件, 退出程序
                logger.info("用户选择了退出不保存的文件!")

        # 关闭窗口
        logger.info("程序退出...")
        self.quit()

    def _compiler_code(self):
        """
        编译代码
        """

        def make_code(output_file: str, source_file: str):
            """
            编译代码
            """
            logger.debug(f"开始在后台编译文件: {source_file}")
            # 执行编译命令
            result = self._exec_cmd(
                cmd=[go_bin, "build", "-o", output_file, source_file],
                return_output=True,
            )
            # 检查编译结果
            if result[0]:
                logger.success(f"编译成功: \n{output_file}")
                msg.showinfo("编译成功", f"编译成功: \n{output_file}")
                self.title(f"{self.file_name} - GoLite")
            else:
                logger.error(f"编译失败: \n{result[1]}")
                msg.showerror("编译失败", f"编译失败: \n{result[1]}")
                self.title(f"{self.file_name} - GoLite")

        # 获取工作空间路径
        workspace_path = self.GOPATH
        if workspace_path is None:
            msg.showerror("错误", "请先设置工作空间")
            logger.error("请先设置工作空间")
            return

        # 获取GO编译器根目录
        if self.GOROOT is None:
            msg.showerror("错误", "请先设置GO编译器根目录")
            logger.error("请先设置GO编译器根目录")
            return
        go_root = self.GOROOT

        # 获取GO编译器可执行文件路径
        go_bin = os.path.join(go_root, "go.exe")

        # 检查源码文件是否已经打开
        if self.file_path is None:
            msg.showerror("错误", "请先打开源码文件")
            logger.error("请先打开源码文件")
            return

        # 检查源码文件是否存在
        if not os.path.isfile(self.file_path):
            logger.error(f"源码文件不存在: \n{self.file_path}")
            msg.showerror("错误", f"源码文件不存在: \n{self.file_path}")
            return

        # 检查源码文件是否以".go"结尾
        if not self.file_path.endswith(".go"):
            logger.error(f"源码文件不是以'.go'结尾: \n{self.file_path}")
            msg.showerror("错误", f"源码文件不是以'.go'结尾: \n{self.file_path}")
            return

        # 判断GO编译器可执行文件是否存在
        if not os.path.isfile(go_bin):
            logger.error(f"GO编译器可执行文件不存在: \n{go_bin}")
            msg.showerror("错误", f"GO编译器可执行文件不存在: \n{go_bin}")
            return

        # 合并输出路径, 并判断是否存在
        if not os.path.isdir(workspace_path):
            logger.error(f"工作空间路径不存在: \n{workspace_path}")
            msg.showerror("错误", f"工作空间路径不存在: \n{workspace_path}")
            return
        else:
            logger.info(f"工作空间路径: \n{workspace_path}")
            output_file = os.path.join(
                workspace_path, f'{self.file_name.rsplit(".go")[0]}.exe'
            )
            logger.info(f"编译输出文件路径: \n{output_file}")
            # 判断输出文件是否冲突
            if os.path.isfile(output_file):
                logger.error(f"目标编译输出文件已存在: \n{output_file}")
                msg.showerror("错误", f"目标编译输出文件已存在: \n{output_file}")
                # 询问用户是否清除
                if not msg.askokcancel(
                    "警告", f"目标编译输出文件已存在: \n{output_file}\n是否清除?"
                ):
                    logger.info("用户取消了清除操作")
                    return
                else:
                    logger.info("用户确认了清除操作")
                    os.remove(output_file)
                    logger.info(f"已清除目标编译输出冲突文件: \n{output_file}")
        # 设置窗口标题
        self.title(f"编译中, 请勿关闭窗口... - GoLite")
        # 执行编译命令
        run_code = thd.Thread(
            target=make_code,
            args=(output_file, self.file_path),
            daemon=True,
            name="make_code",
        )

        # 判断是否已经在运行
        if run_code.is_alive():
            logger.error("编译任务已经在运行")
            msg.showerror("错误", "编译任务已经在运行")
            return

        # 启动线程
        run_code.start()

    def _run_code(self):
        """
        运行代码
        """

        def main_run():
            logger.debug(f"运行代码模块: 开始运行{self.file_path}")
            # 执行运行命令
            try:
                self.title(f"运行中... - {self.file_name} - GoLite")
                # 执行命令, 先切换到工作空间目录, 然后再运行代码
                sp.Popen(
                    [
                        "powershell",
                        "-NoLogo",
                        "-Command",
                        f"cd {workspace_path};{go_bin} run {self.file_path};read-host -Prompt '按任意键退出'",
                    ],
                    creationflags=sp.CREATE_NEW_CONSOLE,
                )
            except Exception as e:
                logger.error(f"运行失败原因: \n{e}")
                msg.showerror("错误", f"运行失败: \n{e}")
                self.title(f"{self.file_name} - GoLite")
            else:
                logger.debug(f"运行结束: {self.file_path}")
                self.title(f"运行结束 - {self.file_name} - GoLite")

        # 检查文件是否保存
        if not self.is_save:
            msg.showerror("错误", "请先保存文件")
            logger.error("请先保存文件")
            return

        # 检查文件是否打开
        if self.file_path is None:
            msg.showerror("错误", "请先打开文件")
            logger.error("请先打开文件")
            return

        # 检查保存的文件是否存在
        if not os.path.isfile(self.file_path):
            msg.showerror("错误", f"保存的文件不存在: \n{self.file_path}")
            logger.error(f"保存的文件不存在: \n{self.file_path}")
            return

        # 检查文件是否以".go"结尾
        if not self.file_path.endswith(".go"):
            msg.showerror("错误", f"文件不是以'.go'结尾: \n{self.file_path}")
            logger.error(f"文件不是以'.go'结尾: \n{self.file_path}")
            return

        # 获取工作空间路径
        workspace_path = self.GOPATH
        if workspace_path is None:
            msg.showerror("错误", "请先设置工作空间")
            logger.error("请先设置工作空间")
            return

        # 检查工作空间路径是否存在
        if not os.path.isdir(workspace_path):
            msg.showerror("错误", f"工作空间路径不存在: \n{workspace_path}")
            logger.error(f"工作空间路径不存在: \n{workspace_path}")
            return

        # 获取GO编译器根目录
        if self.GOROOT is None:
            msg.showerror("错误", "请先设置GO编译器根目录")
            logger.error("请先设置GO编译器根目录")
            return
        else:
            go_root = self.GOROOT
            # 获取GO编译器可执行文件路径
            go_bin = os.path.join(go_root, "go.exe")

        # 判断GO编译器可执行文件是否存在
        if not os.path.isfile(go_bin):
            logger.error(f"GO编译器可执行文件不存在: \n{go_bin}")
            msg.showerror("错误", f"GO编译器可执行文件不存在: \n{go_bin}")
            return

        # 提示用户正在拉起终端运行代码
        logger.debug(f"正在拉起终端运行代码: {self.file_path}")
        self.title(f"正在拉起终端... - {self.file_name} - GoLite")

        # 新建一个线程来运行代码
        run_thd = thd.Thread(target=main_run, daemon=True, name="main_run")

        # 判断线程
        if run_thd.is_alive():
            msg.showwarning("警告", "请先关闭上次运行代码的终端!")
            logger.warning("用户未关闭上次运行代码的终端")
            return
        else:
            # 启动线程
            run_thd.start()
            logger.debug(run_thd.getName())

    def _format_code(self):
        """
        格式化Go代码
        """

        def main_format():
            # 修改窗口标题提示用户
            self.title(f"格式化中... - {self.file_name} - GoLite")

            # 先检查使用的那个工具，然后再检查代码, 如果存在错误则提示用户
            match check_tool_name:
                case "golangci-lint":
                    result = self._exec_cmd(
                        [go_check_tool, "run", self.file_path], return_output=True
                    )
                case "errcheck":
                    result = self._exec_cmd(
                        [go_check_tool, self.file_path], return_output=True
                    )
                case "go vet":
                    result = self._exec_cmd(
                        [go_check_tool, "vet", self.file_path], return_output=True
                    )
                case _:
                    msg.showerror("错误", f"不支持的代码检查工具: \n{check_tool_name}")
                    logger.error(f"不支持的代码检查工具: \n{check_tool_name}")
                    return

            # 检查代码是否存在语法错误
            if not result[0]:
                logger.error(f"{self.file_path} 代码存在语法错误: \n\n{result[1]}")
                # 清空剪贴板
                self.clipboard_clear()
                # 将错误信息写入剪贴板
                self.clipboard_append(result[1])
                # 弹窗提示
                msg.showerror(
                    "错误",
                    f"{self.file_path} 代码存在语法错误, 已添加到剪贴板, 详情如下: \n\n{result[1]}",
                )
                return

            # 调用gofmt命令进行格式化
            result = self._exec_cmd([go_bin, "-w", self.file_path], return_output=True)
            if not result[0]:
                logger.error(f"格式化失败: \n{result[1]}")
                # 清空剪贴板
                self.clipboard_clear()
                # 将错误信息写入剪贴板
                self.clipboard_append(result[1])
                # 弹窗提示
                msg.showerror(
                    "错误", f"格式化失败, 错误已添加到剪贴板, 详情如下: \n{result[1]}"
                )
                return

            # 更新Text组件的内容
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = f.read()
                    self.main_text.delete("1.0", "end")
                    logger.debug("清空Text组件旧内容...")
                    self.main_text.insert("1.0", data)
                    logger.debug("更新Text组件格式化后的新内容...")
            except Exception as e:
                # 日志记录错误信息
                logger.error("更新Text组件内容失败: \n{e}")
                msg.showerror("错误", f"更新Text组件内容失败: \n{e}")

                # 修改窗口标题
                self.title(f"{self.file_name} - GoLite")
                return

            # 更新Text组件的语法高亮
            self._highlight_syntax()

            # 修改窗口标题
            self.title(f"{self.file_name} - GoLite")

            # 显示提示信息
            logger.success("格式化代码成功")
            msg.showinfo("成功", "格式化代码成功")

        # 检查文件是否保存
        if not self.is_save:
            msg.showerror("错误", "请先保存文件")
            logger.error("请先保存文件")
            return

        # 检查文件是否保存
        if self.file_path is None:
            msg.showerror("错误", "请先保存文件")
            logger.error("请先保存文件")
            return

        # 获取GO编译器根目录
        if self.GOROOT is None:
            msg.showerror("错误", "请先设置GO编译器根目录")
            logger.error("请先设置GO编译器根目录")
            return
        else:
            go_root = self.GOROOT

        # 获取 代码检查工具 可执行文件
        result = self._exec_sql(
            "select value from system_cfg where name = ?", ("check_tools",), True
        )
        logger.debug(f"代码检查工具: \n{result}")
        if len(result) == 0:
            msg.showerror("错误", "请先设置代码检查工具")
            logger.error("请先设置代码检查工具")
            return
        else:
            logger.debug(f"代码检查工具: \n{result[0][0]}")
            # 设置 代码检查工具 名称
            check_tool_name = result[0][0]
            match result[0][0]:
                case "golangci-lint":
                    # 获取 golangci-lint 可执行文件
                    go_check_tool = r".\lib\golangci-lint.exe"
                    # 判断 代码检查工具 可执行文件是否存在
                    if not os.path.isfile(go_check_tool):
                        logger.error(
                            f"golangci-lint可执行文件不存在: \n{go_check_tool}"
                        )
                        msg.showerror(
                            "错误", f"golangci-lint可执行文件不存在: \n{go_check_tool}"
                        )
                        return
                case "errcheck":
                    # 获取 errcheck 可执行文件
                    go_check_tool = r".\lib\errcheck.exe"
                    # 判断 代码检查工具 可执行文件是否存在
                    if not os.path.isfile(go_check_tool):
                        logger.error(
                            f"golangci-lint可执行文件不存在: \n{go_check_tool}"
                        )
                        msg.showerror(
                            "错误", f"golangci-lint可执行文件不存在: \n{go_check_tool}"
                        )
                        return
                case "go vet":
                    # 获取 go vet 可执行文件
                    go_check_tool = os.path.join(go_root, "go.exe")
                    # 判断GO编译器可执行文件是否存在
                    if not os.path.isfile(go_check_tool):
                        logger.error(f"GO编译器可执行文件不存在: \n{go_check_tool}")
                        msg.showerror(
                            "错误", f"GO编译器可执行文件不存在: \n{go_check_tool}"
                        )
                        return
                case _:
                    msg.showerror("错误", f"不支持的代码检查工具: \n{result[0][0]}")
                    logger.error(f"不支持的代码检查工具: \n{result[0][0]}")
                    return

        # 获取GO编译器可执行文件路径
        go_bin = os.path.join(go_root, "gofmt.exe")

        # 判断GO编译器可执行文件是否存在
        if not os.path.isfile(go_bin):
            logger.error(f"GO编译器可执行文件不存在: \n{go_bin}")
            msg.showerror("错误", f"GO编译器可执行文件不存在: \n{go_bin}")
            return

        # 检查源码文件是否存在
        if not os.path.isfile(self.file_path):
            msg.showerror("错误", f"源码文件不存在: \n{self.file_path}")
            logger.error(f"源码文件不存在: \n{self.file_path}")
            return

        # 格式化前先设置Text组件不可编辑
        self.main_text.configure(state="disabled")

        # 新线程执行代码格式化
        run_format = thd.Thread(target=main_format, daemon=True, name="main_format")

        # 判断线程
        if run_format.is_alive():
            msg.showwarning("警告", "代码格式化任务已经在运行中")
            logger.warning("代码格式化任务已经在运行中")
            return

        run_format.start()

        # 格式化后再设置Text组件可编辑
        self.main_text.configure(state="normal")

    def _create_table(self, db_path: str = r"./data/GoLite.db"):
        """
        创建数据库
        系统配置表: id name value
        """
        try:
            if not os.path.isdir("./data"):
                raise FileNotFoundError("数据库目录不存在")
            # 创建数据库文件
            with sqlite3.connect(db_path) as data_connect:
                # 创建游标
                data_cursor = data_connect.cursor()
                # 系统配置存储表
                data_sql = """
                create table if not exists system_cfg(
                    id integer primary key autoincrement,
                    name Text not null,
                    value Text not null
                );
                create table if not exists code_history(
                    id integer primary key autoincrement,
                    code Text not null,
                    create_time Text not null
                );
                """
                data_cursor.executescript(data_sql)
                data_connect.commit()
        except Exception as e:
            logger.error(f"数据库初始化失败: \n{e}")
            return None
        else:
            logger.success("数据库初始化成功")
            return db_path

    def _exec_sql(self, sql: str, sql_param: tuple, return_data: bool = False):
        """
        数据库操作: 增删改查
        :param sql: sql语句
        :param sql_param: sql语句占位符的值(元组,)
        :param return_data: 是否返回数据
        :return: 返回一个列表包着元组
        """
        try:
            if not os.path.isfile(self.db_path):
                raise FileNotFoundError("数据库文件不存在")
            with sqlite3.connect(self.db_path) as data_connect:
                # 创建游标
                data_cursor = data_connect.cursor()
                # 检查SQL语句是否为空
                if sql.strip() == "":
                    raise ValueError("SQL语句不能为空")
                # 执行sql
                data_cursor.execute(sql, sql_param)
                data_connect.commit()
                if return_data:
                    # 返回数据
                    return data_cursor.fetchall()
                else:
                    # 无需返回数据，表示操作成功
                    return True
        except sqlite3.DatabaseError as e:
            logger.error(f"数据库文件异常或不存在: \n{e}")
            return False
        except Exception as e:
            logger.error(f"数据库SQL执行异常: \n{e}")
            return False
        finally:
            logger.info(f"数据库执行SQL: {sql}")

    def _settings(self):
        """
        系统设置
        """

        def set_go_root(btn: bool = False):
            """
            设置GO编译器根目录
            """
            # 按钮触发
            if btn:
                # 打开文件夹选择器
                go_root = fdl.askdirectory()
                # 检查是否以bin结尾，如果不是就提示用户
                if not go_root.endswith("bin"):
                    result = msg.askokcancel(
                        "警告", "您选择的目录似乎不是GO编译器的bin目录, 确定要设置吗?"
                    )
                    if result:
                        logger.warning("用户设置了非GO编译器的bin目录")
                    else:
                        logger.info("用户取消了设置GO编译器根目录")
                        return
                # 设置GO编译器根目录
                if go_root:
                    self.GOROOT = go_root
                    logger.info(f"设置GO编译器根目录: {go_root}")
                    result_go_root = self._exec_sql(
                        "select value from system_cfg where name=?", ("go_root",), True
                    )
                    if len(result_go_root) == 0:
                        self._exec_sql(
                            "insert into system_cfg(name, value) values(?, ?)",
                            ("go_root", go_root),
                        )
                        self.goroot_path_var = ctk.StringVar(value=go_root)
                        logger.info(f"设置GO编译器根目录成功: {go_root}")
                        # 关闭窗口
                        self.settings_window.destroy()
                        # 重新打开窗口
                        self._settings()
                    else:
                        self._exec_sql(
                            "update system_cfg set value=? where name=?",
                            (go_root, "go_root"),
                        )
                        self.goroot_path_var = ctk.StringVar(value=go_root)
                        logger.info(f"更新GO编译器根目录成功: {go_root}")
                        # 关闭窗口
                        self.settings_window.destroy()
                        # 重新打开窗口
                        self._settings()
                else:
                    logger.info("取消设置GO编译器根目录")
            # 默认触发
            else:
                go_root = self._exec_sql(
                    "select value from system_cfg where name=?", ("go_root",), True
                )
                if len(go_root) == 0:
                    self.GOROOT = None
                    self.goroot_path_var = ctk.StringVar(value="暂未设置")
                    logger.info(f"未获取到GO编译器根目录: {go_root}")
                else:
                    self.GOROOT = go_root[0][0]
                    self.goroot_path_var = ctk.StringVar(value=go_root[0][0])
                    logger.info(f"获取GO编译器根目录: {self.GOROOT}")

        def set_go_path(value: str = "", btn: bool = False):
            """
            设置GO工作路径
            """
            if btn:
                go_path = fdl.askdirectory()
                if go_path:
                    self.GOROOT = go_path
                    logger.info(f"设置GO工作空间: {go_path}")
                    result_go_path = self._exec_sql(
                        "select value from system_cfg where name=?", ("go_path",), True
                    )
                    if len(result_go_path) == 0:
                        self._exec_sql(
                            "insert into system_cfg(name, value) values(?, ?)",
                            ("go_path", go_path),
                        )
                        self.gopath_path_var = ctk.StringVar(value=go_path)
                        logger.info(f"设置GO工作空间成功: {go_path}")
                        # 关闭窗口
                        self.settings_window.destroy()
                        # 重新打开窗口
                        self._settings()
                    else:
                        self._exec_sql(
                            "update system_cfg set value=? where name=?",
                            (go_path, "go_path"),
                        )
                        self.gopath_path_var = ctk.StringVar(value=go_path)
                        logger.info(f"更新GO工作空间成功: {go_path}")
                        # 关闭窗口
                        self.settings_window.destroy()
                        # 重新打开窗口
                        self._settings()
                else:
                    logger.info("取消设置GO工作空间")
            else:
                go_path = self._exec_sql(
                    "select value from system_cfg where name=?", ("go_path",), True
                )
                if len(go_path) == 0:
                    self.GOPATH = None
                    self.gopath_path_var = ctk.StringVar(value="暂未设置")
                    logger.info(f"未获取到GO工作空间: {go_path}")
                else:
                    self.GOPATH = go_path[0][0]
                    self.gopath_path_var = ctk.StringVar(value=go_path[0][0])
                    logger.info(f"获取到GO工作空间: {self.GOPATH}")

        def is_read(btn: bool = False):
            """
            是否只读
            """
            # 判断是否是按钮触发的
            if not btn:
                if self.main_text._textbox.cget("state") == "normal":
                    # 设置为未选中
                    self.is_read = ctk.StringVar(value="off")
                    return
                elif self.main_text._textbox.cget("state") == "disabled":
                    # 设置为选中
                    self.is_read = ctk.StringVar(value="on")
                    return

            # 根据按钮状态切换Text组件的状态
            if self.main_text._textbox.cget("state") == "normal":
                self.main_text.configure(state="disabled")
                self.is_read = ctk.StringVar(value="on")
            elif self.main_text._textbox.cget("state") == "disabled":
                self.main_text.configure(state="normal")
                self.is_read = ctk.StringVar(value="off")

            # 主窗口标题切换
            logger.info(
                f"Text组件的状态已切换为: {self.main_text._textbox.cget('state')}"
            )
            self.title(f"GoLite - {self.main_text._textbox.cget('state')}")
            logger.info(f"窗口标题已切换为: {self.title()}")

        def set_font_size(value: str = "", btn: bool = False):
            """
            设置字体大小
            """
            # 设置默认字体大小
            if btn:
                var_size = self._exec_sql(
                    "select value from system_cfg where name=?", ("font_size",), True
                )
                self.var_str_size = ctk.StringVar(value=var_size[0][0])
                logger.info(f"获取数据库字体大小: {var_size[0][0]}")
            else:
                # 更新Text组件字体大小
                self.main_text_font.configure(size=int(value))
                logger.info(f"设置Text组件字体大小: {value}")
                # 更新数据库中的值
                self._exec_sql(
                    "update system_cfg set value=? where name=?", (value, "font_size")
                )
                # 更新字体大小变量显示
                self.var_str_size = int(value)
                logger.info(f"设置分段按钮字体大小: {value}")

        def set_font_family(value: str = "", btn: bool = False):
            """
            设置字体族
            """
            # 通过按钮触发
            if btn:
                # 更新Text组件字体族
                self.main_text_font.configure(family=value)
                # 更新字体变量显示
                self.var_str_family = value
                logger.info(f"设置Text组件字体族: {value}")
                # 更新数据库中的值
                self._exec_sql(
                    "update system_cfg set value=? where name=?", (value, "font_family")
                )
                # 日志记录
                logger.info(f"设置分段按钮字体族: {value}")
            # 设置默认字体
            else:
                var_family = self._exec_sql(
                    "select value from system_cfg where name=?", ("font_family",), True
                )
                self.var_str_family = ctk.StringVar(value=var_family[0][0])
                logger.info(f"获取数据库字体族为: {var_family[0][0]}")

        def auto_save(btn: bool = False):
            """
            是否自动保存
            """
            # 判断是否通过按钮触发
            if not btn:
                result_is_save = self._exec_sql(
                    "select value from system_cfg where name=?", ("auto_save",), True
                )
                if len(result_is_save) == 0:
                    logger.info(f"未获取到自动保存状态: {result_is_save}")
                    self._exec_sql(
                        "insert into system_cfg(name, value) values(?,?)",
                        ("auto_save", "False"),
                    )
                    # 设置自动保存状态
                    self.is_auto_save = ctk.StringVar(value="False")
                    logger.info(f"设置自动保存状态: {self.is_auto_save.get()}")
                    # 设置全局变量
                    self.enable_auto_save = False
                else:
                    logger.info(f"获取到自动保存状态: {result_is_save[0][0]}")
                    self.is_auto_save = ctk.StringVar(value=result_is_save[0][0])
                    logger.info(f"设置自动保存状态: {self.is_auto_save.get()}")
                    # 设置全局变量
                    if result_is_save[0][0] == "True":
                        self.enable_auto_save = True
                    elif result_is_save[0][0] == "False":
                        self.enable_auto_save = False
            else:
                # 通过按钮触发
                if self.is_auto_save.get() == "True":
                    result_status = self._exec_sql(
                        "update system_cfg set value=? where name=?",
                        ("True", "auto_save"),
                    )
                    if result_status:
                        # 设置全局变量
                        self.enable_auto_save = True
                        # 运行自动保存, 3秒后运行
                        self.after(3000, lambda: self._exec_auto_save(auto=True))
                        # 日志记录
                        logger.info(
                            f"已开启自动保存任务, 间隔{self.auto_save_time}秒运行"
                        )
                        # 关闭窗口
                        self.settings_window.destroy()
                        # 提示用户
                        msg.showinfo(
                            "提示",
                            f"已开启自动保存任务, 间隔{self.auto_save_time}秒运行",
                        )
                        return
                    else:
                        # 全局变量
                        self.enable_auto_save = False
                        # 日志记录
                        logger.error("开启自动保存失败!")
                        # 关闭窗口
                        self.settings_window.destroy()
                        # 提示用户
                        msg.showerror("错误", "开启自动保存失败!")
                        return
                elif self.is_auto_save.get() == "False":
                    result_status = self._exec_sql(
                        "update system_cfg set value=? where name=?",
                        ("False", "auto_save"),
                    )
                    if result_status:
                        # 设置全局变量
                        self.enable_auto_save = False
                        # 日志记录
                        logger.info("已关闭自动保存功能")
                        # 关闭窗口
                        self.settings_window.destroy()
                        # 提示用户
                        msg.showinfo("提示", "已关闭自动保存功能")
                        return
                    else:
                        # 全局变量
                        self.enable_auto_save = False
                        # 日志记录
                        logger.error("关闭自动保存失败!")
                        # 关闭窗口
                        self.settings_window.destroy()
                        # 提示用户
                        msg.showerror("错误", "关闭自动保存失败!")
                        return

        def set_auto_save_time(value: str = "", btn: bool = False):
            """
            设置自动保存时间
            """
            # 通过按钮触发
            if btn:
                # 判断是否开启自动保存
                if not self.enable_auto_save:
                    logger.warning("自动保存未开启, 无法设置自动保存时间")
                    msg.showerror("错误", "自动保存未开启, 无法设置自动保存时间")
                    # 设置窗口为新焦点
                    self.settings_window.after(
                        150, lambda: self.settings_window.focus_force()
                    )
                    # 再次窗口为焦点
                    self.settings_window.after(
                        300, lambda: self.settings_window.focus_force()
                    )
                    return

                # 设置全局自动保存时间
                self.auto_save_time = value
                logger.debug(f"测试: {value}")
                # 设置数据库自动保存时间
                self._exec_sql(
                    "update system_cfg set value=? where name=?",
                    (value, "auto_save_time"),
                )
                # 设置分段按钮的值
                self.auto_save_time_status = ctk.StringVar(value=value)
                # 日志记录
                logger.debug(f"已设置自动保存时间为: {value}")
            # 设置分段按钮的默认值
            else:
                result_time = self._exec_sql(
                    "select value from system_cfg where name=?",
                    ("auto_save_time",),
                    True,
                )
                if len(result_time) == 0:
                    logger.warning("自动保存时间未设置, 正在设置默认值...")
                    self._exec_sql(
                        "insert into system_cfg (name, value) values (?, ?)",
                        ("auto_save_time", "60"),
                    )
                    self.auto_save_time = "60"
                    self.auto_save_time_status = ctk.StringVar(value="60")
                    logger.success("已设置自动保存时间为默认值: 60")
                else:
                    # 设置全局自动保存时间
                    self.auto_save_time = result_time[0][0]
                    # 设置分段按钮的值
                    self.auto_save_time_status = ctk.StringVar(value=result_time[0][0])
                    logger.success(f"获取数据库自动保存时间: {result_time[0][0]}")

        def set_check_tools(btn: bool = False, value: str = None):
            """
            设置自定义检查工具
            """
            # 通过按钮触发
            if btn:
                # 获取下拉菜单的值
                value_tool = value

                # 更新数据库中的值
                self._exec_sql(
                    "update system_cfg set value=? where name=?",
                    (value_tool, "check_tools"),
                )

                # 日志记录
                logger.debug(f"已设置自定义检查工具为: {value_tool}")

            # 通过页面加载触发
            else:
                # 检查数据库中是否有自定义检查工具
                result = self._exec_sql(
                    "select value from system_cfg where name=?", ("check_tools",), True
                )
                if len(result) == 0:
                    logger.warning("自定义检查工具未设置, 正在设置默认值...")
                    self._exec_sql(
                        "insert into system_cfg (name, value) values (?, ?)",
                        ("check_tools", "go vet"),
                    )
                    # 设置下拉菜单的默认值
                    self.var_str_tool = ctk.StringVar(value="go vet")
                    logger.success("已设置自定义检查工具为默认值: go vet")
                else:
                    # 设置全局自定义检查工具
                    self.check_tools = result[0][0]
                    # 设置下拉菜单的值
                    self.var_str_tool = ctk.StringVar(value=result[0][0])
                    logger.success(f"获取数据库自定义检查工具配置: {result[0][0]}")

        # 检查是否已经打开过设置窗口
        if self.settings_window is not None:
            self.settings_window.destroy()

        # 如果没有打开过设置窗口, 则创建一个新窗口
        self.settings_window = ctk.CTkToplevel(self)  # 确保使用正确的父窗口
        self.settings_window.title("系统设置")

        # 获取父窗口的位置和大小
        # parent_x = self.winfo_x()
        # parent_y = self.winfo_y()
        # parent_width = self.winfo_width()
        # parent_height = self.winfo_height()

        # 设置子窗口的宽度和高度
        child_width = 700
        child_height = 700

        # 设置子窗口居中的位置
        # x = parent_x + (parent_width - child_width) // 2 - 100
        # y = parent_y + (parent_height - child_height) // 2 - 100
        x = 900
        y = 200

        # 设置子窗口的位置
        self.settings_window.geometry(f"{child_width}x{child_height}+{x}+{y}")

        # 设置是否可以调整大小
        self.settings_window.resizable(False, False)

        # 设置窗口为新焦点
        self.settings_window.after(150, lambda: self.settings_window.focus_force())

        # 再次设置窗口为新焦点
        self.settings_window.after(300, lambda: self.settings_window.focus_force())

        # 创建窗口内容 #
        # 设置分段按钮, 设置字体大小
        set_font_size(btn=True)
        set_text_font_size_lab = ctk.CTkLabel(
            self.settings_window,
            text="设置字体大小:",
            font=self.main_text_font,
        )
        set_text_font_size = ctk.CTkSegmentedButton(
            self.settings_window,
            values=["15", "17", "19", "21", "23", "25"],
            # width=200,
            # height=50,
            variable=self.var_str_size,
            command=lambda value: set_font_size(value=value),
        )
        set_text_font_size_lab.place(relx=0.01, rely=0.05, relwidth=0.4, relheight=0.1)
        set_text_font_size.place(relx=0.4, rely=0.05, relwidth=0.55, relheight=0.1)

        # 设置分段按钮, 设置字体族
        set_font_family(btn=False)
        set_text_font_family_lab = ctk.CTkLabel(
            self.settings_window,
            text="设置字体类型:",
            font=self.main_text_font,
        )
        set_text_font_family = ctk.CTkSegmentedButton(
            self.settings_window,
            values=["微软雅黑", "宋体", "楷体", "黑体", "隶书"],
            width=100,
            height=30,
            variable=self.var_str_family,
            command=lambda value: set_font_family(value=value, btn=True),
        )
        set_text_font_family_lab.place(relx=0.01, rely=0.2, relwidth=0.4, relheight=0.1)
        set_text_font_family.place(relx=0.4, rely=0.2, relwidth=0.55, relheight=0.1)

        # 设置分段按钮, 设置自动保存时间间隔
        set_auto_save_time(btn=False)
        set_auto_save_lab = ctk.CTkLabel(
            self.settings_window,
            text="自动保存时间:",
            font=self.main_text_font,
        )
        set_auto_save_sb = ctk.CTkSegmentedButton(
            self.settings_window,
            values=["5", "10", "30", "60", "120", "300"],
            # width=200,
            # height=50,
            variable=self.auto_save_time_status,
            command=lambda value: set_auto_save_time(value=value, btn=True),
        )
        set_auto_save_lab.place(relx=0.01, rely=0.35, relwidth=0.4, relheight=0.1)
        set_auto_save_sb.place(relx=0.4, rely=0.35, relwidth=0.55, relheight=0.1)

        # 显示GoROOT的路径按钮
        set_goroot_btn = ctk.CTkButton(
            self.settings_window,
            text="设置GoROOT路径:",
            font=self.main_text_font,
            command=lambda: set_go_root(btn=True),
        )
        set_goroot_btn.place(relx=0.025, rely=0.52, relwidth=0.35, relheight=0.08)

        # 显示GoROOT的路径标签
        set_go_root(btn=False)
        set_goroot_path_lab = ctk.CTkLabel(
            self.settings_window,
            text="",
            font=self.main_text_font,
            fg_color="#d3d3d3",
            textvariable=self.goroot_path_var,
        )
        set_goroot_path_lab.place(relx=0.4, rely=0.52, relwidth=0.58, relheight=0.08)

        # 显示GoPATH的路径按钮
        set_gopath_btn = ctk.CTkButton(
            self.settings_window,
            text="设置GOPATH路径:",
            font=self.main_text_font,
            command=lambda: set_go_path(btn=True),
        )
        set_gopath_btn.place(relx=0.025, rely=0.65, relwidth=0.35, relheight=0.08)

        # 显示GoPATH的路径标签
        set_go_path(btn=False)
        set_gopath_path_lab = ctk.CTkLabel(
            self.settings_window,
            text="C:\\Go\\bin",
            font=self.main_text_font,
            fg_color="#d3d3d3",
            textvariable=self.gopath_path_var,
        )
        set_gopath_path_lab.place(relx=0.4, rely=0.65, relwidth=0.58, relheight=0.08)

        # 设置代码检查工具的下拉菜单
        set_check_tool_lab = ctk.CTkLabel(
            self.settings_window,
            text="设置代码检查工具:",
            font=self.main_text_font,
        )
        set_check_tool_lab.place(relx=0.01, rely=0.76, relwidth=0.4, relheight=0.1)

        # 设置代码检查工具的下拉菜单
        set_check_tools(btn=False)
        set_check_tool = ctk.CTkComboBox(
            self.settings_window,
            values=["golangci-lint", "errcheck", "go vet"],
            font=self.main_text_font,
            dropdown_font=self.main_text_font,
            button_color="lightblue",
            state="readonly",
            variable=self.var_str_tool,
            command=lambda value: set_check_tools(value=value, btn=True),
        )
        set_check_tool.place(relx=0.4, rely=0.785, relwidth=0.55, relheight=0.055)

        # 是否只读
        is_read(btn=False)
        read_only = ctk.CTkCheckBox(
            self.settings_window,
            text="只读保护",
            font=self.main_text_font,
            command=lambda: is_read(btn=True),
            variable=self.is_read,
            onvalue="on",
            offvalue="off",
        )
        read_only.place(relx=0.6, rely=0.86, relwidth=0.4, relheight=0.1)

        # 是否开启自动保存
        auto_save(btn=False)
        auto_saved = ctk.CTkCheckBox(
            self.settings_window,
            text="自动保存",
            font=self.main_text_font,
            command=lambda: auto_save(btn=True),
            variable=self.is_auto_save,
            onvalue="True",
            offvalue="False",
        )
        auto_saved.place(relx=0.15, rely=0.86, relwidth=0.4, relheight=0.1)

    def _exec_auto_save(self, auto=False):
        """
        自动保存代码到数据库
        :param auto: 是否自动保存, 默认为False
        :return: None
        """
        # 获取自动保存时间
        auto_time = int(self.auto_save_time) * 1000

        # 判断是否运行自动保存
        if not auto:
            # False 表示不运行自动保存
            logger.warning(f"未开启自动保存, 跳过自动保存")
            return

        # 没开启自动保存则跳过
        if not self.enable_auto_save:
            # 日志记录
            logger.warning(f"未开启自动保存, 跳过自动保存")
            # 下次继续运行自动保存 auto_time秒后运行
            self.after(auto_time, lambda: self._exec_auto_save(auto=True))
            return

        # 判断是否开始编辑内容了, 未编辑则跳过
        if self.is_save == None:
            # 日志记录
            logger.warning(f"未开始编辑内容, 跳过自动保存")
            # 下次继续运行自动保存 auto_time秒后运行
            self.after(auto_time, lambda: self._exec_auto_save(auto=True))
            return

        # 判断Text组件是否有内容
        if self.main_text.get(1.0, ctk.END).strip() == "":
            # 日志记录
            logger.warning(f"Text组件内容为空, 跳过自动保存")
            # 下次继续运行自动保存 auto_time秒后运行
            self.after(auto_time, lambda: self._exec_auto_save(auto=True))
            return

        # 判断是否保存, 已保存则跳过
        if self.is_save:
            # 日志记录
            logger.warning(f"已保存内容, 跳过自动保存")
            # 下次继续运行自动保存 auto_time秒后运行
            self.after(auto_time, lambda: self._exec_auto_save(auto=True))
            return

        # 运行自动保存代码
        main_text_data = self.main_text.get(1.0, ctk.END)

        # 清除上一次的自动保存代码
        self._exec_sql("delete from code_history", ())

        # 获取当前时间
        create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        # 保存代码到数据库
        auto_result = self._exec_sql(
            "insert into code_history(code, create_time) values(?,?)",
            (main_text_data, create_time),
            return_data=False,
        )
        if auto_result:
            logger.success(f"自动保存代码成功")
            # 设置保存状态, 已保存
            self.is_save = True
            # 下次继续运行自动保存 auto_time秒后运行
            self.after(auto_time, lambda: self._exec_auto_save(auto=True))
        else:
            logger.error(f"自动保存代码失败")
            # 设置保存状态, 未保存
            self.is_save = False
            # 更新自动保存设置
            self._exec_sql(
                "update system_cfg set value=? where name=?", ("False", "auto_save")
            )
            # 暂时关闭自动保存
            self.is_auto_save = ctk.StringVar(value="False")
            # 提示用户
            msg.showerror(
                "错误", "自动保存代码失败, 已暂时关闭自动保存功能, 请手动保存代码"
            )
            return

    def _show_help(self):
        """
        显示帮助信息
        :return: None
        """
        # 快捷键帮助信息
        help_text = """
                    快捷键帮助信息
                         
        文件操作类：
          Ctrl + o: 打开文件
          Ctrl + s: 保存文件
          Ctrl + n: 新建文件
          Ctrl + j: 另存为 
        
        
        代码操作类：
          Ctrl + r: 运行代码
          Ctrl + b: 编译代码
          Ctrl + f: 格式化代码
          
        
        文本编辑类：
          Ctrl + z: 撤销
          Ctrl + y: 重做
          Ctrl + c: 复制
          Ctrl + v: 粘贴
          Ctrl + x: 剪切
          Ctrl + a: 全选
          ctrl + l: 查找
        
        
        程序操作类：
          Ctrl + g: 打开设置
          Ctrl + q: 退出程序
          Ctrl + h: 帮助信息
        """

        # 判断是否已经打开过帮助窗口
        if self.help_window is not None:
            self.help_window.destroy()

        # 创建帮助窗口
        self.help_window = ctk.CTkToplevel(self)
        self.help_window.title("帮助信息")
        self.help_window.geometry("500x800+900+100")
        self.help_window.resizable(False, False)

        # 创建帮助文本
        help_text_tb = ctk.CTkTextbox(
            self.help_window, wrap="word", font=self.main_text_font
        )
        help_text_tb.place(relx=0, rely=0, relwidth=1, relheight=1)

        # 插入帮助文本
        help_text_tb.insert("1.0", text=help_text)

        # 设置只读
        help_text_tb.configure(state="disabled")

        # 设置窗口为新焦点
        self.after(150, lambda: self.help_window.focus_force())


# 创建应用程序实例
app = GoLite()

if __name__ == "__main__":
    app.mainloop()
