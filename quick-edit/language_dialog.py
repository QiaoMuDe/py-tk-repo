import tkinter as tk
from tkinter import ttk
from utils import set_window_icon


class LanguageDialog:
    """语言选择对话框，允许用户搜索和选择语法高亮语言"""

    def __init__(self, parent, current_language=None):
        """初始化语言选择对话框

        Args:
            parent: 父窗口
            current_language: 当前选中的语言
        """
        self.parent = parent
        # 如果没有提供当前语言，默认使用"auto"
        self.current_language = (
            current_language if current_language is not None else "auto"
        )
        self.selected_language = None
        self.all_languages = []  # 存储所有语言列表
        self.language_aliases = {}  # 存储语言别名映射

        # 获取父窗口的字体名称，使用固定字体大小
        try:
            # 尝试从父窗口获取字体配置
            if hasattr(parent, "text_widget") and parent.text_widget:
                # 获取文本部件的字体
                font_config = parent.text_widget["font"]
                # 如果是元组格式 (family, size)
                if isinstance(font_config, tuple) and len(font_config) >= 1:
                    self.font_family = font_config[0]
                else:
                    # 尝试解析字体配置字符串
                    import tkinter.font as tkfont

                    f = tkfont.Font(font=font_config)
                    self.font_family = f.actual()["family"]
            else:
                # 默认字体名称
                self.font_family = "Arial"
        except:
            # 出错时使用默认字体
            self.font_family = "Arial"

        # 固定字体大小为10
        self.font_size = 10

        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("选择语言")
        self.dialog.geometry("500x450")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()  # 模态对话框
        
        # 设置窗口图标
        set_window_icon(self.dialog)

        # 创建UI
        self.create_ui()

        # 居中显示对话框
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

    def create_ui(self):
        """创建对话框UI"""
        # 当前语言标签
        current_label = tk.Label(
            self.dialog,
            text=f"当前语言: {self.current_language}",
            font=(self.font_family, self.font_size),
        )
        current_label.pack(pady=10, padx=10, anchor=tk.W)

        # 搜索框架
        search_frame = tk.Frame(self.dialog)
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        # 搜索标签
        search_label = tk.Label(
            search_frame, text="搜索:", font=(self.font_family, self.font_size)
        )
        search_label.pack(side=tk.LEFT, padx=(0, 5))

        # 搜索输入框
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=(self.font_family, self.font_size),
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 搜索按钮
        search_button = tk.Button(
            search_frame,
            text="搜索",
            command=self.search_languages,
            font=(self.font_family, self.font_size),
            width=8,
        )
        search_button.pack(side=tk.LEFT, padx=5)

        # 绑定回车键触发搜索
        self.search_entry.bind("<Return>", lambda event: self.search_languages())

        # 创建滚动条和列表框
        list_frame = tk.Frame(self.dialog)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 垂直滚动条
        vscrollbar = tk.Scrollbar(list_frame)
        vscrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 语言列表框
        self.language_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=vscrollbar.set,
            font=(self.font_family, self.font_size),
            selectmode=tk.SINGLE,
        )
        self.language_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        vscrollbar.config(command=self.language_listbox.yview)

        # 加载语言（在后台加载以避免阻塞）
        self.dialog.after(100, self.load_languages)

        # 双击选择语言
        self.language_listbox.bind("<Double-Button-1>", self.on_language_select)

        # 绑定键盘上下键导航
        self.language_listbox.bind("<Up>", self.on_keyboard_navigate)
        self.language_listbox.bind("<Down>", self.on_keyboard_navigate)
        self.language_listbox.bind("<Return>", self.on_language_select)

        # 默认让搜索框获取焦点
        self.search_entry.focus_set()

        # 按钮框架
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(pady=10)

        # 确定按钮
        ok_button = tk.Button(
            button_frame,
            text="确定",
            command=self.on_language_select,
            width=10,
            font=(self.font_family, self.font_size),
        )
        ok_button.pack(side=tk.LEFT, padx=5)

        # 取消按钮
        cancel_button = tk.Button(
            button_frame,
            text="取消",
            command=self.dialog.destroy,
            width=10,
            font=(self.font_family, self.font_size),
        )
        cancel_button.pack(side=tk.LEFT, padx=5)

    def load_languages(self):
        """加载语言列表"""
        try:
            # 动态导入get_all_languages函数
            from enhanced_syntax_highlighter import get_all_languages

            # 获取所有支持的语言
            languages_data = get_all_languages()

            # 提取语言名称和别名映射
            self.all_languages = sorted([lang for lang, _ in languages_data])
            self.language_aliases = dict(languages_data)

            # 显示所有语言
            self._update_listbox(self.all_languages)
        except Exception as e:
            # 如果出错，显示错误信息
            self.language_listbox.delete(0, tk.END)
            self.language_listbox.insert(tk.END, f"加载语言失败: {str(e)}")
            self.language_listbox.config(state="disabled")

    def search_languages(self):
        """根据搜索关键字过滤语言，如果搜索框为空则显示所有语言"""
        keyword = self.search_var.get().lower().strip()
        # 如果搜索框为空，显示所有语言
        if not keyword:
            self._update_listbox(self.all_languages)
            return

        # 过滤匹配的语言
        filtered_languages = [
            lang for lang in self.all_languages if keyword in lang.lower()
        ]
        self._update_listbox(filtered_languages)

    def on_keyboard_navigate(self, event):
        """处理键盘导航事件

        Args:
            event: 事件对象
        """
        selection = self.language_listbox.curselection()
        if not selection:
            # 如果没有选中项，选择第一个
            if self.language_listbox.size() > 0:
                self.language_listbox.selection_set(0)
                self.language_listbox.see(0)
            return

        current_index = selection[0]
        total_items = self.language_listbox.size()

        if event.keysym == "Up" and current_index > 0:
            # 向上移动
            new_index = current_index - 1
            self.language_listbox.selection_clear(current_index)
            self.language_listbox.selection_set(new_index)
            self.language_listbox.see(new_index)
        elif event.keysym == "Down" and current_index < total_items - 1:
            # 向下移动
            new_index = current_index + 1
            self.language_listbox.selection_clear(current_index)
            self.language_listbox.selection_set(new_index)
            self.language_listbox.see(new_index)

    def _update_listbox(self, languages):
        """更新列表框内容

        Args:
            languages: 要显示的语言列表
        """
        self.language_listbox.delete(0, tk.END)

        # 添加语言到列表框
        for lang in languages:
            self.language_listbox.insert(tk.END, lang)

        # 尝试选中当前语言
        if self.current_language in languages:
            index = languages.index(self.current_language)
            self.language_listbox.selection_set(index)
            self.language_listbox.see(index)
        elif languages:
            # 如果当前语言不在列表中，默认选中第一个
            self.language_listbox.selection_set(0)
            self.language_listbox.see(0)

    def on_language_select(self, event=None):
        """处理语言选择

        Args:
            event: 事件对象
        """
        selection = self.language_listbox.curselection()
        if selection:
            self.selected_language = self.language_listbox.get(selection[0])
            self.dialog.destroy()

    def get_selected_language(self):
        """获取选中的语言

        Returns:
            str: 选中的语言名称，取消时返回None
        """
        return self.selected_language

    def update_current_language(self, current_language):
        """更新当前语言显示和词法分析器名称

        Args:
            current_language: 当前语言名称
        """
        # 更新当前语言变量
        self.current_language = current_language

        # 如果父窗口有current_lexer属性，也更新它以保持一致性
        if hasattr(self.parent, "current_lexer"):
            self.parent.current_lexer = current_language

        # 更新标签文本
        for widget in self.dialog.winfo_children():
            if isinstance(widget, tk.Label) and widget.cget("text").startswith(
                "当前语言: "
            ):
                widget.config(text=f"当前语言: {current_language}")
                break
