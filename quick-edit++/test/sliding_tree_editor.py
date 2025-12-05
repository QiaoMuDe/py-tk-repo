import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

class SlidingTreeEditorApp:
    """使用滑动文件树的编辑器应用程序"""
    
    def __init__(self):
        """初始化应用程序"""
        # 设置CTK主题
        ctk.set_appearance_mode("dark")  # 主题: "dark", "light", "system"
        ctk.set_default_color_theme("blue")  # 颜色主题: "blue", "green", "dark-blue"
        
        # 创建主窗口
        self.root = ctk.CTk()
        self.root.title("QuickEdit++ - 滑动文件树编辑器")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # 初始化变量
        self.tree_visible = True
        self.tree_width = 250  # 文件树宽度
        self.tree_animation_speed = 10  # 动画速度
        
        # 创建样式
        self.style = ttk.Style()
        
        # 创建UI
        self.create_ui()
        
        # 绑定事件
        self.bind_events()
        
    def create_ui(self):
        """创建用户界面"""
        # 创建主框架
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建顶部工具栏
        self.create_toolbar(self.main_frame)
        
        # 创建内容区域框架
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # 创建文件树容器（可滑动）
        self.create_sliding_tree_container(self.content_frame)
        
        # 创建编辑器区域
        self.create_editor_panel(self.content_frame)
        
        # 创建底部状态栏和控制按钮
        self.create_bottom_controls(self.main_frame)
        
    def create_toolbar(self, parent):
        """创建顶部工具栏"""
        toolbar = ctk.CTkFrame(parent, height=40)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        toolbar.pack_propagate(False)  # 防止工具栏高度变化
        
        # 文件操作按钮
        file_frame = ctk.CTkFrame(toolbar)
        file_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        new_btn = ctk.CTkButton(file_frame, text="新建", width=60)
        new_btn.pack(side=tk.LEFT, padx=2)
        
        open_btn = ctk.CTkButton(file_frame, text="打开", width=60)
        open_btn.pack(side=tk.LEFT, padx=2)
        
        save_btn = ctk.CTkButton(file_frame, text="保存", width=60)
        save_btn.pack(side=tk.LEFT, padx=2)
        
        # 编辑操作按钮
        edit_frame = ctk.CTkFrame(toolbar)
        edit_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        cut_btn = ctk.CTkButton(edit_frame, text="剪切", width=60)
        cut_btn.pack(side=tk.LEFT, padx=2)
        
        copy_btn = ctk.CTkButton(edit_frame, text="复制", width=60)
        copy_btn.pack(side=tk.LEFT, padx=2)
        
        paste_btn = ctk.CTkButton(edit_frame, text="粘贴", width=60)
        paste_btn.pack(side=tk.LEFT, padx=2)
        
        # 知识库操作按钮
        kb_frame = ctk.CTkFrame(toolbar)
        kb_frame.pack(side=tk.RIGHT, padx=5, pady=5)
        
        search_btn = ctk.CTkButton(kb_frame, text="搜索", width=60)
        search_btn.pack(side=tk.LEFT, padx=2)
        
        settings_btn = ctk.CTkButton(kb_frame, text="设置", width=60)
        settings_btn.pack(side=tk.LEFT, padx=2)
        
    def create_sliding_tree_container(self, parent):
        """创建可滑动的文件树容器"""
        # 文件树容器框架
        self.tree_container = ctk.CTkFrame(parent, width=self.tree_width)
        self.tree_container.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 2))
        self.tree_container.pack_propagate(False)  # 防止容器宽度变化
        
        # 文件树标题栏
        tree_header = ctk.CTkFrame(self.tree_container, height=30)
        tree_header.pack(fill=tk.X, padx=5, pady=(5, 0))
        tree_header.pack_propagate(False)
        
        ctk.CTkLabel(tree_header, text="文件树", font=ctk.CTkFont(size=14, weight="bold")).pack(side=tk.LEFT, padx=10, pady=5)
        
        # 关闭按钮
        close_btn = ctk.CTkButton(tree_header, text="×", width=25, height=25, 
                                  command=self.toggle_tree_visibility)
        close_btn.pack(side=tk.RIGHT, padx=5, pady=2)
        
        # 文件树内容区域
        tree_frame = ctk.CTkFrame(self.tree_container)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建文件树
        self.create_file_tree(tree_frame)
        
    def create_file_tree(self, parent):
        """创建文件树"""
        # 创建一个Frame来容纳TreeView
        tree_container = tk.Frame(parent, bg="#212121")
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        # 创建TreeView
        self.file_tree = ttk.Treeview(tree_container, show="tree")
        
        # 配置样式
        self.style.configure("Treeview", 
                           background="#212121", 
                           foreground="white", 
                           fieldbackground="#212121",
                           font=("Microsoft YaHei", 10),
                           rowheight=24)
        self.style.configure("Treeview.Heading", 
                           background="#333333", 
                           foreground="white",
                           font=("Microsoft YaHei", 11, "bold"))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添加文件夹和文件
        folders = [
            ("📁 笔记", [
                ("📄 学习笔记.md", None),
                ("📄 会议记录.md", None),
                ("📁 项目", [
                    ("📄 项目计划.md", None),
                    ("📄 需求文档.md", None)
                ])
            ]),
            ("📁 文档", [
                ("📄 API文档.md", None),
                ("📄 用户手册.md", None)
            ]),
            ("📁 代码", [
                ("📄 main.py", None),
                ("📄 utils.py", None),
                ("📄 config.py", None)
            ])
        ]
        
        # 递归添加文件夹和文件
        self.add_treeview_items("", folders)
        
    def add_treeview_items(self, parent, items):
        """递归添加文件树项目到TreeView"""
        for name, children in items:
            # 添加项目
            item_id = self.file_tree.insert(parent, "end", text=name, open=False)
            
            # 如果有子项，递归添加
            if children:
                self.add_treeview_items(item_id, children)
                
    def create_editor_panel(self, parent):
        """创建编辑器面板"""
        # 编辑器主框架
        self.editor_frame = ctk.CTkFrame(parent)
        self.editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 编辑器标题栏
        editor_header = ctk.CTkFrame(self.editor_frame, height=30)
        editor_header.pack(fill=tk.X, padx=5, pady=(5, 0))
        editor_header.pack_propagate(False)
        
        ctk.CTkLabel(editor_header, text="编辑器", font=ctk.CTkFont(size=14, weight="bold")).pack(side=tk.LEFT, padx=10, pady=5)
        
        # 当前文件标签
        self.current_file_label = ctk.CTkLabel(editor_header, text="当前文件: 无", text_color="gray")
        self.current_file_label.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # 编辑器内容区域
        editor_content = ctk.CTkFrame(self.editor_frame)
        editor_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建文本编辑器
        self.text_editor = ctk.CTkTextbox(editor_content, wrap=tk.WORD, font=ctk.CTkFont(family="Consolas", size=12))
        self.text_editor.pack(fill=tk.BOTH, expand=True)
        
        # 添加示例文本
        sample_text = """# QuickEdit++ 滑动文件树编辑器

这是一个使用 CustomTkinter 构建的带有滑动文件树的文本编辑器界面。

## 特性

1. **可滑动文件树**
   - 通过底部按钮控制显示/隐藏
   - 平滑的动画效果
   - 不影响编辑器布局

2. **现代化UI设计**
   - 使用 CustomTkinter 组件
   - 深色主题支持
   - 响应式布局

3. **文件树功能**
   - 显示知识库文件结构
   - 支持文件夹展开/折叠
   - 文件图标显示

4. **编辑器功能**
   - 语法高亮支持
   - 自动换行
   - 行号显示（可扩展）

## 使用说明

- 点击底部的"文件树"按钮可以显示/隐藏左侧文件树
- 点击文件树标题栏的"×"按钮也可以隐藏文件树
- 文件树显示/隐藏时有平滑的动画效果
- 使用顶部工具栏进行常用操作
- 底部状态栏显示当前文件信息
"""
        self.text_editor.insert("0.0", sample_text)
        
    def create_bottom_controls(self, parent):
        """创建底部状态栏和控制按钮"""
        # 底部控制框架
        bottom_frame = ctk.CTkFrame(parent, height=30)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
        bottom_frame.pack_propagate(False)
        
        # 左侧状态信息
        left_status = ctk.CTkFrame(bottom_frame)
        left_status.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)
        
        self.line_label = ctk.CTkLabel(left_status, text="行: 1, 列: 1")
        self.line_label.pack(side=tk.LEFT, padx=5)
        
        self.file_type_label = ctk.CTkLabel(left_status, text="Markdown")
        self.file_type_label.pack(side=tk.LEFT, padx=5)
        
        # 中间控制按钮
        control_frame = ctk.CTkFrame(bottom_frame)
        control_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10)
        
        # 文件树切换按钮
        self.tree_toggle_btn = ctk.CTkButton(
            control_frame, 
            text="◀ 文件树", 
            command=self.toggle_tree_visibility,
            width=100
        )
        self.tree_toggle_btn.pack(side=tk.LEFT, padx=5)
        
        # 右侧状态信息
        right_status = ctk.CTkFrame(bottom_frame)
        right_status.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=2)
        
        self.encoding_label = ctk.CTkLabel(right_status, text="UTF-8")
        self.encoding_label.pack(side=tk.LEFT, padx=5)
        
        self.cursor_pos_label = ctk.CTkLabel(right_status, text="插入")
        self.cursor_pos_label.pack(side=tk.LEFT, padx=5)
        
    def bind_events(self):
        """绑定事件"""
        # 绑定文本编辑器的光标移动事件，更新状态栏
        self.text_editor.bind("<KeyRelease>", self.update_cursor_position)
        self.text_editor.bind("<ButtonRelease-1>", self.update_cursor_position)
        
    def update_cursor_position(self, event=None):
        """更新光标位置信息"""
        try:
            # 获取当前光标位置
            cursor_pos = self.text_editor.index(tk.INSERT)
            line, col = cursor_pos.split('.')
            
            # 更新状态栏
            self.line_label.configure(text=f"行: {line}, 列: {int(col)+1}")
        except:
            pass
            
    def toggle_tree_visibility(self):
        """切换文件树的显示/隐藏状态"""
        if self.tree_visible:
            # 隐藏文件树
            self.hide_tree()
        else:
            # 显示文件树
            self.show_tree()
            
    def hide_tree(self):
        """隐藏文件树（直接隐藏）"""
        self.tree_visible = False
        self.tree_toggle_btn.configure(text="▶ 文件树")
        
        # 直接隐藏文件树容器
        self.tree_container.pack_forget()
        
    def show_tree(self):
        """显示文件树（直接显示）"""
        self.tree_visible = True
        self.tree_toggle_btn.configure(text="◀ 文件树")
        
        # 直接显示文件树容器
        self.tree_container.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 2), before=self.editor_frame)
        
    def run(self):
        """运行应用程序"""
        self.root.mainloop()

# 创建并运行应用
if __name__ == "__main__":
    app = SlidingTreeEditorApp()
    app.run()