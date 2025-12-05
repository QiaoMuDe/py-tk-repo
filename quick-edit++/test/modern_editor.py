import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

# 设置CTK主题
ctk.set_appearance_mode("dark")  # 可选: "dark", "light", "system"
ctk.set_default_color_theme("blue")  # 可选: "blue", "green", "dark-blue"


class ModernEditorApp:
    def __init__(self):
        # 主窗口
        self.root = ctk.CTk()
        self.root.title("QuickEdit++ - 现代化编辑器")
        self.root.geometry("1000x700")

        # 配置 ttk 分割线样式
        self.style = ttk.Style(self.root)
        self.style.configure(
            "TPanedwindow", sashwidth=6, background="#555555"
        )  # 设置分割线宽度和背景色

        # 创建主容器
        self.create_ui()

    def create_ui(self):
        """创建UI布局"""
        # 主框架
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 顶部工具栏
        self.create_toolbar(main_frame)

        # 创建主内容区域（使用PanedWindow）
        self.create_main_content(main_frame)

        # 底部状态栏
        self.create_status_bar(main_frame)

    def create_toolbar(self, parent):
        """创建顶部工具栏"""
        toolbar = ctk.CTkFrame(parent, height=40)
        toolbar.pack(fill=tk.X, padx=5, pady=(5, 2))
        toolbar.pack_propagate(False)  # 防止工具栏高度变化

        # 左侧文件操作按钮
        left_frame = ctk.CTkFrame(toolbar)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        ctk.CTkButton(left_frame, text="新建", width=50).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(left_frame, text="打开", width=50).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(left_frame, text="保存", width=50).pack(side=tk.LEFT, padx=2)

        # 中间编辑操作按钮
        middle_frame = ctk.CTkFrame(toolbar)
        middle_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=5)

        ctk.CTkButton(middle_frame, text="撤销", width=50).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(middle_frame, text="重做", width=50).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(middle_frame, text="查找", width=50).pack(side=tk.LEFT, padx=2)

        # 右侧知识库操作按钮
        right_frame = ctk.CTkFrame(toolbar)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        ctk.CTkButton(right_frame, text="新建KB", width=60).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(right_frame, text="打开KB", width=60).pack(side=tk.LEFT, padx=2)

        # 知识库选择下拉框
        kb_options = ["我的知识库", "工作笔记", "学习资料", "项目文档"]
        self.kb_selector = ctk.CTkOptionMenu(right_frame, values=kb_options)
        self.kb_selector.set("我的知识库")
        self.kb_selector.pack(side=tk.LEFT, padx=5)

    def create_main_content(self, parent):
        """创建主内容区域（文件树+编辑器）"""
        # 创建 ttk PanedWindow
        self.paned_window = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)

        # 左侧面板 - 文件树
        self.create_file_tree_panel()

        # 右侧面板 - 编辑器
        self.create_editor_panel()

        # 设置初始分割位置
        self.root.after(100, self.set_initial_pane_position)

        # 绑定事件，限制面板的最小宽度
        self.paned_window.bind("<Configure>", self.limit_pane_size)
        self.paned_window.bind("<ButtonRelease-1>", self.limit_pane_size)

    def create_file_tree_panel(self):
        """创建左侧文件树面板"""
        # 左侧主框架
        left_main_frame = ctk.CTkFrame(self.paned_window)

        # 文件树标题栏
        tree_header = ctk.CTkFrame(left_main_frame, height=30)
        tree_header.pack(fill=tk.X, padx=5, pady=(5, 0))
        tree_header.pack_propagate(False)

        ctk.CTkLabel(
            tree_header, text="文件树", font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side=tk.LEFT, padx=10, pady=5)

        # 文件树内容区域
        tree_frame = ctk.CTkFrame(left_main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 创建一个简单的文件树模拟
        self.create_mock_file_tree(tree_frame)

        # 添加到PanedWindow
        self.paned_window.add(left_main_frame, weight=1)

    def create_mock_file_tree(self, parent):
        """创建模拟的文件树"""
        # 使用CTK的ScrollableFrame来模拟文件树
        scrollable_frame = ctk.CTkScrollableFrame(parent, label_text="我的知识库")
        scrollable_frame.pack(fill=tk.BOTH, expand=True)

        # 添加文件夹和文件
        folders = [
            (
                "📁 笔记",
                [
                    ("📄 学习笔记.md", None),
                    ("📄 会议记录.md", None),
                    ("📁 项目", [("📄 项目计划.md", None), ("📄 需求文档.md", None)]),
                ],
            ),
            ("📁 文档", [("📄 API文档.md", None), ("📄 用户手册.md", None)]),
            (
                "📁 代码",
                [("📄 main.py", None), ("📄 utils.py", None), ("📄 config.py", None)],
            ),
        ]

        # 递归添加文件夹和文件
        self.add_tree_items(scrollable_frame, folders, level=0)

    def add_tree_items(self, parent, items, level=0):
        """递归添加文件树项目"""
        for name, children in items:
            # 创建项目框架
            item_frame = ctk.CTkFrame(parent)
            item_frame.pack(fill=tk.X, padx=5, pady=2)

            # 添加缩进
            indent_label = ctk.CTkLabel(item_frame, text="  " * level, width=20)
            indent_label.pack(side=tk.LEFT)

            # 添加项目名称
            item_label = ctk.CTkLabel(item_frame, text=name, anchor=tk.W)
            item_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

            # 如果是文件夹且有子项，递归添加
            if children:
                self.add_tree_items(parent, children, level + 1)

    def create_editor_panel(self):
        """创建右侧编辑器面板"""
        # 右侧主框架
        right_main_frame = ctk.CTkFrame(self.paned_window)

        # 编辑器标题栏
        editor_header = ctk.CTkFrame(right_main_frame, height=30)
        editor_header.pack(fill=tk.X, padx=5, pady=(5, 0))
        editor_header.pack_propagate(False)

        ctk.CTkLabel(
            editor_header, text="编辑器", font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side=tk.LEFT, padx=10, pady=5)

        # 当前文件标签
        self.current_file_label = ctk.CTkLabel(
            editor_header, text="当前文件: 无", text_color="gray"
        )
        self.current_file_label.pack(side=tk.RIGHT, padx=10, pady=5)

        # 编辑器内容区域
        editor_frame = ctk.CTkFrame(right_main_frame)
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 创建文本编辑器
        self.text_editor = ctk.CTkTextbox(
            editor_frame, wrap=tk.WORD, font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.text_editor.pack(fill=tk.BOTH, expand=True)

        # 添加一些示例文本
        sample_text = """# QuickEdit++ 现代化编辑器

这是一个使用 CustomTkinter 和 ttk.PanedWindow 构建的现代化文本编辑器界面。

## 特性

1. **现代化UI设计**
   - 使用 CustomTkinter 组件
   - 深色主题支持
   - 可调整的面板大小

2. **文件树功能**
   - 显示知识库文件结构
   - 支持文件夹展开/折叠
   - 文件图标显示

3. **编辑器功能**
   - 语法高亮支持
   - 自动换行
   - 行号显示（可扩展）

4. **工具栏**
   - 文件操作按钮
   - 编辑操作按钮
   - 知识库管理按钮

## 使用说明

- 拖动中间的分割线可以调整文件树和编辑器的宽度
- 点击文件树中的文件可以在编辑器中打开
- 使用顶部工具栏进行常用操作
- 底部状态栏显示当前文件信息
"""
        self.text_editor.insert("0.0", sample_text)

        # 添加到PanedWindow
        self.paned_window.add(right_main_frame, weight=3)

    def create_status_bar(self, parent):
        """创建底部状态栏"""
        status_bar = ctk.CTkFrame(parent, height=25)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=(2, 5))
        status_bar.pack_propagate(False)  # 防止状态栏高度变化

        # 左侧状态信息
        left_status = ctk.CTkFrame(status_bar)
        left_status.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)

        self.line_label = ctk.CTkLabel(left_status, text="行: 1, 列: 1")
        self.line_label.pack(side=tk.LEFT, padx=5)

        self.file_type_label = ctk.CTkLabel(left_status, text="Markdown")
        self.file_type_label.pack(side=tk.LEFT, padx=5)

        # 右侧状态信息
        right_status = ctk.CTkFrame(status_bar)
        right_status.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=2)

        self.encoding_label = ctk.CTkLabel(right_status, text="UTF-8")
        self.encoding_label.pack(side=tk.LEFT, padx=5)

        self.cursor_pos_label = ctk.CTkLabel(right_status, text="插入")
        self.cursor_pos_label.pack(side=tk.LEFT, padx=5)

    def set_initial_pane_position(self):
        """设置初始分割位置"""
        # 设置左侧面板初始宽度为250像素
        self.paned_window.sashpos(0, 250)

    def limit_pane_size(self, event=None):
        """限制面板的最小宽度"""
        # 获取当前分割线的位置
        sash_pos = self.paned_window.sashpos(0)

        # 限制左侧面板最小宽度为200像素
        if sash_pos < 200:
            self.paned_window.sashpos(0, 200)

        # 限制右侧面板最小宽度为400像素
        window_width = self.root.winfo_width()
        if sash_pos > window_width - 400:
            self.paned_window.sashpos(0, window_width - 400)

    def run(self):
        """运行应用程序"""
        self.root.mainloop()


# 创建并运行应用
if __name__ == "__main__":
    app = ModernEditorApp()
    app.run()
