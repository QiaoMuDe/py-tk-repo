import tkinter as tk
from tkinter import ttk, messagebox
import re
import queue
from utils import set_window_icon, center_window, get_custom_font_from_parent

class FindDialog:
    def __init__(self, parent, text_widget, file_path=None, selected_text=""):
        self.parent = parent
        self.text_widget = text_widget
        self.file_path = file_path
        self.selected_text = selected_text  # 接收选中文本
        self.matches = []
        self.current_match_index = -1
        self.is_searching = False  # 标记是否正在进行查找操作
        self.search_thread = None  # 查找线程
        self.search_queue = queue.Queue()  # 用于线程间通信的队列
        self.cancel_search = False  # 取消查找标志
        self._last_search_term = ""  # 上次查找的词
        self.replace_entry = None  # 替换输入框引用

        # 不再使用大文件查找器
        self.large_file_searcher = None

        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("查找和替换")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 设置窗口图标
        set_window_icon(self.dialog)
        
        # 绑定窗口关闭事件，确保关闭时清除所有查找标记
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_dialog_close)

        # 居中显示
        center_window(self.dialog, 500, 360)

        # 创建界面元素
        self.create_widgets()

        # 绑定事件
        self.bind_events()

    def create_widgets(self):
        """创建界面控件"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)

        # 配置主框架的网格权重, 使内容居中
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)

        # 查找内容标签和输入框
        ttk.Label(main_frame, text="查找内容:").grid(
            row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5)
        )
        # 使用最小的多行文本输入框代替单行输入框，提升性能
        # 使用通用函数获取自定义字体配置
        custom_font = get_custom_font_from_parent(self.parent, custom_size=18)
        
        # 创建查找输入框
        if custom_font:
            self.search_entry = tk.Text(main_frame, height=1, width=50, wrap=tk.NONE, font=custom_font)
        else:
            # 直接设置一个默认字体和大小，确保字体大小能够生效
            self.search_entry = tk.Text(main_frame, height=1, width=50, wrap=tk.NONE, font=('Microsoft YaHei UI', 15))
        
        self.search_entry.grid(
            row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15)
        )
        # 如果有选中文本，设置为查找输入框的初始内容
        if self.selected_text:
            self.search_entry.insert(tk.END, self.selected_text)
        self.search_entry.focus()

        # 替换内容标签和输入框
        ttk.Label(main_frame, text="替换为:").grid(
            row=2, column=0, columnspan=3, sticky=tk.W, pady=(0, 5)
        )
        # 使用最小的多行文本输入框代替单行输入框，提升性能
        # 应用相同的字体配置到替换输入框
        if custom_font:
            self.replace_entry = tk.Text(main_frame, height=1, width=50, wrap=tk.NONE, font=custom_font)
        else:
            # 直接设置一个默认字体和大小，确保字体大小能够生效
            self.replace_entry = tk.Text(main_frame, height=1, width=50, wrap=tk.NONE, font=('Microsoft YaHei UI', 15))
        
        self.replace_entry.grid(
            row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15)
        )

        # 查找选项框架
        options_frame = ttk.LabelFrame(main_frame, text="查找选项", padding="10")
        options_frame.grid(
            row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15)
        )
        options_frame.columnconfigure(0, weight=1)
        options_frame.columnconfigure(1, weight=1)
        options_frame.columnconfigure(2, weight=1)

        # 查找模式
        self.search_type = tk.StringVar(value="normal")
        ttk.Radiobutton(
            options_frame, text="普通", variable=self.search_type, value="normal"
        ).grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(
            options_frame, text="正则表达式", variable=self.search_type, value="regex"
        ).grid(row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(
            options_frame, text="完整匹配", variable=self.search_type, value="whole"
        ).grid(row=0, column=2, sticky=tk.W)

        # 其他选项
        self.match_case = tk.BooleanVar(value=True)
        self.multiline_match = tk.BooleanVar(value=False)  # 跨行匹配选项
        ttk.Checkbutton(
            options_frame, text="区分大小写", variable=self.match_case
        ).grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        ttk.Checkbutton(
            options_frame, text="跨行匹配", variable=self.multiline_match
        ).grid(row=1, column=1, sticky=tk.W, pady=(10, 0))

        # 按钮框架 - 重新设计为更平衡的布局
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(
            row=5, column=0, columnspan=3, pady=(10, 0), sticky=(tk.W, tk.E)
        )
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        button_frame.columnconfigure(3, weight=1)
        button_frame.columnconfigure(4, weight=1)
        button_frame.columnconfigure(5, weight=1)

        # 查找按钮组
        find_frame = ttk.LabelFrame(button_frame, text="查找", padding="5")
        find_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=(0, 5))
        find_frame.columnconfigure(0, weight=1)
        find_frame.columnconfigure(1, weight=1)
        find_frame.columnconfigure(2, weight=1)

        self.find_prev_button = ttk.Button(
            find_frame, text="上一个", command=self.find_previous
        )
        self.find_prev_button.grid(row=0, column=0, padx=(2, 2), sticky=tk.W + tk.E)

        self.find_button = ttk.Button(find_frame, text="下一个", command=self.find_next)
        self.find_button.grid(row=0, column=1, padx=(0, 2), sticky=tk.W + tk.E)

        self.find_all_button = ttk.Button(
            find_frame, text="查找全部", command=self.find_all
        )
        self.find_all_button.grid(row=0, column=2, padx=(2, 0), sticky=tk.W + tk.E)

        # 替换按钮组
        replace_frame = ttk.LabelFrame(button_frame, text="替换", padding="5")
        replace_frame.grid(
            row=0, column=3, columnspan=3, sticky=(tk.W, tk.E), padx=(5, 0)
        )
        replace_frame.columnconfigure(0, weight=1)
        replace_frame.columnconfigure(1, weight=1)

        self.replace_once_button = ttk.Button(
            replace_frame, text="替换", command=self.replace_once
        )
        self.replace_once_button.grid(row=0, column=0, padx=(0, 2), sticky=tk.W + tk.E)

        self.replace_all_button = ttk.Button(
            replace_frame, text="替换全部", command=self.replace_all
        )
        self.replace_all_button.grid(row=0, column=1, padx=(2, 0), sticky=tk.W + tk.E)

    def bind_events(self):
        """绑定事件"""
        # 多行文本框需要不同的绑定方式
        # 防止在多行文本框中按Enter键插入换行符并触发查找
        def handle_enter(event):
            self.find_next()
            return "break"
        
        self.search_entry.bind("<Return>", handle_enter)
        self.search_entry.bind("<KP_Enter>", handle_enter)

    def find_next(self):
        """查找下一个匹配项"""
        # 从多行文本框获取内容
        search_term = self.search_entry.get("1.0", tk.END).strip()
        if not search_term:
            messagebox.showwarning("查找", "请输入要查找的内容")
            return

        # 检查是否正在进行查找操作
        if self.is_searching:
            # 取消当前查找操作
            self.cancel_search = True
            # 等待当前查找完成
            if self.search_thread and self.search_thread.is_alive():
                self.search_thread.join(timeout=1)  # 等待最多1秒

        # 检查是否需要重新执行查找 (查找词变更或没有匹配结果)
        needs_new_search = (
            not self.matches or getattr(self, "_last_search_term", "") != search_term
        )

        if needs_new_search:
            # 执行查找
            self.matches = self.perform_search(search_term)
            self._last_search_term = search_term  # 保存当前查找词
            self.current_match_index = -1  # 重置索引

        if not self.matches:
            messagebox.showinfo("查找结果", "未找到指定内容")
            return

        # 更新当前匹配索引
        if self.current_match_index < len(self.matches) - 1:
            self.current_match_index += 1
        else:
            self.current_match_index = 0

        # 高亮当前匹配项并滚动到可视区域
        self.highlight_current_match()

    def find_previous(self):
        """查找上一个匹配项"""
        # 从多行文本框获取内容
        search_term = self.search_entry.get("1.0", tk.END).strip()
        if not search_term:
            messagebox.showwarning("查找", "请输入要查找的内容")
            return

        # 检查是否正在进行查找操作
        if self.is_searching:
            # 取消当前查找操作
            self.cancel_search = True
            # 等待当前查找完成
            if self.search_thread and self.search_thread.is_alive():
                self.search_thread.join(timeout=1)  # 等待最多1秒

        # 检查是否需要重新执行查找 (查找词变更或没有匹配结果)
        needs_new_search = (
            not self.matches or getattr(self, "_last_search_term", "") != search_term
        )

        if needs_new_search:
            # 执行查找
            self.matches = self.perform_search(search_term)
            self._last_search_term = search_term  # 保存当前查找词
            self.current_match_index = -1  # 重置索引

        if not self.matches:
            messagebox.showinfo("查找结果", "未找到指定内容")
            return

        # 更新当前匹配索引
        if self.current_match_index > 0:
            self.current_match_index -= 1
        else:
            self.current_match_index = len(self.matches) - 1

        # 高亮当前匹配项并滚动到可视区域
        self.highlight_current_match()

    def find_all(self):
        """查找全部匹配项"""
        # 从多行文本框获取内容
        search_term = self.search_entry.get("1.0", tk.END).strip()
        if not search_term:
            messagebox.showwarning("查找", "请输入要查找的内容")
            return

        # 检查是否正在进行查找操作
        if self.is_searching:
            # 取消当前查找操作
            self.cancel_search = True
            # 等待当前查找完成
            if self.search_thread and self.search_thread.is_alive():
                self.search_thread.join(timeout=1)  # 等待最多1秒

        # 执行查找
        self.matches = self.perform_search(search_term)
        self._last_search_term = search_term  # 保存当前查找词

        if not self.matches:
            messagebox.showinfo("查找结果", "未找到指定内容")
            return

        # 高亮所有匹配项
        self.highlight_all_matches()

        messagebox.showinfo("查找结果", f"找到了 {len(self.matches)} 个匹配项")

    def replace_once(self):
        """替换当前匹配项"""
        # 从多行文本框获取内容
        search_term = self.search_entry.get("1.0", tk.END).strip()
        replace_term = self.replace_entry.get("1.0", tk.END).strip() if self.replace_entry else ""

        if not search_term:
            messagebox.showwarning("替换", "请输入要查找的内容")
            return

        # 如果还没有查找过, 先执行查找
        if not self.matches:
            self.find_next()
            if not self.matches:
                return  # 没有找到匹配项

        # 检查是否有当前匹配项
        if self.current_match_index < 0 or self.current_match_index >= len(
            self.matches
        ):
            messagebox.showinfo("替换", "请先查找内容")
            return

        # 获取当前匹配项的位置
        start_idx, end_idx = self.matches[self.current_match_index]

        # 执行替换
        self.text_widget.delete(start_idx, end_idx)
        self.text_widget.insert(start_idx, replace_term)

        # 重新执行查找以更新匹配项列表
        self.matches = self.perform_search(search_term)
        self._last_search_term = search_term

        # 重置当前索引
        self.current_match_index = -1

        messagebox.showinfo("替换", "已替换当前匹配项")

    def replace_all(self):
        """替换所有匹配项"""
        # 从多行文本框获取内容
        search_term = self.search_entry.get("1.0", tk.END).strip()
        replace_term = self.replace_entry.get("1.0", tk.END).strip() if self.replace_entry else ""

        if not search_term:
            messagebox.showwarning("替换", "请输入要查找的内容")
            return

        # 执行查找获取所有匹配项
        self.matches = self.perform_search(search_term)
        self._last_search_term = search_term

        if not self.matches:
            messagebox.showinfo("替换", "未找到指定内容")
            return

        # 保存替换计数
        replaced_count = len(self.matches)

        # 从后往前替换, 避免位置偏移问题
        for i in range(len(self.matches) - 1, -1, -1):
            start_idx, end_idx = self.matches[i]
            self.text_widget.delete(start_idx, end_idx)
            self.text_widget.insert(start_idx, replace_term)

        # 清除匹配项列表和高亮
        self.matches = []
        self.current_match_index = -1
        self.text_widget.tag_remove("found", "1.0", tk.END)
        self.text_widget.tag_remove("current_match", "1.0", tk.END)

        messagebox.showinfo("替换", f"已替换 {replaced_count} 个匹配项")

    def perform_search(self, search_term):
        """执行实际的查找操作"""
        # 设置查找状态
        self.is_searching = True
        self.cancel_search = False  # 重置取消标志

        # 更新UI状态
        self.find_button.config(state=tk.DISABLED)
        self.find_prev_button.config(state=tk.DISABLED)
        self.find_all_button.config(state=tk.DISABLED)

        # 清除之前的高亮
        self.text_widget.tag_remove("found", "1.0", tk.END)
        self.text_widget.tag_remove("current_match", "1.0", tk.END)

        search_type = self.search_type.get()
        match_case = self.match_case.get()
        multiline_match = self.multiline_match.get()  # 获取跨行匹配选项

        matches = []

        try:
            if search_type == "regex":
                # 正则表达式查找
                try:
                    flags = 0
                    if not match_case:
                        flags |= re.IGNORECASE
                    if multiline_match:
                        flags |= re.DOTALL  # 启用跨行匹配
                    pattern = search_term
                    content = self.text_widget.get("1.0", tk.END + "-1c")

                    # 获取内容总长度用于进度计算
                    total_length = len(content)
                    processed_length = 0

                    # 编译正则表达式以提高性能
                    compiled_pattern = re.compile(pattern, flags)

                    for match in compiled_pattern.finditer(content):
                        # 检查是否需要取消查找
                        if self.cancel_search:
                            # 更新UI状态
                            self.find_button.config(state=tk.NORMAL)
                            self.find_prev_button.config(state=tk.NORMAL)
                            self.find_all_button.config(state=tk.NORMAL)
                            return []
                        start_idx = self.text_widget.index(f"1.0+{match.start()}c")
                        end_idx = self.text_widget.index(f"1.0+{match.end()}c")
                        matches.append((start_idx, end_idx))
                except re.error as e:
                    messagebox.showerror(
                        "正则表达式错误", f"正则表达式语法错误: {str(e)}"
                    )
                    # 更新UI状态
                    self.find_button.config(state=tk.NORMAL)
                    self.find_prev_button.config(state=tk.NORMAL)
                    self.find_all_button.config(state=tk.NORMAL)
                    return []
            else:
                # 普通查找或完整匹配
                search_flags = 0 if match_case else re.IGNORECASE

                start_pos = "1.0"
                content = self.text_widget.get("1.0", tk.END + "-1c")
                total_length = len(content)
                processed_length = 0

                while True:
                    # 检查是否需要取消查找
                    if self.cancel_search:
                        # 更新UI状态
                        self.find_button.config(state=tk.NORMAL)
                        self.find_prev_button.config(state=tk.NORMAL)
                        self.find_all_button.config(state=tk.NORMAL)
                        return []

                    if search_type == "whole":
                        # 完整单词匹配
                        pattern = r"\b" + re.escape(search_term) + r"\b"
                        content_from_start = self.text_widget.get(start_pos, tk.END)
                        flags = 0 if match_case else re.IGNORECASE
                        match = re.search(pattern, content_from_start, flags)
                        if not match:
                            break

                        # 计算实际位置
                        content_up_to_start = self.text_widget.get("1.0", start_pos)
                        full_content_up_to_match = (
                            content_up_to_start + content_from_start[: match.start()]
                        )

                        lines = full_content_up_to_match.split("\n")
                        current_line = len(lines)
                        current_col = len(lines[-1])
                        start_idx = f"{current_line}.{current_col}"
                        end_idx = f"{current_line}.{current_col + len(search_term)}"
                    else:
                        # 普通查找
                        start_idx = self.text_widget.search(
                            search_term, start_pos, tk.END, nocase=not match_case
                        )
                        if not start_idx:
                            break
                        end_idx = f"{start_idx}+{len(search_term)}c"

                    matches.append((start_idx, end_idx))
                    start_pos = f"{end_idx}+1c"

        except re.error as e:
            messagebox.showerror("正则表达式错误", f"正则表达式语法错误: {str(e)}")
            # 更新UI状态
            self.find_button.config(state=tk.NORMAL)
            self.find_prev_button.config(state=tk.NORMAL)
            self.find_all_button.config(state=tk.NORMAL)
            return []
        except Exception as e:
            messagebox.showerror("查找错误", f"查找过程中发生错误: {str(e)}")
            # 更新UI状态
            self.find_button.config(state=tk.NORMAL)
            self.find_prev_button.config(state=tk.NORMAL)
            self.find_all_button.config(state=tk.NORMAL)
            return []

            # 使用固定颜色配置替代主题管理器
        self.text_widget.tag_configure(
            "found", background="orange", foreground="black"
        )
        self.text_widget.tag_configure(
            "current_match", background="orange", foreground="black"
        )

        # 重置查找状态
        self.is_searching = False

        # 更新UI状态
        self.find_button.config(state=tk.NORMAL)
        self.find_prev_button.config(state=tk.NORMAL)
        self.find_all_button.config(state=tk.NORMAL)

        # 如果不是取消操作, 显示查找结果
        if not self.cancel_search:
            pass  # 不再显示进度标签

        return matches

    def highlight_all_matches(self):
        """高亮所有匹配项"""
        # 清除之前的高亮
        self.text_widget.tag_remove("found", "1.0", tk.END)
        self.text_widget.tag_remove("current_match", "1.0", tk.END)

        # 高亮所有匹配项
        for start_idx, end_idx in self.matches:
            self.text_widget.tag_add("found", start_idx, end_idx)
        
        # 将查找标记提升到最顶层
        self.text_widget.tag_raise("found")

    def highlight_current_match(self):
        """高亮当前匹配项"""
        if (
            not self.matches
            or self.current_match_index < 0
            or self.current_match_index >= len(self.matches)
        ):
            return

        # 获取当前匹配项
        start_idx, end_idx = self.matches[self.current_match_index]

        # 清除之前的当前匹配高亮
        self.text_widget.tag_remove("current_match", "1.0", tk.END)

        # 高亮当前匹配项
        self.text_widget.tag_add("current_match", start_idx, end_idx)
        
        # 将当前匹配标记提升到最顶层
        self.text_widget.tag_raise("current_match")

        # 滚动到可视区域
        self.text_widget.see(start_idx)

        # 设置光标位置
        self.text_widget.mark_set(tk.INSERT, start_idx)
        self.text_widget.focus_set()
        
    def on_dialog_close(self):
        """处理对话框关闭事件，清除所有查找标记"""
        # 清除所有查找相关的标记
        self.text_widget.tag_remove("found", "1.0", tk.END)
        self.text_widget.tag_remove("current_match", "1.0", tk.END)
        
        # 销毁对话框
        self.dialog.destroy()