import tkinter as tk
from tkinter import ttk
from quick_edit_utils import set_window_icon, center_window


class TabSettingsDialog:
    """制表符设置对话框，允许用户配置制表符相关选项"""

    def __init__(self, parent, current_tab_width=4, use_spaces_for_tabs=False):
        """初始化制表符设置对话框

        Args:
            parent: 父窗口
            current_tab_width: 当前制表符宽度
            use_spaces_for_tabs: 是否使用空格替代制表符
        """
        self.parent = parent
        self.current_tab_width = current_tab_width
        self.use_spaces_for_tabs = use_spaces_for_tabs
        self.result_tab_width = current_tab_width
        self.result_use_spaces = use_spaces_for_tabs

        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("制表符设置")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()  # 模态对话框
        
        # 设置对话框样式
        style = ttk.Style()
        style.configure("TLabel", font=("Microsoft YaHei UI", 12, "bold"))
        style.configure("TButton", font=("Microsoft YaHei UI", 12))
        style.configure("TCheckbutton", font=("Microsoft YaHei UI", 12))
        style.configure("TEntry", font=("Microsoft YaHei UI", 12))
        style.configure("TLabelframe", font=("Microsoft YaHei UI", 12, "bold"))

        # 创建UI
        self.create_ui()

        # 设置窗口图标
        set_window_icon(self.dialog)

        # 居中显示对话框
        center_window(self.dialog, 500, 550)

    def create_ui(self):
        """创建对话框UI"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题标签
        title_label = ttk.Label(
            main_frame,
            text="制表符设置",
            font=("Microsoft YaHei UI", 15, "bold")
        )
        title_label.pack(pady=(0, 20))

        # 制表符宽度设置
        tab_width_frame = ttk.LabelFrame(main_frame, text="制表符宽度", padding="15")
        tab_width_frame.pack(fill=tk.X, pady=(0, 20))

        # 宽度标签和输入框
        width_frame = ttk.Frame(tab_width_frame)
        width_frame.pack(fill=tk.X)

        ttk.Label(width_frame, text="制表符宽度 (2-8个字符):", style="TLabel").pack(side=tk.LEFT, padx=(0, 10))

        # 宽度变量
        self.tab_width_var = tk.StringVar(value=str(self.current_tab_width))

        # 宽度输入框
        self.tab_width_entry = ttk.Entry(
            width_frame,
            textvariable=self.tab_width_var,
            width=5,
            justify=tk.CENTER,
            style="TEntry"
        )
        self.tab_width_entry.pack(side=tk.LEFT)

        # 常用宽度按钮
        common_widths_frame = ttk.Frame(tab_width_frame)
        common_widths_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(common_widths_frame, text="常用宽度:", style="TLabel").pack(side=tk.LEFT, padx=(0, 10))

        # 常用宽度按钮
        for width in [2, 4, 8]:
            btn = ttk.Button(
                common_widths_frame,
                text=str(width),
                width=3,
                command=lambda w=width: self.tab_width_var.set(str(w)),
                style="TButton"
            )
            btn.pack(side=tk.LEFT, padx=2)

        # 制表符行为设置
        behavior_frame = ttk.LabelFrame(main_frame, text="制表符行为", padding="15")
        behavior_frame.pack(fill=tk.X, pady=(0, 20))

        # 使用空格替代制表符选项
        self.use_spaces_var = tk.BooleanVar(value=self.use_spaces_for_tabs)
        spaces_checkbox = ttk.Checkbutton(
            behavior_frame,
            text="使用空格替代制表符",
            variable=self.use_spaces_var,
            command=self.on_use_spaces_toggled,
            style="TCheckbutton"
        )
        spaces_checkbox.pack(anchor=tk.W, pady=5)

        # 预览区域
        preview_frame = ttk.LabelFrame(main_frame, text="预览", padding="15")
        preview_frame.pack(fill=tk.BOTH, expand=True)

        # 创建预览文本框
        self.preview_text = tk.Text(
            preview_frame,
            height=5,
            font=("Microsoft YaHei UI", 12),
            wrap=tk.NONE,
            state=tk.DISABLED
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True)

        # 添加预览文本并显示效果
        self.update_preview()

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))

        # 提示标签
        info_label = ttk.Label(
            button_frame,
            text="提示: 更改将应用于新输入的文本",
            foreground="gray",
            font=("Microsoft YaHei UI", 10)
        )
        info_label.pack(side=tk.LEFT)

        # 右侧按钮框架
        right_button_frame = ttk.Frame(button_frame)
        right_button_frame.pack(side=tk.RIGHT)

        # 确定按钮
        ok_button = ttk.Button(
            right_button_frame,
            text="确定",
            width=10,
            command=self.on_ok,
            style="TButton"
        )
        ok_button.pack(side=tk.RIGHT, padx=(5, 0))

        # 取消按钮
        cancel_button = ttk.Button(
            right_button_frame,
            text="取消",
            width=10,
            command=self.on_cancel,
            style="TButton"
        )
        cancel_button.pack(side=tk.RIGHT)

        # 绑定事件
        self.tab_width_var.trace_add("write", lambda *args: self.update_preview())
        self.tab_width_entry.bind("<KeyRelease>", lambda event: self.validate_tab_width())

    def validate_tab_width(self):
        """验证制表符宽度输入"""
        try:
            value = int(self.tab_width_var.get())
            if not 2 <= value <= 8:
                self.tab_width_entry.config(foreground="red")
            else:
                self.tab_width_entry.config(foreground="black")
        except ValueError:
            self.tab_width_entry.config(foreground="red")
        self.update_preview()

    def on_use_spaces_toggled(self):
        """处理使用空格选项的切换"""
        self.update_preview()

    def update_preview(self):
        """更新预览区域"""
        # 获取当前设置
        try:
            tab_width = int(self.tab_width_var.get())
            if not 2 <= tab_width <= 8:
                tab_width = 4  # 默认值
        except ValueError:
            tab_width = 4  # 默认值

        use_spaces = self.use_spaces_var.get()

        # 更新预览文本框
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)

        # 配置预览文本框的制表符宽度
        self.preview_text.config(tabs=tab_width * 8)  # 假设每个字符宽度为8像素

        # 添加预览内容
        self.preview_text.insert(tk.END, "无缩进文本\n")
        self.preview_text.insert(tk.END, "\t一级缩进文本\n")
        self.preview_text.insert(tk.END, "\t\t二级缩进文本\n")
        
        # 显示当前设置
        tab_type = "空格" if use_spaces else "制表符"
        self.preview_text.insert(tk.END, f"\n当前设置: {tab_width}个{tab_type}")

        self.preview_text.config(state=tk.DISABLED)

    def on_ok(self):
        """处理确定按钮点击"""
        try:
            tab_width = int(self.tab_width_var.get())
            if 2 <= tab_width <= 8:
                self.result_tab_width = tab_width
                self.result_use_spaces = self.use_spaces_var.get()
                self.dialog.destroy()
            else:
                # 显示错误消息
                error_window = tk.Toplevel(self.dialog)
                error_window.title("输入错误")
                error_window.geometry("300x150")
                error_window.transient(self.dialog)
                error_window.grab_set()
                
                ttk.Label(
                    error_window,
                    text="制表符宽度必须在2到8之间",
                    padding=20,
                    style="TLabel"
                ).pack()
                
                ttk.Button(
                    error_window,
                    text="确定",
                    command=error_window.destroy,
                    style="TButton"
                ).pack(pady=10)
                
                # 居中错误窗口
                error_window.update_idletasks()
                x = (self.dialog.winfo_x() + self.dialog.winfo_width() // 2) - (error_window.winfo_width() // 2)
                y = (self.dialog.winfo_y() + self.dialog.winfo_height() // 2) - (error_window.winfo_height() // 2)
                error_window.geometry(f"+{x}+{y}")
        except ValueError:
            # 显示错误消息
            error_window = tk.Toplevel(self.dialog)
            error_window.title("输入错误")
            error_window.geometry("300x150")
            error_window.transient(self.dialog)
            error_window.grab_set()
            
            ttk.Label(
                error_window,
                text="请输入有效的数字",
                padding=20,
                style="TLabel"
            ).pack()
            
            ttk.Button(
                error_window,
                text="确定",
                command=error_window.destroy,
                style="TButton"
            ).pack(pady=10)
            
            # 居中错误窗口
            error_window.update_idletasks()
            x = (self.dialog.winfo_x() + self.dialog.winfo_width() // 2) - (error_window.winfo_width() // 2)
            y = (self.dialog.winfo_y() + self.dialog.winfo_height() // 2) - (error_window.winfo_height() // 2)
            error_window.geometry(f"+{x}+{y}")

    def on_cancel(self):
        """处理取消按钮点击"""
        # 恢复原始值
        self.result_tab_width = self.current_tab_width
        self.result_use_spaces = self.use_spaces_for_tabs
        self.dialog.destroy()

    def get_settings(self):
        """获取用户设置的制表符选项

        Returns:
            tuple: (tab_width, use_spaces_for_tabs)
        """
        return (self.result_tab_width, self.result_use_spaces)